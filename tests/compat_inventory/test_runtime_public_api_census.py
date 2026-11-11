"""Runtime inventories preserve inherited contracts without invoking methods."""
import importlib.util
from pathlib import Path
import socket
import sys
import types

import pytest

spec = importlib.util.spec_from_file_location("runtime_census", Path(__file__).parents[2] / "scripts/census_runtime_api.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def test_aliases_inherited_methods_properties_and_protocols_are_not_omitted(monkeypatch):
    class Base:
        def inherited(self, point, /, *, shots=1024):
            pytest.fail("Inventory called a method")
        @property
        def forbidden(self):
            pytest.fail("Inventory evaluated a property")
        def __call__(self, point):
            pytest.fail("Inventory instantiated or called an object")
    class Child(Base):
        @staticmethod
        def local(value=None):
            pytest.fail("Inventory called static code")
    module = types.ModuleType("census_fixture")
    module.__all__ = ["First", "Alias", "Missing"]
    module.First = module.Alias = Child
    def dynamic(name):
        if name == "Dynamic":
            return Base
        raise AttributeError(name)
    module.__getattr__ = dynamic
    module.__dir__ = lambda: ["Dynamic", "First", "Alias", "Missing"]
    monkeypatch.setitem(sys.modules, "census_fixture", module)
    census = runtime.RuntimeCensus("fixture")
    census.module("census_fixture")
    result = census.result()
    row = census.records[runtime.type_name(Child)+".inherited"]
    assert row["inherited"] and row["declared_in"] == runtime.type_name(Base)
    assert set(row["exposures"]) == {"census_fixture.First.inherited", "census_fixture.Alias.inherited"}
    assert row["signature"]["parameters"][1]["kind"] == "POSITIONAL_ONLY"
    assert row["signature"]["parameters"][2]["default"]["value"] == 1024
    assert census.records[runtime.type_name(Child)+".forbidden"]["kind"] == "property"
    assert runtime.type_name(Child)+".__call__" in census.records
    assert any(x["id"] == "census_fixture.Missing" for x in result["unresolved"])
    assert result["census_complete"] is False
    assert all(r["status"] == "unverified" and r["native_mapping"] is None for r in result["records"])


def test_nonliteral_defaults_never_invoke_repr_or_dump_secret_values():
    class Secret:
        def __repr__(self):
            pytest.fail("Inventory invoked arbitrary repr")
    def function(value=Secret(), token="private", path="/home/private/data"):
        pass
    parameters = runtime.signature(function)["parameters"]
    assert all(p["default"]["literal"] is False for p in parameters)
    assert all("value" not in p["default"] for p in parameters)


def test_missing_modules_remain_explicitly_in_scope():
    census = runtime.RuntimeCensus("fixture")
    census.module("quantumbridge_missing_census_package")
    assert census.modules[0]["available"] is False
    assert census.modules[0]["still_in_scope"] is True


def test_network_guard_denies_and_restores_python_socket_calls():
    original = socket.create_connection
    with runtime.deny_python_network(), pytest.raises(RuntimeError, match="forbidden"):
        socket.create_connection(("example.invalid", 443))
    assert socket.create_connection is original


def test_distinct_factory_closures_are_not_collapsed_into_a_single_function(monkeypatch):
    def factory():
        def exported(point):
            pytest.fail("Inventory invoked a factory export")
        return exported
    module = types.ModuleType("census_closures")
    module.First = module.Alias = factory()
    module.Second = module.OtherAlias = factory()
    monkeypatch.setitem(sys.modules, "census_closures", module)
    census = runtime.RuntimeCensus("fixture")
    census.module("census_closures")
    rows = list(census.records.values())
    assert len(rows) == 2
    assert len({row["canonical_id"] for row in rows}) == 1
    assert all(len(row["exposures"]) == 2 for row in rows)
    assert all(row["canonical_identity_review_required"] for row in rows)
    assert len(census.unresolved) == 1
