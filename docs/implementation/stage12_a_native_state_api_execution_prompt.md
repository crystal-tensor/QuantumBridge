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

## Stage 12-A P0.6 Received Execution Prompt

Received 2026-10-22 from the designated conversation after reporting the actual
P0.5 code SHA and terminal receipts. An initial full snapshot displayed a
completion marker after Task 10; a later snapshot exposed Task 11 and the
closing execution paragraph. Both are now included below. No missing-task
regeneration was requested. Formatting is normalized, including the tensor-index
equation transcribed as ASCII.
This is a report-based task recommendation, not an independent source/log audit.

### P0.5 有界判断及下一批选择

根据你提供的完整执行记录，P0.5 可以认定为已完成本地受控验收的原生核心函数切片，
并进入下一批开发。本次判断仅依据你的报告，不代表独立检查了本地源码、原始日志或
远端 CI。本地提交 87076d532084f993...，完整 28 段 Matrix exit 0，Main FULL
4032 passed，行覆盖率 90.6213%。

Statevector/DensityMatrix 算术、复数 purity、混合维度传播、公开有效性校验及三条
组合执行链已有原生计算和数学验证依据。发现 Fraction 回归之前的 v1 门禁已废弃，
重新冻结 v2 并全量验证。验收范围限定在已验证函数。Density-Statevector coercion、
tolerance 配置、公开异常契约、P0.2/P0.3 差分仍 Partial。既有 pip 冲突、七个
NOT_EXECUTED 子集、Router 工作区 legal 失败、新 SHA 远端 CI 未验证均保留原状态。

建议下一批是 Stage 12-A P0.6 - Native Mixed-Radix Subsystem Operations:
Permutation, Reduction & Local State Algebra，不选择 channels，不重复 P0.5 算术。
当前已有构造、演化、组合、期望和算术；应先确认子系统重排、维度跟踪和约化态操作
的真实缺口，为 Circuit、channels、PennyLane wires 和 observable transforms 复用。
不能凭应该有某方法就新增公开 API；先调查现有实现及 Qiskit 2.4.1/2.6 黑盒行为。
已有正确 partial_trace、reverse、tensor 等只做回归，没有真实缺口不重写。

### QuantumBridge Stage 12-A P0.6 - Native Mixed-Radix Subsystem Permutation & Reduction

#### Task 0 - 基线、目标和硬边界

当前已提交 HEAD: 87076d532084f993842859318802ef8155455776。
P0.5 已完成本地受控验收。C3 仍为 PARTIAL。

最终目标继续保持：独立原生实现 Qiskit/PennyLane 全部核心功能，真正的 full
functional parity / full replacement，ACTIVE / INCOMPLETE。
本批优先解决 Statevector/DensityMatrix 子系统排列和约化操作中的真实功能缺口，
不是建立 facade、重写已有 state engine 或增加一轮资源管理工程。

#### Task 1 - 先确认真实缺口

先阅读 QuantumBridge 当前公开方法、原生实现及已有测试，确定以下能力是否正确实现：

- Statevector/DensityMatrix 的 reverse_qargs() 或实际对应方法。
- Statevector/DensityMatrix 子系统维度排列与传播。
- DensityMatrix 的 reduced-state / partial-trace 真实入口。
- partial_trace 对非连续、反向 qargs 的执行。
- dims=(2,3,2)、(3,2,4) 等 mixed-radix 系统的子系统保留或丢弃。
- 重排后的 evolve()、expectation_value()、probabilities()、measure() 调用。

在 Qiskit 2.4.1/2.6 使用真实公开 API 黑盒核实方法、参数、返回类型、维度、qargs、
异常行为。特别区分子系统置换（张量因子及对应振幅/矩阵索引排列）、Statevector
数组反转（不一定等价于任意子系统置换）和 partial trace（对子系统求迹，不是矩阵块截取）。
不得臆造 Qiskit 公共方法。如果公开 API 不支持任意 permutation，优先补现有原生操作
实际能力，额外数学能力明确标记 QuantumBridge native extension。先形成函数级证据
清单，已正确实现的只做回归，不重复开发。

