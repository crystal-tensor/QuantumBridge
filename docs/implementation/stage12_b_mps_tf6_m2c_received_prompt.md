# Received TF6-M2C Trace-Inline Boundary Prompt

Actually read on2026-10-24 in the authorized existing default Chrome
conversation after the service marked the response completed and a verified
reload exposed its full body. No new tab/login. Accessibility line splitting
is preserved. This is guidance based on reported evidence, not independent
source inspection, acceptance, or proof of implementation.

QuantumBridge TF6-M2B：CONTROLLED-CACHE-61 检查点审阅
结论：M2B 的受控显式缓存查询与共享资源账本已有真实专项测试证据，但可调用缓存图的外部自动微分边界仍未解决，M2 不能验收，也不能进入 M3。
这次最重要的进展，是把资源管理从原先的 eager Whole-QNode 扩展到受控的缓存执行句柄，同时发现并修复两个真实资源问题：
Owner 失效后，原有资源配置可能被绕过；现在失效 owner 会被拒绝。
二阶组合规则中，HVP 与 JVP 工作量合并后没有完整重新检查 HigherOrder/Device 限额；现在增加了聚合检查。
这些是实质性的原生资源正确性修复。
验收项
你的本地报告
Main / Alternate 最新预算、生命周期、并发专项
各 61 passed
SDK-free request/Device 回归
849 passed / 25 skipped
Managed 显式 value/JVP/VJP/HVP/Hessian
有真实计算与资源测试
Callable cached graph 的外部 loss RoF
2 条正式红灯仍失败
原 100-wire TensorFlow 四条红灯
4 failed
M2
PARTIAL
M3
NOT
_
STARTED
三环境 FULL / GLOBAL / 原始 matrix
NOT
_
RUN
Full independent SDK replacement
ACTIVE / INCOMPLETE
验收项
Main / Alternate 最新预算、生命周期、并发专项
SDK-free request/Device 回归
Managed 显式 value/JVP/VJP/HVP/Hessian
Callable cached graph 的外部 loss RoF
原 100-wire TensorFlow 四条红灯
M2
M3
三环境 FULL / GLOBAL / 原始 matrix
Full independent SDK replacement
你的本地报告
各 61 passed
849 passed / 25 skipped
有真实计算与资源测试
2 条正式红灯仍失败
4 failed
PARTIAL
NOT
_
STARTED
NOT
_
RUN
ACTIVE / INCOMPLETE
验收项
你的本地报告
本次最关键的判断
受控显式查询接口应当保留，并从 callable 外部自动微分能力中明确拆开验收。
已经测试通过的显式 
managed.value()
、
managed.jvp()
、
managed.vjp()
、
managed.hvp()
 和 
managed.hessian()
 可以作为当前受支持子域，但必须继续维护现有资源限制和数学正确性。
另一方面，
managed(theta)
 放入任意外部非线性 TensorFlow loss，再通过缓存 ConcreteFunction 进行 RoF，仍存在实际错误。它不应因显式 HVP 已通过而被标记为二阶可微。
纯 TF 对照也已在两个环境复现相关错误，说明问题不仅发生于 QuantumBridge；但这
不能证明是 TensorFlow 2.21 的普遍缺陷
。
TensorFlow 官方文档明确说明，
tf.function
 的缓存图执行不会重跑 tracing 时的 Python 副作用，而嵌套 custom gradient 的高阶传播也需要区别对上游 cotangent 和输入参数的求导。
本审阅仅依据你提供的本地执行报告。我没有独立检查未提交源码或远端 CI。
下一段 Codex 执行 Prompt：Stage 12-B P4-U3D2-R2O3-B-TF6-M2C
Cached-Graph AD Boundary Isolation, Trace-Inline Differentiation & Managed Execution Contracts
继续原 M2B 和完整 R2，不进入 M3，不重写现有 Compiler、NativeHost、Fréchet、MPS 或统一账本。
0. 本段目标
本段只解决三个问题：
确认为什么已缓存的 ConcreteFunction 在外部 RoF 中丢失二阶项。
尝试一条尚未充分验证的公开 API 路线：在外部 TF 图 tracing 时内联现有原生 TF 执行计算图，而不是调用内部已缓存 ConcreteFunction。
若第二条路线不能安全成立，则正式隔离 callable AD 能力，并完成 M2 当前可保证的显式查询与受控资源契约。
保留目前已通过的 61 项资源测试和原有 2 条 callable RoF 正式红灯。
1. 首先把缓存执行与可微执行分为两个不同合同
建议当前公共行为明确区分：
执行形式
当前目标合同
managed.value(theta)
已验证受控显式查询
managed.jvp/vjp/hvp/hessian(...)
已验证的受支持数学和资源子域
managed.cached_value(theta)
受控缓存图数值执行，需验证账本
managed(theta)
 + 一阶 AD
