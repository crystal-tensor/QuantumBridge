# Received TF6-M2I Frozen Scalar Dataflow Prompt

Full completed response actually read in the authorized existing ChatGPT
conversation in default Chrome on2026-10-24, including its ending. This
responds to the M2H intermediate report, not final wide-regression acceptance.
No new tab or login. Guidance does not override owner/higher-priority rules.
M2 remains PARTIAL, M3 NOT_STARTED, full native SDK replacement ACTIVE /
INCOMPLETE. Receipt is not implementation of a scalar GraphDef lowerer.

QuantumBridge M2H：中间检查点审阅
结论：可以允许你提出的限定性 Scalar GraphDef → Native ParameterExpression lowering，但必须将其定位为“构造期、只读、严格白名单的标量表达式导入”，而不是通用 TensorFlow 图解释器。
不过，我建议优先尝试更小的方案：
在原有 scalar pack 构造阶段直接保留可证明的参数表达式来源；只有无法通过现有原生 AST 捕获的合法路径，才进入受限 GraphDef lowering。
你现在的测试证据已经说明：
项目
状态
原两条 cached RoF
Main/Alternate 专项已转绿
新增 scalar capture 六条
6 failed，仍为正式数学红灯
原 Native Whole-QNode 及显式查询
有通过的专项证据
M2H 宽回归
RUNNING，终态未确认
M2
PARTIAL
M3
NOT
_
STARTED
项目
原两条 cached RoF
新增 scalar capture 六条
原 Native Whole-QNode 及显式查询
M2H 宽回归
M2
M3
状态
Main/Alternate 专项已转绿
6 failed，仍为正式数学红灯
有通过的专项证据
RUNNING，终态未确认
PARTIAL
NOT
_
STARTED
项目
状态
原两条红灯在原公开入口下转绿，是实质进展。但新六条说明：
只有当 TensorFlow 输入与原生量子参数之间的标量依赖关系也被完整冻结，才能消除 cached-inner 自动微分边界。
例如 
tf.sin
 输入映射、
tf.reverse
 重排以及在 native builder 之后追加可训练 RX，三种情况不能统一假定等同于原生 
ParameterExpression
。
关键区别是：
前两种可能通过严格受限的纯标量数据流 lowering 解决。
第三种可能已经涉及线路构建结果、量子门添加顺序及参数来源，
仅修 scalar AST 未必足够
。必须先检查其实际构造过程，不能为了六条全绿而偷偷重跑用户函数。
下一段 Codex Prompt：TF6-M2I — Frozen Scalar Dataflow Lowering
目标：修复新增六条 Cached RoF 红灯，继续 M2，不进入 M3
继续 QuantumBridge R2O3-B-TF6-M2H。
本批允许一个
严格限定的、构造期 Scalar GraphDef → Native ParameterExpression lowering
，但应先完成只读来源审计和独立数学证明，不直接开发通用 GraphDef parser。
不得重新执行用户 QNode 函数，不导入 TensorFlow GraphDef 作为执行图，不复制上游 SDK，不创建第二套 Circuit、Compiler、参数身份或量子执行引擎。
完整独立 Qiskit/PennyLane full functional parity/full replacement 保持 
ACTIVE / INCOMPLETE
。
1. 第一阶段：逐一解释六条真实失败
保留 
test_native_tf_cached_rof_scalar_capture.py
 六条正式红灯。
分别分析三个构造模式，每种覆盖两个外部 loss：
模式
必须识别的真实依赖
潜在解决方式
tf.sin
 input map
Trainable input → sin → native 参数
纯标量表达式 lowering
tf.reverse
输入位置重排 → 参数 UUID occurrence
Shape/index-aware lowering
Native builder 后追加 trainable RX
原线路构造结果 → 新参数化 Gate
先判断是否完整属于构造期原生 operation snapshot
模式
tf.sin
 input map
