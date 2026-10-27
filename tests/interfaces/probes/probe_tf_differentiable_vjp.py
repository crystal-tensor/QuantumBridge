# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Explicit VJP semantics probe; no quantum SDK imports or acceptance claim."""

import argparse
import json
import math
import sys
import traceback

import numpy as np
import tensorflow as tf


def jet(point, kind, library):
    if kind == "scalar":
        p = point[0]
        return [library.sin(p)], [[library.cos(p)]], [[[-library.sin(p)]]]
    p, q = point[0], point[1]
    sp, cp, sq, cq = library.sin(p), library.cos(p), library.sin(q), library.cos(q)
    value = [sp*cq+p*q]
    jacobian = [[cp*cq+q, -sp*sq+p]]
    hessian = [[[-sp*cq, 1-cp*sq], [1-cp*sq, -sp*cq]]]
    if kind == "multioutput":
        e, s, c = library.exp(0.2*p-q), library.sin(p*q), library.cos(p*q)
        value.append(e+s)
        jacobian.append([0.2*e+q*c, -e+p*c])
        hessian.append([[0.04*e-q*q*s, -0.2*e+c-p*q*s], [-0.2*e+c-p*q*s, e-p*p*s]])
    return value, jacobian, hessian


def tensor_jet(point, kind):
    y, j, h = jet(point, kind, tf)
    def stack(items):
        return tf.stack([tf.convert_to_tensor(item, dtype=point.dtype) for item in items])
    return stack(y), tf.stack([stack(row) for row in j]), tf.stack([tf.stack([stack(row) for row in plane]) for plane in h])


def host_model(kind):
    size, outputs = (1 if kind == "scalar" else 2), (2 if kind == "multioutput" else 1)
    def numeric_jet(point):
        return tuple(np.asarray(value, dtype=float) for value in jet(point, kind, np))
    def call(function, shape, *inputs):
        value = tf.numpy_function(function, inputs, tf.float64, stateful=False)
        value.set_shape(shape)
        return value
    def third(point, cotangent, direction, incoming):
        def refuse(x, u, v, a):
            if np.any(u) and np.any(v) and np.any(a):
                raise ValueError("Host third-point transpose guard evaluated; inputs="+json.dumps(
                    dict(point=x.tolist(), cotangent=u.tolist(), direction=v.tolist(), incoming=a.tolist())))
            return np.zeros_like(x)
        return call(refuse, (size,), point, cotangent, direction, incoming)

    @tf.custom_gradient
    def second(point, cotangent, direction):
        value = call(lambda x, u, v: np.einsum("i,ijk,k->j", u, numeric_jet(x)[2], v),
            (size,), point, cotangent, direction)
        def gradient(incoming):
            return third(point, cotangent, direction, incoming), bilinear(point, incoming, direction), second(point, cotangent, incoming)
        return value, gradient

    @tf.custom_gradient
    def bilinear(point, left, right):
        value = call(lambda x, a, d: np.einsum("j,ijk,k->i", a, numeric_jet(x)[2], d),
            (outputs,), point, left, right)
        def gradient(incoming):
            return third(point, incoming, right, left), second(point, incoming, right), second(point, incoming, left)
        return value, gradient

    @tf.custom_gradient
    def jvp(point, direction):
        value = call(lambda x, d: numeric_jet(x)[1] @ d, (outputs,), point, direction)
        def gradient(incoming):
            return second(point, incoming, direction), vjp(point, incoming)
        return value, gradient

    @tf.custom_gradient
    def vjp(point, cotangent):
        value = call(lambda x, u: numeric_jet(x)[1].T @ u, (size,), point, cotangent)
        def gradient(incoming):
            return second(point, cotangent, incoming), jvp(point, incoming)
        return value, gradient

    @tf.custom_gradient
    def primal(point):
        value = call(lambda x: numeric_jet(x)[0], (outputs,), point)
        return value, lambda cotangent: vjp(point, cotangent)
    return primal, vjp


