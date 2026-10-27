# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Build and execute local application tutorials, with no hardware submission path."""

import argparse
import ast
import html
import inspect
import json
from pathlib import Path
import sys

import nbformat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


def domain_builders(domain):
    if domain == "science":
        from quantumbridge.applications import science

        return science, science.BUILDERS
    if domain == "industry":
        from quantumbridge.applications import industry

        return industry, industry.BUILDERS
    from quantumbridge.applications import security

    return security, security.BUILDERS


def main():
    from application_lessons import DOMAIN_NAMES, LESSONS

    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", choices=list(DOMAIN_NAMES), required=True)
    parser.add_argument(
        "--template",
        type=Path,
        default=ROOT / "tmp/jupyter-notebook/application-template.ipynb",
    )
    args = parser.parse_args()
    module, builders = domain_builders(args.domain)
    output = ROOT / "output/jupyter-notebook" / args.domain
    output.mkdir(parents=True, exist_ok=True)
    paths = []
    for index, (key, builder) in enumerate(builders.items(), 1):
        lesson = LESSONS[key]
        book = nbformat.from_dict(json.loads(args.template.read_text(encoding="utf-8")))
        book.metadata.update(
            title=lesson["title"],
            kernelspec={
                "name": "python3",
                "display_name": "Python 3",
                "language": "python",
            },
        )
        book.metadata["quantumbridge"] = {
            "domain": args.domain,
            "direction": key,
            "execution": "local_only",
            "new_cloud_tasks": 0,
        }
        imports = "\n".join(
            ast.unparse(node)
            for node in ast.parse(inspect.getsource(module)).body
            if isinstance(node, (ast.Import, ast.ImportFrom))
        )
        imports = imports.replace(
            "from .common", "from quantumbridge.applications.common"
        )
        prerequisites = {
            "materials": ["hubbard_hamiltonian"],
            "physics": ["dynamics_circuit"],
        }.get(key, [])
        prerequisites += getattr(module, "NOTEBOOK_HELPERS", {}).get(key, [])
        source = "\n\n".join(
            inspect.getsource(getattr(module, name))
            for name in prerequisites + [builder.__name__]
        )
        setup = """import os, sys, json
get_ipython().run_line_magic('matplotlib', 'inline')
from pathlib import Path
root = next((p for p in [Path(os.environ.get("QB_REPO_ROOT", ".")).resolve(), *Path.cwd().resolve().parents] if (p/"quantumbridge").is_dir() and (p/"scripts").is_dir()), None)
if root is None:
    raise RuntimeError("Run from the QuantumBridge checkout or set QB_REPO_ROOT.")
sys.path.insert(0, str(root)); sys.path.insert(0, str(root/"scripts"))
from IPython.display import display, HTML
from application_notebook_support import STYLE, show_json, intermediate_tables, plot_intermediate, show_measurements
from quantumbridge.applications.common import run_local_case
display(HTML(STYLE))
SHOTS, SEED = 1024, 20261023
print("Execution: LOCAL ONLY | cloud submissions: 0 | shots per circuit:", SHOTS)
"""
        steps = "\n".join(f"{n}. {step}" for n, step in enumerate(lesson["steps"], 1))
        sources = "\n".join(f"- [{title}]({url})" for title, url in lesson["sources"])
        cells = [
            nbformat.v4.new_markdown_cell(
                f"# {lesson['title']}\n\nQuantumBridge / {DOMAIN_NAMES[args.domain]} / 中文可执行案例\n\n**执行状态：仅本地运行；未提交夸父真机；新增云任务 0。**\n\n面向了解 Python 的读者：完成建模、检查中间结果、运行原生电路或明确标记的经典密码步骤，并与独立基线核对。\n\n**范围边界：** {lesson['boundary']}"
            ),
            nbformat.v4.new_markdown_cell(
                "## 1. 原理与计算对象\n\n"
                + lesson["principle"].replace(r"\(", "$").replace(r"\)", "$")
            ),
            nbformat.v4.new_markdown_cell("## 2. 实现步骤\n\n" + steps),
            nbformat.v4.new_markdown_cell(
                "## 3. 环境与可复现参数\n\n依赖本仓库、NumPy、Matplotlib、Jupyter；安全案例还使用已安装的 OpenSSL / cryptography。模型和电路不调用 Qiskit 或 PennyLane。Notebook 保留真实执行输出，Python 解释器版本会在下方打印。"
            ),
            nbformat.v4.new_code_cell(setup + "\nprint(sys.version)\n" + imports),
            nbformat.v4.new_markdown_cell(
                "## 4. 完整应用建模代码\n\n以下是本案例实际执行的应用函数，不是伪代码。底层电路、映射、演化与采样复用仓库原生接口；优化类的共享辅助函数也位于 `quantumbridge/applications/common.py`。"
            ),
            nbformat.v4.new_code_cell(source),
            nbformat.v4.new_code_cell(
                f"case = {builder.__name__}()\nshow_json(case.inputs)"
            ),
            nbformat.v4.new_markdown_cell(
                "## 5. 中间结果与效果\n\n下方完整列出模型候选、优化轨迹或物理中间量。图中的 exact / classical 是经典计算基线，不冒充量子实验。图表使用英文坐标避免本机中文字体缺失，解释与表格保留中文。"
            ),
            nbformat.v4.new_code_cell(
                "intermediate_tables(case)\nplot_intermediate(case)"
            ),
            nbformat.v4.new_markdown_cell(
                "## 6. 实际运行与最终效果\n\n模拟器使用固定种子逐次采样，counts 总数必须等于 shots。估计标准误由实际样本方差计算；近似 95% 区间可写作 estimate ± 1.96 × SE，但小样本及零计数需另用适当区间。本例不把这些区间当成硬件精度验收。"
            ),
            nbformat.v4.new_code_cell(
                "evidence = run_local_case(case, shots=SHOTS, seed=SEED)\nshow_measurements(case, evidence)"
            ),
            nbformat.v4.new_markdown_cell(
                "## 7. 可检查的电路输出\n\n导出全部业务电路的 OpenQASM 2，位串采用 q0-first。可导出不等于已通过夸父设备门集、耦合图、深度和精度验收；本批不会访问凭据、提交任务或消耗金融额度。纯经典案例没有伪造量子电路。"
            ),
            nbformat.v4.new_code_cell(
                "for name, result in evidence['experiments'].items():\n    print('\\n---', name, '---\\n'+result['openqasm2'])\nif not evidence['experiments']:\n    print('Classical cryptography / security workflow: no quantum circuit.')"
            ),
            nbformat.v4.new_markdown_cell(
                "## 8. 结果解释、复做与非目标\n\n"
                + lesson["interpret"]
                + "\n\n"
                + lesson["boundary"]
                + "\n\n练习：对已有电路将 shots 改为 2048，比较估计与标准误；如果是纯经典密码案例，比较密文/公钥大小和篡改检测结果。安全案例的私钥只在临时目录或内存中存在，不输出密钥。重新执行此 Notebook 仍然只运行本地代码。"
            ),
            nbformat.v4.new_code_cell(
                "repeat = run_local_case(case, shots=2048, seed=SEED+100)\nshow_json({'execution_mode':repeat['execution_mode'], 'estimates':repeat['estimates'], 'new_cloud_tasks':repeat['new_cloud_tasks']})\nassert all(sum(row['counts'].values()) == 2048 for row in repeat['experiments'].values())\nassert repeat['new_cloud_tasks'] == 0\nassert repeat['hardware_access'] is False"
            ),
            nbformat.v4.new_markdown_cell(
                "## 9. 参考与责任边界\n\n独立编写应用代码，未复制上游 SDK 实现或第三方教程代码；下列资料用于数学与接口背景。\n\n"
                + sources
                + "\n\n本案例不是生产支持证书，也不代表 Qiskit / PennyLane 全量替代已经完成。"
            ),
        ]
        # Persist inspectable numerical evidence without plotting objects or key material.
        cells.insert(
            -1,
            nbformat.v4.new_code_cell(
                f"artifact = {{'inputs':case.inputs, 'intermediate':case.intermediate, 'reference':case.reference, 'evidence':evidence}}\npath = root/'output/jupyter-notebook/{args.domain}/{index:02d}_{key}_evidence.json'\npath.parent.mkdir(parents=True, exist_ok=True)\npath.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding='utf-8')\nprint('Evidence:', path.name)"
            ),
        )
        book.cells = cells
        nbformat.validate(book)
        from nbclient import NotebookClient
        from traitlets.config import Config

        client = NotebookClient(
            book,
            timeout=600,
            kernel_name="python3",
            config=Config({"KernelManager": {"transport": "ipc"}}),
            resources={"metadata": {"path": str(ROOT)}},
        )
        client.km = client.create_kernel_manager()
        client.km.kernel_spec.argv[0] = sys.executable
        book = client.execute()
        path = output / f"{index:02d}_{key}.ipynb"
        nbformat.write(book, path)
        from nbconvert import HTMLExporter

        templates = Path(sys.base_prefix) / "share/jupyter/nbconvert/templates"
        body, _ = HTMLExporter(
            template_name="lab",
            extra_template_basedirs=[str(templates)],
            extra_template_paths=[str(templates)],
        ).from_notebook_node(book, resources={"metadata": {"name": lesson["title"]}})
        body = body.replace("</head>", '<link rel="icon" href="data:,"></head>', 1)
        path.with_suffix(".html").write_text(body, encoding="utf-8")
        paths.append((path, lesson))
        print("Executed and exported:", path.name, flush=True)
    rows = "".join(
        f'<tr><td>{n:02d}</td><td>{html.escape(lesson["title"])}</td><td><a href="{path.stem}.html">原理、代码与执行结果</a></td><td><a href="{path.name}" download>Notebook</a></td></tr>'
        for n, (path, lesson) in enumerate(paths, 1)
    )
    page = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>QuantumBridge · {DOMAIN_NAMES[args.domain]}</title><link rel="icon" href="data:,"><style>
    *{{box-sizing:border-box;letter-spacing:0}}body{{margin:0;color:#242b30;background:#f7f9fb;font:16px/1.8 system-ui,sans-serif}}header{{padding:20px 5%;background:#242b30;color:white}}main{{max-width:1120px;margin:auto;padding:28px 22px}}h1{{font-size:28px}}h2{{font-size:21px}}a{{color:#086d77}}.scroll{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;background:white}}td,th{{padding:14px;text-align:left;border-bottom:1px solid #d5dde3}}th{{background:#e9eff4}}@media(max-width:550px){{h1{{font-size:23px}}td,th{{padding:9px;font-size:14px}}main{{padding:18px 14px}}}}
    </style></head><body><header>QUANTUMBRIDGE / {args.domain.upper()}</header><main><h1>{DOMAIN_NAMES[args.domain]} · {len(paths)} 个本地可执行案例</h1><p>本批仅本地运行，未提交夸父真机，新增云任务 0。每个案例包含中文原理、实现步骤、运行代码、中间图表、最终结果和已执行 Notebook。</p><p>这些是有明确边界的小规模研究案例，不代表完整行业平台、量子优势或安全认证；金融批次原有真机证据与剩余额度保持不变。</p><div class="scroll"><table><thead><tr><th>编号</th><th>细分方向</th><th>案例</th><th>下载</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""
    (output / "index.html").write_text(page, encoding="utf-8")
    print("Published local directory:", output)


if __name__ == "__main__":
    main()
