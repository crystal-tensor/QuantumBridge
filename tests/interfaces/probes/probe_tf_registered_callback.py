# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Pure public TF gradient registration on NumPy callbacks (diagnostic only)."""

import json
import numpy as np
import tensorflow as tf

from probe_tf_callback_mixed import derivatives
from probe_tf_mixed_ad_semantics import experiment, reference, serial


SHAPES = [[()], [(2,)], [(2,), ()], [()], [(2,)]]
CALLS = {}


def evaluate(order, *inputs):
    def callback(*values):
        x, *args = values
        y, g, h = derivatives(x)
        if order == 0:
            return np.asarray(y)
        if order == 1:
            return args[0]*g
        if order == 2:
            c, d = args
            return c*(h @ d), np.asarray(g @ d)
        if order == 3:
            a, d = args
            return np.asarray(a @ h @ d)
        c, d, a = args
        if np.any(c) and np.any(d) and np.any(a):
            raise ValueError("third point derivative not available")
        return np.zeros_like(x)
    graph = tf.compat.v1.get_default_graph()
    with graph.gradient_override_map({"PyFuncStateless": "QBProbeRegisteredCallback"}):
        outputs = tf.numpy_function(callback, inputs, [tf.float64]*len(SHAPES[order]), stateful=False)
    for value, shape in zip(outputs, SHAPES[order]):
        value.set_shape(shape)
    CALLS[outputs[0].op.get_attr("token")] = order
    return outputs


@tf.RegisterGradient("QBProbeRegisteredCallback")
def gradient(operation, *cotangents):
    order = CALLS[operation.get_attr("token")]
    x, *args = operation.inputs
    if order == 0:
        return evaluate(1, x, cotangents[0])
    if order == 1:
        return evaluate(2, x, args[0], cotangents[0])
    if order == 2:
        c, d = args
        a = tf.zeros_like(x) if cotangents[0] is None else cotangents[0]
        b = tf.constant(0., tf.float64) if cotangents[1] is None else cotangents[1]
        hx = evaluate(4, x, c, d, a)[0]+evaluate(2, x, b, d)[0]
        hc = evaluate(3, x, a, d)[0]
        hd = evaluate(2, x, c, a)[0]+evaluate(1, x, b)[0]
        return hx, hc, hd
    if order == 3:
        a, d = args
        c = cotangents[0]
        return evaluate(4, x, c, d, a)[0], evaluate(2, x, c, d)[0], evaluate(2, x, c, a)[0]
    raise ValueError("fourth derivative not available")


def function(x):
    return evaluate(0, x)[0]


def run():
    records = []
    expected = reference("vector", [0.37, 0.82], [0.4, -0.3])
    for inner in [False, True]:
        for mode in ["for", "rof", "tape_tape"]:
            fn = tf.function(function, autograph=False) if inner else function
            def execute(x, direction):
                return experiment(fn, mode, "inside_tape", x, direction)
            evaluator = tf.function(execute, autograph=False)
            record = dict(inner_tf_function=inner, mode=mode)
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
