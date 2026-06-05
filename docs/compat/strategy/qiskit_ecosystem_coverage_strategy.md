# Qiskit Ecosystem Coverage Strategy

Status: Stage 7 planning  
Mode: optional dependency, public API inventory, passthrough, and selective adapter integration

## Goal

QuantumBridge will inventory and selectively adapt Qiskit ecosystem packages without claiming to replace Qiskit or to provide full feature parity. Qiskit ecosystem packages remain upstream optional dependencies.

## Package Groups

- Qiskit core: circuit, transpiler, quantum_info, primitives, and result objects.
- Qiskit Aer: simulator and noise-model passthrough, with native QuantumBridge noise paths kept separate.
- Qiskit IBM Runtime: runtime/backend/job object passthrough only; credentials and service execution remain user-managed.
- Qiskit Experiments: inventory first, with adapter decisions deferred until review.
- Qiskit Addons: SQD, MPF, AQC, and OBP inventory first; no source migration in Stage 7.

## Initial Coverage

Stage 7 is Level 0 to Level 1 for most public APIs. Existing P1 Qiskit circuit import/export remains a small Level 2 adapter for the reviewed subset.

## Review Gate

A public API may move from Level 1 to Level 2 only after:

- schema target is defined;
- tests are based on public behavior, not upstream tests;
- dependency lane is isolated in CI;
- attribution and ledger entries are updated.

## Non-goals

- Full transpiler parity.
- Hardware provider replacement.
- Runtime service emulation.
- Native Aer simulator reimplementation.
- Vendor copy of Qiskit ecosystem source.
