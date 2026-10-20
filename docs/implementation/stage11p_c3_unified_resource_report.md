# Stage 11P-C3 Unified Resource Progress

Date: 2026-10-21. Starting committed main: `d05ad74` (C2A).
Status: IN_PROGRESS / PARTIAL, not ready for C3 acceptance or Capture.
Full independent Qiskit/PennyLane core replacement: ACTIVE / INCOMPLETE.

## Implemented Slices

Device derivative requests for native Circuit/Tape/QNode sources dispatch into
the existing ExecutionPlan/TransformedExecutionPlan, first derivatives, exact
second shifts or C2A second adjoint. Device-level Hessian/HVP tests prohibit
shift fallback for `second_adjoint`. Device VJP/JVP currently materialize the
first Jacobian; directional HVP does not materialize a quantum Hessian.
These are native computations, not quantum SDK lookups or execution.

UnifiedResourceLedger has child/ancestor constraints, preflight, atomic
reservations, observed owned-array values, idempotent release, cumulative
shots/tapes/charged work, conservative live memory peaks and bounded event
history with explicit omissions. Consumed work is not refunded on failure.
Tests distinguish sequential child temporaries from simultaneously retained
storage, active from consumed tapes, and released from consumed shots.
Request scopes use ContextVar, not global mutable device state. Second classical
traces retain direction/node reservations before their numerical allocations.
Second-adjoint forward/tangent/reverse/temporary state reservations are separate.

An actual 100-wire GHZ+RY(.3)+TransformProgram+QWC+MPS Device HVP test forbids
dense state, density and full MPS expansion. E=cos(.3), HVP=-cos(.3), bond=2,
zero truncation/shots, eight logical second-shift evaluations; separate Device
memory and unified memory boundary tests reject. Tensor storage is not SVD
allocator peak; the latter is explicitly unavailable. All reservations release.

## Preliminary Evidence

Initial corrected C3 contracts: 2 failed, exit 1, before production changes,
`/tmp/qb-stage11pc3-initial-red.log` and `.exit`. Existing local HVP and compiled
forward succeeded first; missing new APIs then failed. The contracts subsequently
passed with actual unified preflight and compiled HVP outcomes.

Resource lifecycle: 25 independent passing scenarios. Device API: 13 passing
scenarios. Failure/recovery: 13 passing scenarios including 64 shared RY gates
and actual second-adjoint resource categories. MPS integration: one passing
combined 100-wire execution/boundary scenario (not inflated into many scenarios).
JAX/TF query evidence is in the separate status report.

An initial moving-worktree regression of derivative_execution/qml/interfaces/
transforms/devices completed with 806 passed, 1 missing-installation-contract
skip, exit 0 (`/tmp/qb-stage11pc3-regression-initial.log` and `.exit`). This is
diagnostic only, not a final frozen-tree C3 gate. The suite evolved after that
collection. Independent focused SDK-free/JAX/TF runs also remain preliminary.
Final clean-tree full pytest, true full coverage, alternate full, complete matrix,
legal/privacy and exact tree receipts are pending. C2A's 2200 passing tests and
89.58936018334147% full coverage are historical, not C3 verification.

## Remaining Acceptance Work

- Complete preallocation ownership for source maps, first-order traces, all
  child/processor buffers, result payloads, samples/covariance, snapshots and
  MPS contraction/QR/SVD lifetimes. Current conservative reservations are not
  complete observations or an OS/BLAS/Python/framework allocator sandbox.
- Request-level charged planned work is not measured CPU/FLOP execution.
  Refine work/receipt semantics and compare actual native operations and calls.
- Complete ordinary JAX/TF graph forward/derivative shared accounting. Native
  QNode and eager Torch/Autograd now use the shared executor. A per-query
  pure callback is not a graph-wide shared live-memory or cumulative-work bound.
- Complete all internal partial-trajectory observability; returned complete
  native sample buffers and later-child failures are now accounted. A sampler
  raising without a complete buffer explicitly marks internal work unavailable.
- Resolve the concrete native framework allocation/graph-lifetime ownership
  gaps below before final C3 acceptance. Full clean-tree regression, matrix,
  examples and coverage gates have now completed, but do not close these gaps.
