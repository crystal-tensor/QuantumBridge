# Received R2O3-B-TF5 Native QNode Integration Prompt

Actual completed reply read on2026-10-24 from the owner's authorized existing
default-Chrome conversation after verifying the conversation identity and
completed reply. No new tab or login. Accessibility line splitting is kept.
This is received task guidance, not implementation or acceptance evidence.

+QuantumBridge R2O3-B-TF4：阶段审阅
结论：第一层纯 TensorFlow 数学验证可以接受为已通过专项测试的开发检查点。下一步应进入真正的 Native QNode 接入，而不是继续扩充纯 TF 演示。
从报告看，当前有三项实质性成果：
纯 TF 数值与自动微分闭环已验证。
 Main 和 Alternate 各自完成 234 个数学场景及 38 个非法输入场景，覆盖非对易门、moving-projector 分数幂、复数相位、双输出和不同 AD 组合。
图边界问题已有明确规避条件。
 最终 validator 只返回布尔判定，而可训练的矩阵和相位始终留在调用者的 TensorFlow 计算图内。这比此前尝试在 host callback 外补接 Hessian 更有依据。
正式 QNode 阻断尚未改变。
 四条 100-wire TensorFlow FoR/RoF 红灯在 Main、Alternate 仍然失败，因此公开 TensorFlow 后端没有通过验收。
检查项
当前结果
纯 TF 数学测试
每环境 234 passed
非法输入与分支拒绝
每环境 38 passed
Moving-projector 数学
纯 TF 层已验证
Native QNode TF 接入
NOT
_
IMPLEMENTED
100-wire TF MPS 执行
NOT
_
IMPLEMENTED
原四条 TF 阻断
4 FAILED
三环境 FULL / GLOBAL / matrix
NOT
_
RUN
完整 Qiskit/PennyLane replacement
ACTIVE / INCOMPLETE
检查项
纯 TF 数学测试
非法输入与分支拒绝
Moving-projector 数学
Native QNode TF 接入
100-wire TF MPS 执行
原四条 TF 阻断
三环境 FULL / GLOBAL / matrix
完整 Qiskit/PennyLane replacement
当前结果
每环境 234 passed
每环境 38 passed
纯 TF 层已验证
NOT
_
IMPLEMENTED
NOT
_
IMPLEMENTED
4 FAILED
NOT
_
RUN
ACTIVE / INCOMPLETE
检查项
当前结果
进入第二层时最大的风险
不能把纯 TF 数学表达式直接变成另一套 QuantumBridge 编译器。
现有 
Circuit
、ParameterExpression、Gate、AnnotatedOperation、IR、Compiler、DerivativePlan 和资源限制仍必须是唯一可信来源。TensorFlow 只能是这些已验证语义的一种可微执行实现。
另外，纯 TF 的 branch guard 已经通过测试，但生产接入时要防止用 Python 布尔判断代替运行期张量判断，或者让 
tf.function
 仅在 trace 时验证一次、随后接受不同的非法参数。
TensorFlow 的 
GradientTape
 和 
ForwardAccumulator
 有不同的反向及前向记录规则，嵌套顺序会影响高阶结果；官方 API 文档也强调不能混淆它们的求导语义。
本次审阅仅依据你提供的本地执行报告。我没有独立检查未提交源码、独立 oracle 文件或远端 CI。
下一段 Codex 执行 Prompt：Stage 12-B P4-U3D2-R2O3-B-TF5
Native QNode → TensorFlow Differentiable Execution Integration
继续原 R2O3-B-TF4 和完整 R2。
最高目标始终是独立原生 Qiskit/PennyLane full functional parity/full replacement，
ACTIVE / INCOMPLETE
。
本段只推进两件事：首先让真实 QuantumBridge QNode 使用已经通过纯 TF 验证的数学路径；随后将该路径推进到有界、无全态 dense 的 MPS 执行。
不要重写已通过的 Fréchet、MPSTangentJet、ParameterVector、QPY 或 Compiler。
1. 第一阶段：低量子位真实 QNode 接入
首先只在 1–4 qubit 范围内开发，证明新路径真正使用现有 QuantumBridge 编译结果。
从已验证的原生线路创建：
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
gate
 
=
 
body
.
to_gate()
powered
 
=
 
gate
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
powered
, [
1
])
qnode
 
=
 
QNode
.
from_circuit(
qc
)
运行 TensorFlow 接口，验证：
QNode 在 
p/q
 未绑定时能够构造；
CircuitInstruction
 stored frame 保留；
