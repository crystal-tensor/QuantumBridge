# Stage 11P-C3 Derivative Execution Gap Audit

Date: 2026-10-20. Starting main: `d05ad74` (native second adjoint, C2A).
Full independent Qiskit/PennyLane core replacement: ACTIVE / INCOMPLETE.
This audit records gaps before implementation, not delivered capabilities.

## Existing Ownership And Gaps

| Source | Existing behavior | C3 gap |
| --- | --- | --- |
| `qml/qnode.py` | Native first/second plans, argument tracing, VJP/JVP, streamed HVP | No unified derivative request or shared runtime ledger; VJP/JVP materialize a Jacobian |
| `diff/qnode_engine.py` | Actual native measurement execution and shift/adjoint gradients | Device calls and actual shots need shared reservations/consumption |
| `diff/second_order.py`, `second_adjoint.py` | Exact second shifts or tangent-over-reverse; child/transpose work preflight | Existing cumulative counters are not resource ownership/lifetimes |
| `diff/second_trace.py` | Bounded classical second maps, directional columns | Its accumulated numerical buffers do not describe simultaneous parent/child allocations or releases |
| `transforms/program.py`, `qwc.py` | Multi-child execution and differentiable processors, samples/covariance | Child caps are independent; retained child derivatives, processing arrays and active tapes need a parent ledger |
| `qml/shot_vector.py` | Explicit partitions and seeds | Cumulative consumption must survive partial failure without leaking reservations |
| `interfaces/native_host.py` | Fresh tracer-free native plans for callbacks | Fresh plans must not create independent unlimited resource accounts |
| `interfaces/jax_autodiff.py`, `jax_directional.py` | CPU JIT/VMAP first/second rules; forward status 0-4 | Existing checked second directional callback can return only NaNs, losing derivative failure category; a forward success is not HVP success |
| `interfaces/tensorflow_autodiff.py` | CPU graph callbacks and nested tapes | Forward status does not independently report a later failing derivative callback |
| `interfaces/qnode_autodiff.py` | Torch/Autograd native graph rules | Structured derivative errors and valid/fail/valid recovery require actual tests |
| `devices/{statevector,density_matrix,matrix_product_state,stabilizer}_device.py` | Real separate simulators | No native Device derivative protocol; unsupported Tableau continuous derivatives must not use dense fallback |
| `information/matrix_product_state.py` | Actual final tensor bytes and conservative local SVD guard | Final storage is not observed peak workspace; contraction/QR/SVD reservations and unavailable allocator peaks must be explicit |
| `execution/control_flow_engine.py`, core execution limits | Runtime loops/branches/instructions bounded separately | Not a shared derivative memory/tape/shot account; unsupported dynamic derivatives remain rejected |
| Aer snapshot contexts and results | Independent snapshot/pershot caps and native result schema | Snapshot copies/retention are not part of a unified derivative account; unsupported derivative snapshots must reject explicitly |

There is no existing class named `GradientEngine`. Reuse ExecutionPlan,
TransformedExecutionPlan, their native derivative methods and NativeHostKernel;
do not add a duplicate numerical quantum engine. Existing static limits remain
useful but taking their minimum is not runtime lifecycle accounting.

## Required Initial Red Contracts

1. A nonlinear multi-input, multi-layer QWC plan already passes existing local
   limits. A new unified memory/tape/work cap must reject its combined owned
   live buffers before quantum evaluations, with category/estimate and released
   reservations. Existing separate limits do not provide that contract.
2. One compiled JAX HVP-with-status function must distinguish runtime invalid
   input (1), unsupported (2), resource (3), native runtime (4), success (0),
   including forward success followed by derivative failure, and recovery.
   Status is current execution data, with zero tangent, not a traced constant.

Run these before production changes and retain real failed logs and exit codes.

Initial corrected contracts ran before production changes: 2 failed in 0.36s,
exit 1 (`/tmp/qb-stage11pc3-initial-red.log` and `.exit`). Existing local HVP
and compiled forward both succeeded before the missing unified APIs failed.
An earlier draft put a numerical duplication processor after QWC and received
PauliGroupResult objects; the draft was corrected to duplicate before grouping,
not used as evidence of a production regression.

The subsequent complete ChatGPT reply accepts the reported bounded C2A local
evidence, not an independent source audit. Its ten added C3 requirements are:
preserve d05ad74; add actual `second_adjoint` capability/dispatch; Device-level
Hessian and directional HVP with shift/FD spies; separately account forward,
tangent, adjoint, second accumulators, retained parameter graph and transform
buffers; 64-shared-parameter work regression; explicit unsupported mixed Kraus,
finite-shot adjoint and nonunitary dynamic branches; classified JAX/TF
second-adjoint status; retain every C2A mathematical/four-framework regression;
use the new 89.58936018334147% baseline; keep both original C3 red contracts.
These add to the full scope below, not a replacement or permission to stop early.

## Full Acceptance Scope (Not Yet Implemented)

- Native DerivativeExecutionRequest for value/Jacobian/VJP/JVP/Hessian/HVP:
  source Circuit/Tape/QNode, parameters, order, method, cotangent, tangent,
  shots, seed and limits; input/capability checks and actual native execution.
