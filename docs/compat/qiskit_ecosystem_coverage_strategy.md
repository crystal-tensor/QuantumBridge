# Qiskit Ecosystem Coverage Strategy

Status: Stage 7 planning  
Detailed companion: `docs/compat/strategy/qiskit_ecosystem_coverage_strategy.md`

## Scope

Qiskit core, Aer, IBM Runtime, Finance, Optimization, Machine Learning, Experiments, Addons, and the Stage 6 Nature/Algorithms/chemistry lane are treated as optional dependency ecosystems.

## Non-goals

No full replacement, no full parity, no official endorsement, no hardware-service emulation, no production finance/ML/chemistry/materials claims, and no vendored upstream source.

## Optional Dependency

Each package is installed through an explicit extra such as `qiskit-core`, `qiskit-aer`, `qiskit-finance`, `qiskit-optimization`, or `qiskit-machine-learning`.

## Inventory Status

Stage 7 generates JSON and Markdown matrices under `docs/compat/inventory/` and `docs/compat/matrix/` by runtime public-name introspection.

## Adapter Status

New modules are Level 0 inventory and Level 1 passthrough scaffolds. Existing P1 circuit/result conversion remains the reviewed Level 2 subset.

## Native Status

Native work is limited to QuantumBridge core modules: IR, result schema, compiler/QASM plans, simulators, and reviewed schema conversion.

## Unsupported Status

Full transpiler parity, Runtime service replacement, Aer internals, production chemistry/finance/ML, and materials band gap are unsupported.

## Tests

Smoke tests cover dependency availability, inventory, versions, passthrough lookup where installed, wrappers, provenance, and unsupported warnings.

## Legal / Attribution

Qiskit ecosystem packages remain upstream projects. QuantumBridge uses package names only for compatibility and attribution.

## Risk

High-risk areas are cloud runtime credentials, finance semantics, machine-learning training claims, hardware experiments, addon availability, and transitive dependency conflicts.
