# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Framework graphs use the same native quantum Jacobian, not an SDK oracle.

import numpy as np

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.diff.trace import flatten_tree, unflatten_tree


def _leaves(value):
    if isinstance(value, dict): return sum((_leaves(item) for item in value.values()), [])
    if isinstance(value, (tuple, list)): return sum((_leaves(item) for item in value), [])
    return [value]


def infer_interface(args, kwargs):
    modules = [type(value).__module__ for value in _leaves((args, kwargs))]
    if any(module.startswith("torch") for module in modules): return "torch"
    if any(module.startswith("autograd") for module in modules): return "autograd"
    if any(module.startswith(("jax", "jaxlib")) for module in modules): return "jax"
    if any(module.startswith("tensorflow") for module in modules): return "tf"
    return None


def execute_interface(plan, interface):
    if interface == "torch": return _torch_execute(plan)
    if interface == "autograd": return _autograd_execute(plan)
    raise UnsupportedFeature("qnode_interface", f"Native {interface} autodiff is not implemented/verified; do not treat array conversion as autodiff.")


def _framework_point(plan, indices):
    """Freeze numeric source constants, retaining only actual framework scalars."""
    from quantumbridge.diff.scalars import scalar_primal
    fixed = np.asarray([scalar_primal(angle) for angle in plan.recorder.angles])
    def unpack(values):
        point = fixed.copy()
        point[indices] = values
        return point
    def second(values, direction=None):
        from quantumbridge.diff.higher_order_limits import resolve_higher_order_limits
        limits = resolve_higher_order_limits(plan.node.higher_order_limits)
        limits.check("max_input_parameters", len(indices))
        columns = len(indices) if direction is None else 1
        limits.check("max_memory_bytes", 8*len(fixed)*len(indices)*(1+columns))
        classical = np.zeros((len(fixed), len(indices)))
        classical[indices, np.arange(len(indices))] = 1.
        return plan.second_derivatives(unpack(values), direction=direction, classical=classical, limits=limits)
    return unpack, second


def _torch_execute(plan):
    try: import torch
    except ImportError as exc: raise ImportError("QuantumBridge Torch QNode requires optional torch.") from exc
    angles = plan.recorder.angles
    inputs = [value for value in _leaves(plan.input_values) if isinstance(value, torch.Tensor)]
    tensors = [value for value in angles if isinstance(value, torch.Tensor)]
    if any(value.device.type != "cpu" for value in tensors + inputs): raise UnsupportedFeature("torch_device", "Native QNode Torch execution currently supports CPU tensors only.")
    if any(value.ndim != 0 or not value.is_floating_point() for value in tensors): raise TypeError("Quantum gate angles must be real floating-point scalar tensors.")
    dtype = tensors[0].dtype if tensors else torch.float64
    if any(value.dtype != dtype for value in tensors): raise TypeError("QuantumBridge gate tensors must use one floating dtype.")
    indices = [index for index, value in enumerate(angles) if isinstance(value, torch.Tensor) and value.requires_grad]
    from .ordinary_resources import managed_framework_plan
    plan = managed_framework_plan(plan)
    unpack, second_derivatives = _framework_point(plan, indices)
    packed = torch.stack([angles[index] for index in indices]) if indices else torch.empty(0, dtype=dtype)
    for value in inputs:
        if value.requires_grad: packed = packed + 0 * value.sum()

    def publish(second=False):
        plan.node.last_metadata = {**plan.metadata, "interface": "torch", "native_vjp": True,
                                  "native_second_order": second, "classical_chain_rule": "Torch graph"}

    class NativeSecondVJP(torch.autograd.Function):
        @staticmethod
        def forward(ctx, values, cotangent, incoming):
            direction = incoming.detach().numpy().astype(float)
            _, matrix, product, _ = second_derivatives(values.detach().numpy().astype(float), direction)
            gradient = cotangent.detach().numpy() @ product[:, :, 0]
            tangent = matrix @ direction
            publish(True)
            return torch.as_tensor(gradient, dtype=values.dtype), torch.as_tensor(tangent, dtype=cotangent.dtype)

        @staticmethod
        def backward(ctx, *unused):
            raise UnsupportedFeature("higher_order_derivatives", "Torch native third derivatives are not implemented.")

    class NativeQuantumVJP(torch.autograd.Function):
        @staticmethod
        def forward(ctx, values, cotangent):
            ctx.save_for_backward(values, cotangent)
            _, matrix, _ = plan.jacobian(unpack(values.detach().numpy().astype(float)), **plan.node.gradient_kwargs)
            matrix = matrix[:, indices]
            publish()
            return torch.as_tensor(cotangent.detach().numpy() @ matrix, dtype=values.dtype)

        @staticmethod
        def backward(ctx, incoming):
            return NativeSecondVJP.apply(*ctx.saved_tensors, incoming)

    class NativeQuantumFunction(torch.autograd.Function):
        @staticmethod
        def forward(ctx, values):
            ctx.save_for_backward(values)
            ctx.values = unpack(values.detach().numpy().astype(float))
            result = plan.evaluate(ctx.values)
            flat, plan.last_spec = flatten_tree(result)
            return torch.as_tensor(flat, dtype=values.dtype)

        @staticmethod
        def backward(ctx, cotangent):
            if plan.node.max_diff not in {1, 2}: raise UnsupportedFeature("higher_order_derivatives")
            if torch.is_grad_enabled():
                if plan.node.max_diff != 2:
                    raise UnsupportedFeature("higher_order_derivatives", "Torch higher-order second derivatives require max_diff=2.")
                return NativeQuantumVJP.apply(ctx.saved_tensors[0], cotangent)
            _, jacobian, _ = plan.jacobian(ctx.values, **plan.node.gradient_kwargs)
            jacobian = jacobian[:, indices]
            result = cotangent.detach().numpy().astype(float) @ jacobian
            publish()
            return torch.as_tensor(result, dtype=cotangent.dtype)

    flat = NativeQuantumFunction.apply(packed)
    return unflatten_tree(flat, plan.last_spec)


