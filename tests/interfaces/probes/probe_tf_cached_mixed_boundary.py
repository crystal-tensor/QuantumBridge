# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Diagnostic only: isolate cached function boundaries from ledger rules."""

import json

import numpy as np
import tensorflow as tf


def real_model(x):
    return tf.stack([tf.cos(x[0])*tf.sin(x[1]), tf.exp(x[0]+x[1])])


def complex_model(x):
    z = tf.complex(x[0], x[1])
    a = tf.exp(tf.complex(tf.constant(0., tf.float64), x[0]))
    return tf.stack([tf.math.real(tf.math.conj(z)*z), tf.math.real(z*a)])


def cube_model(x):
    return x**3


def evaluate(function, mode, x, direction, loss_kind="square"):
    def loss():
        values = tf.reshape(function(x), (-1,))
        return tf.reduce_sum((values-0.3)**2 if loss_kind == "square" else values)
    if mode == "tape":
        with tf.GradientTape() as outer:
            outer.watch(x)
            with tf.GradientTape() as inner:
                inner.watch(x)
                value = loss()
            first = inner.gradient(value, x)
            projected = tf.reduce_sum(first*direction)
        return outer.gradient(projected, x)
    if mode == "for":
        with tf.autodiff.ForwardAccumulator(x, direction) as forward:
            with tf.GradientTape() as reverse:
                reverse.watch(x)
                value = loss()
            first = reverse.gradient(value, x)
        return forward.jvp(first)
    with tf.GradientTape() as reverse:
        reverse.watch(x)
        with tf.autodiff.ForwardAccumulator(x, direction) as forward:
            value = loss()
        projected = forward.jvp(value)
    return reverse.gradient(projected, x)


def main():
    x, direction = tf.constant([0.37, 0.82], tf.float64), tf.constant([0.4, -0.3], tf.float64)
    records = []
    for name, source, loss_kind in (("real", real_model, "square"), ("complex", complex_model, "square"),
            ("cube", cube_model, "square"), ("cube", cube_model, "linear")):
        if name == "cube":
            point, vector = np.array([0.37, 0.82]), np.array([0.4, -0.3])
            expected = (30*point**4-3.6*point)*vector if loss_kind == "square" else 6*point*vector
            reference = "elementary closed-form derivative, no TensorFlow differentiation"
        else:
            expected = evaluate(source, "tape", x, direction).numpy()
            reference = "inline TensorFlow TapeTape cross-check, not an independent mathematical oracle"
        for mode in ("tape", "for", "rof"):
            function = tf.function(source, input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False, jit_compile=False)
            function.get_concrete_function()
            item = dict(case=name, mode=mode, loss=loss_kind, reference=reference, expected=expected.tolist())
            try:
                result = evaluate(function, mode, x, direction, loss_kind)
                if result is None:
                    item.update(outcome="disconnected")
                else:
                    value = result.numpy()
                    item.update(outcome="match" if np.allclose(value, expected, atol=2e-10, rtol=0) else "mismatch", actual=value.tolist())
            except Exception as error:
                item.update(outcome="exception", error=type(error).__name__+": "+str(error))
            records.append(item)
    print(json.dumps(dict(diagnostic_only=True, tensorflow=tf.__version__, tensorflow_origin=tf.__file__, records=records), allow_nan=False))


if __name__ == "__main__":
    main()
