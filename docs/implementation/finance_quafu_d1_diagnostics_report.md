# 夸父金融编译与制备测量诊断报告

2026-10-23。五类研究案例已通过真实 Dongling 任务取得结果，但金融数值精度尚未通过验收。
本轮检查原 9 项任务的编译信息，并完成 4 项独立的全零、全一诊断。
累计 **13/20 项任务、每项 1024 shots**，剩余 7 项保留；没有提交 one-hot 或新的金融业务任务。
完整独立原生 Qiskit/PennyLane 替代目标仍为 ACTIVE/INCOMPLETE。

## 原始证据保持不变

原 `session.json`、`plan.json`、`task_ledger.json`、raw/normalized counts、
`finance_metrics.json`、`hardware_vs_ideal.json` 和五份 hardware evidence 均在本轮前后复核 SHA-256。
结果是全部未变。具体文件及散列见
`output/finance-hardware/diagnostics/original_evidence_integrity.json`。
没有更改原金融定义、参数、解码器或事后业务容差。

原 9 项任务的 provider `count` 与原收据逐项一致，provider `circuit` 与原提交 QASM 散列相同。
服务实际提供 `chip,circuit,transpiled,qlisp,tid,status,error,created,finished,corrected`。
编译器名称／版本、完整编译选项、calibration ID 和 raw-counts 字符串位序没有提供。
`corrected` 是空对象，没有将它解释为已完成误差缓解。

## 编译电路审计

使用项目原生 QASM2 解析器和 StatevectorDevice，先把物理寄存器压缩至活动的 2～4 位。
另以安全字面量解析，独立将返回 QLISP 的 U、CZ、Measure 翻译为原生电路。
不调用 Qiskit/PennyLane 执行器；没有执行来自服务的 Python 表达式。

原 9 项 compiled-vs-submitted 的经典测量分布 TVD 最大约 **1.23e-10**；
QLISP-vs-compiled-QASM TVD 全部为 0，二者测量映射也相同。
这验证零输入下理想测量分布基本保留，不证明任意输入酉矩阵、脉冲级行为或具体物理噪声来源。
单纯的返回门级编译差异不足以解释原金融实验中的巨大分布偏差。

| 电路 | 最终 c0,c1,... 对应物理位 |
| --- | --- |
| 原风险 3q | 10,3,4 |
| 原期权／均匀时间索引 3q | 11,4,5 |
| 原资产配置／约束 4q | 10,3,4,11 |
| 原正负相关性 4q | 10,3,11,4 |
| 新全零／全一 3q | 11,4,5 |
| 新全零／全一 4q | 10,11,4,5 |

这里是**最终测量对应关系**，不是完整路由轨迹，也不是 raw counts 字符串排列的声明。
新 4q 实验与原 4q 金融实验的物理集合不同；同样宽度不能当作同一物理校准。

## 四项真实诊断结果

| 准备态 | 真实任务 ID | 目标命中 | 比例 | Wilson 95% 区间 |
| --- | --- | ---: | ---: | --- |
| 000 | 2610231309374778530 | 859/1024 | 83.89% | 81.51%～86.01% |
| 111 | 2610231309431738918 | 726/1024 | 70.90% | 68.04%～73.60% |
| 0000 | 2610231309495020213 | 829/1024 | 80.96% | 78.44%～83.24% |
| 1111 | 2610231310018516967 | 720/1024 | 70.31% | 67.44%～73.03% |

四项均 DONE，单项 1024 shots，实际编译电路的理想准备态与原提交一致。
全零电路没有制备门；全一电路仅对每位施加 X。每项完整 QASM、SHA、raw counts、
编译后 QASM、QLISP、时间和物理测量映射均独立保存。

3q 相对 4q 的全零命中率高约 2.93 个百分点，全一高约 0.59 个百分点。
因为使用物理位不同、实验时刻不同且区间重叠，这不是“多一位必然导致多少噪声”的因果估计。
四项同时多位错误频率依次为 1.46%、2.83%、2.15%、3.61%。
逐字符串位置表观错误率、两位联合错误和经验协方差见 `zero_one_metrics.json`。
尚未证明字符串位序，因此逐位置统计不标成特定物理位或 c0。

这些是**状态制备加测量的综合表观错误**。全一还包含 X 门制备误差；
不能据此单独归因于纯读出、T1/T2、串扰或双比特门。
Wilson 区间仅描述 IID 抽样不确定性，不覆盖漂移或系统误差。

## 决策

原金融精度仍为 INCONCLUSIVE，且原始结果的显著偏差继续保留展示。
全零与全一在所有位排列下不变，不能从这些计数选出 identity 或 reverse；
mapping 状态是 AMBIGUOUS。2q 原校准只是初步 q0-last 证据，不外推为全部物理布局的证明。

不自动提交余下 7 项 one-hot，不增加金融 shots，不反演读出矩阵，不修改原始金融结果。
两个准备态不足以恢复完整多比特混淆矩阵，物理集合差异和漂移也未解决。
先核查物理指定能力、实际 counts 位序、编译版本及 calibration ID，
再决定哪一种最小实验能回答剩余问题。结果已发送指定 ChatGPT 对话进行下一步审阅。

## 安全与测试

诊断独立持久账本与原账本共用 OS 文件锁；联合预算最多 20 项，诊断自身最多 4 项。
原批次在诊断账本存在后禁止新增提交。提交前持久化 intent；
未知提交结果不自动重发，超时仅续查同一任务 ID。没有遇到收费提示；没有授权自动购买。
凭据不在参数、代码、notebook、报告或回传消息中。

本轮离线金融及云协议定向测试：主环境、另一 SDK 环境、无 SDK 环境各 **129 passed**。
金融模块覆盖 **764/811，94.20%**；这不是全仓 GLOBAL coverage。
Ruff 与 `git diff --check` 通过。全仓测试、完整功能覆盖、矩阵和既存 Router/Operator 问题
没有在本轮宣称通过，也没有 commit、push、OAuth、tag、release、依赖安装或 vendor。

新增中文只读回放 notebook：`output/jupyter-notebook/finance/06_hardware_diagnostics.ipynb`，
6 个代码单元实际从头执行，零错误；对应 HTML 可直接打开。
原五类 notebook 和模型保持原样。回放不会提交云任务。

## 产物与复现

新增证据均位于 `output/finance-hardware/diagnostics/`：原任务字段可用性、编译清单、
四项任务账本、raw counts、编译元数据、Wilson/联合错误统计、映射假设和保留额度决策。

```bash
python scripts/run_finance_diagnostics.py
python scripts/build_finance_diagnostic_notebook.py
```

第一条默认只读本地原任务元数据，不访问云。第二条只读回放并生成 notebook 和 HTML。
只有显式 `--execute --prompt-token` 才进入四项受控诊断路径，已保存任务 ID 会复用查询，
不会重发已完成任务。不要删除账本后重跑云命令。
