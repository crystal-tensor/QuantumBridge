#!/usr/bin/env python3
"""Public export/MRO metadata only; never an implementation acceptance claim."""
import argparse
import copy
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import cached_property
import hashlib
import importlib
import importlib.metadata
import inspect
import json
import math
import gzip
from pathlib import Path
import platform
import socket
import sys
import types
import typing


def type_name(value):
    cls = value if isinstance(value, type) else type(value)
    return type.__getattribute__(cls, "__module__")+"."+type.__getattribute__(cls, "__qualname__")


def literal(value, parameter=""):
    if value is inspect.Parameter.empty:
        return {"present": False}
    secret = any(word in parameter.lower() for word in ("token", "password", "secret", "credential", "api_key"))
    if value is not None and secret:
        return {"present": True, "literal": False, "type": type_name(value), "review_required": True}
    if value is None or type(value) in (bool, int) or type(value) is float and math.isfinite(value):
        return {"present": True, "literal": True, "value": value}
    if type(value) is str and not secret and len(value) <= 200 and not value.startswith(("/", "~")):
        return {"present": True, "literal": True, "value": value}
    return {"present": True, "literal": False, "type": type_name(value), "review_required": True}


def annotation_schema(value, parameter="", *, _active=(), _budget=None):
    budget = [128] if _budget is None else _budget
    budget[0] -= 1
    if budget[0] < 0 or len(_active) >= 12:
        return dict(kind="unresolved", reason="depth_limit" if len(_active) >= 12 else "node_limit", review_required=True)
    if any(value is parent for parent in _active):
        return dict(kind="unresolved", reason="cycle", review_required=True)
    if value is inspect.Parameter.empty:
        return dict(kind="empty")
    if value is None:
        return dict(kind="none")
    if value is Ellipsis:
        return dict(kind="ellipsis")
    if type(value) is str:
        return dict(kind="string", value=literal(value, parameter), review_required=True)
    if isinstance(value, typing.ForwardRef):
        return dict(kind="forward_reference", value=literal(value.__forward_arg__, parameter), review_required=True)
    for name in ("TypeVar", "ParamSpec", "TypeVarTuple", "TypeAliasType"):
        cls = getattr(typing, name, None)
        if isinstance(cls, type) and isinstance(value, cls):
            # PEP 695 bounds, constraints and alias values can execute code
            # when read. Names/variance are metadata, not resolved bounds.
            return dict(kind="type_variable" if name != "TypeAliasType" else "type_alias",
                name=value.__name__, covariant=bool(getattr(value, "__covariant__", False)),
                contravariant=bool(getattr(value, "__contravariant__", False)),
                bounds_review_required=True, review_required=True)
    for name in ("Union", "Literal", "Annotated", "ClassVar", "Final", "Required", "NotRequired",
                 "Unpack", "Concatenate", "TypeGuard", "Self", "NoReturn", "Never", "Any", "LiteralString"):
        if value is getattr(typing, name, None):
            return dict(kind="typing", id="typing."+name)
    if isinstance(value, type):
        return dict(kind="class", id=type_name(value))
    active = (*_active, value)
    describe = lambda child: annotation_schema(child, parameter, _active=active, _budget=budget)
    if type(value) in (list, tuple):
        return dict(kind="parameter_list", arguments=[describe(child) for child in value[:64]],
                    **({"review_required": True, "reason": "argument_limit"} if len(value) > 64 else {}))
    origin, args = typing.get_origin(value), typing.get_args(value)
    if origin is not None:
        arguments = []
        for index, child in enumerate(args[:64]):
            if origin is typing.Literal or origin is typing.Annotated and index > 0:
                arguments.append(dict(kind="literal", value=literal(child, parameter)))
            else:
                arguments.append(describe(child))
        return dict(kind="generic", origin=describe(origin), arguments=arguments,
                    **({"review_required": True, "reason": "argument_limit"} if len(args) > 64 else {}))
    return dict(kind="opaque", type=type_name(value), review_required=True)


