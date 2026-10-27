# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Check executed application notebooks and literal local evidence, without reruns."""

import json
import math
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def validate():
    notebooks, cells, plots, experiments = 0, 0, 0, 0
    for domain, expected in {"science": 4, "industry": 5, "security": 5}.items():
        directory = ROOT / "output/jupyter-notebook" / domain
        paths = sorted(directory.glob("*.ipynb"))
        assert len(paths) == expected, (domain, len(paths))
        assert (directory / "index.html").exists()
        for path in paths:
            book = json.loads(path.read_text(encoding="utf-8"))
            metadata = book["metadata"]["quantumbridge"]
            assert metadata["domain"] == domain
            assert (
                metadata["execution"] == "local_only"
                and metadata["new_cloud_tasks"] == 0
            )
            code = [cell for cell in book["cells"] if cell["cell_type"] == "code"]
            assert all(type(cell["execution_count"]) is int for cell in code), path
            assert not any(
                out["output_type"] == "error"
                for cell in code
                for out in cell.get("outputs", [])
            ), path
            images = sum(
                "image/png" in out.get("data", {})
                for cell in code
                for out in cell.get("outputs", [])
            )
            assert images >= 1, path
            exported = path.with_suffix(".html").read_text(encoding="utf-8")
            assert "data:image/png;base64," in exported
            assert not re.search(
                r"-----BEGIN (?:RSA |EC |ENCRYPTED )?PRIVATE KEY-----", exported
            )
            artifact = json.loads(
                path.with_name(path.stem + "_evidence.json").read_text(encoding="utf-8")
            )
            evidence = artifact["evidence"]
            assert (
                evidence["new_cloud_tasks"] == 0
                and evidence["hardware_access"] is False
            )
            for sample in evidence["experiments"].values():
                assert sample["shots"] == 1024
                assert sum(sample["counts"].values()) == sample["shots"]
                assert abs(sum(sample["probabilities"]) - 1) < 1e-10
                assert abs(sum(sample["ideal_probabilities"]) - 1) < 1e-10
                assert sample["bit_order"] == "q0-first"
                assert sample["openqasm2"].startswith("OPENQASM 2.0;")
            for estimate in evidence["estimates"].values():
                assert all(math.isfinite(value) for value in estimate.values())
                assert estimate["standard_error"] >= 0
            notebooks += 1
            cells += len(code)
            plots += images
            experiments += len(evidence["experiments"])
    return {
        "executed_notebooks": notebooks,
        "executed_code_cells": cells,
        "rendered_plots": plots,
        "locally_sampled_circuits": experiments,
        "new_cloud_tasks": 0,
    }


if __name__ == "__main__":
    print(json.dumps(validate(), ensure_ascii=False, indent=2))
