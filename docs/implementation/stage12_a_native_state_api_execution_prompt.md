# Stage 12-A P0 Execution Contract

Date: 2026-10-21. Native code baseline:
`b1d345b3731276f5f2721cb42c2397d98981ac5c`.
C3 remains PARTIAL. Full independent Qiskit/PennyLane replacement remains
ACTIVE / INCOMPLETE. The designated ChatGPT conversation's completed reply
accepted the report-based finite C3 review, not an independent source audit.
Review/status documents created after b1d345b are not part of that checkpoint.

## Scope And Compatibility Decision

P0 implements actual Statevector/DensityMatrix mixed-radix subsystem dimensions,
their numerical propagation and necessary public compatibility contracts. Do not
develop the later RNG/arithmetic/purity batches early. No Capture or Studio.

Preserve existing native q0-first ordering, dictionary probabilities and
DensityMatrix.dim shape tuples. Public compatibility entry points explicitly
translate verified wire/qargs conventions, containers, dimensions and errors.
Prefer existing compatibility entry points and mode mechanisms. If insufficient,
propose and exercise a minimal boundary, not a second state simulator or an
upstream-only facade. Shared native state/density mathematics does the work.
Do not label unchanged native contracts as full Qiskit compatibility.

Explicit dimensions such as (2,4) must remain distinguishable from (2,2,2).
A (3,2) state is not three qubits. Total Hilbert dimension equals the product
of subsystem dimensions; ordering and qubit/qudit identity remain traceable.
Preserve existing legal zero-qubit behavior; distinguish public from_int empty-
dimension quirks from other constructors instead of guessing a universal rule.

## Required Sequence

1. Inspect current native signatures and use installed public Qiskit 2.4.1 and
   2.6 APIs as black-box references only. No upstream implementation/test source
   reads, copies or ports. Build a versioned contract matrix for from_int,
   dims/dim/num_qubits, tensor/expand/evolve, probability qargs, measurement,
   actual public partial_trace entry points and legal/illegal/empty dimensions.
   Include (2,4), (3,2), (2,3,2), one qudit and zero-subsystem boundaries.
2. Record genuine pre-fix native failures: explicit dimensions flattened or
   lost, nonbinary dimensions rejected, and actual invalid-input contract gaps.
   Preserve logs, independent exits, exact call entry and public reference.
3. Reuse existing numeric arrays, Statevector/DensityMatrix objects, ResourceScope
   and ownership helpers. Fix the actual subsystem representation/invariant, not
   only external metadata or a fabricated qubit interpretation.
4. Add genuine propagation failures across state/density conversion, copy,
   tensor/expand/evolve, measure/reset/probabilities/sample, subsystem mapping
   and partial_trace. Include a case with correct amplitudes but incorrect dims.
   Verify both numerical data and dimensions after correction.
5. Keep explicit restrictions for operations not yet extended beyond qubits;
   never silently apply binary logic or call Unsupported a completed feature.
   Do not duplicate already-correct tensor/expand/evolve implementations.
6. Maintain separate native-contract and compatibility-contract tests. A public
   container/wire/error conversion cannot replace genuine native mathematics.
7. Verify mixed-radix basis indexing/order, Bell/qudit products, density trace/
   Hermiticity/PSD, tensor order, reduced density, normalization and collapse,
   using independent mathematics and optional public differentials. Execute
   from_int -> tensor -> DensityMatrix -> partial_trace -> probabilities.
8. Admit directly introduced ndarray buffers before allocation and preserve real
   result/view lifetimes. Fix actual resource errors within this batch, not an
   unbounded whole-allocator audit. Retain state/Tableau/100-qubit MPS/HVP/
   four-framework/QASM/QPY/Aer noise-save-set/H2/Result regressions.
9. After focused SDK-free/main/alternate and public differential gates, freeze
   P0 source and run fresh three-environment FULL, independent JAX/TF,
   Torch/Autograd, explicit full coverage, actual 28-section matrix, compile/
   legal/privacy/no-token/no-vendor. R2 passes cannot accept new P0 source.
   Current exact coverage baseline is 90.35145452152166%, exclusions 68.
10. Stage only P0-owned paths and commit normally after required gates; preserve
    user Studio/Router dirt. No push without restored workflow authorization and
    fresh fast-forward proof; no credentials/OAuth/TLS changes, token reads,
    cloud/hardware, tags/releases, vendor or history rewriting.

## Required Delivery

Report the two-version public behavior matrix, actual native gaps, dimension
invariants, public/native compatibility boundary, real red/fix/math/differential
evidence, composed workflow, fresh test tree/full gates/coverage/matrix exit,
actual local SHA and truthful remote status. Then return to the designated
conversation and ask for the next bounded function batch. Later RNG/arithmetic/
purity gaps remain open. A facade, metadata-only patch or green test count is
not the highest full replacement objective.

The first read-only contract survey is recorded in
[the P0 contract matrix](../compat/stage12_a_state_api_contract_matrix.md).
P0 native implementation is not claimed by that survey.

## Completed Follow-Up: P0.1 Construction And Core Propagation

After the corrected two-version survey and documentation checkpoint d22e88f
were reported, the designated conversation's completed reply was fully read.
It requires direct native implementation next, not repeated public surveys.
The separately failed dirty-workspace Router legal check must remain disclosed;
do not remove or modify the user's Router to manufacture a green result.

- Establish actual dimensions invariants in existing state/density objects and
  ResourceScope: product equals array dimension, ordered subsystems retained,
  mixed radix is not inferred to be qubits merely from power-of-two total size.
  Handle (1,), a single qudit and empty cases per verified entry-point contract.
- Save genuine native construction reds for Statevector.from_int(5,(2,4)),
  from_int(4,(3,2)), from_int(7,(2,3,2)), state-to-density conversion, (6,),
  (1,), invalid dimensions and out-of-range indices. Do not rewrite correct old
  tests merely to obtain failures. Record mathematical/public expectations.
- Implement basis amplitudes/density and dimension-preserving copies/conversion
  using existing native numeric arrays and admitted allocations. No upstream
  quantum engine, source/test port, second state simulator or metadata-only fix.
- Then save and fix propagation reds in existing copy/tensor/expand, full-system
  operators that preserve subsystem structure, state-to-density, probabilities,
  measure/reset and supported partial_trace entry points. Replace binary index
  assumptions with true mixed-radix mathematics, or explicitly reject a still
  unsupported subpath rather than return silently misinterpreted results.
- Preserve native q0-first, dict probabilities, density shape-tuple dim and old
  valid binary callers. Maintain separate native/public contract tests; reuse
  existing compatibility entry points where sufficient. Do not add a large
  facade or count boundary conversion as the native mathematical implementation.
- Execute from_int -> tensor -> DensityMatrix -> partial_trace -> probabilities
  for both (2,4) and (3,2), checking amplitudes, trace, dimensions, reduced
  density, normalized probabilities and qargs ordering against independent
  mathematics and optional public oracles. Include correct numbers/wrong dims
  as a real pre-fix failure.
- Run construction/propagation focuses and state/density/Clifford/Result/MPS/
  Device regressions, then freeze source and report actual native APIs,
  unsupported mixed-radix paths, compatibility differences, math/differentials,
  source equality and remaining gates. Before a code commit, run the previously
  agreed fresh FULL/framework/coverage/28-section/compliance gates on P0 source;
  do not reuse R2 receipts. Only stage P0-owned files, no push or history rewrite.
- P0.1 must deliver actual construction and core dimension propagation. Defer
  RNG/arithmetic/purity/full observables/general-channel expansion, Router,
  global allocator audits, Capture and Studio. Decide P0.2 from actual remaining
  failures. Full functional replacement remains ACTIVE / INCOMPLETE.

## Completed Follow-Up: P0.1 Frozen-Tree Gates And Bounded Acceptance

The completed reply in the designated conversation was fully read after the
native implementation and SDK-free FULL result were reported. The feedback is
based on this execution report, not an independent external source audit.
Its execution requirements are preserved here in English:

