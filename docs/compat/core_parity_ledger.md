# Core Functional Parity Ledger

Updated: 2026-10-20, Stage 11P-C bounded second-order checkpoint, starting from local `612c25a`.
This is the single current-status view. Full Qiskit/PennyLane functional
replacement remains **incomplete**. Line coverage, inventories, passthrough and
green CI are not proof of complete API coverage.

NATIVE_IMPLEMENTED means executable native code exists; NATIVE_TESTED adds
independent behavioral tests; UPSTREAM_DIFFERENTIAL_TESTED adds public black-box
evidence for the stated scenarios only. PARTIAL/UNSUPPORTED/NOT_STARTED describe
remaining scope. Stages 11M/11N pass the three clean tracked-tree local gates;
publication/exact-SHA CI is a separate receipt, not inferred from prior CI.

## Current Core Status

| Capability | Current evidence/status | Remaining functional work |
| --- | --- | --- |
| QuantumCircuit | NATIVE_TESTED; PARTIAL: typed storage, parameters, arithmetic, compose/control/inverse/power and runtime blocks | Complete builders/signatures, all types/scopes, calibrations and instruction schedules |
| Circuit library | NATIVE_TESTED; PARTIAL: standard gates, bounded ansatz/arithmetic/encoding | All library families and edge cases |
| Quantum information | NATIVE_TESTED; PARTIAL: vector/density/operators/Pauli/channels/metrics/random/Clifford/MPS | Full dimensional, subsystem, synthesis and general-map contracts |
| DAG/mutation/roundtrip | NATIVE_TESTED; PARTIAL: actual wire/classical dependencies and validation | Full graph API and noncontiguous contraction |
| PassManager/PropertySet | NATIVE_TESTED; PARTIAL: analysis lifetime, invalidation, prerequisites, callbacks, stages and limits | Full DAG-pass/flow-controller/plugin protocol |
| Target/CouplingMap/Layout | NATIVE_TESTED; PARTIAL: properties, directed paths, initial/final mapping | Full backend/calibration schema and optimal search |
| Basis translation/routing | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: exact phase, directed routing and permutation tracking | Arbitrary/all-gate synthesis and optimal/stochastic routing |
| Optimization | NATIVE_TESTED; PARTIAL: safe cancellation/identity/rotation merging | General commutation and synthesis methods |
| Static ASAP/ALAP | NATIVE_TESTED; PARTIAL: real configured durations, dependencies and alignment | Pulse/calibration and global dynamic timing UNSUPPORTED |
| Structured dynamic compilation | NATIVE_TESTED; PARTIAL: if/for/while/switch/store/break/continue actually compile and execute | Remaining branch/layout combinations and dynamic timing |
| Primitives V2 | NATIVE_TESTED; PARTIAL: native Job/PUB/counts/observables and dynamic results | Full broadcasting, precision/shots/containers/error protocol |
| Provider/Backend/Job | NATIVE_TESTED; PARTIAL: native local backends and jobs | Complete discovery/options/async/cancellation/remote contracts |
| Aer methods/noise/save | NATIVE_TESTED; PARTIAL: in-order Save/Set, gate-bound noise, CPU vector/density/tableau/MPS and bounded maps | Full API/performance/GPU/parallelism and remaining option/aggregation/readout contracts |
| Algorithms | NATIVE_TESTED; PARTIAL: bounded eigen/estimation and VQE/QAOA/Grover | All algorithm families, optimizers and result contracts |
| Nature/Finance/Optimization/ML/Experiments/Dynamics | PARTIAL: native executable slices and separate optional adapters | Complete independent industry functions; upstream passthrough is not parity |
| IBM Runtime | PARTIAL: offline/optional adapters | Authorized real service execution and complete runtime contracts |
| QNode/device/measurement | NATIVE_TESTED; PARTIAL: native vector/density/MPS/tableau, typed trees, dynamic measurements and ordered classical-record/quantum terminal samples | Complete constructor/plugins/devices/operations/measurement protocols; native record keyword API is not complete SDK MeasurementValue parity |
| Native parameter-shift/adjoint | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: actual first-order algorithms and classical chain rule | All generators/transforms, reused parameterized loops and mixed/MPS adjoint |
| VJP/JVP/execute derivatives | NATIVE_TESTED; PARTIAL | Current explicit Jacobian products are not full derivative-device contracts |
| Torch/Autograd | NATIVE_TESTED; PARTIAL: CPU framework graphs with true first/second native quantum derivatives | GPU, third/higher orders and full interface/device contracts |
| JAX | UPSTREAM_DIFFERENTIAL_TESTED first order; NATIVE_TESTED bounded second order; PARTIAL: CPU PyTrees, host JIT/VMAP and explicit seeded sampling | Complete public interfaces, GPU/TPU, dynamic PRNG keys, third/higher orders, capture and full derivative-device protocols |
| TensorFlow | NATIVE_TESTED; PARTIAL: CPU eager/GradientTape/Variable/static tf.function, true first/second child derivatives and coefficients | Complete TF/device protocol, third/higher orders, distributed/GPU/TPU/XLA/export and dynamic contracts |
| Native simulator backprop/capture | UNSUPPORTED / NOT_STARTED | Shift/adjoint interfaces are not simulator backprop or complete capture |
| Shot vectors/dynamic gradients/MPS gradients | NATIVE_TESTED; PARTIAL: actual sampling/branches, native shift and finite difference | Complete stochastic/loop/postselection contracts; numerical truncation risk |
| Higher-order derivatives | NATIVE_TESTED; PARTIAL: opt-in exact native Hessian, streamed native HVP, processor/classical second rules and four CPU frameworks | All generators, second adjoint, streamed framework HVP, finite variance/nonlinear stochastic rules, general loops/postselection, third/higher orders remain open |
| Compiled QNode gradients | NATIVE_TESTED; PARTIAL: expressions, shared inputs, Torch/Autograd and native gradients | Restored identity/equal-width only; general measurement remapping |
| Templates/qchem/math/resources/kernels/qnn/qcut/shadows | PARTIAL: native geometry-derived hydrogen electronic structure now added; other bounded workflows remain | Full library/transform/template and differentiation contracts |
| Compiled 100-qubit MPS | NATIVE_TESTED for GHZ-chain with dense APIs disabled | No arbitrary-entanglement efficiency claim |
| Quafu/QOS-UQCI/industry taxonomy | PARTIAL: offline target/configuration and existing adapters, four categories/19 subdomains | Real authorized backend/job evidence and complete industry workflows |

