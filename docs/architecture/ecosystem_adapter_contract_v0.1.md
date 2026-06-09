# Ecosystem Adapter Contract v0.1

**Version**: v0.1  
**Date**: 2026-06-09  
**Status**: Stage 8A contract design  

## 1. Purpose

This contract defines the minimum common surface for optional ecosystem
adapters. It applies to Qiskit, PennyLane, Quafu/pyquafu, QOS-UQCI, and future
ecosystems.

Adapters are not production replacements. They are explicit compatibility
layers with dependency checks, public API lookup, passthrough, schema wrapping,
warnings, and provenance.

## 2. Capability Levels

| Level | Name | Meaning |
| --- | --- | --- |
| 0 | Inventory | Public API names or planned capabilities are listed only. |
| 1 | Passthrough | Upstream object or call is returned/executed through the optional dependency. |
| 2 | Schema adapter | Upstream result is wrapped in a QuantumBridge schema. |
| 3 | Native subset | Independently implemented QuantumBridge subset. |
| 4 | Production equivalent | Not promised in Stage 8A. |

## 3. Required Adapter Metadata

Each adapter must expose or document:

- `capability_level`;
- `production_ready`;
- `native_implementation`;
- `upstream_required`;
- `ecosystem`;
- `upstream_package`;
- `dependency_extra`;
- `warnings`;
- `provenance`.

## 4. Required Methods

| Method | Requirement |
| --- | --- |
| `dependency_available()` | Return whether the optional dependency can be imported. |
| `get_upstream_version()` | Return installed upstream version or `None`. |
| `list_public_api_inventory()` | Return inventory records without copying upstream source/docs. |
| `get_public_object(name)` | Resolve a public object through the installed dependency. |
| `passthrough_call(name, *args, **kwargs)` | Call an upstream callable with clear dependency errors. |
| `wrap_result(obj)` | Return a QuantumBridge result envelope or schema object. |
| `to_quantumbridge_schema(obj)` | Convert supported objects to QuantumBridge schemas. |
| `get_warnings()` | Return warnings for advisory, scaffold, unsupported, or offline-only modes. |
| `get_provenance()` | Return source package, version, adapter, mode, and capability level. |
| `unsupported(reason)` | Return or raise a structured unsupported result. |
| `validate_environment()` | Check dependency, version, token policy, and lane constraints. |

## 5. Warning Requirements

Warnings must be explicit when an adapter is:

- scaffold-only;
- advisory-only;
- offline-only;
- missing an optional dependency;
- using a dependency version outside tested constraints;
- wrapping a domain that is not production-grade;
- unable to access real cloud/hardware by design.

## 6. Provenance Requirements

Provenance must include:

- ecosystem;
- upstream package;
- upstream version when available;
- QuantumBridge version when available;
- adapter module;
- capability level;
- mode;
- dependency extra;
- timestamp when produced by a runtime path;
- source limitation notes.

## 7. Implementation Policy

Stage 8A may define lightweight Protocol, dataclass, and enum helpers. It must
not rework existing adapters into a large new inheritance hierarchy. Existing
adapter modules can adopt the contract incrementally in later stages.
