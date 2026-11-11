"""Isolated SDK metadata is not coexistence or Native acceptance."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "runtime_isolation_census", Path(__file__).parents[2]/"scripts/census_runtime_api.py"
)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def part(tmp_path, label, *, identity="shared.function", exit_code=0, profile="fixture", python="3.12.6"):
    data = dict(profile=profile, environment=dict(python=python), modules=[dict(name=label, version="fixed")],
        records=[dict(id=identity, canonical_id=identity, exposures=[label+".alias"], status="unverified",
                      native_mapping=None, contract_reviewed=False)], unresolved=[], closure_pending=["contracts"])
    source = tmp_path/(label+".json.gz")
    source.write_bytes(gzip.compress(json.dumps(data).encode()))
    terminal = tmp_path/(label+"-terminal.json")
    terminal.write_text(json.dumps(dict(profile=profile, isolation=label, terminal=True, exit=exit_code,
        artifact_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), modules=[label])))
    return source, terminal


def test_same_canonical_names_are_kept_separate_without_claiming_cross_process_identity(tmp_path):
    first, second = part(tmp_path, "first"), part(tmp_path, "second")
    result = runtime.merge_isolated_files("fixture", [first, second])
    assert result["census_complete"] is False and result["coexistence_verified"] is False
    assert {row["id"] for row in result["records"]} == {
        "shared.function@isolated-first", "shared.function@isolated-second"}
    assert all(row["canonical_id"] == "shared.function" and row["canonical_identity_review_required"]
               and row["native_mapping"] is None and row["status"] == "unverified" for row in result["records"])
    assert result["unresolved"] == [dict(id="shared.function", kind="cross_process_identity_uncompared",
                                         isolations=["first", "second"])]
    assert len(result["collection_receipts"]) == 2
    assert all(row["exit"] == 0 and len(row["receipt_sha256"]) == 64 for row in result["collection_receipts"])
    assert json.loads(gzip.decompress(first[0].read_bytes()))["records"][0]["id"] == "shared.function"


@pytest.mark.parametrize("exit_code", [-11, 1, False])
def test_written_metadata_from_an_abnormal_or_noninteger_exit_is_rejected(tmp_path, exit_code):
    with pytest.raises(ValueError, match="normal process"):
        runtime.merge_isolated_files("fixture", [part(tmp_path, "first", exit_code=exit_code)])


def test_changed_artifact_or_profile_cannot_reuse_a_normal_receipt(tmp_path):
    pair = part(tmp_path, "first")
    with pytest.raises(ValueError, match="normal process"):
        runtime.merge_isolated_files("other", [pair])
    pair[0].write_bytes(pair[0].read_bytes()+b"changed")
    with pytest.raises(ValueError):
        runtime.merge_isolated_files("fixture", [pair])


def test_different_python_versions_and_overlapping_modules_require_review(tmp_path):
    first = part(tmp_path, "first")
    second = part(tmp_path, "second", python="different")
    with pytest.raises(ValueError, match="Python reference"):
        runtime.merge_isolated_files("fixture", [first, second])
    with pytest.raises(ValueError, match="distinct"):
        runtime.merge_isolated_files("fixture", [first, first])
    source, terminal = part(tmp_path, "third")
    data = json.loads(gzip.decompress(source.read_bytes()))
    data["modules"][0]["name"] = "first"
    source.write_bytes(gzip.compress(json.dumps(data).encode()))
    receipt = json.loads(terminal.read_text())
    receipt.update(modules=["first"], artifact_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    terminal.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="Overlapping module"):
        runtime.merge_isolated_files("fixture", [first, (source, terminal)])


def test_census_cannot_promote_records_to_implementation_acceptance(tmp_path):
    source, terminal = part(tmp_path, "first")
    data = json.loads(gzip.decompress(source.read_bytes()))
    data["records"][0]["status"] = "implemented"
    source.write_bytes(gzip.compress(json.dumps(data).encode()))
    receipt = json.loads(terminal.read_text())
    receipt["artifact_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    terminal.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="Native acceptance"):
        runtime.merge_isolated_files("fixture", [(source, terminal)])
