Source: owner-authorized existing default Chrome conversation Claude 代码泄漏与应对.
Retrieved full response 2026-10-23. Advice remains below owner instructions.

QuantumBridge–夸父 D1：验收结论
QuantumBridge–夸父 D1：验收结论
我建议立即进入 D2 离线物理布局与选择性误差诊断，暂时保留剩余 7 个真机任务额度，不提交 one-hot。
D1 的结果已经说明：当前最大的未知量不是“还需要多少 shots”，而是
不同电路实际使用的物理比特集合、测量映射以及状态制备与测量误差是否可以迁移
。
根据你提供的报告：
验收项
实际结果
原九项只读复核
Counts 与原收据一致，QASM SHA 未变
Compiled QASM / QLISP
九项均取得并完成理想分布核验
理想 compiled-vs-submitted TVD
最大约 
1.23
×
10
−
10
三量子位零态 / 一态
83.89% / 70.90%
四量子位零态 / 一态
80.96% / 70.31%
位序判定
AMBIGUOUS
真机任务
13 / 20
剩余额度
7 项，每项最多 1,024 shots
金融效果
INCONCLUSIVE，且存在明显偏差
验收项
原九项只读复核
Compiled QASM / QLISP
理想 compiled-vs-submitted TVD
三量子位零态 / 一态
四量子位零态 / 一态
位序判定
真机任务
剩余额度
金融效果
实际结果
Counts 与原收据一致，QASM SHA 未变
九项均取得并完成理想分布核验
最大约 
1.23
×
10
−
10
83.89% / 70.90%
80.96% / 70.31%
AMBIGUOUS
13 / 20
7 项，每项最多 1,024 shots
INCONCLUSIVE，且存在明显偏差
验收项
实际结果
这些结果支持两项重要判断。
第一，已获取的 compiled QASM 与 QLISP 在零输入、理想测量分布层面一致，说明
目前没有发现能够解释金融偏差的已验证编译逻辑错误
。但这并不排除实际 pulse、物理门、读出或其他硬件层误差。
第二，四量子位 D1 诊断使用 
{10,11,4,5}
，而原 allocation/constraints 使用 
{10,3,4,11}
，相关性任务使用 
{10,3,11,4}
。
不能把 D1 的四位边缘错误率直接当成原金融任务的 readout calibration。
为什么现在不应该执行默认 one-hot？
为什么现在不应该执行默认 one-hot？
3q/4q 全零、全一数据确实不能区分位序；对任意 qubit 排列，全零仍是全零，全一仍是全一。
One-hot 可以增加排列信息，但当前最重要的前提尚不成立：
新任务是否会被编译到原金融任务使用的相同物理位集合？
如果 one-hot 被编译到另一组物理位，即使结果非常清楚，也只能证明那一组新任务的映射，不能证明历史金融任务的映射。
此外，D1 的全一态成功率仅约 70%，说明单次 one-hot 实验本身存在明显的制备加测量污染。可以通过概率统计辨识部分映射，但不能保证一次实验就能唯一确定全部排列。
因此，现在不应该默认消耗剩余七项额度。
下一段执行 Prompt：QuantumBridge Finance–Kuafu D2
下一段执行 Prompt：QuantumBridge Finance–Kuafu D2
Historical Physical-Mapping Audit & Diagnostic Experiment Selection
Historical Physical-Mapping Audit & Diagnostic Experiment Selection
继续既有五类金融模型、九项原始业务及校准任务、四项 D1 诊断任务。
本段默认完全离线、只读，不新增真机任务。
1. 执行边界
1. 执行边界
保留以下事实：
原金融模型、参数、QASM、SHA、counts 和金融指标不变。
已执行 13 个真实 Dongling 任务。
剩余最多 7 个任务，合计最多 7,168 shots。
不使用假定的 readout calibration。
不改变金融业务容差。
不将 
INCONCLUSIVE
 改为 PASS。