def make_model(kind="multioutput", backend="analytic"):
    if backend == "callback":
        return host_model(kind)
    if backend != "analytic":
        raise ValueError("Unknown probe backend")
    # This primitive is defined outside the primal gradient closure. Its only
    # tensor dependencies are its explicit point and cotangent arguments.
    @tf.custom_gradient
    def vjp(point, cotangent):
        _, jacobian, _ = tensor_jet(point, kind)
        result = tf.linalg.matvec(jacobian, cotangent, transpose_a=True)
        def gradient(direction):
            _, j, h = tensor_jet(point, kind)
            return tf.einsum("i,ijk,k->j", cotangent, h, direction), tf.linalg.matvec(j, direction)
        return result, gradient

    @tf.custom_gradient
    def primal(point):
        value, _, _ = tensor_jet(point, kind)
        return value, lambda cotangent: vjp(point, cotangent)
    return primal, vjp


def reference(point, cotangent, direction, weight_direction, upstream):
    _, j, h = (np.asarray(value) for value in jet(point, "multioutput", math))
    weighted = np.einsum("i,ijk->jk", cotangent, h)
    hv, jw = weighted @ direction, j.T @ weight_direction
    gx, gu = weighted @ upstream, j @ upstream
    return dict(vjp=(j.T @ cotangent).tolist(), parameter_term=hv.tolist(), cotangent_term=jw.tolist(),
        variation=(hv+jw).tolist(), point_transpose=gx.tolist(), cotangent_transpose=gu.tolist(),
        duality=float(np.dot(upstream, hv+jw)-np.dot(direction, gx)-np.dot(weight_direction, gu)))


def vjp_case(vjp, point, cotangent, direction, weight_direction, upstream):
    with tf.GradientTape() as reverse:
        reverse.watch((point, cotangent))
        with tf.autodiff.ForwardAccumulator((point, cotangent), (direction, weight_direction)) as forward:
            value = vjp(point, cotangent)
        objective = tf.reduce_sum(upstream*value)
    gx, gu = reverse.gradient(objective, (point, cotangent))
    return value, forward.jvp(value), gx, gu


def check_semantics(point=(0.37, 0.82), cotangent=(0.7, -0.2), seed="both", traced=False, backend="analytic"):
    _, vjp = make_model(backend=backend)
    direction, weight_direction, upstream = np.array([0.4, -0.3]), np.array([0.2, -0.6]), np.array([-0.1, 0.6])
    if seed == "point":
        weight_direction *= 0
    elif seed == "cotangent":
        direction *= 0
    oracle = reference(point, cotangent, direction, weight_direction, upstream)
    def execute(x, u, v, w, z):
        return vjp_case(vjp, x, u, v, w, z)
    function = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    tensors = [tf.constant(value, tf.float64) for value in (point, cotangent, direction, weight_direction, upstream)]
    result = dict(expected=oracle, actual=None)
    try:
        actual = function(*tensors)
        result["actual"] = [None if value is None else np.asarray(value).tolist() for value in actual]
        for value, key in zip(actual, ("vjp", "variation", "point_transpose", "cotangent_transpose")):
            assert value is not None, "Explicit VJP lost "+key
            np.testing.assert_allclose(value, oracle[key], atol=1e-10, rtol=0)
        dual = np.dot(upstream, actual[1])-np.dot(direction, actual[2])-np.dot(weight_direction, actual[3])
        np.testing.assert_allclose(dual, 0., atol=1e-10, rtol=0)
    except Exception as error:
        error.probe_result = result
        raise
    result["tracing_count"] = function.experimental_get_tracing_count() if traced else 0
    return result


def loss_reference(kind, point, direction, weights, loss_kind):
    y, j, h = (np.asarray(value) for value in jet(point, kind, math))
    if loss_kind == "square":
        first, second = 2*(y-0.3), np.full_like(y, 2.)
    else:
        first, second = np.exp(y)+0.6*y*y, np.exp(y)+1.2*y
    hv = j.T @ (weights*second*(j @ direction))+np.einsum("i,ijk,k->j", weights*first, h, direction)
    return y, j.T @ (weights*first), hv


