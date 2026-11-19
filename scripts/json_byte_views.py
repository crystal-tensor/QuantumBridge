"""Lossless structured JSON byte views; transport replay is not verification."""
from bisect import bisect_right, insort
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import tempfile

FORMAT = 'quantumbridge.json-byte-views.v2'
MAX_BYTES = 4 * 1024**3
MAX_COMPRESSED = 100 * 1024**2 - 1
MAX_INDEX = 16 * 1024**2
MAX_SOURCES = 4096
MAX_PIECES = 500000
LITERAL_BYTES = 8 * 1024**2
MAX_LITERAL = 64 * 1024**2


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _size(value, maximum, *, zero=False):
    return type(value) is int and (0 if zero else 1) <= value <= maximum


def _hash(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def _pairs(values):
    result = {}
    for key, value in values:
        if key in result:
            raise ValueError('Duplicate JSON object key')
        result[key] = value
    return result


def _constant(value):
    raise ValueError('Nonfinite JSON constant: ' + value)


def _float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('Nonfinite JSON number')
    return result


DECODER = json.JSONDecoder(object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_float)


def json_value(raw):
    return json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_float)


def _identity(raw, kind):
    value = json_value(raw)
    if type(value) is dict and 'byte_view_format' in value:
        raise ValueError('The restored payload must not be another archive index')
    if kind == 'json_document':
        return None
    if kind != 'full_snapshot':
        raise ValueError('Unknown byte-view document kind')
    if (type(value) is not dict or 'public_snapshot_format' in value or 'deferred_evidence' in value
            or type(value.get('generated_at')) is not str or not value['generated_at']
            or type(value.get('source')) is not dict or not _hash(value['source'].get('fingerprint'))):
        raise ValueError('A full snapshot needs its original source/date identity')
    return dict(generated_at=value['generated_at'], source_fingerprint=value['source']['fingerprint'])


def _safe_name(name):
    return type(name) is str and re.fullmatch(
        r'(?:manifest-[0-9a-f]{64}\.json\.gz|json-piece-[0-9a-f]{64}\.bin\.gz|'
        r'(?:native|target|runtime|runtime-browser|manifest-evidence|runtime-details-[0-9a-f]{2}|'
        r'identity-groups-(?:main|alternate)|namespaces-(?:main|alternate))\.json\.gz)', name) is not None


def _read_file(path, limit):
    path = Path(path)
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError('Archive escaped its directory')
    with path.open('rb') as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError('Archive file exceeds its bound')
    return raw


def _source_raw(directory, descriptor):
    if (type(descriptor) is not dict or not _safe_name(descriptor.get('file'))
            or not _size(descriptor.get('bytes'), MAX_BYTES)
            or not _size(descriptor.get('compressed_bytes'), MAX_COMPRESSED)
            or not _hash(descriptor.get('sha256')) or not _hash(descriptor.get('compressed_sha256'))):
        raise ValueError('Invalid byte-view source descriptor')
    name = descriptor['file']
    compressed_sha = descriptor['compressed_sha256']
    if name.startswith(('manifest-', 'json-piece-')) and compressed_sha not in name:
        raise ValueError('Content-addressed source filename differs')
    path = Path(directory) / name
    if path.resolve().parent != Path(directory).resolve():
        raise ValueError('Archive escaped its directory')
    compressed = _read_file(path, descriptor['compressed_bytes'])
    if len(compressed) != descriptor['compressed_bytes'] or sha(compressed) != compressed_sha:
        raise ValueError('Source compressed bytes/hash differ')
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
            raw = stream.read(descriptor['bytes'] + 1)
    except (OSError, EOFError) as error:
        raise ValueError('Malformed compressed source') from error
    if len(raw) != descriptor['bytes'] or sha(raw) != descriptor['sha256']:
        raise ValueError('Source original bytes/hash differ')
    return raw


