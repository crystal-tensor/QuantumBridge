# Core Functional Parity Ledger

## Stage 11L Compiler Checkpoint (2026-10-19)

| Capability | Evidence/status | Remaining gap |
| --- | --- | --- |
| Native DAG/mutation/roundtrip | native implemented/tested | Full graph API/noncontiguous contraction partial |
| PassManager/PropertySet/stages | native implemented/tested | Full DAG-pass/flow-controller/plugin protocol partial |
| Target/CouplingMap/Layout | native implemented/tested | Full backend/calibration schema partial |
| Algebraic basis translation | native tested + 12 public differential scenarios | Arbitrary synthesis/all gates unsupported |
| Directed routing/permutation | native tested | Optimal/stochastic routing search not started |
| Safe local optimization | native tested | General commutation synthesis not started |
| ASAP/ALAP static scheduling | native tested | Pulse/calibration/dynamic global timing unsupported |
| Dynamic block compilation | native tested for if/for/while/switch/store/break/continue | Dynamic global schedule unsupported |
| Parameter AST/compiled QNode | native/Torch/Autograd tested | Restored identity layout/equal width only; JAX/TF/higher-order gaps unchanged |
| Compiled 100-qubit MPS | native tested with dense calls disabled | Arbitrary entanglement efficiency not claimed |
| QOS-UQCI/Quafu-style target | offline configuration tested | Real cloud/hardware verification not performed |

Full replacement/full parity remains **incomplete**. Stage 11K and earlier
remaining gaps are not erased by compiler progress. See the Stage 11L report.

Updated: 2026-10-19, Stage 11K. Full replacement/full functional parity is the
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

## Stage 11K Differentiation Evidence

Status is scoped to the tested native subset, never an entire upstream module.
NATIVE_IMPLEMENTED means code executes; NATIVE_TESTED means independent
behavioral tests pass; UPSTREAM_DIFFERENTIAL_TESTED adds public black-box evidence.

| Capability | Status | Evidence / remaining gap |
| --- | --- | --- |
| QNode forward / nested measurement trees | NATIVE_TESTED; PARTIAL | Existing/new QNode tests; full signatures/plugins/broadcasting/executors still open |
| Gate-occurrence parameter shift / shared input chain | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Native math and fourteen public gradient scenarios; full generator family/loop recipes open |
| Finite difference | NATIVE_TESTED; PARTIAL | Convergence against analytic derivatives; not a surrogate for adjoint/backprop |
| Pure vector analytic adjoint | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Actual inverse-state/reverse-cotangent algorithm and public oracle comparisons; mixed/MPS/stochastic adjoint unsupported |
| Simulator-level backprop | NOT_STARTED / UNSUPPORTED | Framework native VJP is not simulator backprop |
| VJP / JVP / execute-and-derivative methods | NATIVE_TESTED; PARTIAL | Shape/tree/numerical tests; currently explicit Jacobian products, not complete device derivative protocols |
| Torch backward / gradcheck / optimizer | NATIVE_TESTED; PARTIAL | True CPU tensor graph with native quantum VJP; GPU/higher order/open device contracts unsupported |
| JAX grad / jacrev / JIT / VMAP | NOT_STARTED / UNSUPPORTED | Array helper is not differentiable QNode integration |
| Autograd grad / jacobian / optimizer | NATIVE_TESTED; PARTIAL | Real primitive VJP plus classical preprocessing; higher order unsupported |
| TensorFlow GradientTape | NOT_STARTED / UNSUPPORTED | No fake gradient helper; future optional isolated framework verification required |
| Shot vectors | NATIVE_TESTED; PARTIAL | None/int/partitions/copies, actual sampled statistics and per-measurement metadata; full upstream shot contracts open |
| Dynamic QNode gradients | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Full branch probabilities and conditional angles; nonsmooth thresholds/postselection/reused loop angles unsupported |
| MPS gradients | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Tensor-native shift/finite-diff and no-dense 100-qubit local gradient; truncation warning/resource profiles retained |
| Higher-order derivatives | UNSUPPORTED | Explicit first-order guards in native/Torch/Autograd paths |
| Capture | NOT_STARTED | No capture/Catalyst parity claim |
| Complete gradient/transform execution | PARTIAL | Existing transforms plus QNode derivatives; complete transform/batch/plugin contracts remain open |

Implementation detail: docs/implementation/stage11k_native_qnode_autodiff_report.md.
The original full core ledger remains authoritative; none of these narrow tests
establish full Qiskit/PennyLane replacement.
