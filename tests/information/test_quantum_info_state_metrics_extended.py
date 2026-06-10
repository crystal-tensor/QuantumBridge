# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import numpy as np

from quantumbridge import Circuit
from quantumbridge.information import (
    DensityMatrix,
    Statevector,
    hellinger_distance,
    hellinger_fidelity,
    state_fidelity,
    state_fidelity_general,
    trace_distance,
)


def test_statevector_density_matrix_conversions_and_reduced_states():
    bell = Statevector.from_circuit(Circuit(2).h(0).cx(0, 1))

    rho = bell.to_density_matrix()
    reduced_from_state = bell.partial_trace([0])
    reduced_from_density = rho.partial_trace([1])

    assert rho.is_valid()
    np.testing.assert_allclose(reduced_from_state.data, np.eye(2) / 2, atol=1e-12)
    np.testing.assert_allclose(reduced_from_density.data, np.eye(2) / 2, atol=1e-12)
    np.testing.assert_allclose(bell.to_operator().to_matrix(), rho.to_operator().to_matrix(), atol=1e-12)


def test_density_matrix_from_int_label_and_adjoint_helpers():
    rho = DensityMatrix.from_label("10")
    sigma = DensityMatrix.from_int(2, 4)

    np.testing.assert_allclose(rho.data, sigma.data, atol=1e-12)
    np.testing.assert_allclose(rho.conjugate().data, rho.data, atol=1e-12)
    np.testing.assert_allclose(rho.adjoint().data, rho.data, atol=1e-12)
    assert rho.to_statevector().equiv(Statevector.from_label("10"))
    assert Statevector.from_label("1").adjoint().shape == (1, 2)


def test_general_state_fidelity_trace_and_hellinger_metrics():
    zero = Statevector.from_label("0")
    one = Statevector.from_label("1")
    mixed = DensityMatrix(np.eye(2) / 2)

    assert abs(state_fidelity(zero, zero) - 1.0) < 1e-12
    assert abs(state_fidelity_general(zero, mixed) - 0.5) < 1e-12
    assert abs(trace_distance(zero.to_density_matrix(), one.to_density_matrix()) - 1.0) < 1e-12
    assert abs(hellinger_fidelity({"0": 0.5, "1": 0.5}, {"0": 0.5, "1": 0.5}) - 1.0) < 1e-12
    assert hellinger_distance({"0": 1.0}, {"1": 1.0}) == 1.0
