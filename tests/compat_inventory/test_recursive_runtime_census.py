"""Recursive plans preserve deferred scope and never certify Native parity."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import sys
from types import ModuleType, SimpleNamespace

import pytest

SCRIPTS = Path(__file__).parents[2]/"scripts"
spec = importlib.util.spec_from_file_location("recursive_census", SCRIPTS/"census_recursive_api.py")
recursive = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(SCRIPTS))
try:
    spec.loader.exec_module(recursive)
finally:
    sys.path.pop(0)


def namespace():
    return dict(profile="fixture", packages=[dict(name="fixture", version="1", available=True)],
        modules=[dict(name=name, family="fixture", files=[], private_path=private, test_path=test)
                 for name, private, test in [("fixture", False, False), ("fixture.public", False, False),
                    ("fixture._private", True, False), ("fixture.tests.body", False, True)]])


def test_plan_accounts_for_every_private_test_and_explicit_missing_seed_without_imports():
    plan = recursive.make_plan(namespace(), "fixture", [dict(name="missing_optional", version=None)])
    assert plan["scheduled_modules"] == ["fixture", "fixture.public"]
    assert {row["name"] for row in plan["deferred_modules"]} == {"fixture._private", "fixture.tests.body"}
    assert plan["explicit_seeds"] == [dict(name="missing_optional", version=None)]
    assert plan["census_complete"] is False
    assert "fixture" not in sys.modules


def test_public_module_edges_follow_private_reexports_and_cycles_without_running_methods(monkeypatch):
    root, public, private = [ModuleType(name) for name in ("fixture", "fixture.public", "fixture._private")]
    root.__all__, public.__all__, private.__all__ = ["public"], ["hidden", "again"], ["function"]
    root.public, public.hidden, public.again = public, private, root
    def function(point):
        pytest.fail("Collector executed a function")
    private.function = function
    for module in (root, public, private):
        monkeypatch.setitem(sys.modules, module.__name__, module)
    result = recursive.collect(recursive.make_plan(namespace(), "fixture"))
    traversal = result["traversal"]
    assert set(traversal["attempted_modules"]) == {"fixture", "fixture.public", "fixture._private"}
    assert len(result["modules"]) == 3
    assert traversal["pending_modules"] == []
    assert {row["name"] for row in traversal["deferred_modules"]} == {"fixture.tests.body"}
    assert len(traversal["public_reexport_edges"]) == 3
    assert traversal["public_function_denominator_closed"] is False
    assert all(row["status"] == "unverified" and row["native_mapping"] is None for row in result["records"])


def test_limits_keep_unvisited_and_partially_enumerated_modules_explicit(monkeypatch):
    module = ModuleType("fixture")
    module.__all__ = ["first", "second"]
    module.first = lambda point: point
    module.second = lambda point: point
    monkeypatch.setitem(sys.modules, "fixture", module)
    plan = recursive.make_plan(namespace(), "fixture")
    bounded = recursive.collect(plan, max_modules=1)
    assert bounded["traversal"]["state"] == "MODULE_LIMIT_REACHED"
    assert bounded["traversal"]["pending_modules"] == ["fixture.public"]
    partial = recursive.collect(plan, max_records=1)
    assert partial["traversal"]["state"] == "RECORD_LIMIT_REACHED"
    assert partial["traversal"]["incomplete_module"] == "fixture"
    assert partial["modules"][0]["enumeration_complete"] is False
    assert partial["census_complete"] is False


def test_parent_names_added_by_later_imports_are_explicit_rescan_gaps(monkeypatch):
    root, child = ModuleType("fixture"), ModuleType("fixture.public")
    root.__all__, root.child, child.__all__ = ["child"], child, []
    monkeypatch.setitem(sys.modules, "fixture", root)
    monkeypatch.setitem(sys.modules, "fixture.public", child)
    class LateImport(recursive.RuntimeCensus):
        def module(self, name):
            if name == "fixture.public":
                root.late = lambda point: point
            return super().module(name)
    result = recursive.collect(recursive.make_plan(namespace(), "fixture"), max_export_rescans=0, census_factory=LateImport)
    assert result["traversal"]["namespace_mutations_after_collection"] == [dict(module="fixture",
        added_public_names=["late"], removed_public_names=[], requires_export_rescan=True)]
    assert result["traversal"]["public_function_denominator_closed"] is False


def test_bounded_rescan_captures_late_parent_exports_and_keeps_module_identities_unique(monkeypatch):
    root, child = ModuleType("fixture"), ModuleType("fixture.public")
    root.child, child.__all__ = child, []
    monkeypatch.setitem(sys.modules, "fixture", root)
    monkeypatch.setitem(sys.modules, "fixture.public", child)
    def late(point):
        pytest.fail("Late function executed")
    class LateImport(recursive.RuntimeCensus):
        def module(self, name):
            if name == "fixture.public":
                root.late = late
            return super().module(name)
    result = recursive.collect(recursive.make_plan(namespace(), "fixture"), census_factory=LateImport)
    traversal = result["traversal"]
    assert traversal["namespace_mutations_after_collection"] == []
    assert traversal["export_rescan_passes_completed"] == 1
    assert len(traversal["namespace_mutation_history"]) == 1
    assert any("fixture.late" in row["exposures"] for row in result["records"])
    assert len({row["name"] for row in result["modules"]}) == len(result["modules"])
    assert traversal["public_function_denominator_closed"] is False


def test_import_failures_and_public_test_or_external_exports_are_not_silently_erased(monkeypatch):
    module, private_test, external = [ModuleType(name) for name in ("fixture", "fixture.tests.body", "outside")]
    module.__all__, module.test_body, module.external = ["test_body", "external"], private_test, external
    monkeypatch.setitem(sys.modules, "fixture", module)
    result = recursive.collect(recursive.make_plan(namespace(), "fixture"))
    assert any(row["name"] == "fixture.public" and row["available"] is False for row in result["modules"])
    assert result["traversal"]["deferred_test_exports"][0]["target"] == "fixture.tests.body"
    assert result["traversal"]["external_module_exports"][0]["target"] == "outside"
    assert "outside" not in sys.modules and "fixture.tests.body" not in sys.modules


def test_network_and_cross_sdk_guards_restore_original_process_state():
    before, connect = list(sys.meta_path), socket.create_connection
    with recursive.deny_python_network(), recursive.isolate_family("qiskit") as guard:
        with pytest.raises(RuntimeError, match="forbidden"):
            socket.create_connection(("example.invalid", 443))
        with pytest.raises(recursive.IsolatedSDKImport):
            __import__("pennylane")
        assert guard.blocked == {"pennylane"}
    assert sys.meta_path == before and socket.create_connection is connect


@pytest.mark.parametrize("change", ["version", "bytes", "outside"])
def test_distribution_version_file_hash_and_path_cannot_drift_after_planning(tmp_path, change):
    source = tmp_path/"fixture"/"__init__.py"
    source.parent.mkdir()
    source.write_bytes(b"original bytes")
    plan = recursive.make_plan(namespace(), "fixture")
    plan["namespace_files"] = [dict(file="fixture/__init__.py", sha256=hashlib.sha256(source.read_bytes()).hexdigest())]
    installed = SimpleNamespace(version="1", locate_file=lambda name: tmp_path/name)
    recursive.verify_files(plan, lambda name: installed)
    if change == "version":
        installed.version = "2"
    elif change == "bytes":
        source.write_bytes(b"changed")
    else:
        plan["namespace_files"][0]["file"] = "../outside"
    with pytest.raises(ValueError):
        recursive.verify_files(plan, lambda name: installed)


def test_isolated_merge_preserves_each_traversal_gap_and_original_time(tmp_path):
    module = recursive.RuntimeCensus("fixture")
    value = module.result()
    value["modules"] = [dict(name="fixture", version="1", available=True)]
    value["traversal"] = dict(state="MODULE_LIMIT_REACHED", pending_modules=["fixture.pending"],
        public_function_denominator_closed=False)
    source = tmp_path/"census.json.gz"
    source.write_bytes(gzip.compress(json.dumps(value).encode()))
    terminal = tmp_path/"terminal.json"
    terminal.write_text(json.dumps(dict(profile="fixture", isolation="fixture", terminal=True,
        exit=0, artifact_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), modules=["fixture"])))
    from census_runtime_api import merge_isolated_files
    merged = merge_isolated_files("fixture", [(source, terminal)])
    assert merged["traversal_audits"] == [dict(isolation="fixture", **value["traversal"])]
    assert merged["census_complete"] is False and merged["coexistence_verified"] is False


@pytest.mark.parametrize("mismatch", ["version", "origin", "bytes"])
def test_loaded_sdk_cannot_shadow_metadata_with_another_version_or_source(tmp_path, monkeypatch, mismatch):
    source = tmp_path/"fixture"/"__init__.py"
    source.parent.mkdir()
    source.write_bytes(b"fixed SDK bytes")
    module = ModuleType("fixture")
    module.__version__, module.__file__ = "1", str(source)
    monkeypatch.setitem(sys.modules, "fixture", module)
    plan = recursive.make_plan(namespace(), "fixture")
    plan["namespace_files"] = [dict(module="fixture", file="fixture/__init__.py",
        sha256=hashlib.sha256(source.read_bytes()).hexdigest())]
    installed = SimpleNamespace(version="1", locate_file=lambda name: tmp_path/name)
    assert recursive.verify_loaded_family(plan, lambda name: installed)["import_identity_verified"]
    if mismatch == "version":
        module.__version__ = "2"
    elif mismatch == "origin":
        other = tmp_path/"other.py"
        other.write_bytes(source.read_bytes())
        module.__file__ = str(other)
    else:
        source.write_bytes(b"changed bytes")
    with pytest.raises(ValueError, match="Loaded SDK identity"):
        recursive.verify_loaded_family(plan, lambda name: installed)


@pytest.mark.parametrize("right_versions", [{"numpy": "other"}, None])
def test_isolated_collections_cannot_mix_different_or_missing_dependency_snapshots(tmp_path, right_versions):
    pairs = []
    for label, versions in [("first", {"numpy": "fixed"}), ("second", right_versions)]:
        environment = dict(python="3.12")
        if versions is not None:
            environment["distribution_versions"] = versions
        value = dict(profile="fixture", environment=environment, modules=[dict(name=label)],
            records=[], unresolved=[], closure_pending=[])
        source, terminal = tmp_path/(label+".json.gz"), tmp_path/(label+".terminal.json")
        source.write_bytes(gzip.compress(json.dumps(value).encode()))
        terminal.write_text(json.dumps(dict(profile="fixture", isolation=label, terminal=True, exit=0,
            artifact_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), modules=[label])))
        pairs.append((source, terminal))
    from census_runtime_api import merge_isolated_files
    with pytest.raises(ValueError, match="dependency metadata"):
        merge_isolated_files("fixture", pairs)
