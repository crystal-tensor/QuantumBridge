Source: owner-authorized existing default Chrome conversation Claude 代码泄漏与应对.
Retrieved full response 2026-10-23. Advice remains subordinate to actual evidence and owner instructions.

D3 验收与下一步判断
D3 验收与下一步判断
同意你的建议：保留剩余 7 个夸父任务额度，停止新增硬件实验，优先修复 QuantumBridge 原生 
Operator.power()
 的三项确定性错解。
D3 已经完成了当前最重要的接口溯源：实际客户端是 
quarkstudio 7.3.9
 的 
quark.quafu.Task
，并非新版 
quafu-sdk
。现有接口没有证实物理布局锁定或零收费编译功能，因此不应继续消耗硬件预算来猜测位序。
项目
审阅结论
D3 只读接口核查
报告显示专项验收通过
Raw counts 端序
GATEWAY_ASSUMPTION_UNVERIFIED
物理布局锁定
NOT_VERIFIED
夸父任务预算
13/20，剩余 7
金融业务结果
INCONCLUSIVE
原生 Operator.power
3 项已证实错解，尚未修复
原 R2 FULL / GLOBAL / matrix
尚未完成
项目
D3 只读接口核查
Raw counts 端序
物理布局锁定
夸父任务预算
金融业务结果
原生 Operator.power
原 R2 FULL / GLOBAL / matrix
审阅结论
报告显示专项验收通过
GATEWAY_ASSUMPTION_UNVERIFIED
NOT_VERIFIED
13/20，剩余 7
INCONCLUSIVE
3 项已证实错解，尚未修复
尚未完成
项目
审阅结论
当前最明确的阻断项已经不是硬件接口，而是 
Operator.power()
 对负实轴附近非正规 Jordan 块返回有限但严重错误的矩阵
。
这比明确 Unsupported 更危险，因为调用方会以为计算成功。应将这三项登记为 
NATIVE_BUG / BLOCKING_CORRECTNESS
，优先于一般的返回类型、异常文本或覆盖率补强。
数学定位
数学定位
对于二阶 Jordan 块：
𝐽
=
(
𝜆
𝑐
0
𝜆
)
,
𝑓
(
𝐽
)
=
(
𝑓
(
𝜆
)
𝑐
𝑓
′
(
𝜆
)
0
𝑓
(
𝜆
)
)
其中 
𝑓
(
𝑧
)
=
𝑧
𝑝
，因此：
𝐽
𝑝
=
(
𝜆
𝑝
𝑐
𝑝
𝜆
𝑝
−
1
0
𝜆
𝑝
)
这条公式只有在
对两个幂项使用一致的解析分支
时才成立。
你报告的三个结果误差达到约 
1.7
×
10
7
 至 
2.1
×
10
7
，而平方根重建残差约 0.1333。它们不是可以接受的浮点舍入误差。
最值得怀疑的是：负实轴附近的微小 branch rotation，被错误地用于近重特征值的差商或相位差计算，使理论上应当取解析导数极限的项出现灾难性消减或虚假放大。
这一机制需要通过代码内插桩实证，不能仅凭现象断定已经定位根因。
公开 Qiskit 文档明确指出 
branch_cut_rotation
 可改变负实轴附近根的选择；Higham–Lin 的 Schur–Padé 研究也特别强调三角矩阵分数幂中对角与首超对角项的准确计算。
下一段 Codex 执行 Prompt
下一段 Codex 执行 Prompt
QuantumBridge Stage 12-B P4-U3D2-R2L
QuantumBridge Stage 12-B P4-U3D2-R2L
Native Operator Fractional Power — Negative-Axis Jordan & Branch-Aware Schur Correctness Repair
0. 执行范围
0. 执行范围
继续此前未完成的 Stage 12-B P4-U3D2-R2，不建立新 SDK 阶段。
本批唯一最高优先级是：
修复已有原生 
Operator.power()
 在负实轴 Jordan 块及其酉相似变换下返回错误有限结果的缺陷，并恢复分支敏感矩阵函数的数值可靠性。