#### Task 2 - 建立真实 Red

仅针对 Task 1 已证实缺口建立失败测试，优先考虑：

1. (2,3,2) 的真实子系统反向排列，振幅索引正确变化。
2. (2,3,4) 中不同维度子系统交换后的 output dims。
3. (2,3,2) 保留第 0、2 子系统的约化 DensityMatrix。
4. 保留子系统顺序不同造成的 output basis ordering 差异。
5. 复相位纠缠态的 partial trace，非对角相干项。
6. 非连续和 strided state/density 输入。
7. 重排后局部 mapped evolve 数值及 dims。
8. 重排后 local expectation 的 qargs 语义。
9. 重复、越界、非法 subsystem targets。
10. 输出数值正确但 dims 错误的反例。

保存原始 red 日志及独立 exit，区分真实缺失、数学错误、公开兼容差异和测试设计错误。
已经正确的项不得人为制造失败。

#### Task 3 - 最小原生数学实现

复用 Statevector/DensityMatrix、mixed-radix dimensions 和 stride/index、utils.math、
native partial trace、现有 ResourceScope/ArrayOwnership。确实缺失的子系统重排使用
受控张量轴排列或 mixed-radix basis-index 映射。对合法 permutation p，Statevector 满足：

```text
psi'[i_p(0), ..., i_p(n-1)] = psi[i_0, ..., i_n-1]
```

DensityMatrix 对行和列两组子系统索引施加同一个 permutation。真实 partial trace
使用正确维度张量收缩，保证保留维度、复数非对角项、trace 正确；合法物理输入约化结果
保持 Hermitian、PSD 和 trace；不把 qutrit/qudit 自动拆成 qubits。尽可能复用已有
reshape/transpose/trace 数值路径，不另造 tensor simulator。

#### Task 4 - 两套独立数学 Oracle

Oracle A: mixed-radix 基态枚举，显式计算 input/output basis index，逐元素验证
permutation/reduction。Oracle B: 独立 NumPy 张量轴排列和约化收缩，不调用 production
helper。至少验证 product states、Bell-like/qudit-entangled states、非均匀复振幅、
混合密度矩阵、不同子系统维度、非连续/反向 targets 和 reduced density 非对角元素。
定义适用时置换与逆置换组合返回原态，不以仅比较概率/trace/purity 代替完整复矩阵比较。

#### Task 5 - 真实组合执行

至少两个独立 native 调用链：

```text
A: Mixed Statevector -> subsystem permutation/reverse -> mapped Operator evolve
   -> local expectation
B: Mixed Statevector -> DensityMatrix -> partial trace -> reduced DensityMatrix
   -> expectation/purity
```

两条链都检验实际复数数值、子系统维度和 qargs；已有正确函数直接调用，不重新实现。

#### Task 6 - 公开差分与兼容边界

Qiskit 2.4.1/2.6 公开 API 黑盒验证实际可比操作，分别报告 native mathematics、public
numerical equivalence、public metadata equivalence、public exception/return
contract、native-only extension、Unsupported/Unverified。
保留 native q0-first、dict probabilities、DensityMatrix shape-tuple dim 历史契约。
不得修改 P0.2/P0.3 PUBLIC_DIFFERENTIAL_MISMATCH，不为逐字一致破坏独立数学正确性。

#### Task 7 - 有界资源与回归

只管理本批新增实际 ndarray 输出及已知临时 buffer，测试分配前预算、真实 root/view
生命周期、非连续数组、维度积溢出、valid -> overbudget -> valid、拒绝后原态不变。
不启动全局 allocator 审计，保护 P0.1-P0.5、C2A/C3、MPS 100-qubit、四框架、H2、
QASM/QPY、Aer 和既有 Result/Snapshot。

#### Task 8 - 功能范围停止条件

