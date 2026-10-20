# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independent first-order classical tracing for native quantum derivatives.

import operator
import numpy as np

from quantumbridge.core.classical import UnsupportedFeature


class Dual:
    __array_priority__ = 1000

    def __init__(self, value, derivative, *, _reserved=False):
        if not _reserved:
            self._reserve(np.size(derivative))
        self.value = float(value)
        self.derivative = np.asarray(derivative, dtype=float)

    @staticmethod
    def _reserve(size):
        from quantumbridge.execution.resource_context import current_resources
        scope = current_resources()
        if scope is not None:
            scope.retain("first_parameter_trace_nodes", 8*size)

    def _new(self, value, compute):
        self._reserve(self.derivative.size)
        return Dual(value, compute(), _reserved=True)

    def _other(self, value):
        return value if isinstance(value, Dual) else self._new(value, lambda: np.zeros_like(self.derivative))

    def __add__(self, other):
        other = self._other(other)
        return self._new(self.value + other.value, lambda: self.derivative + other.derivative)

    __radd__ = __add__

    def __neg__(self): return self._new(-self.value, lambda: -self.derivative)
    def __sub__(self, other): return self + -self._other(other)
    def __rsub__(self, other): return self._other(other) + -self

    def __mul__(self, other):
        other = self._other(other)
        return self._new(self.value * other.value, lambda: self.derivative * other.value + other.derivative * self.value)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self._other(other)
        return self._new(self.value / other.value, lambda: (self.derivative * other.value - other.derivative * self.value) / other.value ** 2)

    def __rtruediv__(self, other): return self._other(other) / self

    def __pow__(self, other):
        other = self._other(other)
        value = self.value ** other.value
        if np.any(other.derivative):
            if self.value <= 0: raise UnsupportedFeature("classical_power", "Variable powers require a positive base.")
            return self._new(value, lambda: value * (other.derivative * np.log(self.value) + other.value * self.derivative / self.value))
        elif other.value == 0:
            return self._new(value, lambda: np.zeros_like(self.derivative))
        else:
            return self._new(value, lambda: other.value * self.value ** (other.value - 1) * self.derivative)

    def __rpow__(self, other): return self._other(other) ** self
    def sin(self): return self._new(np.sin(self.value), lambda: np.cos(self.value) * self.derivative)
    def cos(self): return self._new(np.cos(self.value), lambda: -np.sin(self.value) * self.derivative)
    def tan(self): return self._new(np.tan(self.value), lambda: self.derivative / np.cos(self.value) ** 2)
    def exp(self): return self._new(np.exp(self.value), lambda: np.exp(self.value) * self.derivative)
    def log(self): return self._new(np.log(self.value), lambda: self.derivative / self.value)
    def sqrt(self): return self ** .5

    def __abs__(self):
        if self.value == 0: raise UnsupportedFeature("nonsmooth_preprocessing", "Absolute value is not differentiable at zero.")
        return self._new(abs(self.value), lambda: np.sign(self.value) * self.derivative)

    def __float__(self):
        raise UnsupportedFeature("classical_cast", "Converting a trainable input to float loses its classical derivative.")

    def __bool__(self):
        raise UnsupportedFeature("trainable_classical_branch", "Differentiation through trainable Python branch conditions is unsupported.")

    def _compare(self, other): return bool(self)
    __eq__ = __ne__ = __lt__ = __le__ = __gt__ = __ge__ = _compare

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if method != "__call__" or kwargs:
            raise UnsupportedFeature("classical_ufunc", "Unsupported classical differentiation operation.")
        unary = {np.sin: "sin", np.cos: "cos", np.tan: "tan", np.exp: "exp", np.log: "log", np.sqrt: "sqrt", np.absolute: "__abs__", np.negative: "__neg__"}
        if ufunc in unary: return getattr(self, unary[ufunc])()
        binary = {np.add: operator.add, np.subtract: operator.sub, np.multiply: operator.mul,
                  np.divide: operator.truediv, np.true_divide: operator.truediv, np.power: operator.pow}
        if ufunc in binary:
            left, right = (self._other(value) for value in inputs)
            return binary[ufunc](left, right)
        raise UnsupportedFeature("classical_ufunc", f"No native derivative rule for {ufunc.__name__}.")


