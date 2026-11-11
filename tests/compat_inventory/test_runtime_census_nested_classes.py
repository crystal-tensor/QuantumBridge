"""Nested public class contracts remain in scope without executing owners."""
import importlib.util
import json
from pathlib import Path
import sys
import types

import pytest

spec = importlib.util.spec_from_file_location("nested_census", Path(__file__).parents[2]/"scripts/census_runtime_api.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def install(monkeypatch, **exports):
    module = types.ModuleType("nested_fixture")
    module.__all__ = list(exports)
    vars(module).update(exports)
    monkeypatch.setitem(sys.modules, module.__name__, module)
    return module


def test_nested_classes_methods_and_aliases_keep_each_public_exposure(monkeypatch):
    class Outer:
        class Inner:
            class Leaf:
                def execute(self, value, /, *, shots=1024):
                    pytest.fail("Nested method executed")
            def __init__(self):
                pytest.fail("Nested constructor executed")
        Alias = Inner
    module = install(monkeypatch, First=Outer, Second=Outer)
    census = runtime.RuntimeCensus("fixture")
    census.module(module.__name__)
    key = runtime.type_name(Outer.Inner.Leaf)+".execute"
    row = census.records[key]
    assert set(row["exposures"]) == {"nested_fixture."+root+".Inner.Leaf.execute"
                                     for root in ("First", "Second")}
    assert row["signature"]["parameters"][1]["kind"] == "POSITIONAL_ONLY"
    assert row["signature"]["parameters"][2]["default"]["value"] == 1024
    assert len(census.class_exports) == 6
    assert census.class_alias_reuses == [dict(exposure="nested_fixture."+root+".Alias",
        owner_class=runtime.type_name(Outer.Inner), expanded_at="nested_fixture."+root+".Inner")
        for root in ("First", "Second")]
    assert set(census.records[runtime.type_name(Outer.Inner)]["exposures"]) == {
        "nested_fixture."+root+"."+alias for root in ("First", "Second") for alias in ("Inner", "Alias")}
    assert all(record["status"] == "unverified" and record["native_mapping"] is None
               for record in census.result()["records"])


def test_inherited_nested_classes_respect_shadowing_and_private_paths(monkeypatch):
    class Base:
        class Shared:
            def run(self):
                pytest.fail("Inherited nested method executed")
        class Replaced:
            def hidden(self):
                pytest.fail("Shadowed nested method executed")
        class _Private:
            pass
    class Child(Base):
        Replaced = None
    install(monkeypatch, Child=Child)
    census = runtime.RuntimeCensus("fixture")
    census.module("nested_fixture")
    edge, = census.class_exports
    assert edge["inherited"] is True
    assert edge["declared_in"] == runtime.type_name(Base)
    assert edge["exposure"] == "nested_fixture.Child.Shared"
    assert census.records[runtime.type_name(Base.Shared)+".run"]["exposures"] == ["nested_fixture.Child.Shared.run"]
    assert runtime.type_name(Base.Replaced) not in census.records
    assert runtime.type_name(Base._Private) not in census.records


def test_class_cycles_are_finite_alias_edges_not_missing_scope(monkeypatch):
    class First:
        def run(self):
            pytest.fail("Cyclic owner executed")
    class Second:
        def other(self):
            pytest.fail("Cyclic child executed")
    First.Child = Second
    Second.Parent = First
    install(monkeypatch, Root=First)
    census = runtime.RuntimeCensus("fixture")
    census.module("nested_fixture")
    result = census.result()
    assert len(result["class_exports"]) == 2
    assert runtime.type_name(First)+".run" in census.records
    assert runtime.type_name(Second)+".other" in census.records
    assert census.records[runtime.type_name(First)]["exposures"] == ["nested_fixture.Root", "nested_fixture.Root.Child.Parent"]
    cycle, = [row for row in result["unresolved"] if row["kind"] == "cyclic_class_alias"]
    assert cycle["id"] == "nested_fixture.Root.Child.Parent" and cycle["still_in_scope"]
    assert result["census_complete"] is False
    json.dumps(result)


def test_depth_cap_records_untraversed_class_and_leaves_it_in_scope(monkeypatch):
    class Root:
        class Child:
            def run(self):
                pytest.fail("Depth-limited child executed")
    install(monkeypatch, Root=Root)
    census = runtime.RuntimeCensus("fixture", max_class_depth=1)
    census.module("nested_fixture")
    assert runtime.type_name(Root.Child) in census.records
    assert runtime.type_name(Root.Child)+".run" not in census.records
    row, = [row for row in census.unresolved if row["kind"] == "nested_class_depth_limit"]
    assert row["id"] == "nested_fixture.Root.Child" and row["still_in_scope"]


@pytest.mark.parametrize("limit", [0, -1, True, 1.5])
def test_invalid_class_depth_limits_are_not_silent_truncation(limit):
    with pytest.raises(ValueError, match="max_class_depth"):
        runtime.RuntimeCensus("fixture", max_class_depth=limit)


def test_failed_nested_signature_cannot_discard_sibling_methods(monkeypatch):
    class BrokenMeta(type):
        @property
        def __signature__(cls):
            raise RuntimeError("private signature value")
    class Outer:
        class Broken(metaclass=BrokenMeta):
            pass
        def valid(self, value):
            pytest.fail("Sibling method executed")
    install(monkeypatch, Root=Outer)
    census = runtime.RuntimeCensus("fixture")
    census.module("nested_fixture")
    assert runtime.type_name(Outer)+".valid" in census.records
    assert any(row["id"] == "nested_fixture.Root.Broken" and row["kind"] == "export_introspection_failed"
               for row in census.unresolved)
    assert "private signature value" not in json.dumps(census.result())


def test_nested_record_limit_is_not_swallowed_as_an_introspection_error(monkeypatch):
    class Outer:
        class Child:
            pass
    install(monkeypatch, Root=Outer)
    census = runtime.RuntimeCensus("fixture", max_records=1)
    with pytest.raises(runtime.CensusLimitError):
        census.module("nested_fixture")


def test_dense_cyclic_class_graph_is_bounded_by_edges_not_alias_permutations(monkeypatch):
    owners = [type("Unit"+str(index), (), {"run": lambda self: pytest.fail("Unit executed")})
              for index in range(8)]
    for owner in owners:
        for index, child in enumerate(owners):
            setattr(owner, "unit"+str(index), child)
    install(monkeypatch, Root=owners[0])
    census = runtime.RuntimeCensus("fixture")
    census.module("nested_fixture")
    assert len(census.class_exports) == 64
    assert len(census.class_alias_reuses) <= 64
    assert all(runtime.type_name(owner)+".run" in census.records for owner in owners)
    assert not any(row["kind"] == "nested_class_depth_limit" for row in census.unresolved)


def test_isolated_union_keeps_nested_edges_with_their_process_identity(tmp_path):
    import gzip
    import hashlib
    from test_runtime_census_isolation import part

    first, second = part(tmp_path, "first"), part(tmp_path, "second")
    edge = dict(owner_class="Owner", attribute="Child", target_class="Owner.Child",
                exposure="first.Owner.Child", declared_in="Owner", inherited=False)
    source, terminal = first
    value = json.loads(gzip.decompress(source.read_bytes()))
    value["class_exports"] = [edge]
    source.write_bytes(gzip.compress(json.dumps(value).encode()))
    receipt = json.loads(terminal.read_text())
    receipt["artifact_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    terminal.write_text(json.dumps(receipt))
    result = runtime.merge_isolated_files("fixture", [first, second])
    assert result["class_exports"] == [dict(collection_isolation="first", **edge)]
    assert result["coexistence_verified"] is False
    assert value["class_exports"] == [edge]
