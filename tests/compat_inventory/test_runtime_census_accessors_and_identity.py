"""Public access protocols and dynamic identities are metadata, not execution."""
from functools import cached_property
import gc
import importlib.util
import json
from pathlib import Path
import sys
import types
import weakref

import pytest

spec = importlib.util.spec_from_file_location("accessor_census", Path(__file__).parents[2]/"scripts/census_runtime_api.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def installed(monkeypatch, name, **exports):
    module = types.ModuleType(name)
    module.__all__ = list(exports)
    vars(module).update(exports)
    monkeypatch.setitem(sys.modules, name, module)
    return module


def test_inherited_property_read_write_delete_keep_distinct_contracts_and_aliases(monkeypatch):
    class Base:
        @property
        def angle(self):
            pytest.fail("Getter executed")
        @angle.setter
        def angle(self, value):
            pytest.fail("Setter executed")
        @angle.deleter
        def angle(self):
            pytest.fail("Deleter executed")
    class Child(Base):
        pass
    installed(monkeypatch, "accessor_fixture", First=Child, Alias=Child)
    census = runtime.RuntimeCensus("fixture")
    census.module("accessor_fixture")
    owner = runtime.type_name(Child)+".angle"
    for suffix, kind, accessor in [("", "property", "get"), ("@set", "property_setter", "set"),
                                   ("@delete", "property_deleter", "delete")]:
        row = census.records[owner+suffix]
        assert row["kind"] == kind and row["accessor"] == accessor and row["inherited"]
        assert row["declared_in"] == runtime.type_name(Base)
        assert set(row["exposures"]) == {"accessor_fixture.First.angle", "accessor_fixture.Alias.angle"}
    assert [parameter["name"] for parameter in census.records[owner+"@set"]["signature"]["parameters"]] == ["self", "value"]
    assert all(row["status"] == "unverified" and row["native_mapping"] is None for row in census.result()["records"])


def test_write_only_property_is_not_dropped_because_it_has_no_getter(monkeypatch):
    class Owner:
        def set_value(self, value):
            pytest.fail("Setter executed")
        value = property(fset=set_value)
    installed(monkeypatch, "write_only_fixture", Owner=Owner)
    census = runtime.RuntimeCensus("fixture")
    census.module("write_only_fixture")
    key = runtime.type_name(Owner)+".value"
    assert key not in census.records
    assert census.records[key+"@set"]["accessor"] == "set"


def test_read_only_and_cached_properties_are_not_evaluated_or_given_fake_setters(monkeypatch):
    class Owner:
        @property
        def readonly(self):
            pytest.fail("Readonly property executed")
        @cached_property
        def cached(self):
            pytest.fail("Cached property executed")
    installed(monkeypatch, "cached_property_fixture", Owner=Owner)
    census = runtime.RuntimeCensus("fixture")
    census.module("cached_property_fixture")
    owner = runtime.type_name(Owner)
    assert census.records[owner+".readonly"]["accessor"] == "get"
    assert owner+".readonly@set" not in census.records
    assert census.records[owner+".cached"]["kind"] == "cached_property"
    assert census.records[owner+".cached"]["accessor"] == "get"


def test_ephemeral_dynamic_objects_stay_alive_until_identity_comparison_finishes(monkeypatch):
    references = []
    module = types.ModuleType("dynamic_identity_fixture")
    def lookup(name):
        if name not in {"First", "Second", "Third"}:
            raise AttributeError(name)
        def exported(point):
            pytest.fail("Dynamic function executed")
        references.append(weakref.ref(exported))
        return exported
    module.__getattr__ = lookup
    module.__dir__ = lambda: ["First", "Second", "Third"]
    monkeypatch.setitem(sys.modules, module.__name__, module)
    census = runtime.RuntimeCensus("fixture")
    census.module(module.__name__)
    assert len(references) == 3 and all(reference() is not None for reference in references)
    assert len(census.records) == 3
    assert len({row["canonical_id"] for row in census.records.values()}) == 1
    json.dumps(census.result())
    del census
    gc.collect()
    assert all(reference() is None for reference in references)


def test_one_failed_introspection_cannot_drop_the_rest_of_a_module(monkeypatch):
    class Opaque:
        @property
        def __signature__(self):
            raise RuntimeError("do not disclose this private value")
        def __call__(self):
            pytest.fail("Opaque callable executed")
    def available(point):
        pytest.fail("Function executed")
    installed(monkeypatch, "partial_introspection_fixture", First=Opaque(), Second=available)
    census = runtime.RuntimeCensus("fixture")
    census.module("partial_introspection_fixture")
    result = census.result()
    assert result["modules"][0]["available"] is True
    assert any("partial_introspection_fixture.Second" in row["exposures"] for row in result["records"])
    assert any(row["id"] == "partial_introspection_fixture.First" and row["kind"] == "export_introspection_failed"
               for row in result["unresolved"])
    assert "private value" not in json.dumps(result)


def test_extension_children_keep_an_enclosing_binary_hash_without_inventing_python_source(tmp_path, monkeypatch):
    family = tmp_path/"binary_fixture"
    family.mkdir()
    package_file, binary_file = family/"__init__.py", family/"_extension.fake.so"
    package_file.write_bytes(b"package metadata")
    binary_file.write_bytes(b"not executable; fingerprint fixture only")
    package = installed(monkeypatch, "binary_fixture")
    package.__file__ = str(package_file)
    extension = installed(monkeypatch, "binary_fixture._extension")
    extension.__file__ = str(binary_file)
    installed(monkeypatch, "binary_fixture._extension.inner")
    class Owner:
        pass
    Owner.__module__ = "binary_fixture._extension.inner"
    census = runtime.RuntimeCensus("fixture")
    origin = census.source(Owner, "binary_fixture")
    import hashlib
    assert origin == dict(file="binary_fixture/_extension.fake.so",
        source_hash=hashlib.sha256(binary_file.read_bytes()).hexdigest(), source_hash_scope="ancestor_module_file")


def test_foreign_reexports_remain_tagged_metadata_not_assumed_sdk_implementations(monkeypatch):
    def external(point):
        pytest.fail("Foreign function executed")
    installed(monkeypatch, "foreign_export_fixture", Alias=external)
    census = runtime.RuntimeCensus("fixture")
    census.module("foreign_export_fixture")
    row, = census.result()["records"]
    assert row["declaration_module"] == __name__
    assert row["declared_in_reference_namespace"] is False
    assert row["status"] == "unverified" and row["native_mapping"] is None


@pytest.mark.parametrize("missing", ["safe.missing", "/Users/private/token"])
def test_import_dependency_names_are_recorded_without_raw_exception_or_private_paths(monkeypatch, missing):
    def absent(name):
        raise ModuleNotFoundError("private exception message", name=missing)
    monkeypatch.setattr(runtime.importlib, "import_module", absent)
    census = runtime.RuntimeCensus("fixture")
    census.module("missing_fixture")
    row, = census.modules
    assert row["available"] is False
    assert row.get("missing_module") == (missing if missing == "safe.missing" else None)
    assert "private" not in json.dumps(census.result())


def test_repeated_lazy_export_path_keeps_each_distinct_observation_instead_of_merging_defaults(monkeypatch):
    module = installed(monkeypatch, "repeated_lazy_fixture")
    module.__all__ = ["Function"]
    values = iter((1, 2, 3))
    def lookup(name):
        if name != "Function":
            raise AttributeError(name)
        def function(point=next(values)):
            pytest.fail("Lazy function executed")
        return function
    module.__getattr__ = lookup
    census = runtime.RuntimeCensus("fixture")
    for _ in range(3):
        census.module(module.__name__)
    rows = list(census.records.values())
    assert len(rows) == 3
    assert {row["signature"]["parameters"][0]["default"]["value"] for row in rows} == {1, 2, 3}
    assert all(row["canonical_identity_review_required"] for row in rows)
