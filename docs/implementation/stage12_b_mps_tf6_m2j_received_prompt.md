# Received TF6-M2J Public-Path Closure Prompt

The complete response to TF6-M2I-NATIVE-SCALAR-135-CHECKPOINT, including its
ending, was actually read in the authorized existing Chrome conversation
"Claude 代码泄漏与应对" on2026-10-24. The API read_thread view was stale;
the live existing-tab accessibility view contained the new report and full
completed reply. No new tab or login. Below is a structured requirements
record, with duplicated accessibility headings/table echoes removed and prose
condensed; it is not a verbatim raw accessibility dump. All numbered work
requirements and the ending are retained. No permission overrides follow.

## Review

结论：I1/I2/I3 已取得有真实测试支撑的原生实现进展。下一步应进入 I4/I5
的公共入口、错误隔离与资源闭环验收，而不是继续扩充 GraphDef 操作白名单。

这次最重要的突破是：原六条 scalar-capture RoF 失败，在原公开入口、原
loss、原 AD 次序及原容差不变的条件下转绿。修复来源于构造期标量数据流
到既有原生 ParameterExpression 的受限转换，不是重新执行用户 Python、
调用旧缓存图或注入 Hessian。

| 检查项目 | 本地报告结果 |
| --- | --- |
| 原六条 scalar-capture RoF |6 passed，Main/Alternate |
| Scalar 数学、准入及 M2H 回归 |各117 passed |
| 追加复数态、完整 AD 与来源测试 |各18 passed |
| 九项 query sequence |各2 passed |
| Strict SDK-free 参数专项 |116 passed |
| Default/four-framework320 + M2 163 |RUNNING，不能计 PASS |
| 原100-wire MPS TF 选集 |各6 passed/4 failed |
| M2 |PARTIAL |
| M3 |NOT_STARTED |
| 完整原生 Qiskit/PennyLane 替代 |ACTIVE/INCOMPLETE |

当前方案只是构造期的标量来源恢复，最终仍交给同一套原生表达式、冻结
绑定与 Whole-QNode 执行。特别保留：全图 fail-closed，包括未使用未知/
状态/副作用节点；有界 lowering，先分析 DAG/layout/展开工作再创建 AST；
拒绝与合法回退分离，不支持变量指数可以保留旧合法显式查询，但内存、预算、
所有权或账本失败绝不能成为未经准入的执行路线。

本批不能证明通用 TF 标量编译能力或全部控制流/shape/特殊数值正确。
白名单维持冻结。483项/环境尚无终态，I4/I5 需形成公共入口与失败生命周期
的完整联合证据。

## TF6-M2J: Scalar Lowering Public-Path Closure & M2 Integration Gate

继续 QuantumBridge R2O3-B-TF6-M2I。本批只处理 I4/I5：真实公开执行路径、
受限 scalar lowering 的失败原子性、既有方法及资源回归。不扩展新算子，
不进入 M3，不创建新 SDK 阶段。

FULL_INDEPENDENT_NATIVE_QISKIT_PENNYLANE_REPLACEMENT=ACTIVE/INCOMPLETE；
M2=PARTIAL；M3=NOT_STARTED。

### 1. 先取得正在运行的宽回归终态

检查 Main/Alternate 各483项的真实进程结果。记录最终 exit code、
passed/failed/skipped/xfail、JUnit/XML 路径、实际 import origins、运行时
源码版本、是否与当前 worktree 一致。尚未结束不要重复启动同批昂贵测试。
失败先定位是否本批引入。CPU 活跃/尚无失败输出不能推断 PASS。

### 2. 保持原六条 RoF 测试不变

再次确认 direct_tf/remapped_native/mixed_native 各两种 loss。真实公开
QNode 入口验证：用户 Python 恰一次构造；无 runtime QNode rebuild；无内部
scalar/quantum cached callback；无 GraphDef import；无 host Hessian 注入；
原 loss/AD/容差不变；完整量子二阶曲率。原 M2H 两条 cached RoF 持续通过。
不只比较 scalar AST 值，检查最终量子态、expectation、Jacobian、mixed
Hessian 和 HVP。

### 3. 冻结当前白名单

仅静态 float64、已验证算术及 sin/cos/exp、静态 Pow(x,2)、已验证
Pack/Unpack/Reshape/ReverseV2/StridedSlice 子集、仅静态布局元数据的
int32/int64 Const。拒绝变量指数、一般 Div、动态 axis/shape、未验证广播、
Resource/Stateful/Function/PyFunc、控制依赖、非法端口、非有限常量、
超出有界表达式和资源限制的 DAG。验证完整性，不扩大支持面。

### 4. 加强原子性测试

各失败阶段分别注入异常：bounded snapshot -> full graph audit -> static
shape/layout analysis -> scalar AST cost estimation -> UnifiedResourceLedger
admission -> native AST construction -> FrozenParameterBinding -> Whole-QNode
execution。

证明：准入失败不发布部分 frozen binding；AST 失败不污染已有 Circuit/
ParameterVector；owner snapshot 不因失败被替换；已尝试 work 依规则保留；
未用 live reservation 释放；父子账本不重复扣费；失败后合法 QNode 仍可执行；
MemoryError/预算失败不 fallback。覆盖处理多个 occurrence 一部分后失败。

### 5. 身份与数学快照

覆盖同名不同 UUID、同 UUID 多次 occurrence、vector shrink/regrow、input
reverse/reorder、负步长切片、native Gate definition 修改、controlled/
open-control、global phase、后追加 RX、observable 修改、scalar GraphDef
改动、method/max_diff/resource limits 改动、owner 失效。
数学快照可保持旧编译版本，但新受控 Python 调用继续 live resource/config
guard。已缓存外部 TF 图按既有合同 OUT_OF_SCOPE，不声称逐次检查 Python
owner 或扣账。

### 6. 保护方法选择

不改变 Ordinary Gate native parameter-shift、best、已验证 adjoint、默认
eager pfor、固定 projector、moving-projector、managed explicit cached
queries、trace-inline、max_diff1/2、true-third refusal。
合法 capability miss 允许旧真实支持的显式查询；预算、数学域、身份或安全
拒绝不得 fallback。特别确认 p**q 旧合法 query 不回归。

### 7. 资源与请求联合测试

复用既有 DerivativeExecutionRequest/UnifiedResourceLedger/ResourceScope。
至少 value -> gradient -> JVP -> VJP -> HVP(v1) -> HVP(v2) -> full Hessian
-> value。正确请求预算；streamed HVP 不构造完整 Hessian；
max_hessian_elements1 只允许合法方向；构造 scalar work 与 quantum runtime
分开；父子增量一致；zero Host/Device/shots 真实；并发不超卖；异常后全部
reservation 释放。TF allocator 与外部 loss 图内存不作为已测量资源。

### 8. 保留独立失败组

原2+新6 cached RoF 持续数学通过；M2 公开方法/账本/身份/异常联合闭环；
原4条100-wire MPS mixed AD 原样保留未修复。新实际数学失败优先修复，
不通过 capability 标签或 skip/xfail 隐藏。

### 9. 执行顺序

J1 取现483终态；J2 fail-closed/身份/原子性；J3 原2+新6完整 AD；
J4 M1/M2 default-pfor/managed explicit/inline/ledger/scope/concurrency；
J5 Compiler/IR/QPY/四框架；J6 strict SDK-free 受影响回归与原生数值示例；
J7 原4 MPS 状态确认。生产源码变化后此前回执标为旧候选，不能复用为最新通过。

### 10. M2 交接判断

提供简短可复核结论：白名单、AST/UUID 保真、公共二阶 AD、受控缓存查询与
trace-inline 资源差异、旧 query 兼容、原子性/并发账本、全部仍未支持的
TF 标量/量子 API、最新红灯、批次终态及源码版本。
即使全过也只提出 M2_SUPPORTED_SUBSET_READY_FOR_REVIEW，不自动 M2_DONE，
不自行进入 M3。按既定公共合同与未解问题单独判断交接。

### 11. 原 R2 门禁不变

最终冻结阶段真实执行 SDK-free/Main/Alternate FULL、独立完整四框架、
GLOBAL>=91.34108013033072%、68 exclusions 不增、原28-section matrix、全部
原生数值 examples、controlled legal、五实际 import origins、frozen/worktree/
staged/commit equality。不能以当前专项替代。
保持 local-only：不 stage/commit/push/fetch、不修改 Git 历史/认证/TLS、
不安装/vendor、不调用云/真机、不改金融证据、Studio、Router。

下一步将当前6条修复提升为完整可核查的公共调用、资源、身份和失败生命周期
合同。保留 I2/I3 方向，不扩充白名单，不提前触碰100-wire TF MPS。
M2 PARTIAL；M3 NOT_STARTED；完整独立原生替代 ACTIVE/INCOMPLETE。

## Terminal Receipt Confirmation

After TF6-M2I-483-TERMINAL was sent, the entire following completed reply and
ending were actually read from the verified existing Chrome conversation:

确认，继续沿用已归档的 M2J Prompt，按 J2 → J3 → J4 → J5 → J6 → J7 执行，无需调整顺序。
本次终态更新确认：
Main：483 passed，exit 0。
Alternate：483 passed，exit 0。
生产源码在测试期间未变，但缺少同进程完整 manifest 和 import origins，因此不能冒充最终冻结验收。
原六条 Scalar RoF 已转绿；原四条 100-wire MPS 仍是正式红灯。
下一步特别守住两项边界：异常原子性与多 occurrence 身份一致性；同时严格区分合法 capability miss 与资源、安全、数学域或身份拒绝，后四类绝不允许 fallback。
状态保持：M2 PARTIAL；M3 NOT_STARTED；完整独立原生 Qiskit/PennyLane replacement ACTIVE / INCOMPLETE。

## Public Atomicity Checkpoint Confirmation

The complete short response and ending to
TF6-M2J-PUBLIC-ATOMICITY-205-CHECKPOINT were actually read from the existing
authorized Chrome conversation. Operative confirmation:

确认，继续按原 M2J 顺序执行，当前 J2、J3 已完成，J4 正在运行。无需调整计划，也不进入 M3。
本轮有三项实质性进展：
修复错误 fallback：只有明确的 ScalarGraphCapabilityMiss 才允许走已验证的旧查询路径；安全、身份、数学域和资源错误均严格拒绝。
修复重复构造：Native AST 捕获不再因泛化 UnsupportedFeature 重试，避免重复 binding 和潜在副作用。
完成异常原子性与来源验证：J2 两环境各140 passed，J3 各65 passed；同进程1556个指定文件的 SHA 前后一致，并记录实际模块来源。
特别需要保留：合法旧查询兼容性不等于新增 Native AST 支持。p**q、tan、division 等仍属于经过重新准入的旧查询能力，不得计入原生 scalar lowering 覆盖率。
后续继续：J4 取得终态 → J5 Compiler/IR/QPY/四框架 → J6 严格 SDK-free 与数值示例 → J7 原四条 MPS 红灯核查。
J4 未结束前不计 PASS；若出现失败，先处理真实回归，再推进后续门禁。
当前状态不变：M2 PARTIAL；M3 NOT_STARTED；完整独立原生 Qiskit/PennyLane replacement ACTIVE / INCOMPLETE。原 R2 最终验收门槛继续全部开放。

## Special-Dtype Repair Confirmation

The entire completed short reply and ending to TF6-M2J-BFLOAT-REFUSAL-REPAIR
were actually read in the existing authorized Chrome conversation:

确认，继续沿用原 M2J 执行计划，保留全部新旧证据的版本隔离，无需调整任务顺序。
旧 J4：Main/Alternate 各480 passed，但均因主动 SIGINT 以 exit2结束，严格标记 INTERRUPTED/INCOMPLETE，绝不计为 PASS。
新增真实缺陷：bfloat16 非有限值绕过旧 NumPy dtype 分类检查，已改用公开 TensorFlow dtype 属性修复。
修复验证：原始4 failed/22 passed保留；修复后44 passed。有限 bfloat16 的旧查询兼容性也得到保护。
最新源码门禁：此前 J2/J3 的140/65不能替代修复后的 J2-v2/J3-v2。
后续继续 J2-v2 → J3-v2 → J4 新候选完整终态 → J5 → J6 → J7，每组保留同进程 manifest、真实 import origins 和退出码。
特别保持：修复非有限值检查不等于新增原生混合精度能力。
M2 PARTIAL；M3 NOT_STARTED；完整独立原生 Qiskit/PennyLane replacement ACTIVE/INCOMPLETE。

## Latest Candidate Checkpoint Confirmation

The complete short reply and ending to TF6-M2J-V2-REFUSAL-TERMINAL were
actually read from the existing authorized Chrome conversation:

确认，下一步先执行最新源码的 J4 完整回归：Main、Alternate 各483项。
J2-v2（各166 passed）、J3-v2（各65 passed）及原 cached RoF（各2 passed）已取得最新源码专项通过证据。
J4 执行时继续保留同进程1556文件的 before/after SHA、实际 import origins、JUnit 和最终退出码。
只有完整结束且 exit0，才能记录 J4 PASS。旧候选的480 passed/exit2继续标记 INTERRUPTED/INCOMPLETE。
J4 完成后依次执行 J5 → J6 → J7，不扩展白名单，不提前修复 MPS，也不进入 M3。
当前状态不变：M2 PARTIAL；M3 NOT_STARTED；完整独立原生 Qiskit/PennyLane replacement ACTIVE/INCOMPLETE。

## TF7 Gated MPS Implementation Authorization

The entire completed response, including its ending, to
`TF6-M2J-BOUNDARY-INTEGRATION-TERMINAL` was actually read from the existing
authorized Chrome conversation. This is a structured archive of its operative
requirements, not a claim that the following is a verbatim transcript.

The reviewer accepts `M2_SUPPORTED_SUBSET_READY_FOR_REVIEW`, not unconditional
M2 DONE. M1 remains VERIFIED_SUPPORTED_SUBSET; M2 remains FULL_INCOMPLETE.
M3 is IMPLEMENTATION_AUTHORIZED / NOT_ACCEPTED. Full independent native
Qiskit/PennyLane replacement remains ACTIVE / INCOMPLETE.

New task: `QuantumBridge R2O3-B-TF7 -- Native 100-Wire TensorFlow MPS Mixed-AD
Repair`. Only repair the original four real mixed-second-derivative failures.
Do not add SDK stages, Studio/Router work, industry cases or cloud tasks.

1. K1: rerun the original four square/exponential-cubic FoR/RoF tests unchanged.
   Record actual traceback, JUnit, exit, same-process origins and source manifest.
   Identify the real derivative request triggering tensorflow_graph.py's guard.
   Do not simply delete the third-order guard; prove true third still refuses.
2. Audit QNode/TF dispatch, tensorflow_graph/autodiff/whole_execution/
   native_derivatives, existing information/diff MPS tangents, actual MPS Device,
   ExecutionPlan lowering, derivative_planning, second_work,
   DerivativeExecutionRequest, UnifiedResourceLedger and ResourceScope. Record
   the actual public-QNode -> native-plan -> MPS-chain -> TF-local-evolution ->
   expectation -> first/second-directional -> nonlinear-loss chain.
3. K2: first establish 2--6-wire real MPS numerical tests with noncommuting
   parameters, entanglement, noncontiguous wires, phase, two observables,
   moving-projector fractional power and both nonlinear losses. Compare the
   same native compiled plan using independent dense, existing MPS primal,
   MPSTangentJet and TF MPS; check full J/H, JVP/VJP, FoR/RoF and streamed HVP.
4. Implement TF local contractions using existing tensor-chain semantics,
   routing, wire mapping, bond policy, complex scale, observable contractions,
   resource and tangent admission. No new Circuit/IR/compiler/parameter system.
   First domain: exact low-bond, no truncation, no singular gauge gradient.
   No global dense state/operator, host callback, numpy_function/py_function,
   stop_gradient, private gradient/JVP registry, Hessian injection or loss-specific
   HVP. Prefer exact bounded local contraction if QR/SVD higher AD is unsafe.
5. Preserve value/order0, JVP/VJP/order1, mixed HVP/order2. A nonlinear loss's
   second derivative requires at most QNode order2, not order3. Preserve
   max_diff1 first-only, max_diff1 second refusal and genuine third refusal.
   Square loss must include both 2(g.v)g and 2(f-0.3)Hf.v.
6. Reuse DerivativeExecutionRequest, HigherOrderLimits, derivative_planning,
   second_work, shared ledger/scope and Device admission. Before tensor allocation
   account physical wires, active gates, bond bounds, workspace, local matrices,
   AD directions/components, multi-output contraction and graph construction.
   Managed Python entries can be accounted; external cached graph is OUT_OF_SCOPE;
   allocator/RSS is ESTIMATED_ONLY. No TF-MPS-private scheduler or ledger.
7. K3: real 100-wire native Circuit/compiler/device. Prove 100 physical tensors,
   correct active/inactive identities, entanglement, remote routing, phase, bond
   observation and no dense fallback. Patch actual dangerous full-state paths to
   fail, but permit budgeted local gate matrices.
8. K4/K5: actual nonlinear FoR/RoF and all original four tests naturally PASS
   without original math, nesting, tolerance, inputs, skip/xfail or method masking.
   No production finite difference, resource bypass or default-SV regression.
9. High-value counterexamples: 2/4/6 wires, real 100-wire low bond, distant gates,
   two observables, nontrivial cotangent, zero/multiple directions, tiny Hessian
   cap, work/memory/components/bond limits, owner/source mutation, trace cache,
   NaN/Inf/branch cut, true third, parent/child/concurrency and exception release.
   Unsupported exact-bond plans must refuse before execution, never truncate.
10. K6: preserve original2 cached RoF, new6 scalar RoF, pfor, frozen binding,
    restricted GraphDef lowering, capability-miss/fatal separation, bf16 refusal,
    UUID/Vector/config/source identity, compiler/IR/QPY, ordinary shift,
    moving-projector Frechet, native MPS tangent, shared ledger and four frameworks.
11. Delivery sequence K1 -> K2 -> K3 -> K4 -> K5 -> K6. Actual exit/JUnit/origins/
    manifest each stage. Only after all six pass propose
    M3_SUPPORTED_SUBSET_READY_FOR_REVIEW, not full TF or SDK completion.
12. Local-only: no stage/commit/push/fetch/history/auth/TLS/install/vendor/tag/
    release/cloud/hardware/financial-receipt/Studio/Router modifications. All
    original R2 FULL/GLOBAL>=91.34108013033072%/68-exclusion/28-section matrix/
    numerical-example/legal/5-origins/frozen-worktree-staged-commit gates remain
    OPEN. Selected 1556-file equality is not full worktree or Git equality.

Final reporting must separate M2 verified domain and API gaps, M3 actual math,
original four status, resource/cache limits, latest candidate tests and remaining
full independent SDK parity gaps.

### TF7 K5 Checkpoint Confirmation

The entire completed reply and ending to
`TF7-K5-ORIGINAL-FOUR-GREEN-CHECKPOINT` were actually read in the existing
authorized Chrome conversation. It confirms continuation of original K6:
select MPSPlan at the existing managed Device boundary and reuse the common
work planner, ledger, ResourceScope and owner/source contracts. Verify early
resource refusal, cache identity, scope lifecycle, exceptions, concurrency,
and M1/M2 regression. Exact low-bond/no-truncation is not general MPS AD.
The active-ForwardAccumulator pfor/variant composition failure must not be
marked PASS. K2/K3/K5 do not accept M3 before K6. All original R2 final gates
remain OPEN; M2 full INCOMPLETE, M3 IMPLEMENTATION_AUTHORIZED/NOT_ACCEPTED,
independent full replacement ACTIVE/INCOMPLETE; local-only remains mandatory.

### TF7 Selector-Repair Checkpoint Confirmation

The entire completed reply and ending to
`TF7-K6-SELECTOR-REGRESSION-REPAIRED-CHECKPOINT` were actually read from the
existing authorized Chrome conversation. It confirms continuing original K6,
with no new stage or early M3 acceptance. It accepts preservation of ordinary
parameter-shift/old variance/probability/native-host methods, named-rule-only
capability misses, fatal resource/identity/domain refusal and exact parent/child
budget boundaries. It explicitly requires the latest d9cdbf06 candidate's
complete J4 terminal receipts before reviewing M3 readiness; the earlier483
candidate cannot substitute for them. M2 full INCOMPLETE, M3 IMPLEMENTATION_
AUTHORIZED/NOT_ACCEPTED, full independent replacement ACTIVE/INCOMPLETE and all
original R2 gates OPEN/local-only remain unchanged.

Evidence correction to avoid an ambiguous collective count in that reply:
the229 strict SDK-free native tests ran in one isolated native runtime, not in
both TF SDK environments. The63/10/231/1184(+5 existing xfail)/18 scopes each
have distinct Main and Alternate receipts. Neither statement is a FULL gate.

## TF7 Terminal Review And TF8 Received Instructions

The entire completed reply, including its ending, to
`TF7-K1-K6-LATEST-TERMINAL-REVIEW` was actually read from the existing
authorized Chrome conversation. This structured archive preserves the operative
requirements rather than claiming to be a verbatim transcript of the AX layout.

The reviewer accepts M3_SUPPORTED_SUBSET_READY_FOR_REVIEW and development-period
verification of exact low-bond/no-truncation TF MPS. This is based on supplied
local receipts, not the reviewer's independent local/remote CI inspection.
M1=VERIFIED_SUPPORTED_SUBSET; M2 and M3=VERIFIED_SUPPORTED_SUBSET/FULL_INCOMPLETE;
FULL_INDEPENDENT_NATIVE_QISKIT_PENNYLANE_REPLACEMENT=ACTIVE/INCOMPLETE.
The corrected attribution of actual true-third JUnit selections is accepted;
old K5-only unselected cases must never be retroactively counted as PASS.

Next prompt: `Stage12-B R2O3-B-TF8 -- Native MPS Exact-Execution Coverage
Expansion`. Expand a controlled piece of actual MPS operation/observable
semantics, not repeated demonstrations of the original four passes. Continue
the original full SDK objective, no new SDK architecture/second simulator/UI.

1. Preserve TF7 K1--K6 as a regression baseline. Read real code and the actual
   original28-section matrix. Establish real math status of one/two-site gates,
   routing, local contractions, initial state, Pauli/Hamiltonian expectation,
   powered/controlled operations, tangents, TF AD, bond/workspace/owner/scope.
   Do not build another inventory inferred solely from API names.
2. Audit selector misses and distinguish: no valid compiler lowering; native
   Gate math but missing TF local rule; routing gap; insufficient exact bond;
   unverified parameter derivatives; resource/identity/domain faults. Focus on
   genuine missing local rules/routing (categories2/3). Inspect actual lowered
   CX/CZ/SWAP, controlled rotations/phases, distant wires, inverse/power,
   composite gates and global phase. Reuse existing matrices; implement only
   truly missing rules, no arbitrary multi-site/unbounded-bond expansion.
3. Validate2/4/6/20/100-wire real math. Only small wires may use independent
   dense states. For20/100 use existing native MPS, local observables and
   independently reducible analytic circuits; no global dense. Verify complex
   state (small only), expectations, J/H/mixed/HVP/JVP/VJP, nontrivial
   cotangents/two nonlinear losses. Route tests must expose actual permutation
   and phase, not only a final expectation.
4. Keep exact index-split/no-SVD-or-QR-truncation. Test bond increases/decreases,
   entangle/disentangle, exact cap/one above,100-wire inactive identities,
   global complex scale, zero/multiple tangent work. Refuse before execution
   if exact representation cannot fit. Separate predicted conservative bounds
   from actual observed tensor dimensions.
5. Audit actual native observable semantics: Pauli/PauliString/sums, fixed real
   Hamiltonian coefficients, multi-output/noncontiguous/identity/offset. Add
   contraction only if native semantics already exist and TF MPS truly lacks it.
   Never treat trainable coefficients as constants; any such support needs
   separate red/green parameter/derivative/resource evidence and authorization.
6. Reuse ExecutionPlan/DerivativeExecutionRequest/derivative_planning/second_work/
   ledger/ResourceScope/NativeHost/Device admission. Protect ordinary PS/best,
   legacy variance/probs/wider host, moving power, original2+6 cached RoF,
   scalar whitelist and fatal refusal. A named tensor-rule miss may retain
   only independently admitted legal old math. No resource/owner/domain/plan
   inconsistency may fall back.
7. Diagnose the active-ForwardAccumulator pfor=False variant/TensorArray issue
   with independent pure TF and small native MPS comparisons. Diagnostic only
   unless public TF ops produce correct first/second math against an independent
   oracle with no private registry/host callback/lost quantum curvature or M2
   resource/method regression. Keep pure-TF negative evidence if it still fails;
   never change the mathematical objective merely to obtain green.
8. For new rules check workspace, bonds, AD graph/multi-output work, tangent
   slots/Hessian limits, cached identity, owner, parent/child/concurrency and
   failure/recovery. Reject before dangerous TF allocation. Distinguish attempted,
   completed and still-reserved work. No exact TF allocator/RSS/external-loss claim.
9. Execute N1(real minimal red) -> N2(local/routing rule) -> N3(2/4/6 math) ->
   N4(20/100 exact/no-dense) -> N5(observables/multi-output) -> N6(resource/
   failure/concurrency) -> N7(original4 TF MPS/M2 math/default pfor/compiler/
   IR/QPY/SDK-free protections). Save red/green JUnit, exits, actual origins and
   same-process manifest each stage. No hundreds of cases before finding a rule.
10. At most propose TF_MPS_EXACT_COVERAGE_EXPANDED_SUPPORTED_SUBSET. List actual
    new operations/observables/parameter derivative rules, observed max bond,
    resource/rejection limits, remaining MPS/TF AD gaps and original matrix mapping.
    Test counts are not API counts. If no reliable extension exists, report a
    real gap instead of adding duplicate code just to show a change.
11. TF8 is not the endpoint: Circuit/Transpiler/Primitives/Backend/QPY/QASM,
    simulation/noise, PL operations/devices/transforms/gradients/QNode/qchem/
    plugins all remain constrained by full replacement. Original R2 FULL in
    three environments, independent four-framework FULL, GLOBAL>=91.34108013033072%,
    unchanged68 exclusions, original28-section matrix, ALL native examples,
    controlled legal/five actual origins and frozen/worktree/staged/commit
    equality remain OPEN; no completion inferred from MPS subsets.
12. Local-only: no stage/commit/push/fetch/history/auth/TLS/install/vendor/
    cloud/hardware/financial13-result/Studio/Router changes. Preserve the dirty
    checkout and existing user files. No tags/releases.

### TF8 N3--N6 Checkpoint Review

The entire completed reply and ending to
`TF8-N3-N6-MATH-RESOURCE-CHECKPOINT` were read in the existing authorized
Chrome conversation. It confirms continuing original N7, not a new stage or
early TF8 acceptance. Freeze the current selected source until both483-case
Main/Alternate sessions reach real terminal status. Then inspect exit/JUnit/
same-process origins/manifests, original four formal100-wire mixed cases and
true-third refusal. A failure requires raw receipts and new-candidate validation,
not reuse of the old candidate's PASS.

Three explicit gaps remain: public QuantumCircuit.unitary append(metadata)
ABI TypeError (category1); active ForwardAccumulator + pfor=False variant
failure in pure TF and native MPS (UNSUPPORTED/UNRESOLVED); no differentiable
bond compression or general truncated MPS. The20/100-wire vacuum-projection
oracle proves only the actual tested low-active circuits, not arbitrary global
100-wire entangled-state correctness.

