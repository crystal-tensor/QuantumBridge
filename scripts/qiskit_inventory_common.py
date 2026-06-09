# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit, IBM, Aer, Nature, Finance, ML, Optimization, Experiments, Metal, or Addons was copied.
"""Shared public inventory writer for Qiskit ecosystem adapters."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
loaded = sys.modules.get("quantumbridge")
if loaded is not None and not str(getattr(loaded, "__file__", "")).startswith(str(REPO_ROOT)):
    for module_name in list(sys.modules):
        if module_name == "quantumbridge" or module_name.startswith("quantumbridge."):
            del sys.modules[module_name]

from quantumbridge.compat.qiskit_common import normalize_qiskit_inventory_record, summarize_inventory


def write_public_api_inventory(
    *,
    ecosystem: str,
    facade,
    adapters: Iterable,
    inventory_dir: str | Path = "docs/compat/inventory",
    matrix_dir: str | Path = "docs/compat/matrix",
) -> tuple[Path, Path, dict]:
    records = []
    for adapter in adapters:
        for record in adapter.list_public_api_inventory():
            records.append(normalize_qiskit_inventory_record(facade, adapter, record))

    summary = {
        "ecosystem": ecosystem,
        "upstream_package": facade.upstream_package,
        "upstream_version": facade.get_upstream_version(),
        "dependency_available": facade.dependency_available(),
        "advisory": facade.advisory,
        "offline_only": facade.offline_only,
        **summarize_inventory(records),
    }

    inventory_path = Path(inventory_dir) / f"{ecosystem}_public_api_inventory.json"
    matrix_path = Path(matrix_dir) / f"{ecosystem}_fusion_coverage_matrix.md"
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(
        json.dumps({"summary": summary, "records": records}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    matrix_path.write_text(_matrix_markdown(summary, records), encoding="utf-8")
    return inventory_path, matrix_path, summary


def _matrix_markdown(summary: dict, records: list[dict]) -> str:
    lines = [
        f"# {summary['ecosystem']} Fusion Coverage Matrix\n\n",
        "Generated from runtime public-name introspection. No upstream source, tests, comments, or documentation text is copied.\n\n",
        f"- Upstream package: {summary['upstream_package']}\n",
        f"- Upstream version: {summary['upstream_version'] or 'not installed'}\n",
        f"- Dependency available: {summary['dependency_available']}\n",
        f"- Advisory: {summary['advisory']}\n",
        f"- Offline only: {summary['offline_only']}\n",
        f"- Records: {summary['records']}\n",
        f"- Unsupported: {summary['unsupported']}\n\n",
        "| Module | Name | Type | Level | Supported | Advisory | Risk | Notes |\n",
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n",
    ]
    for row in records:
        lines.append(
            "| "
            + " | ".join(
                _cell(value)
                for value in (
                    row["module"],
                    row["name"],
                    row["object_type"],
                    row["quantumbridge_level"],
                    row["supported"],
                    row["advisory"],
                    row["risk"],
                    row["notes"],
                )
            )
            + " |\n"
        )
    return "".join(lines)


def _cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
