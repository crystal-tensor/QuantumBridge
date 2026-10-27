# Received R2O Prompt

Read from the owner's existing default-Chrome conversation
"Claude 代码泄漏与应对" on 2026-10-23. This is the actual assistant body,
not the content-reference placeholder returned by the thread API.
The accessibility extractor splits displayed formulas into individual lines;
that source formatting is retained below. This is a received work request,
not evidence that its scope or acceptance gates have been completed.

+下一段 Codex 执行 Prompt：Stage 12-B P4-U3D2-R2O
Native General Fréchet Derivatives for Parameterized Matrix Powers
继续既有 R2N/R2 原生核心开发，不进入 UI、金融诊断、Studio 或新的 SDK 阶段。
0. 目标及执行顺序
最高目标保持：
QuantumBridge 独立原生 Qiskit/PennyLane full functional parity / full replacement：
ACTIVE / INCOMPLETE
。
本段目标是把当前固定谱投影算法扩展到真正具有
参数变化谱投影与非对易结构
的矩阵幂导数，同时保持已经验证的 fixed-projector 快速路径。
优先顺序：
新增 moving-projector / noncommuting 数学红灯。
设计通用 Fréchet 导数内核。
实现一阶方向导数。
实现二阶混合方向导数及 streamed HVP。
集成 Compiler、QNode 和四框架自动微分。
保护 IR/QPY、100-wire MPS、资源和分支安全。
执行原 R2 最终完整门禁。
先审核并保留当前 73/863/443 个专项测试及相关回归，不重写既有 fixed-projector 子族。
1. 首先构造真正非对易的红灯
不能仅用同一轴的 RX/RY/RZ 或相互独立的张量因子。
至少构造：
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
inner
 
=
 
Circuit
(
1
)
inner
.
rx(
p
, 
0
)
inner
.
rz(
q
, 
0
)
gate
 
=
 
inner
.
to_gate()
power_gate
 
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
power_gate
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
这里一般存在非对易关系及随参数变化的谱投影。
要求先实际运行，记录以下红灯：
QNode 能否在未绑定时编译；
绑定后完整复矩阵；
对 
𝑝
 的一阶导数；
对 
𝑞
 的一阶导数；
混合二阶导数；
给定方向向量的 HVP；
经过 IR roundtrip 后结果；
固定指数为 
0.5
、
-0.5
、
1.5
 的情况。
再增加两量子比特非对易 composite Gate，以及带受控全局相位的组合。
不能通过固定谱投影分解误判为支持。
2. 独立数学 oracle
使用真正独立于生产 matrix-functions 内核的数学对照。
建议至少两类：
A. 2×2 解析 SU(2) / Pauli 表示。
对于合法的 
𝑈
(
𝑝
,
𝑞
)
，可以通过旋转轴与角度构造独立的完整复矩阵及其导数。需要明确处理 global phase 和主值分支。
B. 高精度测试侧矩阵函数。
对小维度输入允许使用已经存在的 mpmath 或独立高精度构造作为 oracle，不加入生产依赖。
参数导数可以在测试侧使用高精度差分或解析/自动微分交叉检查；但有限差分不能作为生产导数算法冒充 adjoint 或 parameter-shift。
至少构造一个明确满足：
[
𝐴
,
∂
𝑝
𝐴
]
≠
0
的测试，防止固定投影算法在错误前提下通过。
3. 原生 Fréchet 一阶导数
对矩阵函数 
𝑓
(
𝐴
)
=
𝐴
𝛼
，实现方向导数：
𝐿
𝑓
(
𝐴
,
𝐸
)
=
𝑑
𝑡
𝑓
(
𝐴
+
𝑡
𝐸
)
∣
𝑡
=
0
针对酉矩阵可利用谱投影与 divided differences：
𝐿
𝑓
(
𝐴
,
𝐸
)
=
∑
𝑖
,
𝑗
𝑓
[
1
]
(
𝜆
𝑖
,
𝜆
𝑗
)
𝑃
𝑖
𝐸
𝑃
𝑗
对于相同或接近的特征值，正确采用解析导数极限；对跨分支近重的特征值，
不能强制合并
，必须保留 R2L 的分支敏感数值安全规则。
对一般非正规矩阵，不能直接套用正规矩阵的酉谱投影算法。应基于现有 Schur–Parlett/Schur–Padé 数值结构，实现经过验证的适用分支，无法可靠计算时明确数值拒绝。
Higham–Lin 的研究明确讨论了矩阵分数幂及其 Fréchet 导数的联合计算；这是合适的数学设计参考，但不得复制第三方实现。
4. 二阶 Fréchet 与 HVP
对于 
𝐴
=
𝐴
(
𝑝
,
𝑞
)
，二阶参数导数不能遗漏 
𝐴
 本身的二阶导数：
