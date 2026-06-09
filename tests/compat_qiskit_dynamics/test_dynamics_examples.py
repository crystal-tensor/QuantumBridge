import subprocess
import sys


def test_single_qubit_dynamics_example_runs():
    completed = subprocess.run(
        [sys.executable, "examples/qiskit_dynamics_single_qubit_quantumbridge.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "z_precession_native" in completed.stdout
    assert "rabi_drive_dynamics_native" in completed.stdout
    assert "hardware_calibration False" in completed.stdout
