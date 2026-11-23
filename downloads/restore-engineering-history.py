"""Lossless historical transport. Replaying an archive is not new verification.

The downloadable copy needs only Python's standard library to list and restore
artifacts. Packing additionally uses the repository's strict JSON byte parser.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urljoin, urlsplit
from urllib.request import urlopen
import zlib

FORMAT = 'quantumbridge.engineering-history.v1'
RECIPE_FORMAT = 'quantumbridge.engineering-history-recipe.v1'
XZ_RECIPE_FORMAT = 'quantumbridge.engineering-history-recipe.v2'
MAX_RAW = 4 * 1024**3
MAX_GZIP = 100 * 1024**2 - 1
MAX_INDEX = 16 * 1024**2
MAX_CHUNK = 8 * 1024**2
TARGET_CHUNK = 512 * 1024
GROUP = 64
MAX_PIECES = 500000
MAX_ENTRIES = 4096
XZ_MEMORY_LIMIT = 64 * 1024**2
ORIGINAL = re.compile(r'manifest-(?:preserved-)?[0-9a-f]{64}\.json\.gz\Z')
ASSET = re.compile(r'(?:chunk-[0-9a-f]{64}\.bin\.(?:gz|xz)|(?:recipe|catalog)-[0-9a-f]{64}\.json(?:\.gz)?)\Z')
METADATA = re.compile(r'(?:recipe-[0-9a-f]{64}\.json(?:\.gz)?|catalog-[0-9a-f]{64}\.json)\Z')
GZIP_CHUNK = re.compile(r'chunk-[0-9a-f]{64}\.bin\.gz\Z')


def sha(body):
    return hashlib.sha256(body).hexdigest()


def digest(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def size(value, limit):
    return type(value) is int and 0 < value <= limit


def pairs(items):
    value = {}
    for key, item in items:
        if key in value:
            raise ValueError('Duplicate JSON key')
        value[key] = item
    return value


def read_json(body):
    def invalid(value):
        raise ValueError('Nonfinite JSON value: ' + value)
    def finite(value):
        number = float(value)
        if not math.isfinite(number):
            invalid(value)
        return number
    return json.loads(body, object_pairs_hook=pairs, parse_constant=invalid, parse_float=finite)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode()


def local_file(path, limit):
    path = Path(path)
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError('Symlink archive path')
    with path.open('rb') as stream:
        body = stream.read(limit+1)
    if len(body) > limit:
        raise ValueError('Archive file exceeds its bound')
    return body


def inflate(body, limit):
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(body)) as stream:
            raw = stream.read(limit+1)
    except (OSError, EOFError, zlib.error) as error:
        raise ValueError('Malformed gzip artifact') from error
    if not raw or len(raw) > limit:
        raise ValueError('Inflated artifact exceeds its bound')
    return raw


def chunk_codec(item, recipe_format=XZ_RECIPE_FORMAT):
    codec = item.get('encoding')
    if recipe_format == RECIPE_FORMAT:
        if codec is not None or not item['file'].endswith('.bin.gz'):
            raise ValueError('Legacy chunks require their original gzip transport')
        return 'gzip'
    if (recipe_format != XZ_RECIPE_FORMAT or type(codec) is not str or codec not in {'gzip', 'xz'}
            or not item['file'].endswith('.bin.'+{'gzip': 'gz', 'xz': 'xz'}[codec])):
        raise ValueError('Unknown or mismatched historical chunk codec')
    return codec


def decode_chunk(body, item, recipe_format=XZ_RECIPE_FORMAT):
    if not size(item.get('raw_bytes'), MAX_CHUNK):
        raise ValueError('Invalid historical chunk output bound')
    codec = chunk_codec(item, recipe_format)
    if codec == 'gzip':
        return inflate(body, item['raw_bytes'])
    import lzma
    try:
        decoder = lzma.LZMADecompressor(format=lzma.FORMAT_XZ, memlimit=XZ_MEMORY_LIMIT)
        raw = decoder.decompress(body, max_length=item['raw_bytes']+1)
    except lzma.LZMAError as error:
        raise ValueError('Malformed or over-memory historical XZ chunk') from error
    if not raw or len(raw) > item['raw_bytes'] or not decoder.eof or decoder.unused_data:
        raise ValueError('Incomplete, concatenated or oversized historical XZ chunk')
    return raw


def immutable(path, body):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if any(part.is_symlink() for part in path.parents):
        raise ValueError('Symlink archive directory')
    fd, temporary = tempfile.mkstemp(prefix='.history-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if local_file(path, len(body)) != body:
                raise ValueError('Existing immutable artifact differs')
    finally:
        os.unlink(temporary)


class Store:
    def __init__(self, catalog):
        self.catalog = str(catalog)
        self.remote = self.catalog.startswith(('https://', 'http://'))
        if self.remote:
            parsed = urlsplit(self.catalog)
            if parsed.username or parsed.password or parsed.query or parsed.fragment:
                raise ValueError('Catalog URL must not contain credentials or query parameters')
            if parsed.scheme != 'https' and parsed.hostname not in ('127.0.0.1', 'localhost'):
                raise ValueError('Remote catalogs require HTTPS')
            self.base = self.catalog.rsplit('/', 1)[0]+'/'
        else:
            self.base = Path(catalog).absolute().parent

    def get(self, name, limit):
        if type(name) is not str or not ASSET.fullmatch(name):
            raise ValueError('Unsafe archive asset name')
        return self.fetch(urljoin(self.base, name) if self.remote else self.base/name, limit)

    def fetch(self, target, limit):
        if not self.remote:
            return local_file(target, limit)
        with urlopen(target, timeout=60) as response:
            final = urlsplit(response.geturl())
            original = urlsplit(self.catalog)
            if (final.scheme, final.netloc) != (original.scheme, original.netloc):
                raise ValueError('Archive redirected to another origin')
            body = response.read(limit+1)
        if len(body) > limit:
            raise ValueError('Downloaded artifact exceeds its bound')
        return body

    def load(self):
        body = self.fetch(self.catalog if self.remote else Path(self.catalog), MAX_INDEX)
        value = read_json(body)
        validate_catalog(value)
        return value


def descriptor(row, maximum, pattern=ASSET):
    if (type(row) is not dict or type(row.get('file')) is not str
            or not pattern.fullmatch(row['file']) or not size(row.get('bytes'), maximum)
            or not digest(row.get('sha256')) or row['sha256'] not in row['file']):
        raise ValueError('Invalid content-addressed descriptor')


def validate_catalog(catalog):
    if (type(catalog) is not dict or catalog.get('format') != FORMAT
            or catalog.get('purpose') != 'TRANSPORT_REPLAY_NOT_NEW_VERIFICATION'
            or type(catalog.get('new_function_acceptances')) is not int
            or catalog['new_function_acceptances'] != 0
            or catalog.get('original_evidence_unchanged') is not True
            or type(catalog.get('entries')) is not list
            or not 1 <= len(catalog['entries']) <= MAX_ENTRIES):
        raise ValueError('Invalid historical catalog')
    names = set()
    for entry in catalog['entries']:
        descriptor(entry, MAX_GZIP, ORIGINAL)
        if entry['file'] in names or not size(entry.get('raw_bytes'), MAX_RAW) or not digest(entry.get('raw_sha256')):
            raise ValueError('Duplicate or invalid original artifact')
        names.add(entry['file'])
        identity = entry.get('snapshot_identity')
        if (type(identity) is not dict or type(identity.get('generated_at')) is not str
                or not identity['generated_at'] or not digest(identity.get('source_fingerprint'))):
            raise ValueError('Invalid original snapshot identity')
        descriptor(entry.get('recipe'), MAX_INDEX)
        if not entry['recipe']['file'].startswith('recipe-'):
            raise ValueError('Invalid recipe filename')
    aliases = catalog.get('legacy_chunk_transports', [])
    if type(aliases) is not list or len(aliases) > MAX_PIECES:
        raise ValueError('Invalid legacy chunk transport table')
    seen = set()
    for item in aliases:
        descriptor(item, MAX_CHUNK+65536, GZIP_CHUNK)
        target = item.get('replacement')
        descriptor(target, MAX_CHUNK+65536)
        chunk_codec(target)
        if (item['file'] in seen or not target['file'].startswith('chunk-')
                or not size(item.get('raw_bytes'), MAX_CHUNK) or not digest(item.get('raw_sha256'))
                or any(item[key] != target.get(key) for key in ('raw_bytes', 'raw_sha256'))
                or type(item.get('gzip_header_hex')) is not str
                or re.fullmatch('1f8b08000000000002[0-9a-f]{2}', item['gzip_header_hex']) is None):
            raise ValueError('Invalid legacy chunk restoration identity')
        seen.add(item['file'])
    metadata = catalog.get('retained_metadata', [])
    if type(metadata) is not list or len(metadata) > MAX_ENTRIES:
        raise ValueError('Invalid retained metadata table')
    names = set()
    for item in metadata:
        descriptor(item, MAX_INDEX, METADATA)
        if item['file'] in names:
            raise ValueError('Repeated retained historical metadata')
        names.add(item['file'])


def checked(store, item, limit):
    descriptor(item, limit)
    body = store.get(item['file'], item['bytes'])
    if len(body) != item['bytes'] or sha(body) != item['sha256']:
        raise ValueError('Artifact hash or size differs')
    return body


def recipe_for(store, entry):
    raw = checked(store, entry['recipe'], MAX_INDEX)
    transport = entry['recipe']
    if transport.get('encoding') == 'gzip-json':
        if (not size(transport.get('original_bytes'), MAX_INDEX) or not digest(transport.get('original_sha256'))
                or transport.get('original_file') != 'recipe-'+transport['original_sha256']+'.json'
                or not transport['file'].endswith('.json.gz')):
            raise ValueError('Invalid compressed recipe identity')
        raw = inflate(raw, transport['original_bytes'])
        if len(raw) != transport['original_bytes'] or sha(raw) != transport['original_sha256']:
            raise ValueError('Original recipe hash or size differs')
    elif 'encoding' in transport or not transport['file'].endswith('.json'):
        raise ValueError('Unknown recipe transport')
    recipe = read_json(raw)
    if (type(recipe) is not dict or recipe.get('format') not in {RECIPE_FORMAT, XZ_RECIPE_FORMAT}
            or any(recipe.get(key) != entry.get(key) for key in ('bytes', 'sha256', 'raw_bytes', 'raw_sha256', 'snapshot_identity'))
            or recipe.get('compression') != dict(method='gzip', level=9, mtime=0)
            or type(recipe.get('pieces')) is not list or not 1 <= len(recipe['pieces']) <= MAX_PIECES
            or type(recipe.get('chunks')) is not list or not 1 <= len(recipe['chunks']) <= MAX_PIECES):
        raise ValueError('Recipe does not match original artifact')
    names = set()
    for chunk in recipe['chunks']:
        descriptor(chunk, MAX_CHUNK+65536)
        if (not chunk['file'].startswith('chunk-') or not size(chunk.get('raw_bytes'), MAX_CHUNK)
                or not digest(chunk.get('raw_sha256')) or chunk['file'] in names):
            raise ValueError('Invalid chunk table')
        chunk_codec(chunk, recipe['format'])
        names.add(chunk['file'])
    total = 0
    used = set()
    for piece in recipe['pieces']:
        if (type(piece) is not list or len(piece) != 2 or type(piece[0]) is not int
                or not 0 <= piece[0] < len(recipe['chunks']) or type(piece[1]) is not int or piece[1] != total):
            raise ValueError('Invalid ordered chunk coverage')
        used.add(piece[0])
        total += recipe['chunks'][piece[0]]['raw_bytes']
        if total > entry['raw_bytes']:
            raise ValueError('Chunk coverage exceeds original artifact')
    if total != entry['raw_bytes'] or used != set(range(len(recipe['chunks']))):
        raise ValueError('Incomplete original artifact coverage')
    return recipe


def restore(store, entry, destination=None):
    """Stream raw chunks into an original gzip; verify BOTH identities before output."""
    recipe = recipe_for(store, entry)
    raw_hash = hashlib.sha256()
    with tempfile.TemporaryFile() as target:
        # GzipFile uses a platform-neutral header; original writers used zlib's
        # OS byte. Reproduce that byte only after the deflate stream is complete.
        with gzip.GzipFile(fileobj=target, mode='wb', filename='', compresslevel=9, mtime=0) as writer:
            for number, _ in recipe['pieces']:
                piece = recipe['chunks'][number]
                body = checked(store, piece, MAX_CHUNK+65536)
                raw = decode_chunk(body, piece, recipe['format'])
                if len(raw) != piece['raw_bytes'] or sha(raw) != piece['raw_sha256']:
                    raise ValueError('Original chunk hash or size differs')
                raw_hash.update(raw)
                writer.write(raw)
        if raw_hash.hexdigest() != entry['raw_sha256']:
            raise ValueError('Reconstructed original JSON hash differs')
        header = recipe.get('gzip_header_hex')
        if type(header) is not str or re.fullmatch('1f8b08000000000002[0-9a-f]{2}', header) is None:
            raise ValueError('Unsupported original gzip header')
        target.seek(0)
        target.write(bytes.fromhex(header))
        target.seek(0)
        compressed = target.read(MAX_GZIP+1)
    if len(compressed) != entry['bytes'] or sha(compressed) != entry['sha256']:
        raise ValueError('Original gzip cannot be reproduced by this zlib; no output written')
    if destination is not None:
        immutable(Path(destination)/entry['file'], compressed)
    return compressed


def restore_asset(store, catalog, filename, destination=None):
    """Recover an exact superseded transport, not merely equivalent JSON."""
    validate_catalog(catalog)
    metadata = next((row for row in catalog.get('retained_metadata', []) if row['file'] == filename), None)
    if metadata is not None:
        body = checked(store, metadata, MAX_INDEX)
    else:
        alias = next((row for row in catalog.get('legacy_chunk_transports', []) if row['file'] == filename), None)
        if alias is None:
            raise ValueError('Historical transport is not in the exact restoration table')
        replacement = alias['replacement']
        raw = decode_chunk(checked(store, replacement, MAX_CHUNK+65536), replacement)
        if len(raw) != alias['raw_bytes'] or sha(raw) != alias['raw_sha256']:
            raise ValueError('Historical transport raw identity differs')
        body = bytearray(gzip.compress(raw, compresslevel=9, mtime=0))
        body[:10] = bytes.fromhex(alias['gzip_header_hex'])
        body = bytes(body)
        if len(body) != alias['bytes'] or sha(body) != alias['sha256']:
            raise ValueError('Legacy gzip transport cannot be reproduced by this zlib')
    if destination is not None:
        immutable(Path(destination)/filename, body)
    return body


def repack(catalog_source, destination, *, progress=None):
    """Transcode existing bounded pieces; retain every original and legacy ID."""
    import lzma
    source = Store(catalog_source)
    old = source.load()
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    entries, known_files, known_raw, aliases, metadata = [], {}, {}, {}, {}

    def retain(item):
        body = checked(source, item, MAX_INDEX)
        immutable(destination/item['file'], body)
        metadata[item['file']] = {key: item[key] for key in ('file', 'bytes', 'sha256')}

    for item in old.get('retained_metadata', []):
        retain(item)
    catalog_bytes = source.fetch(source.catalog if source.remote else Path(source.catalog), MAX_INDEX)
    catalog_name = 'catalog-'+sha(catalog_bytes)+'.json'
    immutable(destination/catalog_name, catalog_bytes)
    metadata[catalog_name] = dict(file=catalog_name, bytes=len(catalog_bytes), sha256=sha(catalog_bytes))

    for entry in old['entries']:
        recipe = recipe_for(source, entry)
        retain(entry['recipe'])
        table, positions, remap = [], {}, []
        for item in recipe['chunks']:
            if item['file'] not in known_files:
                body = checked(source, item, MAX_CHUNK+65536)
                raw = decode_chunk(body, item, recipe['format'])
                if len(raw) != item['raw_bytes'] or sha(raw) != item['raw_sha256']:
                    raise ValueError('Original chunk raw identity differs')
                raw_key = (item['raw_sha256'], item['raw_bytes'])
                target = known_raw.get(raw_key)
                if target is None:
                    if chunk_codec(item, recipe['format']) == 'xz':
                        compressed_piece, codec = body, 'xz'
                    else:
                        compressed_piece, codec = lzma.compress(raw, format=lzma.FORMAT_XZ, preset=3), 'xz'
                        if len(compressed_piece) >= len(body):
                            compressed_piece, codec = body, 'gzip'
                    name = 'chunk-'+sha(compressed_piece)+'.bin.'+('xz' if codec == 'xz' else 'gz')
                    target = dict(file=name, bytes=len(compressed_piece), sha256=sha(compressed_piece),
                        raw_bytes=len(raw), raw_sha256=sha(raw), encoding=codec)
                    if decode_chunk(compressed_piece, target) != raw:
                        raise ValueError('New chunk transport differs from its source')
                    immutable(destination/name, compressed_piece)
                    known_raw[raw_key] = target
                known_files[item['file']] = target
                if target['file'] != item['file']:
                    if not GZIP_CHUNK.fullmatch(item['file']):
                        raise ValueError('An existing XZ identity must not be retired implicitly')
                    aliases[item['file']] = dict(
                        **{key: item[key] for key in ('file', 'bytes', 'sha256', 'raw_bytes', 'raw_sha256')},
                        gzip_header_hex=body[:10].hex(), replacement=target)
            target = known_files[item['file']]
            if target['file'] not in positions:
                positions[target['file']] = len(table)
                table.append(target)
            remap.append(positions[target['file']])
        newer = dict(recipe, format=XZ_RECIPE_FORMAT, chunks=table,
            pieces=[[remap[number], offset] for number, offset in recipe['pieces']])
        raw_recipe = (json.dumps(newer, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n').encode()
        if len(raw_recipe) > MAX_INDEX:
            raise ValueError('Repacked recipe exceeds its unchanged bound')
        body = gzip.compress(raw_recipe, mtime=0)
        name = 'recipe-'+sha(body)+'.json.gz'
        immutable(destination/name, body)
        changed = dict(entry, recipe=dict(file=name, bytes=len(body), sha256=sha(body), encoding='gzip-json',
            original_bytes=len(raw_recipe), original_sha256=sha(raw_recipe), original_file='recipe-'+sha(raw_recipe)+'.json'))
        entries.append(changed)
        if progress:
            progress(dict(file=entry['file'], original_raw_bytes=entry['raw_bytes'],
                unique_chunks=len(known_raw), stored_chunk_bytes=sum(row['bytes'] for row in known_raw.values())))
    for alias in old.get('legacy_chunk_transports', []):
        target = known_raw.get((alias['raw_sha256'], alias['raw_bytes']))
        if target is None:
            raise ValueError('Previous legacy transport lost its replacement')
        updated = dict(alias, replacement=target)
        if alias['file'] in aliases and aliases[alias['file']] != updated:
            raise ValueError('Conflicting legacy transport identity')
        aliases[alias['file']] = updated
    catalog = dict(format=FORMAT, purpose='TRANSPORT_REPLAY_NOT_NEW_VERIFICATION',
        packed_at=datetime.now(timezone.utc).isoformat(), original_evidence_unchanged=True,
        new_function_acceptances=0, zlib_runtime=zlib.ZLIB_RUNTIME_VERSION, entries=entries,
        legacy_chunk_transports=sorted(aliases.values(), key=lambda row: row['file']),
        retained_metadata=sorted(metadata.values(), key=lambda row: row['file']),
        previous_catalog_sha256=sha(catalog_bytes),
        prior_reconstruction_attestations=old.get('reconstruction_attestations', []),
        summary=dict(original_files=len(entries), unique_originals=len({row['sha256'] for row in entries}),
            original_bytes=sum(row['bytes'] for row in entries), unique_chunks=len(known_raw),
            chunk_bytes=sum(row['bytes'] for row in known_raw.values()),
            metadata_bytes=sum(row['bytes'] for row in metadata.values()),
            legacy_transports=len(aliases), original_identities_failures_and_dates_unchanged=True))
    validate_catalog(catalog)
    body = encoded(catalog)
    if len(body) > MAX_INDEX:
        raise ValueError('Repacked catalog exceeds its unchanged bound')
    name = 'catalog-'+sha(body)+'.json'
    immutable(destination/name, body)
    return name, catalog


def text_parser():
    path = Path(__file__).with_name('json_byte_views.py')
    if not path.is_file():
        raise ValueError('Packing requires the repository JSON byte parser')
    spec = importlib.util.spec_from_file_location('qb_history_json_bytes', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Text


def chunks(text):
    """Stable child groups preserve exact framing without reserializing JSON."""
    def span(start, end):
        left, right = text.span(start, end)
        if right == left:
            return
        if right-left <= TARGET_CHUNK:
            yield text.raw[left:right]
            return
        children = text.children(start, end)
        if not children:
            for offset in range(left, right, MAX_CHUNK):
                yield text.raw[offset:min(offset+MAX_CHUNK, right)]
            return
        yield text.data(start, children[0][1])
        for first in range(0, len(children), GROUP):
            group = children[first:first+GROUP]
            group_end = children[first+GROUP][1] if first+GROUP < len(children) else group[-1][2]
            group_left, group_right = text.span(group[0][1], group_end)
            if group_right-group_left <= TARGET_CHUNK:
                yield text.raw[group_left:group_right]
            else:
                cursor = group[0][1]
                for _, child_start, child_end in group:
                    if cursor < child_start:
                        yield text.data(cursor, child_start)
                    yield from span(child_start, child_end)
                    cursor = child_end
                if cursor < group_end:
                    yield text.data(cursor, group_end)
        yield text.data(children[-1][2], end)
    if text.start:
        yield text.data(0, text.start)
    yield from (piece for piece in span(text.start, text.end) if piece)
    if text.end < len(text.text):
        yield text.data(text.end, len(text.text))


def identity(text):
    fields = {key: (start, end) for key, start, end in text.children(text.start, text.end)}
    if any(key in fields for key in ('public_snapshot_format', 'deferred_evidence', 'byte_view_format')):
        raise ValueError('Only complete original snapshots can be packed')
    def field(name):
        if name not in fields:
            raise ValueError('Snapshot identity missing')
        return read_json(text.data(*fields[name]))
    date, source = field('generated_at'), field('source')
    if type(date) is not str or not date or type(source) is not dict or not digest(source.get('fingerprint')):
        raise ValueError('Invalid original snapshot identity')
    return dict(generated_at=date, source_fingerprint=source['fingerprint'])


def pack(paths, destination, *, progress=None):
    """Retain originals. Publish a catalog only after every original replays."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    entries, known, duplicates, original_bytes = [], {}, {}, 0
    Text = text_parser()
    for path in sorted(map(Path, paths)):
        if not ORIGINAL.fullmatch(path.name):
            raise ValueError('Not an immutable historical snapshot filename')
        compressed = local_file(path, MAX_GZIP)
        checksum = sha(compressed)
        if checksum not in path.name:
            raise ValueError('Original filename hash differs')
        if checksum not in path.name:
            raise ValueError('Original filename hash differs')
        original_bytes += len(compressed)
        if checksum in duplicates:
            entry = dict(duplicates[checksum], file=path.name)
            entries.append(entry)
            if progress:
                progress(dict(file=path.name, alias=True))
            continue
        raw = inflate(compressed, MAX_RAW)
        text = Text(raw)
        snapshot_identity = identity(text)
        pieces, offset, table, positions = [], 0, [], {}
        for piece in chunks(text):
            checksum_raw = sha(piece)
            if checksum_raw not in known:
                body = gzip.compress(piece, compresslevel=9, mtime=0)
                name = 'chunk-'+sha(body)+'.bin.gz'
                immutable(destination/name, body)
                known[checksum_raw] = dict(file=name, bytes=len(body), sha256=sha(body),
                    raw_bytes=len(piece), raw_sha256=checksum_raw)
            if checksum_raw not in positions:
                positions[checksum_raw] = len(table)
                table.append(known[checksum_raw])
            pieces.append([positions[checksum_raw], offset])
            offset += len(piece)
        entry = dict(file=path.name, bytes=len(compressed), sha256=checksum,
            raw_bytes=len(raw), raw_sha256=sha(raw), snapshot_identity=snapshot_identity)
        recipe = dict(format=RECIPE_FORMAT, **{k: v for k, v in entry.items() if k != 'file'},
            compression=dict(method='gzip', level=9, mtime=0), gzip_header_hex=compressed[:10].hex(),
            chunks=table, pieces=pieces)
        body = (json.dumps(recipe, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n').encode()
        if len(body) > MAX_INDEX:
            raise ValueError('Recipe exceeds its bound')
        compressed_recipe = gzip.compress(body, mtime=0)
        filename = 'recipe-'+sha(compressed_recipe)+'.json.gz'
        immutable(destination/filename, compressed_recipe)
        entry['recipe'] = dict(file=filename, bytes=len(compressed_recipe), sha256=sha(compressed_recipe),
            encoding='gzip-json', original_bytes=len(body), original_sha256=sha(body), original_file='recipe-'+sha(body)+'.json')
        replay = restore(Store(destination/'catalog.json'), entry)
        if replay != compressed:
            raise ValueError('Original compressed artifact was not reproduced')
        duplicates[checksum] = entry
        entries.append(entry)
        if progress:
            progress(dict(file=path.name, raw_bytes=len(raw), pieces=len(pieces), unique_chunks=len(known),
                stored_chunk_bytes=sum(row['bytes'] for row in known.values()), replay_sha256=sha(replay)))
        del text, raw, compressed, replay
    catalog = dict(format=FORMAT, purpose='TRANSPORT_REPLAY_NOT_NEW_VERIFICATION',
        packed_at=datetime.now(timezone.utc).isoformat(), original_evidence_unchanged=True,
        new_function_acceptances=0, zlib_runtime=zlib.ZLIB_RUNTIME_VERSION, entries=entries,
        summary=dict(original_files=len(entries), unique_originals=len(duplicates), original_bytes=original_bytes,
            unique_chunks=len(known), chunk_bytes=sum(row['bytes'] for row in known.values())))
    validate_catalog(catalog)
    body = encoded(catalog)
    if len(body) > MAX_INDEX:
        raise ValueError('Historical catalog exceeds its bound')
    filename = 'catalog-'+sha(body)+'.json'
    immutable(destination/filename, body)
    return filename, catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', help='Local path or HTTPS catalog URL; list unless --restore is supplied')
    parser.add_argument('--restore', help='Exact original filename from the catalog')
    parser.add_argument('--restore-asset', help='Exact superseded gzip chunk or metadata filename from this catalog')
    parser.add_argument('--repack', help='Local or HTTPS catalog: retain originals using bounded gzip/XZ chunks')
    parser.add_argument('--output', type=Path, help='Destination directory; existing originals are never overwritten')
    parser.add_argument('--pack', nargs='+', type=Path, help='Repository-only: immutable full snapshot files')
    args = parser.parse_args()
    if args.repack:
        if args.pack or args.catalog or args.restore or args.restore_asset or not args.output:
            parser.error('--repack requires --output and no other action')
        filename, catalog = repack(args.repack, args.output, progress=lambda row: print(json.dumps(row), flush=True))
        print(json.dumps(dict(catalog=filename, summary=catalog['summary'],
            exact_reconstruction_still_requires_independent_receipts=True)))
        return
    if args.pack:
        if args.catalog or args.restore or args.restore_asset or not args.output:
            parser.error('--pack requires --output and no --catalog/--restore')
        filename, catalog = pack(args.pack, args.output, progress=lambda row: print(json.dumps(row), flush=True))
        print(json.dumps(dict(catalog=filename, summary=catalog['summary'])), flush=True)
        return
    if (not args.catalog or args.restore and args.restore_asset
            or bool(args.output) != bool(args.restore or args.restore_asset)):
        parser.error('--catalog is required; one restore action and --output must be used together')
    store = Store(args.catalog)
    catalog = store.load()
    if args.restore_asset:
        body = restore_asset(store, catalog, args.restore_asset, args.output)
        print(json.dumps(dict(file=args.restore_asset, bytes=len(body), sha256=sha(body),
            purpose=catalog['purpose'], replay_is_not_new_verification=True)))
        return
    if not args.restore:
        print(json.dumps(catalog, ensure_ascii=False, indent=2))
        return
    entry = next((row for row in catalog['entries'] if row['file'] == args.restore), None)
    if entry is None:
        parser.error('Original filename is not in the catalog')
    body = restore(store, entry, args.output)
    print(json.dumps(dict(file=entry['file'], bytes=len(body), sha256=sha(body),
        purpose=catalog['purpose'], original_snapshot_identity=entry['snapshot_identity'])))


if __name__ == '__main__':
    main()
