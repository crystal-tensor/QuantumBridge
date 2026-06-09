# QOS-UQCI Compatibility Strategy

**Version**: v0.1  
**Date**: 2026-06-09  
**Status**: Stage 8A planning  

## 1. Position

QOS-UQCI is treated as an optional external compatibility target. QuantumBridge
must not vendor QOS-UQCI source code or claim production runtime/hardware
support.

The UQCI IR is the canonical source of truth for this compatibility path.
OpenQASM is a compatibility artifact for import/export, not the canonical model.

## 2. Planned Conversion Paths

| Path | Purpose | Stage |
| --- | --- | --- |
| QuantumBridge IR -> UQCI IR | Export QuantumBridge circuits/workflows to UQCI-compatible IR. | 8G |
| UQCI IR -> QuantumBridge IR | Import UQCI-compatible bundles into QuantumBridge. | 8G |
| UQCI IR -> OpenQASM | Compatibility export. | 8G |
| OpenQASM -> UQCI IR | Compatibility import with warnings. | 8G |

## 3. Planned Metadata Objects

- UQCI bundle metadata;
- `DeviceSpec`;
- `CalSet`;
- `Manifest`;
- provenance;
- warnings;
- unsupported reasons.

## 4. Planned Directory

Stage 8A documents this directory but does not implement it:

```text
quantumbridge/compat/qos_uqci/
  __init__.py
  dependency.py
  uqci_ir_adapter.py
  bundle_adapter.py
  devicespec_adapter.py
  calset_adapter.py
  manifest_adapter.py
  openqasm_bridge.py
  backend_adapter.py
  result_adapter.py
  warnings.py
```

## 5. Runtime Policy

Allowed:

- mock backend planning;
- offline schema and provenance design;
- import/export contract design;
- validation against local fixtures in future stages.

Forbidden:

- real hardware access;
- token storage;
- cloud submission;
- production runtime claim;
- copied QOS-UQCI source code;
- official endorsement claim.

## 6. Adapter Contract

QOS-UQCI adapters must follow the common ecosystem adapter contract:

- dependency availability;
- version/spec availability;
- public artifact inventory;
- object lookup where applicable;
- schema wrapping;
- provenance;
- warnings;
- unsupported reasons;
- environment validation.
