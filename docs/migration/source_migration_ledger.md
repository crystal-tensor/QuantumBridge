# Source Migration Ledger

Status: P0.3 frozen runtime 7a9ebe78 validated, scoped checkpoint pending;
P0.2-A local checkpoint 12098c9, frozen runtime 2973040c validated;
P0.1 checkpoint 89f4dc9;
R2 baseline b1d345b; C3 remains partial and full replacement incomplete
Date: 2026-10-21

This ledger retains historical release and checkpoint sections. Current work
uses Native Implementation, Adapter Integration and Upstream Dependency, with
their boundaries stated separately. Historical checkpoint limitations are not
the current status view; use core_parity_ledger.md for that view.
No Source Port with Attribution was performed.

## Stage 12-A P0.3 Native Operator Composition Inventory

Independent Native Implementation, bounded frozen-runtime gates complete. Existing
Operator.compose and reflected @ gain validated mixed-radix mapped/full raw
rectangular products in `quantumbridge/information/operator.py`. The shared
stride/index machinery in `quantumbridge/utils/math.py` gains direct row/column
contraction into the final output, not a separate full embedded operator.
`tests/information/test_mixed_radix_operator_composition.py` contains independent
enumeration/tensor mathematics, actual state consistency and known-storage/error
tests. `docs/implementation/stage12_a_p03_operator_composition_progress.md`
records genuine gaps, test-author errors, actual recovery and public differences.
`docs/compat/stage12_a_p03_minimal_public_differential_case.json` is generated
literal native/public two-version experiment data, not upstream source or tests.
Public Qiskit is a black-box reference in optional tests only. No source/test
port, upstream engine, Router/Studio change or cloud/credential work is included.

## Stage 12-A P0.2-A Native Local Operator Inventory

Independent Native Implementation; bounded frozen-runtime FULL/framework/matrix
gates complete, scoped local checkpoint 12098c9. Public Qiskit APIs are black-box
references in tests only, not a runtime engine. Observed public numerical
differences remain unresolved compatibility rather than upstream defect claims.

- `quantumbridge/information/operator.py`: actual input/output dimensions,
  rectangular/nonbinary construction and correct existing numeric propagation.
- `quantumbridge/information/statevector.py` and
  `quantumbridge/information/density_matrix.py`: validated local/full typed
  numeric maps and actual output subsystem propagation.
- `quantumbridge/utils/math.py`: extend the existing native operator entry
  points with shared mixed-radix index/stride mathematics and admitted outputs.
- `quantumbridge/information/channels.py`: only a bounded typed-input guard for
  unextended mixed-radix channel conversion, not general channel completion.
- `tests/information/test_mapped_mixed_radix_operators.py`: independently authored
  mathematical, public-reference, order, error, layout and lifetime cases.
- `tests/information/test_mixed_radix_states.py`: retire only the obsolete numeric
  mapped-evolve refusal assertion; preserve circuit/operator-conversion guards.
- `docs/implementation/stage12_a_p02_mapped_operator_progress.md`: actual source,
  red/recovery, public differences, supported/unsupported and actual gates.
- `docs/compat/stage12_a_p02_public_differential_case.json`: generated literal
  black-box numerical reproduction data, not upstream implementation/test code.

No upstream source/test port, SDK engine, vendor, cloud, hardware, token/auth/TLS,
tag/release, history rewrite or user Router/Studio change is part of this work.

## Stage 12-A P0.1 Native Mixed-Radix Inventory

Independent Native Implementation, with completed frozen-runtime gates for the
bounded slices in the progress report, not complete class/API parity. Installed public
Qiskit calls are optional black-box test oracles only; no upstream source/test
port or SDK execution engine is added. Existing state/density and trace kernels
are generalized rather than replaced with a second simulator.

- `quantumbridge/information/state_dimensions.py`: native dimension invariants,
  high-radix q0-first basis digits, labels and explicit binary-only guards.
- `quantumbridge/information/statevector.py` and
  `quantumbridge/information/density_matrix.py`: actual mixed-radix construction,
  native mathematics, dimensions propagation, samples/collapse/reset.
- `quantumbridge/information/partial_trace.py`: existing trace kernel with real
  subsystem dimensions and admitted reduction outputs.
- `quantumbridge/information/analysis.py` and
  `quantumbridge/information/channels.py`: bounded guards against silent binary
  reinterpretation in not-yet-extended consumers, not general API completion.
- `tests/information/test_mixed_radix_states.py`: independently authored numeric,
  dimension, composition, quota/lifetime and optional public-reference tests.
- `docs/implementation/stage12_a_p01_mixed_radix_progress.md`: actual red/fix,
  supported/unsupported contracts and completed same-runtime validation receipts.

No cloud/hardware/token/auth/TLS, vendoring, tag/release or user Router/Studio
source changes are part of this batch. Full functional replacement is incomplete.

## Stage 11P-C3-R2 State/Result Source Inventory

Independent Native Implementation. Public Qiskit APIs are optional black-box
test oracles only; NumPy public array/RNG behavior is used by the native code.
No upstream implementation or test source was read/copied/ported. No SDK
quantum execution engine, vendoring, cloud, hardware, token or auth changes.

- `quantumbridge/execution/array_ownership.py`: shared weak storage provenance
  and pre-admitted independent defensive copies.
- `quantumbridge/execution/mps_arrays.py`: reuse the existing ownership helpers
  and shared weak metadata, preserving native MPS helper names.
- `quantumbridge/execution/resource_context.py`: confirmed categorical buffer
  shots remain consumed before later formatting.
- `quantumbridge/information/statevector.py`: independently authored Pauli
  eigenstates, reset, subsystem counts and bounded existing state operations.
- `quantumbridge/information/density_matrix.py`: existing native density
  construction/measure/tensor/reversal/sampling with explicit admitted buffers.
- `quantumbridge/results/result.py`: existing public state/density accessors
  return independently owned copies with actual source/new-request accounts.
- `tests/derivative_execution/test_quantum_info_state_resources.py` and
  `tests/derivative_execution/test_result_array_resources.py`: independently
  authored mathematical, allocation, lifetime, fault and public differential
  scenarios, not copied upstream tests.
- `docs/implementation/stage11p_c3_r2_execution_prompt.md` and
  `docs/implementation/stage11p_c3_r2_state_result_progress.md`: scoped spec,
  actual red/green receipts, validation status and remaining functional gaps.

The initial slice below predates final Operator/tableau work and R2 gates.
Fresh final receipts and bounded classifications are in
`docs/review/stage11p_c3_joint_review.md`. Old allowance retirement and complete
C3 acceptance are not claimed. Full functional replacement remains incomplete.

The subsequent P1 slice additionally modifies
`quantumbridge/information/operator.py` and
`quantumbridge/information/channels.py`, reusing the audited native field copier
in `array_ownership.py` for shared caller memo and independent roots. Native
reflected matrix arithmetic, standard Pauli permutation labels and stable
scalar global-phase comparison were independently authored. New tests in
`tests/derivative_execution/test_quantum_info_operator_copy_resources.py`
use direct NumPy mathematics and optional public Qiskit calls as black-box
oracles. No implementation/test source port or new quantum engine occurred.
The scope correction for persistent-pool partial-copy failure preserves the
original test rather than changing its established lifetime contract. See
`docs/implementation/stage11p_c3_r2_operator_channel_progress.md` for actual
receipts; P2 and final R2 acceptance remain open.

The bounded P2 slice additionally changes
`quantumbridge/information/clifford.py`,
`quantumbridge/information/stabilizer_state.py`,
`quantumbridge/operators/pauli.py` and
`quantumbridge/devices/statevector_device.py`. It reuses existing native tableau,
GF(2), Pauli and density formulas with admitted ndarray storage and real root
lifetimes. The small-gate cache stores immutable Python descriptors, not
third-party source or a new engine. Mathematical/resource tests in
`tests/derivative_execution/test_tableau_resources.py` were independently
authored; public installed Qiskit calls are optional black-box oracles only.
No implementation/test source port, vendoring, credentials or cloud calls.
The old dense guard is intentionally retained after an actual overlap/residual
audit. Exact results and incomplete final gates are in
`docs/implementation/stage11p_c3_r2_tableau_progress.md`.

## Stage 11P-C3-R1 In-Progress Source Inventory

Independent Native Implementation; optional public classical framework/NumPy
interfaces are behavioral references, not copied source. Zero implementation
or test source ports; no SDK quantum engine, vendoring or credential work.
Existing C3 files modified in this slice remain inventoried below.

- `quantumbridge/execution/array_reservations.py`
- `quantumbridge/execution/array_ownership.py`
- `quantumbridge/execution/persistent_storage.py`
- `quantumbridge/execution/mps_arrays.py`
- `quantumbridge/utils/math.py`
- `quantumbridge/ir/qb_ir.py`
- `quantumbridge/operators/pauli.py`
- `quantumbridge/operators/sparse_operator.py`
- `quantumbridge/chemistry/qubit_hamiltonian.py`
- `quantumbridge/compiler/pass_manager.py`
- `quantumbridge/devices/density_matrix_device.py`
- `quantumbridge/devices/execution.py`
- `quantumbridge/information/channels.py`
- `quantumbridge/information/operator.py`
- `quantumbridge/information/statevector.py`
- `quantumbridge/information/density_matrix.py`
- `quantumbridge/information/stabilizer_state.py`
- `quantumbridge/devices/statevector_device.py`
- `quantumbridge/noise/channels.py`
- `quantumbridge/noise/quantum_error.py`
- `quantumbridge/diff/adjoint.py`
- `quantumbridge/diff/second_adjoint.py`
- `quantumbridge/schema/serialization.py`
- `quantumbridge/serialization/limits.py`
- `quantumbridge/information/matrix_product_state.py`
- `quantumbridge/devices/matrix_product_state_device.py`
- `quantumbridge/diff/qnode_engine.py`
- `quantumbridge/execution/control_flow_engine.py`
- `quantumbridge/simulator/snapshots.py`
- `quantumbridge/simulator/aer.py`
- `quantumbridge/results/result.py`
- `quantumbridge/execution/resource_context.py`
- `quantumbridge/execution/resource_ledger.py`
- `quantumbridge/core/circuit.py`
- `quantumbridge/interfaces/native_host.py`
- `quantumbridge/interfaces/jax_derivative_status.py`
- `quantumbridge/interfaces/tensorflow_derivative_status.py`
- `quantumbridge/interfaces/tensorflow_autodiff.py`
- `quantumbridge/interfaces/tensorflow_callbacks.py`
- `quantumbridge/interfaces/tensorflow_graph.py`
- `quantumbridge/diff/trace.py`
- `tests/derivative_execution/test_array_reservations.py`
- `tests/derivative_execution/test_einsum_workspace.py`
- `tests/derivative_execution/test_native_mapping_preallocation.py`
- `tests/derivative_execution/test_array_ownership.py`
- `tests/derivative_execution/test_framework_array_preallocation.py`
- `tests/derivative_execution/test_graph_resource_lifetime.py`
- `tests/derivative_execution/conftest.py`
- `tests/derivative_execution/test_device_result_ownership.py`
- `tests/derivative_execution/test_native_configuration_ownership.py`
- `tests/derivative_execution/test_persistent_storage.py`
- `tests/derivative_execution/test_persistent_kernel_frameworks.py`
- `tests/derivative_execution/test_persistent_copy_protocols.py`
- `tests/derivative_execution/test_tensorflow_graph_ownership.py`
- `tests/derivative_execution/test_tree_array_ownership.py`
- `tests/derivative_execution/test_mps_array_resources.py`
- `tests/derivative_execution/test_mps_snapshot_ownership.py`
- `tests/derivative_execution/test_mps_partial_shots.py`
- `tests/derivative_execution/test_observable_ir_allocations.py`
- `tests/derivative_execution/test_result_decode_allocations.py`
- `tests/derivative_execution/test_native_validation_allocations.py`
- `tests/derivative_execution/test_native_gate_noise_allocations.py`
- `tests/derivative_execution/test_native_channel_evolution_allocations.py`
- `tests/derivative_execution/test_failure_recovery.py`
- `tests/derivative_execution/test_initial_contracts.py`
- `quantumbridge/qml/tape.py`
- `docs/implementation/stage11p_c3_r1_allocation_audit.md`
- `docs/implementation/stage11p_c3_r1_resource_ownership_report.md`

Initial two corrected allocation and three graph-lifetime red tests were run
before their production fixes. Focused green results are not final clean-tree
R1 acceptance, full allocator control or complete Qiskit/PennyLane parity.

Task 3E independently wraps existing native gate/noise/channel and dense
evolution formulas with prior numeric-buffer ownership. Analytic gate and
channel tests are authored from public mathematical identities, not copied
SDK test source. No upstream implementation port, third-party quantum engine,
vendoring or credential work. Explicit remaining allocation sites and fresh
full-gate requirements are recorded in the R1 ownership report.

## Stage 11P-C3 In-Progress Source Inventory

Independent Native Implementation and optional classical framework integration,
not an accepted complete C3 checkpoint. Zero source/test ports; no SDK engine,
vendoring, credentials, cloud or hardware calls. Scope and missing acceptance
evidence are recorded in the C3 reports.

- `quantumbridge/devices/statevector_device.py`
- `quantumbridge/devices/density_matrix_device.py`
- `quantumbridge/devices/matrix_product_state_device.py`
- `quantumbridge/devices/stabilizer_device.py`
- `quantumbridge/diff/qnode_engine.py`
- `quantumbridge/diff/second_trace.py`
- `quantumbridge/diff/second_adjoint.py`
- `quantumbridge/execution/__init__.py`
- `quantumbridge/execution/derivative_request.py`
- `quantumbridge/execution/derivative_result.py`
- `quantumbridge/execution/derivative_status.py`
- `quantumbridge/execution/derivative_planning.py`
- `quantumbridge/execution/device_derivatives.py`
- `quantumbridge/execution/resource_limits.py`
- `quantumbridge/execution/resource_ledger.py`
- `quantumbridge/execution/resource_context.py`
- `quantumbridge/interfaces/native_host.py`
- `quantumbridge/interfaces/framework_derivatives.py`
- `quantumbridge/interfaces/jax_derivative_status.py`
- `quantumbridge/interfaces/tensorflow_derivative_status.py`
- `quantumbridge/qml/qnode.py`
- `README.md`
- `THIRD_PARTY_NOTICES.md`
- `docs/compat/core_parity_ledger.md`
- `docs/migration/source_migration_ledger.md`
- `docs/implementation/stage11p_c3_derivative_execution_gap_audit.md`
- `docs/implementation/stage11p_c3_unified_resource_report.md`
- `docs/implementation/stage11p_c3_derivative_status_report.md`
- `tests/derivative_execution/test_initial_contracts.py`
- `tests/derivative_execution/test_resource_lifecycle.py`
- `tests/derivative_execution/test_device_derivative_api.py`
- `tests/derivative_execution/test_failure_recovery.py`
- `tests/derivative_execution/test_jax_compiled_status.py`
- `tests/derivative_execution/test_tensorflow_graph_status.py`
- `tests/derivative_execution/test_mps_nondense_hvp.py`
- `tests/derivative_execution/test_independent_math.py`
- `tests/derivative_execution/test_public_differential.py`
- `examples/native_device_derivatives.py`
- `examples/native_unified_resource_budget.py`
- `examples/native_jax_hvp_status.py`
- `examples/native_tensorflow_hvp_status.py`
- `examples/native_mps_hvp_budget.py`
- `tests/derivative_execution/test_ordinary_framework_budget.py`
- `quantumbridge/interfaces/ordinary_resources.py`
- `quantumbridge/interfaces/qnode_autodiff.py`
- `quantumbridge/transforms/program.py`
- `quantumbridge/interfaces/jax_autodiff.py`
- `quantumbridge/interfaces/tensorflow_autodiff.py`
- `tests/derivative_execution/test_partial_shots_failure.py`
- `quantumbridge/qml/pauli_group.py`
- `quantumbridge/diff/second_order.py`
- `tests/derivative_execution/test_qwc_resource_ownership.py`
- `quantumbridge/execution/qnode_derivatives.py`
- `tests/derivative_execution/test_native_qnode_budget.py`
- `tests/derivative_execution/test_fixed_h2_execution.py`
- `quantumbridge/diff/trace.py`
- `tests/derivative_execution/test_execution_examples.py`

