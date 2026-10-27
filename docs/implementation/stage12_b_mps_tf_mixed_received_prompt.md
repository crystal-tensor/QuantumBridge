# Received R2O3-B-TF Prompt

Read from the completed actual assistant body in the authorized existing
Chrome conversation on 2026-10-23. Accessibility line splitting is retained.
The live Main broad session mentioned below has now naturally terminated
with 7016 passed / 2 failed / 1 skipped / 3 xfailed, exit1; it was not cancelled.
Received instructions do not prove execution or full replacement acceptance.

下一段 Codex 执行 Prompt：R2O3-B-TF
TensorFlow Forward/Reverse AD Semantics & Native MPS Second-Order Graph Repair
继续原 Stage 12-B P4-U3D2-R2O3-B，不另起 SDK 阶段，不进入 UI、云硬件、金融诊断或其他应用。
本段只聚焦已经确认的 TensorFlow 混合模式阻断。其余 MPS kernel、Fréchet 数学、四框架已通过子集及完整 R2 门禁全部保留。
1. 首先保持当前宽回归自然结束
session61808
 当前仍在运行。
不要因为已经知道两个 TF 红灯，就取消健康进程。让它自然终止，记录实际退出码和两个失败的详细 traceback。
若它最终失败，明确记录为本次真实开发回归失败，不视为最终验收。
不得把 Torch/Autograd/JAX 的成功结果代替 TensorFlow RoF 验收。
2. 建立纯 TensorFlow 诊断矩阵
新增独立测试脚本，例如：
tests/interfaces/probes/probe_tf_mixed_ad_semantics.py
该脚本不能 import QuantumBridge，也不能 import Qiskit/PennyLane。
使用纯 TF 数学函数：
Python
复制代码
运行代码
def
 
f
(
x
):
    
return
 
tf
.
sin(
x
)
def
 
loss
(
x
):
    
return
 
tf
.
square(
f
(
x
) 
-
 
0.3
)
在以下四种条件下分别运行：
eager + ForwardAccumulator 外层、GradientTape 内层；
eager + GradientTape 外层、ForwardAccumulator 内层；
tf.function(autograph=False)
 + 第一种嵌套；
tf.function(autograph=False)
 + 第二种嵌套。
还要分别观察 
.jvp()
 在 Tape 内部和外部读取时的结果。
另外使用纯 TensorFlow：
Python
复制代码
运行代码
with
 
tf
.
GradientTape() 
as
 
outer
:
    
outer
.
watch(
x
)
    
with
 
tf
.
GradientTape() 
as
 
inner
:
        
inner
.
watch(
x
)
        
y
 
=
 
loss
(
x
)
    
grad
 
=
 
inner
.
gradient(
y
, 
x
)
hvp
 
=
 
outer
.
gradient(
grad
 
*
 
v
, 
x
)
作为公开 Tape-over-Tape 基准。
每个实验记录：
primal；
JVP；
gradient；
HVP；
解析期望值；
dtype；
TF 版本；
eager / traced 状态；
graph nesting；
实际错误或结果。
诊断目标：确认哪一种公开组合正确传播全部二阶项，而不是寻找一个恰好返回预期数字的嵌套方式。
纯 TF 探针结果必须单独归档，不能把它的通过当成 QuantumBridge 已修复。
3. 给纯 TF 增加两个不同形态的函数
除 
sin(x)
 外，再加入：
A. 二参数非线性函数
Python
复制代码
运行代码
def
 
f
(
x
):
    
p
, 
q
 
=
 
x
[
0
], 
x
[
1
]
    
return
 
tf
.
sin(
p
) 
*
 
tf
.
cos(
q
) 
+
 
p
 
*
 
q
B. 纯 TensorFlow 自定义梯度函数
使用公开 
@tf.custom_gradient
，显式验证一阶 VJP 与二阶依赖。
测试包括：
FoR；
RoF；
JVP；
VJP；
nested second derivative；
非线性外部 loss。
这里必须区分 TensorFlow 的自定义 gradient function 对 
dy
 的转置导数，以及真正对原输入 
x
 的二阶导数。
不能只检查一阶结果。
4. 先确定 TensorFlow 的正确公开模式，再修改 QuantumBridge
如果纯 TensorFlow 某一种合法的 Tape/Accumulator 嵌套能够获得正确 RoF：
优先让 QuantumBridge 接口遵守同一调用结构，并确保 
tf.function
 内外一致。
如果纯 TF 自定义梯度默认不能保留完整 RoF：
依照官方公开的嵌套 
@tf.custom_gradient
 模式，为 QuantumBridge 的 native QNode 自定义梯度补充真正的二阶链式规则。
建议以两个明确的可微对象为边界：
原生 QNode value 
𝑓
(
𝜃
)
；
原生一阶 VJP 
𝐽
𝑓
𝑇
𝑢
，并为这个 VJP 对输入参数的导数定义 Hessian contraction。
外部 TensorFlow loss 继续由 TensorFlow 自己构图。
这样 TF 在求：
纯文本
复制代码
loss = (native_qnode(x) - 0.3)^2
时，可以通过标准链式法则获得完整二阶贡献。
不要将外部损失函数写死在 QuantumBridge 的自定义梯度中。
5. 自定义梯度的二阶契约
设 Native QNode 输出 
𝑦
=
𝑓
(
𝜃
)
。
必须具备：
VJP
⁡
(
𝑢
)
=
𝐽
𝑓
𝑇
𝑢
及其对参数的方向导数：
𝐷
𝜃
[
VJP
⁡
(
𝑢
)
]
 
