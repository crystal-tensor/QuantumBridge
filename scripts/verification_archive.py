#!/usr/bin/env python3
"""Lossless, content-addressed transport for verification JSON, not new evidence."""

import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile


FORMAT = "quantumbridge.verification-byte-shards.v1"
CHUNK_BYTES = 8 * 1024**2
MAX_CHUNK_BYTES = 16 * 1024**2
MAX_LEDGER_BYTES = 4 * 1024**3
MAX_CHUNKS = 4096


def sha(data):
    return hashlib.sha256(data).hexdigest()


def _integer(value, minimum, maximum):
    return type(value) is int and minimum <= value <= maximum


def _digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _ledger(raw):
    value = json.loads(raw)
    if not isinstance(value, dict) or not isinstance(value.get("runs"), list) or "archive_format" in value:
        raise ValueError("Expected a verification ledger with its original runs")
    if not all(isinstance(run, dict) for run in value["runs"]):
        raise ValueError("Verification runs must remain objects")
    return value


def _summary(value):
    runs = value["runs"]
    counts = Counter(case.get("status", "unknown") for run in runs for case in run.get("cases", []))
    identities = [[run.get(key) for key in ("name", "profile", "recorded_at", "source_fingerprint", "evidence_hash")]
                  for run in runs]
    return dict(run_count=len(runs), case_status_counts=dict(counts),
                ordered_run_identity_sha256=sha(json.dumps(identities, ensure_ascii=False,
                    separators=(",", ":")).encode("utf-8")))


