#!/usr/bin/env python3
"""Public export/MRO metadata only; never an implementation acceptance claim."""
import argparse
import copy
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import cached_property, partial
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


_TYPE_FIELDS = type.__getattribute__(type, "__dict__")


def _class_field(cls, name):
    return _TYPE_FIELDS[name].__get__(cls)


def _is_class(value):
    return type.__subclasscheck__(type, type(value))


def _class_label(cls, name):
    value = _class_field(cls, name)
    if type(value) is str:
        return value
    # Some extension metaclasses expose their type label through a native
    # getset slot. Do not substitute arbitrary Python properties or callbacks.
    for base in _class_field(type(cls), "__mro__"):
        descriptor = _class_field(base, "__dict__").get(name)
        if descriptor is None:
            continue
        if type(descriptor) is types.GetSetDescriptorType:
            value = descriptor.__get__(cls, type(cls))
            if type(value) is str:
                return value
        break
    raise TypeError("Class label requires an unsupported dynamic metadata protocol")


def type_name(value):
    cls = value if _is_class(value) else type(value)
    return _class_label(cls, "__module__")+"."+_class_label(cls, "__qualname__")


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


def _signature_protocol_review(value, *, _active=()):
    """Admit static signature metadata, not user-defined lookup callbacks."""
    if any(value is parent for parent in _active):
        return dict(reason="signature_wrapper_cycle", attribute="__wrapped__")
    if len(_active) >= 64:
        return dict(reason="signature_wrapper_depth", attribute="__wrapped__")
    missing = object()
    try:
        owner = type(value)
        lookup = inspect.getattr_static(owner, "__getattribute__", None)
        if (type(lookup) is types.FunctionType
                or inspect.getattr_static(owner, "__getattr__", missing) is not missing):
            return dict(reason="dynamic_signature_protocol", attribute="attribute_lookup")
        attributes = {name: inspect.getattr_static(value, name, missing)
                      for name in ("__signature__", "__wrapped__", "__text_signature__")}
        safe_descriptors = (types.FunctionType, types.MethodType, types.BuiltinFunctionType,
                            types.GetSetDescriptorType, types.MemberDescriptorType, staticmethod, classmethod)
        for name, raw in attributes.items():
            if (raw is not missing and inspect.getattr_static(type(raw), "__get__", missing) is not missing
                    and not any(type(raw) is kind for kind in safe_descriptors)):
                return dict(reason="dynamic_signature_protocol", attribute=name)
        raw_signature = attributes["__signature__"]
        if raw_signature is not missing and raw_signature is not None:
            if type(raw_signature) is not inspect.Signature:
                return dict(reason="opaque_signature_metadata", attribute="__signature__")
            return None
        active = (*_active, value)
        if owner is types.MethodType:
            return _signature_protocol_review(value.__func__, _active=active)
        if owner is partial:
            return _signature_protocol_review(value.func, _active=active)
        # Signature(None) stops inspect.unwrap but still delegates bound methods
        # and functools.partial through their ordinary signature implementations.
        wrapped = attributes["__wrapped__"]
        if raw_signature is missing and wrapped is not missing:
            return _signature_protocol_review(wrapped, _active=active)
    except Exception as error:
        return dict(reason="static_signature_inspection_failed", error=type(error).__name__)
    return None


class SignatureProtocolDeferred(RuntimeError):
    """Signature metadata requires an executable protocol, not passive reading."""

    def __init__(self, review):
        self.review = review
        super().__init__(review["reason"])


