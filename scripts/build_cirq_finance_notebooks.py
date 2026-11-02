#!/usr/bin/env python3
# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Execute original Cirq finance teaching cases and export their public pages.

Only local Cirq simulation is used. No provider client, credential, download,
installation or hardware path is present. Existing Quafu artifacts are untouched.
"""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
import textwrap

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/jupyter-notebook/finance"
SOURCES = {
    "qaoa": ("Google Cirq · QAOA / Ising", "https://quantumai.google/cirq/experiments/qaoa/qaoa_ising"),
    "walk": ("Google Cirq · Quantum walk", "https://quantumai.google/cirq/experiments/quantum_walks"),
    "simulation": ("Google Cirq · Simulation", "https://quantumai.google/cirq/simulate/simulation"),
    "diagonal": ("Cirq · DiagonalGate API", "https://quantumai.google/reference/python/cirq/DiagonalGate"),
    "experiments": ("Google Cirq · Experiments", "https://quantumai.google/cirq/experiments"),
}

COMMON = r"""
import json, sys
import cirq
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, HTML

SEED, SHOTS = 20261101, 4096
simulator = cirq.Simulator(dtype=np.complex128, seed=SEED)
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
print('Backend: local cirq.Simulator | Cirq:', cirq.__version__)
print('Python:', sys.version.split()[0], '| hardware jobs: 0')
print('Bit order: q0 first / most significant bit; synthetic data only.')

def probabilities(circuit, qubits):
    state = simulator.simulate(circuit, qubit_order=qubits).final_state_vector
    return np.abs(state)**2

def measured_counts(circuit, qubits, key='out'):
    measured = circuit + cirq.Circuit(cirq.measure(*qubits, key=key))
    histogram = simulator.run(measured, repetitions=SHOTS).histogram(key=key)
    return np.array([histogram.get(i, 0) for i in range(2**len(qubits))], dtype=int)

def compare_plot(labels, exact, sampled, title):
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8, 3.3), layout='constrained')
    ax.bar(x-.18, exact, .36, label='Exact model', color='#137f76')
    ax.bar(x+.18, sampled, .36, label='4096 local Cirq shots', color='#bc4164')
    ax.set(xticks=x, xticklabels=labels, ylabel='Probability', title=title)
    ax.legend()
    plt.show()
"""

PREPARE = r"""
def prepare_four(probabilities, qubits):
    p = np.asarray(probabilities, dtype=float)
    assert p.shape == (4,) and np.all(p > 0) and np.isclose(p.sum(), 1)
    left = p[0] + p[1]
    circuit = cirq.Circuit(cirq.ry(2*np.arccos(np.sqrt(left)))(qubits[0]))
    circuit.append(cirq.ry(2*np.arccos(np.sqrt(p[0]/left)))(qubits[1])
                   .controlled_by(qubits[0], control_values=[0]))
    circuit.append(cirq.ry(2*np.arccos(np.sqrt(p[2]/(1-left))))(qubits[1])
                   .controlled_by(qubits[0], control_values=[1]))
    return circuit
"""

QAOA = r"""
qubits = list(cirq.LineQubit.range(3))
states = np.array([[int(c) for c in f'{i:03b}'] for i in range(8)])
costs = np.array([objective(x) for x in states])
allowed = np.array([feasible(x) for x in states])
assert allowed.any() and allowed[np.argmin(costs)]
exact_best = float(costs[allowed].min())
optimal = allowed & np.isclose(costs, exact_best)
scaled = (costs-costs.min()) / np.ptp(costs)

def qaoa_circuit(gamma, beta):
    return cirq.Circuit(cirq.H.on_each(*qubits),
                        cirq.DiagonalGate((-gamma*scaled).tolist()).on(*qubits),
                        [cirq.rx(2*beta)(q) for q in qubits])

# Exact simulator expectations choose angles; no measured solution is preloaded.
trace, best = [], None
for gamma in np.linspace(0, 2*np.pi, 25):
    for beta in np.linspace(0, np.pi, 25):
        candidate = qaoa_circuit(gamma, beta)
        probs = probabilities(candidate, qubits)
        energy = float(probs @ costs)
        if best is None or energy < best[0]:
            best = (energy, float(gamma), float(beta), candidate, probs)
            trace.append(energy)
