# Received R2O3-B-TF6 Whole-QNode Integration Prompt

Actual completed reply read on2026-10-24 in the owner's authorized existing
default Chrome conversation. Its completed turn was verified before reading
the complete response, after transient partial/disconnected UI output.
No new tab or login. Accessibility line splitting is preserved. This is
received next-step guidance, not implementation or independent CI evidence.

QuantumBridge TF5：开发检查点审阅
结论：TF5 已完成真实编译计划下的局部可微算子接入，但尚未完成 Whole-QNode 执行。下一步必须把重点从 
TensorFlowLocalOperator
 转移到公开 
QNode.__call__
、整条线路的资源规划与 TensorFlow 执行。
本轮没有从报告中发现需要撤销新局部算子实现的已证实数学缺陷，但存在两个尚未关闭的集成阻断。
检查项
报告中的实际结果
新原生 TF LocalOperator 测试
269 passed
纯 TF 数学基线
272 passed
Main 综合 FOCUS
577 passed / 
12 failed
，exit 1
低量子位公开 QNode
4 passed / 8 failed
100-wire 公开 MPS
32 passed / 4 failed
失败入口
tensorflow_graph.py:44
整体 QNode 资源规划
尚未完成
三环境 FULL / GLOBAL / 28-section matrix
NOT
_
RUN
完整 SDK 替代
ACTIVE / INCOMPLETE
检查项
新原生 TF LocalOperator 测试
纯 TF 数学基线
Main 综合 FOCUS
低量子位公开 QNode
100-wire 公开 MPS
失败入口
整体 QNode 资源规划
三环境 FULL / GLOBAL / 28-section matrix
完整 SDK 替代
报告中的实际结果
269 passed
272 passed
577 passed / 
12 failed
，exit 1
4 passed / 8 failed
32 passed / 4 failed
tensorflow_graph.py:44
尚未完成
NOT
_
RUN
ACTIVE / INCOMPLETE
检查项
报告中的实际结果
TensorFlowLocalOperator(plan, compiled_operation_index)
 直接读取现有 
ExecutionPlan.lowered()
，通过 occurrence UUID 恢复符号参数，并使用已验证的 TF 数学公式，这是正确的架构选择。
但目前它仍是
单个 compiled operation 的执行器
，尚不是支持整条 Circuit、observables、参数绑定和设备预算的可微 QNode。
三个需要优先解决的问题
1. Whole-QNode 的执行语义。
 不能只让 QNode 内某一个 Gate 使用 TF local kernel，而其余操作依赖另一套独立状态或旧 NumPy callback。必须保证所有影响可训练输出的操作都能在同一个 TF 可微图中执行，或在规划阶段明确拒绝。
2. 完整资源预算。
 现在只证明了局部 kernel 的 preflight，没有证明整条线路、多输出、二阶图、MPS tensor storage 和 repeated execution 都在统一预算内。
3. 导数阶数和方法选择。
 PennyLane 公共 
max_diff
 语义与 differentiation method 有关，不能机械地按嵌套 
GradientTape
 数量推断导数阶数。TensorFlow 
backprop
、设备提供的导数和 parameter-shift 又是不同的执行路径，必须分别处理。
本次判断仅依据你提交的本地测试报告。我没有独立检查未提交源码或远端 CI。
下一段 Codex 执行 Prompt：Stage 12-B P4-U3D2-R2O3-B-TF6
Native Whole-QNode TensorFlow Execution, Shared Resource Planning & Non-Dense MPS Integration
继续现有 R2O3-B-TF5 及原始 R2。不得将本任务视为新 SDK 阶段。
最高目标始终是 QuantumBridge 独立原生实现 Qiskit/PennyLane full functional parity/full replacement：
ACTIVE / INCOMPLETE
。
本批实施顺序必须是：
Whole-QNode 低量子位执行 → 统一资源与导数阶数规划 → 真实公开 TF 混合微分 → 100-wire 非稠密 MPS → 最终联合回归。
不继续单独扩充 LocalOperator 的数学测试数量，除非 Whole-QNode 真实失败证明局部内核存在缺陷。
1. 先锁定 12 条现有正式红灯
保留当前 Main 的真实结果：
8 条低量子位 QNode FoR/RoF 失败；
4 条 100-wire MPS FoR/RoF 失败；
其余 577 条通过。
先独立复现这 12 条失败，并记录调用栈。
必须检查首次进入：
纯文本
复制代码
QNode.__call__