## Stage 11P-C Second-Order Status

Bounded opt-in `max_diff=2`, not full gradient/device or SDK parity. Native
HVP does not form a full Hessian; framework second rules currently use bounded
packed Hessians. See the [second-order report](../implementation/stage11p_c_native_second_order_report.md).
Quantum rules are independently convolved parameter shifts, not finite
differences or second adjoint. Actual QWC children/processors include classical
map Hessians, coefficient and cross-child terms. Three/higher orders reject.
Sampled support is limited to verified linear output processing with explicit
seeds; finite variance and coefficient-dependent weighted allocation reject.
Derivative-buffer memory and native device-state memory have separate budgets.

## Stage 11P-B TensorFlow Status (Historical Checkpoint)

Bounded CPU first-order implementation, not full TensorFlow or SDK parity.
Detailed receipts: [TF report](../implementation/stage11p_b_native_tensorflow_autodiff_report.md).

| Contract | Status | Boundary |
| --- | --- | --- |
| Eager / GradientTape / tf.Variable | NATIVE_TESTED; PARTIAL | Explicit packed inputs, real native shift/adjoint VJP; tested closure reads |
| tf.custom_gradient | NATIVE_TESTED; PARTIAL | Real native quantum/postprocessing Jacobians, not a constant wrapper |
| tf.function | NATIVE_TESTED; PARTIAL | Static real shape CPU same-process callback; fresh runtime values, not quantum XLA |
| Preprocessing / outer losses / trees | NATIVE_TESTED; PARTIAL | TF chain rule, nested dict/list/tuple output and cotangents |
| Coefficients / transforms / QWC | NATIVE_TESTED; PARTIAL | Product rule and actual child/reverse postprocessing, including compile/defer |
| Keras SGD/Adam | NATIVE_TESTED; PARTIAL | Twenty actual updates in tested scalar workflows, not all optimizer/layer contracts |
| Finite shots / vectors | NATIVE_TESTED; PARTIAL | Explicit integer seed, estimates and actual eager forward/backward work |
| tensorflow_batch | NATIVE_TESTED; PARTIAL | Static single-argument leading-axis CPU mapping, bounded logical work |
| 100-wire MPS / native H2 | NATIVE_TESTED; PARTIAL | Low entanglement no-dense proof; one fixed-geometry SCF and optimizer, not DiffHF |
| Legacy public TF oracle | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Six actual public scenarios per installed PL 0.44.1/0.42.3; deprecation is not inferred unavailability |
| Higher order / native backprop | UNSUPPORTED | Explicit first-order guard; Hessian/HVP remains open |
| XLA / GPU / TPU / distributed / portable SavedModel | UNSUPPORTED or unverified | Host callback cannot imply these capabilities |
| Full TF/PennyLane/Qiskit replacement | INCOMPLETE | Full final goal retained |

