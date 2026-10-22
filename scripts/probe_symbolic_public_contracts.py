# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Observe installed public APIs only; never inspect upstream implementation."""

import inspect
import json
import math
from uuid import UUID

import qiskit
from qiskit.circuit import Parameter, ParameterExpression, ParameterVector


def encode(value):
    if isinstance(value, ParameterExpression):
        return {"type": type(value).__name__, "text": str(value),
                "parameters": sorted((p.name, str(p.uuid)) for p in value.parameters)}
    if isinstance(value, complex):
        return {"complex": [value.real, value.imag]}
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return {"type": type(value).__name__, "text": str(value)}


def record(name, call):
    try:
        result = {"name": name, "result": encode(call())}
        encoded = json.dumps(result, sort_keys=True, allow_nan=False)
    except Exception as error:
        encoded = json.dumps({"name": name, "exception": type(error).__name__, "message": str(error)}, sort_keys=True)
    print(encoded)


print(json.dumps({"qiskit_version": qiskit.__version__}))
p = Parameter("p", uuid=UUID(int=1))
q = Parameter("q", uuid=UUID(int=2))
other = Parameter("p", uuid=UUID(int=3))
vector = ParameterVector("v", 3)
functions = ("sin", "cos", "tan", "exp", "log", "arcsin", "arccos", "arctan",
             "abs", "sign", "conjugate", "sqrt")
for method in functions + ("gradient", "subs", "assign", "bind", "bind_all", "numeric", "is_real", "is_symbol", "sympify"):
    record(method + ".signature", lambda method=method: str(inspect.signature(getattr(ParameterExpression, method))))
for method in functions:
    record(method + ".construction", lambda method=method: getattr(p, method)())
    record(method + ".bound", lambda method=method: getattr(p, method)().bind({p: .4}))
    record(method + ".gradient", lambda method=method: getattr(p, method)().gradient(p))
    record(method + ".vector", lambda method=method: getattr(vector[1], method)().bind({vector[1]: .4}))
expression = (p*q+p**2).sin() + (2*p-q).exp()
for name, call in {
    "chain.partial": lambda: expression.bind({p: .4}),
    "chain.full": lambda: expression.bind({p: .4, q: -.2}),
    "chain.gradient": lambda: expression.gradient(p),
    "chain.mixed": lambda: expression.gradient(p).gradient(q).bind({p: .4, q: -.2}),
    "subs.swap": lambda: (p-2*q).subs({p: q, q: p}),
    "subs.cross": lambda: (p-2*q).subs({p: p+q, q: p-q}),
    "subs.numeric": lambda: (p+q).subs({p: .4}),
    "subs.unknown": lambda: expression.subs({Parameter("missing"): q}),
    "subs.unknown_allowed": lambda: expression.subs({Parameter("missing"): q}, allow_unknown_parameters=True),
    "subs.identity": lambda: expression.subs({p: p}),
    "subs.collision": lambda: (p+q).subs({q: other}),
    "subs.wrong_uuid": lambda: (p+q).subs({other: 3*q}),
    "assign.numeric": lambda: (p+q).assign(p, .4),
    "assign.symbolic": lambda: (p+q).assign(p, 2*q),
    "bind.symbolic": lambda: (p+q).bind({p: q}),
    "bind.unknown": lambda: expression.bind({Parameter("missing"): .4}),
    "bind.unknown_allowed": lambda: expression.bind({Parameter("missing"): .4}, allow_unknown_parameters=True),
    "bind.string": lambda: expression.bind({"p": .4}),
    "bind.wrong_uuid": lambda: expression.bind({other: .4}),
    "bind.nan": lambda: p.sin().bind({p: math.nan}),
    "bind.infinity": lambda: p.sin().bind({p: math.inf}),
    "bind.complex": lambda: p.sin().bind({p: .4+.2j}),
    "zero.membership": lambda: sorted(x.name for x in (0*p).parameters),
    "zero.numeric_strict": lambda: (0*p).numeric(),
    "zero.numeric_nonstrict": lambda: (0*p).numeric(strict=False),
    "zero.gradient": lambda: (0*p).gradient(p),
    "cancel.membership": lambda: sorted(x.name for x in (p-p).parameters),
    "cancel.numeric": lambda: (p-p).numeric(strict=False),
    "constant.gradient": lambda: (p+q).gradient(p),
    "abs.zero.gradient": lambda: p.abs().gradient(p).bind({p: 0.}),
    "sign.zero.gradient": lambda: p.sign().gradient(p),
    "log.negative": lambda: p.log().bind({p: -1.}),
    "log.zero": lambda: p.log().bind({p: 0.}),
    "arcsin.outside": lambda: p.arcsin().bind({p: 2.}),
    "arccos.outside": lambda: p.arccos().bind({p: 2.}),
    "exp.overflow": lambda: p.exp().bind({p: 1000.}),
    "is_real.unbound": lambda: p.sin().is_real(),
    "is_real.complex": lambda: (p+1j).bind({p: .4}).is_real(),
    "is_symbol.symbol": lambda: p.is_symbol(),
    "is_symbol.identity": lambda: (p+0).is_symbol(),
    "sympify": lambda: expression.sympify(),
}.items():
    record(name, call)
