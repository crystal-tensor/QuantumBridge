# Stage 11P-B Native TensorFlow Autodiff Report

Date: 2026-10-20. Starting local main:
`edf4728f9d51d8825a2f07390edbea71435fa80d`.
Full independent Qiskit/PennyLane functional replacement remains ACTIVE /
INCOMPLETE. This CPU first-order checkpoint does not narrow that goal.

## Architecture and Red Evidence

Existing Tape/QNode/AngleRecorder, native Device, parameter-shift/adjoint and
transformed child/postprocessing Jacobians are reused. Shared host-plan code
was extracted from the independent JAX bridge into `interfaces/native_host.py`.
TensorFlow supplies classical differentiation, variables, optimizers and
outer-loss graphs, never the quantum simulator/quantum derivative algorithm.
There is no TF Quantum/PennyLane runtime on the native quantum path.

Two independently authored actual TF tests failed before production edits:
RY/Z squared-loss GradientTape and QWC with a shared gate/coefficient variable.
Result: 2 failed, 1.33s, exit 1, explicit pre-existing UnsupportedFeature guards.
Both then passed without changing their formulas and with actual native
ExecutionPlan.jacobian spies prohibiting finite differences.

Classical source recording is symbolically traced even in eager calls, so
float(x), x.numpy() and np.asarray(symbolic_x) cannot silently erase the graph.
All TF variables, including tested closures, are read into explicit packed
inputs outside custom_gradient. The primitive therefore does not capture/read
resource variables in its body and does not invent missing grad_vars.
Forward execution and the first-order VJP build fresh native plans. A second
custom-gradient boundary explicitly rejects second derivatives; max_diff=1
is not merely a label.
Native result-tree reconstruction gained a framework reshape callback;
symbolic TF template arrays use static indexing rather than Python tensor
iteration. Native Circuit reconstruction now distinguishes scalar TensorShape
from a vector and uses TF reshape/unstack without a numeric cast. Eager
classical recording intentionally traces per call and can emit TF retracing
warnings; this checkpoint does not claim optimized tracing/cache throughput.

## Supported and Unsupported Contracts

| Contract | Implemented evidence / boundary |
| --- | --- |
| Eager / GradientTape / Variable | Real native derivatives, float32/64, scalar/vector/shared/kwargs/nested/unused/nontrainable inputs |
| Preprocessing / outer loss | Actual tf.sin and nonlinear shared expressions; no Python numeric read during source tracing |
| Hamiltonian coefficients | Coefficient-only and gate/coefficient product rules; fresh concrete coefficients per execution |
| Transforms | Real child execution, reverse nonlinear processing, cancel/merge/compile/defer/QWC and template inputs |
| tf.function | Fully defined static real shapes, same-process CPU host callbacks; fresh runtime .2/.7 values and gradients |
| Nested outputs / cotangents | Native dict/list/tuple reconstruction with TF reshape; explicit vector cotangents and Jacobian axes |
| Bounded mapping | tensorflow_batch: one real tensor argument, static nonempty leading axis, sequential CPU map |
| Finite shots / vectors | Explicit immutable integer seed; None/uniform/weighted QWC allocation and repeated shot partitions |
| SGD/Adam | Twenty actual optimizer updates with variable changes, lower losses and actual gradient traces |
| MPS / chemistry | 100-wire no-dense native MPS and actual Gaussian/RHF/JW fixed-geometry H2 optimizer |
| Higher order / Hessian / HVP | UNSUPPORTED, explicit nested-tape rejection |
| Dynamic shapes / arbitrary data-dependent control | UNSUPPORTED or unverified, not implied by tf.function support |
| Complex / full-state derivatives | UNSUPPORTED; real expval/analytic variance/probability trees only |
| GPU / TPU / distributed | UNSUPPORTED; native CPU host execution only |
| XLA / portable SavedModel | UNSUPPORTED; host callbacks are same-process Python/native execution, not portable quantum lowering |
| Complete TF/device/plugin/PennyLane/Qiskit parity | INCOMPLETE; full final goal retained |

Callback limits bound logical forward/backward work per call and explicit
bounded map expansion, not arbitrary external TF scheduling/loops/repeated
graph invocations. Eager repeated persistent backward calls are checked before
additional native work. Source/expanded parameter, Jacobian, output and child
Tape budgets precede native allocation/execution. Device/Transform/MPS limits
remain active. Finite gradients are estimates, not pathwise or exact/stochastic
accuracy claims. Forward standard errors do not bound arbitrary derivatives.

