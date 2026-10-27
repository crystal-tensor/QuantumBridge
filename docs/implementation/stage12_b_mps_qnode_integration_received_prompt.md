# Received R2O3-B Prompt

Read from the completed actual assistant body in the authorized existing
Chrome conversation on 2026-10-23, following the R2O3-A terminal report.
Accessibility formula/code line splitting and repeated table cells are
retained below. This is the next received request, not completed acceptance.
The full replacement objective remains ACTIVE / INCOMPLETE.

下一段 Codex 执行 Prompt：Stage 12-B P4-U3D2-R2O3-B
Native QNode–MPS Tangent Integration, Unified Derivative Planning & Resource Admission
继续原 R2O3 和完整 R2，不创建新的 SDK 阶段。
本段唯一最高优先级：让已经通过直接 kernel 测试的 
MPSTangentJet
 真正接入公开 QNode 的 Jacobian、Hessian、streamed HVP，并统一编译、执行、资源规划与导数方法分派。
不重写 
information/mps_tangent.py
、现有 Fréchet 内核或 MPS 模拟器。
1. 首先修复已确认的公开 QNode 红灯
将以下链路保留为正式阻断性测试：
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
rx(
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
ry(
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
100
)
qc
.
append(
annotated
, [
99
])
qnode
 
=
 
QNode
.
from_circuit(
qc
)
构造阶段不能提前求解未绑定矩阵幂。
绑定后必须在 MPS 上实际完成：
expectation；
∂p
、
∂q
；
∂pp
、
∂pq
、
∂qq
；
streamed HVP；
JVP/VJP；
QNode 原有公开返回协议。
现有 
matrix_power_parameter_shift
 失败必须真实复现，再修复生产分派逻辑。
不能通过捕获异常后强行返回 numerical finite difference 或提前调用 Statevector 解决。
2. 建立统一的导数方法规划
审计现有：
QNode；
Compiler/lowering；
NativeHost；
DerivativeExecution；
Device derivative dispatch；
Parameter-shift；
Adjoint/second-adjoint；
MPSTangentJet
。
建议建立统一的内部 
DerivativePlan
，但优先复用已有计划结构，不允许第二套调度系统。
规划时必须区分：
操作类别
正确处理方式
普通 Pauli rotation
保留已有 parameter-shift
固定谱投影 fractional power
保留已验证解析路径
Moving-projector fractional power
General Fréchet/tangent
未知 generator
明确拒绝
不可数值保证的 branch-cut
LinAlgError
不可表示 symbolic exponent
按原格式契约拒绝
操作类别
普通 Pauli rotation
固定谱投影 fractional power
Moving-projector fractional power
未知 generator
不可数值保证的 branch-cut
不可表示 symbolic exponent
正确处理方式
保留已有 parameter-shift
保留已验证解析路径
General Fréchet/tangent
明确拒绝
LinAlgError
按原格式契约拒绝
操作类别
正确处理方式
best
 只能从
合法且完整计量的导数方案
中选择，不能再引入之前 blanket-adjoint 导致的既有 shift 预算回归。
规划结果应明确记录选择的算法、方向数量、局部矩阵尺寸、预计 tangent components、workspace 与设备执行路径。
3. 在 MPS 上完成真正的二阶链式传播
对每个局部 Gate，使用已有 
MPSTangentJet
，将：
𝜓
,
𝜓
𝑝
,
𝜓
𝑞
,
𝜓
𝑝
𝑞
作为一致的状态导数图传播。
混合导数必须保留：
∂
𝑝
𝑞
(
𝑈
𝜓
)
=
𝑈
𝑝
𝑞
𝜓
+
𝑈
𝑝
𝜓
𝑞
+
𝑈
𝑞
𝜓
𝑝
+
𝑈
𝜓
𝑝
𝑞
.
期望值的混合二阶导数还必须计入 bra/ket 的交叉项。
测试至少包含：
单层 moving-projector；
两层非对易 moving-projector；
参数分别出现在不同层；
相同 UUID 多次出现；
global phase 含 
p*q
；
open-control 与 nested control；
相邻活动 wires；
远距离活动 wires；
zero derivative；
很小的非零复切向量。
完整复矩阵和微分结果使用独立小规模 Statevector/解析 oracle 比较，而不是使用同一个 MPS kernel 生成期望值。
4. 真正 streamed HVP
优先沿已有 directional derivative execution 接入 MPS tangent。
必须证明：
不构造完整参数 Hessian；
不调用 
compute_hessian()
；
多参数方向逐步传播；
多输出 observables 的工作量累计正确；
不为全部参数对建立 MPS 副本；
资源需求随实际方向数有明确上界。
继续使用此前八参数 HVP 的测试，并新增一个 100-wire moving-projector 版本。
在测试中将完整 Hessian 入口 monkeypatch 为失败，HVP 仍必须成功。
对 MPS 中多项切向量的求和，必须保留复振幅及相干项，不能把每项分别归一化后再求和。
5. 统一 NativeHost 与 Device 资源 admission
这是本段第二个核心交付。
必须将资源预算贯穿：
纯文本
复制代码
QNode construction


→ derivative method planning


→ compiler lowering


→ NativeHost


→ Device dispatch


→ local Fréchet jets


→ MPS tangent updates


→ observable contraction
特别计量：
100-wire MPS bond 工作空间；
远线 SWAP/routing；
局部 2×2 / 4×4 Fréchet block；
4d 二阶矩阵函数工作空间；
tangent chain 组件数；
coherent sum 的最大中间 bond；
multi-output observables；
directional HVP 数量；
copy amplification；
discarded weight；
实际 host calls 与 shots。
所有可提前确定的危险工作量，必须在模拟执行前 admission。
新增红灯：故意把 tangent component budget 设得低于所需值，并 patch MPS 
_apply
 为失败；正确实现应该在 
_apply
 被调用之前拒绝。
另外，导数计划失败不能修改原 Circuit、参数 owner、Device state 或缓存。
6. 四框架真实 QNode 微分图
分别在 Torch、Autograd、JAX、TensorFlow 上，使用
公开 QNode → MPS
 执行路径测试：
first gradient；
mixed Hessian；
streamed HVP；
JVP；
VJP；
forward-over-reverse；
reverse-over-forward。
必须包含外部非线性 loss，例如：
𝐿
=
(
⟨
𝑍
⟩
−
0.3
)
2
.
不能仅在 Python 中预计算 Hessian，再包装成对应框架 Tensor。
尤其保护：
Autograd 
defjvp
；
JAX JIT 与 x64；
TF graph；
Torch 二阶 graph；
参数共享；
不可导 branch-cut 的明确拒绝。
如果特定框架尚未支持当前 MPS 导数接口，要先记录真实红灯，不能通过改为 StatevectorDevice 冒充 MPS 通过。
7. IR/QPY 端到端闭环
必须实际运行：
纯文本
复制代码
Unbound Generic Gate(p,q)


→ AnnotatedOperation(PowerModifier(0.5))


→ Native IR / QPY v13


→ restored QuantumCircuit


→ QNode.from_circuit


→ 100-wire MPS


→ bind


→ Jacobian/Hessian/streamed HVP
检查：
UUID/vector；
modifier 顺序；
base definition；
ctrl_state；
global phase；
Bit/Register mapping；
cached execution frame；
source owner 生命周期；
返回的参数顺序。
QPY v13 对 symbolic exponent 的现有明确拒绝继续保留，不使用 metadata sidecar 或私有伪标准记录。
8. 100-wire 无 dense 证明
在新增公开 QNode 测试中，至少 patch 以下入口为失败：
Python
复制代码
运行代码
Gate
.
to_matrix
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
并对全线路 Operator materialization 设置阻断。
只有局部、经过资源 admission 的矩阵函数和 tensor contraction 可以使用 dense 小矩阵。
不要仅因线路宽度为 100，就宣称任意高纠缠复杂度的 MPS 都具有可扩展性。
必须报告：
active wire positions；
实际最大 bond dimension；
tangent components；
discarded weight；
各导数方法；
数值误差；
实际运行资源。
9. 数值可靠性与拒绝范围
保留 R2O2 的 near-cut 结果：
可靠分离参数点：必须成功；
严格 cut：明确拒绝；
高敏感度近 cut：有数值依据的 
LinAlgError
；
fixed-projector 快速路径：不被过度拒绝；
一般 moving-projector：不返回已知错误有限导数。
同时保护 R2L 的 Jordan 修复：
108 个严格 Jordan；
32 个条件良好跨 cut；
三项 rounded Fourier 的 justified numerical rejection；
原 45 probe 的 
WRONG_FINITE_RESULT = 0
。
MPS tangent 的数值截断策略必须独立列示，不能把 discarded weight 当成严格导数误差界。
10. 先红后绿的具体测试
建议新增或增强：
纯文本
复制代码
tests/qml/test_native_mps_moving_power_qnode.py


tests/gradients/test_native_mps_tangent_dispatch.py


tests/gradients/test_native_mps_streamed_hvp.py


tests/interfaces/test_native_mps_four_frameworks.py


tests/serialization/test_native_mps_power_roundtrip.py


tests/resources/test_native_mps_derivative_admission.py
最低独立场景目标：
12 个 QNode dispatch；
12 个混合导数；
10 个 streamed HVP；
8 个远线 MPS；
12 个四框架图；
8 个 IR/QPY；
12 个资源与原子失败反例。
先保存 
matrix_power_parameter_shift
 的真实错误回执，再修改生产代码。不能通过 skip、xfail、放宽容差或改用 mock device 获得绿色。
11. 本段完成后的开发期宽回归
至少重新执行：
Core / Circuit / Information；
Compiler；
Serialization；
Gradients/QML；
DerivativeExecution；
Interfaces；
Devices/Noise；
H₂；
existing MPS and new MPSTangentJet；
Operator.power；
双版本公开 API 差分；
SDK-free 数值示例。
不能拿本轮 R2O3-A 的 3,137/3,135 个通过结果作为新源码的回归成绩。
12. 原 R2 最终冻结门禁
完成公开 QNode 集成与资源规划后，原 R2 全量验收依然必须执行：
SDK-free FULL；
Main Qiskit 2.4.1 / PennyLane 0.44.1 FULL；
Alternate Qiskit 2.6.0 / PennyLane 0.42.3 FULL；
Independent JAX FOCUS；
Independent TensorFlow FOCUS；
Torch/Autograd FOCUS；
显式 GLOBAL coverage；
原始未修改的 28-section matrix；
全部 SDK-free numerical examples；
controlled legal；
no-vendor/no-token；
五个实际 import origins；
frozen/worktree/staged/committed runtime equality。
Global line coverage 基线：
91.34108013033072%
。
Exclusions：
68，不得增加
。
若本批发现新的正确性失败，先修复、重新冻结再执行门禁；不能用旧 FULL 或 FOCUS 代替。
13. Git、权限与成果状态
继续 owner 已授权的 local-only 开发：
不 push、fetch、修改 OAuth/TLS；
不 reset/rebase/amend/force；
不安装依赖、不 vendor 上游源码；
不新增 Dongling 真机任务；
不修改既有金融 13 项硬件证据；
不继续 UI/Studio 或应用案例扩张；
保留已有 Studio/Router 脏文件和来源问题。
只有最终冻结及规定门禁真实完成后，才考虑 normal scoped local commit。
最终报告必须分别说明：
matrix_power_parameter_shift
 是否真正修复。
公开 QNode 的 MPS Jacobian/Hessian/HVP 是否实际执行。
与直接 MPSTangentJet kernel 之间的数学误差。
四框架一、二阶真实图结果。
Streamed HVP 是否没有完整 Hessian。
统一 DerivativePlan 与资源计量证据。
相邻、远线与 100-wire 的实际执行。
IR/QPY 保真与 Unsupported 范围。
三环境 FULL、GLOBAL 和 matrix 真实状态。
本地提交、远端 CI 和剩余 SDK 核心缺口。
下一步明确为：修复公开 QNode → MPS 的导数方法分派，再将已通过的非酉切向量 kernel 纳入 Host/Device 统一工作预算，最后打通四框架、IR/QPY 和 streamed HVP。
只有这条链通过真实测试，R2O3 才能从“直接 kernel 已实现”推进到“公开原生计算与高阶微分可执行”的支持子集。完整 Qiskit/PennyLane full replacement 继续保持 
ACTIVE / INCOMPLETE
。