## Stage 11P-C2A Native Second Adjoint

Native Implementation, zero upstream implementation/test source ports. The
existing native reverse gradient recurrence is differentiated independently;
Jones/Gacon's public first-order adjoint paper is a mathematical reference only.
No quantum SDK is an execution or derivative engine for this path.

| Files | Changes | Independent evidence |
| --- | --- | --- |
| `quantumbridge/diff/second_adjoint.py` | Native forward state tangent and reverse curvature; direct source-map Hessian/HVP contraction | Trigonometric controlled-frequency and complex matrix references, variance, probabilities, stationary maps and zero shifted circuits |
| `quantumbridge/diff/higher_order_limits.py`, `quantumbridge/diff/second_order.py` | Explicit adjoint dispatch, combined working-buffer and aggregate child work preflight; actual second processors retained | Resource failures before native execution, live coefficient/cross-child rules and existing shift regressions |
| `quantumbridge/interfaces/native_host.py` | Aggregate transposed-output-row adjoint work preflight | JAX reverse-mode limit rejects before executing any row |
| `tests/qml/test_native_second_adjoint.py`, `tests/interfaces/test_native_second_adjoint_frameworks.py` | Independently authored native math, true four-framework second graphs and unsupported negatives | Initial three real red contracts; long shared-parameter/no-shift execution and eager/JIT composition |
| `tests/compat/test_native_second_order_pennylane_differential.py` | Native second adjoint additionally compared to public backprop Hessians | Four new actual public numerical scenarios; prior public shift limitations retained separately |
| `tests/qml/test_native_second_order.py`, `tests/qml/test_native_second_order_workflows.py`, `examples/native_framework_hvp.py` | Valid adjoint replaces obsolete analytic rejection; sampled rejection retained; H2 Newton/example supports both methods | Actual one-build fixed-geometry H2 second derivatives/updates, no tolerance relaxation |
| `docs/implementation/stage11p_c2a_native_second_adjoint_audit.md`, `docs/implementation/stage11p_c2a_native_second_adjoint_report.md`, `docs/compat/core_parity_ledger.md`, `README.md`, `THIRD_PARTY_NOTICES.md` | Observed gaps, implementation math, scoped receipts and complete remaining boundaries | Full replacement is not declared complete by this checkpoint |

No Studio/Router, tag/release, package/environment tree, source vendoring,
credential, authentication/TLS or cloud/hardware work is included.

## Stage 11P-C2 Streamed Framework HVPs

Native Implementation and optional classical framework integration. No upstream
implementation/test source ports. Existing plans, native devices, shift recipes
and processors remain the quantum engine. Public JAX extension/derivative and
Autograd primitive contracts are behavioral references, not copied source.

| Files | Changes | Independent evidence |
| --- | --- | --- |
| `quantumbridge/diff/second_order.py`, `quantumbridge/diff/second_trace.py` | Reusable transform preflight, direction-independent sampled schedules and structural input dependency | Seeded HVP additivity/homogeneity, stationary maps and fixed-constant exclusion |
| `quantumbridge/interfaces/native_host.py` | Directional classical maps and two-pass row-transpose execution with aggregate preflight | Combined row shift/tape/shot rejection before quantum work |
| `quantumbridge/interfaces/qnode_autodiff.py`, `quantumbridge/interfaces/tensorflow_autodiff.py` | Real Torch/Autograd/TF second VJPs using HVPs and live cotangent branches | Shared/coefficient/nonlinear-loss/vector-output rules with full-Hessian budget one |
| `quantumbridge/interfaces/jax_autodiff.py`, `quantumbridge/interfaces/jax_directional.py` | One optional module-global linear primitive with explicit JVP/transpose/batching/CPU lowering | Forward/reverse/JIT/mapped/direct-direction differentiation and real host failures |
| `tests/interfaces/test_native_streamed_hvp.py`, `tests/interfaces/test_native_streamed_hvp_mps.py`, `tests/interfaces/test_native_second_order_frameworks.py` | Independently authored framework, resource, negative and no-dense MPS contracts | Real native directional-plan spies, physical shot receipts and all four frameworks |
| `tests/qml/test_native_sampled_hvp_linearity.py`, `tests/qml/test_native_second_classical_trace.py` | Independent stochastic-linear and structural trace tests | None/uniform/weighted shot vectors, zero directions, stationary variables and numeric constants |
| `examples/native_framework_hvp.py` | Actual four-framework toy and native geometry-derived H2 HVP workflows | Independent analytic references, one SCF build and explicit framework dtypes |
| `docs/implementation/stage11p_c2_streamed_framework_hvp_audit.md`, `docs/implementation/stage11p_c2_streamed_framework_hvp_report.md`, `docs/compat/core_parity_ledger.md`, `README.md`, `THIRD_PARTY_NOTICES.md` | Observed gaps, scoped receipts, source attribution and remaining full-parity boundaries | No reduction of the full independent replacement goal |

First Jacobians/classical maps can remain dense; no combined whole-device and
derivative resident-memory bound is claimed. No Studio/Router, cloud/hardware,
token, tag/release, package/environment tree or source vendoring is included.

## Stage 11P-C Native Second Derivatives

Native Implementation and optional classical framework integration. Existing
native quantum plans/devices remain the execution engine. Published math/API
contracts and installed public numerical calls are references only; upstream
implementation/test source ports remain zero.

| Files | Changes | Independent evidence |
| --- | --- | --- |
| `quantumbridge/diff/higher_order_limits.py`, `quantumbridge/diff/second_trace.py`, `quantumbridge/diff/second_order.py`, `quantumbridge/diff/__init__.py` | Bounded second classical graph, exact shift convolution and streamed native HVP | Analytic mixed/controlled/nonlinear rules, preflight resource rejection and real shifted calls |
| `quantumbridge/diff/trace.py`, `quantumbridge/diff/qnode_engine.py`, `quantumbridge/diff/processing.py`, `quantumbridge/qml/qnode.py` | Native Hessian/HVP APIs, moment corrections and actual processor second chain rule | Initial four real red contracts; source-input, coefficient and cross-child terms |
| `quantumbridge/transforms/program.py`, `quantumbridge/transforms/qwc.py`, `quantumbridge/transforms/measurement_transforms.py` | Actual child second derivatives, declared linear sampled processors and allocation boundaries | QWC None/uniform/weighted shot vectors, independent streams and exact integer physical work |
| `quantumbridge/interfaces/native_host.py`, `quantumbridge/interfaces/qnode_autodiff.py`, `quantumbridge/interfaces/jax_autodiff.py`, `quantumbridge/interfaces/tensorflow_autodiff.py` | Fixed numeric/source-variable separation, true second framework rules and third-order rejection | Real Torch gradgradcheck, Autograd Hessian, JAX forward/reverse/JIT/VMAP and nested TF eager/function derivatives |
| `tests/qml/test_native_second_classical_trace.py`, `tests/qml/test_native_second_order.py`, `tests/qml/test_native_second_order_workflows.py` | Independently authored math, resource, stochastic and integrated native tests | Non-dense 100-wire MPS and one fixed-geometry H2 build with ansatz Hessian/HVP/Newton updates |
| `tests/interfaces/test_native_second_order_contracts.py`, `tests/interfaces/test_native_second_order_frameworks.py` | Real second-order graphs and explicit third-order negatives | No detached tensor/constant-gradient substitution |
| `tests/interfaces/test_native_jax_resource_limits.py`, `tests/interfaces/test_native_tensorflow_negative.py`, `tests/gradients/test_native_qnode_derivatives.py` | Obsolete max_diff=2 rejection becomes max_diff=3 rejection; max_diff=2 first gradient checked numerically | Existing default-first-order higher-order negatives remain |
| `tests/compat/test_native_second_order_pennylane_differential.py`, `examples/native_qnode_second_order.py` | Optional public black boxes and SDK-free executable example | Unresolved upstream objects are not numeric parity evidence |
| `docs/implementation/stage11p_c_higher_order_gap_audit.md`, `docs/implementation/stage11p_c_native_second_order_report.md`, `docs/compat/core_parity_ledger.md`, `README.md`, `THIRD_PARTY_NOTICES.md` | Starting gaps, scoped evidence and explicit remaining boundaries | Full independent functional replacement remains incomplete |

No Studio/Router, tags/releases, remote publication, cloud/hardware/token,
authentication/TLS or third-party source/package/environment changes belong to
this historical checkpoint. At that point only the native HVP API streamed;
Stage 11P-C2 above supersedes the framework packed-Hessian limitation.

## Stage 11P-B Native TensorFlow Autodiff

Native Implementation and optional classical framework integration, zero
upstream implementation/test source ports. Public TF contracts are references;
PennyLane public numerical calls are test-only black boxes, not native engines.

| Files | Native changes | Independent evidence |
| --- | --- | --- |
| `quantumbridge/interfaces/native_host.py`, `quantumbridge/interfaces/jax_autodiff.py` | Extracted shared source snapshots, static output shape, fresh native plans and quantum Jacobians; retained JAX behavior | Old JAX regressions plus native TF derivatives; no second quantum engine |
| `quantumbridge/interfaces/tensorflow_autodiff.py`, `quantumbridge/interfaces/__init__.py` | Optional CPU custom-gradient VJP, traced preprocessing, eager/graph status, bounded mapping and work | Real TF GradientTape, variables, graph inputs, failure injection and allocation preflight |
| `quantumbridge/qml/qnode.py`, `quantumbridge/diff/scalars.py`, `quantumbridge/diff/trace.py` | TF dispatch, status/map API, live coefficient retention and framework reshape callback | Nested outputs/cotangents, native circuit reconstruction, coefficient product rule |
| `quantumbridge/qml/template_core.py`, `quantumbridge/qml/embeddings.py` | Static TF scalar validation and shape-indexed template emission | Native AngleEmbedding in eager/graph/MPS derivatives; static state-preparation boundaries |
| `tests/interfaces/test_native_tensorflow_grad.py`, `tests/interfaces/test_native_tensorflow_graph.py`, `tests/interfaces/test_native_tensorflow_transforms.py` | Independently authored basic/transform/Variable/graph math and optimizer tests | Two actual pre-runtime red tests, true native Jacobian spies, fresh graph values and real updates |
| `tests/interfaces/test_native_tensorflow_shots_limits.py`, `tests/interfaces/test_native_tensorflow_negative.py`, `tests/interfaces/test_native_tensorflow_examples.py` | Sampling/limits, explicit unsupported cases, SDK-free MPS/H2 workflows | Actual physical work/seed receipts, failure codes, no-dense 100-wire and one SCF build |
| `tests/interfaces/test_native_qnode_autodiff.py` | Replaced obsolete TF-unsupported assertions with installed/absent optional dependency contracts | Does not skip installed TF as false completion evidence |
| `tests/compat/test_native_tensorflow_pennylane_differential.py` | Six independent public TF black-box scenarios | Explicit typed coefficients prevent public float32 literal conversion from polluting the float64 oracle |
| `examples/native_tensorflow_qnode_gradient.py`, `examples/native_tensorflow_transform_training.py`, `examples/native_tensorflow_mps_100qubits.py`, `examples/native_tensorflow_qchem_h2.py` | Actual native derivative, Keras optimizer, MPS and geometry-derived chemistry examples | No upstream quantum runtime, no cloud/hardware/token, measured native work |
| `docs/implementation/stage11p_b_tensorflow_gap_audit.md`, `docs/implementation/stage11p_b_native_tensorflow_autodiff_report.md`, `pyproject.toml` | Audited gaps, scoped receipts and optional TF extra | Full replacement remains incomplete; no core TF dependency or package vendoring |

No Studio/Router, tag/release, authentication/TLS, remote publication or
third-party source/binary/environment work belongs to this batch.

## Stage 11P-A Native JAX Autodiff

Native Implementation and optional framework integration, not an upstream
quantum-engine adapter. Independent implementation/test source ports: zero.
JAX public custom-JVP/callback/batching contracts are references. All quantum
values/Jacobians are computed by existing native plans, devices and derivatives.

| Files | Native changes | Independent evidence |
| --- | --- | --- |
| `quantumbridge/interfaces/jax_autodiff.py`, `quantumbridge/interfaces/__init__.py` | Optional CPU JAX custom-JVP and real native plan bridge; pure callback shape/status and resource boundaries | Persisted two-test red/green, actual native derivative spies, independent math and public JAX composition |
| `quantumbridge/qml/qnode.py`, `quantumbridge/qml/template_core.py`, `quantumbridge/diff/scalars.py` | Reused source recording, retained JAX scalar/coefficient graphs, static template validation, explicit checked status | Shared/nonlinear/preprocessing/coefficient/PyTree, QWC/defer/compile and dtype tests |
| `tests/interfaces/test_native_jax_grad.py`, `tests/interfaces/test_native_jax_jit.py`, `tests/interfaces/test_native_jax_resource_limits.py` | Independent value/grad/JVP/VJP/Jacobian/JIT/VMAP/error/shape/resource contracts | No finite-diff substitution, actual host return values, x64 subprocess checks and preflight failures |
| `tests/interfaces/test_native_jax_transform_gradients.py`, `tests/interfaces/test_native_jax_shots.py`, `tests/interfaces/test_native_jax_mps_non_dense.py` | Actual child/reverse/coefficient derivatives, seeded sample partitions, non-dense MPS and native H2 | Quantum execution/gradient/work receipts, 100-wire dense APIs forbidden, fixed geometry constructed once |
| `tests/interfaces/test_native_qnode_autodiff.py` | Old JAX-unsupported assertion updated to new tested support; explicit missing-optional-dependency contract added; TF guards retained | Missing-installation behavior is tested separately from installed JAX, not silently skipped as proof |
| `tests/compat/test_native_jax_pennylane_differential.py` | Independently authored public API oracles | Eight matching numerical scenarios per public version; public eager shift/VMAP tracer rejection recorded as a separate expected failure, not matching evidence |
| `examples/native_jax_qnode_gradient.py`, `examples/native_jax_transform_training.py`, `examples/native_jax_mps_100qubits.py`, `examples/native_jax_qchem_h2.py` | Four actual native/JAX workflows | Analytic values/derivatives, optimizer updates, actual MPS telemetry and real Gaussian/RHF/JW Hamiltonian |
| `docs/implementation/stage11p_a_jax_gap_audit.md`, `docs/implementation/stage11p_a_native_jax_autodiff_report.md` | Initial missing interface audit and bounded implementation receipts | Full functional replacement remains incomplete; no reduction of the final goal |

No third-party source/binary/package tree or environment is placed in the
repository. No cloud/token/hardware, Studio/Router or publication work is included.

## Stage 11O-B6 Native Coherent Deferred Measurements

Native Implementation, zero implementation/test source ports. The measurement
record purification and bounded commuting-projector expansion are independently
authored. Existing native dynamic, matrix, compiler and derivative components
are reused. Public documentation and public installed PennyLane calls are
behavioral references/oracles, not the production implementation.

| Files | Native changes | Independent evidence |
| --- | --- | --- |
| `quantumbridge/transforms/deferred_measurements.py`, `quantumbridge/transforms/__init__.py` | Fresh record wires, conditional unitary lowering, phase preservation, logical output mapping and preflight limits | Reused-wire red/green, reduced-state proofs, complete complex control matrices, invalid capacity/noise/reset/postselection boundaries |
| `quantumbridge/transforms/program.py` | Device-specific transform validation, actual record receipts and generic sampled-output storage budgeting | Existing batch regressions; exact physical work and source/ancilla mapping checks |
| `quantumbridge/qml/measurement_records.py`, `quantumbridge/qml/tape.py`, `quantumbridge/qml/qnode.py`, `quantumbridge/diff/qnode_engine.py` | Ordered real classical records and quantum terminal samples on the existing dynamic engine; coherent ancilla reconstruction | Native statevector/density/MPS probabilities, joint finite records, seed/vector and derivative tests |
| `tests/transforms/test_native_deferred_measurements.py`, `tests/compat/test_native_deferred_measurement_differential.py` | Independently authored physics, matrix, framework, resource and public black-box scenarios | Both installed public versions; actual coherent child derivatives, no-dense 101-wire execution and geometry-derived H2 integration |
| `examples/native_defer_measurements.py`, `examples/native_defer_reused_wire.py`, `examples/native_defer_transform_gradient.py`, `examples/native_defer_mps_100qubits.py`, `examples/native_stage11o_integrated_h2.py` | Five SDK-free executable workflows | Actual values, record mapping, gradients, resource receipts and unsupported boundaries |
| `docs/implementation/stage11o_b6_native_deferred_measurements_report.md`, `docs/implementation/stage11o_joint_acceptance_report.md`, `docs/implementation/stage11o_remaining_functional_parity_gaps.md` | Scoped evidence and remaining full functional contracts | No conversion of a bounded joint checkpoint into complete Qiskit/PennyLane parity |

