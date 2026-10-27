# Received R2O3 Prompt

Read from the actual assistant body in the authorized existing default-Chrome
conversation on2026-10-23, after transmitting the R2O2 terminal results.
Accessibility formula line splitting is retained. This is a received request,
not completed implementation or verified full-SDK acceptance.

Factual clarification: the new general moving-projector derivatives have
Statevector/adjoint evidence. Density and MPS evidence so far belongs to the
older fixed-projector subset; this prompt's opening must not be interpreted
as claiming general moving-projector Density/MPS derivatives already pass.

+下一段 Codex 执行 Prompt：Stage 12-B P4-U3D2-R2O3
Native Moving-Projector MPS Tangent Propagation & Mixed Fréchet Derivative Integrity
继续原 R2O2 和完整 R2，不新建独立 SDK 阶段，不进入 UI、金融诊断或应用案例。
最高目标保持：QuantumBridge 独立原生 Qiskit/PennyLane full functional parity/full replacement，
ACTIVE / INCOMPLETE
。
本段优先解决：将已通过小维度 Statevector/Density/Adjoint 的双参数矩阵幂微分，真正接入 
100-wire MPS 的非酉切向量传播
，同时补齐 mixed Fréchet 的对称性、近切线拒绝和多方向资源契约。
1. 先建立 MPS 导数幅度丢失红灯
不要直接修改现有 MPS 
_block_gate
 / 
_split
，先审计它们何时执行：
QR/SVD；
Schmidt 系数截断；
状态归一化；
bond dimension 控制；
奇异值归一化；
global scalar 丢弃。
构造一量子比特参数化状态：
∣
𝜓
(
𝜃
)
⟩
=
𝑅
𝑌
(
𝜃
)
∣
0
⟩
其导数范数一般不等于 1。对局部切向量应用现有 MPS Gate 入口，确认是否出现幅度丢失。
再构造真正非对易的：
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
op
 
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
要求在 100-wire MPS 上真实验证：
value；
∂p、∂q；
∂pp、∂pq、∂qq；
streamed HVP；
两个活动量子位相邻及远距离的情况。
先运行红灯并保留错误幅度的数值证据，再修改生产代码。
2. 实现原生 norm-preserving tangent MPS
在现有 MPS 引擎内部增加受控的非酉切向量更新能力，而不是创建第二套模拟器。
建议采用以下两种经过数学验证的方案之一：
方案 A：带显式 scale 的 MPS tangent state。
分解和截断时保留全局复数尺度因子：
纯文本
复制代码
TangentMPS = normalized_tensor_chain × complex_scale
每次非酉局部算子更新后，同时更新尺度，不能强制切向量范数为 1。
方案 B：未归一化的局部 tensor contraction。
允许切向量使用受控的非酉局部算子更新，保持真实振幅；正交化可以改变 gauge，但不能改变物理状态范数。
无论采用哪种方案，都必须验证：
复数尺度而非仅实数范数；
zero tangent；
very small tangent；
global phase derivative；
repeated tangent contributions；
MPS routing；
source state 不被修改；
copy 生命周期；
bond dimension 与 truncation error；
资源预算。
不能把 
dU
 伪装成合法酉 Gate。
3. 混合二阶导数必须传播所有贡献
对局部操作 
𝑈
(
𝑝
,
𝑞
)
 和状态 
∣
𝜓
⟩
：
∂
𝑝
𝑞
(
𝑈
∣
𝜓
⟩
)
=
𝑈
𝑝
𝑞
∣
𝜓
⟩
+
𝑈
𝑝
∣
𝜓
𝑞
⟩
+
𝑈
𝑞
∣
𝜓
𝑝
⟩
+
𝑈
∣
𝜓
𝑝
𝑞
⟩
实现必须保留四项。
如果只支持部分由 Gate 参数贡献、而不支持输入状态本身的切向量，不能宣称支持真正的多层参数化 Circuit。
至少使用两个连续、分别依赖不同参数的非对易 Gate，验证第二阶交叉项。
对期望值：
⟨
𝑂
⟩
=
⟨
𝜓
∣
𝑂
∣
𝜓
⟩
混合二阶导数必须同时包含 bra 与 ket 的相应贡献，不能只计算 ket 的二阶导数。
使用独立小规模 Statevector 解析结果作 oracle，再在 100-wire MPS 上运行同一局部线路。
4. 真正 streamed HVP
继续保护已经实现的八参数 HVP。
新 MPS 路径必须：
接收方向向量；
直接传播方向切向量；
不构造完整参数 Hessian；
不构造完整 Statevector；
不把方向数作为完整参数对矩阵预分配；
使用共享的 derivative work budget；
保留已有多输出 observable 的资源计量。
测试中明确禁止调用：
Python
复制代码
运行代码
compute_hessian
(...)
MPS
.
statevector(...)
StatevectorDevice
.
statevector(...)
DensityMatrixDevice
.
density_matrix(...)
并对整个 Circuit 的 dense Gate/Operator materialization 设置失败桩。
允许受预算限制的局部 2×2、4×4 或当前 MPS 支持的局部 block 运算。
5. Fréchet 数学对称性和方向契约
在不重写已有四块 kernel 的前提下，增加：
𝐿
𝑓
(
2
)
(
𝑈
;
𝐸
,
𝐺
)
 与交换方向的一致性；
对方向向量的线性性；
零方向；
同一方向；
重复参数 UUID；
不同 UUID 但相同 name；
多次 partial binding；
global phase 包含 
p*q
；
QPY/IR 后参数顺序；
Hessian 对称性；
JVP/VJP 对偶测试。
特别检查四块 
(0,3)
 输出提取时是否正确使用底层混合二阶输入项，且不存在额外的 