energy, gamma, beta, circuit, exact = best

# Independent dense tensor-product formula validates the selected circuit.
rotation = np.array([[np.cos(beta), -1j*np.sin(beta)],
                     [-1j*np.sin(beta), np.cos(beta)]])
mixer = np.kron(np.kron(rotation, rotation), rotation)
reference = np.abs(mixer @ (np.exp(-1j*gamma*scaled)/np.sqrt(8)))**2
assert np.allclose(exact, reference, atol=1e-12)
print('All candidates: bitstring, objective, feasible')
for i, x in enumerate(states):
    print(''.join(map(str, x)), round(float(costs[i]), 6), bool(allowed[i]))
print('Selected angles / expected cost:', gamma, beta, energy)
print('Circuit:', circuit, sep='\n')
plt.figure(figsize=(8, 3))
plt.plot(trace, marker='.', color='#137f76')
plt.xlabel('Improving grid candidate'); plt.ylabel('Expected cost')
plt.title('Local QAOA angle search, p=1'); plt.tight_layout(); plt.show()

counts = measured_counts(circuit, qubits)
sampled = counts/SHOTS
observed_feasible = np.flatnonzero(allowed & (counts > 0))
winner = (int(min(observed_feasible, key=lambda i: costs[i]))
          if len(observed_feasible) else None)
