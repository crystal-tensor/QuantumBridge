# Contributing to QuantumBridge

QuantumBridge is an experimental SDK. Contributions must keep the current P1
scope clear: native SDK functionality plus optional compatibility layers, not
full replacement claims for Qiskit or PennyLane.

## Development Flow

1. Work from the repository design, roadmap, review, and implementation records.
2. Keep P1 maintenance changes small and reviewable.
3. Do not enter P2 feature implementation unless a P2 task is explicitly opened.
4. Run the local test suite before handoff.
5. Record meaningful engineering or compliance changes in the relevant docs.

## Tests

Run the standard suite:

```bash
pytest -q -rs
```

Run the local matrix simulation:

```bash
bash scripts/run_local_matrix.sh
```

Optional dependency tests should either pass when the dependency is installed or
skip/report unavailable with a clear reason.

## Optional Dependencies

Qiskit, PennyLane, Torch, and JAX are optional dependencies. Do not make core SDK
tests require these packages. Adapter tests must remain isolated to their
optional dependency paths.

## License and Attribution

QuantumBridge is distributed under Apache License 2.0. Keep the root `LICENSE`,
`NOTICE`, `THIRD_PARTY_NOTICES.md`, and files under `LICENSES/` intact.

Any new upstream dependency, adapter, or source-port decision must update
`docs/migration/source_migration_ledger.md`. Do not copy source code, tests,
comments, documentation prose, or error text from upstream projects unless the
project has explicitly approved a source-port task with attribution.

## Public Claims

Do not describe QuantumBridge as having full Qiskit or PennyLane feature parity.
Do not describe QuantumBridge as a complete replacement for Qiskit or PennyLane.
Do not imply endorsement by IBM, Xanadu, Qiskit, or PennyLane.
