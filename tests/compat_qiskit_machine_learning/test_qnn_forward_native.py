import math

from quantumbridge.compat.qiskit_machine_learning import build_qnn_ansatz, qnn_expectation_z, qnn_forward_native


def test_qnn_forward_returns_finite_expectation():
    ansatz = build_qnn_ansatz(num_qubits=2, depth=1)
    weights = [0.0] * ansatz.num_parameters
    expectation = qnn_expectation_z([0.25, -0.5], weights)
    result = qnn_forward_native([0.25, -0.5], weights)

    assert math.isfinite(expectation)
    assert -1.0 <= expectation <= 1.0
    assert result.expectation == expectation
    assert result.predictions in ([0], [1])
