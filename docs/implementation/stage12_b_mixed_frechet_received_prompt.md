# Received R2O2 Prompt

Read from the actual default-Chrome conversation body on 2026-10-23 after
verifying the foreground PID and authorized conversation title before reload.
No new page or login was opened. This is not an API reference placeholder.
Accessibility formula line splitting is retained. Receipt does not establish
completion of these requirements or of the original full replacement goal.

+Codex 执行 Prompt：Stage 12-B P4-U3D2-R2O2
Native Mixed Fréchet Derivatives, Matrix-Free Parameter HVP & Multi-Parameter QNode
继续原 Stage 12-B P4-U3D2-R2O，不另起 SDK 阶段，不进入 Studio、UI 或应用案例。
最高目标保持：
QuantumBridge 独立原生 Qiskit/PennyLane full functional parity/full replacement — 
ACTIVE / INCOMPLETE
。
1. 首个任务：真正的双参数红灯
先使用当前已存在的 native Generic Gate：
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
-
p
, 
0
)
gate
 
=
 
body
.
to_gate()
annotated
 
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
1
)
qc
.
append(
annotated
, [
0
])
qnode
 
=
 
QNode
.
from_circuit(
qc
)
先独立证明该电路在测试点具有非对易性和随参数变化的谱投影，避免将固定投影测试误算为 moving-projector。
必须先运行真实失败测试：
未绑定的 QNode 构造。
∂p
、
∂q
。
∂pp
、
∂pq
、
∂qp
、
∂qq
。
JVP、VJP。
指定方向的 streamed HVP。
不同参数绑定顺序。
QPY/IR roundtrip 后重复微分。
不能因为单参数 
Hessian
 已经通过，就将 
∂pq
 自动视为已实现。
2. 实现多参数原生矩阵 jets
扩展现有 
unitary_power_jet
 的方向接口，复用既有 Fréchet 和 native matrix-function 内核。
需要真正计算：
𝑈
,
𝑈
𝑝
,
𝑈
𝑞
,
𝑈
𝑝
,
𝑈
𝑝
𝑞
,
𝑈
𝑞
然后计算：
𝑉
=
𝑈
𝛼
𝑉
𝑝
=
𝐿
𝑓
(
𝑈
,
𝑈
𝑝
)
,
𝑉
𝑞
=
𝐿
𝑓
(
𝑈
,
𝑈
𝑞
)
以及：
𝑉
𝑝
𝑞
=
𝐿
𝑓
(
𝑈
,
𝑈
𝑝
𝑞
)
+
𝐿
𝑓
(
2
)
(
𝑈
;
𝑈
𝑝
,
𝑈
𝑞
)
二阶 Fréchet 项必须包含两个方向的对称贡献，且通过 
∂pq ≈ ∂qp
 的数学测试。
建议构建一般化的 directional jet API，而不是为每个参数对复制一套矩阵求幂算法。
生产内核不得使用有限差分。
3. 使用独立数学 oracle
至少准备两种独立 oracle：
解析小维 SU(2) oracle：
 从 Pauli 表示与旋转关系推导完整复矩阵及混合偏导。
测试侧高精度 oracle：
 对实际输入矩阵使用独立高精度矩阵函数与参数微分方法交叉核对。
有限差分只能用在测试侧。涉及 branch cut 时不能跨越不可微点取差分。
至少检查：
∂pq
 和 
∂qp
 数值一致；
full complex operator；
Jacobian；
Hessian；
HVP；
parameter-shift 与 adjoint 方法选择；
多次 partial binding；
global phase 和 open-control；
同名不同 UUID 参数。
4. 真正 streamed HVP
不要通过生成完整 Hessian 再做矩阵乘法。
对于参数向量 
𝜃
 与方向 
𝑣
，实现方向矩阵导数：
𝑈
𝑣
=
∑
𝑗
𝑣
𝑗
𝑈
𝑗
和：
𝑈
𝑖
𝑣
=
∑
𝑗
𝑣
𝑗
𝑈
𝑖
𝑗
随后：
𝑉
𝑖
𝑣
=
𝐿
𝑓
(
𝑈
,
𝑈
𝑖
𝑣
)
+
𝐿
𝑓
(
2
)
(
𝑈
;
𝑈
𝑖
,
𝑈
𝑣
)
沿现有 native QNode directional execution 计算最终 observable 的 HVP。
验收要求：
Streamed HVP 不创建完整 
𝑛
×
𝑛
 参数 Hessian。
工作空间随请求的方向和活动参数数量有明确界限。
输出与独立 Hessian oracle 乘向量一致。
不以调用完整 
compute_hessian()
 作为内部实现。