No third-party implementation, test suite, environment, binary package,
credential or source tree is vendored. Full replacement remains incomplete.

## Stage 11O-B5 Native Transformed Autodiff

Native Implementation; zero implementation/test source ports. Existing native
quantum engines supply all quantum derivatives. Optional Torch/Autograd retain
classical graphs; public PennyLane 0.44.1/0.42.3 calls are differential test
oracles only. No SDK implementation/tests, package artifacts, credentials,
environment trees or private SDK gradient helpers are copied or used at runtime.

| Files | Native changes | Independent evidence |
| --- | --- | --- |
| `quantumbridge/diff/processing.py`, `quantumbridge/transforms/program.py`, `quantumbridge/diff/qnode_engine.py` | Means-only derivative payload, bounded chunked Dual postprocessing Jacobian, child native shift/adjoint and complete result/input chain | Torch QWC squared-loss red/green; native Jacobian/VJP/JVP, reverse-order and nested/multi-child tests |
| `quantumbridge/diff/scalars.py`, `quantumbridge/utils/math.py`, `quantumbridge/qml/tape.py`, `quantumbridge/qml/qnode.py`, `quantumbridge/transforms/qwc.py`, `quantumbridge/transforms/measurement_transforms.py` | Retained scalar coefficient graphs, declared processing slots/product rules, ordinary live-coefficient native preprocessing and explicit unsupported boundaries | Coefficient-only/shared-angle/identity/zero/scaling/native/Torch/Autograd tests and public coefficient derivatives |
| `quantumbridge/qml/pauli_group.py`, `quantumbridge/devices/matrix_product_state_device.py`, `quantumbridge/information/matrix_product_state.py` | Actual-call MPS telemetry, no extra resource-only circuits, tensor storage and group receipts | 100-wire GHZ+AngleEmbedding+Transform gradient with dense APIs forbidden, actual bond/storage/truncation proof |
| `tests/transforms/test_native_transformed_autodiff.py`, `tests/compat/test_native_transformed_gradient_differential.py`, existing B1/B2/B4 tests | Independently authored mathematical/runtime/framework/sampling tests; old unsupported assertions upgraded to real derivative checks without deleting scenarios | Both public SDK versions, full regression gates, actual shared sample/shift/partition receipts |
| `examples/native_transformed_autodiff.py`, `examples/native_mps_template_transform_gradient.py`, `examples/native_qchem_transformed_gradient.py` | SDK-free coefficient/gate VJP, non-dense MPS and geometry-derived H2 optimization | Executable numerical assertions and actual metadata |
| `docs/implementation/stage11o_b5_native_transformed_autodiff_report.md`, `docs/compat/core_parity_ledger.md`, `README.md`, `THIRD_PARTY_NOTICES.md` | Test receipts, implementation boundaries and source accounting | B6/full parity remain incomplete; no new-SHA remote CI is inferred |

No source port was performed. This is a supported first-order native checkpoint,
not all PennyLane transform/gradient or Qiskit functional replacement.

## Stage 11O-B4 Native QWC And Shot Allocation

Native Implementation, zero implementation/test source ports. Native Tape,
QNode, Device sampling and existing parameter binding are reused. Public
PennyLane 0.44.1/0.42.3 APIs are behavioral oracles only. No upstream source,
private helpers, tests, credentials, package artifacts or environments are
copied, imported as implementations or vendored.

| Files | Independently implemented behavior | Evidence |
| --- | --- | --- |
| `quantumbridge/qml/pauli_group.py`, `quantumbridge/diff/qnode_engine.py` | Validated common Pauli basis, actual single shared native sample buffer, per-word eigenvalues, exact/empirical covariance and truthful execution receipts | XX/YY non-QWC counterexample, per-shot X/XZ equality, Y sign/wire order, covariance/anticorrelation, density/dynamic/MPS execution |
| `quantumbridge/qml/qnode.py` | Reject currently unsupported transformed live input graphs before a builder can detach coefficient-only inputs | Red/green Torch coefficient-only counterexample; ordinary untransformed behavior unchanged |
| `quantumbridge/transforms/qwc.py`, `quantumbridge/transforms/program.py`, `quantumbridge/transforms/__init__.py` | Bounded grouping, deduplication/identity offsets/nested reconstruction, deterministic uniform/weighted allocation, sibling allocation validation and resource budgets | Integer/partition conservation, copies/seed independence, budget/undersampling errors and unchanged B1-B3 regressions |
| `tests/transforms/test_native_qwc_grouping.py`, `tests/compat/test_native_qwc_differential.py` | Independent mathematical/runtime/counterexample tests and public API differential scenarios | Both installed public PennyLane versions; real geometry-generated H2 execution |
| `examples/native_qwc_shot_allocation.py` | SDK-free shared sampling example with group IDs, basis, counts, shots, energy and standard error | Per-partition physical-shot conservation and numerical assertions |
| `docs/implementation/stage11o_b4_native_qwc_shot_allocation_report.md`, `docs/compat/core_parity_ledger.md`, `README.md`, `THIRD_PARTY_NOTICES.md` | Actual supported contracts, version differences, test receipts and remaining work | Full replacement remains incomplete; B5 derivatives and B6 defer/integration remain open |

Public 0.42.3 has no shot allocation API; 0.44.1 collapses distributed shot
vectors and may omit zero-shot groups. Native preservation of partitions and
explicit rejection of undersampled nonzero groups are documented differences,
not claimed parity. No new source port was performed.

## Stage 11O-B2/B3 Native QNode And Basic Transforms

Native Implementation; no implementation/test source ports. Optional public
PennyLane calls are black-box behavioral oracles only, with explicit complex
matrix/global-phase checks. SDK implementation/test files are not copied,
imported as private helpers or vendored. Native execution requires no SDK.

| Files | Native changes | Independent evidence |
| --- | --- | --- |
| `quantumbridge/qml/qnode.py`, `quantumbridge/transforms/dispatch.py`, `quantumbridge/transforms/program.py`, `quantumbridge/transforms/__init__.py` | Fresh QNode construction, Tape/callable dispatch and shared child native plans, dependency/parameter slices and recorder ownership | Repeated .2/.7 inputs, changing batch widths, shared/nonlinear/keyword inputs, direct mutation and framework rejection tests |
| `quantumbridge/transforms/circuit_transforms.py`, `quantumbridge/transforms/gate_transforms.py`, `quantumbridge/transforms/measurement_transforms.py` | Safe native inverse/rotation algebra, recursive definition and basis expansion, target compiler integration, one-Tape deduplicated measurement reconstruction | Exact complex matrices, dynamic boundaries, source ownership, resource and layout counterexamples |
| `quantumbridge/compiler/decomposition.py`, `quantumbridge/compiler/transpile.py` | Shared decomposition output/work/nesting budgets, including lexical control bodies | Compiler regression suite and cross-body expansion budget tests |
| `tests/transforms/test_native_qnode_transform_dispatch.py`, `tests/transforms/test_native_basic_transforms.py`, `tests/compat/test_native_transform_differential.py` | Independently authored native mathematics/runtime tests and public black-box differential comparisons | Both pinned PennyLane versions, no private SDK implementation use |
| `examples/native_transform_qnode.py`, `examples/native_measurement_splitting.py`, `examples/native_qchem_transform_energy.py` | Real repeated QNode/measurement and geometry-derived H2 computation | SDK-free executable numerical assertions and execution IDs |
| `docs/implementation/stage11o_ab_native_gap_audit.md`, `docs/implementation/stage11o_b2_b3_native_transform_report.md`, `docs/compat/core_parity_ledger.md`, `README.md`, `THIRD_PARTY_NOTICES.md` | Supported behavior, test receipts, provenance and remaining full-parity gaps | B4-B6 and the full-replacement objective remain unfinished |

Transformed VJP, QWC/shot allocation, defer_measurements and joint Stage 11O
acceptance are not claimed by this checkpoint. Source port count remains zero.

## Stage 11O-B1 Native Transform Execution Checkpoint

Native Implementation, zero implementation/test source ports. Native child
Tapes execute through the existing QuantumBridge QNode plan and Device, not
an upstream SDK. The Hamiltonian splitting prototype is not the full public
PennyLane split_to_single_terms contract. No SDK source/tests, credentials,
package artifacts or environment are included.

| Files | Independently implemented behavior | Evidence |
| --- | --- | --- |
| `quantumbridge/qml/tape.py` | Owned structural copies retaining parameter graphs; explicit nested outputs and local shots/seed | Mutation, nested tree, native expression and live scalar graph tests |
| `quantumbridge/transforms/program.py`, `quantumbridge/transforms/__init__.py` | Bounded Tape batching, reverse reconstruction and independent native execution | Counting Device, IDs, staged errors and resource preflight |
| `quantumbridge/transforms/circuit_transforms.py`, `quantumbridge/transforms/measurement_transforms.py` | Safe rotation segment merging and real weighted Hamiltonian child-Tape execution | Complete unitary, dynamic boundary, zero/identity/duplicate/shot tests |
| `quantumbridge/qml/templates.py`, `quantumbridge/templates.py` | Explicit legacy functional migration warning, unchanged modern object and legacy ansatz alternative | Independent old/new gate-sequence regression |
| `tests/transforms/test_native_transform_program.py`, `examples/native_transform_program.py` | Independently authored multi-Tape correctness tests and SDK-free example | Actual three-child evaluation and geometry-generated H2 energy |
| `scripts/run_local_matrix.sh` | Consume the coverage-help probe fully under pipefail instead of misreporting an installed plugin as absent | Old probe exits 1; full-consuming probe exits 0; full matrix coverage rerun |
| `docs/implementation/stage11o_b1_native_transform_execution_report.md`, `docs/compat/core_parity_ledger.md`, `README.md`, `THIRD_PARTY_NOTICES.md` | Explicit checkpoint evidence, limitations and source accounting | No full transform, SDK replacement or publication claim |

QWC grouping, shot allocation, transformed native VJP and complete Stage 11O-B
are still required. Source port count remains zero.

## Stage 11O-A Native Templates Checkpoint

Native Implementation; zero third-party implementation/test source ports.
Existing QML helpers and native Operation/Circuit/Tape/QNode/gradient engines
are enhanced, not replaced by a second execution system. Public PennyLane
0.44.1/0.42.3 functions are optional differential oracles. No runtime SDK
dependency, package tree, wheel, environment or token is included.

| Files | Independently implemented behavior | Evidence |
| --- | --- | --- |
| `quantumbridge/qml/template_core.py`, `quantumbridge/templates.py` | Bounded concrete template decomposition, named-wire mapping and live native emission | Native shape/resource/graph and public tests |
| `quantumbridge/qml/embeddings.py`, `quantumbridge/qml/templates.py`, `quantumbridge/qml/subroutines.py`, `quantumbridge/qml/__init__.py` | Real amplitude/basis/angle, entangler layers, IQP/QFT/Trotter gates and exports | Independent complex matrices/states, gradients and public contracts |
| `quantumbridge/devices/execution.py`, `quantumbridge/devices/statevector_device.py`, `quantumbridge/devices/density_matrix_device.py`, `quantumbridge/devices/matrix_product_state_device.py`, `quantumbridge/execution/control_flow_engine.py` | Actual runtime zero-subsystem precondition for bounded amplitude preparation | Nonzero initial state rejection, IR and shared dynamic path tests |
| `tests/templates/test_native_templates.py`, `tests/templates/test_native_template_gradients.py`, `tests/compat/test_native_template_differential.py`, `tests/qml/test_pennylane_templates_p2.py` | Mathematical/runtime/gradient/resource tests; obsolete metadata-only test now checks actual complex state | Native and optional black-box differential, no copied upstream tests |
| `examples/native_angle_embedding_qnode.py`, `examples/native_entangling_templates_training.py`, `examples/native_qft_and_trotter.py` | Actual SDK-free input derivative, two-wire training and complex QFT/Trotter convergence | Executable assertions and measured values |

Stage 11O-B real multi-Tape execution and postprocessing are still unfinished.
This checkpoint is not full PennyLane template or transform parity.

## Stage 11O-C Native Molecular Electronic Structure Checkpoint

Native Implementation, zero implementation/test source ports. Six numerical
hydrogen STO-3G parameters are scientific input data from MolSSI BSE v1, with
source and license boundary in `LICENSES/BSE_DATA_NOTICE.txt`; no BSE software
or environment is included. Native computation uses only NumPy/standard math.
Public PennyLane/PySCF calls are optional test oracles, not runtime chemistry
dependencies. Templates and multi-Tape transforms remain unfinished Stage 11O
work; neither whole Stage 11O nor complete qchem is marked complete.

| Files | Native computation | Evidence |
| --- | --- | --- |
| `quantumbridge/chemistry/fermion.py`, `quantumbridge/chemistry/mappings.py`, `quantumbridge/chemistry/qubit_hamiltonian.py` | CAR contractions/signs, independent occupation action, complex general Jordan-Wigner mapping and bounded matrices | Native algebra and public operator comparisons |
| `quantumbridge/chemistry/molecule.py`, `quantumbridge/chemistry/limits.py`, `quantumbridge/chemistry/basis.py` | Validated elements/electrons/spin/units, native resource budgets and normalized H s shells | Native invalid/input/unit and numerical tests |
| `quantumbridge/chemistry/gaussian_integrals.py`, `quantumbridge/chemistry/integrals.py` | Analytic Gaussian overlap/kinetic/attraction/ERI/Boys, AO tensors and nuclear geometry | Mathematical tests and independent public AO integrals |
| `quantumbridge/chemistry/scf.py`, `quantumbridge/chemistry/molecular_hamiltonian.py` | Actual RHF iterations, MO tensor transform, fermionic Hamiltonian, JW and electron-sector exact energy | Multiple geometries, HF/FCI energy and public comparisons |
| `quantumbridge/chemistry/excitations.py`, `quantumbridge/chemistry/__init__.py`, `quantumbridge/qchem.py` | Concrete API exports, HF occupations/excitations and exact commuting-Pauli native excitation circuits | Matrix exponential, native shift/adjoint, Torch/Autograd and VQE |
| `tests/qchem/test_native_fermionic_algebra.py`, `tests/qchem/test_native_hydrogen_electronic_structure.py`, `tests/compat/test_native_qchem_differential.py` | Independently authored mathematical/runtime/optional public tests | SDK-free and two pinned public SDK versions |
| `tests/chemistry/test_pyscf_driver_optional.py` | Existing availability test now specifies the physical hydrogen doublet | Full installed regression; no native open-shell claim |
| `examples/native_qchem_h2_integrals.py`, `examples/native_qchem_h2_scf.py`, `examples/native_qchem_h2_vqe.py` | Geometry-based SDK-free integral/RHF/VQE workflows | Actual computation, not fixed Hamiltonian lookup |

## Stage 11N Native Simulator And Noise

Native Implementation; source port count zero. Public SDK behavior is tested
only through optional black-box calls. No runtime SDK dependency, source/test
copying, environment/package upload, token access or hardware job. Full API,
GPU, parallelism, arbitrary correlated-readout and performance parity remain
unsupported or partial as recorded in the Stage 11N report.