def python_binding_signature(value):
    """Read a Python function's lexical binder, ignoring advertised signatures."""
    bound = type(value) is types.MethodType
    function = value.__func__ if bound else value
    policy = dict(scope="python_function_argument_binding_only", behavior_verified=False,
                  annotations_not_inspected=True, follows_wrapped=False,
                  honors_signature_override=False, bound_receiver_removed=bound)
    if type(function) is not types.FunctionType:
        return dict(available=False, reason="not_a_direct_python_function_or_method", **policy)
    code, defaults, keywords = function.__code__, function.__defaults__, function.__kwdefaults__
    if defaults is not None and type(defaults) is not tuple or keywords is not None and type(keywords) is not dict:
        return dict(available=False, reason="opaque_default_container", **policy)
    defaults, keywords = defaults or (), keywords or {}
    count = code.co_argcount
    if any(type(name) is not str for name in keywords):
        return dict(available=False, reason="non_string_keyword_defaults_require_review", **policy)
    if any(type(name) is not str for name in code.co_varnames):
        return dict(available=False, reason="non_string_code_names_require_review", **policy)
    if len(defaults) > count:
        return dict(available=False, reason="excess_positional_defaults_require_review", **policy)
    if bound and not count:
        return dict(available=False, reason="bound_method_has_no_named_receiver", **policy)
    parameters = []
    for index, name in enumerate(code.co_varnames[:count]):
        default_index = index - (count - len(defaults))
        default = inspect.Parameter.empty if default_index < 0 else defaults[default_index]
        parameters.append(dict(name=name,
            kind="POSITIONAL_ONLY" if index < code.co_posonlyargcount else "POSITIONAL_OR_KEYWORD",
            default=literal(default, name)))
    cursor = count + code.co_kwonlyargcount
    if code.co_flags & inspect.CO_VARARGS:
        parameters.append(dict(name=code.co_varnames[cursor], kind="VAR_POSITIONAL", default={"present": False}))
        cursor += 1
    for name in code.co_varnames[count:count + code.co_kwonlyargcount]:
        parameters.append(dict(name=name, kind="KEYWORD_ONLY",
            default=literal(keywords.get(name, inspect.Parameter.empty), name)))
    if code.co_flags & inspect.CO_VARKEYWORDS:
        parameters.append(dict(name=code.co_varnames[cursor], kind="VAR_KEYWORD", default={"present": False}))
    if bound:
        parameters.pop(0)
    return dict(available=True, parameters=parameters, **policy)


def signature(value, *, _overloads=True):
    review = _signature_protocol_review(value)
    if review is not None:
        if review["reason"] in {"dynamic_signature_protocol", "static_signature_inspection_failed"}:
            raise SignatureProtocolDeferred(review)
        return dict(available=False, review_required=True, overload_review_required=True, **review)
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


def validate_object_identity_groups(reference):
    """Validate the partition, not the truth of a serialized worker observation."""
    records = {row["id"]: row for row in reference["records"]}
    if len(records) != len(reference["records"]):
        raise ValueError("Object identity groups require distinct record IDs")
    if "object_identity_groups" not in reference:
        if any("object_identity_group" in row for row in records.values()):
            raise ValueError("Object identity groups are missing")
        return []
    seen, labels = set(), set()
    groups = reference["object_identity_groups"]
    if not isinstance(groups, list):
        raise ValueError("Object identity groups require a partition")
    for group in groups:
        if not isinstance(group, dict):
            raise ValueError("Invalid object identity group partition")
        label, members = group.get("id"), group.get("record_ids")
        if (not isinstance(label, str) or not label or label in labels
                or not isinstance(members, list) or not members
                or any(not isinstance(key, str) for key in members)
                or members != sorted(set(members)) or not set(members) <= records.keys()
                or seen.intersection(members)
                or group.get("basis") != "held_python_object_is_within_worker"
                or group.get("behavior_equivalence_verified") is not False
                or group.get("context_contracts_preserved") is not True
                or any(records[key].get("object_identity_group") != label for key in members)):
            raise ValueError("Invalid object identity group partition")
        labels.add(label)
        seen.update(members)
    if seen != records.keys():
        raise ValueError("Object identity group partition omitted records")
    return groups


_CLASS_LINKS = ("class_identity", "owner_class_identity", "declaring_class_identity",
                "target_class_identity", "metaclass_identity")
_CLASS_LINK_LISTS = ("mro_identities", "direct_base_identities", "metaclass_mro_identities")


