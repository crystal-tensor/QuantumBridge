# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Algorithms was copied.

import math

from quantumbridge.compat.qiskit_algorithms import (
    build_two_qubit_test_hamiltonian,
    build_vqe_ansatz_rx_ry,
    evaluate_ansatz_statevector,
    expectation_value_statevector,
    run_vqe_native,
)


def test_native_vqe_actually_runs_and_returns_finite_eigenvalue():
    result = run_vqe_native(parameter_grid=(0.0, math.pi))
    assert result.algorithm == "VQE"
    assert result.mode == "native_minimal"
    assert result.native_implementation is True
    assert result.production_ready is False
    assert result.eigenvalue is not None
    assert math.isfinite(result.eigenvalue)
    assert result.optimal_parameters
    assert result.validate()


def test_native_vqe_statevector_expectation_path_runs():
    hamiltonian = build_two_qubit_test_hamiltonian()
    ansatz = build_vqe_ansatz_rx_ry(2, depth=1)
    state = evaluate_ansatz_statevector(ansatz, [0.0] * ansatz.num_parameters)
    value = expectation_value_statevector(state, hamiltonian)
    assert math.isfinite(value)
    assert state.shape == (4,)