## Stage 11P-A JAX Status (Historical Checkpoint)

These are bounded native CPU contracts, not full JAX/PennyLane parity.
Current detailed receipts are in the
[JAX report](../implementation/stage11p_a_native_jax_autodiff_report.md).

| Contract | Status | Boundary |
| --- | --- | --- |
| Eager | NATIVE_TESTED; PARTIAL | Real native plans/devices and first-order numerical outputs |
| grad | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Native shift/adjoint, real scalar loss |
| value_and_grad | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Actual value plus native derivative in the same graph |
| jacrev | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Bounded real output/input trees |
| jacfwd | NATIVE_TESTED; PARTIAL | Verified linear custom-JVP rule, not custom-VJP-only support |
| jvp / vjp | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Explicit bounded native Jacobian products |
| jit | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Pure CPU host callback with explicit shape/dtype/status, not quantum XLA lowering |
| jit-grad | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Static supported graph and bounded native quantum derivatives |
| vmap | NATIVE_TESTED; PARTIAL | Sequential CPU host mapping and per-axis expansion limits |
| vmap-grad | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Public backprop numerical oracle; public eager shift/vmap rejection reported separately |
| PyTrees | NATIVE_TESTED; PARTIAL | Native nonempty dict/list/tuple result trees, static shapes |
| Classical preprocessing | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | JAX-owned graph and native occurrence derivatives |
| Trainable coefficients | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Full tested gate/coefficient product rule in supported native Hamiltonians |
| Transformed QNode | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Actual children and reverse native postprocessing, not original-QNode gradient bypass |
| Finite shots | NATIVE_TESTED; PARTIAL | Explicit immutable integer seed; estimates and real eager physical-work receipts |
| Shot vectors | NATIVE_TESTED; PARTIAL | Partitions and supported group allocations preserved |
| 100-wire MPS | NATIVE_TESTED; PARTIAL | Low-entanglement no-dense proof with actual eager telemetry; not arbitrary efficiency |
| Geometry-derived H2 optimizer | NATIVE_TESTED; PARTIAL | One native Gaussian/RHF/JW build, native excitation/QWC/JAX updates; not differentiable HF |
| Higher-order derivatives | UNSUPPORTED | Explicit guard; Hessian/HVP remains open |
| Capture/Catalyst | NOT_STARTED | Not implemented by host JIT |
| TensorFlow | NOT_STARTED / UNSUPPORTED | Existing explicit interface rejection retained |
| Native simulator backprop | UNSUPPORTED | Native quantum shift/adjoint bridge is not differentiable simulator backprop |
| Complete device derivative protocols | PARTIAL | Existing explicit native products; full plugin/device contracts remain open |
| Dynamic keys / GPU / TPU | UNSUPPORTED | No false device-native quantum or full stochastic-interface claim |

## Native Simulator Status

These are scoped native/public test results, not full Aer replacement. Final
three-environment and coverage receipts are in the Stage 11N report.