def trace_arguments(args, kwargs, argnums=0, argnames=(), *, order=1, direction=None, limits=None):
    if order not in {1, 2}:
        raise UnsupportedFeature("higher_order_derivatives", "Native classical tracing implements orders one and two.")
    positions = (argnums,) if isinstance(argnums, int) else tuple(argnums)
    names = (argnames,) if isinstance(argnames, str) else tuple(argnames)
    single = isinstance(argnums, int) and not argnames or not positions and len(names) == 1
    selected = [("arg", index, args[index]) for index in positions] + [("kw", name, kwargs[name]) for name in names]
    if not selected: raise ValueError("Select at least one trainable argument.")
    if len(set((kind, key) for kind, key, _ in selected)) != len(selected): raise ValueError("Duplicate trainable argument selection.")
    arrays = [np.asarray(value) for _, _, value in selected]
    if any(array.dtype.kind not in "f" for array in arrays):
        raise TypeError("Native QNode differentiation requires real floating-point trainable inputs.")
    if any(not np.all(np.isfinite(array)) for array in arrays): raise ValueError("Trainable inputs must be finite.")
    total, offset = sum(array.size for array in arrays), 0
    if total > 1024: raise MemoryError("Native classical trace exceeds the 1024-input derivative budget.")
    context = None
    if order == 2:
        from .second_trace import SecondContext
        context = SecondContext(total, direction, limits)
    traced_args, traced_kwargs, layout = list(args), dict(kwargs), []
    for (kind, key, _), array in zip(selected, arrays):
        traced = np.empty(array.shape, dtype=object)
        for index in np.ndindex(array.shape):
            position = offset + np.ravel_multi_index(index, array.shape)
            if context is None:
                Dual._reserve(total)
                derivative = np.zeros(total)
                derivative[position] = 1
                traced[index] = Dual(array[index], derivative, _reserved=True)
            else:
                traced[index] = context.variable(array[index], position)
        value = traced.item() if array.ndim == 0 else traced
        if kind == "arg": traced_args[key] = value
        else: traced_kwargs[key] = value
        layout.append((array.shape, slice(offset, offset + array.size)))
        offset += array.size
    return tuple(traced_args), traced_kwargs, layout, single, total


def flatten_tree(value):
    leaves = []
    def visit(item):
        if isinstance(item, dict): return ("dict", tuple((key, visit(child)) for key, child in item.items()))
        if isinstance(item, (tuple, list)): return ("tuple" if isinstance(item, tuple) else "list", tuple(visit(child) for child in item))
        array = np.asarray(item)
        if array.dtype.kind not in "fiu": raise UnsupportedFeature("differentiable_output", "Derivatives currently require real numeric outputs.")
        start = sum(leaf.size for leaf in leaves)
        leaves.append(array.astype(float).reshape(-1))
        return ("leaf", array.shape, start, array.size)
    spec = visit(value)
    return np.concatenate(leaves) if leaves else np.empty(0), spec


def unflatten_tree(flat, spec, trailing_shape=(), *, reshape=None):
    kind = spec[0]
    if kind == "dict": return {key: unflatten_tree(flat, child, trailing_shape, reshape=reshape) for key, child in spec[1]}
    if kind in {"tuple", "list"}:
        values = [unflatten_tree(flat, child, trailing_shape, reshape=reshape) for child in spec[1]]
        return tuple(values) if kind == "tuple" else values
    _, shape, start, size = spec
    part = flat[start:start + size]
    value = part.reshape(shape + trailing_shape) if reshape is None else reshape(part, shape + trailing_shape)
    return value.item() if not shape and not trailing_shape and isinstance(value, np.ndarray) else value
