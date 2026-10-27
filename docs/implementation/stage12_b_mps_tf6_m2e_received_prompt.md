# Received TF6-M2E Capability Isolation And Readiness Prompt

Full response actually read on2026-10-24 in the authorized existing
ChatGPT conversation in default Chrome. No new tab/login. Accessibility
line splitting is preserved. This is guidance based on our reported results,
not independent inspection of source/remote CI and not M2/full SDK acceptance.

QuantumBridge TF6-M2D：NATIVE-INLINE-110 检查点审阅
结论：D1/D2/D3 的低量子位 Trace-inline 原生集成有真实测试支持，可以作为 M2 的开发期支持子集。但 M2 仍为 
PARTIAL
，M3 尚不能启动。
本次最重要的架构成果是：
QNode.compile_tensorflow_inline()
 不再依赖 cached 
self._pack
 或运行时重新构造 Circuit，而是复用现有编译计划、冻结参数 AST 和 TensorFlow 局部算子，在调用者的可微图中生成计算。
项目
实际报告结果
Main / Alternate 最新 inline + ledger
各 
110 passed
其中新增测试
49 项，包含在 110 项内
SDK-free 原生专项
348 passed
旧路径保护回归
各 147 passed / 
2 failed
Cached callable RoF
仍有 2 条正式红灯
100-wire 原四条 TF 测试
4 failed
M2
PARTIAL
M3
NOT
_
STARTED
R2 FULL / GLOBAL / 原始 matrix
NOT
_
RUN
项目
Main / Alternate 最新 inline + ledger
其中新增测试
SDK-free 原生专项
旧路径保护回归
Cached callable RoF
100-wire 原四条 TF 测试
M2
M3
R2 FULL / GLOBAL / 原始 matrix
实际报告结果
各 
110 passed
49 项，包含在 110 项内
348 passed
各 147 passed / 
2 failed
仍有 2 条正式红灯
4 failed
PARTIAL
NOT
_
STARTED
NOT
_
RUN
项目
实际报告结果
尚需关闭的 M2 合同
1. Cached callable 应从正式可承诺的二阶 AD 能力中隔离。
建议把以下三种模式明确区分：
MANAGED_EXPLICIT_QUERY
：通过 QuantumBridge 管理的入口执行显式 value/JVP/VJP/HVP/Hessian，并按照已验证范围使用共享账本。
TRACE_INLINE_DIFFERENTIABLE
：在同一个外层 AD/tracing 过程中直接生成 TF 运算，支持已验证的低量子位微分，但
不承诺缓存外层图每次执行都有 Python 账本扣账
。
EXPERIMENTAL_CACHED_CALLABLE
：保留供开发诊断，但当前外部 nonlinear loss RoF 仍可能失败，不能宣称二阶支持。
我的建议是：
从受支持功能发现、默认方法选择和兼容性统计中排除第三种模式的二阶能力，而不是删除实验代码或将失败测试改成 xfail。
还应明确：即使实验模式在部分调用下已经返回错误有限结果，也不能只依靠一个能力标签就宣称所有用户调用都会被安全拒绝。必须测试公开入口能够识别并拒绝的场景，并如实登记无法识别的外部 TF 图调用。
2. Trace-inline 的数学快照与实时资源限制应分开处理。
你目前实现了数学计划 snapshot、Python 入口 live owner guard，这是合理的设计。
但 
tf.function
 缓存后从外部直接执行时，不会自动再次经过 Python owner guard。对此只能承诺创建图时的结构上界和每次执行的 TF 数值断言。
如果在资源上限收紧后仍允许旧缓存图继续运行，就不能把该执行称为最新资源限制下的 
LEDGER_ACCOUNTED
。
3. Method、order 和资源合同尚需做完整组合验收。
尤其需要区分：
普通旋转门既有的 parameter-shift / adjoint；
moving-projector 分数幂的已验证低量子位路径；
受控显式 HVP 与完整 Hessian；
eager inline 与外部 traced inline；
不支持的 trainable observable coefficients、dynamic operations 和一般矩阵函数；
max_diff=1/2
 与真正三阶请求。