→ TensorFlow interface dispatch


→ Native ExecutionPlan


→ tensorflow_graph.py


→ tensorflow_autodiff.py


→ Device / NativeHost
的位置。
目标是证明失败确实由旧的 
order2
 graph callback 路径触发，而不是 
TensorFlowLocalOperator
 的数学错误。
保留 
tensorflow_graph.py:44
 的现有 typed refusal；新路径通过完整验证后，才允许针对精确受支持情况绕过旧路径。
不要删除或放宽旧 refusal，使未知输入落入错误有限结果。
2. Whole-QNode 必须复用唯一原生编译计划
先审计现有：
QNode；
Compiler；
ExecutionPlan.lowered()
；
compiled parameter occurrence records；
DerivativePlan
；
SecondWork
；
NativeHost
；
Device；
TensorFlowLocalOperator。
建议新增一个严格受控的内部执行入口，逻辑上相当于：
Python
复制代码
运行代码
execute_tf_compiled_qnode
(
    
plan
,
    
trainable_parameters
,
    
observables
,
    
execution_config
,
)
实际函数名由现有架构决定，不要求新建第二个 scheduler。
此函数只能消费已验证的原生执行计划。
不得重新解析 QASM 构造另一条线路，不得创建第二个 Circuit store、Gate registry、UUID 系统或 Compiler。
首条架构红灯
对同一 QNode，验证：
纯文本
复制代码
Native Circuit


→ Native Compiler


→ ExecutionPlan.lowered()


→ TensorFlow Whole-QNode
实际执行的操作顺序、wire、Parameter UUID、modifier 和 global phase，与原有 Statevector/Fréchet 路径一致。
对 compiled plan 中任意操作的删除、重排、非法 wire 或参数错配，必须产生对应的失败或数学变化，不能让 TF 执行仍使用一条独立硬编码线路。
3. 先实现 1–4 qubit Whole-QNode
本段第一阶段允许小规模 dense TF state tensor，但必须是真正的 Whole-QNode。
从现有计划执行完整流程：
初始化合法的 TF complex128 quantum state。
遍历所有 lowered operations。
对已验证的 
native_matrix_power
 occurrence 调用 
TensorFlowLocalOperator
。
对其他受支持 primitive 使用现有公开语义对应的 TF 局部运算。
保留真实 wire ordering 和 global phase。
计算 QNode observable。
返回真正依赖 trainable TF tensors 的输出。
必须支持至少：
RX/RY/RZ；
H、X、Y、Z；
CX；
可表示的 local composite；
moving-projector fractional power；
inverse；
open/closed controls；
两个 observables；
ParameterVector；
partial binding；
noncontiguous wires。
重要限制：固定 primitive 的 TF 运算实现应复用已存在的 Gate 语义及经过验证的局部数学构造，不以名称猜测自定义 Gate definition。
首个必须完成的闭环
Python
复制代码
运行代码
p
 
=
 
Parameter
(
"p"
)
q
 
=
 
Parameter
(
"q"
)
body
 
=
 
Circuit
(
1
)
body
.
ry(
-
p
, 
0
)
body
.
rz(
q
*
q
 
+
 
0.4
, 
0
)
body
.
rx(
p
, 
0
)
power_gate
 
=
 
body
.
to_gate()
.
power(
0.5
, 
annotated
=
True
)
qc
 
=
 
