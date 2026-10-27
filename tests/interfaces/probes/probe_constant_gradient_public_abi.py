# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Real SDK return ABI, formal UUIDs and numerical semantics, without coercion."""

import pytest

from tests.core.test_native_constant_gradient_api import CASES, CONSTANTS, SYMBOLIC, gradient_case, value_at_point


@pytest.mark.parametrize("case", CASES)
def test_actual_sdk_gradient_return_type_identity_and_math(case):
    pytest.importorskip("qiskit")
    from qiskit.circuit import Parameter, ParameterVector, ParameterExpression
    public, public_ids = gradient_case(case, Parameter, ParameterVector)
    native, native_ids = gradient_case(case)
    if case in CONSTANTS:
        expected_type, value = CONSTANTS[case]
        assert type(public) is expected_type and public == value
        assert type(native) is type(public)
        assert native == public
    else:
        names, value = SYMBOLIC[case]
        assert isinstance(public, ParameterExpression)
        assert type(native).__name__ == type(public).__name__
        assert {p.name for p in public.parameters} == {p.name for p in native.parameters} == names
        for result, identities in ((public,public_ids),(native,native_ids)):
            assert all(str(p.uuid) == str(identities[p.name].uuid) for p in result.parameters)
            assert value_at_point(result) == pytest.approx(value, abs=5e-15, rel=0)
            first = sorted(result.parameters,key=lambda p:p.name)[0]
            replacement = type(identities["p"])("renamed")
            renamed = result.subs({first:replacement})
            assert {p.name for p in renamed.parameters} == names-{first.name}|{"renamed"}
