# Qiskit Finance Compatibility Strategy

Status: Stage 9A executable subset update
Mode: optional dependency, adapter scaffold, and educational native portfolio subset

## Goal

QuantumBridge provides inventory and passthrough scaffolds for selected Qiskit Finance application, data-provider, circuit-library, and uncertainty-model objects. Stage 9A adds an independently implemented educational portfolio optimization subset that can solve small deterministic binary mean-variance examples by exact enumeration.

## Scope

Stage 7 supports dependency detection, version capture, public-name inventory, passthrough object lookup, result wrapping, and provenance metadata.

Stage 9A additionally supports:

- deterministic four-asset mean-variance portfolio optimization inputs;
- native exact enumeration for binary selections with a fixed budget;
- result serialization through `PortfolioOptimizationResult`;
- optional upstream exact / SamplingVQE / QAOA calls when Qiskit Finance, Qiskit Optimization, and Qiskit Algorithms are installed.

Domain validation, pricing accuracy, real market data, trading, advisory use, and production finance claims are out of scope.

## Adapter Boundary

Future adapters may convert more finance problem outputs into QuantumBridge optimization or Hamiltonian schemas after review. Stage 9A implements only a small educational native portfolio subset and optional upstream passthrough execution. It does not implement production portfolio, derivative pricing, credit risk, or market data analytics.

## Risks

- Financial semantics are domain-sensitive.
- Data providers may have separate service terms.
- Upstream dependencies may conflict with other optional environments.
- Educational exact enumeration does not scale to large portfolios.