4. 性能是明确的待处理项，但不能通过改变数学路径来换取速度。
110 项综合测试耗时超过 700 秒，其中复杂 4q 二阶图是实际成本。建议下一段先对时间、trace count、张量工作空间做测量，再优化重复的静态表达式处理；不得缓存带特定参数数值的数学结果。
以上判断仅基于你的本地报告。我没有独立检查未提交源码或远端 CI。
下一段 Codex 执行 Prompt：Stage 12-B P4-U3D2-R2O3-B-TF6-M2E
Cached Callable Capability Isolation, Derivative Contracts & M2 Final Readiness
继续原 TF6-M2D，不创建新 SDK 阶段。
本批只完成 M2 的剩余能力隔离、方法/资源验收与性能验证；未经 M2 验收，不进入 M3。
完整独立原生 Qiskit/PennyLane full functional parity/full replacement 始终保持 
ACTIVE / INCOMPLETE
。
1. 第一优先：隔离仍有错误的 Cached Callable
这是本批首要任务。
当前 
ManagedTensorFlowQNode
 至少涉及三种不同的能力：
能力
应声明的状态
Managed explicit value/JVP/VJP/HVP/Hessian
已有受支持子集专项测试
Trace-inline low-qubit differentiable QNode
已有受支持子集专项测试
Experimental cached callable + external nonlinear RoF
UNRESOLVED，不得宣传二阶支持
能力
Managed explicit value/JVP/VJP/HVP/Hessian
Trace-inline low-qubit differentiable QNode
Experimental cached callable + external nonlinear RoF
应声明的状态
已有受支持子集专项测试
UNRESOLVED，不得宣传二阶支持
能力
应声明的状态
需要实现或补齐一个
只读、结构化的能力描述
，复用现有 method/capability 系统，不另建全局注册表。
建议语义字段：
纯文本
复制代码
execution_mode


supported_derivative_methods


maximum_verified_quantum_derivative_order


external_mixed_ad_contract


resource_accounting_scope


graph_cache_contract


unsupported_reason
这些是逻辑字段，不要求创建新的类。
必须先运行两条正式 cached RoF 红灯，确认仍是真实失败。
随后验证：
实验 cached callable 不被 
best
 自动选为二阶 AD 路径；
显式 value/HVP 查询继续可用；
Trace-inline 继续支持已验证的 FoR/RoF；
用户显式请求未支持的 cached callable 二阶合同，能够在
可识别的受控入口
提前收到 typed refusal；
直接在外部 cached ConcreteFunction 上追加 AD 的情形，如无法事先识别，明确 
UNGUARANTEED_EXTERNAL_AD
；
不得因为添加 capability label，就把实际上仍可能返回错误有限值的调用宣传为安全。
不要删除或修改原有两条红灯的数学断言。
 可以新增专门的安全拒绝测试，但须与原测试分别统计。
2. 能力选择器与方法隔离
审计：
QNode TensorFlow interface dispatch；
best
；
adjoint
；
parameter-shift
；
backprop
；
Managed cached query；
Trace-inline；
max_diff
。
要求：
普通 Pauli rotation 的现有 shift 计划不变。
Moving-projector 的合法 low-qubit TensorFlow 路径使用现有已验证计划。
不支持的 general matrix-function 不得误入 TF inline。
max_diff=1
 的二阶拒绝继续有效。
max_diff=2
 对已验证低量子位子域允许二阶。
