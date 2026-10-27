# Finance Hardware Acceptance: Received Collaboration Prompt

Source conversation: Claude 代码泄漏与应对
Source message: ea413159-dce2-4fdd-9c74-2d2f56163533
Retrieved: 2026-10-23, actual existing default Chrome accessibility text after refresh.
This is collaborator advice authorized by the owner, not a new authority over owner priorities.
The following is the received UI text; duplicated headings/table columns are retained.

+QuantumBridge 金融五大方向：阶段审阅
结论：这批金融案例可以认定为已完成本地原生计算、Notebook 执行和真机提交准备的支持子集；但不能认定已经完成夸父真机验证。
根据你提供的报告，目前没有发现必须撤销现有金融实现的确定性数学缺陷。不过，部分结果需要更加严格地区分理论值、有限采样误差、模型近似误差与未来的硬件噪声。
验收项
当前报告结果
金融原生模块
kernels / cases / execution
 已实现
五份中文 Notebook
45/45 代码单元执行成功
数值图表
15 张生成成功
Finance 专项测试
57 项
SDK-free 相关回归
87 passed
QASM 本地解析
8 个业务电路通过
真机任务计划
9 × 1,024 shots
真机预算
最多 20 任务，每任务 1,024 shots
真机 counts
NOT
_
EXECUTED
完整 Qiskit/PennyLane parity
ACTIVE / INCOMPLETE
验收项
金融原生模块
五份中文 Notebook
数值图表
Finance 专项测试
SDK-free 相关回归
QASM 本地解析
真机任务计划
真机预算
真机 counts
完整 Qiskit/PennyLane parity
当前报告结果
kernels / cases / execution
 已实现
45/45 代码单元执行成功
15 张生成成功
57 项
87 passed
8 个业务电路通过
9 × 1,024 shots
最多 20 任务，每任务 1,024 shots
NOT
_
EXECUTED
ACTIVE / INCOMPLETE
验收项
当前报告结果
这些结论只依据你提供的本地执行报告。我没有独立检查未提交源码、Notebook 或远端硬件任务。
我认为最重要的三个数学边界
我认为最重要的三个数学边界
1. VaR 与 ES 的离散尾部定义。
你给出的精确值 EL=1.54、VaR=6、ES=11.6 可以作为当前损失模型的基准，但必须在 Notebook 中严格定义置信水平和分位点规则。
对于离散分布，若 VaR 位置存在概率质量，ES 应按尾部概率预算拆分 VaR 边界的概率质量，而不能直接将所有 
loss >= VaR
 的样本取平均并自动称为标准 ES。
2. 金融约束优化必须报告可行条件下的表现。
你目前报告的可行率约为 71.09% 与 47.85%。因此，最优观测 bitstring 的 gap=0 并不能单独证明求解器整体表现良好。
还应分别报告可行率、条件最优命中率、无条件成功率及目标函数分布。真机出现最优解但概率极低，也不能被记成稳定求解成功。
3. 真机误差必须分层。
最终结果至少区分：
金融模型误差：例如三步二叉树相对于更精细定价模型的离散化误差。
有限 shots 误差：即使在理想模拟器上也会出现。
硬件偏差：物理执行分布与对应理想电路分布之间的差异。
编译偏差：夸父平台编译、门分解、位序及测量映射导致的可能差异。
不能将真机结果与金融解析值的全部差异都归因为量子硬件噪声。
下一步 Codex 执行 Prompt：QuantumBridge Finance–Kuafu Hardware Acceptance
下一步 Codex 执行 Prompt：QuantumBridge Finance–Kuafu Hardware Acceptance
五类金融案例的真机 Counts 回收、统计验证与误差归因
五类金融案例的真机 Counts 回收、统计验证与误差归因
继续 owner 当前优先的五类金融方向，不切回 Studio 框架扩张或提前恢复旧 R2 总验收。
启动条件：取得真实夸父任务 ID 和 counts 后执行验收。未获得有效凭据或真实 counts 时，只准备验收代码与测试，不提交任务、不制造硬件成功记录。
1. 保持原始任务预算
1. 保持原始任务预算
保留既定计划：
8 个业务电路；
1 个位序校准电路；
每任务 1,024 shots；
最多 20 个任务；
最大 6 qubits；
现有计划总计 9,216 shots。
执行前核验真实线路 hash、shots、backend、任务 ID 和预算余额。
对于超时、未知状态或网络异常，必须先按现有任务 ID 查询，
禁止直接重复提交产生额外收费任务
。
不要求重新登录 ChatGPT，也不能从旧参考代码中复制硬编码 token。
2. 首先完成位序校准
2. 首先完成位序校准
用已规划的非对称 calibration bitstring 确认：
qubit index 与 classical-bit index；
QASM 测量目标；
夸父 counts 字符串的展示顺序；
是否存在 register 分组或空格；
是否有缺失前导零；
bitstring 到组合资产选择的解码关系。
保存原始 counts 与规范化后的 counts，不能覆盖原始硬件证据。
如果位序无法唯一确定，
阻断后续金融指标的正式验收
，但不必因此重新提交业务任务；优先利用已有任务、QASM 和测量映射定位。
3. 八条业务电路逐项统计验收
3. 八条业务电路逐项统计验收
对每个任务独立输出：
指标
必须报告
Task ID / circuit hash
原始可追溯证据
Actual shots
counts 求和与任务元数据一致
Ideal probabilities
同一提交电路的原生理想分布
Hardware probabilities
counts / actual shots
Total variation distance
两分布偏差
95% uncertainty interval
合适的二项或多项分布统计方法
Business metric
按固定金融解码器还原
Status
PASS / FAIL / INCONCLUSIVE / NOT_EXECUTED
指标
Task ID / circuit hash
Actual shots
Ideal probabilities
Hardware probabilities
Total variation distance
95% uncertainty interval
Business metric
Status
必须报告
原始可追溯证据
counts 求和与任务元数据一致
同一提交电路的原生理想分布
counts / actual shots
两分布偏差
合适的二项或多项分布统计方法
按固定金融解码器还原
PASS / FAIL / INCONCLUSIVE / NOT_EXECUTED
指标
必须报告
不能预设 TVD 的任意门槛已经具有硬件认证意义。建议在执行前冻结每个场景的容许业务误差及判定规则；样本不够时返回 INCONCLUSIVE，而不是事后调整门槛。
4. 五类金融场景专项验收
4. 五类金融场景专项验收
资产配置：
 报告所有可行 bitstring、可行率、最优或近优命中率、目标值差距、条件期望目标值。将无约束组合和有换仓约束组合分开。
