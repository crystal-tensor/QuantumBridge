# Stage 11P-A Native JAX Autodiff And Transform Integration

Date: 2026-10-20. Starting main HEAD
`bc17863eef852419b52263112724a6659e67a8f8`.
Full independent Qiskit/PennyLane replacement remains ACTIVE / INCOMPLETE.
Final clean-snapshot gates passed. This is a bounded native/JAX checkpoint,
not completion of the full SDK replacement objective.

## Native Execution Contract

Two persisted tests actually failed before runtime edits: qnode_interface and
transform_interface UnsupportedFeature, with real JAX/jaxlib 0.12.0 on CPU,
x64 enabled, no Qiskit/PennyLane installed. The implementation reuses QNode
source construction, AngleRecorder/parameter AST, native ExecutionPlan or
TransformedExecutionPlan, B5 child/postprocessing Jacobians and native
shift/adjoint. No second QNode, quantum simulator or gradient engine is created.

JAX records preprocessing and outer loss derivatives. A custom JVP is linear
in its tangents and uses the native Jacobian, allowing actual grad, VJP, JVP,
jacrev and jacfwd. Shared/nonlinear parameters and live Hamiltonian coefficients
remain in that graph. Coefficient product rules are tested independently.
Fresh host plans rebind each actual input, retaining native child reverse
postprocessing and B5 bounded explicit Jacobian products, not matrix-free VJP.
JIT captures owned device, immutable shot partitions, transform configuration
and a copy of gradient options. Later mutation of the original node cannot
change that compiled static definition. Gradient options cannot override the
validated diff_method; unknown options or invalid static step values reject.
Regression tests cover both the override route and post-trace configuration
mutation. Supported devices are native vector/density/MPS, not an SDK engine.

Trace planning uses static shapes and bounded native structural preflight,
not quantum execution or conversion of JAX tracers to NumPy/float. Source
coefficient placeholders define only structure; actual values and coefficients
are installed in fresh host plans. Raw unrecorded live circuit values reject.
Native Device copies isolate runtime scratch metadata. JAX is optional and
never imported by the core bridge module until a JAX call is requested.

## JIT, Status, Dtype And Randomness

Supported CPU JIT/VMAP uses public ShapeDtypeStruct, pure_callback, custom-JVP
and custom batching with explicit sequential host semantics. This is Python
native quantum execution on the host, not quantum simulation lowered to XLA
or GPU quantum batching. JIT metadata is a trace-configuration description;
pure callbacks may be dropped/duplicated/reordered, so actual scheduled call
counts or telemetry are not inferred from callback side effects.

Checked calls return explicit nondifferentiable status (zero tangent):
0 success, 1 invalid/nonfinite numerical value, 2 unsupported runtime path,
3 resource failure, 4 other runtime failure. Failed value/derivative buffers
are NaN. Tests exercise nonfinite input, recovery on a valid next input and
injected runtime failures. Intentional callback exceptions are not the error
protocol. Static capabilities, shapes and derivative methods reject before
callbacks; normal eager calls retain ordinary exceptions.

Float32 and caller-enabled float64 are tested in separate subprocesses.
Import does not change JAX x64. Complex inputs/outputs, unsupported gate
broadcasting and half precision reject rather than dropping imaginary parts.
Only native real expval/variance/probability outputs are currently verified.

Finite shots require immutable nonnegative integer seeds. Identical parameters
and seed reproduce output and estimated gradient; distinct seeds change sample
streams. Group/shift/partition seeds are independent, with actual eager physical
work receipts. Sampled seeded JIT matches eager values but does not claim a
guaranteed execution count. Dynamic PRNG keys/general stochastic and sampled
variance protocols remain open. Forward energy SE is not a gradient error bound.

## Functional Evidence

Native independent scenarios cover scalar/array/keyword/nontrainable/unused
inputs, nested input/output PyTrees, classical preprocessing, shared gate and
coefficient graphs, vector cotangents, multiple real child Tapes, reverse stage
order, merge/cancel/compile/QWC, coherent reused-wire records, template arrays,
fresh coefficient primals, analytic variance and explicit algorithm selection.