| Files | Independent behavior | Evidence |
| --- | --- | --- |
| `quantumbridge/simulator/__init__.py`, `quantumbridge/simulator/aer.py`, `quantumbridge/simulator/limits.py` | Existing Backend/Job integration, real method selection, bounded maps and options | Native method/resource tests; public optional comparisons |
| `quantumbridge/simulator/instructions.py`, `quantumbridge/simulator/snapshots.py` | In-order Save/Set, native tensor/tableau and grouped snapshots, JSON-safe result data | Intermediate states, replacement, conditional/pershot, no-dense and hostile-input tests |
| `quantumbridge/noise/quantum_error.py`, `quantumbridge/noise/error_model.py`, `quantumbridge/noise/__init__.py` | Native CPTP algebra, ten constructor families, physical gate and readout bindings | Independent mathematical/CPTP and public channel comparisons |
| `quantumbridge/core/circuit.py`, `quantumbridge/results/result.py`, `quantumbridge/execution/control_flow_engine.py` | Actual instruction timing, feedback, per-executed-gate noise, snapshots and result serialization | Runtime-loop/noise, IR/JSON and physical-target tests |
| `quantumbridge/devices/execution.py`, `quantumbridge/devices/density_matrix_device.py`, `quantumbridge/devices/matrix_product_state_device.py`, `quantumbridge/devices/stabilizer_device.py`, `quantumbridge/diff/adjoint.py` | Reuse native state adapters and reject unsupported noisy adjoint | Existing devices/gradients regressions and 100-wire tensor tests |
| `tests/compat_qiskit_aer/test_native_aer_engine.py`, `tests/compat_qiskit_aer/test_native_aer_dynamic_and_limits.py`, `tests/compat_qiskit_aer/test_native_aer_differential.py`, `tests/noise/test_native_quantum_error_algebra.py` | Independently authored tests; installed SDKs are optional oracles only | Three isolated environments |
| `examples/native_aer_save_set.py`, `examples/native_aer_gate_noise.py`, `examples/native_aer_density_mps.py`, `examples/native_aer_dynamic_snapshots.py` | Actual SDK-free native workflows | Executed examples |

## Stage 11M Native Serialization

Native Implementation; source port count zero. Public OpenQASM and QPY format
documentation and public SDK reader/writer calls are references, not copied
implementations or runtime dependencies. No upstream source/tests, package
artifacts, environment, credentials or hardware submissions are included.
Full format/SDK parity is not claimed; supported protocol branches and explicit
rejections are recorded in the Stage 11M report.

| Files | Independent behavior | Evidence |
| --- | --- | --- |
| `quantumbridge/serialization/__init__.py`, `quantumbridge/serialization/errors.py`, `quantumbridge/serialization/limits.py`, `quantumbridge/serialization/common.py` | Native public API, structured errors, bounded I/O and register maps | Native malformed/resource/file tests |
| `quantumbridge/serialization/text_ast.py`, `quantumbridge/serialization/text_lexer.py`, `quantumbridge/serialization/text_parser.py` | Tokenization, typed syntax tree and recursive grammar | QASM2/3 source programs and hostile input |
| `quantumbridge/serialization/text_lowering.py`, `quantumbridge/serialization/text_exporter.py`, `quantumbridge/serialization/text_api.py`, `quantumbridge/serialization/control_normalization.py` | Source/Circuit semantics, runtime blocks, branch snapshots, standard phase and explicit Qiskit dialect | Actual native execution and public optional comparisons |
| `quantumbridge/serialization/qpy.py`, `quantumbridge/serialization/qpy_expressions.py` | Actual QPY v13 binary protocol and arithmetic replay | Real binary bilateral loading, multiple circuits, parameters and corruption tests |
| `quantumbridge/serialization/interchange.py` | Standard-format conversion and explicitly external provenance sidecars | Compiler/layout, QNode gradients, IR and 100-qubit MPS |
| `quantumbridge/core/classical.py`, `quantumbridge/core/control_flow.py`, `quantumbridge/core/parameters.py`, `quantumbridge/ir/qb_ir.py` | Signed classical storage, loop types and optional parameter UUID preservation | Existing native regressions and new serialization tests |
| `quantumbridge/qasm/importer.py`, `quantumbridge/qasm/exporter.py`, `quantumbridge/qml/qnode.py` | Existing source API integration and native restored-circuit differentiation | Existing QASM and gradient regressions |
| `quantumbridge/compat/qos_uqci/openqasm_bridge.py`, `quantumbridge/compat/quafu/cloud_backend.py` | Existing source-only adapter integration uses explicit external metadata policy | Offline/mock regressions only; no hardware job or token access |
| `tests/serialization/`, `tests/compat/test_native_serialization_differential.py` | Independently authored native and optional public black-box tests | Three isolated environments, no source copying |
| `examples/native_qasm2_roundtrip.py`, `examples/native_qasm3_dynamic_roundtrip.py`, `examples/native_qpy_binary_roundtrip.py`, `examples/native_format_interchange.py`, `examples/native_serialization_compiled_circuit.py` | SDK-free callable workflows | Native execution; optional SDK codec only |

## Stage 11L Native Compiler

Native Implementation only; zero source ports. Public SDK black-box behavior
is used in optional tests; neither SDK is used to compile native circuits.
No new dependency, vendored package, credentials, cloud or hardware submission.
Review pending; exact-phase, numeric tolerance, layout decoding and bounded
resource growth are documented risks. Full parity remains incomplete.

| Files | Native behavior | Evidence |
| --- | --- | --- |
| `quantumbridge/compiler/dag.py`, `quantumbridge/compiler/traversal.py`, `quantumbridge/compiler/limits.py` | Dependency graph, scope traversal and limits | tests/compiler/test_native_transpiler_engine.py |
| `quantumbridge/compiler/pass_manager.py`, `quantumbridge/compiler/pass_base.py`, `quantumbridge/compiler/analysis.py` | Analysis lifetime, callbacks, staged bounded passes, structural/runtime distinction | Mutation, requirement, invalidation and runtime tests |
| `quantumbridge/compiler/target.py`, `quantumbridge/compiler/coupling.py`, `quantumbridge/compiler/layout.py` | Target properties, directed paths and mapping | Capacity/qargs/duration/layout tests |
| `quantumbridge/compiler/decomposition.py`, `quantumbridge/compiler/routing.py`, `quantumbridge/compiler/scheduling.py`, `quantumbridge/compiler/transpile.py`, `quantumbridge/compiler/cancellation.py`, `quantumbridge/compiler/__init__.py` | Exact-phase translation, real routing, static timing, symbolic optimization | Independent operators and public SDK comparison |
| `quantumbridge/core/circuit.py`, `quantumbridge/ir/qb_ir.py`, `quantumbridge/information/operator.py`, `quantumbridge/devices/statevector_device.py`, `quantumbridge/utils/math.py` | Phase binding/composition/control/execution/IR | Exact operators, coherent control, IR and existing regressions |
| `quantumbridge/devices/matrix_product_state_device.py`, `quantumbridge/execution/control_flow_engine.py`, `quantumbridge/compat/qiskit_adapter.py` | Phase in existing execution/adapter paths | MPS/dynamic/optional SDK tests |
| `quantumbridge/diff/compiled_parameters.py`, `quantumbridge/qml/qnode.py` | First-order compiled parameter-expression chain rule | Native/Torch/Autograd gradient tests |
| `tests/compat/test_native_transpiler_differential.py` | Twelve meaningful public operator scenarios | Optional Qiskit 2.4/2.6 oracle only |
| `examples/native_transpile_*.py` | Static timing, runtime branch and offline DeviceSpec execution | SDK-free examples |

## Stage 11K Native QNode Differentiation

Native Implementation, source port count zero. Optional Torch/Autograd provide
classical framework integration, not quantum derivatives; installed PennyLane
is a public black-box oracle only. No source/test copying, secret reading,
vendored package or environment upload. Review remains pending. Numerical
truncation, stochastic estimates, resource growth and unsupported higher-order,
JAX/TF/backprop/capture semantics remain documented limitations.

| Files | Native behavior | Evidence |
| --- | --- | --- |
| `quantumbridge/diff/trace.py`, `quantumbridge/diff/qnode_engine.py`, `quantumbridge/diff/parameter_shift.py` | First-order classical chain rule, recorded gate occurrences, native shift/finite-diff, shape/capability budgets | tests/gradients/test_native_qnode_derivatives.py |
| `quantumbridge/diff/adjoint.py` | Forward vector and inverse-state/reverse-cotangent derivatives | Independent analytic and public oracle comparisons |
| `quantumbridge/qml/qnode.py`, `quantumbridge/qml/tape.py`, `quantumbridge/qml/shot_vector.py` | Unified QNode forward/gradient/Jacobian/VJP/JVP and shot partitions | Native nested-output, shot, training and dynamic tests |
| `quantumbridge/interfaces/qnode_autodiff.py` | Torch and Autograd native-quantum VJPs with framework classical graphs | tests/interfaces/test_native_qnode_autodiff.py |
| `quantumbridge/devices/matrix_product_state_device.py`, `quantumbridge/execution/control_flow_engine.py` | Observed trajectory bond profiles retained without dense expansion | MPS/dynamic regressions and 100-qubit derivative test |
| `tests/compat/test_native_autodiff_differential.py` | Fourteen meaningful public gradient scenarios and explicit upstream version difference | PL 0.44.1 and 0.42.3 environments |
| `examples/native_qnode_*.py` | Native/Torch training, adjoint and shot partitions | SDK-free native examples; optional Torch example |

## Stage 11J Native Dynamic Control Flow

Native Implementation only; no third-party source or tests copied, no vendored
packages/environments. Public API/mathematical behavior is the reference.
Review is pending. Resource exhaustion, numeric approximation and differing
SDK interfaces remain documented risks; this is not a full replacement claim.

| Files | Native behavior | Evidence |
| --- | --- | --- |
| `quantumbridge/core/classical.py` | Typed immutable expressions, UInt wrapping, register order, initialized lexical storage and JSON | tests/circuit/test_classical_expressions_native.py |
| `quantumbridge/core/control_flow.py`, `quantumbridge/core/circuit.py` | Structured blocks, scoped variables, binding/remapping, runtime assignments and execution budgets | 43 distinct control-flow tests |
| `quantumbridge/execution/control_flow_engine.py` | Native runtime interpreter, branching/trajectories, reset, CPTP, feedback and limits | Same suite, 100-qubit non-dense test, optional SDK comparisons |
| `quantumbridge/devices/*`, `quantumbridge/providers/backend.py`, `quantumbridge/primitives/estimator.py` | Incremental dynamic vector/density/MPS/tableau and Job/V2 integration | Existing suites plus dynamic execution tests |
| `quantumbridge/ir/qb_ir.py` | Executable structured IR and parameter AST roundtrips | Native nested JSON/remapping tests |
| `quantumbridge/qml/tape.py` | Native mid-circuit measurement/reset and conditional callback | Native and PennyLane black-box comparisons |
| `examples/native_dynamic_control_flow.py`, `examples/native_measurement_feedforward.py`, `examples/native_mps_dynamic_100_qubits.py` | Runnable SDK-free workflows | Clean isolated environment |

## Stage 11I Native MPS Execution

All paths below use Native Implementation. No upstream source/test files or
environments were copied or vendored. Only public mathematical/API definitions
were consulted; optional installed SDKs are behavioral oracles. Review remains
pending; the main risk is numerical truncation, exponential entanglement or
analytic branch growth. Full SDK/device/save-instruction parity is not claimed.

| Files | Implemented behavior | Verification |
| --- | --- | --- |
| `quantumbridge/information/matrix_product_state.py` | Connected qubit tensors, QR center, Schmidt truncation, local/nonlocal gates, reduced states/probabilities, Pauli contractions, collapse and JSON | Native random-complex, truncation and dense-call-blocked 100-qubit tests |
| `quantumbridge/devices/matrix_product_state_device.py` | Native MPS analytic ensembles, Kraus/measurement trajectories, reset, feedback, readout and observables | Device suite and optional Aer MPS differential tests |
| `quantumbridge/devices/execution.py`, `quantumbridge/devices/density_matrix_device.py` | Shared validated ordered execution program, retaining mixed-device behavior | Existing density/stabilizer suites plus MPS tests |
| `quantumbridge/providers/matrix_product_state_backend.py`, `quantumbridge/providers/provider.py` | Discoverable Backend/Job, binding, batches and isolated MPS options | Native provider/V2 tests |
| `quantumbridge/results/result.py`, `quantumbridge/qml/qnode.py`, `quantumbridge/noise/execution.py` | Compressed MPS Result, direct QNode reduction and noisy sampler dispatch | JSON roundtrip, 100-qubit reduced QNode and noisy-observable tests |
| `quantumbridge/primitives/estimator.py` | Allow analytic precision zero; reject nonfinite/negative/bool precision | V2 MPS integration and precision validation tests |
| `quantumbridge/compat/qiskit_aer/simulator_native.py`, package exports | Callable native MPS method and IR dispatch without upstream execution | Native IR roundtrip and optional Aer/PennyLane comparisons |
| `examples/native_matrix_product_state_quantumbridge.py` | Runnable 100-qubit compressed simulation, sampling and noisy native QNode | SDK-free example execution |

## Historical Ledger