2!
 系数错误。
独立 oracle 不得调用生产的 
unitary_power_jet()
 或相同 block evaluator。
6. Branch-cut 数值保护
保留当前 
q≈2π±10^-4
 的真实失败与拒绝证据。
新增：
同分支、谱明确分离的计算成功；
跨 cut、但可可靠区分的导数成功；
±0.03 等已通过范围不回归；
fixed-projector 近 cut 快速路径不误拒；
exact cut 明确拒绝；
high sensitivity 的拒绝包含 gap、coupling、resolution、screen；
数值拒绝之前 source owner 和 Circuit 不改变。
不要为了让 near-cut 测试通过而改成无条件 Unsupported、放宽既有 
8e-11 / 3e-9
 容差或静默返回不可靠的有限导数。
同时在报告中明确：
这是保守数值筛查，不是严格的通用条件数证书。
7. 四框架真实微分图
Torch、Autograd、JAX 和 TensorFlow 分别运行：
first gradient；
mixed Hessian；
streamed HVP；
JVP；
VJP；
forward-over-reverse；
reverse-over-forward。
尤其回归 Autograd 的 
defjvp
、VJP 与二阶方向规则。
不得让新 MPS tangent engine 绕过框架的可微计算图，也不能仅把预先计算的 Hessian 包装为 Tensor。
JAX 测试明确启用 x64；既有缺依赖 skip 应实际报告。
8. 数学、格式与资源完整链
必须至少完成：
纯文本
复制代码
Generic Gate(p, q)


→ AnnotatedOperation(PowerModifier(0.5))


→ Native IR / QPY v13


→ Native QNode


→ 100-wire MPS


→ norm-preserving tangent propagation


→ Jacobian / mixed Hessian / streamed HVP


→ independent small-system oracle
保持 QPY v13 仅使用真正支持的 numeric exponent 和 symbolic base parameters。
Symbolic exponent 的标准 QPY Unsupported 不改变。
资源反例：
非酉 tangent 被错误按 unitary admission 处理；
SVD 丢失幅度；
scale overflow/underflow；
exact zero derivative；
truncation 后误差无法估计；
huge bond；
noncontiguous wires；
无界 direction iterable；
foreign ndarray callbacks；
malformed IR/QPY；
branch-cut derivative refusal；
循环定义和过深 modifier；
QNode 编译中途失败。
工作预算必须在危险 tensor expansion 或 dense materialization 前计量。
9. 测试与阶段验收
至少新增：
12 个 tangent amplitude 测试；
12 个双参数 mixed-state derivative 测试；
8 个 streamed HVP 测试；
8 个远距离 MPS wire 测试；
8 个四框架真实计算图测试；
8 个 IR/QPY 测试；
12 个资源与失败原子性反例。
先红后绿，不用增大 skip/xfail 或改写数学 oracle 达到绿色。
本段完成后执行最新源码的 Core/Circuit/Information/Serialization/Compiler/Gradients/QML/DerivativeExecution/Interfaces/Devices/Noise/H₂ 开发期宽回归，并与已有单参数、双参数专项测试同时验证。
10. 原 R2 完整门禁保留
只有当前受支持范围内不再存在已确认 correctness failure，且最新代码宽回归通过后，才进入原 R2 最终冻结。
必须执行：
SDK-free FULL；
Main Qiskit 2.4.1 / PennyLane 0.44.1 FULL；
Alternate Qiskit 2.6.0 / PennyLane 0.42.3 FULL；
Independent JAX FOCUS；
Independent TensorFlow FOCUS；
Torch/Autograd FOCUS；
显式 GLOBAL coverage；
未修改的 28-section local matrix；
全部 SDK-free 数值示例；
controlled legal；
五个 actual import origins；
frozen/worktree/staged/committed runtime equality。
GLOBAL 基线仍为 
91.34108013033072%
，exclusions 
68
 不增加。
旧的 5,076/921 宽回归不能作为最终版本验收。
RUNNING
 不记 PASS，FOCUS 不等于 FULL。
11. Git、任务权限和最终报告
继续 owner 的 local-only 限制：
不 push/fetch、不改 OAuth/TLS；
不重写历史；
不安装依赖、不复制上游 SDK 源码；
不新增 Dongling 任务；
不修改金融 13 项历史证据；
不进入 UI、Studio 或新行业案例；
保留已有 Studio/Router 工作区文件。
只有新冻结全量门禁完成，并核对受测代码与 scoped staged/committed runtime 完全一致后，才考虑正常本地提交。
最终报告必须分别回答：
MPS tangent 是否保留非酉导数的复数幅度。
双参数 mixed derivative 的全部乘积项是否正确。
Streamed HVP 是否真正没有生成完整 Hessian。
相邻与远距离活动 wires 的实际结果。
四框架计算图是否通过。
数值切线拒绝的范围与证据。
IR/QPY 的实际支持范围。
数学误差、资源和失败原子性。
三环境 FULL、GLOBAL、原始 matrix 的真实状态。
本地提交和远端 CI 状态。
尚未完成的通用 Qiskit/PennyLane 核心函数。
优先修复 MPS 中非酉 tangent normalization 的正确性风险，再扩展通用 moving-projector 的多参数执行。
即使本段通过，也只表示原生 MPS/Fréchet 的受支持子集进一步完善，不能自动宣称完整 R2O2、P4 或 full SDK 完成。
最终目标保持 
ACTIVE / INCOMPLETE
。
