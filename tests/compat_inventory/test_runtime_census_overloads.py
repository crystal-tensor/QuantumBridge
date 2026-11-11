"""Declared overloads and type trees are metadata, not execution contracts."""
import collections.abc
import importlib.util
import inspect
import json
from pathlib import Path
import sys
import types
import typing

import pytest

spec = importlib.util.spec_from_file_location("overload_census", Path(__file__).parents[2]/"scripts/census_runtime_api.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def test_public_overloads_keep_positional_keyword_defaults_and_annotations(monkeypatch):
    @typing.overload
    def execute(value: int, /) -> int:
        pytest.fail("Overload body executed")
    @typing.overload
    def execute(value: str, /, *, shots: int = 1024) -> list[str]:
        pytest.fail("Overload body executed")
    def execute(value, /, *, shots=1024):
        pytest.fail("Implementation executed")
    module = types.ModuleType("overload_fixture")
    module.First = module.Alias = execute
    monkeypatch.setitem(sys.modules, module.__name__, module)
    census = runtime.RuntimeCensus("fixture")
    census.module(module.__name__)
    row, = census.result()["records"]
    signature = row["signature"]
    assert len(signature["overloads"]) == 2
    assert signature["overload_registry_identity_verified"] is False
    first, second = signature["overloads"]
    assert first["parameters"][0]["kind"] == "POSITIONAL_ONLY"
    assert first["parameters"][0]["annotation_schema"] == dict(kind="class", id="builtins.int")
    assert second["parameters"][1]["kind"] == "KEYWORD_ONLY"
    assert second["parameters"][1]["default"]["value"] == 1024
    assert second["return_annotation_schema"] == dict(kind="generic", origin=dict(kind="class", id="builtins.list"),
        arguments=[dict(kind="class", id="builtins.str")])
    assert set(row["exposures"]) == {"overload_fixture.First", "overload_fixture.Alias"}
    assert row["status"] == "unverified" and row["native_mapping"] is None


def test_nested_generic_callable_and_union_annotations_keep_structure():
    def execute(value: dict[str, tuple[int, ...]],
                callback: typing.Callable[[int, str], bool]) -> int | None:
        pytest.fail("Typed function executed")
    signature = runtime.signature(execute)
    mapping, callback = [row["annotation_schema"] for row in signature["parameters"]]
    assert mapping["origin"]["id"] == "builtins.dict"
    assert mapping["arguments"][1]["arguments"][1] == dict(kind="ellipsis")
    assert callback["origin"]["id"] == "collections.abc.Callable"
    assert callback["arguments"][0]["kind"] == "parameter_list"
    assert callback["arguments"][0]["arguments"] == [dict(kind="class", id="builtins.int"), dict(kind="class", id="builtins.str")]
    assert signature["return_annotation_schema"]["origin"]["id"] == "types.UnionType"


def test_literal_annotated_and_forward_references_are_never_evaluated(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Forward annotation evaluated")
    monkeypatch.setattr(typing, "get_type_hints", forbidden)
    def execute(value: typing.Annotated[typing.Literal["read", "write"], "mode"],
                later: "forbidden()") -> typing.ForwardRef("forbidden()"):
        pytest.fail("Annotated implementation executed")
    signature = runtime.signature(execute)
    annotated = signature["parameters"][0]["annotation_schema"]
    assert annotated["origin"]["id"] == "typing.Annotated"
    assert annotated["arguments"][0]["origin"]["id"] == "typing.Literal"
    assert [row["value"]["value"] for row in annotated["arguments"][0]["arguments"]] == ["read", "write"]
    assert signature["parameters"][1]["annotation_schema"]["kind"] == "string"
    assert signature["return_annotation_schema"]["kind"] == "forward_reference"
    assert signature["return_annotation_schema"]["review_required"] is True


def test_type_variables_keep_names_and_variance_without_evaluating_bounds():
    bounded = typing.TypeVar("bounded", bound=int, covariant=True)
    constrained = typing.TypeVar("constrained", str, bytes)
    schema = runtime.annotation_schema(bounded)
    assert schema["kind"] == "type_variable" and schema["covariant"]
    assert schema["name"] == "bounded" and schema["bounds_review_required"]
    assert runtime.annotation_schema(constrained)["name"] == "constrained"
    if sys.version_info >= (3, 12):
        def forbidden():
            pytest.fail("Lazy type bound evaluated")
        namespace = dict(forbidden=forbidden)
        exec("def generic[T: forbidden()](point: T) -> T: pass", namespace)
        assert runtime.signature(namespace["generic"])["parameters"][0]["annotation_schema"]["bounds_review_required"]


@pytest.mark.parametrize("value", [847291, .918273, True, "hidden-credential"])
def test_sensitive_defaults_are_redacted_for_every_primitive_type(value):
    def execute(api_key=value):
        pytest.fail("Sensitive function executed")
    default = runtime.signature(execute)["parameters"][0]["default"]
    assert default["present"] and not default["literal"] and "value" not in default
    assert runtime.literal(None, "api_key") == dict(present=True, literal=True, value=None)


def test_unknown_annotations_and_nonliteral_defaults_never_call_repr():
    class Opaque:
        def __repr__(self):
            pytest.fail("Opaque metadata repr executed")
    value = Opaque()
    def execute(point: value = value) -> value:
        pytest.fail("Opaque annotated implementation executed")
    signature = runtime.signature(execute)
    assert signature["parameters"][0]["annotation_schema"]["kind"] == "opaque"
    assert signature["parameters"][0]["default"]["review_required"]
    assert signature["return_annotation_schema"]["review_required"]
    json.dumps(signature)


def test_deep_and_cyclic_annotations_stop_with_explicit_review_not_recursion():
    value = int
    for _ in range(30):
        value = list[value]
    deep = runtime.annotation_schema(value)
    assert "depth_limit" in json.dumps(deep)
    loop = []
    loop.append(loop)
    assert "cycle" in json.dumps(runtime.annotation_schema(loop))


def test_inherited_overloaded_methods_are_not_erased_by_class_binding(monkeypatch):
    class Base:
        @typing.overload
        def sample(self, value: int) -> int: ...
        @typing.overload
        def sample(self, value: str) -> str: ...
        def sample(self, value):
            pytest.fail("Inherited overloaded method executed")
    class Child(Base):
        pass
    module = types.ModuleType("inherited_overload_fixture")
    module.Child = Child
    monkeypatch.setitem(sys.modules, module.__name__, module)
    census = runtime.RuntimeCensus("fixture")
    census.module(module.__name__)
    row = census.records[runtime.type_name(Child)+".sample"]
    assert row["inherited"] and len(row["signature"]["overloads"]) == 2


def test_overload_cardinality_cap_is_explicit_and_preserves_runtime_signature(monkeypatch):
    def execute(value=1):
        pytest.fail("Function executed")
    monkeypatch.setattr(typing, "get_overloads", lambda function: [execute]*70)
    signature = runtime.signature(execute)
    assert signature["available"] and signature["parameters"][0]["default"]["value"] == 1
    assert len(signature["overloads"]) == 64 and signature["overload_review_required"]
    assert signature["overload_observed_count"] == 70 and signature["overload_limit_reached"]