不自动提交任何 one-hot 任务。
使用现有 QuantumBridge 原生 QASM、QLISP 解析、理想状态模拟、统计模块和持久账本。
不调用 Qiskit/PennyLane 作为原生计算执行器，不安装新依赖。
2. 首要任务：建立 13 项物理布局矩阵
2. 首要任务：建立 13 项物理布局矩阵
读取已有原始证据，按实际 compiled measurement mapping 建立逐任务对照表。
至少包含：
任务组
物理比特集合
有序映射
Risk
{3,4,10}
[10,3,4]
Pricing / History
{4,5,11}
[11,4,5]
Allocation / Constraints
{3,4,10,11}
[10,3,4,11]
Signed correlation
{3,4,10,11}
[10,3,11,4]
D1 3q
{4,5,11}
[11,4,5]
D1 4q
{4,5,10,11}
[10,11,4,5]
任务组
Risk
Pricing / History
Allocation / Constraints
Signed correlation
D1 3q
D1 4q
物理比特集合
{3,4,10}
{4,5,11}
{3,4,10,11}
{3,4,10,11}
{4,5,11}
{4,5,10,11}
有序映射
[10,3,4]
[11,4,5]
[10,3,4,11]
[10,3,11,4]
[11,4,5]
[10,11,4,5]
任务组
物理比特集合
有序映射
表中的集合和顺序来自现有报告；执行时必须重新从已保存的 compiled records 解析验证，不要将上表硬编码为可信事实。
这里可以得到一个非常重要的区别：
D1 3q 与 Pricing/History 的物理集合及报告中的有序测量映射一致，因此具有直接比较价值；但 D1 4q 与原四比特金融任务集合不同，不具备同等的直接迁移依据。
即使物理集合一致，也必须继续比较任务时间、编译选项和实际门序列，不能自动认为噪声相同。
3. 第二项：原始 counts 位序的离线可辨识性
3. 第二项：原始 counts 位序的离线可辨识性
对已有 13 项 counts 枚举候选解释：
identity；
reversed；
由 compiled QASM 支持的 register ordering；
若 QLISP measurement 字段足以约束，则只保留合法排列。
对每个候选分别生成：
原始 counts 的规范化解码。
对应的理想概率分布。
Multinomial log-likelihood。
TVD。
各位 marginal deviation。
该候选是否与 compiled measurement map 相容。
必须区分三个概念：
compiled logical-to-physical mapping；
physical-to-classical measurement mapping；
服务端 raw count label 的字符串排序。
前两项已部分可知，不代表第三项已被证明。
对全零和全一态，所有合法位排列的观测似然相同；它们不能给候选排序提供有效信息。
对金融或 H 电路计算的 likelihood 可以作为诊断性比较，但由于真实物理误差分布未知，
不能直接把“最接近理想分布的排列”宣布为真实 bit order
。
如果现有 counts 无法唯一识别，结论保持 
AMBIGUOUS
。
4. 第三项：历史任务的可迁移性判定
4. 第三项：历史任务的可迁移性判定
为每项旧任务与每项 D1 任务生成配对记录。
至少评估：
exact physical qubit set；
ordered measurement mapping；
compiled gate family；
compiled circuit depth；
task creation/finish time separation；
available calibration identifier；
是否有完全相同的测量线路；
state preparation 差异；
是否存在真实 readout correction 标记。
分别输出：
DIRECTLY_COMPARABLE
、
PARTIALLY_COMPARABLE
、
NOT_TRANSFERABLE
、
UNKNOWN
。
其中 
DIRECTLY_COMPARABLE
 也只能表示
布局与可观测执行条件足够接近，可以作有条件的诊断比较
，不能等同于已经证明误差模型可迁移。
特别检查 D1 3q 与 Pricing/History。比较历史任务的时间间隔和编译后最终 measurement mapping。
对于 Risk、Allocation、Constraints、Correlation，不得直接把 D1 的边缘错误率代入金融模型。
5. 第四项：选择性误差与相关性
5. 第四项：选择性误差与相关性
使用四项 D1 raw counts，计算完整联合错误模式，而不仅是每位 marginal。
至少计算：
𝑃
(
𝑏
^
𝑖
≠
𝑏
𝑖
)
；
两位同时错误的实际概率；
与独立边缘错误模型预测的双位错误概率之差；
观察到的 Hamming-distance 分布；
三位/四位整串成功率；
零态与一态的错误不对称；
Wilson 区间；
bootstrap 对联合错误指标的不确定性。
可以额外计算一个
假设独立 readout-like bit-flip 的敏感性模型
，但必须标为：
HYPOTHETICAL_MODEL
不能把 D1 结果直接命名为物理读出矩阵，更不能用该模型修正原金融 counts。
6. 第五项：确定最小后续硬件实验
6. 第五项：确定最小后续硬件实验
离线分析后，输出是否需要进一步实验的决策，不自动执行。
按信息价值排序：
优先 A：获取明确的 raw counts bit-order 或可固定物理布局的服务端字段。
若旧任务的元数据能直接解释位序，则可能不需要额外任务。
优先 B：能否在提交前指定并验证目标物理比特布局。
必须通过实际服务端公开能力确认，例如：
是否接受物理 qubit 约束；
是否允许固定初始布局；
是否提供 dry-run compile 或 compile-only；
是否能在收费执行前返回计划中的 measurement mapping。
不能因 QASM 使用了特定物理编号，就假定服务端一定按该编号执行。
优先 C：同布局的 one-hot。
如果能够固定或预先验证原金融任务的物理集合，优先设计针对该集合的 one-hot，而不是默认 3q+4q 七个全部运行。
对于 
{3,4,10,11}
 这个四位集合，可考虑识别其中的排列；但 allocation/constraints 与 correlation 的
