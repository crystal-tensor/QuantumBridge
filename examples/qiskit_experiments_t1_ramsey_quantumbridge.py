# This file is independently implemented for QuantumBridge SDK.
# No source code from IBM, Qiskit, or Qiskit Experiments was copied.
"""Run educational offline T1 and Ramsey experiments with QuantumBridge."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.qiskit_experiments import (
    run_ramsey_experiment_native,
    run_t1_experiment_native,
    run_upstream_experiments_if_available,
)


def main() -> None:
    t1 = run_t1_experiment_native(seed=11)
    ramsey = run_ramsey_experiment_native(seed=13)
    upstream = run_upstream_experiments_if_available()
    print(t1.to_json())
    print(ramsey.to_json())
    print("t1_fit", t1.fit_parameters)
    print("ramsey_fit", ramsey.fit_parameters)
    print("warnings", t1.warnings + ramsey.warnings)
    print("provenance", {"t1": t1.provenance, "ramsey": ramsey.provenance})
    print("upstream_available", upstream.unsupported_reason is None)
    print("cloud_access", t1.provenance["cloud_access"] or ramsey.provenance["cloud_access"])
    print("token_read", t1.provenance["token_read"] or ramsey.provenance["token_read"])
    print("hardware_access", t1.provenance["hardware_access"] or ramsey.provenance["hardware_access"])
    print("production_ready", t1.production_ready or ramsey.production_ready)
    print("hardware_calibration", t1.hardware_calibration or ramsey.hardware_calibration)


if __name__ == "__main__":
    main()