| Feature | Implemented/tested behavior | Remaining scope |
| --- | --- | --- |
| Statevector/density methods | NATIVE_TESTED: unitary/CPTP, branches/trajectories, save/set, feedback | Complete optimized Aer API/performance |
| MPS method | NATIVE_TESTED: tensors/local reductions, Kraus trajectories, noise/save/set, 100-wire no-dense case | Arbitrary entanglement efficiency not promised; truncation is approximate |
| Stabilizer method | NATIVE_TESTED: native tableau, save/set, compatible Clifford-mixture noise | Non-Clifford gates and selective damping reject |
| Unitary/superop | UPSTREAM_DIFFERENTIAL_TESTED: bounded actual map composition, global phase, reset/CPTP for superop | Measurement and unitary noise/reset reject; large maps resource-limited |
| Save families | NATIVE_TESTED: state/vector/dict/density/probabilities/dict/amplitudes/squared/expectation/variance/MPS/tableau/Clifford/maps | Method-specific subset; native compact payload shapes, not universal SDK object shapes |
| Save grouping | UPSTREAM_DIFFERENTIAL_TESTED subset: conditional and pershot physical branches | Analytic mixed vector rejects; raw finite state is last trajectory; full SDK aggregation variants partial |
| Set families | NATIVE_TESTED: actual vector/density/MPS/tableau/unitary/superop replacement | Full-register only, validated method-specific subset |
| QuantumError | UPSTREAM_DIFFERENTIAL_TESTED subset: bounded CPTP Kraus, compose/front/tensor/expand | Complete SDK conversion/signatures/optimizations partial |
| Noise constructors | UPSTREAM_DIFFERENTIAL_TESTED: Pauli/depolarizing/mixed/coherent/reset/amplitude/phase/phase-amplitude/thermal/Kraus | Explicit bounded widths/Kraus counts; native constructor schema |
| NoiseModel | NATIVE_TESTED: global/specific physical gate error, specific overrides global | Arbitrary backend-derived model/transformation helpers not implemented |
| Readout | UPSTREAM_DIFFERENTIAL_TESTED subset: asymmetric single and complete consecutive correlated groups | Partial/overlapping/conditional/implicit correlated measurements reject |
| Physical compiler/noise contract | NATIVE_TESTED: errors attach to actual emitted physical gates | Arbitrary noisy pre/post-compilation equivalence not claimed |
| Result/Backend/Job/options | NATIVE_TESTED: data/index, JSON, counts/memory/batches/seed, real failure status and budgets | Full result/async/parallel/GPU options partial or unsupported |
| Serialization | NATIVE_TESTED: native IR and Result JSON retain events/data | Standard QASM2/3/QPY explicitly reject unsupported simulator-specific instructions |
| Noisy differentiation | NATIVE_TESTED: fixed-channel native shift/finite-difference regression | No noisy adjoint, noise-parameter derivative or arbitrary stochastic gradient claim |

Individual simulator contracts below remain PARTIAL even when a stated native
or public comparison passed. The status applies only to the supported subset.

