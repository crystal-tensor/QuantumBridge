# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/api_contract_v0.1.md and docs/mvp/mvp_scope_v0.1.md.

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from typing import Any, Iterator, Mapping, Sequence, Union


@dataclass(frozen=True)
class Parameter:
    """Named scalar parameter used by QuantumBridge circuits."""

    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("QuantumBridge parameter names must be non-empty strings.")

    def __repr__(self) -> str:
        return f"Parameter({self.name!r})"

    def __str__(self) -> str:
        return self.name

    def expression(self) -> "ParameterExpression":
        return ParameterExpression("parameter", (self,))

    def bind(self, mapping: Mapping[Union["Parameter", str], Real], allow_partial: bool = False):
        return self.expression().bind(mapping, allow_partial=allow_partial)

    def __neg__(self) -> "ParameterExpression":
        return -self.expression()

    def __add__(self, other: Any) -> "ParameterExpression":
        return self.expression() + other

    def __radd__(self, other: Any) -> "ParameterExpression":
        return _coerce_expression(other) + self.expression()

    def __sub__(self, other: Any) -> "ParameterExpression":
        return self.expression() - other

    def __rsub__(self, other: Any) -> "ParameterExpression":
        return _coerce_expression(other) - self.expression()

    def __mul__(self, other: Any) -> "ParameterExpression":
        return self.expression() * other

    def __rmul__(self, other: Any) -> "ParameterExpression":
        return _coerce_expression(other) * self.expression()

    def __truediv__(self, other: Any) -> "ParameterExpression":
        return self.expression() / other

    def __rtruediv__(self, other: Any) -> "ParameterExpression":
        return _coerce_expression(other) / self.expression()

    def __pow__(self, other: Any) -> "ParameterExpression":
        return self.expression() ** other

    def __rpow__(self, other: Any) -> "ParameterExpression":
        return _coerce_expression(other) ** self.expression()


@dataclass(frozen=True)
class ParameterExpression:
    """Arithmetic expression over scalar QuantumBridge parameters."""

    op: str
    args: tuple[Any, ...]

    @property
    def parameters(self) -> frozenset[Parameter]:
        if self.op == "const":
            return frozenset()
        if self.op == "parameter":
            return frozenset({self.args[0]})
        found: set[Parameter] = set()
        for arg in self.args:
            if isinstance(arg, ParameterExpression):
                found.update(arg.parameters)
        return frozenset(found)

    @property
    def name(self) -> str:
        if self.op == "parameter":
            return self.args[0].name
        return str(self)

    def bind(self, mapping: Mapping[Union[Parameter, str], Real], allow_partial: bool = False):
        if self.op == "const":
            return self.args[0]
        if self.op == "parameter":
            parameter = self.args[0]
            if parameter in mapping:
                return mapping[parameter]
            if parameter.name in mapping:
                return mapping[parameter.name]
            if allow_partial:
                return self
            raise ValueError(f"QuantumBridge parameter {parameter.name!r} is not bound.")
        if self.op == "neg":
            value = _bind_arg(self.args[0], mapping, allow_partial)
            return -value if isinstance(value, Real) else ParameterExpression("neg", (value,))
        left = _bind_arg(self.args[0], mapping, allow_partial)
        right = _bind_arg(self.args[1], mapping, allow_partial)
        if isinstance(left, Real) and isinstance(right, Real):
            return _evaluate_binary(self.op, left, right)
        if not allow_partial:
            missing = ", ".join(sorted(parameter.name for parameter in self.parameters if parameter not in mapping and parameter.name not in mapping))
            raise ValueError(f"QuantumBridge parameters are not fully bound: {missing}")
        return ParameterExpression(self.op, (_coerce_expression(left), _coerce_expression(right))).simplify()

    def evaluate(self, mapping: Mapping[Union[Parameter, str], Real]) -> Real:
        return self.bind(mapping, allow_partial=False)

    def simplify(self):
        if self.op in {"const", "parameter"}:
            return self
        if self.op == "neg":
            value = self.args[0]
            if isinstance(value, ParameterExpression) and value.op == "const":
                return ParameterExpression("const", (-value.args[0],))
            return self
        left, right = self.args
        if isinstance(left, ParameterExpression) and isinstance(right, ParameterExpression):
            if left.op == "const" and right.op == "const":
                return ParameterExpression("const", (_evaluate_binary(self.op, left.args[0], right.args[0]),))
        return self

    def __repr__(self) -> str:
        return f"ParameterExpression({str(self)!r})"

    def __str__(self) -> str:
        if self.op == "const":
            return repr(self.args[0])
        if self.op == "parameter":
            return self.args[0].name
        if self.op == "neg":
            return f"-({self.args[0]})"
        symbol = {"+": "+", "-": "-", "*": "*", "/": "/", "**": "**"}[self.op]
        return f"({self.args[0]} {symbol} {self.args[1]})"

    def __float__(self) -> float:
        if self.op == "const":
            return float(self.args[0])
        raise TypeError("QuantumBridge parameter expressions must be bound before conversion to float.")

    def __neg__(self) -> "ParameterExpression":
        return ParameterExpression("neg", (self,))

    def __add__(self, other: Any) -> "ParameterExpression":
        return ParameterExpression("+", (self, _coerce_expression(other))).simplify()

    def __radd__(self, other: Any) -> "ParameterExpression":
        return _coerce_expression(other) + self

    def __sub__(self, other: Any) -> "ParameterExpression":
        return ParameterExpression("-", (self, _coerce_expression(other))).simplify()

    def __rsub__(self, other: Any) -> "ParameterExpression":
        return _coerce_expression(other) - self

    def __mul__(self, other: Any) -> "ParameterExpression":
        return ParameterExpression("*", (self, _coerce_expression(other))).simplify()

    def __rmul__(self, other: Any) -> "ParameterExpression":
        return _coerce_expression(other) * self

    def __truediv__(self, other: Any) -> "ParameterExpression":
        return ParameterExpression("/", (self, _coerce_expression(other))).simplify()

    def __rtruediv__(self, other: Any) -> "ParameterExpression":
        return _coerce_expression(other) / self

    def __pow__(self, other: Any) -> "ParameterExpression":
        return ParameterExpression("**", (self, _coerce_expression(other))).simplify()

    def __rpow__(self, other: Any) -> "ParameterExpression":
        return _coerce_expression(other) ** self


