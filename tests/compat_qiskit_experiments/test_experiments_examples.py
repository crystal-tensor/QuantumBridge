import subprocess
import sys


def test_rabi_example_runs():
    completed = subprocess.run(
        [sys.executable, "examples/qiskit_experiments_rabi_quantumbridge.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "rabi_experiment_native" in completed.stdout
    assert "hardware_calibration False" in completed.stdout


def test_t1_ramsey_example_runs():
    completed = subprocess.run(
        [sys.executable, "examples/qiskit_experiments_t1_ramsey_quantumbridge.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "t1_experiment_native" in completed.stdout
    assert "ramsey_experiment_native" in completed.stdout
