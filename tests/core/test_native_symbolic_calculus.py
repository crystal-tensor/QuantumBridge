# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent analytic checks for executable native symbolic mathematics."""

import builtins
import cmath
import math
import numpy as np

import pytest

from quantumbridge import Circuit, Parameter, ParameterExpression, ParameterVector
from quantumbridge.core import SymbolicExpressionLimits, SymbolicResourceLimitError, symbolic_expression_scope


POINTS = [(0.4, -0.2), (-0.7, 0.5), (0.8, 1.1)]


@pytest.mark.parametrize("pvalue,qvalue", POINTS)
def test_symbolic_sin_exp_construct_bind_and_differentiate_without_float(pvalue, qvalue):
    p, q = Parameter("p"), Parameter("q")
    expression = (p*q + p**2).sin() + (2*p - q).exp()
    assert expression.parameters == {p, q}
    partial = expression.bind({p: pvalue}, allow_partial=True)
    assert partial.parameters == {q}
    a, b = pvalue*qvalue + pvalue**2, 2*pvalue - qvalue
    assert partial.bind({q: qvalue}) == pytest.approx(math.sin(a) + math.exp(b))
    dp, dq = expression.gradient(p), expression.gradient(q)
    assert isinstance(dp, ParameterExpression)
    assert dp.bind({p: pvalue, q: qvalue}) == pytest.approx(
        (qvalue + 2*pvalue)*math.cos(a) + 2*math.exp(b))
    assert dq.bind({p: pvalue, q: qvalue}) == pytest.approx(
        pvalue*math.cos(a) - math.exp(b))
    expected_mixed = (math.cos(a) - pvalue*(qvalue + 2*pvalue)*math.sin(a)
                      - 2*math.exp(b))
    assert dp.gradient(q).bind({p: pvalue, q: qvalue}) == pytest.approx(expected_mixed)
    assert dq.gradient(p).bind({p: pvalue, q: qvalue}) == pytest.approx(expected_mixed)
    assert expression.parameters == {p, q}


@pytest.mark.parametrize("pvalue,qvalue", POINTS)
def test_public_simultaneous_substitution_does_not_revisit_replacements(pvalue, qvalue):
    p, q = Parameter("p"), Parameter("q")
    expression = p - 2*q
    swapped = expression.subs({p: q, q: p})
    assert swapped.parameters == {p, q}
    assert swapped.bind({p: pvalue, q: qvalue}) == pytest.approx(qvalue - 2*pvalue)
    crossed = expression.subs({p: p+q, q: p-q})
    assert crossed.bind({p: pvalue, q: qvalue}) == pytest.approx(-pvalue + 3*qvalue)
    assert expression.bind({p: pvalue, q: qvalue}) == pytest.approx(pvalue - 2*qvalue)


FUNCTIONS = [
    ("sin", math.sin, math.cos, lambda x: -math.sin(x)),
    ("cos", math.cos, lambda x: -math.sin(x), lambda x: -math.cos(x)),
    ("tan", math.tan, lambda x: 1/math.cos(x)**2, lambda x: 2*math.tan(x)/math.cos(x)**2),
    ("exp", math.exp, math.exp, math.exp),
    ("log", lambda x: math.log(x) if x > 0 else cmath.log(x), lambda x: 1/x, lambda x: -1/x**2),
    ("arcsin", math.asin, lambda x: 1/math.sqrt(1-x*x), lambda x: x/(1-x*x)**1.5),
    ("arccos", math.acos, lambda x: -1/math.sqrt(1-x*x), lambda x: -x/(1-x*x)**1.5),
    ("arctan", math.atan, lambda x: 1/(1+x*x), lambda x: -2*x/(1+x*x)**2),
    ("abs", abs, lambda x: 1 if x > 0 else -1, lambda x: 0),
    ("sign", lambda x: 1 if x > 0 else -1, lambda x: 0, lambda x: 0),
    ("conjugate", lambda x: x, lambda x: 1, lambda x: 0),
]


def numeric_at(expression, mapping):
    if type(expression) in (int, float, complex):
        return expression
    return expression.bind({key: value for key, value in mapping.items() if key in expression.parameters})


@pytest.mark.parametrize("value", [.2, -.7, .8])
@pytest.mark.parametrize("name,forward,first,second", FUNCTIONS)
def test_eleven_elementary_families_have_independent_values_and_two_derivatives(name, forward, first, second, value):
    vector = ParameterVector("v", 2)
    parameter = vector[1]
    expression = getattr(parameter, name)()
    assert expression.parameters == {parameter}
    assert next(iter(expression.parameters)).vector is vector
    assert expression.bind({parameter: value}) == pytest.approx(forward(value))
    derivative = expression.gradient(parameter)
    assert numeric_at(derivative, {parameter: value}) == pytest.approx(first(value))
    internal = expression._gradient_expression(parameter)
    assert type(internal) is ParameterExpression
    assert numeric_at(internal, {parameter: value}) == pytest.approx(first(value))
    assert numeric_at(internal._gradient_expression(parameter), {parameter: value}) == pytest.approx(second(value))
    assert expression.is_real() is None


