# Qiskit Ecosystem Fusion Risk Review v0.1

**Version**: v0.1  
**Date**: 2026-06-09  
**Status**: Stage 8D risk review

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
| Optional package absence | Medium | Contract returns dependency reports and unsupported metadata. |
| Inventory misread as support | Medium | Inventory records include supported, unsupported_reason, advisory, risk, and notes fields. |

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

## Stage 8D Risk Disposition

Stage 8D reduces adapter contract risk by adding one shared facade across the
Qiskit ecosystem adapters. Every adapter now reports capability level,
production-readiness status, native-implementation status, upstream dependency
status, warnings, provenance, and environment validation through the same
surface.

The largest remaining risks are dependency drift and domain overread. Generated
inventory should be treated as public-name coverage, not as evidence of runnable
QuantumBridge behavior. The Stage 8D schema wrappers preserve raw type,
upstream package, upstream version, warnings, and unsupported reasons so callers
can see the boundary explicitly.

Runtime and Metal remain high-sensitivity domains. Runtime tests must continue
to verify no cloud calls, no token reads, and no credential storage. Metal tests
must continue to verify advisory-only language and must not imply fabrication,
simulation, or layout signoff capability.

## Stage 9B Risk Disposition

Stage 9B introduces a bounded native optimization subset. The primary risks are
domain overread and solver overclaim:

- The native solver is deterministic brute-force enumeration for small binary
  problems only.
- QUBO and Ising outputs are metadata, not production solver certification.
- Optional upstream execution requires installed `qiskit-optimization` and
  `qiskit-algorithms` packages.
- The adapter must keep explicit warnings that this is not a full Qiskit
  Optimization replacement and not production optimization software.
- Tests must continue to verify no cloud access, no token reads, and no real
  hardware access.

## Stage 9D Risk Disposition

Stage 9D introduces a bounded native chemistry subset for H2 and LiH. The
primary risks are chemistry overclaim, upstream provenance confusion, and
materials-science overread:

- The native Hamiltonians are educational small-qubit models for exact
  diagonalization tests and examples, not production electronic-structure
  calculations.
- Optional Qiskit Nature / PySCF execution is local upstream passthrough and
  must remain labeled as upstream behavior.
- The adapter must keep explicit warnings that this is not a full Qiskit Nature
  replacement, not production quantum chemistry, and not a materials band-gap
  workflow.
- Tests must continue to verify no cloud access, no token reads, no hardware
  access, clear provenance, and no vendored chemistry stack artifacts.

## Stage 9E Risk Disposition

Stage 9E introduces a bounded native educational QML subset for toy datasets,
quantum kernels, kernel classifiers, QNN forward passes, and QNN classifiers.
The primary risks are ML-performance overclaim, production-readiness overclaim,
and high-risk automated-decision overread:

- The native workflows use deterministic toy datasets only, not real user data.
- The native kernel and QNN classifiers are educational small workflows, not
  production ML systems.
- Optional Qiskit Machine Learning execution is runtime introspection or clear
  unsupported metadata, not upstream behavior ownership.
- The adapter must keep explicit warnings that this is not a full Qiskit
  Machine Learning replacement, not production ML, and not intended for
  medical, financial, employment, identity, safety, or other high-risk
  automated decisions.
- Tests must continue to verify no cloud access, no token reads, no hardware
  access, clear provenance, and no vendored ML stack artifacts.

## Stage 9G Risk Disposition

Stage 9G introduces a bounded native educational error-mitigation subset. The
primary risks are production-readiness overclaim, Mitiq parity confusion,
hardware calibration overread, and statistical-performance overclaim:

- Native ZNE uses small simulated circuits and simple extrapolation only.
- Native readout mitigation uses educational calibration matrices, not hardware
  calibration data.
- Optional Mitiq handling is dependency detection and clearly labeled upstream
  passthrough metadata unless the caller supplies a real local executor.
- The adapter must keep explicit warnings that this is not a full Mitiq
  replacement and not production error-mitigation software.
- Tests must continue to verify no cloud access, no token reads, no hardware
  access, clear provenance, and no vendored Mitiq or Qiskit artifacts.
