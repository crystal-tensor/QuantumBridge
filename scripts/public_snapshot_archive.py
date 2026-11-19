"""Lossless gzip transport for a public snapshot, never a new verification."""
import argparse
import gzip
import hashlib
import io
import importlib.util
import json
import os
from pathlib import Path
import tempfile

FORMAT = 'quantumbridge.public-snapshot-gzip.v1'
VIEW_FORMAT = 'quantumbridge.public-snapshot-byte-views.v2'
INDEX_FORMAT = 'quantumbridge.public-snapshot-index-gzip.v3'
RAW_INDEX_THRESHOLD = 1024**2
RAW_THRESHOLD = 50 * 1024**2
MAX_COMPRESSED_BYTES = 100 * 1024**2 - 1
MAX_ORIGINAL_BYTES = 4 * 1024**3

_view_spec = importlib.util.spec_from_file_location('qb_json_byte_views',
    Path(__file__).with_name('json_byte_views.py'))
_views = importlib.util.module_from_spec(_view_spec)
_view_spec.loader.exec_module(_views)


def _sha(body):
    return hashlib.sha256(body).hexdigest()


def _digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _size(value, maximum):
    return type(value) is int and 0 < value <= maximum


def _identity(value):
    source = value.get('source')
    if not isinstance(value.get('generated_at'), str) or not value['generated_at'] or not isinstance(source, dict) or not _digest(source.get('fingerprint')):
        raise ValueError('Invalid public snapshot identity')
    return dict(generated_at=value['generated_at'], source_fingerprint=source['fingerprint'])


