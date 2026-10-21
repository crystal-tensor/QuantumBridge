# Stage 11P-C3-R1 Allocation Audit

## Task 3E Scoped Contracts

Development red/green receipts are in the ownership report. These contracts
apply inside an active ResourceScope; they do not certify unrelated methods.

| Site | Prior admission / storage | Lifetime / remaining boundary |
| --- | --- | --- |
| Named gates and U/controlled helpers | Actual complex destinations; controlled target/output and DCX input/product coexistence preflight | Output root leases; matching metadata dtype borrows without invented charge |
| Stacked Kraus and noise factories | Base numeric ndarray views or explicit builtin groups; all genuine defensive copies admitted together | Distinct roots and views; opaque arbitrary iterators reject before dispatch |
| QuantumError algebra/canonicalization | Product groups, validation copies/arena, one Choi, eigenvalues/vectors and reconstructed operators | Actual retained roots; hidden LAPACK/iterator workspace unavailable |
| Six channel representations | Owned dtype/copy/basis/Choi/SuperOp destinations, rectangular/generalized Kraus reconstruction and stack outputs | Conversion and arithmetic output views retain full roots; no upstream quantum engine |
| Integer matrix power | Existing owned contractions for every repeated-squaring product; admitted inverse output for negative powers | No opaque matrix_power ndarray intermediates; internal inverse LAPACK workspace unavailable |
| Dense evolution/reset | Numeric input conversion, conjugate/reshape copies, destination contractions, projection and reset buffers | Full output root retained; unrelated sample/measure/copy helpers still open |
| Dynamic noise / Aer linear and ensemble maps | Whole weighted noise group, embedded operator/SuperOp products and analytic density contributions/accumulator | Native Result/view lease; incomplete shots do not become a success Result |
| Explicit dense tableau request | Final dense dimension/bytes preflight before Clifford synthesis | Internal tableau bool arrays and synthesis scratch remain unclosed, not certified by preflight |

R1/C3 remains PARTIAL. Final Task 3E tree 66b10f4 now has fresh three-environment
FULL, independent framework and actual complete 28-section matrix exits 0;
both full coverage exports record 90.17352569642976%, excluded 68. Seven
unavailable optional matrix subsets are not executed, not passed. See the
ownership report for receipts, pip conflicts and exact remaining native sites.
The older Task 3D gates below are historical, not evidence for newer code.

## Task 3D Scoped Contracts

The current ownership report records actual red/green receipts. These rows do
not certify unlisted arrays, quantum feature parity or strict process RSS.

| Site | Prior admission and output | Lifetime/remaining boundary |
| --- | --- | --- |
| Gate and square Kraus validation | `33*d` arena: two complex128 columns plus bool mask; scalar Gram entries, unchanged tolerances | No full Gram/identity matrix; vdot/scalar/iterator internals unavailable |
| Kraus defensive operator copies | All `16*k*d*d` output bytes and validation arena admitted before first factory | Independent output roots; views retain leases; failed unused reservations release |
| CP/TP representation validation | Native Choi/basis products owned, Hermitian/eigenvalue outputs reserved before eigvalsh; scalar TP trace | All six native representations covered; arbitrary channel constructors/algebra remain outside this audit; LAPACK internals unavailable |
| Pauli CSR | Direct signed permutation, three separate data/index/pointer roots; group admission before NumPy/SciPy | No dense fallback, copy=False borrowing verified; SciPy internals unavailable |
| Dense snapshot storage | Owned production/aggregation/normalization buffers, candidate cell before commit | Failure preserves old cells/groups/counters; encoded public Result schema unchanged; Python JSON heap unavailable |
| Snapshot density/moments/amplitudes | Controlled tensor reshape/contraction or scalar Pauli expectation; MPS selection non-dense | Unrelated state engine and tableau statevector expansion remain open, not mislabeled controlled |

## Task 3C Next Allocation Closure

The paragraphs below are the initial audit. Current runtime changes and real
red/green evidence now appear in the ownership report; they do not certify
all native array allocation sites or Python process-memory control.

After the Task 3B results were sent to the authorized ChatGPT conversation,
its completed reply continued Observable/JSON allocation closure. This is
report-based coordination, not independent audit or R1 acceptance. The next
runtime work has not started; no Task 3C red or fix is claimed here.

Source inspection identifies these actual boundaries for the next red tests:

- `utils/math.py::observable_matrix`: Hamiltonian output zeros, coefficient
  products, Pauli Kronecker outputs and fallback object-to-matrix/dtype copies
  can precede unified reservations. Existing MPS Pauli-native paths must remain
  native; explicit dense requests still need dimension/dtype/byte preflight.