1. Keep production/tests/examples frozen at tree
   7aeb821e37b374ce0c3676d6d49236828155dccc (HEAD d22e88f). Wait for the
   already-running main FULL coverage process to terminate naturally; record
   its real exit, complete counts and coverage JSON. Then run alternate FULL,
   independent JAX/TF, Torch/Autograd focus, actual 28-section matrix, compile,
   legal/privacy/security/no-token/no-vendor, five environment versions and
   import origins, and pip check. Preserve full logs and independent exits.
   Missing matrix dependencies are NOT_EXECUTED. Recheck source equality.
   Baseline coverage is 90.35145452152166%, with 68 exclusions; it is not a
   functional-completion metric. Preserve genuine failures, minimally fix real
   regressions, refreeze and rerun affected/necessary FULL gates. Never borrow
   old-tree passes.
2. After gates, accept only the bounded P0.1 native functions: typed mixed-radix
   from_int/dimensions, state/density construction and conversion, tensor/expand/
   copy/conjugate/transpose/adjoint/reverse, full-system numeric evolve,
   probabilities/sample/measure/reset, partial trace and the composed basis ->
   tensor -> density -> partial_trace -> probabilities workflow. Per function,
   report actual native calls, pre-fix reds, independent complex mathematics,
   public Qiskit 2.4.1/2.6 differentials, dimension/qargs/error/ownership contracts
   and unsupported paths. Keep mixed mapped operators/circuits/general channels
   Unsupported until implemented; never confuse a single qudit with qubits in
   analysis. Preserve native q0-first/dict probabilities/density shape-tuple dim.
3. Only after required gates, stage explicitly owned P0.1 paths, compare staged
   runtime/tests/examples with the tested tree, commit normally and report SHA.
   No push, force/rebase/reset/amend, token/auth/TLS, cloud/hardware, tag/release
   or vendoring. Preserve user Router/Studio files. Report whole-workspace Router
   ledger failure separately from controlled-export legal success.
4. Only after P0.1 gates/checkpoint, consider P0.2: first mixed-radix mapped
   numeric operators with correct local embedding/dimension/qargs order; then a
   mathematically justified finite mixed-radix Kraus/channel subset; preserve
   binary-only analysis guards and separately define any true generalization.
   Each requires verified public behavior, native red/fix, independent oracle,
   public differential and composed calls. No RNG/arithmetic/purity, new global
   allocator audit, upstream passthrough, wrapper-as-engine or large facade.
5. Report verified native P0.1 functions separately from remaining public
   incompatibilities, P0.2 functions, actual gates/coverage/matrix, local SHA,
   remote CI and remaining full-SDK APIs. The order is current main FULL ->
   remaining gates -> bounded acceptance -> local checkpoint -> mapped numeric
   operator work. Full functional replacement remains ACTIVE / INCOMPLETE,
   C3 stays PARTIAL, Capture/Studio remain out of scope and Studio stays last.

## Completed Clarification: Public Metadata Differences

After main FULL coverage and the supplementary numerical comparisons were
reported, the designated conversation's completed clarification was fully read:

- Retain the native actual-partition num_qubits invariant. The four observed
  public partial_trace num_qubits differences per version are Partial Public
  Compatibility; correct native mathematics must not be changed merely to
  imitate an unexplained public result. Any later compatibility mapping belongs
  at its explicitly defined public boundary.
- Public DensityMatrix methods that do not exist, such as transpose in both
  installed versions, are NATIVE_MATH_ONLY when checking the existing native
  method. Do not count this as public-method parity or an upstream feature gap.
  Retain the incomplete initial comparison/harness failures.
- Keep tree 7aeb821e production/tests/examples frozen. Complete alternate FULL,
  independent JAX/TF/Torch/Autograd and the real 28-section matrix with logs and
  independent exits before acceptance, checkpoint or P0.2. Recheck workspace
  and export equality afterwards. Source changes require refreezing and actual
  affected/necessary full reruns, not reused receipts.
- Numerical checks and public contracts are separate judgments: the two sets
  of 158 numerical comparisons support only their measured mathematical slices.
  Keep the four metadata differences Partial and absent public methods outside
  public pass counts. Preserve mixed mapped operator/circuit/general channel
  Unsupported boundaries, and disclose the independent dirty-workspace Router
  legal failure without touching the user's files.
- After remaining gates, classify only sufficiently evidenced native slices as
  Verified Native, others Partial/Unsupported, then make a scoped normal local
  checkpoint and report SHA, tested tree and truthful remote CI. Main's 3189
  passed / 5 skipped / 3 xfailed and 90.44385395138274% coverage with 68 unchanged
  exclusions are quality evidence, not all-gates acceptance or an SDK parity
  percentage. Full replacement stays ACTIVE / INCOMPLETE; C3 stays PARTIAL and
  Capture/Studio remain excluded.

## Completed Next Prompt: Stage 12-A P0.2-A Mapped Numeric Operator

After the actual P0.1 checkpoint and all final gate results were reported, the
designated conversation's completed reply was fully read. This is a faithful
English preservation of its complete task requirements, based on the execution
report rather than an independent external source audit.

Baseline: P0.1 code commit 89f4dc95bd38076c869c13e9176423698d6efb53;
C3 PARTIAL; full independent Qiskit/PennyLane replacement ACTIVE / INCOMPLETE.
Implement real local numeric-operator action on selected mixed qubit/qudit
subsystems, not another dimensions-only patch. Limit the batch to existing
Statevector/DensityMatrix mapped numeric evolution. No general channels, RNG,
arithmetic/purity, Capture or Studio.

### Task 1: Verify Public Contracts

Use installed Qiskit 2.4.1/2.6 public numerical APIs as black boxes, never reading
or copying upstream source/tests. Probe Statevector.evolve(Operator,qargs=...)
and DensityMatrix.evolve(Operator,qargs=...) for (2,4), (3,2), (2,3,2), single
qudit (6,), noncontiguous (0,2), reversed (2,0), different input/output subsystem
dimensions, actual rectangular-operator boundaries, duplicate/out-of-range/
illegal qargs, complex non-diagonal and nonunitary matrices. Record actual
versioned numbers, exceptions, dims, dtype and subsystem order. Confirm version
differences experimentally, not by guessing.

### Task 2: Preserve Genuine Reds

Cover at least: a non-diagonal operation on the 4-level subsystem of (2,4);
a complex qutrit unitary on (3,2); coupled operation on (0,2) of (2,3,2);
the SAME matrix on reversed (2,0) without sorting qargs; noncontiguous state or
operator buffers and incorrect copy/reshape behavior; state/density evolution
disagreement; invalid duplicate/out-of-range qargs; and correct numeric output
with incorrectly flattened dimensions. Save full red logs and independent
exits, distinguishing unsupported implementation, mathematical error and public
compatibility difference. Do not fabricate failures in already-correct paths.

### Task 3: Actual Native Local Action

Reuse existing Statevector, DensityMatrix, Operator and native tensor/array
kernels. Derive subsystem sizes/strides from actual dims, map qargs in their
given order (including reversed/noncontiguous), act identically on unselected
subsystems, and perform native complex tensor contractions or controlled index
operations. Share consistent state/density mapping. Density follows U rho U-dagger;
do NOT silently normalize a nonunitary result. For verified supported dimension-
changing operators, update actual output dims; reject unproved combinations as
Unsupported. No second simulator, SDK engine/facade or full-system Kronecker
embedded matrix masquerading as local execution. In a (2,3,2) system, do not
default to constructing a complete 12x12 embedded matrix for a local operator.

### Task 4: Independent Mathematics And Public Differentials

Author an independent NumPy oracle using explicit mixed-radix basis enumeration,
without Qiskit/PennyLane. Include mixed product states, complex entanglement,
complex Hadamard/Fourier unitaries, non-diagonal/nonunitary matrices,
noncontiguous/reversed qargs, different target dimensions, and applicable
density Hermiticity/PSD/trace behavior. Compare both public versions, reporting
numeric/dims/qargs/error differences separately. Explicitly transform native
q0-first versus public ordering; transformed equality is not identical calling
convention parity.