只修复 Task 1 已证实的 subsystem permutation/reduction 缺口。若现有实现完整覆盖
本批全部数学操作，不得为完成任务发明 API 或包装层；报告 NO_NEW_FUNCTIONAL_GAP，
附现有原生调用证据，结束本批，不作虚假功能提交，下一阶段再选真实缺失核心函数。
不扩展 general channels、circuit execution、RNG、fractional Operator.power、
PennyLane Capture、Studio 或其他新方向。

#### Task 9 - 最终冻结和完整门禁

真实新增功能及专项回归完成后，冻结 production/tests/examples，记录唯一受测 tree SHA。
同树执行：

1. SDK-free FULL pytest。
2. Main FULL pytest + explicit coverage。
3. Alternate FULL pytest。
4. 独立 JAX/TF、Torch/Autograd focused。
5. 原始完整 28 段 scripts/run_local_matrix.sh，保存最终 shell exit。
6. Compileall、controlled legal、privacy/security/no-token/no-vendor。
7. 五环境真实版本、import origins、pipcheck。
8. Frozen/export/workspace/staged/committed production/tests/examples 一致性。

覆盖率基线 90.62125675806922%，excluded 68 不增加；不删测、不放宽容差、不新增
exclusion 求通过。Finance/Optimization/ML/Dynamics/Metal/Experiments/Addons 缺依赖
标 NOT_EXECUTED。QOS/Quafu/Runtime 离线结果不冒充真机。Whole dirty workspace Router
ledger 失败与 controlled-export legal 通过分开报告，不改用户 Router；如实披露历史
pip 冲突。真实回归保存失败证据、最小修复、重新冻结并重跑必要完整门禁。

#### Task 10 - Scoped 本地提交

所有必要门禁通过后，仅 stage 明确归属文件，核对 staged tree 与最终受测 tree，正常
本地 commit，再核对 committed production/tests/examples 一致性，报告实际 SHA。
不触碰用户 Studio/Router；不 push、不改认证/TLS、不读 token、不调用云/硬件、不
vendor/tag/release、不 force/reset/rebase/amend。仅 Owner 后续明确恢复授权且完成
fresh fast-forward 核验才重新考虑正常 push。新提交远端 CI 为 NOT_VERIFIED。

#### Task 11 - 最终验收报告

报告：

1. 实际存在且被修复的函数级缺口。
2. 公开 Qiskit 2.4.1/2.6 契约调查。
3. 原生 subsystem permutation/reduction 数学。
4. Red->green 及独立退出码。
5. 两套独立数学 oracle。
6. 两条真实组合执行链。
7. Native/Public 兼容差异。
8. 新增数组资源边界。
9. SDK-free/main/alternate FULL。
10. 四框架专项、coverage、28 段 matrix。
11. Frozen/staged/committed equality 与本地 SHA。
12. 未实现核心函数及本批限制。

只对证据完整的具体功能切片标记 Verified Native。

### 明确执行要求

现在启动 Stage 12-A P0.6。第一步不是编写新代码，而是核实子系统置换和 mixed-radix
reduction 在现有 Statevector/DensityMatrix 中究竟还缺什么。只有发现真实缺口，
才按 red -> 原生最小修复 -> 独立数学 oracle -> 公开差分 -> 完整门禁 -> scoped
commit 执行。整个项目继续以完整 Qiskit/PennyLane 原生函数库替代为最高目标，
绝不把当前 90.62% 行覆盖率解释为 SDK 完成度。C3 PARTIAL，不进入 Capture/Studio，
Studio 最后。

## Stage 12-A P0.7 Received Execution Prompt

Received 2026-10-22 from the designated conversation after the evidence-first
P0.6 audit. This is report-based collaboration, not independent source/log audit.
Formatting and equations are normalized here; all functional and gate requirements
are retained. An initially completed-marked snapshot ended at Task 11; a request
for the tail was sent before a later snapshot exposed original Tasks 12-13.
Both the original tail and the completed supplemental reply were read. The
supplement clarifies the same scope, not a new feature or a product red.

