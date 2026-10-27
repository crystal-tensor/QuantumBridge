# Received TF6-M2B Controlled Cached-Graph Prompt

Actual full reply read on2026-10-24 from the authorized existing default
Chrome conversation after transient disconnected output. No new tab/login.
Accessibility line splitting is retained. This is next-step guidance, not
independent source review or acceptance of the current development state.

QuantumBridge TF6-M2：Eager 共享账本检查点审阅
结论：当前 M2 已实现真实的 eager 共享账本与资源预留子集，可以继续下一段；但 M2 仍为 PARTIAL，不能进入 M3。
本轮最重要的进展，是把 TensorFlow Whole-QNode 的资源管理接入现有 
ExecutionPlan
、
derivative_planning
、
second_work
、
UnifiedResourceLedger
 和 
ResourceScope
，没有再创建第二个调度器或账本。
项目
当前报告结果
Main / Alternate 当前综合专项
各 99 passed
Shared ledger 强化专项
各 17 passed
SDK-free admission/directives
38 passed
原生 moving-power/MPS tangent/Fréchet
105 passed
Eager unified_limits / active scope
有真实并发和原子性测试证据
Traced/cached graph 的受控逐次记账
UNSUPPORTED / 未完成
M2
PARTIAL
M3 原四条 100-wire TF 红灯
仍未通过
三环境 FULL / GLOBAL / matrix
NOT
_
RUN
项目
Main / Alternate 当前综合专项
Shared ledger 强化专项
SDK-free admission/directives
原生 moving-power/MPS tangent/Fréchet
Eager unified_limits / active scope
Traced/cached graph 的受控逐次记账
M2
M3 原四条 100-wire TF 红灯
三环境 FULL / GLOBAL / matrix
当前报告结果
各 99 passed
各 17 passed
38 passed
105 passed
有真实并发和原子性测试证据
UNSUPPORTED / 未完成
PARTIAL
仍未通过
NOT
_
RUN
项目
当前报告结果
我认为需要继续保护的三个边界
1. 计划工作量与实际执行量不能混淆。
你现在先 
consume
 保守 planned work，再在成功后记录完成的 logical evaluations/tapes，这种分离是合理的。应继续区分：
已预留资源；
已尝试的逻辑工作；
成功完成的执行；
实际 Host/Device 调用；
估计的 TensorFlow tensor workspace；
不可观测的真实 allocator/RSS。
错误或取消后，已实际尝试的工作不能被回滚为零。
2. 缓存 ConcreteFunction 是核心缺口。
TensorFlow 官方说明，
tf.function
 的 Python side effects 通常只在 tracing 阶段发生，而已缓存的图会直接重新执行。因此，在图内部使用 Python ledger 调用，无法证明每次调用都会重新计量。
你的 
OUT_OF_SCOPE
 标记是准确的，但若想完成 M2 的
受控缓存图调用
，应提供一个明确属于 QuantumBridge 管理范围的执行入口，而不是要求用户直接持有任意 ConcreteFunction 也自动被计量。
3. 导数请求的预算不能等同于最高二阶 envelope。
目前 eager 每次 tensor evaluation 按已准入的最高二阶工作量保守扣账，可以作为安全上界。但仍需区分 value、VJP/JVP、完整 Hessian 和 streamed HVP 的不同执行请求，否则可能产生过度拒绝，也无法证明方向数和输出数的资源合并正确。
本次没有从报告中识别出必须撤销 eager 共享账本实现的已证实缺陷。真正剩余的是请求契约、缓存图所有权和运行期执行的计量保证范围。
以下审阅只依据你提供的本地测试报告。我没有独立检查未提交源码或远端 CI。
Codex 下一段执行 Prompt：Stage 12-B P4-U3D2-R2O3-B-TF6-M2B
Unified Derivative Requests, Controlled Cached-Graph Execution & ResourceScope Lifecycle
继续现有 Stage 12-B P4-U3D2-R2O3-B-TF6-M2，不新建 SDK 阶段。
本批仅关闭 M2 剩余的资源、导数请求与缓存图契约。未实际通过 M2 全部受支持范围前，不开始 M3。
完整独立原生 Qiskit/PennyLane full functional parity/full replacement 仍为：
ACTIVE / INCOMPLETE
1. 第一优先：统一导数请求描述
首先审计现有 
ExecutionPlan
、
derivative_planning
、
second_work
，不要创建名义上的新 
DerivativePlan
 或 
