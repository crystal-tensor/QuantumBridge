#!/usr/bin/env python3
"""Run a QuantumBridge Bell circuit through a Quafu-compatible payload."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.quafu.examples import run_quafu_bell_payload_example


def main() -> None:
    data = run_quafu_bell_payload_example()
    print("Quafu-compatible Bell payload")
    print(json.dumps(data["circuit_ir"], sort_keys=True))
    print(json.dumps(data["payload"], sort_keys=True))
    print(json.dumps(data["job_spec"], sort_keys=True))
    print("Warnings:", json.dumps(data["payload"]["warnings"], sort_keys=True))
    print("Provenance:", json.dumps(data["payload"]["provenance"], sort_keys=True))
    print("Upstream:", data["upstream"].to_json())


if __name__ == "__main__":
    main()
