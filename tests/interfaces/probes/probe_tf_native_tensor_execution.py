# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Pure public TF quantum tensor math; no QNode/MPS acceptance claim."""

import json
import math
from numbers import Real
from pathlib import Path
import sys
import traceback

import numpy as np
import tensorflow as tf

ORACLES = json.loads((Path(__file__).parents[2] / "information/data/tf_native_tensor_execution_oracles.json").read_text())["cases"]


def complex_real(value):
    return tf.complex(value, tf.zeros_like(value))


def phase(angle):
    return tf.complex(tf.cos(angle), tf.sin(angle))


def rotation(axis, angle):
    c, s = tf.cos(angle/2), tf.sin(angle/2)
    z, c, s = tf.zeros_like(c), complex_real(c), complex_real(s)
    if axis == "x":
        return tf.stack([tf.stack([c, -1j*s]), tf.stack([-1j*s, c])])
    if axis == "y":
        return tf.stack([tf.stack([c, -s]), tf.stack([s, c])])
    return tf.linalg.diag(tf.stack([c-tf.complex(z, tf.math.real(s)), c+tf.complex(z, tf.math.real(s))]))


def kron(a, b):
    return tf.reshape(tf.einsum("ij,kl->ikjl", a, b), (a.shape[0]*b.shape[0], a.shape[1]*b.shape[1]))


@tf.function(autograph=False, jit_compile=False)
def _validated_source(matrix, global_phase, exponent):
    # Only boolean validation decisions cross this boundary. No trainable
    # output is hidden inside a function that also executes assertion ops.
    identity = tf.eye(2, dtype=tf.complex128)
    residual = tf.reduce_max(tf.reduce_sum(tf.abs(tf.linalg.adjoint(matrix) @ matrix-identity), axis=0))
    checks = [tf.debugging.assert_all_finite(tf.math.real(matrix), "Nonfinite local matrix"),
        tf.debugging.assert_all_finite(tf.math.imag(matrix), "Nonfinite local matrix"),
        tf.raw_ops.Assert(condition=residual <= tf.constant(512*2*np.finfo(float).eps, tf.float64),
            data=[tf.constant("Non-unitary SU(2) source"), residual]),
        tf.raw_ops.Assert(condition=tf.abs(tf.linalg.det(matrix)-1) <= tf.constant(512*2*np.finfo(float).eps, tf.float64),
            data=[tf.constant("SU(2) determinant must equal one")])]
    checks.append(tf.debugging.assert_all_finite(global_phase, "Nonfinite local phase"))
    if exponent.is_integer():
        with tf.control_dependencies(checks):
            return tf.constant(False), tf.constant(False)
    center = tf.math.real(tf.linalg.trace(matrix))/2
    negative = center < 0.
    flip = tf.where(negative, tf.constant(-1., tf.float64), tf.constant(1., tf.float64))
    matrix = complex_real(flip)*matrix
    global_phase += tf.where(flip < 0., tf.constant(math.pi, tf.float64), tf.constant(0., tf.float64))
    center = tf.math.real(tf.linalg.trace(matrix))/2
    delta = matrix-complex_real(center)*identity
    squared = tf.reduce_sum(tf.math.real(tf.math.conj(delta)*delta))/2
    small = squared*(1+abs(exponent))**2 < 1e-6
    safe_squared = tf.where(small, tf.constant(1e-6, tf.float64), squared)
    sine = tf.sqrt(safe_squared)
    theta = tf.math.atan2(sine, center)
    def wrap(angle):
        return tf.math.atan2(tf.sin(angle), tf.cos(angle))
    plus, minus, principal = wrap(global_phase+theta), wrap(global_phase-theta), wrap(global_phase)
    resolution = tf.constant(512*2*np.finfo(float).eps, tf.float64)
    gap = 2*sine
    screen = (64*np.finfo(float).eps*4*(1+abs(exponent))**2*abs(math.sin(math.pi*exponent)))/gap**3
    regular_safe = ((tf.abs(tf.abs(plus)-math.pi) > resolution)
        & (tf.abs(tf.abs(minus)-math.pi) > resolution)
        & ((tf.abs(plus-minus) <= math.pi) | (screen <= math.sqrt(np.finfo(float).eps))))
    # asin(sqrt(t))**2 has a regular power series at t=0. Use it only
    # for the branch guard; the returned matrix contains no sqrt(0) graph.
    theta_squared = tf.zeros_like(squared)
    for index in range(1, 7):
        theta_squared += (4**index/(2*index*index*math.comb(2*index, index)))*squared**index
    margin = math.pi-tf.abs(principal)
    small_safe = (margin > resolution) & ((margin-resolution)**2 > theta_squared)
    guard = tf.raw_ops.Assert(condition=tf.where(small, small_safe, regular_safe),
        data=[tf.constant("Fractional SU(2) principal branch/cubic separation screen is unresolved")])
    with tf.control_dependencies([*checks, guard]):
        return tf.identity(negative), tf.identity(small)


