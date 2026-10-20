# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native numeric result leaves and bounded first-order postprocessing rules."""

from dataclasses import replace

import numpy as np

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.qml.pauli_group import PauliGroupResult
from .trace import Dual, flatten_tree, unflatten_tree


def result_payload(value):
    if isinstance(value, PauliGroupResult):
        return value.means
    if isinstance(value, dict):
        return {key: result_payload(child) for key, child in value.items()}
    if isinstance(value, (tuple, list)):
        children = [result_payload(child) for child in value]
        return tuple(children) if isinstance(value, tuple) else children
    return value


def with_payload(template, payload):
    if isinstance(template, PauliGroupResult):
        return replace(template, means=payload)
    if isinstance(template, dict):
        return {key: with_payload(child, payload[key]) for key, child in template.items()}
    if isinstance(template, (tuple, list)):
        children = [with_payload(child, value) for child, value in zip(template, payload)]
        return tuple(children) if isinstance(template, tuple) else children
    return payload


def _traced_output(value, width):
    primals, derivatives = [], []
    def walk(item):
        if isinstance(item, dict):
            return ("dict", tuple((key, walk(child)) for key, child in item.items()))
        if isinstance(item, (tuple, list)):
            return ("tuple" if isinstance(item, tuple) else "list", tuple(walk(child) for child in item))
        array = np.asarray(item, dtype=object)
        start = len(primals)
        for scalar in array.flat:
            if isinstance(scalar, Dual):
                primals.append(scalar.value)
                derivatives.append(scalar.derivative)
            else:
                if not np.isscalar(scalar) or np.iscomplexobj(scalar):
                    raise UnsupportedFeature("postprocessing_output", "Native postprocessing derivatives need real numeric result leaves.")
                primals.append(float(scalar))
                derivatives.append(np.zeros(width))
        return ("leaf", array.shape, start, array.size)
    spec = walk(value)
    return np.asarray(primals), np.asarray(derivatives).reshape(len(primals), width), spec


def processing_jacobian(prepared, results, parameter_values, *, max_entries=2000000):
    """Trace only quantum means and declared classical slots, never metadata.

    Chunked tangent seeds bound working storage without forming an input-sized
    identity matrix. Reconstruction follows the actual reverse stage order.
    """
    payload = result_payload(results)
    raw, raw_spec = flatten_tree(payload)
    keys = tuple(parameter_values)
    sizes = [len(parameter_values[key]) for key in keys]
    values = np.concatenate([raw] + [np.asarray(parameter_values[key], dtype=float) for key in keys])
    base = prepared.processing_fn(results, parameter_values=parameter_values)
    flat, spec = flatten_tree(base)
    if len(flat) * max(1, len(values)) > max_entries:
        raise MemoryError("Native postprocessing Jacobian exceeds its output budget.")
    matrix = np.zeros((len(flat), len(values)))
    for start in range(0, len(values), 16):
        stop = min(start + 16, len(values))
        width = stop - start
        if len(values) * width > max_entries:
            raise MemoryError("Native postprocessing tangent work exceeds its budget.")
        traced = np.empty(len(values), dtype=object)
        for index, value in enumerate(values):
            derivative = np.zeros(width)
            if start <= index < stop:
                derivative[index-start] = 1.
            traced[index] = Dual(value, derivative)
        traced_results = with_payload(results, unflatten_tree(traced[:len(raw)], raw_spec))
        traced_parameters, offset = {}, len(raw)
        for key, size in zip(keys, sizes):
            traced_parameters[key] = traced[offset:offset+size]
            offset += size
        output = prepared.processing_fn(traced_results, parameter_values=traced_parameters, differentiating=True)
        primal, derivative, traced_spec = _traced_output(output, width)
        if traced_spec != spec or not np.allclose(primal, flat, atol=1e-12, rtol=0):
            raise UnsupportedFeature("postprocessing_trace", "Postprocessing tracing changed the actual forward result or structure.")
        if not np.all(np.isfinite(derivative)):
            raise ValueError("Postprocessing produced a nonfinite derivative.")
        matrix[:,start:stop] = derivative
    return base, matrix, spec, len(raw)
