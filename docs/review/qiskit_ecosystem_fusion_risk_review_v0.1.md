# Qiskit Ecosystem Fusion Risk Review v0.1

**Version**: v0.1  
**Date**: 2026-06-09  
**Status**: Stage 8A risk review  

## Summary

Overall risk is medium-high because the Qiskit ecosystem spans many optional
packages, domain-specific semantics, dependency constraints, and cloud/runtime
boundaries.

## Key Risks

| Risk | Level | Mitigation |
| --- | --- | --- |
| False replacement claim | High | Required non-goal language in docs, README, warnings. |
| Runtime credential exposure | High | Runtime remains offline-only; no token reads or storage. |
| Domain overclaim | High | Finance, ML, optimization, chemistry, experiments, dynamics, and Metal are not production-grade. |
| Dependency conflicts | High | Separate extras and constraints by ecosystem lane. |
| API drift | Medium | Inventory snapshots and version provenance. |
| Advisory package failures | Medium | Advisory workflow lanes may continue on error when clearly labeled. |
| Result semantic mismatch | Medium | Schema wrappers must include raw type, mode, warnings, and provenance. |
| Upstream endorsement implication | High | No official endorsement claim. |

## Required Warnings

Adapters must warn when support is scaffold-only, advisory, offline-only, or
dependent on an optional package that is not installed.

Qiskit Runtime-specific warning:

```text
QuantumBridge qiskit-runtime support is offline-only in this stage. It does not
access IBM Cloud, read tokens, store credentials, or submit jobs.
```

Qiskit Metal-specific warning:

```text
QuantumBridge qiskit-metal support is advisory only. It is not executable chip
design, EM simulation, layout signoff, or fabrication support.
```

## Test Expectations

- Core tests pass without Qiskit ecosystem packages.
- Optional package lanes either pass when installed or skip clearly when absent.
- Advisory lanes do not imply production support.
- Runtime lanes verify offline-only behavior.
- Result wrappers validate schema fields and provenance.
