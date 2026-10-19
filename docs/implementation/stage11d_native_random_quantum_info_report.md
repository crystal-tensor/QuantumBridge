# Stage 11D Native Random Quantum Information Report

Date: 2026-10-19

## Scope

This slice adds native seeded generators and Pauli-basis construction to the
shared QuantumBridge information layer. The capability remains shared
infrastructure beneath the canonical four product categories.

## Implemented capability

- Seeded Gaussian-unitary-ensemble `random_hermitian`.
- Optional traceless Hermitian generation.
- Ordered and Pauli-weight-ordered `pauli_basis`.
- Seeded Haar-isometry `random_quantum_channel`.
- Explicit input dimension, output dimension, and Kraus rank control.
- Rectangular Stinespring dimension metadata for generated channels.
- Native exposure through the Qiskit quantum-info adapter.

## Validation

Focused native and installed-Qiskit tests pass:

```text
10 passed
```

Hermitian seeded values and both Pauli-basis orders match Qiskit 2.6.0 exactly.
Random-channel parity verifies dimensions, Stinespring shape, Kraus rank, and
CPTP behavior.

The staged change applied to a clean tracked archive passes the complete suite:

```text
639 passed, 4 skipped
```

## Risk and non-goals

- QuantumBridge and Qiskit use valid but different random-isometry sampling
  procedures, so an equal seed does not imply equal channel matrix entries.
- Native `Operator` currently limits random Hermitian output to qubit-sized
  dimensions.
- Random Pauli, Pauli-list, Clifford, and CNOT-dihedral generation remain
  future work.
- This does not claim complete `qiskit.quantum_info`, Qiskit, or PennyLane
  parity.
- No frontend, Studio, industry workflow, or third-party source is included.

## Result

The native quantum-info adapter now exposes 38 of 60 public symbols observed in
the installed Qiskit 2.6.0 environment. Behavior evidence, not the inventory
ratio alone, remains the completion criterion.