After terminal N7 evidence, form TF8_SUPPORTED_SUBSET_READY_FOR_REVIEW with
these and other unsupported domains separated. Until review TF8 remains
N7 RUNNING/NOT_ACCEPTED; M2/M3 full remain INCOMPLETE, full independent native
replacement ACTIVE/INCOMPLETE, all original R2 final gates OPEN. No FULL/GLOBAL
or Git flow is requested now; strict local-only continues.

## TF8 Terminal Review And QC1 Received Prompt

The complete reply and ending to `TF8-N1-N7-LATEST-TERMINAL-REVIEW` were read
in the existing authorized Chrome conversation. The reviewer accepts
TF8_SUPPORTED_SUBSET_READY_FOR_REVIEW and the reported development-period
verification of the exact local-matrix MPS subset, not TF8_FULL_DONE, general
M3 completion or SDK parity. This is review of supplied local receipts, not
independent inspection/execution by the reviewer. All original R2 gates OPEN;
full native replacement ACTIVE/INCOMPLETE.

Next task: Stage12-B P4-U3D2-R2O3-B-QC1, Public QuantumCircuit Unitary ABI &
Inherited Method Consistency. Operative instructions, fully read:

1. QC1-A: create real Main/Alternate public QuantumCircuit.unitary(U,[0,1])
   red using a nontrivial complex4x4 U, alongside working native Circuit.
   Record traceback, actual append signatures, metadata/return types, and
   whether the authoritative operation store partially changes on failure.
   TypeError must be repaired, not relabelled Unsupported.
2. Audit Circuit.unitary/append, public append/data, InstructionSet,
   CircuitInstruction, UnitaryGate, native Operation/Instruction, metadata,
   copy/compose/decompose, Compiler/IR/QPY. Fix the correct ABI layer. Preserve
   native Circuit fluent returns and public append InstructionSet returns;
   public unitary ABI must follow actual public differential evidence. Never
   add arbitrary private metadata kwargs to public append, a second Circuit,
   operation store or instruction registry.
3. Run installed public Qiskit2.4.1(Main)/2.6.0(Alternate) independently as
   behavior oracles, no source copying. Observe signatures/returns/label,
   matrix validation/wire types/storage. Cover2x2/4x4, noncontiguous wires,
   asymmetric complex matrix, global phase, label, wrong shape/nonunitary,
   duplicate/out-of-range wires, illegal dtype and existing valid loose
   Bit/Register domain. Record version drift without inferring one from another.
4. Before repair define independent NumPy complex128 math for local wire
   ordering/state/global phase, input/stored matrix, compose/inverse and exact
   MPS. Use an endian-sensitive asymmetric matrix, not only identity/SWAP/CZ.
   Invalid inputs must not partially mutate the store.
5. QC1-D: inspect only adjacent inherited append override conflicts in actual
   initialize/reset/delay/barrier/measure/append/unitary/compose/to_gate/
   to_instruction. Check signature mismatch, fluent vs InstructionSet return,
   lost metadata, duplicate/partial append and stored identity. Repair only
   same-root-cause defects demonstrated by real reds; no broad Circuit rewrite.
6. Preserve native UnitaryGate type/label, ndarray ownership after caller
   mutation, copy/inverse/repeat/control/AnnotatedOperation, parameter UUID,
   stable CircuitInstruction references, single .data/store and metadata
   isolation. Do not silently change existing readonly/copy=False NumPy1/2
   borrowing guards.
7. QC1-E: actual public unitary -> native store -> existing Compiler -> IR ->
   restored Circuit -> native Statevector/MPS. Respect existing QPYv13 standard
   record and QASM supported domains; accurate refusal is allowed outside them,
   no private sidecar pretending standard interop. Keep five old upstream xfails.
8. QC1-G: regress TF7/TF8 fixed1/2wire,2/4/6 state/J/H,20/100 exact low bond,
   original4 FoR/RoF, true third refusal, ordinary PS, old var/probs/moving
   projector, owner/config/resources. Do not expand the TF fixed predicate or
   imply public unitary admits trainable/wider matrices to that tensor subset.
9. QC1-F: reuse ledger/scope/compiler/device admission. Check rejection/store
   atomicity, oversize before allocation, owned matrix bytes, resource-failed
   append, copy/inverse no double count, concurrent append/legal readonly
   execution under existing locking/ownership, recovery after failure and bad
   metadata not changing plan identity. No private new budget system.
10. Order QC1-A red/differential -> B minimal fix -> C complex math/wire order ->
    D bounded inherited audit -> E compiler/serialization -> F resources ->
    G Main/Alternate/strict SDK-free affected regression. Suggested filenames
    are tests/circuit/test_quantumcircuit_unitary_public_abi.py,
    test_quantumcircuit_inherited_append_contract.py, compiler unitary test and
    interfaces unitary-TF-MPS regression; adapt to real layout. No skips/xfails,
    deleted tests or relaxed tolerances to manufacture green.
11. Before/after re-enumerate selected roots/hash, actual loaded origins,
    raw JUnit/exit and independent runtime versions. Source changes after wide
    tests invalidate using old receipts for latest source; selected equality
    is not full worktree/staged/commit equality.
12. Propose QC1_PUBLIC_UNITARY_ABI_SUPPORTED_SUBSET_READY_FOR_REVIEW only after
    TypeError really fixed, public ABI/identities/ownership/wire math/compiler/
    supported serialization/atomicity/native fluent/old4TFMPS/affected two-env
    and strict SDK-free evidence. Still not complete Circuit or SDK parity.
13. After QC1 return to unchanged28-section matrix to choose next actual
    public-API red; possible Circuit/Instruction/Transpiler/Primitives/Backend,
    later Aer/PL ops/devices/transforms, only evidence-driven. Do not start those
    broader tasks in this batch. No MPS expansion/pfor repair/UI/industry cases.
14. Local-only: no stage/commit/push/fetch/history/OAuth/TLS/install/vendor/
    cloud/hardware/financial13-receipt/Studio/Router/tag/release change. Original
    SDK-free/Main/Alternate FULL, independent four-framework FULL, GLOBAL line
    coverage>=91.34108013033072%,68 exclusions, original28-section matrix,
    ALL numerical examples, controlled legal/five actual origins and frozen/
    worktree/staged/commit equality remain OPEN. M1/M2/M3 full INCOMPLETE.

### QC1 A--C Checkpoint Confirmation

The completed reply and ending to `QC1-A-C-TARGETED-CHECKPOINT` were read in
the existing authorized Chrome conversation. It confirms the minimal public
ABI adapter and A--C evidence, not QC1 acceptance; continue original D -> E ->
F -> G. No rollback or new stage is requested. Native owned matrix snapshots
versus both public SDKs' caller aliasing remain a precise unresolved parity
difference, not equivalent behavior. Preserve the original JAX x64 configuration
failure receipts as configuration failures, not production math failures.

Priorities remain actual inherited self.append conflicts with bounded real-red
repairs; actual public-unitary Compiler/IR/QPY/QASM/device end-to-end proof;
observed Gate/Operator input forms and wire conventions; owner/storage/resource/
concurrency/failure atomicity; latest Main/Alternate/strict SDK-free and TF7/TF8
20/100/original4/true-third protection. The128 A--C passes are not D--G proof
or complete public unitary parity. Local-only and all original R2 OPEN/full
replacement INCOMPLETE constraints continue unchanged.

### QC1-W1 Wire-Parity Correction

The complete reply and ending to `QC1-D-E-F-REAL-WIRE-PARITY-RED` were read.
Continue inside QC1, not a new stage. Fix the actual two-version public wire
math red before freezing D--G. The39 native-convention passes cannot outweigh
the public complex-amplitude mismatch. Actual probe path is
`tests/interfaces/probes/probe_public_unitary_wire_parity.py` (the reply's
shortened tests/probes path is not a request to create a duplicate).

W1--W8 operative requirements: preserve original width1/2 same-U/same-qargs
probe and raw failures; independent oracles distinguish local public/native
bases, global state basis and qarg permutations [0,1]/[1,0]/[3,1]/[0,3], with
asymmetric complex U, nonzero state, CX and phase. Audit the real source ->
UnitaryGate -> public append/frame/store -> definition -> lowering -> SV/MPS/TF
-> IR/QPY conversion-count table before code edits. Convert only known public
invocations at the existing frame/native boundary, candidate P*U*P^-1 only
where mathematically justified. Do not change displayed U/qargs/label, native
Circuit.unitary q0-first, global state basis, operation store or TF rules.
Do not infer provenance from a gate name. Converted operations cannot convert
again; use a minimal existing-frame marker if needed, no parallel SDK/IR/store.

Verify definition/inverse/control/annotations/open&closed controls/decompose/
compose/repeat/copy/ownership. Inspect QPY's existing wire-order encoding to
avoid double conversion; public and native sources must each retain physical
math. Use only standard QPYv13 records, no private sidecar; distinguish math
transport from preserving proprietary origin/display identity. Protect old
QPY annotation/control/ParameterVector/phase and unchanged upstream xfails.
Actual two-version full complex amplitudes, not just probabilities or arbitrary
phase equivalence, must match for width1/2, array/Gate/Operator, all qarg orders,
source/compiled/QPY restored and SV/MPS. Keep failure atomicity/resources and
native owned-copy versus upstream aliasing as a separate unresolved difference.

Protect native q0-first/fluent/public InstructionSet, CH/CSwap, MPS exact,
original four100-wire FoR/RoF, true third, PS/moving power/legacy var-probs,
ledger/scope/source/owner. Final wide tests only after real red is repaired;
new source requires new manifests/origins/JUnit/exit. No skip/xfail/tolerance
loosening or transforming public test inputs. At most propose
QC1_PUBLIC_UNITARY_WIRE_PARITY_SUPPORTED_SUBSET_READY_FOR_REVIEW, never full
parity completion. All original R2 gates OPEN; strict local-only unchanged.

### QC1-W1 Targeted Green: Further Boundary Audit

The completed reply and ending to `QC1-W1-ACTUAL-ORACLES-CHECKPOINT` were fully
read in the existing authorized conversation. The reviewer confirms the
provenance direction, not QC1 acceptance or independent source inspection.
Current designation is QC1_W1_PUBLIC_WIRE_PARITY_TARGETED_GREEN only.

Keep the running broad candidate unchanged to terminal first. Then remain in
QC1 and audit, in order: (1) marked/unmarked derived-owner equivalence for
derive-before-lowering versus lowering-before-derive, including copy/inverse/
power/repeat/control/QPY and exactly-once conversion; (2) recursive family
classification with cycles, shared DAGs, active-path versus visited distinction,
depth/work refusal before exponential expansion, mixed origins, repeated owners,
open controls, normalized repeat bodies and ordinary nonmatrix GenericGates;
change recursion only for a real demonstrated defect; (3) independent actual
two-version full-complex public append(UnitaryGate(U)) and Operator(circuit)
entry probes with identical U/qargs, never infer these from unitary(U) success;
repair actual misses at existing frame/owner boundaries, no parallel conversion
store; (4) standard QPY/raw/marked/derived objects and invalid-owner/depth/budget
atomicity; (5) only then latest frozen Main/Alternate/strict SDK-free/compiler/
IR/QPY/TF7-TF8 20/100/original four mixed AD/true-third and affected public gates.

Owned native matrix versus upstream ndarray aliasing stays separately open;
without owner approval do not break existing native ownership/readonly/borrowed
NumPy contracts for alias parity. No new SDK stage or redesign is requested.
Original R2 final gates OPEN; independent full replacement ACTIVE/INCOMPLETE;
all prior local-only prohibitions remain unchanged.

### QC1-W1 Four Public-Entry Expectations: Scoped Decision

The completed `QC1-W1-ADDITIONAL-ENTRY-REDS-AND-CONTRACT-CONFLICT` reply was
fully read, including its ending. It authorizes correcting only the four
proven conflicting public-entry expectations for native Operator powers
(-1,.5,-.3,2), explicitly PUBLIC_ENTRY_EXPECTATION_CORRECTION. Keep their exact
matrices/exponents/tolerances and native Operator.power math, plus add native
Circuit.unitary/raw-matrix execution assertions. Only the public append path
must now use the actual SDK's public local-basis interpretation. No wholesale
old-test rewrite, deletion, skip/xfail or tolerance changes are authorized.

First finish Alternate broad without source edits (it subsequently finished
5173 passed/3 original xfailed). Then repair both actual public append/raw-Ugate
and Operator(body) reds at existing frame/owner boundaries. Public append may
interpret raw UGate from its invocation context, but explicit native-origin
factories must retain their proven origin. No array-value/name/label/history
guessing or global ndarray registry. Operator(raw_U) remains literal input;
only proven from-circuit representation can be marked, and _new/copy/compose/
tensor/power propagation must be numerically justified, not blindly spread.

Keep the shared binary GenericGate DAG cap7/count>=30 red and repair using
existing GateCircuitLimits: memoized expanded cost, per-reference charging,
active-path cycles, depth/node/work caps before expansion. Memo avoids duplicate
analysis, not semantic charging. Then latest Main/Alternate same-U/qargs complex
amplitudes across all three public entries/native raw/derived/inverse/power/
repeat/control/compiler/IR/QPY/SV/MPS and TF original4/third, followed by latest
frozen affected D--G/strict SDK-free/numerical examples/origins/manifests/JUnit.
No second store/SDK/executor or QPY sidecar. Native data/global math and ownership
unchanged. QC1 PARTIAL, full replacement ACTIVE/INCOMPLETE, all R2 gates OPEN,
strict local-only remains in force.

### QC1-W1 One Additional Width2 Expectation

The completed reply to `QC1-W1-SCOPED-CORRECTION-FOLLOWUP` was fully read. It
extends PUBLIC_ENTRY_EXPECTATION_CORRECTION precisely to the single old
test_public_factory_promotes_numeric_matrix_to_an_owned_unitary_not_an_opaque_generic_definition[2]
assertion. Keep original matrix/width/tolerance/type/copy/inverse/decompose/QPY,
preserve width0/1 behavior, and add native raw Circuit.unitary inverse/QPY math.
Do not represent the corrected old assumption as a production fix. No other
old-test math changes are authorized. Raw constructor modifiers -> public-method
owners -> native wrappers -> recursion -> IR/QPY -> two-env targeted -> final
D--G stays the order. Native copy=False/owned identities must stay valid.
The reviewer explicitly accepts temporary precise refusal of unproved
Operator.compose/tensor origins only as an OPEN parity gap, not implemented
support. Full replacement INCOMPLETE, original R2 OPEN, strict local-only.

### QC1-F Invalid Definition No-Callback Correction

The completed reply to `QC1-W1-FROZEN-VALIDATION-RUNNING-AND-INVALID-OWNER-RED`
was fully read. QC1 remains NOT_ACCEPTED. Wait for all current sessions to reach
terminal; preserve old frozen receipts. Then add formal original ForeignBody
and stricter traps before production edits. Confirm exact trusted native Circuit
type before touching body.operations, and exact closed native list/tuple,
Operation entries, parameter tuples and provenance enum before child traversal.
Foreign properties, __iter__/__len__, malicious containers and native subclasses
must refuse before callback, not catch/wrap an already executed foreign error.

Retain memo/active-path/depth/nodes/projected per-reference work refusal before
expansion, unchanged source store and released ledger on every failure. Check
provenance propagation only from validated owners/construction paths. Preserve
legal GenericGate, UnitaryGate, control/annotation, native wrappers, public ABI,
IR/QPY/math/resources. New candidate requires new affected two-env/strict
SDK-free/TF-MPS and original D--G broad evidence. Do not expand compound Operator
support while fixing admission; those compose/tensor/ambiguous controlled-owner
origins remain OPEN, as do full replacement and all original R2 final gates.

### QC1-F One QPY User Metadata Expectation

The completed reply to `QC1-W1-TERMINAL-27D6-CANDIDATE` was fully read. It
authorizes one additional, independent old-test contract correction only:
test_public_qpy_metadata_cannot_smuggle_a_fake_native_classical_scope. Keep
original classical_scope key/JSON/native source/public QPY input. First prove
both actual Alternate/Main frozen TF8 baseline identity and semantics: userdata
preserved, no executable scope/vars/captures/declared bindings across native
copy/compose/IR/execution, legitimate typed native scope still strictly refused
by unsupported QPY encoding. If semantic pollution exists, do not correct the
test; repair production instead. These preconditions were subsequently verified
in both actual baseline runtimes using real methods iter_captured_vars and
iter_declared_vars (not nonexistent num_captured_vars fields).

Only replace the stale mandatory refusal with stronger no-smuggling assertions,
labelled QPY_USER_METADATA_VS_EXECUTION_SCOPE_CONTRACT_CORRECTION -- one test
only. No production QPY Reader or whitelist/sidecar change. Preserve all
27d6 wide failure receipts; they cannot be relabelled PASS. Then new candidate
foreign-owner fix, affected two-env/strict SDK-free/TF-MPS/examples and D--G
broad remain required. All original R2 final gates OPEN/local-only unchanged.

### QC1-F2 Final Evidence Review Conditions

The complete reply to `QC1-F2-PUBLIC-OWNER-ADMISSION-CLOSED` was read, including
its ending. No new feature/stage or large new test requirement. Keep the5c2af77d
candidate immutable until all existing sessions terminal; do not restart or
reuse earlier a2fe PASS for it. Then latest supported-subset evidence may be
proposed, not accepted yet. Final checks are consistency of unitary/append/
execution-operation qualification before foreign reads, finite per-reference
DAG cost/cycle/depth admission, failure/store/owner/ledger atomicity, and legal
two-wire/QPY/derived/native-q0/TF7-TF8 original4/true-third compatibility.
Existing targeted proofs may be referenced. All original parity gaps, full
replacement ACTIVE/INCOMPLETE and local-only/R2 OPEN constraints remain.

All5c2 sessions subsequently finished; an additional valid-input post-transport
Gate reuse red was then discovered within original QC1-E/W1 exactly-once
serialization scope. This is not a new SDK stage or ignoring a running freeze.
QPY and JSON IR restored matrix Gate records need native representation origin
at their existing shared record factory before public reuse. Original same
U/qargs and raw14 failures are retained; fresh latest-candidate gates follow.

### QC1-W2 Freeze Review Conditions

The completed reply to QC1-W2-POST-TRANSPORT-OWNER-REUSE was fully read,
including its ending. W2 stays within original QC1-E/W1; no new feature/stage
or unrequested new test requirement. Keep the e3ee8aa5 source frozen until
all six current gates are terminal. Final review checks: detached owner reuse
converts exactly once; native/public/restored coordinate frames stay distinct;
trusted record native-origin construction cannot bypass malformed-owner or
resource admission; old wire/compiler/QPY annotations, original four actual
mixed-AD cases, true-third and legacy behavior remain preserved. Propose
supported-subset ready only after latest terminal receipts. All original R2
gates stay OPEN, full replacement ACTIVE/INCOMPLETE and local-only unchanged.

## QC1 Terminal Acceptance And QC2 Received Prompt

The completed reply to QC1-W2-LATEST-TERMINAL-SUBSET-REVIEW was fully read
through its ending. It accepts QC1_PUBLIC_UNITARY_VERIFIED_SUPPORTED_SUBSET
based on supplied local receipts, not independent source inspection or full
Circuit/SDK replacement. Do not repeat QC1 verification absent a new change.
Previously listed parity differences stay OPEN, not permanently excluded.

Next: Stage12-B QC2, Native Operator Composition, Tensor Ordering And
Provenance Closure. Full independent Qiskit/PennyLane replacement stays
ACTIVE/INCOMPLETE. Operative prompt:

A. Audit existing Operator/from_circuit/_new/compose/tensor/expand/copy/power,
UnitaryGate and QC1 provenance before edits. Actual installed Qiskit2.4.1 and
2.6.0 are separate public behavioral oracles, no copied source. Create genuine
math reds for raw, circuit-origin, native from_circuit, mixed origins, derived
results in public unitary/append and tensor/expand on noncontiguous qargs.
Preserve old explicit Unsupported counterexamples as historical evidence;
do not replace new math implementation with expected refusal.

B. Independently prove compose default=B@A, front=True=A@B, dot, tensor,
expand, local/global basis and noncontiguous subsystem positions. Use NumPy
complex128, independent basis index mapping, noncommuting asymmetric complex
unitaries, nonzero state and explicit phase; not identity/SWAP/diagonal only.
Mixed subsystem dimensions require independent index proof, not naive kron.

C. Reuse existing owner/basis provenance, no external ndarray registry. Raw
Operator must not be guessed circuit-origin. Preserve proved from_circuit
origin and unchanged-representation copy. Prove arithmetic output basis before
propagation; mixed origins need one explicit normalization. Already normalized
outputs must not reconvert during public invocation. Preserve power/inverse/
adjoint origins. Both-native tensor/expand origins alone do not prove correct
physical output wire order.

D. Preserve existing Operator.power Jordan/Schur/branch-cut boundaries,
native q0-high math, public q0-low execution, QC1 owned-copy, Gate provenance,
native/public unitary and append return ABI. Preserve native raw-matrix math,
fractional power and near-cut refusal. Unsupported branches, nonunitary gates
and incompatible dimensions must reject before execution, not fabricate math.

E. End-to-end Operator(circuit_a).compose/tensor/expand(Operator(circuit_b))
through real public unitary/append. Compare data/independent matrix/stored
matrix/compiler lowered ops/Statevector/MPS/QPYv13/JSON IR/restored detached
owners/repeated public append. Use actual bytes/JSON encode-decode, no private
serialization sidecar. Follow actual native/public construction APIs.

F. Reuse GateCircuitLimits/HigherOrderLimits/UnifiedResourceLedger/ResourceScope.
Test invalid qargs/dimensions/nonunitary/unproved origin/oversize tensor/memory
shortfall/foreign subclass/side-effect data or __array__/forged owner/origin
mutation/concurrent readonly/source mutation/recovery. Refuse BEFORE foreign
properties; no partially published result/source mutation; charge attempted
work/release live reservations. No second authoritative Circuit/Operator data
system or owner-admission bypass.

G. After true reds fixed: (1) two-env public differential and independent
oracle; (2) QC1 ABI/owner/detached transports; (3) native power/branch cuts;
(4) Compiler/IR/QPY/SV/MPS; (5) TF7/8 original4 100wire mixedAD/true-third/
20/100exact; (6) M1/M2 cachedRoF/defaultpfor/ledger/scope/4framework affected;
(7) two-env broad/strictSDKfree/all affected numerical examples. Record actual
exit/JUnit/import origins/re-enumerated before-after source manifests. Source
change invalidates reusing old6649/207/557 receipts. No new skip/xfail or old
xfail counted native pass.

Only after complete bounded proofs propose
QC2_OPERATOR_ARITHMETIC_PUBLIC_PARITY_SUPPORTED_SUBSET_READY_FOR_REVIEW.
Any remaining specific unsupported/math failure must be explicit, not replaced
by other passing subsets. Continue existing internal progress docs; no new
isolated owner-facing page. Original28-section matrix remains overall priority.
All original R2 FULL/independent4framework/GLOBAL>=91.34108013033072%/68
exclusions/originalmatrix/ALLexamples/controlledlegal/5origins/fullGit equality
remain OPEN. LOCAL ONLY: no stage/commit/push/fetch/install/auth/TLS/vendor/
cloud/hardware/tag/release/financial13/Studio/Router changes.

### QC2-A Contract Decision: Explicit Public Arithmetic Only

The complete reply to QC2-A-REAL-REDS-AND-NATIVE-PUBLIC-CONTRACT-CONFLICT was
fully read through its ending. It authorizes the same existing Operator class
with an explicit as_qiskit_operator-style view/factory, NOT global default
migration, a second class/store/executor or a matrix registry. Native default
compose=A@B/front=B@A/q0-high and all old assertions stay unchanged. Original
56 default-public reds remain OPEN_DEFAULT_API_PARITY_GAP; explicit opt-in
success must never replace those failure receipts/statistics.

QC2-B1 operative requirements: keep representation provenance separate from
an immutable native/qiskit arithmetic-convention field. No origin-based call
order guessing. Prove normalization, same-type/owned/idempotent conversion,
copy/_new/power/adjoint propagation and mixed-mode conversion or explicit
refusal. Public-mode .data must truly be declared public-little coordinates.
Use existing numeric kernels. First independent full products; then mapped
qargs(2,0)/(0,2), mixed-radix/dimensions; then tensor/expand factor and dims;
then raw/circuit/from_circuit mixed provenance and actual Circuit transports;
then resources/owners; finally affected Main/Alternate/SDK-free/TF7/TF8 guards.

Make a conversion-path table before implementation. Normalize once at proved
arithmetic boundary; public-little outputs must not be bit-reversed again by
public unitary. Real public unitary(derived) and append(UnitaryGate(...)) are
required; direct append(Operator) is a separately observed gap, not assumed
supported. Compare .data/independent math/compiler/SV/MPS/real JSON IR/QPYv13/
restored detached owners/repeated append or unitary without pretransforming
original U/qargs. Preserve old default-red probe unmodified.

Retain strict forged-origin/subclass/property/data/array callback/qargs/dims/
oversize/work/memory/parent-child ledger/concurrency/source-mutation/recovery
and idempotence proofs, before foreign reads, no partial results/new budgets.
All old native compose/mixedradix/power, QC1, original4 100wireTF/third/M2
cachedRoF/scalar/defaultpfor/ABI tests must stay unchanged and pass. After this
batch document default-migration affected callers/risks/boundary options and
need for Owner approval; DO NOT switch defaults. Maximum bounded claim:
QC2_EXPLICIT_PUBLIC_ARITHMETIC_SUPPORTED_SUBSET_READY_FOR_REVIEW, original
56 default-red gaps OPEN; all R2 final gates OPEN/full replacement
ACTIVE/INCOMPLETE/local-only restrictions unchanged.

### QC2 Targeted Checkpoint Review

The completed QC2-B1-B4-EXPLICIT-PUBLIC-TARGETED-CHECKPOINT reply and ending
were read. Direction accepted from supplied receipts, no independent source
inspection or QC2 acceptance. Continue B5 then B6 in existing scope. Check
forged modes/owners before callbacks, grouped memory/work admission, parent/
child accounting, copy/power/adjoint basis preservation, concurrency and owned
snapshot behavior. Actual isolated probe rerun is required after its import
repair; earlier470 cannot replace final-source gates. Original56 default gaps
and all R2 final gates stay OPEN; full replacement ACTIVE/INCOMPLETE/local-only.

### QC2 B5 Review And B6 Freeze Conditions

The complete QC2-B5-CLOSED-B6-FROZEN-RUNNING reply and ending were read.
B5 targeted repairs may remain; QC2 is NOT_ACCEPTED pending terminal B6.
Keep the1579-file candidate frozen and do not duplicate expensive running
tests. After all terminal, verify source/origins/JUnit/exits, QC1 transports/
native arithmetic, M1/M2 cache/pfor/scalar/resources and original4 100wireTF/
third/legacy guards. Only then propose explicit supported-subset review; on
failure preserve receipts and repair a new candidate. No speculative safety
stage/default migration, all R2 gates OPEN/full goal ACTIVE INCOMPLETE/localonly.

## QC2 Terminal Acceptance And QC3 Received Prompt

The completed QC2-B6-LATEST-TERMINAL-EXPLICIT-SUBSET-REVIEW response was
fully read through its ending. Based on supplied local evidence (not reviewer
source inspection), QC2_EXPLICIT_PUBLIC_ARITHMETIC_SUPPORTED_SUBSET_READY_FOR_REVIEW
is accepted. Bare default56 failures remain OPEN. Explicit mode is a migration
mechanism, NOT the final full SDK replacement state or a permanent goal cut.

