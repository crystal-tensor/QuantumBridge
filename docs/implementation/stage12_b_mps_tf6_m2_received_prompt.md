# Received TF6-M2 Unified Resource Contract Prompt

Actual complete reply read on2026-10-24 in the authorized existing default
Chrome conversation after transient disconnected partial output. No new tab
or login. Accessibility line splitting and table repetitions are preserved.
This is received next-step guidance, not independent review or acceptance.

QuantumBridge R2O3-B-TF6：M1 检查点审阅
结论：M1 可以认定为已通过本地专项测试的低量子位 TensorFlow Whole-QNode 支持子集。接下来严格按照 Owner 的顺序，先完成 M2 统一资源与导数阶数契约，再进入 M3 的 100-wire 非稠密 TensorFlow MPS。
根据你的报告，M1 不再只是独立局部算子测试：公开 
QNode.__call__
 已经进入现有 
ExecutionPlan.lowered()
，由 TensorFlow 张量计算真实线路和观测值，低量子位 FoR/RoF 也已通过。
验收项
当前实际结果
低量子位 Whole-QNode 原 12 条测试
12 passed
最终 M1 综合专项
Main / Alternate 各 107 passed
最后新增 selector、method、live-coefficient
Main / Alternate 各 8 passed
SDK-free admission
24 passed
100-wire 原四条 TF 红灯
4 failed，仍未修复
M1
低量子位支持子集成立
M2
PARTIAL
M3
INCOMPLETE
三环境 FULL / GLOBAL / 28-section matrix
NOT
_
RUN
R2 / P4 / 完整 SDK parity
ACTIVE / INCOMPLETE
验收项
低量子位 Whole-QNode 原 12 条测试
最终 M1 综合专项
最后新增 selector、method、live-coefficient
SDK-free admission
100-wire 原四条 TF 红灯
M1
M2
M3
三环境 FULL / GLOBAL / 28-section matrix
R2 / P4 / 完整 SDK parity
当前实际结果
12 passed
Main / Alternate 各 107 passed
Main / Alternate 各 8 passed
24 passed
4 failed，仍未修复
低量子位支持子集成立
PARTIAL
INCOMPLETE
NOT
_
RUN
ACTIVE / INCOMPLETE
验收项
当前实际结果
此前 Main/Alternate broad FOCUS 的 exit 1，原因仍是 M3 尚未实现的四条 100-wire 测试；不能改记为通过，也不能用 M1 的专项成功覆盖它们。
M2 最重要的架构判断
不要试图仅靠 Python 账本对 
tf.function
 的每一次 ConcreteFunction 执行收费式扣账。
TensorFlow 的 Python 代码可能只在 tracing 时运行，之后同一图会被重复执行；Python side effect 不会因此逐次重新执行。TensorFlow 官方对此有明确说明。
因此，M2 应当拆成三个具有不同保证范围的层次：
结构准入
：在编译或 trace 前核对整个已编译线路、导数方法、阶数、方向、输出和静态资源上限。
每次执行的张量校验
：对 NaN/Inf、分支切线、动态 shape、非法参数等使用真正随图执行的 TF assertions。
受控调用记账
：复用现有 
UnifiedResourceLedger
 对 QuantumBridge 明确管理的调用进行预留、提交和释放；不能声称 TensorFlow 任意外部 loss 图或真实 allocator/RSS 都受到这个账本的精确限制。
TensorFlow 的 
tf.function
 可以通过输入签名控制 ConcreteFunction 的形状和 dtype 专门化，而 
tf.debugging.assert_all_finite
 可在图运行时检查非法数值。