允许在测试侧构造完整 Hessian 作对照。
建议在测试中 monkeypatch 完整 Hessian 入口为抛错，以证明 streaming 路径未调用它。
5. 参数表达式、相位及 QNode 集成
必须支持实际受控子集中的：
q*q
；
sin(p)
、
exp(q)
；
同一参数多次出现在定义中；
global phase 含 
p*q
；
ParameterVectorElement；
同名不同 UUID；
partial binding；
Generic Gate → ControlledGate → AnnotatedOperation；
inverse/control/power 的正确 modifier 顺序。
编译时只能提取合法的局部符号执行图，不能在未绑定状态下尝试求 matrix power。
特别保护原 R2N fixed-projector 快速路径与普通 Gate parameter-shift，不允许新 general method selector 覆盖原有 shift 资源预算。
6. 四框架真实二阶图
在 Torch、Autograd、JAX、TensorFlow 中分别执行：
一阶梯度；
mixed second derivative；
Hessian；
directional HVP；
JVP/VJP；
JAX JIT / TF graph 的可支持路径。
不能在 Python 侧计算好结果后只包装成框架 Tensor。
运行 JAX 时明确启用 x64，不改变既有容差。
若某框架当前没有真实的二阶计算图支持，明确记录 
UNSUPPORTED
，不能用 SDK-free 结果替代。
7. IR/QPY 边界
测试：
纯文本
复制代码
Unbound Generic Gate(p, q)


→ AnnotatedOperation(PowerModifier(0.5))


→ Native IR / QPY v13


→ Native QNode


→ Bind


→ Mixed Jacobian/Hessian/HVP
必须保留 UUID、ParameterVector、global phase、控制态及 modifier 顺序。
QPY v13 对 symbolic exponent 仍明确拒绝；numeric exponent + symbolic gate 参数继续双向互操作。
不得使用私有 metadata sidecar 或上游 SDK passthrough。
8. 资源与安全反例
至少新增：
大参数维度但只请求一个 HVP direction；
完整 Hessian 入口 patched-to-fail；
多方向请求计量；
nested AnnotatedOperation depth；
matrix block workspace 预检；
unsupported nonunitary matrix；
branch-cut 跨越；
near-repeated eigenvalues；
parameter UUID collision；
unbounded iterable directions；
foreign ndarray callback；
IR/QPY malformed parameter map；
QNode 编译失败的原子性。
对每个局部 
𝑑
×
𝑑
 幂运算，应计量块矩阵工作空间，不能只计量最终 
𝑑
×
𝑑
 输出。
不得对 100-wire Circuit 生成全局 
2
100
 密集矩阵。
9. 必须新增的测试
至少完成：
12 个真正双参数非对易场景；
10 个混合二阶 Fréchet 测试；
10 个 streamed HVP 测试；
8 个 JVP/VJP 测试；
12 个四框架计算图测试；
8 个 IR/QPY roundtrip 测试；
12 个资源和错误反例。
测试数量不能作为 SDK 函数实现比例。
先真实红灯，再修复，不扩大 skip/xfail，不放宽数学阈值。
10. 开发期联合回归
本段完成后，运行最新代码的：
Core/Circuit/Information；
Compiler；
Serialization；
Gradients/QML；
DerivativeExecution；
Interfaces；
Devices/Noise；
H₂；
SDK-free numerical examples；
Qiskit 2.4.1/2.6.0 public differential。
尤其要对照已有的单参数 150/975/555 项专项回归。
不把旧源码的宽回归成绩当作本次源码的验收。
11. 原 R2 最终冻结门禁保留
只有当前支持功能全部通过、没有未解决的 native correctness failure，才能冻结最终源码。
继续原 R2 全部门禁：
SDK-free FULL；
Main FULL；
Alternate FULL；
Independent JAX FOCUS；
Independent TF FOCUS；
Torch/Autograd FOCUS；
GLOBAL coverage；
原始未修改的 28-section matrix；
所有 SDK-free examples；
controlled legal；
实际 import origins；
frozen/worktree/staged/committed runtime equality。
GLOBAL line coverage 底线仍是 
91.34108013033072%
，exclusions 
68
 不得增加。
若发现真实失败，修复后重新冻结并重跑；不得把 RUNNING、FOCUS、SKIP 或 XFAIL 算作 FULL 通过。
12. Git 和最终汇报
保持 owner local-only 授权：
不 push、不更改 OAuth/TLS；
不重写历史；
不触碰 Studio/Router 原有修改；
不安装依赖、不 vendor；
不新增夸父任务；
不修改 13 项金融硬件证据或已交付应用案例。
仅在最终冻结、完整门禁和代码一致性审计通过后，才进行 normal scoped 本地提交。
最终报告必须分别说明：
双参数 mixed Fréchet 的真实适用范围。
∂pq/∂qp
 的独立误差。
Streamed HVP 是否确实未构造完整 Hessian。
四框架一、二阶图。
IR/QPY 与参数身份。
100-wire MPS 是否真正无 dense。
资源预算和分支拒绝边界。
三环境 FULL、GLOBAL、28-section matrix 真实状态。
本地提交/远端 CI 的真实状态。
U3D2/R2O 与完整 Qiskit/PennyLane SDK 仍缺哪些核心能力。
本批优先实现真正的双参数 mixed Fréchet 和 streamed HVP，而不是继续扩大单参数固定投影测试。
完整独立原生 Qiskit/PennyLane full functional parity/full replacement 继续为 
ACTIVE / INCOMPLETE
。
