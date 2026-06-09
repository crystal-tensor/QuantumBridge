"""Run the QuantumBridge clean-room DDSIM-like simulation example."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.mqt.examples import run_mqt_ddsim_like_example


def main() -> None:
    result = run_mqt_ddsim_like_example(shots=64, seed=11)
    statevector = result["statevector"]
    counts = result["counts"]
    comparison = result["comparison"]
    upstream = result["upstream"]
    print(statevector.to_json())
    print(counts.to_json())
    print(comparison.to_json())
    print(upstream.to_json())
    print("warnings:", counts.warnings)
    print("provenance:", counts.provenance)


if __name__ == "__main__":
    main()
