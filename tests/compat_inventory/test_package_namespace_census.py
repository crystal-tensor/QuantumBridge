"""Namespace inventory is static, includes extension candidates and stays open."""
import importlib.util
import importlib.metadata
from pathlib import Path, PurePosixPath
import sys
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location("namespace_census",
    Path(__file__).parents[2]/"scripts/census_package_namespaces.py")
census = importlib.util.module_from_spec(spec)
spec.loader.exec_module(census)


def test_namespace_files_never_execute_and_private_reexports_stay_pending(tmp_path):
    names = ["fixture/__init__.py", "fixture/public.py", "fixture/_private.py",
             "fixture/tests/test_code.py", "fixture/extension.abi3.so", "fixture/public.pyi"]
    for name in names:
        path = tmp_path/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"raise RuntimeError('SDK module must not execute')\n")
    installed = SimpleNamespace(version="fixture-version", files=list(map(PurePosixPath, names)),
        locate_file=lambda name: tmp_path/name)
    result = census.inventory("fixture", {"fixture"}, ("fixture",), lambda name: installed)
    rows = {row["name"]:row for row in result["modules"]}
    assert len(rows) == 5
    assert rows["fixture"]["runtime_inspected"]
    assert not rows["fixture.public"]["runtime_inspected"]
    assert len(rows["fixture.public"]["files"]) == 2
    assert rows["fixture._private"]["private_path"]
    assert rows["fixture.tests.test_code"]["test_path"]
    assert rows["fixture.extension"]["files"][0]["kind"] == "extension"
    assert result["summary"]["public_path_candidates"] == 3
    assert "fixture" not in sys.modules
    assert result["census_complete"] is False
    assert not any(row["contract_reviewed"] for row in rows.values())


def test_outside_or_malformed_distribution_paths_are_not_read():
    for name in ("../fixture/private.py", "/fixture/private.py", "fixture/../private.py",
                 "other/module.py", "fixture/not-a-module.py", "fixture/data.json"):
        assert census.module_file(name, "fixture") is None


def test_unavailable_packages_and_missing_files_are_not_removed_from_scope(tmp_path):
    def distribution(name):
        if name == "absent":
            raise importlib.metadata.PackageNotFoundError(name)
        return SimpleNamespace(version="fixture", files=[PurePosixPath("present/missing.py")],
            locate_file=lambda name: tmp_path/name)
    result = census.inventory("fixture", set(), ("absent", "present"), distribution)
    assert result["packages"][0]["still_in_scope"]
    assert result["packages"][0]["available"] is False
    assert {row["kind"] for row in result["unresolved"]} == {
        "declared_file_missing", "no_package_module_files_observed"}