The 100-wire GHZ/template/QWC MPS test forbids dense vector, full density and
MPS expansion APIs. At theta .3, actual energy/gradient match cos(theta) /
-sin(theta), peak bond 2, 12672 tensor bytes, zero discarded weight/truncations,
zero physical shots and
two shifted evaluations. Storage is not peak SVD workspace or an arbitrary-
entanglement efficiency guarantee. Actual eager metadata, not extra resource-
only runs, supplies the receipt.

Real H2 geometry at 1.4 bohr constructs normalized Gaussian integrals/RHF/
fermionic/JW Hamiltonian once. Native excitation/QWC plus JAX gradients match
native untransformed energy/gradient, execute four optimizer steps and reduce
energy. SCF is not rebuilt per child/shift. This is not differentiable HF,
general molecules or a universal VQE convergence claim.
The observed initial energy/gradient are -1.0279252771620968 /
.40622294673301496; four updates reach theta -.047535396965457145 and energy
-1.124436398279178. The two-group simpler training example reduces energy
from .5465058110692771 to -.46668730879882847 in 12 updates.

Eight independently authored public PennyLane scenarios compare values,
native shift gradients, preprocessing, coefficients, array/kwargs, probability
Jacobians, QWC, JIT and JVP/VMAP. PennyLane's tested eager parameter-shift VMAP
path rejects abstract tracer conversion; that case is separately expected-
failed and is not matching-oracle evidence. Public backprop is the numerical
oracle for the matching VMAP scene only, never the native quantum engine.
No upstream implementation/test source or private helper is used as production
code. Public stack traces from failed calls are diagnostic output, not source
ports or design input.

## Resource Boundaries

JAXBridgeLimits checks input/output elements, source and expanded parameter
counts, input/expanded Jacobian storage, transform Tape count, mapped batch
size and conservative total sampled derivative work before quantum execution.
Structural preflight uses zero-width Dual seeds; full source tangent bases are
allocated only within verified matrix budgets. Existing TransformLimits,
native device and control-flow limits still apply.

Callback budget means logical mapped expansion per axis, not a strict global
JIT scheduling counter. Arbitrary nested/dynamic user control flow and global
aggregate callback scheduling are not a proven resource protocol. Pure host
callbacks do not remove native MPS entanglement/memory limits.

## Verification Receipts

| Gate | Current receipt |
| --- | --- |
| First two red tests | Actually failed before implementation in isolated JAX 0.12.0 |
| Complete new native focused | 53 independent test functions passed in isolated JAX 0.12.0, 6.35s |
| Main PL 0.44.1 / JAX 0.7.1 public and grad/JIT focused | 24 passed / 1 separately expected public failure |
| Alternate PL 0.42.3 / JAX 0.6.2 public and grad/JIT focused | 24 passed / 1 separately expected public failure |
| SDK-free full | 1568 passed / 209 skipped / 5 warnings, 52.14s, independent exit receipt 0 |
| Main installed full | 1975 passed / 5 skipped / 1 known public xfail / 51 warnings, 70.87s, exit 0 |
| Alternate installed full | 1919 passed / 61 skipped / 1 known public xfail / 8 warnings, 63.90s, exit 0; ten QASM3 scenarios restored |
| Independent JAX focused | Full interfaces 56 passed / 10 skips, 6.61s, exit 0; all 53 new native tests executed |
| Focused system/previous-stage integration | 1232 passed / 1 skip / 1 known public xfail / 6 warnings, 58.71s, exit 0 |
| Explicit full-package coverage | 1975 passed / 5 skipped / 1 xfailed / 51 warnings, 178.57s, exit 0; 22751 / 25453 = 89.3843554787255%, 68 unchanged excluded lines; JAX bridge 277 / 290 = 95.51724137931035% |
| Complete local matrix and independent shell exit receipt | All 28 sections completed; separately persisted shell exit 0; two plain fulls 1975 passed / 5 skipped / 1 public xfail / 51 warnings (72.05s / 69.24s); actual embedded coverage 1975 passed / 5 skipped / 1 xfailed / 51 warnings (177.04s), 25453 statements / 2702 missing |
| Compileall / attribution/privacy / examples | Final runtime snapshot compileall exit 0; legal/no-vendor/no-cloud/no-token 9 passed; all four CLI examples pass in SDK-free-plus-JAX isolated environment |

