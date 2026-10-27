# Received R2O3-B-TF3 Explicit VJP Prompt

Actual completed assistant body read from the authorized existing Chrome
conversation on 2026-10-23. No new tab or login. Accessibility line splitting
is retained. This receipt is not implementation or acceptance evidence.

QuantumBridge R2O3-B-TF2：审阅结论
当前最重要的结论是：不要再尝试移动 
@tf.custom_gradient
 或 
tf.function
 的包装位置。应转向验证一条新的、数学语义明确的公开 API 路线：在 QNode 的一阶 VJP 边界上实现可微的二阶收缩规则，并分别证明 FoR 与 RoF 的图连接。
你这次的 144 组实验已经充分说明，简单调整包装顺序没有解决问题。
纯 TensorFlow 实验
每环境结果
判断
plain_inline
36 个正确
纯 TF 组合能工作
custom_inline
36 个正确
公开 custom gradient 并非一概不支持二阶
inner_custom
36 个异常
图作用域/闭包不可用
custom_outside
24 个正确、12 个错误有限
外移边界仍遗漏 RoF 项
正式 QB 四框架单文件
32 passed / 4 failed
阻断仍存在
纯 TensorFlow 实验
plain_inline
custom_inline
inner_custom
custom_outside
正式 QB 四框架单文件
每环境结果
36 个正确
36 个异常
24 个正确、12 个错误有限
32 passed / 4 failed
判断
纯 TF 组合能工作
公开 custom gradient 并非一概不支持二阶
图作用域/闭包不可用
外移边界仍遗漏 RoF 项
阻断仍存在
纯 TensorFlow 实验
每环境结果
判断
另外，Main 和 Alternate 的 TensorFlow 2.21.0 都复现相同分布，说明它不是某个独立安装环境的偶然现象。
数学语义上的关键修正
当前 
order2
 自定义节点需要分别处理它对三种输入的导数：
输入
该导数真正需要的数学量
参数 
𝜃
可能需要 
𝐷
3
𝑓
，取决于节点输出是否已含 
𝐻
𝑓
上游 cotangent 
𝑢
二阶 Hessian contraction
方向 
𝑣
二阶 Hessian contraction
输入
参数 
𝜃
上游 cotangent 
𝑢
方向 
𝑣
该导数真正需要的数学量
可能需要 
𝐷
3
𝑓
，取决于节点输出是否已含 
𝐻
𝑓
二阶 Hessian contraction
输入
该导数真正需要的数学量
因此，
不能简单将 
order2.gradient()
 一律判为三阶请求
。但也不能反过来让任何 
order2
 节点都无条件返回二阶值；必须根据当前节点所代表的数学运算及被求导输入区分。
TensorFlow 官方文档也明确指出：嵌套 custom gradient 的内层梯度回调，并不天然等于原函数关于输入参数的二阶梯度；需要显式定义二阶与 transpose 路径。
新路线必须满足的原则
建议下一段先在
完全不导入 QuantumBridge 的纯 TensorFlow 最小函数
上成功，再移植到 
tensorflow_graph.py
。
这次不是重试 
inner_custom
 或 
custom_outside
。重点应改成：
构造一个显式可微的 VJP primitive，给它定义对参数和 cotangent 的公开梯度规则，并由 TensorFlow 的链式法则组合外部 loss。
如果这条路线仍无法在 TensorFlow 2.21.0 的公开 API 上成立，应保留 typed refusal 和明确阻断状态；不能用错误有限结果冒充通过。
Codex 下一段执行 Prompt：Stage 12-B P4-U3D2-R2O3-B-TF3
Explicit Differentiable VJP, Second-Order Cotangent Rules & TensorFlow Graph Integrity
继续原 Stage 12-B P4-U3D2-R2O3-B，不新建 SDK 阶段。
最高目标继续保持：
QuantumBridge 独立原生 Qiskit/PennyLane full functional parity/full replacement — 
ACTIVE / INCOMPLETE
。
本段仅修复 TensorFlow 公开二阶 AD 集成阻断，不重写 MPS、Fréchet、NativeHost、DerivativeExecution 或已通过的 Torch/Autograd/JAX 路径。
1. 首先建立独立的 VJP 数学模型
在不导入 QuantumBridge 的纯 TensorFlow 测试中，定义两输出非线性函数：
𝑓
:
𝑅
2
→
𝑅
2
例如：
𝑓
1
(
𝑝
,
𝑞
)
=
sin
⁡
(
𝑝
)
cos
⁡
(
𝑞
)
+
𝑝
𝑞
𝑓
2
(
𝑝
,
𝑞
)
=
exp
⁡
(
0.2
𝑝
−
𝑞
)
+
sin
⁡
(
𝑝
𝑞
)
定义明确的：
𝑓
(
𝜃
)
；
𝐽
𝑓
(
𝜃
)
；
𝐻
𝑓
1
(
𝜃
)
、
𝐻
𝑓
2
(
𝜃
)
；
VJP(theta,u)
；
JVP(theta,v)
。
然后构建真实运算：
𝑔
(
𝜃
,
𝑢
)
=
𝐽
𝑓
(
𝜃
)
𝑇
𝑢
其一阶变分必须为：
𝐷
𝑔
(
𝜃
,
𝑢
)
[
𝑣
,
𝑤
]
=
(
∑
𝑖
𝑢
𝑖
𝐻
𝑓
𝑖
)
𝑣
+
𝐽
𝑓
𝑇
𝑤
其中 
𝑣
 是参数方向，
