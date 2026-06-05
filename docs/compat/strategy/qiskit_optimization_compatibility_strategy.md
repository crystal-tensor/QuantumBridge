# Qiskit Optimization Compatibility Strategy

Status: Stage 7 planning  
Mode: optional dependency and adapter scaffold

## Goal

QuantumBridge will inventory and selectively adapt Qiskit Optimization QuadraticProgram, converter, and optimizer surfaces.

## Initial Focus

- Level 0 inventory for public names.
- Level 1 passthrough for installed objects.
- Future Level 2 conversion between QuadraticProgram-like objects and QuantumBridge optimization/Hamiltonian schemas.

## Non-goals

QuantumBridge does not claim complete mathematical-programming coverage, optimizer parity, or production optimization guarantees in Stage 7.