def _atomic(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.snapshot-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _immutable(path, body):
    descriptor, temporary = tempfile.mkstemp(prefix='.snapshot-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if path.is_symlink() or path.read_bytes() != body:
                raise ValueError('Existing snapshot archive object differs')
    finally:
        os.unlink(temporary)


def _read_index(path, value):
    if (value.get('encoding') != 'gzip-index'
            or value.get('file') != path.stem+'-index-'+str(value.get('index_compressed_sha256'))+'.json.gz'
            or not _size(value.get('index_bytes'), _views.MAX_INDEX)
            or not _size(value.get('index_compressed_bytes'), _views.MAX_INDEX)
            or not _digest(value.get('index_sha256')) or not _digest(value.get('index_compressed_sha256'))):
        raise ValueError('Invalid compressed snapshot index')
    target = path.with_name(value['file'])
    if target.is_symlink() or target.parent.is_symlink() or target.stat().st_size != value['index_compressed_bytes']:
        raise ValueError('Compressed snapshot index escaped or differs in size')
    compressed = target.read_bytes()
    if _sha(compressed) != value['index_compressed_sha256']:
        raise ValueError('Compressed snapshot index hash differs')
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        raw = stream.read(value['index_bytes']+1)
    if len(raw) != value['index_bytes'] or _sha(raw) != value['index_sha256']:
        raise ValueError('Snapshot index original bytes differ')
    inner = _views.json_value(raw)
    if (type(inner) is not dict or inner.get('public_snapshot_format') != VIEW_FORMAT
            or inner.get('kind') != 'full_snapshot'
            or any(inner.get(name) != value.get(name) for name in ('bytes', 'sha256', 'snapshot_identity', 'download'))):
        raise ValueError('Compressed snapshot index identity differs')
    return raw, inner


def read_bytes(path):
    """Accept original JSON or verify a bounded, sibling-only gzip archive."""
    path = Path(path)
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError('Public snapshot archive escaped its directory')
    if path.stat().st_size > MAX_ORIGINAL_BYTES:
        raise ValueError('Public snapshot exceeds the read limit')
    raw = path.read_bytes()
    value = json.loads(raw)
    if isinstance(value, dict) and value.get('public_snapshot_format') == INDEX_FORMAT:
        if len(raw) > 4096:
            raise ValueError('Compressed snapshot index wrapper exceeds its bound')
        raw, value = _read_index(path, _views.json_value(raw))
    if isinstance(value, dict) and value.get('public_snapshot_format') == VIEW_FORMAT:
        if len(raw) > _views.MAX_INDEX or value.get('kind') != 'full_snapshot':
            raise ValueError('Invalid public snapshot byte-view descriptor')
        return _views.restore(value, path.parent).raw
    if isinstance(value, dict) and 'byte_view_format' in value:
        raise ValueError('Expected an explicit full public snapshot descriptor')
    if not isinstance(value, dict) or 'public_snapshot_format' not in value:
        return raw
    if (value['public_snapshot_format'] != FORMAT or value.get('encoding') != 'gzip'
            or value.get('file') != path.stem+'-'+str(value.get('compressed_sha256'))+'.json.gz'
            or not _size(value.get('bytes'), MAX_ORIGINAL_BYTES)
            or not _size(value.get('compressed_bytes'), MAX_COMPRESSED_BYTES)
            or not _digest(value.get('sha256')) or not _digest(value.get('compressed_sha256'))):
        raise ValueError('Invalid public snapshot archive descriptor')
    payload = path.with_name(value['file'])
    if payload.is_symlink() or payload.parent.is_symlink() or not payload.resolve().is_relative_to(path.parent.resolve()):
        raise ValueError('Public snapshot archive escaped its directory')
    if payload.stat().st_size != value['compressed_bytes']:
        raise ValueError('Public snapshot compressed size differs')
    compressed = payload.read_bytes()
    if _sha(compressed) != value['compressed_sha256']:
        raise ValueError('Public snapshot compressed hash differs')
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        raw = stream.read(value['bytes']+1)
    if len(raw) != value['bytes'] or _sha(raw) != value['sha256']:
        raise ValueError('Public snapshot original bytes differ')
    restored = json.loads(raw)
    if not isinstance(restored, dict) or 'public_snapshot_format' in restored or 'deferred_evidence' in restored or _identity(restored) != value.get('snapshot_identity'):
        raise ValueError('Public snapshot identity differs')
    return raw


def load(path):
    return json.loads(read_bytes(path))


def _preserve_index(path, body):
    compressed = gzip.compress(body, mtime=0)
    filename = path.stem+'-index-'+_sha(compressed)+'.json.gz'
    _immutable(path.with_name(filename), compressed)
    return dict(file=filename, index_bytes=len(body), index_sha256=_sha(body),
        index_compressed_bytes=len(compressed), index_compressed_sha256=_sha(compressed))


def _index_wrapper(path, body, descriptor):
    archived = _preserve_index(path, body)
    return dict(public_snapshot_format=INDEX_FORMAT, encoding='gzip-index', **archived,
        **{name: descriptor[name] for name in ('bytes', 'sha256', 'snapshot_identity', 'download')})


def _wrapper_bytes(value):
    raw = (json.dumps(value, separators=(',', ':'))+'\n').encode()
    if len(raw) > 4096:
        raise ValueError('Compressed snapshot index wrapper exceeds its bound')
    return raw


def compact_index(path):
    """Shard only an existing index; preserve full download and evidence bytes."""
    path = Path(path)
    restored = read_bytes(path)
    body = path.read_bytes()
    descriptor = _views.json_value(body)
    if descriptor.get('public_snapshot_format') == INDEX_FORMAT:
        return descriptor
    if descriptor.get('public_snapshot_format') != VIEW_FORMAT or len(body) < RAW_INDEX_THRESHOLD:
        raise ValueError('Expected a large full byte-view index')
    download = descriptor.get('download', {})
    if download.get('file') != path.name+'.gz':
        raise ValueError('Complete snapshot download identity differs')
    target = path.with_name(download['file'])
    if target.is_symlink() or target.stat().st_size != download.get('bytes'):
        raise ValueError('Complete snapshot download escaped or differs in size')
    compressed = target.read_bytes()
    if _sha(compressed) != download.get('sha256'):
        raise ValueError('Complete snapshot download hash differs')
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        actual = stream.read(len(restored)+1)
    if actual != restored:
        raise ValueError('Complete snapshot download original bytes differ')
    wrapper = _index_wrapper(path, body, descriptor)
    _atomic(path, _wrapper_bytes(wrapper))
    return wrapper


def write_bytes(path, raw, *, raw_threshold=RAW_THRESHOLD, reuse_views=False):
    """Keep every byte and original identity; never resample or restamp data."""
    path = Path(path)
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError('Public snapshot archive escaped its directory')
    if type(raw_threshold) is not int or raw_threshold < 1 or not _size(len(raw), MAX_ORIGINAL_BYTES):
        raise ValueError('Invalid public snapshot transport bounds')
    value = _views.json_value(raw)
    if (not isinstance(value, dict) or 'public_snapshot_format' in value
            or 'byte_view_format' in value or 'deferred_evidence' in value):
        raise ValueError('Expected a complete public snapshot')
    identity = _identity(value)
    compressed = gzip.compress(raw, mtime=0)
    if len(compressed) > MAX_COMPRESSED_BYTES:
        raise ValueError('Compressed snapshot needs additional sharding before publication')
    path.parent.mkdir(parents=True, exist_ok=True)
    if reuse_views and len(raw) >= raw_threshold and path.exists():
        previous_body = path.read_bytes()
        previous = _views.json_value(previous_body)
        if isinstance(previous, dict) and previous.get('public_snapshot_format') == INDEX_FORMAT:
            if len(previous_body) > 4096:
                raise ValueError('Compressed snapshot index wrapper exceeds its bound')
            _, previous = _read_index(path, previous)
        base = None
        if isinstance(previous, dict) and previous.get('public_snapshot_format') == VIEW_FORMAT:
            if previous.get('kind') != 'full_snapshot' or len(previous_body) > _views.MAX_INDEX:
                raise ValueError('Invalid prior snapshot byte views')
            base = _views.restore(previous, path.parent)
        elif isinstance(previous, dict) and previous.get('public_snapshot_format') == FORMAT:
            previous_raw = read_bytes(path)
            base = _views.anchor(path.with_name(previous['file']))
            if base.raw != previous_raw:
                raise ValueError('Prior snapshot anchor differs')
        if base is not None:
            descriptor = _views.archive(raw, path.parent, base)
            descriptor['public_snapshot_format'] = VIEW_FORMAT
            descriptor['download'] = dict(file=path.name+'.gz', bytes=len(compressed), sha256=_sha(compressed))
            encoded = (json.dumps(descriptor, ensure_ascii=False, separators=(',', ':'))+'\n').encode()
            if len(encoded) > _views.MAX_INDEX:
                raise ValueError('Public snapshot byte-view index exceeds its bound')
            _preserve_index(path, previous_body)
            _preserve_index(path, encoded)
            _atomic(path.with_name(path.name+'.gz'), compressed)
            if len(encoded) >= RAW_INDEX_THRESHOLD:
                wrapper = _index_wrapper(path, encoded, descriptor)
                _atomic(path, _wrapper_bytes(wrapper))
                return wrapper
            _atomic(path, encoded)
            return descriptor
    descriptor = dict(public_snapshot_format=FORMAT, encoding='gzip',
        file=path.stem+'-'+_sha(compressed)+'.json.gz',
        bytes=len(raw), sha256=_sha(raw), compressed_bytes=len(compressed),
        compressed_sha256=_sha(compressed), snapshot_identity=identity)
    _immutable(path.with_name(descriptor['file']), compressed)
    _atomic(path.with_name(path.name+'.gz'), compressed)
    # Small snapshots keep the legacy JSON shape. Larger files become an
    # explicit index; the complete gzip download has exactly the same bytes.
    _atomic(path, raw if len(raw) < raw_threshold else (json.dumps(descriptor, indent=2)+'\n').encode())
    return descriptor


def dump(path, value, *, raw_threshold=RAW_THRESHOLD, reuse_views=False):
    return write_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8'),
        raw_threshold=raw_threshold, reuse_views=reuse_views)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    args = parser.parse_args()
    print(json.dumps(write_bytes(args.snapshot, read_bytes(args.snapshot))))