Codex 执行 Prompt：Stage 12-B P4-U3D2-R2O3-B-TF6-M2
Unified Derivative Admission, TensorFlow Graph Contracts & Shared Resource Ledger
继续原 R2O3-B-TF6，不创建新 SDK 阶段。
本批
仅完成 M2
。M2 实际验收后，才启动 M3 的非稠密 100-wire MPS 实现。
最终目标始终是 QuantumBridge 独立原生 Qiskit/PennyLane full functional parity/full replacement，保持 
ACTIVE / INCOMPLETE
。
1. 首先建立资源保证范围
审计现有：
ExecutionPlan
DerivativePlan
SecondWork
HigherOrderLimits
UnifiedResourceLedger
NativeHost
Device admission
tensorflow_whole_execution.py
tensorflow_native_derivatives.py
TensorFlowLocalOperator
QNode.__call__
不得创建第二个资源账本或调度器。
先制作一份明确的 M2 契约：
资源层
必须提供的保证
Static plan
所有 compiled operations、参数和 observables 经过准入
Derivative plan
方法、最高导数阶数、方向数和所需工作量经过准入
Tensor workspace
根据支持的 dtype、shape 和执行算法建立保守上界
Runtime parameters
每次 TF 图执行重新检查数值和分支合法性
NativeHost / Device
对确实调用的原生 Host/Device 工作使用现有账本
TensorFlow allocator
仅能报告预估量与有限观测，不能声称精确限制真实 RSS
External loss
不承诺任意用户 TensorFlow 图的资源由 QuantumBridge 全面控制
资源层
Static plan
Derivative plan
Tensor workspace
Runtime parameters
NativeHost / Device
TensorFlow allocator
External loss
必须提供的保证
所有 compiled operations、参数和 observables 经过准入
方法、最高导数阶数、方向数和所需工作量经过准入
根据支持的 dtype、shape 和执行算法建立保守上界
每次 TF 图执行重新检查数值和分支合法性
对确实调用的原生 Host/Device 工作使用现有账本
仅能报告预估量与有限观测，不能声称精确限制真实 RSS
不承诺任意用户 TensorFlow 图的资源由 QuantumBridge 全面控制
资源层
必须提供的保证
必须分别记录 
GUARANTEED_STATIC_BOUND
、
GRAPH_RUNTIME_VALIDATED
、
LEDGER_ACCOUNTED
、
ESTIMATED_ONLY
、
OUT_OF_SCOPE
。
不能把“资源估计”写成“实际 TensorFlow 内存限制已经实现”。
2. 第一组红灯：缓存 ConcreteFunction 后的非法参数
复用现有同一份真实 QNode 和编译计划。
测试顺序：
纯文本
复制代码
Valid parameters


    ↓


第一次 tf.function trace


    ↓


NaN


    ↓


Inf


    ↓


Branch-cut-invalid parameters


    ↓


Valid parameters again
必须满足：
合法输入有正确 expectation/Jacobian/HVP。
NaN/Inf 每次运行均拒绝。
不可靠的 branch-cut 输入每次运行均拒绝。
再次输入合法参数后，输出正确。
支持的静态形状不发生无意义 retrace。
trace_count
、每次执行的断言结果和预算状态均可审计。
失败不改变 Circuit、参数 owner、ExecutionPlan 或共享账本。
对于 TensorFlow 图，动态断言必须依赖真实运行输入，而不能只执行一次 Python 检查。
此外，断言的控制依赖必须确保其先于有风险的运算生效；不能先进行数值矩阵函数分配，再检查是否有 NaN。
3. 第二组红灯：实际统一资源准入
把当前 
tensorflow_statevector_work
 扩展为现有统一规划器的一种受支持工作量估算方式。
建议复用现有 
DerivativePlan
，增加可审计的工作描述，逻辑上包括：
纯文本
复制代码
compiled_plan_identity


execution_method


device_method


requested_derivative_order


trainable_parameter_count


output_count


direction_count


local_matrix_work


state_tensor_work


derivative_graph_work


temporary_workspace


host_work


