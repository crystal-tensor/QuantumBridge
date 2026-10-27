# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Presentation of bounded application evidence; never submits cloud jobs."""

import html
import json

import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML, display


STYLE = """<style>
*{letter-spacing:0}body{color:#242b30} .jp-Notebook{max-width:1180px;margin:auto}
.jp-RenderedHTMLCommon{line-height:1.8}h1{font-size:28px!important}h2{font-size:22px!important}
.qb-scroll{max-width:100%;overflow-x:auto;margin:12px 0} .qb-scroll table{border-collapse:collapse;font-size:13px;white-space:nowrap}
.qb-scroll th,.qb-scroll td{padding:8px 12px;border-bottom:1px solid #d4dde1;text-align:left!important;max-width:540px}
.qb-scroll th{background:#eaf0f4} .qb-json{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px;line-height:1.6}
.jp-OutputArea-output{max-width:100%;overflow-x:auto}.jp-RenderedImage img{max-width:100%;height:auto}
@media(max-width:600px){.jp-Notebook{padding:10px!important}h1{font-size:23px!important}.jp-Cell{padding:4px!important}}
</style>"""


def show_json(value):
    display(
        HTML(
            '<pre class="qb-json">'
            + html.escape(json.dumps(value, ensure_ascii=False, indent=2))
            + "</pre>"
        )
    )


def show_table(rows):
    if not rows:
        return
    if not isinstance(rows[0], dict):
        show_json(rows)
        return
    columns = list(rows[0])

    def cell(value):
        if isinstance(value, float):
            return f"{value:.8g}"
        return (
            json.dumps(value, ensure_ascii=False)
            if isinstance(value, (list, dict))
            else str(value)
        )

    header = "".join(f"<th>{html.escape(key)}</th>" for key in columns)
    body = "".join(
        "<tr>"
        + "".join(f"<td>{html.escape(cell(row.get(key, '')))}</td>" for key in columns)
        + "</tr>"
        for row in rows
    )
    display(
        HTML(
            f'<div class="qb-scroll"><table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table></div>'
        )
    )


def intermediate_tables(case):
    for key, value in case.intermediate.items():
        display(HTML(f"<h3>{html.escape(key)}</h3>"))
        if isinstance(value, list) and value and isinstance(value[0], dict):
            show_table(value)
        else:
            show_json(value)