def signature(value, *, _overloads=True):
    try:
        sig = inspect.signature(value, eval_str=False)
        parameters = [{"name": p.name, "kind": p.kind.name, "default": literal(p.default, p.name),
                       "annotation": literal(p.annotation),
                       **({"annotation_schema": annotation_schema(p.annotation, p.name)}
                          if p.annotation is not inspect.Parameter.empty else {})} for p in sig.parameters.values()]
        result = {"available": True, "parameters": parameters, "return_annotation": literal(sig.return_annotation)}
        if sig.return_annotation is not inspect.Signature.empty:
            result["return_annotation_schema"] = annotation_schema(sig.return_annotation)
    except (TypeError, ValueError) as error:
        result = {"available": False, "reason": type(error).__name__, "review_required": True}
    if _overloads:
        try:
            overloads = typing.get_overloads(value)
            if overloads:
                result.update(overloads=[signature(function, _overloads=False) for function in overloads[:64]],
                    overload_observed_count=len(overloads), overload_limit_reached=len(overloads) > 64,
                    overload_registry_identity_verified=False, overload_review_required=True,
                    overload_source="typing_runtime_registry_not_executed_contract")
        except Exception as error:
            result.update(overload_review_required=True, overload_error=type(error).__name__)
    return result


@contextmanager
def deny_python_network():
    def denied(*args, **kwargs):
        raise RuntimeError("Network access is forbidden during API metadata enumeration")
    original = (socket.socket.connect, socket.create_connection, socket.getaddrinfo)
    socket.socket.connect = socket.create_connection = socket.getaddrinfo = denied
    try:
        yield
    finally:
        socket.socket.connect, socket.create_connection, socket.getaddrinfo = original


class CensusLimitError(RuntimeError):
    """Metadata cardinality limit; never a claim that the API scope ended."""


