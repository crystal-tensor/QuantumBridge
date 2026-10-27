# 夸父金融历史布局与位序诊断

2026-10-23。D2 对已有 13 项真实 Dongling 实验作纯离线分析，**新增提交为 0**。
当前仍为 13/20 项，每项 1024 shots，保留 7 项。建议
**NO_NEW_SUBMISSION_RECOMMENDED**：在原金融任务的物理布局不能提前固定或验证之前，不运行默认映射 one-hot。
金融数值验收仍 INCONCLUSIVE；完整原生 Qiskit/PennyLane 目标仍 ACTIVE/INCOMPLETE。

## 证据与只读边界

13 项源 QASM、raw counts、provider 返回编译信息和两个持久账本重新读取并复核。
物理集合、有序测量和门层深从保存的编译记录重新解析，不依赖先前报告的手工表格。
原金融 SHA 清单及 D1 诊断证据的文件散列在运行前后全部相同。
细目见 `output/finance-hardware/diagnostics/d2/d2_readonly_audit.json`。
分析期间同时禁用 socket connect/connect_ex 和 QuafuCloudBackend.submit；
不读取密钥、不查询云、不安装依赖、不提交电路。

## 物理布局及可迁移性

| 任务组 | 物理集合 | 最终 c0,c1,... 对应物理位 |
| --- | --- | --- |
| Risk | 3,4,10 | 10,3,4 |
| Pricing／History | 4,5,11 | 11,4,5 |
| Allocation／Constraints | 3,4,10,11 | 10,3,4,11 |
| Signed correlation | 3,4,10,11 | 10,3,11,4 |
| D1 3q | 4,5,11 | 11,4,5 |
| D1 4q | 4,5,10,11 | 10,11,4,5 |

9 项历史任务与 4 项 D1 任务共有 36 组配对，其中 **32 组 NOT_TRANSFERABLE，4 组 PARTIALLY_COMPARABLE**。
只有 Pricing／History 与 D1 3q 的集合和有序测量对应关系同时一致。
历史任务结束到对应 D1 开始约 1982～2024 秒，即约 33～34 分钟；
没有 calibration ID，也没有已验证稳定性，不能把同布局解释为同一噪声模型。
各任务门族、逻辑层深、时间及原始 correction 字段都在配对 JSON 中保留。
逻辑层深采用单位门时长、barrier 同步，排除末尾测量，不是物理脉冲时间。

## Counts 位序的可辨识性

物理放置、物理到经典测量连接、raw count label 字符串排序是不同概念。
对每项 2～4 位结果枚举全部 2!／3!／4! 字符串候选，
标记 identity、reverse 和按物理编号排序的假设，生成规范化 counts、理想概率、
multinomial log-likelihood、TVD、边缘偏差和与已有元数据的关系。
缺少 raw label 序列化声明时，测量连接本身不能排除这些序列化假设。

严格无噪声模型下，若观测到了理想概率为零的状态，似然就是零，log 为负无穷。
JSON 使用 `null` 配合 `positive_counts_at_zero_ideal_probability=true`，
没有添加伪计数把不可能事件人为变成有限似然。
最佳拟合仍可能由选择性制备／硬件偏差造成，**所有任务均保持 AMBIGUOUS，不选定排列**。
全零与全一的任意排列似然完全相同，已由实际计数和单元测试验证。

| 历史电路 | 所有排列中最小 TVD |
| --- | ---: |
| Allocation | 0.366456 |
| Risk base／stress | 0.253281／0.232070 |
| Pricing | 0.164001 |
| Constraints | 0.314217 |
| Positive correlation | 0.509355 |
| Negative correlation | 0.565952 |
| Uniform history sampling | 0.138672 |

这说明单一输出位排列不能消除观察到的主要分布偏差；
它不证明具体噪声机制，也不改变原金融 decoder 或数值。

## 选择性与联合错误

四项 D1 raw counts 给出完整错误位串、Hamming 距离分布、逐位置 Wilson 区间、
两位联合错误、边缘乘积基线以及 2000 次 empirical multinomial bootstrap 的协方差区间。
raw label 位序未确认，所以统计使用字符串位置，不伪标为某个物理位。

全一相对全零的目标整串命中率，3q 低 12.99 个百分点，4q 低 10.64 个百分点。
逐位置的“全一错误率减全零错误率”为：

- 3q：0.09375、0.0478516、0。
- 4q：0.0263672、0.0302734、-0.0009766、0.0644531。

这只能说明综合表观错误存在状态不对称。X 制备、读出、门误差及漂移没有被分离。
独立边缘乘积仅作为比较基线，不声称构造了真实 readout matrix，
也未将任何模型用于修正原金融 counts。bootstrap 只覆盖 IID 经验采样，不恢复未见状态或漂移。

## 最小后续实验的条件计划

已离线枚举实验编码的无噪声可辨识性：

| 候选 | 任务数 | Shots 总计 | 最坏仍不可区分排列数 |
| --- | ---: | ---: | ---: |
| 3q 单 one-hot：001 | 1 | 1024 | 2 |
| 3q 两条：001、010 | 2 | 2048 | 1 |
| 4q 单 one-hot：0001 | 1 | 1024 | 6 |
| 4q 三条 one-hot：0001、0010、0100 | 3 | 3072 | 1 |
| 4q 两条非对称态：0011、0101 | 2 | 2048 | 1 |

例如两条 4q 编码给每个位置分配不同的二位签名，可在无噪声、各任务映射一致时区分 24 种排列。
这是组合可辨识性，不是实际噪声下的成功保证，也不是新增提交授权。
有噪声时仍可能出现错误排列拟合更高，回归测试对此明确拒绝宣布真实映射。

当前 adapter 明确暴露 chip／compile 选项；固定物理布局、initial-layout 约束、
收费前 compile-only 或 dry-run 能力在 D2 中**未验证**，不能由 QASM 物理编号推断服务承诺。
因此所有候选 `execute=false`，保留额度。优先获取服务端位序声明与布局约束的公开契约；
只有在目标集合、实际测量对应关系、预计成本和停止条件可验证后，
再把具体 QASM 与最小计划交 owner 决定。不自动耗尽剩余七项。

## 交付与验证

证据目录 `output/finance-hardware/diagnostics/d2/` 包含：
`physical_layout_matrix.json`、`historical_task_pairing.json`、`count_order_hypotheses.json`、
`joint_error_patterns.json`、`zero_one_asymmetry.json`、`mapping_identifiability.json`、
`candidate_experiment_plan.json` 和 `d2_readonly_audit.json`。

新增中文只读 notebook 为
`output/jupyter-notebook/finance/finance_quafu_d2_mapping_diagnosis.ipynb`，
对应 HTML 同名；6 个代码单元实际执行，零错误，不覆盖五份金融 notebook。
D1 和 D2 HTML 在 1440／390 像素视口验证，无页面横向溢出，图片正常，未发现 notebook 错误输出。

金融及云协议定向测试在主环境、另一 SDK 环境、无 SDK 环境各 **149 passed**。
金融模块覆盖 **859/906，94.81%**；新增位序诊断模块 95/95 statements。
这是定向覆盖，不是全仓 GLOBAL 或完整 SDK 功能门禁。
Ruff、diff 检查通过；111 项金融相关源码／文档／输出的本地凭据泄漏扫描未发现该密钥。
没有推送、提交、OAuth、tag、release、Studio、依赖安装或 vendor。

```bash
python scripts/analyze_finance_mapping.py
python scripts/build_finance_mapping_notebook.py
```

以上均为离线只读回放。完整源码与原始实验结果留在本机，后续诊断不以“任务成功”代替精度验收。