第三阶明确拒绝。
实验 cached callable 不影响默认 QNode 的方法选择。
不支持的 trainable Hamiltonian coefficients 不能被静态化后假装成功。
尤其需要做一组默认模式对照：引入新 capability 后，原默认 QNode 的 return type、导数方法、工作预算和异常行为均不变化。
3. 受控句柄的数学快照与资源所有权
保留当前 FrozenParameterBinding、owned storage snapshot 与 live owner resource guard。
本批重点补齐：
源 Circuit 修改；
source Gate definition 修改；
ParameterVector shrink/regrow；
observable 修改；
method/max_diff 改变；
resource limits 收紧；
scope 退出；
新 active scope；
handle copy；
同一 handle 多次调用；
多 handle 并发。
对可识别的 Python 受控入口，继续真实检查 live owner 和资源配置。
对外部缓存 TF 图，不能声称 Python guard 每次重新执行。TensorFlow 官方明确说明，
tf.function
 缓存图的重新执行不等于重新运行 tracing 时的 Python 代码。
因此必须准确报告：
SNAPSHOT_MATH
;
LIVE_GUARD_AT_CONTROLLED_ENTRY
;
RUNTIME_TF_ASSERTIONS
;
EXTERNAL_CACHED_GRAPH_OUT_OF_SCOPE
.
不要将四者合并为“完全受控”。
4. 请求级数学与账本闭环
对受控显式查询，逐项检查：
value；
gradient；
JVP；
VJP；
单方向 HVP；
多方向 HVP；
full Hessian；
多输出及 cotangent 加权。
至少测试：
纯文本
复制代码
value → gradient → HVP → value
以及：
纯文本
复制代码
valid → invalid → valid
要求：
数学输出仍正确；
max_hessian_elements
 对完整 Hessian 生效；
streamed HVP 不构造完整 Hessian；
多方向资源累计正确；
原有 
UnifiedResourceLedger
 不超卖；
scope/child ledger 不重复计量；
已尝试工作不会在异常后被错误回滚；
physical shots、NativeHost calls、Device updates 不虚报；
cache 命中不重复扣 graph-construction 预算。
外部任意 nonlinear loss 的 TensorFlow 图工作量继续标记 
OUT_OF_SCOPE
，不能假装已经完全计入账本。
5. Trace-inline 性能与保真审计
本轮 110 项测试耗时较高，但不能只凭整体耗时推断瓶颈。
先针对相同冻结计划收集：
handle 创建时间；
外层首次 trace 时间；
后续缓存执行时间；
eager 执行时间；
FoR/RoF/TapeTape 时间；
GraphDef 节点数量；
TensorFlow FunctionDef 数量；
可观察峰值 workspace；
trace count；
retained output 生命周期中可观测的资源。
至少选择：
一量子位非对易 moving-projector；
两输出；
四量子位 entangling；
八参数 streamed HVP。
性能优化只允许针对已确认的重复静态工作，例如不可变 AST/operation 描述的只读缓存。
不得缓存输入相关的 TF 数值张量，也不得把训练参数转为 NumPy 常量。
不得仅为提速切换到旧的 host callback 或 cached-inner 路径。
6. 保留 M1 的数学正确性
所有修改必须回归：
低量子位 M1 原 12 条；
M2D 当前 110 项；
两个独立高精度参数点；
两个 nonlinear losses；
JVP/VJP；
mixed Hessian；
streamed HVP；
IR/QPY；
coherent control/global phase；
ParameterVector/UUID；
runtime NaN/Inf/cut；
旧 ordinary Gate shift/adjoint。
特别验证 trace-inline 并没有引入新的内层缓存函数边界，使 RoF 重新丢失 Hessian 项。
TensorFlow 的公开 
tf.custom_gradient
 文档也明确指出，嵌套自定义梯度的回调并不自动对应输入的二阶导数。因此本批不应再把实验 cached callable 的不完整回调包装成生产二阶支持。
