# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Public-TF diagnostic; independent analytic references, no quantum SDK."""

import json

import numpy as np
import tensorflow as tf


def scalar_model(x):
    return x**3


def vector_model(x):
    return tf.stack([tf.cos(x[0])*tf.sin(x[1]), tf.exp(x[0]+x[1])])


def complex_model(x):
    z = tf.complex(x[0], x[1])
    phase = tf.exp(tf.complex(tf.constant(0., tf.float64), x[0]))
    return tf.stack([tf.math.real(tf.math.conj(z)*z), tf.math.real(z*phase)])


def analytic(model, point, direction, weights, loss_kind):
    if model == "scalar":
        y = point**3
        jacobian = (3*point**2).reshape(1, 1)
        hessians = (6*point).reshape(1, 1, 1)
    else:
        a, b = point
        if model == "vector":
            f, g = np.cos(a)*np.sin(b), np.exp(a+b)
            cross = -np.sin(a)*np.cos(b)
            y = np.array([f, g])
            jacobian = np.array([[-np.sin(a)*np.sin(b), np.cos(a)*np.cos(b)], [g, g]])
            hessians = np.array([[[-f, cross], [cross, -f]], [[g, g], [g, g]]])
        else:
            y = np.array([a*a+b*b, a*np.cos(a)-b*np.sin(a)])
            jacobian = np.array([[2*a, 2*b], [(1-b)*np.cos(a)-a*np.sin(a), -np.sin(a)]])
            hessians = np.array([[[2., 0.], [0., 2.]],
                [[-(2-b)*np.sin(a)-a*np.cos(a), -np.cos(a)], [-np.cos(a), 0.]]])
    if loss_kind == "square":
        first, second = 2*(y-0.3), np.full(y.shape, 2.)
    else:
        first, second = np.exp(y)+0.6*y*y, np.exp(y)+1.2*y
    return dict(value=y, jvp=jacobian @ direction, vjp=weights @ jacobian,
        gradient=jacobian.T @ (weights*first),
        hvp=jacobian.T @ (weights*second*(jacobian @ direction))
            +np.einsum("o,oij,j->i", weights*first, hessians, direction))


def evaluator(source, loss_kind, mode):
    def evaluate(point, direction, weights):
        def loss():
            y = source(point)
            terms = (y-0.3)**2 if loss_kind == "square" else tf.exp(y)+0.2*y**3
            return tf.reduce_sum(weights*terms)
        # Evaluate the mixed path first; no prior numeric AD warmup is used.
        if mode == "for":
            with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                with tf.GradientTape() as reverse:
                    reverse.watch(point)
                    value = loss()
                gradient = reverse.gradient(value, point)
            product = forward.jvp(gradient)
        elif mode == "rof":
            with tf.GradientTape() as reverse:
                reverse.watch(point)
                with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                    value = loss()
                projected = forward.jvp(value)
            product = reverse.gradient(projected, point) if projected is not None else None
            with tf.GradientTape() as first:
                first.watch(point)
                value = loss()
            gradient = first.gradient(value, point)
        else:
            with tf.GradientTape() as outer:
                outer.watch(point)
                with tf.GradientTape() as inner:
                    inner.watch(point)
                    value = loss()
                gradient = inner.gradient(value, point)
                projected = tf.reduce_sum(gradient*direction)
            product = outer.gradient(projected, point)
        with tf.GradientTape() as reverse:
            reverse.watch(point)
            with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                values = source(point)
        return dict(value=values, jvp=forward.jvp(values),
            vjp=reverse.gradient(values, point, output_gradients=weights), gradient=gradient, hvp=product)
    return evaluate