- `operators/pauli.py::to_matrix`: each Kronecker step owns a new complex root;
  its intermediate coexistence is not yet a controlled allocation contract.
- `ir/qb_ir.py::matrix_from_ir`: real/imag asarray, astype, scalar multiplication
  and addition can allocate multiple simultaneous buffers before a caller's
  guard. `_matrix_to_ir` calls that converter before making Python lists.
- `MatrixProductState.to_dict/from_dict`, `Result.from_json/data` and snapshot
  decode need separate native array and JSON/Python-container bounds. Direct
  tolist on an existing strided view is not evidence of an ndarray copy: a new
  red must demonstrate a real conversion/copy boundary, not invent one.

Next order: actual overbudget observable reds, then strided export/import reds,
scoped fixes through existing resource/codec APIs, then final frozen-source
three-environment FULL/coverage/28-section gates. Keep the current Task 3B
source receipts separate. No new runtime change invalidates them in this audit.

### Current Scoped Allocation Contracts

| Site | Preallocation/known payload | Owner and release | Remaining boundary |
| --- | --- | --- | --- |
| Native dense Pauli sum | One complex128 `(2**n,2**n)` destination, `16*4**n` bytes, before filling a signed basis permutation; no Kronecker intermediates | Actual output root lease, retained by views | Sparse CSR conversion and unrelated operator constructors are not certified |
| Managed numeric/IR conversion | Shape/real-component checks before one admitted destination; existing matching-dtype ndarray is borrowed; Python numeric leaves fill the destination directly | Each true new complex/real root retains its own lease; real/imag views do not charge again | Opaque object/string conversion protocols explicitly reject; internal NumPy iterator workspace is unavailable |
| Hermitian observable validation | One uint8 arena of `33*N` bytes for N matrix entries: complex128 difference, two float64 arrays and bool mask | All scratch views retain one arena root; no new full matrix conjugate/allclose output | Scalar/iterator allocator peaks remain unavailable; gate-unitarity and general CPTP validators are separate sites |
| Result state/density import | One complex128 output for the full vector or rectangular matrix, before filling existing scalar real/imag records | User views retain the actual root after Result deletion | JSON native MPS snapshot-map reconstruction remains explicitly unavailable |
| Saved-array decode | One complex128 or float64 output plus a separately admitted finite-validation bool mask | Numeric output escapes with its root lease; mask dies after validation | Other non-MPS snapshot aggregation buffers are not all individually audited |
| Existing JSON wrappers | UTF-8 bytes before decode; decoded nodes/depth/elements/labels before numerical conversion; output chunks checked before final join | Numerical imports use existing root leases; logical transport bounds are not Python-object leases | Decoder/list/string/allocator heap is explicitly unavailable, not claimed strict RSS |
| MPS tolist/export | Existing strided complex tensors produce Python real/imag lists without an ndarray copy; exported logical scalar count checked first | Original tensor root unchanged; no invented new ndarray charge | Logical exported scalar bytes are not exact JSON text size or Python heap |

JSON physical depth is separately bounded by `max_json_depth` (256 by default),
not the existing QASM/control-flow `max_nesting_depth` (32). Internal compiler
pass comparison preserves its original canonical JSON normalization directly
over structured IR, without invoking external transport policy. It still
detects AnalysisPass mutation, including float/int representation changes;
its Python comparison strings remain explicitly unavailable heap accounting.

## Task 3B Initial Snapshot Ownership Audit

This is the pre-fix snapshot audit, not acceptance. The foundation tree above
does not own native snapshots: `observe` serializes MPS tensors into Python
lists; cells deep-copy those lists; metadata serializes/deep-copies them again.
`Result.data()` decodes that transport structure, not a native MPS instance.
Do not silently replace its public dict/list schema with another object type.

| Boundary | Existing storage/copy | Required ownership contract |
| --- | --- | --- |
| SaveMPS / SaveState in `SnapshotContext.observe` | `state.to_dict()` creates numeric Python containers, not a retained tensor copy | Copy native MPS roots before later gates can mutate trajectory state; reserve every real tensor copy before allocation; count pershot copies cumulatively |
| Context cell to analytic ExecutionRecords / shot Result | Only encoded metadata currently crosses this boundary | Transfer references to the already charged native snapshots, without a second array copy or a scope-exit release; preserve label/group/pershot nesting |
| Device / simulator / Backend / Job | Synchronous Job retains executor and Result; native device final MPS already has root leases | Results must remain valid independently of Job/context; shared references must not double-charge a root |
| `Result.data()` | Existing defensive serialized dict/list structure; other snapshot kinds may decode ndarrays | Preserve existing format and complex values. Serialized Python heap is distinct from observed ndarray bytes; arbitrary decode/JSON allocations remain a separate open audit |
| Native labeled MPS extraction | Existing `matrix_product_state()` only copies final state, not labeled intermediate saves | Extend this existing accessor with an optional label; returned nested MPS copies reserve through the current or actual source account, and final tensor views keep real roots alive |
| JSON export / import | Existing schema stores encoded MPS dictionaries and final-state MPS separately | Keep round-trip transport compatible; native export uses no dense statevector; imported data must not falsely claim an existing native lease |
| Snapshot failure | Context/job exception can retain partial state in debugging tracebacks | No success Result for an incomplete collection; release temporary storage when actual exception owners disappear; status paths must detach traces explicitly |