本批不得：
新增夸父任务；
修改原 13 项硬件数据或金融模型；
改变金融业务容差；
转向 Studio 或新行业；
引入 Qiskit/PennyLane 执行包装；
安装新数值依赖；
读取或复制上游 SDK 源码和测试；
修改 GitHub OAuth、TLS 或凭据；
push、PR、tag、release 或重写 Git 历史。
保持原有本地提交和未提交工作。
1. 首先固定三个真正的错误案例
1. 首先固定三个真正的错误案例
在现有 Operator.power 测试中加入新的回归模块：
纯文本
复制代码
tests/information/test_native_operator_power_branch_jordan.py
先保留当前 45 项探索测试的真实结果：
18 个正确；
24 个明确拒绝；
3 个有限但错误的结果。
其中 3 个错解必须先实际失败。
构造：
Python
复制代码
运行代码
import
 
numpy
 
as
 
np
lam
 
=
 
-
1.0
coupling
 
=
 
0.3
jordan
 
=
 
np
.
array([
    [
lam
, 
coupling
],
    [
0.0
, 
lam
],
], 
dtype
=
np
.
complex128)
并按你此前独立探针中真实使用的 Fourier 相似变换矩阵 
𝐹
 生成：
Python
复制代码
运行代码
A
 
=
 
F
 
@
 
jordan
 
@
 
F
.
conj()
.
T
注意 
𝐹
 必须具有已验证的酉性。不要为了方便直接替换成任意未经验证的矩阵。
测试：
Python
复制代码
运行代码
branch_cut_rotation
 
=
 
np
.
pi 
*
 
1e-12
exponents
 
=
 [
0.5
, 
0.3
, 
-
0.3
]
针对每个指数同时记录：
原生计算结果；
独立 Jordan 解析结果；
最大逐元素复数误差；
相对矩阵误差；
全部矩阵元素是否有限；
输入矩阵是否保持不变；
对 
𝑝
=
0.5
 的平方根重建残差；
原生是否错误地返回了一个看似有效的有限矩阵。
不能将这三项改为 xfail、skip 或无条件 Unsupported 来隐藏已知错解。
确实无法在声明的数值有效域内可靠计算的其他病态输入，可以经过明确分析后安全拒绝；但这三个有解析解的核心回归必须真正计算正确。
2. 独立解析 oracle：分支必须一致
2. 独立解析 oracle：分支必须一致
建立不依赖 QuantumBridge matrix-functions 内核的数学 oracle。
设 
𝐽
=
𝜆
𝐼
+
𝑁
，其中 
𝑁
2
=
0
，则：
𝐽
𝑝
=
𝜆
𝑝
𝐼
+
𝑝
𝜆
𝑝
−
1
𝑁
先定义与公开 
branch_cut_rotation
 语义一致的旋转对数分支，再计算两个幂项。
不得使用两个独立 
np.power()
 调用让 
𝜆
𝑝
 和 
𝜆
𝑝
−
1
 意外选择不同分支。
推荐建立明确的辅助测试函数：
Python
复制代码
运行代码
def
 
branch_power
(
z
, 
exponent
, 
branch_rotation
):
    
log_z
 
=
 
independently_defined_branch_log
(
z
, 
branch_rotation
)
    
return
 
np
.
exp(
exponent
 
*
 
log_z
)
随后：
Python
复制代码
运行代码
lambda_p
 
=
 
branch_power
(
lam
, 
p
, 
rotation
)
lambda_p_minus_1
 
=
 
lambda_p
 
/
 
lam
expected_jordan
 
=
 (
    
lambda_p
 
*
 
np
.
eye(
2
, 
dtype
=
np
.
complex128)
    
+
 
p
 
*
 
lambda_p_minus_1
 
*
 
nilpotent
)
expected
 
=
 
F
 
@
 
expected_jordan
 
@
 