| API/capability | Status | Boundary |
| --- | --- | --- |
| AerSimulator.run | NATIVE_TESTED; PARTIAL | Existing native Job; batch/index retrieval |
| available_methods | NATIVE_TESTED; PARTIAL | Actual CPU methods only |
| automatic selection | NATIVE_TESTED; PARTIAL | Selects real compatible native representation |
| statevector | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Pure/trajectory/analytic branch subset |
| density_matrix | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Bounded exact CPTP/dynamic execution |
| matrix_product_state | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Native tensors and documented truncation |
| stabilizer | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Clifford and compatible mixtures only |
| unitary | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Bounded ideal matrix, no measurement/reset/noise |
| superop | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Bounded actual CPTP map, no measurement |
| extended_stabilizer | UNSUPPORTED | Not aliased to statevector |
| tensor_network | UNSUPPORTED | Not aliased to MPS |
| SaveState | NATIVE_TESTED; PARTIAL | Actual selected-method state |
| SaveStatevector | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Full register, pure or finite trajectory |
| SaveStatevectorDict | NATIVE_TESTED; PARTIAL | Native q0-first hex indices |
| SaveDensityMatrix | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Ordered subset, bounded local dimension |
| SaveMPS | NATIVE_TESTED; PARTIAL | Native tensor schema, not SDK tuple schema |
| SaveStabilizer | NATIVE_TESTED; PARTIAL | Native validated tableau schema |
| SaveClifford | NATIVE_TESTED; PARTIAL | Native tableau, automatic selection tested |
| SaveUnitary | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Actual matrix, deterministic |
| SaveSuperOp | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Actual channel, deterministic |
| SaveProbabilities | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Native wire order, no vector-to-density allocation |
| SaveProbabilitiesDict | NATIVE_TESTED; PARTIAL | Native q0-first hex indices |
| SaveAmplitudes | NATIVE_TESTED; PARTIAL | Selected indices; compact MPS contraction |
| SaveAmplitudesSquared | NATIVE_TESTED; PARTIAL | Pure probabilities or density diagonal |
| SaveExpectationValue | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Hermitian local matrix/Pauli forms |
| SaveExpectationValueVariance | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Actual second moment/cross terms |
| conditional snapshots | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Actual classical groups; grouping budget |
| pershot snapshots | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Actual finite trajectories, bounded storage |
| SetStatevector | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Full-register normalized replacement |
| SetDensityMatrix | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Full-register positive trace-one replacement |
| SetMPS | NATIVE_TESTED; PARTIAL | Native normalized tensor payload |
| SetStabilizer | NATIVE_TESTED; PARTIAL | Native validated Clifford tableau |
| SetUnitary | NATIVE_TESTED; PARTIAL | Full-register bounded unitary replacement |
| SetSuperOp | NATIVE_TESTED; PARTIAL | Full-register bounded CPTP replacement |
| NoiseModel | NATIVE_TESTED; PARTIAL | Global and specific physical bindings |
| QuantumError | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Bounded native Kraus algebra |
| ReadoutError | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Stochastic 1q and complete correlated groups |
| Gate-attached noise | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Actual repeated gate execution; explicit qargs order |
| Thermal relaxation | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL | Physical T1/T2/time/population domains |
| physical Target noise | NATIVE_TESTED; PARTIAL | Emitted gates compared to explicit inline Kraus reference |
| Backend / Job / Result | NATIVE_TESTED; PARTIAL | Existing lifecycle, real errors, JSON/data/counts/memory |
| SimulatorOptions | NATIVE_TESTED; PARTIAL | CPU/double, MPS and budgets; unsupported options reject |
| QASM/QPY integration | NATIVE_TESTED; PARTIAL | Simulator-specific instructions reject in standard formats |
| MPS non-dense execution | NATIVE_TESTED; PARTIAL | 100-wire GHZ saves, later phase gate, local density/amplitudes/shots |
| noisy gradients | NATIVE_TESTED; PARTIAL | Fixed noise shift/finite difference; noisy adjoint rejects |

## Stage 11O Templates And Transform Status