def validate_class_graph(reference):
    """Validate serialized links, not the truth of a worker's live observation."""
    graph = reference.get("class_graph")
    if graph is None:
        if "class_graph" in reference:
            raise ValueError("Invalid class graph observation policy")
        if any(any(field in row for field in (*_CLASS_LINKS, *_CLASS_LINK_LISTS))
               for row in reference["records"]):
            raise ValueError("Class graph is missing")
        return None
    if (not isinstance(graph, dict) or type(graph.get("schema")) is not int or graph["schema"] != 1
            or graph.get("basis") != "held_python_class_is_within_worker"
            or any(graph.get(key) is not False for key in ("behavior_verified",
                "declaration_body_provenance_verified", "topology_atomicity_verified", "cross_process_identity_verified"))
            or not isinstance(graph.get("nodes"), list)):
        raise ValueError("Invalid class graph observation policy")
    nodes = {}
    for node in graph["nodes"]:
        if not isinstance(node, dict) or type(node.get("id")) is not str or not node["id"] or node["id"] in nodes:
            raise ValueError("Invalid class graph node identity")
        nodes[node["id"]] = node
    records = {row["id"]: row for row in reference["records"]}
    for identity, node in nodes.items():
        if (not isinstance(node.get("names"), list) or not node["names"]
                or any(type(name) is not str for name in node["names"])
                or not isinstance(node.get("sources"), dict)
                or not isinstance(node.get("record_ids"), list)
                or any(type(key) is not str or key not in records for key in node["record_ids"])
                or len(node["record_ids"]) != len(set(node["record_ids"]))
                or node.get("behavior_verified") is not False
                or node.get("declaration_body_provenance_verified") is not False
                or not isinstance(node.get("topology_observations"), list) or not node["topology_observations"]):
            raise ValueError("Invalid class graph node metadata")
        for observation in node["topology_observations"]:
            if (not isinstance(observation, dict) or type(observation.get("metaclass")) is not str
                    or observation["metaclass"] not in nodes):
                raise ValueError("Invalid class graph metaclass link")
            for field in ("direct_bases", "mro"):
                values = observation.get(field)
                if (not isinstance(values, list) or any(type(value) is not str or value not in nodes for value in values)
                        or len(values) != len(set(values))):
                    raise ValueError("Invalid class graph topology link")
            if (not observation["mro"] or observation["mro"][0] != identity
                    or not set(observation["direct_bases"]).issubset(observation["mro"][1:])):
                raise ValueError("Invalid class graph MRO relationship")
        for key in node["record_ids"]:
            if records[key].get("kind") != "class" or records[key].get("class_identity") != identity:
                raise ValueError("Invalid class graph record link")
    for row in reference["records"]:
        for field in _CLASS_LINKS:
            if field in row and (type(row[field]) is not str or row[field] not in nodes):
                raise ValueError("Invalid class graph record identity")
        for field in _CLASS_LINK_LISTS:
            if field in row and (not isinstance(row[field], list)
                    or any(type(value) is not str or value not in nodes for value in row[field])):
                raise ValueError("Invalid class graph record topology")
        if "class_identity" in row and row["id"] not in nodes[row["class_identity"]]["record_ids"]:
            raise ValueError("Class graph omitted a class record")
        if "owner_class_identity" in row:
            if "declaring_class_identity" not in row or row.get("lookup_plane") not in {"instance", "metaclass"}:
                raise ValueError("Invalid class graph member context")
            owner = nodes[row["owner_class_identity"]]
            planes = [owner] if row["lookup_plane"] == "instance" else [nodes[item["metaclass"]]
                for item in owner["topology_observations"]]
            if not any(row["declaring_class_identity"] in item["mro"] for plane in planes
                       for item in plane["topology_observations"]):
                raise ValueError("Invalid class graph declaring relationship")
    for row in (*reference.get("class_exports", []), *reference.get("class_alias_reuses", []),
                *graph.get("alias_reuses", [])):
        if any(field in row and (type(row[field]) is not str or row[field] not in nodes) for field in _CLASS_LINKS):
            raise ValueError("Invalid class graph export edge")
    return graph