device_work
具体字段服从现有代码结构。
必须明确：
TF Whole-QNode 是消费现有统一 DerivativePlan 的一个执行后端，不是再建一套 TensorFlow 特有的导数规划器。
验收要求：
完整验证线路及所有 operations。
确定 method 和导数阶数。
估算前向、反向及混合方向工作。
先执行现有统一 ledger 的资源 admission。
成功后构建 TensorFlow 执行图。
对动态图参数附加每次运行的断言。
对可直接观察的 NativeHost/Device 执行记录实际工作。
错误或取消后确保资源状态一致。
低预算情况下，必须在 
TensorFlowLocalOperator
、大张量构造和 Device 更新之前拒绝。
4. 明确 graph cache 与预算的生命周期
重点测试同一个 ConcreteFunction 的重复调用。
区分两种资源：
A. 编译/graph construction 工作：
 仅在实际构建新的受控图时消耗。
B. QNode 执行工作：
 每次受控 QNode 调用都可能产生，但不能靠 trace 时的 Python 副作用来计数。
建议让资源预留发生在 QuantumBridge 实际管理的 QNode 调用边界，而不是藏在 
tf.function
 函数体里的 Python callback 中。
但必须承认一个限制：
如果用户直接持有已经 trace 好的 TensorFlow ConcreteFunction，在 QuantumBridge Python 入口之外重复调用，现有 Python 账本不能保证每次实际 TensorFlow graph execution 都被重新扣账。
因此必须选择并验证一个明确契约：
对受控入口的每次调用实施 ledger reservation；
对缓存图的运行期参数执行 TF 原生断言；
对绕过受控入口的独立 ConcreteFunction 调用，只声明已实现的静态图上界及运行期断言；
不将未观测到的执行次数伪称为 NativeHost 实际工作次数。
不得通过在 TF 图内使用 Python side effects、
py_function
 或私有 hook 伪造逐次扣账。
5. 第三组红灯：
max_diff
 与 method 的正确语义
5. 第三组红灯：max_diff 与 method 的正确语义
保留现有 M1 已通过路径：
best
当前受支持的 
adjoint
静态 exact statevector
固定有限实数 Hamiltonian 系数
同时回归：
普通 Pauli rotation 继续原有 parameter-shift。
Moving-projector fractional power 不误选 parameter-shift。
backprop
 只有经过验证的原生 TF execution 路径才能支持。
未知导数 recipe 明确拒绝。
不支持的 trainable observable coefficient 不得静默常量化。
导数阶数测试
至少覆盖：
请求
M2 判定
Value
不需要量子导数
First gradient
一阶支持路径
Mixed Hessian
二阶支持路径
Streamed HVP
二阶方向支持路径
External nonlinear loss second derivative
按实际需要的 QNode 导数阶数判断
True third derivative
继续明确拒绝
max_diff=1
 请求不受支持的二阶量子导数
保留合法拒绝
max_diff=2
 当前 M1 合法二阶子域
实际执行通过
请求
Value
First gradient
Mixed Hessian
Streamed HVP
External nonlinear loss second derivative
True third derivative
max_diff=1
 请求不受支持的二阶量子导数
max_diff=2
 当前 M1 合法二阶子域
M2 判定
不需要量子导数
一阶支持路径
二阶支持路径
二阶方向支持路径
按实际需要的 QNode 导数阶数判断
继续明确拒绝
保留合法拒绝
实际执行通过
请求
M2 判定
不能以嵌套了几层 
GradientTape
 来判断 QuantumBridge 被请求的导数阶数。
同样，公开 PennyLane 的 
max_diff
 行为具有 differentiation-method 依赖性；你的双版本实际探针已经观察到部分运行模式返回 disconnected、非有限值或异常。QuantumBridge 应记录差异，不能仅凭参数名称相同就宣称完全 parity。
6. 多输出、方向及合并预算
针对原生两个 observables 的 QNode，分别测试：
一个输出；
两个输出；
nontrivial cotangent；
单个 HVP direction；
多个 directions；
零 direction；
多个方向请求的累计资源；
full Hessian；
streamed HVP。
完整 Hessian 和 streamed HVP 的预算必须分开。
对于 
𝑛
 个参数：
HVP 不得隐式分配完整 
𝑛
×
𝑛
 Hessian。