- Mixed main/alternate installed environments still have their pre-existing
  pyquafu/NumPy and WeasyPrint/tinycss2 pip-check conflicts; no dependency version
  was changed to hide them. This checkpoint is not complete environment parity.

## Frozen Progress Receipts (Not Final C3 Acceptance)

Progress tree: `c8780ec093ca9b011c858bb97d981111c0b826c3`, exported to
`/tmp/qb-stage11pc3-progress3.ZYTPqC`. Production subtree:
`8039645888297eb6bbecfa5939f3192787226f44`. This excludes user Router/Studio
changes. Production is byte-for-byte identical to progress2 tree
`1852c63170bcc67ea21d9f74d6de06ac38824d3e`, used for the broader regression.
Subsequent report updates and example license headers are not runtime changes.

| Actual gate | Result | Log and independent exit prefix under `/tmp/` |
| --- | --- | --- |
| Main installed C3 derivative_execution focus | 88 passed, exit 0 | `qb-stage11pc3-progress3-main` |
| SDK-free C3 focus | 61 passed, 4 missing-dependency skips, exit 0 | `qb-stage11pc3-progress3-sdkfree` |
| Independent JAX 0.12 focus | 70 passed, 2 missing-dependency skips, exit 0 | `qb-stage11pc3-progress3-jax012` |
| Independent TF 2.21 focus | 74 passed, 3 missing-dependency skips, exit 0 | `qb-stage11pc3-progress3-tf` |
| Alternate installed C3 focus | 86 passed, 2 observed public oracle xfails, exit 0 | `qb-stage11pc3-progress3-alternate` |
| Frozen qml/interfaces/transforms/devices regression | 758 passed, 1 missing-installation-contract skip, exit 0 | `qb-stage11pc3-progress2-regression` |
| Frozen legal and compileall | 4 passed; compileall exit 0 | progress2 direct tool receipts |

Focused coverage covers new request/result/context/ledger/limit modules 100%,
planning 194/204, status 45/46, Device execution 87/94, common framework maps
39/39, JAX query 69/76 and TF query 97/100. The **whole-package number from
this focused run is 26%, not full-suite coverage**; it is not comparable to the
historical true-full 89.58936018334147% baseline. No exclusions were added.
An earlier attempt to pass nested package names as coverage sources failed
collection with a repeated NumPy import error (exit 2); it is preserved at
`qb-stage11pc3-focus-coverage`. Using the normal whole-package source on the
clean frozen tree succeeded; no environment or production code was changed
to hide that failed invocation.

Eight additional independent mathematical scenarios check nonlinear mixed
partials, coefficient curvature, complex Hermitian/phase handling, variance,
ordered probabilities, controlled frequencies, QWC identity processing and a
seeded linear finite-shot HVP. The latter records 32768 actually sampled native
shots and eight independent seeds; it is an estimate, not a hardware run or an
HVP uncertainty bound. The identity zero-tape assertion requires the actual QWC
transform, not the default separate-term processor; its initial test setup was
corrected without changing native runtime behavior.

Four public PennyLane Autograd problems match numerically in main 0.44.1.
Two fail in alternate 0.42.3 with the specifically observed complex
NotImplementedType TypeError. They remain narrow, explicit xfails, not matching
passes. An additional test genuinely evaluates public Torch Hessians for those
same two problems in both versions; these are additional oracles, not two new
independent mathematical scenarios. No upstream implementation/test source was
used as native code. Failed and corrected oracle logs are retained.

Five executable examples now exist: native Device HVP, unified budget failure,
JAX HVP status, TF HVP status and the 100-wire MPS budget. Native scalar HVP is
-0.3821345956502423 at theta=.3, direction=.4; MPS energy/HVP are respectively
0.955336489125606 and -0.955336489125606, with a 154384-byte conservative
reserved peak (not observed allocator peak). Both framework examples report
success, invalid-input, success for .3/NaN/.7. No Studio/frontend work is added.