@pytest.mark.parametrize("value", [.2+.3j, -.7+.1j])
@pytest.mark.parametrize("name", ["sin", "cos", "tan", "exp", "log", "arcsin", "arccos", "arctan", "conjugate", "abs"])
def test_complex_scalar_functions_use_principal_branches_without_silently_casting(name, value):
    p = Parameter("p")
    alias = {"arcsin": "asin", "arccos": "acos", "arctan": "atan"}
    expected = abs(value) if name == "abs" else value.conjugate() if name == "conjugate" else getattr(cmath, alias.get(name, name))(value)
    assert getattr(p, name)().bind({p: value}) == pytest.approx(expected)


@pytest.mark.parametrize("pvalue,qvalue", POINTS)
@pytest.mark.parametrize("kind", ["product", "quotient", "variable_power", "reverse_power", "nested", "shared_square", "cancel"])
def test_derivative_algebra_and_partial_assignment(kind, pvalue, qvalue):
    p, q = Parameter("p"), Parameter("q")
    if kind == "product": expression, expected = p*q, qvalue
    elif kind == "quotient": expression, expected = p/(q+3), 1/(qvalue+3)
    elif kind == "variable_power": expression, expected = (p+2)**q, qvalue*(pvalue+2)**(qvalue-1)
    elif kind == "reverse_power": expression, expected = 2**p, 2**pvalue*math.log(2)
    elif kind == "nested": expression, expected = (p.sin().exp()).log(), math.cos(pvalue)
    elif kind == "shared_square": expression, expected = p*p+p**2, 4*pvalue
    else: expression, expected = p-p, 0.
    derivative = expression.gradient(p)
    assert numeric_at(derivative, {p: pvalue, q: qvalue}) == pytest.approx(expected)
    partial = expression.assign(p, pvalue)
    assert partial.parameters <= {q}
    if not partial.parameters:
        assert partial.numeric() == pytest.approx(expression.bind({p: pvalue}))


def test_identity_unknown_keys_aliases_and_replacement_collisions_are_atomic():
    p, q, impostor = Parameter("p"), Parameter("q"), Parameter("p")
    expression = (p*q).sin()
    with pytest.raises(ValueError, match="Unknown"): expression.bind({impostor: .4})
    with pytest.raises(ValueError, match="Conflicting"): expression.subs({q: impostor})
    with pytest.raises(ValueError, match="Unknown"): expression.subs({impostor: q})
    with pytest.raises(TypeError): expression.subs({p: .4})
    with pytest.raises(TypeError): expression.bind({p: q})
    with pytest.raises(ValueError, match="more than once"): expression.bind({p: .4, "p": .5})
    assert expression.subs({impostor: q}, allow_unknown_parameters=True) == expression
    assert expression.bind({impostor: .4}, allow_unknown_parameters=True) == expression
    assert expression.parameters == {p, q}
    assert expression.subs({p: q}).parameters == {q}
    assert expression.assign(p, 2*q).parameters == {q}


def test_scalar_reconstruction_of_a_vector_uuid_does_not_merge_distinct_parameter_kinds():
    vector = ParameterVector("v", 2)
    parameter = vector[1]
    alias = Parameter(parameter.name, parameter.uuid)
    assert alias != parameter
    assert len({alias, parameter}) == 2
    with pytest.raises(ValueError, match="Conflicting"):
        parameter.sin()+alias.cos()
    with pytest.raises(ValueError, match="unknown"):
        Circuit(1).ry(parameter, 0).bind({alias: .4})


def test_numeric_and_syntactic_membership_are_distinct_and_constants_remain_differentiable():
    p = Parameter("p")
    for expression in (0*p, p-p):
        assert expression.parameters == {p}
        with pytest.raises(TypeError, match="Unbound"): expression.numeric()
        assert expression.numeric(strict=False) == 0
        derivative = expression.gradient(p)
        assert type(derivative) is float and derivative == 0
    assert (p+0).is_symbol()
    assert not p.sin().is_symbol()
    constant = (p+3).gradient(p)
    assert type(constant) is float and constant == 1
    internal = (p+3)._gradient_expression(p)
    assert type(internal) is ParameterExpression and internal.numeric() == 1
    assert internal._gradient_expression(p).numeric() == 0
    assert p.assign(p, 3).is_real() is True
    assert (p+1j).assign(p, .2).is_real() is False
    assert (p+1j).bind_all({p: .2, Parameter("unused"): 4}) == .2+1j
    with pytest.raises(TypeError): float(p.sin())


