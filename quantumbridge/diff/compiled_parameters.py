# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Preserve the classical graph when compilation splits or merges gate angles.

import operator
from dataclasses import replace

from quantumbridge.core import Parameter, ParameterExpression
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
        return binary[value.op](*(evaluate(arg) for arg in value.args))
    def angle(value):
        return recorder(evaluate(value)) if isinstance(value, (Parameter, ParameterExpression)) else value
    def walk(body):
        out = body.copy()
        out.global_phase = angle(body.global_phase)
        out.operations = [map_control_bodies(op, walk) if op.metadata.get("control_node") is not None
                          else replace(op, params=tuple(angle(value) for value in op.params)) for op in body.operations]
        return out
    return walk(circuit), recorder