SecondWork
 类。
在现有请求结构上增加一个可审计、不可变的导数请求描述，逻辑上包含：
Python
复制代码
运行代码
DerivativeRequest
(
    
method
,
    
order
,
    
operation
,       
# value / jvp / vjp / gradient / hessian / hvp
    
input_count
,
    
output_count
,
    
direction_count
,
    
cotangent_count
,
    
parameter_identity
,
    
plan_identity
,
    
resource_limits
,
)
这是接口示意，实际字段和名称必须复用当前代码结构。
同一请求必须分别得到：
正确的数学操作；
正确的导数阶数；
与该请求匹配的静态工作估计；
正确的 NativeHost/Device 使用范围；
正确的 ResourceScope 归属；
可核查的账本结果。
不允许继续把所有 value、gradient 和 directional HVP 无条件计为同一个最高二阶 envelope，除非明确标为可审计的保守模式。
首组红灯
同一个低量子位 Whole-QNode：
纯文本
复制代码
value


gradient


JVP


VJP


single-direction HVP


two-direction HVP


full Hessian
分别测试宽松预算和紧预算。
必须证明：
value 的资源需求不大于相同条件下的二阶请求；
单方向 HVP 不暗中申请完整 Hessian；
多方向请求累计正确；
full Hessian 受 
max_hessian_elements
 约束；
不把外部 TensorFlow loss 的完整图当成 QuantumBridge 自有工作。
2. 第二优先：真正的 streamed HVP 合同
继续使用已有八参数、双 observable 的 Whole-QNode。
强制：
Python
复制代码
运行代码
max_hessian_elements
 
=
 
1
并 patch：
Python
复制代码
运行代码
QNode
.
compute_hessian 
=
 
fail
tf
.
GradientTape
.
jacobian 
=
 
fail
真实 streamed HVP 仍必须通过。
对每个方向 
𝑣
，应明确计划：
𝐽
𝑣
；
𝐻
𝑓
𝑣
；
多输出 cotangent 的收缩；
local Fréchet work；
MPS/Statevector workspace；
实际可控的 logical tensor evaluations。
方向数改变时，资源账本必须有可观测且合理的增量。
不要将一次 
HVP(v)
 记为已计算完整 Hessian。
此外，
tf.function
 内由外部 loss 触发的若干 TF AD 运算，若 QuantumBridge 无法观测真实次数，只能以已批准的受控请求 envelope 计量，不能虚报精确执行次数。
3. 第三优先：受控缓存图调用入口
这是本批最重要的新实现。
建议提供一个公开、明确受 QuantumBridge 管理的执行句柄，例如：
Python
复制代码
运行代码
managed
 
=
 
qnode
.
compile_tensorflow(
    
controlled_execution
=
True
,
    
input_signature
=
...,
)
名称仅为示意，须先审计现有公共 QNode API，避免与已有方法冲突。
该句柄应具有以下行为：
Python
复制代码
运行代码
y1
 
=
 
managed
(
theta1
)
y2
 
=
 
managed
(
theta2
)
每次通过 
managed(...)
 的调用都必须：
核验当前 plan identity。
核验 method、order 和资源约束。
取得当前 ResourceScope。
在 Python 受控入口预留已有共享账本额度。
执行已缓存的 TensorFlow graph。
在真正得到同步执行结果后提交完成记录。
出错时释放未使用的 live reservation。
不回滚已记录的 attempted work。
不要在 TensorFlow graph 内用 Python callbacks 伪造每次扣账。
必须清楚限定：
通过 
managed(...)
 调用：
LEDGER_ACCOUNTED
。
直接拿到内部 ConcreteFunction 并调用：
OUT_OF_SCOPE
。
TensorFlow allocator/RSS：
ESTIMATED_ONLY
。
必须正视的限制
如果一个受控入口返回的是仍带未执行 TensorFlow graph 的异步结果，不能在 Python 返回时就宣称 Device work 完成。
优先验证当前 CPU/eager 调用的同步语义；对无法可靠观测完成的异步执行模式，明确拒绝或标记未支持。
TensorFlow 
get_concrete_function()
 可以产生可复用的图，并按 input signature 进行专门化；它本身不提供 QuantumBridge 账本的逐次调用保证。
4. 缓存与执行句柄的所有权
建议使用一个不可变的已验证计划快照和受控执行句柄：
纯文本
复制代码
Native Circuit / QNode


       ↓


Existing ExecutionPlan


       ↓