For a native snapshot with actual distinct root bytes `B`, a genuine defensive
copy allocates one complex tensor payload of the corresponding shapes, not a
new full Hilbert-space vector. Old trajectory roots and new snapshot roots may
coexist. A view must charge its full backing root, not just the visible slice.
Snapshot JSON byte limits measure transport size; they do not measure Python
container headers, allocator peaks or total process RSS. Those remain unavailable.

## Current MPS Foundation Update

Two real initial MPS reds precede these Task 3 fixes, at
`/tmp/qb-stage11pc3r1-mps-initial-red.log/.exit`. The ownership report records
their meaning, regressions and unverified requirements. The baseline site table
below is historical, not a statement that every row is closed.

Known numeric MPS arrays use existing ResourceScope/ledger and root leases.
QR/SVD outputs reserve together before linalg; contracted outputs and reshape/
packing copies reserve before NumPy. Schmidt/statistics/gate/normalization/
reduction buffers have owners. Weak root/account metadata is not a global
budget. Borrowed mutable tensors are adopted by real copies into an unrelated
active account. Raw MPS Result/view lifetime is tested, not full snapshots.

The old `12*stored` common tensor allowance is not also held during explicit
allocations. Full estimates remain conservative admission guards; execution
keeps the old conservative external allowance. Hidden LAPACK/BLAS/iterator
workspace remains unavailable. Public gate failure restores the prior state;
QR commits each complete center movement and split commits a complete region.
No numerical QR/SVD routine is replaced. Public API shape references, not
implementation/test source ports:
https://numpy.org/doc/stable/reference/generated/numpy.linalg.qr.html ,
https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html ,
https://numpy.org/doc/stable/reference/generated/numpy.tensordot.html .

Serialized snapshots, Job/context and all failure/trajectory requirements stay
open. Generic observable/IR conversions and internal validation workspace are
not a proven whole-process bound. Final R1 gates must use the final Task 3 tree.

## Task 1 And Task 2 Update

The current working tree adds controlled foreign-copy rejection, ordinary TF
gradient graph ownership and strided flatten/reconstruction leases. Exact red
and green receipts, rejected TF prototypes and remaining limits are recorded
at the top of the [ownership report](stage11p_c3_r1_resource_ownership_report.md).
The ownership report now records fresh three-environment full tests and
independent framework gates for tree `9d6bd5c083a6bc706419e093c9112955c51cda76`.
The older coverage/matrix table below is historical, not evidence for new runtime.

`flatten_tree` uses one reserved contiguous destination; strided sources are
copied into destination-shaped views, without per-leaf astype/concatenate.
`unflatten_tree` uses a shape-only view attempt, then an independently reserved
copy only if necessary. NumPy >=2.1 uses reshape(copy=False), avoiding 2.5's
shape-assignment deprecation. Older versions retain a shape-only fallback;
that branch is unit-tested, not a real NumPy 1.x runtime gate.
Public references: https://numpy.org/doc/stable/reference/generated/numpy.copyto.html
and https://numpy.org/doc/stable/reference/generated/numpy.reshape.html .
These contracts bound explicit owned ndarray data, not unexposed iterator or
allocator workspace. Supported argument layouts use slices, and ordinary
selected Jacobians already copy into explicit reserved columns. Internal
reordered/repeated integer selection now has its own prior reservation, with
two actual initial red tests. Arbitrary indexing and the MPS QR/SVD/contraction
sites remain audit boundaries.

No QR/SVD site was changed in this slice. Existing MPS `_guard` and executor
aggregate reservations do not constitute a site-by-site proof of temporaries,
LAPACK allocator workspace, or persistent tensor lifetimes.

## Task 3 Initial Source Inventory

This is the initial source audit, not a measured peak or completed Task 3.
The update above records later real reds/fixes; initial table entries describe
baseline gaps. Keep the Task 1/2 frozen-source receipts separate from later
Task 3 implementation and final gates.