def _atomic_write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".verification-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(body)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _immutable_write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink():
        raise ValueError("Verification archive object directory is a symlink")
    descriptor, temporary = tempfile.mkstemp(prefix=".verification-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(body)
            output.flush()
            os.fsync(output.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if path.is_symlink() or path.read_bytes() != body:
                raise ValueError("Existing verification archive object changed")
    finally:
        os.unlink(temporary)


def archive_bytes(raw, destination, *, chunk_bytes=CHUNK_BYTES):
    """Keep exact input bytes, including formatting, unknown fields and failures.

    An index replacement preserves its preceding index by content identity.
    Chunks are immutable; interrupted writes cannot expose a partial new index.
    This is not a public-data sanitizer or an upgrade of any test status.
    """
    destination = Path(destination)
    if not _integer(chunk_bytes, 1, MAX_CHUNK_BYTES) or not 0 < len(raw) <= MAX_LEDGER_BYTES:
        raise ValueError("Verification archive size is outside its bounded transport")
    count = (len(raw) + chunk_bytes - 1) // chunk_bytes
    if count > MAX_CHUNKS:
        raise ValueError("Too many verification archive chunks")
    value = _ledger(raw)
    chunks = []
    for offset in range(0, len(raw), chunk_bytes):
        part = raw[offset:offset + chunk_bytes]
        compressed = gzip.compress(part, mtime=0)
        identity = sha(compressed)
        filename = "verification-shards/" + identity + ".json.gz"
        _immutable_write(destination.parent / filename, compressed)
        chunks.append(dict(file=filename, offset=offset, bytes=len(part), sha256=sha(part),
                           compressed_bytes=len(compressed), compressed_sha256=identity))
    index = dict(archive_format=FORMAT, encoding="gzip-byte-concatenation", chunk_bytes=chunk_bytes,
                 original_bytes=len(raw), original_sha256=sha(raw), summary=_summary(value), chunks=chunks)
    previous = destination.read_bytes() if destination.exists() else None
    if previous is not None:
        old_index = json.loads(previous)
        if old_index.get("archive_format") != FORMAT:
            raise ValueError("Archive destination is not an archive index; keep the source separately")
        if old_index.get("original_sha256") == index["original_sha256"]:
            if read_bytes(destination) != raw:
                raise ValueError("Existing verification archive does not match its source")
            return old_index
        read_bytes(destination)
        identity = sha(previous)
        filename = "verification-index-" + identity + ".json"
        _immutable_write(destination.parent / filename, previous)
        index["previous_index"] = dict(file=filename, sha256=identity, bytes=len(previous))
    body = (json.dumps(index, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _atomic_write(destination, body)
    return index


def read_bytes(path, *, max_bytes=MAX_LEDGER_BYTES):
    """Verify every compressed/raw hash, exact order, size and original identity."""
    path = Path(path)
    if not _integer(max_bytes, 1, MAX_LEDGER_BYTES) or path.stat().st_size > max_bytes:
        raise ValueError("Verification ledger exceeds the read limit")
    encoded = path.read_bytes()
    value = json.loads(encoded)
    if not isinstance(value, dict) or "archive_format" not in value:
        if len(encoded) > max_bytes:
            raise ValueError("Verification ledger exceeds the read limit")
        return encoded
    if (value.get("archive_format") != FORMAT or value.get("encoding") != "gzip-byte-concatenation"
            or not _integer(value.get("chunk_bytes"), 1, MAX_CHUNK_BYTES)
            or not _integer(value.get("original_bytes"), 1, max_bytes)
            or not _digest(value.get("original_sha256"))
            or not isinstance(value.get("chunks"), list)
            or not 1 <= len(value["chunks"]) <= MAX_CHUNKS):
        raise ValueError("Invalid verification archive index")
    output = bytearray()
    base = path.parent.resolve()
    for position, chunk in enumerate(value["chunks"]):
        if not isinstance(chunk, dict):
            raise ValueError("Invalid verification archive chunk")
        identity = chunk.get("compressed_sha256")
        if (not _digest(identity) or chunk.get("file") != "verification-shards/" + identity + ".json.gz"
                or not _digest(chunk.get("sha256")) or chunk.get("offset") != len(output)
                or type(chunk.get("offset")) is not int
                or not _integer(chunk.get("bytes"), 1, value["chunk_bytes"])
                or (position + 1 < len(value["chunks"]) and chunk["bytes"] != value["chunk_bytes"])
                or not _integer(chunk.get("compressed_bytes"), 1, MAX_CHUNK_BYTES + 65536)
                or len(output) + chunk["bytes"] > value["original_bytes"]):
            raise ValueError("Invalid verification archive chunk descriptor")
        source = path.parent / chunk["file"]
        if source.is_symlink() or source.parent.is_symlink() or not source.resolve().is_relative_to(base):
            raise ValueError("Verification archive chunk escaped its directory")
        if source.stat().st_size != chunk["compressed_bytes"]:
            raise ValueError("Verification archive compressed size differs")
        compressed = source.read_bytes()
        if sha(compressed) != identity:
            raise ValueError("Verification archive compressed hash differs")
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
            part = stream.read(chunk["bytes"] + 1)
        if len(part) != chunk["bytes"] or sha(part) != chunk["sha256"]:
            raise ValueError("Verification archive raw bytes differ")
        output.extend(part)
    raw = bytes(output)
    if len(raw) != value["original_bytes"] or sha(raw) != value["original_sha256"]:
        raise ValueError("Verification archive original identity differs")
    if _summary(_ledger(raw)) != value.get("summary"):
        raise ValueError("Verification archive run identities or status counts differ")
    previous = value.get("previous_index")
    if previous is not None:
        identity = previous.get("sha256") if isinstance(previous, dict) else None
        if (not _digest(identity) or previous.get("file") != "verification-index-" + identity + ".json"
                or not _integer(previous.get("bytes"), 1, MAX_CHUNK_BYTES)):
            raise ValueError("Invalid verification archive history descriptor")
        history = path.parent / previous["file"]
        if history.is_symlink() or history.parent.is_symlink() or not history.resolve().is_relative_to(base):
            raise ValueError("Verification archive history escaped its directory")
        if history.stat().st_size != previous["bytes"] or sha(history.read_bytes()) != identity:
            raise ValueError("Verification archive history identity differs")
    return raw


def load(path):
    return json.loads(read_bytes(path))


def save(path, value):
    """Retain existing raw-ledger behavior or append via an existing archive."""
    path = Path(path)
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    prior = json.loads(path.read_bytes()) if path.exists() else {}
    if "archive_format" in prior:
        archive_bytes(raw, path)
    else:
        _atomic_write(path, raw)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--restore", action="store_true", help="Restore exact bytes to a new file")
    args = parser.parse_args()
    raw = read_bytes(args.source)
    if args.restore:
        with args.destination.open("xb") as output:
            output.write(raw)
        print(json.dumps(dict(restored_bytes=len(raw), sha256=sha(raw))))
    else:
        if args.source.resolve() == args.destination.resolve():
            raise ValueError("Keep the original ledger; choose a separate archive index")
        result = archive_bytes(raw, args.destination)
        print(json.dumps({key: result[key] for key in ("original_bytes", "original_sha256", "summary")}))
