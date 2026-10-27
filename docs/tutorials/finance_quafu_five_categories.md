# 量子金融五类案例：QuantumBridge × 夸父

本批为五个小规模合成研究工作流，不是生产金融系统、投资建议、全部 Qiskit Finance
功能或量子优势声明。完整的中文原理、逐步代码、测量分布、中间图和最终结果均在
已执行的 Jupyter notebook 中。

入口：`output/jupyter-notebook/finance/index.html`。可直接用浏览器打开，不需要启动服务。

| 分类 | Notebook | 当前实现 |
| --- | --- | --- |
| 量化投资与资产配置 | `01_allocation_quafu.ipynb` | 四资产二元均值—方差、两资产持仓约束、QUBO/QAOA、可行性与经典最优对照 |
| 风险计量 | `02_risk_quafu.ipynb` | 三比特八种损失情景、正常/压力分布、EL、95% VaR、正确处理边界原子的期望短缺 |
| 衍生品定价与对冲 | `03_derivatives_quafu.ipynb` | 三步风险中性树、看涨/看跌、有限差分 Delta、采样标准误差、静态对冲情景损益 |
| 金融约束优化 | `04_constraints_quafu.ipynb` | 持仓/行业/资本约束、换仓成本、罚项验证、QAOA、逐项约束解码 |
| 相关性与市场波动 | `05_correlation_quafu.ipynb` | 保留符号的正/负 Pearson 干涉电路、历史时间重采样、日波动率及252日年化 |

## 本地执行

需要 Python、NumPy、Matplotlib、nbformat、nbclient、ipykernel 和 nbconvert。
核心金融计算只依赖项目既有 NumPy 与原生电路/设备。Jupyter 包仅用于生成和执行教程，
不加入项目核心依赖。

```bash
python scripts/build_finance_notebooks.py --execute --html
```

第一次生成使用现有 notebook 技能的教程模板；如模板安装在其他位置，使用
`--scaffolder /path/to/new_notebook.py`。已存在五份 notebook 时重建无需模板。
执行使用当前 Python 解释器、独立内核和本机 IPC 传输。

## 真机执行与安全

owner 已批准的整批上限：20个任务、每任务1024 shots、最多6量子比特；遇收费提示停止。
当前计划8个业务电路加1个位序校准，共9个任务、9216 shots，业务电路最多4量子比特。
这不是价格报价或免费保证；SDK没有可用的账单报价接口。

云端需要 Python>=3.12，以及项目已有 `quafu-cloud` 可选依赖。将有效密钥在本机通过
`QUAFU_TOKEN` 或 `QUAFU_API_TOKEN` 注入进程环境，不写入 notebook，不粘贴聊天，不提交 Git。
不要使用文档、源码或搜索结果中的示例 token。

```bash
# 先在本机安全配置密钥环境；以下命令不包含密钥。
QB_FINANCE_RUN_CLOUD=1 QB_QUAFU_BACKEND=Dongling \
  python scripts/build_finance_notebooks.py --execute --html
```

默认设备不保证当前在线。需要根据真实平台状态选择设备；不得把模拟器作为真机回退。
五份笔记顺序共享 `output/finance-hardware/session.json`。任务 ID 在等待结果前落盘，
超时后重跑取回原任务，不自动再次提交。不要并行使用同一个账本，不要删账本绕过上限。
远端接受与本地持久化之间的崩溃窗口无法消除，应先核对平台任务页。

位序校准使用非对称态 `|10>`，不根据对称 Bell 态猜位序。校准优势不足80%、
counts 格式不符、shots 不一致或任务失败时停止金融分析。
云账本保留 task ID、设备、QASM、SHA256 和原始 counts，不包含凭据。
`*_hardware_evidence.json` 与本地 `*_evidence.json` 分开，重跑模拟器不会覆盖硬件证据。

## 已取回的真机结果

本批9个 Dongling 任务已完成，共9216实际shots。原始证据保存在
`output/finance-hardware/`，详细误差见
`docs/implementation/finance_quafu_hardware_acceptance.md`。真实结果存在较大偏差，
数值验收尚未通过；不能因任务完成就视为金融计算准确。
不必重新提交即可生成包含真实结果的笔记：

```bash
QB_FINANCE_REPLAY_HARDWARE=1 python scripts/build_finance_notebooks.py --execute --html
python scripts/export_finance_hardware_report.py
```

回放从账本加载实际提交的原始QASM，严格核对plan与receipt的SHA，并以原有
2e-14状态制备容差核对完整复状态，避免跨NumPy环境末位浮点差异造成错误重发。
原始counts与normalized counts分别导出。账本SHA是本地一致性检查，不是防恶意伪造签名。

## 解释结果的边界

- 数据准备、QAOA 角度训练、金融后处理和正确性对照是经典本地步骤；仅量子门电路提交云端。
- 风险与定价采用直接测量采样，不是 QAE，不获得 QAE 的渐近加速结论。
- 状态加载显式使用完整小向量，成本指数增长；没有隐藏免费 QRAM。
- VaR 在离散概率原子附近会跳档，1024 shots 不支持精确尾部风险认证。
- 三步二叉树和 Black–Scholes 的差异是离散模型误差；硬件噪声又是另一种误差。
- 静态对冲会降低本案例的损益标准差，不意味着所有市场情景无风险或已实现动态对冲系统。
- 本案例只有8天人工收益；年化历史波动率不是预测或真实资产评估。
- 没有最终真实 counts 的案例一律标记 `not_executed`，不宣称硬件通过。

实现代码：`quantumbridge/finance/{kernels,cases,execution}.py`。
验证：`tests/finance/test_finance_cases.py`。参考链接在每份 notebook 末尾。