风险计量：
 从 counts 重建八情景损失分布，重新计算 EL、VaR、ES。报告 VaR 所在概率边界是否稳定、ES 对尾部稀有样本的敏感性，以及 Monte Carlo / multinomial bootstrap 区间。bootstrap 必须保留离散损失与边界分位点规则。
衍生品定价与对冲：
 验证风险中性概率、payoff 编码、折现因子、call/put 定价及 Delta。定价误差拆分为三步树模型误差和采样/硬件误差。静态对冲损益的降低必须基于同一情景集比较。
金融约束优化：
 区分 feasible probability、conditional optimum probability、unconditional optimum probability。检查约束惩罚项的强度是否足以防止不可行解反而优于可行解。
相关性与市场波动：
 保留有符号振幅干涉和正负相关的符号信息。验证 Pearson 分母非零、数据标准化和波动率年化约定。不能把仅从测量概率得到的结果误称为直接读取量子振幅符号。
5. 金融误差归因报告
5. 金融误差归因报告
每个指标至少建立以下对照链：
纯文本
复制代码
Financial reference calculation


             ↓


Circuit encoding + model approximation


             ↓


Exact native ideal probability


             ↓


Native 1024-shot sampling


             ↓


Actual Kuafu hardware counts


             ↓


Same frozen financial decoder
要求：
exact native 与采样版本使用相同电路；
硬件 counts 进入相同业务后处理器；
不根据真机结果重新调优金融参数后再比较；
记录全部 QASM、参数、编译选项和 bit mapping；
若平台提供 compiled circuit，保存其真实元数据并核对语义；
缺少硬件噪声或校准数据时，不臆测具体噪声来源。
1024 shots 对离散 VaR 和低概率尾部事件的判定可能不足，必须允许最终状态为 
INCONCLUSIVE
。
6. 真机验收的必要资源与安全红灯
6. 真机验收的必要资源与安全红灯
必须验证：
counts 求和不等于 shots；
未知 bitstring；
超出测量位宽；
bit order mismatch；
重复 task ID 对应不同 circuit hash；
已存在任务不再提交；
网络超时后先查询；
status=failed 不冒充 counts；
缺少 token 时不发请求；
超过剩余任务预算拒绝；
未授权收费任务拒绝；
历史任务 JSON 被篡改；
原始硬件证据不可被模拟输出覆盖。
账本应使用原子写入及现有文件锁，保留任务提交和结果读取的审计轨迹。
7. 需要生成的最终证据
7. 需要生成的最终证据
建议在现有金融目录内形成：
纯文本
复制代码
docs/implementation/finance_quafu_hardware_acceptance.md


output/finance/kuafu/task_ledger.json


output/finance/kuafu/raw_counts/


output/finance/kuafu/normalized_counts/


output/finance/kuafu/finance_metrics.json


output/finance/kuafu/hardware_vs_ideal.json
路径可按已有目录规范调整；不覆盖或伪造既有结果。
五份 Notebook 增加“真实硬件结果”章节，使用实际读取的 counts。没有 counts 时明确显示 
NOT_EXECUTED
，不使用假硬件柱状图。
8. 最终验收与阶段关系
8. 最终验收与阶段关系
获得真实硬件 counts 后，执行：
位序校准。
任务 hash / shots / ledger 校验。
八条业务电路逐项重建分布。
真实硬件与 native exact / finite-shot 基准比较。
五类金融业务指标及不确定性分析。
三种误差来源分解。
Notebook 全部代码单元重跑。
Finance native tests、SDK-free tests、格式与资源测试。
受控 legal 和真实 evidence provenance。
仅按 owner 授权范围进行正常本地提交，不 push。
保持当前本地 Studio/Router 脏文件，不修改凭据、Git 认证、TLS 或历史。
如果硬件尚未执行，只能完成验收准备，不能把 
NOT_EXECUTED
 改成 PASS。
原 R2 的三 FULL、四框架、GLOBAL coverage、28-section matrix 和 frozen/staged/commit 一致性要求依旧保留；本次金融专项验收不能替代这些门禁。
我的最终建议
我的最终建议
现在不要增加新金融案例数量，也不要修改已经交付的五份 Notebook 的核心金融定义。
 先保证这九个计划任务的真实可追溯执行和可信统计分析。
尤其关注两个可能决定验收结果的指标：
风险计量：
 1024 shots 下 VaR 跳档和 ES 的置信区间。
优化：
 真机可行率、最优命中率与无条件成功概率，而不仅是最佳 bitstring 的目标值。
完成真机专项验收后，可以判断 QuantumBridge 在这五类具体金融场景中具备怎样的实际硬件执行能力；
不能据此推论已实现整个金融行业函数库，更不能宣称完整 Qiskit/PennyLane full replacement 完成。
最终目标继续为 
ACTIVE / INCOMPLETE
。