QuantumCircuit
(
2
)
qc
.
append(
power_gate
, [
1
])
从这个实际原生 Circuit 构建 QNode，通过 TensorFlow 公共接口执行，并比较：
完整复数 state；
expectation；
Jacobian；
mixed Hessian；
directional HVP；
JVP；
VJP。
必须与独立 SU(2) oracle 及既有 Native Statevector 的合法计算一致。
不能只比较 TF local gate 的矩阵。
4. 整体受支持性检查：不得部分降级
Whole-QNode 在进入 TF 执行前，必须对所有 lowered operations 做完整 preflight。
建议为当前支持子域生成不可变的执行能力描述：
纯文本
复制代码
all operations TF-compatible


all measurements supported


all trainable expressions traceable


all wire mappings valid


all branch guards available


all resources admitted
仅当整条 QNode 都满足条件时，才选择 TensorFlow-native execution。
如果某一步操作无法在 TF 图中合法执行：
不得将可训练参数转换为 NumPy；
不得部分执行 TF、部分执行未知梯度的 host callback；
不得把不支持的非酉动态行为当酉门；
不得静默改为 Statevector；
必须在执行前明确拒绝，或按经过验证的既有旧路径处理它确实支持的其他方法。
best
 方法不得为了通过 TF 测试而改变普通 Pauli rotation 的已验证 parameter-shift/资源契约。
5. 统一导数阶数，不按 callback 层数猜测
必须明确区分：
原生函数 value；
first JVP/VJP；
second Hessian/HVP；
真正 third derivative。
对于用户请求：
纯文本
复制代码
loss( QNode(theta) )
TensorFlow 对外部 loss 的二阶求导不等于原生 QNode 被请求三阶。
max_diff
 应依据原始 QNode 实际所需的导数阶数和所选计算策略判断，而不是按碰到 
order2
 callback 就拒绝。
实施要求：
max_diff=1
 对明确的二阶 QNode 请求保持既有合法拒绝；
max_diff=2
 支持当前已验证的二阶子域；
真正第三阶请求继续拒绝；
外部非线性 loss 的 TF AD 不得错误增加 QNode 导数阶数；
method=
best
、
backprop
、
adjoint
、
parameter-shift
 分别按实际原生支持能力规划。
对公开 PennyLane 的差异另作两版本观测，不能把 QuantumBridge 内部 
max_diff
 规则直接宣称完全兼容。
6. 图级资源预算必须先于 TF 运算
扩展现有 
ExecutionPlan/DerivativePlan/SecondWork/NativeHost/Device
 的统一 admission。
不要创建独立 TF 全局预算表。
规划至少包含：
operations 总数；
compiled wires；
trainable parameters；
requested differentiation order；
observable 数量；
方向数量；
local matrix workspace；
TF state tensor workspace；
tape/forward graph 保存的张量；
forward/reverse/mixed AD 的额外工作量；
tracing/retracing 边界；
MPS bond/tangent components；
host calls / shots。
建议执行流程：
纯文本
复制代码
Validate native plan


→ Validate TF support


→ Determine derivative order/method


→ Estimate complete workspace/work


→ Reserve through existing budget


→ Build TF tensor execution


→ Contract observables


→ Return differentiable result
不得先构造 tensor，再用异常补做预算检查。
必须新增一个资源红灯
将完整计划预算设得低于预计工作量，并 patch 以下执行入口为抛错：
TensorFlow 危险张量分配；
TensorFlowLocalOperator.__call__
；
Device update。
正确实现应在调用这些入口之前拒绝。
另外测试同一 
tf.function
 graph 首次 trace 与后续不同参数运行，确保不能利用 trace 缓存绕过动态 shape、branch 或有限性校验。