按实际测试声明
managed(theta)
 + 外部二阶 FoR/RoF
未关闭，不能承诺正确
直接调用内部 ConcreteFunction
OUT_OF_SCOPE
外部任意 TF loss 的资源消耗
OUT_OF_SCOPE
执行形式
managed.value(theta)
managed.jvp/vjp/hvp/hessian(...)
managed.cached_value(theta)
managed(theta)
 + 一阶 AD
managed(theta)
 + 外部二阶 FoR/RoF
直接调用内部 ConcreteFunction
外部任意 TF loss 的资源消耗
当前目标合同
已验证受控显式查询
已验证的受支持数学和资源子域
受控缓存图数值执行，需验证账本
按实际测试声明
未关闭，不能承诺正确
OUT_OF_SCOPE
执行形式
当前目标合同
实际 API 名称服从已有代码，不必创建 
cached_value
，也不要凭此表虚构已经存在的接口。
阻断性要求：在修复前，不能让错误的 cached RoF 返回有限值而被认为执行成功。
对于能够可靠识别的受控接口，采用明确的能力声明及提前拒绝；对于无法在调用前判定的任意外部 AD 嵌套，不得宣称具有普遍拦截能力。必须记录这种拦截能力的边界。
2. 新路线：Trace-inline differentiable execution
已有纯 TF 实验显示：
plain_inline
 和 
custom_inline
 的目标混合导数正确；
调用某些已缓存内层 
tf.function
 时会出错；
调整包装位置、NumPy callback、VJP callback 等路线均未解决。
因此，本段只验证一个新的结构：
纯文本
复制代码
External GradientTape / ForwardAccumulator


               ↓


Outer user tf.function tracing


               ↓


QuantumBridge managed differentiable callable


               ↓


Emit existing TF Whole-QNode ops directly


into the current active TensorFlow graph


               ↓


External nonlinear loss


               ↓


TF native mixed autodiff
关键区别：可微 callable 不调用内部已缓存的独立 ConcreteFunction。
它仍复用：
原有 
ExecutionPlan.lowered()
；
TensorFlowLocalOperator
；
tensorflow_native_math
；
原生参数 identity；
原有资源规划；
已验证的 TensorFlow Whole-QNode 数学。
这不是第二条量子线路或新编译器，而是同一计划的两种 TensorFlow 执行边界。
不得在训练参数路径中调用 NumPy callback。
3. 先用独立纯 TF 实验证明
建立完全不导入 QB 的小型 probe。
比较：
A. Cached-inner
纯文本
复制代码
outer tf.function


→ inner cached tf.function


→ loss


→ mixed AD
B. Trace-inline
纯文本
复制代码
outer tf.function


→ ordinary Python callable emitting tf.ops


→ loss


→ mixed AD
C. Eager-inline
纯文本
复制代码
GradientTape / ForwardAccumulator


→ ordinary Python callable emitting tf.ops


→ loss
保留相同的 scalar、vector、complex 和 nonlinear loss。
必须检验：
FoR；
RoF；
Tape-over-Tape；
JVP/VJP；
eager/traced；
repeated calls；
input signature；
trace count；
是否出现内层独立 FunctionDef 调用边界。
只使用公开 TF API，不检查或修改 TensorFlow 私有梯度注册表。
如果 B 不能通过原先的解析数学 oracle，
不得进入 QuantumBridge 生产集成
。
4. Trace-inline 的资源语义必须单独定义
这里存在关键限制：
在 Python callable 被外层 
tf.function
 
