# Core Functional Parity Ledger

Updated: 2026-10-19, Stage 11J. Full replacement/full functional parity is the
objective, not an achieved status. Inventory counts and line coverage are not
API/functionality coverage. Every row below remains PARTIAL or OPEN.

| Requirement | Current native evidence | Remaining functional work |
| --- | --- | --- |
| QuantumCircuit API | Parameters/expressions, compose/control/inverse/power, ordered reads, Stage 11J typed variables and runtime if/for/while/switch/break/continue/store | Complete signatures/builders, all classical types/expressions/scopes, calibration/schedule semantics and SDK equivalence |
| Circuit library | Existing standard-gate, ansatz, arithmetic, encoding tests | Full library families, parameters, decompositions and edge cases |
| Quantum information | Native states/operators/Pauli/channels/metrics/random/Clifford plus MPS; Stage 11B-I reports | All APIs/subsystem conventions, synthesis methods and dimensional/general-map contracts |
| Transpiler | Existing pass manager/target/routing subsets | Full DAG/layout/basis/scheduling/optimization; structured dynamic transpilation explicitly rejected pending implementation |
| Primitives V2 | Native Job/PUB/counts/observable workflows; exact dynamic branch expectations and finite-shot records | Complete broadcasting, precision/shot semantics, containers and error contracts |
| Provider/Backend/Job | Local native backends with dynamic execution | All discovery/options/async/cancellation/remote/provider contracts |
| QPY/QASM2/QASM3 | Existing QASM subset; executable native structured IR JSON with nested parameters | Complete standards, QPY interchange, dynamic source import/export and version coverage |
| Aer methods/noise/save | Vector/density/tableau/MPS execution and native noise/CPTP paths | Full AerSimulator interface, save/set snapshots, gate-attached noise, all methods/options and errors |
| Algorithms | Existing VQE/QAOA/Grover and bounded eigensolver/estimation paths | Complete algorithm families, result semantics and optimizers |
| Nature/Finance/Optimization/ML/Experiments/Dynamics | Mixed native executable slices and optional adapters; inspect per-project reports | Independent complete functions, industry workflows and behavioral parity; passthrough is not native parity |
| IBM Runtime | Offline/optional adapter work only | Authorized real service path and matching runtime contracts; no token/hardware evidence in Stage 11J |
| QNode execution | Native Tape callbacks, dynamic measure/cond/reset and multiple measurement types | Complete PennyLane QNode constructor/interfaces, shots/capture/executors/transforms and returned-tree protocols |
| PennyLane devices/plugins | Native vector/density/MPS/tableau devices and bridges | Full default/plugin/device API, all operations and device families |
| Observables/measurements | Native Pauli/Hamiltonian, state/probability/density/shadow subsets and dynamic measurements | Complete sparse/operator algebra and all measurement protocols |
| Transforms/gradients/interfaces | Existing finite-difference/shift/SPSA/QNG and interface subsets | Full native adjoint/backprop/gradient transforms and Torch/JAX/Autograd/TF end-to-end autodiff |
| Templates/qchem/math | Existing bounded templates and chemistry workflows | Complete templates, qchem, multi-interface math and differentiation contracts |
| Resources/kernels/qnn/qcut/shadows | Existing executable subsets only | Full resource estimation, kernels, QNN, cutting and shadow APIs |
| Quafu/QOS-UQCI and industries | Existing adapters/taxonomy; four categories/19 subdomains unchanged | Real authorized hardware validation and complete cross-domain workflows, separate from simulation evidence |

Primary Stage 11J evidence: tests/circuit (52 native scenarios),
tests/compat/test_dynamic_control_flow_differential.py (six optional black-box
comparisons), and docs/implementation/stage11j_native_dynamic_control_flow_report.md.
SDK-free tests prohibit upstream execution; the MPS 100-qubit test prohibits
dense expansion. Neither narrow proof establishes the full objective.

Priority after Stage 11J: native QNode/autodiff, complete transpilation, complete
serialization, full simulator noise/save/set and templates/qchem expansion.
Studio remains deferred until the core objective and hardware work are handled.