def test_internal_physical_resolution_retains_the_existing_string_key_contract():
    from quantumbridge.core.parameters import resolve_parameter
    p = Parameter("p")
    assert resolve_parameter(p.sin(), {"p": .4}) == pytest.approx(math.sin(.4))
    assert resolve_parameter(p.sin(), {"unused": .4}, allow_partial=True).parameters == {p}


def test_internal_expression_resolution_does_not_scan_unrelated_circuit_bindings():
    from quantumbridge.core.parameters import resolve_parameter
    class Bindings(dict):
        def items(self): pytest.fail("Per-expression resolution scanned the complete circuit bindings")
    p = Parameter("p")
    assert resolve_parameter(p.sin(), Bindings({p: .4, "unrelated": 1.})) == pytest.approx(math.sin(.4))


def test_default_symbolic_magnitude_preserves_the_existing_finite_double_range():
    p = Parameter("p")
    assert (p+0).bind({p: 1.5e308}) == 1.5e308


def test_numpy_integer_binding_cannot_silently_wrap_a_native_numeric_power():
    p = Parameter("p")
    expected = 3000000**3
    assert (p**3).bind({p: np.int64(3000000)}) == expected
    assert (p*p*p).bind({p: np.int64(3000000)}) == expected


@pytest.mark.parametrize("name,value", [("log", 0), ("arcsin", 2), ("arccos", -2), ("exp", 1000), ("sign", .3j)])
def test_domains_and_singular_numeric_values_are_explicit(name, value):
    with pytest.raises((ValueError, ArithmeticError)):
        getattr(Parameter("p"), name)().bind({"p": value})


@pytest.mark.parametrize("name", ["abs", "sign", "arcsin", "arccos"])
def test_nonsmooth_and_boundary_derivatives_never_report_a_fake_zero(name):
    p = Parameter("p")
    expression = getattr(p, name)()
    point = 0 if name in {"abs", "sign"} else 1
    assert math.isfinite(expression.bind({p: point}))
    with pytest.raises((ValueError, ArithmeticError)):
        expression.gradient(p).bind({p: point})


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, complex(0, math.inf)])
def test_nonfinite_bindings_are_rejected_before_evaluation(value):
    p = Parameter("p")
    with pytest.raises(ValueError, match="finite"): p.sin().bind({p: value})


def test_native_calculus_does_not_import_upstream_or_sympy(monkeypatch):
    original = builtins.__import__
    def guarded(name, *args, **kwargs):
        if name.split(".")[0] in {"qiskit", "sympy", "symengine"}:
            pytest.fail("Native calculus attempted to import a third-party symbolic engine")
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", guarded)
    p = Parameter("p")
    expression = (p*p).sin()+p.exp()
    assert expression.gradient(p).gradient(p).bind({p: .4}) == pytest.approx(
        2*math.cos(.16)-.64*math.sin(.16)+math.exp(.4))


@pytest.mark.parametrize("field,limit,build", [
    ("max_nodes", 5, lambda p: (p+p)*(p+p)),
    ("max_depth", 3, lambda p: p.sin().cos().exp()),
    ("max_parameters", 1, lambda p: p+Parameter("q")),
    ("max_substitutions", 1, lambda p: (p+Parameter("q")).bind({"p": 1, "q": 2})),
    ("max_expansion_work", 2, lambda p: (p*p).gradient(p)),
    ("max_derivative_order", 1, lambda p: p.exp().gradient(p).gradient(p)),
    ("max_integer_bits", 16, lambda p: (2**p).bind({p: 1000})),
    ("max_power_exponent", 10, lambda p: (2**p).bind({p: 1000})),
])
def test_construction_and_calculus_reject_before_unbounded_expansion(field, limit, build):
    with symbolic_expression_scope(SymbolicExpressionLimits(**{field: limit})):
        with pytest.raises(SymbolicResourceLimitError, match=field): build(Parameter("p"))


def test_substitution_growth_is_bounded_and_scope_is_restored():
    p = Parameter("p")
    expression = p.expression()
    with symbolic_expression_scope(SymbolicExpressionLimits(max_nodes=50)):
        with pytest.raises(SymbolicResourceLimitError, match="max_nodes"):
            for _ in range(20): expression = expression.subs({p: p*p})
    assert p.exp().gradient(p).gradient(p).bind({p: .2}) == pytest.approx(math.exp(.2))


def test_nested_symbolic_scopes_share_cumulative_work_and_cannot_relax_a_parent_budget():
    p = Parameter("p")
    with symbolic_expression_scope(SymbolicExpressionLimits(max_expansion_work=8)):
        p.sin()
        with symbolic_expression_scope(SymbolicExpressionLimits(max_expansion_work=1000)):
            with pytest.raises(SymbolicResourceLimitError, match="max_expansion_work"):
                for _ in range(10): p.cos()
    assert p.sin().bind({p: .2}) == pytest.approx(math.sin(.2))