需要区分一次性结构 admission 和每次运行时参数 admission。不得声称 Python 侧预算检查已经精确限制 TensorFlow allocator 的真实 RSS；必须报告估计预算与实际可观测内存之间的证据范围。
7. 真正让低量子位 TF 四条对应红灯变绿
对真实 Whole-QNode，而不是纯 TensorFlow fixture，运行：
squared loss FoR；
squared loss RoF；
exponential/cubic loss FoR；
exponential/cubic loss RoF；
Tape-over-Tape；
JVP/VJP；
mixed Hessian；
两输出、非平凡 cotangent。
在 eager 与：
Python
复制代码
运行代码
tf
.
function(
autograph
=
False
, 
jit_compile
=
False
)
下分别验证。
trainable matrix 和相位不得跨不可微 host callback 边界。
必须证明外部 loss 的二阶完整链式贡献由 TF 真正自动微分得到，而不是专门注入该 loss 的 HVP。
此阶段若通过，只能记录：
LOW_QUBIT_TF_WHOLE_QNODE_SUPPORTED_SUBSET
不能把原 100-wire 四条正式测试标记为通过。
8. 第二阶段：100-wire TF tensor-network 执行
低量子位完成后，再进入现有公开 100-wire QNode。
这里不能使用长度为 
2
100
 的 TF statevector。
建议优先设计稳定的 exact low-bond tensor contraction：
纯文本
复制代码
Existing native plan


→ Local TF gate tensors


→ TF MPS tensor chain


→ Local contraction / swap routing


→ Observable contraction


→ TF autodiff
必须保证：
与现有 MPS 的物理状态语义一致；
保留 global complex scale；
不把非酉 tangent 归一化；
不引入全局 dense；
支持少量相邻 active wires；
再支持远距离 active wires；
保留源 owner 和参数身份；
bond 及 workspace 受现有 Device 预算约束。
特别注意 QR/SVD
不能假定对任意 SVD/QR、Schmidt 截断和奇异值退化直接做 TF AD 就能得到正确高阶导数。
优先对
无截断、bond 维度稳定
的子域验证。
可以通过数学上精确的局部 tensor-network contraction 实现该子域，但必须有独立的小规模解析对照，并且在 100-wire 上禁止全态密集展开。
如果已有 native MPS 的 canonicalization 不适合 TF AD，不要为了复用代码而让 trainable tensor 脱离 TF 图。可以复用其 wire routing、budget 和 tensor contract，在 TensorFlow 层明确实现可微的局部 contraction，但这仍必须使用同一已编译计划，而非第二套线路定义。
9. 100-wire 原四条阻断必须原样重跑
以下四条仍是正式验收门槛：
Square loss FoR；
Square loss RoF；
Exponential/cubic loss FoR；
Exponential/cubic loss RoF。
不得修改 loss、降低精度、增加 skip/xfail 或切换 mock/Statevector。
同时测试：
open/closed controls；
两控制位；
global phase；
parameter UUID/vector；
IR/QPY roundtrip；
远距离 wire；
100-wire no-dense；
max bond；
tangent-component limits；
exhausted budget；
branch-cut refusal；
source owner 不变。
保留当前 
max_mps_tangent_components
 与 wide barrier/delay 的预算修复；未知 directive 不得自动豁免。
10. IR/QPY 与 Device 连接
必须证明：
纯文本
复制代码
Native QNode


→ Native IR or QPY v13


→ restored native Circuit


→ same compiler plan


→ TensorFlow Whole-QNode


→ expectation / mixed Hessian / streamed HVP
检查：
真实 ParameterVector identity；
stored execution frames；
numeric exponent；
symbolic base；
modifier 顺序；
ctrl_state；
global phase；
measurement mapping；
资源计划。
QPY v13 不支持 symbolic exponent 的边界继续严格拒绝，不能通过私有 metadata sidecar 冒充标准互操作。
11. 保护非 TensorFlow 路径
新增专用 TF Whole-QNode selector，不得改变：
Torch forward_ad；
Autograd JVP；
JAX JIT/VJP；
原生 Statevector；
Density；
native MPS；
fixed-projector fast path；
moving-projector Fréchet；
原有 parameter-shift/adjoint；
H₂；
Aer noise；
Operator.power Jordan 正确性；
classical dynamic ControlBlock。
尤其防止新的 
best
 selector 再次导致普通 Gate 从 parameter-shift 偷偷改走资源不同的 adjoint/backprop。
12. 新增测试
建议按功能新增或增强：
纯文本
复制代码
tests/interfaces/test_native_tf_whole_qnode_execution.py