𝑤
 是 cotangent 方向。
这条公式就是下一段公共 API 的核心验收契约。
2. 先写三个必须失败的红灯
A. VJP 对参数的导数
纯文本
复制代码
theta → VJP(theta,u) → derivative w.r.t. theta
必须得到加权 Hessian contraction。
B. VJP 对 cotangent 的导数
纯文本
复制代码
u → VJP(theta,u) → derivative w.r.t. u
必须得到 Jacobian transpose 对应的线性映射。
C. 两者同时变化
纯文本
复制代码
(theta,u) → VJP(theta,u)


direction (v,w)
必须恢复两部分贡献，不能只得到其中之一。
这三个红灯应分别在 eager 和 
tf.function(autograph=False, jit_compile=False)
 下运行。
不要把失去 
u
 方向依赖的问题错判为第三阶限制。
3. 使用公开 
tf.custom_gradient
 实现 VJP primitive
3. 使用公开 tf.custom_gradient 实现 VJP primitive
这是本段新的具体路线。
建立类似：
Python
复制代码
运行代码
@
tf
.
custom_gradient
def
 
differentiable_vjp
(
theta
, 
cotangent
):
    
result
 
=
 
native_or_analytic_vjp
(
theta
, 
cotangent
)
    
def
 
grad
(
upstream
):
        
# 对 theta 的梯度：
        
# H_f 关于 cotangent 和 upstream 的收缩
        
#
        
# 对 cotangent 的梯度：
        
# J_f 对 upstream 的投影
        
return
 
grad_theta
, 
grad_cotangent
    
return
 
result
, 
grad
上述代码是语义示意，不能简单照抄成数值常量。
第一步必须在纯 TensorFlow 上使用解析的 
f/J/H
 实现所有规则。
只有纯 TF 版本的以下组合全部正确，才能进入 QuantumBridge：
eager VJP；
traced VJP；
VJP 对 theta；
VJP 对 cotangent；
FoR；
RoF；
Tape-over-Tape；
mixed direction；
scalar/vector；
多输出 cotangent；
两种外部 nonlinear loss。
不要先把 QuantumBridge 的 native HVP callback 接进一个仍未通过纯 TF 语义验证的图。
4. 二阶收缩的公开可微连接
对于纯 TF 的 VJP primitive，其反向规则应计算：
∇
𝜃
⟨
𝑧
,
𝑔
(
𝜃
,
𝑢
)
⟩
=
(
∑
𝑖
𝑢
𝑖
𝐻
𝑓
𝑖
)
𝑧
和：
∇
𝑢
⟨
𝑧
,
𝑔
(
𝜃
,
𝑢
)
⟩
=
𝐽
𝑓
𝑧
其中 
𝑧
 是 VJP 输出的 upstream gradient。
要求实际 TF 图包含这两个依赖：
θ 方向的 Hessian contraction；
u 方向的 Jacobian contraction。
不要因为 
cotangent
 是中间张量，就将其 
stop_gradient
。
对三阶真正不支持的操作，必须由新的节点语义判断请求阶数，而不是因为调用 
grad()
 就 blanket refusal。