def inspect_graph(function):
    concrete = function.get_concrete_function()
    graph = concrete.graph.as_graph_def()
    return dict(trace_count=function.experimental_get_tracing_count(),
        root_calls=[dict(op=op.type, function=op.get_attr("f").name)
            for op in concrete.graph.get_operations() if op.type in {"PartitionedCall", "StatefulPartitionedCall"}],
        inner_model_function_defs=[f.signature.name for f in graph.library.function if "inner_model" in f.signature.name],
        function_def_count=len(graph.library.function), graph_bytes=graph.ByteSize())


def boundary(model, source, loss_kind, mode, strategy):
    width = 1 if model == "scalar" else 2
    signature = [tf.TensorSpec((width,), tf.float64)]*3
    inner = None
    record = dict(strategy=strategy, execution_resource_scope="OUT_OF_SCOPE; pure TensorFlow diagnostic", observations=[])
    if strategy == "cached_inner":
        def inner_model(x):
            return source(x)
        inner = tf.function(inner_model, input_signature=signature[:1], autograph=False, jit_compile=False)
        inner.get_concrete_function()
    evaluate = evaluator(inner if inner is not None else source, loss_kind, mode)
    function = evaluate if strategy == "eager_inline" else tf.function(evaluate, input_signature=signature, autograph=False, jit_compile=False)
    direction = np.array([0.4] if width == 1 else [0.4, -0.3])
    weights = np.array([0.7] if width == 1 else [0.7, -0.2])
    for raw_point in ([0.37] if width == 1 else [0.37, 0.82], [0.4] if width == 1 else [0.4, 0.91]):
        point = np.array(raw_point)
        expected = analytic(model, point, direction, weights, loss_kind)
        observation = dict(point=raw_point, expected={name: value.tolist() for name, value in expected.items()})
        try:
            with tf.device("/CPU:0"):
                result = function(tf.constant(point, tf.float64), tf.constant(direction, tf.float64), tf.constant(weights, tf.float64))
            actual = {name: None if value is None else value.numpy() for name, value in result.items()}
            observation["actual"] = {name: None if value is None else value.tolist() for name, value in actual.items()}
            disconnected = [name for name, value in actual.items() if value is None]
            mismatches = [name for name, value in actual.items() if value is not None and not np.allclose(value, expected[name], atol=2e-10, rtol=0)]
            observation.update(outcome="disconnected" if disconnected else "mismatch" if mismatches else "match",
                disconnected=disconnected, mismatches=mismatches)
        except Exception as error:
            observation.update(outcome="exception", error=type(error).__name__+": "+str(error))
        record["observations"].append(observation)
    if strategy != "eager_inline":
        try:
            record["graph"] = inspect_graph(function)
        except Exception as error:
            record["graph"] = dict(error=type(error).__name__+": "+str(error))
    if inner is not None:
        record["inner_trace_count"] = inner.experimental_get_tracing_count()
    return record


def main():
    cases = []
    for model, source in (("scalar", scalar_model), ("vector", vector_model), ("complex", complex_model)):
        for loss_kind in ("square", "exponential_cubic"):
            for mode in ("for", "rof", "tape"):
                item = dict(model=model, loss=loss_kind, mode=mode, boundaries=[])
                for strategy in ("cached_inner", "trace_inline", "eager_inline"):
                    item["boundaries"].append(boundary(model, source, loss_kind, mode, strategy))
                cases.append(item)
    inline = [r for c in cases for r in c["boundaries"] if r["strategy"] != "cached_inner"]
    passed = all(o["outcome"] == "match" for r in inline for o in r["observations"])
    inlined = all(r["graph"].get("trace_count") == 1 and r["graph"].get("inner_model_function_defs") == []
        for r in inline if r["strategy"] == "trace_inline")
    print(json.dumps(dict(diagnostic_only=True, reference="independent elementary analytic values, Jacobians and Hessian contractions",
        tensorflow=tf.__version__, tensorflow_origin=tf.__file__, inline_math_matches=passed,
        inline_graph_contract_passes=inlined, native_integration_accepted=False, cases=cases), allow_nan=False))


if __name__ == "__main__":
    main()
