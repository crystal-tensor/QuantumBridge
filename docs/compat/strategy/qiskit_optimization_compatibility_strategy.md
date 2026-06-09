# Qiskit Optimization Compatibility Strategy

Status: Stage 9B executable subset
Mode: optional dependency, adapter scaffold, and bounded native educational subset

## Goal

QuantumBridge inventories and selectively adapts Qiskit Optimization QuadraticProgram, converter, and optimizer surfaces. Stage 9B adds the first executable native subset for small binary QuadraticProgram examples.

## Initial Focus

- Level 0 inventory for public names.
- Level 1 passthrough for installed objects.
- Level 2 schema wrappers and QUBO/Ising metadata.
- Level 3 native minimal binary QuadraticProgram exact enumeration.

## Non-goals

QuantumBridge does not claim complete mathematical-programming coverage, optimizer parity, production optimization guarantees, cloud execution, token access, hardware execution, or IBM/Qiskit endorsement.
