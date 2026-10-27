Source: actual owner-authorized collaborator reply in existing Chrome conversation.
Retrieved full response 2026-10-23. This corrects the ideal-Jordan oracle assumption for rounded binary inputs.

核准。你提出的最新证据进一步明确了 R2L 的数学验收边界，应该正式采用。
尤其重要的是，你证明了：即使使用真实浮点输入的高精度矩阵平方根，再将结果舍入为 complex128，普通双精度矩阵乘法的平方残差仍可能达到 
0.1267783
。因此，不能把 
||X @ X - A|| < 1e-12
 当作这三个极端病态输入的统一验收条件。
但对于新构造的、严格满足 
𝑁
2
=
0
 的 Jordan 族，必须保留严格的解析数学验收，不能简单拒绝。
R2L 验收条款正式修订
R2L 验收条款正式修订
测试类别
强制要求
合法结果
原 rounded Fourier 三例
与真实 complex128 输入的高精度分支 oracle 比较，并评估数值可信性
正确数值，或有依据的 
LinAlgError
108 项严格 Jordan 测试
保留重复特征值解析导数项，符合既定容差
必须返回正确数值
条件良好的跨 cut 非正规矩阵
采用真实浮点输入及分支一致 oracle
必须返回正确数值
整数幂、对角矩阵、可靠三角矩阵
维持既有计算能力
必须返回正确数值
真正无法可靠计算的其他病态输入
提供可核查的条件或误差依据
明确数值拒绝
测试类别
原 rounded Fourier 三例
108 项严格 Jordan 测试
条件良好的跨 cut 非正规矩阵
整数幂、对角矩阵、可靠三角矩阵
真正无法可靠计算的其他病态输入
强制要求
与真实 complex128 输入的高精度分支 oracle 比较，并评估数值可信性
保留重复特征值解析导数项，符合既定容差
采用真实浮点输入及分支一致 oracle
维持既有计算能力
提供可核查的条件或误差依据
合法结果
正确数值，或有依据的 
LinAlgError
必须返回正确数值
必须返回正确数值
必须返回正确数值
明确数值拒绝
测试类别
强制要求
合法结果
1. 严格 Jordan 族必须计算成功
1. 严格 Jordan 族必须计算成功
你新增的构造：
𝐴
=
𝜆
𝐼
+
𝑁
,
𝑁
=
𝑡
(
1
1
−
1
−
1
)
,
𝑁
2
=
0
其中：
𝜆
∈
{
−
0.25
,
−
1
,
−
2
}
𝑡
∈
{
0.125
,
0.25
,
0.5
}
这些矩阵条目可以精确表示为二进制浮点数，其严格 Jordan 结构不应被 Schur 分解产生的微小数值特征值分裂误导。
对于选定的一致解析分支，仍必须满足：
𝐴
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
并保留当前 
3e-12 / 3e-13
 容差
，不放宽、不通过 xfail/skip/Unsupported 规避。
实现时不能仅凭 Schur 计算得到的近重特征值距离决定是否调用导数公式；必须有可靠的重复谱结构判定。也不能仅凭近似重复就强行合并真实跨 cut 的两个不同特征值。
2. Rounded Fourier 三例采用真实输入条件化验收
2. Rounded Fourier 三例采用真实输入条件化验收
必须固定原始 complex128 元素的十六进制表示，使用你已经建立的高精度 characteristic-polynomial oracle。
对于 
𝑝
=
0.5
,
0.3
,
−
0.3
，验收允许：
NUMERIC
_
PASS：
 真正匹配实际浮点输入的正确分支矩阵函数，满足既定 forward 精度。
JUSTIFIED
_
NUMERICAL
_
REJECTION：
 当 branch-sensitive 条件放大超出 double precision 可可靠判别范围时，在输出错误有限矩阵前抛出 
LinAlgError
，并记录数值依据。
不允许：
返回原来的错误有限矩阵；
强行套用范数约 1.422 的理想 Jordan 极限；
删除实际输入中的微小虚部；
对所有负轴 Jordan 或所有跨 cut 矩阵一律拒绝；
仅因结果范数很大而拒绝；
事后改变 oracle 或容差。
重要补充：
 对 Rounded Fourier 输入，平方残差可以作为诊断指标，但不能单独作为正确性判据。高精度 oracle 的输出及其向 complex128 舍入后的实际可达到残差，应共同记录。
3. 实现上的优先判断
3. 实现上的优先判断
下一步先运行这两组红灯：
三个真实 rounded Fourier 输入的高精度 oracle 测试；
108 个严格 Jordan 解析测试。
然后判断数值分支。
对
可证明严格重复
的谱结构，使用解析导数或可靠的等价算法，保留 Jordan 非对角项。
对
真实跨 cut、极度接近
的特征值，不得人为合并；如果误差条件无法保证，明确数值拒绝。
对
可靠分离且跨 cut
的非正规矩阵，必须使用真实分支差商正确计算。
对
一般可靠输入
，继续现有 Schur/矩阵函数路径，并用独立数学测试保护。
有一点需要避免：在浮点计算中检测到 
𝑁
2
 很小，并不足以一般性证明矩阵具有严格重复特征值。因此严格 Jordan 快捷路径必须具备可靠的结构或误差证明，不能简单设置一个较宽的阈值来合并谱。
4. 更新 R2L 测试门禁
4. 更新 R2L 测试门禁
原 R2L 第 1–5 节中与这两个输入族冲突的要求，以本次修订为准。
本次专项通过标准为：
108 项严格 Jordan：全部实际数值通过。
三项 Rounded Fourier：全部数值正确或具备可核查依据的数值拒绝。
条件良好的跨 cut 非正规测试：真实数值通过。
原有 45 项 probe：
WRONG_FINITE_RESULT = 0
。
保留整数幂、对角矩阵、scalar 与现有 matrix-workspace 安全回归。
不增加 skip/xfail、不降低容差、不增加新的 blanket Unsupported。
只有上述数学红灯全部修复后，才进入原 R2L 规定的开发期宽回归和原 R2 完整冻结门禁。
最终判断：你这次修订是必要的。
 它把两类原本被混淆的问题正确拆开了：
严格 Jordan：
 必须保持解析结构，计算正确。
浮点扰动且跨分支的近 Jordan：
 必须尊重实际输入和分支；计算无法保证时，明确、可解释地数值拒绝。
本次确认仅依据你提供的高精度实验报告，不代表我已独立运行 mpmath 或查看未提交代码。
QuantumBridge 的完整独立原生 Qiskit/PennyLane full functional parity/full replacement 继续保持 
ACTIVE / INCOMPLETE
。
