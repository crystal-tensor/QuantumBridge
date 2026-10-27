# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent public-TF/NumPy callback Jacobian experiment; no quantum SDK."""

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import tensorflow as tf


def model(mode):
    def matrix(a):
        return np.array([-np.sin(a), np.cos(a)], dtype=np.float64)

    @tf.custom_gradient
    def first(a, cotangent):
        def native(x, c):
            return np.asarray(matrix(x) @ c, dtype=np.float64)
        if tf.executing_eagerly():
            value = tf.constant(native(a.numpy(), cotangent.numpy()), tf.float64)
        elif mode == "numpy_callback":
            value = tf.numpy_function(native, (a, cotangent), tf.float64)
        else:
            value = tf.py_function(first, (a, cotangent), tf.float64)
        value.set_shape(())
        def second(direction):
            def rule(x, c, d):
                return np.asarray((-np.cos(x)*c[0]-np.sin(x)*c[1])*d, dtype=np.float64), matrix(x)*d
            if tf.executing_eagerly():
                x, c = rule(a.numpy(), cotangent.numpy(), direction.numpy())
                return tf.constant(x, tf.float64), tf.constant(c, tf.float64)
            x, c = tf.numpy_function(rule, (a, cotangent, direction), (tf.float64, tf.float64))
            x.set_shape(())
            c.set_shape((2,))
            return x, c
        return value, second

    @tf.custom_gradient
    def forward(a):
        y = tf.constant([np.cos(a.numpy()), np.sin(a.numpy())], tf.float64)
        return y, lambda cotangent: first(a, cotangent)

    def execute(point):
        angle = point[0]**2+point[1]
        return tf.stack([tf.cos(angle), tf.sin(angle)]) if mode == "pure_tf" else forward(angle)
    return execute


def run(mode, point, pfor):
    x = tf.constant(point, tf.float64)
    angle, slope = point[0]**2+point[1], np.array([2*point[0], 1.])
    expected_j = np.array([-np.sin(angle)*slope, np.cos(angle)*slope])
    expected_h = np.array([-np.cos(angle)*np.outer(slope, slope)-np.sin(angle)*np.diag([2., 0.]),
        -np.sin(angle)*np.outer(slope, slope)+np.cos(angle)*np.diag([2., 0.])])
    record = dict(mode=mode, point=point, pfor=pfor, expected_jacobian=expected_j.tolist(), expected_hessians=expected_h.tolist())
    try:
        with tf.GradientTape(persistent=True) as outer:
            outer.watch(x)
            with tf.GradientTape(persistent=True) as inner:
                inner.watch(x)
                value = model(mode)(x)
            jacobian = inner.jacobian(value, x, experimental_use_pfor=pfor)
        record["jacobian"] = jacobian.numpy().tolist()
        hessian = outer.jacobian(jacobian, x, experimental_use_pfor=pfor)
        record.update(hessians=hessian.numpy().tolist(),
            outcome="match" if np.allclose(jacobian, expected_j, atol=1e-11, rtol=0) and np.allclose(hessian, expected_h, atol=1e-10, rtol=0) else "MISMATCH")
    except Exception as error:
        record.update(outcome="ERROR", error_type=type(error).__name__, error=str(error)[-2000:])
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    logging.getLogger("tensorflow").setLevel(logging.CRITICAL)
    records = [run(mode, point, pfor) for mode in ("pure_tf", "numpy_callback", "eager_callback")
        for point in ([0.37, 0.82], [0.41, 0.91]) for pfor in (False, True)]
    result = dict(diagnostic_only=True, tensorflow=tf.__version__, tensorflow_origin=tf.__file__, records=records,
        scope="Public TF custom gradients, numpy_function and py_function; no QB, SDK, private registry, stop_gradient or derivative injection")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(dict(diagnostic_only=True, tensorflow=tf.__version__,
        outcomes=[dict(mode=r["mode"], point=r["point"], pfor=r["pfor"], outcome=r["outcome"]) for r in records])))


if __name__ == "__main__":
    main()
