# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Native V2 binding arrays execute on the existing circuit/binding engine."""

from math import cos, sin

import numpy as np
import pytest

from quantumbridge import Circuit, Parameter, ParameterVector
from quantumbridge.devices import StatevectorDevice
import quantumbridge.primitives as primitives


@pytest.fixture
def bindings():
    return primitives.BindingsArray


def test_multidimensional_bindings_keep_parameter_axis_and_execute(bindings):
    theta, phi = Parameter("theta"), Parameter("phi")
    values = np.array([[[.23, .11], [.61, -.17]], [[.91, .37], [1.21, .53]]])
    circuit = Circuit(1).ry(theta, 0).rz(phi, 0)
    array = bindings({(theta, phi): values})
    assert array.shape == (2, 2)
    assert (array.ndim, array.size, array.num_parameters) == (2, 4, 2)
    np.testing.assert_array_equal(array.as_array([phi, theta]), values[..., ::-1])
    for loc in np.ndindex(array.shape):
        bound = array.bind(circuit, loc)
        t, p = values[loc]
        expected = np.array([cos(t/2)*np.exp(-.5j*p), sin(t/2)*np.exp(.5j*p)])
        np.testing.assert_allclose(StatevectorDevice().statevector(bound), expected, atol=3e-14, rtol=0)
    assert circuit.num_parameters == 2


@pytest.mark.parametrize("shape", [(), (3,), (2, 3), (0,), (2, 0)])
def test_single_parameter_missing_axis_and_explicit_shape(bindings, shape):
    values = np.arange(np.prod(shape), dtype=float).reshape(shape)
    array = bindings({"theta": values}, shape=shape)
    assert array.shape == shape
    assert array.as_array().shape == shape+(1,)
    np.testing.assert_array_equal(array.as_array()[..., 0], values)


@pytest.mark.parametrize("shape", [(), (0,), (2, 0), (2, 3)])
def test_parameterless_binding_sets_include_zero_axes(bindings, shape):
    array = bindings(shape=shape)
    assert array.shape == shape and array.num_parameters == 0
    assert array.as_array().shape == shape+(0,)
    result = array.bind_all(Circuit(1).x(0))
    assert result.shape == shape
    for circuit in result.flat:
        np.testing.assert_allclose(StatevectorDevice().statevector(circuit), [0, 1], atol=0, rtol=0)


def test_grouped_and_named_parameters_reorder_without_changing_identity(bindings):
    a, b, c = Parameter("a"), Parameter("b"), Parameter("c")
    values = bindings({(c, a): [[.3, .1], [.6, .4]], "b": [.2, .5]}, shape=(2,))
    np.testing.assert_array_equal(values.as_array([a, b, c]), [[.1, .2, .3], [.4, .5, .6]])
    circuit = Circuit(1).ry(a+b+c, 0)
    out = values.bind_all(circuit)
    assert out.shape == (2,) and all(x.num_parameters == 0 for x in out)
    for loc, angle in enumerate([.6, 1.5]):
        np.testing.assert_allclose(StatevectorDevice().statevector(out[loc]),
                                   [cos(angle/2), sin(angle/2)], atol=3e-14, rtol=0)


def test_parameter_vectors_and_repeated_uuid_share_existing_binding_rules(bindings):
    first, second = ParameterVector("a", 2), ParameterVector("b", 2)
    theta = Parameter("theta")
    same = Parameter("theta", uuid=theta.uuid)
    circuit = Circuit(1).ry(theta+same+first[0]+second[1], 0)
    array = bindings({(theta, first[0], second[1]): [[.1, .2, .3], [.4, .5, .6]]})
    assert array.num_parameters == circuit.num_parameters == 3
    for loc, angle in enumerate([.7, 1.9]):
        np.testing.assert_allclose(StatevectorDevice().statevector(array.bind(circuit, (loc,))),
                                   [cos(angle/2), sin(angle/2)], atol=3e-14, rtol=0)


def test_slicing_reshape_and_ravel_keep_binding_order(bindings):
    array = bindings({("a", "b"): np.arange(12.).reshape(2, 3, 2)})
    view = array.reshape(3, 2)
    assert view.shape == (3, 2) and view.ravel().shape == (6,)
    np.testing.assert_array_equal(view.as_array(), np.arange(12.).reshape(3, 2, 2))
    np.testing.assert_array_equal(array[1].as_array(), np.arange(6., 12.).reshape(3, 2))
    np.testing.assert_array_equal(array[:, 1:].as_array(), np.arange(12.).reshape(2, 3, 2)[:, 1:])
    assert array[1, 2].shape == ()
    assert array.reshape(-1).shape == (6,)
    assert array.reshape((1, 6)).shape == (1, 6)
    with pytest.raises(ValueError):
        array.reshape(5)