class RuntimeCensus:
    def __init__(self, profile, *, max_records=None, max_class_depth=64):
        if max_records is not None and (type(max_records) is not int or max_records < 1):
            raise ValueError("max_records must be a positive integer or None")
        if type(max_class_depth) is not int or max_class_depth < 1:
            raise ValueError("max_class_depth must be a positive integer")
        self.max_records = max_records
        self.max_class_depth = max_class_depth
        self.profile, self.records, self.identities = profile, {}, {}
        self.canonical_objects = {}
        self.modules, self.unresolved, self.files = [], [], {}
        self.class_exports = []
        self.class_alias_reuses = []

    def source(self, value, family):
        try:
            filename = inspect.getsourcefile(value)
        except TypeError:
            filename = None
        defining = getattr(value, "__module__", None)
        if not isinstance(defining, str):
            owner = getattr(value, "__objclass__", None)
            defining = type.__getattribute__(owner, "__module__") if isinstance(owner, type) else None
        package = sys.modules.get(family)
        package_file = None if package is None else vars(package).get("__file__")
        if not package_file:
            return {"file": None, "source_hash": None}
        candidates = [(filename, "definition_file")]
        if isinstance(defining, str) and (defining == family or defining.startswith(family+".")):
            parts = defining.split(".")
            for end in range(len(parts), 0, -1):
                module = sys.modules.get(".".join(parts[:end]))
                if module is not None:
                    candidates.append((vars(module).get("__file__"), "module_file" if end == len(parts) else "ancestor_module_file"))
        base = Path(package_file).resolve().parent
        for filename, kind in candidates:
            if not filename:
                continue
            path = Path(filename).resolve()
            if not path.is_file() or not path.is_relative_to(base):
                continue
            if path not in self.files:
                self.files[path] = hashlib.sha256(path.read_bytes()).hexdigest()
            return {"file": str(Path(family)/path.relative_to(base)), "source_hash": self.files[path],
                    "source_hash_scope": kind}
        return {"file": None, "source_hash": None}

    def record(self, key, kind, value, exposure, family, **extra):
        canonical = key
        identity = (canonical, id(value))
        if identity in self.canonical_objects:
            key = self.canonical_objects[identity]
        elif key in self.records and self.identities[key] is not value:
            self.unresolved.append({"id": key, "kind": "canonical_identity_collision", "exposure": exposure})
            self.records[key]["canonical_identity_review_required"] = True
            key += "@"+exposure
            base, observation = key, 2
            while key in self.records and self.identities[key] is not value:
                key = base+"@observation-"+str(observation)
                observation += 1
            extra["canonical_identity_review_required"] = True
        if key in self.records:
            row = self.records[key]
            if exposure not in row["exposures"]:
                row["exposures"].append(exposure)
            return
        if self.max_records is not None and len(self.records) >= self.max_records:
            raise CensusLimitError("max_records")
        defining = getattr(value, "__module__", None)
        row = {"id": key, "canonical_id": canonical, "kind": kind, "family": family, "exposures": [exposure],
            "declaration_module": defining if isinstance(defining, str) else None,
            "declared_in_reference_namespace": (defining == family or defining.startswith(family+".")) if isinstance(defining, str) else None,
            "signature": signature(value), **self.source(value, family), **extra,
            "status": "unverified", "native_mapping": None, "contract_reviewed": False}
        # An address alone is not an identity once a lazy export is collected.
        # Keep each observed object alive until the metadata process finishes.
        self.identities[key] = value
        self.canonical_objects[identity] = key
        self.records[key] = row

    def class_members(self, cls, exposure, family, *, _active=(), _expanded=None):
        owner = type_name(cls)
        mro = type.__getattribute__(cls, "__mro__")
        self.record(owner, "class", cls, exposure, family, mro=[type_name(c) for c in mro])
        reason = ("cyclic_class_alias" if any(cls is active for active in _active) else
                  "nested_class_depth_limit" if len(_active) >= self.max_class_depth else None)
        if reason is not None:
            row = dict(id=exposure, kind=reason, owner_class=owner, still_in_scope=True)
            if row not in self.unresolved:
                self.unresolved.append(row)
            return
        if _expanded is None:
            _expanded = {}
        if id(cls) in _expanded:
            # Class graphs can be cyclic or have exponentially many alias
            # paths. Preserve edges instead of materializing their language.
            row = dict(exposure=exposure, owner_class=owner, expanded_at=_expanded[id(cls)])
            if row not in self.class_alias_reuses:
                self.class_alias_reuses.append(row)
            return
        _expanded[id(cls)] = exposure
        active = (*_active, cls)
        seen = set()
        for base in mro:
            for name, descriptor in type.__getattribute__(base, "__dict__").items():
                if name in seen:
                    continue
                seen.add(name)
                if name.startswith("_") and not (name.startswith("__") and name.endswith("__")):
                    continue
                if isinstance(descriptor, type):
                    edge = dict(owner_class=owner, attribute=name, exposure=exposure+"."+name,
                        target_class=type_name(descriptor), declared_in=type_name(base), inherited=base is not cls)
                    if edge not in self.class_exports:
                        self.class_exports.append(edge)
                    try:
                        self.class_members(descriptor, edge["exposure"], family,
                                           _active=active, _expanded=_expanded)
                    except CensusLimitError:
                        raise
                    except Exception as error:
                        self.unresolved.append(dict(id=edge["exposure"], kind="export_introspection_failed",
                            error=type(error).__name__, still_in_scope=True))
                    continue
                extra = {}
                if isinstance(descriptor, (staticmethod, classmethod)):
                    value, kind = descriptor.__func__, type(descriptor).__name__
                elif isinstance(descriptor, property):
                    for accessor, value in (("get", descriptor.fget), ("set", descriptor.fset),
                                            ("delete", descriptor.fdel)):
                        if value is None:
                            continue
                        suffix = "" if accessor == "get" else "@"+accessor
                        kind = {"get": "property", "set": "property_setter", "delete": "property_deleter"}[accessor]
                        self.record(owner+"."+name+suffix, kind, value, exposure+"."+name, family,
                            owner_class=owner, declared_in=type_name(base), inherited=base is not cls,
                            accessor=accessor)
                    continue
                elif type(descriptor) is cached_property:
                    value, kind, extra = descriptor.func, "cached_property", {"accessor": "get"}
                elif inspect.isgetsetdescriptor(descriptor) or inspect.ismemberdescriptor(descriptor):
                    value, kind = descriptor, "property"
                elif inspect.isroutine(descriptor):
                    value, kind = descriptor, "method"
                else:
                    continue
                if value is None:
                    continue
                self.record(owner+"."+name, kind, value, exposure+"."+name, family,
                    owner_class=owner, declared_in=type_name(base), inherited=base is not cls, **extra)

    def module(self, name):
        family = name.split(".")[0]
        try:
            version = importlib.metadata.version(family.replace("_", "-"))
        except importlib.metadata.PackageNotFoundError:
            version = None
        try:
            module = importlib.import_module(name)
        except Exception as error:
            row = {"name": name, "version": version, "available": False,
                   "error": type(error).__name__, "still_in_scope": True}
            missing = getattr(error, "name", None)
            if isinstance(missing, str) and all(part.isidentifier() for part in missing.split(".")):
                row["missing_module"] = missing
            self.modules.append(row)
            return
        declared = vars(module).get("__all__")
        dictionary_names = sorted(name for name in vars(module) if not name.startswith("_"))
        if declared is not None:
            names = set(declared)
            policy = "declared_all"
        else:
            names = {n for n in vars(module) if not n.startswith("_")}
            policy = "public_dictionary_and_dir_candidates"
        try:
            advertised = {n for n in dir(module) if not n.startswith("_")}
        except Exception as error:
            advertised = set()
            self.unresolved.append({"id": name, "kind": "dir_failed", "error": type(error).__name__})
        dynamic = advertised-set(vars(module))
        names.update(dynamic)
        children, constants = [], []
        if any(not isinstance(exported, str) for exported in names):
            self.unresolved.append({"id": name, "kind": "non_string_export"})
        names = {exported for exported in names if isinstance(exported, str)}
        for exported in sorted(names):
            exposure = name+"."+exported
            try:
                value = getattr(module, exported)
            except Exception as error:
                self.unresolved.append({"id": exposure, "kind": "export_resolution_failed", "error": type(error).__name__})
                continue
            try:
                if isinstance(value, types.ModuleType):
                    children.append({"exposure": exposure, "module": vars(value).get("__name__")})
                elif isinstance(value, type):
                    self.class_members(value, exposure, family)
                elif callable(value):
                    defining = getattr(value, "__module__", None)
                    qualified = getattr(value, "__qualname__", None)
                    key = defining+"."+qualified if defining and qualified else exposure
                    self.record(key, "function" if inspect.isroutine(value) else "callable", value, exposure, family)
                else:
                    constants.append(exported)
            except CensusLimitError:
                raise
            except Exception as error:
                self.unresolved.append({"id": exposure, "kind": "export_introspection_failed", "error": type(error).__name__})
        self.modules.append({"name": name, "version": version, "available": True,
            "export_policy": policy, "export_names": sorted(names), "dynamic_names": sorted(dynamic),
            "submodule_exports": children, "noncallable_exports": constants,
            "public_dictionary_names": dictionary_names,
            "submodule_traversal_complete": False})

    def result(self):
        dependencies = {}
        for name in ("qiskit", "pennylane", "numpy", "scipy", "jax", "jaxlib", "torch",
                     "tensorflow", "pyarrow", "autoray", "autograd", "pennylane-catalyst", "pennylane-lightning"):
            try:
                dependencies[name] = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                dependencies[name] = None
        return {"schema": 1, "profile": self.profile, "collected_at": datetime.now(timezone.utc).isoformat(),
            "environment": {"python": platform.python_version(), "distribution_versions": dependencies},
            "loaded_reference_roots": {name: name in sys.modules for name in
                ("qiskit", "pennylane", "tensorflow", "pyarrow")},
            "scope": "explicit_modules_public_exports_nested_classes_and_static_mro", "census_complete": False,
            "policy": "Metadata only. The collector does not call SDK constructors or algorithms; package initialization and lazy export resolution may have side effects. No implementation source copied. Python sockets denied; not an OS network sandbox. No Native mapping inferred.",
            "import_initialization_side_effects_verified_absent": False,
            "modules": self.modules, "records": sorted(self.records.values(), key=lambda row: row["id"]),
            "class_exports": self.class_exports,
            "class_alias_reuses": self.class_alias_reuses,
            "class_alias_policy": "Finite static class graph; each class expands once per module export root. Reused and cyclic aliases remain edges, not an exhaustive list of arbitrarily long member paths.",
            "unresolved": self.unresolved,
            "closure_pending": ["recursive public module traversal", "optional packages and plugins",
                "canonical identity collisions", "signatures/defaults unavailable to introspection",
                "per-function Native contracts and both-profile execution evidence"]}