def fractional_su2(matrix, exponent, global_phase):
    if matrix.shape != (2, 2) or matrix.dtype != tf.complex128:
        raise ValueError("The prototype requires a static complex128 2x2 SU(2) matrix")
    if isinstance(exponent, bool) or not isinstance(exponent, Real):
        raise TypeError("The exponent must be a static real scalar")
    exponent = float(exponent)
    if not math.isfinite(exponent):
        raise ValueError("The exponent must be a finite static real number")
    global_phase = tf.convert_to_tensor(global_phase, tf.float64)
    if global_phase.shape != ():
        raise ValueError("The local global phase must be scalar")
    negative, small = _validated_source(matrix, global_phase, exponent)
    identity = tf.eye(2, dtype=tf.complex128)
    if exponent.is_integer():
        count, base, result = abs(int(exponent)), matrix, identity
        if exponent < 0:
            base = tf.linalg.adjoint(base)
        while count:
            if count & 1:
                result = base @ result
            count >>= 1
            if count:
                base = base @ base
        return phase(exponent*global_phase)*result
    matrix = tf.where(negative, -matrix, matrix)
    global_phase += tf.where(negative, tf.constant(math.pi, tf.float64), tf.constant(0., tf.float64))
    center = tf.math.real(tf.linalg.trace(matrix))/2
    delta = matrix-complex_real(center)*identity
    squared = tf.reduce_sum(tf.math.real(tf.math.conj(delta)*delta))/2
    safe_squared = tf.where(small, tf.constant(1e-6, tf.float64), squared)
    sine = tf.sqrt(safe_squared)
    theta = tf.math.atan2(sine, center)
    def wrap(angle):
        return tf.math.atan2(tf.sin(angle), tf.cos(angle))
    plus, minus, principal = wrap(global_phase+theta), wrap(global_phase-theta), wrap(global_phase)

    a_coefficients, b_coefficients = [1.], [exponent]
    for index in range(4):
        a_coefficients.append(a_coefficients[-1]*((2*index)**2-exponent**2)/((2*index+2)*(2*index+1)))
        b_coefficients.append(b_coefficients[-1]*((2*index+1)**2-exponent**2)/((2*index+3)*(2*index+2)))
    if not all(math.isfinite(value) for value in a_coefficients+b_coefficients):
        raise FloatingPointError("SU(2) derivative series coefficients exceed float64")
    def polynomial(coefficients):
        result = tf.constant(coefficients[-1], tf.float64)
        for value in reversed(coefficients[:-1]):
            result = result*squared+value
        return result
    small_a = phase(exponent*principal)*complex_real(polynomial(a_coefficients))
    small_b = phase(exponent*principal)*complex_real(polynomial(b_coefficients))
    regular_a = (phase(exponent*plus)+phase(exponent*minus))/2
    regular_b = (phase(exponent*plus)-phase(exponent*minus))/tf.complex(tf.zeros_like(sine), 2*sine)
    a = tf.where(small, small_a, regular_a)
    b = tf.where(small, small_b, regular_b)
    return a*identity+b*delta


def local_operator(point, case):
    p, q = point[0], point[1]
    matrix = rotation("z", q) @ rotation("x", p)
    if case["body"] == "requested":
        matrix = rotation("y", -p) @ rotation("z", q*q+0.4) @ rotation("x", p)
    angle = tf.constant(case["phase_offset"], tf.float64)+case["phase_scale"]*p*q
    return fractional_su2(matrix, case["power"], angle)


def state(point, case):
    p, q = point[0], point[1]
    identity = tf.eye(2, dtype=tf.complex128)
    if case["body"] == "baseline":
        cnot = tf.constant([[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]], tf.complex128)
        operator = phase(0.13*p*q)*kron(rotation("y", q), rotation("x", p*q)) @ cnot @ kron(
            rotation("z", q*q+0.4), rotation("y", -p)) @ kron(identity, rotation("x", p))
        return tf.linalg.matvec(operator, tf.constant([1, 0, 0, 0], tf.complex128))
    operator = local_operator(point, case)
    if case.get("control") is None:
        return operator[:, 0]
    zero, one = tf.constant([[1, 0], [0, 0]], tf.complex128), tf.constant([[0, 0], [0, 1]], tf.complex128)
    selected, other = (one, zero) if case["control"] else (zero, one)
    controlled = kron(selected, operator)+kron(other, identity)
    return tf.linalg.matvec(controlled, tf.constant([1, 0, 1, 0], tf.complex128))/tf.sqrt(tf.constant(2., tf.complex128))


