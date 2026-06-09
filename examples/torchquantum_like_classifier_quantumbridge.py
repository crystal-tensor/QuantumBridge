#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from TorchQuantum or PyTorch was copied.
"""Run a clean-room TorchQuantum-like classifier training example."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.torchquantum.examples import run_torchquantum_like_classifier_example


def main() -> None:
    payload = run_torchquantum_like_classifier_example()
    native = payload["native"]
    print("TorchQuantum-like native classifier")
    print(native.to_json())
    print("Warnings:", json.dumps(native.warnings))
    print("Provenance:", json.dumps(native.provenance, sort_keys=True))
    print("Upstream:", payload["upstream"].to_json())


if __name__ == "__main__":
    main()
