# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Public nested custom-gradient boundaries, no native quantum acceptance.

Analytic small test functions provide exact Jacobians/Hessians in this probe
only. They are not a production callback implementation or a substitute for
the native direction-only derivative/resource contract.
"""

import json
import math
import sys
import traceback

import numpy as np
import tensorflow as tf


def math_jet(x, kind, mathlib):
    if kind == "scalar":
        value = mathlib.sin(x[0])
        return [value], [[mathlib.cos(x[0])]], [[[-value]]]
    p, q = x[0], x[1]
    value = mathlib.sin(p)*mathlib.cos(q)+p*q
    g = [mathlib.cos(p)*mathlib.cos(q)+q, -mathlib.sin(p)*mathlib.sin(q)+p]
    z, w = -mathlib.sin(p)*mathlib.cos(q), 1-mathlib.cos(p)*mathlib.sin(q)
    values, jacobian, hessian = [value], [g], [[[z, w], [w, z]]]
    if kind == "multioutput":
        values.append(p*p+0.3*mathlib.sin(q))
        jacobian.append([2*p, 0.3*mathlib.cos(q)])
        hessian.append([[2., 0.], [0., -0.3*mathlib.sin(q)]])
    return values, jacobian, hessian


def tf_jet(x, kind):
    value, jacobian, hessian = math_jet(x, kind, tf)
    # Stack each level so numeric constants inherit float64 from the tensors.
    dtype = x.dtype
    def stack(row):
        return tf.stack([tf.cast(item, dtype) for item in row])
    return stack(value), tf.stack([stack(row) for row in jacobian]), tf.stack([tf.stack([stack(row) for row in plane]) for plane in hessian])


def make_function(kind, layout):
    def plain(x):
        return tf_jet(x, kind)[0]
    forward = tf.function(plain, autograph=False, jit_compile=False) if layout == "custom_outside" else plain

    @tf.custom_gradient
    def boundary(x):
        value = forward(x)

        @tf.custom_gradient
        def first(point, cotangent):
            _, jacobian, _ = tf_jet(point, kind)
            result = tf.linalg.matvec(jacobian, cotangent, transpose_a=True)
            def second(direction):
                _, j, h = tf_jet(point, kind)
                return tf.einsum("i,ijk,k->j", cotangent, h, direction), tf.linalg.matvec(j, direction)
            return result, second

        return value, lambda cotangent: first(x, cotangent)

    if layout == "inner_custom":
        function = tf.function(boundary, autograph=False, jit_compile=False)
        return function, function
    return (plain, None) if layout == "plain_inline" else (boundary, forward if layout == "custom_outside" else None)


def expected(kind, point, direction, loss_kind):
    value, jacobian, hessian = (np.asarray(item, dtype=float) for item in math_jet(point, kind, math))
    weights = np.array([0.7, -0.2]) if kind == "multioutput" else np.array([0.7])
    if loss_kind == "square":
        terms, first, second = (value-0.3)**2, 2*(value-0.3), np.full_like(value, 2.)
    else:
        terms = np.exp(value)+0.2*value**3
        first, second = np.exp(value)+0.6*value**2, np.exp(value)+1.2*value
    gradient = jacobian.T @ (weights*first)
    hvp = jacobian.T @ (weights*second*(jacobian @ direction))+np.einsum("i,ijk,k->j", weights*first, hessian, direction)
    return dict(value=value.tolist(), jvp=(jacobian @ direction).tolist(), loss=float(weights @ terms),
        loss_jvp=float(gradient @ direction), gradient=gradient.tolist(), hvp=hvp.tolist(), vjp=(jacobian.T @ weights).tolist())


def evaluate(function, x, d, weights, mode, loss_kind):
    def loss(y):
        terms = (y-0.3)**2 if loss_kind == "square" else tf.exp(y)+0.2*y**3
        return tf.reduce_sum(weights*terms)
    if mode == "for":
        with tf.autodiff.ForwardAccumulator(x, d) as forward:
            with tf.GradientTape() as reverse:
                reverse.watch(x)
                y = function(x)
                value = loss(y)
            gradient = reverse.gradient(value, x)
        jvp, loss_jvp, hvp = forward.jvp(y), forward.jvp(value), forward.jvp(gradient)
    elif mode == "rof":
        with tf.GradientTape(persistent=True) as reverse:
            reverse.watch(x)
            with tf.autodiff.ForwardAccumulator(x, d) as forward:
                y = function(x)
                value = loss(y)
            jvp, loss_jvp = forward.jvp(y), forward.jvp(value)
        gradient, hvp = reverse.gradient(value, x), reverse.gradient(loss_jvp, x)
    else:
        with tf.GradientTape() as outer:
            outer.watch(x)
            with tf.GradientTape(persistent=True) as inner:
                inner.watch(x)
                y = function(x)
                value = loss(y)
            gradient = inner.gradient(value, x)
            contract = tf.reduce_sum(gradient*d)
            jvp = tf.linalg.matvec(inner.jacobian(y, x, experimental_use_pfor=False), d)
        loss_jvp, hvp = contract, outer.gradient(contract, x)
    with tf.GradientTape() as reverse:
        reverse.watch(x)
        raw = function(x)
    vjp = reverse.gradient(raw, x, output_gradients=weights)
    return y, jvp, value, loss_jvp, gradient, hvp, vjp


def run():
    records = []
    for kind in ["scalar", "vector", "multioutput"]:
        point = [0.37] if kind == "scalar" else [0.37, 0.82]
        direction = [0.4] if kind == "scalar" else [0.4, -0.3]
        weights = [0.7, -0.2] if kind == "multioutput" else [0.7]
        for layout in ["plain_inline", "custom_inline", "inner_custom", "custom_outside"]:
            for traced in [False, True]:
                for loss_kind in ["square", "exponential_cubic"]:
                    oracle = expected(kind, point, direction, loss_kind)
                    for mode in ["for", "rof", "tape_tape"]:
                        fn, inner = make_function(kind, layout)
                        def execute(x, d):
                            return evaluate(fn, x, d, tf.constant(weights, tf.float64), mode, loss_kind)
                        executor = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
                        record = dict(kind=kind, layout=layout, traced=traced, mode=mode, loss=loss_kind,
                            dtype="float64", jit_compile=False, expected=oracle)
                        try:
                            outputs = executor(tf.constant(point, tf.float64), tf.constant(direction, tf.float64))
                            actual = {key: None if value is None else np.asarray(value).tolist() for key, value in zip(oracle, outputs)}
                            errors = {key: None if actual[key] is None else float(np.max(np.abs(np.asarray(actual[key])-oracle[key]))) for key in oracle}
                            outcome = ("disconnected_or_nonfinite" if any(error is None or not np.isfinite(error) for error in errors.values())
                                       else "wrong_finite" if any(error > 1e-10 for error in errors.values()) else "matches_analytic")
                            record.update(outcome=outcome, actual=actual, absolute_errors=errors)
                        except Exception as error:
                            record.update(outcome="exception", error=type(error).__name__+": "+str(error), traceback=traceback.format_exc())
                        record.update(inner_tracing_count=inner.experimental_get_tracing_count() if inner is not None else 0,
                            outer_tracing_count=executor.experimental_get_tracing_count() if traced else 0)
                        records.append(record)
    if any(name.split(".")[0] in {"quantumbridge", "qiskit", "pennylane"} for name in sys.modules):
        raise AssertionError("Diagnostic imported a quantum SDK")
    return dict(diagnostic_only=True, tensorflow=tf.__version__, python=sys.version.split()[0],
        global_optimizer_jit=tf.config.optimizer.get_jit(), all_functions_jit_compile=False,
        outcomes={name: sum(record["outcome"] == name for record in records)
                  for name in ["matches_analytic", "wrong_finite", "disconnected_or_nonfinite", "exception"]}, records=records)


if __name__ == "__main__":
    print(json.dumps(run(), allow_nan=False))