No C3 commit/push or new-SHA CI is claimed yet. Ordinary fresh fetch previously
failed; remote remains stale/unverified. No authentication/TLS changes, force/
reset/rebase/amend, tags/releases, vendor/package/environment trees, Studio/Router
user changes, cloud/hardware or token operations belong to this work.

## Subsequent Ordinary Framework Increment

The complete next ChatGPT reply confirms the original C3 scope and prioritizes
ordinary Torch/Autograd graph budgets, array ownership, actual partial-shot
failure and one-build H2/all-framework receipts, without entering Capture.
It specifically forbids mutable global ledgers captured by JAX/TF graphs and
false strict RSS claims. All original acceptance requirements remain open until
actually evidenced.

Eight ordinary Torch/Autograd contracts first failed in 0.69s, exit 1
(`/tmp/qb-stage11pc3-ordinary-initial-red.log` and `.exit`): the new budget was
silently ignored by existing forward/backward/double-backward callbacks. The
native plan adapter now shares one invocation ledger across these eager
callbacks, using the existing Device executor and actual first/second plans,
not a second quantum engine. It exposes raw Jacobian/second arrays by reference
for the existing framework VJP rules, without recomputing quantum derivatives.

All eight failure/recovery contracts then passed; two additional successful
second-graph tests verify HVP=-.4*cos(.3) and cumulative 11 logical tape/work
units across forward/first/second callbacks, with released numerical storage.
Ordinary JAX/TF calls with the new unified option now explicitly reject the
unimplemented cross-callback shared account rather than silently ignoring it.
Their existing ordinary graphs with no unified option are unchanged; explicit
per-query status APIs remain available. This is PARTIAL shared-graph support,
not full four-framework unified accounting.

Current moving-tree derivative_execution focus: 100 passed in 7.00s, exit 0
(`/tmp/qb-stage11pc3-ordinary-focus.log` and `.exit`). Compileall and diff check
also pass. This increment changes production after the 88-test frozen progress
tree above; those prior frozen receipts are historical, not final validation of
this new source. Fresh broad/cross-environment/full gates remain required.

## Sample, Payload And Native QNode Increment

Two genuine sampling-accounting reds observed zero consumed shots after 32
native samples had completed (`qb-stage11pc3-partial-shots-red`, exit 1).
Sampling reservations now precede native dispatch and completed buffers consume
their reservation immediately, before covariance/metadata processing can fail.
Tests cover a legitimate peer reservation between children, post-sampling
statistics failure, released reservations, stopped later children and recovery.
An internally failed sampler with no returned buffer records the missing
observation explicitly, not an invented actual trajectory count.

QWC retained arrays/bitstrings and temporary decoding/covariance work have
separate scopes. Metadata numerical lists and copied execution receipts reserve
before allocation/copy; copies are distinct retained payload, while sequential
temporary work releases. These are logical numerical/text bytes, not Python
container/object memory or strict RSS. Tests exercise analytic versus sampled
covariance, one-shot semantics, rejection before sampling and seeded shot-vector
HVPs with None/uniform/weighted QWC allocation. Preflight estimates are not later
retained-receipt peaks; the 100-wire boundary test now explicitly tests the
initial estimate boundary, with runtime payload limits tested separately.

Five native QNode contracts first failed (`qb-stage11pc3-native-qnode-red`,
5 failed, exit 1): forward/Jacobian/Hessian/HVP silently ignored unified limits,
and selected/keyword derivatives had no receipt. Native calls now use the same
Device executor, retaining their existing input selection/layout. First-order
parameter nodes and classical source maps reserve before owned allocations;
their conservative lifetimes are request-scoped, not exact garbage-collector
lifetimes. Default calls without this option retain their existing behavior.

Fixed H2 geometry tests count one AO integral/RHF/fermionic/JW Hamiltonian build,
then prohibit rebuilding it during multiple Device/native-QNode HVP directions,
ordinary Torch/Autograd double backward, JAX compiled HVP and TF nested tapes.
Compiled query budget failure/recovery is real. All five tests pass in main
(`qb-stage11pc3-h2-corrected`, 11.16s, exit 0). The initial test incorrectly
forbade *all* JW mappings, including geometry-independent ansatz generators;
that test spy was corrected, not treated as a chemistry runtime defect.
JAX/TF query statuses are verified, but graph-wide resource receipts are not
claimed for their ordinary compiled callbacks.