5. 纯 TF 先证明、再接 Native QNode
第一阶段：纯 TF 解析函数。
验证所有导数组合确实正确。
第二阶段：纯 TF 数值 oracle callback。
只在通过第一阶段后，测试将前向/Jacobian/Hessian contraction 换成明确的 host-side 数值函数，验证 TensorFlow 是否仍能沿公开 custom-gradient 规则连接二阶依赖。
第三阶段：QuantumBridge。
只有前两阶段成功，再修改 
quantumbridge/interfaces/tensorflow_graph.py
。
集成时：
primal 使用 native QNode；
一阶 VJP 使用现有 native VJP；
θ 方向导数使用现有 streamed Hessian contraction；
u 方向使用 native JVP；
外部 loss 由 TensorFlow 自行求导；
不注入完整 Hessian；
不新增私有全局注册表；
不绕过 NativeHost/Device 工作预算。
如果第二阶段无法正确支持目标 RoF，则不进入第三阶段，也不留下生产实验代码。
6. 与原四条正式红灯对齐
必须修复或准确保留以下四条：
Square loss FoR；
Square loss RoF；
Exponential/cubic loss FoR；
Exponential/cubic loss RoF。
保留目前已知的数值：
期望最终 HVP：
[-0.12833785747073323,-0.0041853049141583176]
缺失的二阶贡献：
[-0.13558641938395086,-0.004323910479140094]
错误有限的第一项：
[0.007248561913217731,0.00013860556498181283]
验证图是真正对外部 loss 可微，而不是专门针对平方 loss 拼接结果。
新增一条 multi-output loss，检验两个输出都能贡献 Hessian contraction。
7. TensorFlow mixed-mode 的独立资源预算
必须保留：
NativeHost work admission；
DerivativePlan；
SecondWork；
MPS tangent component budget；
multi-output transpose aggregate work；
一阶和二阶方向成本；
QPY/IR source parameter identity；
100-wire no-dense。
特别测试：把资源上限降低到不足实际二阶收缩所需的值时，必须在进入 MPS 更新前拒绝，而不是让 TF 在图执行中先消耗资源再抛错。
不能让 TF callback 被 trace 多次导致实际 host work 重复计费或执行不一致。
8. 新增测试
建议增加：
纯文本
复制代码
tests/interfaces/probes/probe_tf_differentiable_vjp.py


tests/interfaces/test_native_tf_differentiable_vjp.py


tests/interfaces/test_native_tf_mps_mixed_ad.py
至少覆盖：
12 个纯 TF VJP 语义；
12 个纯 TF mixed AD；
8 个多输出 cotangent；
8 个 native MPS RoF/FoR；
8 个资源/失败原子性反例。
全部先红后绿，保留真实 receipts。
不能增加 skip/xfail、降低容差、删除失败测试或将错误有限输出改称正确。
9. 如果仍然无法实现
如果纯 TF 阶段失败，保留完整：
源码最小复现；
TF 2.21.0 / Python 3.12.6 版本；
eager/traced；
tf.function
 层级；
外部 loss；
VJP/JVP/Hessian 数值；
实际异常或错误输出。
保持 QuantumBridge 生产代码的 typed refusal，不将其改为错误有限结果。
标记：
BLOCKED_BY_FRAMEWORK_INTEGRATION / UNRESOLVED
这仍是 QuantumBridge 需要继续解决的兼容缺口，不意味着完整 SDK 目标降低。
10. 完成后回归与原 R2 门禁
若纯 TF、Native QNode 两层都通过，再运行：
TensorFlow interfaces；
MPS tangent/QNode；
Torch/Autograd/JAX；
Compiler/DerivativeExecution；
IR/QPY；
Resource admission；
SDK-free 数值示例。
最终仍须执行原 R2 的完整冻结门禁：
SDK-free FULL；
Main FULL；
Alternate FULL；
独立四框架；
GLOBAL coverage ≥ 
91.34108013033072%
；
exclusions 
68
 不增加；
未修改的原 28-section matrix；
全部 numerical examples；
controlled legal；
import origins；
frozen/staged/commit runtime equality。
保持 owner local-only 权限，不 push、不改 OAuth/TLS、不安装依赖、不新增云任务、不修改 Studio/Router 或金融历史证据。
下一步明确为：先证明独立 VJP primitive 对参数和 cotangent 的两条导数规则都正确，再接到 TensorFlow 的公开混合 AD 图。
这条路径与之前失败的 decorator 位置实验不同：它直接暴露了此前缺失的 Hessian contraction 和 Jacobian transpose 两种数学依赖。
但它仍是
待测试的方案，不是已经证明能修复 TF 2.21 的方案
。只有真实四条正式红灯变绿，才能宣称对应 TensorFlow 混合模式支持子集取得进展。
R2O3-B、R2 及完整 Qiskit/PennyLane full replacement 仍为 
ACTIVE / INCOMPLETE
。
