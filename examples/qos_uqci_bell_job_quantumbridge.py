#!/usr/bin/env python3
"""Run a QuantumBridge Bell circuit through a QOS-UQCI offline job spec."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.qos_uqci.examples import run_qos_uqci_bell_job_example


def main() -> None:
    data = run_qos_uqci_bell_job_example()
    print("QOS-UQCI Bell job spec")
    print(json.dumps(data["circuit_ir"], sort_keys=True))
    print(json.dumps(data["job_spec"], sort_keys=True))
    print("Warnings:", json.dumps(data["job_spec"]["warnings"], sort_keys=True))
    print("Provenance:", json.dumps(data["job_spec"]["provenance"], sort_keys=True))
    print("Upstream:", data["upstream"].to_json())


if __name__ == "__main__":
    main()