def outputs(point, case):
    psi = state(point, case)
    x = tf.constant([[0, 1], [1, 0]], tf.complex128)
    y = tf.constant([[0, -1j], [1j, 0]], tf.complex128)
    z = tf.constant([[1, 0], [0, -1]], tf.complex128)
    observables = [z, x]
    if psi.shape[0] == 4:
        identity = tf.eye(2, dtype=tf.complex128)
        observables = [kron(identity, z), kron(x, identity)]
        if case["body"] == "baseline":
            observables[1] += 0.2*kron(z, y)
    return tf.stack([tf.math.real(tf.reduce_sum(tf.math.conj(psi)*tf.linalg.matvec(observable, psi))) for observable in observables])


def decoded(value):
    data = np.asarray(value)
    return data[..., 0]+1j*data[..., 1]


def no_callback_ops(concrete):
    graph = concrete.graph.as_graph_def()
    operations = [node.op for node in graph.node]
    operations.extend(node.op for function in graph.library.function for node in function.node_def)
    forbidden = {"PyFunc", "PyFuncStateless", "EagerPyFunc", "Eig", "SelfAdjointEigV2", "MatrixLogarithm"}
    assert not forbidden.intersection(operations), "Tensor-math graph contains a callback or generic spectral evaluator"
    return len(operations)


def check_value(case, traced=False):
    def execute(point):
        psi = state(point, case)
        operator = tf.eye(1, dtype=tf.complex128) if case["body"] == "baseline" else local_operator(point, case)
        return psi, outputs(point, case), operator
    function = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    actual_state, actual_outputs, actual_operator = function(tf.constant(case["point"], tf.float64))
    np.testing.assert_allclose(actual_state, decoded(case["state"])[:, 0], atol=2e-12, rtol=0)
    np.testing.assert_allclose(actual_outputs, case["outputs"], atol=3e-12, rtol=0)
    np.testing.assert_allclose(np.vdot(actual_state, actual_state), 1., atol=2e-12, rtol=0)
    if case["body"] != "baseline":
        np.testing.assert_allclose(actual_operator, decoded(case["operator"]), atol=2e-12, rtol=0)
    return dict(outputs=np.asarray(actual_outputs).tolist(), graph_ops=no_callback_ops(function.get_concrete_function(tf.TensorSpec((2,), tf.float64))) if traced else None)


def check_derivatives(case, traced=False):
    d, u = tf.constant([0.4, -0.3], tf.float64), tf.constant([0.7, -0.2], tf.float64)
    def execute(point):
        with tf.GradientTape(persistent=True) as outer:
            outer.watch(point)
            with tf.GradientTape(persistent=True) as inner:
                inner.watch(point)
                value = outputs(point, case)
            jacobian = inner.jacobian(value, point, experimental_use_pfor=False)
        hessian = outer.jacobian(jacobian, point, experimental_use_pfor=False)
        vjp = inner.gradient(value, point, output_gradients=u)
        with tf.autodiff.ForwardAccumulator(point, d) as forward:
            raw = outputs(point, case)
        return jacobian, hessian, forward.jvp(raw), vjp
    function = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    j, h, jvp, vjp = function(tf.constant(case["point"], tf.float64))
    expected_j, expected_h = np.array(case["jacobian"]), np.array(case["hessians"])
    for actual, expected in [(j, expected_j), (h, expected_h), (jvp, expected_j @ [0.4, -0.3]), (vjp, expected_j.T @ [0.7, -0.2])]:
        assert actual is not None
        np.testing.assert_allclose(actual, expected, atol=3e-10, rtol=0)
    return dict(jacobian=np.asarray(j).tolist(), hessians=np.asarray(h).tolist())


