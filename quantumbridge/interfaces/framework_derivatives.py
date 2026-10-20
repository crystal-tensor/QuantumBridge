# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native execution of classical source maps supplied by optional frameworks."""

import numpy as np

from quantumbridge.execution import DerivativeExecutionRequest
from quantumbridge.execution.device_derivatives import execute_device_derivatives
from quantumbridge.execution.derivative_planning import finish_derivative
from quantumbridge.execution.resource_context import current_resources
from quantumbridge.diff.trace import flatten_tree


def execute_mapped_derivative(kernel, raw, packed, classical, second_map, direction, *,
                              kind, input_shape, method, limits, cotangent=None):
    """The framework supplies only classical maps; quantum work stays native."""
    order = 2 if kind in {"hvp", "hessian"} else 0 if kind == "value" else 1
    size = int(np.prod(input_shape))
    request = DerivativeExecutionRequest(kernel.source, (), derivative_order=order,
        derivative_kind=kind, method=method, tangent=None if kind != "hvp" else direction,
        cotangent=cotangent, limits=limits)
    def prepare(device, request):
        if method == "second_adjoint" and order != 2:
            raise ValueError("second_adjoint requires derivative order two.")
        for array in (raw, packed, classical, second_map, direction):
            if np.asarray(array).dtype.kind not in "fiu" or not np.all(np.isfinite(array)):
                raise ValueError("Derivative source maps must be finite and real.")
        if np.shape(raw) != (size,) or np.shape(packed) != (kernel.size,) or np.shape(classical) != (kernel.size, size):
            raise ValueError("Framework source map shape changed after tracing.")
        if kind == "vjp":
            cot, spec = flatten_tree(cotangent)
            if spec != kernel.spec or not np.all(np.isfinite(cot)):
                raise ValueError("Derivative cotangent must match the native output.")
        packed_direction = classical @ direction if kind == "hvp" else None
        plan = kernel.plan(packed, derivative=max(1, order), direction=packed_direction)
        own = plan.recorder.classical_jacobian(kernel.size)
        mapped = own @ classical
        scope = current_resources()
        scope.retain("framework_source_maps", mapped.nbytes+second_map.nbytes)
        scope.ledger.unavailable("framework_allocator_memory", "Classical framework graphs and allocator-owned source maps are outside the native owned-array account.")
        mapped_second = None
        if order == 2:
            expected = (kernel.size, size, 1 if kind == "hvp" else size)
            if np.shape(second_map) != expected:
                raise ValueError("Framework second source map has an invalid shape.")
            internal = plan.recorder.classical_second(kernel.size, 1 if kind == "hvp" else kernel.size)
            mapped_second = (np.einsum("rpk,pn->rnk", internal, classical) if kind == "hvp"
                else np.einsum("rpq,pn,qm->rnm", internal, classical, classical))
            mapped_second += np.einsum("rp,pnk->rnk", own, second_map)
        return finish_derivative(request, plan.node, plan, plan.recorder.native_values(), mapped,
            mapped_second, direction if kind == "hvp" else None, size,
            [(input_shape, slice(0, size))], True, kernel.spec, kernel.output_size)
    return execute_device_derivatives(kernel.node.device, request, return_status=True, _prepare=prepare)