工作预算必须包含真正参与的方向和多输出收缩。
不得依靠没有被真正执行的 Host call 数量夸大实际资源。
方向生成器必须有界接纳。
保留之前 eight-parameter HVP：
max_hessian_elements=1
并 patch 完整 Hessian 入口为失败，确认 directional HVP 仍可运行。
7. 资源账本的正确原子语义
需要验证：
reservation 失败前没有危险执行；
编译中途失败不会留下不一致的持久预留；
同一 ledger 中多个 concurrent QNode 调用不会超卖；
retrace 和缓存命中不会重复计入 graph-construction 工作；
NativeHost/Device 的同一物理执行不被两次计量；
aborted execution 不会被记录为成功完成；
错误后的账本仍能支持合法后续调用；
更换 source owner 或执行计划会触发新的合法准入，而不是使用旧图继续执行。
必须审计现有 ledger 是否真正支持并发 reservation/commit/rollback。如果不支持，不允许只依靠普通字典读写宣称原子并发正确。
对可恢复、可撤销的工作使用既有生命周期管理；对已经实际消耗的工作，不能因为失败就错误地回滚为未执行。
特别增加一条身份测试
对于同一参数输入，如果执行计划、observables、method 或 
max_diff
 发生变化，旧的缓存图不能自动代表新的配置。
缓存身份至少应覆盖所有影响数学语义及资源约束的实际字段，或者在每次调用时重新验证它们。
8. ResourceScope 与 unified_limits
你已明确报告：
node.unified_limits
 在 M1 路径中仍 Unsupported；
active ResourceScope 在 M1 路径中仍 Unsupported。
本批必须优先分析现有公开原生接口的实际支持范围，而不是简单删去拒绝分支。
如果现有统一 ledger 提供安全 scoped admission，就让 TF Whole-QNode 消费同一个 scope。
需要验证：
scope 内和 scope 外；
nested scope；
tight aggregate limits；
多个 QNode 共享 scope；
一个 QNode 多次调用；
graph cache 重用；
scope 退出；
不合法资源上限；
host/device 账本复用。
如果确实无法安全连接，仍保持明确 Unsupported，不能用一个独立 TF 私有 scope 冒充统一资源接口。
M2 不能在 active scope 仍可能被绕过的情况下宣称完整。
9. TensorFlow 动态检查与数学保护
保持 M1 正确的：
float64/complex128；
Parameter UUID/vector；
local matrix phase；
coherent open controls；
moving-projector fractional power；
多输出 observables。
验证每次运行期：
NaN/Inf；
branch cut；
denominator/spectral pole；
input shape；
允许的 dtype；
trainable coefficient scope；
active parameter count。
对于固定静态 shape，可以在构图前检查。对于运行时数值，必须有真正的 TF 图断言。
不能根据 TensorFlow allocator 的实际内存使用推断完整操作数值正确，也不能以估计 workspace 成功代替 branch validity。
10. 新增受控测试
建议增加或增强：
纯文本
复制代码
tests/interfaces/test_native_tf_unified_derivative_plan.py


tests/interfaces/test_native_tf_whole_qnode_ledger.py


tests/interfaces/test_native_tf_concrete_cache.py


tests/interfaces/test_native_tf_runtime_admission.py


tests/interfaces/test_native_tf_resource_scope.py