def check_complex_derivatives(case, traced=False):
    def components(point):
        value = state(point, case) if case["body"] == "baseline" else local_operator(point, case)
        return tf.concat([tf.reshape(tf.math.real(value), (-1,)), tf.reshape(tf.math.imag(value), (-1,))], axis=0)
    def execute(point):
        directions = [tf.constant([1., 0.], tf.float64), tf.constant([0., 1.], tf.float64)]
        first, second = [], []
        for direction in directions:
            with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                value = components(point)
            first.append(forward.jvp(value))
        for left in directions:
            row = []
            for right in directions:
                with tf.autodiff.ForwardAccumulator(point, left) as outer:
                    with tf.autodiff.ForwardAccumulator(point, right) as inner:
                        value = components(point)
                    tangent = inner.jvp(value)
                row.append(outer.jvp(tangent))
            second.append(tf.stack(row, axis=1))
        return tf.stack(first, axis=1), tf.stack(second, axis=1)
    function = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    j, h = function(tf.constant(case["point"], tf.float64))
    np.testing.assert_allclose(j, case["complex_jacobian"], atol=5e-10, rtol=0)
    np.testing.assert_allclose(h, case["complex_hessians"], atol=8e-10, rtol=0)
    return dict(max_jacobian_error=float(np.max(np.abs(np.asarray(j)-case["complex_jacobian"]))),
        max_hessian_error=float(np.max(np.abs(np.asarray(h)-case["complex_hessians"]))))


def check_mixed(case, mode, loss_kind, traced=False):
    weights, direction = np.array([0.7, -0.2]), np.array([0.4, -0.3])
    value, j, h = np.array(case["outputs"]), np.array(case["jacobian"]), np.array(case["hessians"])
    first, second = ((2*(value-0.3), np.full(2, 2.)) if loss_kind == "square"
        else (np.exp(value)+0.6*value**2, np.exp(value)+1.2*value))
    expected = j.T @ (weights*second*(j @ direction))+np.einsum("i,ijk,k->j", weights*first, h, direction)
    def execute(point):
        d = tf.constant(direction, tf.float64)
        def loss():
            y = outputs(point, case)
            terms = (y-0.3)**2 if loss_kind == "square" else tf.exp(y)+0.2*y**3
            return tf.reduce_sum(tf.constant(weights, tf.float64)*terms)
        if mode == "for":
            with tf.autodiff.ForwardAccumulator(point, d) as forward:
                with tf.GradientTape() as reverse:
                    reverse.watch(point)
                    value = loss()
                gradient = reverse.gradient(value, point)
            return forward.jvp(gradient)
        if mode == "rof":
            with tf.GradientTape() as reverse:
                reverse.watch(point)
                with tf.autodiff.ForwardAccumulator(point, d) as forward:
                    value = loss()
                tangent = forward.jvp(value)
            return reverse.gradient(tangent, point)
        with tf.GradientTape() as outer:
            outer.watch(point)
            with tf.GradientTape() as inner:
                inner.watch(point)
                value = loss()
            gradient = inner.gradient(value, point)
            contraction = tf.reduce_sum(gradient*d)
        return outer.gradient(contraction, point)
    function = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    actual = function(tf.constant(case["point"], tf.float64))
    assert actual is not None
    np.testing.assert_allclose(actual, expected, atol=5e-10, rtol=0)
    return dict(actual=np.asarray(actual).tolist(), expected=expected.tolist())


def run():
    records = []
    for case in ORACLES:
        for traced in [False, True]:
            for family in ["value", "derivatives", "complex_derivatives", "for_square", "rof_square", "tape_tape_square", "for_exponential_cubic", "rof_exponential_cubic", "tape_tape_exponential_cubic"]:
                record = dict(case=case["name"], traced=traced, family=family)
                try:
                    if family == "value":
                        result = check_value(case, traced)
                    elif family == "derivatives":
                        result = check_derivatives(case, traced)
                    elif family == "complex_derivatives":
                        result = check_complex_derivatives(case, traced)
                    else:
                        mode = "tape_tape" if family.startswith("tape_tape") else family.split("_", 1)[0]
                        result = check_mixed(case, mode, "square" if family.endswith("_square") else "exponential_cubic", traced)
                    record.update(outcome="matches_oracle", result=result)
                except Exception as error:
                    record.update(outcome="failure", error=type(error).__name__+": "+str(error), traceback=traceback.format_exc())
                records.append(record)
    assert not any(name.split(".")[0] in {"quantumbridge", "qiskit", "pennylane"} for name in sys.modules)
    return dict(diagnostic_only=True, tensorflow=tf.__version__, python=sys.version.split()[0], jit_compile=False,
        outcomes={outcome: sum(r["outcome"] == outcome for r in records) for outcome in ["matches_oracle", "failure"]}, records=records)


if __name__ == "__main__":
    print(json.dumps(run(), allow_nan=False))