Next operative prompt: Stage12-B QC3, Default Operator Arithmetic Parity
Migration Preparation. Continue original28-section R2/P4 priorities. Full
independent native Qiskit/PennyLane replacement stays ACTIVE/INCOMPLETE.

QC3-A/P1: preserve original QC2-A/B6 public default56 reds, matrices/qargs/
orders/tolerances/calls. Actual raw Operator compose/default/front/dot/@/
tensor/expand, mixed-radix, noncontiguous qargs, output data/public unitary and
native high-first contracts need separate two-SDK and independent math proof.
Do NOT flip production defaults to manufacture a pass.

QC3-B/P2: add an explicit same-class as_native_operator or equivalent legacy
native arithmetic entry, reusing QC2 kernels/provenance/one matrix system. No
second class/store/executor. Idempotent owned conversion; copy/power/adjoint
preserve convention and representation; validated mixed modes; strict existing
scope/resource/ownership boundaries. First explicit native mode, NOT a default
switch.

QC3-C/P3: audit real internal Operator compose/tensor/expand dependencies,
especially information/channels.py:_embed_operator. Check channels, subsystem/
mixedradix, state/density/noise/compiler/QML/primitives/backend/Gate factories.
Only actual Operator callsites should explicitly select native convention;
never mechanical replacement of Circuit/Pauli/Clifford or other types. Prove
unchanged qargs/product/dims/factor order/channel/Choi/fractionalpower/physical
Gate math using original independent numerical oracles.

QC3-D/P7: produce machine-checkable call inventory: internal Operator native
products/factors -> explicit native; public raw Operator -> future public
default; existing explicit public -> unchanged; from_circuit -> distinguish
matrix representation from call convention; other types -> individually audit,
not auto migrate. Include production Python, numerical tests, examples, public
compatibility, restored IR/QPY owners and user constructors. Repository audit
does NOT certify external user-code compatibility.

QC3-E/P4: shadow differential WITHOUT changing default. Current default and
explicit native must equal independent native math. Explicit public must equal
actual Qiskit default and independent public complex math. Keep results
separate; original56 still red. Prove internal calls can select native without
relying on old defaults; focused callsite tests may block new implicit native
usage, but no broad static rule harming other types.

QC3-F/P7: report migrated sites, remaining implicit native dependencies,
affected old tests/user API, unproved origins/mixedradix, whether all public
defaults can be satisfied without kernel change, numerical/resource/performance
cost and original matrix impact. Actual default Operator convention switch
requires internally verified cleanup AND explicit Owner approval of the
breaking default ABI. This batch must not execute that switch or edit original
56 tests. Shadow/explicit pass is not default-parity completion.

P5 resource/owner/concurrency/atomicity; P6 latest Main/Alternate/TF-MPS/
strictSDKfree affected regression. Protect QC1, QC2explicit, nativepower,
subsystem/mixedradix/channels/Circuit/Compiler/IR/QPY/SV/Density, TF7/8 exact
20/100/original4FoRRoF/third, M2cachedRoF/defaultpfor/scalar and ledger/scope.
No MPS expansion/GraphDef whitelist/QASM synthesis/new PL devices. Preserve
real red/green JUnit/exits/origins/reenumerated manifests at each step; QC2
terminal receipts cannot certify any later changed source.

Maximum claim after all P1--P7 proofs:
QC3_NATIVE_CALLSITE_MIGRATION_READY_FOR_DEFAULT_SWITCH_REVIEW, not default
parity. All R2 SDKfree/Main/AlternateFULL/independent4frameworkFULL/GLOBAL>=
91.34108013033072%/68exclusions/original28-sectionmatrix/ALLnumericalexamples/
controlledlegal/fiveactualorigins/full frozen-worktree-staged-commit equality
remain OPEN. Continue existing docs/evidence only, no isolated ownerpage.
LOCALONLY: no stage/commit/push/fetch/history/auth/TLS/install/vendor/cloud/
hardware/financial13/Studio/Router/tag/release changes. Default migration is
preparation only until explicit Owner decision; no permanent subset goal.

### QC3 P1/P2 And P3 Constructor-Scope Decisions

Both completed replies QC3-P1-P2-NATIVE-ENTRY-TARGETED-CHECKPOINT and
QC3-P3-CALLSITE-MIGRATED-AND-CONSTRUCTOR-IMPACT-AUDIT were fully read through
their endings. Direction retained, no QC3 acceptance/default switch. P3 runtime
guard and original Channel/Choi oracle must prove unchanged math. AST hints
must keep aliases/factory/attribute/unknown receivers, not certify absence.
Unresolved provenance cannot be laundered through explicit native selection.

Continue P4--P7, NOT a batch migration of the26 constructor/data candidates.
P7 must separate PROVEN/UNRESOLVED/NOT_APPLICABLE arithmetic receivers from
raw-literal/circuit-derived/native .data consumers. Do not add
from_native_circuit or modify from_circuit defaults this batch. Additional
constructor boundaries are design options with unresolved identity/allocation/
math/ABI proof, not implemented/approved. Record external-user/dynamic receiver
risks explicitly. Current P3 CONFIRMED_NATIVE_ARITHMETIC_CALLSITE_MIGRATED is
not full source/default parity. Maximum QC3 readiness is bounded review only;
original56/default and R2 gates OPEN/full goal ACTIVE INCOMPLETE/local-only.

### QC3 Binary Arithmetic Defect During Freeze

The complete QC3-P5-ACTUAL-BINARY-ARITHMETIC-RED-DURING-P6-FREEZE reply and
ending were read. It confirms a real P5 defect, not a new safety stage: mixed
native/public +/- error1.0317455788350143 and other.data read before owner/
mode/origin admission can launder _new provenance. Stop only owned current
test processes, verify terminal exits, preserve INTERRUPTED/INCOMPLETE receipts;
old SDKfree724/nine examples belong only to48ed candidate. Formal red then
minimal existing _arithmetic admission, no implicit conversion/source guessing,
no default switch/second system. New candidate requires latest targeted and
full affected two-env/TF-MPS/SDKfree/nine-example proof. Native defaults remain
unchanged, no unproved provenance inheritance. QC3 NOT_ACCEPTED, R2/default56
OPEN, full goal ACTIVE INCOMPLETE/localonly.

### QC3 P6B Freeze Review Conditions

The completed QC3-BINARY-CLOSED-NEW-FROZEN-P6B reply and ending were read.
Binary math/owner/group-budget repair has targeted evidence, but QC3 remains
NOT_ACCEPTED until all latestb960cf60 sessions terminal. Keep1585-file source
frozen, no duplicate runs/new stage/default switch/constructor batch. Preserve
old exit2/143 interruption classification, never use it for new success. After
terminal verify manifests/origins/JUnit/exits and propose only bounded QC3
callsite-migration review.32unresolved receivers/26constructor origins and all
original R2/default56 gaps stay OPEN; full SDK goal ACTIVE INCOMPLETE/localonly.

## QC3 Terminal Acceptance And QC4 Received Prompt

The complete QC3-P6B-LATEST-TERMINAL-REVIEW response was fully read through
its ending. It accepts QC3_NATIVE_CALLSITE_MIGRATION_READY_FOR_DEFAULT_SWITCH_REVIEW
as a BOUNDED supplied-evidence development checkpoint, not independent source
inspection. GLOBAL_DEFAULT_SWITCH_NOT_READY/NOT_AUTHORIZED; default56,32dynamic
receivers,26constructor sources,external users,R2full gates remain unverified.
QC1--QC3 supported domains do not complete their SDK-wide requirements.

Next complete operative prompt: Stage12-B QC4, Native Operator Construction
And Matrix-Origin Parity. Continue full independent native Qiskit/PennyLane
replacement ACTIVE/INCOMPLETE. No default arithmetic switch/second Operator/
batch26-site migration. Only actual proved construction/data-basis/public-reuse
defects should be fixed, in service of eventual NO-OPT-IN public SDK parity.

QC4-A/H1: audit real Operator(raw),Operator(nativeCircuit),from_circuit,
Operator(nativeGate),from_instruction ONLY IF PRESENT, Statevector.to_operator,
DensityMatrix.to_operator actual return contract, Clifford.to_operator,
Gate.to_matrix -> Operator, _new/copy/power/adjoint. Record input/data source,
raw representation, input/output dims, arithmetic convention, owner/provenance,
matrix copies, resource/cache identity and subsequent public conversion.
Classify26candidates PROVEN_NATIVE_DEPENDENCY/PROVEN_PUBLIC_COMPATIBILITY/
UNRESOLVED/NOT_APPLICABLE using source AND runtime proof, not AST names.

QC4-B/H2: actual Qiskit2.4.1/2.6.0 public raw/Circuit/from_circuit/Gate
construction and equivalent supported native entries. Independent asymmetric
complex128 2x2/4x4,1/2/3/4qubit,noncontiguous qargs,H/RY/CX,global phase,
nontrivial input state,tensor/expand,integer/fractional power,copy/adjoint,
input/output dims,realJSONIR/QPYv13. Compare whole complex matrices/amplitudes,
not probability-only or arbitrary phase tolerance. Original56 arithmetic
default reds unchanged; explicit success must not replace them.

QC4-C: raw Operator(U).data keeps defined literal numeric semantics; never
unconditional reversal for migration preparation. Prove Circuit/Gate/state-
derived data matches its representation. Follow existing native execution/
matrix construction -> existing Operator -> provenance -> explicit public
conversion -> public unitary. No gate-name/value/label/address origin guessing.

QC4-D/H3: repair only actual math/provenance red at existing factory/_new/
validated-owner boundary. Same owned matrix storage, no array registry; native
Circuit.unitary q0-first and QC1/QC2 public representation unchanged. No private
QPY sidecar, MatrixFunctions/power math change. Do NOT precreate
from_native_circuit; propose only if proved unavoidable with concrete ABI,
identity, math and allocation evidence.

QC4-E/H4: individually check true .data/.power consumers among26: Gate
factories,AnnotatedOperation,state/density,Clifford,Pauli/sparse,channels,
random/metrics,compiler/serialization proof. Use independent numeric oracles.
For each, identify required native/public coords, reliance on constructor
default, need for existing native selector, additional buffers and applicable
GateCircuitLimits/ResourceScope. No mechanical changes absent a proved scoped
numeric/source defect.

QC4-F/H5: existing owner/ledger/budgets; illegal matrix/shape/dtype/dims,
foreign subclass/side-effect data,forged provenance,expired owner,exact budget
and budget-minus1,copy/power/adjoint,concurrent readonly construction,source
Circuit mutation,failed construction recovery. Applicable source/resource
admission BEFORE dangerous reads/copies; no partial published Operator/source
or ledger pollution. Do not infer unsupported owner contracts from names.

QC4-G: legal construction -> explicit native/public -> arithmetic -> public
unitary -> existing Compiler -> SV/MPS -> actualJSONIR/QPYv13 -> restored
detached owner -> public reuse. Preserve QC1exactly-once,QC2explicit,QC3native
callsite and binary guards, originalpower/branchcut,TF7/8 original4actual100wire
mixedAD/third,M2cachedRoF/defaultpfor/scalarlowering,Channel/SuperOp/Choi. No
extra QASM synthesis/MPS truncation feature.

QC4-H/H6: after H1classification,H2red,H3repair,H4consumer,H5resources, run
latest two-env broad/TF-MPS/strictSDKfree/actual numerical examples, with real
red/green JUnit/exits/origins/reenumerated before-after manifests. QC3 receipts
cannot certify later changed source. H7 explicit remaining default-migration
blockers, unresolved no-opt-in public failures and source/ABI/external-user
risks. Max bounded proposal
QC4_OPERATOR_CONSTRUCTION_ORIGIN_SUPPORTED_SUBSET_READY_FOR_REVIEW, not full
replacement or permission for global default switch. Must prove raw/derived
sources distinct, supported construction math/data/dims/provenance/convention,
no repeated conversion, ownership/resources and real consumer math, with all
gaps explicit. Actual breaking default migration still needs Owner decision.

Original R2 SDKfree/Main/AltFULL/independent4frameworkFULL/GLOBALline>=
91.34108013033072%/68exclusions/original28matrix/ALLnumericalexamples/
controlledlegal/fiveactualorigins/fullfrozen-worktree-staged-commit equality
OPEN. M1/M2/M3full INCOMPLETE. Strict LOCALONLY: no stage/commit/push/fetch/
history/auth/TLS/install/vendor/cloud/hardware/financial13/Studio/Router/tag/
release changes. Existing docs/evidence only, no isolated owner-facing page.
Do not permanently maintain Native/Public opt-in as the full SDK endpoint.

### QC4 State-Origin Red Review

The complete QC4-H1-H2-ACTUAL-STATE-PROJECTOR-ORIGIN-RED reply and ending were
read. Continue QC4, NOT_ACCEPTED. Formal asymmetric complex state/density
projector red must precede minimal existing provenance repair. Native numbers,
dims and legacy arithmetic stay unchanged; state projector remains one owned
buffer, density operator borrowed alias, explicit public conversion separately
owned. Validate actual mixed-radix mapping independently of arithmetic mode;
never infer origins from Hermiticity/rank/trace/names/values. No blanket tags
for Clifford/Pauli/Kraus/random/Gates. Test source mutation, exact/minus-one
budgets and actual downstream unitary/Compiler/SV/MPS/JSON/QPY paths. Nonunitary
projectors must be refused, not relabeled as successful unitary execution.
Main2.4.1/Alt2.6.0 same inputs; absent from_instruction stays NOT_APPLICABLE.
Default56/R2/full independent replacement remain OPEN/ACTIVE INCOMPLETE;
strict local-only boundaries unchanged.

### QC4 H3--H5 Review Continuation

The complete QC4-H3-H5-STATE-ORIGIN-GREEN-BOUNDED reply and ending were read.
Direction accepted for continued work, NOT QC4 acceptance. Keep basis/mode
independent, densityalias/publicsnapshot distinct, projector rejection real.
Complete Gate/annotation/channel consumer audit and27candidate classifications
without equating count to migrations, then latest frozen H6 two-env broad,
TF20/100original4mixedAD/third, strictSDKfree and9examples with actual imports,
manifests/JUnit/exits. Old108/2083 are not later-source certification. No new
stage/defaultABI switch; full goal ACTIVEINCOMPLETE/R2OPEN/localonly unchanged.

### QC4 H4B Received Prompt: Annotation And Kraus Origins

The complete QC4-H4-CONCRETE-OPEN-CONSUMER-REDS reply and ending were read.
Priority: repair BOTH actual H4 reds inside original QC4-H4/H5, no new stage
and no default ABI switch. State-origin passing gates cannot hide these reds
or redefine them outside supported scope. QC4 remains PARTIAL/NOT_ACCEPTED.

Preserve tmp/r2o3b-qc4-h4-open-origins-corrected-* failures and original
incorrect Kraus matrix-gauge test receipt. Do not change circuits/matrices/
tolerances. Annotation inverse uses complete complex matrix/global phase;
channels compare complete SuperOp, since Kraus factor gauges are nonunique.

Trace native Circuit -> Gate/annotation -> inverse modifiers -> native matrix
resolution -> Operator -> explicit public conversion, recording actual basis,
_base_gate preservation, modifier order, to_matrix coords and copy/inverse/
power/control derivatives. Repair the existing validated generation boundary,
not generic Operator(raw). Preserve raw literal UnitaryGate(U) inverse and
annotations; never universal-native-tag annotations or blindly wrap resolved
gates. Track Circuit -> channel -> Kraus -> Operator similarly: internal basis,
vectorization/subsystem order, alias/ownedcopy and origin. Tag ONLY proven
native physical coordinates; no universal rawKraus/Channel/Choi/SuperOp tags.
General/multi-Kraus nonunitary maps must retain proper to_operator refusal.

Independent tests: native circuit-derived and raw literal annotations; inverse,
power,control,combined inverse/control, asymmetriccomplex/globalphase and
existingJ/H paths. Channels: single nativeunitary,rawliteral,Circuitderived,
multi-Krausnonunitary,fullSuperOp/Choiconsistency,noncontiguouswires,source
mutation andcopy/derivedorigins. Reuse existing Operator/Gate/Channel owners,
validated factories/_new, basis conversion andGateLimits/UnifiedLedger/Scope.
If a specific source cannot be expressed, minimal readonly origin at a proved
factory is allowed, but no global ndarray registry/secondsystem/valueguessing.

Resources: forged Gate/Channel owner,side-effectdata,invalidmodifiers/dims,
unsupportedchannel-to-operator,oversizematrix,parentchildledger,readonly
snapshot,recovery. Admission before untrusted reads; no partial published
Operator/provenance/reservation leaks. First rerun originaltwo mathematics
reds, then statefactory/Gatepower/QC1/QC2/QC3/channels/compiler/IR/QPY/
TF7TF8original4100wiremixedAD/true-third/strictSDKfree. Only after these pass
freeze latest QC4 for originalH6 twoenvbroad+nineexamples. A pre-H4B state-only
freeze had already started before this completed reply was received; its
terminal results can certify only that state-factory candidate, not QC4/H4B.

Default56/M1M2M3full/R2 gates OPEN; full native replacement ACTIVEINCOMPLETE.
Strictlocalonly/noGit/install/cloud/hardware/Studio/Router remains unchanged.

### State-Factory Terminal Review And Original H4B Continuation

The complete QC4-STATE-FACTORY-TERMINAL-REGRESSION-H4B-REMAINS-OPEN response
and ending were read. Confirms supplied state-factory7258/305/805/nine-example
receipts show no regression in tested scope, NOT independent source inspection
or H4B/QC4-H6 acceptance. TWO actual H4B reds and default56 remain OPEN.

Continue original H4B with two separate repair loops, annotation FIRST, Kraus
SECOND. Test existing Operator(resolved) only with Circuit-derived inverse/
control versus raw literal UnitaryGate semantics; no unconditionalnative tag.
For channels prove Circuit -> Kraus -> copy/representation conversion ->
Operator origin with FULLSuperOp/Choi oracles and correct multi-Kraus refusal.
Preserve old originalredinputs/tolerances/assertions, basis/mode separation,
foreignowner admission beforeproperties, existing work/storage/scope/failure
atomicity and QC1--QC3/state/TF7TF8 behavior. Reproduce originalreds -> locate
eachsourcegap -> minimalexistingfactoryrepair -> raw-vs-derived/resource
specialties -> latesttwoenvbroad/TFMPS/SDKfree/nineexamples. Anyfuture source
change makes current7258/305/805 baseline-only, never newcandidate proof.
QC4 PARTIAL/NOT_ACCEPTED; fullreplacementACTIVEINCOMPLETE; alloriginalR2 gates
OPEN. Strictlocalonly/noGit/install/cloud/hardware/financial13/Studio/Router.

### QC4 H4C Limited Hybrid Source Descriptor Approval

The complete QC4-H4B-RAW-LITERAL-CONTROL-PERMUTATION-PROPOSAL reply and ending
were read. Authorizes original QC4-H4B work, not a new SDK stage/default switch:
one finite readonly representation variant on SAME Operator for an exact
validated raw UnitaryGate(origin=None) plus bounded ordered annotation modifiers.
Unknown/Generic/dynamic/foreign source bases are NOT admitted to this variant.
Preserve original data, owned storage, native arithmetic, existing matrix
permutation/admission/resource systems; no registry/secondexecutor/QPYsidecar.

Important mathematical correction: public conversion must move the control and
target REGISTERS as well as reverse control significance; reversing only the
control prefix is insufficient. Define independent hybrid_index(cbits,tbits),
public_index and native_index, enumerate allrows/columns/bijections for c,k=1,2.
For source h=Cbig*2**k+Tlittle, desired p=Tlittle*2**c+Clittle and
n=Cbig*2**k+Tbig. No dense permutation matrix; bounded existing owned index
permutation is required. Different inverse/power/control orders, open/closed
states, asymmetriccomplex/globalphase must match BOTH actual SDK versions.

Admit source/shape/dims/controlcount/descriptor before foreign reads or dangerous
allocation. At most one variant plus necessary control/target widths; propagation
through copy/adjoint/power only with preserved coordinate meaning. Single
hybrid->native/public conversion boundary, repeated explicitselection idempotent.
Public Operator(annotation)->unitary and legitimateappend(UnitaryGate) require
unchanged U/qargs/label inputs and complete native SV/MPS complex amplitudes;
existing Compiler and real supported QPY13/JSON IR roundtrips. Unsupported
modifier encodings keep typedrefusal, no standardinteroperability claim via
private origin metadata. Owner/memory equal-minus1/concurrentreadonly/failure
atomicity, originaltwoH4B/state/QC1-QC3/channel/power/TF7TF8original4mixedAD/
thirdrefusal and actualtwoenv/SDKfree affected regressions remain required.

Raw uncontrolled literal staysliteral; Circuit-derived staysnative; unproved
mixedwrappers remainunresolved. Default56/fullSDK/R2 gates stayOPEN, fullgoal
ACTIVEINCOMPLETE; strictlocalonly/noGit/install/cloud/hardware/auth/financial13/
Studio/Router. No acceptance granted by the proposal approval itself.

### QC4 H4C Frozen-Validation Review

Complete QC4-H4C-HYBRID-MATH-GREEN-READY-FOR-LATEST-FREEZE reply and ending
were read. No deterministic rollback defect identified from supplied local
receipts; maintain latest source freeze until all six H6 sessions terminal.
No new stage/default ABI migration or further production edit now. Verify
descriptor propagation, exactly-once native/public conversion, unproved-wrapper
refusal; distinguish standard materialized matrix QPY/JSON transport from
arbitrary modifier interop; numeric and equal-minus1/no-leak resource proof.
Structural fields/source checks are not private-attribute tamper authentication.
Then actual manifests/JUnit/import origins/originalfour100wiremixedAD/third
refusal/default56 states. Current3345/229 remain older targeted checkpoints,
not later-source gates. QC4 still PARTIAL/NOT_ACCEPTED, H4C TARGETEDGREEN/
FROZENVALIDATIONRUNNING, fullgoalACTIVEINCOMPLETE/R2OPEN/localonly unchanged.

### QC4 H4B/H4C Bounded Acceptance; H4D Received Prompt

The complete QC4-H4B-H4C-LATEST-SIX-TERMINAL-REVIEW reply and ending were
read. Accepts QC4_OPERATOR_CONSTRUCTION_ORIGIN_SUPPORTED_SUBSET_READY_FOR_REVIEW
ONLY as supplied-evidence local development acceptance of proved construction/
hybrid sources, not independent code inspection, QC4_DONE, default public parity
or full SDK. Latest1595/source7489/305/932/nineexamples are current baseline;
selected equality is not full worktree/staged/committed runtime equality and
4oldxfails are not implemented successes. All full goals/R2 remain open.

Next COMPLETE operative prompt: original QC4-H4D, Hybrid Operator -> Native
Channel construction closure, no new SDK stage/default-arithmetic migration.
Goal: remove the actual bare Kraus(Operator(raw-controlled-annotation)) refusal
without requiring users to select an explicit mode manually forever. Normalize
ONLY admitted proved hybrid sources at the existing native Channel boundary.
Reuse Operator origin, existing hybrid->native permutation, Channel/Kraus,
SuperOp/Choi kernels, GateLimits/UnifiedLedger/Scope. No second system/registry.

D1: turn the current diagnostic into permanent formal public reds. Actual
Qiskit2.4.1/2.6.0 and native use same asymmetric complex U, annotation, control
state/qargs/globalphase and same Operator(annotation)->Kraus->SuperOp/Choi
calls. Save channel_matrix_origin refusals; explicit selection pass is NOT
the original public-call pass. Do not premutate matrices/inputs/tolerances.

D2: locate the single existing Operator->Channel numeric consumption boundary.
Admit exact source/type/descriptor/dtype/dims/shape/caps first. For only the
proved hybrid domain, use the existing permutation to one bounded OWNED native
snapshot, pass it to existing construction, record true normalized native
origin. Do not mutate original Operator.data or tag all Channel inputs native.
Raw literal path unchanged; already-native Circuit-derived Operators must not
be converted twice. Snapshot/storage ownership must be explicit, not zero-copy.

D3: independent whole-map proof and BOTH actual SDK versions for c/k1,2,
open/closedstates,inverse/power/controlorder/globalphase; raw/native/hybrid
sources; copy/adjoint/conjugate/representationconversions; FULLSuperOp/Choi;
noncontiguouswires and legal multi-Kraus nonunitary maps. Verify E(rho)=U rho Udag
and actual column vectorization. Kraus gauges are nonunique; preserve full
annotation matrix phases and compare complete channels, not gauged factors.

D4: hybrid provenance becomes native ONLY after normalization. Copies and
representation changes preserve exactly-once source meaning; unknown/mixed
owners never qualified by values. Illegalinput/dims/nonfinite/cap failures
before dangerous matrix allocation, exact/minus1budget,parent-childaccounting,
all temporary reservations released, readonlyconcurrency/no source/store
pollution/recovery. Distinguish originalhybridbuffer from NEWsnapshot, never
count as one buffer or claim no copy. Source/Channel owners remain unchanged.

D5: preserve state/density->Operator, nativeannotations,Circuit-derivedKraus,
rawliteralKraus,hybridexplicitviews,QC1publicunitary/detachedQPY/JSON,QC2public
arithmetic,QC3nativecallsites,power/branchcut,channels/SuperOp/Choi,TF7TF8original
four100wiremixedAD/true-thirdrefusal. Do not change default compose or admit
arbitraryGenericGate/dynamicwrappers into the hybrid descriptor.

D6: originalpublicred first -> minimalproduction -> actualtwoenvdifferential/
specialties -> freeze latest -> broad2env/TFMPS2env/strictSDKfree/nineactual
examples/default56. Save actual in-process origins/manifests/JUnit/exits and
rawred/green. Current7489/305/932 become baseline-only after any source edit.
Maximum later proposal QC4_HYBRID_CHANNEL_CONSTRUCTION_SUPPORTED_SUBSET_READY_
FOR_REVIEW, never QC4/default/fullSDK done. GeneralChannel/Device/noise/
transforms/plugin/pforvariants/fullMPS and real unknown-wrapper gaps stay open.

Original R2 SDKfree/Main/AltFULL/independent4frameworkFULL/GLOBAL>=
91.34108013033072%/68exclusions/original28matrix/ALLexamples/controlledlegal/
fiveactualorigins/fullGit3state equality allOPEN. Full independent replacement
ACTIVEINCOMPLETE. Strictlocalonly: no stage/commit/push/fetch/auth/TLS/install/
vendor/cloud/hardware/financialhistory/Studio/Router mutation. No tag/release.

### QC4 H4D First-Green Checkpoint Review

Complete QC4-H4D-D1-RED-D2-FIRST-GREEN reply and ending read. No deterministic
rollback defect identified from supplied receipts. Continue original D3->D4->
D5->D6 without new stage. Preserve distinct originalhybrid/normalizednative/
channel sources and exactly-once conversion through derivations. Legal multi-
Kraus maps require whole SuperOp/Choi, trace preservation and independent rho
evolution, not matching gauge-dependent factors or pretending they are unitary.
One owned snapshot means separately accounted source/output buffers, exact/
minus1 preallocation budgets, parent-child attribution, fault release and
readonly concurrency. No widening unproved generalized Stinespring origins.
After focused math/resource verification freeze latest and rerun actualdualSDK
broad/TF-MPS, strictSDKfree, nineexamples and originaldefault56, with manifests/
in-process origins/JUnit/terminalexits. Old7489/305/932 not latestsourceproof.
H4D TARGETEDGREEN/NOT_ACCEPTED, QC4fullINCOMPLETE/default56OPEN/fullgoalACTIVE
INCOMPLETE/R2OPEN/strictlocalonly. No defaultarithmetic change or scope expansion.