Verified plan snapshot + resource signature


       ↓


Managed cached-graph handle


       ↓


Existing UnifiedResourceLedger


       ↓


TensorFlow ConcreteFunction
必须保护：
源 Circuit 后续修改；
ParameterVector resize；
owner definition 改变；
observable 改变；
method 或 max_diff 改变；
limits 收紧；
active ResourceScope 改变；
已退出 scope；
句柄复制；
多线程并发调用；
旧句柄调用时的非法身份。
这里要明确区分两种合法策略：
Snapshot handle：
 执行编译时固定的数学计划，不随 source 变化；必须明确标识其版本。
Live handle：
 每次检查当前 QNode 并在变化后重新编译或拒绝。
选择其中一种并通过公开测试验证，不能在某些字段上 snapshot、另一些字段上 silent live。
对已创建的句柄，后续收紧资源上限不得被静默绕过。
5. 
tf.function
 重复调用与动态校验
5. tf.function 重复调用与动态校验
对同一个缓存图执行：
纯文本
复制代码
valid


→ valid


→ NaN


→ Inf


→ branch cut


→ valid
记录：
trace count；
actual managed-call count；
ledger attempted work；
successful evaluation count；
aborted evaluation count；
runtime assertion results；
work remaining；
source state；
cached graph identity。
对可支持的固定 input signature，应验证没有无意义 retracing。
对于非法 shape/dtype，应该在受控调用前明确拒绝；非法数值则必须由真正图运行期断言捕获。
不能仅靠首次 trace 的 Python 参数校验。
6. ResourceScope 生命周期
针对以下场景写真实红灯：
无 active scope；
active parent scope；
nested scope；
child unified_limits；
parent 更严格；
scope 退出后使用句柄；
在另一个无关 scope 调用句柄；
两个 QNode 共享 parent ledger；
concurrent managed handles；
限额刚好等于需求；
限额比需求小 
1；
两个线程同时竞争剩余额度。
资源预留和提交必须沿用已有 
UnifiedResourceLedger
 
的锁与层级关系。
不得创建 
TF 
私有全局 
ledger。
7. 
避免双重计量
7. 避免双重计量
你之前已经修复 
whole-plan 
reserve
 
与 
local._admit
 
对同一 
workspace 
重复预检的问题。
本段必须覆盖：
whole-plan 
work 
reservation；
local 
matrix 
preflight；
statevector 
work；
derivative 
work；
NativeHost 
work；
Device 
work；
tensor 
evaluation；
多 
observable 
contraction。
每项应有明确的预算责任人。
建议将
已预留的受控工作额度
沿调用链传播，而不是每进入一层就重新申请完整额度。
同时不能因为已有 
reservation 
就跳过局部算子的类型、形状、分支和数学合法性检查。
8. 
max_diff
 
和真实导数阶数
8. max_diff 和真实导数阶数
按当前已验证的 
M1 
行为制定规则：
value：order 
0。
gradient/JVP/VJP：order 
1。
Hessian/HVP：order 
2。
外部 
nonlinear 
loss 
的二阶 
AD：只要求 
QNode 
原函数到二阶。
真正 
third-order 
请求：保持拒绝。
但还必须解决一个细节：
已经被 
TensorFlow 
trace 
的函数，其 
AD 
调用层数可能晚于 
QuantumBridge 
受控句柄创建。
所以受控句柄必须声明一个最高允许阶数及对应 
envelope：
Python
复制代码
运行代码
managed
 
=
 
compile_tensorflow
(
    
max_derivative_order
=
2
,
)
在这个 
envelope 
内，外部 
TensorFlow 
可以合法请求一阶或二阶；超出则按现有 
true-third 
guard 
拒绝。
若用户只批准 
order 
1，不能事后在同一图中无限升级到 
order 
2。
同时，不能因为两个嵌套 
TF 
AD 
容器就直接判定是三阶。
9. 
受控缓存图的资源合同边界
9. 受控缓存图的资源合同边界
这一点必须单独形成报告。
在 
eager 
CPU 
与受控同步调用中：
可以验证 
managed 
invocation 
的 
ledger 
reservation/commit。
可以验证静态 
workspace 
上界。
可以验证运行期参数断言。
可以验证已知的 
NativeHost/Device 
实际调用数。
不能承诺：
精确 
TensorFlow 
allocator 
字节数；
任意 
TF 
graph 
内部操作次数；
用户私有 
ConcreteFunction 
的执行次数；
任意外部 
loss 
的完整资源；
GPU/XLA 
异步完成及内存；
TensorFlow 
保留张量对象的实际生命周期。
如果某项保证无法实现，应以 
OUT_OF_SCOPE 
/ 
ESTIMATED_ONLY 
/ 
UNSUPPORTED
 