| API | Supported native evidence/status | Remaining gap |
| --- | --- | --- |
| Template decomposition/apply | NATIVE_TESTED; PARTIAL: existing Operation/Circuit/Tape emission, ordered and explicitly mapped named wires | Complete operation/queue/capture/broadcast/serialization object protocols |
| AngleEmbedding | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: actual axes/partial input/live first-order graph | Complete broadcasting/interface/device contracts |
| BasisEmbedding | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: integer/string/vector occupation gates | General state-preparation and complete parameter/operation API |
| AmplitudeEmbedding | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: actual bounded complex state, padding/normalization/zero-input guards | Input gradients, portable gate decomposition, full StatePrep and QPY object support |
| BasicEntanglerLayers | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: actual one/two/multiple wire ring, rotation choices and native gradients | Arbitrary rotation objects, broadcast/capture and complete API |
| StronglyEntanglingLayers | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: actual Euler/ranges/CX-CZ, tensor/shared/nonlinear gradients | General imprimitives and complete family API |
| IQPEmbedding | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: feature products, pair patterns, repeats and native gradients | Full public operation/shape/capture surface |
| QFT | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: complete bounded complex unitary, inverse/swaps/ordered wires | Complete operation API and large-scale resource semantics |
| TrotterProduct | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: positive-time Pauli order 1/2 gates, actual approximation and time gradients | Higher formulas, grouped/general operands, trainable coefficients and complete API |
| UCCSD and other template families | NOT_STARTED beyond separately tested bounded chemistry excitation helpers | Full native template catalogue and semantics |
| Tape transform protocol / TransformProgram | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: actual batches, fresh dispatch, native child shift/adjoint Jacobians and native postprocessing products | Full matrix-free VJP/derivative-device/public/capture protocols and arbitrary user processor derivatives |
| merge_rotations Tape transform | NATIVE_TESTED; PARTIAL: same-axis adjacent rotations, parameter graphs, runtime boundaries and actual transformed native gradients | Full public commuting/operation semantics |
| cancel_inverses | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: proved adjacent fixed/symbolic pairs with strict runtime/metadata boundaries | Full commuting/non-adjacent/operation catalogue and public protocol |
| decompose | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: real bounded native definition/template/compound gate expansion and full complex phase | General SDK operation/capture/graph-compiler/ancilla and complete decomposition catalogue |
| compile | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: actual native target/routing/basis pipeline with equal-width restored identity measurement maps | Full public pipeline/API and generalized measurement/layout remapping |
| Internal split_hamiltonian prototype | NATIVE_TESTED; PARTIAL: real per-term child execution, identity/duplicates/zero/static coefficients, nested and shot-vector reconstruction | Not public split_to_single_terms parity; no QWC grouping or shot allocation |
| split_to_single_terms | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: deduplicated native Pauli measurements, real scalar coefficient graphs, tree reconstruction and native gradients | General symbolic observable families, raw Tape autodiff and full public protocols |
| split_non_commuting | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: actual native Pauli grouping, joint samples, coefficient/identity/tree reconstruction and native gradients | General observables/measurement kinds and full default/cache/operation protocols |
| Transformed coefficient/gate derivatives | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: native quantum means plus coefficient product rule, Torch/Autograd/JAX/native first-order interfaces | Weighted zero-valued trainable groups reject; changed prepared coefficient primals require a fresh plan; no TF/GPU/higher order |
| Transformed sampled gradients | NATIVE_TESTED; PARTIAL: real grouped parameter shifts with independent streams, partitions and actual work receipts | Stochastic estimates, not a universally unbiased nonlinear estimator or an SE-derived gradient bound; finite variance/local-seed/postselection/parameterized-loop gaps |
| QWC shot distribution | NATIVE_TESTED; PARTIAL: full per-group budget or deterministic uniform/L1-weighted total allocation, exact per-vector-partition conservation | Random/custom allocation and full SDK parity; PL 0.42.3 has no allocation API, PL 0.44.1 flattens distributed vectors and may drop undersampled groups |
| QWC estimator statistics | NATIVE_TESTED; PARTIAL: exact analytic group covariance or real empirical shared-sample covariance and source expectation standard error | Not full quantum variance across incompatible groups, uncertainty of variance estimators or calibrated hardware confidence guarantees |
| defer_measurements | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: actual fresh record ancillas, unitary child circuit, logical reduced outputs, native gradients and QWC/compiler composition | Reset/postselection/noisy feedback/conditional MCM/Store/arithmetic/capture/full state semantics and complete public transform protocol remain unsupported |
| Classical measurement records | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: ordered bit records plus explicit quantum wires, analytic probabilities and real joint sample/counts; record ancillas retain reused-wire outcomes | Full MeasurementValue expressions/signatures, all device kinds, conditional records and general classical memory reconstruction |

Remaining Stage 11O-B requirements stay active. Eight executable template
families and the B1-B6 execution/gradient foundation do not establish full
template or transform parity. The native postprocessing trace visits means
and declared classical slots only, not passive statistics or execution data.
Coherent deferral has actual execution evidence, including 100 logical wires
expanded to 101 MPS wires and a geometry-derived H2 feedback gradient. It does
not cover every mid-measurement contract. Native default terminal wire
selection preserves the original logical wires; the public API may require
explicit wires. Record outputs use an explicit native `records=` keyword.
Native weighted zero-contribution groups can be omitted, but a nonzero group
with zero assigned samples explicitly rejects instead of silently biasing the
answer. These documented boundaries must not be described as full parity.

