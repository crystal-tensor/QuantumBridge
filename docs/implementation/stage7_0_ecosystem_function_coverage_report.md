# Stage 7.0 Ecosystem Function Coverage Report

Status: local verification complete
Branch: p2/ecosystem-full-coverage-planning

## 1. New / Modified Files

Added ecosystem registry, adapter scaffolds, inventory scripts, coverage matrices, strategy docs, legal attribution docs, constraints files, CI matrix entries, README updates, and tests under:

- `quantumbridge/ecosystem/`
- `quantumbridge/compat/qiskit_core/`
- `quantumbridge/compat/qiskit_aer/`
- `quantumbridge/compat/qiskit_runtime/`
- `quantumbridge/compat/qiskit_finance/`
- `quantumbridge/compat/qiskit_optimization/`
- `quantumbridge/compat/qiskit_machine_learning/`
- `quantumbridge/compat/qiskit_experiments/`
- `quantumbridge/compat/qiskit_addons/`
- `quantumbridge/compat/pennylane_full/`
- `scripts/inventory_*_api.py`
- `docs/compat/inventory/`
- `docs/compat/matrix/`
- `tests/ecosystem/`
- `tests/compat_qiskit_*`
- `tests/compat_pennylane_full/`

## 2. Supported Ecosystem Packages

Stage 7 supports planning and scaffold coverage for Qiskit core, Qiskit Aer, Qiskit IBM Runtime, Qiskit Finance, Qiskit Optimization, Qiskit Machine Learning, Qiskit Experiments, Qiskit Addons, and PennyLane full-ecosystem modules.

## 3. Local Package Versions

Runtime inventory found installed Qiskit core, Qiskit Aer, and PennyLane packages in the local environment:

- `qiskit==2.4.1`
- `qiskit-aer==0.17.2`
- `pennylane==0.44.1`

Finance, Optimization, Machine Learning, Runtime, Experiments, and Addons were not installed locally and were recorded as optional dependency placeholders.

## 4. Coverage Counts

| Ecosystem | Level 0 inventory records | Installed public-name records | Level 1 passthrough scaffold | Level 2 adapter | Level 3 native |
| --- | ---: | ---: | --- | --- | --- |
| Qiskit core | 304 | 304 | Yes | Existing P1 subset only | No |
| Qiskit Aer | 24 | 24 | Yes | No | No |
| Qiskit Finance | 4 | 0 | Yes when installed | No | No |
| Qiskit Optimization | 4 | 0 | Yes when installed | No | No |
| Qiskit Machine Learning | 4 | 0 | Yes when installed | No | No |
| Qiskit IBM Runtime | 3 | 0 | Yes when installed | No | No |
| Qiskit Experiments | 3 | 0 | Yes when installed | No | No |
| Qiskit Addons | 4 | 0 | Yes when installed | No | No |
| PennyLane full | 442 | 442 | Yes | Existing P1 subset only | No |

## 5. Finance Coverage

Finance coverage is Level 0/1 scaffold. Tests cover PortfolioOptimization, EuropeanCallPricing, RandomDataProvider availability when installed, dependency-missing behavior, provenance, and unsupported warnings. No production finance is claimed.

## 6. Optimization Coverage

Optimization coverage is Level 0/1 scaffold. Tests cover QuadraticProgram, converter and optimizer availability, simple problem smoke when installed, schema wrapper, provenance, and unsupported warnings.

## 7. Machine Learning Coverage

Machine Learning coverage is Level 0/1 scaffold. Tests cover QNN, kernel, classifier, TorchConnector lanes, wrappers, provenance, and unsupported warnings. No training or production ML claim is made.

## 8. Aer Coverage

Aer coverage is Level 0/1 scaffold with local installed smoke tests for AerSimulator statevector and density-matrix methods, plus noise-model availability. No Aer parity is claimed.

## 9. PennyLane Full Coverage

PennyLane full coverage is Level 0/1 scaffold across operations, measurements, QNode, devices, qchem, transforms, gradients, templates, resources, and plugin-adjacent inventory. Existing P1 tape/observable support remains the only Level 2 subset.

## 10. Nature / Algorithms Stage 6 Status

Qiskit Nature, Qiskit Algorithms, PySCF, OpenFermion, and Quafu remain part of the separate Stage 6 dual-track branch and PR review context. Stage 7 planning does not vendor or merge those upstream packages into core.

## 11. Tests

- `pytest -q -rs tests/ecosystem tests/compat_qiskit_finance tests/compat_qiskit_optimization tests/compat_qiskit_machine_learning tests/compat_qiskit_aer tests/compat_pennylane_full`: 33 passed, 1 skipped.
- `pytest -q -rs`: 101 passed, 1 skipped.
- `pytest --cov=quantumbridge`: 101 passed, 1 skipped, total coverage 85%.
- `bash scripts/run_local_matrix.sh`: passed; local Finance/Optimization/ML lanes were unavailable and reported as not executed.

## 12. Skipped Tests

Local pytest skipped one qiskit-optimization simple problem smoke because qiskit-optimization was not installed. Local matrix skipped optional Finance, Optimization, and Machine Learning compatibility subsets because those optional packages were not installed in this environment.

## 13. Failed Optional Dependencies

No optional dependency install was attempted locally for missing ecosystems in this stage. CI matrix will install each extra separately.

## 14. CI Matrix

Added `qiskit-aer-extra`, `qiskit-finance-extra`, `qiskit-optimization-extra`, `qiskit-machine-learning-extra`, `pennylane-full-extra`, and `ecosystem-inventory`. Each job installs only the relevant extra.

## 15. Legal / Attribution

Updated `THIRD_PARTY_NOTICES.md`, `docs/migration/source_migration_ledger.md`, `docs/legal/third_party_source_policy.md`, and added Qiskit/PennyLane ecosystem attribution docs. No third-party source was vendored.

## 16. Stage 7 Review Recommendation

Recommend entering Stage 7 Review after rerunning the full test suite with expanded tests and after remote CI validates optional extras.

## 17. v0.2.0-alpha1 Recommendation

Do not publish v0.2.0-alpha1 from this branch until Stage 7 Review and remote matrix validation pass.

## 18. v0.3.0 Ecosystem Beta Recommendation

Begin planning v0.3.0 ecosystem beta only after Level 2 schema targets are reviewed for specific high-value workflows.
