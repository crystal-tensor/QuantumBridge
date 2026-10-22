# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Preserve the classical graph when compilation splits or merges gate angles.

import operator
from numbers import Complex
from dataclasses import replace

from quantumbridge.core import Parameter, ParameterExpression
from quantumbridge.core.parameters import UNARY_FUNCTIONS, _evaluate_unary
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.compiler.traversal import map_control_bodies


def record_compiled_parameters(circuit, original_recorder):
    from .qnode_engine import AngleRecorder
    recorder = AngleRecorder()
    values = dict(zip(original_recorder.parameters, original_recorder.angles))
    binary = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv, "**": operator.pow}
    def evaluate(value):
        if isinstance(value, Parameter):
            if value not in values: raise UnsupportedFeature("compiled_loop_parameter", "Compiled QNode gradients require bound loop parameters.")
            return values[value]
        if not isinstance(value, ParameterExpression): return value
        if value.op == "const": return value.args[0]
        if value.op == "parameter": return evaluate(value.args[0])
        if value.op == "neg": return -evaluate(value.args[0])
        if value.op in UNARY_FUNCTIONS | {"abs_gradient", "sign_gradient"}:
            return _unary(value.op, evaluate(value.args[0]))
        return binary[value.op](*(evaluate(arg) for arg in value.args))
    def angle(value):
        return recorder(evaluate(value)) if isinstance(value, (Parameter, ParameterExpression)) else value
    def walk(body):
        out = body.copy()
        phase = angle(body.global_phase)
        out.operations = [map_control_bodies(op, walk) if op.metadata.get("control_node") is not None
                          else replace(op, params=tuple(angle(value) for value in op.params)) for op in body.operations]
        # Replace old gate identities before validating the new phase namespace.
        out.global_phase = phase
        return out
    return walk(circuit), recorder


def _unary(name, value):
    if isinstance(value, Complex): return _evaluate_unary(name, value)
    from .trace import Dual
    if isinstance(value, Dual):
        if name == "abs_gradient": return value.sign()
        if name == "sign_gradient": return value.sign()*0
        return abs(value) if name == "abs" else getattr(value, name)()
    module = type(value).__module__
    if module.startswith("torch"):
        import torch as numeric
    elif module.startswith("autograd"):
        import autograd.numpy as numeric
    elif module.startswith(("jax", "jaxlib")):
        import jax.numpy as numeric
    elif module.startswith("tensorflow"):
        import tensorflow.math as numeric
    else:
        raise UnsupportedFeature("symbolic_scalar_interface", "Symbolic function needs a supported scalar/trace interface.")
    if name in {"abs_gradient", "sign_gradient"}:
        raise UnsupportedFeature("symbolic_nonsmooth_interface", "Guarded nonsmooth symbolic derivatives require the native real trace.")
    if name in {"abs", "sign", "arcsin", "arccos"}:
        from quantumbridge.interfaces.symbolic_math import guarded_symbolic_unary
        return guarded_symbolic_unary(value, name, numeric, module)
    alias = {"conjugate": "conj", "arcsin": "asin", "arccos": "acos", "arctan": "atan"}
    if module.startswith(("autograd", "jax", "jaxlib")): alias = {"conjugate": "conj"}
    return getattr(numeric, alias.get(name, name))(value)