Let `T_i=(D_i,2,D_(i+1))`, `B=sum(root.nbytes)` over distinct actual tensor
storage roots, and `b(dtype)=dtype.itemsize`. The current MPS constructor casts
to complex128, so its present complex buffers use 16 bytes per element and
SVD singular values use float64/8. Helpers must still infer actual result dtypes.
Logical tensor view sizes are not a substitute for actual root storage bytes.

| Actual site | Shapes / known owned bytes | Owner and live interval | Current gap / next preallocation proof |
| --- | --- | --- | --- |
| `information/matrix_product_state.py`: constructor, zero, copy, tensors, from_dict | Numeric conversion plus each `T_i` copy; complex data `16*sum(prod(T_i))` per genuine copy | Caller inputs, constructor copies and canonicalized replacements can coexist; property copies escape to callers | `_guard` follows initial asarray conversion; known copies and returned roots need prior leases, partial-failure cleanup and no duplicate charge for aliases |
| Constructor / `_move_center` QR | Matrix `(m,n)`, `k=min(m,n)`; Q `(m,k)`, R `(k,n)`; complex output `16*k*(m+n)` | Old site/neighbor, optional reshape-copy, Q/R and updated neighbor contraction overlap; Q views can survive in state | Reserve known input copies and Q/R before QR; infer new neighbor contraction shape; internal LAPACK workspace remains unavailable unless separately justified |
| `_block_gate` local contraction | Two-site block `(a,2,2,b)`, `64*a*b` complex bytes; general width `16*a*2**w*b` | Old tensors, contracted block, gate-action output and normalized block may coexist | Existing aggregate/local estimates are not individual buffer leases; reject before tensordot/einsum or necessary reshape-copy |
| `_split` SVD | Matrix `(m,n)`, `k=min(m,n)`; U `(m,k)`, S `(k,)`, Vh `(k,n)`; `16*k*(m+n)+8*k` returned bytes | Input block/matrix, old tensors, U/S/Vh, truncation statistics and next block overlap | Reserve outputs before SVD; inspect strided input copying; `U[:,:rank]` may keep the full U root, not just the view's bytes |
| `_split` rank/statistics/update | S-square/tails/cumsum real arrays up to `k`; next complex block `(rank,n)` and its normalization | Temporary arrays until rank/update completes; left tensor can retain a U view while right block is built | Bound every known statistics/product copy; transfer persistent roots only after complete successful replacement; preserve truncation math |
| `apply` nonadjacent wires | Forward SWAP chain, target gate and reversed SWAP chain repeat local shapes above | Intermediate state roots change per operation; old/new local roots can overlap | Reuse the existing gate engine, not a second MPS implementation; preserve cumulative work and peak active accounting rather than summing sequential buffers |
| probabilities / reduced_density_matrix / expectation_pauli | Environments scale with bond-square times `2**kept` or `4**kept`; output/conjugate/transpose-reshape copies have actual dtype sizes | Prior environment, conjugate input, new contraction environment and final result may overlap | Audit einsum intermediate planning; lease returned numerical roots; unknown optimizer/allocator workspace is not zero |
| Device `_initial`, `_branches`, `_trajectories`, `_kraus_choices` | Initial property copies plus constructor copies; prefix + branch copies; local density/Kraus products and trajectory outputs | Prefix lives across shots; analytic branches and selected/readout copies can coexist | Local `_guard_branches` and common executor aggregate reservation are not per-root ownership; no refund of spent shots/work on failure |
| `execution/control_flow_engine.py`: adapter project/channel, reset and dynamic branches | Projected state copies, Kraus candidates, local reduced states; reset may add X gate work | Source state plus live candidate/child branches; unreachable outcome copies must be released | Keep shared source versus actual child copies separate; preserve existing branch-limit/error/shot semantics |
| `simulator/snapshots.py`: observe/replace/metadata | MPS to_dict/from_dict numeric-list conversions and deepcopy; optional statevector/reduced outputs | Snapshot/context/backend Result can outlive Device; transport/Python storage is distinct from tensor ndarray roots | Existing snapshot-byte limit is not an ndarray lifetime proof; managed derivative simulator instructions remain explicitly Unsupported, not silently reopened |
| `providers/matrix_product_state_backend.py` and common backend | Delegates to existing Device; configured initial state and returned Results can retain roots | Configuration/source, Job/Result and external user views have separate lifetimes | Do not introduce a parallel backend execution path; audit ownership through delegated Results and snapshots |
| Native gradient / streamed HVP through `ExecutionPlan.evaluate` | Existing source maps/results plus the active MPS execution buffers above | Common `native_device_workspace` surrounds one evaluation; HVP streams native evaluations, not a full Hessian | Replace unjustified aggregate assumptions with explicit contracts without double-charging the same roots; preserve 100-wire no-dense and shared-parameter tests |