### P0.6 Decision And P0.7 Scope

确认 P0.6 原调查范围为 NO_NEW_FUNCTIONAL_GAP_IN_SURVEYED_EXISTING_OPERATIONS。
432 组断言支持被调查原生函数的数学，不等于完整公开对等；公开异常和 metadata 差异
仍 Partial。下一批选择真实缺失的 DensityMatrix.partial_transpose(qargs)，复用现有
mixed-radix DensityMatrix 引擎，不再重写 reverse_qargs 或 partial_trace。

### Task 0 - 基线与范围

当前本地 HEAD ac34b6d79fc00291f72ea132248c822895057a74，P0.5 原生代码
87076d532084f993842859318802ef8155455776。P0.6 保持上述无新数学缺口结论。
不修改正确 reverse_qargs、partial_trace 及既有 native 契约。本批只实现既有
DensityMatrix 的 mixed-radix partial transpose，不开发 general channels、negativity
计算器、任意 subsystem permutation API 或新引擎。完整独立原生 Qiskit/PennyLane
full functional parity/full replacement ACTIVE / INCOMPLETE，C3 PARTIAL，Studio 最后。

### Task 1 - 公开 API 黑盒契约

在已安装 Qiskit 2.4.1/2.6.0 调查实际 DensityMatrix.partial_transpose(qargs) 类方法、
签名、参数和返回契约；覆盖 qubit/qutrit/qudit/mixed-radix dimensions，单个/多个、
非连续/反向、空/全部、重复/越界/bool/非法 qargs，Hermitian/非 Hermitian、归一化/
未归一化/非物理矩阵，dtype、dims、num_qubits、异常类型。分别保存两版本公开实验，
不读或移植上游源码和测试，不把 public probe records 算作 native passed tests。

### Task 2 - 先建立真正数学红灯

在未修改 DensityMatrix 上新增、执行测试，至少复现：

1. 单 qubit partial transpose 未实现。
2. 单 qutrit partial transpose 未实现。
3. (3,2) 纠缠 density 的真正 partial transpose。
4. (2,3,2) 的单个中间子系统。
5. (2,3,2) 非连续 (0,2)。
6. 多个 qargs 的反向选择。
7. 非 Hermitian 复矩阵的虚部或行列交换错误。
8. mixed-radix dims 正确但索引错误。
9. strided/noncontiguous 输入。
10. 合法输入但输出超过预算。

保存原始 red 和独立 exit，不人为破坏已正确 tensor/reshape/trace，测试作者错误与
production 缺陷分开报告。已经完成的 197 failed 初始红不需再次制造。

### Task 3 - 最小原生数学实现

在既有 DensityMatrix 类及共享 native 数值工具实现 partial_transpose(qargs)。
维度 d0,...,d(n-1)，行列多重指标 i,j，对所选子系统集合 S 交换 i[k],j[k]：

```text
(rho^T_S)[i,j] = rho[i',j']
i'[k] = j[k], j'[k] = i[k] for k in S; otherwise unchanged.
```

这是行列索引交换，不是 adjoint，不额外共轭。复用现有 dimensions、数组表示和
ResourceScope，不建第二套引擎；输入不变，输出分区不变；支持不同维度、非连续
qargs、complex128、strided、非 Hermitian。没有 normalization、PSD projection 或
物理态修正，不为局部 PT 构造全系统 superoperator。可用已有受控 tensor 重排，
必须保证实际 row/column 轴映射正确。

### Task 4 - 严格数学不变量

验证 (rho^T_S)^T_S=rho、Tr(rho^T_S)=Tr(rho)、rho^T_all=rho.T，后者不是共轭转置。
Hermitian 输入的 PT 保持 Hermitian，但不要求 PSD。纠缠态 PT 的负特征值不能截断。
对非 Hermitian、未归一化输入只检验适用线性代数，不强求物理密度矩阵性质。

