# This file is independently implemented for QuantumBridge SDK.
# No source code, prose, UI, or branding from IBM, Qiskit, PennyLane, or third-party projects was copied.
"""Generate local frontend seed data from QuantumBridge Studio backend services."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quantumbridge.studio.frontend_contract import DEFAULT_FRONTEND_SEED_DIR, write_frontend_seed_bundle


def main() -> None:
    written = write_frontend_seed_bundle(DEFAULT_FRONTEND_SEED_DIR)
    print(json.dumps({"written_files": [str(path) for path in written]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