| QuantumBridge file | Feature | Mode | Referenced Qiskit? | Referenced PennyLane? | Original project path | Original license | Copied code? | Modified code? | Modification notes | Copyright retained? | THIRD_PARTY_NOTICES updated? | Tests? | Reviewer | Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `quantumbridge/compat/qiskit_adapter.py` | Qiskit circuit import/export, IR bridge, counts Result adapter | Adapter Integration | API only | No | N/A | Apache-2.0 dependency | No | No | Converts public Qiskit objects to/from QuantumBridge Circuit/IR and adapts counts mappings to Result | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/pennylane_adapter.py` | PennyLane observable, tape, and executable subset bridge | Adapter Integration | No | API only | N/A | Apache-2.0 dependency | No | No | Converts public PennyLane observables/tapes and builds a minimal executable form from QuantumBridge circuits or IR | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/__init__.py` | Compatibility adapter exports | Adapter Integration | API naming only | API naming only | N/A | Apache-2.0 dependencies | No | No | Re-exports QuantumBridge adapter functions | N/A | Yes | Import coverage | Pending | Low |
| `quantumbridge/__init__.py` | Top-level optional adapter exports | Adapter Integration | API naming only | No | N/A | Apache-2.0 dependency | No | No | Re-exports adapter functions for user convenience | N/A | Yes | Import coverage | Pending | Low |
| `quantumbridge/legal/attribution.py` | Attribution file validation | Native Implementation | Filename/check only | Filename/check only | N/A | N/A | No | No | Checks required license and notice files exist | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/compat/qasm_adapter.py` | OpenQASM subset import | Native Implementation | No | No | N/A | N/A | No | No | Native parser for QuantumBridge supported subset | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/operators/*` | Pauli and sparse Pauli-like operators | Native Implementation | No | No | N/A | N/A | No | No | Native data structures | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/information/*` | Statevector, DensityMatrix, and Operator native quantum-information wrappers | Native Implementation | API naming only where compatibility docs mention Qiskit | No | N/A | N/A | No | No | Native linear algebra wrappers; no upstream source copied | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/primitives/*` | Sampler and Estimator | Native Implementation | No | No | N/A | N/A | No | No | Native wrappers over QuantumBridge device/runtime | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/qml/*` | QNode/Tape/templates | Native Implementation | No | Conceptual workflow only | N/A | N/A | No | No | Native minimal QML API | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/interfaces/*` | NumPy/Torch/JAX interfaces | Adapter Integration | No | No | N/A | Various optional dependencies | No | No | Optional array conversion adapters | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/providers/*` | Backend/Job/Provider | Native Implementation | No | No | N/A | N/A | No | No | Native provider abstraction | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/compiler/*` | Compiler placeholders | Native Implementation | No | No | N/A | N/A | No | No | Minimal native pass/coupling/target abstractions | N/A | Yes | Not P0 tested | Pending | Low |
| `quantumbridge/visualization/*` | Text drawer | Native Implementation | No | No | N/A | N/A | No | No | Minimal native text visualization | N/A | Yes | Not P0 tested | Pending | Low |
| `quantumbridge/legal/*` | Attribution validation automation | Native Implementation | No | No | N/A | N/A | No | No | Checks required notice, ledger, and license files exist | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/qasm/*` | P2 grammar-based QASM subset parser/exporter | Native Core | No | No | N/A | N/A | No | No | QuantumBridge-owned lexer/parser/AST for documented subset | N/A | Yes | P2 tests | Pending | Medium |
| `quantumbridge/schema/*` | P2 result schema and JSON serialization | Native Core | No | No | N/A | N/A | No | No | Versioned QuantumBridge result payload schema | N/A | Yes | P2 tests | Pending | Low |
| `quantumbridge/chemistry/*` | P2 chemistry native models and optional adapters | Native Core / Adapter Integration / Upstream Passthrough | API only where optional | No | N/A | Optional upstream dependencies | No | No | Molecule/FermionicOp/JW native subset; Qiskit Nature, PySCF, OpenFermion adapters require optional packages | N/A | Yes | P2 tests | Pending | High |
| `quantumbridge/algorithms/adapters/*` | Qiskit Algorithms optional adapter | Upstream Passthrough | API only | No | N/A | Optional qiskit-algorithms dependency | No | No | Calls/wraps installed upstream algorithms only when available | N/A | Yes | P2 tests | Pending | High |
| `scripts/inventory_qiskit_nature_api.py` | Qiskit Nature public API runtime inventory | Upstream API inventory | Runtime public API only | No | N/A | Optional qiskit-nature dependency | No | No | Uses Python introspection of installed package; does not copy source or docs | N/A | Yes | Inventory tests | Pending | Medium |
| `scripts/inventory_qiskit_algorithms_api.py` | Qiskit Algorithms public API runtime inventory | Upstream API inventory | Runtime public API only | No | N/A | Optional qiskit-algorithms dependency | No | No | Uses Python introspection of installed package; does not copy source or docs | N/A | Yes | Inventory tests | Pending | Medium |
| `quantumbridge/noise/*` | P1 basic noise channels and error model | Native Implementation | No | No | N/A | N/A | No | No | Native BitFlip, PhaseFlip, Depolarizing, ReadoutError, NoiseModel metadata | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compiler/*` | P1 compiler PassManager and basic passes | Native Implementation | No | No | N/A | N/A | No | No | Native PassResult, analysis passes, cancellation pass, merge placeholder | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/ecosystem/*` | Optional ecosystem dependency/version/inventory/provenance registry | Native Implementation | Public package names only | Public package names only | N/A | N/A | No | No | Independently implemented registry for optional dependency introspection and result provenance | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/qiskit_core/*` | Qiskit core inventory and passthrough scaffold | Adapter Integration | API names only | No | N/A | Apache-2.0 dependency | No | No | Lazy imports public Qiskit modules when installed and wraps metadata | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/qiskit_aer/*` | Qiskit Aer inventory, passthrough scaffold, and educational native simulator/noise subset | Adapter Integration / Native Subset | API names only | No | N/A | Apache-2.0 dependency | No | No | Optional Aer objects plus independently implemented small statevector, qasm-counts, and simple sampling-noise workflows; no Aer parity or production simulator claim | N/A | Yes | Yes | Stage 9F partial executable | Medium |
| `quantumbridge/compat/mitiq/*` | Mitiq optional dependency metadata plus educational native ZNE/readout mitigation subset | Adapter Integration / Native Subset | API names only through optional ecosystem context | No | N/A | Upstream dependency if installed separately | No | No | Optional Mitiq dependency detection plus independently implemented small zero-noise extrapolation and readout calibration-matrix workflows; no Mitiq parity, production error-mitigation, or hardware calibration claim | N/A | Yes | Yes | Stage 9G partial executable | Medium |
| `quantumbridge/schema/error_mitigation_results.py` | Error mitigation result envelopes | Native Implementation | No | No | N/A | N/A | No | No | QuantumBridge-owned schemas for native ZNE, readout mitigation, upstream passthrough, and comparison results | N/A | Yes | Yes | Stage 9G partial executable | Low |
| `quantumbridge/compat/pennylane_qiskit/*` | PennyLane-Qiskit optional dependency metadata plus educational native bidirectional bridge subset | Adapter Integration / Native Subset | API names only through optional ecosystem context | No | N/A | Upstream dependency if installed separately | No | No | Optional PennyLane-Qiskit dependency detection plus independently implemented Qiskit/PennyLane bridge workflows; no plugin parity, production parity, cloud, token, or hardware claim | N/A | Yes | Yes | Stage 9H partial executable | Medium |
| `quantumbridge/schema/pennylane_qiskit_bridge_results.py` | PennyLane-Qiskit bridge result envelopes | Native Implementation | No | No | N/A | N/A | No | No | QuantumBridge-owned schemas for native bridge, upstream passthrough, IR summary, execution, and equivalence results | N/A | Yes | Yes | Stage 9H partial executable | Low |
| `quantumbridge/compat/qiskit_runtime/*` | Qiskit IBM Runtime inventory and passthrough scaffold | Adapter Integration | API names only | No | N/A | Upstream dependency | No | No | Optional runtime/backend/job dependency lane; no credentials or service emulation | N/A | Yes | Inventory smoke | Pending | High |
| `quantumbridge/compat/qiskit_finance/*` | Qiskit Finance inventory, passthrough scaffold, FinanceResult wrapper, and educational native portfolio subset | Adapter Integration / Native Subset | API names only | No | N/A | Upstream dependency | No | No | Optional finance objects plus independently implemented deterministic mean-variance exact enumeration; no production finance claims | N/A | Yes | Yes | Pending | High |
| `quantumbridge/compat/qiskit_optimization/*` | Qiskit Optimization inventory, passthrough scaffold, and educational native QuadraticProgram subset | Adapter Integration / Native Subset | API names only | No | N/A | Upstream dependency | No | No | Optional optimization objects plus independently implemented small binary QuadraticProgram exact enumeration; no parity or production optimizer claim | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/qiskit_algorithms/*` | Qiskit Algorithms inventory, passthrough scaffold, and educational native VQE/QAOA/Grover subset | Adapter Integration / Native Subset | API names only | No | N/A | Upstream dependency | No | No | Optional algorithms objects plus independently implemented small VQE, QAOA-compatible MaxCut, and Grover educational workflows; no parity or production algorithm claim | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/qiskit_nature/*` | Qiskit Nature inventory, passthrough scaffold, and educational native H2/LiH chemistry subset | Adapter Integration / Native Subset | API names only | No | N/A | Upstream dependency | No | No | Optional chemistry objects plus independently implemented small molecular problem metadata, qubit Hamiltonians, and exact diagonalization; no parity, production chemistry, or materials claim | N/A | Yes | Yes | Pending | High |
| `quantumbridge/ecosystem/catalog.py` | Clean-room ecosystem project catalog schema | Native Implementation | Public project names only | Public project names only | N/A | N/A | No | No | Manual catalog schema for compatibility targets; no website scraping or copied project-card text | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/qiskit_machine_learning/*` | Qiskit Machine Learning inventory, passthrough scaffold, and educational native QML subset | Adapter Integration / Native Subset | API names only | No | N/A | Upstream dependency | No | No | Optional ML objects plus independently implemented toy quantum kernel, kernel classifier, QNN forward, and QNN classifier; no production ML or high-risk decision claims | N/A | Yes | Yes | Stage 9E partial executable | High |
| `quantumbridge/compat/qiskit_experiments/*` | Qiskit Experiments inventory and passthrough scaffold | Adapter Integration | API names only | No | N/A | Upstream dependency | No | No | Optional experiments objects; no lab workflow guarantees | N/A | Yes | Inventory smoke | Pending | High |
| `quantumbridge/compat/qiskit_experiments/*_native.py` | Stage 9I educational offline Rabi/T1/Ramsey workflows | Clean-room implementation | Public concept names only | No | N/A | QuantumBridge native | No | No | Synthetic data and educational fitting only; no hardware calibration | N/A | Yes | Native tests and examples | Complete | Medium |
| `quantumbridge/compat/qiskit_dynamics/*_native.py` | Stage 9I educational offline one-qubit dynamics workflows | Clean-room implementation | Public concept names only | No | N/A | QuantumBridge native | No | No | Z precession, Rabi drive, dephasing metadata only; no production dynamics | N/A | Yes | Native tests and examples | Complete | Medium |
| `quantumbridge/compat/mqt/*` | Stage 9J MQT Core/DDSIM/QMAP clean-room compatibility slice | Clean-room implementation / optional upstream boundary | Public project and package names only | No | N/A | QuantumBridge native; upstream optional if installed separately | No | No | Core-like circuit dict/QASM, DDSIM-like simulation metadata, and QMAP-like routing; no full MQT, decision-diagram, optimal-mapper, or production parity claim | N/A | Yes | Native tests and examples | Complete | Medium |
| `quantumbridge/schema/mqt_results.py` | Stage 9J MQT compatibility result envelopes | Native Implementation | Public project names only | No | N/A | QuantumBridge native | No | No | QuantumBridge-owned schemas for native MQT Core-like, DDSIM-like, QMAP-like, upstream passthrough, routing, and comparison results | N/A | Yes | Yes | Complete | Low |
| `quantumbridge/compat/torchquantum/*` | Stage 9K TorchQuantum/PyTorch-style QML clean-room compatibility slice | Clean-room implementation / optional upstream boundary | Public project and package names only | No | N/A | QuantumBridge native; torch and TorchQuantum optional if installed separately | No | No | Tensor adapters, native educational quantum layer, batch forward, deterministic toy classifier training, optional torch tensor path, and optional TorchQuantum upstream boundary; no full TorchQuantum/PyTorch or production QML claim | N/A | Yes | Native tests and examples | Complete | Medium |
| `quantumbridge/schema/torchquantum_results.py` | Stage 9K TorchQuantum compatibility result envelopes | Native Implementation | Public project names only | No | N/A | QuantumBridge native | No | No | QuantumBridge-owned schemas for tensor, layer, batch, training, classifier, upstream passthrough, and comparison results | N/A | Yes | Yes | Complete | Low |
| `quantumbridge/compat/qos_uqci/*` | Stage 10A QOS-UQCI clean-room backend executable slice | Clean-room implementation / optional upstream boundary | Public project and package names only | No | N/A | QuantumBridge native; QOS-UQCI optional if installed separately | No | No | UQCI IR, job spec, DeviceSpec, CalSet, Manifest, OpenQASM artifact, offline mock runtime, and optional upstream boundary; no production runtime, cloud, token, hardware, or endorsement claim | N/A | Yes | Native tests and examples | Complete | Medium |
| `quantumbridge/compat/quafu/*` | Stage 10A Quafu / pyquafu clean-room backend executable slice | Clean-room implementation / optional upstream boundary | Public project and package names only | No | N/A | QuantumBridge native; pyquafu optional if installed separately | No | No | Quafu-compatible payload, job spec, offline mock backend, and optional pyquafu boundary; no full pyquafu replacement, production backend, cloud, token, hardware, or endorsement claim | N/A | Yes | Native tests and examples | Complete | Medium |
| `quantumbridge/schema/backend_results.py` | Stage 10A backend compatibility result envelopes | Native Implementation | Public project names only | No | N/A | QuantumBridge native | No | No | QuantumBridge-owned schemas for QOS-UQCI mock runtime, Quafu mock backend, and upstream passthrough results | N/A | Yes | Yes | Complete | Low |
| `quantumbridge/compat/benchpress/*` | Stage 10B Benchpress / benchmarking clean-room executable slice | Clean-room implementation / optional upstream boundary | Public project and package names only | No | N/A | QuantumBridge native; Benchpress optional if installed separately | No | No | Local benchmark registry, runner, suites, metrics, JSON / Markdown reports, and optional upstream boundary; no official benchmark or production performance ranking claim | N/A | Yes | Native tests and examples | Complete | Medium |
| `quantumbridge/schema/benchmark_results.py` | Stage 10B benchmark result envelopes | Native Implementation | Public project names only | No | N/A | QuantumBridge native | No | No | QuantumBridge-owned schemas for benchmark case, suite, comparison, and upstream passthrough results | N/A | Yes | Yes | Complete | Low |
| `quantumbridge/compat/qiskit_addons/*` | Qiskit Addons inventory and passthrough scaffold | Adapter Integration | API names only | No | N/A | Upstream dependency | No | No | Optional addons inventory; no source migration | N/A | Yes | Inventory smoke | Pending | High |
| `quantumbridge/compat/pennylane_full/*` | PennyLane full ecosystem inventory and passthrough scaffold | Adapter Integration | No | API names only | N/A | Apache-2.0 dependency | No | No | Optional PennyLane modules; no full plugin parity claim | N/A | Yes | Yes | Pending | High |
| `scripts/inventory_*_api.py` | Runtime public-name inventory generation | Native Implementation | Public package names only | Public package names only | N/A | N/A | No | No | Generates QuantumBridge JSON/Markdown matrices from runtime introspection | N/A | Yes | Yes | Pending | Medium |

## Source port summary

- Qiskit source files copied: 0.
- PennyLane source files copied: 0.
- Qiskit ecosystem source files copied during Stage 7: 0.
- PennyLane ecosystem source files copied during Stage 7: 0.
- Files requiring upstream copyright headers beyond notices: none in current P0.

## Stage 6.1 source-file coverage path index

The following paths are explicitly indexed for ledger completeness tests because
their headers or adapter text mention upstream projects while stating that no
upstream source was copied:

- `quantumbridge/__init__.py`
- `quantumbridge/providers/__init__.py`
- `quantumbridge/providers/backend.py`
- `quantumbridge/providers/exceptions.py`
- `quantumbridge/providers/job.py`
- `quantumbridge/providers/options.py`
- `quantumbridge/providers/provider.py`
- `quantumbridge/core/circuit.py`
- `quantumbridge/core/operations.py`
- `quantumbridge/algorithms/__init__.py`
- `quantumbridge/algorithms/adapters/__init__.py`
- `quantumbridge/algorithms/adapters/qiskit_algorithms_adapter.py`
- `quantumbridge/algorithms/amplitude.py`
- `quantumbridge/algorithms/eigensolvers.py`
- `quantumbridge/algorithms/gradients.py`
- `quantumbridge/algorithms/grover.py`
- `quantumbridge/algorithms/minimum_eigensolvers.py`
- `quantumbridge/algorithms/optimizers.py`
- `quantumbridge/chemistry/__init__.py`
- `quantumbridge/chemistry/adapters/__init__.py`
- `quantumbridge/chemistry/adapters/openfermion_adapter.py`
- `quantumbridge/chemistry/adapters/pyscf_adapter.py`
- `quantumbridge/chemistry/adapters/qiskit_nature_adapter.py`
- `quantumbridge/chemistry/ansatz.py`
- `quantumbridge/chemistry/drivers.py`
- `quantumbridge/chemistry/fermion.py`
- `quantumbridge/chemistry/integrals.py`
- `quantumbridge/chemistry/mappings.py`
- `quantumbridge/chemistry/molecule.py`
- `quantumbridge/chemistry/qubit_hamiltonian.py`
- `quantumbridge/chemistry/result.py`
- `quantumbridge/chemistry/second_quantized.py`
- `quantumbridge/chemistry/solvers.py`
- `quantumbridge/compat/__init__.py`
- `quantumbridge/compat/pennylane_adapter.py`
- `quantumbridge/compat/qiskit_adapter.py`
- `quantumbridge/compiler/config.py`
- `quantumbridge/compiler/transpile.py`
- `quantumbridge/compiler/report.py`
- `quantumbridge/legal/attribution.py`
- `quantumbridge/noise/execution.py`
- `quantumbridge/qasm/__init__.py`
- `quantumbridge/qasm/ast.py`
- `quantumbridge/qasm/errors.py`
- `quantumbridge/qasm/exporter.py`
- `quantumbridge/qasm/importer.py`
- `quantumbridge/qasm/lexer.py`
- `quantumbridge/qasm/parser.py`
- `quantumbridge/qasm/tokens.py`
- `quantumbridge/qasm/visitor.py`
- `quantumbridge/schema/__init__.py`
- `quantumbridge/schema/errors.py`
- `quantumbridge/schema/result_schema.py`
- `quantumbridge/schema/serialization.py`
- `quantumbridge/schema/validation.py`

## Stage 7 exact path registration

The following implementation files mention upstream package names for optional dependency, attribution, or adapter metadata purposes. Each file is independently implemented and copies no upstream source, tests, comments, errors, or documentation text.

- `quantumbridge/ecosystem/__init__.py`
- `quantumbridge/ecosystem/capability.py`
- `quantumbridge/ecosystem/dependency.py`
- `quantumbridge/ecosystem/provenance.py`
- `quantumbridge/ecosystem/registry.py`
- `quantumbridge/compat/qiskit_core/__init__.py`
- `quantumbridge/compat/qiskit_core/circuit_adapter.py`
- `quantumbridge/compat/qiskit_core/primitives_adapter.py`
- `quantumbridge/compat/qiskit_core/quantum_info_adapter.py`
- `quantumbridge/compat/qiskit_core/result_adapter.py`
- `quantumbridge/compat/qiskit_core/transpiler_adapter.py`
- `quantumbridge/compat/qiskit_aer/__init__.py`
- `quantumbridge/compat/qiskit_aer/aer_adapter.py`
- `quantumbridge/compat/qiskit_aer/aer_upstream_adapter.py`
- `quantumbridge/compat/qiskit_aer/circuit_execution_adapter.py`
- `quantumbridge/compat/qiskit_aer/examples.py`
- `quantumbridge/compat/qiskit_aer/noise_adapter.py`
- `quantumbridge/compat/qiskit_aer/qasm_simulator_adapter.py`
- `quantumbridge/compat/qiskit_aer/simulator_native.py`
- `quantumbridge/compat/qiskit_aer/statevector_simulator_adapter.py`
- `quantumbridge/compat/qiskit_aer/warnings.py`
- `quantumbridge/compat/qiskit_runtime/__init__.py`
- `quantumbridge/compat/qiskit_runtime/backend_adapter.py`
- `quantumbridge/compat/qiskit_runtime/job_adapter.py`
- `quantumbridge/compat/qiskit_runtime/runtime_adapter.py`
- `quantumbridge/compat/qiskit_finance/__init__.py`
- `quantumbridge/compat/qiskit_finance/applications_adapter.py`
- `quantumbridge/compat/qiskit_finance/circuits_adapter.py`
- `quantumbridge/compat/qiskit_finance/data_provider_adapter.py`
- `quantumbridge/compat/qiskit_finance/portfolio_examples.py`
- `quantumbridge/compat/qiskit_finance/portfolio_native.py`
- `quantumbridge/compat/qiskit_finance/portfolio_optimization_adapter.py`
- `quantumbridge/compat/qiskit_finance/portfolio_result.py`
- `quantumbridge/compat/qiskit_finance/uncertainty_adapter.py`
- `quantumbridge/compat/qiskit_optimization/__init__.py`
- `quantumbridge/compat/qiskit_optimization/converter_adapter.py`
- `quantumbridge/compat/qiskit_optimization/converters_adapter.py`
- `quantumbridge/compat/qiskit_optimization/minimum_eigen_optimizer_adapter.py`
- `quantumbridge/compat/qiskit_optimization/optimizer_adapter.py`
- `quantumbridge/compat/qiskit_optimization/quadratic_program_adapter.py`
- `quantumbridge/compat/qiskit_optimization/quadratic_program_native.py`
- `quantumbridge/compat/qiskit_optimization/quadratic_program_result.py`
- `quantumbridge/compat/qiskit_optimization/warnings.py`
- `quantumbridge/compat/qiskit_machine_learning/__init__.py`
- `quantumbridge/compat/qiskit_machine_learning/classifier_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/kernel_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/qnn_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/torch_connector_adapter.py`
- `quantumbridge/compat/qiskit_experiments/__init__.py`
- `quantumbridge/compat/qiskit_experiments/calibration_adapter.py`
- `quantumbridge/compat/qiskit_experiments/experiments_adapter.py`
- `quantumbridge/compat/qiskit_experiments/tomography_adapter.py`
- `quantumbridge/compat/qiskit_addons/__init__.py`
- `quantumbridge/compat/qiskit_addons/aqc_adapter.py`
- `quantumbridge/compat/qiskit_addons/mpf_adapter.py`
- `quantumbridge/compat/qiskit_addons/obp_adapter.py`
- `quantumbridge/compat/qiskit_addons/sqd_adapter.py`
- `quantumbridge/compat/pennylane_full/__init__.py`
- `quantumbridge/compat/pennylane_full/device_adapter.py`
- `quantumbridge/compat/pennylane_full/gradients_adapter.py`
- `quantumbridge/compat/pennylane_full/measurement_adapter.py`
- `quantumbridge/compat/pennylane_full/operations_adapter.py`
- `quantumbridge/compat/pennylane_full/plugin_adapter.py`
- `quantumbridge/compat/pennylane_full/qchem_adapter.py`
- `quantumbridge/compat/pennylane_full/qnode_adapter.py`
- `quantumbridge/compat/pennylane_full/resource_adapter.py`
- `quantumbridge/compat/pennylane_full/templates_adapter.py`
- `quantumbridge/compat/pennylane_full/transforms_adapter.py`

## Stage 7.2 exact path registration

The following files are independently implemented adapter/schema modules. They reference upstream package names or public object names only. No upstream source, tests, documentation, comments, or error strings were copied.

- `quantumbridge/schema/__init__.py`
- `quantumbridge/schema/ecosystem_results.py`
- `quantumbridge/compat/qiskit_nature/__init__.py`
- `quantumbridge/compat/qiskit_nature/nature_adapter.py`
- `quantumbridge/compat/qiskit_nature/driver_adapter.py`
- `quantumbridge/compat/qiskit_nature/problem_adapter.py`
- `quantumbridge/compat/qiskit_nature/openfermion_adapter.py`
- `quantumbridge/compat/qiskit_nature/result_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/__init__.py`
- `quantumbridge/compat/qiskit_algorithms/eigensolver_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/algorithms_native.py`
- `quantumbridge/compat/qiskit_algorithms/examples.py`
- `quantumbridge/compat/qiskit_algorithms/grover_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/minimum_eigensolver_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/optimizer_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/qaoa_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/result_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/vqe_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/warnings.py`
- `quantumbridge/compat/qiskit_algorithms/amplitude_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/grover_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/optimizer_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/gradient_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/result_adapter.py`
- `quantumbridge/compat/qiskit_dynamics/__init__.py`
- `quantumbridge/compat/qiskit_dynamics/solver_adapter.py`
- `quantumbridge/compat/qiskit_dynamics/model_adapter.py`
- `quantumbridge/compat/qiskit_dynamics/signal_adapter.py`
- `quantumbridge/compat/qiskit_dynamics/backend_adapter.py`
- `quantumbridge/compat/qiskit_dynamics/result_adapter.py`
- `quantumbridge/compat/qiskit_metal/__init__.py`
- `quantumbridge/compat/qiskit_metal/design_adapter.py`
- `quantumbridge/compat/qiskit_metal/component_adapter.py`
- `quantumbridge/compat/qiskit_metal/renderer_adapter.py`
- `quantumbridge/compat/qiskit_metal/simulation_adapter.py`
- `quantumbridge/compat/qiskit_metal/result_adapter.py`
- `quantumbridge/compat/qiskit_finance/result_adapter.py`
- `quantumbridge/compat/qiskit_optimization/applications_adapter.py`
- `quantumbridge/compat/qiskit_optimization/result_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/regressor_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/dataset_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/result_adapter.py`
- `quantumbridge/compat/qiskit_experiments/rb_adapter.py`
- `quantumbridge/schema/optimization_results.py`
- `quantumbridge/compat/qiskit_experiments/result_adapter.py`
- `quantumbridge/compat/qiskit_aer/result_adapter.py`
- `quantumbridge/schema/aer_results.py`
- `quantumbridge/compat/qiskit_runtime/result_adapter.py`
- `quantumbridge/compat/qiskit_addons/result_adapter.py`
- `quantumbridge/compat/pennylane_full/result_adapter.py`

Stage 7.2 source port count remains zero.

## Stage 11A quantum_info native parity path registration

The following files are independently implemented QuantumBridge native
linear-algebra and operator modules. They use public compatibility names such
as Qiskit `quantum_info` only as API targets. No upstream source, tests,
documentation prose, comments, or error strings were copied.

- `quantumbridge/information/operator.py`
- `quantumbridge/information/channels.py`
- `quantumbridge/information/clifford.py`
- `quantumbridge/information/metrics.py`
- `quantumbridge/information/random.py`
- `quantumbridge/operators/pauli_list.py`
- `quantumbridge/compat/qiskit_core/quantum_info_adapter.py`
- `tests/compat_qiskit_core/test_quantum_info_native.py`

Stage 11A source port count remains zero.

## Stage 8A exact path registration

The following Stage 8A contract file mentions upstream package names only to
define independent QuantumBridge adapter metadata, provenance, and warnings.
No upstream source, tests, documentation prose, comments, or error strings were
copied.

- `quantumbridge/compat/contracts.py`

Stage 8A source port count remains zero.

## Stage 8B exact path registration

The following Stage 8B PennyLane full API inventory, adapter, bridge, and schema
files mention upstream package names only for optional dependency discovery,
public API introspection, provenance, warnings, schema metadata, or conversion
scaffold labels. They are independently implemented and copy no upstream
source, tests, documentation prose, comments, or error strings.

- `quantumbridge/compat/pennylane_full/data_adapter.py`
- `quantumbridge/compat/pennylane_full/dependency.py`
- `quantumbridge/compat/pennylane_full/interface_adapter.py`
- `quantumbridge/compat/pennylane_full/inventory.py`
- `quantumbridge/compat/pennylane_full/io_adapter.py`
- `quantumbridge/compat/pennylane_full/kernels_adapter.py`
- `quantumbridge/compat/pennylane_full/math_adapter.py`
- `quantumbridge/compat/pennylane_full/measurements_adapter.py`
- `quantumbridge/compat/pennylane_full/observables_adapter.py`
- `quantumbridge/compat/pennylane_full/operations_adapter.py`
- `quantumbridge/compat/pennylane_full/passthrough.py`
- `quantumbridge/compat/pennylane_full/qaoa_adapter.py`
- `quantumbridge/compat/pennylane_full/qcut_adapter.py`
- `quantumbridge/compat/pennylane_full/qiskit_bridge.py`
- `quantumbridge/compat/pennylane_full/qnn_adapter.py`
- `quantumbridge/compat/pennylane_full/qnode_adapter.py`
- `quantumbridge/compat/pennylane_full/qos_uqci_bridge.py`
- `quantumbridge/compat/pennylane_full/registry.py`
- `quantumbridge/compat/pennylane_full/result_adapter.py`
- `quantumbridge/compat/pennylane_full/shadows_adapter.py`
- `quantumbridge/compat/pennylane_full/tape_adapter.py`
- `quantumbridge/compat/pennylane_full/warnings.py`
- `quantumbridge/schema/pennylane_results.py`

Stage 8B source port count remains zero.

## Stage 8D exact path registration

The following Stage 8D Qiskit ecosystem adapter contract, schema, inventory,
and test files mention upstream package names only for optional dependency
discovery, runtime public API introspection, passthrough metadata, provenance,
warnings, schema metadata, or unsupported/advisory labels. They are
independently implemented and copy no upstream source, tests, documentation
prose, comments, or error strings.

- `quantumbridge/compat/qiskit_common.py`
- `quantumbridge/compat/qiskit_contract_helpers.py`
- `quantumbridge/compat/qiskit_adapter.py`
- `quantumbridge/compat/qiskit_core/__init__.py`
- `quantumbridge/compat/qiskit_core/circuit_adapter.py`
- `quantumbridge/compat/qiskit_aer/__init__.py`
- `quantumbridge/compat/qiskit_nature/__init__.py`
- `quantumbridge/compat/qiskit_algorithms/__init__.py`
- `quantumbridge/compat/qiskit_finance/__init__.py`
- `quantumbridge/compat/qiskit_optimization/__init__.py`
- `quantumbridge/compat/qiskit_machine_learning/__init__.py`
- `quantumbridge/compat/qiskit_dynamics/__init__.py`
- `quantumbridge/compat/qiskit_experiments/__init__.py`
- `quantumbridge/compat/qiskit_metal/__init__.py`
- `quantumbridge/compat/qiskit_runtime/__init__.py`
- `quantumbridge/compat/qiskit_addons/__init__.py`
- `quantumbridge/schema/qiskit_results.py`
- `scripts/qiskit_inventory_common.py`
- `scripts/inventory_qiskit_core_api.py`
- `scripts/inventory_qiskit_aer_api.py`
- `scripts/inventory_qiskit_nature_api.py`
- `scripts/inventory_qiskit_algorithms_api.py`
- `scripts/inventory_qiskit_finance_api.py`
- `scripts/inventory_qiskit_optimization_api.py`
- `scripts/inventory_qiskit_machine_learning_api.py`
- `scripts/inventory_qiskit_dynamics_api.py`
- `scripts/inventory_qiskit_experiments_api.py`
- `scripts/inventory_qiskit_metal_api.py`
- `scripts/inventory_qiskit_ibm_runtime_api.py`
- `scripts/inventory_qiskit_addons_api.py`
- `tests/compat_qiskit_core/test_qiskit_core_contract.py`
- `tests/compat_qiskit_aer/test_qiskit_aer_contract.py`
- `tests/compat_qiskit_nature/test_qiskit_nature_contract.py`
- `tests/compat_qiskit_algorithms/test_qiskit_algorithms_contract.py`
- `tests/compat_qiskit_finance/test_qiskit_finance_contract.py`
- `tests/compat_qiskit_optimization/test_qiskit_optimization_contract.py`
- `tests/compat_qiskit_machine_learning/test_qiskit_ml_contract.py`
- `tests/compat_qiskit_dynamics/test_qiskit_dynamics_contract.py`
- `tests/compat_qiskit_experiments/test_qiskit_experiments_contract.py`
- `tests/compat_qiskit_metal/test_qiskit_metal_advisory_contract.py`
- `tests/compat_qiskit_runtime/test_qiskit_runtime_offline_contract.py`
- `tests/compat_qiskit_addons/test_qiskit_addons_contract.py`
- `tests/ecosystem/test_qiskit_ecosystem_contract_coverage.py`
- `tests/ecosystem/test_qiskit_result_schema.py`
- `tests/ecosystem/test_qiskit_no_vendor_no_token.py`

Stage 8D generated inventory JSON and coverage matrix Markdown files under
`docs/compat/inventory/` and `docs/compat/matrix/` contain public API names,
capability metadata, warnings, risk labels, and provenance notes only. They do
not contain upstream implementation source or vendored dependency artifacts.

Stage 8D source port count remains zero.

## Stage 9D exact path registration

The following Stage 9D Qiskit Nature chemistry files mention upstream package
names only for optional dependency discovery, provenance, warnings, schema
metadata, or passthrough comparison labels. They are independently implemented
and copy no upstream source, tests, documentation prose, examples, comments,
error strings, wheels, dist-info, egg-info, site-packages trees, or virtual
environments.

- `quantumbridge/compat/qiskit_nature/chemistry_native.py`
- `quantumbridge/compat/qiskit_nature/__init__.py`
- `quantumbridge/compat/qiskit_nature/result_adapter.py`
- `quantumbridge/schema/chemistry_results.py`
- `quantumbridge/schema/__init__.py`
- `examples/qiskit_nature_h2_quantumbridge.py`
- `examples/qiskit_nature_lih_quantumbridge.py`
- `tests/compat_qiskit_nature/test_h2_native_workflow.py`
- `tests/compat_qiskit_nature/test_lih_native_workflow.py`
- `tests/compat_qiskit_nature/test_qubit_hamiltonian_exact_solver.py`
- `tests/compat_qiskit_nature/test_chemistry_result_schema.py`
- `tests/compat_qiskit_nature/test_h2_upstream_passthrough.py`
- `tests/compat_qiskit_nature/test_lih_upstream_passthrough.py`
- `tests/compat_qiskit_nature/test_chemistry_no_cloud_no_token.py`
- `tests/compat_qiskit_nature/test_chemistry_warnings_provenance.py`
- `tests/compat_qiskit_nature/test_chemistry_examples.py`

Stage 9D source port count remains zero.

## Stage 9E exact path registration

The following Stage 9E files mention Qiskit Machine Learning, IBM Quantum
Ecosystem, or ecosystem project names only for optional dependency,
compatibility target, clean-room catalog, provenance, warning, test, or
documentation purposes. They are independently implemented and copy no upstream
source, tests, documentation prose, website text, UI, screenshots, icons, logos,
error strings, wheels, dist-info, egg-info, site-packages trees, or virtual
environments.

- `quantumbridge/compat/qiskit_machine_learning/qml_dataset_native.py`
- `quantumbridge/compat/qiskit_machine_learning/feature_map_native.py`
- `quantumbridge/compat/qiskit_machine_learning/quantum_kernel_native.py`
- `quantumbridge/compat/qiskit_machine_learning/kernel_classifier_native.py`
- `quantumbridge/compat/qiskit_machine_learning/qnn_native.py`
- `quantumbridge/compat/qiskit_machine_learning/qnn_classifier_native.py`
- `quantumbridge/compat/qiskit_machine_learning/upstream_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/examples.py`
- `quantumbridge/compat/qiskit_machine_learning/warnings.py`
- `quantumbridge/schema/ml_results.py`
- `examples/qiskit_ml_quantum_kernel_quantumbridge.py`
- `examples/qiskit_ml_kernel_classifier_quantumbridge.py`
- `examples/qiskit_ml_qnn_classifier_quantumbridge.py`
- `tests/compat_qiskit_machine_learning/test_qml_dataset_native.py`
- `tests/compat_qiskit_machine_learning/test_quantum_feature_map_native.py`
- `tests/compat_qiskit_machine_learning/test_quantum_kernel_native.py`
- `tests/compat_qiskit_machine_learning/test_kernel_classifier_native.py`
- `tests/compat_qiskit_machine_learning/test_qnn_forward_native.py`
- `tests/compat_qiskit_machine_learning/test_qnn_classifier_native.py`
- `tests/compat_qiskit_machine_learning/test_ml_result_schema.py`
- `tests/compat_qiskit_machine_learning/test_ml_upstream_passthrough.py`
- `tests/compat_qiskit_machine_learning/test_ml_no_cloud_no_token.py`
- `tests/compat_qiskit_machine_learning/test_ml_warnings_provenance.py`
- `tests/compat_qiskit_machine_learning/test_ml_examples.py`

Stage 9E source port count remains zero.

## Stage 9C exact path registration

The following Stage 9C files mention Qiskit Algorithms, IBM Quantum Ecosystem,
or ecosystem project names only for optional dependency, compatibility target,
clean-room catalog, provenance, warning, test, or documentation purposes. They
are independently implemented and copy no upstream source, tests,
documentation prose, website text, UI, screenshots, icons, logos, error
strings, wheels, dist-info, egg-info, site-packages trees, or virtual
environments.

- `quantumbridge/compat/qiskit_algorithms/algorithms_native.py`
- `quantumbridge/compat/qiskit_algorithms/vqe_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/qaoa_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/grover_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/examples.py`
- `quantumbridge/compat/qiskit_algorithms/eigensolver_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/optimizer_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/result_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/warnings.py`
- `quantumbridge/schema/algorithms_results.py`
- `quantumbridge/ecosystem/catalog.py`
- `examples/qiskit_algorithms_vqe_quantumbridge.py`
- `examples/qiskit_algorithms_qaoa_quantumbridge.py`
- `examples/qiskit_algorithms_grover_quantumbridge.py`
- `tests/compat_qiskit_algorithms/test_vqe_native.py`
- `tests/compat_qiskit_algorithms/test_qaoa_native.py`
- `tests/compat_qiskit_algorithms/test_grover_native.py`
- `tests/compat_qiskit_algorithms/test_algorithms_result_schema.py`
- `tests/compat_qiskit_algorithms/test_vqe_upstream_passthrough.py`
- `tests/compat_qiskit_algorithms/test_qaoa_upstream_passthrough.py`
- `tests/compat_qiskit_algorithms/test_grover_upstream_passthrough.py`
- `tests/compat_qiskit_algorithms/test_algorithms_no_cloud_no_token.py`
- `tests/compat_qiskit_algorithms/test_algorithms_warnings_provenance.py`
- `tests/compat_qiskit_algorithms/test_algorithms_examples.py`
- `tests/ecosystem/test_ecosystem_catalog_schema.py`
- `docs/implementation/stage9c_qiskit_algorithms_executable_adapter_report.md`
- `docs/tutorials/qiskit_algorithms_vqe_quantumbridge.md`
- `docs/tutorials/qiskit_algorithms_qaoa_quantumbridge.md`
- `docs/tutorials/qiskit_algorithms_grover_quantumbridge.md`
- `docs/roadmap/ibm_quantum_ecosystem_clean_room_parity_master_plan.md`
- `docs/compat/ecosystem/ibm_quantum_ecosystem_project_catalog_schema.md`
- `docs/compat/ecosystem/ibm_quantum_ecosystem_project_catalog_seed.md`
- `docs/legal/ibm_quantum_ecosystem_clean_room_boundary.md`

Stage 9C source port count remains zero.

## Stage 9G source-file coverage path index

The following Stage 9G files are explicitly indexed for ledger completeness
tests because their clean-room comments or adapter text mention upstream
projects while stating that no upstream source was copied:

- `quantumbridge/compat/mitiq/__init__.py`
- `quantumbridge/compat/mitiq/executor_adapter.py`
- `quantumbridge/compat/mitiq/examples.py`
- `quantumbridge/compat/mitiq/readout_mitigation_native.py`
- `quantumbridge/compat/mitiq/warnings.py`
- `quantumbridge/compat/mitiq/zne_native.py`

Stage 9G source port count remains zero.

## Stage 9H source-file coverage path index

The following Stage 9H files are explicitly indexed for ledger completeness
tests because their clean-room comments or adapter text mention upstream
projects while stating that no upstream source was copied:

- `quantumbridge/compat/pennylane_qiskit/__init__.py`
- `quantumbridge/compat/pennylane_qiskit/bridge_native.py`
- `quantumbridge/compat/pennylane_qiskit/dependency.py`
- `quantumbridge/compat/pennylane_qiskit/examples.py`
- `quantumbridge/compat/pennylane_qiskit/upstream_adapter.py`
- `quantumbridge/compat/pennylane_qiskit/warnings.py`
- `quantumbridge/schema/pennylane_qiskit_bridge_results.py`
- `examples/pennylane_qiskit_qiskit_to_pennylane_quantumbridge.py`
- `examples/pennylane_qiskit_pennylane_to_qiskit_quantumbridge.py`
- `examples/pennylane_qiskit_bridge_equivalence_quantumbridge.py`

Stage 9H source port count remains zero.

## Stage 9I Source Inventory

The following Stage 9I files are clean-room QuantumBridge implementations or
optional dependency boundaries; no upstream source, prose, wheels, dist-info,
egg-info, site-packages trees, or virtual environments were copied:

- `quantumbridge/compat/qiskit_experiments/dependency.py`
- `quantumbridge/compat/qiskit_experiments/warnings.py`
- `quantumbridge/compat/qiskit_experiments/calibration_fit_native.py`
- `quantumbridge/compat/qiskit_experiments/experiment_data_native.py`
- `quantumbridge/compat/qiskit_experiments/rabi_experiment_native.py`
- `quantumbridge/compat/qiskit_experiments/t1_experiment_native.py`
- `quantumbridge/compat/qiskit_experiments/ramsey_experiment_native.py`
- `quantumbridge/compat/qiskit_experiments/experiments_upstream_adapter.py`
- `quantumbridge/compat/qiskit_experiments/examples.py`
- `quantumbridge/compat/qiskit_dynamics/dependency.py`
- `quantumbridge/compat/qiskit_dynamics/warnings.py`
- `quantumbridge/compat/qiskit_dynamics/hamiltonian_model_native.py`
- `quantumbridge/compat/qiskit_dynamics/time_evolution_native.py`
- `quantumbridge/compat/qiskit_dynamics/single_qubit_dynamics_native.py`
- `quantumbridge/compat/qiskit_dynamics/dynamics_upstream_adapter.py`
- `quantumbridge/compat/qiskit_dynamics/examples.py`
- `quantumbridge/schema/experiments_results.py`
- `quantumbridge/schema/dynamics_results.py`

Stage 9I source port count remains zero.

## Stage 9J Source Inventory

The following Stage 9J files are clean-room QuantumBridge implementations or
optional dependency boundaries; no upstream source, prose, wheels, dist-info,
egg-info, site-packages trees, or virtual environments were copied:

- `quantumbridge/compat/mqt/__init__.py`
- `quantumbridge/compat/mqt/dependency.py`
- `quantumbridge/compat/mqt/core_adapter.py`
- `quantumbridge/compat/mqt/ddsim_adapter.py`
- `quantumbridge/compat/mqt/qmap_adapter.py`
- `quantumbridge/compat/mqt/routing_native.py`
- `quantumbridge/compat/mqt/mapping_native.py`
- `quantumbridge/compat/mqt/decision_diagram_metadata.py`
- `quantumbridge/compat/mqt/upstream_adapter.py`
- `quantumbridge/compat/mqt/result_adapter.py`
- `quantumbridge/compat/mqt/warnings.py`
- `quantumbridge/compat/mqt/examples.py`
- `quantumbridge/schema/mqt_results.py`
- `examples/mqt_core_like_circuit_quantumbridge.py`
- `examples/mqt_ddsim_like_simulation_quantumbridge.py`
- `examples/mqt_qmap_like_routing_quantumbridge.py`

Stage 9J source port count remains zero.

## Stage 9K Source Inventory

The following Stage 9K files are clean-room QuantumBridge implementations or
optional dependency boundaries; no upstream source, prose, model weights,
wheels, dist-info, egg-info, site-packages trees, or virtual environments were
copied:

- `quantumbridge/compat/torchquantum/__init__.py`
- `quantumbridge/compat/torchquantum/dependency.py`
- `quantumbridge/compat/torchquantum/tensor_adapter.py`
- `quantumbridge/compat/torchquantum/qml_dataset_native.py`
- `quantumbridge/compat/torchquantum/quantum_layer_native.py`
- `quantumbridge/compat/torchquantum/training_native.py`
- `quantumbridge/compat/torchquantum/torch_adapter.py`
- `quantumbridge/compat/torchquantum/upstream_adapter.py`
- `quantumbridge/compat/torchquantum/result_adapter.py`
- `quantumbridge/compat/torchquantum/warnings.py`
- `quantumbridge/compat/torchquantum/examples.py`
- `quantumbridge/schema/torchquantum_results.py`
- `examples/torchquantum_like_layer_quantumbridge.py`
- `examples/torchquantum_like_batch_forward_quantumbridge.py`
- `examples/torchquantum_like_classifier_quantumbridge.py`

Stage 9K source port count remains zero.

## Stage 10A Source Inventory

The following Stage 10A files are clean-room QuantumBridge implementations or
optional dependency boundaries; no QOS-UQCI, Quafu, pyquafu, IBM, Qiskit,
PennyLane, MQT, Mitiq, TorchQuantum, PyTorch, wheels, dist-info, egg-info,
site-packages trees, or virtual environments were copied:

- `quantumbridge/compat/qos_uqci/__init__.py`
- `quantumbridge/compat/qos_uqci/dependency.py`
- `quantumbridge/compat/qos_uqci/uqci_ir_adapter.py`
- `quantumbridge/compat/qos_uqci/job_spec.py`
- `quantumbridge/compat/qos_uqci/devicespec_adapter.py`
- `quantumbridge/compat/qos_uqci/calset_adapter.py`
- `quantumbridge/compat/qos_uqci/manifest_adapter.py`
- `quantumbridge/compat/qos_uqci/openqasm_bridge.py`
- `quantumbridge/compat/qos_uqci/mock_runtime.py`
- `quantumbridge/compat/qos_uqci/upstream_adapter.py`
- `quantumbridge/compat/qos_uqci/result_adapter.py`
- `quantumbridge/compat/qos_uqci/warnings.py`
- `quantumbridge/compat/qos_uqci/examples.py`
- `quantumbridge/compat/quafu/__init__.py`
- `quantumbridge/compat/quafu/dependency.py`
- `quantumbridge/compat/quafu/payload_adapter.py`
- `quantumbridge/compat/quafu/job_adapter.py`
- `quantumbridge/compat/quafu/mock_backend.py`
- `quantumbridge/compat/quafu/upstream_adapter.py`
- `quantumbridge/compat/quafu/result_adapter.py`
- `quantumbridge/compat/quafu/warnings.py`
- `quantumbridge/compat/quafu/examples.py`
- `quantumbridge/schema/backend_results.py`
- `examples/qos_uqci_bell_job_quantumbridge.py`
- `examples/qos_uqci_mock_runtime_quantumbridge.py`
- `examples/quafu_bell_payload_quantumbridge.py`
- `examples/quafu_mock_backend_quantumbridge.py`

Stage 10A source port count remains zero.

## Stage 10B Source Inventory

The following Stage 10B files are clean-room QuantumBridge implementations or
optional dependency boundaries; no IBM, Qiskit, Benchpress, QOS-UQCI, Quafu,
pyquafu, PennyLane, MQT, Mitiq, TorchQuantum, PyTorch, wheels, dist-info,
egg-info, site-packages, or virtual environments are vendored:

- `quantumbridge/compat/benchpress/__init__.py`
- `quantumbridge/compat/benchpress/benchmark_case.py`
- `quantumbridge/compat/benchpress/benchmark_registry.py`
- `quantumbridge/compat/benchpress/benchmark_runner.py`
- `quantumbridge/compat/benchpress/benchmark_suites.py`
- `quantumbridge/compat/benchpress/dependency.py`
- `quantumbridge/compat/benchpress/examples.py`
- `quantumbridge/compat/benchpress/metrics.py`
- `quantumbridge/compat/benchpress/reporting.py`
- `quantumbridge/compat/benchpress/result_adapter.py`
- `quantumbridge/compat/benchpress/upstream_adapter.py`
- `quantumbridge/compat/benchpress/warnings.py`
- `quantumbridge/schema/benchmark_results.py`
- `examples/benchpress_*_quantumbridge.py`
- `tests/compat_benchpress/*`
- `docs/compat/benchpress_benchmarking_strategy.md`
- `docs/implementation/stage10b_benchpress_benchmarking_executable_slice_report.md`
- `docs/tutorials/benchpress_*_quantumbridge.md`

Stage 10B source port count remains zero.

## Stage 10C Source Inventory

The following Stage 10C files are clean-room QuantumBridge implementations or
local backend API documentation; no IBM, Qiskit, PennyLane, Benchpress,
QOS-UQCI, Quafu, MQT, Mitiq, TorchQuantum, PyTorch, FastAPI, wheels,
dist-info, egg-info, site-packages, or virtual environments are vendored:

- `quantumbridge/studio/__init__.py`
- `quantumbridge/studio/api_models.py`
- `quantumbridge/studio/catalog_service.py`
- `quantumbridge/studio/workflow_registry.py`
- `quantumbridge/studio/workflow_inputs.py`
- `quantumbridge/studio/execution_service.py`
- `quantumbridge/studio/result_store.py`
- `quantumbridge/studio/export_service.py`
- `quantumbridge/studio/benchmark_service.py`
- `quantumbridge/studio/provenance_service.py`
- `quantumbridge/studio/warning_service.py`
- `quantumbridge/studio/local_router.py`
- `quantumbridge/studio/fastapi_adapter.py`
- `quantumbridge/studio/warnings.py`
- `quantumbridge/studio/examples.py`
- `examples/studio_catalog_api_quantumbridge.py`
- `examples/studio_workflow_execution_quantumbridge.py`
- `examples/studio_benchmark_api_quantumbridge.py`
- `examples/studio_export_api_quantumbridge.py`
- `tests/studio/*`
- `docs/studio/*`
- `docs/implementation/stage10c_quantumbridge_studio_backend_api_slice_report.md`
- `docs/tutorials/studio_*_quantumbridge.md`

Stage 10C source port count remains zero.

## Stage 10D Source Inventory

The following Stage 10D files are clean-room QuantumBridge implementations,
generated local seed data from QuantumBridge-owned APIs, or local frontend
prototype documentation. No IBM, Qiskit, PennyLane, Benchpress, QOS-UQCI,
Quafu, MQT, Mitiq, TorchQuantum, PyTorch, React, Vite, Carbon, wheels,
dist-info, egg-info, site-packages, `node_modules`, build outputs, copied UI,
copied prose, logos, or virtual environments are vendored:

- `examples/studio_generate_frontend_seed_data_quantumbridge.py`
- `studio/package.json`
- `studio/index.html`
- `studio/src/main.js`
- `studio/src/App.js`
- `studio/src/api/studioClient.js`
- `studio/src/api/mockStudioClient.js`
- `studio/src/api/localJsonClient.js`
- `studio/src/components/Badge.js`
- `studio/src/components/Card.js`
- `studio/src/components/ExportPanel.js`
- `studio/src/components/Header.js`
- `studio/src/components/JsonViewer.js`
- `studio/src/components/Layout.js`
- `studio/src/components/ProvenancePanel.js`
- `studio/src/components/ResultPanel.js`
- `studio/src/components/Sidebar.js`
- `studio/src/components/WarningPanel.js`
- `studio/src/pages/BenchmarksPage.js`
- `studio/src/pages/CatalogPage.js`
- `studio/src/pages/ExecutePage.js`
- `studio/src/pages/ExportsPage.js`
- `studio/src/pages/ResultsPage.js`
- `studio/src/pages/WorkflowDetailPage.js`
- `studio/src/pages/WorkflowsPage.js`
- `studio/src/styles/globals.css`
- `studio/scripts/smoke-check.mjs`
- `studio/src/data/sampleCatalog.json`
- `studio/src/data/sampleWorkflows.json`
- `studio/src/data/sampleResults.json`
- `studio/src/data/sampleBenchmarkReport.json`
- `studio/src/data/seedData.js`
- `docs/implementation/stage10d_quantumbridge_studio_frontend_prototype_report.md`
- `docs/studio/frontend_prototype_v0.1.md`
- `docs/studio/frontend_local_data_contract_v0.1.md`
- `docs/studio/frontend_security_boundary_v0.1.md`
- `docs/tutorials/studio_frontend_local_prototype_quantumbridge.md`

Stage 10D source port count remains zero.

## Stage 10E Source Inventory

The following Stage 10E files are clean-room QuantumBridge implementations,
generated local seed data from QuantumBridge-owned APIs, or local integration
hardening documentation. No IBM, Qiskit, PennyLane, Benchpress, QOS-UQCI,
Quafu, MQT, Mitiq, TorchQuantum, PyTorch, React, Vite, Carbon, wheels,
dist-info, egg-info, site-packages, `node_modules`, build outputs, copied UI,
copied prose, logos, or virtual environments are vendored:

- `quantumbridge/studio/frontend_contract.py`
- `quantumbridge/studio/__main__.py`
- `quantumbridge/studio/export_service.py`
- `examples/studio_generate_frontend_seed_data_quantumbridge.py`
- `studio/src/api/studioClient.js`
- `studio/src/api/mockStudioClient.js`
- `studio/src/api/localJsonClient.js`
- `studio/src/pages/BenchmarksPage.js`
- `studio/src/pages/CatalogPage.js`
- `studio/src/pages/ExecutePage.js`
- `studio/src/pages/ExportsPage.js`
- `studio/src/pages/ResultsPage.js`
- `studio/src/pages/WorkflowDetailPage.js`
- `studio/src/pages/WorkflowsPage.js`
- `studio/src/styles/globals.css`
- `studio/scripts/smoke-check.mjs`
- `studio/src/data/sampleCatalog.json`
- `studio/src/data/sampleWorkflows.json`
- `studio/src/data/sampleWorkflowDetails.json`
- `studio/src/data/sampleResults.json`
- `studio/src/data/sampleBenchmarkReport.json`
- `studio/src/data/sampleExports.json`
- `studio/src/data/studioSchemaVersion.json`
- `studio/src/data/seedData.js`
- `tests/studio/test_backend_frontend_contract_coverage.py`
- `tests/studio/test_frontend_seed_contract.py`
- `tests/studio/test_frontend_seed_no_branding_no_secrets.py`
- `tests/studio/test_studio_cli.py`
- `docs/implementation/stage10e_studio_backend_frontend_integration_hardening_report.md`
- `docs/studio/backend_frontend_contract_v0.1.md`
- `docs/studio/studio_cli_contract_v0.1.md`
- `docs/tutorials/studio_generate_seed_and_execute_workflow_quantumbridge.md`

Stage 10E source port count remains zero.

## Stage 10F Source Inventory

The following Stage 10F files are clean-room QuantumBridge implementations
for native PennyLane-like QML measurement execution. No PennyLane source,
Qiskit source, examples, tutorials, wheels, dist-info, egg-info, site-packages,
or virtual environments are vendored:

- `quantumbridge/qml/measurements.py`
- `quantumbridge/qml/qnode.py`
- `quantumbridge/qml/tape.py`
- `quantumbridge/qml/__init__.py`
- `tests/qml/test_pennylane_measurement_coverage_p2.py`

Stage 10F source port count remains zero.

## Stage 10G Source Inventory

The following Stage 10G files are clean-room QuantumBridge implementations,
architecture records, or tests for the optional QuarkStudio public API. No
Quafu, QuarkStudio, pyquafu, Qiskit, PennyLane, Cirq, OpenFermion, wheels,
dist-info, egg-info, site-packages, credentials, tokens, or virtual
environments are copied or vendored:

- `quantumbridge/ecosystem/industry_taxonomy.py`
- `quantumbridge/ecosystem/__init__.py`
- `quantumbridge/compat/quafu/cloud_backend.py`
- `quantumbridge/compat/quafu/dependency.py`
- `quantumbridge/compat/quafu/warnings.py`
- `quantumbridge/compat/quafu/__init__.py`
- `quantumbridge/schema/backend_results.py`
- `tests/ecosystem/test_industry_taxonomy.py`
- `tests/compat_quafu/test_quafu_cloud_backend.py`
- `docs/architecture/industry_capability_taxonomy_v1.md`
- `docs/compat/quafu_cloud_execution.md`
- `docs/implementation/stage10g_industry_taxonomy_and_quafu_cloud_report.md`

Stage 10G source port count remains zero.

## Stage 11B Source Inventory

The following Stage 11B files are clean-room QuantumBridge implementations,
tests, or implementation records for native quantum-channel representations
and metrics. No Qiskit, PennyLane, Aer, wheels, dist-info, egg-info,
site-packages, or virtual environments are copied or vendored:

- `quantumbridge/information/channels.py`
- `quantumbridge/information/metrics.py`
- `quantumbridge/information/__init__.py`
- `quantumbridge/compat/qiskit_core/quantum_info_adapter.py`
- `tests/information/test_quantum_channels_extended.py`
- `tests/compat_qiskit_core/test_quantum_channel_parity.py`
- `tests/compat_qiskit_core/test_quantum_info_native.py`
- `docs/implementation/stage11b_native_quantum_channels_report.md`

Stage 11B source port count remains zero.

## Stage 11C Source Inventory

The following Stage 11C files are clean-room QuantumBridge implementations,
tests, or implementation records for native state analysis and operator
algebra. No Qiskit, PennyLane, wheels, dist-info, egg-info, site-packages, or
virtual environments are copied or vendored:

- `quantumbridge/information/analysis.py`
- `quantumbridge/information/entropy.py`
- `quantumbridge/information/__init__.py`
- `quantumbridge/compat/qiskit_core/quantum_info_adapter.py`
- `tests/information/test_state_analysis_extended.py`
- `tests/compat_qiskit_core/test_state_analysis_parity.py`
- `tests/compat_qiskit_core/test_quantum_info_native.py`
- `docs/implementation/stage11c_native_state_analysis_report.md`

Stage 11C source port count remains zero.

## Stage 11D Source Inventory

The following Stage 11D files are clean-room QuantumBridge implementations,
tests, or implementation records for native random quantum-information
generators. No Qiskit, PennyLane, wheels, dist-info, egg-info, site-packages,
or virtual environments are copied or vendored:

- `quantumbridge/information/random.py`
- `quantumbridge/information/channels.py`
- `quantumbridge/information/__init__.py`
- `quantumbridge/compat/qiskit_core/quantum_info_adapter.py`
- `tests/information/test_random_quantum_info_extended.py`
- `tests/compat_qiskit_core/test_random_quantum_info_parity.py`
- `tests/compat_qiskit_core/test_quantum_info_native.py`
- `docs/implementation/stage11d_native_random_quantum_info_report.md`

Stage 11D source port count remains zero.

## Stage 11E Source Inventory

The following files implement native phase-aware Pauli algebra, integrate
matrix observables and verify behavior against optional installed packages.
No upstream source, tests, package files, credentials or virtual environments
are vendored:

- `quantumbridge/operators/pauli.py`
- `quantumbridge/operators/pauli_list.py`
- `quantumbridge/operators/sparse_operator.py`
- `quantumbridge/information/random.py`
- `quantumbridge/information/statevector.py`
- `quantumbridge/information/density_matrix.py`
- `quantumbridge/information/__init__.py`
- `quantumbridge/compat/qiskit_core/quantum_info_adapter.py`
- `quantumbridge/utils/math.py`
- `tests/operators/test_pauli_phase_algebra.py`
- `tests/operators/test_pauli_algebra_extended.py`
- `tests/operators/test_operator_hamiltonian_extended.py`
- `tests/operators/test_p1_operator_coverage.py`
- `tests/compat_qiskit_core/test_pauli_phase_parity.py`
- `tests/compat_qiskit_core/test_quantum_info_native.py`
- `tests/qml/test_native_pauli_pennylane_parity.py`
- `examples/native_pauli_algebra_quantumbridge.py`
- `docs/implementation/stage11e_native_pauli_algebra_report.md`
- `docs/compat/matrix/qiskit_core_quantum_info_coverage_matrix.md`
- `README.md`
- `THIRD_PARTY_NOTICES.md`

Stage 11E source port count remains zero.

## Stage 11F Source Inventory

The following files independently implement, integrate or verify native
Clifford and pure stabilizer-state algebra. Installed Qiskit is used only as
an optional behavioral oracle. No upstream source, tests, package artifacts,
credentials or virtual environments are copied or vendored:

- `quantumbridge/information/clifford.py`
- `quantumbridge/information/stabilizer_state.py`
- `quantumbridge/information/random.py`
- `quantumbridge/information/__init__.py`
- `quantumbridge/operators/pauli.py`
- `quantumbridge/operators/pauli_list.py`
- `quantumbridge/compat/qiskit_core/quantum_info_adapter.py`
- `tests/information/test_clifford_stabilizer_native.py`
- `tests/compat_qiskit_core/test_clifford_stabilizer_parity.py`
- `examples/native_clifford_stabilizer_quantumbridge.py`
- `docs/implementation/stage11f_native_clifford_stabilizer_report.md`
- `docs/compat/matrix/qiskit_core_quantum_info_coverage_matrix.md`
- `README.md`
- `THIRD_PARTY_NOTICES.md`

Stage 11F source port count remains zero.

## Stage 11G Source Inventory

The following files independently implement, integrate, test or document
native stabilizer backend and ordered dynamic execution. Installed Qiskit/Aer
is an optional test oracle, not a native runtime dependency. No upstream
source, tests, credentials, package artifacts or environments are vendored:

- `quantumbridge/__init__.py`
- `quantumbridge/core/circuit.py`
- `quantumbridge/devices/__init__.py`
- `quantumbridge/devices/stabilizer_device.py`
- `quantumbridge/devices/sampler_device.py`
- `quantumbridge/devices/statevector_device.py`
- `quantumbridge/providers/__init__.py`
- `quantumbridge/providers/stabilizer_backend.py`
- `quantumbridge/providers/backend.py`
- `quantumbridge/providers/provider.py`
- `quantumbridge/primitives/backend.py`
- `quantumbridge/primitives/sampler.py`
- `quantumbridge/primitives/estimator.py`
- `quantumbridge/results/result.py`
- `quantumbridge/information/operator.py`
- `quantumbridge/ir/qb_ir.py`
- `quantumbridge/compat/qiskit_adapter.py`
- `quantumbridge/compat/qiskit_aer/__init__.py`
- `quantumbridge/compat/qiskit_aer/simulator_native.py`
- `quantumbridge/compiler/pass_base.py`
- `quantumbridge/compiler/pass_manager.py`
- `quantumbridge/compiler/cancellation.py`
- `quantumbridge/compiler/decomposition.py`
- `quantumbridge/compiler/optimization.py`
- `quantumbridge/compiler/routing.py`
- `quantumbridge/qasm/exporter.py`
- `quantumbridge/qasm/importer.py`
- `quantumbridge/qasm/parser.py`
- `tests/core/test_ordered_measurements.py`
- `tests/devices/test_stabilizer_device.py`
- `tests/providers/test_provider_model.py`
- `tests/compat_qiskit_aer/test_stabilizer_native.py`
- `examples/native_stabilizer_backend_quantumbridge.py`
- `docs/implementation/stage11g_native_stabilizer_backend_report.md`
- `docs/compat/matrix/qiskit_aer_fusion_coverage_matrix.md`
- `docs/compat/matrix/qiskit_core_primitives_coverage_matrix.md`
- `README.md`
- `THIRD_PARTY_NOTICES.md`

Stage 11G source port count remains zero.

## Stage 11H Source Inventory

The following files independently implement, integrate or verify native
mixed-state execution and physical Kraus instructions. Installed Qiskit/Aer
and PennyLane are optional behavioral oracles only. No upstream source,
tests, credentials, package artifacts or environments are copied or vendored:

- `quantumbridge/__init__.py`
- `quantumbridge/core/circuit.py`
- `quantumbridge/utils/math.py`
- `quantumbridge/devices/__init__.py`
- `quantumbridge/devices/execution.py`
- `quantumbridge/devices/density_matrix_device.py`
- `quantumbridge/devices/stabilizer_device.py`
- `quantumbridge/providers/__init__.py`
- `quantumbridge/providers/backend.py`
- `quantumbridge/providers/provider.py`
- `quantumbridge/providers/density_matrix_backend.py`
- `quantumbridge/providers/stabilizer_backend.py`
- `quantumbridge/information/channels.py`
- `quantumbridge/information/density_matrix.py`
- `quantumbridge/noise/channels.py`
- `quantumbridge/noise/execution.py`
- `quantumbridge/qml/qnode.py`
- `quantumbridge/qml/tape.py`
- `quantumbridge/results/result.py`
- `quantumbridge/schema/__init__.py`
- `quantumbridge/schema/aer_results.py`
- `quantumbridge/ir/qb_ir.py`
- `quantumbridge/compiler/pass_manager.py`
- `quantumbridge/compat/qiskit_adapter.py`
- `quantumbridge/compat/qiskit_aer/__init__.py`
- `quantumbridge/compat/qiskit_aer/simulator_native.py`
- `tests/devices/test_density_matrix_device.py`
- `tests/devices/test_stabilizer_device.py`
- `tests/providers/test_provider_model.py`
- `tests/qml/test_mixed_qnode_native.py`
- `tests/compat_qiskit_aer/test_density_matrix_native.py`
- `examples/native_mixed_state_quantumbridge.py`
- `docs/implementation/stage11h_native_mixed_state_execution_report.md`
- `docs/compat/matrix/qiskit_aer_fusion_coverage_matrix.md`
- `docs/compat/matrix/pennylane_devices_coverage_matrix.md`
- `README.md`
- `THIRD_PARTY_NOTICES.md`

Stage 11H source port count remains zero.