tf.reverse
Native builder 后追加 trainable RX
必须识别的真实依赖
Trainable input → sin → native 参数
输入位置重排 → 参数 UUID occurrence
原线路构造结果 → 新参数化 Gate
潜在解决方式
纯标量表达式 lowering
Shape/index-aware lowering
先判断是否完整属于构造期原生 operation snapshot
模式
必须识别的真实依赖
潜在解决方式
第三类尤其重要。必须确定 RX 是否已经存在于最终 captured native operations 中。
如果存在，补齐该 operation 的参数来源与最终 plan identity。
如果不存在，不能单靠恢复 scalar AST 解决；需要检查构造期捕获流程是否遗漏后续 append。
若意味着执行时必须重新运行任意用户 Python，则当前冻结合同不能支持，应保留正式失败。
不得把三类失败强行归因于同一个 TF 梯度问题。
2. 第二阶段：先用来源保留方案，后用 GraphDef lowering
优先检查构造期是否能够直接获取：
纯文本
复制代码
User TF input


→ Immutable scalar mapping


→ Existing native ParameterExpression


→ FrozenParameterBinding


→ Compiled occurrence UUID
如果原生参数表达式已经存在，只是没有持久化输入映射，应直接保存该映射。
对于只存在于 TensorFlow 标量图中的变换，才允许读取当前构造期已捕获的 scalar GraphDef。
GraphDef 本身是 TensorFlow 生成的数据流表示，但其结构不能自动证明某节点是纯函数、无状态或有合法高阶导数。TensorFlow 的 tracing 行为还会捕获 Python 对象与闭包状态，因此必须严格核查图输入和捕获来源。
3. 建立 Scalar Lowering 白名单
首批仅考虑这些确定性操作：
操作
准入条件
Placeholder
精确对应已登记的输入 index/dtype/shape
Const
有界 float64 数值，不含外部引用
Identity
单输入无副作用
Pack/Unpack
静态 rank/axis/index
Reshape
静态目标 shape，元素数严格一致
StridedSlice
静态整数索引，经过真实布局验证
ReverseV2
静态 axis，输出 index 映射可证明
Add/AddV2/Sub/Mul
与现有 AST 一致的实数逐元素语义
Sin/Cos/Exp
现有原生 AST 已支持的光滑标量运算
操作
Placeholder
Const
Identity
Pack/Unpack
Reshape
StridedSlice
ReverseV2
Add/AddV2/Sub/Mul
Sin/Cos/Exp
准入条件
精确对应已登记的输入 index/dtype/shape
有界 float64 数值，不含外部引用
单输入无副作用
静态 rank/axis/index
静态目标 shape，元素数严格一致
静态整数索引，经过真实布局验证
静态 axis，输出 index 映射可证明
与现有 AST 一致的实数逐元素语义
现有原生 AST 已支持的光滑标量运算
操作
准入条件
不要在首批加入动态控制流、资源变量、随机数、查表、未知函数调用、
PyFunc
 或任意外部 TF callable。
Div/Pow
 可以后续单独准入，但必须有定义域、分支及二阶导数证明，不能因现有 AST 支持就自动接受任意图。
需要特别强调：
shape 操作不能简单丢弃。
 
tf.reverse
 和 
StridedSlice
 必须还原精确的输入索引映射，否则同名 UUID 的 Jacobian/Hessian 仍可能错位。
4. 编译期 GraphDef 安全审计
Lowerer 只读取已捕获的标量图，不执行它。
实施前验证：
GraphDef 节点数量上限。
总 protobuf 字节上限。
Tensor 元素数与 rank 上限。
所有输入都可追溯到允许的 Placeholder 或 Const。
所有输出都可追溯到输入。
无环。
无 resource/ref tensor。
无 stateful operation。
无 function-library call。
无 control dependency 或未知副作用。
无动态 shape/axis。
无非有限常量及非法 dtype。
采用
全图 fail-closed
：任何节点不满足要求，就不生成部分可执行 AST。
这些限制仍不足以证明任意 GraphDef 安全，因此只能针对列出的节点语义逐项验证。
5. Lower 到既有 Native ParameterExpression
目标不是生成第二套 TF 解释器。
应形成：
纯文本
复制代码
Captured scalar GraphDef


        ↓