tests/interfaces/test_native_tf_method_order_contracts.py
至少覆盖：
12 个 ExecutionPlan/DerivativePlan 一致性场景；
12 个 graph-cache/runtime 参数场景；
10 个 
max_diff
/method 场景；
10 个 multi-output/direction 场景；
12 个 ledger reservation/rollback/concurrency 场景；
10 个 active scope/unified_limits 场景；
12 个资源不足与失败原子性反例。
这些属于独立场景目标，不是已完成 SDK 函数数量。
先实际红灯，再修改生产代码。不得扩大 skip/xfail、放宽数学容差或静默改用旧 NumPy callback。
11. M2 正式验收要求
只有以下条件均通过，才能将 M2 记为本地支持子集通过：
M1 真实 12 条低量子位红灯持续全绿。
所有 supported Whole-QNode operations 在执行前完成能力检查。
导数 method、order、direction 与资源计划一致。
受控 QNode 调用正确使用现有 UnifiedResourceLedger。
Cached ConcreteFunction 不导致静态资源合同失效。
每次运行的非法参数都被 TF 断言拒绝。
ResourceScope 和 unified_limits 的声称支持范围真实有效。
多输出、HVP 和外部 nonlinear loss 计算正确。
没有误用 full Hessian 或 NumPy quantum callback。
普通 Gate 既有 shift/adjoint 资源契约不回归。
全部最新 M2 专项和受影响开发期宽回归通过。
如果仍存在明确 Unsupported，应准确标记为 
M2 PARTIAL
，不能仅凭全绿局部测试关闭 M2。
12. M2 完成后再进入 M3
不要在 M2 没有完整支持合同前，把 100-wire TF MPS 接入新的 TensorFlow tensor-network 代码。
M3 的下一阶段应该以已经验证的同一份资源契约为前提，新增：
MPS tensor-chain workspace；
maximum bond；
局部 contraction；
wire routing；
二阶自动微分图；
截断策略；
no-dense guarantees；
原四条 100-wire FoR/RoF 正式红灯。
M3 不允许创建单独的资源账本；必须直接使用 M2 的统一规划与准入机制。
若 M2 未完全通过，先修复 M2，再开展 M3。
13. 最终开发回归与原 R2 门禁
M2 功能完成后，先运行最新源码：
Core/Circuit；
Compiler；
Serialization；
Information；
Gradients/QML；
DerivativeExecution；
Interfaces；
Devices/Noise；
H₂；
SDK-free 数值示例；
两版公开差分。
原四条 100-wire TF 红灯在 M3 之前可能继续失败，必须原样保留并准确记录，不能将其纳入 M2 成功数。
原 R2 的最终冻结门禁全部保留：
SDK-free FULL；
Main FULL；
Alternate FULL；
Independent JAX FOCUS；
Independent TF FOCUS；
Torch/Autograd FOCUS；
显式 GLOBAL coverage；
原始未修改的 28-section matrix；
全部 SDK-free examples；
controlled legal；
no-token/no-vendor；
五个实际 import origins；
frozen/worktree/staged/commit runtime equality。
GLOBAL line coverage 基线：
91.34108013033072%
Exclusions：
68，不增加
。
不能使用 M1/M2 的局部 FOCUS 替代最终 FULL。
14. Git、安全与最终报告
继续 Owner 的本地开发权限：
不 push/fetch，不更改 OAuth/TLS；
不安装依赖、不 vendor 上游源码；
不新增夸父真机任务；
不修改金融 13 项原始硬件证据；
不扩大 UI/Studio；
不重写历史；
不修改既有 Router 来源问题。
只有按原 R2 要求完成最终冻结与一致性验收，才进行 normal scoped 本地提交；在此之前保持当前未提交的真实开发状态。
最终报告必须说明：
M2 是否真的使用同一套 ExecutionPlan、DerivativePlan、SecondWork 和 UnifiedResourceLedger。
tf.function
 tracing 与执行的预算边界。
每次运行时断言的真实结果。
Scope、unified_limits 和多个 QNode 共享账本的真实行为。
导数方法与 
max_diff
 的执行规则。
多输出/HVP 资源是否正确累计。
资源不足是否能在危险执行前拒绝。
哪些只是 workspace 估计，哪些确实由账本计量。
M1 回归与 M3 四条红灯的真实状态。
三环境 FULL/GLOBAL/matrix 是否执行。
本地提交、远端 CI 和剩余 SDK 功能缺口。
下一步明确为：M2 统一资源与导数阶数准入，而不是立刻编写 100-wire TensorFlow MPS。
只有 M2 把“编译计划 → 方法与导数阶数 → 资源预留 → TensorFlow 图 → 每次运行检查 → 可核查的账本”真正连接起来，M3 的非稠密执行才有可靠的工程基础。
完整独立 Qiskit/PennyLane full functional parity/full replacement 始终为 
ACTIVE / INCOMPLETE
。

