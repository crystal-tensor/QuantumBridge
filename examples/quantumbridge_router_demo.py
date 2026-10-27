#!/usr/bin/env python3
"""Generate the QuantumBridge Router-first demo artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.router import run_router_demo


def main() -> None:
    output_dir = ROOT / "output" / "router_demo"
    payload = run_router_demo(output_dir=output_dir, job_count=100, seed=7)
    print(json.dumps({"output_dir": str(output_dir), "written_files": payload["written_files"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
