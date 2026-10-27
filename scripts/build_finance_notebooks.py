#!/usr/bin/env python3
# Copyright 2026 QuantumBridge Contributors. Licensed under Apache-2.0.
"""Build and optionally execute the five Chinese finance tutorial notebooks.

Normal execution is entirely local. Hardware execution requires explicit
QB_FINANCE_RUN_CLOUD=1 and credentials in the kernel environment. Notebook JSON,
HTML, plots and receipts never intentionally contain credentials.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import subprocess
import sys
import textwrap

import nbformat


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "jupyter-notebook" / "finance"
KEYS = ["allocation", "risk", "derivatives", "constraints", "correlation"]
TITLES = ["量化投资与资产配置", "风险计量", "衍生品定价与对冲", "金融约束优化", "相关性与市场波动"]
PRINCIPLES = [
    r"""
    ## 1. 原理：均值—方差组合、QUBO 与 QAOA

    四个合成资产各用一个比特 $x_i\in\{0,1\}$ 表示是否持有，固定持有两个资产。
    最小化 $f(x)=q x^T\Sigma x-\mu^T x$。这里是二元选择，不是连续权重优化，
    收益率和协方差统一采用年化量纲。协方差是对称正定的人工输入。

    将约束并入 $C(x)=f(x)+\lambda(\sum_i x_i-2)^2$，穷举16种组合仅用于小规模
    **经典正确性对照**，不把已知最优解制备成量子态。$x_i=(1-Z_i)/2$ 将成本变成
    $Z_i$ 和 $Z_iZ_j$；程序通过成本真值表的 Walsh 系数得到相同的 Ising 展开。
    一个成本层加一个混合层：
    $|\psi(\gamma,\beta)\rangle=e^{-i\beta\sum_i X_i}e^{-i\gamma C(Z)}|+\rangle^{\otimes4}$。
    $Z_iZ_j$ 项用 CX—RZ—CX 实现。经典本地网格搜索和细化选择角度，
    **只将最终电路提交真机**，本例不是完整的硬件闭环优化。

    实现步骤：输入模型 → 枚举并验证罚项 → 本地训练角度 → 编译 QASM → 测量 →
    检查可行性 → 在实际测得的可行候选中选成本最低者 → 与经典最优比较。
    还会显示可行概率和最优解概率，不能只展示恰好命中的一个解。
    """,
    r"""
    ## 1. 原理：损失分布、VaR、CVaR 与压力测试

    用三量子比特编码8种损失情景。假设分布来自一个已给定的合成物理概率模型，
    正常和压力分布各运行一次电路：$|\psi\rangle=\sum_j\sqrt{p_j}|j\rangle$。
    由前缀条件概率决定 RY 角度，用 Walsh 分解及 CX 实现条件旋转。
    输入全部概率的成本是 $O(2^n)$，不假设免费 QRAM。

    $EL=\sum_jp_jL_j$；$VaR_\alpha=\inf\{l:F_L(l)\ge\alpha\}$。
    离散分布在分位点有概率原子，所以不能简单对所有 $L\ge VaR$ 取条件平均。
    使用期望短缺定义：
    $ES_\alpha=VaR_\alpha+\frac{\sum_jp_j\max(L_j-VaR_\alpha,0)}{1-\alpha}$。
    它只取足以补满尾部的那部分 VaR 边界概率质量。

    实现步骤：定义损失情景与正常/压力概率 → 制备概率态 → 测量 counts → 得到经验 CDF →
    定位95%分位点 → 计算 EL/ES → 对照精确模型与压力情景。
    本实现是**直接量子采样**，没有运行 QAE，也不声称 QAE 的渐近加速。
    1024 shots 的5%尾部只有约51个观测，VaR 可能跳档；采样误差、模型误差和硬件误差必须分开。
    """,
    r"""
    ## 1. 原理：风险中性定价、Delta 与静态对冲

    一年期欧式期权采用三步二叉树。$u=e^{\sigma\sqrt{T/n}},d=1/u$，
    $p_Q=(e^{rT/n}-d)/(u-d)$；它是风险中性概率，不能直接用于实际收益预测。
    三比特记录上/下路径，$S_T=S_0u^kd^{n-k}$。独立步概率只需三个 RY 门。

    看涨期权 $C=e^{-rT}E_Q[(S_T-K)^+]$，看跌同理。
    共享同一组测量路径，计算现货上下各扰动1单位后的收益差：
    $\Delta\approx e^{-rT}E_Q[(g(S_0+h)-g(S_0-h))/(2h)]$。
    用样本方差估计价格标准误差，95%区间采用大样本正态近似，不包含硬件系统误差。

    对一份空头看涨期权，初始持有 $\Delta$ 股，现金为 $C-\Delta S_0$；
    到期损益 $\Pi=-g(S_T)+\Delta S_T+(C-\Delta S_0)e^{rT}$。
    与不对冲的 $Ce^{rT}-g(S_T)$ 比较情景损益和标准差。
    这是**静态 Delta 对冲**，不是逐日再平衡或无风险复制。离散树的精确价格与
    Black–Scholes 解析价格不同是模型离散误差，不是量子测量错误。

    实现步骤：设定期权参数 → 验证风险中性鞅关系 → 制备路径分布 → 测量 →
    计算价格/Delta/标准误差 → 建立现金与股票对冲头寸 → 展示每个路径的最终损益。
    """,
    r"""
    ## 1. 原理：资本、行业与持仓约束的 QUBO

    仍为四资产，但加入持仓数、行业和资本约束：
    $\sum_i x_i=2$，$x_0+x_1=1$，$2x_0+2x_1+x_2+x_3=3$。
    前两资产属于行业一，后两资产属于行业二。资本单位是人工离散单位，不是股价。
    现有持仓 $x^{old}=(1,0,1,0)$，每个变化的比特付0.03单位成本。
    二元情况下 $|x_i-x_i^{old}|$ 是线性的，因此总成本仍是二次函数：
    $C(x)=q x^T\Sigma x-\mu^Tx+0.03\sum_i|x_i-x_i^{old}|+
    \lambda[ (\sum_i x_i-2)^2+(x_0+x_1-1)^2+(2x_0+2x_1+x_2+x_3-3)^2 ]$。

    有些约束在这个小案例中冗余，保留它们用于展示完整可行性报告。
    罚系数过小会让违约解更便宜，过大会压缩原目标在有限深度 QAOA 中的分辨率。
    本例穷举16个状态验证罚项后的全局最小值确实可行，**这不是任意输入的罚系数保证**。

    实现步骤：原目标+换仓成本 → 建立线性等式 → 平方罚项转 QUBO → 本地 QAOA 训练 →
    夸父测量 → 对每个观测位串检查所有约束 → 输出最好可行解、最优差距、违约概率。
    本例没有实现任意混合整数、多周期或不等式通用求解器。
    """,
    r"""
    ## 1. 原理：带符号干涉相关性与历史波动率

    对8天合成收益序列，先中心化并归一化：
    $u=(a-\bar a)/\|a-\bar a\|$，$v=(b-\bar b)/\|b-\bar b\|$。
    Pearson 相关系数为 $\rho=u^Tv$。制备4比特态
    $|\Psi\rangle=(|0\rangle|u\rangle+|1\rangle|v\rangle)/\sqrt2$，
    再对首比特做 H 门，测得 $P(0)=(1+\rho)/2$，因此 $\rho=2P(0)-1$。
    这里保留实振幅的符号；普通 SWAP-test 得到 $|u^Tv|^2$，会丢失正负号，不能直接替代。

    同时对3比特均匀时间索引做一次测量，将 counts 作为历史收益的重采样权重。
    $\bar r=\sum_j\hat p_jr_j$，$\sigma_d=\sqrt{\sum_j\hat p_j(r_j-\bar r)^2}$，
    假设独立同分布且每年252交易日，$\sigma_{ann}=\sqrt{252}\sigma_d$。
    这是 ddof=0 的历史总体波动率，不是无偏样本估计，不是未来波动率预测。

    实现步骤：生成合成收益 → 中心化/归一化 → 对正、负相关各制备一次干涉态 →
    测量首比特 → 恢复相关系数与采样标准误差 → 测量时间索引 → 估计均值/波动率。
    使用16个真实振幅的经典数据加载，不宣称大数据加速或已训练金融 AI 模型。
    """,
]

DETAIL_CODE = [
    """
    mu = np.array(case.inputs['expected_returns'])
    sigma = np.array(case.inputs['covariance'])
    print('Covariance eigenvalues:', np.linalg.eigvalsh(sigma))
    assert np.linalg.eigvalsh(sigma).min() > 0
    rows = case.intermediate['candidates']
    display_table(rows, ['bitstring', 'objective', 'feasible', 'penalized_cost'])
    print('Exact feasible oracle:', case.reference)
    trace = case.intermediate['local_optimizer_trace']
    print('Local optimizer final angles:', trace[-1])
    plt.plot([row['expected_cost'] for row in trace], marker='.')
    plt.xlabel('Improving grid points + refinement steps'); plt.ylabel('Expected penalized cost')
    plt.title('Local QAOA training (no hardware calls)'); plt.grid(alpha=.2); plt.show()
    """,
    """
    display_table(case.intermediate['loss_table'], ['state', 'loss', 'base', 'stress'])
    print('Classical exact EL / VaR / ES:')
    pretty(case.reference)
    for name, probs in case.inputs['probabilities'].items():
        plt.step(case.inputs['losses'], np.cumsum(probs), where='post', label=name)
    plt.axhline(.95, color='black', linestyle='--', label='95% quantile')
    plt.xlabel('Loss'); plt.ylabel('Cumulative probability'); plt.legend(); plt.show()
    """,
    """
    paths = []
    for i, label in enumerate(labels(3)):
        paths.append({'path': label, 'Q_probability': case.inputs['probabilities'][i],
                      'terminal_S': case.intermediate['terminal_prices'][i],
                      'call_payoff': case.intermediate['call_payoff'][i],
                      'delta_payoff': case.intermediate['delta_payoff'][i]})
    display_table(paths, ['path', 'Q_probability', 'terminal_S', 'call_payoff', 'delta_payoff'])
    discounted_terminal_mean = np.exp(-case.inputs['rate']) * np.dot(
        case.inputs['probabilities'], case.intermediate['terminal_prices'])
    assert abs(discounted_terminal_mean - case.inputs['spot']) < 1e-10
    print('Risk-neutral martingale checked; exact references:'); pretty(case.reference)
    """,
    """
    rows = case.intermediate['candidates']
    display_table(rows, ['bitstring', 'objective', 'violations', 'feasible', 'penalized_cost'])
    assert case.reference['penalized_global_minimum_is_feasible']
    print('Prior holdings:', case.inputs['previous_selection'])
    print('Exact constrained optimum:', case.reference)
    trace = case.intermediate['local_optimizer_trace']
    plt.plot([row['expected_cost'] for row in trace], marker='.')
    plt.xlabel('Improving grid points + refinement steps'); plt.ylabel('Expected penalized cost')
    plt.title('Constraint-penalized local training'); plt.grid(alpha=.2); plt.show()
    """,
    """
    returns = np.array([case.inputs['asset_a_returns'], case.inputs['asset_b_returns'],
                        case.inputs['asset_c_returns']])
    print('Classical Pearson matrix:'); print(np.corrcoef(returns))
    for name, series in zip(['A', 'B: positive', 'C: negative'], returns):
        plt.plot(range(1, 9), series, marker='.', label=name)
    plt.xlabel('Synthetic trading day'); plt.ylabel('Daily return'); plt.legend(); plt.show()
    print('Centered normalized A:', case.intermediate['normalized_asset_a'])
    pretty(case.reference)
    """,
]

FINAL_CODE = [
    """
    print('Best sampled feasible holdings:', sampled['best_observed_feasible']['selection'])
    print('Observed optimum gap:', sampled['best_observed_gap'])
    print('Feasibility / optimum probabilities:', sampled['feasible_probability'], sampled['optimal_probability'])
    assert sampled['best_observed_gap'] >= -1e-12
    """,
    """
    for name, result in local_results.items():
        measured_cdf = np.cumsum(result['probabilities'])
        exact_cdf = np.cumsum(case.inputs['probabilities'][name])
        epsilon = np.sqrt(np.log(2 / .05) / (2 * result['shots']))
        plt.step(case.inputs['losses'], measured_cdf, where='post', label=name + ' sampled')
        plt.plot(case.inputs['losses'], exact_cdf, '.', label=name + ' exact')
        print(name, '95% DKW CDF epsilon under IID sampling:', round(epsilon, 4))
        print('VaR shift is possible near an atom:', case.reference[name]['VaR'], '->', sampled[name]['VaR'])
    plt.axhline(.95, color='black', linestyle='--'); plt.xlabel('Loss'); plt.ylabel('CDF'); plt.legend(); plt.show()
    """,
    """
    final = case.analyze(local_results)
    plt.plot(final['unhedged_terminal_pnl'], 'o-', label='Short call, no hedge')
    plt.plot(final['hedged_terminal_pnl'], 's-', label='Static delta hedge')
    plt.xlabel('Measured path index (000..111)'); plt.ylabel('Terminal P&L'); plt.legend(); plt.show()
    print('Unhedged / hedged P&L std:', final['unhedged_pnl_std'], final['hedged_pnl_std'])
    print('Price absolute sampling error:', abs(final['call_price'] - case.reference['call_price']))
    print('3-step model discretization error vs Black-Scholes:',
          case.reference['call_price'] - case.reference['black_scholes_call'])
    print('Finite-shot parity residual:', final['put_call_parity_residual'])
    """,
    """
    best = sampled['best_observed_feasible']
    print('Decoded feasible candidate:', best)
    if best is not None:
        assert all(value == 0 for value in best['violations'].values())
    print('Raw infeasible measurement probability:', 1 - sampled['feasible_probability'])
    print('Do not silently discard this probability when reporting solver performance.')
    """,
    """
    names = ['positive_correlation', 'negative_correlation']
    values = [sampled[name]['correlation'] for name in names]
    error = [1.96 * sampled[name]['sampling_standard_error'] for name in names]
    plt.errorbar([0, 1], values, yerr=error, fmt='o', label='1024-shot estimate + approximate 95% error')
    plt.scatter([0, 1], [case.reference[name] for name in names], marker='x', label='Classical exact')
    plt.xticks([0, 1], ['A vs B', 'A vs C']); plt.axhline(0, color='gray'); plt.ylim(-1.05, 1.05)
    plt.ylabel('Signed Pearson correlation'); plt.legend(); plt.show()
    print('Historical annual volatility:', sampled['annualized_volatility_252'])
    """,
]


def code(source):
    return nbformat.v4.new_code_cell(textwrap.dedent(source).strip())


def markdown(source):
    return nbformat.v4.new_markdown_cell(textwrap.dedent(source).strip())


def build(index, *, scaffolder):
    key, title = KEYS[index], TITLES[index]
    path = OUTPUT / f"{index + 1:02d}_{key}_quafu.ipynb"
    if not path.exists():
        subprocess.run([sys.executable, str(scaffolder), "--kind", "tutorial", "--title", title,
                        "--out", str(path)], check=True, capture_output=True, text=True)
    notebook = nbformat.from_dict(json.loads(path.read_text(encoding="utf-8")))
    notebook.nbformat_minor = 5
    notebook.metadata["title"] = f"QuantumBridge · {title} · 夸父云案例"
    notebook.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
    notebook.cells = [
        markdown(f"""# {index + 1:02d} · {title}：QuantumBridge × 夸父云

        面向会基础 Python、概率和量子门的读者。本笔记可从首格运行到末格，默认不访问网络、
        不读取密钥、不产生真机任务。目标是一个可核验的小规模端到端案例，不等于该金融行业全部能力。

        数据全部为明确给定的合成数据，不是投资建议，不用于真实交易或生产风险管理。
        步骤：原理 → 输入与经典参考 → 电路与中间结果 → 本地实际采样 → 云任务与结果 → 最终比较。
        """),
        code(f"""
        from pathlib import Path
        import json, os, sys
        import numpy as np
        import matplotlib.pyplot as plt
        from IPython.display import display, HTML
        ROOT = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'quantumbridge').is_dir()), None)
        if ROOT is None:
            raise RuntimeError('Run this notebook from inside the QuantumBridge repository')
        sys.path.insert(0, str(ROOT))
        from quantumbridge.finance import build_finance_cases, run_local, FinanceCloudSession
        from quantumbridge.finance.execution import circuit_artifact
        from quantumbridge.finance.kernels import labels
        from quantumbridge.devices import StatevectorDevice
        import html
        def pretty(value):
            print(json.dumps(value, ensure_ascii=False, indent=2))
        def display_table(rows, fields):
            table = '<table><thead><tr>' + ''.join('<th>' + html.escape(f) + '</th>' for f in fields) + '</tr></thead><tbody>'
            for row in rows:
                table += '<tr>' + ''.join('<td>' + html.escape(str(row[f])) + '</td>' for f in fields) + '</tr>'
            display(HTML(table + '</tbody></table>'))
        case = build_finance_cases()[{key!r}]
        if os.environ.get('QB_FINANCE_REPLAY_HARDWARE') == '1':
            from quantumbridge.finance.acceptance import restore_submitted_circuits
            case = restore_submitted_circuits(case, ROOT / 'output' / 'finance-hardware' / 'session.json')
            print('Using EXACT originally submitted QASM; strict plan/receipt hashes retained.')
        print('Case:', case.key, '| quantum circuits:', len(case.experiments))
        print('Result labels use q0-first ordering. Cloud ordering is calibrated separately.')
        """),
        markdown(PRINCIPLES[index]),
        markdown("## 2. 输入模型与精确对照\n先检查输入、量纲和约束，随后所有量子采样结果使用同一个模型比较。"),
        code("pretty(case.inputs)"),
        code(DETAIL_CODE[index]),
        markdown(r"""## 3. 中间效果：电路、门数、理想概率

        所有实际提交门限定为 H、RY、RX、RZ、CX。概率/带符号实振幅加载在本地生成门序列，
        不是在云上执行 Python/NumPy。下格展示将提交的完整 QASM、量子比特数、双比特门数以及
        本地理想概率。真实设备的编译映射和噪声可能改变深度与分布。
        """),
        code("""
        for name, circuit in case.experiments.items():
            artifact = circuit_artifact(circuit)
            print(name, '| qubits:', artifact['num_qubits'], '| gates:', artifact['gates'],
                  '| two-qubit gates:', artifact['two_qubit_gates'], '| SHA256:', artifact['sha256'])
            print(artifact['openqasm'])
            print('Ideal probabilities:', StatevectorDevice().probabilities(circuit))
        """),
        markdown("## 4. 中间效果：1024 shots 本地实际采样\n固定种子保证可重现。以下输出明确是本地模拟器，不是真机结果。"),
        code("""
        local_results = run_local(case, shots=1024, seed=20261023)
        for name, result in local_results.items():
            print(name, result['execution_mode'], '| measured shots:', result['shots'])
            print('Raw measured counts:', result['counts'])
            xs = np.arange(len(result['probabilities']))
            plt.bar(xs - .18, result['ideal_probabilities'], width=.36, label='Exact native simulation')
            plt.bar(xs + .18, result['probabilities'], width=.36, label='1024 local shots')
            plt.xticks(xs, labels(case.experiments[name].num_qubits), rotation=70)
            plt.xlabel('q0-first bitstring'); plt.ylabel('Probability'); plt.title(name); plt.legend(); plt.tight_layout(); plt.show()
        sampled = case.analyze(local_results)
        pretty(sampled)
        """),
        markdown("## 5. 最终效果与误差解释\n理想参考、有限采样和离散模型误差分别呈现。命中经典最优不等于获得量子优势。"),
        code(FINAL_CODE[index]),
        markdown("""## 5.1 统计边界与硬件验收状态

        优化案例另外区分可行率、可行条件下最优命中率、无条件最优命中率及条件平均目标值。
        风险案例使用保留离散分位点规则的多项分布 bootstrap，并用 DKW 范围检查 VaR 是否稳定。
        未观测尾部在经验 bootstrap 中仍然没有概率质量，因此这些区间不能认证未见的稀有风险。
        各状态概率给出 Bonferroni 调整的 Wilson 近似区间；TVD 仅作分布诊断。
        没有事先批准的业务容差，不能自行宣称硬件 PASS。本地结果的硬件状态始终为 NOT_EXECUTED。
        """),
        code("""
        from quantumbridge.finance.acceptance import analyze_case_evidence
        sampling_acceptance = analyze_case_evidence(case, local_results)
        print('Hardware acceptance:', sampling_acceptance['hardware_status'])
        for name, diagnostic in sampling_acceptance['experiment_diagnostics'].items():
            print(name, '| ideal-vs-local TVD:', diagnostic['total_variation_distance'])
            if 'optimization' in diagnostic:
                pretty({key: value for key, value in diagnostic['optimization'].items() if key != 'feasible_states'})
            if 'risk_uncertainty' in diagnostic:
                pretty(diagnostic['risk_uncertainty'])
        """),
        markdown("""## 6. 同一电路接入夸父真机

        本批已获 owner 授权的上限：总计20个任务（包括位序校准），每任务1024 shots，最多6量子比特，
        遇收费提示停止。实际五类共8个业务电路，加1个非对称位序校准，共9个任务、9216 shots。
        通过 `QB_FINANCE_RUN_CLOUD=1` 显式开启；有效密钥仅通过 `QUAFU_TOKEN` 或
        `QUAFU_API_TOKEN` 进入内核环境，**不要写在代码格中**。
        Python>=3.12 的云环境需要项目已有的 `quafu-cloud` 可选依赖。

        `QB_QUAFU_BACKEND` 可指定真实设备，默认 Dongling（不保证当前在线）；
        所有五份笔记共享 `output/finance-hardware/session.json` 任务账本。
        每个 task ID 在等待结果前落盘，超时后重跑只取回该任务，不自动重复提交。
        该账本不能被多个内核同时写入。一次完整批次应顺序执行这五份笔记。
        不删除账本来重试；服务端接受与本地落盘之间仍有崩溃窗口，应先核对任务页。

        校准制备 $|10\rangle$，从 counts 识别 q0-first/q0-last；优势频率不足80%时停止。
        硬件结果必须包含真实任务 ID、实际 shots、原始 counts、位序与电路 SHA256。
        没有最终 counts 时不能标为硬件验收通过，也不会拿本地结果填充。
        SDK没有账单报价接口；限制任务/shot 数不等于保证免费。
        """),
        code("""
        cloud_results = None
        if os.environ.get('QB_FINANCE_RUN_CLOUD') == '1':
            session = FinanceCloudSession.from_environment(
                os.environ.get('QB_QUAFU_BACKEND', 'Dongling'),
                journal=ROOT / 'output' / 'finance-hardware' / 'session.json',
                max_tasks=20, shots=1024, max_qubits=6)
            pretty(session.preflight(list(build_finance_cases().values())))
            cloud_results = session.run(case, timeout=300, poll_interval=2)
            assert all(result['hardware_access'] for result in cloud_results.values())
            pretty({name: {k: result[k] for k in ['task_id', 'backend', 'shots', 'raw_counts', 'provider_bit_order']}
                    for name, result in cloud_results.items()})
            print('REAL CLOUD FINANCIAL RESULTS:')
            pretty(case.analyze(cloud_results))
        elif os.environ.get('QB_FINANCE_REPLAY_HARDWARE') == '1':
            evidence_path = ROOT / 'output' / 'jupyter-notebook' / 'finance' / (case.key + '_hardware_evidence.json')
            existing = json.loads(evidence_path.read_text(encoding='utf-8'))
            cloud_results = existing['hardware_results']
            print('Previously retrieved real hardware counts; no new submission:')
            pretty(analyze_case_evidence(case, cloud_results))
        else:
            print('HARDWARE NOT EXECUTED: cloud opt-in disabled. All results above are LOCAL ONLY.')
        if cloud_results is not None:
            hardware_acceptance = analyze_case_evidence(case, cloud_results)
            print('Hardware execution COMPLETE; numerical acceptance:', hardware_acceptance['hardware_status'])
            for name, result in cloud_results.items():
                print('Actual task:', result['task_id'], '| backend:', result['backend'], '| shots:', result['shots'])
                print('Raw provider counts:', result['raw_counts'])
                print('Normalized q0-first counts:', result['counts'])
                xs = np.arange(len(result['probabilities']))
                ideal = local_results[name]['ideal_probabilities']
                plt.bar(xs - .18, ideal, width=.36, label='Same-circuit ideal')
                plt.bar(xs + .18, result['probabilities'], width=.36, label='Actual ' + result['backend'] + ' hardware')
                plt.xticks(xs, labels(case.experiments[name].num_qubits), rotation=70)
                plt.xlabel('q0-first bitstring'); plt.ylabel('Probability'); plt.title(name + ': real hardware')
                plt.legend(); plt.tight_layout(); plt.show()
        """),
        markdown("""## 7. 本案例的交付证据

        下格保存可复查的输入、参考、中间结果、模拟 counts 和分析结果。
        `hardware_status=not_executed` 不是通过认证；只在取得真实 counts 时写入硬件证据。
        云平台执行硬件电路，本地执行数据加载、优化和金融后处理。
        """),
        code("""
        evidence = {
            'case': case.key, 'title': case.title, 'inputs': case.inputs,
            'intermediate': case.intermediate, 'reference': case.reference,
            'local_results': local_results, 'local_analysis': case.analyze(local_results),
            'hardware_status': 'completed' if cloud_results is not None else 'not_executed',
            'hardware_results': cloud_results,
            'hardware_analysis': None if cloud_results is None else case.analyze(cloud_results),
            'acceptance': analyze_case_evidence(case, cloud_results),
            'scope': 'synthetic small research case; not full industry coverage or investment advice',
        }
        suffix = '_hardware_evidence.json' if cloud_results is not None else '_evidence.json'
        destination = ROOT / 'output' / 'jupyter-notebook' / 'finance' / (case.key + suffix)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
        print('Evidence:', destination.name, '| hardware:', evidence['hardware_status'])
        """),
        markdown(r"""## 8. 练习、边界和扩展

        练习：将本地采样从1024增加到4096 shots，保持模型和电路不变，比较误差。
        下面只运行模拟器，**不会增加云端shots或创建新任务**。
        解答思路：比较多个随机种子的误差分布，不能要求每个种子的误差都单调下降。
        采样标准误差一般随 $1/\sqrt N$ 缩小；量子硬件偏差不会由增加 shots 自动消失。

        常见陷阱：把纯 Python 预处理称为硬件能力、把本地 counts 称为真机、按最多出现的位串直接作业务决策、
        忽略负相关符号、混淆风险中性和真实概率、把1024 shots尾部结果当作精确VaR。
        后续可扩展更大模型、真实数据、读出误差缓解、硬件闭环与独立回测；这里没有宣称这些已实现。
        """),
        code("""
        more_shots = run_local(case, shots=4096, seed=20261023)
        print('LOCAL 4096-shot comparison (no cloud):')
        pretty(case.analyze(more_shots))
        """),
        markdown("""## 9. 数学与接口参考

        本项目独立实现，未拷贝上游 SDK 源码或教程代码。
        [Qiskit Finance：组合优化](https://qiskit-community.github.io/qiskit-finance/tutorials/01_portfolio_optimization.html)、
        [欧式看涨期权](https://qiskit-community.github.io/qiskit-finance/tutorials/03_european_call_option_pricing.html)、
        [信用风险](https://qiskit-community.github.io/qiskit-finance/tutorials/09_credit_risk_analysis.html)
        提供应用定义参考；本批采用直接采样，而不是复现其 QAE 算法。
        [Quantum Risk Analysis](https://arxiv.org/abs/1806.06893)、
        [Option Pricing using Quantum Computers](https://arxiv.org/abs/1905.02666) 是算法背景，
        论文中的加速结论不适用于本批直接采样实现。
        [QuarkStudio 电路提交接口](https://quarkstudio.readthedocs.io/en/latest/usage/code/transpiler/)
        用于 `quark.Task`、QASM 和 `repeat × 1024` 传输合同。
        """),
    ]
    nbformat.validate(notebook)
    nbformat.write(notebook, path)
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--scaffolder", type=Path,
                        default=Path.home() / ".codex/skills/jupyter-notebook/scripts/new_notebook.py")
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    paths = [build(i, scaffolder=args.scaffolder) for i in range(5)]
    for path in paths:
        notebook = nbformat.read(path, as_version=4)
        if args.execute:
            from nbclient import NotebookClient
            from traitlets.config import Config
            client = NotebookClient(notebook, timeout=600, kernel_name="python3",
                                    config=Config({"KernelManager": {"transport": "ipc"}}),
                                    resources={"metadata": {"path": str(ROOT)}})
            client.km = client.create_kernel_manager()
            client.km.kernel_spec.argv[0] = sys.executable
            notebook = client.execute()
            nbformat.write(notebook, path)
            print("Executed:", path.name, flush=True)
        if args.html:
            from nbconvert import HTMLExporter
            templates = Path(sys.base_prefix) / "share/jupyter/nbconvert/templates"
            body, _ = HTMLExporter(template_name="lab", extra_template_basedirs=[str(templates)],
                                   extra_template_paths=[str(templates)]).from_notebook_node(
                                       notebook, resources={"metadata": {"name": notebook.metadata["title"]}})
            body = body.replace("</head>", '<link rel="icon" href="data:,"></head>', 1)
            path.with_suffix(".html").write_text(body, encoding="utf-8")
    if args.html:
        rows = "".join(f'<tr><td>{i+1:02d}</td><td>{html.escape(title)}</td><td><a href="{path.stem}.html">阅读案例</a></td>'
                       f'<td><a href="{path.name}" download>Jupyter notebook</a></td></tr>'
                       for i, (title, path) in enumerate(zip(TITLES, paths)))
        status_rows = []
        for key, title in zip(KEYS, TITLES):
            hardware_path = OUTPUT / f"{key}_hardware_evidence.json"
            evidence_path = hardware_path if hardware_path.exists() else OUTPUT / f"{key}_evidence.json"
            evidence = json.loads(evidence_path.read_text(encoding="utf-8")) if evidence_path.exists() else {}
            status = "已取回真机结果 / 精度尚未通过验收" if evidence.get("hardware_status") == "completed" else "真机待验证"
            status_rows.append(f'<li>{html.escape(title)}：{status}</li>')
        page = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,">
        <title>QuantumBridge · 量子金融案例</title><style>
        *{{box-sizing:border-box;letter-spacing:0}}body{{margin:0;color:#202427;background:#f6f7f8;font:16px/1.65 system-ui,sans-serif}}
        header{{background:#202427;color:white;padding:20px 6%}}main{{max-width:1050px;margin:auto;padding:28px 22px}}
        h1{{font-size:28px;margin:0}}h2{{font-size:21px}}p{{max-width:850px}}a{{color:#086d77}}table{{width:100%;border-collapse:collapse;background:white}}
        td,th{{text-align:left;padding:14px;border-bottom:1px solid #d9dfe2}}th{{background:#eaf0f1}}.scroll{{overflow-x:auto}}
        @media(max-width:550px){{h1{{font-size:23px}}td,th{{padding:10px;font-size:14px}}main{{padding:20px 14px}}}}
        </style><header>QUANTUMBRIDGE / FINANCE</header><main><h1>量子金融 · 五类可执行案例</h1>
        <p>中文原理、实现步骤、完整电路、本地采样、中间图表、最终结果和夸父执行入口。</p>
        <p>这是一组小规模合成研究案例，不代表金融全行业覆盖、量子优势或投资建议。每份案例单独标明硬件状态。</p>
        <div class="scroll"><table><thead><tr><th>编号</th><th>分类</th><th>案例与输出</th><th>代码</th></tr></thead><tbody>{rows}</tbody></table></div>
        <h2>执行状态</h2><ul>{''.join(status_rows)}</ul><p>全批次8个业务电路加1个位序校准，计划9个任务、9216 shots，业务电路最多4量子比特。
        授权上限为20任务，每任务1024 shots，最多6量子比特。无硬件结果时不以模拟输出代替。</p>
        </main></html>'''
        (OUTPUT / "index.html").write_text(page, encoding="utf-8")
    print("Finance artifacts:", OUTPUT)


if __name__ == "__main__":
    main()