### QC4 H4D Frozen Validation Checkpoint Review

Complete QC4-H4D-FOCUSED337-FROZEN reply and ending read. No deterministic
rollback defect found from supplied focused receipts. Keep latest1598candidate
frozen until all six H6 sessions terminal; no new matrix/source edits now.
Retain207pass1fail incorrectwireoracle receipt, classify correction as test-only,
not productionmath repair. Verify exactly-once normalizedsource/ownership and
raw/native/multiKraus/QC1-QC3/power/TF100wiremixedAD/thirdrefusal on latestsource.
Then submit actualterminal/JUnit/in-processorigins/before-aftermanifests for
bounded QC4_HYBRID_CHANNEL_CONSTRUCTION_SUPPORTED_SUBSET_READY_FOR_REVIEW.
No acceptance beforeterminalproof, default56/fullR2OPEN/fullgoalINCOMPLETE.
Localonly/noGit/install/cloud/hardware/Studio/Router changes unchanged.

### QC4 H4D Terminal Review And QC4 H5 Received Prompt

Complete QC4-H4D-LATEST-SIX-TERMINAL-REVIEW reply and ending actually read
from the existing authorized Chrome conversation. The following removes only
duplicated accessibility headings/table echoes and line-wrap artifacts; all
numbered requirements and the final limits are retained.

结论：接受 QC4_HYBRID_CHANNEL_CONSTRUCTION_SUPPORTED_SUBSET_READY_FOR_REVIEW，
确认 Hybrid Operator -> Native Channel 构造的已验证支持子域通过所报告的
开发期验收。这是基于所提供证据的支持子域审阅，不是独立源码审计，也不
代表 QC4 全域、Operator 默认公共 parity 或完整 Qiskit/PennyLane 替代完成。
六份最新1598文件回执：Main/Alternate broad各7703pass/4既有xfail，TF-MPS各
305pass，Strict SDKfree1053pass，九个数值示例exit0。原57公开Hybrid Channel
案例、四条100-wire mixed AD及true-third refusal保持PASS；默认各56fail/5pass
继续OPEN。未发现报告中必须撤销H4D的确定性数学或资源缺陷，不再补重复Channel
测试。完整SuperOp/Choi/密度演化、一次规范化、分开计量snapshot和原buffer、
失败不发布部分Channel、未知nested Stinespring拒绝、原红灯与测试搭建错误的
区分都须保留。一般Channel兼容性、默认算术、矩阵alias、动态线路和全API仍未完成。

#### Stage 12-B QC4-H5: Gate / Clifford Operator Construction Origin Parity

继续原QC4，不创建新阶段，不修改Operator默认arithmetic convention。本批目标：
针对真实Gate/Clifford -> Operator来源缺口，完成公开构造、完整复矩阵、后续
public unitary和合法序列化的一致性。优先Gate/Clifford，不继续扩展已通过的
Kraus/TF-MPS数值内核，也不创建新的来源安全框架。

H5-1：先找真实红灯，不直接增加来源标记。
审计实际存在的Operator(Gate)、Operator(Circuit-derived Gate)、
Operator(AnnotatedOperation)、Gate.to_matrix()、Clifford.to_operator()、
Clifford.to_matrix()（仅当实际存在）、Operator._new()/copy()/adjoint()/power()，
及当前provenance/basis conversion。实际Main Qiskit2.4.1和Alternate2.6.0分别运行。
原始UnitaryGate(U)保留public literal basis；Native Circuit-derived Gate保留
native matrix basis；Native Gate inverse/power/control依派生前真实来源；Native
Circuit-derived Clifford依实际生成矩阵基序；Raw/外部Clifford不得仅按类型猜native；
Operator -> Gate -> Operator必须exactly-once conversion。用非对称复数矩阵、
非连续wires、非零初态、完整相位逐元素比较。只有实测错误触发生产修复。

H5-2：独立Clifford数学验证。
至少2/3/4-qubit Clifford circuits：H、S/Sdg、CX、CZ、SWAP、非连续wires、
inverse和compose。用独立稳定子或矩阵oracle与实际Qiskit Operator比较完整复矩阵。
区分Clifford定义的变换、矩阵相位约定、Native Circuit global phase和Operator基序。
若合法Clifford表示仅在未固定全局相位上不同，必须明确来源/约定证明，不能一概忽略相位。

H5-3：只在真实失败的合法构造边界做最小来源修复。
复用现有Operator provenance；不创建第二个Operator/Clifford/Circuit，不重写Gate
matrix engine，不改native .data/q0-high合同，不使用全局ndarray来源注册表，不根据
Gate名称或矩阵值猜来源。若Gate.to_matrix()返回无provenance的原始ndarray，而已
准入Gate owner自身保有合法来源，应从该owner传递，不从ndarray猜测。Raw Gate保持
literal，Native Circuit-derived Gate保持native，Hybrid只按QC4-H4C已证明条件转换。

H5-4：对每条已证明合法来源执行完整公开路径。
Native Gate/Clifford -> Existing Operator construction -> Explicit public
conversion -> Public QuantumCircuit.unitary -> Native Compiler -> Statevector/
MPS -> JSON IR/QPYv13 -> Restored detached owner -> Public reuse。
与两个已安装Qiskit版本比较完整复振幅，不在测试侧调整输入U或qargs。标准格式不支持
的Clifford/AnnotatedOperation记录保持原typed refusal，不用私有QPY sidecar伪造互操作。

H5-5：资源、所有权、失败原子性。
至少验证forged Gate/Clifford owner、foreign property callback、malformed definition、
invalid dims/width/matrix dtype、work/memory equal与one-below、source mutation、
owned buffer、copy/power/adjoint、parent/child ResourceScope、concurrent readonly、
fault recovery。既有owner admission必须在危险属性读取或矩阵复制前生效；新增来源
传播不能绕过QC1-F/QC2-B5/QC3-P5非法owner拒绝。

H5-6：保持既有支持子域。
回归QC1 publicUnitary、QC2显式Qiskitarithmetic、QC3 Nativearithmetic、QC4
Statevector/DensityMatrix origin、AnnotatedOperation原两条红灯、Hybrid56条、
HybridKraus57条、Channel/SuperOp/Choi、Operator.power/branchcut、Compiler/IR/QPY、
TF7/TF8原四条100-wire mixedAD、true-thirdrefusal、M2 cachedRoF/defaultpfor/scalar
lowering。不重复开发已经完成的TF-MPS或Channel数值内核。

H5-7：执行顺序。
A. 真实Gate/Clifford构造差分，保存原始数学红灯。
B. 证明Native/Raw/Hybrid来源及相位合同。
C. 仅修复实际失败的来源边界。
D. Public Circuit/Compiler/Statevector/MPS/JSON/QPY端到端。
E. Owner、资源、并发和异常原子性。
F. Main/Alternate最新候选受影响回归。
G. StrictSDKfree、九数值示例、原默认56parity核查。
每步保留真实JUnit、exitcode、同进程importorigins、selected-source before/after
manifest。源码变更后旧H4D7703/305/1053不可代替最新候选回归。

最多提出QC4_GATE_CLIFFORD_OPERATOR_ORIGIN_SUPPORTED_SUBSET_READY_FOR_REVIEW。
明确实际修复来源、当前已正确而未改的来源、仍不支持的公共构造API、互操作QPY/IR
路径、只能typedrefusal的路径、资源和所有权成本、仍未解决的默认.data/arithmetic
parity。不得把测试用例数量作为SDK API完成率。

H5不是新项目阶段，是原QC4 Operator构造来源任务继续。完整独立原生Qiskit/
PennyLane replacement保持ACTIVE/INCOMPLETE；原R2 SDKfreeFULL/MainFULL/AltFULL、
独立四框架FULL、GLOBALcoverage>=91.34108013033072%、exclusions68不增加、原28section
matrix、ALLnumericalexamples、controlledlegal、五实际importorigins、frozen/worktree/
staged/commitequality继续OPEN。严格localonly：不stage/commit/push/fetch，不安装依赖/
vendor，不修改认证/TLS，不调用云/真实硬件，不改金融历史证据，不扩大Studio/Router，
不tag/release。下一步优先Gate/Clifford构造来源的真实公开数学缺口；已验证支持子域
逐项审阅通过不代表QC4full完成，原默认56parity仍OPEN，完整SDK替代目标不变。

### QC4 H5 Initial-Red Review

Complete QC4-H5-INITIAL45RED-35GREEN reply and ending actually read. Continue
existing H5, not newstage. Finite readonly origin on SAME Clifford allowed
only from proved construction: nativeCircuit/nativeOperator, rawtableau/raw
matrix literal, mixedcompose/tensor unresolved. Never blanket-mark allClifford
native. Source->result numeric relation must be proved before propagation.
Projective Clifford tableau equivalence may use each-own intrinsic pivot
representative; exactnative synthesis/Operator.data/inverse/power/transport
must retain full complexphase. This is NOT exactQiskitsynthesisphaseparity.
Circuitglobalphase discardedbytableau must not be recreated. Prove derivations
individually and both homogeneous algebra domains; mixedsource keptunresolved.
Admit exactClifford before __array__/data/properties, close wrongtableau
coercion/nativebasisloss, preserve literalbehavior, use existingto_instruction/
UnitaryGate paths (Operator.to_gate absent bothSDKs), then publicexecution/
serialization/resources/latestregressions. Gate20alreadygreen needsno math
changes. FullgoalACTIVEINCOMPLETE/default56/R2OPEN/localonly unchanged.

### QC4 H5 Focused-345 Frozen Review

Complete QC4-H5-FOCUSED345-FROZEN reply/ending read. No deterministicrollback
defect in supplied evidence; freeze5ba1601 candidate and await sixterminals,
NOT_ACCEPTED. Exactly-once instructionnormalize through append/Compiler/QPY/
IR/detachedreuse, no falselegacy/customprovenance; native/literal/unresolved
and projective/fullphase distinctions; actualsnapshot+Gatecopy+validationpeak,
equal/minus1/no foreigncallback/leak/read-onlyconcurrency. No newcode/matrix
untilrealregression; require actualexits/JUnit/origins/manifests/originalfour
100wiremixedAD/thirdrefusal/default56. Fullgoal/R2/strictlocalonly unchanged.

### QC4 H5 Real Mixed-Radix Defect Review

Complete QC4-H5-FROZEN-REAL-MIXEDRADIX-DEFECT reply/ending read. The measured
projectivematherror (diagnosticmax1.4142) is real, NOT dismissible because pure
qubit casespass. Permit boundednormalize only qualifiednativeOperator with
num_qubitsNone, legal2^n square matchingdims and validated partition-to-qubit
map; do NOT infer total-bit reversal from num_qubitsNone alone. Independently
prove(4,),(2,4),(4,2) indexmaps, untouchedsource.data/dims, same projectiveClifford
and exactnative-synthesis outputphase. Existingfrom_operator path uses existing
as_qiskit_operator thenfrom_matrix public/literalframe; no generalreshape/data/
tableau/to_matrix kernelchange. Normalizeownedbytes/peak/equalminus1/failure/
concurrency; purequbitnative/raw/public unchanged; invaliddims/nonClifford/
unknownowner precisely refused. ActualQiskit from_operator accepts the tested
qudit partitions; directQClifford(QOperator) rejects (native constructor support
is preexisting extension, not an upstreamAPIparity claim).

Knownbad5ba candidate's four ownedlongprocesses may be interrupted after exact
PID/command identification, actualsignal/terminalexit and partialreceipts kept.
Old1197pass4optionalSDKskips/nineexamples cannot count as repairedcandidateproof.
Formalred->minimalfix->freshH5/QC1-QC4/Compiler/IR/QPY/TFMPS/SDKfree/nineexamples.
FullgoalACTIVEINCOMPLETE/default56/R2OPEN/localonly, no Git/cloud/install/UI.

### QC4 H5 R1 Refrozen Review

Complete QC4-H5-R1-MIXEDRADIX363-REFROZEN reply/ending read. No deterministic
rollback defect in supplied R1 receipts; maintain1601 SHA0924e250... freeze
until sixfreshterminals, NOT_ACCEPTED. Nineactualreds eachthen363targetedPASS.
Old5ba fourlongsessions terminalexit2 are INTERRUPTED/INCOMPLETE, not R1pass.
Keep independent(2,4)vs(4,2) mapping, not totalbitreverse; projective vs exact
synthesisphase distinctions; originisstructuralnot authenticationagainst
arbitraryPythonprivatefieldwrites. Preserve all raw/native/QC1-QC4/channel/
power/originalfour100wiremixedAD/thirdrefusal/strictSDKfree. No furthercode or
stage beforeterminals, then boundedH5reviewonly. All fullgoal/R2 limits remain.

### QC4 H5 R1 Terminal Review; QPY1 Received Prompt

Complete QC4-H5-R1-LATEST-SIX-TERMINAL-REVIEW response and ending actually read
from the existing authorized Chrome conversation. Duplicate accessibility
headings/tables removed below; all numbered requirements and ending retained.

结论：接受 QC4_GATE_CLIFFORD_OPERATOR_ORIGIN_SUPPORTED_SUBSET_READY_FOR_REVIEW，
仅关闭H5已验证Gate/Clifford->Operator来源支持子域的开发期审阅。根据报告的本地
证据，无必须回滚的确定性缺陷；不是独立源码/远端CI审核，不代表QC4全域或完整
Qiskit/PennyLane parity。最新R1 Main/Alt各8043pass/4既有xfail，TF/MPS各305pass，
原四100-wire mixedAD/true-thirdrefusal保持PASS，专项各363pass，SDKfree1212pass/
4可选上游skip，九示例exit0，默认各56fail/5pass继续OPEN。认可来源、projective/
完整原生合成相位分层、真实QPY13双向/IR/SV/MPS/detached复用，以及保留实际
Qiskit.from_operator和原生构造器扩展的ABI区别。下一项优先QPY13参数身份/索引，
针对原有两条相关xfail，不继续扩大Clifford来源矩阵。

#### Stage 12-B QPY1: V13 Parameter Identity, Vector Index And Symbolic Expressions

继续原R2/P4 full independent native Qiskit/PennyLane replacement，不创建第二
序列化引擎或新SDK阶段。本批唯一主要任务：定位并修复实际QPY13参数索引/符号表达式
互操作缺口，优先原两条xfail双版本数学和二进制红绿证据。不处理默认Operator56，
不扩展MPS/Clifford/Studio/行业案例。

1. QPY1-A：精确锁定原两条xfail。
从最新Main/Alt JUnit记录完整nodeID、原输入Circuit/ParameterVector、实际异常或数据
差异、QPY header/record类型、native dump/load路线、xfail原因，区分UUID/vector
index/表达式映射/上游版本。不预设均为native writer索引错误。分别实测四方向：
Qiskit->Qiskit、QuantumBridge->QuantumBridge、QuantumBridge->Qiskit、
Qiskit->QuantumBridge，实际Qiskit2.4.1和2.6.0分开记录。同版本上游写读也失败须
单列upstream failure，不为追逐上游缺陷而写不合标准字节。