### Task 5: Bounded Resources And Regression

Reuse ResourceScope/Ledger/ArrayOwnership. Only account new known ndarray
outputs/temporaries introduced here; no global allocator audit. Prove known
outputs admitted before allocation, no unmetered strided-input copy, independent
charging for actual copies with shared roots for views, budget rejection before
the core contraction, valid -> overbudget -> valid recovery, and the lifetime
of user-held result views. Preserve P0.1 native q0-first, probability dicts and
DensityMatrix shape-tuple dim.

### Task 6: Explicit Non-Goals

No general Kraus/Choi/SuperOp mapped channels, mixed-radix circuit instructions,
qudit synthesis, general observable framework, object RNG/seed, state arithmetic/
purity, overall SDK facade or global resource-ledger refactor. Classify calls
involving an unsupported channel/circuit instead of forwarding to upstream.
The reply also mentions "Operator.evolve" in this caution: verify actual public
method names during Task 1 rather than inventing an API from that wording.

### Task 7: Acceptance And Local Checkpoint

Deliver at least 12 mixed-radix local-action math scenarios, 6 noncontiguous/
reversed-qargs scenarios, 6 state/density-consistency scenarios, 6 failure/
resource/lifetime scenarios, both public-version differentials, and an actual
composed call: from_int -> tensor -> mapped evolve -> DensityMatrix ->
partial_trace -> probabilities. These minimum case counts are not feature-
completion metrics. Freeze final code, then run fresh SDK-free/main/alternate
FULL, independent JAX/TF, Torch/Autograd, true full coverage, actual 28-section
matrix, compile/legal/privacy/security and tested-tree equality. Baseline is
90.44385395138274%, exclusions 68 must not increase; coverage is not API parity.
Stage only owned P0.2-A paths and commit normally after gates. Preserve user
Router/Studio; no push, auth/TLS/credential changes or token reads, cloud or
hardware, vendor/tag/release, or history rewriting.

### Task 8: Delivery And Execution Order

Report actual newly implemented native APIs; mixed-radix index/stride/qargs
mapping; genuine red/green; independent complex state/density results; both
public-version differentials and actual differences; supported/Unsupported
matrix types; resources/views; three FULL environments, coverage/matrix;
actual local SHA and remote CI status; then the next real core gaps. Metadata,
wrappers and upstream passthrough do not count as native computation.

First implement dimension-preserving square local operators for arbitrary
verified qargs on (2,4)/(3,2)/(2,3,2), for both state types. Only then extend
rectangular input/output operators where public contracts are verified; update
target subsystem output dimensions rather than only changing total array size.
Decide whether to start P0.2-B mapped channels AFTER this batch. The highest
goal stays ACTIVE / INCOMPLETE, C3 PARTIAL, Studio last.

## Completed P0.2-A Clarification: Freeze And Bounded Acceptance

The designated conversation received actual 240-case/version public outcomes,
native reds/repairs and the then-current 207-case focus. Its completed reply was
fully read. It is report-based feedback, not an independent source audit. It
approves freezing the bounded implementation, not adding general channels or
other Stage 12 functions. Its stated HEAD 89f4dc9 names the runtime checkpoint;
the actual starting HEAD is documentation commit 2bd746c over that same runtime.
Do not reset history to change the documentation baseline.

- Keep local Statevector rectangular maps Unsupported only within the sampled
  public failure boundary. It is mathematically defined and can be extended in
  a future native batch. Support verified local Density A rho A-dagger without
  normalization, and full-system typed rectangles for both classes with actual
  ordered output dims. Preserve raw-rectangle/public-acceptance differences.
- Finish the live broad regression naturally; preserve actual failures and
  distinguish real regressions, obsolete Unsupported assertions and test/command
  errors. Update only genuinely obsolete assertions, never numerical tolerances.
- Strengthen unequal total dimensions (e.g. 4 -> 6), ordered/noncontiguous and
  reversed targets with a non-symmetric complex matrix, non-Hermitian/nonunitary
  density action using conjugate transpose, and adjoint input/output side swaps.
  Prove native independent numerical results, not merely metadata.
- Validate rectangular Dout != Din known work arrays, strided inputs, failure
  recovery and real user-held view/root leases. Check unselected reduced density
  against the correct mathematical map: non-trace-preserving maps need NOT leave
  it unchanged. Limit resources work to directly introduced known buffers.
- Freeze and run fresh three-environment FULL, independent JAX/TF/Torch/Autograd,
  true full coverage, actual 28-section matrix, compile/legal/privacy/security,
  versions/import origins/pip and tested-tree equality. Preserve separate logs
  and exits, exclusions 68 unchanged. Only then stage owned paths and commit
  normally; no push, Router/Studio, token/auth/TLS, cloud/hardware, vendor/tag/
  release or history rewrite.
- Report square local maps, rectangular density and typed full-system maps,
  local Statevector rectangles still Unsupported, actual target order, math/
  public differences, ownership, gates and remaining compatibility separately.
  After P0.2-A acceptance, update the actual state-function ledger before
  deciding whether mapped channels should be the next highest-value gap.
  Full replacement stays ACTIVE / INCOMPLETE; C3 PARTIAL; Studio last.

## Completed Frozen Clarification: Unresolved Public Numerical Difference

After the 232-case focuses, frozen tree and actual SDK-free FULL were reported,
the completed designated-conversation response was read. It classifies the
reported example as Verified Native Math / Partial Public Compatibility, with
an important limit: two independent oracles plus public DensityMatrix agreement
do not prove an upstream Statevector defect. An unresolved public dimension or
target-semantics issue remains possible. The nonzero public state-outer/density
delta rules out merely a global phase difference in the measured example.

- Keep frozen tree 2973040c unchanged and wait for main FULL coverage, then
  alternate FULL/frameworks/actual matrix/final equality. Do not expand this
  batch, add a facade, guess upstream internals, weaken tolerances or add an
  unconditional xfail to manufacture public equality.
- Preserve complete reproducible input: native dims (2,3,2), selected (2,1),
  matrix input/output dimensions and elements, complex amplitudes, explicit
  public-order conversion and actual native/public state/density outputs.
  Label PUBLIC_DIFFERENTIAL_MISMATCH; a reporter's exit 0 is not a public pass.
- Record how basis enumeration, independent tensor contraction and density
  action differ as implementations; do not let a shared untested target-order
  conversion masquerade as two independent public-contract oracles.
- Finish all required gates/equality before bounded acceptance and scoped local
  commit. Preserve real regressions and minimally fix/refreeze if needed. The
  observed case remains unresolved public compatibility even if local gates pass.
- Later, but not blocking these frozen gates, investigate a minimal pure-state/
  nonunitary/single-basis/swapped-target example to distinguish public semantics,
  common version behavior or a potential defect. Do not assert its cause now.
  This feedback is based on the execution report, not an external source audit.

## Received Next Batch Prompt: P0.3

The complete designated-conversation reply finished on 2026-10-21 (the UI showed
the completed response, not a partial stream). The prompt below is transcribed
with Markdown formatting from that response. It is the NEXT implementation
batch, not a claim that P0.3 has already been implemented or accepted. Its stated
HEAD is the actual P0.2-A code commit; later checkpoint-receipt edits are docs only.

### QuantumBridge Stage 12-A P0.3 — Native Mixed-Radix Operator Composition & Subsystem Evolution

#### 0. 任务目标

当前 HEAD：`12098c950236597ae17c157376fffcce8785acbf`

本批目标是让现有原生 Operator 支持真实的 mixed-radix operator-to-operator
composition，并与已完成的 Statevector/DensityMatrix 局部 evolve 形成可组合数学体系。

