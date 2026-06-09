# This file is independently implemented for QuantumBridge SDK.
# No source code from IBM, Qiskit, or Qiskit Dynamics was copied.
"""Run educational offline single-qubit dynamics with QuantumBridge."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.qiskit_dynamics import (
    run_dephasing_metadata_simulation_native,
    run_rabi_drive_dynamics_native,
    run_upstream_dynamics_if_available,
    run_z_precession_native,
)


def main() -> None:
    z_precession = run_z_precession_native()
    rabi_drive = run_rabi_drive_dynamics_native()
    dephasing = run_dephasing_metadata_simulation_native(gamma=0.05)
    upstream = run_upstream_dynamics_if_available()
    print(z_precession.to_json())
    print(rabi_drive.to_json())
    print(dephasing.to_json())
    print("z_final_state", z_precession.to_dict()["final_state"])
    print("rabi_final_state", rabi_drive.to_dict()["final_state"])
    print("dephasing_expectations", dephasing.expectation_values)
    print("warnings", z_precession.warnings + rabi_drive.warnings + dephasing.warnings)
    print("provenance", {"z": z_precession.provenance, "rabi": rabi_drive.provenance})
    print("upstream_available", upstream.unsupported_reason is None)
    print("cloud_access", z_precession.provenance["cloud_access"] or rabi_drive.provenance["cloud_access"])
    print("token_read", z_precession.provenance["token_read"] or rabi_drive.provenance["token_read"])
    print("hardware_access", z_precession.provenance["hardware_access"] or rabi_drive.provenance["hardware_access"])
    print("production_ready", z_precession.production_ready or rabi_drive.production_ready)
    print("hardware_calibration", z_precession.hardware_calibration or rabi_drive.hardware_calibration)


if __name__ == "__main__":
    main()
