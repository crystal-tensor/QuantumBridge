#!/usr/bin/env python3
# Copyright 2026 QuantumBridge Contributors. Licensed under Apache-2.0.
"""Chinese D2 notebook, offline replay only; never imports a hardware client."""

import json
from pathlib import Path
import subprocess
import sys

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from traitlets.config import Config

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "output/jupyter-notebook/finance/finance_quafu_d2_mapping_diagnosis.ipynb"


def main():
    subprocess.run([sys.executable, str(Path.home() / ".codex/skills/jupyter-notebook/scripts/new_notebook.py"),
                    "--kind", "experiment", "--title", "夸父金融 D2：历史布局与位序诊断", "--out", str(DEST), "--force"], check=True)
    book = nbformat.from_dict(json.loads(DEST.read_text(encoding="utf-8")))
    md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
    book.cells = [
        md("""# 夸父金融 D2：历史布局与位序诊断

本附件只读取已经完成的 13 项真实实验，不提交新任务、不使用密钥、不修改五类金融结果。
核心结论：**保留剩余 7 项额度，暂不提交默认映射的 one-hot。**
物理位集合、有序测量映射、服务端 counts 字符串排序是三个不同概念。
以下候选分数只是相对无噪声理想分布的诊断，不能将最佳拟合当成真实位序。
"""),
        code('''import json, hashlib
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
root = Path.cwd()
while not (root / "quantumbridge/finance").is_dir() and root != root.parent:
    root = root.parent
base = root / "output/finance-hardware/diagnostics/d2"
load = lambda name: json.loads((base / name).read_text())
integrity = load("d2_readonly_audit.json")
assert integrity["total_tasks"] == 13 and integrity["new_submissions"] == 0
assert all(hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
           for name, digest in integrity["file_hashes"].items())
print("13项实验及原始证据复核通过，无新云任务；剩余额度:", integrity["remaining_tasks"])
layout = load("physical_layout_matrix.json")
'''),
        md("""## 1. 真实物理布局矩阵

从已保存 compiled QASM 和 QLISP 重新解析，不把先前报告中的表格硬编码为事实。
层深采用每门单位时长的逻辑层数，不是脉冲时间，也不是设备保真度。
"""),
        code('''display(pd.DataFrame([{"experiment": key, "task": value["task_id"],
    "physical_set": sorted(value["native_compiled"]["active_physical_qubits"]),
    "ordered_c_to_physical": value["ordered_measurement_mapping"],
    "gates": value["gate_profile"]["unitary_operation_count"],
    "layer_depth": value["gate_profile"]["logical_layer_depth"],
    "created": value["fields"]["created"]["value"]} for key, value in layout.items()]))
'''),
        md("""## 2. 候选 counts 位序：分数不等于证明

对宽度 n 枚举所有 n! 种字符串解释，保留 identity、reverse 及按物理编号排序的候选标记。
计算规范化 counts、TVD、边缘偏差和 multinomial log-likelihood（省略共同组合常数）。
如果观测结果在理想分布中的概率为零，严格无噪声似然为零，log 为负无穷；JSON 中记为 None，
并显示 `positive_counts_at_zero_ideal_probability=True`，不添加事后伪计数。
全零、全一的候选似然完全相同。真实噪声未知，金融结果的最好拟合也不能证明位序。
"""),
        code('''hypotheses = load("count_order_hypotheses.json")
rows = []
for key, value in hypotheses.items():
    assert value["status"] == "AMBIGUOUS" and value["selected_permutation"] is None
    if key.startswith("diagnostic/"):
        assert len({item["noiseless_multinomial_log_likelihood_up_to_constant"] for item in value["candidates"]}) == 1
    for item in value["candidates"]:
        if item["aliases"]:
            rows.append({"experiment": key, "interpretation": ", ".join(item["aliases"]),
                         "TVD": item["TVD"], "log_likelihood": item["noiseless_multinomial_log_likelihood_up_to_constant"],
                         "ideal_zero_mass_conflict": item["positive_counts_at_zero_ideal_probability"],
                         "marginal_deviation": item["marginal_deviation"]})
display(pd.DataFrame(rows))
'''),
        md("""## 3. 历史业务与诊断配对的可比性

36 组配对同时检查物理集合、有序测量、门族、层深、任务时间、编译选项与校准 ID。
同布局的 Pricing／History 与 D1 3q 可以条件性比较，但时间间隔及缺失 calibration ID
意味着仍未证明误差可迁移。D1 4q 与历史 4q 物理集合不同，不能直接套用边缘错误率。
"""),
        code('''pairs = load("historical_task_pairing.json")
display(pd.DataFrame([{"pair": name, "set_matches": value["physical_set_matches"],
    "ordered_mapping_matches": value["ordered_measurement_mapping_matches"],
    "time_gap_seconds": value["finish_to_probe_creation_seconds"], "classification": value["classification"],
    "calibration_matches": value["calibration_id_available_and_equal"]} for name, value in pairs.items()]))
assert all(not value["error_model_transfer_proven"] for value in pairs.values())
'''),
        md("""## 4. 联合错误、独立模型偏差与零／一不对称

经验联合错误概率与两个边缘错误概率之积作比较，并显示 2000 次 multinomial bootstrap
的协方差区间。独立边缘乘积只是比较基线，不是物理读出模型。
bootstrap 只描述 IID 经验样本，不能分离制备与读出、恢复未观测事件或校正漂移。
"""),
        code('''joint = load("joint_error_patterns.json")
display(pd.DataFrame([{"probe": key, **pair} for key, value in joint.items() for pair in value["pairs"]]))
display(load("zero_one_asymmetry.json"))
fig, axes = plt.subplots(2, 2, figsize=(10, 6))
for ax, (key, value) in zip(axes.flat, joint.items()):
    histogram = value["metrics"]["number_of_bit_errors_histogram"]
    ax.bar(list(histogram), np.array(list(histogram.values())) / 1024, color="#197d86")
    ax.set(title=key.split("/")[1], xlabel="Hamming error count", ylabel="Frequency", ylim=(0, 1))
fig.tight_layout()
plt.show()
'''),
        md("""## 5. 最少实验的条件可辨识性与额度决策

单个 4q one-hot 在无噪声时也保留 3! = 6 种不可区分排列；两条非对称基态 0011／0101
可给四个位置提供不同的二位签名，条件性区分 24 种排列，只需 2 个任务。
但前提是各次任务使用同一个已验证物理映射、位序语义明确且信号足够；有噪声时不是确定证明。
当前固定物理布局和收费前编译预览能力未验证，因此下面所有计划 execute=False。
"""),
        code('''plans = load("candidate_experiment_plan.json")
display(pd.DataFrame([{"candidate": key, "patterns": value["patterns_q0_first"], "tasks": value["tasks"],
    "shots": value["total_shots"], "target_physical_set": value["target_physical_set"],
    "worst_remaining_permutations_noiseless": value["worst_indistinguishable_permutations"],
    "decision": value["decision"]} for key, value in plans.items()]))
assert all(not value["execute"] for value in plans.values())
display(load("mapping_identifiability.json"))
print("NO_NEW_SUBMISSION_RECOMMENDED；金融验收仍INCONCLUSIVE，13/20任务，保留7项。")
'''),
    ]
    book.metadata["title"] = "夸父金融 D2：历史布局与位序诊断"
    client = NotebookClient(book, timeout=120, kernel_name="python3", config=Config({"KernelManager": {"transport": "ipc"}}),
                            resources={"metadata": {"path": str(ROOT)}})
    client.km = client.create_kernel_manager()
    client.km.kernel_spec.argv[0] = sys.executable
    book = client.execute()
    nbformat.write(book, DEST)
    templates = Path(sys.base_prefix) / "share/jupyter/nbconvert/templates"
    body, _ = HTMLExporter(template_name="lab", extra_template_basedirs=[str(templates)], extra_template_paths=[str(templates)]).from_notebook_node(book)
    DEST.with_suffix(".html").write_text(body.replace("</head>", '<link rel="icon" href="data:,"></head>', 1), encoding="utf-8")
    print(json.dumps({"notebook": str(DEST), "executed_code_cells": 6, "new_tasks": 0}))


if __name__ == "__main__":
    main()