@pytest.mark.parametrize("transform", [lambda expression, p: expression.assign(p, p),
                                       lambda expression, p: expression.subs({p: p}),
                                       lambda expression, p: expression.bind({})])
def test_identity_transformations_do_not_reset_the_derivative_order_budget(transform):
    p = Parameter("p")
    with symbolic_expression_scope(SymbolicExpressionLimits(max_derivative_order=1)):
        expression = transform(p.exp().gradient(p), p)
        with pytest.raises(SymbolicResourceLimitError, match="max_derivative_order"):
            expression.gradient(p)


def test_replacement_cannot_import_an_oversized_existing_ast_into_a_small_scope():
    p, q = Parameter("p"), Parameter("q")
    replacement = q.sin().cos().exp()
    with symbolic_expression_scope(SymbolicExpressionLimits(max_nodes=2)):
        with pytest.raises(SymbolicResourceLimitError, match="max_nodes"):
            p.assign(p, replacement)
        with pytest.raises(SymbolicResourceLimitError, match="max_nodes"):
            Circuit(1).ry(p, 0).assign_parameters({p: replacement})


def test_internal_local_substitutions_still_honor_an_explicit_per_expression_limit():
    p, q = Parameter("p"), Parameter("q")
    circuit = Circuit(1).ry(p+q, 0)
    with symbolic_expression_scope(SymbolicExpressionLimits(max_substitutions=1)):
        with pytest.raises(SymbolicResourceLimitError, match="max_substitutions"):
            circuit.assign_parameters({p: .2, q: .3})


@pytest.mark.parametrize("kwargs", [{"max_depth": 0}, {"max_nodes": True}, {"max_numeric_magnitude": math.inf}, {"max_numeric_magnitude": -1}])
def test_invalid_symbolic_limit_definitions_reject(kwargs):
    with pytest.raises(ValueError): SymbolicExpressionLimits(**kwargs)


def test_unsupported_foreign_values_ast_shapes_and_scope_types_never_coerce_callbacks():
    class Foreign:
        def __float__(self): pytest.fail("Untrusted numeric conversion executed")
    p = Parameter("p")
    with pytest.raises(TypeError): p.assign(p, Foreign())
    with pytest.raises(TypeError): p.gradient("p")
    with pytest.raises(TypeError): p.expression().bind([(p, .4)])
    with pytest.raises(TypeError): p.expression().bind({object(): .4})
    with pytest.raises(ValueError): ParameterExpression("unknown", ())
    with pytest.raises(ValueError): ParameterExpression("sin", ())
    with pytest.raises(TypeError): ParameterExpression("sin", (Foreign(),))
    with pytest.raises(TypeError):
        with symbolic_expression_scope({}): pass


def test_optional_sympy_is_an_outward_only_interoperability_boundary():
    sympy = pytest.importorskip("sympy")
    p, q = Parameter("p"), Parameter("q")
    expression = (p*q).sin()+p.exp()
    converted = expression.sympify()
    assert complex(converted.subs({sympy.Symbol("p"): .4, sympy.Symbol("q"): -.2})) == pytest.approx(expression.bind({p: .4, q: -.2}))
    with pytest.raises(TypeError): expression.assign(p, sympy.Symbol("foreign"))


def test_complex_expression_is_not_silently_accepted_as_a_physical_rotation():
    p = Parameter("p")
    circuit = Circuit(1).ry(p+1j, 0)
    with pytest.raises(ValueError, match="must be real"): circuit.assign_parameters({p: .4})
    real = Circuit(1).ry((p+1j)-(2j/2), 0).assign_parameters({p: .4})
    assert real.operations[0].params == (.4,)


@pytest.mark.parametrize("value", [.2, .4, .8])
@pytest.mark.parametrize("name,forward,first,second", FUNCTIONS)
def test_optional_public_elementary_values_and_supported_gradient_contracts(name, forward, first, second, value):
    pytest.importorskip("qiskit")
    from qiskit.circuit import Parameter as PublicParameter
    p, public = Parameter("p"), PublicParameter("p")
    native_expression, public_expression = getattr(p, name)(), getattr(public, name)()
    assert native_expression.bind({p: value}) == pytest.approx(public_expression.bind({public: value}).numeric())
    if name == "sign":
        with pytest.raises(RuntimeError): public_expression.gradient(public)
        assert numeric_at(native_expression.gradient(p), {p: value}) == 0
    else:
        derivative = public_expression.gradient(public)
        public_value = derivative.bind({public: value}).numeric() if hasattr(derivative, "parameters") else derivative
        assert numeric_at(native_expression.gradient(p), {p: value}) == pytest.approx(public_value)
