#!/usr/bin/env python3
# Copyright 2026 QuantumBridge Contributors. Licensed under Apache-2.0.
"""Read-only Chinese D3 notebook, replaying existing contract evidence."""

import json
from pathlib import Path
import subprocess
import sys

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from traitlets.config import Config

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "output/jupyter-notebook/finance/finance_quafu_d3_client_contract.ipynb"


def main():
    subprocess.run([sys.executable, str(Path.home() / ".codex/skills/jupyter-notebook/scripts/new_notebook.py"),
                    "--kind", "experiment", "--title", "夸父金融 D3：客户端契约与位序溯源", "--out", str(DEST), "--force"], check=True)
    book = nbformat.from_dict(json.loads(DEST.read_text(encoding="utf-8")))
    md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
    book.cells = [
        md("""# 夸父金融 D3：客户端契约与位序溯源

本附件只读回放 13 项真实实验的已有证据；不读取密钥、不导入或创建 Task、不查询云、不提交电路。
当前是 13/20 项，保留 7 项；金融数值验收仍 INCONCLUSIVE。
本轮确认软件版本和项目侧转换链，不把某份文档的字段补写进旧任务响应。
"""),
        code('''import json, hashlib
from pathlib import Path
import pandas as pd
from IPython.display import display
root = Path.cwd()
while not (root / "quantumbridge/finance").is_dir() and root != root.parent:
    root = root.parent
base = root / "output/finance-hardware/diagnostics/d3"
load = lambda name: json.loads((base / name).read_text())
audit = load("d3_no_submit_audit.json")
assert audit["total_tasks"] == 13 and audit["new_submissions"] == 0
assert all(hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
           for name, digest in audit["file_hashes"].items())
print("全部原始证据散列未变，任务13/20，新增0，保留7。")
'''),
        md("""## 1. 当前安装的是什么

`quark` 命名空间同时出现于多个发行包的元数据中；以实际 Task 所在文件与发行包文件清单对应，
确认 `quark.quafu.Task` 来自 `quarkstudio 7.3.9`。这里只检查公开签名、帮助和安装元数据，
不读取上游实现或测试源码，不实例化需凭据的客户端。
另一个 `quafu-sdk` 发行包未安装，不能拿其 `Result.bit_order` 当旧服务响应的事实。
"""),
        code('''contract = load("installed_client_contract.json")
display(pd.DataFrame([{"distribution": name, **value} for name, value in contract["distributions"].items()]))
print("Python:", contract["python_executable"])
print("Actual Task:", contract["Task_module"], contract["Task_module_path"])
display(contract["Task_public_method_signatures"])
assert "repeat" in contract["Task_public_method_signatures"]["run"]
assert "compile" in contract["gateway_signatures"]["submit"]
assert not contract["Task_instantiated"]
display(contract["call_path"])
'''),
        md("""## 2. 能力矩阵：文档、签名和实际观测分开

旧 QuarkStudio 文档展示 `options.target_qubits`；这不证明本机 gateway 接受它，
更不证明 Dongling 一定保持指定物理集合或有序映射。
`compile=False` 仍属于提交执行的任务参数，不等于免费 compile-only 或 dry-run。
实际 13 份响应没有 bit_order、compiler version 或 calibration ID；不回填、不猜测。
"""),
        code('''display(pd.DataFrame([{"capability": key, **value} for key, value in load("public_api_capability_matrix.json").items()]))
fields = load("historical_response_field_matrix.json")
display(pd.DataFrame([{"experiment": key, "bit_order": value["bit_order"]["status"],
    "compiler": value["compiler"]["status"], "calibration_id": value["calibration_id"]["status"],
    "transpiled": value["transpiled"]["status"]} for key, value in fields.items()]))
assert all(value["bit_order"]["observed_value"] is None for value in fields.values())
'''),
        md("""## 3. Counts 逐层转换：哪里已经证明，哪里没有

保存的原始证据是 **Task.result 已解码的 Python 响应**，不是原始 HTTP 字节；
因此不能声称已证明服务端到 SDK 内部完全没有换序。项目 gateway 的 `_extract_counts` 不改变标签；
8 项业务结果由显式 q0-last 假设执行反转，所有转换可严格逆向恢复，shots 不丢失也不重复。
这个假设状态标成 **GATEWAY_ASSUMPTION_UNVERIFIED**，不是已知服务端端序。
原 2q 校准和 D1 四项不是金融解码输入，单独标成 NOT_USED_FOR_FINANCE_DECODING。
"""),
        code('''traces = load("raw_label_provenance.json")
display(pd.DataFrame([{"experiment": key, "width": value["label_width"], "shots": value["shots"],
    "client_decode": value["client_decoding_stage"]["status"],
    "gateway_changes_labels": value["project_extraction_changes_labels"],
    "financial_order": value["saved_finance_decoder_order"], "status": value["finance_decoder_status"],
    "reversible": value["project_transforms_exactly_invertible"]} for key, value in traces.items()]))
assert all(value["project_transforms_exactly_invertible"] for value in traces.values())
example = traces["derivatives/risk_neutral_paths"]
display(example["stages"])
display(example["hypotheses"])
'''),
        md("""## 4. 三个反例及禁止提交保护

文档里的假 bit_order 不能传播成历史字段；本地接受 target_qubits 后仍映射到另一集合时，
不能称为锁定布局；同一组 counts 的 identity／reverse／物理排序解释必须保留来源、可逆且不覆盖原始结果。
下面仅用本地字典复现，全部是假设性软件反例，不是真机任务。
"""),
        code('''from quantumbridge.finance.client_contract import response_field_matrix, layout_pinning_verdict, trace_count_labels
from quantumbridge.compat.quafu import QuafuCloudBackend
from quantumbridge.providers import JobError
fake_documentation = {"bit_order": "c0_rightmost"}
historical = {"count": {"001": 200, "100": 824}}
assert response_field_matrix(historical, documentation=fake_documentation)["bit_order"]["status"] == "ABSENT"
assert layout_pinning_verdict([3,4,10,11], [10,11,4,5])["status"] == "ERROR"
display(trace_count_labels(historical, 3, ordered_physical_mapping=[11,4,5])["hypotheses"])
class NeverSubmit:
    def submit(self, *args, **kwargs):
        raise AssertionError("不应触及提交网关")
backend = QuafuCloudBackend(transport=NeverSubmit(), read_only=True)
try:
    backend.run(object())
except JobError as error:
    print(str(error))
else:
    raise AssertionError("禁止提交保护没有生效")
'''),
        md("""## 5. 决策和供应商待确认问题

当前不申请新增真机任务。先确认 counts 字符串排序、Task.result 是否转换标签、
历史 compiled measurement 的语义、布局固定保证、零任务／零收费 compile-only 契约和历史 calibration ID。
这些问题尚未向供应商发送，不能把草案当成其回复。若未来能够验证目标布局，再形成具体 QASM 和最小预算交 owner 决定。
"""),
        code('''display(load("layout_pinning_capability.json"))
display(load("compile_only_capability.json"))
proposal = load("next_experiment_approval_proposal.json")
display(proposal)
assert proposal["execute"] is False and proposal["additional_tasks_requested_now"] == 0
print("NO_NEW_SUBMISSION_RECOMMENDED；原始数值不修正，金融精度仍未通过验收。")
'''),
        md("""## 资料来源

- [QuarkStudio Transpiler 文档](https://quarkstudio.readthedocs.io/en/latest/usage/code/transpiler/)：历史任务与 target_qubits 示例。
- [Quafu-SQC 使用说明](https://quafu-sqc.readthedocs.io/en/latest/)：任务查询和返回字典。
- [另一个 quafu-sdk 发行包自述](https://pypi.org/project/quafu-sdk/0.2.2/)：不同的结果对象契约，未安装、未用于历史证据回填。

本附件不包含资料页面的 token 示例，不复制第三方实现，不代表全 SDK 功能验收完成。
"""),
    ]
    book.metadata["title"] = "夸父金融 D3：客户端契约与位序溯源"
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