F
.
conj()
.
T
对于不同符号的 branch rotation，分别验证根的选择。不能只检验数值大小、模长或概率。
3. 诊断 Schur/Parlett 发生误差的具体位置
3. 诊断 Schur/Parlett 发生误差的具体位置
在受控开发测试中记录但不泄露凭据或其他工作区信息：
输入矩阵的 Schur 三角因子。
Schur 分解重建残差。
重复特征值的数值分裂幅度。
负实轴附近的旋转后特征值。
分支化对数的具体选择。
首超对角项的计算方法。
是否误用小分母差商。
是否发生跨分支的两个函数值相减。
是否使用错误的正规矩阵快捷路径。
Schur 回变换后的误差增长。
重点检测：
纯文本
复制代码
near-repeated eigenvalues


        +


branch-cut-adjacent spectrum


        +


nonzero Jordan offdiagonal


        ↓


unstable divided difference
不能因为两个特征值在浮点数下略有不同，就直接把它们当成相距足够远的特征值进行普通差商。
也不能因为矩阵的某个 commutator 很小，就当作正规矩阵丢弃上三角非对角项。
4. 实施原生数值修复
4. 实施原生数值修复
复用现有 
quantumbridge/information/matrix_functions.py
 或项目中实际对应的数值模块。
对相近特征值及重复特征值区域，应优先考虑稳定的局部解析展开、分块三角函数或已有 Schur–Parlett 路径。
需要实现：
重复特征值的一阶导数极限；
分支一致的首超对角项；
对接近重复特征值的稳定差商；
分支切线附近的安全数值判断；
非正规 Jordan offdiagonal 的保留；
结果重建残差及误差估计；
失败时明确数值拒绝，不返回严重错误的有限矩阵。
禁止仅增加一个针对 
lambda=-1
、
coupling=0.3
 的硬编码分支。
修复必须对一族 Jordan 参数和相似变换成立。
可参考 Higham–Lin 的 Schur–Padé 算法研究思路，特别是 inverse scaling/squaring 与首超对角项的准确计算，但不得复制上游 SciPy/Qiskit 实现代码。
5. 扩展独立数学测试族
5. 扩展独立数学测试族
至少覆盖：
Jordan 2×2，
𝜆
=
−
1
，多种 coupling；
𝜆
=
−
0.3
,
−
1
,
−
2
；
上下不同方向的微小 branch rotation；
𝑝
=
0.5
,
0.3
,
−
0.3
；
近重但不完全重合的特征值；
无 Jordan 非对角项的退化矩阵；
一般 2×2 非正规三角矩阵；
Fourier 或其他固定酉相似变换；
更高维 4×4 block diagonal；
正规/酉矩阵反例；
既有 scalar 1×1；
奇异 Jordan 和非有限输入拒绝。
至少采用两种独立核验：
A. 解析 Jordan oracle
，直接计算矩阵函数。
B. 数学恒等式和 backward residual
，例如平方根应满足 
𝑋
2
≈
𝐴
。
但对于 
𝑝
=
0.3
 等非整数幂，不能任意把 
𝑋
1
/
𝑝
=
𝐴
 当作无条件正确恒等式；必须考虑分支及谱区域。