def _remap_class_links(row, class_ids, record_ids):
    result = copy.deepcopy(row)
    for field in _CLASS_LINKS:
        if field in result:
            result[field] = class_ids[result[field]]
    for field in _CLASS_LINK_LISTS:
        if field in result:
            result[field] = [class_ids[value] for value in result[field]]
    if "owner_class" in result:
        result["owner_class"] = record_ids.get(result["owner_class"], result["owner_class"])
    return result


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
        self.descriptor_reclassifications = []
        self._module_stack = []
        self._class_objects, self._class_nodes = {}, {}
        self._class_owners, self._class_owner_objects = {}, {}
        self._class_alias_identities = []

    def source(self, value, family):
        is_class = _is_class(value)
        if is_class:
            filename = None
        else:
            try:
                filename = inspect.getsourcefile(value)
            except TypeError:
                filename = None
        defining = _class_label(value, "__module__") if is_class else getattr(value, "__module__", None)
        if not isinstance(defining, str):
            owner = getattr(value, "__objclass__", None)
            defining = _class_label(owner, "__module__") if _is_class(owner) else None
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

    def class_identity(self, cls, family, *, observe=False):
        """Retain real classes; names and declaration files are labels, not identity."""
        pending = []
        def reserve(value):
            address = id(value)
            if address not in self._class_nodes:
                self._class_objects[address] = value
                self._class_nodes[address] = dict(id="class-object:"+str(len(self._class_nodes)+1),
                    names=[], sources={}, record_ids=[], topology_observations=[],
                    behavior_verified=False, declaration_body_provenance_verified=False)
                pending.append(value)
            elif family not in self._class_nodes[address]["sources"]:
                pending.append(value)
            return self._class_nodes[address]["id"]
        identity = reserve(cls)
        if not pending:
            if not observe:
                return identity
            pending.append(cls)
        visited = set()
        while pending:
            value = pending.pop()
            address = id(value)
            if address in visited:
                continue
            visited.add(address)
            node = self._class_nodes[address]
            name = type_name(value)
            if name not in node["names"]:
                node["names"].append(name)
            if family not in node["sources"]:
                node["sources"][family] = self.source(value, family)
            observation = dict(direct_bases=[reserve(base) for base in _class_field(value, "__bases__")],
                mro=[reserve(base) for base in _class_field(value, "__mro__")],
                metaclass=reserve(type(value)))
            if observation not in node["topology_observations"]:
                node["topology_observations"].append(observation)
                if len(node["topology_observations"]) > 1:
                    self.unresolved.append(dict(id=node["id"], kind="class_topology_changed",
                        still_in_scope=True, review_required=True))
        return identity

    def class_owner(self, cls, exposure):
        address = id(cls)
        if address not in self._class_owners:
            canonical = type_name(cls)
            owner, ordinal = canonical, 2
            while owner in self._class_owner_objects and self._class_owner_objects[owner] is not cls:
                owner = canonical+"@"+exposure+("@observation-"+str(ordinal) if ordinal > 2 else "")
                ordinal += 1
            self._class_owners[address] = owner
            self._class_owner_objects[owner] = cls
        return self._class_owners[address]

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
            origins = row["exposure_origins"].setdefault(exposure, [])
            origin = self._module_stack[-1] if self._module_stack else "direct_class_scan"
            if origin not in origins:
                origins.append(origin)
            return key
        if self.max_records is not None and len(self.records) >= self.max_records:
            raise CensusLimitError("max_records")
        observed_signature = signature(value)
        defining = (_class_label(value, "__module__") if _is_class(value)
            else getattr(value, "__module__", None))
        row = {"id": key, "canonical_id": canonical, "kind": kind, "family": family, "exposures": [exposure],
            "exposure_origins": {exposure: [self._module_stack[-1] if self._module_stack else "direct_class_scan"]},
            "declaration_module": defining if isinstance(defining, str) else None,
            "declared_in_reference_namespace": (defining == family or defining.startswith(family+".")) if isinstance(defining, str) else None,
            "signature": observed_signature, "python_binding_signature": python_binding_signature(value),
            **self.source(value, family), **extra,
            "status": "unverified", "native_mapping": None, "contract_reviewed": False}
        # An address alone is not an identity once a lazy export is collected.
        # Keep each observed object alive until the metadata process finishes.
        self.identities[key] = value
        self.canonical_objects[identity] = key
        self.records[key] = row
        return key

    def member_records(self, owner, name, descriptor, exposure, family, *, declared_in,
                       inherited, lookup_plane="instance", metaclass=None,
                       owner_identity=None, declaring_identity=None, metaclass_identity=None):
        separator = "@type." if lookup_plane == "metaclass" else "."
        key, exposed = owner+separator+name, exposure+separator+name
        extra = dict(owner_class=owner, declared_in=declared_in, inherited=inherited,
                     lookup_plane=lookup_plane)
        if owner_identity is not None:
            extra.update(owner_class_identity=owner_identity, declaring_class_identity=declaring_identity)
        if metaclass_identity is not None:
            extra["metaclass_identity"] = metaclass_identity
        if metaclass is not None:
            extra.update(metaclass=metaclass,
                         implicit_class_protocol=name.startswith("__") and name.endswith("__"))
        if isinstance(descriptor, (staticmethod, classmethod)):
            value, kind = descriptor.__func__, type(descriptor).__name__
        elif isinstance(descriptor, property):
            for accessor, value in (("get", descriptor.fget), ("set", descriptor.fset),
                                    ("delete", descriptor.fdel)):
                if value is not None:
                    suffix = "" if accessor == "get" else "@"+accessor
                    kind = {"get": "property", "set": "property_setter", "delete": "property_deleter"}[accessor]
                    self.record(key+suffix, kind, value, exposed, family, accessor=accessor, **extra)
            return
        elif type(descriptor) is cached_property:
            value, kind = descriptor.func, "cached_property"
            extra["accessor"] = "get"
        elif inspect.isgetsetdescriptor(descriptor) or inspect.ismemberdescriptor(descriptor):
            value, kind = descriptor, "property"
        else:
            # Custom nondata descriptors can satisfy ismethoddescriptor even
            # though inspecting them as ordinary methods loses their getter.
            routines = (types.FunctionType, types.BuiltinFunctionType, types.MethodType,
                        types.WrapperDescriptorType, types.MethodDescriptorType,
                        types.ClassMethodDescriptorType, types.MethodWrapperType)
            protocols = {}
            if type(descriptor) not in routines:
                for base in _class_field(type(descriptor), "__mro__"):
                    for magic in ("__get__", "__set__", "__delete__"):
                        if magic not in protocols and magic in _class_field(base, "__dict__"):
                            protocols[magic] = _class_field(base, "__dict__")[magic]
            if protocols:
                replacements = self.custom_descriptor_records(key, descriptor, exposed, family, protocols, extra)
                if inspect.ismethoddescriptor(descriptor):
                    row = dict(previous_id=key, previous_kind="method", exposure=exposed,
                        replacement_ids=sorted(set(replacements)), still_in_scope=True,
                        reason="custom_descriptor_protocol_not_ordinary_bound_method")
                    if row not in self.descriptor_reclassifications:
                        self.descriptor_reclassifications.append(row)
                return
            if inspect.isroutine(descriptor):
                value, kind = descriptor, "method"
            elif callable(descriptor):
                value, kind = descriptor, "callable_attribute"
            else:
                return
        if value is not None:
            self.record(key, kind, value, exposed, family, **extra)

    def custom_descriptor_records(self, key, descriptor, exposure, family, protocols, context):
        extra = dict(context, descriptor_type=type_name(type(descriptor)),
                     descriptor_semantics_review_required=True)
        records = []
        for magic, accessor in (("__get__", "get"), ("__set__", "set"), ("__delete__", "delete")):
            if magic not in protocols:
                continue
            value = protocols[magic]
            if type(value) in (staticmethod, classmethod):
                value = value.__func__
            if not callable(value):
                self.unresolved.append(dict(id=key, kind="custom_descriptor_protocol_unresolved",
                    protocol=magic, still_in_scope=True))
                continue
            try:
                records.append(self.record(key+"@descriptor-"+accessor, "descriptor_protocol", value, exposure, family,
                    accessor=accessor, descriptor_protocol=magic,
                    signature_semantics="unbound_descriptor_protocol", **extra))
            except CensusLimitError:
                raise
            except Exception as error:
                self.unresolved.append(dict(id=key, kind="custom_descriptor_protocol_failed",
                    protocol=magic, error=type(error).__name__, still_in_scope=True))
        for field, accessor in (("fget", "get"), ("fset", "set"), ("fdel", "delete")):
            value = inspect.getattr_static(descriptor, field, None)
            if value is None:
                continue
            binding = type(value).__name__ if type(value) in (staticmethod, classmethod) else "function"
            if type(value) in (staticmethod, classmethod):
                value = value.__func__
            if not callable(value):
                self.unresolved.append(dict(id=key, kind="custom_descriptor_accessor_unresolved",
                    accessor=accessor, still_in_scope=True))
                continue
            suffix = "" if accessor == "get" else "@"+accessor
            try:
                records.append(self.record(key+suffix, "descriptor_accessor", value, exposure, family,
                    accessor=accessor, wrapped_accessor_binding=binding,
                    signature_semantics="unbound_wrapped_accessor_candidate", **extra))
            except CensusLimitError:
                raise
            except Exception as error:
                self.unresolved.append(dict(id=key, kind="custom_descriptor_accessor_failed",
                    accessor=accessor, error=type(error).__name__, still_in_scope=True))
        return records

    def class_members(self, cls, exposure, family, *, _active=(), _expanded=None):
        owner = self.class_owner(cls, exposure)
        identity = self.class_identity(cls, family, observe=True)
        mro = _class_field(cls, "__mro__")
        meta = type(cls)
        meta_mro = _class_field(meta, "__mro__")
        meta_identity = self.class_identity(meta, family)
        try:
            key = self.record(owner, "class", cls, exposure, family, canonical_id=type_name(cls),
                mro=[type_name(c) for c in mro], class_identity=identity,
                mro_identities=[self.class_identity(c, family) for c in mro],
                direct_base_identities=[self.class_identity(c, family) for c in _class_field(cls, "__bases__")],
                metaclass=type_name(meta), metaclass_identity=meta_identity,
                metaclass_mro=[type_name(c) for c in meta_mro],
                metaclass_mro_identities=[self.class_identity(c, family) for c in meta_mro])
            owner = self._class_owners[id(cls)] = key
            self._class_owner_objects[key] = cls
            record_ids = self._class_nodes[id(cls)]["record_ids"]
            if key not in record_ids:
                record_ids.append(key)
        except SignatureProtocolDeferred as error:
            self.unresolved.append(dict(id=exposure, kind="export_introspection_failed",
                owner_class=owner, error=type(error).__name__, signature_review=error.review,
                deferred=True, still_in_scope=True))
        reason = ("cyclic_class_alias" if any(cls is active for active in _active) else
                  "nested_class_depth_limit" if len(_active) >= self.max_class_depth else None)
        if reason is not None:
            row = dict(id=exposure, kind=reason, owner_class=owner,
                owner_class_identity=identity, still_in_scope=True)
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
            identified = dict(row, owner_class_identity=identity)
            if identified not in self._class_alias_identities:
                self._class_alias_identities.append(identified)
            return
        _expanded[id(cls)] = exposure
        active = (*_active, cls)
        seen = set()
        for base in mro:
            for name, descriptor in _class_field(base, "__dict__").items():
                if name in seen:
                    continue
                seen.add(name)
                if name.startswith("_") and not (name.startswith("__") and name.endswith("__")):
                    continue
                if _is_class(descriptor):
                    edge = dict(owner_class=owner, attribute=name, exposure=exposure+"."+name,
                        target_class=type_name(descriptor), declared_in=type_name(base), inherited=base is not cls,
                        owner_class_identity=identity, target_class_identity=self.class_identity(descriptor, family),
                        declaring_class_identity=self.class_identity(base, family))
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
                try:
                    self.member_records(owner, name, descriptor, exposure, family,
                        declared_in=type_name(base), inherited=base is not cls,
                        owner_identity=identity, declaring_identity=self.class_identity(base, family))
                except CensusLimitError:
                    raise
                except Exception as error:
                    self.unresolved.append(dict(id=exposure+"."+name, kind="member_introspection_failed",
                        error=type(error).__name__, still_in_scope=True))
        seen = set()
        for base in meta_mro:
            for name, descriptor in _class_field(base, "__dict__").items():
                if name in seen:
                    continue
                seen.add(name)
                if name.startswith("_") and not (name.startswith("__") and name.endswith("__")):
                    continue
                target = exposure+"@type."+name
                try:
                    if _is_class(descriptor):
                        edge = dict(owner_class=owner, attribute=name, exposure=target,
                            target_class=type_name(descriptor), declared_in=type_name(base),
                            inherited=base is not meta, lookup_plane="metaclass", metaclass=type_name(meta),
                            owner_class_identity=identity, target_class_identity=self.class_identity(descriptor, family),
                            declaring_class_identity=self.class_identity(base, family), metaclass_identity=meta_identity)
                        if edge not in self.class_exports:
                            self.class_exports.append(edge)
                        self.class_members(descriptor, target, family, _active=active, _expanded=_expanded)
                    else:
                        self.member_records(owner, name, descriptor, exposure, family,
                            declared_in=type_name(base), inherited=base is not meta,
                            lookup_plane="metaclass", metaclass=type_name(meta), owner_identity=identity,
                            declaring_identity=self.class_identity(base, family), metaclass_identity=meta_identity)
                except CensusLimitError:
                    raise
                except Exception as error:
                    self.unresolved.append(dict(id=target, kind="metaclass_introspection_failed",
                        error=type(error).__name__, still_in_scope=True))

    def module(self, name):
        self._module_stack.append(name)
        try:
            return self._collect_module(name)
        finally:
            self._module_stack.pop()

    def _collect_module(self, name):
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
                if type.__subclasscheck__(types.ModuleType, type(value)):
                    children.append({"exposure": exposure, "module": vars(value).get("__name__")})
                elif _is_class(value):
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
        # Identity is independent of name, code bytes and object equality.
        # Strong references in identities prevent address reuse during this scan.
        partition = {}
        for key, value in self.identities.items():
            partition.setdefault(id(value), []).append(key)
        records = {key: dict(row, exposure_origins={path: list(origins)
            for path, origins in row.get("exposure_origins", {}).items()}) for key, row in self.records.items()}
        groups = []
        for keys in partition.values():
            keys.sort()
            label = "python-object:"+hashlib.sha256(json.dumps(keys, separators=(",", ":")).encode()).hexdigest()
            groups.append(dict(id=label, record_ids=keys,
                basis="held_python_object_is_within_worker", behavior_equivalence_verified=False,
                context_contracts_preserved=True))
            for key in keys:
                records[key]["object_identity_group"] = label
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
            "scope": "explicit_modules_public_exports_nested_classes_static_mro_descriptors_and_metaclasses", "census_complete": False,
            "policy": "Metadata only. The collector does not call SDK constructors or algorithms; package initialization and lazy export resolution may have side effects. No implementation source copied. Python sockets denied; not an OS network sandbox. No Native mapping inferred.",
            "import_initialization_side_effects_verified_absent": False,
            "modules": self.modules, "records": sorted(records.values(), key=lambda row: row["id"]),
            "object_identity_groups": sorted(groups, key=lambda row: row["id"]),
            "object_identity_policy": "Groups certify only that held raw callable/class objects are identical within this collection worker. Binding, owner, accessor and lookup-plane contracts remain separate records. Labels derive from observed record IDs, are snapshot-local, and are not executable paths or stable API identities. No equal names, signatures, source hashes, wrappers, code objects or cross-process objects are merged; a group is not a unique function denominator or behavior acceptance.",
            "class_exports": self.class_exports,
            "class_graph": dict(schema=1, nodes=copy.deepcopy(list(self._class_nodes.values())),
                alias_reuses=copy.deepcopy(self._class_alias_identities),
                basis="held_python_class_is_within_worker", behavior_verified=False,
                declaration_body_provenance_verified=False, topology_atomicity_verified=False,
                cross_process_identity_verified=False,
                policy="Snapshot-local held class identities retain direct bases, ordered MROs, metaclasses, declaration-module file hashes and distinct member owners. Labels/files are not class-body identity, behavior, atomic mutation snapshots or a closed function denominator."),
            "class_alias_reuses": self.class_alias_reuses,
            "descriptor_reclassifications": self.descriptor_reclassifications,
            "class_alias_policy": "Finite static class graph; each class expands once per module export root. Reused and cyclic aliases remain edges, not an exhaustive list of arbitrarily long member paths.",
            "class_protocol_policy": "Instance and metaclass lookup planes are distinct metadata contexts. @type paths label metaclass dispatch, not importable dotted paths. Custom descriptor protocols and static wrapped-accessor fields are candidates only; getter/setter bodies and metaclass constructors are never explicitly called by enumeration. Dynamic metaclass attributes and descriptor behavior still require review.",
            "unresolved": self.unresolved,
            "closure_pending": ["recursive public module traversal", "optional packages and plugins",
                "canonical identity collisions", "dynamic metaclass exports and descriptor behavior",
                "signatures/defaults unavailable to introspection",
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
        validate_object_identity_groups(reference)
        validate_class_graph(reference)
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
    if len({"object_identity_groups" in value for _, value, _ in inputs}) > 1:
        raise ValueError("Mixed object identity observation schemas require recollection")
    if len({"class_graph" in value for _, value, _ in inputs}) > 1:
        raise ValueError("Mixed class graph observation schemas require recollection")
    modules = [module for _, value, _ in inputs for module in value["modules"]]
    if len({row["name"] for row in modules}) != len(modules):
        raise ValueError("Overlapping module collections require an explicit identity review")
    observed = {}
    for label, value, _ in inputs:
        for row in value["records"]:
            observed.setdefault(row["id"], []).append(label)
    records, identity_groups, identity_audits, class_nodes, class_audits = [], [], [], [], []
    class_aliases = []
    exports, reuses, unresolved = [], [], []
    for label, value, _ in inputs:
        record_ids = {row["id"]: row["id"]+("@isolated-"+label if len(observed[row["id"]]) > 1 else "")
                      for row in value["records"]}
        graph = value.get("class_graph")
        class_ids = {node["id"]: node["id"]+"@isolated-"+label for node in graph["nodes"]} if graph else {}
        for original in value["records"]:
            row = _remap_class_links(original, class_ids, record_ids)
            row["collection_isolation"] = label
            if len(observed[row["id"]]) > 1:
                row["id"] += "@isolated-"+label
                row["canonical_identity_review_required"] = True
            if "object_identity_group" in row:
                row["object_identity_group"] += "@isolated-"+label
            records.append(row)
        for original in value.get("object_identity_groups", []):
            group = copy.deepcopy(original)
            group["id"] += "@isolated-"+label
            group["record_ids"] = sorted(record_ids[key] for key in original["record_ids"])
            group["collection_isolation"] = label
            identity_groups.append(group)
        if graph is not None:
            for original in graph["nodes"]:
                node = copy.deepcopy(original)
                node["id"] = class_ids[node["id"]]
                node["record_ids"] = [record_ids[key] for key in node["record_ids"]]
                for observation in node["topology_observations"]:
                    observation["direct_bases"] = [class_ids[key] for key in observation["direct_bases"]]
                    observation["mro"] = [class_ids[key] for key in observation["mro"]]
                    observation["metaclass"] = class_ids[observation["metaclass"]]
                node["collection_isolation"] = label
                class_nodes.append(node)
            class_aliases.extend(dict(collection_isolation=label, **_remap_class_links(row, class_ids, record_ids))
                for row in graph.get("alias_reuses", []))
        class_audits.append(dict(collection_isolation=label, observed=graph is not None,
            nodes=len(class_ids), cross_process_identity_verified=False))
        exports.extend(dict(collection_isolation=label, **_remap_class_links(row, class_ids, record_ids))
            for row in value.get("class_exports", []))
        reuses.extend(dict(collection_isolation=label, **_remap_class_links(row, class_ids, record_ids))
            for row in value.get("class_alias_reuses", []))
        for original in value["unresolved"]:
            row = _remap_class_links(original, class_ids, record_ids)
            if row.get("kind") == "class_topology_changed":
                row["id"] = class_ids[row["id"]]
            unresolved.append(row)
        identity_audits.append(dict(collection_isolation=label,
            observed="object_identity_groups" in value,
            records=len(value["records"]), groups=len(value.get("object_identity_groups", [])),
            policy=value.get("object_identity_policy"), cross_process_identity_verified=False))
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
        **({"object_identity_groups": sorted(identity_groups, key=lambda row: row["id"])}
           if all("object_identity_groups" in value for _, value, _ in inputs) else {}),
        **({"class_graph": dict(schema=1, nodes=class_nodes, alias_reuses=class_aliases,
            basis="held_python_class_is_within_worker",
            behavior_verified=False, declaration_body_provenance_verified=False,
            topology_atomicity_verified=False, cross_process_identity_verified=False,
            policy="Worker-local class identities and declaration labels remain isolated; no class-body provenance, behavior or complete denominator is inferred.")}
           if all("class_graph" in value for _, value, _ in inputs) else {}),
        class_graph_audits=class_audits,
        object_identity_audits=identity_audits,
        object_identity_policy="Worker-local identity partitions remain isolated. No same-name, same-source or cross-process equivalence and no behavior, unique function denominator or Native acceptance is inferred.",
        class_exports=exports,
        class_alias_reuses=reuses,
        descriptor_reclassifications=[dict(collection_isolation=label, **copy.deepcopy(row))
            for label, value, _ in inputs for row in value.get("descriptor_reclassifications", [])],
        class_protocol_audits=[dict(collection_isolation=label, policy=value["class_protocol_policy"])
            for label, value, _ in inputs if "class_protocol_policy" in value],
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