UUID/vector 身份不变；
Compiler 输出合法原生执行计划；
TF 从执行计划获得参数化局部 Gate；
TF Tensor 参与真实量子计算；
外部 loss 由 TensorFlow 直接求导；
不调用 NumPy/Python host callback 计算 trainable value/gradient；
不使用 Qiskit/PennyLane executor。
验收时必须证明调用来源：不是手写另一条 RY/RZ/RX 电路冒充 QuantumBridge QNode。
2. 定义唯一的 TF 执行适配边界
建议在现有 execution/interfaces 架构内新增受控 adapter，例如：
quantumbridge/interfaces/tensorflow_native_execution.py
该模块只能消费现有 Compiler/DerivativePlan 已验证的执行计划。
它可以负责：
ParameterExpression → TF ops；
局部 primitive → TF complex tensor；
local SU(2) principal fractional power；
Gate wire mapping；
local tensor contraction；
observable expectation。
但不得拥有：
独立 Circuit store；
独立量子 IR；
独立 Gate registry；
独立参数 UUID 系统；
第二套 Compiler；
未受预算控制的全线路 dense fallback。
已有 
tensorflow_graph.py
 和 
tensorflow_autodiff.py
 不要整体替换。只为可证明正确的受支持执行子域增加显式选择路径，其他合法旧路径继续保持原样。
3. 先做执行计划一致性测试
针对同一 Native QNode，建立：
纯文本
复制代码
Native Circuit / AnnotatedOperation


              ↓


Existing Compiler / Native ExecutionPlan


              ↓


Native TensorFlow local execution


              ↓


Expectation / Gradient / Hessian / HVP
与当前 Native Statevector/Density/Fréchet 路径比较。
至少覆盖：
RY/RZ/RX 非对易；
controlled/open-control；
symbolically parameterized Gate；
global phase；
ParameterVector；
noncontiguous wires；
inverse/power modifiers；
两个输出 observables；
partial bind；
IR/QPY roundtrip。
不能只通过最终期望值一致就认为执行计划一致。还需要比较：
operations 顺序；
operand indices；
parameter UUID；
modifier 顺序；
控制位状态；
global phase；
branch-policy；
返回 dtype 和形状。
4. TensorFlow 可微数学必须留在真实图内
重点保护你已经发现的成功条件：
Trainable matrix、phase 和 observable contraction 必须在 TensorFlow 可微图中完成。
非训练性的合法性检查可以提前使用静态数据；参数依赖的合法性则必须在运行期检查。
禁止：
通过 
numpy_function
 或 
py_function
 计算 trainable tensor；
把 
theta.numpy()
 转成原生 NumPy 后再包装 Tensor；
对 trainable local matrix 调用 
stop_gradient
；
使用完整 Hessian tensor 注入图；
为特定外部 loss 编写导数；
私有全局 JVP registry；
新安装依赖。
对 trace-time 和 runtime validation 分别进行恶意输入测试。
5. 必须真正通过的低量子位 AD 测试
先将已存在的四条正式 QNode TF 红灯，增加对应的 1–4 qubit 变体。
使用：
Python
复制代码
运行代码
loss_a
 
=
 (
y
 
-
 
0.3
)
**
2
loss_b
 
=
 
tf
.
exp(
y
) 
+
 
0.2
*
y
**
3
必须验证：
FoR；
RoF；
Tape-over-Tape；
JVP；
VJP；
mixed Hessian；
streamed directional HVP；
JAX/TF 之外原有框架结果不变。
数学 oracle 由独立 SU(2)、完整小规模复矩阵或高精度测试侧计算生成。
低量子位 TF 真正修复后，只能标记“低量子位 TensorFlow 可微 QNode 子集通过”；原 100-wire 四条红灯仍为失败。
6. 资源规划先于 TensorFlow 运算
任何受支持 TF specialization 必须先经过已有：
ExecutionPlan
；
DerivativePlan
；
SecondWork
；
NativeHost
；
Device admission；
max_mps_tangent_components
；
局部 matrix workspace；
参数方向及输出数量预算。
新增测试应 patch TF 危险分配入口，确保超预算输入在分配前拒绝。
尤其应防止 
tf.function
 retracing 后重复执行 host-side work 或重新扣费。