@pytest.mark.parametrize("data,shape", [
    ({("a", "b"): [1.]}, None),
    ({("a", "b"): [[1., 2.], [3., 4.]], "c": [1., 2., 3.]}, None),
    ({("a", "a"): [1., 2.]}, None),
    ({"a": [1.], ("a", "b"): [2., 3.]}, None),
    ({"a": [1., 2.]}, (3,)),
    ({"a": [[1.], [2., 3.]]}, None),
])
def test_inconsistent_parameter_groups_are_rejected(bindings, data, shape):
    names = [name for key in data for name in (key if isinstance(key, tuple) else (key,))]
    if len(set(names)) != len(names):
        # These two descriptions are now publicly representable, but the
        # original safety assertion remains at the execution boundary.
        with pytest.raises(ValueError, match="duplicate|ambiguous"):
            bindings(data, shape=shape).bind(Circuit(1), ())
        return
    with pytest.raises(ValueError):
        bindings(data, shape=shape)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), 1j])
def test_nonfinite_and_complex_bindings_do_not_reach_native_execution(bindings, value):
    with pytest.raises((ValueError, TypeError)):
        bindings({"a": value}).bind(Circuit(1).ry(Parameter("a"), 0), ())


@pytest.mark.parametrize("shape", [(-1,), (True,), (1.5,), (2**63,), (0, 2**63)])
def test_shape_validation_precedes_array_allocation(bindings, shape):
    with pytest.raises((ValueError, OverflowError, MemoryError)):
        bindings(shape=shape)


def test_requested_order_requires_every_parameter_once(bindings):
    array = bindings({("a", "b"): [1., 2.]})
    for order in (["a"], ["a", "a"], ["a", "c"], ["a", "b", "c"]):
        with pytest.raises(ValueError):
            array.as_array(order)


def test_binding_cannot_use_wrong_owner_with_equal_name(bindings):
    theta = Parameter("theta")
    alien = Parameter("theta")
    circuit = Circuit(1).ry(theta, 0)
    with pytest.raises(ValueError):
        bindings({alien: .5}).bind(circuit, ())
    assert circuit.num_parameters == 1


def test_bind_loc_requires_exact_integer_batch_coordinates(bindings):
    array = bindings({"a": [[.1], [.2]]})
    circuit = Circuit(1).ry(Parameter("a"), 0)
    for loc in ((), (0, 0), (True,), (.5,)):
        with pytest.raises((ValueError, TypeError, IndexError)):
            array.bind(circuit, loc)
    with pytest.raises(IndexError):
        array.bind(circuit, (2,))


def test_sampler_pub_coercion_precedence_shapes_and_real_binding(bindings):
    pub_type = primitives.SamplerPub
    theta = Parameter("theta")
    circuit = Circuit(1, 1).ry(theta, 0)
    circuit.measure(0, 0)
    values = np.array([[[0.], [.2]], [[.4], [.6]]])
    pub = pub_type.coerce((circuit, values, 13), shots=7)
    assert pub.circuit is circuit
    assert pub.shape == (2, 2) and pub.size == 4 and pub.ndim == 2
    assert pub.shots == 13
    assert pub_type.coerce(pub, shots=5) is pub
    assert pub_type.coerce((circuit, values), shots=7).shots == 7
    assert pub_type.coerce((circuit, values)).shots is None
    assert pub_type.coerce((Circuit(1),), shots=5).shape == ()
    assert pub_type.coerce(Circuit(1)).parameter_values.num_parameters == 0
    assert pub.parameter_values.bind(circuit, (1, 0)).num_parameters == 0


@pytest.mark.parametrize("shots", [0, -1, True, 1.5, "2"])
def test_sampler_pub_rejects_invalid_shots(shots):
    with pytest.raises((TypeError, ValueError)):
        primitives.SamplerPub(Circuit(1), shots=shots)


def test_sampler_pub_checks_full_binding_before_any_quantum_execution(bindings):
    a, b = Parameter("a"), Parameter("b")
    circuit = Circuit(1).ry(a+b, 0)
    with pytest.raises(ValueError):
        primitives.SamplerPub(circuit, bindings({a: .3}))
    with pytest.raises(ValueError):
        primitives.SamplerPub(circuit, bindings({(a, Parameter("other")): [.3, .4]})).parameter_values.bind(circuit, ())
    with pytest.raises(ValueError):
        primitives.SamplerPub.coerce((circuit, [[.3]]))
    for invalid in ((), (circuit, None, 3, 4), 3, "circuit"):
        with pytest.raises((TypeError, ValueError)):
            primitives.SamplerPub.coerce(invalid)


def test_pub_inputs_do_not_change_legacy_native_execution():
    result = primitives.Sampler(shots=16, seed=11).run([(Circuit(1).x(0),)])
    assert result.result() is result
    assert result.job_id() == "quantumbridge-primitive-result"
    assert result[0].data.meas.get_counts() == {"1": 16}