𝑣
=
𝐻
𝑓
(
 
⋅
 
,
𝑣
)
𝑇
𝑢
同时，VJP 对上游 cotangent 
𝑢
 的导数仍要返回 Jacobian 对应的线性转置关系。
这两种导数不能混淆。
对于多输出 QNode，必须测试不同输出的 cotangent 权重；对于 direction HVP，只请求实际需要的 directional Hessian contraction，不构造完整 Hessian。
使用现有 native Fréchet/MPSTangentJet/DerivativeExecution 计算正确方向贡献，TensorFlow adapter 仅负责把这些贡献以公开可微规则连接成计算图。
不允许：
将已经计算好的完整 Hessian 包装成 Tensor；
私有全局 JVP registry；
tf.py_function
 的默认梯度冒充二阶支持；
通过 
tf.stop_gradient
 删除本应存在的二阶依赖；
用有限差分作为生产导数；
将缺失项硬编码进特定 loss。
6. 针对当前数字的阻断测试
保留你现有的真实 QNode：
𝜃
=
(
0.37
,
0.82
)
；
𝑣
=
(
0.4
,
−
0.3
)
；
𝑓
=
0.9822051865077258
；
loss=(f-0.3)**2
。
要求 TF 最终 RoF 的结果与：
Python
复制代码
运行代码
expected
 
=
 (
    
2.0
 
*
 
np
.
dot(
g
, 
v
) 
*
 
g
    
+
 
2.0
 
*
 (
f
 
-
 
0.3
) 
*
 
native_hvp_f
)
相符。
必须单独验证：
2(g·v)g
；
2(f-0.3)H_fv
；
两项合计。
在 TensorFlow 最终图中明确证明第二项没有被丢弃。
并增加一个不同外部 loss，例如：
Python
复制代码
运行代码
loss
 
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
以排除为平方损失特判。
7. 四框架与 MPS 保护
TF 修复不能损害：
Torch forward_ad；
Torch RoF/FoR；
Autograd defjvp；
JAX JIT/JVP/VJP；
普通 Gate parameter-shift；
固定投影 fractional power；
moving-projector Fréchet；
100-wire MPS；
IR/QPY；
global phase/open control。
必须继续禁止 100-wire 路径上的全线路 dense materialization。
尤其保持 
max_mps_tangent_components
、
SecondWork
、NativeHost 与 Device work admission 的统一计量，不为了 TF 图成功绕过资源预检。
8. 如果 TF 2.21 的公开模式仍不支持
若独立测试显示，当前已安装 TF 2.21 在严格要求的 RoF 嵌套组合下无法正确传播二阶项，并且使用公开 API 的合法自定义导数结构仍无法修复：
保留现有明确 typed refusal；
不返回错误的有限 HVP；
报告最小纯 TF 复现；
列明具体受影响的调用组合；
继续支持已经真实验证正确的 TF 一阶、普通二阶或 FoR 子域；
将 RoF 标记为 
BLOCKED_BY_FRAMEWORK_INTEGRATION
，而非完成。
这只是在本次开发检查点中记录尚未关闭的阻断，不意味着降低最终 full SDK replacement 的目标。
9. 完成后的验证门禁
先运行：
纯 TF probe；
Native TF interface tests；
QNode/MPS moving-power tests；
mixed Hessian/HVP；
多输出 transpose；
Torch/Autograd/JAX 相关回归；
NativeHost/resource guards。
只有新增红灯真正绿色，才运行最新代码的宽范围开发回归。
原 R2 全量冻结验收继续保留：
SDK-free FULL；
Main FULL；
Alternate FULL；
Independent JAX/TF；
Torch/Autograd；
GLOBAL coverage 不低于 
91.34108013033072%
；
exclusions 
68
 不增加；
原始 28-section matrix；
全部 SDK-free 数值示例；
controlled legal；
五个 import origins；
frozen/staged/commit equality。
RUNNING
 不等于 PASS，局部 FOCUS 不等于 FULL，任何失败必须如实记录。
保持 Git local-only、不安装依赖、不修改凭据/OAuth、不新增硬件任务、不碰 Studio/Router 和金融原始数据。
下一步应先确定纯 TensorFlow 的正确嵌套二阶语义，再在 
tensorflow_graph
 adapter 中实现输入方向与上游 cotangent 两条真正独立的导数规则。
目前证据最强的判断是：
缺失项并非 Native HVP 没算出来，而是 TensorFlow 混合 AD 图没有正确传播它。
 这需要通过上面的纯 TF 诊断矩阵进一步定位。
R2O3-B 继续 
IN_PROGRESS
，完整独立原生 Qiskit/PennyLane full functional parity/full replacement 继续 
ACTIVE / INCOMPLETE
。

