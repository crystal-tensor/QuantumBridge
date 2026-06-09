#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from TorchQuantum or PyTorch was copied.
"""Run a clean-room TorchQuantum-like batch-forward example."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.torchquantum.examples import run_torchquantum_like_batch_forward_example


def main() -> None:
    payload = run_torchquantum_like_batch_forward_example()
    native = payload["native"]
    print("TorchQuantum-like native batch forward")
    print(native.to_json())
    print("Warnings:", json.dumps(native.warnings))
    print("Provenance:", json.dumps(native.provenance, sort_keys=True))
    if payload["torch"] is None:
        print("Optional torch path: skipped because torch is unavailable")
    else:
        print("Optional torch path:", payload["torch"].to_json())
    print("Upstream:", payload["upstream"].to_json())


if __name__ == "__main__":
    main()
