#!/usr/bin/env python3
"""Restore ordered metadata archives; this never imports or executes an SDK."""
import argparse
import gzip
import hashlib
import io
import json
import math
from pathlib import Path

MARKER = '_quantumbridge_group_order'
FORMAT = 'quantumbridge.identity-groups-ordered.v1'
MAX_RAW = 64 * 1024**2
MAX_GROUPS = 200000


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def _reject(value):
    raise ValueError('Nonfinite JSON value: '+value)


def _float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('Nonfinite JSON number')
    return number


def _load(raw):
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_RAW:
        raise ValueError('Metadata byte limit exceeded')
    value = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_reject, parse_float=_float)
    if type(value) is not dict:
        raise ValueError('Expected an identity-group metadata object')
    return value


def _encode(value):
    return json.dumps(value, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


def encode_groups(raw):
    value = _load(raw)
    groups = value.get('groups')
    if MARKER in value or type(groups) is not list or not 0 < len(groups) <= MAX_GROUPS:
        raise ValueError('Invalid or already ordered identity groups')
    if _encode(value) != raw:
        raise ValueError('Original metadata is not the exact supported compact encoding')
    for group in groups:
        if (type(group) is not dict or type(group.get('id')) is not str
                or type(group.get('record_ids')) is not list
                or not all(type(name) is str for name in group['record_ids'])):
            raise ValueError('Unknown group shape; original metadata must remain unchanged')
    order = sorted(range(len(groups)), key=lambda index: tuple(groups[index]['record_ids']))
    value['groups'] = [groups[index] for index in order]
    value[MARKER] = dict(format=FORMAT, original_indices=order,
        original_json_bytes=len(raw), original_json_sha256=sha(raw),
        encoding='json-ascii-compact', new_collection=False, native_functions_accepted=0)
    encoded = _encode(value)
    if len(encoded) > MAX_RAW or restore_groups(encoded) != raw:
        raise ValueError('Ordered metadata does not restore the original bytes')
    return encoded


def restore_groups(raw):
    value = _load(raw)
    if MARKER not in value:
        return raw
    metadata = value.pop(MARKER)
    groups = value.get('groups')
    if (type(metadata) is not dict or metadata.get('format') != FORMAT
            or metadata.get('encoding') != 'json-ascii-compact'
            or metadata.get('new_collection') is not False
            or type(metadata.get('native_functions_accepted')) is not int
            or metadata['native_functions_accepted'] != 0
            or type(groups) is not list or not 0 < len(groups) <= MAX_GROUPS):
        raise ValueError('Invalid ordered metadata descriptor')
    order = metadata.get('original_indices')
    if (type(order) is not list or len(order) != len(groups)
            or any(type(index) is not int or not 0 <= index < len(groups) for index in order)
            or len(set(order)) != len(groups)):
        raise ValueError('Original group order is not a complete permutation')
    restored = [None] * len(groups)
    for index, group in zip(order, groups, strict=True):
        restored[index] = group
    value['groups'] = restored
    original = _encode(value)
    if (type(metadata.get('original_json_bytes')) is not int
            or not 0 < metadata['original_json_bytes'] <= MAX_RAW
            or len(original) != metadata['original_json_bytes']
            or sha(original) != metadata.get('original_json_sha256')):
        raise ValueError('Original metadata bytes/hash differ')
    return original


def restore_file(source, output):
    source, output = Path(source), Path(output)
    if source.stat().st_size > MAX_RAW:
        raise ValueError('Compressed metadata byte limit exceeded')
    compressed = source.read_bytes()
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        raw = stream.read(MAX_RAW+1)
    restored = restore_groups(raw)
    with output.open('xb') as target:
        target.write(restored)
    return dict(restored_bytes=len(restored), restored_sha256=sha(restored),
        source_compressed_sha256=sha(compressed), sdk_executed=False,
        scientific_evidence_refreshed=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(restore_file(args.source, args.output)))
