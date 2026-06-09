# Qiskit Aer Compatibility Strategy

Status: Stage 9F executable educational slice
Mode: optional dependency, passthrough scaffold, and native educational simulator subset

## Goal

QuantumBridge supports Qiskit Aer as an optional upstream simulator dependency through passthrough and result wrapping. Stage 9F adds independently implemented native educational statevector, qasm-style counts, and simple sampling-noise workflows for small circuits.

## Initial Coverage

Stage 7 provides dependency detection, version reporting, public-name inventory, AerSimulator lookup when installed, noise-model inventory, schema wrapping, and provenance metadata.

Stage 9F provides executable native educational workflows for 1-4 qubit circuits, basic gates, statevector output, seeded counts, simple measurement bit-flip noise, optional upstream passthrough, and Aer result schemas.

## Non-goals

- Native reimplementation of Aer internals.
- Claiming Aer-level simulator performance.
- Claiming Qiskit Aer noise-model parity.
- Hardware noise accuracy claims.
- Production noisy execution guarantees.