## Stage 11O Chemistry Progress

This is a scoped scientific checkpoint, not whole Stage 11O completion.
Template catalogue completion and general derivative contracts remain
unfinished. A geometry-derived H2 excitation/QWC/gradient/optimizer workflow
is now tested; pedagogical fixed H2/LiH models are not native molecular integrals.

| API | Current evidence/status | Remaining work |
| --- | --- | --- |
| Molecule | NATIVE_TESTED; PARTIAL: elements/electrons/spin/units and validated real geometry | Complete molecular API and all electronic models |
| Gaussian basis | NATIVE_TESTED; PARTIAL: normalized H STO-3G s shells | Other elements/contractions/angular shells and basis catalogue |
| overlap/kinetic/nuclear attraction | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: actual analytic s-Gaussian AO integrals | General angular momentum, derivatives and complete dimensional contracts |
| electron repulsion | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: actual chemist ERI tensor | General angular recurrence and derivatives |
| RHF | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: actual closed-shell iterations and explicit convergence failure | Open-shell/robust general SCF/differentiable response |
| electron_integrals | NATIVE_TESTED; PARTIAL: real RHF AO-to-MO tensor transformation | General orbital/active-space/differentiability contracts |
| FermionicOp | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: CAR signs/contractions, products/adjoint and independent Fock matrix | Complete algebra/API and advanced encodings |
| Jordan-Wigner | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: bounded general complex ladder words and parity strings | Complete mapper family/options/resource scaling |
| molecular_hamiltonian | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: actual geometry -> RHF -> fermionic -> untapered 4-qubit H2 | All molecules/bases/mappings and differentiable construction |
| hf_state | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: occupation representation | Other encodings and complete interface |
| excitations | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: spin-selected singles/doubles | Full excitation families/options |
| excitations_to_wires | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: ordered ranges/custom wire labels | Complete shape/index/interface contracts |
| Excitation circuit and VQE | NATIVE_TESTED; PARTIAL: exact commuting-Pauli single/double circuit, native shift/adjoint/Torch/Autograd | Complete UCCSD and general optimization guarantees |
| active_space/tapering | NOT_STARTED for new native molecular workflow | Actual active-space transformation and symmetry handling |
| geometry derivatives | PARTIAL: central finite-difference consistency test only | Native analytic integral/SCF derivatives |
| differentiable HF | NOT_STARTED | Full end-to-end differentiable integrals and SCF |
| molecular properties/larger elements and bases | NOT_STARTED beyond stated subset | Full native chemistry library |

## Serialization Status

| Capability | Stage 11M current status | Remaining gate |
| --- | --- | --- |
| QASM2 parsing/exporting/files/strings | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: 27 native + 10 bilateral public scenarios | Full language/object API is not claimed |
| QASM2 custom gates | NATIVE_TESTED via budgeted semantic expansion | Full definition-object identity/opaque execution not claimed |
| QASM2 conditional subset | NATIVE_TESTED for complete-register equality | Nonrepresentable dynamic/phase/delay objects explicitly reject |
| QASM3 typed AST/source lowering | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: typed source executes, 10 bilateral public scenarios | Complete language types/functions/arrays remain partial; standard U vs SDK dialect explicit |
| QASM3 control flow | NATIVE_TESTED: 14 independent dynamic sources + 3 legacy snapshot cases | Full types/capture/subroutine behavior remains partial |
| QASM3 timing/custom definitions | NATIVE_TESTED subset: real delay units/expanded definitions | Full timing algebra and object fidelity partial |
| QASM3 OpenPulse/defcal/stretch/extern/complex arrays | UNSUPPORTED | Must reject without deleting statements |
| QPY native reader/writer | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: 18 native binary + 10 bilateral public + multicircuit cases | Real public version 13 binary, not an IR envelope; unsupported branches below |
| QPY format versions | Version 13 only; all other versions UNSUPPORTED | Version is distinct from source SDK version |
| QPY parameters/global phase | UPSTREAM_DIFFERENTIAL_TESTED: UUIDs, arithmetic replay, symbolic/numeric phase | Full symbolic function/vector/object encoding partial; native equality remains name-based |
| QPY dynamic circuits/custom instructions/layout | UNSUPPORTED at this checkpoint | Do not infer completion from static QPY success |
| QPY non-dt Delay | UNSUPPORTED | Tested v13 SDK payload loses units; native export rejects; QASM3 retains units |
| Cross-format interchange | NATIVE_TESTED; PARTIAL | Default lossless semantics or rejection; explicit external root metadata only |
| Serialization gradient/compiler/MPS preservation | NATIVE_TESTED: six gradient scenarios in two formats, compiled routing/phase/order, 100-qubit non-dense MPS | Does not serialize Python callables or promise arbitrary MPS efficiency |
| Parsing security/limits | NATIVE_TESTED: hostile includes/code-like source, lengths/flags/versions/replay/identity/numeric budgets | Full protocol and all source types remain partial |