class ParameterVector(Sequence[Parameter]):
    """Ordered vector of scalar parameters."""

    def __init__(self, name: str, length: int) -> None:
        if not isinstance(name, str) or not name:
            raise ValueError("QuantumBridge parameter vector names must be non-empty strings.")
        if not isinstance(length, int) or length < 0:
            raise ValueError("QuantumBridge parameter vector length cannot be negative.")
        self.name = name
        self._params = tuple(Parameter(f"{name}[{index}]") for index in range(length))

    def __getitem__(self, index):
        return self._params[index]

    def __iter__(self) -> Iterator[Parameter]:
        return iter(self._params)

    def __len__(self) -> int:
        return len(self._params)

    def __repr__(self) -> str:
        return f"ParameterVector({self.name!r}, {len(self)})"

    @property
    def params(self) -> tuple[Parameter, ...]:
        return self._params


ParameterValue = Union[Real, Parameter, ParameterExpression]


def resolve_parameter(value: ParameterValue, mapping: Mapping[Union[Parameter, str], Real], allow_partial: bool = False):
    if isinstance(value, Parameter):
        if value in mapping:
            return mapping[value]
        if value.name in mapping:
            return mapping[value.name]
        if allow_partial:
            return value
        raise ValueError(f"QuantumBridge parameter {value.name!r} is not bound.")
    if isinstance(value, ParameterExpression):
        return value.bind(mapping, allow_partial=allow_partial)
    if isinstance(value, Real):
        return value
    raise TypeError("QuantumBridge parameters must be real numbers, Parameter objects, or ParameterExpression objects.")


def parameter_set(values: Sequence[Any]) -> frozenset[Parameter]:
    found: set[Parameter] = set()
    for value in values:
        if isinstance(value, Parameter):
            found.add(value)
        elif isinstance(value, ParameterExpression):
            found.update(value.parameters)
    return frozenset(found)


def _coerce_expression(value: Any) -> ParameterExpression:
    if isinstance(value, ParameterExpression):
        return value
    if isinstance(value, Parameter):
        return value.expression()
    if isinstance(value, Real):
        return ParameterExpression("const", (value,))
    raise TypeError("QuantumBridge parameter expressions require real numbers or parameters.")


def _bind_arg(arg: Any, mapping: Mapping[Union[Parameter, str], Real], allow_partial: bool):
    if isinstance(arg, ParameterExpression):
        return arg.bind(mapping, allow_partial=allow_partial)
    return arg


def _evaluate_binary(op: str, left: Real, right: Real) -> Real:
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        return left / right
    if op == "**":
        return left**right
    raise ValueError(f"Unknown QuantumBridge parameter expression operator {op!r}.")