不是创建新的 Quantum Operator 框架，而是在现有 Operator、utils.math 和原生状态内核上
补齐缺失的实际计算功能。最高目标保持：Qiskit + PennyLane 全部核心功能独立原生
full functional parity/full replacement，ACTIVE / INCOMPLETE。

#### Task 1 — 公开行为调查与差异最小反例

先使用现有 Qiskit 2.4.1、2.6 的公开 API 黑盒实验，核对实际存在的：

- `Operator.compose(other, qargs=..., front=...)`
- `Operator.dot(other)`
- `Operator @ other`
- `Operator.tensor(other)`
- `Operator.expand(other)`
- `Operator.adjoint()`
- `Operator.power(n)` 的已支持边界
- 不同 input_dims/output_dims 的矩形 Operator 组合

必须核实两个版本各自的实际签名、qargs 顺序、维度传播、异常类型，不猜测 API。

同时，对已经保留的 `stage12_a_p02_public_differential_case.json` 做有界最小反例分析：

1. 保留原始完整案例和输出，不覆写既有证据。
2. 缩减为更少子系统、简单复相位、可手算矩阵的实验。
3. 依次排除 qargs 翻转、矩阵张量排序、输入/输出维度排序、Statevector 与 DensityMatrix 使用不同公开映射语义等可能性。
4. 将每种解释与真实黑盒输出比较，而不是推断上游源码。
5. 如仍不能解释，继续保留 PUBLIC_DIFFERENTIAL_MISMATCH，不阻塞本批原生功能实现。

时间范围限定为一轮专项调查，不允许演变成无限追踪上游内部实现。

#### Task 2 — 真实红灯：Mixed Operator Composition

至少建立以下修复前失败案例：

1. (2,3) mixed-radix Operator 的正确 compose 数值。
2. (2,3,2) 全系统 Operator 与作用在 qargs (0,2) 的局部 Operator 组合。
3. 反向 qargs (2,0)，证明目标位置不被偷偷排序。
4. 非对称复矩阵组合，证明左右乘法方向正确。
5. 相同总维度、不同 subsystem partition 的合法与非法组合。
6. 矩形 Operator 组合，例如 4→6→3。
7. front=True/False 对应的真实组合顺序。
8. 输出矩阵正确，但 input_dims/output_dims 丢失的反例。
9. 非连续、转置、带复相位的 Operator 数组。
10. 数学上不可组合的输入/输出维度被错误接受。

先运行并持久化 red log、独立 exit 和真实差异。不能为了制造红灯修改已经正确的旧测试。

#### Task 3 — 原生最小实现

复用现有：

- Operator numeric representation；
- Mixed-radix dimensions；
- 原生 stride/index 映射；
- ResourceScope / ArrayOwnership；
- 已有 matrix multiplication kernel。

实现真实的：

A. Full-system Operator composition

正确支持兼容维度的矩形矩阵复合，包括输入总维度和输出总维度不同的情形。

B. Mapped Operator composition

在现有支持的 subsystem count 不变场景下，将局部算符映射到指定 qargs，与全系统 Operator 组合。

- 不排序 qargs。
- 保留未选子系统恒等作用。
- 正确区分 front 与默认 compose 顺序。
- 正确传递 output partition。
- 矩形局部映射只有在数学和公开契约已验证时纳入；否则明确 Unsupported。

C. Operator 与 State 一致性

验证 `(A.compose(B)).evolve` 所对应的状态作用，与在现有 Statevector/DensityMatrix 上
按正确顺序连续执行 A、B 的结果一致。这里需以仓库真实 API 为准，不得调用不存在的
Operator.evolve 方法。应使用现有 Statevector.evolve(Operator) /
DensityMatrix.evolve(Operator) 等真实入口。

D. 不构造不必要的全局中间 Operator

对于 mapped composition，尽量复用 P0.2-A 的局部收缩和目标索引规则，不默认构造完整
embedded Kronecker 算符。如果公开 API 要求最终返回完整 Operator，允许为最终结果
分配完整输出矩阵，但必须明确其数学必要性，并在分配前预约；不能声称整个计算过程都没有全局矩阵。

#### Task 4 — 独立数学 Oracle

至少使用两种独立验证方式：

- 显式 mixed-radix 基态枚举；
- 独立 NumPy 张量指标收缩或小规模 Kronecker 参考计算。

使用非对称复矩阵、非幺正矩阵和矩形矩阵，避免只测试 Pauli/Clifford 等容易掩盖维度顺序
错误的特殊矩阵。必须验证：

- compose 左右顺序；
- front；
- qargs；
- wire ordering；
- global phase；
- mixed dimensions；
- output partition；
- Statevector/DensityMatrix 数值一致性；
- 非幺正时不自动归一化。

对 Qiskit 2.4.1/2.6 只做公开黑盒 differential，不使用上游 SDK 执行 QuantumBridge 的生产计算。

#### Task 5 — Native 与 Public 兼容边界

继续保留：

- QuantumBridge native q0-first；
- 已有 Operator/state 实际 dims 不变量；
- native probabilities dict；
- DensityMatrix shape-tuple dim。

公开兼容差异独立记录，不能静默改写 native API。

特别注意：如果某个公开 Statevector.evolve(mapped Operator) 的结果与独立数学不一致，
不能借由 Operator.compose 的实现把错误传播到核心内核。将其归类为已验证 native
mathematics 与未解决 public contract mismatch，直至独立证据支持修改。

#### Task 6 — 最小资源与错误处理

只管理本批新增输出和已知临时数组。要求：

- 分配前计算矩阵输出大小；
- 预预约；
- view/root lease 正确；
- 矩形中间量与最终结果分开计量；
- 超限在大矩阵分配前拒绝；
- valid → overbudget → valid；
- invalid qargs、dimension mismatch 和 foreign ndarray protocol 在执行前安全拒绝。

不要开启全局 allocator 审计，不重写 C3 ledger。

#### Task 7 — 明确排除项

本批不做：

- General mapped Kraus/Choi/SuperOp；
- General quantum channels；
- Circuit instruction lowering；
- Qudit gate synthesis；
- PennyLane 新 template；
- RNG；
- State arithmetic；
- Purity；
- Capture；
- Studio；
- 全局资源预算重构。

如果任务调查发现 Operator compose 当前已经正确支持某个子集，应直接复用并列为回归，而不是重新实现。

#### Task 8 — 有界验收标准

至少交付：

- 12 个 mixed-radix composition 数学场景；
- 8 个 qargs/front/order 场景；
- 6 个矩形输入输出维度场景；
- 6 个 state-vs-composition 一致性场景；
- 6 个资源/非法输入/失败恢复场景；
- 两个 Qiskit 版本的公开 API 黑盒差分；
- 一个端到端组合：

`Operator A → Operator B → mapped compose → Statevector evolve → DensityMatrix → partial_trace → probabilities`

这些应当是真实执行场景，不以大量重复参数化测试取代关键独立数学证据。

#### Task 9 — 最终门禁

冻结全部生产源码与测试后执行：

1. SDK-free FULL。
2. Main FULL + explicit coverage。
3. Alternate FULL。
4. 独立 JAX/TF 和 Torch/Autograd focused。
5. 完整 28 段 local matrix，独立 shell exit。
6. compileall、legal、privacy/security/no-token/no-vendor。
7. 五环境版本、import origins 和 pipcheck。
8. tested tree、export、workspace 和 staged/committed production/tests/examples 一致性检查。

Coverage 历史值 90.45969876172117%，68 exclusions 不增加。不得把行覆盖率解释为功能完成率。
受控 legal 与带用户 Router 脏文件的整个 workspace legal 结果仍须分别披露。

#### Task 10 — 限定提交与报告

必要门禁全部通过后，仅 stage Stage 12-A P0.3 归属文件并正常本地 commit。

不修改 Studio/Router 用户文件；不 push；不改认证/TLS；不读取 token；不调用云或真实硬件；
不 vendor、force、reset、rebase、amend、tag 或 release。

