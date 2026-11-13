"""Archiving transports exact evidence; it never accepts or rewrites a result."""

from contextlib import redirect_stdout
import copy
import gzip
import importlib.util
import io
import json
from pathlib import Path

import pytest

from test_verification_worker_environment import fixture, recorder


SCRIPTS = Path(__file__).parents[2] / "scripts"


def module(name):
    spec = importlib.util.spec_from_file_location("archive_test_" + name, SCRIPTS / (name + ".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


archive = module("verification_archive")
builder = module("build_engineering_progress")


def original_bytes():
    row = dict(name="original-failure", profile="main", recorded_at="2026-11-11T00:00:00Z",
        source_fingerprint="original-source", evidence_hash="original-junit",
        process_terminal_validation=dict(provided=True, exit=1, receipt_hash="original-exit"),
        cases=[dict(id="tests.example::test_value[中文]", status="failed"),
               dict(id="tests.example::test_unknown", status="unverified")],
        test_context=dict(files=["tests/example.py"], sha256="original-test"))
    return (json.dumps(dict(schema=1, runs=[row, copy.deepcopy(row)],
        unknown_metadata=dict(original=[None, True, 1.25], date="do-not-restamp")),
        ensure_ascii=False, indent=3) + "\r\n").encode("utf-8")


def make_archive(tmp_path):
    path = tmp_path / "index.json"
    raw = original_bytes()
    index = archive.archive_bytes(raw, path, chunk_bytes=256)
    return path, raw, index


def test_byte_exact_roundtrip_preserves_order_duplicate_ids_dates_failures_and_unknowns(tmp_path):
    path, raw, index = make_archive(tmp_path)
    assert len(index["chunks"]) > 1
    assert archive.read_bytes(path) == raw
    assert archive.load(path) == json.loads(raw)
    assert index["summary"]["run_count"] == 2
    assert index["summary"]["case_status_counts"] == dict(failed=2, unverified=2)
    assert index["original_sha256"] == archive.sha(raw)
    before = {file: file.read_bytes() for file in tmp_path.rglob("*") if file.is_file()}
    assert archive.archive_bytes(raw, path, chunk_bytes=256) == index
    assert all(file.read_bytes() == body for file, body in before.items())
    assert not list(tmp_path.rglob(".verification-*"))


def test_updates_preserve_immutable_original_index_and_all_old_bytes(tmp_path):
    path, raw, index = make_archive(tmp_path)
    original_index = path.read_bytes()
    value = json.loads(raw)
    value["runs"].append(dict(name="new-pass", cases=[dict(id="other", status="passed")]))
    archive.save(path, value)
    assert archive.load(path) == value
    newest = json.loads(path.read_bytes())
    history = path.parent / newest["previous_index"]["file"]
    assert history.read_bytes() == original_index
    assert archive.read_bytes(history) == raw
    assert newest["summary"]["case_status_counts"] == dict(failed=2, unverified=2, passed=1)
    for chunk in index["chunks"]:
        assert (path.parent / chunk["file"]).is_file()


def test_legacy_ledger_load_and_save_stay_ordinary_json(tmp_path):
    path = tmp_path / "runs.json"
    raw = original_bytes()
    path.write_bytes(raw)
    assert archive.read_bytes(path) == raw
    value = archive.load(path)
    archive.save(path, value)
    assert json.loads(path.read_bytes()) == value
    assert "archive_format" not in json.loads(path.read_bytes())


@pytest.mark.parametrize("fault", ["format", "encoding", "total", "total_bool", "original_hash",
    "chunk_size", "chunk_size_bool", "offset", "offset_bool", "raw_size", "compressed_size",
    "compressed_hash", "raw_hash", "path", "order", "missing", "summary", "run_identity"])
def test_index_tampering_is_rejected_not_silently_reconstructed(tmp_path, fault):
    path, _, value = make_archive(tmp_path)
    if fault == "format": value["archive_format"] = "future"
    elif fault == "encoding": value["encoding"] = "zip"
    elif fault == "total": value["original_bytes"] += 1
    elif fault == "total_bool": value["original_bytes"] = True
    elif fault == "original_hash": value["original_sha256"] = "0" * 64
    elif fault == "chunk_size": value["chunk_bytes"] = archive.MAX_CHUNK_BYTES + 1
    elif fault == "chunk_size_bool": value["chunk_bytes"] = True
    elif fault == "offset": value["chunks"][1]["offset"] += 1
    elif fault == "offset_bool": value["chunks"][0]["offset"] = False
    elif fault == "raw_size": value["chunks"][0]["bytes"] -= 1
    elif fault == "compressed_size": value["chunks"][0]["compressed_bytes"] += 1
    elif fault == "compressed_hash": value["chunks"][0]["compressed_sha256"] = "0" * 64
    elif fault == "raw_hash": value["chunks"][0]["sha256"] = "0" * 64
    elif fault == "path": value["chunks"][0]["file"] = "../private.json.gz"
    elif fault == "order": value["chunks"].reverse()
    elif fault == "missing": value["chunks"].pop()
    elif fault == "summary": value["summary"]["case_status_counts"] = dict(passed=4)
    elif fault == "run_identity": value["summary"]["ordered_run_identity_sha256"] = "0" * 64
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        archive.read_bytes(path)


def test_changed_compressed_object_is_not_reused_or_read(tmp_path):
    path, raw, index = make_archive(tmp_path)
    chunk = path.parent / index["chunks"][0]["file"]
    body = bytearray(chunk.read_bytes())
    body[-1] ^= 1
    chunk.write_bytes(body)
    with pytest.raises(ValueError, match="hash differs"):
        archive.read_bytes(path)
    with pytest.raises(ValueError, match="object changed"):
        archive.archive_bytes(raw, path, chunk_bytes=256)


def test_gzip_expansion_and_total_read_are_bounded(tmp_path):
    path, _, index = make_archive(tmp_path)
    bomb = gzip.compress(b"x" * 2048, mtime=0)
    chunk = index["chunks"][0]
    chunk.update(compressed_sha256=archive.sha(bomb), compressed_bytes=len(bomb),
        file="verification-shards/" + archive.sha(bomb) + ".json.gz")
    (path.parent / chunk["file"]).write_bytes(bomb)
    path.write_text(json.dumps(index))
    with pytest.raises(ValueError, match="raw bytes differ"):
        archive.read_bytes(path)
    with pytest.raises(ValueError, match="read limit|Invalid verification archive index"):
        archive.read_bytes(path, max_bytes=64)


def test_symlink_objects_and_directories_cannot_escape_or_replace_source(tmp_path):
    path, raw, index = make_archive(tmp_path)
    chunk = path.parent / index["chunks"][0]["file"]
    outside = tmp_path / "untouched.gz"
    outside.write_bytes(chunk.read_bytes())
    chunk.unlink()
    chunk.symlink_to(outside)
    with pytest.raises(ValueError, match="escaped"):
        archive.read_bytes(path)
    with pytest.raises(ValueError, match="object changed"):
        archive.archive_bytes(raw, path, chunk_bytes=256)
    assert outside.read_bytes() == gzip.compress(raw[:256], mtime=0)


def test_raw_source_cannot_be_overwritten_as_an_index(tmp_path):
    path = tmp_path / "source.json"
    raw = original_bytes()
    path.write_bytes(raw)
    with pytest.raises(ValueError, match="source separately"):
        archive.archive_bytes(raw, path)
    assert path.read_bytes() == raw


def test_corrupt_history_is_refused_and_no_new_index_replaces_it(tmp_path):
    path, raw, _ = make_archive(tmp_path)
    value = json.loads(raw)
    value["runs"].append(dict(name="new", cases=[]))
    archive.save(path, value)
    before = path.read_bytes()
    prior = json.loads(before)["previous_index"]
    history = path.parent / prior["file"]
    history.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="history identity"):
        archive.read_bytes(path)
    with pytest.raises(ValueError, match="history identity"):
        archive.save(path, dict(value, future=True))
    assert path.read_bytes() == before


def test_recorder_appends_a_real_receipt_without_losing_archived_old_failure(tmp_path):
    args, _, _ = fixture(tmp_path)
    path = args.output
    raw = original_bytes()
    archive.archive_bytes(raw, path)
    with redirect_stdout(io.StringIO()):
        recorder.collect(args)
    value = archive.load(path)
    assert value["runs"][:-1] == json.loads(raw)["runs"]
    new = value["runs"][-1]
    assert new["passed"] == 1 and new["process_terminal_validation"]["exit"] == 0
    assert new["environment_validation"]["verified"]
    assert value["unknown_metadata"] == json.loads(raw)["unknown_metadata"]


def test_abnormal_exit_cannot_be_laundered_by_an_archive_append(tmp_path):
    args, _, terminal = fixture(tmp_path)
    archive.archive_bytes(original_bytes(), args.output)
    before = args.output.read_bytes()
    terminal["exit"] = -11
    args.terminal.write_text(json.dumps(terminal))
    with pytest.raises(ValueError, match="Process terminal exit"):
        recorder.collect(args)
    assert args.output.read_bytes() == before


def test_builder_projection_and_strict_backlog_are_identical_for_both_transports(tmp_path):
    path, raw, _ = make_archive(tmp_path)
    original = json.loads(raw)
    restored = builder.load_json(path)
    assert restored == original
    before = builder.verification_projection(original)
    after = builder.verification_projection(restored)
    assert before == after
    for projection in (before, after):
        for run in projection["runs"]:
            run["source_match"] = False
    assert builder.strict_backlog([], before["runs"]) == builder.strict_backlog([], after["runs"])
    assert archive.read_bytes(path) == raw


@pytest.mark.parametrize("value", [[], {}, dict(runs=None), dict(runs=[False]),
    dict(runs=[], archive_format="nested")])
def test_nonledger_or_nested_archive_cannot_claim_lossless_verification(tmp_path, value):
    with pytest.raises(ValueError, match="ledger|objects"):
        archive.archive_bytes(json.dumps(value).encode(), tmp_path / "index.json")


@pytest.mark.parametrize("size", [True, 0, -1, archive.MAX_CHUNK_BYTES + 1])
def test_invalid_chunk_budgets_are_not_normalized_into_acceptance(tmp_path, size):
    with pytest.raises(ValueError, match="bounded transport"):
        archive.archive_bytes(original_bytes(), tmp_path / "index.json", chunk_bytes=size)


def test_failure_and_later_pass_remain_distinct_observations_after_archiving(tmp_path):
    value = json.loads(original_bytes())
    old = value["runs"][0]
    new = copy.deepcopy(old)
    new.update(name="later-pass", source_fingerprint="newer-source", recorded_at="2026-11-12T00:00:00Z")
    new["cases"][0]["status"] = "passed"
    value["runs"].append(new)
    raw = json.dumps(value).encode()
    path = tmp_path / "index.json"
    archive.archive_bytes(raw, path)
    rows = archive.load(path)["runs"]
    assert rows[0]["cases"][0]["status"] == "failed"
    assert rows[-1]["cases"][0]["status"] == "passed"
    assert rows[0]["recorded_at"] == old["recorded_at"]
    assert rows[-1]["recorded_at"] == new["recorded_at"]
    assert archive.read_bytes(path) == raw
