# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.pennylane_full.measurements_adapter import describe_measurement, list_measurements, wrap_measurement_result


def test_pennylane_measurements_adapter_describes_common_measurements():
    assert {"expval", "probs", "sample", "counts", "state", "density_matrix"}.issubset(set(list_measurements()))
    assert describe_measurement("probs")["supported"] is True


def test_pennylane_measurement_result_wrapper():
    result = wrap_measurement_result({"counts": {"0": 1}})
    assert result.metadata["adapter"] == "measurements_adapter"
    assert result.ecosystem == "pennylane"
