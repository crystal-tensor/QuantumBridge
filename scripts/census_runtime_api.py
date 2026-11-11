#!/usr/bin/env python3
"""Public export/MRO metadata only; never an implementation acceptance claim."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
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


def type_name(value):
    cls = value if isinstance(value, type) else type(value)
    return type.__getattribute__(cls, "__module__")+"."+type.__getattribute__(cls, "__qualname__")


def literal(value, parameter=""):
    if value is inspect.Parameter.empty:
        return {"present": False}
    if value is None or type(value) in (bool, int) or type(value) is float and math.isfinite(value):
        return {"present": True, "literal": True, "value": value}
    secret = any(word in parameter.lower() for word in ("token", "password", "secret", "credential", "api_key"))
    if type(value) is str and not secret and len(value) <= 200 and not value.startswith(("/", "~")):
        return {"present": True, "literal": True, "value": value}
    return {"present": True, "literal": False, "type": type_name(value), "review_required": True}


def signature(value):
    try:
        sig = inspect.signature(value, eval_str=False)
        parameters = [{"name": p.name, "kind": p.kind.name, "default": literal(p.default, p.name),
                       "annotation": literal(p.annotation)} for p in sig.parameters.values()]
        return {"available": True, "parameters": parameters, "return_annotation": literal(sig.return_annotation)}
    except (TypeError, ValueError) as error:
        return {"available": False, "reason": type(error).__name__, "review_required": True}


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


class RuntimeCensus:
    def __init__(self, profile):
        self.profile, self.records, self.identities = profile, {}, {}
        self.canonical_objects = {}
        self.modules, self.unresolved, self.files = [], [], {}

    def source(self, value, family):
        try:
            filename = inspect.getsourcefile(value)
        except TypeError:
            filename = None
        module = sys.modules.get(getattr(value, "__module__", ""))
        filename = filename or (vars(module).get("__file__") if module is not None else None)
        package = sys.modules.get(family)
        package_file = None if package is None else vars(package).get("__file__")
        if not filename or not package_file:
            return {"file": None, "source_hash": None}
        path, base = Path(filename).resolve(), Path(package_file).resolve().parent
        if not path.is_file() or not path.is_relative_to(base):
            return {"file": None, "source_hash": None}
        if path not in self.files:
            self.files[path] = hashlib.sha256(path.read_bytes()).hexdigest()
        return {"file": str(Path(family) / path.relative_to(base)), "source_hash": self.files[path]}

    def record(self, key, kind, value, exposure, family, **extra):
        canonical = key
        identity = (canonical, id(value))
        if identity in self.canonical_objects:
            key = self.canonical_objects[identity]
        elif key in self.records and self.identities[key] != id(value):
            self.unresolved.append({"id": key, "kind": "canonical_identity_collision", "exposure": exposure})
            self.records[key]["canonical_identity_review_required"] = True
            key += "@"+exposure
            extra["canonical_identity_review_required"] = True
        if key in self.records:
            row = self.records[key]
            if exposure not in row["exposures"]:
                row["exposures"].append(exposure)
            return
        self.identities[key] = id(value)
        self.canonical_objects[identity] = key
        self.records[key] = {"id": key, "canonical_id": canonical, "kind": kind, "family": family, "exposures": [exposure],
            "signature": signature(value), **self.source(value, family), **extra,
            "status": "unverified", "native_mapping": None, "contract_reviewed": False}

    def class_members(self, cls, exposure, family):
        owner = type_name(cls)
        mro = type.__getattribute__(cls, "__mro__")
        self.record(owner, "class", cls, exposure, family, mro=[type_name(c) for c in mro])
        seen = set()
        for base in mro:
            for name, descriptor in type.__getattribute__(base, "__dict__").items():
                if name in seen:
                    continue
                seen.add(name)
                if name.startswith("_") and not (name.startswith("__") and name.endswith("__")):
                    continue
                if isinstance(descriptor, (staticmethod, classmethod)):
                    value, kind = descriptor.__func__, type(descriptor).__name__
                elif isinstance(descriptor, property):
                    value, kind = descriptor.fget, "property"
                elif inspect.isgetsetdescriptor(descriptor) or inspect.ismemberdescriptor(descriptor):
                    value, kind = descriptor, "property"
                elif inspect.isroutine(descriptor):
                    value, kind = descriptor, "method"
                else:
                    continue
                if value is None:
                    continue
                self.record(owner+"."+name, kind, value, exposure+"."+name, family,
                    owner_class=owner, declared_in=type_name(base), inherited=base is not cls)

    def module(self, name):
        family = name.split(".")[0]
        try:
            version = importlib.metadata.version(family.replace("_", "-"))
        except importlib.metadata.PackageNotFoundError:
            version = None
        try:
            module = importlib.import_module(name)
        except Exception as error:
            self.modules.append({"name": name, "version": version, "available": False,
                                 "error": type(error).__name__, "still_in_scope": True})
            return
        declared = vars(module).get("__all__")
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
        self.modules.append({"name": name, "version": version, "available": True,
            "export_policy": policy, "export_names": sorted(names), "dynamic_names": sorted(dynamic),
            "submodule_exports": children, "noncallable_exports": constants,
            "submodule_traversal_complete": False})

    def result(self):
        return {"schema": 1, "profile": self.profile, "collected_at": datetime.now(timezone.utc).isoformat(),
            "environment": {"python": platform.python_version()},
            "scope": "explicit_modules_public_exports_and_static_mro", "census_complete": False,
            "policy": "Metadata only, no SDK object instantiation or implementation source copied. Python sockets denied; not an OS network sandbox. No Native mapping inferred.",
            "modules": self.modules, "records": sorted(self.records.values(), key=lambda row: row["id"]),
            "unresolved": self.unresolved,
            "closure_pending": ["recursive public module traversal", "optional packages and plugins",
                "canonical identity collisions", "signatures/defaults unavailable to introspection",
                "per-function Native contracts and both-profile execution evidence"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", action="append", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
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