Next required evidence: an actual low-cap two-site contraction red before the
NumPy call, an actual low-cap SVD-output coexistence red, then scoped fixes.
Further QR/strided/failed-decomposition, trajectory/reset, retained-view/Result,
repeat/concurrent request and 100-wire regressions follow. Do not claim these
rows are closed based on source inspection or the older aggregate estimates.

## Persistent Construction And Resident Admission Update

The latest slice separates a kernel's known ndarray construction pool from a
callback's admission account. Exact numeric ndarray copies reserve in the pool
before allocation; readonly roots and their surviving views keep those leases.
One construction memo preserves repeated object identities, while distinct input
views cause genuine separate copies. Tested foreign plain-object custom copy
protocols and ndarray subclasses are rejected by the pool; arbitrary container,
closure, reduction and slotted-object protocols remain to be audited. This is not a bound on arbitrary closures,
Python containers, framework or BLAS/LAPACK allocators.

Per-request resident admission charges existing roots once per request token,
not as a new allocation or an observed buffer. Independent concurrent requests
charge separately through shared parent caps. Releasing admission never refunds
work/shots and does not release the persistent physical owner. Receipts expose
persistent-owned bytes separately from resident charges and conservative new
allocation reservations; the last are not measured allocator peaks.

Actual pre-fix failures found mutable caller-array aliasing and repeated kernel
snapshots during classical JAX/TF mapping (four and two snapshots respectively).
The public compiled-query tests now verify one snapshot, changed inputs, runtime
low-cap status 3 before quantum work, shared callable owners, a surviving TF
ConcreteFunction, eventual final release and two concurrent native HVP requests.
TF callback registration retains a weak callback reference; a weak graph-identity
table owns the payload. The status-gradient rejection is registered without a
per-call closure over output tensors/graphs. Graph collection ownership was
tried and rejected after an actual public TF lifetime regression remained red.

This is intermediate progress, not final R1 acceptance. Ordinary JAX/TF unified
graph budgets remain unsupported; all ordinary TF gradient graph lifetimes,
unknown copy/closure protocols, MPS QR/SVD and universal scratch ownership are
not certified by these explicit derivative-query tests.

The current frozen tree `10d077e8490050c26a1eaaefddfacad70a977abc`
now has SDK-free/main/alternate full, independent JAX/TF, retained-graph focus,
true full coverage and the complete 28-section matrix, all with exit receipts.
Coverage is 25410/28237 = 89.98831320607714%, with 68 exclusions unchanged.
The [ownership report](stage11p_c3_r1_resource_ownership_report.md) records exact
counts, skipped/unexecuted lanes and the two pre-existing mixed-environment pip
failures. Passing these gates does not close the known audit boundaries above.

Date: 2026-10-21. Baseline: `71f211dc2c106fdb675603d112c80dc2c334423e`.
Status: IMPLEMENTATION / IN_PROGRESS. Initial allocation and graph-lifetime
red contracts have been run, followed by the scoped fixes recorded below.
The preceding C3 checkpoint is tested but partial.
Full independent Qiskit/PennyLane replacement remains ACTIVE / INCOMPLETE.

The complete authorized ChatGPT C3-R1 instructions, sections 0-16, were read
through the normal conversation UI, including the initially off-screen tail.
R1 continues C3; it is not permission to start Capture, Studio or hardware work.

## Concrete Data Flow

Use A for packed framework source occurrences, P for explicit input scalars,
G for resulting native recorder slots, O for flat measured outputs and T for
actual Torch/Autograd trainable packed occurrences. C is one for a directional
HVP or P for a full input Hessian. G, A, P and T are not interchangeable: one
shared user parameter can appear in many gate occurrences.

Explicit JAX/TF queries provide classical maps to `execute_mapped_derivative`.
Its callback creates a native plan and composes the native recorder maps with
the framework maps. That plan then enters the existing Device executor and
existing quantum derivative algorithms. The new work must not replace them
with another quantum or gradient engine. There is no existing GradientEngine
class to extend.

Ordinary Torch/Autograd calls instead create a managed plan per invocation,
freeze source primals in `_framework_point`, pack actual framework scalars,
and later call the same plan through forward/backward/double-backward rules.
Their work consumption is already shared, but some numerical arrays live
outside an individual callback scope or are created before its reservation.

## Allocation Ownership Inventory

The following table follows actual consumers/lifetimes, not counts of NumPy
function names. Bytes are logical ndarray data, not Python/BLAS/framework RSS.
An entry marked open is not fixed by the earlier passing regression gates.