6. 双版本公开 Qiskit 差分
6. 双版本公开 Qiskit 差分
在 Qiskit 2.4.1、2.6.0 分别运行现有 45 项探针及新增 Jordan 测试。
记录：
public 返回值；
native 返回值；
独立解析解；
public 是否出现 branch inconsistency；
public 是否正确；
native 是否正确；
原生明确拒绝的数值边界；
输入矩阵是否被修改。
分类使用：
MATCH / INTENTIONAL_SAFETY_DIFFERENCE / UPSTREAM_DEFECT / UNSUPPORTED / NATIVE_BUG
解析数学答案优先于简单 public/native 数值相等。
即使公开版本在极端 branch-cut 情形下也发生错解，QuantumBridge 不应复制错误。
7. 资源与恶意输入安全
7. 资源与恶意输入安全
保留：
大矩阵维度预算；
Schur workspace 预算；
中间数组累计占用；
dtype 和输入所有权校验；
ndarray subclass / foreign callback 拒绝；
非有限元素拒绝；
branch_cut_rotation 非法值拒绝；
参数有限性；
迭代次数、收敛次数限制；
不修改输入；
不调用上游 SDK 的计算器；
不做不受控 dense MPS fallback。
新增极端情况：
branch rotation 极小；
非正规度很高；
repeated eigenvalue cluster；
高条件数相似变换；
不可逆矩阵的负幂；
Schur 无法满足误差预算；
长时间不收敛；
预估 workspace 超预算。
不能为了通过这三项红灯扩大整体资源上限，也不能放松数学容差。
8. 执行顺序与验收
8. 执行顺序与验收
先完成本段针对性的真实红绿测试：
纯文本
复制代码
3 native wrong finite outputs


    ↓


independent branch-aware Jordan oracle


    ↓


numerical cause instrumentation


    ↓


native mathematical repair


    ↓


entire 45-case regression


    ↓


expanded nonnormal/branch tests


    ↓


dual Qiskit public differential
然后运行：
Operator / Information FOCUS；
Core / Circuit / Compiler；
Serialization；
Gradients/QML；
Devices/Noise；
H₂；
四框架相关回归；
SDK-free 数值示例；
compileall、Ruff/F821、diffcheck。
只有确认三项原生错解真正修复、没有新增正确性问题，才考虑原 R2 的最终冻结条件。
完整 R2 门禁依然是：
SDK-free FULL；
Main Qiskit 2.4.1 / PennyLane 0.44.1 FULL；
Alternate Qiskit 2.6.0 / PennyLane 0.42.3 FULL；
Independent JAX FOCUS；
Independent TF FOCUS；
Torch/Autograd FOCUS；
显式 GLOBAL coverage；
原始 28-section matrix；
全部 SDK-free 数值示例；
controlled legal；
五个真实 import origins；
frozen/worktree/staged/committed runtime equality。
覆盖率最低基线：
91.34108013033072%
，exclusions 
68
 不增加。
原 R2 的其他 Factory/Error/Resource/ParameterView 差异仍在任务中，不因修复 Jordan 错解自动宣称 R2、P4 或 SDK 全部完成。
9. Git 与硬件保护
9. Git 与硬件保护
继续 owner 本地开发授权：
保留所有已有提交和脏工作区；
不推送、不更新 OAuth；
不修改 Studio/Router；
不安装数值依赖；
不读取或发送 Quafu 凭据；
不提交新的 Dongling 任务；
不更改金融模型、Notebook 原始证据或硬件 counts；
不做 force、reset、rebase、amend、PR、tag 或 release。
本段完成开发回归后，只有在最终冻结和全量门禁满足条件时，才进行普通 scoped 本地提交；否则保持准确的 PARTIAL 状态。
10. 最终报告要求
10. 最终报告要求
必须报告：
三项已知错解修复前后的具体复数误差。
负轴分支处理的真实数学依据。
Schur 重复特征值与近重特征值处理。
Jordan 非对角项是否得到保留。
45 个原探针结果的逐类变化。
新增独立数学场景结果。
两版本公开差分与上游错误边界。
Numerical workspace 与收敛拒绝。
SDK-free 和主要开发回归的真实终态。
原 R2 FULL、GLOBAL、matrix 是否实际执行。
本地提交及远端 CI 真实状态。
仍未实现的核心函数和 ABI。
当前最明确的下一步就是修复 
Operator.power
 负轴 Jordan 的三项错误有限输出。
 这是真正的原生数学正确性缺陷，应优先于更多硬件诊断或界面扩张。
D3 保持已完成的只读检查点，13 项硬件证据全部不变、7 项预算继续保留。完整 Qiskit/PennyLane 独立原生 full functional parity/full replacement 继续为 
ACTIVE / INCOMPLETE
。