trace 
时，QuantumBridge 
的 
Python 
入口只执行 
tracing，不会随着已缓存外层图的每次执行重新调用。
因此不得声称 
trace-inline 
自动拥有 
M2B 
cached 
managed 
handle 
的逐次账本保证。
建议将两者明确区分：
Managed 
explicit 
cached 
execution
通过 
QB 
受控 
Python 
句柄逐次调用。
使用现有 
UnifiedResourceLedger。
适用显式 
value/JVP/VJP/HVP/Hessian 
合同。
保证范围限定于已验证的同步 
CPU 
调用。
Trace-inline 
differentiable 
execution
在 
TF 
当前可微图中生成受支持量子运算。
有静态计划上界和 
TF 
运行期数值断言。
不承诺外部任意图每次执行时 
Python 
ledger 
逐次扣账。
外部图执行和 
allocator 
标记 
OUT_OF_SCOPE 
/ 
ESTIMATED_ONLY
。
若 
active 
ResourceScope 
要求逐次资源记账且无法保障，应明确拒绝进入该模式。
这两种合同不可互相冒充。
5. 
QuantumBridge 
低量子位最小红灯
5. QuantumBridge 低量子位最小红灯
只有纯 
TF 
trace-inline 
通过后，才新增受控 
QB 
测试。
复用现有 
M1 
的两个参数 
moving-projector 
QNode，验证：
不重新编译 
Circuit；
不复制 
operation 
store；
不绕过 
Parameter 
UUID；
不使用旧 
GraphKernel.evaluate；
不调用 
TensorFlow 
host 
quantum 
callback；
不调用内部缓存 
ConcreteFunction；
数学结果与原 
Native 
Whole-QNode 
一致。
运行：
Python
复制代码
运行代码
with
 
tf
.
GradientTape() 
as
 
tape
:
    
with
 
tf
.
autodiff
.
ForwardAccumulator(
theta
, 
direction
) 
as
 
fw
:
        
value
 
=
 
native_qnode
(
theta
)
        
loss
 
=
 (
value
 
-
 
0.3
) 
**
 
2
    
tangent
 
=
 
fw
.
jvp(
loss
)
hvp
 
=
 
tape
.
gradient(
tangent
, 
theta
)
还需采用正确的 
Tape/Accumulator 
嵌套方式分别验收 
FoR 
与 
RoF，不能用单一代码结构冒充全部方法。
必须通过：
原平方 
loss；
exponential/cubic 
loss；
multi-output 
cotangent；
mixed 
Hessian；
JVP/VJP；
eager；
outer 
traced；
重复调用。
不修改原有数学容差和正式测试。
6. 
防止“数学通过，资源合同失真”
6. 防止“数学通过，资源合同失真”
新执行分派必须在选择 
trace-inline 
前完成：
原生计划身份验证。
全部 
operation 
capability 
scan。
method 
和 
max_diff
 
审核。
输出、方向、参数形状检查。
静态工作空间预算。
ResourceScope 
合同检查。
TF 
参数依赖的运行时断言。
如果调用发生在无法逐次记账的外部缓存图内，必须明确标记其受控保证范围。
不能为了让 
RoF 
通过，暗中把 
managed 
cached 
execution 
改为不记账的 
trace-inline。
此外，保留：
invalid 
owner 
refusal；
aggregate 
HVP/JVP 
工作量；
full 
Hessian 
的独立上限；
max_hessian_elements=1
 
下 
streamed 
HVP；
多线程竞争；
scope 
退出；
plan/config 
identity 
变化；
runtime 
NaN/Inf/cut 
guard。
7. 
若 
trace-inline 
可行，才考虑可微公开接口
7. 若 trace-inline 可行，才考虑可微公开接口
优先把它实现成
明确选择的执行模式
，而不是无条件替换现有 
managed(...)
。
例如：
Python
复制代码
运行代码
qnode
(..., 
interface
=
"tensorflow"
, 
execution_mode
=
"differentiable_inline"
)
这只是建议接口形式。实际必须先审计 
QuantumBridge 
现有调用参数与公共 
PennyLane 
兼容层，避免引入错误的 
ABI。
特别要求：
默认模式不因为新选项而改变已验证的普通 
parameter-shift/adjoint。
可微内联模式只接受完整支持的 
operation 
graph。
对 
active 
managed 
ResourceScope 
下无法逐次计账的外部 
graph 
明确拒绝。
不能为了匹配返回类型而让旧路径返回错误 
HVP。
此接口若通过低量子位数学测试，可标记为：
TF_TRACE_INLINE_DIFFERENTIABLE_LOW_QUBIT_SUBSET
它不是 
M2 
全域完成，也不是 
M3。
8. 
如果 
trace-inline 
仍失败
8. 如果 trace-inline 仍失败
若新的纯 
TF 
及 
QB 
实验仍不能完整通过：
保留生产 
TF 
adapter 
当前已验证功能；
不留下失败实验代码；
保留原 
2 
条 
cached 
callable 
RoF 
红灯；
继续明确的 
typed 
refusal；
报告 
CACHED_CF_EXTERNAL_ROF_UNRESOLVED
；
将 
M2 
保持 
PARTIAL
。
不再重复尝试已经失败的 
decorator 
移位、linear 
slots、host 
callback 
transpose、
IdentityN
、私有全局 
JVP、Hessian 
包装或停止梯度。
9. 
新增最小测试
9. 新增最小测试
建议：
纯文本
复制代码
tests/interfaces/probes/probe_tf_trace_inline_boundary.py