| Site / operation | Shape and dtype | Expected owned bytes | Owner / lifetime / alias facts | Baseline reservation and release |
| --- | --- | --- | --- | --- |
| Framework-supplied raw/packed/classical/second maps | raw P; packed A; classical A x P; second A x P x C; framework float32/64 | No new native buffer if borrowed without conversion | External callback inputs; `asarray` can be a view, dtype conversion can copy | Framework allocator explicitly outside native account; conversion sites still need audit |
| `framework_derivatives`: packed direction | A, result dtype of classical and tangent | A x result itemsize | New matmul result, needed during native directional plan construction | Created before reservation: open |
| `NativeHostKernel.plan`: first seed identity | A x A, float64 | 8 A^2 | Identity owns storage; each `eye[index]` is a row view, not another full identity | Eye allocates before Dual row reservations; must pre-reserve/deduplicate ownership |
| `NativeHostKernel.plan`: second trace context | Directional or full first/second seed arrays | Existing SecondContext sizes, not a new independent engine | Native parameter graph; source rows retained conservatively for the request | Existing context reserves its nodes; inspect input conversions and aliases separately |
| Native recorder own Jacobian | G x A, float64 from AngleRecorder | 8 G A | Newly assembled native array; feeds both first and second chain maps | Getter allocates before the new framework-source reservation: open |
| `mapped = own @ classical` | G x P, `result_type(own, classical)`; currently float64 for real native maps | G P x itemsize | Distinct output, no alias with either input | Matmul runs before `scope.retain`: genuine preallocation gap |
| Recorder internal second map | G x A x (1 for HVP, A for full) | Shape product x actual itemsize | Native map needed for the chain-rule contraction | Assembly and retained ownership require explicit preallocation audit |
| First second-order contraction | G x P x C | G P C x result itemsize | New mapped-second result; full expression uses two classical maps | Bare einsum before an individual output/workspace reservation: open |
| Coefficient/classical-second contribution | G x P x C | Same output size plus bounded workspace | Separate einsum temporary then in-place addition to mapped second | Temporary is not independently reserved: open |
| Common executor native first Jacobian product | O x P | O P x result itemsize | Existing quantum Jacobian composed with classical map; product is new | Group derivative-buffer reservation exists; verify every necessary concurrent buffer |
| `_framework_point`: fixed primals | G, float64: scalar_primal returns Python float | 8 G | New ndarray retained by unpack/second closures, including fixed and live source slots | Created outside managed callback; no graph-lifetime lease |
| `_framework_point.unpack`: fixed.copy | G, float64 | 8 G per actual copy | Distinct array; index assignment mutates this copy, not fixed primals | Currently before managed callback; forward stores a copy on Torch context |
| `_framework_point.second`: selected map | G x T, float64 | 8 G T | Fixed slots are not trainable; repeated source references need correct occurrence mapping | Zeros assembled before managed second callback: open |
| Selection arange / integer indices | T, platform integer width | T x intp itemsize for the actual array | Assignment index data, not a trainable parameter vector | Small but real native allocation; include in allocation policy |
| Managed identity/zero second map | G x G / G x size x columns, float64 | Existing exact shape products | Per-callback numerical buffers | Explicit reservations exist; check generic prepared buffers do not double-charge them |
| Torch `detach().numpy().astype(float)` | Packed scalar count, float64 result | Count x 8 for default astype copy | numpy view can borrow Torch storage; astype defaults to copying even at equal dtype | Conversion/copy happens outside the managed callback in several rules |
| First Jacobian indexed selection | O x T, float64 | 8 O T | Python-list advanced indexing copies; not a simple slice view | Happens after plan.jacobian returns: open |
| Torch/Autograd cotangent and direction products | Input-gradient and output-tangent vectors | Actual vector sizes x dtype itemsize | New postprocessing products; Tensor/as_tensor can share underlying NumPy storage | Need explicit allocation and ownership-transfer boundaries |
| Autograd second-result concatenate | T + O, plus operand temporaries | (T+O) x result itemsize plus concurrent operands | Concatenate owns new storage; its subsequent slices can share it | Outside current callback accounting: open |
| Flatten/reconstruction/conversion helpers | Depends on declared output tree | Actual leaf/copy/concatenate products | reshape may be a view or copy; astype/concatenate can create distinct buffers | Existing coarse bounds are not a site-by-site preallocation proof |
| NativeHost source/device copies | Circuit operations and configured initial numerical state | Depends on actual arrays and copy behavior | Persistent kernel source versus per-callback plan/device; initial MPS tensors can be copied | Configuration/initial-state copy lifetimes need explicit audit, not a false allocator claim |