Latest moving-source derivative/C2A focus: 155 passed in 15.83s, exit 0
(`qb-stage11pc3-maps-focus`). Four additional executable-example contracts pass
in 3.48s (`qb-stage11pc3-example-focus`), covering all five examples. These
observations precede the next clean-tree full gates; C3 remains PARTIAL.

The subsequent complete ChatGPT reply retains the original scope, requires the
three full environments and full matrix first, and adds same-compiled-graph
valid/budget-failure/valid plus preallocation spies. These now have actual JAX/TF
runtime tests (x*x's input-dependent shifted work, no mutable global ledger),
QWC covariance and source/Jacobian reservation-order spies. A first draft missed
one test import (NameError, not a production failure); the corrected 47-test
focus passed in 5.48s. Reused Torch backward/Autograd pullbacks preserve spent
work; fresh invocations recover. KeyboardInterrupt releases active reservations
without refunding already charged attempted work.

An actual additional red found managed `save_statevector` derivative requests
returning success despite unowned snapshot results (`qb-stage11pc3-repeat-cancel`,
27 passed/1 failed, exit 1). Managed save/set/snapshot instructions now explicitly
reject before native execution until their derivative/result ownership is
implemented. Snapshot-reject/native-QNode focus: 21 passed, exit 0
(`qb-stage11pc3-snapshot-reject`). This is an honest unsupported path, not a
claim that snapshot differentiation has been implemented. It changes production
after the first validation export and requires fresh final gates.

Normal fresh fetch subsequently succeeded, confirming cached remote main
`45fe338fc0f02de9c19e0af89723755952e5fc98` is an ancestor of local `d05ad74`.
One ordinary push of the previously committed, already-tested chain was rejected
by GitHub because the OAuth App lacks `workflow` scope for historical workflow
updates (`qb-stage11pc3-push-validated-c2a`, exit 1). Remote was not updated.
No retry/bypass, workflow deletion, credential/token access or authentication/
TLS change was performed. `gh` is installed but not authenticated (exit 4);
there is no exact-new-SHA CI evidence. Owner must resolve normal authorization.

## Callable Contract And Open Boundaries

| Surface | Actual implemented contract | Important boundary |
| --- | --- | --- |
| Native Device | Circuit/Tape/QNode requests: value, Jacobian, VJP, JVP, Hessian and HVP; compute and execute-and-compute variants | Circuit requests need an observable; order/kind/input layouts validate, unsupported paths do not substitute another SDK |
| Native QNode | Explicit unified limits cover value and selected positional/keyword first/second derivatives through the shared executor | This option is not a universal sandbox for user Python, arbitrary processors or external allocation |
| Statevector | Native analytic first/second adjoint and parameter shifts | Second adjoint is opt-in, noiseless/unitary/analytic; best second order remains shift |
| Density/MPS | Separate native engines and supported shifts, including directional second rules | No mixed/MPS second-adjoint claim, no dense fallback, no arbitrary-entanglement efficiency guarantee |
| Tableau | Continuous derivative capability rejects | No hidden conversion to Statevector |
| Torch/Autograd | Actual CPU first/second graphs share invocation consumption; reused backward fails when spent, fresh invocation recovers | Framework graph allocations and retained external tensors are not a native memory bound; third/higher orders reject |
| JAX | Explicit CPU Jacobian/Hessian/HVP data plus runtime status; eager/JIT/sequential VMAP | Single static floating-array input; explicit query payloads do not add extra derivative rules; ordinary unified graph scope rejects |
| TensorFlow | Explicit CPU value/Jacobian/VJP/Hessian/HVP plus runtime status; true GradientTape and tf.function | Same argument/static-host restrictions; no XLA/distribution/export claim; ordinary unified graph scope rejects |
| Products | Native VJP/JVP contract a first Jacobian; HVP streams quantum second directions | First Jacobians and classical source maps can still be dense |
| Shots | Completed returned native buffers consume before downstream processing; later failure cannot refund them | Internal failed samplers without complete buffers have unavailable partial work, not a fabricated actual count |
| Receipts | Estimated/reserved/observed/released/high-water logical storage and cumulative work/shots/tapes | Logical executions are not simulator method-call counts; charged planned work is not measured CPU FLOPs |
| Save/set snapshots | Managed derivative requests reject explicitly | Dedicated simulator snapshot execution exists separately, but derivative snapshot ownership is not implemented |

In particular, this checkpoint does **not** claim all native allocation sites
are covered before allocation. The common framework source-map composition
currently creates some native matrix products before its new reservation, and
the ordinary framework source-constant/selection closures predate the scoped
callback. Complete ownership of those matrices, contraction temporaries and
graph-lifetime retained native arrays remains a concrete implementation gap,
not something an `unavailable` marker turns into a tested strict budget.
QWC and direct native source-map allocation-order spies verify their specific
sites only. All green gates below are regression evidence, not closure of this
gap or acceptance of complete C3/full core parity.

Final production/test freeze for the next gates:
`115a7b60030613af123217bb67d5951c25f2856d`, exported to
`/tmp/qb-stage11pc3-final.U94e6a`; production subtree
`0bcbaadddf6c2f6ad13228d907bb848702bcf3e1`. The earlier full coverage gate used
`ab02064be2b46a842ca78e1b9e78a0feb9b74f0c` (2326 passed, 5 skipped, 3 public
xfails, exit 0, 24932/27744 = 89.86447520184545%, 68 exclusions). The production
difference is the explicit save/set snapshot rejection; newer tests also cover
reused graphs, cancellation, allocation order and runtime-input budget recovery.
That earlier full coverage is therefore **not** final-source verification.

Final-tree gates completed so far: SDK-free full 1742 passed/369 skipped, exit 0;
alternate installed full 2332 passed/5 skipped/5 public xfailed, exit 0;
independent JAX 0.12 focus 117 passed/21 absent-framework skipped, exit 0;
independent TF focus 103 passed/23 absent-framework skipped, exit 0;
Torch/Autograd/C2A focus 17 passed, exit 0. Compileall and legal 4 tests pass.
Each gate has `/tmp/qb-stage11pc3-final-<label>.log` and an independent `.exit`.
Broad focused regression and the complete main matrix/true coverage are still
running at this report update; no final C3 commit or acceptance is claimed.

## Completed Final-Tree Regression Receipts

The running gates described above subsequently finished on the same frozen
production/test source. Working-tree updates after the freeze are report-only;
an explicit temporary-index comparison confirms no production, test or example
source difference. This is a tested **partial implementation checkpoint**, not
final C3 acceptance. No Capture/D implementation was started.

| Gate on `115a7b60030613af123217bb67d5951c25f2856d` | Actual result | Independent log/exit prefix under `/tmp/` |
| --- | --- | --- |
| SDK-free full | 1742 passed, 369 conditional/missing-dependency skipped; exit 0 | `qb-stage11pc3-final-sdkfree` |
| Main installed full, core-only matrix section | 2334 passed, 5 skipped, 3 public xfailed; exit 0 | `qb-stage11pc3-final-matrix` |
| Main installed repeated full, dev section | Same counts; exit 0 | same full matrix log |
| True full coverage suite | Same counts; 24934/27746 statements = 89.86520579542997%; 68 exclusions | matrix log and `qb-stage11pc3-final-coverage.json` |
| Alternate installed full | 2332 passed, 5 skipped, 5 public xfailed; exit 0 | `qb-stage11pc3-final-alternate` |
| Independent JAX 0.12 CPU focus, x64 enabled and explicit float32 examples | 117 passed, 21 absent-framework skipped; exit 0 | `qb-stage11pc3-final-jax012` |
| Independent TF 2.21 CPU focus | 103 passed, 23 absent-framework skipped; exit 0 | `qb-stage11pc3-final-tf` |
| Torch/Autograd/C2A focus | 17 passed; exit 0 | `qb-stage11pc3-final-torch-autograd` |
| Derivative/interfaces/qml/transforms/devices/chemistry/compiler/serialization/Aer focus | 1328 passed, 1 conditional skip; exit 0 | `qb-stage11pc3-final-focused` |
| Complete unmodified 28-section local matrix | All 28 sections reached; shell exit 0 | `qb-stage11pc3-final-matrix` |
| Compileall; legal | exit 0; 4 legal tests passed | `qb-stage11pc3-final-compile`, `qb-stage11pc3-final-legal` |
| Privacy/no-cloud/no-token/no-vendor focus | 19 passed; exit 0 | `qb-stage11pc3-final-privacy` |

The unrounded coverage gain from C2A's 89.58936018334147% is approximately
0.2758456119 percentage points. No exclusion/configuration change was made.
Coverage's rounded display of 90% is not the exact percentage. New modules
include request/result/status/ledger/limits and shared framework maps at 100%,
planning 203/212, Device execution 92/98, native QNode bridge 61/68, resource
context 75/78, ordinary eager bridge 64/66, JAX query 69/76 and TF query 97/100.
Line coverage does not establish complete SDK API or resource ownership parity.

Executed matrix subsets include Qiskit core 5, PennyLane adapter 9, Aer 146,
Nature 21, Algorithms 26, Runtime offline adapter 5, PennyLane-full subset 44,
MQT compatibility 15, TorchQuantum compatibility 17, QOS-UQCI compatibility 11,
Quafu offline compatibility 15, Benchpress compatibility 19, existing Studio
backend API 33, ecosystem inventory/contracts 27, chemistry core 5, chemistry
extra 30, Nature-P2 5, algorithms extra 10 and OpenFermion 1 passing test.
These subset labels do not imply complete library implementation, production
support, successful cloud jobs or new frontend work. Runtime/Quafu/QOS offline
checks are not real hardware evidence.

Finance, Optimization, Machine Learning, Dynamics, Metal, Experiments and Addons
installed-environment matrix lanes explicitly report unavailable/not executed.
The full-suite 5 skips remain conditional availability/dependency contracts,
including incompatible pyquafu NumPy ranges; the public xfails are real upstream
oracle limitations, not native numerical passes. The two additional alternate
PennyLane 0.42.3 complex-Autograd xfails retain their specific observed signatures;
public Torch Hessian oracles for those same problems also run successfully.

Version receipts (`qb-stage11pc3-validation-<env>-versions-corrected`) record
Python 3.12.6 throughout: main NumPy 2.4.6/Qiskit 2.4.1/PennyLane 0.44.1/
JAX 0.7.1/Autograd 1.8.0; alternate Qiskit 2.6.0/PennyLane 0.42.3/JAX 0.6.2/
Autograd 1.9.1; both use Torch 2.12.0 and TF 2.21.0. SDK-free NumPy 2.5.4 has
none of those SDKs/frameworks. Independent JAX uses 0.12 with NumPy 2.5.4;
independent TF uses 2.21.0 with NumPy 2.5.4. No environments were installed or
repaired. Earlier failed shell-quoted version invocations are retained separately.

Pip check: SDK-free, independent JAX and independent TF exit 0. Main and alternate
exit 1 with the same pre-existing conflicts: pyquafu 0.4.5 requires NumPy <2
but has 2.4.6; WeasyPrint 68.1 requires tinycss2 >=1.5 but has 1.4.0. Logs are
`qb-stage11pc3-validation-{main,alternate,sdkfree}-pip` and
`qb-stage11pc3-final-{jax012,tf}-pip`. They are not mislabeled as passing checks.

All source/test history remains intact. The local checkpoint may be committed
with the tested source and these report-only receipts; its final commit SHA is
provided by the actual Git command/chat receipt rather than embedding a
self-referential SHA in this file. Remote publication remains blocked by the
observed OAuth workflow-scope denial. There is no new-SHA CI claim and no
additional push attempt. Full Qiskit/PennyLane replacement remains ACTIVE /
INCOMPLETE; the next work is the concrete remaining C3 allocation/lifetime gaps,
not D/Capture or Studio.
