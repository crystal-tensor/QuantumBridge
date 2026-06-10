# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from math import cos, sin

import numpy as np

from quantumbridge import Circuit, PauliZ, StatevectorDevice
from quantumbridge.compat.pennylane_full.gradients_adapter import describe_gradient, get_gradient_transform, list_native_gradients
from quantumbridge.transforms import finite_difference, metric_tensor, qng_step, spsa_gradient


def _ry_state(params):
    return StatevectorDevice().statevector(Circuit(1).ry(float(params[0]), 0))


def _ry_z_objective(params):
    return StatevectorDevice().expectation(Circuit(1).ry(float(params[0]), 0), PauliZ(0))


def test_native_spsa_gradient_matches_single_parameter_derivative():
    theta = np.array([0.31])

    fd = finite_difference(_ry_z_objective, theta)[0]
    spsa = spsa_gradient(_ry_z_objective, theta, step=1e-5, samples=4, seed=3)[0]

    assert abs(fd + sin(theta[0])) < 1e-6
    assert abs(spsa - fd) < 1e-5


def test_native_metric_tensor_for_single_ry_state():
    theta = np.array([0.27])
    metric = metric_tensor(_ry_state, theta)

    np.testing.assert_allclose(metric, [[0.25]], atol=1e-6)


def test_native_qng_step_uses_metric_tensor_preconditioning():
    theta = np.array([0.2])
    updated = qng_step(_ry_z_objective, _ry_state, theta, stepsize=0.05, regularization=0.0)

    expected = theta[0] - 0.05 * (-sin(theta[0]) / 0.25)
    assert abs(updated[0] - expected) < 1e-5
    assert _ry_z_objective(updated) < cos(theta[0])


def test_pennylane_gradients_adapter_exposes_native_transforms():
    assert {"finite_difference", "spsa_gradient", "metric_tensor", "qng_step"}.issubset(set(list_native_gradients()))
    assert describe_gradient("metric_tensor")["native"] is True
    assert get_gradient_transform("finite_difference") is finite_difference
    assert get_gradient_transform("spsa") is spsa_gradient