## Workspace And Shape Rules To Prove

The mapped first product requires compatible G x A and A x P matrices.
Validate rank/broadcast behavior rather than assuming any NumPy matmul shape
is supported. Infer result dtype before allocating; a complex buffer, when a
helper supports it, has its actual itemsize rather than an unconditional eight
bytes. Physical framework input parameters remain real under the existing API.
Zero-size dimensions and shape-product overflow must reject or execute correctly
without attempting enormous arrays; use bounded integer shape calculations.

Current second expressions are `rpk,pn->rnk` for HVP mapping,
`rpq,pn,qm->rnm` for a full Hessian map and `rp,pnk->rnk` for the classical
second-map contribution. Output shape is not a bound on optimized contraction
intermediates. R1 must reserve outputs and a demonstrably bounded explicit
workspace, use bounded contractions/blocks, or reject an unbounded combination.
`optimize=True` is not a memory proof. Unexposed BLAS/LAPACK allocator space
must remain an accurately stated limitation, not an invented observed peak.

No HVP implementation may secretly materialize G x P x P or O x P x P merely
because a full-Hessian helper already exists. The max_hessian_elements=1
directional tests and C2A no-shift/64-shared-parameter tests remain protected.

## Graph Ownership Questions

Separate caller/framework-owned tensors from QB-owned native arrays retained
by closures or backward contexts. A callback returning does not prove its
native arrays died. Conversely, a view of one owned buffer must not receive a
second charge as though another buffer were allocated. A real copy needs its
own lease. Retained-for-backward and retained-for-double-backward storage need
normal, exceptional, repeated-use and graph-release tests.

In Torch, `ctx.values` currently keeps an unpack copy while saved tensor and
custom Function lifetimes govern callback reuse. `retain_graph=True` makes a
premature callback-end release particularly unsafe. In Autograd, per-invocation
primitive/VJP closures capture the plan, fixed source array and values. Their
actual post-GC retention needs a black-box weak-reference/lifetime test before
attributing a leak to any external registration mechanism; no private upstream
source or registry behavior has been assumed as proven here.

Ordinary JAX/TF graph-wide unified budgets remain explicitly unsupported.
Explicit per-query native array ownership is a different, supported scope.
Do not capture a mutable process-global ledger in JIT/pure callbacks or equate
tracing counts with actual executions. TF persistent tapes and repeated graph
calls require their own supported-boundary tests. Explicit lifetime management
is acceptable when a safe external graph release signal is unavailable, but
must not be sold as automatic full-framework allocator control.

## Next Evidence

Before changing production: persist and actually run the mapped-matmul and
second-contraction preallocation red contracts. Preserve complete logs and
independent exits. Then implement scoped allocation/ownership helpers only
where they remove real duplication in these paths, retaining the same native
quantum execution and second-order math.

The complete R1 checklist also requires packed-direction/Jacobian/fixed-copy/
selection/retained-graph/exception/reuse/alias/overflow/complex/workspace/
partial-shots negatives, ledger invariants for the same managed resources,
100-wire no-dense MPS and one-build H2/all-four-framework regression. After
runtime fixes: fresh clean-tree SDK-free/main/alternate full suites, independent
JAX/TF and Torch/Autograd focuses, full 28-section matrix, true full coverage
against 89.86520579542997% with the same 68 exclusions, legal/privacy and exact
production/test-tree receipts. Earlier C3 gates are baseline evidence only.

No R1 commit is justified by this audit alone. Preserve 71f211d and history;
no user Studio/Router changes, broad staging, token/auth/TLS operations,
workflow deletion, tag/release, hardware/cloud or permission-bypass push.

## Observed R1 Changes And Evidence

The table above is the baseline allocation inventory, not a claim that every
open entry has now been closed. Actual initial failures were preserved:

- `/tmp/qb-stage11pc3r1-initial-red-corrected.log/.exit`: two genuine allocation
  timing failures, exit 1. An earlier draft fixture lacked its fake plan's node;
  that fixture was corrected before these two pre-fix failures were recorded.
- `/tmp/qb-stage11pc3r1-graph-initial-red.log/.exit`: three failures, exit 1.
  Live Torch/Autograd graphs reported zero native storage; completed Autograd
  invocations still retained execution-plan owners after collection.

Current implementation pre-reserves packed directions, recorder Jacobian and
second maps, native points, mapped products and bounded row/column second-map
workspace. Dtypes, shape products, zero extents, explicit strided/cast workspace
and non-overlapping output contracts are validated before their allocations.
Native first-order identity seeds have one prior reservation; row views no
longer get a second ownership charge. CPU callback source maps are borrowed via
NumPy's documented no-copy DLPack API when they are not already ndarrays; an
unavailable no-copy conversion is explicitly unsupported, not an implicit copy.
Reference: https://numpy.org/doc/stable/reference/generated/numpy.from_dlpack.html

