# Qiskit Optimization Compatibility Strategy

Status: Stage 7 planning
Detailed companion: `docs/compat/strategy/qiskit_optimization_compatibility_strategy.md`

## Scope

QuadraticProgram, converters, translators, algorithms, minimum-eigen optimizer paths, and small optimization problem smoke tests.

## Non-goals

No full optimization-suite parity, no production optimizer guarantees, and no CPLEX/DOcplex bundling.

## Optional Dependency

Install with `.[qiskit-optimization]`.

## Inventory Status

Current local environment records dependency-not-installed placeholders; remote extra CI should validate installed inventory.

## Adapter Status

Level 0/1 scaffold only.

## Native Status

No native QuadraticProgram clone.

## Unsupported Status

Complete converter/optimizer parity and production solver behavior are unsupported.

## Tests

Tests cover QuadraticProgram, converter, optimizer availability, a tiny problem smoke when installed, schema wrapping, and unsupported warnings.

## Legal / Attribution

Qiskit Optimization remains upstream. No source is vendored.

## Risk

Medium to high due to solver dependency and optimizer behavior drift.