Eager receipts distinguish actual forward_execution, backward_calls and
observed_physical_shots. The native derivative's own gradient_physical_shots
and group/partition/base/linear/shift receipts are retained. Graph metadata is
explicit trace configuration only, not observed callback/physical work counts.
Checked forward status is 0 success, 1 invalid/nonfinite, 2 unsupported,
3 resource limit, 4 unexpected failure. Failed derivatives are NaN; the forward
status is not a retroactive backward-status channel. Ordinary graph execution
asserts on host failure. Static invalid contracts reject before callbacks.

## Actual Examples

Independent TF-only environment, no installed Qiskit/PennyLane/Torch/JAX:

- Nonlinear preprocessing: value 0.4521558453381717, gradient -2.615456975338976.
- QWC SGD: 20 real updates, energy 0.5465058110692771 to -0.7019909554519349;
  final theta 3.1517273488880067, two QWC children, actual native postprocessing derivative.
- 100-wire GHZ/RY99 MPS: E 0.955336489125606, gradient -0.2955202066613397,
  max bond 2, tensor bytes 12672, discarded weight/truncations/shots 0,
  two shifted evaluations, two transforms. Dense statevector/density/MPS
  expansion APIs explicitly fail if called. Config: bond<=4, 2 MiB, cutoff=0.
  Low-entanglement only; reported tensor storage excludes peak workspace.
- H2 1.4 bohr: one native Gaussian/RHF/JW construction, four TF SGD updates,
  initial E -1.0279252771620968, initial gradient 0.40622294673301496,
  final theta -0.04753540588441414, E -1.1244363995597488,
  five QWC children, two transforms. Unsplit native value/gradient checked.
  This is not differentiable Hartree-Fock or general VQE convergence.

## Public References and Oracles

