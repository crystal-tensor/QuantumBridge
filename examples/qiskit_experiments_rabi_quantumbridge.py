# This file is independently implemented for QuantumBridge SDK.
# No source code from IBM, Qiskit, or Qiskit Experiments was copied.
"""Run an educational offline Rabi experiment with QuantumBridge."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.qiskit_experiments import (
    run_rabi_experiment_native,
    run_upstream_experiments_if_available,
)


def main() -> None:
    result = run_rabi_experiment_native(seed=7)
    upstream = run_upstream_experiments_if_available()
    print(result.to_json())
    print("fit_parameters", result.fit_parameters)
    print("warnings", result.warnings)
    print("provenance", result.provenance)
    print("upstream_available", upstream.unsupported_reason is None)
    print("cloud_access", result.provenance["cloud_access"])
    print("token_read", result.provenance["token_read"])
    print("hardware_access", result.provenance["hardware_access"])
    print("production_ready", result.production_ready)
    print("hardware_calibration", result.hardware_calibration)


if __name__ == "__main__":
    main()
