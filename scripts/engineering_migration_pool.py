"""Lossless JSON transport of repeated migration tables, never run identity."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

FORMAT = 'approved-test-migrations-pool-v1'
FIELD = 'verification_migration_pool'
REFERENCE = 'approved_test_migrations_ref'
MAX_CONTEXTS = 4096
MAX_CONTEXT_BYTES = 8*1024**2
MAX_POOL_BYTES = 16*1024**2


def _body(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def pack(value):
    if not isinstance(value, dict) or not isinstance(value.get('verification'), list):
        raise ValueError('Expected a verification list')
    if FIELD in value:
        raise ValueError('Migration tables are already pooled')
    contexts, rows = {}, []
    for original in value.get('verification', []):
        if not isinstance(original, dict) or REFERENCE in original:
            raise ValueError('Unexpected migration table reference')
        row = dict(original)
        table = row.get('approved_test_migrations')
        if isinstance(table, list) and table:
            body = _body(table)
            if len(body) > MAX_CONTEXT_BYTES:
                raise ValueError('Migration table exceeds its bound')
            if len(body) >= 256:
                key = hashlib.sha256(body).hexdigest()
                context = dict(sha256=key, bytes=len(body), json=body.decode())
                if key in contexts and contexts[key] != context:
                    raise ValueError('Migration context hash collision')
                contexts[key] = context
                row.pop('approved_test_migrations')
                row[REFERENCE] = key
        rows.append(row)
    if len(contexts) > MAX_CONTEXTS or sum(item['bytes'] for item in contexts.values()) > MAX_POOL_BYTES:
        raise ValueError('Migration pool exceeds its bound')
    return dict(value, verification=rows, **{FIELD:dict(schema=1, encoding=FORMAT, contexts=contexts)})


def restore(value):
    if not isinstance(value, dict):
        raise ValueError('Expected a snapshot object')
    if FIELD not in value:
        if any(not isinstance(row, dict) or REFERENCE in row for row in value.get('verification', [])):
            raise ValueError('Missing migration pool')
        return value
    pool = value[FIELD]
    if (type(pool) is not dict or type(pool.get('schema')) is not int or pool['schema'] != 1
            or pool.get('encoding') != FORMAT or type(pool.get('contexts')) is not dict
            or set(pool) != {'schema', 'encoding', 'contexts'} or len(pool['contexts']) > MAX_CONTEXTS):
        raise ValueError('Invalid migration pool')
    contexts, total = {}, 0
    for key, item in pool['contexts'].items():
        if (not isinstance(key, str) or len(key) != 64 or any(c not in '0123456789abcdef' for c in key)
                or type(item) is not dict or set(item) != {'sha256', 'bytes', 'json'}
                or item['sha256'] != key or type(item['bytes']) is not int
                or not 0 < item['bytes'] <= MAX_CONTEXT_BYTES or not isinstance(item['json'], str)):
            raise ValueError('Invalid migration context')
        body = item['json'].encode()
        total += len(body)
        if total > MAX_POOL_BYTES or len(body) != item['bytes'] or hashlib.sha256(body).hexdigest() != key:
            raise ValueError('Migration context hash or size differs')
        table = json.loads(body)
        if not isinstance(table, list) or not table or not all(isinstance(row, dict) for row in table):
            raise ValueError('Expected a migration table')
        contexts[key] = table
    rows, used = [], set()
    for original in value.get('verification', []):
        if not isinstance(original, dict):
            raise ValueError('Invalid verification record')
        row = dict(original)
        if REFERENCE in row:
            key = row.pop(REFERENCE)
            if not isinstance(key, str) or key not in contexts or 'approved_test_migrations' in row:
                raise ValueError('Missing or ambiguous migration context')
            row['approved_test_migrations'] = deepcopy(contexts[key])
            used.add(key)
        rows.append(row)
    if used != set(contexts):
        raise ValueError('Unused migration context')
    result = dict(value, verification=rows)
    result.pop(FIELD)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    value = json.loads(args.input.read_bytes())
    result = restore(value) if args.restore else pack(value)
    if not args.restore and restore(result) != value:
        raise ValueError('Migration pooling changed evidence')
    with args.output.open('xb') as stream:
        stream.write((json.dumps(result, ensure_ascii=False, indent=2)+'\n').encode())
