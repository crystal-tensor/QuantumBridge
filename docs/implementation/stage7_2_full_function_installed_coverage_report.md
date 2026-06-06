# Stage 7.2 Full Function Installed Coverage Report

Status: local implementation and isolated verification complete
Date: 2026-06-06

## 1. Branch

`p2/ecosystem-full-coverage-planning`

## 2. Base Commit

Stage 7.2 started from `aaf5d32ecc90d418fae94f7f34ca989b5b605513`. The final Stage 7.2 commit is recorded after review and commit.

## 3. Installed Environment Results

The verifier created one temporary Python 3.12.6 virtual environment per optional extra. It did not install an all-optional environment.

| Profile | Version | Status | Tests | pip check |
| --- | --- | --- | --- | --- |
| qiskit-nature | qiskit-nature 0.8.0; qiskit-algorithms 0.4.0; PySCF 2.13.1; OpenFermion 1.7.1 | verified | 7 passed | clean |
| qiskit-finance | 0.4.1 | verified | 6 passed | clean |
| qiskit-algorithms | 0.4.0 | verified | 9 passed | clean |
| qiskit-machine-learning | 0.9.0 | verified | 7 passed | clean |
| qiskit-optimization | 0.7.0 | verified | 7 passed | clean |
| qiskit-dynamics | 0.6.0 | verified, advisory | 4 passed | clean |
| qiskit-experiments | 0.14.1 | verified, advisory | 5 passed | clean |
| qiskit-metal | unresolved | install failed, advisory | not run | not run |
| qiskit-aer | 0.17.2 | verified | 7 passed | clean |
| pennylane-full | 0.42.3 | verified | 7 passed | clean |

Machine-readable evidence is stored in `docs/compat/inventory/stage7_2_installed_env_report.json`.

## 4. Inventory Results

| Ecosystem | Public API records | Unsupported/import-risk records |
| --- | ---: | ---: |
| Nature | 140 | 0 |
| Finance | 27 | 0 |
| Algorithms | 168 | 0 |
| Machine Learning | 21 | 0 |
| Optimization | 65 | 0 |
| Dynamics | 29 | 1 |
| Experiments | 22 | 1 |
| Metal | 0 installed | 5 planned/missing |
| Aer | 24 | 0 |
| PennyLane full | 444 | 0 |

Counts describe runtime public-name inventory, not complete semantic compatibility.

## 5. Coverage Levels

- Level 0: runtime inventory exists for all planned ecosystems; Metal remains missing-package inventory.
- Level 1: installed passthrough smoke is verified for nine ecosystems. Metal is not Level 1.
- Level 2: independently implemented and installed-environment-verified result-schema wrappers exist for Chemistry, Finance, Algorithms, ML, Optimization, Dynamics, Experiments, Aer, and PennyLane. A Metal design schema is defined but is not counted as Level 2 because upstream installation failed.
- Level 3: no new ecosystem-native reimplementation was added. Existing QuantumBridge core remains separate.
- Level 4: not promised.

## 6. Nature

Qiskit Nature, PySCF, OpenFermion, and Qiskit Algorithms installed together in the isolated Nature lane. The tests ran a real STO-3G PySCF driver workflow for H2 and smoke workflows for LiH and H2O. This is not a production chemistry or materials band-gap claim.

## 7. Finance

Qiskit Finance installed successfully. Portfolio, option-pricing, and data-provider public availability checks passed without market-data network access. FinanceResult is a schema wrapper, not financial validation.

## 8. Algorithms

Qiskit Algorithms installed successfully. VQE, QAOA, SamplingVQE, NumPy eigensolvers, VQD, Grover, amplitude-estimation inventory, optimizers, and gradients were verified at passthrough/inventory level.

## 9. Machine Learning

QNN, kernels, classifier, regressor, dataset, and TorchConnector surfaces were inventoried and tested. No training performance or production inference claim is made.

## 10. Optimization

QuadraticProgram, converters, optimizers, and application surfaces installed and passed smoke tests. No solver parity or production optimization guarantee is made.

## 11. Dynamics

Qiskit Dynamics installed and passed Solver/model/signal/backend smoke tests. One optional submodule inventory entry remained unavailable. The lane is advisory and does not establish production control-system behavior.

## 12. Experiments

Qiskit Experiments installed and passed offline inventory/schema tests. One optional submodule inventory entry remained unavailable. No backend, calibration, or laboratory claim is made.

## 13. Metal

The `qiskit-metal` installation failed on Python 3.12.6 while resolving legacy pinned build dependencies, including old NumPy/matplotlib/gdspy build paths. The observed final failure was a build-backend availability error while preparing legacy source distributions. This remains an advisory compatibility risk. QuantumBridge does not claim installed Metal support, EM simulation, or fabrication readiness.

Recommended follow-up: investigate a dedicated supported Python version and upstream-maintained package path before changing the extra.

## 14. Aer

Qiskit Aer installed and passed statevector, density-matrix, noise-model, and schema smoke tests. QuantumBridge does not claim Aer implementation or performance parity.

## 15. PennyLane Full

The isolated constraints resolved PennyLane 0.42.3 with `autoray<0.8`. Operations, measurements, QNode, devices, qchem, gradients, transforms, templates, resources, and result-schema tests passed. This does not establish complete PennyLane replacement or plugin parity.

## 16. Repository Tests

- `python3 -m pytest -q -rs`: 150 passed, 3 skipped.
- `python3 -m pytest --cov=quantumbridge`: 150 passed, 3 skipped.
- Total coverage: 91%.
- Targeted ecosystem suite before final integration: 82 passed, 3 skipped.

The three main-environment skips were caused by optional packages absent from that environment. Dynamics and Optimization passed in their isolated installed environments.

## 17. Local Matrix

`bash scripts/run_local_matrix.sh` completed successfully. Its Python 3.9/default-pytest lane reported 138 passed and 15 optional skips, then completed inventory and coverage successfully at 91%. Isolated verification is the authoritative evidence for extras not installed in that default environment.

## 18. CI

The workflow includes separate jobs for Nature, Finance, Algorithms, Machine Learning, Optimization, Dynamics, Experiments, Metal, Aer, PennyLane full, and ecosystem inventory. Dynamics, Experiments, Addons, Runtime, and Metal are advisory where configured. Remote GitHub Actions still requires user confirmation after push.

## 19. Dependency Conflicts

No conflict was found in the nine verified isolated environments. The project still does not require all optional dependencies to coexist. Metal has a Python/build-stack compatibility failure rather than a verified coexistence path.

## 20. Unsupported Claims

The implementation does not claim full replacement, full parity, official endorsement, production chemistry, production finance, production ML, production dynamics, production experiments, chip fabrication, materials band gap, IBM Cloud access, or native Aer/PennyLane equivalence.

## 21. Legal / Attribution

Third-party notices, migration ledger, Qiskit/PennyLane ecosystem attribution, and the Stage 7.2 attribution review were updated. No upstream source or installed package tree was committed.

## 22. Review Recommendation

Recommend entering Stage 7.2 Review after remote CI completes.

## 23. Merge Recommendation

Do not merge until remote non-advisory jobs pass and reviewers accept Metal as a documented advisory failure.

## 24. Release Recommendation

Do not publish `v0.3.0-ecosystem-alpha1` yet. A release candidate can be reconsidered after remote CI, dependency/license review, and Stage 7.2 review approval.