- Device supports/execute/compute derivatives and execute-and-compute variants;
  actual Statevector and MPS proofs, restricted fixed-CPTP density shifts;
  Tableau rejection, no fallback. QNode and Device results must agree.
- UnifiedResourceLedger shared through nested transforms/shifts/frameworks:
  estimate, reserve, observe, release, peak and unavailable. Track quantum
  states, MPS tensors/contraction/SVD workspace, density, snapshots, classical
  trace, derivative arrays, retained child outputs, active tapes, samples,
  covariance, partitions/seeds, shift expansion and result payload.
- Sequential temporary memory must not sum as simultaneous peak; retained
  outputs do count. Work and shots accumulate. Release on success/failure;
  consumed shots remain recorded after failure. This is not an OS RSS bound
  or a claim about arbitrary user Python/BLAS/framework allocator memory.
- Structured status/error/result: success, invalid, unsupported, resource,
  numerical failure, native runtime failure; code, stage, kind, method, failed
  operation, safe message, receipt, warnings and provenance. Eager errors and
  graph-readable outcomes must agree; failed derivatives never report success.
- Explicit JAX Jacobian/Hessian/HVP status in eager/JIT/supported VMAP, CPU
  float32/64, static output shapes, current parameters and nondifferentiable
  status. TF forward/Jacobian/VJP/Hessian/HVP graph status and nested-tape
  consistency, or explicit rejection of an unreportable graph path.
- Torch and Autograd valid/overbudget/valid, including double backward: no
  partial gradient, stale graph, swallowed error or finite-difference fallback.
- Preserve RX/RY/RZ/controlled/Pauli rotation math, shared/nonlinear inputs,
  coefficient cross terms, transformed mixed Hessians and streamed HVPs.
  Allocation spies must forbid a full Hessian in directional execution.
- 100-qubit GHZ plus RY(theta) on q99, TransformProgram/QWC/MPS/HVP with
  theta=.3 and direction=1: E=cos(theta), HVP=-cos(theta); prohibit dense
  state/density/full MPS expansion. Record bonds, stored bytes, conservative
  workspace limitations, transforms/shifts/shots, retained peak, work and
  truncation. Test Device and unified memory boundaries separately.
- Actual native H2 fixed geometry Gaussian/RHF/fermionic/JW built once,
  multiple HVP directions without SCF rebuild; transformed/unsplit,
  Device/QNode and all four supported framework results match. No geometry
  Hessian or differentiable-HF claim.
- Finite shots: explicit seed, QWC None/uniform/weighted, shot vectors,
  independent streams, actual vs logical work, estimate/uncertainty labels.
  Partial failure stops later children, preserves consumed shots and releases.
  Keep stochastic variance/nonlinear/integer allocation, postselection,
  dynamic random derivative and invalid local-seed rejections. Forward SE is
  not an HVP error bound.

## Negative And Validation Checklist

Cover joint local-vs-global memory, irrelevant full-Hessian cap for HVP,
forward-success/HVP-failure, runtime status classification, TF NaN-only failure,
sequential peak double count, nested cumulative shots, failure leaks, false MPS
workspace observation, receipt/call mismatch, Tableau fallback, nonfinite vs
budget, bad cotangent shape, hidden dense Hessian, stale JIT status, retained
snapshots, continued children after shot failure and too-late preflight.

Minimum distinct scenarios: resource lifecycle 20; Device requests 12;
status/recovery 12; JAX/TF graph status 10; Torch/Autograd failure 8;
MPS/H2/finite shots 8; independent math/public API differential 8. Repeated
parameterization does not replace distinct behavioral scenarios. Public SDK
APIs are black-box oracles, not imported native engines or copied source/tests.

Required final gates: compileall; separate derivative_execution suite; focused
interfaces/qml/transforms/devices/chemistry/compiler/serialization/Aer; SDK-free
full, main installed full, alternate installed full; independent JAX CPU and TF
CPU focus, Torch/Autograd focus; 100q/H2; Stage11H-C2A regressions; legal/privacy/
no-vendor/no-token; pip check; true full coverage with no new exclusions;
complete local matrix with full logs, independent exits, interpreter/versions,
executed vs unavailable lanes and tested tree SHA; diff check. Coverage before
C3 is 89.58936018334147%; aim >=90% for new core resource/status/request modules.

Reports must mark implemented/tested/differential/partial/unsupported/not-started
accurately, distinguish materialized vs directional derivatives and peak vs
cumulative resources, and list unbounded resources and all remaining full-core
gaps. C3 is not complete until all acceptance evidence exists. After C3, D is
Capture/ExecutionGraph/TransformDispatcher (including captured first/second
derivatives, runtime control, compiler/QASM3, MPS/H2), then full per-function
core completion. Studio stays last. No cloud/hardware/token, vendor, tags or
releases. Preserve unrelated user files. Only scoped local commits; remote is
stale/unverified after failed fetch, so no push until normal fresh fetch and
verified fast-forward. Never use old remote CI as new-source evidence.
