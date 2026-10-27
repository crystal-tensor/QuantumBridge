#!/usr/bin/env python3
# Copyright 2026 QuantumBridge Contributors. Licensed under Apache-2.0.
"""Build a separately executed Chinese D1 evidence notebook; no cloud calls."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from traitlets.config import Config

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "output/jupyter-notebook/finance/06_hardware_diagnostics.ipynb"


def main():
    subprocess.run([sys.executable, str(Path.home() / ".codex/skills/jupyter-notebook/scripts/new_notebook.py"),
                    "--kind", "experiment", "--title", "夸父金融 D1：编译与制备／测量诊断", "--out", str(DEST), "--force"], check=True)
    book = nbformat.from_dict(json.loads(DEST.read_text(encoding="utf-8")))
    md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
    book.cells = [
        md("""# 夸父金融 D1：编译与制备／测量诊断

这是五类金融案例的**独立诊断附件**，不是第六个金融模型。所有图表读取已完成的真实任务收据。
重跑本 notebook **不会访问网络、读取密钥或提交任务**。原有 9 项金融实验不覆盖、不修正。

问题：金融电路已在 Dongling 执行，但为什么与理想结果偏差明显？先检查返回的编译电路，
再用最简单的 3／4 比特全零、全一态观测制备和测量的综合偏差。总额度已使用 **13/20**，保留 7 项。
不能把“任务 DONE”写成“金融精度通过”。"""),
        code('''import hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
root = Path.cwd()
while not (root / "quantumbridge/finance").is_dir() and root != root.parent:
    root = root.parent
base = root / "output/finance-hardware/diagnostics"
load = lambda name: json.loads((base / name).read_text())
integrity = load("original_evidence_integrity.json")
assert integrity["unchanged"]
assert all(hashlib.sha256((root / name).read_bytes()).hexdigest() == value
           for name, value in integrity["before"].items())
print("原始证据 SHA-256 复核通过，文件数:", len(integrity["before"]))
audits = load("compiled_circuit_manifest.json")
probes = load("diagnostic_compiled_manifest.json")
metrics = load("zero_one_metrics.json")
decisions = load("diagnosis_decisions.json")
assert decisions["total_tasks"] == 13 and decisions["remaining_tasks"] == 7
'''),
        md(r"""## 1. 编译前后：比较测量输出，不比较不同物理编号的裸态向量

将返回的稀疏物理寄存器压缩为实际活动量子位，再使用 QuantumBridge 原生执行器。
QASM2 与独立的安全 QLISP 字面量解析分别执行 U、CZ、测量；没有调用 Qiskit／PennyLane 执行器。
经典输出按 `c0,c1,...` 排列后计算总变差距离 $TVD=\frac12\sum_x|p(x)-q(x)|$。
这只验证零输入下理想分布，**不是**完整酉矩阵、脉冲时序或硬件校准的证明。
"""),
        code('''rows = []
for name, audit in audits.items():
    rows.append({"experiment": name, "task_id": audit["task_id"],
                 "compiled_TVD": audit["compiled_vs_submitted_tvd"],
                 "QLISP_TVD": audit["qlisp_vs_compiled_tvd"],
                 "c_to_physical": audit["native_compiled"]["physical_measurement_map"],
                 "physical_set": sorted(audit["native_compiled"]["active_physical_qubits"])})
display(pd.DataFrame(rows))
assert max(row["compiled_TVD"] for row in rows) < 1e-8
assert all(row["QLISP_TVD"] == 0 for row in rows)
print("原始任务的编译电路理想分布与提交电路几乎相同，不能解释已观察到的巨大真机偏差。")
'''),
        md("""## 2. 中间证据：实际 QASM、任务 ID、编译选项与缺失字段

全零态只测量，不加制备门；全一态对每位施加 X 后测量。每项 1024 shots。
下方电路来自持久收据，不重新生成替代原始证据。
`compile=True` 及返回 QASM 可读，但编译器版本、校准 ID、raw counts 字符串位序未提供；不能猜测。
"""),
        code('''ledger = load("diagnostic_task_ledger.json")
for key, saved in ledger["jobs"].items():
    print(key, saved["job"]["job_id"], saved["job"]["status"], "shots=", saved["job"]["shots"])
    print(saved["artifact"]["openqasm"])
    print("SHA-256:", saved["artifact"]["sha256"])
    assert saved["job"]["shots"] == 1024 and saved["job"]["status"] == "DONE"
    assert sum(saved["raw_counts"].values()) == 1024
display(pd.DataFrame([{ "probe": key, "physical_map": value["native_compiled"]["physical_measurement_map"],
                       "compiled_TVD": value["compiled_vs_submitted_tvd"],
                       "calibration_id": value["fields"]["calibration_id"]["status"]}
                      for key, value in probes.items()]))
'''),
        md("""## 3. 最终观测：目标态命中率与 Wilson 95% 区间