Fixed Torch/Autograd snapshots, unpacked points, explicit dtype conversions,
selected Jacobians, selected second source maps and returned VJP/HVP buffers
are pre-reserved. Their leases follow native storage roots through views;
independent copies have independent leases. Generic result buffer reservations
are conservative and can transfer to surviving native result roots. Already
owned source maps are removed from that generic result reservation. Torch
returns explicit framework copies, not untracked aliases of released NumPy
outputs. Framework-owned tensors remain outside the native allocator claim.

Torch Function classes and Autograd primitives now register generic rules once;
per-invocation owners are nondifferentiable graph inputs/context, not global
registration closures. Actual weak-reference tests cover completed calls,
retained graphs/pullbacks, repeated work consumption and failed second backward.
Removing per-call Torch classes was also necessary for failed-backward owner
collection in the observed environment. This is a black-box lifetime result,
not an assertion about private framework implementation details.

Receipts are snapshots. A snapshot taken inside a callback may legitimately
include its still-live native outputs and graph snapshot. Tests now verify that
snapshot's conservation equation, then inspect the live captured ledger after
dropping actual graph/output references and collecting. They do not force a
false zero at callback return. Work and completed physical shots are not refunded.

The MPS workspace estimator previously evaluated `initial_state.tensors`, whose
public property copies tensor storage (including via hasattr). It now reads
the existing allocation-free bond-dimension property. Actual MPS kernels still
have a conservative aggregate tensor/contraction/SVD reservation; internal
LAPACK allocation and all persistent kernel/source-device copies are not yet
a universally proved allocation-by-allocation memory bound.

Focused observations so far (not final R1 clean-tree acceptance):

- `/tmp/qb-stage11pc3r1-arrays-second`: 33 passed, exit 0.
- `/tmp/qb-stage11pc3r1-framework-focus`: 373 passed, one missing-installation
  contract skipped, exit 0; includes real four-framework/native H2 and streamed
  HVP/second-adjoint interface regressions.
- `/tmp/qb-stage11pc3r1-allocation-final-focus`: 67 passed, exit 0; includes
  explicit packed-direction/Jacobian rejection, MPS estimate, graph ownership,
  overflow/complex/alias/workspace and repeated backward tests.

The framework focus preceded the last small MPS-estimator/no-copy-version
guards and extra unit negatives. Final-tree broad/full gates must be rerun.
Strict ordinary JAX/TF cross-callback budgets, source/device-copy ownership,
all metadata/validation scratch arrays and unexposed allocator workspace remain
open; R1 and C3 remain incomplete. No new remote push or CI result is claimed.

Subsequent clean export `71f72ce03998d0baa356a1cd9b07f6fdfa33669c` passed
main full (2389/5 skipped/3 existing xfailed), SDK-free full (1789/377 skipped),
independent JAX derivative/interfaces (223/136 skipped) and independent TF
derivative/interfaces (242/122 skipped), all exit 0. These are intermediate R1
regressions, not final acceptance after the remaining copy/Result ownership
changes. The [ownership report](stage11p_c3_r1_resource_ownership_report.md)
records exact source hashes, log/exit prefixes, versions and the fully read
authorized review follow-up. Public Device Result lifetime ownership
was still open at that earlier snapshot despite private ordinary-framework
result-buffer transfer. The following slice changes that public boundary.

Public result retention is now unconditional in the common executor. Seven
actual initial red public lifetime cases preceded the fix; five derivative
kinds, nested user views, concurrent budget pressure and release recovery are
verified. Three later red observations exposed undercounted raw retained
Jacobian/second data. `native_storage_bytes` now observes the same deduplicated
roots that the conservative result lease follows; no whole-process RSS claim
is made. Success receipts no longer falsely require zero while arrays live.

Tape and native host Device configuration copies now use one prior-lease copy
memo under an active ResourceScope. Three actual initial negatives proved
copies were previously unbudgeted. Shared input object references produce one
destination; distinct ndarray views produce distinct actual copied storage.
Known subclass behavior is preserved with unknown extra workspace disclosed.
Persistent construction without an active scope is not newly budgeted.

A further actual failure showed returned status exception frames holding an
otherwise unused partial copy. Status results now detach traceback/cause/context;
raising APIs keep normal debug tracebacks. Release is tested with the failure
Result still alive and after collecting genuinely unreachable cyclic garbage,
not by forcing a false zero before storage dies. All new red/green log prefixes
and the 867-test broader intermediate regression are in the ownership report.