最终报告至少列出：

- 真实新增 API；
- Operator compose/front/qargs 数学；
- mixed-radix 矩形维度传播；
- 两种独立 oracle；
- Qiskit 2.4.1/2.6 差分；
- 原公开 Statevector 异常案例的调查结果；
- SDK-free/main/alternate FULL；
- coverage、28 段 matrix；
- 本地 commit；
- 未验证远端 CI；
- 下一批真实核心函数缺口。

#### 明确执行要求

立即执行 Stage 12-A P0.3，先完成公开 Operator.compose 契约调查与既有 Statevector 差异的
有限最小反例，再建立真实 composition 红灯，随后实现原生 mapped composition。

我选择这项任务，而不是马上做 mapped channels，是因为它直接扩展现有核心 Operator
的组合能力，同时能够为后续 State、Circuit、Channel 的数学操作提供可复用基础。

但本批有一个必须坚持的工程原则：以真实函数能力和独立数学正确性为验收中心，
而不是把工作重新变成资源账本或兼容包装工程。

完整 Qiskit/PennyLane full native functional parity/full replacement 仍为
ACTIVE / INCOMPLETE，C3 仍为 PARTIAL，Studio 最后。

## Completed P0.3 Freeze Clarification

The designated reply completed on 2026-10-21. It permits freezing, not acceptance
or an independent audit. The existing tests cover the actual native A @ B versus
B @ A convention and explicit public conversion; a rectangular type chain with
different total input/output sizes; and validation/budget/foreign protocols
before allocation. A final minimal forbidden-factory assertion strengthens the
existing invalid-dimension test before the one final runtime tree is frozen.
No new feature, allocator audit or facade is requested.

### QuantumBridge Stage 12-A P0.3 — Freeze, Full Gates & Bounded Acceptance

当前开发基线：9e3224b，P0.2 代码基线 12098c9。本批只验收现有 Mixed-Radix Native
Operator Composition，不实现新的 API。

#### Task 1 — 冻结

将当前归属 P0.3 的 production/tests/examples 和必要文档通过独立 Git index 导出，记录
完整 frozen tree SHA、production subtree SHA 和限定文件清单。排除用户 Studio/Router
脏文件，保持真实 index 状态可追溯。冻结后不得继续修改生产代码、测试或示例；如发现
回归，必须修复并重新冻结。

#### Task 2 — 完整质量门禁

在同一冻结树顺序执行：

1. SDK-free FULL。
2. Main FULL + explicit coverage。
3. Alternate FULL。
4. 独立 JAX 0.12、TF 2.21 derivative/interfaces。
5. Torch/Autograd focused。
6. 完整、未缩减的 28 段 scripts/run_local_matrix.sh，保存 shell exit。
7. Compileall、受控 legal、privacy/security、no-token/no-vendor。
8. 五环境版本及实际 import origins、pipcheck。
9. 最终 production/tests/examples、export、staged tree 一致性验证。

每项保存完整 .log、独立 .exit 和耗时。历史 coverage 为 90.45969876172117%，68 exclusions
不增加；不得以行覆盖率代表 SDK 功能对等率。七个依赖未安装的生态子集必须如实标记
NOT_EXECUTED。Quafu/QOS/Runtime 离线测试不能当作云或真机验证。

#### Task 3 — 有界功能验收

仅对本批真实实现的函数切片逐项判断：

- Full-system Operator composition；
- Mapped square/rectangular Operator composition；
- front 与左右乘法；
- 非连续/反序 qargs；
- input/output mixed dimensions；
- Operator 与 State 数值组合一致性；
- 真实资源准入及结果生命周期。

保留明确限制：

- Local subsystem-count change：Unsupported；
- Public negative/repeated/bool qargs：Partial Compatibility；
- Public Operator.power 浮点等扩展：Partial；
- 公开 Statevector 最小差异：PUBLIC_DIFFERENTIAL_MISMATCH；
- General channels/circuits：本批未实现。

不得将本次测试通过扩展表述为完整 Operator、State 或 SDK parity。

#### Task 4 — 限定提交

只有所有必要本地门禁满足验收条件后：

- 仅 stage P0.3 归属文件；
- 核对 staged 与 frozen tree；
- 正常本地 commit；
- 提交后再次比较 production/tests/examples；
- 报告真实 commit SHA。

不得触碰用户 Studio/Router，不修改认证/TLS，不读取 token，不访问云/硬件，不 push，
不 force/rebase/reset/amend，不创建 tag/release，不 vendor。
没有本轮提交 SHA 的远端 CI 证据，必须标记 NOT_VERIFIED。

#### Task 5 — 交付报告

输出：

- 实际 native composition 能力；
- 红灯与修复；
- 独立数学及 Qiskit 2.4.1/2.6 差分；
- 公开 Statevector 最小反例；
- 三环境 FULL；
- 独立框架专项；
- Coverage；
- 28 段 matrix 实际退出码；
- Frozen/committed tree 一致性；
- 本地 SHA；
- 仍未实现的核心函数。

不要在 P0.3 最终报告中启动 P0.4 或其他下一批开发。

现在冻结 P0.3，并执行完整门禁。暂时不需要新增 allocator、facade、Channel、Circuit、RNG
或 Studio 工作。完成全部测试后，再依据最终结果判断本批哪些 Operator 函数切片可以列为
Verified Native，哪些仍属于 Partial Public Compatibility。
最高目标继续保持 Qiskit + PennyLane 完整独立原生 full functional parity/full replacement：
ACTIVE / INCOMPLETE。C3 仍为 PARTIAL，Studio 最后。

## Received Next Batch Prompt: P0.4

The designated response completed on 2026-10-21 after the actual P0.3 code SHA
and final receipts were reported. The full implementation prompt is transcribed
below in Markdown. This is the NEXT execution segment, not a P0.3 implementation
or acceptance claim. Later checkpoint-receipt commits are documentation only;
the stated baseline is the actual P0.3 code commit.

### QuantumBridge Stage 12-A P0.4 — Native Mixed-Radix Observable Expectation

#### 0. 基线和目标

当前已提交 HEAD：`be9d5e3fbdd50aaa80cf975bf88f00246e260dfd`

本批只实现现有 Statevector/DensityMatrix 的 mixed-radix observable expectation 能力，
以及必要的现有 Operator 数学复用。必须真正计算：

`<O>_psi = <psi|O|psi>`

`<O>_rho = Tr(rho O)`

这里 O 可以作用于指定的 qubit、qutrit、qudit 或混合维度子系统。不得通过新建 facade、
调用 Qiskit/PennyLane 执行器、把 qudit 当多个 qubit、或默认展开完整系统 observable
来代替原生实现。

#### Task 1 — 公开 API 黑盒契约调查

先审计仓库真实签名，然后在已安装 Qiskit 2.4.1 和 2.6 中调用公开 API：

- `Statevector.expectation_value(oper, qargs=...)`
- `DensityMatrix.expectation_value(oper, qargs=...)`
- Operator 与对应 observable 的受支持构造
- Typed mixed-radix operator 输入/输出维度
- 非连续、反序 qargs
- 非 Hermitian observable 的复数返回
- 重复、非法、越界 qargs
- 总维度不匹配及局部维度不匹配
- 空 qargs、标量 observable（仅按真实公开契约）
- qubit-only Pauli 输入在 mixed-radix state 下的实际边界

注意：公开 Statevector/DensityMatrix 是否具有某个 variance 方法必须先核实；本批不新增
凭空推测的 variance() API。记录两个版本的返回类型、数值、异常及真实差异。
黑盒结果是兼容性依据，不是 native 测试通过次数。

#### Task 2 — 先建立真实数学红灯

至少覆盖：