资源验证不能只在第一次 trace 时运行，而下一次参数改变后绕过 branch-cut、finite-value 或 shape 限制。
7. 第二阶段：真正的 100-wire TF MPS
只有低量子位真实 QNode 已通过后，才推进 100-wire。
优先使用已验证的低 bond 情形，例如少数活动 wire 的 100-wire Circuit。
要求：
使用现有 Circuit/Compiler 计划；
真正 TensorFlow 张量局部收缩；
保留 MPS 的物理张量语义；
不生成全态 statevector；
不生成全线路 Operator；
保留 global complex scale；
避免普通归一化吞掉 tangent 幅度；
真实支持相邻和远距离 active wires；
不将截断可微性自动标记为完成。
这里需要一个非常重要的限制：
如果 TF 对 SVD/QR 归一化或截断的自动求导无法保证与已验证 MPSTangentJet 一致，不应强行依赖原生 TF autodiff 穿过不稳定 gauge。
可以针对无截断、稳定 bond 的子域设计可微 contraction；更一般的截断与退化奇异值仍明确保留 Unsupported。
8. 100-wire 正式四条红灯
必须让原先四条真实测试直接通过：
squared loss FoR；
squared loss RoF；
exponential/cubic FoR；
exponential/cubic RoF。
不改外部 loss，不改数学容差，不删除测试、不扩大 skip/xfail。
测试中禁止：
Python
复制代码
运行代码
MPS
.
statevector
MPS
.
reduced_density_matrix
StatevectorDevice
.
statevector
DensityMatrixDevice
.
density_matrix
Gate
.
to_matrix  
# 禁止整线路密集展开
允许有预算的局部矩阵计算。
必须报告：
实际 active wire；
最大 bond；
截断情况；
TensorFlow tensor workspace；
trace 次数；
dtype；
每条导数路径；
数值误差；
与 Native MPSTangentJet 的差异。
9. IR/QPY 与参数身份
至少完成：
纯文本
复制代码
Unbound Native QNode


→ IR/QPY v13


→ restored Circuit


→ Compiler/ExecutionPlan


→ TF tensor execution


→ mixed Hessian/HVP
保留：
UUID；
ParameterVector；
AnnotatedOperation
；
control/open-control；
symbolic angle；
numeric exponent；
global phase；
Bit/Register；
cached execution frame。
QPY v13 不支持符号 exponent 的边界继续严格拒绝，不能用私有 sidecar 伪装标准格式。
10. 回归与完成门槛
本批按顺序验收：
A. 纯 TF 基线：
 保留 234+38 已通过用例。
B. 真实低量子位 Native QNode：
 完整复矩阵、FoR/RoF、Hessian/HVP、两种 loss 通过。
C. 真实 100-wire MPS：
 原四条阻断测试通过、无 dense、预算与 AD 正确。
然后重新运行：
TF Interfaces；
Torch/Autograd/JAX；
Native QNode/MPS；
Compiler；
IR/QPY；
Device/DerivativeExecution；
H₂/Noise；
SDK-free examples。
只有最新代码开发回归通过，才考虑原 R2 的最终冻结。
原 R2 全部门禁保留：
SDK-free FULL；
Main FULL；
Alternate FULL；
Independent JAX / TF；
Torch/Autograd；
GLOBAL coverage ≥ 
91.34108013033072%
；
exclusions 
68
 不增；
原始未改 28-section matrix；
全部 numerical examples；
controlled legal；
五个实际 import origins；
frozen/worktree/staged/commit equality。
如果仅完成 A+B，明确 C 未完成；不能借此关闭 R2O3-B。
11. Git 与权限
保持 owner local-only：
不 push、不修改 OAuth/TLS；
不安装依赖、不 vendor；
不修改 Studio/Router；
不新增夸父硬件任务；
不改 13 项金融真机证据；
不重写历史；
不复制上游 SDK 源码。
只有达到规定最终门禁，才考虑正常 scoped 本地提交。没有真实验收就维持当前未提交开发状态。
最终报告需要明确区分：
纯 TF prototype；
真实 Native QNode low-qubit；
真实 100-wire TensorFlow MPS；
原四条正式红灯；
IR/QPY；
资源与图追踪；
三环境 FULL/GLOBAL/matrix；
本地提交和远端 CI；
尚未实现的完整 SDK API。
下一步应该实现的是：让现有 QuantumBridge 编译计划成为 TensorFlow 可微张量执行的唯一语义来源，然后从低量子位实际 QNode 开始逐层验证，最终攻克 100-wire 的四条正式 TF 混合微分红灯。
这条路线不需要重新实现量子数学定义，也不能借纯 TF 演示提前声称 QuantumBridge 的 TF 高阶微分已经完成。
完整 Qiskit/PennyLane 独立原生 full functional parity/full replacement 继续保持 
ACTIVE / INCOMPLETE
。
