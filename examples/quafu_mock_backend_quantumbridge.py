#!/usr/bin/env python3
"""Run the Quafu-compatible offline mock backend."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.quafu.examples import run_quafu_mock_backend_example


def main() -> None:
    data = run_quafu_mock_backend_example()
    result = data["result"]
    print("Quafu mock backend")
    print(result.to_json())
    print("Counts:", json.dumps(result.counts, sort_keys=True))
    print("Warnings:", json.dumps(result.warnings, sort_keys=True))
    print("Provenance:", json.dumps(result.provenance, sort_keys=True))
    print("Upstream:", data["upstream"].to_json())


if __name__ == "__main__":
    main()