7. M2 当前支持子集的验收条件
在本批结束时，至少应该能够准确回答：
A. Managed explicit cached queries
哪些方法数学正确、受账本管理、支持并发及资源收紧？
B. Trace-inline differentiable QNode
哪些低量子位线路、导数方法、二阶外部 loss 可以正确执行？其图执行是否处于 Python 账本外？
C. Experimental cached callable
两个 RoF 红灯是否依然存在？是否已从默认成功路径及二阶 capability 中隔离？哪些受控入口可安全拒绝，哪些外部 AD 调用无法拦截？
D. Resource guarantees
哪些是静态界限，哪些是每次运行的 TF 数值断言，哪些是真正账本记录，哪些仅是估计？
只有这些范围都经过真实测试，才可以考虑给 M2 一个
明确限定的受支持子集检查点
。这不能被解释为整个 TensorFlow interface、M2 全域或完整 SDK 已完成。
如果现有公开二阶 callable 仍可能在被声明支持的模式下返回错误有限值，M2 继续 
PARTIAL
。
8. 本批开发门禁
先运行最新源码：
M1 Whole-QNode；
M2B managed ledger；
M2D inline；
TF mixed AD；
ResourceScope/concurrency；
Compiler/IR/QPY；
TensorFlow/Autograd/JAX/Torch 相关回归；
SDK-free admission 与数值示例。
明确分列：
成功的 M2 专项；
两个 cached callable RoF 正式失败；
四个 M3 100-wire 正式失败；
其他真实 native correctness failure。
不能把已知正式红灯从测试集合中移除后，称整个 TensorFlow interface 已验收。
9. M2 与 M3 的交接条件
Owner 顺序仍是：
M1 → M2 → M3。
M2 可以交接给 M3 的条件应是：
共享资源账本与作用域合同经过验证；
数学快照、方法、阶数及计划身份不发生静默漂移；
受控缓存执行的合同明确且正确；
trace-inline 的非账本执行边界明确；
旧 cached callable 不再被任何受支持二阶能力声明错误覆盖；
无新增未修复 native correctness failure；
M2 最新代码的必要开发回归已完成。
只满足以上受支持子集条件，也应写作 
M2_SUPPORTED_SUBSET_ACCEPTED / FULL_M2_INCOMPLETE
，而不是无限定的 
M2_DONE
。
如果 Owner 的 M2 完成门槛要求所有 TensorFlow callable 二阶路径都通过，则当前两个 cached RoF 红灯仍是阻断，不能进入 M3。
10. 原 R2 完整冻结门禁不变
后续仍必须执行：
SDK-free FULL；
Main FULL；
Alternate FULL；
独立四框架；
GLOBAL line coverage ≥ 
91.34108013033072%
；
exclusions 
68
 不增加；
原始未修改的 28-section matrix；
所有 SDK-free 数值示例；
controlled legal；
五个实际 import origins；
frozen/worktree/staged/commit runtime equality。
当前这些门禁均不能因 110 项专项测试通过而视为完成。
11. Git 与最终报告
保持 owner local-only：
不 stage/commit，除非达到既定冻结与 scoped 提交条件；
不 push/fetch；
不改 OAuth/TLS；
不安装依赖、不 vendor；
不新增夸父任务；
不修改金融历史证据；
不扩大 UI/Studio；
不碰 Router 来源文件或重写历史。
最终报告必须说明：
Cached callable 二阶能力的隔离是否生效。
Managed explicit 与 trace-inline 的真实功能边界。
是否仍存在可能返回错误有限值的公开受支持路径。
同步 ledger 与外部缓存 TF 图的不同保证范围。
方法、阶数和 
max_diff
 兼容差异。
资源、并发、owner mutation、scope 的真实测试。
性能诊断与是否发生可验证优化。
两个 cached RoF 和四个 M3 红灯的真实状态。
三环境 FULL/GLOBAL/matrix 的实际状态。
尚未实现的完整 SDK 核心能力。
下一步最具体的任务：先把实验 cached callable 的二阶能力从默认成功路径和公开能力声明中隔离，再完成请求级账本、live owner/scope 与 trace-inline 性能闭环。
这样可以避免将已知错误有限输出暴露为受支持二阶 API，同时保留现有 managed explicit queries 与 trace-inline 的真实成果。
M2 仍为 
PARTIAL
，M3 仍为 
NOT_STARTED
。完整独立 Qiskit/PennyLane full functional parity/full replacement 继续为 
ACTIVE / INCOMPLETE
。