Verified pure scalar DAG


        ↓


Existing ParameterExpression + input UUID map


        ↓


Existing FrozenParameterBinding


        ↓


Existing ExecutionPlan.lowered()


        ↓


Native TF Whole-QNode readonly execution
对于 shape-only 操作，允许使用构造期内部的有界索引映射描述，但最终进入量子参数的每个标量仍必须落到已有原生表达式系统。
若现有 
ParameterExpression
 不能完整表达该节点，不允许偷偷新增独立 TF scalar evaluator。可以扩充现有 AST 的通用语义，但必须同时考虑其他原生框架的行为、序列化及导数合同；如果改动过大，就先保留 Unsupported。
必须保留：
真实 UUID；
ParameterVector root/index；
source occurrence；
local Gate/body；
parameter order；
global phase；
snapshot identity；
owner resource identity。
6. 独立数学红灯
先使用不导入 QuantumBridge 的纯 NumPy/mpmath oracle，验证：
sin(p)
；
reverse([p,q])
；
reshape/slice/reorder；
sin(p*q + 0.4)
；
二输出组合；
至少两个参数点；
完整 Jacobian；
mixed Hessian；
非平凡方向 HVP；
非平凡 cotangent VJP。
再验证 lowering 后的 
ParameterExpression
 求值，不调用原 TensorFlow scalar pack。
必须特别测试：
参数顺序交换后，数值可能偶然一致，但 Jacobian 的列身份必须仍严格对应原 UUID。
7. 原生 Whole-QNode 端到端测试
重新运行新增六条正式 Cached RoF 红灯。
要求：
原公开 QNode 入口不变；
原两种外部 loss 不变；
AD nesting 不变；
容差不变；
不改 skip/xfail；
不重新运行用户 QNode 函数；
不调用旧 cached scalar pack；
不调用 cached-inner quantum graph；
不使用 
tf.import_graph_def
；
不使用 NumPy callback/Hessian 注入。
同时运行：
Eager FoR/RoF；
外部 co-traced RoF；
Tape-over-Tape；
pfor Jacobian；
两个参数点；
valid → NaN/Inf/cut → valid。
只有六条原测试自身通过，才能记录为六条修复。
如果第三类涉及未被原生捕获的附加 RX，不允许仅靠前两类通过就声称六条全部解决。
8. 资源、缓存与安全反例
复用现有 
ExecutionPlan
、
DerivativeExecutionRequest
、
UnifiedResourceLedger
 和 ResourceScope。
新增预算必须覆盖：
GraphDef bytes；
node count；
scalar AST nodes；
rank/shape；
index mapping；
expression depth；
lowering workspace；
compilation work；
derivative expression complexity。
必须在危险内存构造前拒绝超限输入。
同时测试：
修改 scalar GraphDef；
修改 input signature；
同名不同 UUID；
换序的 ParameterVector；
source owner 销毁；
限额收紧；
GraphDef 中伪造未知 op；
unsupported function call；
非有限常量；
参数输入缺失；
冗余未使用输入；
循环依赖；
控制依赖；
恶意巨大 shape；
scope 生命周期；
concurrent handles。
Lowering 只发生在构造期，不能利用图缓存绕过实际 owner/config 检查。
外部缓存图的 Python 逐次账本仍是 
OUT_OF_SCOPE
，不能因数学转绿改变这一事实。
9. 优先测试范围
建议新增：
纯文本
复制代码
tests/interfaces/test_native_tf_scalar_graph_lowering.py


tests/interfaces/test_native_tf_scalar_graph_security.py


