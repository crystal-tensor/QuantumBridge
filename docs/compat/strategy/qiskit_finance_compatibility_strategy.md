# Qiskit Finance Compatibility Strategy

Status: Stage 7 planning  
Mode: optional dependency and adapter scaffold

## Goal

QuantumBridge will provide inventory and passthrough scaffolds for selected Qiskit Finance application, data-provider, circuit-library, and uncertainty-model objects.

## Scope

Stage 7 supports dependency detection, version capture, public-name inventory, passthrough object lookup, result wrapping, and provenance metadata. Domain validation, pricing accuracy, and production finance claims are out of scope.

## Adapter Boundary

Future Level 2 adapters may convert finance problem outputs into QuantumBridge optimization or Hamiltonian schemas after review. Stage 7 does not implement production portfolio, derivative pricing, or risk analytics.

## Risks

- Financial semantics are domain-sensitive.
- Data providers may have separate service terms.
- Upstream dependencies may conflict with other optional environments.
