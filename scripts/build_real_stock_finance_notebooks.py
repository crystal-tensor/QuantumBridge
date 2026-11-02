#!/usr/bin/env python3
# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Execute two real-data finance applications and publish five taxonomy entries.

No network or cloud access occurs here. Existing synthetic cases/receipts remain
unchanged. Entry aliases share the same executed experiment, not invented runs.
"""
from copy import deepcopy
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import subprocess
import sys
import textwrap

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from nbconvert.preprocessors import TagRemovePreprocessor
from jupyter_client import KernelManager


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/jupyter-notebook/finance"
ENTRIES = [
    ("dwave_portfolio", "portfolio", "D-Wave CQM · 真实股票组合", "D-Wave CQM · Real-stock portfolio", "portfolio"),
    ("dwave_constraints", "financial-constraints", "D-Wave CQM · 预算与行业约束", "D-Wave CQM · Budget & sector constraints", "constraints"),
    ("qmc_pricing", "pricing", "量子蒙特卡洛 · IBM 期权模型定价", "Quantum Monte Carlo · IBM model pricing", "pricing"),
    ("qmc_risk", "risk", "量子蒙特卡洛 · 真实损失与 CVaR", "Quantum Monte Carlo · Historical loss & CVaR", "risk"),
    ("qmc_hybrid", "market-models", "可微混合模型 · IBM 波动研究", "Differentiable hybrid · IBM volatility research", "hybrid"),
]

COMMON = r'''
import sys, json, importlib.metadata, html
import numpy as np
from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
from IPython.display import display, HTML
from quantumbridge.finance import (
    load_stock_history, build_portfolio_cqm, solve_portfolio,
    pricing_case, risk_case, pennylane_qmc, hybrid_volatility_case,
)
from quantumbridge.finance.gate_exports import measurement_artifact
SHOTS, SEED = 1024, 20261102
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
versions = {p: importlib.metadata.version(p) for p in ['numpy','scipy','dimod','pennylane','torch']}
print('Python', sys.version.split()[0], '| installed dependencies:', versions)
print('Hardware jobs: 0 | Frozen historical replay, not current quotes or investment advice')

def table(rows):
    keys = list(rows[0])
    def cell(value):
        return html.escape(f'{value:.6g}' if isinstance(value, (float, np.floating)) else str(value))
    markup = '<div class="qb-table"><table><thead><tr>'+''.join('<th>'+cell(k)+'</th>' for k in keys)+'</tr></thead><tbody>'
    markup += ''.join('<tr>'+''.join('<td>'+cell(row[k])+'</td>' for k in keys)+'</tr>' for row in rows)
    display(HTML(markup+'</tbody></table></div>'))

def clean(value):
    if isinstance(value, dict):
        return {k: clean(v) for k,v in value.items() if k not in ('circuit','circuits','preparation')}
    if isinstance(value, (list,tuple)): return [clean(v) for v in value]
    if isinstance(value, np.generic): return value.item()
    return value

history = load_stock_history()
print(json.dumps(history.provenance, ensure_ascii=False, indent=2))
table([dict(symbol=s, first=history.dates[0], last=history.dates[-1], source_price_usd=float(history.prices[-1,i]))
       for i,s in enumerate(history.symbols)])
'''

INTRO = r'''
## 真实数据与运行条件 / Real data & reproducibility

输入是 MSFT、IBM、SBUX、AAPL 的真实历史价格序列，不是生成的股票数据。
固定训练窗口为 **2015-01-02 至 2015-12-31（252 个交易日）**；组合验证使用 2016 年的独立留出窗口。
行情来源为 Plotly 公开数据仓库，数据字节以 SHA-256 验证，源提交和许可保存在包内。
原始复权方法未得到独立核验，因此价格、单股成本与损益均为**来源价格口径的历史回放**，不宣称经审计总收益或今天可以买卖的报价。

在本仓库安装 `pip install -e ".[finance-apps]"`，另装 `jupyter nbconvert matplotlib`，选择同一个 Python 内核。
本 Notebook 可在仓库根目录从上到下运行；不自动联网、不读取 token、不提交云任务。
包内数据支持离线重跑，改变参数后得到的是重新计算的模型结果。

所有金额均为 USD。定价是模型估值而非已观测期权成交价；历史风险与未来风险不等价。
读取、统计、分箱和一般状态制备都有经典成本；这里不假设免费 QRAM，也未建立端到端量子加速。
'''

PORTFOLIO_MODEL = r'''
<a id="portfolio"></a>
## 1. CQM 投资组合：原理和约束

四个二元变量 xᵢ 表示是否持有一份来源价格单位；不是无限精度连续权重优化。
以 2015 年简单日收益估计年化 μ = 252 mean(r)，Σ = 252 cov(r)，权重 wᵢ = Pᵢ xᵢ / B。
目标为 **min λ wᵀΣw − μᵀw + fee Σxᵢ/B**。
预算约束为 Σ(Pᵢ + fee)xᵢ ≤ B；持仓数量 Σxᵢ = 2；MSFT、IBM、AAPL 的技术行业合计不超过 1。
SBUX 归入消费类。未投资现金按零利率计，单边交易费为每个买入 0.10 美元，不含退出费用。
收益年化与一次性费用的组合是示意目标，不是完备期限投资效用。

步骤：读取真实行情 → 仅训练期估计 μ/Σ → 建立真实 dimod CQM → ExactCQMSolver 枚举 →
独立检查全部 16 个位串的目标和约束 → 门电路 QAOA 对照 → 不参与训练的 2016 年价格回放。

**ExactCQMSolver 是经典 CPU 求解器，不是 D-Wave 量子硬件。**
CQM 对象可以交给另行配置的 Ocean 采样器，但这里没有创建或调用 Leap 客户端。
'''

PORTFOLIO = r'''
problem = build_portfolio_cqm(budget=220., risk_aversion=2., holdings=2, tech_cap=1, fee=.10)
print('Actual CQM variables:', list(problem.cqm.variables))
print('Actual CQM constraints:', list(problem.cqm.constraints))
print('Annual covariance:'); print(problem.covariance)
portfolio = solve_portfolio(problem, shots=SHOTS, seed=SEED, grid=13)
table(portfolio['candidates'])
print('CQM independently checked optimum:', portfolio['optimum'])
assert portfolio['status'] == 'solved'
assert all(row['cost'] <= 220+1e-9 for row in portfolio['candidates'] if row['feasible'])
fig, ax = plt.subplots(figsize=(9,3.3), layout='constrained')
ax.plot(history.dates, history.prices/history.prices[0]*100)
ax.set(xticks=np.arange(0,len(history.dates),50), ylabel='Source-price index (first day = 100)', title='Real stock history / 2015 training window')
ax.legend(history.symbols, ncol=4); plt.show()
'''

QAOA_MODEL = r'''
## 2. 面向夸父门电路的 QAOA 对照

夸父是门模型平台，不能直接执行 D-Wave 的 CQM/退火 API。
这里把同一组 16 个候选目标加上显式不可行惩罚，惩罚系数取目标极差加 1，保证惩罚后的全局最小点可行。
预算不等式没有假装变成二次式：使用完整对角真值表及 Walsh 展开，可能包含高阶 Z 串。
每个 Z 串由 CX 奇偶校验链和 RZ 实现，混合层为 RX，实际电路为 4 量子比特、p=1。
本地 13×13 网格通过理想期望值选择角度，随后独立测量 1024 shots，保留不可行样本。
有限网格、浅层电路和模拟测量都不保证找到最优；经典搜索成本也计入实现步骤，没有量子加速声明。
'''

QAOA = r'''
q = portfolio['qaoa']
print('Angles gamma/beta:', q['gamma'], q['beta'])
print('Encoding:', q['encoding'])
print('Best observed feasible:', q['best_observed'])
print('Observed objective gap:', q['observed_gap'])
print('Ideal feasible probability / sampled rate:', q['feasible_probability'], q['observed_feasible_rate'])
labels = [r['bits'] for r in portfolio['candidates']]
x = np.arange(16)
fig, ax = plt.subplots(figsize=(9,3.4), layout='constrained')
ax.bar(x-.18, q['ideal_probabilities'], .36, label='Native ideal probabilities', color='#087f72')
ax.bar(x+.18, [q['counts'][s]/SHOTS for s in labels], .36, label='1024 native simulator shots', color='#ba4164')
ax.set(xticks=x,xticklabels=labels,ylabel='Probability',title='QAOA real measured bitstrings / q0 first')
ax.tick_params(axis='x', labelrotation=45); ax.legend(); plt.show()
qaoa_artifact = measurement_artifact(q['circuit'])
print('Measurement-only QASM2:'); print(qaoa_artifact['openqasm'])
print('SHA / gates:', qaoa_artifact['sha256'], qaoa_artifact['gates'])
'''

CONSTRAINTS = r'''
<a id="constraints"></a>
## 3. 约束敏感性、中间结果和留出验证

下面改变预算，实际重复 CQM 检查。不可行结果保留为 `infeasible`，不偷偷删除约束。
最优模型组合固定于 2015-12-31，再用 2016 年行情回放；这不是在未来价格上选股票。
基准是四股等来源市值权重、现金零收益；基准未收取费用，不能视为完全匹配的可交易比较。
'''

CONSTRAINT_CODE = r'''
sensitivity = []
for budget in (100., 150., 220.):
    solved = solve_portfolio(build_portfolio_cqm(budget=budget), shots=32, grid=3)
    sensitivity.append(dict(budget=budget, status=solved['status'],
                            feasible_count=sum(r['feasible'] for r in solved['candidates']),
                            optimum=None if solved['optimum'] is None else solved['optimum']['bits']))
table(sensitivity)
h = portfolio['holdout']
fig, ax = plt.subplots(figsize=(9,3.3), layout='constrained')
ax.plot(h['dates'], np.array(h['portfolio_return'])*100, label='Fixed CQM portfolio incl. entry fees', color='#087f72')
ax.plot(h['dates'], np.array(h['equal_weight_return'])*100, label='Equal-weight, no fees', color='#ba4164')
ax.axhline(0, color='#687874', linewidth=.7)
ax.set(xticks=np.arange(0,len(h['dates']),10), ylabel='Source-price return (%)',title='2016 holdout / not used for portfolio selection')
ax.legend(); plt.show()
table([dict(portfolio_holdout_return=h['portfolio_return'][-1], equal_weight_return=h['equal_weight_return'][-1])])
portfolio_evidence = dict(application='D-Wave CQM + native gate-model comparison', result=clean(portfolio),
                          budget_sensitivity=sensitivity, gate_artifact=qaoa_artifact, versions=versions,
                          hardware_jobs=0)
'''

PRICING_MODEL = r'''
<a id="pricing"></a>
## 1. 量子蒙特卡洛：IBM 欧式期权模型定价

输入是 IBM 2015 年真实价格，S₀ 为来源中 2015-12-31 的价格，σ 由训练期对数收益标准差年化。
示例假设 r=3%、零股息、剩余 30/252 年、K=S₀；这些是明确的模型参数，不是市场期权合约报价。
风险中性 Q 下的 GBM 为 Sᵀ = S₀ exp[(r−σ²/2)T + σ√T z]。
将标准正态等概率分为 8 格，采用各格中点分位数，支付为折现后的 max(Sᵀ−K,0) 或 max(K−Sᵀ,0)。

先把支付仿射归一化到 [0,1]，RY/CX 制备 A|0〉 = Σ√pᵢ |i〉(√(1−fᵢ)|0〉+√fᵢ|1〉)。
末位 1 的概率即 μ=Σpᵢfᵢ。QuantumBridge 运行 A、QA、Q²A、Q⁴A，
对各电路实际计数拟合 sin²[(2k+1)θ] 的二项似然，再反归一化得到金融金额。
不是从经典期望值直接填入“量子结果”。每个电路 1024 shots，共 4096 shots；
Grover 调用总计 7168，A/A† 等价制备调用总计 18432（不等于物理门数）。

比较三个量：连续 Black–Scholes、8 格经典精确期望、本地有限 shots 的 MLAE。
前两者差是模型离散化误差；后两者差才是本次估计误差，不能混在一起。
'''

PRICING = r'''
pricing = pricing_case(strike_ratio=1., rate=.03, maturity_days=30, shots=SHOTS, seed=SEED)
print({k:pricing[k] for k in ['spot','strike','volatility','rate','maturity_days','dates','probability_measure']})
table([dict(scenario=i, probability=p, terminal_price=s, discounted_call=c, discounted_put=v)
       for i,(p,s,c,v) in enumerate(zip(pricing['probabilities'],pricing['scenario_prices'],pricing['call_payoffs'],pricing['put_payoffs']))])
table([dict(payoff=k, black_scholes=pricing['black_scholes'][k], discrete=pricing[k]['exact_discrete'],
            native_mlae=pricing[k]['estimate'], unamplified=pricing[k]['unamplified_estimate'],
            grid_error=pricing[k]['exact_discrete']-pricing['black_scholes'][k],
            estimation_error=pricing[k]['estimate']-pricing[k]['exact_discrete'],
            likelihood_95_interval=pricing[k]['confidence_interval']) for k in ['call','put']])
fig, ax = plt.subplots(figsize=(9,3.3), layout='constrained')
ax.plot(pricing['scenario_prices'],pricing['call_payoffs'],'o-',label='Discounted call',color='#087f72')
ax.plot(pricing['scenario_prices'],pricing['put_payoffs'],'o-',label='Discounted put',color='#ba4164')
ax.set(xlabel='IBM terminal scenario / USD',ylabel='Discounted payoff / USD',title='Actual-stock calibrated 8-point risk-neutral model')
ax.legend(); plt.show()
'''

PL_MODEL = r'''
## 2. 实际 PennyLane 参考调用和中间结果

下面真正调用已安装 PennyLane 的 `QuantumMonteCarlo` 模板和 `default.qubit`。
该模板用矩阵实现、不可直接求导，属于模拟器参考路径；不是夸父直接执行入口。
为避免平方反射的 μ 与 1−μ 相位歧义，支付编码到 [0,1/2]，取共轭峰折叠后的模态格点。
保留所有相位概率，5 个估计位加 4 个目标位共 9 比特，显示有限相位分辨率误差。
这与只需 4 比特的 Native MLAE 是两条不同实现路径，不把参考模板冒充原生完整替代。
'''

PL_CODE = r'''
pl_reference = pennylane_qmc(pricing['probabilities'], pricing['call_payoffs'], estimation_wires=5)
print({k:v for k,v in pl_reference.items() if k != 'probabilities'})
q = pricing['call']
table([dict(power=k, counts=c, successes=n, success_rate=n/SHOTS)
       for k,c,n in zip(q['schedule'],q['counts'],q['good_counts'])])
fig, axes = plt.subplots(1,2,figsize=(10,3.4),layout='constrained')
theta = np.arcsin(np.sqrt((q['exact_discrete']-q['normalization']['offset'])/q['normalization']['scale']))
powers = np.array(q['schedule'])
axes[0].plot(powers,np.sin((2*powers+1)*theta)**2,'o-',label='Exact model',color='#087f72')
axes[0].plot(powers,np.array(q['good_counts'])/SHOTS,'s--',label='Measured native shots',color='#ba4164')
axes[0].set(xlabel='Grover power k',ylabel='Success probability',title='Native MLAE actual circuit counts'); axes[0].legend()
axes[1].bar(np.arange(32)/32,pl_reference['probabilities'],width=.025,color='#087f72')
axes[1].set(xlabel='Estimated phase',ylabel='Probability',title='Actual PennyLane QMC / 9-qubit simulator')
plt.show()
gate_artifacts = [measurement_artifact(c) for c in q['circuits']]
table([dict(power=k,qubits=a['num_qubits'],gates=a['gates'],two_qubit_gates=a['two_qubit_gates'],sha256=a['sha256'])
       for k,a in zip(q['schedule'],gate_artifacts)])
print('Native A / preparation circuit QASM2:'); print(gate_artifacts[0]['openqasm'])
'''

RISK_MODEL = r'''
<a id="risk"></a>
## 3. 风险计量：真实损失、VaR 与 CVaR

本金 1000 美元，真实日损失 Lₜ = −1000 rₜ，可为负值（盈利）。此处概率测度为历史 P，**不是定价的风险中性 Q**。
先从全部 251 个历史收益计算 95% VaR，以及含阈值处分数概率质量的 ES/CVaR。
按损失排序分为 8 组，以各组均值压缩，保留精确期望损失；分组会改变分位数和质心 CVaR，因此单独列出偏差。
为估计原历史分布的 CVaR，经典求得阈值 v，再对每组的 max(L−v,0) 求条件均值，
量子估计其期望；最后 CVaR = v + E[(L−v)⁺]/0.05。
这样尾部期望在离散化前后严格相同。**VaR 阈值仍是经典计算，不是量子分位数搜索。**
同一组尾部支付另交给真正的 PennyLane `QuantumMonteCarlo` 模板执行，
保留相位格点和全部概率。其有限相位分辨率误差会被 1/0.05 放大，不能用 MLAE 的采样区间替它背书。
95% 似然比区间仅是渐近采样区间包络，不包含模型、历史抽样不确定性或硬件误差，也不保证有限样本覆盖率。
'''

RISK_CODE = r'''
risk = risk_case(confidence=.95,notional=1000.,shots=SHOTS,seed=SEED)
table([dict(bin=i,probability=p,mean_loss=v,mean_tail_excess=e)
       for i,(p,v,e) in enumerate(zip(risk['probabilities'],risk['bin_values'],risk['excess_values']))])
print('Full-history classical reference:', {k:v for k,v in risk['raw_reference'].items() if k not in ['cdf','sorted_losses']})
print('Centroid-only reference:', {k:v for k,v in risk['centroid_binned_reference'].items() if k not in ['cdf','sorted_losses']})
table([dict(metric='Expected loss',historical=risk['raw_reference']['expected_loss'],native_mlae=risk['mean']['estimate'],interval=risk['mean']['confidence_interval']),
       dict(metric='CVaR / ES',historical=risk['raw_reference']['CVaR_expected_shortfall'],native_mlae=risk['cvar_estimate'],interval=risk['cvar_interval'])])
pl_risk_reference = pennylane_qmc(risk['probabilities'], risk['excess_values'], estimation_wires=5)
pl_risk_reference['cvar_estimate'] = risk['raw_reference']['VaR'] + pl_risk_reference['estimate']/(1-risk['confidence'])
pl_risk_reference['cvar_discrete_reference'] = risk['raw_reference']['VaR'] + pl_risk_reference['exact_discrete']/(1-risk['confidence'])
print('Actual PennyLane tail-excess phase grid:', {k:v for k,v in pl_risk_reference.items() if k != 'probabilities'})
table([dict(metric='CVaR / ES',historical=risk['raw_reference']['CVaR_expected_shortfall'],
            native_mlae=risk['cvar_estimate'],pennylane_qmc=pl_risk_reference['cvar_estimate'],
            pennylane_grid_error=pl_risk_reference['cvar_estimate']-pl_risk_reference['cvar_discrete_reference'])])
assert np.isclose(np.dot(risk['probabilities'],risk['bin_values']),np.mean(risk['losses']))
assert np.isclose(risk['raw_reference']['VaR']+np.dot(risk['probabilities'],risk['excess_values'])/.05,risk['raw_reference']['CVaR_expected_shortfall'])
assert np.isclose(pl_risk_reference['cvar_discrete_reference'],risk['raw_reference']['CVaR_expected_shortfall'])
fig, ax = plt.subplots(figsize=(9,3.4), layout='constrained')
ax.hist(risk['losses'],bins=30,color='#087f72',alpha=.85)
ax.axvline(risk['raw_reference']['VaR'],color='#ba4164',label='95% historical VaR')
ax.set(xlabel='One-session loss on USD 1000 / negative = gain',ylabel='Observed sessions',title='IBM actual 2015 loss history, not synthetic returns')
ax.legend(); plt.show()
'''

HYBRID_MODEL = r'''
<a id="hybrid"></a>
## 4. 可微分电路：混合波动模型研究

QMC 相位估计模板本身不可微；以下是**独立**的可训练模型，不能混为同一个可微算法。
用前两个已知日收益预测下一交易日绝对收益。最早 75% 为训练，末尾 25% 为验证，归一化仅从训练期估计。
2 比特 Native QNode 用 RY 编码、4 个旋转参数和 CNOT，测量 Z 期望；
经典线性头加 softplus 输出非负预测，PyTorch Adam 对量子参数和经典参数真实反向传播。
当前核心不支持本例多来源广播 backprop，因此逐条执行标量 QNode，**没有放宽资源上限**。
展示每轮损失、量子梯度范数、留出 MSE 与训练均值常数预测的 MSE。
若未优于常数基线也原样保留，不称为预测优势。
'''

HYBRID_CODE = r'''
hybrid = hybrid_volatility_case(epochs=15,seed=SEED)
print('Training / validation dates:',hybrid['train_dates'],hybrid['validation_dates'])
table([dict(epoch=i+1,train_mse=mse,quantum_gradient_norm=g)
       for i,(mse,g) in enumerate(zip(hybrid['train_mse'],hybrid['circuit_gradient_norms']))])
print('Real trained circuit parameters:',hybrid['weights'],'| classical head:',hybrid['classical_head'])
table([dict(validation_mse=hybrid['validation_mse'],constant_baseline_mse=hybrid['baseline_mse'],
            beats_constant=hybrid['validation_mse'] < hybrid['baseline_mse'])])
fig, axes=plt.subplots(2,1,figsize=(9,5.5),layout='constrained')
axes[0].plot(range(1,16),hybrid['train_mse'],'o-',color='#087f72')
axes[0].set(xlabel='Epoch',ylabel='Training MSE',title='Actual native differentiable circuit training')
axes[1].plot(hybrid['dates'],np.array(hybrid['actual'])*100,label='Observed next-session absolute return',color='#626e6a')
axes[1].plot(hybrid['dates'],np.array(hybrid['predictions'])*100,label='Hybrid prediction',color='#ba4164')
axes[1].axhline(hybrid['target_scale']*100,color='#087f72',linestyle='--',label='Train-mean baseline')
axes[1].set(xticks=np.arange(0,len(hybrid['dates']),15),ylabel='Absolute return (%)',title='Chronological validation / no future fitting')
axes[1].legend(); plt.show()
qmc_evidence = dict(application='Native MLAE + PennyLane QMC + differentiable hybrid research',
                    pricing=clean(pricing), risk=clean(risk), hybrid=hybrid,
                    pennylane_reference=pl_reference, pennylane_risk_reference=pl_risk_reference,
                    gate_artifacts=gate_artifacts,
                    versions=versions, hardware_jobs=0)
'''

LIMITS = r'''
## 运行边界与夸父迁移 / Limits & Quafu path

本次 **0 个云端/真机任务**，不消耗原金融批次额度、不改写其回执。
现有 D3 审计仍是 NO_NEW_SUBMISSION_RECOMMENDED；物理布局、位序和精度验收没有被本批模拟解除。
Native QAOA/MLAE 电路已分解为基础门并导出可检查的 QASM2，量子比特不超过 4；
QASM2 不能保存全局相位，因此导出显式记录所移除的顶层相位，只承诺终端测量概率，不能作为保相位受控子程序复用。
PennyLane 矩阵参考电路是 9 比特模拟，未承诺可在旧的 6 比特真机额度下运行。
未来接真机前需要独立核验 gate basis、耦合图、深度、布局、位序和额外任务预算；
深 Grover 电路可能受噪声限制，不能把成功序列化称为硬件可用，更不能声称量子优势。

本次只有小规模金融研究应用，并不表示已完成 Qiskit + PennyLane 全部核心函数融合或生产金融系统。

### 练习与解答骨架
改变预算或执行价，只使用训练期重新计算；比较目标、可行性、离散化和有限 shots 误差。
不要用留出期选择预算、股票、角度或训练超参数。

### 一手来源
- [D-Wave ExactCQMSolver：经典本地枚举](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/sampler_composites.html)
- [D-Wave 官方组合优化示例：概念参考，未复制源码](https://github.com/dwave-examples/portfolio-optimization)
- [PennyLane QuantumMonteCarlo：模板和模拟器限制](https://docs.pennylane.ai/en/stable/code/api/pennylane.QuantumMonteCarlo.html)
- [真实行情源：固定提交](https://github.com/plotly/datasets/blob/0f7c47868a3393316098a8bf97d548e1ee23d22a/stockdata.csv)
- [行情源仓库 MIT 许可](https://github.com/plotly/datasets/blob/master/LICENSE)
- [原有夸父 D3 契约审计](finance_quafu_d3_client_contract.html)

QuantumBridge · 所属 相干(北京)科技有限公司
'''

STYLE = '''<style>
*{letter-spacing:0}body{color:#202a28;background:#fff}.jp-Notebook{max-width:1100px;margin:auto}
.jp-RenderedHTMLCommon{line-height:1.85}h1{font-size:27px!important;overflow-wrap:anywhere}h2{font-size:21px!important}
.jp-InputArea-editor,.jp-OutputArea-output{max-width:100%;overflow-x:auto}
.jp-RenderedImage img{max-width:100%;height:auto}.jp-RenderedText pre{white-space:pre-wrap;overflow-wrap:anywhere}
.qb-table{overflow:auto}table{font-size:13px}.qb-table td,.qb-table th{padding:8px;max-width:400px;overflow-wrap:anywhere}
.qb-overview{max-width:1060px;margin:24px auto 12px;padding:20px 24px;border-block:1px solid #d8e2dd;font:15px/1.7 system-ui,sans-serif}
.qb-overview h1{margin:4px 0 12px}.qb-overview a{color:#087467;text-underline-offset:3px}.qb-overview nav{display:flex;flex-wrap:wrap;gap:8px 24px}
.qb-facts{display:flex;flex-wrap:wrap;gap:12px 30px;padding:12px 0;border-block:1px solid #d8e2dd}.qb-facts strong{color:#087467}
.qb-overview figure{margin:20px 0 0}.qb-overview img{max-width:100%;height:auto;width:850px}.qb-overview figcaption{font-size:13px;color:#576b61}
.qb-warning{border-left:3px solid #ba4164;padding:8px 14px;background:#fbf5f7}.qb-overview small{color:#53685e}
@media(max-width:600px){h1{font-size:23px!important}.jp-Notebook{padding:8px!important}.jp-Cell{padding:4px!important}.qb-overview{padding:16px;margin:12px 0}.qb-table{max-width:100%}}
</style>'''


def code(source):
    return nbformat.v4.new_code_cell(textwrap.dedent(source).strip())


def md(source):
    return nbformat.v4.new_markdown_cell(textwrap.dedent(source).strip())


def execute(name, title, sections, evidence_name):
    scaffold = ROOT / "tmp/jupyter-notebook" / (name+".ipynb")
    helper = Path.home()/".codex/skills/jupyter-notebook/scripts/new_notebook.py"
    subprocess.run([sys.executable, str(helper), "--kind", "tutorial", "--title", title,
                    "--out", str(scaffold), "--force"], check=True)
    notebook = nbformat.read(scaffold, as_version=4)
    notebook.metadata.title = title
    notebook.metadata.kernelspec = {"name":"python3", "display_name":"Python 3", "language":"python"}
    notebook.cells = [md("# "+title+"\n\n真实股票历史回放 / Local execution, not hardware"), md(INTRO), code(COMMON)]
    notebook.cells += sections
    notebook.cells += [md(LIMITS), code(f"print('EVIDENCE_JSON='+json.dumps({evidence_name}, ensure_ascii=False, allow_nan=False))")]
    manager = KernelManager(kernel_name="python3")
    manager.kernel_spec.argv = [sys.executable,"-m","ipykernel_launcher","-f","{connection_file}"]
    NotebookClient(notebook, timeout=300, km=manager).execute(cwd=ROOT)
    nbformat.validate(notebook)
    evidence, images = None, []
    for cell in notebook.cells:
        for output in cell.get("outputs", []):
            if output.output_type == "error":
                raise RuntimeError(output)
            if "image/png" in output.get("data", {}):
                images.append(output.data["image/png"])
            for line in output.get("text", "").splitlines():
                if line.startswith("EVIDENCE_JSON="):
                    evidence = json.loads(line[len("EVIDENCE_JSON="):])
    if evidence is None or not images or evidence["hardware_jobs"] != 0:
        raise RuntimeError("Missing real experiment output")
    # Keep audit JSON in the downloadable notebook, but collapse its long cell.
    notebook.cells[-1].metadata["tags"] = ["audit-json"]
    return notebook, evidence, images


def export_entry(entry, notebook, evidence, images):
    filename, direction, title, english, section = entry
    notebook = deepcopy(notebook)
    notebook.metadata["quantumbridge"] = dict(domain="finance",direction=direction,execution_mode="local-simulation",hardware_jobs=0,
                                              shared_experiment="dwave_portfolio" if filename.startswith("dwave") else "qmc_pricing")
    nbformat.write(notebook, OUTPUT/(filename+".ipynb"))
    exporter = HTMLExporter(template_name="lab", exclude_input_prompt=True, exclude_output_prompt=True)
    exporter.register_preprocessor(TagRemovePreprocessor(remove_cell_tags={"audit-json"}), enabled=True)
    body, _ = exporter.from_notebook_node(notebook)
    links = ''.join(f'<a href="{file}.html#{anchor}">{html.escape(zh)}</a>' for file,_,zh,_,anchor in ENTRIES)
    if filename.startswith("dwave"):
        result = evidence["result"]
        facts = f'<span>CQM 最优位串 <strong>{result["optimum"]["bits"]}</strong></span><span>QAOA 采样可行率 <strong>{result["qaoa"]["observed_feasible_rate"]:.1%}</strong></span>'
        image = images[1]
        caption = "本次真实本地输出：原生 QAOA 理想概率与 1024 次模拟测量。CQM 求解为经典 CPU。"
    else:
        if section == "risk":
            result = evidence["risk"]
            facts = f'<span>历史 CVaR <strong>${result["raw_reference"]["CVaR_expected_shortfall"]:.4f}</strong></span><span>MLAE 估计 <strong>${result["cvar_estimate"]:.4f}</strong></span>'
        elif section == "hybrid":
            result = evidence["hybrid"]
            facts = f'<span>混合模型 MSE <strong>{result["validation_mse"]:.8f}</strong></span><span>常数基线 MSE <strong>{result["baseline_mse"]:.8f}</strong></span>'
        else:
            result = evidence["pricing"]["call"]
            facts = f'<span>离散看涨期望 <strong>${result["exact_discrete"]:.4f}</strong></span><span>MLAE 估计 <strong>${result["estimate"]:.4f}</strong></span>'
        image = images[0] if section == "pricing" else images[2] if section == "risk" else images[3]
        caption = "本次已执行输出：真实 IBM 历史校准、有限离散模型、本地模拟。不是实时市场报价。"
    banner = f'''<section class="qb-overview" aria-label="应用执行摘要">
<small>QUANTUMBRIDGE / FINANCE / REAL STOCK HISTORY</small><h1>{html.escape(title)}</h1><p>{html.escape(english)}</p>
<div class="qb-facts">{facts}<span>真机任务 <strong>0</strong></span></div>
<p class="qb-warning">历史数据：2015 年。已执行的函数库与 Notebook 示例，不是网页实时求解或今天的股票报价。未宣称量子优势或生产支持。</p>
<nav aria-label="金融应用分类">{links}</nav><p><a href="#{section}">本分类的原理、步骤、代码与结果</a> · <a href="{filename}.ipynb" download>下载已执行 Notebook</a></p>
<figure><img src="data:image/png;base64,{image}" alt="{html.escape(caption)}"><figcaption>{caption}</figcaption></figure></section>'''
    body = body.replace("</head>", STYLE+"</head>")
    index = body.index('>', body.index('<body'))+1
    body = body[:index]+banner+body[index:]
    body = body.replace('<html lang="en">','<html lang="zh-CN">')
    (OUTPUT/(filename+".html")).write_text(body, encoding="utf-8")
    print("Exported", filename, "actual executed experiment; hardware jobs 0", flush=True)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    portfolio = execute("dwave_real_stock", "D-Wave CQM 与 QuantumBridge 门模型组合应用", [
        md(PORTFOLIO_MODEL), code(PORTFOLIO), md(QAOA_MODEL), code(QAOA), md(CONSTRAINTS), code(CONSTRAINT_CODE),
    ], "portfolio_evidence")
    qmc = execute("qmc_real_stock", "QuantumBridge 量子蒙特卡洛与可微金融研究", [
        md(PRICING_MODEL), code(PRICING), md(PL_MODEL), code(PL_CODE), md(RISK_MODEL), code(RISK_CODE),
        md(HYBRID_MODEL), code(HYBRID_CODE),
    ], "qmc_evidence")
    for entry in ENTRIES:
        export_entry(entry, *(portfolio if entry[0].startswith("dwave") else qmc))
    evidence = dict(generated_at=datetime.now(timezone.utc).isoformat(), hardware_jobs=0,
                    portfolio=portfolio[1], qmc=qmc[1])
    (ROOT/"tmp/real_stock_finance_evidence.json").write_text(json.dumps(evidence,indent=2,ensure_ascii=False,allow_nan=False)+"\n")


if __name__ == "__main__":
    main()
