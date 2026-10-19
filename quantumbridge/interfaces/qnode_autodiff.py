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
    packed = torch.stack([value if isinstance(value, torch.Tensor) else torch.as_tensor(value, dtype=dtype) for value in angles]) if angles else torch.empty(0, dtype=dtype)
    for value in inputs:
        if value.requires_grad: packed = packed + 0 * value.sum()

    class NativeQuantumFunction(torch.autograd.Function):
        @staticmethod
        def forward(ctx, values):
            ctx.values = values.detach().numpy().astype(float)
            result = plan.evaluate(ctx.values)
            flat, plan.last_spec = flatten_tree(result)
            return torch.as_tensor(flat, dtype=values.dtype)

        @staticmethod
        def backward(ctx, cotangent):
            if torch.is_grad_enabled(): raise UnsupportedFeature("higher_order_derivatives", "Torch higher-order native QNode derivatives are not implemented.")
            if plan.node.max_diff != 1: raise UnsupportedFeature("higher_order_derivatives")
            _, jacobian, _ = plan.jacobian(ctx.values, **plan.node.gradient_kwargs)
            result = cotangent.detach().numpy().astype(float) @ jacobian
            plan.node.last_metadata = {**plan.metadata, "interface": "torch", "native_vjp": True, "classical_chain_rule": "Torch graph"}
            return torch.as_tensor(result, dtype=cotangent.dtype)

    flat = NativeQuantumFunction.apply(packed)
    return unflatten_tree(flat, plan.last_spec)


def _autograd_execute(plan):
    try:
        import autograd.numpy as anp
        from autograd.extend import primitive, defvjp
    except ImportError as exc: raise ImportError("QuantumBridge Autograd QNode requires optional autograd.") from exc

    @primitive
    def native_quantum(values):
        result = plan.evaluate(np.asarray(values, dtype=float))
        flat, plan.last_spec = flatten_tree(result)
        return flat

    def vjp_rule(answer, values):
        if plan.node.max_diff != 1: raise UnsupportedFeature("higher_order_derivatives")
        if type(values).__module__.startswith("autograd"):
            raise UnsupportedFeature("higher_order_derivatives", "Autograd higher-order native QNode derivatives are not implemented.")
        _, jacobian, _ = plan.jacobian(np.asarray(values, dtype=float), **plan.node.gradient_kwargs)
        plan.node.last_metadata = {**plan.metadata, "interface": "autograd", "native_vjp": True, "classical_chain_rule": "Autograd graph"}
        return lambda cotangent: anp.dot(cotangent, jacobian)

    defvjp(native_quantum, vjp_rule)
    packed = anp.stack(plan.recorder.angles) if plan.recorder.angles else anp.empty(0)
    for value in _leaves(plan.input_values):
        if type(value).__module__.startswith("autograd"): packed = packed + 0 * anp.sum(value)
    flat = native_quantum(packed)
    return unflatten_tree(flat, plan.last_spec)
