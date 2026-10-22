# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Keep valid forwards while explicitly rejecting singular symbolic derivatives."""

from quantumbridge.core.classical import UnsupportedFeature
from threading import RLock


_tf_registered = set()
_tf_guard_registered = set()
_tf_registration_lock = RLock()


def _assert_domain(value, name):
    bad = value == 0 if name in {"abs", "sign"} else abs(value) >= 1
    if bad:
        raise UnsupportedFeature("symbolic_nondifferentiable_domain",
                                 "Symbolic derivative is nondifferentiable at zero or an inverse-trigonometric boundary.")


def _factor(value, name, numeric):
    if name == "abs": return numeric.sign(value)
    if name == "sign": return value*0
    factor = 1/numeric.sqrt(1-value*value)
    return -factor if name == "arccos" else factor


def _tensorflow_guard(value, source, name, tf):
    valid = tf.not_equal(source, 0) if name in {"abs", "sign"} else tf.less(tf.abs(source), 1)
    assertion = tf.debugging.assert_equal(valid, True,
        message="Symbolic derivative is nondifferentiable at zero or an inverse-trigonometric boundary.")
    with tf.control_dependencies([] if assertion is None else [assertion]):
        if tf.executing_eagerly(): return tf.identity(value)
        rule_name = "QuantumBridgeSymbolicGuard"+name
        with _tf_registration_lock:
            if name not in _tf_guard_registered:
                # Carry the assertion through subsequent derivatives as a
                # real input edge, including mathematically zero derivatives.
                def rule(op, *cotangents, _name=name):
                    return [_tensorflow_guard(tf.zeros_like(item) if gradient is None else gradient,
                                              op.inputs[1], _name, tf)
                            for item, gradient in zip(op.inputs, cotangents)]
                tf.RegisterGradient(rule_name)(rule)
                _tf_guard_registered.add(name)
        with tf.compat.v1.get_default_graph().gradient_override_map({"IdentityN": rule_name}):
            return tf.raw_ops.IdentityN(input=[value, source])[0]


def _tensorflow_derivative(source, cotangent, name, tf):
    return _tensorflow_guard(cotangent*_factor(source, name, tf.math), source, name, tf)


def guarded_symbolic_unary(value, name, numeric, module):
    alias = name if module.startswith(("autograd", "jax", "jaxlib")) else {"arcsin": "asin", "arccos": "acos"}.get(name, name)
    function = getattr(numeric, alias)
    if module.startswith("torch"):
        class Guarded(numeric.autograd.Function):
            @staticmethod
            def forward(ctx, source):
                ctx.save_for_backward(source)
                return function(source)

            @staticmethod
            def backward(ctx, cotangent):
                source, = ctx.saved_tensors
                _assert_domain(source.detach().item(), name)
                return cotangent*_factor(source, name, numeric)
        return Guarded.apply(value)
    if module.startswith("autograd"):
        from autograd.tracer import getval
        _assert_domain(float(getval(value)), name)
        return function(value)
    if module.startswith("tensorflow"):
        import tensorflow as tf
        if not tf.executing_eagerly():
            operation = {"abs": "Abs", "sign": "Sign", "arcsin": "Asin", "arccos": "Acos"}[name]
            rule_name = "QuantumBridgeSymbolicDomain"+operation
            with _tf_registration_lock:
                if name not in _tf_registered:
                    # Only literal operation names live in the process-wide
                    # registry; inputs/graphs are read from each operation.
                    def rule(op, cotangent, _name=name):
                        return _tensorflow_derivative(op.inputs[0], cotangent, _name, tf)
                    tf.RegisterGradient(rule_name)(rule)
                    _tf_registered.add(name)
            @tf.function(autograph=False)
            def graph_call(source):
                with tf.compat.v1.get_default_graph().gradient_override_map({operation: rule_name}):
                    return function(source)
            return graph_call(value)
        @tf.custom_gradient
        def guarded(source):
            def gradient(cotangent):
                return _tensorflow_derivative(source, cotangent, name, tf)
            return function(source), gradient
        return guarded(value)
    import jax
    @jax.custom_jvp
    def guarded(source): return function(source)
    @guarded.defjvp
    def derivative(primals, tangents):
        source, = primals
        tangent, = tangents
        jax.debug.callback(lambda x: _assert_domain(float(x), name), source, ordered=True)
        return guarded(source), tangent*_factor(source, name, numeric)
    return guarded(value)
