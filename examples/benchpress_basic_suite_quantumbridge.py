#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from IBM, Qiskit, or Benchpress was copied.
"""Run the Stage 10B basic circuit benchmark suite."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.benchpress.examples import run_basic_suite_example


def main() -> None:
    output = run_basic_suite_example()
    print(output["native"].to_json())
    print(output["markdown_report"])
    print(output["warnings"])
    print(output["provenance"])


if __name__ == "__main__":
    main()