compare_plot([f'{i:03b}' for i in range(8)], exact, sampled, 'Cirq QAOA: all bitstrings')
evidence = {
    'qubits': 3, 'shots': SHOTS, 'counts': counts.tolist(),
    'gamma': gamma, 'beta': beta, 'expected_cost': energy,
    'exact_feasible_optimum': exact_best,
    'best_sampled_feasible': None if winner is None else f'{winner:03b}',
    'sampled_gap': None if winner is None else float(costs[winner]-exact_best),
    'feasible_probability': float(sampled[allowed].sum()),
    'optimal_probability': float(sampled[optimal].sum()),
    'ideal_probability': exact.tolist(),
    'validation': 'Cirq state checked against independent dense QAOA formula',
}
assert counts.sum() == SHOTS and np.isclose(exact.sum(), 1)
"""

CASES = [
    {
        "file": "cirq_portfolio", "direction": "portfolio",
        "title": "QAOA 资产组合选择", "en": "QAOA portfolio selection",
        "method": "QAOA / Ising", "sources": ["qaoa", "diagonal"],
        "summary": "3 个合成资产中选 2 个，比较风险收益目标、可行率和最优命中率。",
        "principle": r"""
        三个合成资产以二元持仓 $x_i$ 表示，目标为
        $C(x)=0.5x^T\Sigma x-\mu^Tx+2(\sum_i x_i-2)^2$。
        收益与协方差使用同一示意期；这不是连续权重优化。
        $x_i=(1-Z_i)/2$ 将二次成本变成对角 Ising 哈密顿量。
        本例用对角成本门精确施加相位，再用 RX 混合器构成单层 QAOA。
        角度采用 $e^{-i\gamma C_{scaled}}$ 与 $e^{-i\beta\sum X}$ 约定，
        不直接套用官方教程的另一种角度归一化。
        """,
        "steps": "给定均值与正定协方差 → 枚举 8 个状态检验罚项 → 625 组角度的本地精确期望搜索 → 4096 shots → 按原持仓约束解码 → 与经典最优比较。",
        "boundary": "Google 官方提供通用 QAOA 教程，不是此资产模型。金融目标和代码由 QuantumBridge 自行编写。p=1 网格搜索不保证最优；枚举成本表是指数规模教学实现，不是可扩展投资系统或量子优势证明。",
        "code": """
        mu = np.array([.08, .12, .10])
        covariance = np.array([[.04,.01,.005],[.01,.09,.015],[.005,.015,.06]])
        assert np.linalg.eigvalsh(covariance).min() > 0
        def objective(x):
            return .5*x@covariance@x-mu@x+2*(x.sum()-2)**2
        def feasible(x):
            return x.sum() == 2
        """,
        "kernel": QAOA,
    },
    {
        "file": "cirq_risk", "direction": "risk",
        "title": "损失分布与 VaR / CVaR", "en": "Loss distribution & VaR / CVaR",
        "method": "Probability encoding / sampling", "sources": ["simulation"],
        "summary": "两量子比特编码四种损失情景，用经验分布估计预期损失与尾部风险。",
        "principle": r"""
        假定损失 $L=(0,1,4,12)$，物理概率 $p=(0.55,0.25,0.15,0.05)$。
        用受控 RY 制备 $\sum_j\sqrt{p_j}|j\rangle$，测量得到经验概率。
        $VaR_\alpha=\inf\{l:F(l)\ge\alpha\}$；离散 CVaR 使用期望短缺定义
        $ES_\alpha=VaR_\alpha+\frac{\sum_jp_j(L_j-VaR_\alpha)^+}{1-\alpha}$，
        不能误用 $E[L|L\ge VaR]$。本例 $\alpha=0.85$，精确 EL=1.45、VaR=4、ES=20/3。
        """,
        "steps": "定义合成损失与概率 → 条件概率转 RY → 检查振幅平方 → 4096 次本地测量 → 经验 CDF → EL / VaR / ES → DKW 分位不确定区间。",
        "boundary": "Cirq 官方模拟与测量 API 是技术基础；VaR/CVaR 业务逻辑是我们的扩展。这里是直接采样，不是量子振幅估计；没有信用校准、稀有风险认证或完整风控平台。",
        "code": """
        qubits = list(cirq.LineQubit.range(2))
        p, losses, alpha = np.array([.55,.25,.15,.05]), np.array([0.,1.,4.,12.]), .85
        """,
        "kernel": PREPARE + textwrap.dedent(r"""
        circuit = prepare_four(p, qubits)
        exact = probabilities(circuit, qubits)
        assert np.allclose(exact, p, atol=1e-12)
        print('Prepared state probabilities:', exact)
        print('Circuit:', circuit, sep='\n')
        counts = measured_counts(circuit, qubits)
        empirical = counts/SHOTS
        def risk(probability):
            index = int(np.searchsorted(np.cumsum(probability), alpha))
            var = float(losses[index])
            return {'EL': float(probability@losses), 'VaR': var,
                    'CVaR_ES': float(var+probability@np.maximum(losses-var, 0)/(1-alpha))}
        reference, sampled = risk(p), risk(empirical)
        assert np.isclose(reference['EL'], 1.45)
        assert reference['VaR'] == 4 and np.isclose(reference['CVaR_ES'], 20/3)
        epsilon = float(np.sqrt(np.log(2/.05)/(2*SHOTS)))
        quantile = lambda a: float(losses[min(np.searchsorted(np.cumsum(empirical), a), 3)])
        var_interval = [quantile(max(0, alpha-epsilon)), quantile(min(1, alpha+epsilon))]
        compare_plot([str(v) for v in losses], p, empirical, 'Loss scenarios, not market observations')
        plt.figure(figsize=(8,3))
        plt.step(losses, np.cumsum(p), where='post', label='Exact CDF', color='#137f76')
        plt.step(losses, np.cumsum(empirical), where='post', label='Sampled CDF', color='#bc4164')
        plt.axhline(alpha, color='black', ls='--', label='alpha=.85')
        plt.xlabel('Loss'); plt.ylabel('CDF'); plt.legend(); plt.tight_layout(); plt.show()
        evidence = {'qubits': 2, 'shots': SHOTS, 'counts': counts.tolist(),
                    'exact': reference, 'sampled': sampled,
                    'var_95pct_DKW_interval': var_interval, 'dkw_epsilon': epsilon,
                    'ideal_probability': exact.tolist(),
                    'validation': 'Prepared distribution and independent exact EL/VaR/ES checked'}
        """),
    },
    {
        "file": "cirq_pricing", "direction": "pricing",
        "title": "离散欧式期权定价", "en": "Discrete European option pricing",
        "method": "Payoff rotation / sampling", "sources": ["simulation"],
        "summary": "离散风险中性情景加收益辅助比特，展示折现价格与采样误差。",
        "principle": r"""
        假定到期价格 $S_T=(80,95,110,130)$，风险中性概率 $Q=(0.55,0.25,0.15,0.05)$，
        $K=100,r=0.02,T=1$。这些是自定义离散风险中性模型，隐含现货
        $S_0=e^{-rT}E_Q[S_T]$，不是从行情校准或复刻 Black–Scholes。
        为每个情景在辅助位施加 $RY(2\arcsin\sqrt{(S_T-K)^+/30})$，
        则 $P(a=1)=E_Q[(S_T-K)^+]/30=0.1$；价格 $C=e^{-rT}30P(a=1)$。
        95% Wilson 区间仅表示二项抽样不确定性，不包含模型和硬件误差。
        """,
        "steps": "声明风险中性假设和隐含现货 → 制备情景 → 受控收益旋转 → 检查辅助位精确概率 → 4096 shots → 折现价格与 Wilson 区间。",
        "boundary": "这是 QuantumBridge 用 Cirq API 编写的金融教学扩展，不是 Google 官方期权教程。使用普通采样而非 QAE；未实现动态对冲、路径依赖、多资产定价或量子加速。",
        "code": """
        scenarios = list(cirq.LineQubit.range(2))
        ancillary = cirq.LineQubit(2)
        p = np.array([.55,.25,.15,.05])
        terminal = np.array([80.,95.,110.,130.])
        rate, maturity, strike, scale = .02, 1., 100., 30.
        payoff = np.maximum(terminal-strike, 0)
        """,
        "kernel": PREPARE + textwrap.dedent(r"""
        circuit = prepare_four(p, scenarios)
        for i, value in enumerate(payoff):
            bits = [int(c) for c in f'{i:02b}']
            circuit.append(cirq.ry(2*np.arcsin(np.sqrt(value/scale)))(ancillary)
                           .controlled_by(*scenarios, control_values=bits))
        exact = probabilities(circuit, [*scenarios, ancillary]).reshape(4, 2)
        success = float(exact[:,1].sum())
        discount = float(np.exp(-rate*maturity))
        reference = float(discount*(p@payoff))
        assert np.allclose(exact.sum(axis=1), p, atol=1e-12)
        assert np.isclose(success, .1) and np.isclose(success*scale*discount, reference)
        print('Terminal / probability / payoff:', list(zip(terminal, p, payoff)))
        print('Implied spot:', discount*(p@terminal))
        print('Ancillary success probability:', success)
        print('Circuit:', circuit, sep='\n')
        counts = measured_counts(circuit, [ancillary])
        estimate = float(counts[1]/SHOTS)
        z = 1.959963984540054
        center = (estimate+z*z/(2*SHOTS))/(1+z*z/SHOTS)
        half = z*np.sqrt(estimate*(1-estimate)/SHOTS+z*z/(4*SHOTS**2))/(1+z*z/SHOTS)
        interval = [(center-half)*scale*discount, (center+half)*scale*discount]
        compare_plot(['ancilla=0', 'ancilla=1'], [1-success, success], counts/SHOTS,
                     'Payoff-encoded ancillary measurement')
        evidence = {'qubits': 3, 'shots': SHOTS, 'counts': counts.tolist(),
                    'exact_price': reference, 'sampled_price': estimate*scale*discount,
                    'price_95pct_wilson_interval': interval,
                    'implied_spot': float(discount*(p@terminal)),
                    'ancilla_ideal_probability': success,
                    'validation': 'Scenario marginal and discounted expected payoff checked'}
        """),
    },
    {
        "file": "cirq_constraints", "direction": "financial-constraints",
        "title": "预算与持仓约束", "en": "Budget & position constraints",
        "method": "QUBO / QAOA", "sources": ["qaoa", "diagonal"],
        "summary": "离散预算、持仓数及行业互斥转为二次罚项，测量后逐项检查。",
        "principle": r"""
        收益单位为 $u=(9,7,5)$，资金成本 $b=(4,3,2)$，要求预算恰为 6、持仓恰为 2，
        且资产 0 与 1 不能同时持有。使用
        $C(x)=-u^Tx+4(b^Tx-6)^2+3(\sum_i x_i-2)^2+5x_0x_1$。
        这仍然是二次二元模型。对本例枚举验证：唯一可行解为 101，原收益为 14。
        单层 QAOA 的低期望成本并不等同于每次抽样都可行，因此展示全部位串、可行率和最优命中率。
        """,
        "steps": "定义预算与行业规则 → 写出 QUBO 罚项 → 穷举检验本例罚系数 → 本地训练 QAOA → 4096 shots → 原始预算 / 持仓 / 互斥三项检查。",
        "boundary": "官方 QAOA 是通用方法；此金融约束模型为我们的扩展。罚系数只对这个已验证的小输入成立；不是任意约束求解器，不包含多期交易、整数松弛或商业优化器。",
        "code": """
        utility, budget_cost = np.array([9.,7.,5.]), np.array([4,3,2])
        def objective(x):
            return -utility@x+4*(budget_cost@x-6)**2+3*(x.sum()-2)**2+5*x[0]*x[1]
        def feasible(x):
            return bool(budget_cost@x == 6 and x.sum() == 2 and x[0]*x[1] == 0)
        """,
        "kernel": QAOA + textwrap.dedent(r"""
        assert [f'{i:03b}' for i in np.flatnonzero(allowed)] == ['101']
        evidence['sampled_checks'] = [
            {'state': f'{i:03b}', 'count': int(counts[i]),
             'budget_equals_6': bool(budget_cost@x == 6),
             'holdings_equal_2': bool(x.sum() == 2), 'sector_exclusion': bool(x[0]*x[1] == 0)}
            for i, x in enumerate(states) if counts[i] > 0]
        """),
    },
    {
        "file": "cirq_market_walk", "direction": "market-models",
        "title": "量子游走与波动情景", "en": "Quantum walk & volatility scenarios",
        "method": "Coined quantum walk", "sources": ["walk", "simulation"],
        "summary": "五步量子游走与经典二项分布对照，观察干涉改变情景权重。",
        "principle": r"""
        4 个位置量子比特编码 16 个点，另加 1 个硬币位。初始位置为 8，
        硬币态 $(|0\rangle+i|1\rangle)/\sqrt{2}$。每步先施加 H，再按硬币值向左或向右移动。
        步算符 $U=S(H\otimes I)$；移位使用循环置换，但 5 步只到位置 3 至 13，未跨边界。
        经典对照为相同起点和步数、独立公平抛币的二项分布。
        可将位移乘 1% 作为**示意情景**，但量子干涉概率不是已经校准的市场价格过程。
        """,
        "steps": "设定起点与平衡硬币 → 五次硬币 / 受控移位 → 每步位置边缘概率 → 独立振幅递推校验 → 4096 次最终采样 → 对照经典游走。",
        "boundary": "Google 官方确有 Quantum walk 教程，并提及随机游走与金融的联系；官方例子没有完成金融定价或波动率模型。此处为我们独立编写的小规模情景扩展，不是行情预测、相关性估计或训练完成的金融 AI。",
        "code": """
        from math import comb
        coin, *position = cirq.LineQubit.range(5)
        order = [coin, *position]
        size, start, steps = 16, 8, 5
        """,
        "kernel": """
        # A transparent finite permutation, not a market-fitted transition model.
        plus = np.roll(np.eye(size), 1, axis=0)
        minus = plus.T
        circuit = cirq.Circuit(cirq.X(position[0]), cirq.H(coin), cirq.S(coin))
        recurrence = np.zeros((2, size), dtype=complex)
        recurrence[:,start] = [1/np.sqrt(2), 1j/np.sqrt(2)]
        snapshots = []
        for _ in range(steps):
            circuit.append(cirq.H(coin))
            circuit.append(cirq.MatrixGate(plus).on(*position)
                           .controlled_by(coin, control_values=[1]))
            circuit.append(cirq.MatrixGate(minus).on(*position)
                           .controlled_by(coin, control_values=[0]))
            state = simulator.simulate(circuit, qubit_order=order).final_state_vector.reshape(2,size)
            marginal = np.abs(state[0])**2 + np.abs(state[1])**2
            mixed = np.array([recurrence[0]+recurrence[1], recurrence[0]-recurrence[1]])/np.sqrt(2)
            recurrence = np.array([np.roll(mixed[0], -1), np.roll(mixed[1], 1)])
            assert np.allclose(state, recurrence, atol=1e-12)
            snapshots.append(marginal.tolist())
        exact = np.array(snapshots[-1])
        classical = np.zeros(size)
        for right in range(steps+1):
            classical[start+2*right-steps] = comb(steps,right)/2**steps
        counts = measured_counts(circuit, position)
        assert np.isclose(exact.sum(), 1) and np.isclose(classical.sum(), 1)
        assert not np.allclose(exact, classical)
        assert np.isclose(exact @ (np.arange(size)-start), 0, atol=1e-12)
        plt.figure(figsize=(8,3.4))
        plt.imshow(snapshots, aspect='auto', cmap='viridis', interpolation='nearest')
        plt.yticks(range(steps), range(1,steps+1)); plt.xlabel('Position'); plt.ylabel('Step')
        plt.title('Intermediate quantum-walk position probabilities'); plt.colorbar(label='Probability')
        plt.tight_layout(); plt.show()
        compare_plot([str(i-start) for i in range(size)], exact, counts/SHOTS,
                     'Final walk: position displacement, not observed market returns')
        plt.figure(figsize=(8,3))
        plt.plot(np.arange(size)-start, classical, 'o-', label='Classical random walk', color='#bc4164')
        plt.plot(np.arange(size)-start, exact, 's-', label='Coherent quantum walk', color='#137f76')
        plt.xlabel('Displacement'); plt.ylabel('Probability'); plt.legend(); plt.tight_layout(); plt.show()
        displacement = np.arange(size)-start
        evidence = {'qubits': 5, 'shots': SHOTS, 'counts': counts.tolist(), 'steps': steps,
                    'ideal_probability': exact.tolist(), 'classical_probability': classical.tolist(),
                    'intermediate_probability': snapshots,
                    'quantum_variance': float(exact @ displacement**2),
                    'classical_variance': float(classical @ displacement**2),
                    'validation': 'All five Cirq step states checked against independent amplitude recurrence'}
        """,
    },
]

STYLE = """<style>
*{letter-spacing:0}body{color:#202a2a}.jp-Notebook{max-width:1100px;margin:auto}
.jp-RenderedHTMLCommon{line-height:1.8}h1{font-size:28px!important}h2{font-size:22px!important}
.jp-InputArea-editor,.jp-OutputArea-output{max-width:100%;overflow-x:auto}
.jp-RenderedImage img{max-width:100%;height:auto}.jp-RenderedText pre{white-space:pre-wrap;overflow-wrap:anywhere}
@media(max-width:600px){h1{font-size:23px!important}.jp-Notebook{padding:10px!important}.jp-Cell{padding:4px!important}}
</style>"""


def source_cell(source):
    return nbformat.v4.new_code_cell(textwrap.dedent(source).strip())


def build_notebook(case):
    path = OUTPUT / (case["file"] + ".ipynb")
    notebook = nbformat.read(path, as_version=4) if path.exists() else nbformat.v4.new_notebook()
    notebook.metadata.title = f"Cirq · {case['title']} / {case['en']}"
    notebook.metadata.kernelspec = {"name": "python3", "display_name": "Python 3", "language": "python"}
    notebook.metadata["quantumbridge"] = {"domain": "finance", "direction": case["direction"], "execution_mode": "local-cirq-simulation", "hardware_jobs": 0}
    sources = "\n".join(f"- [{SOURCES[key][0]}]({SOURCES[key][1]})" for key in case["sources"])
    notebook.cells = [
        nbformat.v4.new_markdown_cell(f"# Cirq · {case['title']}\n\n{case['en']}\n\n[金融 Cirq 总目录](cirq_finance.html) · **QuantumBridge 原创金融教学扩展 / Cirq 本地仿真**\n\n{case['summary']}\n\n合成模型；不是投资建议，不是完整行业支持，也不证明 QuantumBridge 原生替代 Cirq。"),
        nbformat.v4.new_markdown_cell("## 1. 官方方法与归属 / Sources\n\n" + case["boundary"] + "\n\n" + sources),
        nbformat.v4.new_markdown_cell("## 2. 原理与步骤 / Model & workflow\n\n" + textwrap.dedent(case["principle"]).strip() + "\n\n" + case["steps"]),
        nbformat.v4.new_markdown_cell("## 3. 运行环境 / Local environment\n\n需要已安装 `cirq`、`numpy`、`matplotlib` 与 Jupyter。代码不依赖本仓库私有模块，可在安装上述依赖的 Python 内核从上到下运行。没有自动安装、联网或密钥读取。"),
        source_cell(COMMON),
        nbformat.v4.new_markdown_cell("## 4. 输入与电路 / Inputs & circuit"),
        source_cell(case["code"]),
        nbformat.v4.new_markdown_cell("## 5. 中间结果与实际本地采样 / Intermediate & sampled results\n\n图中 Exact 为同一模型的精确分布；Cirq shots 为有限次模拟测量，不是真机回执。"),
        source_cell(textwrap.dedent(case["kernel"])),
        nbformat.v4.new_markdown_cell("## 6. 最终输出与边界 / Evidence & limitations\n\n" + case["boundary"] + "\n\n本次硬件任务为 0。不同 SDK 版本的随机抽样序列可能不同，解析断言仍应成立。"),
        source_cell("evidence.update({'backend': 'local cirq.Simulator', 'cirq_version': cirq.__version__, 'python': sys.version.split()[0], 'seed': SEED, 'hardware_jobs': 0})\nprint('EVIDENCE_JSON=' + json.dumps(evidence, ensure_ascii=False, allow_nan=False))"),
    ]
    NotebookClient(notebook, timeout=180, kernel_name="python3").execute(cwd=ROOT)
    nbformat.validate(notebook)
    records, images = [], []
    for cell in notebook.cells:
        for output in cell.get("outputs", []):
            if output.output_type == "error":
                raise RuntimeError(f"Failed notebook: {case['file']}")
            for line in output.get("text", "").splitlines():
                if line.startswith("EVIDENCE_JSON="):
                    records.append(json.loads(line.removeprefix("EVIDENCE_JSON=")))
            if "image/png" in output.get("data", {}):
                images.append(output.data["image/png"])
    assert len(records) == 1 and images
    evidence = records[0]
    assert evidence["shots"] == 4096 and sum(evidence["counts"]) == 4096
    assert evidence["hardware_jobs"] == 0
    nbformat.write(notebook, path)
    exported, _ = HTMLExporter(template_name="lab").from_notebook_node(notebook)
    exported = exported.replace("</head>", STYLE + "</head>")
    path.with_suffix(".html").write_text(exported, encoding="utf-8")
    print(f"Executed: {case['file']} | {evidence['qubits']} qubits | 4096 local shots", flush=True)
    return evidence, images[0]


def build_index(results):
    rows = []
    for case, (evidence, _) in zip(CASES, results):
        filename = html.escape(case["file"])
        rows.append(f'<tr><td><a href="{filename}.html">{html.escape(case["title"])}</a><small>{html.escape(case["en"])}</small></td><td>{html.escape(case["method"])}</td><td>{evidence["qubits"]} qubits / {evidence["shots"]} shots</td><td><a href="{filename}.ipynb" download>Notebook ↓</a></td></tr>')
    citations = "".join(f'<li><a href="{url}" target="_blank" rel="noopener noreferrer">{html.escape(title)}</a></li>' for title, url in SOURCES.values())
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>Cirq 量子金融 · QuantumBridge</title>
<style>*{{box-sizing:border-box;letter-spacing:0}}body{{margin:0;background:#fff;color:#202a2a;font:15px/1.75 system-ui,sans-serif}}main{{max-width:1080px;padding:30px 24px;margin:auto}}h1{{font-size:30px;margin:8px 0}}h2{{font-size:21px;margin:26px 0 12px}}a{{color:#096f67;text-underline-offset:3px;overflow-wrap:anywhere}}a:focus-visible{{outline:3px solid #127f76;outline-offset:4px}}.eyebrow{{font-size:12px;color:#536a65}}.lead{{font-size:17px;max-width:800px}}.status{{display:flex;flex-wrap:wrap;gap:12px 28px;padding:14px 0;border-block:1px solid #cdd8d4;margin:20px 0}}.status strong{{color:#096f67}}.boundary{{padding:14px 18px;border-left:3px solid #bc4164;background:#fbf5f7}}.scroll{{overflow-x:auto}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:14px 12px;border-bottom:1px solid #dbe3df;vertical-align:top}}th{{font-size:12px;background:#f0f5f3;color:#536a65}}td small{{display:block;font-size:12px;color:#61726c}}.method{{display:grid;grid-template-columns:1fr 1fr;gap:25px;align-items:start;border-bottom:1px solid #dbe3df;padding-bottom:24px}}.method img{{width:100%;height:auto}}figure{{margin:0}}figcaption{{font-size:12px;color:#61726c}}footer{{border-top:1px solid #dbe3df;margin-top:28px;padding-top:18px;color:#61726c;font-size:13px}}@media(max-width:650px){{main{{padding:22px 16px}}h1{{font-size:25px}}.method{{grid-template-columns:1fr}}th,td{{padding:12px 8px}}table{{min-width:590px}}}}</style></head><body><main>
<span class="eyebrow">QUANTUMBRIDGE / FINANCE / CIRQ</span><h1>Cirq 量子金融</h1><p class="lead">Google Cirq 方法与 QuantumBridge 金融教学扩展<br><small>Official methods, independently authored finance examples</small></p>
<div class="status"><span><strong>5</strong> 个对应金融方向</span><span><strong>Cirq {html.escape(results[0][0]['cirq_version'])}</strong> 本地仿真</span><span><strong>0</strong> 云端 / 真机任务</span></div>
<p class="boundary"><strong>归属与能力边界：</strong>在核查的官方 Cirq 实验目录中，未发现与 Qiskit Finance 对等的成套金融应用库。Google 提供 QAOA、量子游走和模拟 API；下列金融模型与案例由 QuantumBridge 自行编写，直接使用已安装的 Cirq。它们不是 Google 官方金融产品，也不代表 QuantumBridge 已原生替代 Cirq 或实现全量金融能力。</p>
<h2>金融方向与案例 / Finance cases</h2><div class="scroll"><table><thead><tr><th>对应分类 / Direction</th><th>方法 / Method</th><th>本次本地执行 / Local run</th><th>代码 / Code</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<h2>方法到业务模型 / From methods to models</h2><div class="method"><div><p><strong>QAOA → 组合与约束：</strong>官方教程解决通用 Ising 优化问题；我们补充金融目标、预算和可行性解码。案例保留所有抽样位串，不把命中一次最优解称为算法保证。</p><p><strong>模拟与测量 → 风险与定价：</strong>用合成概率情景演示 EL、VaR/ES 和收益编码。此批使用直接采样，没有运行 QAE，也不声称量子加速。</p><p><strong>量子游走 → 市场情景研究：</strong>官方教程介绍干涉与位置分布；示意波动情景不是校准后的市场预测。</p></div><figure><img src="data:image/png;base64,{results[0][1]}" alt="本次 Cirq 资产配置案例实际执行的 QAOA 期望成本搜索曲线"><figcaption>本次真实本地输出：p=1 QAOA 角度搜索，非硬件结果。</figcaption></figure></div>
<h2>官方来源 / Official sources</h2><ul>{citations}</ul><p>每个案例包含原理、输入、步骤、电路、图表、采样结果、独立数学断言及可下载的已执行 Notebook。全部数据为合成数据，不是投资建议。</p>
<p><a href="index.html">返回原有金融案例与真机报告</a></p><footer>QuantumBridge · 所属 相干(北京)科技有限公司 · Sources checked 2026-11-01<br>Local simulation is not hardware execution, production finance, or full parity.</footer></main></body></html>'''
    mobile = """<style>@media(max-width:650px){
    .scroll{overflow:visible}table{min-width:0}thead{display:none}
    tbody,tr{display:block}tr{display:grid;grid-template-columns:minmax(0,1fr) auto;
    padding:14px 0;border-bottom:1px solid #dbe3df;gap:6px 12px}
    td{border:0;padding:0;overflow-wrap:anywhere;min-width:0}
    td:first-child{grid-column:1/-1;font-size:16px}td:first-child>a{font-weight:600}
    td:nth-child(2){grid-column:1/-1;color:#536a65;font-size:13px}
    td:nth-child(3){font-size:13px}td:nth-child(4){text-align:right;font-size:13px}
    }</style>"""
    (OUTPUT / "cirq_finance.html").write_text(page.replace("</head>", mobile + "</head>"), encoding="utf-8")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = [build_notebook(case) for case in CASES]
    build_index(results)
    receipt = {"generated_at": datetime.now(timezone.utc).isoformat(), "hardware_jobs": 0,
               "sources": SOURCES, "cases": {case["direction"]: result[0] for case, result in zip(CASES, results)}}
    (OUTPUT / "cirq_finance_evidence.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
