# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent public-TF point/cotangent guard separation; no quantum SDK."""

import json

import tensorflow as tf


def candidate():
    source = tf.function(lambda x: x**3, input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False, jit_compile=False)
    first = tf.function(lambda x, c: 3*x*x*c, input_signature=[tf.TensorSpec((2,), tf.float64)]*2, autograph=False, jit_compile=False)
    @tf.custom_gradient
    def first_point(x):
        def refuse(incoming):
            raise RuntimeError("SECOND_POINT_FORBIDDEN")
        return tf.identity(x), refuse
    @tf.custom_gradient
    def function(x):
        y = source(x)
        return y, lambda cotangent: first(first_point(x), cotangent)
    return function


def run(mode):
    f = candidate()
    x, d = tf.constant([0.37, 0.82], tf.float64), tf.constant([0.4, -0.3], tf.float64)
    if mode == "jvp":
        with tf.autodiff.ForwardAccumulator(x, d) as fw:
            y = f(x)
        return fw.jvp(y)
    if mode == "gradient":
        with tf.GradientTape() as reverse:
            reverse.watch(x)
            y = tf.reduce_sum(f(x))
        return reverse.gradient(y, x)
    if mode == "for":
        with tf.autodiff.ForwardAccumulator(x, d) as fw:
            with tf.GradientTape() as reverse:
                reverse.watch(x)
                y = tf.reduce_sum(f(x))
            g = reverse.gradient(y, x)
        return fw.jvp(g)
    if mode == "rof":
        with tf.GradientTape() as reverse:
            reverse.watch(x)
            with tf.autodiff.ForwardAccumulator(x, d) as fw:
                y = tf.reduce_sum(f(x))
            projected = fw.jvp(y)
        return reverse.gradient(projected, x)
    with tf.GradientTape() as outer:
        outer.watch(x)
        with tf.GradientTape() as inner:
            inner.watch(x)
            y = tf.reduce_sum(f(x))
        g = inner.gradient(y, x)
        projected = tf.reduce_sum(g*d)
    return outer.gradient(projected, x)


def main():
    records = []
    for mode in ("gradient", "jvp", "for", "rof", "tape"):
        item = dict(mode=mode)
        try:
            value = run(mode)
            item.update(outcome="disconnected" if value is None else "returned", value=None if value is None else value.numpy().tolist())
        except Exception as error:
            item.update(outcome="refused", error=type(error).__name__+": "+str(error))
        records.append(item)
    print(json.dumps(dict(diagnostic_only=True, tensorflow=tf.__version__, tensorflow_origin=tf.__file__,
        analytic_gradient=[3*0.37**2, 3*0.82**2], analytic_jvp=[3*0.37**2*0.4, 3*0.82**2*-0.3], records=records)))


if __name__ == "__main__":
    main()