No QPY or serialization subsystem is marked complete merely because a file has
the correct header. Actual independent readers/writers and both SDK versions
must load and execute the resulting circuits. Hardware/cloud work and Studio
are outside this serialization batch.

## Evidence History

The obsolete pre-reconciliation text is preserved verbatim in
[Stage 11L ledger snapshot](history/core_parity_ledger_stage11l_snapshot.md);
it is historical, not a second current status table.

- [Stage 11J dynamic execution report](../implementation/stage11j_native_dynamic_control_flow_report.md)
- [Stage 11K differentiation report](../implementation/stage11k_native_qnode_autodiff_report.md)
- [Stage 11L compiler report](../implementation/stage11l_native_transpiler_report.md)
- [Stage 11M gap audit](../implementation/stage11m_serialization_gap_audit.md)
- [Stage 11M implementation/test report](../implementation/stage11m_native_qasm_qpy_serialization_report.md)
- [Stage 11N gap audit](../implementation/stage11n_aer_native_gap_audit.md)
- [Stage 11N implementation/test report](../implementation/stage11n_native_aer_report.md)
- [Stage 11O initial gap audit](../implementation/stage11o_pennylane_native_gap_audit.md)
- [Stage 11O chemistry checkpoint](../implementation/stage11o_native_qchem_report.md)
- [Stage 11O-A/B gap audit](../implementation/stage11o_ab_native_gap_audit.md)
- [Stage 11O-A template checkpoint](../implementation/stage11o_ab_native_templates_report.md)
- [Stage 11O-B1 transform checkpoint](../implementation/stage11o_b1_native_transform_execution_report.md)
- [Stage 11O-B2/B3 QNode and basic transforms](../implementation/stage11o_b2_b3_native_transform_report.md)
- [Stage 11O-B4 QWC joint samples and shots](../implementation/stage11o_b4_native_qwc_shot_allocation_report.md)
- [Stage 11O-B5 native transformed autodiff](../implementation/stage11o_b5_native_transformed_autodiff_report.md)
- [Stage 11O-B6 coherent deferral](../implementation/stage11o_b6_native_deferred_measurements_report.md)
- [Stage 11O joint acceptance](../implementation/stage11o_joint_acceptance_report.md)
- [Remaining full functional parity gaps](../implementation/stage11o_remaining_functional_parity_gaps.md)

Stage 11L exact-SHA CI: 39259350086, 22/22 success. Its clean local runs:
SDK-free 899 passed/116 skipped, installed 1090/4, alternate 1054/40, measured
line coverage 87.5253299%, local matrix exit 0. These are Stage 11M baselines,
not proof that new serialization changes pass. Stage 11M local results are
1030/117 SDK-free, 1252/4 installed, 1216/40 alternate; 162 new serialization
cases pass in each SDK environment; coverage 87.8801865%. Stage 11N final local
results are 1120/118 SDK-free, 1366/4 installed and 1330/40 alternate; 114 new
cases (73 native simulator, 17 noise mathematical/runtime, 24 public oracle),
coverage 88.1810076%, unchanged exclusions and full local matrix exit 0.
Publication is still blocked by existing workflow authorization, not inferred
from older CI. Next work includes remaining serialization/Aer contracts,
complete templates/qchem/transforms and JAX/TF/capture/higher-order autodiff.
Studio stays last.