1. (3,) qutrit 上的对角 observable，计算非均匀概率分布的期望。
2. (3,) qutrit 上含复数非对角元素的 Hermitian observable。
3. (2,3) 中仅对 qutrit 作用的 observable。
4. (2,3,2) 中对 (0,2) 的两体 observable。
5. 同一系统中反序 qargs (2,0)。
6. 含复相位的 qubit-qudit 纠缠态。
7. DensityMatrix 混态与纯态外积一致性。
8. 非 Hermitian observable 返回真正的复数期望。
9. 非连续 State/Operator ndarray。
10. 合法 zero-qubit/标量边界。
11. 错误维度、重复 qargs、foreign ndarray 拒绝。
12. 数值正确但 observable 输入/输出 dims 不符合要求的反例。

保存每条 red 的独立日志、退出码以及独立数学期望。不要修改正确旧测试来制造新红灯。

#### Task 3 — 最小原生实现

复用 P0.1–P0.3 的现有 mixed-radix subsystem mapping、Statevector/DensityMatrix、
Operator 与 utils.math。核心要求：

Statevector：根据真实 dims 和 qargs，在已有原生映射规则下计算 O|psi>，再与原态计算
复数内积。不得无条件归一化中间态。

DensityMatrix：根据真实 dims 和 qargs，计算 Tr(rho O)。允许通过已受控的小规模局部
contraction 或直接索引完成。不得先构造完整 D x D embedded observable，除非本来
就是 full-system operator。

Observable 验证：

- 局部 expectation 所用 observable 必须是维度保持型方阵。
- 区分 Hermitian 与非 Hermitian。
- 对非 Hermitian 结果保留虚部。
- 不将 complex dtype 静默转换为 float。
- 保留 native q0-first 与实际 subsystem dims。
- 不改变已有 qubit Pauli expectation 的正确路径。

实现应共享局部索引/stride 规则，而不是创建第二套 observable engine。

#### Task 4 — 两套独立数学 Oracle

必须使用：

Oracle A：显式基态枚举。独立生成小规模局部 embedded matrix，计算复数期望。

Oracle B：Tensor contraction / partial trace。独立求出目标子系统 reduced density，
再计算局部 trace。

两个 oracle 不得共用 production 的 qargs-to-stride helper。测试包括：

- 非均匀 qutrit 态；
- 纠缠态；
- 混态；
- 非对角复数矩阵；
- 非 Hermitian observable；
- qargs 非连续与反序；
- 复相位；
- mixed dimensions。

对于合法 Hermitian observable，检查结果虚部在数值容差内接近零；对于非 Hermitian
observable，不强制结果为实数。

#### Task 5 — 与现有量子算法组合验证

本批不开发新 VQE 算法，但必须通过一个真实原生端到端案例：

`mixed-radix Statevector → mapped Operator evolve → DensityMatrix → partial_trace → local expectation`

再加入一个真实参数化 observable 或参数化态的有限差分数学检查，证明 expectation 能
作为后续优化算法的数值目标。这里只验证数值函数，不新增参数移位框架、autodiff 系统
或 PennyLane QNode 接口。

#### Task 6 — 公开兼容差异

分别报告：

- Native 数学 oracle 是否通过；
- Qiskit 2.4.1 differential；
- Qiskit 2.6 differential；
- 维度、qargs 与返回类型差异；
- Unsupported 的 observable 类型。

特别保留 P0.2/P0.3 的 PUBLIC_DIFFERENTIAL_MISMATCH。不要利用新的 expectation 实现
修改已有正确 mapped evolution，以模仿尚未解释的公开 Statevector 行为。
对公开 API 行为没有证据的子集，应标记 UNVERIFIED，不能直接写 Supported。

#### Task 7 — 有界资源验证

只处理本批新增的局部 contraction、临时 state/reduced-density 和输出存储。必须验证：

- 已知 ndarray 在分配前预约；
- 不隐式构造整个系统 observable；
- 不连续数组的真实 copy 受控；
- 结果与临时 buffer 生命周期正确；
- valid → overbudget → valid；
- 非法输入在核心矩阵分配前拒绝。

不启动全局 allocator 审计，不重构 C3 资源系统。

#### Task 8 — 必须保护的现有回归

保留：

- P0.1 mixed-radix construction/propagation；
- P0.2 mapped State/Density evolve；
- P0.3 Operator composition；
- 100-qubit MPS non-dense；
- C2A second-adjoint/HVP；
- 64 shared parameters；
- QWC sample covariance；
- H2 native chemistry；
- Torch/Autograd/JAX/TF；
- QASM/QPY；
- Aer Noise/Save/Set；
- Result/Snapshot ownership；
- 已保存公开 Statevector 最小差异证据。

不得通过放宽容差、删除断言或扩大 exclusions 获取通过。

#### Task 9 — 最终门禁与提交

新增专项测试至少覆盖：

- 12 个 mixed-radix 数学场景；
- 8 个 qargs/ordering 场景；
- 6 个 Statevector/DensityMatrix 一致性场景；
- 6 个失败/资源/异常场景；
- 两版本公开 API 黑盒差分；
- 至少一个端到端 expectation 组合。

完成后冻结最终树，执行：

1. SDK-free FULL。
2. Main FULL + explicit coverage。
3. Alternate FULL。
4. 独立 JAX/TF、Torch/Autograd focused。
5. 完整 28 段 local matrix。
6. compileall、legal/privacy/security/no-token/no-vendor。
7. 五环境版本、import origins 和 pipcheck。
8. Workspace/export/tested/staged/committed tree equality。

Coverage 历史基线 90.47525850539844%，68 exclusions 不得增加。不能将覆盖率当作 API
完成率。全部必要门禁通过后，仅 stage P0.4 归属文件并正常本地 commit。
不得触碰用户 Studio/Router，不 push、不改 auth/TLS、不读取 token、不访问云/硬件、
不 vendor、不 tag/release、不改写历史。

#### Task 10 — 最终报告

报告：

1. 原生 Statevector/DensityMatrix expectation 的新增功能。
2. Mixed-radix qargs 与复杂 observable 数学。
3. 真实 red-green。
4. 两种独立数学 oracle。
5. 两版本公开 API 差分。
6. 非 Hermitian 复数行为。
7. 与 mapped evolve、partial trace 的组合。
8. 资源及错误边界。
9. 三环境 FULL、coverage、28 段 matrix。
10. 本地提交和远端 CI 真实状态。
11. 仍未实现的真实核心功能。

不得称 State/Operator 模块或完整 SDK 已实现 full parity。

#### 为什么优先做 Expectation，而不是 Channel？

目前已有的 Operator 局部作用和 composition 解决了“如何变换量子态”，但还缺少足够
通用的“如何从量子态计算物理可观测结果”。补齐 mixed-radix expectation 后，同一原生
数学基础便能支持更多 Hamiltonian evaluation、优化目标、量子线路验证及后续量子化学
与 PennyLane QNode 使用场景。这不意味着本批直接实现这些高级模块；本批只交付真实的
原生可观测量期望计算。

明确执行要求：现在启动 Stage 12-A P0.4，先完成 Qiskit 2.4.1/2.6 公开 expectation_value
行为调查，然后保存真实 mixed-radix 数学红灯，复用既有 native subsystem kernel 实现
最小修复，完成双 oracle、差分和最终全量门禁后再提交。

完整 Qiskit/PennyLane full native functional replacement 继续保持 ACTIVE / INCOMPLETE，
C3 仍 PARTIAL，Capture/Studio 不进入，Studio 最后。

## Received Next Batch Prompt: P0.5

The designated response completed on 2026-10-22 (Asia/Shanghai) after the actual
P0.4 code SHA and terminal gates were reported. It accepts only the reported
bounded native slice, not an independent source/log audit or remote CI. The
complete next execution prompt is transcribed below; this is NOT P0.5
implementation or acceptance. The stated baseline is actual P0.4 code; later
checkpoint/prompt receipt commits are documentation only.

### QuantumBridge Stage 12-A P0.5 - Native State Arithmetic, Purity & Core State Semantics

#### 0. 基线、最高目标和边界