def _autograd_execute(plan):
    try:
        import autograd.numpy as anp
        from autograd.extend import primitive, defvjp, defvjp_argnums
    except ImportError as exc: raise ImportError("QuantumBridge Autograd QNode requires optional autograd.") from exc
    indices = [index for index, angle in enumerate(plan.recorder.angles) if type(angle).__module__.startswith("autograd")]
    from .ordinary_resources import managed_framework_plan
    plan = managed_framework_plan(plan)
    unpack, second_derivatives = _framework_point(plan, indices)

    def publish(second=False):
        plan.node.last_metadata = {**plan.metadata, "interface": "autograd", "native_vjp": True,
                                  "native_second_order": second, "classical_chain_rule": "Autograd graph"}

    @primitive
    def native_second_vjp(values, cotangent, direction):
        _, matrix, product, _ = second_derivatives(np.asarray(values, dtype=float), np.asarray(direction, dtype=float))
        publish(True)
        return np.concatenate([np.asarray(cotangent) @ product[:, :, 0], matrix @ direction])

    def reject_third(*unused):
        raise UnsupportedFeature("higher_order_derivatives", "Autograd native third derivatives are not implemented.")
    defvjp(native_second_vjp, reject_third, reject_third, reject_third)

    @primitive
    def native_vjp(values, cotangent):
        _, matrix, _ = plan.jacobian(unpack(np.asarray(values, dtype=float)), **plan.node.gradient_kwargs)
        matrix = matrix[:, indices]
        publish()
        return np.asarray(cotangent) @ matrix

    def second_vjp_rule(argnums, answer, arguments, keywords):
        values, cotangent = arguments
        if plan.node.max_diff != 2:
            raise UnsupportedFeature("higher_order_derivatives", "Autograd second derivatives require max_diff=2.")
        def backward(direction):
            result = native_second_vjp(values, cotangent, direction)
            full = (result[:len(indices)], result[len(indices):])
            return tuple(full[index] for index in argnums)
        return backward
    defvjp_argnums(native_vjp, second_vjp_rule)

    @primitive
    def native_quantum(values):
        result = plan.evaluate(unpack(np.asarray(values, dtype=float)))
        flat, plan.last_spec = flatten_tree(result)
        return flat

    def vjp_rule(answer, values):
        if plan.node.max_diff not in {1, 2}: raise UnsupportedFeature("higher_order_derivatives")
        if plan.node.max_diff == 1 and type(values).__module__.startswith("autograd"):
            raise UnsupportedFeature("higher_order_derivatives", "Autograd higher-order native QNode derivatives are not implemented.")
        return lambda cotangent: native_vjp(values, cotangent)

    defvjp(native_quantum, vjp_rule)
    packed = anp.stack([plan.recorder.angles[index] for index in indices]) if indices else anp.empty(0)
    for value in _leaves(plan.input_values):
        if type(value).__module__.startswith("autograd"): packed = packed + 0 * anp.sum(value)
    flat = native_quantum(packed)
    return unflatten_tree(flat, plan.last_spec)
