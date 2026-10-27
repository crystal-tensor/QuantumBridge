# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Analytic scalar return contracts independently observed in both public SDKs."""

import math
from uuid import UUID

import numpy as np
import pytest

from quantumbridge import Parameter, ParameterExpression, ParameterVector


CONSTANTS = {
    "identity": (float, 1.), "absent": (float, 0.),
    "sum": (float, 1.), "zero_product": (float, 0.),
    "integer_coefficient": (int, 3), "integer_negative_one": (float, -1.),
    "negation": (float, -1.), "sum_duplicate": (int, 2),
    "float_integer_coefficient": (float, 3.),
    "negative_integer_coefficient": (int, -3),
    "negative_float_integer_coefficient": (float, -3.),
    "float_unit_coefficient": (float, 1.), "imaginary_zero": (float, 0.),
    "float_coefficient": (float, .25), "numpy_float_coefficient": (float, .25),
    "real_complex_coefficient": (float, 2.),
    "complex_coefficient": (complex, 2+3j), "imaginary_coefficient": (complex, 3j),
    "difference": (float, 0.), "retained_zero_coefficient": (float, 0.),
    "second_same": (int, 2), "second_mixed": (float, 1.),
    "second_unrelated": (float, 0.), "vector_zero": (float, 0.),
    "ratio_cancel": (float, 0.),
}
SYMBOLIC = {
    "bilinear": ({"p", "q"}, .17), "square": ({"p"}, .62),
    "trig_retained": ({"q", "r"}, math.cos(-.23)),
    "vector_bilinear": ({"v[0]", "v[2]"}, .19),
    "trig_identity": ({"p"}, 0.),
}
CASES = tuple(CONSTANTS)+tuple(SYMBOLIC)


def gradient_case(name, P=Parameter, V=ParameterVector):
    p, q, r = [P(key, uuid=UUID(int=i)) for key, i in (("p",111),("q",222),("r",333))]
    vector = V("v", 3)
    cases = {
        "identity": (p,(p,)), "absent": (p,(q,)), "sum": (p+q,(p,)),
        "zero_product": (p*0,(p,)), "integer_coefficient": (p*3,(p,)),
        "integer_negative_one": (p*-1,(p,)), "negation": (-p,(p,)),
        "sum_duplicate": (p+p,(p,)), "float_integer_coefficient": (p*3.,(p,)),
        "negative_integer_coefficient": (p*-3,(p,)),
        "negative_float_integer_coefficient": (p*-3.,(p,)),
        "float_unit_coefficient": (p*1.,(p,)), "imaginary_zero": (p*0j,(p,)),
        "float_coefficient": (p*.25,(p,)),
        "numpy_float_coefficient": (p*np.float64(.25),(p,)),
        "real_complex_coefficient": (p*(2+0j),(p,)),
        "complex_coefficient": (p*(2+3j),(p,)), "imaginary_coefficient": (p*3j,(p,)),
        "bilinear": (p*q,(p,)), "square": (p**2,(p,)),
        "trig_retained": (r.sin()+q*q,(r,)), "difference": (p-p,(p,)),
        "retained_zero_coefficient": (p*(q-q),(p,)),
        "second_same": (p*p,(p,p)), "second_mixed": (p*q,(p,q)),
        "second_unrelated": (p*q,(p,p)),
        "vector_bilinear": (vector[0]*vector[2],(vector[0],)),
        "vector_zero": (vector[2]*0,(vector[2],)), "ratio_cancel": (p/p,(p,)),
        "trig_identity": (p.sin()**2+p.cos()**2,(p,)),
    }
    expression, chain = cases[name]
    identities = {item.name:item for item in (p,q,r,*vector)}
    original = frozenset(expression.parameters)
    result = expression
    for parameter in chain:
        result = result.gradient(parameter)
    assert frozenset(expression.parameters) == original
    return result, identities


def value_at_point(expression):
    values = {p:{"p":.31,"q":.17,"r":-.23}.get(p.name,.19) for p in expression.parameters}
    return complex(expression.bind(values))


@pytest.mark.parametrize("case", CASES)
def test_public_gradient_returns_native_python_scalar_or_owned_symbolic_result(case):
    result, identities = gradient_case(case)
    if case in CONSTANTS:
        expected_type, value = CONSTANTS[case]
        assert type(result) is expected_type
        assert result == value
    else:
        names, value = SYMBOLIC[case]
        assert type(result) is ParameterExpression
        assert {p.name for p in result.parameters} == names
        for parameter in result.parameters:
            assert parameter.uuid == identities[parameter.name].uuid
        assert value_at_point(result) == pytest.approx(value, abs=5e-15, rel=0)
        simplified = result.simplify()
        assert simplified.parameters == result.parameters
        assert value_at_point(simplified) == pytest.approx(value, abs=5e-15, rel=0)


def test_scalar_return_does_not_waive_source_work_or_internal_derivative_order():
    from quantumbridge.core import SymbolicExpressionLimits, symbolic_expression_scope
    p = Parameter("p")
    expression = (p+p)*(p+p)
    with symbolic_expression_scope(SymbolicExpressionLimits(max_expansion_work=2)):
        with pytest.raises(ValueError, match="max_expansion_work"):
            expression.gradient(Parameter("unrelated"))
    with symbolic_expression_scope(SymbolicExpressionLimits(max_derivative_order=1)):
        internal = (p+3)._gradient_expression(p)
        assert internal.numeric() == 1 and internal._derivative_order == 1
        with pytest.raises(ValueError, match="max_derivative_order"):
            internal._gradient_expression(p)
    assert type((p*3).gradient(p)) is int
    assert (p*3).gradient(p) == 3


@pytest.mark.parametrize("kind", ["log", "division", "zero_product", "equal_difference"])
def test_constant_gradient_proof_never_erases_a_known_singular_source(kind):
    p = Parameter("p")
    zero = ParameterExpression("const", (0,))
    invalid = ParameterExpression("log", (zero,))
    if kind == "division":
        invalid = ParameterExpression("/", (p.expression(),zero))
    elif kind == "zero_product":
        invalid = ParameterExpression("*", (zero,invalid))
    elif kind == "equal_difference":
        invalid = ParameterExpression("-", (invalid,invalid))
    with pytest.raises((ValueError, ArithmeticError)):
        invalid.gradient(p)
    assert type(p.gradient(p)) is float and p.gradient(p) == 1.


def test_symbolic_ratio_zero_derivative_does_not_make_singular_source_bindable():
    p = Parameter("p")
    expression = p/p
    result = expression.gradient(p)
    assert type(result) is float and result == 0.
    with pytest.raises((ValueError, ArithmeticError)):
        expression.bind({p:0.})
    assert expression.bind({p:.31}) == 1.