tests/interfaces/test_native_tf_scalar_capture_lineage.py


tests/interfaces/test_native_tf_cached_rof_scalar_capture.py
最小顺序：
I1：
 六条正式红灯分类定位。
I2：
 只读来源捕获与有限 DAG admission。
I3：
 scalar DAG → 原有 native AST，独立 J/H 验证。
I4：
 真实 QNode 六条 RoF 数学测试。
I5：
 资源、身份、scope 和负例。
不要先写一个支持任意 GraphDef 的通用解释器，然后再试图限制它。
10. 完成后联合回归
必须按最新代码重跑：
原两条已转绿 cached RoF；
新六条 scalar capture；
默认 eager pfor 85；
M2 请求与账本 163；
M1 Whole-QNode；
两框架 TF；
Torch/Autograd/JAX；
Compiler/IR/QPY；
严格 SDK-free；
Operator.power；
Fréchet；
Native MPS tangent；
ResourceScope/concurrency。
当前 M2H 宽回归仍在运行，必须记录最终退出码，不得事先写 PASS。
原四条 100-wire MPS TF 红灯继续保留；不能借 Scalar GraphDef lowering 提前开始 M3。
原 R2 最终门禁仍为三环境 FULL、独立四框架、GLOBAL ≥ 
91.34108013033072%
、exclusions 
68
 不增、原始 28-section matrix、全部数值示例、controlled legal、五个实际 import origins 以及 frozen/staged/commit equality。
继续 local-only：不 stage/commit/push/fetch，不安装依赖或 vendor，不更改认证/TLS，不调用云/硬件，不修改金融历史证据，不动 Studio/Router。
最终工程建议
允许严格限定的 Scalar GraphDef lowering，但只作为现有 Native ParameterExpression 的构造期来源恢复手段。
不要将 TensorFlow GraphDef 当作新的 QuantumBridge IR，也不要把 TensorFlow 图导入后执行。尤其不能将 
tf.reverse
 的索引语义或追加 RX 的原生 operation 来源问题简化成普通数值函数映射。
本批最重要的验收结果应该是：六条新增 RoF 原始测试中究竟哪些因冻结标量表达式而真正恢复，哪些还需要修复 Circuit 构造捕获边界。
即使六条全部转绿，也只是 M2 数学支持域的进一步扩大，不能直接宣称 M2 或完整 SDK 替代完成。
M2：PARTIAL；M3：NOT
_
STARTED；完整独立原生 Qiskit/PennyLane replacement：ACTIVE / INCOMPLETE。


## Terminal M2H Confirmation And I2/I3 Boundaries

The following completed reply, including its ending, was actually read after
the final M2H results and I1 source audit were reported. No lowerer is implied
by this receipt.

确认，下一步继续 M2I 的 I2 → I3，不改变原执行顺序。
两点边界均同意：
1. 
整数 Const：
 仅允许 
int32/int64
 用于静态 shape、axis、slice/index 等结构性参数。不得作为可训练数值表达式参与计算，也不得隐式转换为 float64 量子参数。
2. 
Pow：
 首批只考虑指数为静态常量 
2
 的平方运算，必须先通过独立解析 Jacobian/Hessian、定义域及原生 AST 语义一致性验证，再加入白名单。其他 Pow（尤其变量指数）及 Div 暂时严格拒绝，不得静默降级。
另保留两个关键约束：
整个 scalar DAG 必须 fail-closed；原有合法 query 不得因为新的冻结子域不支持而失效。
 不支持的 scalar 来源可以保留既有合法 query 路径，但资源准入失败绝不能触发 fallback。
原六条 scalar-capture RoF 和四条 100-wire MPS 红灯继续保留，不能修改断言或放宽容差。
当前状态不变：
M2 
PARTIAL
；M3 
NOT_STARTED
；完整独立原生 Qiskit/PennyLane replacement 
ACTIVE / INCOMPLETE
。