### Task 5 - 两套独立数学 Oracle

Oracle A 显式枚举行列 mixed-radix basis index，交换选中行列数字并独立填充矩阵。
Oracle B 独立 NumPy 2n 维 tensor-axis 交换再恢复矩阵。都不得使用 production
stride/index helper。至少 (2,2)、(3,2)、(2,3,2)、(3,2,4)，以及纯态外积、混态、
非 Hermitian、未归一化、非连续输入；比较完整复矩阵，不只 trace/eigenvalues/probs。

### Task 6 - 公开 Qiskit 差分

两版本公开黑盒逐项对照完整复矩阵、dims/dim/num_qubits、qargs 顺序、返回类型、
空/重复/非法 qargs、异常类别和消息。明确 native q0-first 参数转换。边界行为不同
时分列 Verified Native Math 与 Partial Public Compatibility，不让 Qiskit 生成
生产结果，不为模仿未解释公开行为破坏 native 数学。

### Task 7 - 真实组合调用

```text
A: Mixed-radix Statevector -> DensityMatrix -> partial_transpose
   -> eigenvalue inspection
B: Mixed-radix Statevector -> mapped Operator evolve -> DensityMatrix
   -> partial_trace -> partial_transpose -> expectation
```

A 用 (3,2) 等真实纠缠输入，与公开两版及独立谱比较，原报告约
[-0.5,0,0,0.5,0.5,0.5] 例子必须按真实输入重算，不硬编码代替推导。
B 核对 dims、完整复矩阵、最终 expectation，实际调用既有 native kernel。
只允许测试中 NumPy eigenvalues 验证，不新增 negativity/monotone/channel API。

### Task 8 - 有界资源与异常

只管理新函数输出 ndarray 和可确定临时 workspace；证明分配前 shape/dtype/nbytes
确定且预约、非连续复制受控、root/view 生命周期、超限在真实 factory 前拒绝、
valid -> overbudget -> valid、失败不改输入、foreign ndarray protocol 不被擅自执行。
沿用 UnifiedResourceLedger/ArrayOwnership，不开全局 allocator 审计，不称严格 RSS 上界。

### Task 9 - 回归保护和停止边界

保护 P0.1-P0.5 mixed-radix State/Density、mapped evolve/compose、expectation、state
arithmetic/purity/validity、partial trace/reverse、C2A second-adjoint/HVP、100-qubit MPS、
四框架、H2、QASM/QPY、Aer Noise/Save/Set、Result/Snapshot ownership。保留 P0.2/P0.3
公开 mismatch 原始证据。本批不做 general channels、negativity、Circuit、Capture、
Studio、RNG、fractional Operator.power、全面 allocator 或新 public facade。

### Task 10 - 验收用例

至少 12 个 mixed-radix 完整复矩阵数学场景、8 个 qargs/顺序场景、6 个非 Hermitian/
未归一化/纠缠场景、6 个失败/预算/所有权场景、双版本实际公开差分及两条端到端链。
数字是最低要求，不以大量重复参数化代替独立数学覆盖。先真实 red，再最小 native
修复，再专项及广域回归。

### Task 11 - 冻结和完整质量门禁

冻结唯一 production/tests/examples，记录 tree SHA、export 路径和归属清单。同树执行：

1. SDK-free FULL pytest。
2. Main FULL pytest + explicit full coverage。
3. Alternate FULL pytest。
4. 独立 JAX、独立 TF、Torch/Autograd focused。
5. 原始完整 28 段 scripts/run_local_matrix.sh，实际 shell exit。
6. Compileall、controlled legal、privacy/security/no-token/no-vendor。
7. 五环境真实 versions、import origins、pipcheck。
8. Frozen/export/workspace/staged/committed production/tests/examples 一致性。