def plot_intermediate(case):
    plt.rcParams.update(
        {"font.size": 10, "axes.spines.top": False, "axes.spines.right": False}
    )
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), layout="constrained")
    left, right = axes
    data = case.intermediate
    if case.direction == "chemistry":
        rows = sorted(data["variational_trace"], key=lambda row: row["theta"])
        left.plot(
            [r["theta"] for r in rows],
            [r["energy_hartree"] for r in rows],
            color="#087e8b",
        )
        left.axhline(
            case.reference["exact_ground_energy_hartree"],
            color="#b34050",
            ls="--",
            label="Exact N=2",
        )
        left.set(
            xlabel="Excitation angle (rad)",
            ylabel="Energy (Hartree)",
            title="Variational search",
        )
        left.legend()
        rows = data["bond_scan"]
        for key, label in [
            ("rhf_hartree", "RHF"),
            ("exact_sector_hartree", "Exact N=2"),
        ]:
            right.plot(
                [r["distance_angstrom"] for r in rows],
                [r[key] for r in rows],
                marker="o",
                label=label,
            )
        right.set(
            xlabel="H-H distance (angstrom)",
            ylabel="Energy (Hartree)",
            title="Classical bond scan",
        )
        right.legend()
    elif case.direction == "materials":
        rows = data["interaction_sweep"]
        u = [r["U_over_t"] for r in rows]
        left.plot(u, [r["energy_N2"] for r in rows], "o-", label="E(N=2)")
        left.plot(
            u,
            [r["finite_cluster_charge_gap"] for r in rows],
            "s-",
            label="Finite charge gap",
        )
        left.set(
            xlabel="U / t",
            ylabel="Energy / t",
            title="Two-site cluster, not a band structure",
        )
        left.legend()
        right.plot(u, [r["double_occupation"] for r in rows], "o-", color="#087e8b")
        right.set(
            xlabel="U / t",
            ylabel="Double occupation",
            title="Classical exact-state prediction",
        )
    elif case.direction == "physics":
        for steps in (1, 4, 12):
            rows = [r for r in data["time_evolution"] if r["trotter_steps"] == steps]
            left.plot(
                [r["time"] for r in rows],
                [r["magnetization_z0"] for r in rows],
                label=f"{steps} steps",
            )
            right.semilogy(
                [r["time"] for r in rows[1:]],
                [max(r["infidelity"], 1e-16) for r in rows[1:]],
                label=f"{steps} steps",
            )
        left.plot(
            [r["time"] for r in rows],
            [r["exact_z0"] for r in rows],
            "k--",
            label="Exact",
        )
        left.set(xlabel="Time (hbar/J)", ylabel="<Z0>", title="Magnetization")
        left.legend()
        right.set(
            xlabel="Time (hbar/J)",
            ylabel="1 - fidelity",
            title="First-order Trotter error",
        )
        right.legend()
    elif case.optimization:
        rows = data["candidates"]
        left.bar(
            range(16),
            [r["penalized_cost"] for r in rows],
            color=["#087e8b" if r["feasible"] else "#b34050" for r in rows],
        )
        left.set(
            xlabel="Four-bit candidate (decimal)",
            ylabel="Penalized cost",
            title="All 16 candidates: teal = feasible",
        )
        if case.direction == "biomedicine":
            row = next(
                r for r in rows if r["bitstring"] in case.reference["best_bitstrings"]
            )
            points = np.asarray(row["coordinates"])
            right.plot(points[:, 0], points[:, 1], "o-", color="#087e8b", ms=13)
            for i, point in enumerate(points):
                right.annotate(
                    f"H{i}", point, xytext=(8, 8), textcoords="offset points"
                )
            right.plot(points[[0, -1], 0], points[[0, -1], 1], "--", color="#b34050")
            right.set(
                aspect="equal",
                title="One exact lattice optimum",
                xlabel="Lattice x",
                ylabel="Lattice y",
            )
        elif "pareto_front" in data:
            rows = data["pareto_front"]
            right.scatter(
                [r["emissions"] for r in rows],
                [r["profit"] for r in rows],
                color="#b34050",
            )
            right.set(
                xlabel="Emissions (model units)",
                ylabel="Profit (model units)",
                title="Enumerated Pareto frontier",
            )
        elif case.direction == "routing-scheduling":
            row = next(
                r for r in rows if r["bitstring"] in case.reference["best_bitstrings"]
            )
            for i, operation in enumerate(row["operations"]):
                right.barh(
                    operation["machine"],
                    1,
                    left=operation["start"],
                    color=["#087e8b", "#b34050"][i // 2],
                    alpha=0.8,
                )
                right.text(
                    operation["start"] + 0.5,
                    operation["machine"],
                    operation["name"],
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=9,
                )
            right.set(
                xlabel="Time slot", ylabel="Machine", title="Exact feasible schedule"
            )
        else:
            trace = data["optimizer_trace"]
            right.plot(
                [r["improvement"] for r in trace],
                [r["expected_penalized_cost"] for r in trace],
                "o-",
                color="#b34050",
            )
            right.set(
                xlabel="Accepted improvement",
                ylabel="Expected cost",
                title="Local ideal-state optimizer trace",
            )
    else:
        plt.close(fig)
        plot_security(case)
        return
    plt.show()
    plt.close(fig)


def plot_security(case):
    rows = case.intermediate.get("chart_rows", [])
    if not rows:
        return
    fig, ax = plt.subplots(figsize=(9, 3.6), layout="constrained")
    ax.bar(
        [str(r["label"]) for r in rows],
        [r["value"] for r in rows],
        color=["#087e8b", "#b34050", "#73609b"] * (len(rows) // 3 + 1),
    )
    ax.set(
        ylabel=case.intermediate.get("chart_units", "Model value"),
        title=case.intermediate.get("chart_title", "Local experimental evidence"),
    )
    plt.show()
    plt.close(fig)


def show_measurements(case, evidence):
    show_json(
        {
            "execution_mode": evidence["execution_mode"],
            "hardware_access": False,
            "new_cloud_tasks": 0,
        }
    )
    show_table(
        [
            {
                "experiment": name,
                "qubits": row["qubits"],
                "gates": row["gate_count"],
                "shots": row["shots"],
                "seed": row["seed"],
            }
            for name, row in evidence["experiments"].items()
        ]
    )
    show_table(
        [{"observable": name, **row} for name, row in evidence["estimates"].items()]
    )
    if evidence["experiments"]:
        name, row = next(iter(evidence["experiments"].items()))
        x = np.arange(len(row["probabilities"]))
        fig, ax = plt.subplots(figsize=(10, 3.5), layout="constrained")
        ax.bar(
            x - 0.2,
            row["ideal_probabilities"],
            width=0.4,
            label="Native ideal",
            color="#087e8b",
        )
        ax.bar(
            x + 0.2,
            row["probabilities"],
            width=0.4,
            label="Local sampled",
            color="#b34050",
        )
        ax.set(
            xlabel="q0-first bitstring",
            ylabel="Probability",
            title=f"{name}: local simulation, not hardware",
        )
        ax.set_xticks(x, [format(i, f"0{row['qubits']}b") for i in x], rotation=45)
        ax.legend()
        plt.show()
        plt.close(fig)
        show_table(
            [
                {"experiment": name, "counts": row["counts"]}
                for name, row in evidence["experiments"].items()
            ]
        )
    show_json({"reference": case.reference, "final": evidence["summary"]})
