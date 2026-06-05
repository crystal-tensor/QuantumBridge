# Qiskit Aer Compatibility Strategy

Status: Stage 7 planning  
Mode: optional dependency and passthrough scaffold

## Goal

QuantumBridge will support Qiskit Aer as an optional upstream simulator dependency through passthrough and result wrapping. Native QuantumBridge simulation and noise paths remain independently implemented.

## Initial Coverage

Stage 7 provides dependency detection, version reporting, public-name inventory, AerSimulator lookup when installed, noise-model inventory, schema wrapping, and provenance metadata.

## Non-goals

- Native reimplementation of Aer internals.
- Claiming Aer-level simulator performance.
- Hardware noise accuracy claims.
- Production noisy execution guarantees.
