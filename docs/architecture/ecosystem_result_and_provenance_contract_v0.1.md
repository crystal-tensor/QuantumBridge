# Ecosystem Result and Provenance Contract v0.1

**Version**: v0.1  
**Date**: 2026-06-09  
**Status**: Stage 8A schema design  

## 1. Purpose

QuantumBridge ecosystem results need a stable envelope so downstream tools can
inspect capability level, provenance, warnings, and unsupported states without
depending on native upstream result classes.

This document extends the current `quantumbridge.schema.ecosystem_results`
model without breaking compatibility.

## 2. Required Fields

| Field | Requirement |
| --- | --- |
| `schema_version` | Non-empty schema identifier. |
| `ecosystem` | Logical ecosystem, such as `qiskit`, `pennylane`, `quafu`, `qos-uqci`. |
| `upstream_package` | Upstream package or external spec name. |
| `upstream_version` | Installed upstream version or `None`. |
| `quantumbridge_version` | QuantumBridge package version when available. |
| `capability_level` | Integer 0 through 4. |
| `mode` | Inventory, passthrough, adapter, native subset, advisory, offline-only. |
| `raw_type` | Upstream/native Python type name or planned artifact type. |
| `data` | JSON-safe data or representation. |
| `metadata` | Adapter-specific metadata. |
| `warnings` | User-facing warnings and limitations. |
| `provenance` | Source and execution provenance. |
| `unsupported_reason` | Structured reason when no execution path exists. |

## 3. Required Behaviors

| Behavior | Requirement |
| --- | --- |
| `to_dict` | Return a JSON-safe dictionary. |
| `to_json` | Return sorted JSON for stable snapshots. |
| `validate` | Enforce required fields and capability level bounds. |

## 4. Provenance Payload

Minimum provenance keys:

- `ecosystem`;
- `upstream_package`;
- `upstream_version`;
- `dependency_extra`;
- `adapter`;
- `capability_level`;
- `mode`;
- `official_endorsement`: always false unless explicitly approved by upstream;
- `cloud_access`: false unless a future runtime stage explicitly enables it;
- `token_storage`: false;
- `source_code_copied`: false.

## 5. Unsupported Results

Unsupported paths should avoid vague failures. They should include:

- a stable `unsupported_reason`;
- dependency availability;
- required extra or environment lane;
- whether the limitation is advisory, offline-only, scaffold-only, or not
  planned;
- a warning that no production parity is claimed.

## 6. Compatibility Notes

The current `EcosystemResult` dataclass already provides:

- `schema_version`;
- `ecosystem`;
- `upstream_package`;
- `upstream_version`;
- `capability_level`;
- `mode`;
- `raw_type`;
- `data`;
- `metadata`;
- `provenance`;
- `warnings`;
- `to_dict`;
- `to_json`;
- `validate`.

Stage 8A does not remove or rename any existing field. Later stages may add
`quantumbridge_version` and `unsupported_reason` as optional metadata keys
before promoting them to first-class dataclass fields.