Only public contracts were consulted:
[custom_gradient](https://www.tensorflow.org/api_docs/python/tf/custom_gradient)
and [numpy_function](https://www.tensorflow.org/api_docs/python/tf/numpy_function).
These fetched pages identify their documentation snapshot as v2.16.1; actual
runtime verification uses TF 2.21.0, not an assumed matching docs version.
No upstream implementation/test source was opened/copied or used as runtime.
Six independently authored public PennyLane TF scenarios cover basic gradient,
shared nonlinear preprocessing, QWC, gate/coefficient product rule, vector
weights and probability cotangents. The actual 0.44.1 installation still
executes these calls despite its removal/deprecation warning; version labels
alone are not treated as proof of unavailability. For the coefficient oracle,
all constants are explicitly float64: a public Python-literal cast initially
introduced a ~1e-9 value difference. Independent native formulas remain strict;
no tolerance relaxation or success claim for a failed comparison was used.

## Final Verification

Environment facts: Python 3.12.6, macOS 27.0.1 arm64; actual TF CPU/eager
operations. Independent TF environment uses TF 2.21.0 / NumPy 2.5.4 and has
no installed quantum SDK/JAX/Torch/Autograd. Its actual uv pip check exits 0.
Main installed overlay uses TF 2.21.0, NumPy 2.4.6, Qiskit 2.4.1, Aer 0.17.2,
PennyLane 0.44.1, JAX/jaxlib 0.7.1, Torch 2.12.0, Autograd 1.8.0, PySCF
2.13.1 and OpenFermion 1.7.1. Alternate overlay pins Qiskit 2.6.0,
PennyLane 0.42.3, JAX/jaxlib 0.6.2, Autograd 1.9.1 and the same TF/native
numeric stack. Unlike the preceding phase's isolated alternate, this overlay
inherits the main installation's Torch/chemistry packages; test availability
and counts must not be presented as the same environment as that earlier run.

Both inherited overlays' full `python -m pip check` exits 1 for exactly the
two unchanged base conflicts: WeasyPrint/tinycss2 and pyquafu/NumPy<2.
They are not clean dependency resolutions, and a local uv-only package check
cannot establish inherited environment health. Additional temporary TF
installer conflicts were removed in the new overlays only by compatible
NumPy 2.4.6, protobuf 6.33.6, requests 2.32.5, setuptools 81.0.0 and alternate
cachetools 5.5.2; no base environment or project dependency metadata was changed
except the optional TF extra. An additional isolated all-framework download
attempt was terminated as unnecessary; it supplies no validation evidence.

### Native Library Collision

The first full installed runs hung and were deliberately terminated, exit 143,
not counted as passing. A minimal subprocess with no QuantumBridge imported
reproduced a timeout after importing PyArrow 24 before TF 2.21 and evaluating
tf.function(sin). The sampled native stack crosses TensorFlow absl mutex code
into libarrow.2400.dylib's same-version synchronization symbol. This suggests
native symbol interposition, not a demonstrated native QNode quantum error.
Loading TF first worked; using PyArrow 23.0.1 in the test overlays also made
the Arrow-first minimal graph execute normally. This is environment evidence,
not proof of arbitrary library co-installability or a universal root-cause fix.
No import-order mutation, global framework setting or TLS/authentication
workaround was added to QuantumBridge. Final installed validation uses the
explicit PyArrow 23.0.1 overlay and must be reported with that condition.

### Scope and Receipts

Final runtime/source snapshot tree:
`cc81bc2cb2a5bd2aca8a79229238cf68fc44b465`, extracted into
`/tmp/qb-stage11pb-verified-ihQs70`; independent matrix copy:
`/tmp/qb-stage11pb-verified-matrix-PlMVuF`. All 21 changed Python files plus
pyproject.toml match the tested tree's blobs. Subsequent changes are report,
README and other scoped documentation only, separately checked before commit.

| Gate | Actual terminal result | Independent receipt |
| --- | --- | --- |
| SDK-free full | 1570 passed, 291 skipped, 5 warnings, 54.23s | `/tmp/qb-stage11pb-verified-sdkfree.{log,exit}`, exit 0 |
| Main installed full | 2059 passed, 5 skipped, 1 known public xfail, 57 warnings, 85.16s | `/tmp/qb-stage11pb-verified-main.{log,exit}`, exit 0 |
| Alternate installed full | 2059 passed, 5 skipped, 1 known public xfail, 49 warnings, 83.64s | `/tmp/qb-stage11pb-verified-alternate.{log,exit}`, exit 0 |
| Independent TF full | 1646 passed, 215 skipped, 5 warnings, 61.06s | `/tmp/qb-stage11pb-verified-independent.{log,exit}`, exit 0 |
| Independent TF focused | 78 passed, 7.49s; no missing-TF skips | `/tmp/qb-stage11pb-verified-tf-focus.{log,exit}`, exit 0 |
| Interfaces/QML/transforms/templates/devices/chemistry | 704 passed, 1 optional missing-JAX-test skip, 2 warnings, 58.80s | `/tmp/qb-stage11pb-verified-focus.{log,exit}`, exit 0 |
| Independent latest JAX 0.12 interface regression | 58 passed, 86 unavailable-other-framework skips, 14.31s | Actual terminal exit 0; quantum SDKs/TF/Torch/Autograd absent |
| Full explicit coverage | 2059 passed, 5 skipped, 1 known public xfail, 57 warnings, 200.34s | `/tmp/qb-stage11pb-verified-coverage.{log,exit}`, exit 0 |
| Legal/privacy/no-vendor/no-token scoped snapshot | 9 passed, 0.28s | Actual terminal exit 0 |
| compileall quantumbridge/examples/tests | No diagnostics | Actual terminal exit 0 |
| Four isolated-TF CLI examples | Actual main functions and assertions | `/tmp/qb-stage11pb-verified-examples.{log,exit}`, exit 0 |
| Complete local matrix | All 28 sections completed, shell exit 0 | `/tmp/qb-stage11pb-verified-matrix.{log,exit}` |

`tests/gradients` is not an existing directory; native gradient tests actually
reside under interfaces/QML/transforms/templates and the public differential
tests, all included in full gates. No `|| true` or test-result masking is used.
The known public xfail remains the separately recorded upstream eager
JAX/parameter-shift/vmap tracer rejection; it is not a TF/native success.
Unavailable dependency skips do not count as functional validation.

Final explicit coverage: 22958 / 25669 = **89.43862246289298%**,
above 89.3843554787255%; exclusions remain **68**, unchanged. New TF bridge:
170 / 174 = **97.70114942528735%**. Shared host bridge: 175 / 182 =
**96.15384615384616%**. JSON: `/tmp/qb-stage11pb-verified-coverage.json`.
Line coverage is not complete API coverage or full parity.

The complete final matrix's two plain full suites each pass 2059 / 5 skipped /
1 known public xfail / 57 warnings (83.95s and 77.97s). Its actual embedded
coverage suite also passes the same counts (190.36s), TOTAL 25669 / missing
2711, consistent with explicit coverage. Finance, Optimization, ML, Dynamics,
Metal, Experiments and Addons installed lanes are genuinely unavailable/not
executed, not advertised as validated industry functionality. Existing Studio
backend tests run as regressions only; no Studio implementation is included.

Independent native test function counts: 25 basic GradientTape/classical/
Variable scenarios, 10 transform scenarios, 9 graph scenarios, 14 finite-shot/
resource scenarios, 16 negative scenarios, 4 real example scenarios = 78.
Six public TF black-box scenarios additionally pass on each installed public
PennyLane version; 0.44.1 emits six deprecation warnings, not unavailable skips.

Final resource review added a separate preflight on each fresh runtime native
plan. Data-dependent transform child growth must recheck child count and shot
work before any quantum execution, rather than trusting placeholder-value
planning. Repeated eager backward calls also check actual remaining shots.
Three independent child-growth/cumulative-budget tests cover these cases.
All final full/focused/coverage gates were rerun after the production fix.
Earlier pre-review 2057-pass/89.43615% snapshots and their completed matrix
are not substituted for the final runtime snapshot's verification.

The dirty user workspace still has one independent pre-existing legal failure:
untracked `quantumbridge/router/core.py` mentions upstream but is absent from
the source ledger. A live probe reports 1 failed / 7 passed / 1 skipped;
the same TF-only clean snapshot probe reports 8 passed / 1 skipped, and the
main installed clean probe reports 9 passed. User Router/Studio are not changed,
staged, reverted or misrepresented as a clean full working directory.

## Acceptance Answers

1. Start HEAD: edf4728f9d51d8825a2f07390edbea71435fa80d. End is the ordinary
   local main checkpoint commit containing this report; its exact SHA is
   resolved after commit and included in the execution handoff. Tested source
   tree and blob identity are recorded above, not inferred from HEAD alone.
2. TF 2.21.0, Python 3.12.6, Apple Silicon CPU; exact environment conditions above.
3. Both red tests failed before runtime edits and then passed unchanged.
4. Actual GradientTape consumes the native quantum VJP, not an array wrapper.
5. Real tf.Variable values change in eager SGD and graph Adam workflows.
6. ExecutionPlan.jacobian spies, independent math and actual shift/adjoint selection.
7. Actual transformed child quantum Jacobians and reverse postprocessing VJP;
   no bypass to the original untransformed node.
8. Shared gate/coefficient full product rule, coefficient-only and fresh primals.
9. TF sin/nonlinear/vector/shared/kwargs preprocessing stays in its actual graph.
10. Concrete tf.function traces do not simulate; runtime .2/.7 values and
    gradients change without retracing, including closure Variable assignment.
11. Twenty actual SGD and Adam updates, real traces and decreasing tested losses.
12. Actual seeded finite-shot estimates and separate eager forward/gradient work.
13. Shot vector partitions and None/uniform/weighted group allocation verified.
14. 100-wire MPS with dense APIs forbidden; actual bounded storage/gradient above.
15. Native geometry-derived H2, one SCF build, unsplit reference and four updates.
16. At least 25 independent basic math scenarios plus transforms, graph,
    sampling, negatives, native shift/adjoint and classical TF references.
17. Six actual public TF oracle scenarios on PL 0.44.1 and 0.42.3; no fictional
    unavailability inferred from the newer installation's deprecation warning.
18. SDK-free full passes, with genuine unavailable optional paths skipped.
19. Installed full passes under the explicitly documented test overlay.
20. Alternate pinned Qiskit/PennyLane full passes, with inherited packages disclosed.
21. Independent TF full/focused pass; no upstream quantum SDK is needed.
22. Actual 89.43862246289298% overall / 97.70114942528735% new TF core;
    exclusions unchanged, not proof of full parity.
23. Complete matrix: 28 sections, actual independently recorded shell exit 0;
    complete log and successful embedded full coverage above.
24. CPU first-order/static host subset only; all unsupported boundaries above remain.
25. All required local runtime gates completed before the ordinary scoped
    checkpoint commit. No push/auth recovery/remote CI is claimed. Successful
    commit makes local_commits_ready=true; remote_pushed=false and
    remote_ci_verified=false remain unchanged.
26. Next: real native higher order/Hessian/HVP and framework second-order chains,
    then capture/dispatcher/execution graph, complete device protocols and all
    remaining Qiskit/PennyLane core/industry functions. Studio remains last.

Does GradientTape actually traverse the native QNode, child quantum executions,
postprocessing and VJP? **Yes, for the independently tested supported subset.**
Is complete TensorFlow/PennyLane/Qiskit full functional parity achieved? **No.**

## Remaining Work and Publication

No Studio/Router edits, cloud/hardware/token execution, source vendoring,
package artifacts, tags/releases, workflow deletion, history rewriting,
authentication/TLS changes or remote publication belong to this checkpoint.
User dirty files are preserved. Prior cached origin/main is not fresh remote
evidence; no new remote CI success is inferred from it. Higher order/Hessian/HVP,
capture/dispatcher/device protocols and the remaining full core/industry API
contracts still require actual implementations and independent tests.