当前 committed HEAD：`84623f0d3a7915aaccc57c1b45293490efaac334`。
P0.4 已完成本地受控功能切片验收。最终目标保持：Qiskit + PennyLane 完整核心函数库的
独立原生实现、真实可调用功能及 full functional parity / full replacement：
ACTIVE / INCOMPLETE。C3 保持 PARTIAL。

本批只扩展现有 Statevector、DensityMatrix 的真实数学能力，不新建状态模拟器、SDK
facade、上游 passthrough 或新的资源管理体系。不进入 Stage 11P-D/Capture/Studio。

#### Task 1 - 两版本公开 API 黑盒调查

先检查 QuantumBridge 的真实类、已有签名和现有测试，再在 Qiskit 2.4.1、2.6 环境调用
公开 API。至少调查：

Statevector：

- `__add__`、`__sub__`；
- `__mul__`、`__rmul__`；
- `__truediv__`（仅当公开对象确实支持）；
- `__neg__`；
- `inner()`；
- `is_valid()`；
- `purity()`；
- `to_dict()` 及实际支持的相关参数。

DensityMatrix：

- 加减与标量乘法；
- 反向标量乘法；
- 除法及负号的实际支持情况；
- `trace()`；
- `purity()`；
- `is_valid()`；
- `to_dict()`。

记录：

1. 方法是否真实存在；
2. 输入类型；
3. 返回对象类型；
4. `dims()` 传播；
5. 对复数、非有限数值及未归一化输入的行为；
6. 公开异常；
7. 两个版本的真实差异。

不得为追求表面 API 数量而创造上游不存在的方法。如果公开 Statevector.purity() 不存在
或行为不同，必须以实际实验为准；不能继续沿用先前的缺口猜测。

#### Task 2 - 建立真实红灯

在当前 native 代码上，至少保存以下修复前失败案例：

1. Statevector 同维度线性相加。
2. Statevector 相减及复数标量乘法。
3. 不同 subsystem partition 但总维度相同的状态相加。
4. DensityMatrix 加权组合。
5. DensityMatrix 复数/实数标量运算的真实支持边界。
6. 未归一化 Statevector 的 inner/norm。
7. DensityMatrix trace 与 purity。
8. 混合态 purity 小于纯态 purity 的明确数值例子。
9. 非连续 state buffer 的运算。
10. 非法维度、foreign ndarray 和非有限值处理。
11. Arithmetic 结果数值正确但 mixed-radix dims 丢失。
12. 资源不足时 NumPy 输出在预约前已经分配。

对于已经正确实现的函数，只做回归，不把它伪造为新增红灯。红灯日志必须分别记录数学
错误、功能缺失、API 契约不一致和测试作者错误。

#### Task 3 - Statevector 原生线性代数

复用既有数值数组、mixed-radix dimensions 和 ResourceScope。对公开契约确认支持的
操作，实现：

- 状态加法、减法；
- 标量乘法；
- 受支持的相反数；
- `inner()`；
- 有依据的 norm/validity 行为；
- 必要的 `to_dict()` 数值导出。

数学不变量：`(alpha |psi> + beta |phi>)_i = alpha psi_i + beta phi_i`。
保留复振幅，不偷偷归一化。对于 mixed-radix dimensions：

- subsystem partition 匹配时正常运算；
- partition 不同时按核实的公开语义决定接受、拒绝或标记 Partial；
- 不把 `(2,4)` 与 `(2,2,2)` 当成无条件相同的子系统结构。

必须验证状态线性组合与 density matrix 物理混合的区别。

#### Task 4 - DensityMatrix 算术与 Purity

按已确认的公开契约实现原生：

- density matrix 加减；
- 标量乘法；
- trace；
- purity；
- validity；
- 受支持的导出。

使用真实 NumPy 线性代数或已有原生 kernel，不引入上游 SDK。
重点数学：`Tr(rho^2) = sum_(i,j) rho_ij rho_ji`。
对于 Hermitian density matrix，等价于元素模平方求和，但通用数值定义不能假设所有
输入已严格 Hermitian。独立验证：

- 纯态：purity = 1；
- 最大混合 qubit：purity = 1/2；
- 最大混合 qutrit：purity = 1/3；
- 非归一化矩阵的 trace/purity 缩放；
- 合法凸混合保持 Hermiticity、PSD 和 trace 1；
- 非物理输入按公开契约处理，不偷偷修复成物理态。

不要把 Statevector 振幅相加误当作 DensityMatrix 概率混合。

#### Task 5 - 两套独立数学 Oracle

Oracle A：显式 NumPy 向量/矩阵计算。独立构造复杂复数输入，并计算运算结果、inner、
trace 和 purity。

Oracle B：解析或谱分解。例如使用对角混态本征值的平方和验证 purity，再构造带相干项
的 Hermitian density matrix。必须覆盖：

- `(2,4)`、`(3,2)`、`(2,3,2)`；
- 单 qutrit/qudit；
- noncontiguous/strided arrays；
- complex amplitudes；
- zero states；
- non-normalized states；
- dimensions mismatch。

不共享 production 数值 helper 作为 oracle。

#### Task 6 - 真实跨函数组合

必须实现并测试：

组合 A：状态线性叠加

`Statevector basis -> scalar multiplication -> addition -> norm/inner -> expectation`

组合 B：物理混合态

`Statevector psi1/psi2 -> DensityMatrix -> weighted mixture -> purity -> partial_trace -> expectation`

组合 C：mixed-radix

`from_int -> tensor -> State arithmetic -> DensityMatrix -> mapped evolve -> expectation`

这里可直接复用 P0.1-P0.4 的原生功能，不重复实现 evolve、partial_trace 或 expectation。

#### Task 7 - 公开 API Differential

在 Qiskit 2.4.1、2.6 的公开入口运行相同输入。分别对照：

- 数值；
- dimensions；
- 返回类型；
- 异常；
- `to_dict()` 的真实键格式；
- purity / validity；
- 边界值。

对 QuantumBridge 原生语义和公开行为不同的情况，必须记录 Partial Public Compatibility。
既有 P0.2/P0.3 PUBLIC_DIFFERENTIAL_MISMATCH 继续保留原始字面案例，不通过本批状态
算术改写已有 mixed-radix 核心数学。

#### Task 8 - 有界资源与错误行为

只审计本批新增的输出数组和已知临时数值缓冲：

- 在分配前计算 shape/dtype/bytes；
- 复数类型不发生静默截断；
- 不连续数组的真实 copy 预约；
- 按 ndarray root 保留 lease；
- valid -> overbudget -> valid；
- 数值错误不导致旧对象部分修改；
- foreign protocol 未经许可不得执行。

不开展新一轮全局 allocator 审计。

#### Task 9 - 回归保护

必须保护：

- P0.1 mixed-radix dimensions；
- P0.2-A mapped evolve；
- P0.3 Operator composition；
- P0.4 local expectation；
- C3 State/Result ownership；
- 100-qubit MPS；
- C2A second-adjoint/HVP；
- 四框架；
- H2；
- QASM/QPY；
- Aer Noise/Save/Set；
- 既有公共差异字面证据。

不放宽数值容差，不修改正确旧断言，不新增 coverage exclusions。

#### Task 10 - 冻结与完整门禁

在功能及 focused 回归结束后冻结完整 production/tests/examples。必须执行：

1. SDK-free FULL。
2. Main FULL + explicit coverage。
3. Alternate FULL。
4. 独立 JAX/TF。
5. Torch/Autograd focused。
6. 完整 28 段 local matrix，保存实际 shell exit。
7. Compileall、legal/privacy/security/no-token/no-vendor。
8. 五环境真实版本、import origins 和 pipcheck。
9. Frozen/export/workspace/staged/committed tree equality。

Coverage 历史基线：90.49588122293491%，68 exclusions 不增加。不得通过删除已有测试、
增加排除或放宽容差取得全绿。七个可选生态依赖子集缺失时继续标记 NOT_EXECUTED。
Offline Quafu/QOS/Runtime 不冒充真机验证。Whole dirty workspace Router legal 失败与
controlled legal 通过必须分开记录，不碰用户文件。

