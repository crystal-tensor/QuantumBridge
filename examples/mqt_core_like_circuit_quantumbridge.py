"""Run the QuantumBridge clean-room MQT Core-like circuit example."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.mqt.examples import run_mqt_core_like_example


def main() -> None:
    result = run_mqt_core_like_example()
    native = result["native"]
    upstream = result["upstream"]
    print(native.to_json())
    print(upstream.to_json())
    print(result["qasm"])
    print("warnings:", native.warnings)
    print("provenance:", native.provenance)


if __name__ == "__main__":
    main()
