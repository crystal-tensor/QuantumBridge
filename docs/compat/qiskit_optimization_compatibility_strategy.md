# Qiskit Optimization Compatibility Strategy

Status: Stage 9B executable subset
Detailed companion: `docs/compat/strategy/qiskit_optimization_compatibility_strategy.md`

## Scope

QuadraticProgram, converters, translators, algorithms, minimum-eigen optimizer paths, and small optimization problem smoke tests. Stage 9B adds an independently implemented minimal binary QuadraticProgram subset.

## Non-goals

No full optimization-suite parity, no production optimizer guarantees, and no CPLEX/DOcplex bundling.

## Optional Dependency

Install with `.[qiskit-optimization]`.

## Inventory Status

Current local environment records dependency-not-installed placeholders for upstream `qiskit-optimization`; the native minimal subset does not require the upstream package.

## Adapter Status

Level 0/1 passthrough scaffold remains for most upstream APIs. Stage 9B adds Level 3 native support for small binary QuadraticProgram examples and Level 2/3 result schemas.

## Native Status

Native support is limited to:

- binary variables;
- linear and quadratic objectives;
- linear equality and inequality constraints;
- deterministic brute-force exact solving for small problems;
- QUBO and Ising metadata.

This is not a full native clone of Qiskit Optimization.

## Unsupported Status

Complete converter/optimizer parity, production solver behavior, continuous/integer-variable support beyond binary, advanced algorithms, and performance guarantees are unsupported.

## Tests

Tests cover native binary QuadraticProgram creation, objective evaluation, constraints, brute-force solving, QUBO and Ising metadata, result schemas, optional upstream passthrough, no cloud/token/hardware access, schema wrapping, and unsupported warnings.

## Legal / Attribution

Qiskit Optimization remains upstream. No source is vendored.

## Risk

Medium to high due to solver dependency and optimizer behavior drift.
