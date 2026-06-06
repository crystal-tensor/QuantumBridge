# Qiskit Aer Compatibility Strategy

Status: Stage 7 planning
Detailed companion: `docs/compat/strategy/qiskit_aer_compatibility_strategy.md`

## Scope

AerSimulator, simulator methods, primitives if available, and noise models.

## Non-goals

No native Aer reimplementation, performance parity, or production noisy execution guarantee.

## Optional Dependency

Install with `.[qiskit-aer]`.

## Inventory Status

Current local environment has Qiskit Aer installed and generated runtime inventory.

## Adapter Status

Level 0/1 scaffold; result wrappers carry provenance.

## Native Status

QuantumBridge native simulator/noise modules remain independent and limited.

## Unsupported Status

Full Aer simulator method parity and noise-model behavioral equivalence are unsupported.

## Tests

Tests cover AerSimulator availability, statevector smoke, density-matrix smoke, noise model availability, wrapper provenance, and unsupported warnings.

## Legal / Attribution

Qiskit Aer remains upstream. No source is vendored.

## Risk

Medium due to simulator method availability and upstream version drift.
