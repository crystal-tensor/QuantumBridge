# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Pure NumPy callback / public TF custom-gradient mixed-mode diagnostic."""

import json
import numpy as np
import tensorflow as tf

from probe_tf_mixed_ad_semantics import experiment, reference, serial


def derivatives(x):
    p, q = x
    y = np.sin(p)*np.cos(q)+p*q
    g = np.array([np.cos(p)*np.cos(q)+q, -np.sin(p)*np.sin(q)+p])
    z, w = -np.sin(p)*np.cos(q), 1-np.cos(p)*np.sin(q)
    return y, g, np.array([[z, w], [w, z]])


def callback(fn, shapes, *args):
    values = tf.numpy_function(fn, args, [tf.float64]*len(shapes), stateful=False)
    for value, shape in zip(values, shapes):
        value.set_shape(shape)
    return values


@tf.custom_gradient
def third(x, c, d, a):
    def refuse(point, cotangent, direction, incoming):
        if np.any(cotangent) and np.any(direction) and np.any(incoming):
            raise ValueError("third point derivative not available")
        return np.zeros_like(point)
    value, = callback(refuse, [(2,)], x, c, d, a)
    def gradient(unused):
        raise ValueError("fourth derivatives unavailable")
    return value, gradient


@tf.custom_gradient
def mixed(x, c, d):
    def run(point, cotangent, direction):
        _, g, h = derivatives(point)
        return cotangent*(h @ direction), np.asarray(g @ direction)
    first, second = callback(run, [(2,), ()], x, c, d)
    def gradient(a, b):
        a = tf.zeros_like(first) if a is None else a
        b = tf.zeros_like(second) if b is None else b
        hx = mixed(x, b, d)[0]
        hc = bilinear(x, a, d)
        hd = mixed(x, c, a)[0]+vjp(x, b)
        return third(x, c, d, a)+hx, hc, hd
    return (first, second), gradient


@tf.custom_gradient
def bilinear(x, a, d):
    def run(point, first, second):
        return np.asarray(first @ derivatives(point)[2] @ second)
    value, = callback(run, [()], x, a, d)
    def gradient(c):
        return third(x, c, d, a), mixed(x, c, d)[0], mixed(x, c, a)[0]
    return value, gradient


@tf.custom_gradient
def vjp(x, c):
    value, = callback(lambda point, cotangent: derivatives(point)[1]*cotangent, [(2,)], x, c)
    def gradient(d):
        return mixed(x, c, d)
    return value, gradient


@tf.custom_gradient
def function(x):
    value, = callback(lambda point: np.asarray(derivatives(point)[0]), [()], x)
    def gradient(c):
        return vjp(x, c)
    return value, gradient


def run():
    records = []
    expected = reference("vector", [0.37, 0.82], [0.4, -0.3])
    for inner in [False, True]:
        for traced in [False, True]:
            for mode in ["for", "rof", "tape_tape"]:
                fn = tf.function(function, autograph=False) if inner else function
                def evaluate(x, direction):
                    return experiment(fn, mode, "inside_tape", x, direction)
                evaluator = tf.function(evaluate, autograph=False) if traced else evaluate
                record = dict(inner_tf_function=inner, outer_traced=traced, mode=mode)
                try:
                    values = evaluator(tf.constant([0.37, 0.82], tf.float64), tf.constant([0.4, -0.3], tf.float64))
                    actual = dict(zip(expected, (serial(value) for value in values)))
                    errors = {k: None if actual[k] is None else float(np.max(np.abs(np.asarray(actual[k])-expected[k]))) for k in expected}
                    record.update(actual=actual, errors=errors)
                except Exception as error:
                    record.update(error=type(error).__name__+": "+str(error))
                records.append(record)
    return dict(tensorflow=tf.__version__, expected=expected, records=records)


if __name__ == "__main__":
    print(json.dumps(run()))