def _immutable(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.byte-view-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if path.is_symlink() or path.read_bytes() != raw:
                raise ValueError('Existing immutable archive source changed')
    finally:
        os.unlink(temporary)


class View:
    def __init__(self, raw, sources, pieces):
        self.raw, self.sources, self.pieces = raw, sources, pieces


def anchor(path):
    """Bind actual existing gzip bytes, not a recompressed stand-in."""
    path = Path(path)
    if not _safe_name(path.name):
        raise ValueError('Not an admitted anchor filename')
    compressed = _read_file(path, MAX_COMPRESSED)
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
            raw = stream.read(MAX_BYTES + 1)
    except (OSError, EOFError) as error:
        raise ValueError('Malformed anchor') from error
    if not _size(len(raw), MAX_BYTES):
        raise ValueError('Anchor original bytes exceed their bound')
    json_value(raw)
    descriptor = dict(file=path.name, bytes=len(raw), sha256=sha(raw),
        compressed_bytes=len(compressed), compressed_sha256=sha(compressed))
    if _source_raw(path.parent, descriptor) != raw:
        raise ValueError('Anchor bytes differ')
    return View(raw, [descriptor], [[0, 0, len(raw)]])


def restore(index, directory):
    if (type(index) is not dict or index.get('byte_view_format') != FORMAT
            or index.get('encoding') != 'gzip-byte-spans' or not _size(index.get('bytes'), MAX_BYTES)
            or not _hash(index.get('sha256')) or type(index.get('sources')) is not list
            or not 1 <= len(index['sources']) <= MAX_SOURCES or type(index.get('pieces')) is not list
            or not 1 <= len(index['pieces']) <= MAX_PIECES):
        raise ValueError('Invalid byte-view index')
    sources = index['sources']
    names = [row.get('file') if type(row) is dict else None for row in sources]
    if any(type(name) is not str for name in names) or len(set(names)) != len(names):
        raise ValueError('Duplicate or malformed byte-view source identity')
    if any(type(row) is not dict or not _size(row.get('bytes'), MAX_BYTES) for row in sources):
        raise ValueError('Invalid source bounds')
    if sum(row['bytes'] for row in sources) > MAX_BYTES:
        raise ValueError('Cumulative source bytes exceed their bound')
    used, total = set(), 0
    for piece in index['pieces']:
        if (type(piece) is not list or len(piece) != 3 or not _size(piece[0], len(sources)-1, zero=True)
                or not _size(piece[1], sources[piece[0]]['bytes'], zero=True)
                or not _size(piece[2], sources[piece[0]]['bytes'])
                or piece[1]+piece[2] > sources[piece[0]]['bytes']):
            raise ValueError('Invalid byte-view piece bounds')
        total += piece[2]
        used.add(piece[0])
        if total > index['bytes']:
            raise ValueError('Byte-view coverage exceeds original size')
    if total != index['bytes'] or used != set(range(len(sources))):
        raise ValueError('Byte-view coverage differs')
    buffers = [_source_raw(directory, row) for row in sources]
    raw = b''.join(buffers[number][start:start+length] for number, start, length in index['pieces'])
    if sha(raw) != index['sha256']:
        raise ValueError('Reconstructed original byte hash differs')
    if _identity(raw, index.get('kind')) != index.get('snapshot_identity'):
        raise ValueError('Reconstructed snapshot identity differs')
    return View(raw, sources, index['pieces'])


class Text:
    """Use the standard parser, mapping only visited UTF-8 boundaries."""
    def __init__(self, raw):
        self.raw, self.text = raw, raw.decode('utf-8')
        self.positions = [0, len(self.text)]
        self.offsets = {0: 0, len(self.text): len(raw)}
        _, end = DECODER.raw_decode(self.text, self.space(0))
        if self.space(end) != len(self.text):
            raise ValueError('Trailing JSON content')
        self.start, self.end = self.space(0), end

    def space(self, position):
        while position < len(self.text) and self.text[position] in ' \t\r\n':
            position += 1
        return position

    def byte(self, position):
        if position not in self.offsets:
            start = self.positions[bisect_right(self.positions, position)-1]
            self.offsets[position] = self.offsets[start]+len(self.text[start:position].encode('utf-8'))
            insort(self.positions, position)
        return self.offsets[position]

    def span(self, start, end):
        return self.byte(start), self.byte(end)

    def data(self, start, end):
        left, right = self.span(start, end)
        return self.raw[left:right]

    def children(self, start, end):
        kind = self.text[start]
        if kind not in '[{':
            return None
        position, result, seen, ordinal = self.space(start+1), [], set(), 0
        if self.text[position] in ']}':
            return result
        while position < end:
            if kind == '{':
                key, after = DECODER.raw_decode(self.text, position)
                if type(key) is not str or key in seen:
                    raise ValueError('Duplicate or malformed JSON object key')
                seen.add(key)
                position = self.space(after)
                if self.text[position] != ':':
                    raise ValueError('Missing object colon')
                position = self.space(position+1)
            else:
                key, ordinal = ordinal, ordinal+1
            value, after = DECODER.raw_decode(self.text, position)
            del value
            self.byte(position)
            self.byte(after)
            result.append((key, position, after))
            position = self.space(after)
            if self.text[position] in ']}':
                break
            if self.text[position] != ',':
                raise ValueError('Missing JSON separator')
            position = self.space(position+1)
        return result


class Writer:
    def __init__(self, base, destination):
        self.base, self.destination = base, Path(destination)
        self.sources, self.pieces = list(base.sources), []
        self.literals, self.pending, self.starts = bytearray(), [], []
        position = 0
        for piece in base.pieces:
            self.starts.append(position)
            position += piece[2]
        if position != len(base.raw):
            raise ValueError('Anchor coverage differs')

    def piece(self, number, start, length):
        if not length:
            return
        if self.pieces and self.pieces[-1][0] == number and self.pieces[-1][1]+self.pieces[-1][2] == start:
            self.pieces[-1][2] += length
        else:
            self.pieces.append([number, start, length])
        if len(self.pieces) > MAX_PIECES:
            raise ValueError('Byte-view piece bound exceeded')

    def flush(self):
        if not self.literals:
            return
        raw = bytes(self.literals)
        compressed = gzip.compress(raw, mtime=0)
        name = 'json-piece-'+sha(compressed)+'.bin.gz'
        descriptor = dict(file=name, bytes=len(raw), sha256=sha(raw),
            compressed_bytes=len(compressed), compressed_sha256=sha(compressed))
        if len(compressed) > MAX_COMPRESSED:
            raise ValueError('Compressed literal source exceeds its bound')
        _immutable(self.destination/name, compressed)
        matching = [i for i, row in enumerate(self.sources) if row == descriptor]
        if matching:
            number = matching[0]
        else:
            number = len(self.sources)
            self.sources.append(descriptor)
        for index, start, length in self.pending:
            self.pieces[index] = [number, start, length]
        self.literals.clear()
        self.pending.clear()

    def literal(self, raw):
        if not raw:
            return
        if len(raw) > MAX_LITERAL:
            raise ValueError('A primitive literal exceeds the structured chunk bound')
        if self.literals and len(self.literals)+len(raw) > LITERAL_BYTES:
            self.flush()
        start = len(self.literals)
        self.literals.extend(raw)
        self.pending.append((len(self.pieces), start, len(raw)))
        self.pieces.append([-1, start, len(raw)])
        if len(self.pieces) > MAX_PIECES:
            raise ValueError('Byte-view piece bound exceeded')

    def existing(self, start, end):
        position = start
        while position < end:
            index = bisect_right(self.starts, position)-1
            number, offset, length = self.base.pieces[index]
            inside = position-self.starts[index]
            take = min(length-inside, end-position)
            self.piece(number, offset+inside, take)
            position += take

    def new(self, text, start, end):
        left, right = text.span(start, end)
        if right-left <= LITERAL_BYTES or text.text[start] not in '[{':
            self.literal(text.raw[left:right])
            return
        cursor = start
        for _, first, last in text.children(start, end):
            self.literal(text.data(cursor, first))
            self.new(text, first, last)
            cursor = last
        self.literal(text.data(cursor, end))

    def diff(self, old, new, start, end, before, after):
        left, right = new.span(start, end)
        old_left, old_right = old.span(before, after)
        if right-left == old_right-old_left and new.raw[left:right] == old.raw[old_left:old_right]:
            self.existing(old_left, old_right)
            return
        kind = new.text[start]
        if kind not in '[{' or old.text[before] != kind:
            self.new(new, start, end)
            return
        old_children = {key: (first, last) for key, first, last in old.children(before, after)}
        cursor = start
        for key, first, last in new.children(start, end):
            self.literal(new.data(cursor, first))
            if key in old_children:
                self.diff(old, new, first, last, *old_children[key])
            else:
                self.new(new, first, last)
            cursor = last
        self.literal(new.data(cursor, end))


def archive(raw, destination, base, *, kind='full_snapshot'):
    if not _size(len(raw), MAX_BYTES):
        raise ValueError('Original document exceeds its bound')
    identity = _identity(raw, kind)
    writer = Writer(base, destination)
    if raw == base.raw:
        writer.existing(0, len(raw))
    else:
        old, new = Text(base.raw), Text(raw)
        writer.literal(new.data(0, new.start))
        writer.diff(old, new, new.start, new.end, old.start, old.end)
        writer.literal(new.data(new.end, len(new.text)))
        writer.flush()
    used = sorted({piece[0] for piece in writer.pieces})
    mapping = {number: i for i, number in enumerate(used)}
    sources = [writer.sources[number] for number in used]
    pieces = [[mapping[number], start, length] for number, start, length in writer.pieces]
    index = dict(byte_view_format=FORMAT, encoding='gzip-byte-spans', kind=kind,
        bytes=len(raw), sha256=sha(raw), snapshot_identity=identity, sources=sources, pieces=pieces)
    encoded = (json.dumps(index, ensure_ascii=False, separators=(',', ':'))+'\n').encode()
    if len(encoded) > MAX_INDEX:
        raise ValueError('Byte-view index exceeds its bound')
    if restore(index, destination).raw != raw:
        raise AssertionError('Archive replay changed original bytes')
    return index
