# Full Function Coverage Policy

QuantumBridge uses four levels for Qiskit Nature and Qiskit Algorithms
compatibility coverage.

## Level 0: Inventory Coverage

The public API has been identified and support status is recorded. This does not
mean the API is executable through QuantumBridge.

## Level 1: Adapter Coverage

The upstream package can be called through a QuantumBridge adapter when the
optional dependency is installed. Results are wrapped in QuantumBridge schema.
This is not native implementation.

## Level 2: Native Subset

QuantumBridge implements the behavior without upstream dependency and has
independent tests.

## Level 3: Production Equivalent

Behavior, edge cases, performance, and diagnostics approach upstream production
quality. P2 does not promise Level 3 coverage.

P2 targets Level 0 inventory for Qiskit Nature and Qiskit Algorithms, Level 1/2
for selected chemistry workflows, and no Level 3 production equivalence claim.