准确标注，而不是包装成功。
10. 
新增受控测试
10. 新增受控测试
建议新增或增强：
纯文本
复制代码
tests/interfaces/test_native_tf_derivative_request_contract.py


tests/interfaces/test_native_tf_managed_cached_execution.py


tests/interfaces/test_native_tf_managed_scope_lifecycle.py


tests/interfaces/test_native_tf_managed_concurrency.py


tests/interfaces/test_native_tf_budget_attribution.py
至少实现：
12 
个 
derivative 
request；
12 
个 
cached 
graph；
12 
个 
scope 
生命周期；
10 
个 
concurrency；
10 
个预算归属；
10 
个失败原子性与 
source 
mutation。
先红后绿，保留真实原始失败证据。
不扩大 
skip/xfail、不放宽数学容差、不把 
estimated 
memory 
计成实际 
allocator 
bytes。
11. 
M2 
的最终验收门槛
11. M2 的最终验收门槛
M2 
至少需要证明：
Eager 
shared-ledger 
路径继续全绿。
Managed 
cached 
graph 
每次受控调用真实计量。
Direct 
ConcreteFunction 
调用明确标记 
OUT_OF_SCOPE
。
ResourceScope 
/ 
unified_limits 
不被绕过。
order/method/direction/output 
预算正确。
Full 
Hessian 
与 
streamed 
HVP 
的限制分开。
Source/plan/cache 
identity 
合法。
错误、取消、并发的账本状态一致。
Runtime 
参数 
guard 
每次真实生效。
普通 
Gate 
原有 
parameter-shift/adjoint 
不回归。
M1 
十二条低量子位测试全部保持通过。
当前受支持域没有未修复的 
native 
correctness 
failure。
如果只能保证 
eager 
受控入口，而缓存图仍不能安全纳入管理，则准确标记 
M2 
PARTIAL
，不要进入 
M3。
12. 
完成 
M2 
后再启动 
M3
12. 完成 M2 后再启动 M3
按照 
Owner 
的顺序：
M1（已验证支持子集） 
→ 
M2（当前任务） 
→ 
M3（100-wire 
非稠密 
TensorFlow 
MPS）。
M3 
必须直接使用 
M2 
的统一资源描述和账本，不得另建 
TF 
scheduler。
原四条 
100-wire 
TF 
FoR/RoF 
红灯仍保留；M2 
完成前不得把它们当成已修复。
13. 
原 
R2 
全量门禁和本地限制
13. 原 R2 全量门禁和本地限制
完成 
M2 
后，先运行针对最新源码的开发期宽回归。
最终原 
R2 
门禁仍然包括三环境 
FULL、独立四框架、GLOBAL 
coverage、原始 
28-section 
matrix、所有数值示例、controlled 
legal、真实 
import 
origins、frozen/staged/commit 
equality。
Global 
coverage 
基线：
91.34108013033072%
Exclusions：
68，不增加
。
保留现有本地 
HEAD、历史提交和用户脏文件。不 
push/fetch，不修改 
OAuth/TLS，不安装依赖，不 
vendor，不新增夸父任务，不修改金融原始证据，不扩大 
Studio 
或应用案例。
只有规定的最终冻结及一致性验收完成后，才考虑 
normal 
scoped 
local 
commit。
下一步执行重点：用现有 
UnifiedResourceLedger 
实现明确受控的 
cached-graph 
调用句柄，同时关闭 
derivative 
request、full-Hessian/streamed-HVP、ResourceScope、缓存身份和并发账本的真实契约。
TensorFlow 
官方文档支持缓存图复用，但并不替 
QuantumBridge 
提供逐次 
Python 
账本记账；因此必须由受控调用入口承担它能够真实保证的部分，其余直接 
ConcreteFunction/任意外部图仍明确列为 
OUT_OF_SCOPE
。
本阶段即使通过，也不代表 
TF 
allocator 
全面受控，更不代表完整 
SDK 
替代完成。QuantumBridge 
full 
independent 
Qiskit/PennyLane 
replacement 
仍保持 
ACTIVE 
/ 
INCOMPLETE
。

