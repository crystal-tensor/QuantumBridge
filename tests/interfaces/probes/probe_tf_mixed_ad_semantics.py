# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Pure TensorFlow diagnostics, not a QuantumBridge acceptance test.

Prints every actual result, including wrong finite/disconnected outcomes.
No QuantumBridge, Qiskit or PennyLane import; no file writes or installations.
"""

import json
import math
import sys
import traceback

import numpy as np
import tensorflow as tf


def scalar(x):
    return tf.sin(x)


def vector(x):
    p, q = x[0], x[1]
    return tf.sin(p)*tf.cos(q)+p*q


@tf.custom_gradient
def custom_vector(x):
    p, q = x[0], x[1]
    value = tf.sin(p)*tf.cos(q)+p*q
    def vjp(dy):
        return dy*tf.stack([tf.cos(p)*tf.cos(q)+q, -tf.sin(p)*tf.sin(q)+p])
    return value, vjp


def reference(kind, point, direction):
    if kind == "scalar":
        value, gradient, hessian = math.sin(point), np.asarray(math.cos(point)), np.asarray(-math.sin(point))
    else:
        p, q = point
        value = math.sin(p)*math.cos(q)+p*q
        gradient = np.array([math.cos(p)*math.cos(q)+q, -math.sin(p)*math.sin(q)+p])
        diagonal = -math.sin(p)*math.cos(q)
        cross = 1-math.cos(p)*math.sin(q)
        hessian = np.array([[diagonal, cross], [cross, diagonal]])
    loss_gradient = 2*(value-0.3)*gradient
    loss_hessian = (2*gradient*gradient+2*(value-0.3)*hessian if kind == "scalar"
                    else 2*np.outer(gradient, gradient)+2*(value-0.3)*hessian)
    hvp = loss_hessian*direction if kind == "scalar" else loss_hessian @ direction
    return dict(primal=value, loss=(value-0.3)**2,
        jvp=float(np.sum(gradient*direction)), loss_jvp=float(np.sum(loss_gradient*direction)),
        gradient=loss_gradient.tolist(), hvp=np.asarray(hvp).tolist(), vjp=(0.7*gradient).tolist())


def experiment(function, mode, read_location, x, direction):
    if mode == "for":
        with tf.autodiff.ForwardAccumulator(x, direction) as forward:
            with tf.GradientTape() as reverse:
                reverse.watch(x)
                raw = function(x)
                loss = (raw-0.3)**2
                if read_location == "inside_tape":
                    raw_jvp, loss_jvp = forward.jvp(raw), forward.jvp(loss)
            gradient = reverse.gradient(loss, x)
            if read_location == "outside_tape":
                raw_jvp, loss_jvp = forward.jvp(raw), forward.jvp(loss)
        hvp = forward.jvp(gradient)
    elif mode == "rof":
        with tf.GradientTape(persistent=True) as reverse:
            reverse.watch(x)
            with tf.autodiff.ForwardAccumulator(x, direction) as forward:
                raw = function(x)
                loss = (raw-0.3)**2
            if read_location == "inside_tape":
                raw_jvp, loss_jvp = forward.jvp(raw), forward.jvp(loss)
        if read_location == "outside_tape":
            raw_jvp, loss_jvp = forward.jvp(raw), forward.jvp(loss)
        gradient = reverse.gradient(loss, x)
        hvp = None if loss_jvp is None else reverse.gradient(loss_jvp, x)
    else:
        with tf.GradientTape() as outer:
            outer.watch(x)
            with tf.GradientTape(persistent=True) as inner:
                inner.watch(x)
                raw = function(x)
                loss = (raw-0.3)**2
            gradient = inner.gradient(loss, x)
            raw_gradient = inner.gradient(raw, x)
            # This contraction must be recorded inside the outer Tape.
            contracted = tf.reduce_sum(gradient*direction)
        hvp = outer.gradient(contracted, x)
        raw_jvp = tf.reduce_sum(raw_gradient*direction)
        loss_jvp = tf.reduce_sum(gradient*direction)
    with tf.GradientTape() as reverse:
        reverse.watch(x)
        vjp_raw = function(x)
    vjp = reverse.gradient(vjp_raw, x, output_gradients=tf.constant(0.7, tf.float64))
    return raw, loss, raw_jvp, loss_jvp, gradient, hvp, vjp


def serial(value):
    if value is None:
        return None
    value = np.asarray(value)
    return value.tolist() if np.all(np.isfinite(value)) else None


def run():
    records = []
    for kind, function in [("scalar", scalar), ("vector", vector), ("custom_vector", custom_vector)]:
        point = 0.37 if kind == "scalar" else [0.37, 0.82]
        direction = 0.4 if kind == "scalar" else [0.4, -0.3]
        expected = reference(kind, point, direction)
        for inner_boundary in [False, True]:
            for traced in [False, True]:
                for mode in ["for", "rof", "tape_tape"]:
                    reads = ["inside_tape", "outside_tape"] if mode != "tape_tape" else ["not_applicable"]
                    for read_location in reads:
                        fn = tf.function(function, autograph=False) if inner_boundary else function
                        def evaluate(x, d):
                            return experiment(fn, mode, read_location, x, d)
                        evaluator = tf.function(evaluate, autograph=False) if traced else evaluate
                        record = dict(function=kind, inner_tf_function=inner_boundary,
                            outer_execution="traced" if traced else "eager", mode=mode,
                            loss_jvp_read_location=read_location, dtype="float64", expected=expected)
                        try:
                            values = evaluator(tf.constant(point, tf.float64), tf.constant(direction, tf.float64))
                            record["actual"] = dict(zip(expected, (serial(value) for value in values)))
                            errors = {}
                            for key, target in expected.items():
                                actual = record["actual"][key]
                                errors[key] = None if actual is None else float(np.max(np.abs(np.asarray(actual)-target)))
                            record["absolute_errors"] = errors
                            record["outcome"] = ("disconnected_or_nonfinite" if any(error is None for error in errors.values())
                                else "wrong_finite" if any(error > 1e-10 for error in errors.values()) else "matches_analytic")
                        except Exception as error:
                            record.update(outcome="exception", error=type(error).__name__+": "+str(error), traceback=traceback.format_exc())
                        records.append(record)
    forbidden = [name for name in sys.modules if name.split(".")[0] in {"quantumbridge", "qiskit", "pennylane"}]
    if forbidden:
        raise AssertionError("Pure TensorFlow probe imported a forbidden SDK")
    return dict(provenance="Pure TensorFlow public AD APIs; analytic Python/math oracle; no SDK import; diagnostic, not native acceptance.",
        tensorflow=tf.__version__, python=sys.version.split()[0],
        outcomes={name: sum(record["outcome"] == name for record in records)
                  for name in ["matches_analytic", "wrong_finite", "disconnected_or_nonfinite", "exception"]},
        records=records)


if __name__ == "__main__":
    print(json.dumps(run(), allow_nan=False))