def check_loss(kind="multioutput", mode="rof", loss_kind="square", traced=False, backend="analytic"):
    primal, _ = make_model(kind, backend)
    point = np.array([0.37]) if kind == "scalar" else np.array([0.37, 0.82])
    direction = np.array([0.4]) if kind == "scalar" else np.array([0.4, -0.3])
    weights = np.array([0.7, -0.2]) if kind == "multioutput" else np.array([0.7])
    _, expected_gradient, expected_hvp = loss_reference(kind, point, direction, weights, loss_kind)
    def execute(x, d):
        def loss():
            y = primal(x)
            terms = (y-0.3)**2 if loss_kind == "square" else tf.exp(y)+0.2*y**3
            return tf.reduce_sum(tf.constant(weights, tf.float64)*terms)
        if mode == "for":
            with tf.autodiff.ForwardAccumulator(x, d) as forward:
                with tf.GradientTape() as reverse:
                    reverse.watch(x)
                    value = loss()
                gradient = reverse.gradient(value, x)
            return gradient, forward.jvp(gradient)
        if mode == "rof":
            with tf.GradientTape(persistent=True) as reverse:
                reverse.watch(x)
                with tf.autodiff.ForwardAccumulator(x, d) as forward:
                    value = loss()
                tangent = forward.jvp(value)
            return reverse.gradient(value, x), reverse.gradient(tangent, x)
        with tf.GradientTape() as outer:
            outer.watch(x)
            with tf.GradientTape() as inner:
                inner.watch(x)
                value = loss()
            gradient = inner.gradient(value, x)
            contraction = tf.reduce_sum(gradient*d)
        return gradient, outer.gradient(contraction, x)
    function = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    result = dict(expected_gradient=expected_gradient.tolist(), expected_hvp=expected_hvp.tolist(), actual=None)
    try:
        actual = function(tf.constant(point, tf.float64), tf.constant(direction, tf.float64))
        result["actual"] = [None if value is None else np.asarray(value).tolist() for value in actual]
        for value, oracle in zip(actual, (expected_gradient, expected_hvp)):
            assert value is not None, "Mixed AD lost a derivative"
            np.testing.assert_allclose(value, oracle, atol=1e-10, rtol=0)
    except Exception as error:
        error.probe_result = result
        raise
    result["tracing_count"] = function.experimental_get_tracing_count() if traced else 0
    return result


def run(backend="analytic"):
    records = []
    def record(description, function):
        item = dict(description)
        try:
            item.update(outcome="matches_analytic", result=function())
        except Exception as error:
            item.update(outcome="exception_or_mismatch", error=type(error).__name__+": "+str(error),
                result=getattr(error, "probe_result", None), traceback=traceback.format_exc())
        records.append(item)
    for traced in (False, True):
        for point in ((0.37, 0.82), (0.17, -0.42)):
            for seed in ("point", "cotangent", "both"):
                record(dict(family="semantics", point=point, seed=seed, traced=traced),
                    lambda: check_semantics(point=point, seed=seed, traced=traced, backend=backend))
        for cotangent in ((1., 0.), (0., 1.), (0.7, -0.2), (-0.4, 0.8)):
            record(dict(family="multioutput", cotangent=cotangent, traced=traced),
                lambda: check_semantics(cotangent=cotangent, traced=traced, backend=backend))
        for kind in ("scalar", "vector", "multioutput"):
            for mode in ("for", "rof", "tape_tape"):
                for loss_kind in ("square", "exponential_cubic"):
                    record(dict(family="mixed_ad", kind=kind, mode=mode, loss=loss_kind, traced=traced),
                        lambda: check_loss(kind=kind, mode=mode, loss_kind=loss_kind, traced=traced, backend=backend))
    if any(name.split(".")[0] in {"quantumbridge", "qiskit", "pennylane"} for name in sys.modules):
        raise AssertionError("Probe imported a quantum SDK")
    return dict(diagnostic_only=True, backend=backend, tensorflow=tf.__version__, python=sys.version.split()[0],
        jit_compile=False, global_jit=tf.config.optimizer.get_jit(), records=records,
        outcomes={name: sum(item["outcome"] == name for item in records)
                  for name in ("matches_analytic", "exception_or_mismatch")})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("analytic", "callback"), default="analytic")
    print(json.dumps(run(parser.parse_args().backend), allow_nan=False))