def merge_isolated_files(profile, pairs):
    """Union metadata, retaining process boundaries and ambiguous identities."""
    inputs = []
    for source, terminal in pairs:
        raw = source.read_bytes()
        receipt_raw = terminal.read_bytes()
        receipt = json.loads(receipt_raw)
        if (receipt.get("terminal") is not True or type(receipt.get("exit")) is not int
                or receipt["exit"] != 0 or receipt.get("profile") != profile
                or receipt.get("artifact_sha256") != hashlib.sha256(raw).hexdigest()):
            raise ValueError("Isolated census requires matching normal process receipts")
        reference = json.loads(gzip.decompress(raw) if source.suffix == ".gz" else raw)
        if reference.get("profile") != profile:
            raise ValueError("Isolated census requires matching normal process receipts")
        label = receipt.get("isolation", "")
        if not isinstance(label, str) or not label.isidentifier():
            raise ValueError("Invalid collection isolation identity")
        names = [row["name"] for row in reference["modules"]]
        if len(names) != len(set(names)) or sorted(names) != sorted(receipt.get("modules", [])):
            raise ValueError("Isolated module selections differ")
        records = reference["records"]
        if (len({row["id"] for row in records}) != len(records)
                or any(row["status"] != "unverified" or row["native_mapping"] is not None
                       or row["contract_reviewed"] is not False for row in records)):
            raise ValueError("A census cannot claim Native acceptance or duplicate record identity")
        inputs.append((label, reference, dict(isolation=label, terminal=True, exit=0,
            artifact_sha256=hashlib.sha256(raw).hexdigest(),
            source_sha256=receipt.get("source_sha256"),
            loaded_reference_roots=reference.get("loaded_reference_roots", {}),
            receipt_sha256=hashlib.sha256(receipt_raw).hexdigest())))
    if not inputs or len({label for label, _, _ in inputs}) != len(inputs):
        raise ValueError("Collection isolations must be nonempty and distinct")
    if len({value["environment"]["python"] for _, value, _ in inputs}) != 1:
        raise ValueError("Isolated Python reference versions differ")
    if any(value["environment"].get("distribution_versions") != inputs[0][1]["environment"].get("distribution_versions")
           for _, value, _ in inputs):
        raise ValueError("Isolated dependency metadata versions differ or are missing")
    modules = [module for _, value, _ in inputs for module in value["modules"]]
    if len({row["name"] for row in modules}) != len(modules):
        raise ValueError("Overlapping module collections require an explicit identity review")
    observed = {}
    for label, value, _ in inputs:
        for row in value["records"]:
            observed.setdefault(row["id"], []).append(label)
    records, unresolved = [], [copy.deepcopy(row) for _, value, _ in inputs for row in value["unresolved"]]
    for label, value, _ in inputs:
        for original in value["records"]:
            row = copy.deepcopy(original)
            row["collection_isolation"] = label
            if len(observed[row["id"]]) > 1:
                row["id"] += "@isolated-"+label
                row["canonical_identity_review_required"] = True
            records.append(row)
    unresolved += [dict(id=key, kind="cross_process_identity_uncompared", isolations=labels)
                   for key, labels in observed.items() if len(labels) > 1]
    if len({row["id"] for row in records}) != len(records):
        raise ValueError("Isolated identity suffix collision")
    return dict(schema=1, profile=profile, collected_at=datetime.now(timezone.utc).isoformat(),
        environment=copy.deepcopy(inputs[0][1]["environment"]),
        scope="isolated_sdk_metadata_union_not_coexistence_or_acceptance", census_complete=False,
        coexistence_verified=False,
        policy="Public metadata collected in separate SDK processes with unchanged versions. Python sockets denied during enumeration, not an OS sandbox. Normal terminal receipts required. No cross-process object identity inferred, SDK source copied, Native mapping or implementation acceptance claimed.",
        modules=copy.deepcopy(modules), records=sorted(records, key=lambda row: row["id"]),
        class_exports=[dict(collection_isolation=label, **copy.deepcopy(edge))
                       for label, value, _ in inputs for edge in value.get("class_exports", [])],
        class_alias_reuses=[dict(collection_isolation=label, **copy.deepcopy(row))
                            for label, value, _ in inputs for row in value.get("class_alias_reuses", [])],
        class_alias_policy="Finite per-process static class graphs; no cross-process object identity or exhaustive expansion of arbitrary alias paths is inferred.",
        unresolved=unresolved, collection_receipts=[receipt for _, _, receipt in inputs],
        traversal_audits=[dict(isolation=label, **copy.deepcopy(value["traversal"]))
                          for label, value, _ in inputs if "traversal" in value],
        closure_pending=sorted({item for _, value, _ in inputs for item in value["closure_pending"]}
            | {"SDK coexistence and cross-process identities are not certified by isolated metadata"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", action="append")
    parser.add_argument("--isolated", nargs=2, action="append", type=Path,
                        metavar=("CENSUS", "TERMINAL"))
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if bool(args.module) == bool(args.isolated):
        parser.error("Choose either explicit modules or isolated census/terminal pairs")
    if args.isolated:
        result = merge_isolated_files(args.profile, args.isolated)
    else:
        census = RuntimeCensus(args.profile)
        with deny_python_network():
            for name in args.module:
                census.module(name)
        result = census.result()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    body = (json.dumps(result, ensure_ascii=False, indent=2)+"\n").encode("utf-8")
    args.output.write_bytes(gzip.compress(body, mtime=0) if args.output.suffix == ".gz" else body)
    print(json.dumps({"profile": args.profile, "modules": len(result["modules"]),
                      "records": len(result["records"]), "unresolved": len(result["unresolved"]),
                      "census_complete": False}, indent=2))
