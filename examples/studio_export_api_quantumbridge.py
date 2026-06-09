#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
"""Run the local QuantumBridge Studio export API example."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.studio.api_models import to_json_safe
from quantumbridge.studio.examples import run_export_api_example


def main() -> None:
    print(json.dumps(to_json_safe(run_export_api_example()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