Coverage 基线 90.62125675806922%，excluded 68 不增加，不是功能完成率。
缺依赖 lanes 标 NOT_EXECUTED；QOS/Quafu/Runtime 离线不当作真机。Whole dirty workspace
Router ledger 与 controlled-export legal 分开披露。所有必要进程真实终止，完整日志及
独立退出码保留。回归先留失败证据、最小修复、重新冻结并重跑必要完整门禁，不借旧树绿。

### Task 12 - Scoped 正常本地提交与一致性核验

只在最终同树必要门禁达到既定验收条件且相关进程真实结束后提交：

1. 记录 frozen tree、production/tests/examples subtrees、独立 export 和归属清单。
2. 检查真实 index，仅 stage 本批 production/tests/字面公开证据/必要报告，不 git add .。
3. Tested/export/workspace/staged runtime 差异检查全部 exit 0。
4. git diff --cached --check，确认无无关、vendor 或用户 Studio/Router 改动。
5. 正常 git commit，不 amend 或历史改写。
6. Committed runtime 再比最终冻结树，保存退出码。
7. 报实际 SHA、文件数量、改动摘要、最终 tree SHA。

不触碰、暂存、提交用户 Studio/Router；不 push，除非 Owner 之后恢复授权且 fresh
fetch 证明正常 fast-forward；不改 OAuth/Git认证/TLS/凭证/workflow权限；不读取、输出、
传送 token/private keys；不云/真机；不 vendor 源码/测试/wheel/site-packages；不
force/reset/rebase/amend/tag/release；不 Capture/Studio/第二引擎/无界 allocator。
本地提交不等于远端验证，新 SHA CI 为 NOT_VERIFIED。门禁、一致性或范围失败不得提交；
留原始证据、最小修复、重新冻结并重跑必要门禁。

### Task 13 - P0.7 有界最终验收与完整实施报告

报告至少包括：

1. 新增 partial_transpose(qargs) 的签名、实际调用、mixed-radix 范围、返回契约。
2. 双版各 196 records 分类、35 exceptions、153 正常数学对照，不当 native pass；
   显式 sorted compact JSON UTF-8 无尾换行 SHA256
   4207d5d5e3316bd221a5a0da19d1559f55380ecc4e8d1c34dbfffe392c660062。
3. 初始 197 failed、qb-stage12a-p07-native-red.log/.exit1、实际修复、测试作者错误、
   最终专项结果，不能重复制造 red。
4. 完整复矩阵、mixed-radix 索引、非连续/反向targets、非 Hermitian/未归一化数学。
5. 对合性、trace、全转置、Hermitian保持及非PSD边界。
6. 两个真正独立 oracle 的完整矩阵比较。
7. 两条真实调用链及实际结果。
8. 独立 owned output、预约、root/view、失败恢复；public 空/全可能shares_input=True，
   native copy语义单列 Partial Public Compatibility。
9. public 重复/部分越界/bool 与 native 严格校验差异；shape-tuple dim 和历史 metadata
   差异保留，不能为逐字兼容破坏数学。
10. SDK-free/main/alternate FULL、独立JAX/TF、Torch/Autograd、coverage、28段matrix
    实际日志和退出码。
11. compile/legal/privacy/no-token/no-vendor、五环境版本/origin/pip，dirty Router单列。
12. tested/export/workspace/staged/committed hashes、exit、本地SHA、文件数、远端CI未验证。
13. 完整State/Density/Operator/general mapped channels/Circuit/PennyLane等真实剩余缺口。

P0.7 Verified Native Slice 仅在数学、专项和必要门禁全部通过后认定；DensityMatrix Full
Public Parity PARTIAL；C3 PARTIAL；完整 Qiskit/PennyLane native full replacement
ACTIVE / INCOMPLETE；新SHA CI NOT_VERIFIED；Studio DEFERRED。

最终沿用 Tasks 0-11，加以上 Tasks 12-13，继续实际原生数学、双oracle、公开差分、
组合、同树完整门禁、限定本地commit和有界报告。无 negativity/general channels/RNG/
Circuit/Capture/Studio，不以 facade/passthrough 冒充native。最终目标不缩小。