Environment changes are isolated outside the repo. Main overlay adds JAX
0.7.1 to the existing PL 0.44.1/Qiskit 2.4.1/Torch 2.12/Autograd 1.8/PySCF
2.13.1 base while retaining NumPy 2.4.6. Alternate isolated environment uses
PL 0.42.3/Qiskit 2.6/Aer 0.17.2/JAX 0.6.2/NumPy 2.5.4/Autograd 1.9.1.
Independent JAX 0.12.0 has NumPy 2.5.4 and no SDKs. SDK-free retains no JAX
or SDKs. Missing framework skips are not framework evidence.

Independent/alternate pip checks are clean. The overlay-only uv check sees
only its own installed packages; the full inherited main pip check still
reports the existing pyquafu/NumPy and WeasyPrint/tinycss2 conflicts. Neither
base environment nor global TLS/auth settings is changed. Initial pip TLS
failures and a package-download timeout were not bypassed: normal uv verified
downloads succeeded, with a longer HTTP timeout for the retry.

Initial full and explicit coverage gates passed on the pre-final-review tree.
Final review found a gradient-options override route and mutable captured
configuration, which are now guarded and covered by new tests. Those earlier
full receipts are not used as final-source proof; all full/coverage/matrix gates
are rerun from the frozen runtime tree. The pre-review matrix was deliberately
terminated (exit 143), not passed. The alternate environment also restored
qiskit-qasm3-import 0.6.0 before the final run so ten previous public QASM3
scenarios are not silently dropped as newly missing dependencies.

The frozen runtime snapshot is `/tmp/qb-stage11pa-check-yGS7jH`. The separate
matrix snapshot is `/tmp/qb-stage11pa-matrix-check-xUtmY0`, avoiding competing
coverage databases. All 17 staged Python source/test/example files match both
snapshots. Report-only final receipt changes do not alter runtime code.
Every final full run has its own `/tmp/qb-stage11pa-final-*.exit` file with
the actual shell exit code, not an inference from the last log line.
The final matrix log is `/tmp/qb-stage11pa-final-matrix.log`; its explicit
exit receipt is `/tmp/qb-stage11pa-final-matrix.exit` (0). It uses the unchanged
matrix script and a temporary pytest entry point to the same validated Python
environment, preserving pytest 9.0.3/pytest-cov 7.1.0/coverage 7.14.1.
Finance, Optimization, ML, Dynamics, Metal, Experiments and Addons installed
lanes are explicitly unavailable, not installed coverage. Existing Studio
backend tests run as regression only; no Studio implementation is included.

The dirty user workspace attribution probe remains 5 passed / 1 failed,
specifically the pre-existing untracked `quantumbridge/router/core.py` absent
from its ledger. It is not part of either clean snapshot. No user Router file
is modified/staged/deleted to hide it. Package line coverage and pytest counts
are not percentages of complete SDK functional coverage.

## Git And Remaining Full Parity

The preserved local Stage 11M-11O chain ends at starting B6 bc17863. No rewrite,
tag/release/vendor/cloud/hardware/token or user Studio/Router work is included.
Publication remains separate: pushed=false, remote_ci_verified=false; stale
origin/main is not live remote evidence. Restored normal authorization, fresh
fetch, verified fast-forward, ordinary main push and exact-SHA CI are still
required. Dirty user Router attribution must remain a separate receipt.

Higher-order/Hessian/HVP, TensorFlow, capture/Catalyst, full JAX/device/plugin
protocols, GPU/TPU, dynamic keys, native backprop, complete QNode/operations/
templates/measurements/qchem and the remaining Qiskit full APIs remain open.
Stage 11P-A adds independently executed native quantum functionality through
JAX, not complete JAX/PennyLane/Qiskit functional parity.

