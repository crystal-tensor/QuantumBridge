# Stage 11P-C3 Derivative Status Progress

Date: 2026-10-21. Status: IN_PROGRESS / PARTIAL.

Protocol version 1 outcomes: success=0, invalid input=1, unsupported=2,
resource limit=3, native runtime failure=4, numerical failure=5. Structured eager
errors carry stage, derivative kind, method, safe message and a released-resource
receipt. Unified budget errors also carry category, estimated total, actual
consumption/live reservation and limit. Arbitrary simulator exception messages
are not included in graph-safe outcomes. Known TransformError wrappers preserve
the underlying resource/unsupported outcome rather than becoming generic code 4.

Explicit QNode JAX Jacobian/Hessian/HVP query methods return the outcome of each
actual native Device request. They support one static real floating array input,
CPU float32/64 and sequential VMAP. Classical JAX source Jacobian/second maps
are combined with native recorder maps; nonlinear gate/coefficient chain terms
are not discarded. One compiled function changes status with runtime inputs.
Status cotangents are zero. Query payloads reject additional differentiation;
ordinary QNode automatic differentiation remains the existing separate interface.

Explicit TensorFlow value/Jacobian/VJP/Hessian/HVP query methods use the same
Device executor and native quantum methods. Classical maps come from real
GradientTape/Jacobian operations. tf.function receives payload plus integer
runtime status, not Python callback exception propagation alone. Native output
tree order is retained in VJP cotangents, not tf.nest's sorted dict order.
Unreportable extra differentiation of query payloads explicitly rejects rather
than silently returning a disconnected gradient. Closure trainable Variables,
complex cotangents and unsupported shapes reject. No XLA/GPU/TPU/distributed/
portable-graph support is claimed.

Preliminary main-environment query tests: JAX 8 passed; TF 9 passed in 4.04s,
exit 0 (`/tmp/qb-stage11pc3-tf-status-second.log` and `.exit`). Initial TF query
tests caught a missing explicit tf.reshape adapter in output reconstruction;
the runtime was corrected without enabling global NumPy behavior or changing
test expectations. Independent TF 2.21 / NumPy 2.5.4 derivative_execution focus:
62 passed, 2 JAX missing-dependency skips, exit 0
(`/tmp/qb-stage11pc3-independent-tf.log` and `.exit`). These are not final full
C3 multi-environment or coverage receipts.

Still open: multi-positional/keyword derivative queries, ordinary JAX/TF graph
callback shared accounting, derivative statuses consistent across every supported
nested graph, actual Torch/Autograd structured errors/recovery, finite-shot
partial failures and complete acceptance scenarios/gates. Legacy forward-only
status does not certify a subsequent derivative. No complete derivative-device
or Qiskit/PennyLane functional parity is claimed.

Latest frozen progress receipts are listed in the resource report: main C3
focus 88 passed, alternate 86 passed/2 specifically observed upstream xfails,
independent TF focus 74 passed/3 missing-dependency skips. The TF status file
now has 13 tests, including static dtype/shape/order/tangent checks, explicit
distributed rejection, tuple cotangent containers and direct real native host
source-map validation. New TF query statements cover 97/100 in the focused
run. This does not replace full-suite coverage or complete graph acceptance.

After that frozen progress tree, ordinary eager Torch/Autograd callbacks gained
a shared invocation account and structured budget failures. The eight initial
real failures are preserved; ten ordinary failure/recovery/success scenarios
now pass. Ordinary JAX/TF with a unified graph-budget option explicitly reject
the unsupported cross-callback scope, instead of pretending query-local budgets
cover the whole compiled graph. Current moving-tree C3 focus is 100 passed;
new-source frozen/full gates are still pending. See the resource report.

Subsequent native QNode budgeting and returned-sample failure recovery are now
tested through the same executor. Fixed-geometry H2 has real Device/native/
ordinary Torch/Autograd and compiled JAX/TF numerical evidence, with explicit
query resource-limit status/recovery. This closes those specific earlier gaps,
not ordinary JAX/TF graph-wide resource ownership, multi-input compiled-query
support, all internal sampler partial-work observations or full core parity.

Final frozen-tree regression has now completed: main full 2334 passed/5 skipped/
3 public xfailed, alternate full 2332 passed/5 skipped/5 public xfailed,
SDK-free full 1742 passed/369 skipped, full 28-section matrix exit 0, actual full
coverage 89.86520579542997% with 68 exclusions unchanged. Independent JAX/TF
focuses pass 117/103 tests respectively; the main Torch/Autograd/C2A focus passes
17. Full receipts and concrete unresolved allocation/retained-graph ownership
gaps are in the resource report. Passing these gates does not close those gaps
or promote this partial checkpoint to complete C3/full SDK parity.
