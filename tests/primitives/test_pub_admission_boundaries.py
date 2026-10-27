# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Public container representation is separate from native execution admission."""
import numpy as np
import pytest

from quantumbridge import Circuit, Parameter
from quantumbridge.primitives import BindingsArray, SamplerPub


@pytest.mark.parametrize("data,expected", [
    ({("a", "a"): [1., 2.]}, [1., 2.]),
    ({"a": [1.], ("a", "b"): [2., 3.]}, [1., 2., 3.]),
])
def test_duplicate_descriptions_are_representable_but_not_ambiguous_execution(data, expected):
    values = BindingsArray(data)
    assert values.num_parameters == len(expected)
    np.testing.assert_array_equal(values.as_array(), expected)
    np.testing.assert_array_equal(values[()].reshape(1).ravel().as_array(), [expected])
    circuit = Circuit(1).ry(Parameter("a"), 0)
    with pytest.raises(ValueError, match="duplicate|ambiguous"):
        values.bind(circuit, ())


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
def test_nonfinite_values_survive_containers_but_never_bind_to_gates(value):
    a = Parameter("a")
    circuit = Circuit(1).ry(a, 0)
    values = BindingsArray({a: value})
    values.validate()
    np.testing.assert_equal(values.as_array(), [value])
    pub = SamplerPub(circuit, values)
    pub.validate()
    with pytest.raises(ValueError, match="finite"):
        pub.parameter_values.bind(circuit, ())


def test_wrong_names_are_a_pub_representation_not_an_execution_authorization():
    a, b, c = (Parameter(name) for name in ("a", "b", "c"))
    circuit = Circuit(1).ry(a+b, 0)
    pub = SamplerPub(circuit, BindingsArray({(a, c): [.1, .2]}))
    pub.validate()
    with pytest.raises(ValueError, match="parameters"):
        pub.parameter_values.bind(circuit, ())


def test_foreign_uuid_is_retained_across_container_views_and_denied_at_bind():
    owner, foreign = Parameter("theta"), Parameter("theta")
    circuit = Circuit(1).ry(owner, 0)
    pub = SamplerPub(circuit, BindingsArray({foreign: [[.1], [.2]]}))
    for values in (pub.parameter_values, pub.parameter_values[:], pub.parameter_values.reshape(2).ravel()):
        with pytest.raises(ValueError, match="UUID"):
            values.bind(circuit, (0,))


def test_duplicate_reordering_cannot_expose_uninitialized_columns():
    values = BindingsArray({"a": [1.], ("a", "b"): [2., 3.]})
    repeated = BindingsArray({("a", "a"): [1., 2.]})
    # Upstream advanced placement leaves some duplicate-order columns
    # uninitialized. Those bytes are not a reproducible numerical oracle.
    for array, order in ((values, ["b", "a", "a"]), (repeated, ["a", "a"])):
        with pytest.raises(ValueError, match="ambiguous"):
            array.as_array(order)


def test_normalized_key_collision_preserves_the_effective_original_owner():
    first, second = Parameter("a"), Parameter("a")
    values = BindingsArray({first: .1, second: .2})
    assert list(values.data) == [("a",)]
    np.testing.assert_array_equal(values.as_array(), [.2])
    with pytest.raises(ValueError, match="UUID"):
        values.bind(Circuit(1).ry(first, 0), ())
    assert values.bind(Circuit(1).ry(second, 0), ()).num_parameters == 0
