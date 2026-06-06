# Stage 7.2 Full Function Coverage Matrix

Generated from isolated installed-environment verification on Python 3.12.6 and independently implemented QuantumBridge result wrappers.

| Ecosystem | Package | Version | Installed | Public API Count | Level 0 Count | Level 1 Count | Level 2 Count | Level 3 Count | Unsupported Count | Tests | Limitations |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Nature | qiskit-nature 0.8.0; PySCF 2.13.1; OpenFermion 1.7.1 | 0.8.0 | Yes | 140 | 140 | 140 | 1 | 0 | 0 | 7 passed; pip check clean | Not production chemistry; no band gap |
| Finance | qiskit-finance | 0.4.1 | Yes | 27 | 27 | 27 | 1 | 0 | 0 | 6 passed; pip check clean | No market network or production finance |
| Algorithms | qiskit-algorithms | 0.4.0 | Yes | 168 | 168 | 168 | 1 | 0 | 0 | 9 passed; pip check clean | No full algorithm parity |
| Machine Learning | qiskit-machine-learning | 0.9.0 | Yes | 21 | 21 | 21 | 1 | 0 | 0 | 7 passed; pip check clean | No production training |
| Optimization | qiskit-optimization | 0.7.0 | Yes | 65 | 65 | 65 | 1 | 0 | 0 | 7 passed; pip check clean | No solver parity |
| Dynamics | qiskit-dynamics | 0.6.0 | Yes | 29 | 29 | 29 | 1 | 0 | 1 | 4 passed; pip check clean | Advisory; one submodule unavailable; no control-system claim |
| Experiments | qiskit-experiments | 0.14.1 | Yes | 22 | 22 | 22 | 1 | 0 | 1 | 5 passed; pip check clean | Advisory; one submodule unavailable; no hardware calibration claim |
| Metal | qiskit-metal | unresolved | No | 0 | 0 | 0 | 0 | 0 | 5 | install failed before import | Schema defined but unverified; advisory Python 3.12 conflict with legacy pinned build stack |
| Aer | qiskit-aer | 0.17.2 | Yes | 24 | 24 | 24 | 1 | 0 | 0 | 7 passed; pip check clean | No Aer implementation parity |
| PennyLane | pennylane | 0.42.3 | Yes | 444 | 444 | 444 | 1 | 0 | 0 | 7 passed; pip check clean | Constraint resolution selected 0.42.3; no full PennyLane or plugin parity |

Level 4 production equivalence is not promised for any row.