∂
𝑝
𝑞
𝑓
(
𝐴
)
=
𝐿
𝑓
(
𝐴
,
∂
𝑝
𝑞
𝐴
)
+
𝐿
𝑓
(
2
)
(
𝐴
;
∂
𝑝
𝐴
,
∂
𝑞
𝐴
)
要求实际实现：
一阶 JVP；
一阶 VJP；
Jacobian；
二阶混合偏导；
Hessian；
streamed HVP；
batch direction 的受控内存处理。
优先实现具有真实数学依据的二阶谱 divided-difference 或等价的受控小维度算法。
不能通过完整 Hessian 矩阵再乘向量冒充 streamed HVP。
更高阶 Fréchet 导数及条件数的数学理论已有研究基础，但本批必须区分真正实现的最高阶数，不能声称任意阶。
5. QNode 与原生导数引擎集成
目标链：
纯文本
复制代码
Generic Parameterized Gate


→ AnnotatedOperation(PowerModifier)


→ Native QNode


→ symbolic execution graph


→ numerical parameter binding


→ local matrix-power evaluation


→ native derivative rule


→ Jacobian / Hessian / streamed HVP
必须保证：
未绑定 QNode 可以构造；
参数 UUID/vector 身份正确；
base operation 参数变化被追踪；
modifier 顺序正确；
global phase 不丢失；
control/open-control 正确；
source owner/cached frame 正确；
不建立第二套 QuantumCircuit、参数系统或模拟器。
对真正已经支持的 fixed-projector 子族，继续使用已验证的快速路径；对 moving-projector 的数学支持范围，新增明确的受控分派。
如果导数是通过真正的局部 Fréchet 规则进入 QNode，则应清楚标记其导数方法，不得将其伪称为普通单频 parameter-shift。
6. 四框架一阶与二阶
分别验证：
Torch；
Autograd；
JAX；
TensorFlow。
每个框架必须有真实计算图：
first gradient；
nested second derivative；
mixed Hessian；
JVP/VJP；
directional HVP。
不能先用 Python 算好 Hessian，再仅包装成框架 Tensor。
必须确保 JAX 的 x64 环境已显式启用，保留既有严格数值容差，不通过 float32 精度降低阈值。
7. IR/QPY 与序列化
至少验证：
纯文本
复制代码
Moving-projector symbolic Gate


→ Native IR


→ QNode compilation


→ bind


→ Operator/Jacobian/HVP
以及：
纯文本
复制代码
Symbolic base parameters + numeric exponent


→ QPY v13


→ native reload


