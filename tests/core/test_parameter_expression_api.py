import math

import numpy as np
import pytest

from quantumbridge.core import Circuit, Parameter, ParameterExpression, ParameterVector
from quantumbridge.devices import StatevectorDevice


def test_parameter_expression_arithmetic_and_binding():
    theta = Parameter("theta")
    phi = Parameter("phi")

    expr = theta + 2 * phi - 0.25

    assert isinstance(expr, ParameterExpression)
    assert expr.parameters == frozenset({theta, phi})
    assert expr.bind({theta: 1.0, "phi": 2.0}) == pytest.approx(4.75)
    assert str(theta) == "theta"


def test_parameter_expression_partial_binding_preserves_free_parameters():
    theta = Parameter("theta")
    phi = Parameter("phi")
    expr = (theta + phi) / 2

    partial = expr.bind({theta: 0.5}, allow_partial=True)

    assert isinstance(partial, ParameterExpression)
    assert partial.parameters == frozenset({phi})
    assert partial.bind({phi: 1.5}) == pytest.approx(1.0)


def test_parameter_vector_and_circuit_sequence_binding_execute():
    params = ParameterVector("theta", 2)
    circuit = Circuit(1)
    circuit.rx(params[0], 0)
    circuit.ry(params[1], 0)

    assert tuple(parameter.name for parameter in circuit.parameters) == ("theta[0]", "theta[1]")
    assert circuit.num_parameters == 2

    bound = circuit.assign_parameters([0.0, math.pi])
    assert bound.parameters == ()

    state = StatevectorDevice().run(bound).state
    assert np.allclose(np.abs(state) ** 2, [0.0, 1.0], atol=1e-10)


def test_circuit_partial_binding_keeps_remaining_parameter_and_ir_expression():
    theta = Parameter("theta")
    phi = Parameter("phi")
    circuit = Circuit(1)
    circuit.rx(theta + phi, 0)
    circuit.rz(phi, 0)

    partial = circuit.assign_parameters({theta: 0.25}, strict=False)

    assert tuple(parameter.name for parameter in partial.parameters) == ("phi",)
    ir = partial.to_ir().to_dict()
    assert ir["instructions"][0]["params"][0]["parameters"] == ["phi"]


def test_strict_binding_rejects_unknown_or_unbound_parameters():
    theta = Parameter("theta")
    circuit = Circuit(1).rx(theta, 0)

    with pytest.raises(ValueError, match="unknown parameter"):
        circuit.assign_parameters({"other": 0.2})
    with pytest.raises(ValueError, match="not bound"):
        circuit.assign_parameters({})