目标全零／全一态是确定性的，任何其他结果都是相对目标的表观错误。
Wilson 区间描述假设独立同分布时的抽样不确定性，不覆盖漂移和系统性硬件误差。
全一态还包含 X 制备误差，不能把下表称作“纯读出保真度”。
"""),
        code('''table = pd.DataFrame([{"probe": key, "task_id": value["task_id"], "shots": value["shots"],
                       "success": value["success_probability"], "Wilson95": value["success_wilson_95"],
                       "multi_bit_error": value["multiple_bit_error_probability"]}
                      for key, value in metrics.items()])
display(table)
names = [key.split("/")[1] for key in metrics]
values = np.array([value["success_probability"] for value in metrics.values()])
bounds = np.array([value["success_wilson_95"] for value in metrics.values()])
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(names, values, color=["#197d86", "#b44462", "#197d86", "#b44462"])
ax.errorbar(names, values, yerr=[values - bounds[:, 0], bounds[:, 1] - values], fmt="none", color="#202427", capsize=5)
ax.axhline(1, color="#6d7477", linestyle=":")
ax.set(ylim=(0, 1.05), ylabel="Target-state frequency", title="Dongling: preparation + measurement diagnostics (1024 shots each)")
fig.tight_layout()
plt.show()
'''),
        md("""## 4. 原始分布、逐位置错误与相关错误

由于 raw counts 字符串的位序尚未独立确认，这里使用**字符串从左到右的位置**，不伪称 c0 或某一物理位。
两位同时错误的经验协方差为 $E[e_i e_j]-E[e_i]E[e_j]$；不能先假设误差独立，再反推出所谓真实读出矩阵。
"""),
        code('''fig, axes = plt.subplots(2, 2, figsize=(11, 6))
for ax, (key, metric) in zip(axes.flat, metrics.items()):
    counts = load("zero_one_raw_counts/" + metric["task_id"] + ".json")
    labels = [format(i, "0" + str(len(metric["prepared"])) + "b") for i in range(2**len(metric["prepared"]))]
    ax.bar(labels, [counts.get(label, 0) for label in labels], color="#197d86")
    ax.set_title(key.split("/")[1])
    ax.set_ylabel("Raw counts")
    ax.tick_params(axis="x", rotation=90)
fig.tight_layout()
plt.show()
display(pd.DataFrame([{ "probe": key, **row } for key, value in metrics.items()
                      for row in value["marginal_errors_by_raw_label_position"]]))
display(pd.DataFrame([{ "probe": key, **row } for key, value in metrics.items() for row in value["pair_errors"]]))
'''),
        md(r"""## 5. 为什么不自动做 one-hot 或误差缓解？

全零、全一在所有位排列下不变，因此它们对 identity／reverse 的匹配得分完全相同。
新 4 比特诊断的物理集合是 `{4,5,10,11}`，原 4 比特金融电路用 `{3,4,10,11}`；
新 3 比特诊断用 `{4,5,11}`，风险电路用 `{3,4,10}`。宽度相同不是同一组校准。

只有两个准备态，不能恢复完整 $2^n\times2^n$ 混淆矩阵；制备误差、测量误差和漂移也没有分离。
本附件不反演矩阵、不修改原始金融结果、不选择事后容差、不宣称硬件或金融精度通过。
"""),
        code('''for key, metric in metrics.items():
    target = metric["prepared"]
    counts = load("zero_one_raw_counts/" + metric["task_id"] + ".json")
    scores = {"identity": counts.get(target, 0), "reverse": counts.get(target[::-1], 0)}
    assert scores["identity"] == scores["reverse"]
    print(key, scores, "AMBIGUOUS")
display(load("mapping_hypotheses.json"))
display(decisions)
print("结论：云执行完成；金融数值验收仍 INCONCLUSIVE；未提交 one-hot，剩余7项保留。")
'''),
        md("""## 6. 下一步与复现边界

先离线比较原业务电路的具体物理布局、深度和差异，对需要与上游核查的编译器版本、校准 ID、
物理指定能力及 counts 位序列清单。只有明确实验能回答什么、如何匹配目标布局，才考虑动用剩余额度。

本 notebook 与五份金融 notebook 是可复现实验，不是全金融产品，也不代表 Qiskit／PennyLane 全函数库已完成。
原始证据位于 `output/finance-hardware/`；新增独立证据位于 `diagnostics/`。
"""),
    ]
    book.metadata["title"] = "夸父金融 D1：真实编译与制备／测量诊断"
    nbformat.write(book, DEST)
    client = NotebookClient(book, timeout=120, kernel_name="python3",
                            config=Config({"KernelManager": {"transport": "ipc"}}),
                            resources={"metadata": {"path": str(ROOT)}})
    client.km = client.create_kernel_manager()
    client.km.kernel_spec.argv[0] = sys.executable
    book = client.execute()
    nbformat.write(book, DEST)
    templates = Path(sys.base_prefix) / "share/jupyter/nbconvert/templates"
    body, _ = HTMLExporter(template_name="lab", extra_template_basedirs=[str(templates)],
                           extra_template_paths=[str(templates)]).from_notebook_node(book)
    DEST.with_suffix(".html").write_text(body.replace("</head>", '<link rel="icon" href="data:,"></head>', 1), encoding="utf-8")
    print(json.dumps({"notebook": str(DEST), "executed_code_cells": sum(cell.cell_type == "code" for cell in book.cells),
                      "errors": sum(output.output_type == "error" for cell in book.cells if cell.cell_type == "code" for output in cell.outputs),
                      "new_tasks": 0}))


if __name__ == "__main__":
    main()