## Final Acceptance Questions

| Question | Answer / final receipt |
| --- | --- |
| 1. Starting / ending SHA | Starting bc17863eef852419b52263112724a6659e67a8f8; ending normal main commit is supplied in the external Git/execution handoff, not a self-referential file hash |
| 2. Retained history | Normal descendant of 11M/11N/11O-C/11O-A/B1-B6; no reset/rebase/amend/force |
| 3. Real grad | Yes: actual JAX grad/value_and_grad invokes native quantum derivatives, not a constant surrogate |
| 4. JVP/VJP | Yes within tested real first-order bounded Jacobian contracts; JVP linearity and cotangents verified |
| 5. jacrev/jacfwd | Both execute native quantum Jacobian products, with nested/array and JIT tests |
| 6. JIT/JIT-grad | Supported CPU host-callback subset, explicit shape/dtype/status; not quantum XLA lowering |
| 7. VMAP | Sequential CPU host mapping with checked per-axis expansion; not GPU or full batching parity |
| 8. TransformProgram | Actual child plans, coefficient/source maps and reverse postprocessing derivatives |
| 9. Coefficients | Shared gate/coefficient product rule, coefficient-only and zero-primal cases verified |
| 10. Nested output | Stable real dict/list/tuple PyTrees, probability maps and vector cotangents |
| 11. Finite gradient | Real native independent shifted estimates with explicit immutable seed; not pathwise bitstring differentiation |
| 12. Shot vectors | Native partitions/group allocations and actual eager physical work preserved |
| 13. Quantum execution proof | Existing native ExecutionPlan Jacobian instrumentation, method receipts and actual mathematical outputs; no SDK engine |
| 14. MPS | 100 wires, dense APIs forbidden, peak bond 2 / 12672 bytes / two shifts / zero physical shots; bounded example |
| 15. H2 optimizer | Native geometry/integrals/RHF/JW built once, actual energy/gradient and four updates; not differentiable HF |
| 16. Independent math | Analytic trig, coefficient product rule, probability Jacobian, tangent/cotangent and native dynamic/defer comparisons |
| 17. Public differential | Eight matching scenes per public version; separate known eager shift/VMAP unsupported case is not matching evidence |
| 18. SDK-free full | 1568 passed / 209 skipped / 5 warnings, actual exit 0 |
| 19. Main installed full | 1975 passed / 5 skipped / 1 public xfail / 51 warnings, actual exit 0 |
| 20. Alternate installed full | 1919 passed / 61 skipped / 1 public xfail / 8 warnings, actual exit 0 |
| 21. Independent JAX | 53 new native scenes plus existing interfaces: 56 passed / 10 explicit missing-framework skips, actual exit 0; no SDKs |
| 22. Explicit coverage | 89.3843554787255%, 68 unchanged exclusions; new JAX bridge 95.51724137931035%; exact test/exit receipt above |
| 23. Full matrix exit | All 28 sections complete, actual independent shell exit 0, real embedded coverage executed; full log/receipt paths above |
| 24. Resources | Preflight input/output/parameters/Jacobians/Tapes/shots/batch, native device limits; callback budget is logical expansion, not guaranteed JIT schedule |
| 25. Legal/privacy | Final runtime snapshot 9 passed; final receipt-only index snapshot checked before commit; no source ports/vendor/token/cloud; dirty user Router 5 passed / 1 failed reported separately |
| 26. Git/CI | Local only; pushed=false / remote_ci_verified=false, no stale-origin/new-SHA CI substitution |
| 27. Unsupported | Higher order, capture, TF, native backprop, complex/full-state derivatives, full plugin/device protocols, dynamic keys, GPU/TPU and other stated contracts |
| 28. Remaining parity | Complete JAX/TF and derivative/device interfaces plus all outstanding Qiskit/PennyLane core, chemistry and ecosystem APIs remain active |

The first-order native/JAX paths genuinely execute independent native quantum
values and derivatives. Phase completion does not imply complete JAX interface,
PennyLane interface or Qiskit/PennyLane full functional parity.