tests/interfaces/test_native_tf_trace_inline_qnode.py


tests/interfaces/test_native_tf_execution_mode_contracts.py


tests/interfaces/test_native_tf_trace_inline_resources.py
重点是 
12–20 
个相互独立的可证伪场景，
不要再通过排列组合数百个参数网格替代真实功能验证
。
最低必须包括：
原两个 
cached 
RoF 
红灯；
两个 
nonlinear 
loss；
eager/traced；
mixed 
derivative；
受控 
scope；
cached 
graph 
复用；
invalid 
owner；
plan 
mutation；
资源不足零执行；
source 
不变；
direct 
ConcreteFunction 
OUT_OF_SCOPE
；
方法及阶数限制。
10. 
M2 
继续条件
10. M2 继续条件
本段完成后分别报告：
A. 
Managed 
explicit 
cached 
queries
逐项说明实际已支持操作、ledger、数学及所有权。
B. 
Callable 
external 
mixed 
AD
明确区分 
cached-inner、trace-inline，以及 
eager 
模式的成功或失败。
C. 
Resource 
guarantees
准确区分逐次记账、静态上界、运行时断言和外部图不可观测工作。
D. 
M2 
状态
只有受支持的缓存执行、ResourceScope、导数请求及公开 
AD 
模式均具有明确且通过测试的合同，才能评估 
M2 
是否达成该支持子集的验收。仍存在错误有限 
RoF 
或不能可靠阻断的支持宣称时，必须保持 
PARTIAL
。
不进入 
M3，直到 
M2 
的资源和方法合同真正闭合。
11. 
原 
R2 
门禁与权限
11. 原 R2 门禁与权限
全部 
R2 
最终门禁继续保留：
三环境 
FULL；
四框架独立验证；
GLOBAL 
coverage 
≥ 
91.34108013033072%
；
exclusions 
68
 
不增加；
原始 
28-section 
matrix；
全部 
SDK-free 
数值示例；
controlled 
legal；
actual 
import 
origins；
frozen/staged/commit 
equality。
继续 
Owner 
的 
local-only 
授权：不 
push、fetch，不修改 
OAuth/TLS，不安装新依赖、不 
vendor、不调用新硬件、不修改金融原始证据或 
Studio/Router。
不得用 
M2B 
的 
61 
passed 
或低量子位 
M1 
的 
107 
passed 
替代新的最终冻结验收。
最终建议
下一段不应再扩展资源账本，也不应直接进入 
100-wire 
MPS。
先用纯 
TensorFlow 
验证 
trace-inline 
可微执行
 
是否确实避开内部 
cached 
ConcreteFunction 
的错误 
RoF 
边界，再将它严格限定地连接到真实低量子位 
QNode。
与此同时，保留现有 
managed 
explicit 
cached-query 
作为独立、已验证的资源受控能力，不强求一个执行入口同时承担 
TensorFlow 
外部任意图的自动微分和 
Python 
逐次记账这两种无法同时证明的保证。
如果 
trace-inline 
也失败，接受当前 
M2 
仍有框架集成阻断，保留正式失败证据和安全拒绝；不要以局部数学正确或账本正确代替完整 
SDK 
的实现。
QuantumBridge 
full 
independent 
native 
Qiskit/PennyLane 
full 
functional 
parity/full 
replacement：
ACTIVE 
/ 
INCOMPLETE
。