有序映射不同
，需要在分析中按实际 classical-bit 位置分别解码。
一个成功的 one-hot 只能提供该实验对应 mapping 的证据，不能证明服务器在其他任务中沿用同样 mapping。
7. 后续任务的成本与识别能力优化
7. 后续任务的成本与识别能力优化
当前剩余七项，不应默认一次耗尽。
要求离线构建候选实验集，对每个候选计算：
需要的任务数；
shots；
目标物理集合；
预测可区分的排列假设；
是否可能受制备误差影响；
需要何种服务端固定布局能力；
最坏情况下仍无法区分的假设；
对金融结果解释的边际价值。
除了 one-hot，也应评估
非对称多位基态编码
：若有可靠的 raw label 语义和足够的信号，少量精心选择的基态可能区分多种排列。但必须证明其组合可辨识性，且不能把有噪声的结果当作确定的 bit permutation。
在没有可靠的物理布局约束或证明实验可迁移之前，输出：
NO_NEW_SUBMISSION_RECOMMENDED
而不是自动开跑。
8. D2 离线安全红灯
8. D2 离线安全红灯
必须覆盖：
同物理集合但不同测量顺序；
相同测量顺序但物理集合不同；
raw counts reversed 与 classical mapping 区分；
全零/全一对所有 permutations 的相同似然；
选择性偏差与读出偏差混淆；
噪声导致错误排列似然较高；
calibration identifier 缺失；
task timestamp 漂移；
mapping metadata 冲突；
one-hot 编译到错误物理集合；
repeated task ID；
原始 evidence SHA 改变；
超过 20-task 联合预算；
读取操作误触发新任务。
D2 运行期间将提交网关置于 read-only/no-submit 模式。
任何意外的新任务创建都应视为测试失败。
9. 交付物
9. 交付物
建议新增：
纯文本
复制代码
docs/implementation/finance_quafu_d2_mapping_diagnosis.md


output/finance-hardware/diagnostics/d2/


    physical_layout_matrix.json


    historical_task_pairing.json


    count_order_hypotheses.json


    joint_error_patterns.json


    mapping_identifiability.json


    candidate_experiment_plan.json


    d2_readonly_audit.json
还应提供一份中文只读 Notebook：
finance_quafu_d2_mapping_diagnosis.ipynb
内容包括物理集合对比、历史 counts 的各种合法位序解释、零/一状态的联合错误模式、不同任务的可迁移性，以及是否值得消耗下一项任务的决策。
Notebook 不应覆盖五份原金融 Notebook 或硬件原始证据。
10. D2 验收标准
10. D2 验收标准
D2 完成时必须证明：
13 项原始和诊断任务 SHA 全部未改变。
没有提交新任务。
已执行仍为 13/20。
物理集合和有序 mapping 来自真实 compiled evidence。
全零/全一对 permutation 无辨识力已验证。
D1 3q 与历史 Pricing/History 的映射关系得到条件化评估。
D1 4q 不会被错误迁移到另一物理集合。
所有 counts 的候选排序都附带噪声模型限制。
所有读出模型只作为 hypothetical sensitivity analysis。
给出明确的下一任务提交或继续保留额度的决策依据。
如果最终需要 one-hot，先向 owner 提交
具体 QASM、目标物理集合、预计任务数、可辨识假设和停止条件
，再由 owner 根据诊断结果决定是否授权。
本阶段不自动使用剩余七项额度。
最终建议
最终建议
现在最应该做的是把已有 13 项真机证据的物理布局、counts 字符串位序和联合误差模式彻底区分开，而不是继续付费提交新电路。
D1 已经提供了有用的错误不对称证据，但还没有识别出可靠的物理读出模型。尤其 D1 四位校准与历史四位金融任务并不使用同一物理集合，这使直接套用校准更加不可靠。
因此，下一步明确为：
D2 纯离线只读诊断 → 确认物理布局可否固定或验证 → 决定最少数量的可辨识实验 → 再考虑新增真机任务。
金融业务状态继续 
INCONCLUSIVE
，原始指标和容差不变；QuantumBridge 完整独立原生 Qiskit/PennyLane full functional parity/full replacement 继续保持 
ACTIVE / INCOMPLETE
。
本次审阅仅依据你提供的 D1 本地报告，并不代表我已独立检查本地源码或硬件服务端。