2. QPY1-B：定义可证明的身份合同。
独立用例至少：单Parameter、多元素ParameterVector、shrink/regrow、非连续index、
同名不同UUID、同UUID多occurrence、不同vector同index、部分绑定、嵌套表达式、
+/-/*/常量平方及已有其他符号运算、AnnotatedOperation数值exponent+符号base、
copy/compose/decompose后身份。逐项验证UUID、vector root/size/index、每次出现身份、
排序/.parameters、恢复符号AST、绑定后的线路及Compiler/SV/MPS真实数学。值相同不能
替代身份正确。

3. QPY1-C：实际v13字节结构。
依据官方QPY13文档及本地双版本真实写出的记录审计现有codec：
PARAMETER_VECTOR_ELEMENT、PARAMETER_EXPR、PARAM_EXPR_ELEM_V13、symbol map、
UUID lookup、vector index/size、表达式子记录顺序、nested start/end、substitution
mapping及AnnotatedOperation引用关系。v13表达式用操作序列，不只旧SymPy/SymEngine
序列化。不同QPY版本的substitution mapping变化不能未经验证套用到v13。
不复制Qiskit源码，仅公开格式规范、独立二进制fixture、实际SDK输出作为验证依据。

4. QPY1-D：按证据修身份/数学根因。
逐条分类nativewriter、nativereader、Vectoridentity、Expression重建、v13格式错配、
实际upstream限制、未支持symbolicfeature或错误测试预期。只改确证最小根因。
不重写整个reader/writer，不私有sidecar，不伪header冒充新版，不用name代替UUID，
不按排序重造vectorindex，不预绑定数值掩盖身份缺失，不放宽原数学容差，不为新问题
加xfail/skip。上游真缺陷保留独立差异，证明native标准范围内正确行为。

5. QPY1-E：真实线路/导数端到端。
Native symbolic Circuit -> QPY13 bytes -> restored -> partial/full binding ->
Compiler -> Statevector/MPS -> Expectation -> JVP/VJP/HVP，与恢复前独立原生数学对照。
另实际QiskitQPY->Native及NativeQPY->Qiskit两方向，检查vectorindex/UUID/表达式
跨实现读取，不只内部roundtrip。未支持符号exponent、typedclassicalscope或非标准
Gate definition保持已有精准Unsupported，不增私有格式。

6. QPY1-F：资源/恶意记录/失败原子性。
复用既有序列化限制、GateCircuitLimits及资源体系。至少invalidUUID、重复UUID冲突、
invalidvectorindex/size、截断表达式、循环/过深、symbolmap缺条目、超大record/表达式、
非法opcode、nested序列格式错、参数owner失效、构造中途异常、资源不足、失败后合法
QPY仍可读。危险分配前拒绝，失败无部分Circuit发布/既有owner污染/live reservation
泄漏。不对可信二进制字段以外的任意Python对象做未验证属性读取。

7. QPY1-G：必要保护回归。
QC1Unitary/标准QPYmatrixrecord，QC2/QC3 Operatorprovenance，QC4 Gate/Clifford来源，
P4-U1 AnnotatedOperationQPY13，P4-U2 ParameterList/Vector，P4-U3D Bit/Register，
NativeCompiler/IR，symbolicmovingprojector，M1/M2cachedRoF/defaultpfor，TF7/TF8原四
100-wire mixedAD，true-thirdrefusal，Operator.power，SDKfree和数值示例。
先定向数学，再冻结最新候选，Main/Alt受影响宽回归。当前R18043/305/1212不能移作
未来新源码通过证明。

8. 执行顺序及证据。
A 原两条xfail精确定位、双版本上游自检。
B UUID/Vector/index/AST独立oracle。
C 标准v13记录解析/对照。
D 只修确证writer/reader/身份根因。
E 双向QPY/Compiler/数学/AD。
F 资源/异常/非法记录。
G 两环境及SDKfree回归。
每批原redJUnit、独立QPYfixture、实际importorigins、Main/Alt版本、before/after
selectedmanifest、真实exit、身份/数学差异、最新源码最终回执全部保留。

9. 交付边界。
最多QPY1_V13_PARAMETER_IDENTITY_SUPPORTED_SUBSET_READY_FOR_REVIEW。列真正修复的
身份/索引、实际Qiskitbug、仍不支持v13类型、原两xfail是否还在、不同版本真实差异、
双向恢复/完整数学、资源/所有权合同。不能因上游xfail属于上游缺陷而删测试或声称
全部QPYparity完成。

原R2 SDKfreeFULL/MainFULL/AltFULL/独立四框架FULL/GLOBAL>=91.34108013033072%、
exclusions68不增加、原未改28sectionmatrix、ALLnumericalexamples、controlledlegal、
五actualorigins、frozen/worktree/staged/commitequality继续OPEN。严格localonly：
不stage/commit/push/fetch，不改OAuth/TLS，不install/vendor，不云/真机，不改金融13项
原证据，不扩大Studio/Router，不重写Git，不tag/release。最终决定：H5已验证支持子域
可接受；下一项优先QPY13参数身份/索引真实互操作缺口。完整独立原生替代仍为
ACTIVE/INCOMPLETE。

### QPY1 Initial-Red Review And D4 Correction

Complete QPY1-A/C-INITIAL-REAL-RED response and ending actually read in the
authorized existing Chrome conversation. Three confirmed roots approved:
bounded iterative v13 op255 s/e replay, op13 native symbolicgradient, same
reader-context UUID/name/kind/vectoridentity admission. Keep separate frame
depth/parsework/resultAST bounds, reject malformed/truncated/unclosed/empty
frames without partialpublication, preserve UUID/index/freeparameters through
copy/compose/binding/Compiler/math. Existing native calculus, not finite
differences, and all original R2/fullgoal/localonly boundaries unchanged.

Initial review mistakenly requested a native Circuit owner/index repair based
on originaltwo annotationxfails. It required a complete executable owner/index
chain rather than merely changing displayedparameters. We sent the exact test
line202 showing actual qiskit.qpy.load and allfour directionresults, before
making any Circuitedit. Complete QPY1-D4-OWNER-INDEX-CLARIFICATION response and
ending then actuallyread: peer explicitly corrects its earlier interpretation.
Native->Native andPublic->Native index/UUID/bind/math are ALREADY correct;
Native->Public andPublic->Public are real upstream qiskit.qpy.load indexloss.
These two original--runxfail reds are NOT grounds for a native Circuit repair.
No monkeypatch/vendor/privateformat workaround, no deletedoriginaltest.

Both complete replies retain UPSTREAM_2_4_1_MALFORMED_PARTIAL_BIND_QPY as an
observed version-specific defect, not universalwriterfailure: keep actualraw
writerbytes, own2.4readerfailure/native refusal, 2.6success and exactstack
imbalance. Do not accept malformedstack or addxfail. Native partialbound
writerpaths still require true math, no diagnosis substituted for nativepass.

u/substitution remains UNSUPPORTED/NOT_CLOSED, split from the three confirmed
readerroots for review. Only independentbinaryfixtures+identity/substitution
oracles+twoSDKdiff may establish semantic support; syntaxrecognition/length
checks alone are not support. AccurateUnsupported permitted meanwhile, never
ignoremapping. Must retain variablelength/mapping/depth/boundary investigation.

Continue same QPY1: reader math andAST; UUID/vectorroot/index/size/repeated
occurrence/conflict refusal; executablepartialbind/copy/compose/Compiler/
Statevector/MPS/JVP/VJP/HVP; frame/record/ASTwork andfailureatomicity; actual
two-version differences; QC1-QC4/M1-M3/TF7-TF8 original100wiremixedAD/third
refusal protection, freeze andfreshMain/Alt/strictSDKfree/examples. Original
two upstreamxfails remainOPEN. Initial13fail32passMain/11fail34passAlt are
redproofonly; interim212pass/2originalxfail each validfocusedproof, not QPY1
acceptance. QPY1 ACTIVE/NOT_ACCEPTED; independentfullreplacementACTIVE/
INCOMPLETE; default56 andallR2FULL/GLOBAL/original28/legal/threeGitstate gates
OPEN. Strictlocalonly, noGit/install/auth/cloud/hardware/financial/UI actions.

### QPY1 Frozen Three-Root Review; QPY1-H Received Prompt

Complete QPY1-THREE-READER-ROOTS-FROZEN response and ending actually read in
the existing authorized Chrome conversation. Duplicated accessibility table/
headings removed; all numbered requirements and final boundaries retained.

Three confirmed native reader roots form a valid development checkpoint for
latestcandidate regression, NOT QPY1acceptance. Frozen1603source4adfe5c8...
must remain unchanged until allsix actualterminalresults. Latestreported
230focusedpass/2originalxfail each, strict1240pass/4oldoptionalSKIPs andnine
examplesexit0 only applythiscandidate. Broads2env/TFMPS2env stillRUNNING.
Actual2.4.1 partialbindstream residualstack2 is specificupstreaminput/version
defect, not all2.4filesbad. u/subs NOT_IMPLEMENTED, originaltwoindexxfailsOPEN.

#### QPY1-H: V13 Substitution Mapping Reader Closure

Continue sameStage12-B QPY1, not a newSDKstage. Implement boundedstandard
u/subs mapping parse, actualnative symbolicreplacement andtwoSDKinterop.
NoCircuitownershipchange/upstreamQiskitpatch/SymPy-SymEngineexecutor/private
sidecar/formatrewrite. v13/14MAPPING keys areParameternames; laterformatraw
UUIDkeyrules must NOT be substituted. Namekey isbinaryformat only: actual
nativeidentity remains validatedUUID/contextobject.

H0. Finish currentfreeze first. Keep4adfe5c8...1603files unchanged; awaitMain
broad,Altbroad,MainTFMPS,AltTFMPS originalprocesses. Saveactualexits/JUnit/
sameprocessorigins/selectedbeforeafter. ExistingSDKfree1240/4 andnineexamples
belongthiscandidateonly. Only AFTER allsixterminal startproductionedits.

H1. Actualbinaryred. ActualQiskit2.4.1/2.6.0 publicParameterExpression.subs()
QPY13 plusindependentpublishedformatfixtures: single/double/partial/nested
replacement, remainingfreeparameters, samename/differentUUID, sparsevector
index,shrink/regrow,constant/Parameter/Expressionvalues,subs+gradient+s/e,
globalphaseandGateparams. FourdirectionsPublic->Public/Public->Native/
Native->Native/Native->Public perinput. Ifnativewriterdoesnotemit actualsubs
record, do notmisrepresentreaderrepairaswritercompletion. Retainrawfailure
bytes/recordoffsets/JUnit/UUID/AST/boundnumericresults.

H2. Strictv13 name-keyedMAPPING. Verifyopcode15,lhsu,rhsn; boundeddeclared
mappingbytes immediatelyafterrecord; exactconsumption, restoreouterreplay
cursor. ReuseexistingReaderlimits. Rejecttruncated/overflowlength,invalidUTF8,
duplicatekeys,incompletemapping,badvaluetag,illegalnested,trailingbytes,
oversizedmapping,innerunbalancedstack. Neverignoremappingtorecoverapparently
successfulexpression.

H3. Mapname toUUIDidentity onlyinvalidatedexpressioncontext, uniquely. Reuse
canonicalParameterUUID, neverconstructbyname. Ambiguoussamename/differentUUID
failclosed; Vectorroot/index/size/UUIDchecked; replacementexpressionsalsoUUID
admitted. Result.parametersactualfreeparameters. Do notchooseouterCircuit's
unrelatedsamenameparameter. CompareactualtwoSDKlegalbehavior anddistinguish
formatidentityprecisionfromstricternativein-memoryidentitycontract.

H4. ReuseexistingnativeAST/substitution, not strings/eval/finitediff/host
callback. Provesimultaneousvssequentialreplacement,nounintendedrecursive
replacement,nestedremainingfreeparameters,gradientaftersubs,divisionbyzero/
badexponent/branchdomainrefusals,existingworkbudget. PreciselyUnsupported
unsupportedactualmappingvaluetype; nevercoercetofloat.

H5. ExistingQPYlimits,SymbolicExpressionLimits,GateCircuitLimits,UUIDadmission,
UnifiedResourceLedger/ResourceScope. Boundencodedbytes,keycount,valuedepth,
ASTwork/resultsize,replaystack,allocationworkspace BEFORElargematerialization/
expansion. Failureafterpartiallyparsedmultiplesubs: nopartialCircuit/oldowner
pollution/livelease, attemptedworknotwronglyrolledback, subsequentlegalfile
loads. Logicalarrayaccounting isnotPythonallocatorRSSproof.

H6. ActualQPY13->nativeAST->Circuit->partial/fullbind->Compiler->SV/MPS->
expectation->Jacobian/JVP/VJP/Hessian/HVP, independentlyanalyticmath. Test
bothSDKdirections,AnnotatedOperation,Vector,globalphase,copy/compose/decompose,
nativeIR/QPYreserialization. Originaltwoactualpublicindexxfails separately
retained, neverclaimedfixedfromreadermathsuccess.

H7. Realred->minimalfix->newfrozenlatestgates:QPYreader/writer,Compiler/
Serialization,QC1-QC4,ParameterExpression,Operator.power,M1/M2TFAD,TF7/8
originalfour100wiremixedAD,true-thirdrefusal,Main/Altbroads,strictSDKfree,
nineexamples. Actualexits/JUnit/origins/manifests. Ifwriterchanged, additionally
provestandardrecords/version/symbolmapcorrect; no writerrewriteforreaderneed.

MaximumproposalQPY1_V13_SUBSTITUTION_READER_SUPPORTED_SUBSET_READY_FOR_REVIEW:
statelegitimateUUIDresolutionfromnamekeys,actualAST/freeparameters/math,
whichnative/publicdirectionspass,writeractualrecordsupport,remaininglegal
unsupportedexpressions,actualupstreamversionfailures,currentlatestregressions.
NeverfullQPYv13completionfromreader-onlysupport.

FullindependentQiskit/PennyLanereplacementACTIVE/INCOMPLETE. OriginalR2three
envFULL/fourframeworkFULL/GLOBAL>=91.34108013033072%/68exclusions/original28
sections/ALLexamples/controlledlegal/fiveorigins/fullfrozen-worktree-staged-
commit equalityOPEN. Strictlocalonly:noGitstage/commit/push/fetch/auth/TLS/
install/vendor/cloud/hardware/financial13/Studio/Routeractions. Nextaction:
finishcurrentterminals,thenstandardv13u/subsmapping. Do NOTrevisit already
provedcorrectnativeCircuitparameterindex.

### QPY1 Three-Root Six-Terminal Final Review

Complete QPY1-THREE-ROOTS-LATEST-SIX-TERMINALS reply andending actuallyread.
Peerrecords QPY1_THREE_READER_ROOTS_VERIFIED_SUPPORTED_SUBSET fromreported
localreceipts: both8106/4,TFMPS305each,strict1240/4optional,nineexamples,
originalfour100wiremixedAD/thirdrefusalPASS. Actualoriginaltwo--runxfail
each2failed anddefault56fail/5pass remainOPEN. Same1603selectedsourcebefore/
after/current isnot fullworktree/Git3stateacceptance. No deterministicrollback
defectidentifiedfromterminalreport; not an independentcode/remoteCIaudit.

NextpromptUNCHANGED H1trueactualSDK2.4.1/2.6.0u/subsrecords+independentbinary
fixture/mathred;H2-H3variablelengthv13namekeymapping->validatedUUID;H4-H5
existingnative simultaneous/nested/gradient/substitution withbudget/atomicity;
H6-H7actualbilateralQPY/bind/Compiler/SV-MPS/JVP-VJP-HVP thenlatestfreeze/
regression. No inventednativeCircuitindexrepair. Keep actual2.4malformed
partialbindstreamrefusal andspecificscope; no nonstandarderrorrecovery.
u/subs UNSUPPORTED/NOT_CLOSED;three-rootproofcannotclaimit. QPY1fullACTIVE/
NOT_ACCEPTED,fullindependentSDKreplacementACTIVE/INCOMPLETE;originalR2final
gatesOPEN,strictlocalonly/noGit/install/cloud/hardware/Studio/Router.

### QPY1-H1 Format Correction And H4R Retained-Formal Authorization

Complete QPY1-H1-FORMAT-EVIDENCE reply+ending read: two modernSDKwriters need
notemitop15/u. Actualsubs() examplesserializefinalAST; keeprealrawbytes/math
separatefromindependentpublished-v13u fixtures acceptedbybothSDKreaders. No
claimSDKemittedu/historysupport. Confirmwirefacts:opcode15/lhsu/rhsn, first8
lhsbytes!Qlength+8trailingzero (notnumericpadding);MAPPING!Qcount,MAP_ITEM
!HcH, exactboundaries/cursor. Firstprovengoldens p+q,p->r andp->sin(r), then
simultaneous/UUID/freeparams/grad/math. Rawfloat/int andunprovedtags refuse
precisely. Keeporiginalupstreamindex/default56,actual2.4malformedstream,
no newxfail/skip/tolerancechanges, existingwriterASTbehaviorunchanged.

Complete QPY1-H1-RED-AND-FIRST-FIX reply+ending read. Initial37red each retained,
latest99pass/1fail each (atthatpreOct25source) notaccepted. Lastgradientcase
mathcos(r) vsparams(q,r) needsactualAPIvsQPYdiagnosis, not immediatelyassumed
readerbug. H4R R1: actual2.4.1/2.6.0 g=(p+q²).subs(p->sinr),h=g.gradient(r),
values/UUID/parameters/num_parameters/bind/assignq-r, directcoscontrol; distinct
directgrad/subsgrad/u-replay/finalASTwriter. R2: rawsymbolmaps/beforeafteru/
gradientcontext vsnativeASTdependencies/PEparameters/Circuitparameters; don't
mixsymbolreferencesandCircuitindex. R3: hcosr,qderivative0,partial/fullbind,
copy/compose/index/UUID/JVP-VJP-HVP/Compiler/SV-MPS, numericexecutioncondition.
R4: iflegalformalcontractmissing minimallyfixsameowner/context, noCircuitfix/
name-basedUUIDcreation/fakezeroCoreAST/privateformat/looserlimits. Ifcache-only
divergencekeepmathcorrectbutparityredOPEN. R5: actualtwoSDK+analytic+fixture
identitydiagnosisbeforeclosing; latestregressionsafterproductionedits.

Complete QPY1-H4R-DIRECT-SEMANTICS-CONFIRMED reply+ending actuallyread:
directAPIconfirmslegalretainedformalcontext, notcachebug. Limitedexception
APPROVED: existingPEfiniteownedUUIDcontext + nativecalculus/bind/subs and
standardQPYwriterprojectionONLYwherecontextpresent. CoreASTmustremainreal
math, noartificial0*q. Wire-onlyordinaryzeroarithmetic projectionaccepted,
noQPYprivatetag/sidecar/secondengine, existingno-contextbytesunchanged.

#### QPY1-H4R2 Retained Formal Parameter Semantics And Standard Projection

SameStage12-B/QPY1-H, no newstage. R1: freezebothactualSDKAPIevidencefor
f=p+q²,g=subsp->sinr,h=gradientr; value,UUID,formalsets,bind,strict/nonstrict
numeric,realCircuitbind/execution. Controls directcosonlyr,0*p,product
derivatives,const/multiplederivatives andactualreturntypes; do notlabelall
resultsPEwithoutcheckingpublictypes. R2: samePErealAST+validatedownedretained
UUIDs/Parameter-Vectorowners/sourcecontext, separatemathdependencies/formals/
Circuitbindableparams/numericalexecution. Notparameters-displayonlypatch.
R3: finiteprovedsimultaneoussubs,gradientretention,bindremoval,copy,arithmetic
propagation; constreturntypes/setscompareactualSDK. Formalqhaszeroquantum
derivative; noextraFréchet/MPStangent/HVPquantumworkfromfake dependency.
R4: ONLYcontext-bearingPEstandardv13wireprojection; zero termsONLYwire,
standardopcodes/symbolUUID/vectors, acceptedactual2.4.1/2.6.0readers, correct
restoredparams/UUID/bind/math. Nocontextwriterbytesunchanged. Boundprojection
work/expansion/encodedbytes; noconstunconditionalzeroformaladdition. Repeated
Native->QPY->Public/Native->QPY->Public/Native stablemath/identity/nogrowing
zeroterms; notbytecanonicalityunlessactuallyguaranteed.
R5: readAST/formals/vector/index/partial-fullbind/copy-compose/Compiler/
SV-MPS/expectation/Jacobian/JVP-VJP/Hessian-HVP. NoCircuitindexrewrite or
upstreampatch; originaltwoannotationindexxfailseparateOPEN. R6: samename/
differentUUID,conflictingUUIDdescriptor,vectorresize/orphan,sub/gradchains,
contextlimits,projectiongrowth,nonfinitevalues,invalidmapping,parentchild
ledger,constructor/writerfault/no partialCircuit-or-QPYpublication, work/
reservationsnotrolledbackincorrectly. R7: original99/1 difference genuinely
closedwithmath/identity/tolerances, no skip/xfail/writer-onlymask. Thenreader
u/255/13/UUID/vector/QC1-QC4/TF7-TF8/protectiveframeworks/freeze/Main-Alt/
strictSDKfree/nineexamples actualJUnit/origins/manifests/exits. ProveNative
andQPYseparatelyifoneunverified. NoQPYrewrite/newformat/symbolicengine/TF-JAX
privateAD/SDKpatch/defaultOperator/UIchanges. AlloriginalfullR2gates andSDK
replacementACTIVEINCOMPLETE/localonly unchanged; noGit/install/vendor/auth/
TLS/cloud/hardware/financial13actions absentnewhumanpermission.

### QPY1-H4R3 Numerical Attribution And Human Environment Authorization

The complete QPY1-H4R2-FROZEN-VERIFICATION-UPDATE peer reply and its ending
were read from the existing authorized ChatGPT conversation. The peer agrees
only with OLD_KERNEL_CURRENT_ENV_REPRODUCED and alignment sensitivity. A
NumPy-version change as the cause is NOT_PROVEN: both old and new source were
tested in the same current environment. Strict SDK-free remains FAILED/OPEN.
Do not retry until green, change old exact assertions, or replace them with
allclose. A test-contract change would need a separate, precise request with
old-source and numerical evidence; none is approved here.

The bounded additional diagnostic fixes the same complex128 input and varies
C/F output layouts, offsets and strides. Record shape, strides, dtype,
alignment, differing component positions and ULPs, then compare both paths
with independently exact or high-precision multiplication. Distinguish
mathematical equivalence with rounding differences from bitwise identity.
Preserve the frozen source and collect true terminal results. No-context QPY
byte equality, constant-gradient return types and actual dual-version
interchange must be assessed separately. Full QPY1 and SDK replacement remain
NOT_ACCEPTED/INCOMPLETE; all original R2 final gates remain OPEN.

Subsequently the HUMAN explicitly answered the pending asynchronous question:
permission granted to rebuild the test environments OUTSIDE the repository.
This permits dependency restoration only, not repo dependency changes,
GitHub authorization changes, cloud/hardware calls or unrelated work. Stable
paths under /Users/avalok/.cache/quantumbridge/test-envs are used instead of
the cleaned /tmp environments. No peer message is treated as human authority.

### QPY1-H4R3-E Frozen Candidate Revalidation

Complete QPY1-H4R3-ENV-AUTH-AND-EXACT-DIAGNOSTIC reply and ending read.
FLOAT_ROUNDING_BITWISE_CONTRACT_CONFLICT is the bounded classification, not
permission to change old tests. The current candidate stays frozen at
32d0f44a72794f8034c84ec816167760e3059730cced2f21a8590c7a88b064ff.

E1: finish only the two authorized external environments. Verify actual
__file__, versions, imports, dependencies, QPY reader/writer origins and real
minimal numerical operations, not just pip list. Main Qiskit 2.4.1/PennyLane
0.44.1/JAX 0.7.1; Alternate 2.6.0/0.42.3/0.6.2; TensorFlow 2.21.0 in both,
with actual NumPy/SciPy origins. No certificate-store/credential edits,
trusted-host, disabled TLS or repo dependency changes.

E2: real dual-version u/subs fixtures; retained formal math and UUIDs;
gradient/bind/subs/simplify; standard wire-only projection; stable QPY
rewrites; no-context bytes; four native/public directions; Compiler,
Statevector/MPS and JVP/VJP/HVP. Record real origins, JUnit and process exits.
The nominal Alternate 319-pass receipt must never be counted as version 2.6.

E3: rerun the affected TensorFlow and four-framework protections, including
the original four 100-wire mixed AD cases, true-third refusal, cached M2 RoF,
default pfor, scalar lowering, Torch/Autograd/JAX, QC1-QC4, Operator.power and
QPY/IR/Compiler. Keep real failures; no added skip/xfail or derivative tolerance
relaxation. A source change would invalidate prior candidate evidence.

E4: strict SDK-free stays separate, with no new environment on its PYTHONPATH
and no override of its NumPy 1.26.4. Preserve the exact failure and old-source
reproduction. No kernel/test/tolerance changes or repeated attempts for a
passing result. A different numeric test contract needs separate precise
authorization supported by the independent mathematical evidence.

E5: report separately environment recovery, actual dual QPY results,
retained-formal math/standard interoperability, original two annotation-index
xfails, public 2.4.1 malformed partial-bind stream, constant-gradient type
gap, strict bitwise failure, new framework protection, selected hashes,
origins/JUnit/exits, default 56 and all open QPY1/R2 gates. No full replacement
claim. Priority is environment recovery, QPY proof, TF regression, while
preserving strict's independent failure. Do not rewrite Statevector for this
rounding difference. Local-only and all original final gates remain in force.

### QPY1-H4R3-E Isolation Review

Complete QPY1-H4R3-E2-RESULTS-AND-ENV-ISOLATION reply and ending read.
The precise classification is
ALTERNATE_EXTERNAL_BINARY_IMPORT_CONFLICT_REPRODUCED. The observations do not
prove PyArrow is the only cause or that all Qiskit 2.6.0 installations are
defective. No native QPY compatibility patch is warranted by these facts.

The peer corrects the earlier in-place rebuild proposal: use a NEW isolated
external directory/suffix, preserve old venv/crash matrix/exit codes/traces,
and prove isolation through sys.path, pyvenv.cfg, actual __file__ and imports.
Run independent SDK/framework imports, joint numerical calls, QPY dump/load
and fixed repeated sanity processes to verify clean shutdown BEFORE broad.
List and classify any pip-check conflicts; do not claim full health from
successful calculations alone. Normal dependency isolation is permitted by
the existing human authorization, not by additional peer-granted authority.

Finish the already-live Main broad, Main TF and old Alternate TF original
handles; no duplicate runs of those tasks. After new-runtime sanity, execute
real Alternate QPY, standard bilateral/formal projection, numerical/AD and
broad protections. Do not count old crashed broad as passing, new-runtime
success as repairing the old environment, or SDK recovery as closing strict.
No global uninstalls, residual .so package assembly, SDK/private allocator or
gradient-registry patches, credential/TLS changes, source/dependency/Git edits,
Studio/Router, financial-history or cloud/hardware actions. Full SDK parity,
QPY1 and all original R2 final gates remain OPEN/INCOMPLETE.

### QPY1-H4R3-E Latest Waiting Boundary

Complete QPY1-H4R3-E3-ISOLATED-RUNTIME-AND-MAIN-TERMINALS reply and ending
read. New Alternate isolation/sanity and genuine 332-case focused proof are
accepted as local environment progress, not a repair of the old environment.
No production change is requested. Keep the candidate frozen and await the
two original isolated Alternate broad/TF-MPS handles; do not start duplicates.
After terminal exits, inspect JUnit, same-process origins and manifest plus
the original four mixed AD cases and true-third refusal. Then submit the
same-source Main/Alternate terminal summary for bounded supported-subdomain
review. A real failure must retain its original exit and traceback before any
minimal repair decision.

The old projector comparison remains a formal strict gate failure. Exact
HUMAN authorization for that one test's numerical contract is still pending;
no old assertion/tolerance/kernel edits until it arrives. Retained-formal
projection, constant gradient type, two public annotation-index xfails and
public 2.4.1 malformed partial-bind streams are distinct proof obligations.
QPY1 PARTIAL/NOT_ACCEPTED; strict FAILED/OPEN; full independent replacement
ACTIVE/INCOMPLETE. Original FULL/GLOBAL >= 91.34108013033072%/68 exclusions/
28-section/controlled legal/five actual origins/Git three-state gates stay
OPEN. External environment authorization does not authorize Git, repo
dependencies, Studio/Router, financial history or hardware actions.

### Human Approval Of One Projector Test Contract

After all 32d0-candidate gates reached terminal, the HUMAN answered the pending
precise question: allow only the old projector test's comparison-contract
correction. Authorized scope: strict complex multiplication error bounds,
exact coordinate/memory-sharing/roundtrip assertions preserved, no production
calculation change and no other test tolerance change. This is new human
authority, not inferred from a peer message. The old strict FAIL remains
historical evidence and must not be relabeled as a passing old-source gate.

Only tests/information/test_operator_construction_origins.py changes for the
new candidate. The state factory checks exact rational input-float products
with the binary64 two-term dot-product gamma_2 bound. Density's direct alias
comparison stays bitwise exact. An independent native-matrix snapshot backs
exact public-coordinate, roundtrip and nonmutation comparisons. New selected
candidate and fresh gate receipts are required; do not silently reuse the
32d0 full-selected manifest as the new one.

### QPY1-H4R3-E5 Contract Review

Complete reply to QPY1-H4R3-E5 terminal update and new HUMAN authorization
read, including ending. Prior 32d0 double-environment terminals are recognized
only for that candidate; original strict failure remains its genuine result.
Human authority permits the single named projector test correction, not
production mathematics or other old tests/tolerances/skip/xfail changes.

Use actual complex128 input Fractions, per-element real/imaginary product
magnitudes and gamma_2, not an unconditional constant absolute tolerance.
Independently examine zero/near-zero cases. Preserve exact coordinate,
density-alias, memory ownership/copy and roundtrip contracts. Deliberate
perturbations, coordinate swaps and missing conjugation must still fail.
Retain original strict failure and old-source diagnosis, run focused related
Statevector/DensityMatrix mathematics/ownership, full affected SDK-free, then
freeze and rerun all fresh same-source Main/Alternate broad/TF-MPS/strict/nine
examples with actual origins/JUnit/exits. Only a real complete affected
strict exit 0 can close this one contract blocker; focused success alone
cannot. All default 56, public index defects, constant-gradient type and
original final R2/full replacement obligations stay OPEN. Local-only remains.

### QPY1-H4R3 Latest Six-Terminal Review And QPY1-I Prompt

Complete QPY1-H4R3-APPROVED-CONTRACT-LATEST-SIX-TERMINALS reply and ending
actually read in the existing default-Chrome conversation. Peer accepts only
QPY1_READER_AND_RETAINED_FORMAL_SUPPORTED_SUBSET_READY_FOR_REVIEW as local
development evidence for candidate 05b3, not an independent remote/code/legal
audit or full QPY/SDK acceptance. The authorized projector contract blocker
is closed for the demonstrated affected strict set. Original four optional
SDK skips are not native passes. Old failed receipts remain valid history.

The next executable prompt is preserved below with duplicate UI labels and
duplicated table renderings omitted; instructions and boundaries retained.

#### Stage 12-B QPY1-I: Constant Gradient Return ABI And Native Symbolic Compatibility

继续 QuantumBridge 原 R2/P4/QPY1 任务，不开启第二套符号引擎或新的 SDK 阶段。
唯一主要目标：修复 ParameterExpression.gradient() 在数学导数已经是常数时的
公开返回类型差异，同时保持 Native Core、retained-formal、QPY v13 和 AD 内核正确。
FULL_INDEPENDENT_NATIVE_QISKIT_PENNYLANE_REPLACEMENT = ACTIVE / INCOMPLETE。

I1. 建立真正的双版本返回类型红灯。
使用真实 Qiskit 2.4.1 / 2.6.0，对同一输入记录：p+q 对 p 的常数 1 类型；
p*q 对 p 的符号结果及 q/p 形式参数；p*0 对 p 的零与参数集合；sin(p) 对无关
q 的零；p**2 对 p 的非常数；sin(r)+q**2 对 r 的 cos(r) 与 retained-formal；
p-p 对 p 的常数化；二次连续求导对不同参数的数值/符号转换边界。
每个 case 检查 Python 类型、UUID、形式参数集合、数值以及 bind/subs/simplify
的合法性。原有四个常数梯度控制 case 必须作为正式红灯保留。

I2. 审计现有 Native 调用者。
先调查 gradient() 返回对象被哪些真实 Native 生产模块消费，特别是 QPY v13
op13 replay、symbolic calculus、Frechet/HVP、Compiler parameter binding、
FrozenParameterBinding、QNode symbolic expressions、IR、ParameterVector、
Gate/AnnotatedOperation。不能把内部需要 AST 的路径直接改为 Python float。
先以实际源码确认能否最小区分现有核心计算函数和公开返回边界；这只是架构
选项，不能据此建立第二套微分系统。

I3. 最小生产修复。
真正常数且没有必须保留的符号上下文时，公开 gradient() 返回两版本实测的
Python 数值类型。具有真实 retained-formal 的表达式不能仅因数值常数就丢弃
形式参数。内部若需要 PE，通过现有受验证 AST/constant-construction 机制消费
结果，不在改变公开返回值后猜测参数身份。防止 0*q 身份被丢弃、retained context
丢失、float/complex/int 混淆、无关参数导数类型错误、AD 零 tangent 被错误计费为
非零导数、writer 为常数额外生成不必要记录。无真正双版本证据，不得将所有
数学常数导数一律返回 float。

I4. QPY v13 双向数学保护。
已有 op13、u/subs()、255 replay 必须经过 QPY -> Native PE/numeric result ->
Circuit binding -> Compiler -> Statevector/MPS -> JVP/VJP/HVP。Reader 能处理
replay operation 产生常数数值，并遵守合法记录的符号上下文。不修改 v13 格式、
不加私有 sidecar、不通过异常历史记录伪造参数身份。

I5. 资源与失败原子性。
复用 SymbolicExpressionLimits、reader limits、GateCircuitLimits 和共享资源。
测试大表达式最终常数化、gradient 资源不足、retained context 过大、同 UUID
冲突、非有限系数、nested substitution、多次 gradient、失败后合法恢复、
parent/child ledger。资源拒绝先于危险展开；最终常数不能绕过已发生的工作量。

I6. 真正的开发期验收。
A 原四个常数梯度 ABI 红灯与更多 oracle；B 内部 Core/public 边界审计；
C 最小生产修复；D retained-formal/QPY1-H/Compiler/Statevector-MPS/AD 专项；
E QC1-QC4、Operator.power、M1-M3 关键回归；F Main/Alternate 最新 broad、
TF-MPS、严格 SDK-free 和九个数值示例；G 原两条 public annotation-index 及
默认 Operator 56 条差分保留真实未完成状态。每组记录 JUnit、同进程 origins、
candidate SHA、selected before/after 和真实退出码。

本批最多提出 QPY1_CONSTANT_GRADIENT_PUBLIC_ABI_SUPPORTED_SUBSET_READY_FOR_REVIEW。
必须证明公开常数类型和两实际版本一致、Core 数学/身份不回归、retained-formal
不被错误常数化、QPY 保存恢复正确、JVP/VJP/HVP 正确、两环境及严格 SDK-free
最新候选回归通过。无法安全关闭的类型差异保留真实红灯，列出必要内部 API
兼容调整，禁止测试层 coercion 假阳性。

本批不处理默认 Operator arithmetic、不修补 public2.4.1 异常字节流、不修改
上游 SDK、不扩大 TF-MPS/Studio。所有原 R2 最终门禁继续 OPEN：SDK-free FULL、
Main FULL、Alternate FULL、独立四框架 FULL、GLOBAL >= 91.34108013033072%、
exclusions 68 不增加、原始 28-section matrix、ALL numerical examples、controlled
legal、五实际 import origins、frozen/worktree/staged/commit equality。
严格 local-only：不 stage/commit/push/fetch、不改认证/TLS、不安装仓库依赖、
不 vendor、不调用云或真实硬件、不改金融历史证据及 Studio/Router。
下一步集中修复公开常数 gradient 类型，不重复已通过的 QPY 数学工作。
完整独立原生 SDK replacement 始终 ACTIVE / INCOMPLETE。

### QPY1-I3-F Received Scope Ruling (2026-10-26)

Complete reply to "QPY1-I3 first production fix, before old-test adjustments."
read in the existing default Chrome conversation. Duplicate UI headings/table
renderings omitted here; executable requirements and boundaries retained.

批准将 FrozenParameterBinding 的 retained-formal 传递缺陷纳入当前 QPY1-I3
修复范围，不开启新阶段。Core 正确保留 {q,r}，冻结绑定丢弃 q，属于现有参数
系统真实集成缺口。当前 25 个 Native scalar ABI 失败已修复；Alternate 60 pass，
Main 59 pass/1 fail 不能改称 60/0。QPY1 整体验收 NOT_ACCEPTED。

Qiskit 2.4.1 三角恒等式错误原始公开对照仍执行，保留 FAIL 及独立解析证明。
可将 Native 数学正确性和上游版本差异分组，不能改原比较、加 skip/xfail 或复制
错误数学。2.6.0 正确结果可单列正向证据。

F1 保留冻结绑定真实红灯。独立测试 cos(r) 仅 r、cos(r) retained {q,r}、同名
不同 UUID、ParameterVector 非连续 index、部分绑定 r 后 retained q、完整绑定
数值、重复 occurrence、输入缺失/冗余/重复。

F2 复用现有冻结参数映射/owned 参数身份。读取经过验证的 retained context，
纳入所有权及输入匹配，数学 AST 不变。retained-only 参数零数学依赖，保留 UUID/
vector root/index/size，计入 AST/workspace 和参数预算。访问不可信对象前 owner
admission。不得加 0*q。TF q 的 JVP/VJP/HVP 数学零，来自真实图和已验证 AD，
不得注入私有梯度。审计现有合法 unconnected ZERO 规则，不能任意把 None 当零。

F3 验证 retained 身份预算不虚增非零量子导数工作，work/memory/tapes admission、
max_diff 1/2、max_hessian_elements=1 streamed HVP、parent/child ledger、forged
owner、失败原子性、source mutation、重复调用/缓存身份。防止同 UUID 被 AST 与
retained context 双重计入。

F4 先保存旧 PE-extension 实际失败，仅精确修改 gradient 永远返回 PE 的断言及
辅助调用。数学点/容差、raw int/float/complex、内部 AST 二阶、formal、UUID、
资源、失败恢复保留。不得测试侧统一 PE(result) 掩盖 ABI。

F5 scalar ABI 正向数学；2.4.1 三角错误独立诊断；op13/u/subs/255 replay；QPY
formal wire projection；Native IR；FrozenBinding；MatrixJet；SV/MPS；四框架
受影响 AD；原四条 100-wire mixed AD 与 true-third refusal。

F6 F1-F4 红绿后冻结候选，最新 Main/Isolated Alternate/strict SDK-free/TF-MPS/
九数值例。真实 origins、source before/after、JUnit、退出码。冻结绑定不正确不能
因 Core ABI 已绿宣称完成。

边界仅上述已证明缺陷和 ABI 冲突旧测试。不得改 Circuit owner/index、QPY13
格式、上游 SDK、私有 JVP/Hessian、默认 Operator arithmetic。QPY1-I3 PARTIAL/
NOT_ACCEPTED，full independent replacement ACTIVE/INCOMPLETE。默认 56 parity、
两 annotation-index xfail、2.4 malformed QPY、原 R2 全部门禁 OPEN。strict local-only。

#### QPY1-I3-F Projection Review

Complete checkpoint reply read in default Chrome: no demonstrated production
defect requiring reversal; proceed four-framework terminal then affected Core/
QPY/Compiler, freeze and fresh broad/TF-MPS/strict/nine examples. Projection
must keep the original frozen parameter UUID/vector root/index/size, AST/formal/
derivative order, input admission and full-plan node budget. Source owner/vector
resize/configuration tightening invalidation must remain. Verify q-independent
value, zero Jacobian/JVP/VJP/mixed HVP, correct r curvature and external nonlinear
loss chain rule. All-constant/empty selected-angle, zero tangent, repeated calls,
max_diff 1/2 and streamed HVP cannot bypass owner/method/resource checks. Only
verified unconnected-gradient normalization is allowed. Upstream 2.4 trig real
red, original default56/index/malformed/R2 gates and local-only remain unchanged.

#### QPY1-I3-F2 Read-only Occurrence Provenance Verification

Complete owner/source-attestation rulings read in the existing default Chrome
conversation after reporting the actually accepted forged constant2/node_count0
and the valid-but-wrong p*2 AST. Old four b5f1 runner terminal exits must remain
INTERRUPTED/INCOMPLETE; historical completed evidence cannot transfer to a new
candidate. Full FrozenParameterBinding.create plus exact native owner guard is
approved, but structural validity alone cannot prove source correspondence.

Reuse the existing lower_scalar_graph bounded construction scan in a strictly
read-only occurrence mode. Emit no AST, execute/import no GraphDef, create no
compiler/UUID, change no ordinary lowering whitelist and use no private TF hook.
Canonicalization is limited to admitted side-effect-free Identity, exact static
shape/index layouts, the same floating dtype/literal IEEE-754 bits, original
input positions and ordered native operations. No commutative reordering,
algebraic simplification, constant folding or numeric sample equivalence proof.

F2-1 Keep both actual red counterexamples. Wrong-source p*2 must typed-refuse
before quantum tensor graph construction or host/device execution, without a
wrong finite expectation, source/Circuit/UUID mutation or live reservations.
F2-2/3 Scan only current admitted scalar snapshot/compiled plan/input map. Compare
bounded ordered signatures including root UUID order, output occurrence index,
formal identities, actual AST dependencies, dtype/shape, derivative order and
current limits. A SHA field alone is not source attestation.
F2-4 Reuse existing AST access and finite layout analysis, not a second evaluator,
symbolic algebra, AD engine or graph executor. Unsupported source proofs must
explicitly refuse; no unproved managed projection fallback, and resource errors
must not become capability misses.

F2-5 Positive: p, p+q, q*q+.4, sin(p), native RY(-p) RZ(q*q+.4) RX(p), reversed
input, vectors, partial binding, retained-only q, all-constant, repeated occurrence.
Negative: p->2p, p->q, p+q->q+p under ordered contract, +0/-0 literal bits,
missing/extra outputs, forged AST/count/UUID, source or GraphDef mutation, foreign
properties, unproved functions/dynamic shapes/capture.
F2-6 Reuse FrozenBinding, ExecutionPlan.lowered, DerivativeExecutionRequest,
GateCircuitLimits, UnifiedResourceLedger and ResourceScope. Complete proof before
dangerous quantum tensor operations; charge static proof work/memory; publish no
partial executable binding on failure. Preserve full original resource envelope,
owner invalidation and the distinction between trace-time and runtime guards.
F2-7 After red->green run frozen formal, scalar lowering, managed whole QNode,
default pfor, cached RoF, MPS100/third refusal, MatrixJet, QPY13 op13/u/255, IR,
Core calculus, QC1-QC4 and both actual environments/strict affected regressions.
Unsupported legitimate proof coverage remains explicit work, not relaxed checks.

Status before source proof: BLOCKED_BY_SOURCE_ATTESTATION/NOT_ACCEPTED (not a goal
tool blocked status). Full replacement ACTIVE/INCOMPLETE; original 56/default,
annotation-index, malformed-public-QPY and all original R2 final gates OPEN.
Strict local-only remains: no Git mutation/dependency installation/cloud/hardware/
Studio/Router, and no phase or objective reduction.

#### Frozen a381d80b Review

Complete peer response to "QPY1-I3-F2 read-only occurrence proof implemented,
fresh frozen gates running (not accepted yet)." read in default Chrome. No
demonstrated deterministic defect requiring reversal from the reported receipts.
Keep a381d80b/1612files frozen; do not restart expensive tests or add features.
Final checks: repeated occurrences and identical expressions at different gates/
noncontiguous wires stay anchored to trusted plan occurrence positions, not only
matching structural hashes. Retained-only/empty-output paths keep full owner,
method/resource admission. Proof/UUID/GraphDef refusal precedes tensor-plan
construction and never degrades identity/resource/domain errors into fallback.
Wait real terminals, audit origins/JUnit/before-after-current, originalIDs/xfails,
four100wire mixed AD/third refusal, all retained/QPY/Core/MatrixJet coverage and
all explicit old red probes. No new proof engine/normal-lowering expansion.
TARGETED_GREEN/FROZEN_VALIDATION_RUNNING only; fullSDK/QPY/R2 still incomplete.

#### Partial-Capture Regression Ruling

Complete a381d80b terminal-review reply read in default Chrome. That candidate
really has two old mixed-native cached-RoF failures per environment despite broad
8218PASS/4oldXFAIL. Do not rename failures or transfer its passing receipts.
Bounded approved repair: complete native capture retains readonly occurrence
proof. A readmitted exact strict PREFIX of recorder occurrences is not a complete
binding; lower the entire actual scalar pack through the existing bounded normal
lowerer instead. Nonprefix/wrong order/forged/conflicting ownership typed-refuses.
Prefix capability misses must SOURCE_PROOF_UNAVAILABLE, never unverified old
projection/callback fallback; resource/safety/identity/domain errors propagate.
Check complete lowered outputs again against the final lowered plan occurrence
order, including appended RX UUID/operation index and repeated/noncontiguous
targets. Original two losses/AD nesting/tolerances remain unchanged. Retained/
partial/empty-output, multioutput/Jacobian/HVP/third refusal and all source stores/
ownership must remain correct. Test dispatch, fake admissions, unsafe source and
full plan mapping, then new freeze and fresh both broad/TF-MPS/strict/nine examples.
No new phase, engine, normal whitelist, Git/dependency/cloud/UI changes.
NOT_ACCEPTED until the actual compatibility regression is closed; wholeSDK/R2
and default56/publicindex/malformedQPY obligations remain OPEN.

#### Frozen 51a96b21 Review

Complete final-prefix-repair checkpoint reply read in default Chrome. Direction
fits approved contract; no demonstrated deterministic reversal defect from the
reported55pass receipts. Keep51a96b21/1612files frozen until actual terminals.
Verify ordered operation indices/occurrences/wires/final slots, not set equality;
prefix capability miss typed-refuses, while resource/identity/nonfinite/domain
errors propagate, and no full-plan work/workspace/order envelope shrinks. Audit
all origins/manifests/JUnit/exits, original four100wire mixed/third refusal, both
old mixed-native losses and all forged-binding counterexamples. No new features,
source edits during expensive runs, or early bounded acceptance. FullSDK/R2 and
all old red probes remain OPEN; strict local-only unchanged.

### QPY1-I3-F2 Final Review And Next QASM1 Prompt

Complete LATEST_SIX_TERMINALS_AND_AUDIT reply and ending actually read in the
existing default Chrome conversation. Peer accepts only
QPY1_CONSTANT_GRADIENT_PUBLIC_ABI_SUPPORTED_SUBSET_READY_FOR_REVIEW from the
51a96b21 local receipts. QPY full/default API parity/full replacement remain
INCOMPLETE; full replacement ACTIVE. Peer explicitly did not independently
inspect uncommitted source/worktree/remoteCI/legal. Main raw29/1trig red, public
annotation-index, public2.4malformedQPY, default56 and all R2 gates remain OPEN.

Next executable prompt, duplicate UI labels/table renderings omitted:

#### Stage12-B QASM1: QASM2 Custom Gate Definition, Name Collision And Native Roundtrip Parity

Continue original R2/P4 full independent SDK replacement. Only investigate the
existing formal QASM2 custom-definition/standard-name xfail first. Do not assume
native writer is responsible; do not redo passed QPY/QC/TF work or switch default
Operator arithmetic.

A Original red and format evidence: locate complete original xfail nodeID/input/
assertion/history in latest8218 broad. MainQiskit2.4.1/isolatedAlt2.6.0 run public
to public, native to native, public to native, native to public QASM2. Distinguish
wrong standard-name reuse, body loss, declaration-invocation association, parameter
mapping, bit/qarg ordering and semantics QASM2 cannot express.

B Independent math oracle: actual conflicting name, custom h/x, one/multiple
qubits, parametric/nonparametric, nested definitions, copy/inverse, noncontiguous
qargs, custom/standard mixed, different action order, expressible nontrivial
global phase. Compare full complex Operator and Statevector amplitudes, not text/
probabilities only. Preserve accurate Unsupported for inexpressible QASM2; no
private syntax.

C Minimal production repair: reuse sole Circuit operation store, Gate.definition,
existing compiler/lowering/QASM2 reader-writer/ParameterExpressionUUID/GateLimits.
Identity must follow validated definition/scope, not only name. Do not globally
rename all standard gates, create another registry or copy upstream parser.
Verify published declaration rules and both actual SDK versions before choosing
standard representation or precise refusal.

D Boundaries: self/cyclic definitions, duplicate declarations, same name/different
bodies, undefined gate, parameter count mismatch, illegal qargs, excessive depth/
expansion, malformed text, foreign owner, illegal parameter expressions and parse
failure. Reuse depth/work/memory/resource limits before dangerous expansion; no
partial published Circuit or polluted UUID/definition/operation store after failure.

E Execute each legal case through native/publicCircuit -> QASM2export/import ->
nativeCompiler -> SV/MPS -> Operator -> QPY13/JSONIR -> restoredCircuit -> execute.
Both actual SDKs bilateral differential; prove gate math/binding/qargs, not merely
successful parsing. Protect QPY parameter/formal/annotation, publicUnitary wire
parity and default parameter-shift.

F Preserve original real red first, implement actual production red->green, then
QASM affected parser/writer, Core/Circuit/Gate, Compiler, serialization/QPY/IR,
QC1-QC4, QPY1 formal/constantgradient, Operator.power, M2 cachedRoF/defaultpfor/
scalar lowering, originalTF7/8 four100wire mixed/third-refusal, fresh both broad,
strict SDKfree and nine examples. Original mathematical assertions unchanged.
Only review original xfail removal under existing governance after real original
test executes and is mathematically fixed; no relabel-only pass. Do not copy an
actual upstream mathematical bug into native behavior.

G At most QASM1_CUSTOM_GATE_DEFINITION_PARITY_SUPPORTED_SUBSET_READY_FOR_REVIEW
after proven cause/fix/current affected regression. Enumerate repaired public
semantics, standard limitations, remaining upstream differences, actual gate-name/
definition/UUID/wire outcomes, genuinely closed xfails and unimplemented APIs.
One repaired xfail is not fullQASM/QPY/SDK completion.

Original independent native fullfunctional parity/replacement objective stays
ACTIVE/INCOMPLETE. Original SDKfree/Main/AltFULL, independent4frameworkFULL,
GLOBAL>=91.34108013033072%,68exclusionsnoincrease, original28sectionmatrix,
ALLexamples, controlledlegal, fiveactualorigins, completefrozen/worktree/staged/
committed equality remain OPEN. Strict local-only: no stage/commit/push/fetch,
OAuth/TLS/repo dependency/vendor/cloud/hardware/finance13history/StudioRouter/
tag/release changes. Next priority is the already-proven QASM2 definition/name
collision gap, not repetition of already passed TensorFlow/QPY examples.

### QASM1-A Evidence Review And QASM1-B Scope

Complete reply to `QASM1-A actual evidence on unchanged51a9, not native-writer
presumption.` read in the existing default Chrome conversation. Peer confirms
the upstream/native root-cause separation. Original public writer xfail remains
UPSTREAM_PUBLIC_QASM_WRITER_DEFINITION_LOSS / OPEN, with original call, X/H
definitions, expectations, tolerance and --runxfail unchanged.

QASM1-B is authorized local implementation, not accepted completion. Validate
source-order visible declarations, literal declaration before primitive aliases,
include-at-point conflicts/duplicates, previous-only gate references, formal-only
parameter/wire scope, arity and unused bodies before publication. Reuse current
parser/lowerer, existing limits and typed errors; no second gate registry or
parser rewrite. Separate U/CX/measure/reset/barrier grammar. Record actual
Qiskit2.4.1 and isolated2.6.0 behavior for each input. Public acceptance of unused
`rx a` is PUBLIC_QASM2_SIGNATURE_ACCEPTANCE_DIFFERENCE, not evidence of valid
signature or native parity; no silent default parameter is authorized.

Legal math must cover full complex Operator, SV/MPS, binding, qarg order, nested
definitions, compiler, QASM2 roundtrip, JSON IR/QPY13 restoration. Invalid input
must refuse before dangerous work with no partial publication, polluted prior
declarations or leaked reservation, and legal parsing must recover. After real
red->green run QASM-specific then latest Core/Circuit/Compiler/Serialization/QC1-4/
QPY1/M1-M2 cachedRoF/defaultpfor/scalar/TF7-TF8 original100wire/third-refusal,
Main+isolatedAlternate broad, strict SDK-free and nine numerical examples. Save
JUnit, terminal exits, actual same-process origins and before/after manifests.
Original writer xfail/default56/annotation-index stay separately OPEN. Full SDK
replacement ACTIVE/INCOMPLETE and original R2 gates OPEN. Strict local-only
unchanged: no git mutation/auth/TLS/install/vendor/cloud/hardware/finance13history/
Studio/Router/tag/release.

#### QASM1-B Frozen Validation Review

Complete reply to `QASM1-B native admission repair, preliminary local receipts
before freeze.` actually read in the existing default Chrome conversation. Peer
finds no deterministic reversal defect in preliminary receipts, approves frozen
validation only, not QASM1 acceptance. Recheck source visibility/U-CX/include
separation, unused-body validation, memoized shared-DAG reference multiplicity,
pre-publication refusal/no partial executable definition or leaked reservation.
Both unused builtin and custom missing-parameter acceptance differences stay
PUBLIC_QASM2_SIGNATURE_ACCEPTANCE_DIFFERENCE / OPEN. All original writer losses
and initial harness failures stay separately recorded. Freeze1614 and obtain
actual Main+isolatedAlternate broad,411TF each, affected, strict, nine examples,
original public writer red and signature differences. Do not edit selected
production/tests during runs or duplicate expensive runs. After all required
terminals and audit, at most propose
QASM1_NATIVE_DECLARATION_SCOPE_SUPPORTED_SUBSET_READY_FOR_REVIEW, not wholeQASM1.
Full replacement ACTIVE/INCOMPLETE and R2 gates OPEN; strict local-only unchanged.

### QASM1-B Final Bounded Acceptance And QPY2 Prompt

Complete reply to QASM1-B ALL_ACTUAL_TERMINALS_AND_FROZEN_AUDIT actually read in
existing default Chrome. Exact complete extracted body saved as structured
tmp/r2o3b-qasm1-final-peer-reply.json (complete=true), including all QPY2 clauses.
Peer accepts only QASM1_NATIVE_DECLARATION_SCOPE_SUPPORTED_SUBSET_READY_FOR_REVIEW
from reported3aa2f50b/1614 local receipts, not independent source/legal/remoteCI
audit, fullQASM2 or SDK replacement. All writer/signature/default56/publicindex/
oldtrig and original final R2 gates remain OPEN.

Next exact task: Stage12-B QPY2, Standard UnitaryGate Inverse, Derived Owner And
QPY v13 Roundtrip Closure. First independently verify old QC1-W1 inverse_of /
unitary_dg refusal, do not assume it still occurs for every raw UnitaryGate or
assume writer must change. Audit UnitaryGate/Gate inverse,power,repeat,annotated,
standard_from_record, reader/writer, QC1 provenance and raw standard matrix record.

A Real red: asymmetric complex128 one/two-wire U, nonzero input/globalphase,
unmodified qargs including2wire[1,0]. Native->Native/public2.4/public2.6 and public->
Native/public. Full inverse matrix, source name/label/metadata, actual restored
type/customdefinition, refusal location, physical/local basis. Preserve actual
original refusal; existing Unsupported is not automatically expectedPASS.

B Independent NumPy fullcomplex math versus encoding proofs: rawNative/public/
Circuitderived/restoredIR-QPY detached, inverse-before-QPY/QPY-before-inverse,
copy/inverse/inverse,repeat/inverse,integerpower/inverse,controlled,annotated,
noncontiguousqargs/globalphase. Mathematical success+writerrefusal is incomplete;
encoding success+wrongbasis is failure.

C Minimal validated serialization-boundary normalization only if actual v13
and SDK observations prove derived native representation safely admits standard
UnitaryGate matrix record. No caller mutation/inverse math change/new definition
system/privateQPYtype/sidecar/name-onlyguessing. Reuse validated owner/provenance
and pre-allocation work/memory admission. Standard-unrepresentable stays typed
Unsupported; do not dense-expand everyderivedGate.

D Exactly-once conversion: rawNative->inverse->standardQPY->detachedowner->public
append->compiler->SV/MPS; public->inverse->standardQPY->restored->nativeexecution.
Protect nativeq0high/publiclocalq0low,privateprovenance,detachednativecoordinates,
ownedcopy,label/ctrlstate,ParameterUUID,soleoperationstore,no double reversal.

E Controlled/annotated boundaries: closed/open/multicontrol,inverse/control order,
integer/fractionalpower,modifierorder,annotated/nonannotated,numericexponent.
Symbolicexponent,unknownGenericdefinition,illegalmodifier/unknownowner retain
existing typed refusal. Only demonstrated safe local matrix subset normalization.

F Resources/ownership/atomicity: existingGateCircuitLimits,QPYsize,owneradmission,
UnifiedResourceLedger/ResourceScope. Nonunitary,forgedinverse_of,foreignsubclass,
sideeffectmatrixproperty,recursivedefinition,oversizelocalmatrix,invalidctrlstate,
wrongdims,exactbudget/onebelow,concurrentreadonlydump,midconstructionexception,
legaldumpafterfailure. No source mutation/partial validQPY/reservationleak.

G After actual red->green, affected NativeunitaryQPY,QPY1 255/op13/u/formal,
annotatedQPY,QC1unitary,QC2/3Operator,QC4GateCliffordChannel,QASM1scope,CompilerIR,
Operatorpower,M2cachedRoF/defaultpfor,originalfour100wiremixed/thirdrefusal; then
freeze and fresh Main+isolatedAlternate broad,TF/MPSboth,strictSDKfree,nine actual
examples. Actualsameprocessmanifests/origins/JUnit/exits; all old reds separate.

At most QPY2_DERIVED_UNITARY_STANDARD_RECORD_SUPPORTED_SUBSET_READY_FOR_REVIEW
after demonstrated standardinterop/math/basis/owner/resources regression. List
actual encodableversusUnsupported,SDKdifferences,extrasnapshotallocations,ABI
impact,actualrepairedredsversusupstreamdefects. Not fullQPY/SDK complete.
FullreplacementACTIVE/INCOMPLETE. All original R2 FULL/GLOBAL>=91.34108013033072%/
68exclusions/28section/ALLexamples/legal/5origins/frozen-worktree-staged-commit
gates OPEN. Strictlocalonly,no git/auth/TLS/install/vendor/cloud/hardware/finance
history/StudioRouter/tag/release changes. Read exact archived reply before any
later QPY2 implementation if this semantic copy is insufficient.

#### QPY2-A Root-Cause Review And Focused B/C Execution

Complete reply to QPY2-A_INITIAL_ROOT_CAUSE_SPLIT actually read in default Chrome;
exact meaningful full body archived tmp/r2o3b-qpy2-initial-peer-reply.json. Initial
transient empty assistant label is not the executable prompt. Peer confirms
classification corrected by actual current evidence, not independent repository
audit. Continue originalQPY2. Raw UnitaryGate.inverse and retained-owner inverse
already encode; do not rewrite. Focus TWO independent native issues: baseCircuit
primitive unitary_dg standardQPY encoding and QuantumCircuit-derivedrepeat(2)
apparent cycle. Public repeat/inverse construction error remains separate.

First establish two formal real reds with independent asymmetric complex NumPy
U-adjoint/U-squared math and standardbinary records. For repeat prove actual
acyclic owner/definition dependency DAG, record owner identities, activepath and
work; only independently proven false-cycle may be corrected, never weaken real
cycle refusal. For primitive inverse, validated serialization construction
boundary normalization may be considered ONLY trusted exact native inverse
matrix/provenance and actuallegalv13 record, not name/inverse_of strings alone.
No general *_dg/denseGate fallback, sidecar, sourceGate/label/metadata/operation
mutation, doublebasispermutation or RawUnitary rewrite.

Prove one/two-wire inverse/doubleinverse/repeatinverse,noncontiguousqargs/phase,
native-native/native-public/public-native,restored-detachedownerpublicreuse,
sharedacyclicDAG versus truecycle,invalidowner/forgedinverse_of/badmatrix,
exact/onebelowlimits,atomicfailure,parent-childledger. Repetition means two
successive U applications with correct inverse order. Then originalQPY2 D-G
and all stated latestfrozen bothbroad/TF/MPS/strict/nineexample regressions.
QPY2 ACTIVE/NOT_ACCEPTED until two actualred->green proofs and final regressions;
fullreplacementACTIVE/INCOMPLETE, all originalR2gatesOPEN, strictlocalonly.

#### QPY2-B Design Review And Required Implementation Order

Complete reply to `QPY2-B implementation design question before primitive
normalization.` read in existing default Chrome. Exact full body saved as
tmp/r2o3b-qpy2-design-peer-reply.json. Peer approves bounded strong-reference
identity validation first, then limited exact Native UnitaryGate witness, not
general writer fallback or whole-QPY acceptance. Keep actual ancestor objects
alive for the complete pending-definition interval, is-only comparisons, one
snapshot read, active-path versus shared-DAG distinction and per-reference work
limits. Prove source DAG acyclic before repairing false-cycle; true cycles stay
refused.

Witness may qualify current operation for canonical record, not cryptographic
historical authenticity. Only actual validated native unitary inverse constructor
creates exact owned Native UnitaryGate witness; check operation identity binding,
matrix/width/nativebasis/type/owner agreement and preallocation work/memory.
Read-only consumer, no source mutation. Copy only via trusted owner-copy with
revalidation; remap without changed local basis may preserve eligibility; IR
canonicalizes existing standard matrix representation or Unsupported, never
reconstructs witness from loose inverse_of string/privateIR field/sidecar.
Real inverse A and ordinary forged B with identicalmatrix/width/inverse_of must
diverge: A encodes, B refuses. Arbitrary rewriting of all private Python fields
is outside structural guarantee, not cryptographic unforgeability; no signatures,
global registry or trusted execution mechanism authorized.

Order: formal independent NumPy red/QPY13 evidence; lifetime repair plustruecycle/
sharedDAG/resource stress; bounded constructor witness; canonical standardQPY13
with revalidation; copy/remap/IR/mutation/forgery/concurrency/exact-onebelowtests;
actual public bilateral/compiler/SV/MPS/controlphase/repeat math; only then freeze
and latest Main+isolatedAlternatebroad/TF/strict/nineexamples. QPY2NOT_ACCEPTED,
fullgoalACTIVE/INCOMPLETE, allR2gatesOPEN, strictlocalonly unchanged.

#### QPY2-B/C Targeted Review: Readonly Copy Required

Complete response to QPY2-B/C TARGETED_REAL_RED_GREEN_REVIEW read from the
existing default Chrome conversation, not the API's opaque content reference.
Peer confirms three actual repairs but does not accept whole QPY2. Mandatory
local invariant: every trusted inverse witness creation/copy keeps its owned
matrix flags.writeable=False; consumer digest checks are additional protection,
not a replacement. Do not make all Gate/ndarray storage globally readonly.

Audit actual original inverse, Operation/Gate copy, Circuit copy/compose,
parameter binding/wire remap and QPY/IR temporary owned copies. A path that
canonicalizes to ordinary standard UnitaryGate and carries no private witness
keeps the existing ordinary owned-buffer contract. Never borrow an external
mutable array to avoid budget accounting. Check normal writes refuse, source
matrix/digest remain unchanged, copied owner/identity/readonly match, external
matrix isolation, forged digest/metadata refusal, exact/onebelow preallocation
budget and full complex matrix/phase after copy/compose/remap.

Execution order: minimal readonly repair with actual targeted red->green;
rerun original ten Native failures, eight controlled-inverse failures and all
latest mathematical/interoperability/resource/cycle/atomicity tests; freeze
fresh source; Main/isolatedAlternate broad, both411 TF/MPS, strict SDK-free and
nine numerical examples, with actual origins/JUnit/manifests/terminal exits.
Public UnitaryGate.repeat().inverse() construction differences stay OPEN.
Full QPY2 NOT_ACCEPTED; full independent replacement ACTIVE/INCOMPLETE; all
original R2 FULL/GLOBAL>=91.34108013033072%/68exclusions/28section/legal/5origins/
Git-three-state gates OPEN. Strict local-only remains: no stage/commit/push/
fetch/auth/TLS/dependency/vendor/cloud/hardware/financehistory/StudioRouter.

#### QPY2-C2 Qualified Inverse Contract And Frozen Regression

Complete peer reply to QPY2 READONLY_COPY_FIXED / OLD_REFUSAL_CONTRACT_CONFLICT
read in the existing default Chrome conversation. It approves updating only
test_native_inverse_matrix_metadata_keeps_precise_qpy_refusal_without_sidecar
in tests/circuit/test_unitary_provenance_boundaries.py: preserve its test ID,
original diagonal input and precise unqualified unitary_dg refusal. Split
trusted real inverse (readonly witness, independent adjoint, standardQPY13,
no private sidecar, native/actualpublic fullcomplexmatrix/phase/execution and
copy/inverse/publicappend exactlyonce) from plain Operation with identical
public matrix/targets/inverse_of/metadata and no qualification (precise refusal,
source/store unchanged, no foreign callback/partial stream or reservation leak).
No production writer/Gate math/resource-setting/other old-test changes.

Preserve71e951fc/1619 actual8529PASS/1FAIL/4originalXFAIL receipt and archive;
it is not accepted. Run updated contract and all originalQPY2 targeted maths/
owner/readonly/IR/remap/binding/resource/cycle/atomicity; preserve any new red,
repair minimally only if genuine. Freshfreeze then BOTHbroad, BOTH TF/MPS,
strictSDKfree,nineactualnumericalexamples,originalupstreamdifferenceprobes with
latest sameprocessorigins/manifests/JUnit/actualterminalexit. Prior220/836
receipts are old-source evidence, not transferred. At most propose
QPY2_DERIVED_UNITARY_STANDARD_RECORD_SUPPORTED_SUBSET_READY_FOR_REVIEW afterward.

After QPY2 final terminals, next prioritize function-level gap accounting from
the original unmodified28-section matrix: actual implemented/executed APIs,
partial parameter/device/serialization contracts, Unsupported/knownerrors/
upstreamdifferences, function/branch/behavior evidence, remaining wholecore
functions, dependencies/order and uncertain effort intervals. Do not infer
completion percent or completion date from test counts. Existing broad
Operator56parity and all originalR2FULL/GLOBAL>=91.34108013033072%/68exclusions/
28section/legal/5origins/Git3state remain OPEN; fullreplacementACTIVE/INCOMPLETE.
Strictlocalonly unchanged, no cloud/hardware/Studio/financehistory/auth/git.

#### QPY2-C2 Bounded Acceptance And Complete R2-GAP1 Execution Requirements

Complete final QPY2-C2 review read in existing default Chrome. Initial partial
stream/interrupted connection was not treated as the complete prompt. After
API confirmed completed, existing-tab reload and a native upward scroll exposed
review items0-12; the prior read already covered items13-113, including G1-G10
and all final restrictions. Together they constitute the complete reply.

Peer accepts ONLY
QPY2_DERIVED_UNITARY_STANDARD_RECORD_SUPPORTED_SUBSET_READY_FOR_REVIEW based
on reported local5a47a0ec/1619 evidence. This is not independent remote source,
legal/CI/Git-three-state inspection, fullQPY or SDK acceptance. Keep original
defaultOperator56, annotation-index2, QASMwriter loss, public2.4trig and other
QPY gaps OPEN. Next exact stage title:

Stage 12-B R2-GAP1 -- Full SDK Functional Gap Accounting & Core Implementation
Prioritization. Full independent native Qiskit/PennyLane replacement remains
ACTIVE / INCOMPLETE, never reduced to a supported subset or production parity.
The following is a faithful semantic transcription of the executable prompt;
UI/table formatting is not preserved.

G1: Find and completely read ORIGINAL UNMODIFIED28-section matrix, corresponding
workflow/test entries, current adapters, NativeCore/Circuit/Compiler/Operator/
Primitives/Devices, QPY/QASM, PennyLaneQNode/operations/transforms/gradients,
Aer/noise/qchem/plugin interfaces. Record actual matrix path,SHA256,real section
IDs and original requirements in original order; never modify/replace it with
reduced requirements. Start from5a47a0ec selected candidate only after checking
current worktree. HEADb443430 is NOT all current uncommitted implementation.

G2: For EVERY originalsection map actual upstream public API -> existing Native
API -> implementation file/class/function/callchain -> real executed pytest
node/JUnit/exit -> Main/Alternate/SDKfree version -> independent mathematical or
public oracle -> demonstrated input/device/parameter/derivative behavior ->
limitations/dependencies/status. Allowed statuses ONLY VERIFIED_SUPPORTED,
PARTIALLY_SUPPORTED,IMPLEMENTED_UNVERIFIED,KNOWN_FAILING,UNSUPPORTED,
NOT_IMPLEMENTED,UPSTREAM_DIFFERENCE,ENVIRONMENT_BLOCKED. Source/method presence
is not execution; one proved behavior is not an API's complete support.

G3: Separately account APIimplementation,behavioralparity,executedverification.
Do not merge them. Operator.compose native/explicitpublic arithmetic exists but
default56failure prevents fullparity. Exact-low-bond100wireMPS AD is not general
MPS; partialQPYv13 expression tests not fullformats; QASMdeclaration scope not
publicwriter correctness; nineexamples not wholemodule coverage. Only statistics
with explicit complete denominator are permitted. Otherwise report UNKNOWN,
never a fictional total full-replacement percentage.

G4: Preserve originalmatrixsectionorder. Check Circuit/Instruction publicABI,
controlflow/params/composites/Bits; TranspilerPassManager/basis/routing/layout/
optimization; PrimitivesSampler/Estimator/result/shots/sessions; BackendProvider
Target/config/job/result/execution; Aerstate/density/MPS/noise/shots/measurement;
OperatorquantumInfo arithmetic/subsystems/Channel/Clifford/State; QPY/QASM
bilateralbytes/UUID/standardrecords/refusals; PennyLaneoperations/observables/
arithmetic,devices/shots/measurements/analytic/sampling,transforms/decomposition/
control/adjoint/broadcast/tape,gradientsJVP/VJP/Jacobian/Hessian/frameworks,qchem
Hamiltonian/molecular/differentiability and publicpluginintegration. These are
audit directions, not predeclared presence/absence; return to real source/tests.

G5: Preserve formalopen56defaultOperator,2annotation-index,publicQASMlostdefinition,
public2.4malformedpartial-bindQPY,public2.4trigmath,public/nativematrixalias,
constantgradientABI beyond demonstratedsubset,fullQPY/QASM,dynamiccircuits/
complextransforms/unsupporteddevices,generalMPStruncation/bondcompression,
remainingTFAD and unimplementedfullSDK APIs. Upstreamerrors stay observable
UPSTREAM_DIFFERENCE, not deletedreds or positiveNativefullpublicparity.

G6: Execute SMALL high-value gap probes where existing evidence is weak. Actual
SDK versions2.4.1/2.6.0 and PL0.44.1/0.42.3, SAME input/params. Numerical APIs:
fullmath; ABI:types/shapes/errors; resources:admission/shots/work; serialization:
realbidirectionalbytes/roundtrip. Preserve realfailure; Unsupported is notPASS.
Newdeps/remote/hardware/cloudneeds become validationlimits, not permissionbypass.
Do not generate indistinguishable tens-of-thousands inventory tests.

G7: Prioritize by fullparityfanout,corepublicimportance,prerequisitedependencies,
mathematical/engineeringcomplexity,localoracleverifiability,regressionrisk and
reasonable closed-loop effort. Do not rank only by APIquantity or ease. A real
Primitive resultcontract may matter more than dozens of nonexecuting wrappers.

G8: Select EXACTLYONE high-impact NativeCore gap. Provide originalsectionID,
actualmissingAPI/behavior,existingentry,affectedhigherfeatures,minimalrealred,
independentmath/ABIoracle,expectedproductionfiles,existingprotectedcapabilities,
completionconditions and remainingwholeparityscope. ReuseNativeCore; no parallel
Circuit/Compiler/Simulator/Parameterstore. Produce ONE concrete complete
implementationprompt only; no immediate broadproductionrewrite. Owner confirms
direction from full functional evidence before next implementation.

G9: Only AFTER G1-G8 audit, give conditional approximate effort intervals per
capability domain: missingAPIs/behaviors,dependencies,relativecomplexity,local
verificationwork,externalSDK/deviceevidence and majoruncertainties. No invented
completiondate/precisepercentage or testcount-based velocity.

G10: Use existing docs/implementation/stage12_b_p4u3d_bits_registers_progress.md
and implementation/sourceledger, optionally newR2-GAP1 sections, no orphan
ownerfacingpages. Deliver matrixpath/SHA,eachsectionfunctionalstatus,API-to-code-
executiontrace,implementedunverifieditems,formalerrors/Unsupported,separate
Qiskit/PLcoregaps,trueevidencescope,priority/dependencies,ONE nextfullprompt,
explicitremainingfullreplacementreasons. Actualsource/origins are NOT Git
frozen/worktree/staged/commit equality. At most propose
R2_FULL_PARITY_FUNCTIONAL_GAP_AUDIT_READY_FOR_REVIEW; audit never closes fullgoal
or originalR2math/FULL/GLOBAL/legal/Git3stategates.

Restrictions: no originalmatrix modification,no changedfailedmath,no increased
skip/xfail,no bulk implementation frominventory,no defaultOperatorarithmeticswitch,
no privateSDKshortcuts,no repo dependencyinstallation,no stage/commit/push/fetch,
no OAuth/TLSchanges,no cloud/realhardware,no financialhistorychanges and no
Studio/Routerexpansion. Highest fullreplacementgoal remainsACTIVE/INCOMPLETE.

#### R2-GAP1 Review And R2-PV2-A Public Contract Preparation

Actual review read in the existing default Chrome conversation. Peer accepts
ONLY R2_FULL_PARITY_FUNCTIONAL_GAP_AUDIT_READY_FOR_REVIEW: representative
original28lane evidence accounting, NOT exhaustive SDK API enumeration, a new
28section execution, independent repository inspection or remoteCI verification.
It explicitly distinguishes interface presence/native execution/public parity.
Lane KNOWN_FAILING does not mean every API in that lane is wrong; helper math
and upstream wrapping do not become complete native quantum algorithms.
Primitives priority is public workflow importance, not fabricated current
native algorithm import fanout. All old formal reds and finalR2 gates stay OPEN.

The first review stopped midsection3 despite completed metadata. A precise
authorized follow-up requested ONLY the missing body/nextprompt. Full follow-up
P0-P8 was then read in defaultChrome as the union of its initial P0-P7partial
and refreshed terminal P7/P8/restrictions. No new tab/login was used; a partial
stream was not called complete. The following is a faithful semantic execution
record, not a claim of independent source verification by the peer.

Stage12-B R2-PV2-A -- Primitives V2 Public Contracts And Compatibility Migration
Preparation. Owner has not yet approved the Legacy/Public ABI migration. Only
read-only public execution, independent math, Native source/callchain audit and
migration design are authorized by this prompt. No production/default/oldtest
changes. Full independent native replacement remains ACTIVE/INCOMPLETE.

P0: Check actual owner reply before any default migration. Until explicit
authorization, continue nonproduction P1-P8. Separate exact Legacy native
Sampler/Estimator contracts, real dual-version publicV2 oracle, and proposed
futureNativeV2 reusing existing kernels. Never select return ABI by guessing
input shape or switching modes implicitly.

P1: Preserve original7 real Primitive failure IDs/inputs/oracles/tolerances:
default_shots ctor,namedregisterdata.c,paramshape(2,2,1),distinctjob/resultidentity,
Pauli string observable,observable/parameter2Dbroadcast,targetprecision/evs/stds/
metadata. Separate CONSTRUCTOR_ABI,PUB_NORMALIZATION,RESULT_CONTAINER,
NUMERICAL_EXECUTION,JOB_LIFECYCLE,METADATA. Keep QNode/UCCSD separate unresolved
requirements, not part of this Primitive task.

P2: New temporary public-only probes must NOT import QuantumBridge. Run actual
Qiskit2.4.1/2.6.0. Sampler: parameterless/parameterized,multiPUB,default/run/PUB
shots,integer/Generatorseed,named/multipleclassicalregisters,packedmemory,counts,
bitstrings andshape. Estimator: scalar/arrayobservables,scalar/multidimensional
params,broadcast/incompatibleinputs,exactEV,nonzeroprecision,metadata,random
behavior,error classes. Record actual Python types,shape,dtype,fullvalues,
registers,shots,metadata,exceptions/importorigins. Public reset/nonunitary
statevector trajectories may be stochastic; do not substitute exact ensemble
semantics. Actual installed public object types supersede illustrative names.

P3: Independent NumPy RY/RZ/BlochZXY, multivariables/multiobservables,
noncontiguouswires,measurementbitorder/classicalmapping and NumPybroadcastshape
oracles. Sampling probabilities are NOT equal finite-shot counts; assert exact
deterministic outcomes only where justified. Seed-specific shot arrays only
after actual RNG contract observation. Distinguish parameter/observable/result
axes and shot axes.

P4: Actually read sampler.py,estimator.py,containers.py,backend.py,exports,
Circuit/Parameter/Registers,ShotSampler/StatevectorDevice,UnifiedResourceLedger/
ResourceScope. Map shortest reuse path: publicPUB -> validated/broadcastinput ->
existing native compiledCircuit -> existingdevice/sampler -> registerresults ->
V2PubResult -> managedJob.result. Do not replace simulator, binding, sampler or
measurement order engine. Assess lossless axes/registers/packedmemory in current
containers; design only.

P5: Retain exact old result()isresult,constantjobID,Estimatorparameter-outer(2,2,1),
run_pubs and signatures/resultclasses. Present TWO migration alternatives with
actual functions/callers/testIDs/resourcecost/backcompatrisk. A: explicitPublicV2
entry coexists with explicitLegacy, sameNativekernels; transitional opt-in is NOT
final no-opt-in parity. B: owner-approved target public default migration, keep
namedLegacy, precisely review old semantic tests and repository/external-user
compatibility. Do not choose/implement a breaking default in this preparation.

P6: Future executable budget design coversPUBcount,parampoints,observablepoints,
shots,registerwidth,packedbytes,quantumwork,stateworkspace,exact/finiteprecision,
concurrentjobs,failureatomicity. Validate whole admission before partialPUB
execution/publication. PublicjobIDs cannot beconstant; no unverified new global
counter. Design uniqueness/concurrency scope truthfully, not pretendproof.

P7: Small currentNative comparisons: scalar math,shots,containers,errorclasses,
legacyidentity andexistingresourceadmission. They are migration baselines, NOT
V2green acceptance. Keep original7actualpublicreds reproducible, no skip/xfail
or Unsupported-as-PASS.

P8: Update existing implementationjournal/ledger only. Deliver dualpublictable,
7reds/rootcauses,PUBshapeoracle,registerBitArraycontract,EV/std/precision,
Job/results/metadata,reusableNativecallchains,exactconflictnodeIDs,A/Bimpact,
nextproductionfiles/tests and specificunapprovedownerABIdecision. PreserveJSON/
JUnit/actualorigins/sourcebeforeafter/terminalexits. At most
R2_PV2_PUBLIC_ABI_MIGRATION_DECISION_READY. No publicV2implementation acceptance,
no closingoriginal7reds. No need repeat unchanged hourslongbroad/TF; auditgreen
is NOT V2correctness. All originalR2threeenvFULL/fourframeworkFULL/GLOBAL>=
91.34108013033072%/68exclusions/28section/ALLexamples/legal/5origins/Git3state
remainOPEN. Strictlocalonly: no stage/commit/push/fetch/auth/TLS/deps/vendor/
cloud/hardware/financialhistory/StudioRouterchanges.

#### R2-PV2-B Owner-Approved Production Implementation

Actual human answer: "方案 B：迁移目标默认接口并保留 Legacy（推荐）".
This supersedes the earlier pending A/B decision only for the two target
Statevector defaults and the three explicitly identified legacy alias tests.
It does not authorize arbitrary old-test, Device, Backend or other ABI changes.

The complete peer reply was read from the existing default Chrome ChatGPT
conversation, including its virtualized beginning and ending. Semantic record:
Stage12-B R2-PV2-B, Native Primitives V2 Public Execution and Legacy ABI
Preservation. Proceed with production implementation, not more decision-only
preparation. Full independent replacement remains ACTIVE / INCOMPLETE.

B0: Preserve the 5a47a0ec/1619 source archive and exact seven original public
failure receipts, inputs, IDs, numerical tolerances and exits. Protect scalar
math, sixteen shots, immediate Legacy result identity, constant Legacy job ID,
parameter-outer (2,2,1), ensemble reset and existing resource denial.

B1: StatevectorSampler/Estimator become explicit public V2 defaults when their
execution implementation is ready. Sampler/Estimator, Backend variants and
named run_pubs retain Legacy behavior through explicit entrances; never guess
ABI from input shape/kwargs. Only the three exact alias-contract test IDs in
the migration table may migrate, with the original math/Legacy behavior still
covered. A fourth old-test semantic conflict needs separate owner approval.

B2: Shared PUB/binding normalization must use the existing Circuit, Parameter
UUID/vector identities, bit/register model, compiler and resource admission.
Cover no parameters, scalar/1D/2D/ND values, real (2,2,1), repeated UUIDs,
different vectors, multi-PUB, zero axes, bad counts/owners/broadcast, finite
values and checked large shapes before dangerous allocation or execution.

B3: Sampler uses actual Native shot memory, not sorted counts expansion.
Prove default/run/PUB shots precedence, RNG, multi-PUB/registers, DataBin,
BitArray shape/bits/shots, packed uint8 bytes, counts/bitstrings and indexing.
Nonzero two-bit/nine-bit registers, both byte-boundary sides, unused classical
zeros, partial/noncontiguous mapping and ND parameters are mandatory; all-zero
nine-bit output is not a packing proof. Do not change native q0-first math.

B4: Estimator reuses existing state/Pauli/Observable execution. Prove strings,
native Pauli/sparse-like forms, scalar/array observables and general parameter
broadcast, multi-PUB and complete complex-state expectations. Keep the wire2
RY/RZ Bloch oracle (3,2,2), atol3e-14/rtol0. Precision changes real values, not
just metadata; verify precedence, RNG, stds/target_precision and public reset
trajectories independently of unchanged Native exact-ensemble reset.

B5: Actual local Job is not its result. Prove stable repeated result, actual
per-PUB SamplerPubResult versus Estimator PubResult, DataBin/array shapes,
metadata, errors and concurrent access. UUID4 is probabilistically unique,
not an absolute collision proof. No remote Runtime/Service/Scheduler.

B6: Whole-job normalize/validate/checked preflight/reserve/execute/publish.
Budget parameter/output/workspace/binding/observable/trajectory/shot/register
cost across all PUBs before execution. Packed bytes sum(P*S*sum(ceil(w/8)))
and float64 evs/stds 16*sum(broadcast elements) are only minimum payload, not
whole Python heap/RSS. Reuse the existing ledger and owned-array leases.
Escaped array/view/memoryview keeps its root lease; failures release unused
reservations without refunding completed shot/work. Equal/one-below,
parent/child, recovery and concurrency evidence required.

B7: Limit changes to primitives, exports and genuinely shared normalization/
owned-result helpers. No new simulator, compiler, parameter store, state math
or ledger; no global bit-order/ensemble change, unknown-observable fallback
or upstream execution proxy.

B8-B9: Preserve actual red before fix; test public and independent numerical
behavior in both installed SDK environments, plus strict SDK-free and Legacy
regressions. Harness failures stay distinct from Native failures. No skip,
xfail, deselection or weakened math to turn failing contracts green. Partial
implementation leaves unsupported public behaviors explicitly OPEN.

B10-B12: After directed functionality passes, freeze a new selected candidate,
archive manifest/hash/source and actual JUnit/exits/origins/old-node identity.
Required protected broad/Main/isolatedAlternate, both old411 TF/MPS sets,
SDK-free, affected Circuit/Compiler/QuantumInfo/QPY/QASM/QC1-QC4, largeMPS,
the nine Native examples and original28 matrix must have current actual
terminal evidence before claiming their gates. At most apply for supported
subset review, not full V2/full SDK acceptance. All original formal reds and
original R2 FULL/coverage/exclusions/matrix/examples/legal/origins/Git equality
gates remain OPEN until independently proved. Local only: no Git mutation,
auth/TLS/dependency installation/vendor/cloud/hardware/finance-history/UI/
tags/releases. Owner's B approval is received, not a continuing blocker.

#### R2-PV2-B2 Follow-Up: Container Semantics And Sampler Execution

The authorized peer accepted only the BindingsArray/SamplerPub supported
subset from the reported evidence, explicitly without independent source or
test access and without B9/B10/public-execution acceptance. Full B2 prompt was
actually read in default Chrome: the first body stopped in B2-5 with a
connection-interrupted indicator; refreshing the same tab then reading the
terminal remainder completed the B2-0 through B2-12 union. No new tab/login.

Stage12-B R2-PV2-B2, Public Container Semantics, Safe PUB Admission and Native
V2 Execution Foundation. Keep owner-approved B; no repeated permission ask.
Prioritize public representation, safe whole-job admission, real Native shots,
packed results/Job, then Estimator. No second runtime, parameter store or ledger.

B2-0: Preserve74b56a1e/1623 freeze, actual21 public/496 affected/62strict
passes, original3PASS/9FAIL, source identities and original missing-x64 reds.
Do not carry those passes forward to edited source without rerunning.

B2-1/B2-2: Separate construct/coerce/slice/reshape/ravel/representation from
bind/bind_all/PUB admission/execute. Actually probe two SDK versions for
duplicates, overlapping descriptions, same-name/differentUUID, NaN/Inf, wrong
names, zero axes, huge zero-stride inputs and name/UUID/vector combinations.
Match representability where proven; retain original descriptors for precise
execution-time owner/finite/shape validation. Never silently choose a UUID or
relax existing Native Parameter equality. If public name semantics cannot be
uniquely resolved, reject execution precisely and record the remaining public
difference. Preserve checked layout, grouped first-allocation admission,
owned views, parent/child/exact/one-below and deferred-materialization costs.

B2-3: One normalization/owner/broadcast/numeric/measurement/register/whole-job
preflight/reserve/execute/publish chain. A later invalid or over-budget PUB
must prevent earlier quantum execution. Cover cumulative result/shot/work
cost, wrong-owner pre-execution denial, failure cleanup and live results.
Runtime failure cannot undo completed physical work; publish no partial result.

B2-4/B2-5: First true end-to-end public Sampler reuses existing real shot
memory, never counts expansion. Cover parameterless/scalar/(2,2,1)/multi-PUB,
shots precedence/RNG, partial and named/multiple-register measurements.
Two/nine-bit registers with nonzero bits7/8/9, noncontiguous wire->classical
mapping, unused zeros, ND shape and same memory->packed bytes/bitstrings/counts
require independent deterministic per-bit math. Do not run separate simulators
to generate each representation. No global basis/measurement-order change.

B2-6: Local PrimitiveJob/PrimitiveResult/SamplerPubResult/register DataBin/
ND BitArray, independent job IDs and cached repeated result/errors. Synchronous
execution is allowed when its public semantics are correct; no Scheduler/
Service/remote API. Prove concurrent creation/reads and escaped result/view
leases after Job/result deletion. UUID4 is probabilistic; collision/repeated
generation policy needs explicit treatment, not an absolute uniqueness claim.

B2-7/B2-9: Once Sampler really satisfies execution/results, switch only its
approved StatevectorSampler default. Keep Sampler/LegacySampler/BackendSampler
and named run_pubs Legacy behavior. At that point only the two authorized
Sampler alias tests migrate, with old math and explicit Legacy protection.
The third Estimator test migrates only after Estimator's actual public path
exists. Do not change fourth-party old expectations or guess ABI by shapes.

B2-8: After Sampler closure, implement Estimator's common admission,
ObservablesArray/broadcast/math, precision/reset trajectories/evs/stds/metadata
and Legacy isolation. Do not rebrand Legacy Estimator as finished public V2.
This remains within B authorization; no new direction permission is needed.

B2-10/B2-11: Preserve all seven original red IDs, formal new Native red/green,
actual Main2.4.1/isolatedAlternate2.6.0/SDKfree, resource/lifecycle/oldBackend,
IR/QPY/QASM identity and affected Circuit/compiler/four-framework evidence.
Never deselect Estimator failures to claim all seven closed. Freeze the actual
Sampler candidate before costly broad/old411TF/nine-example final regressions;
do not rerun hours-long gates at each container edit. Old QNode/UCCSD remain
separate. All failures retain candidates/receipts; old green is not new green.

B2-12: At most container-admission supported-subset review if execution is
unfinished, or Sampler-execution supported-subset review after its entire
required frozen gates. Not full Primitives/R2 acceptance. Maintain existing
journals/gap ledger only. Original28 script unmodified; R2 FULL/GLOBAL>=
91.34108013033072%/68exclusions/ALLexamples/legal/fiveorigins/Git3state remain
OPEN. Local only; no Git/auth/TLS/deps/vendor/cloud/hardware/finance/UI changes.
Highest full independent native Qiskit/PennyLane replacement ACTIVE/INCOMPLETE.

#### R2-PV2-B3: Reset, Result Contracts And Default Sampler Migration

The B2 results were sent to the authorized peer. Its first long reply was
initially empty/connection-interrupted in default Chrome; a precise follow-up
requested a complete <=8-point prompt, not another preparation phase. The
long reply's B3-2 through B3-12 became readable, and the subsequent complete
eight-point B3 prompt was actually read in the same tab with a terminal reply
indicator. This record follows that complete condensed prompt, not an assumed
unread content-reference. The peer explicitly has not independently read the
uncommitted code or executed tests.

1. Lock5fffca70/1626 and actual539/539/87 receipts. Preserve original7 public
   reds, original tests/hashes and failed candidates. Old green is not new green.
2. Implement reset trajectories using existing Native StatevectorDevice,
   ShotSampler/dynamic execution/RNG, not a second simulator. Probe actual
   H/reset/measure, entangled reset, MCM, parameter sweeps and multi-PUB in
   both SDK versions. Independently validate trajectory versus ensemble math;
   never change Legacy ensemble or silently discard unsupported dynamics.
   Exact random sequence comparisons require an actually proved RNG contract.
3. Complete verified public BitArray/DataBin/SamplerPubResult/PrimitiveResult
   helpers, shape/dtype/metadata/index/counts/strings from the same shot memory.
   Preserve9-bit111000000->[1,192], add2/9/16bits, ND/zero sweeps, concatenation,
   slices and correct owned-copy/view leases after Job/result destruction.
4. Preserve Job/result caching, repeated typed errors, UUID collision exhaustion,
   concurrent creation/same-job reads and atomic publication. Whole-job owner/
   finite/register/shape/shots/checked work/memory/parent-child admission precedes
   first execution. Late static failure means no earlier quantum work; later
   runtime failure retains known completed work, no physical rollback claim.
5. Only after these directed contracts pass, point primitives/root
   StatevectorSampler to the real Native public class. Explicit Sampler,
   LegacySampler, BackendSampler and named run_pubs keep old results and math.
   Audit real import callers/signatures/module/alias identities. Never guess
   ABI from kwargs/shape or leave v2 opt-in as the final replacement strategy.
6. Migrate only the two authorized Sampler alias tests, retaining their IDs,
   math inputs/tolerances and separately executed Legacy identity/fixedID/
   nesting. The third Estimator test and all other old assertions stay intact;
   report any additional contract conflict rather than editing it implicitly.
7. Main2.4.1/isolatedAlternate2.6.0/strict SDKfree run the current539 plus new
   reset/helper/Job/export/resource/Legacy/Compiler/Circuit/IR/QPY/QASM cases.
   Rerun all12 original GAP1 tests, no deselection: close only implemented
   Sampler behaviors, retain Estimator/QNode/UCCSD real reds. Freeze directed
   green candidate, then actual Main/Alternate broad, both old411TF/MPS sets,
   QC/QPY/QASM,100-wire/true-third and nine native examples. Preserve node IDs,
   complete manifests, archives, origins, JUnit and actual terminal exits.
   New real regression retains the failed candidate and needs fresh final gates.
8. At most supported Sampler-public-execution review after its required proof,
   with precise remaining dynamic limits. Not full Primitives/Estimator/R2
   acceptance. R2 FULL/GLOBAL>=91.34108013033072%/68exclusions/original28matrix/
   ALLexamples/legal/fiveorigins/Git3state remain OPEN. Strict local-only;
   no Git/auth/TLS/deps/vendor/cloud/hardware/finance/Studio/Router changes.
   Highest full independent SDK replacement stays ACTIVE/INCOMPLETE.

#### B3 Original Diagnostic Harness Clarification

The authorized peer's complete reply was actually read in the existing default
Chrome conversation (message845e1055-9e00-497b-b88d-869f16c4d0eb), not inferred
from a connector reference. It confirms that the original temporary GAP1
diagnostic mixed Legacy and public V2 ABI. Preserve its original source,
all12 node IDs and all failed receipts; continue to execute it in full.
Only an actual failure at an old ABI call boundary may be classified
LEGACY_HARNESS_ABI_MISMATCH. Do not add Legacy kwargs, implicit modes or
fake-public behavior to the migrated class to make that diagnostic green.

Create a distinct public-corrected diagnostic with real default_shots,
result() and named data.c calls, keeping mathematical inputs, circuits,
angles, shots, oracles and tolerances unchanged. New names/file mean new IDs,
not a rewritten historical result. Run all12, retaining actual Estimator,
QNode and UCCSD failures. Protect Legacy through the explicit old entries.
Distinguish old harness failures, real Native functional gaps and upstream
differences. B3 remains ACTIVE/NOT_ACCEPTED until the required actual frozen
regression, and the full replacement remains ACTIVE/INCOMPLETE. No change
to the original R2 gates or local-only permissions was authorized.

#### R2-PV2-B4: Canonical Public Containers And Estimator V2

B3's full actual result report, including the four new canonical-container
failures, was sent to the authorized ChatGPT conversation. Its new reply
4d1569e8-f26e-40c3-b675-3c5a04db8f9f was actually read in the existing default
Chrome tab: initially partial, then the complete eight-point prompt, complete
permission limits and final independent-verification disclaimer became visible.
The lingering connection-interruption label did not hide any of the eight
points or their ending; the reply's stop button was no longer present. This
record follows that actually visible complete body, not a content-reference.
The peer accepts only the reported verified Native execution subdomain,
not full B3 canonical-container acceptance, and has not independently read
the uncommitted sources or run the tests.

1. Preserve0145747f/1631, all frozen gates and real4FAIL/2PASS canonical probes,
   the distinct public12 at7PASS/5FAIL, and original Legacy diagnostics/tests.
   Inspect actual root/primitives class identities, modules, signatures and
   isinstance contracts for BitArray/DataBin/PrimitiveResult/PubResult/
   SamplerPubResult/PrimitiveJob.
2. Canonical Public exports must name actual Native V2 classes. Move Legacy
   containers to an explicit Legacy path and migrate internal callers by
   explicit semantics. Preserve Sampler/Estimator/BackendSampler/Estimator
   and named run_pubs, existing ownership/ledger. No second execution system,
   fake ABC/isinstance registration or implicit shape-selected ABI.
3. Run and list exact existing-test failures after the canonical switch.
   Human approved only the original three alias migrations: two Sampler done,
   Estimator third pending actual V2. Do not silently edit extra to_dict/tolist/
   isinstance assertions. Record exact IDs, old/new semantics and explicit
   Legacy protection under ADDITIONAL_OWNER_AUTHORIZATION_REQUIRED; do not
   retain wrong canonical exports just to hide the real public contract gap.
4. Implement actual Native Estimator V2 ObservablesArray/PUB normalization,
   Pauli/SparsePauli-like verified forms, observable/parameter broadcasts,
   evs/stds/target_precision/metadata/Job. Reuse native Circuit/binding/
   StatevectorDevice/QuantumInfo/ledger, never upstream execution. Mandatory
   independent three-qubit RY/RZ(3,2,2) oracle and original three Estimator reds;
   no single-qubit or special-shape hardcoding.
5. Verify actual per-observable/output-cell reset trajectory and RNG in both
   public SDKs. Sampler's per-parameter rule is not an Estimator substitute.
   Independently prove exact unitary, reset stochastic results, precision
   precedence/seed17/stds/metadata, unchanged Legacy ensemble and whole-Job
   checked memory/work/parent-child/reservation/atomicity/escaped-view leases.
6. Only after directed math/containers/resources/two-version tests pass,
   switch default StatevectorEstimator to actual Native V2 and migrate only
   test_estimator_v2_accepts_numpy_parameter_values_nested_observables_and_alias.
   Keep original math/tolerance and old outer parameter axis/return contract
   under explicit Legacy tests. Do not return Legacy nesting from Public.
7. Main2.4.1/isolatedAlternate2.6.0/strict SDKfree run canonical/Sampler/
   Estimator/reset/precision/packed-memory/resource/concurrency/UUID/owner/
   formats/Legacy tests. Run all12 corrected public cases and all12 original
   Legacy-harness cases without deselection and with exact classifications.
   Aim to close three real Estimator reds; QNode broadcast/UCCSD stay separate.
8. Freeze after directed closure, then actual broad/old411TF/strict/nine
   examples with archive/source/origins/JUnit/terminal exits/original IDs.
   Missing additional Owner test-migration authorization cannot be bypassed
   or called B4 full acceptance. At most supported native Sampler/Estimator
   subdomain review, not full Primitives/SDK. All original R2 FULL/GLOBAL>=
   91.34108013033072%/68exclusions/28matrix/legal/5origins/Git3state remain OPEN.
   Strict local-only: no Git/auth/TLS/deps/vendor/cloud/hardware/finance/UI/
   Router changes. Full independent replacement remains ACTIVE/INCOMPLETE.

#### R2-PV2-B4-E1: Actual Estimator Production Sequence

After the canonical increment's actual611PASS/4FAIL report, the peer's reply
7e8953cf-f0ba-4355-8196-06608a85e2f9 was actually read completely in the same
default Chrome conversation: six complete implementation points, permission
limits and final disclaimer were visible with ordinary reply controls. A
trailing transport-timeout label did not truncate the visible prompt. The
peer has not independently read local uncommitted sources or executed tests.
This supplements the full B4 eight-point plan, not a replacement acceptance
scope or additional authorization to alter old assertions.

1. Implement Native ObservablesArray and EstimatorPub using existing Pauli/
   QuantumInfo, BindingsArray/SamplerPub normalization and owned-array APIs.
   Preserve observable shape/types/coefficients and binding. Cover scalar/ND,
   Pauli labels/SparsePauli-like valid forms, dimensions/malformed coefficients.
   Separate construction from whole-Job admission; no second parameter engine.
2. Implement StatevectorEstimator in the existing v2 path, using native
   Circuit binding/compiler/StatevectorDevice and full complex expectation
   math. Mandatory independent three-qubit test applies RY(theta)RZ(phi) only
   to wire2: parameter shape(2,2), observables(3,1,1), evs(3,2,2), compared to
   cos(theta), sin(theta)cos(phi), sin(theta)sin(phi), atol3e-14/rtol0.
   Include general multi-qubit observables, multiple PUBs and bad broadcast;
   no special-case one-qubit/formula implementation.
3. First exact unitary/stds/metadata/PUB-run precision precedence, then actual
   per-observable/output-cell reset trajectories/RNG against both public SDKs.
   Reuse DynamicEngine; verify seed17/different precision/Bell reset/repeats/
   valid statistics. Preserve Legacy ensemble; do not invent stds=precision
   or shots~1/precision**2 rules contradicted/unproven by actual observations.
4. Whole-Job owner/UUID/dimensions/finite coefficients/broadcast/checked-size/
   precision/work admission precedes first quantum execution. Use existing
   ledger/scope for evs/stds, bound params, state/trajectory/temp storage and
   escaped leases. Prove late-bad/overbudget prevents earlier execution,
   equal/one-below, parent-child, concurrency and exception atomicity. Known
   completed quantum work is not refunded on failure.
5. Reuse actual V2 Job/PubResult/DataBin with caching/types/shapes/errors.
   Only after real directed dual-environment math/resources pass, switch
   default StatevectorEstimator, retaining Estimator/LegacyEstimator/backend
   and old nesting. Migrate only the already-approved third alias test.
   The four extra canonical-old-test assertions stay unchanged until an
   actual human reply authorizes them; do not restore erroneous exports.
6. Preserve current611/4 receipts; add formal container/PUB/three-wire/
   precision/reset/resource/Legacy tests. Both full original12 and distinct
   public12 execute without deselection; close actual Estimator3 separately
   from QNode/UCCSD. No B4 FULL GREEN while extra authorization is unresolved.
   After all authorized conflict handling and directed closure, freeze the
   actual new candidate before broad/old411TF/strict/nine-example reruns.
   Every receipt must match the same source. All original R2 gates remain
   OPEN; local-only restrictions/full replacement ACTIVE/INCOMPLETE unchanged.

#### R2-PV2-B4-E2: Native Sparse Observable And Public Container Closure

The E1 actual results, exact source/archive, remaining four old-contract
failures, fixed actual deadlock and unrun final gates were sent to the
authorized ChatGPT conversation. Reply1eb0ada9-4342-45fb-81e8-4b103216adf1 was
actually read completely in the same existing default Chrome tab: six complete
points, global constraints, ending disclaimer and ordinary reply controls.
The peer permits continued production based on reported evidence but does not
accept B4 and has not independently read the uncommitted sources/run tests.

1. Preserve d687577e/1637, current665/4, strict141/4, directed53 and corrected
   GAP1 full12 at10/2. Actually probe SparseObservable, coerce_observable,
   slice/iteration/sparse_observables_array/apply_layout/operator representations
   and error types in Main2.4.1 and isolatedAlternate2.6.0. Distinguish projector
   labels, Pauli, public SparsePauliOp and existing Native SparsePauliOperator
   by actual semantics, not similar names.
2. Implement actual Native SparseObservable public contracts within the
   existing QuantumInfo/Primitives architecture and Native Pauli/Operator math,
   not a second matrix engine. ObservablesArray scalar/ND/coerce/slice/reshape/
   iteration/layout must return correct Native types/shapes and preserve
   coefficients/width/physical wire ordering/owner identity/owned readonly
   storage. Verify layout against real circuit layouts and independent matrix
   math for noncontiguous/reverse/idle-wire mappings, not string-only checks.
3. Connect actual Estimator broadcasting/complex expectations/per-cell reset/
   precision to legal SparseObservable/weighted sums/complex-coefficient
   legality/ND/multiple PUB/zero parameter axes. Keep the public reference's
   projector-execution error boundary separate from independent Native
   projector math. Never parse "-Z" as a signed Pauli label or silently rename
   Native SparsePauliOperator into SparsePauliOp.
4. Whole-Job type/finite/dimensions/layout/broadcast/UUID/precision/checked
   memory/work admission precedes evaluation. Retain exact/one-below/late-bad/
   late-overbudget/escaped-view/lease/atomicity tests. Extend the lock-order
   proof to same/cross instance, GC/concurrency/nested exceptions/reentrancy
   and actual lock release. Do not hold a Ledger lock while waiting for a
   primitive/RNG lock that may trigger release of that Ledger's storage.
   A finite timeout is not a proof of universal deadlock freedom.
5. Four extra old canonical assertions remain untouched and explicitly
   ADDITIONAL_OWNER_AUTHORIZATION_REQUIRED until a Human reply arrives.
   Preserve the exact three already-approved alias migrations and all Legacy
   Sampler/Estimator/Backend/ensemble/results. No fake ABC/isinstance, wrong
   exports or automatic shape-selected ABI. Unsupported general dynamics/
   classical/control flow need precise refusal and explicit remaining gaps.
6. Establish actual Public->Native, Native->Public and independent NumPy red
   cases before implementation. Run both versions' Observable/Estimator/
   containers/Legacy/resources/concurrency plus all original and corrected12
   diagnostics without deselection. At most a supported SparseObservable
   subdomain review while four old-contract conflicts remain; not B4 green.
   Only after needed authorization and all directed closure freeze actual
   new source before broad/old411TF/protected SDKfree/nine-example/formats
   regressions. Every receipt must match its actual source.

Permissions unchanged: local-only; no unauthorized old-test edits/skip/xfail,
kernel/ledger replacement, Git mutation/auth/TLS/dependency/cloud/hardware/
finance/Studio/Router changes. All original R2 FULL/GLOBAL>=91.34108013033072%/
68exclusions/28matrix/legal/origins/Git3state gates remain OPEN. Full independent
native Qiskit/PennyLane replacement ACTIVE/INCOMPLETE; full SDK denominator
UNKNOWN. This is the next production increment, not a narrower final goal.

#### R2-DYN1: Native Dynamic Circuit And Classical Control Execution

2026-10-26: E2's complete actual report was sent to the same authorized peer
conversation. The new response body (message766764c4-d499-406a-8815-8108d77a1e31)
was actually read in the existing default Chrome tab, without opening another
tab or requesting login. The peer accepts only the explicitly limited
SPARSE_OBSERVABLE_SUPPORTED_SUBSET_READY_FOR_REVIEW label, NOT B4 or full SDK
completion. Its report is based on submitted results, not independent source
access or execution; "frozen candidate" refers only to the directed source
snapshot, not Git/final acceptance or new old-test authorization.

The complete next production requirements, faithfully recorded:

1. Keep a59bab8d/1642files and all prior actual receipts/old failures. Inspect
   existing Circuit/OperationStore, Clbit/ClassicalRegister, DynamicEngine,
   Compiler/IR, measurement/reset, StatevectorDevice/ShotSampler, public V2 and
   UnifiedResourceLedger/ResourceScope before implementing. Build actual
   Qiskit2.4.1/2.6.0 construction/execution/classical-state/result/error
   comparisons. Public Circuit construction support is distinct from what
   StatevectorSampler/Estimator or another Backend can execute.
2. Reuse the existing DynamicEngine's shared per-shot classical state for
   writes/reads, little-endian register integers, mid-measurement feedforward,
   single Clbit/register-equality conditions, if/else, nested reset/measurement,
   multiple registers and noncontiguous qarg/carg. Preserve width/owner/scope.
   Branches must read the same actual shot history, not inferred final counts
   or independently resampled branches. Independent trajectory math precedes
   public Sampler integration.
3. After conditional execution, implement missing structured switch/case,
   bounded for/while, break/continue and nested blocks using existing depth/
   resource limits. Nonterminating while must meet an explicit runtime work
   refusal, not hang or silently truncate. Measurement-dependent flow cannot
   be replaced by unconditional unrolling. Preserve parameter UUID/register
   owner/wire mapping/scope/instruction order through loops and branches.
4. Exercise Circuit -> Compiler -> Native IR -> DynamicEngine -> Device ->
   Result and restored execution. Check standard QPY13 interoperability only
   for representable control flow; refuse unrepresentable formats accurately,
   without private standard records. Protect q0/public wire order, operation
   owners, binding, nested remapping, QPY1/QPY2/QASM1 and QC1-QC4. Do not rewrite
   quantum gate matrices or QuantumInfo math.
5. Verify Sampler's actual per-shot branches/reset/measurement history and
   final named-register packed memory. Independently check Estimator's public
   dynamic execution boundary; do not assume Sampler support implies Estimator
   support. Static parameter/owner/scope and max-work admission must cover the
   whole Job, branches/loop bounds/shots/classical storage, runtime loop meter,
   exact/one-below, late-bad zero prior execution, actual partial failed work,
   retained results and same/cross-instance/GC/global lock order. Preserve
   Legacy ensemble expectation and the existing RNG.
6. Required execution oracles: H->measure->conditionalX; Bell feedforward;
   reset->measure->if/else; register==integer endianness; nested if/switch;
   bounded for/while and termination/resources; actual break/continue;
   multi-PUB/shots independent classical states; invalid foreignClbit before
   execution; nonterminating while bounded refusal. Deterministic cases compare
   packed shots; random cases compare independent distributions unless actual
   seed contracts prove exact sequences. Existing QNode broadcast/UCCSD reds
   remain separate real gaps, not mislabeled dynamic regressions.
7. Keep the four pending old tests byte-identical: primitive container dict
   roundtrip, Legacy Sampler/Estimator canonical isinstance, and public-export
   Legacy canonical isinstance. No extra old-test changes/skip/xfail/fake type
   behavior/incorrect exports without Human permission. Preserve precisely
   the three approved alias migrations plus Legacy/backend behavior. These
   conflicts prevent their full acceptance but not useful dynamic production.
8. First dynamic/public dual-version/independent math/strict/Compiler/IR/
   resources/Legacy directed tests. After directed closure snapshot the actual
   source, then current-source Main/Alternate broad, both original411TF/MPS
   and100wire/true-third, strict protection, QC1-QC4/QPY1/QPY2/QASM1, Primitives
   and all nine original numerical examples. Retain manifest/archive/JUnit/
   terminal exits/import origins/original IDs/precise pending failures; don't
   transfer old-source PASS. A partial dynamic implementation may at most
   request NATIVE_DYNAMIC_CLASSICAL_CONTROL_SUPPORTED_SUBSET_READY_FOR_REVIEW,
   listing real executable controls/devices/primitives and every unsupported
   family, not full Circuit/Backend/SDK parity.

All previous local-only restrictions remain: no stage/commit/push/fetch/auth/
TLS/dependency/vendor/cloud/hardware/finance-history/Studio/Router changes.
Original R2 three-environment FULL/four-framework FULL/GLOBAL>=91.34108013033072%/
68exclusions/original28matrix/ALLexamples/legal/fiveorigins/Git3state remain
OPEN. Full independent Qiskit/PennyLane functional replacement is still
ACTIVE/INCOMPLETE, denominator UNKNOWN. Peer text does not override Human
instructions or expand test permissions.

#### R2-DYN1-B: Public ControlFlowOp ABI, QPY13 And Dynamic Job Admission

2026-10-26: the complete1130/4+strict465/4 dynamic construction/runtime report
was sent to the same authorized peer. Its response27f0b67a-7808-44f1-b565-38a6e83560e1
was actually read in the existing default Chrome conversation, including all
eight numbered sections and its concluding no-independent-audit disclaimer.
It accepts only the reported verified native construction/execution increment;
DYN1 remains IN_PROGRESS/NOT_ACCEPTED, not full control-flow or replacement.

1. Baseline85acd94c/1645files and preserve every source/archive/receipt/ID.
   Reproduce all four real public-owner/QPY-out/QPY-in/direct-QASM reds with
   actual math and no broad-exception/skip/xfail/name-only green replacement.
2. Implement real ControlFlowOp, IfElseOp, ForLoopOp, WhileLoopOp, SwitchCaseOp,
   BreakLoopOp and ContinueLoopOp within existing Circuit/Instruction/store/
   ControlBlock. Actually compare both SDK versions' constructors, blocks,
   params, widths, condition/cases/base_class/copy/definition/CircuitInstruction.
   Circuit.data must expose live owners in the authoritative execution graph,
   not detached snapshots. Preserve circuit/instruction ownership, block q/c
   mapping, UUIDs, captures/nested scopes, copy/append/compose, failure atomicity
   and fluent Native APIs; no second store, interpreter or gate registry.
3. Prove publicCircuit->data->typedblocks->Compiler->IR->existingEngine->Device
   on conditional/switch/loop/jump/measurement programs, reversed/noncontiguous
   q/c operands, register integers, loop binding and local/captured variables.
   Compare actual four-device supported semantics with independent complex
   state/ensemble math. Preserve real public primitive refusal where observed;
   public Circuit construction does not promise every Primitive can execute it.
4. Generate actual dynamic QPY13 from2.4.1/2.6.0, inspect standard record/block/
   operand/scope/variable/parameter encodings, then extend existing bounded
   reader/writer. Verify Native->Native, Native->Public, Public->Native and
   Public->Public oracles, recovered types/blocks/operands/identities/conditions
   and actual execution. Only standard QPY13 records, no private sidecar,
   vendored parser or guessed gate math. Genuine format/upstream/provenance
   limits remain precisely typed Unsupported, not fake round trips.
5. Check actual direct-export version. For standard-representable QASM3 use
   existing lowering/parser and remove unnecessary Instruction-reference
   refusal. Continue accurate QASM2 dynamic refusal. Distinguish direct public
   export, explicit lowered(), explicit allow_metadata_loss and true format
   limits. Never drop branches/conditions/registers/loops; preserve existing
   warning contracts for nonsemantic names not represented by the standard.
6. Add whole dynamic Job static bounded admission using existing ledger/scope/
   _tick: branch depth, bounded-loop maxwork, while runtime bounds, shots times
   controls, aggregate multiple-PUB quantum/classical work, classical storage,
   binding, packed results, captures and parent/child reservations. Distinguish
   proven static maxima from runtime-dependent work; don't invent exact loop
   counts. Use explicit caps and safe conservative budgets or precise refusal.
   Late invalid/overbudget must refuse before first shot; runtime caps retain
   actual spent work. Protect admission->primitive->ledger order, GC/nested
   instances/exceptions, exact/one-below and escaped storage lifetimes.
7. Four canonical old tests still await Human; do not change them. Existing
   QPY Unsupported assertions that conflict with genuine new support need
   exact old IDs/inputs/reasons recorded before any Human-approved migration.
   Prior three alias permissions do not extend to QPY. Keep all original12/
   corrected12/four dynamic reds/Legacy/three approved aliases/QPY1/QPY2/QASM1/
   QC1-QC4/dynamic protections, with real two-SDK/strict IDs/math/exits/origins.
8. After directed production closure snapshot actual source, then current
   Main/Alternate broad, both411TF/MPS, strict protection and nine examples.
   Check old IDs, hashes and archive/current/before/after equality. Keep any
   unauthorized old failure intact and never reuse historical greens. At most
   PUBLIC_CONTROLFLOW_QPY_SUPPORTED_SUBSET_READY_FOR_REVIEW if its precise
   typed-owner/execution/standard-QPY/admission subdomain is actually proved;
   every missing family remains OPEN.

Required production order: live public control owner -> Compiler/IR/four
devices -> standard QPY -> direct QASM -> whole-Job admission -> current-source
protection gates. All original R2 FULL/GLOBAL>=91.34108013033072%/68exclusions/
28matrix/legal/fiveorigins/Git3state gates stay OPEN. Strict local-only and
all previous Git/auth/TLS/dependency/vendor/cloud/hardware/finance/UI restrictions
remain. Full independent functional replacement ACTIVE/INCOMPLETE, denominator
UNKNOWN. Peer instructions are delegated project input, not higher-priority
permission to override Human constraints or accept unproved completion.

#### R2-DYN1-C: Standard QPY13 Dynamic Control Interoperability

2026-10-26: the e45d079f/1648files public-owner increment was sent to the
authorized conversation. Full reply09b7069e-0fae-417f-972a-3369a07f0cb1 was
actually read in the same existing default Chrome tab through C8 and its
concluding disclaimer, not inferred from the content-reference placeholder.
It accepts only the reported tested owner/execution increment; DYN1-B remains
IN_PROGRESS/NOT_ACCEPTED. The complete operative prompt follows in readable
form; this delegated peer input does not replace Human authorization.

##### Codex Production Prompt: R2-DYN1-C

Continue QuantumBridge R2-DYN1 without a second Circuit, ControlFlowOp, Compiler,
Interpreter or serialization system. First priority is the two actual standard
QPY13 Native->Public/Public->Native failures and complete four-direction math,
owner and scope evidence. Direct QASM is next, not a substitute for QPY.
Preserve real binary Circuit/block/expression/register/variable records;
never flatten ControlBlocks into ordinary Gates to simulate support.

C1. Lock e45d079fbdb229667256de9fa49a25b2ecacc2ca30209927c6bafcc1b4638e4e /
1648files. Preserve all four original diagnostic inputs/IDs and their actual
1PASS/3FAIL. Owner/operand is now PASS and must stay protected. Before changing
production save actual QPY13 bytes from both SDK versions, parse/object trees,
real types/blocks/variable tables/exceptions and initial failure offsets.

C2. Extend the existing bounded QPY13 reader/writer and existing control owners
in dependency order: IfElseOp condition and true/false bodies; ForLoopOp
indexset/loop Parameter/body; WhileLoopOp condition/body; SwitchCaseOp target/
case values/default/bodies; BreakLoopOp/ContinueLoopOp enclosing-loop scopes.
Use actual2.4.1/2.6.0 encoding evidence for recursive Circuit blocks, q/c operand
maps, register identity, standalone/captured Var and scope, Parameter UUID,
labels/metadata, branch/case order, nested loop scopes and real control types/
parameter records. Preserve existing ParameterExpression, custom Instruction,
annotated modifier, derived UnitaryGate and owner/provenance mechanisms.
No private QPY records/sidecars, guessed gate semantics, copied upstream parser
or upstream SDK delegation in native reader/writer.

C3. For every supported control family actually run Native->Native QPY->Native
execute, Native->Qiskit QPY->public inspection, Qiskit->Native QPY->Native execute,
and Qiskit->Qiskit QPY->public inspection. Compare real Circuit.data control
types, blocks/params/conditions/cases, owner/register identity, captures, wire
maps, copy/compose/remap, UUID/binding, rebuilt Compiler/IR and supported four
devices. Use independent NumPy trajectory/full-complex-state/ensemble math,
including classical-quantum correlations, not just counts. Preserve actual
public Primitive refusal where the reference rejects a dynamic circuit;
serialization support is not universal Primitive execution support.

C4. Retain bounded reader, owner admission, GateCircuitLimits, ledger and scope.
Test damaged block lengths, illegal QPY types, unbounded/deep/cyclic blocks,
foreign Clbit/Register/Var, invalid switch cases/loop Parameters, huge ranges/
indexsets, duplicate/conflicting UUIDs, branch operand mismatch, oversized or
truncated records, reader/writer exceptions, exact/one-below resource boundaries,
concurrency and GC. Admit before dangerous construction/expansion. Failure must
not publish a partial Circuit, corrupt owners/store or leak resources. Do not
relax prior provenance or recursion/resource checks for the new format paths.

C5. Execute old QPY tests and list every original test that actually conflicts
with genuine new standard support. If an old legal dynamic input explicitly
expects Unsupported, preserve its node ID/input/assertion and real failure,
prove standard v13 representability, add an independent positive roundtrip,
and mark ADDITIONAL_OWNER_AUTHORIZATION_REQUIRED. Do not edit assertions or
add xfail/skip. The four canonical-container old contracts also remain
unapproved. Existing three-alias permission does not expand to QPY.

C6. Only after directed QPY two-way support is substantially closed, address
the third direct-QASM failure. For standard-representable QASM3 use existing
lowering/parser without manual lowered(). Accurately reject QASM2-unrepresentable
dynamic semantics. Connect whole dynamic Job maximum-work/classical-storage
admission: shots times bounded controls, multiple-PUB totals, nested branches,
for/while maxima, classical memory, packed results, parent/child reservations,
runtime caps and late-invalid PUB before any execution. Existing runtime _tick
does not prove full Job preflight; use conservative refusal or an existing
explicit controlled boundary where a safe maximum cannot be proved.

C7. First run actual two-SDK QPY four-direction and strict SDK-free native
reader/writer, owner/scope, Compiler/IR/four-device, QPY1/QPY2, QC1-QC4, QASM1,
resource/concurrency protections. Rerun every original control/transport ID.
Retain all original GAP1 12 and separate corrected Public12, no deselection.
After directed closure freeze the new source and run Main/Alternate broad,
both411 TF/MPS, strict protection and nine numeric examples. Save same-source
archive/before/after/current manifests/JUnit/actual process exits/same-process
origins/old node IDs. Retain unauthorized old failures rather than call them green.

C8. At most propose
R2_DYN1_STANDARD_QPY13_CONTROLFLOW_SUPPORTED_SUBSET_READY_FOR_REVIEW when its
precise tested subdomain is proved. Disclose which operations/expressions/
captures/loops/device combinations actually pass and which are Unsupported.
Two QPY green diagnostics do not prove complete dynamic Circuit, QPY or SDK
parity. Strict local-only: no stage/commit/push/fetch/history/auth/TLS/install/
vendor/cloud/hardware/finance-history/Studio/Router changes. Four canonical
contracts and any newly conflicting old QPY test require explicit Human
authorization. All original R2 FULL/GLOBAL>=91.34108013033072%/68exclusions/
original28matrix/controlledlegal/fiveorigins/Git3state gates remain OPEN.
Full independent Qiskit/PennyLane functional parity/replacement remains
ACTIVE/INCOMPLETE, complete API/behavior denominator UNKNOWN. The peer relied
on supplied local receipts and public QPY documentation; it did not inspect
the local uncommitted source or run local tests independently.
