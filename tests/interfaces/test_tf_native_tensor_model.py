# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent pure TF local-operator gates; not native QNode acceptance."""

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("tensorflow")
_spec = importlib.util.spec_from_file_location("tf_tensor_probe", Path(__file__).parent / "probes/probe_tf_native_tensor_execution.py")
_probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_probe)


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("case", _probe.ORACLES, ids=lambda case: case["name"])
def test_full_operator_and_state(case, traced):
    _probe.check_value(case, traced)


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("case", _probe.ORACLES, ids=lambda case: case["name"])
def test_actual_matrix_quantum_jacobian_hessian_jvp_vjp(case, traced):
    _probe.check_derivatives(case, traced)


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("case", _probe.ORACLES, ids=lambda case: case["name"])
def test_full_complex_operator_or_state_derivatives(case, traced):
    _probe.check_complex_derivatives(case, traced)


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("case", _probe.ORACLES, ids=lambda case: case["name"])
@pytest.mark.parametrize("mode", ["for", "rof", "tape_tape"])
@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
def test_actual_mixed_ad_without_hessian_materialization(case, mode, loss_kind, traced, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Direction-only mixed AD requested a full Jacobian/Hessian")
    monkeypatch.setattr(_probe.tf.GradientTape, "jacobian", forbidden)
    _probe.check_mixed(case, mode, loss_kind, traced)


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("exponent", [0.5, -0.5, 1.5])
def test_exact_identity_complete_complex_jet_and_zero_direction(exponent, traced):
    import numpy as np
    tf = _probe.tf
    def execute(point):
        def matrix(x):
            value = _probe.rotation("z", x[1]) @ _probe.rotation("x", x[0])
            return _probe.fractional_su2(value, exponent, 0.13*x[0]*x[1])
        with tf.GradientTape(persistent=True) as outer:
            outer.watch(point)
            with tf.GradientTape(persistent=True) as inner:
                inner.watch(point)
                value = matrix(point)
                components = tf.concat([tf.reshape(tf.math.real(value), (-1,)), tf.reshape(tf.math.imag(value), (-1,))], 0)
            jacobian = inner.jacobian(components, point, experimental_use_pfor=False)
        hessian = outer.jacobian(jacobian, point, experimental_use_pfor=False)
        with tf.autodiff.ForwardAccumulator(point, tf.zeros_like(point)) as forward:
            zero_value = matrix(point)
        return value, jacobian, hessian, forward.jvp(zero_value)
    fn = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    value, j, h, zero = fn(tf.constant([0., 0.], tf.float64))
    identity, x, y, z = np.eye(2), np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]]), np.diag([1., -1.])
    def flat(matrix):
        return np.r_[matrix.real.reshape(-1), matrix.imag.reshape(-1)]
    first = np.stack([flat(-0.5j*exponent*x), flat(-0.5j*exponent*z)], axis=1)
    diagonal = flat(-exponent**2*identity/4)
    cross = flat(-0.25j*exponent*y+0.13j*exponent*identity)
    second = np.stack([np.stack([diagonal, cross], axis=1), np.stack([cross, diagonal], axis=1)], axis=1)
    np.testing.assert_allclose(value, identity, atol=1e-14, rtol=0)
    np.testing.assert_allclose(j, first, atol=1e-12, rtol=0)
    np.testing.assert_allclose(h, second, atol=1e-11, rtol=0)
    np.testing.assert_array_equal(zero, np.zeros((2, 2), complex))


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("offset", [-1e-4, 0., 1e-4])
def test_branch_cut_guard_does_not_return_an_unreliable_tensor(offset, traced):
    import math
    tf = _probe.tf
    def execute(point):
        value = _probe.rotation("y", -point[0]) @ _probe.rotation("z", point[1]) @ _probe.rotation("y", point[0])
        return _probe.fractional_su2(value, 0.5, tf.constant(0., tf.float64))
    fn = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    with pytest.raises(tf.errors.InvalidArgumentError, match="branch/cubic"):
        fn(tf.constant([0.37, 2*math.pi+offset], tf.float64))


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("bad", ["nonunitary", "determinant", "phase"])
def test_invalid_unitary_and_phase_inputs_refuse(bad, traced):
    tf = _probe.tf
    def execute():
        matrix, phase = tf.eye(2, dtype=tf.complex128), tf.constant(0., tf.float64)
        if bad == "nonunitary":
            matrix *= 2
        elif bad == "determinant":
            matrix *= tf.constant(1j, tf.complex128)
        else:
            phase = tf.constant(float("nan"), tf.float64)
        return _probe.fractional_su2(matrix, 0.5, phase)
    fn = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    with pytest.raises(tf.errors.InvalidArgumentError):
        fn()


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("mode", ["value", "for", "rof", "tape_tape"])
@pytest.mark.parametrize("bad", ["nonunitary", "determinant", "phase", "branch"])
def test_validation_is_not_bypassed_by_nested_ad(bad, mode, traced):
    import math
    tf = _probe.tf
    def execute(point):
        def loss():
            matrix = _probe.rotation("z", point[1]) @ _probe.rotation("x", point[0])
            phase = 0.13*point[0]*point[1]
            if bad == "nonunitary":
                matrix *= 2
            elif bad == "determinant":
                matrix *= tf.constant(1j, tf.complex128)
            elif bad == "phase":
                phase += tf.constant(float("nan"), tf.float64)
            else:
                matrix = _probe.rotation("y", -point[0]) @ _probe.rotation("z", point[1]) @ _probe.rotation("y", point[0])
                phase *= 0
            return tf.math.real(tf.linalg.trace(_probe.fractional_su2(matrix, 0.5, phase)))
        direction = tf.constant([0.4, -0.3], tf.float64)
        if mode == "value":
            return loss()
        if mode == "for":
            with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                with tf.GradientTape() as reverse:
                    reverse.watch(point)
                    value = loss()
                derivative = reverse.gradient(value, point)
            return forward.jvp(derivative)
        if mode == "rof":
            with tf.GradientTape() as reverse:
                reverse.watch(point)
                with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                    value = loss()
                derivative = forward.jvp(value)
            return reverse.gradient(derivative, point)
        with tf.GradientTape() as outer:
            outer.watch(point)
            with tf.GradientTape() as inner:
                inner.watch(point)
                value = loss()
            derivative = inner.gradient(value, point)
            contraction = tf.reduce_sum(derivative*direction)
        return outer.gradient(contraction, point)
    fn = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    point = [0.37, 2*math.pi if bad == "branch" else 0.82]
    message = {"nonunitary": "Non-unitary", "determinant": "determinant", "phase": "Nonfinite", "branch": "branch/cubic"}[bad]
    with pytest.raises(tf.errors.InvalidArgumentError, match=message):
        fn(tf.constant(point, tf.float64))


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("exponent", [0., 2., -3.])
def test_integer_power_does_not_prune_validation(exponent, traced):
    tf = _probe.tf
    def execute(point):
        matrix = 2*_probe.rotation("x", point[0])
        return _probe.fractional_su2(matrix, exponent, point[1])
    fn = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    with pytest.raises(tf.errors.InvalidArgumentError, match="Non-unitary"):
        fn(tf.constant([0.37, 0.82], tf.float64))
