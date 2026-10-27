# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Public callback-free TF scalar/complex pfor controls, no quantum SDK."""

import argparse
import json
from pathlib import Path

import numpy as np
import tensorflow as tf


def values(point, complex_model, scalar_model=False):
    angle = point[0]**2+point[1]
    if scalar_model:
        return tf.reshape(angle, (1,))
    if not complex_model:
        return tf.stack([tf.cos(angle), tf.sin(angle)])
    c, s = tf.cast(tf.cos(angle/2), tf.complex128), tf.cast(tf.sin(angle/2), tf.complex128)
    rotation = tf.stack([tf.stack([c, -s]), tf.stack([s, c])])
    state = tf.linalg.matvec(rotation, tf.constant([1., 0.], tf.complex128))
    return tf.stack([tf.math.real(tf.math.conj(state[0])*state[0]-tf.math.conj(state[1])*state[1]),
        2*tf.math.real(tf.math.conj(state[0])*state[1])])


def run(complex_model, traced, mode, point, scalar_model=False):
    direction = tf.constant([0.4, -0.3], tf.float64)
    def execute(x):
        if mode == "jacobian_hessian":
            with tf.GradientTape(persistent=True) as outer:
                outer.watch(x)
                with tf.GradientTape() as inner:
                    inner.watch(x)
                    y = values(x, complex_model, scalar_model)
                jacobian = inner.jacobian(y, x, experimental_use_pfor=True)
            return y, jacobian, outer.jacobian(jacobian, x, experimental_use_pfor=True)
        if mode == "for":
            with tf.autodiff.ForwardAccumulator(x, direction) as forward:
                with tf.GradientTape() as reverse:
                    reverse.watch(x)
                    y = tf.reduce_sum(tf.exp(values(x, complex_model, scalar_model)))
                gradient = reverse.gradient(y, x)
            return forward.jvp(gradient)
        with tf.GradientTape() as reverse:
            reverse.watch(x)
            with tf.autodiff.ForwardAccumulator(x, direction) as forward:
                y = tf.reduce_sum(tf.exp(values(x, complex_model, scalar_model)))
            tangent = forward.jvp(y)
        return reverse.gradient(tangent, x)
    function = tf.function(execute, input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False) if traced else execute
    a, slope = point[0]**2+point[1], np.array([2*point[0], 1.])
    y = np.array([np.cos(a), np.sin(a)])
    j = np.array([-np.sin(a)*slope, np.cos(a)*slope])
    h = np.array([-np.cos(a)*np.outer(slope, slope)-np.sin(a)*np.diag([2., 0.]),
        -np.sin(a)*np.outer(slope, slope)+np.cos(a)*np.diag([2., 0.])])
    if scalar_model:
        y, j, h = np.array([a]), slope[None, :], np.diag([2., 0.])[None, :, :]
    expected = (y, j, h) if mode == "jacobian_hessian" else j.T @ (np.exp(y)*(j @ [0.4, -0.3]))+np.einsum("o,oij,j->i", np.exp(y), h, [0.4, -0.3])
    actual = function(tf.constant(point, tf.float64))
    for result, oracle in zip(tf.nest.flatten(actual), tf.nest.flatten(expected)):
        np.testing.assert_allclose(result, oracle, atol=2e-10, rtol=0)
    graph = tf.function(execute, input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False).get_concrete_function().graph.as_graph_def()
    nodes = list(graph.node)+[node for f in graph.library.function for node in f.node_def]
    assert not any(node.op in {"PyFunc", "EagerPyFunc", "PyFuncStateless"} for node in nodes)
    return dict(complex_model=complex_model, scalar_model=scalar_model, traced=traced, mode=mode, point=point,
        outcome="match", top_level_nodes=len(graph.node), function_definitions=len(graph.library.function), callback_ops=[])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = [run(c, traced, mode, point) for c in (False, True) for traced in (False, True)
        for mode in ("jacobian_hessian", "for", "rof") for point in ([0.37, 0.82], [0.41, 0.91])]
    records += [run(False, traced, mode, point, scalar_model=True) for traced in (False, True)
        for mode in ("jacobian_hessian", "for", "rof") for point in ([0.37, 0.82], [0.41, 0.91])]
    result = dict(tensorflow=tf.__version__, tensorflow_origin=tf.__file__, assertions_completed=True, records=records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(dict(assertions_completed=True, scenarios=len(records), callback_ops=[])))


if __name__ == "__main__":
    main()