tests/interfaces/test_native_tf_whole_qnode_mixed_ad.py


tests/interfaces/test_native_tf_whole_qnode_resources.py


tests/interfaces/test_native_tf_mps_contraction.py


tests/interfaces/test_native_tf_mps_nodense.py


tests/serialization/test_native_tf_qnode_roundtrip.py
必须包含：
真实计划来源与 operation occurrence 验证；
低量子位四条 FoR/RoF；
max_diff 一阶/二阶/三阶区分；
不同外部 loss；
多输出；
资源不足零执行；
trace cache 后非法参数；
100-wire no-dense；
IR/QPY；
four-framework 回归。
先红后绿，保留真实日志，不用复制测试数量替代函数完成率。
13. 本段完成门槛
依次评估三个里程碑。
M1：Whole-QNode Low-Qubit
实际公开 QNode 使用现有 Compiler、TF local operator、TF observable contraction；低量子位四条对应红灯通过。
M2：Unified Planning
整条 QNode 的 method、max_diff、direction、workspace 和 Device admission 经过单一原生计划验证，资源失败发生在危险执行之前。
M3：100-Wire MPS
原四条正式 MPS TF 红灯通过，确实由非稠密 TF tensor network 执行，且四框架既有数学能力不回归。
任何里程碑未完成必须明确保留 PARTIAL，不得由其他里程碑替代。
14. 原 R2 最终冻结门禁继续有效
全部所声明的支持范围经过最新代码的开发期宽回归后，再冻结最终 runtime。
必须真实执行：
SDK-free FULL；
Main Qiskit 2.4.1 / PennyLane 0.44.1 FULL；
Alternate Qiskit 2.6.0 / PennyLane 0.42.3 FULL；
Independent JAX FOCUS；
Independent TF FOCUS；
Torch/Autograd FOCUS；
显式 GLOBAL coverage；
原始未修改的 28-section matrix；
所有 SDK-free numerical examples；
controlled legal；
no-token/no-vendor；
实际 import origins；
frozen/worktree/staged/commit runtime equality。
Global line coverage 底线：
91.34108013033072%
。Exclusions：
68，不增加
。
旧的 577/12 综合 FOCUS、269 局部 kernel 专项及纯 TF 272 项都不能替代新的 Whole-QNode/100-wire 全量门禁。
15. Git、安全与最终报告
继续 owner 的 local-only 权限：不 push/fetch，不更新 OAuth/TLS，不安装依赖，不 vendor、不读取 token、不调用云或真实硬件、不改金融 13 项证据、不扩大 Studio/Router、不重写 Git 历史。
只有实际冻结验收满足原 R2 规定，才考虑 normal scoped 本地提交。
最终报告必须列明：
新 TF 执行是否真正使用原生 ExecutionPlan。
Whole-QNode 具体支持哪些操作、测量和线路。
低量子位 QNode FoR/RoF 是否真实通过。
100-wire 原四条红灯是否真实通过。
max_diff 与 method 的实际执行语义。
NativeHost/Device 的工作预算及真实拒绝入口。
TF trace/retrace 与 runtime 参数 guard。
IR/QPY 与 UUID/controlled phase。
100-wire bond、workspace、无 dense 的证据。
非 TF 框架和原生内核回归。
三环境 FULL、GLOBAL、matrix 真实状态。
最新本地 SHA、提交与远端 CI 状态。
R2O3-B、R2/P4 和完整 Qiskit/PennyLane 替代还缺哪些核心功能。
下一步明确：停止继续单独打磨 LocalOperator，先把它变成真实 Whole-QNode 中可执行的一环，完成整条计划的能力校验、统一资源预算和低量子位 TensorFlow 混合 AD；再以现有计划为唯一语义来源推进非稠密 100-wire MPS。
目前 TF5 新 kernel 是可信的局部数学基础，但那 12 条公开 QNode 失败仍然是必须修复的集成阻断。完整独立 Qiskit/PennyLane full functional parity/full replacement 继续保持 
ACTIVE / INCOMPLETE
。