#### Task 11 - 限定本地提交

全部必要门禁达到验收条件后，只 stage Stage 12-A P0.5 的归属文件，并正常本地 commit。
不 push；不修改用户 Studio/Router；不改 auth/TLS；不读取 token；不调用云/硬件；不
vendor、tag/release、force、reset、rebase 或 amend。远端 CI 标记 NOT_VERIFIED，
不得借用旧 SHA 结果。

#### Task 12 - 最终交付报告

提交：

1. 真正新增的 Statevector/DensityMatrix API。
2. 公开契约调查结果。
3. 红灯和原生修复。
4. 复数数学、mixed dimensions、trace/purity。
5. 三条组合执行链。
6. 两套独立 oracle。
7. Qiskit 2.4.1/2.6 差分。
8. 实际资源/异常边界。
9. 三环境 FULL、coverage、28 段 matrix。
10. 本地 SHA、远端 CI 状态。
11. 保留的 Partial/Unsupported API。
12. 后续真正缺失的核心函数优先级。

#### 最终执行要求

正式启动 Stage 12-A P0.5，先完成 Statevector/DensityMatrix 公开算术、inner、trace、
purity、validity 和导出接口的黑盒合同调查。然后根据真实结果进行 red -> native
implementation -> 两种独立数学 oracle -> 公共差分 -> 组合调用 -> 最终同树质量门禁。

此批只交付可实际执行的核心数学函数，不增加大型兼容 facade、不启动 general
channels/Capture/Studio，也不把项目转成纯资源治理。

完整 Qiskit/PennyLane 独立原生 full functional parity / full replacement 仍为
ACTIVE / INCOMPLETE；C3 PARTIAL，Studio 最后。

### Received Closing Clarification: P0.5 Tasks 10-12

The initial AX delivery ended at Task 9 while showing a completed marker; the
original Tasks 10-12 arrived with a later observation during the clarification
send. The complete original prompt above is retained. The subsequent completed
reply below expands the SAME closing requirements; it adds no functional scope
and governs final gate/receipt details. Tasks 0-9 stay unchanged.

确认，完全沿用原有门禁、提交和安全边界。以下内容直接接在已保存的 P0.5 Prompt
Task 9 之后，作为 Task 10-12。无需修改或重复 Task 0-9。

#### Task 10 - 最终冻结与完整质量门禁

完成 P0.5 原生功能开发、真实 red->green、独立数学 oracle 和公开 API 差分后，冻结
production/tests/examples，使用独立 Git index/export 记录唯一受测 tree SHA。
在同一冻结树上执行：

1. SDK-free FULL pytest：不得依赖 Qiskit、PennyLane 或四个 AD 框架作为原生执行后端。
2. Main FULL pytest + explicit coverage：保存完整结果、coverage JSON 和真实退出码。
3. Alternate FULL pytest：验证备用 Qiskit/PennyLane 版本组合。
4. 四框架回归：独立 JAX、独立 TensorFlow，以及 Torch/Autograd 专项测试。
5. 完整 28 段 local matrix：执行原始 scripts/run_local_matrix.sh，不得缩减、替换为
   focused tests 或借用历史结果。保存 28 个 section 状态、完整日志及独立 shell exit。
6. 合规与环境检查：compileall、controlled legal、privacy/security、no-token/no-vendor、
   五环境版本和实际 import origins、pipcheck、git diff --check。
7. 最终源码一致性：确认 workspace/export/tested tree 的 production/tests/examples 完全一致。

Coverage 历史基线：90.49588122293491%；excluded 68，不得增加。不得通过删除测试、
放宽容差或新增 exclusion 维持覆盖率。代码行覆盖率不代表 API 功能完成率。

Finance/Optimization/ML/Dynamics/Metal/Experiments/Addons 等依赖缺失的子集继续明确
标记 NOT_EXECUTED；离线 QOS/Quafu/Runtime 不冒充云或真机验证。既有 main/alternate
pip 依赖冲突如实披露。Whole dirty workspace 的 Router ledger 失败与 controlled
export legal 通过必须分别记录，不能相互替代。如果出现真实回归：

- 保存原始失败日志及 .exit。
- 区分 production 缺陷、测试作者错误和已证实过时的断言。
- 最小范围修复，不放宽正确数学标准。
- 重新冻结源码，并在最终新树上重跑必要的完整门禁。
- 不得复用旧冻结树的绿色结果。

所有必需测试和 matrix 进程必须真实终止后，才能进行最终验收和提交。

#### Task 11 - Scoped 本地提交

仅当 Task 10 所有必要门禁满足既定验收条件后：

1. 核实当前 HEAD 和工作区状态。
2. 明确列出 Stage 12-A P0.5 归属文件。
3. 仅 stage 这些文件，不使用 git add .。
4. 核对 staged production/tests/examples 与最终受测树一致。
5. 正常本地 commit，不 amend。
6. 提交后再次核对 committed tree 与最终受测版本一致。
7. 报告真实 commit SHA、文件数量和改动摘要。

必须完整保留用户 Studio/Router 的未提交及未跟踪文件。禁止事项：

- 不 push，除非 Owner 后续明确恢复授权且完成 fresh fast-forward 核验。
- 不修改 OAuth、认证、TLS 或 Git 凭证。
- 不读取、输出或传送 token/private keys。
- 不调用真实云服务或量子硬件。
- 不 vendor 上游源码、wheel、site-packages。
- 不 force、reset、rebase、amend 或改写历史。
- 不创建 tag/release。
- 不进入 Capture/Studio。
- 不启动新的全局 allocator 审计。
- 不新增第二套 State 数学引擎或上游 SDK passthrough。

新提交的远端 CI 必须标记 NOT_VERIFIED，不得借用历史 SHA 的 CI 状态。

#### Task 12 - P0.5 有界验收及最终报告

输出一份完整 Stage 12-A P0.5 实施报告，至少包括：

1. 公开契约调查：Qiskit 2.4.1/2.6 实际存在的 Statevector/DensityMatrix 方法、签名、
   异常和返回行为；明确不存在或不支持的接口。
2. 真实新增原生功能：逐函数列出新增、修复、原已正确以及仍 Unsupported 的部分。
3. Red->Green 证据：原始失败数量、根因、修复和最终专项测试结果，区分测试错误与生产缺陷。
4. 独立数学验证：复数状态算术、inner、trace、purity、dimensions 和未归一化行为，
   仅报告实际验证的函数。
5. 公开 API 差分：分别统计数值通过、异常差异、metadata 差异和未解决 mismatch，
   不把 probe records 当成 native passed tests。
6. 真实组合执行：Task 6 的三条 State/Density 数学调用链及其数值结果。
7. 资源及所有权：本批新增数组的分配前预算、root/view 生命周期和失败恢复；
   外部内存限制照实披露。
8. 完整门禁收据：SDK-free/main/alternate FULL、四框架专项、coverage JSON、28 段
   matrix shell exit、compile/legal/privacy/security、五环境 origin/pip。
9. 冻结与提交一致性：tested tree、export、workspace、staged、committed 的核对结果及本地 SHA。
10. 明确剩余缺口：完整 State/Operator/Channel/QNode/Circuit 等尚未实现或未验证的核心
    函数、公开兼容问题及下一批候选方向。

只将证据充分的具体函数切片认定为 Verified Native，其余保留 Partial / Unsupported /
Unverified。报告必须明确：QuantumBridge 完整独立原生 Qiskit/PennyLane full functional
parity / full replacement：ACTIVE / INCOMPLETE。Stage 11P-C3：PARTIAL。
Studio 最后，不在本批启动。

最终执行要求：原样保留 Task 0-9，追加上述 Task 10-12，然后按完整 P0.5 Prompt 开始
执行。本批完成后先报告真实运行和本地提交结果，再决定下一批核心函数开发；
不提前扩大当前范围。
