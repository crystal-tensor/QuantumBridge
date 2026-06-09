"""Run the QuantumBridge clean-room QMAP-like routing example."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.mqt.examples import run_mqt_qmap_like_example


def main() -> None:
    result = run_mqt_qmap_like_example(shots=64, seed=13)
    mapping = result["mapping"]
    comparison = result["comparison"]
    upstream = result["upstream"]
    print(mapping.to_json())
    print(comparison.to_json())
    print(upstream.to_json())
    print("cost:", result["cost"])
    print("warnings:", mapping.warnings)
    print("provenance:", mapping.provenance)


if __name__ == "__main__":
    main()