→ QNode/Jacobian/HVP
QPY v13 不能表示的符号 exponent 继续明确拒绝；Native IR 应保留其受支持的 symbolic exponent。
不得使用 QPY 私有扩展或 metadata sidecar 假装标准兼容。
继续保护 custom g/c/a/m/i、Parameter UUID/vector、Bit/Register records、open controls 以及跨 records/circuits 的 numeric budget。
8. 资源与错误边界
新增至少以下反例：
高维 generic matrix-power；
非正规矩阵误入 unitary fast path；
接近分支切线；
跨 cut 的相近特征值；
exact Jordan 与 rounded Jordan 区分；
unknown eigenprojector derivative；
Schur workspace 超限；
二阶方向数爆炸；
参数表达式图循环；
foreign ndarray callback；
malformed QPY modifier；
未绑定 symbolic exponent；
非法 complex angle；
QNode 编译中途失败；
100-wire 全态 dense fallback。
资源预算必须覆盖实际需要的矩阵存储、谱分解、Fréchet 方向及二阶工作空间，而不仅是最终输出矩阵。
若无法保证给定输入的数值可靠性，应进行有依据的数值拒绝，不能输出错误有限矩阵。
9. 100-wire MPS 验证
至少两类：
A. 小型局部 moving-projector Gate 施加到 100-wire MPS。
允许预算内的 2×2 或 4×4 局部矩阵与局部导数，但不得构造全线路 
2
100
 维矩阵。
B. 两个相距较远的活动量子位。
在已有 MPS 路由支持范围内测试非连续 wires，并确保 SWAP/routing 与导数执行一致。
继续 monkeypatch 禁止：
full Gate.to_matrix；
StatevectorDevice.statevector；
DensityMatrixDevice.density_matrix；
MPS.statevector。
保留 GHZ 与既有 100-wire 梯度/HVP 回归。
10. 测试要求
至少新增：
12 个真正 moving-projector 数学场景；
12 个完整复矩阵及分支场景；
10 个一阶 Fréchet 场景；
10 个二阶/HVP 场景；
12 个四框架图测试；
8 个 IR/QPY 场景；
12 个资源/失败原子性反例。
先红后绿，记录原始失败，不允许通过 skip、xfail 或扩大 Unsupported 掩盖此前已声称支持的输入。
测试数量不是功能完成比例。
11. 原 R2 最终冻结门禁
本段数学实现完成并通过最新开发期宽回归后，仍需在同一冻结代码树运行：
SDK-free FULL；
Main Qiskit 2.4.1 / PennyLane 0.44.1 FULL；
Alternate Qiskit 2.6.0 / PennyLane 0.42.3 FULL；
Independent JAX FOCUS；
Independent TF FOCUS；
Torch/Autograd FOCUS；
GLOBAL line coverage；
原始未修改的 28-section matrix；
所有 SDK-free numerical examples；
controlled legal；
actual import origins；
frozen/worktree/staged/commit runtime equality。
GLOBAL coverage 基线：
91.34108013033072%
Exclusions：
68，不增加
。
若宽回归发现新正确性缺陷，修复并重新冻结；不得拿旧专项测试替代最终 FULL。
12. Git、Owner 授权与最终报告
继续本地工作，不 push、不修改 OAuth/TLS、不修改现有 Git 历史、不安装依赖、不复制上游 SDK 源码。
保留 owner 已交付的 14 个应用案例及金融历史证据，不进行新增云硬件任务或界面扩张。
只有真正冻结、全部规定门禁取得终态并核对源码一致性后，才考虑 normal scoped local commit。
最终报告必须回答：
Moving-projector Gate 是否真正可编译和执行。
适用哪些矩阵类别与分支条件。
一阶 Fréchet 是否真实实现。
二阶 Fréchet/HVP 是否真实实现。
四框架执行图结果。
100-wire MPS 及远线支持范围。
IR/QPY 互操作范围。
分支数值拒绝与错误有限输出。
最新三 FULL、GLOBAL、28-section matrix。
本地提交及远端 CI 真实性。
尚未实现哪些 Qiskit/PennyLane 核心 API。
完成 R2O 后也不自动宣布 R2/P4 或整个 SDK 完成。
 当前 fixed-projector 快速路径可以保留，但不能以此替代通用 Fréchet 导数实现。
最终目标仍为：
QuantumBridge 独立原生 Qiskit/PennyLane full functional parity/full replacement：
ACTIVE / INCOMPLETE
。
