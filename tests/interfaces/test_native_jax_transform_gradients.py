# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.

import numpy as np
import pytest

from quantumbridge import Circuit, Parameter, PauliX, PauliZ, templates
from quantumbridge.qml import QNode
from quantumbridge.transforms import (TransformProgram, cancel_inverses, compile, defer_measurements,
                                     merge_rotations, split_non_commuting, transform)
from quantumbridge.utils.math import Hamiltonian


def framework():
    return pytest.importorskip("jax"), pytest.importorskip("jax.numpy")


def test_jax_real_multiple_child_tapes_and_reconstruction():
    jax, jnp = framework()
    @transform
    def branch(tape):
        a, b = tape.copy(), tape.copy()
        b.circuit.ry(.2, 0)
        return (a, b), lambda result: result[0] + 2 * result[1]
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.expval(PauliZ(0))
    node = branch(QNode(circuit, 1, interface="jax"))
    value, gradient = jax.value_and_grad(node)(jnp.asarray(.3))
    np.testing.assert_allclose(value, np.cos(.3) + 2 * np.cos(.5), atol=2e-6, rtol=0)
    np.testing.assert_allclose(gradient, -np.sin(.3) - 2 * np.sin(.5), atol=2e-6, rtol=0)
    assert node.last_metadata["executed_tape_count"] == 2


def test_jax_reverse_postprocessing_order_is_not_forward_stage_order():
    jax, jnp = framework()
    @transform
    def times_two(tape): return (tape,), lambda result: 2 * result[0]
    @transform
    def plus_three(tape): return (tape,), lambda result: result[0] + 3
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.expval(PauliZ(0))
    node = TransformProgram([times_two, plus_three])(QNode(circuit, 1, interface="jax"))
    value, gradient = jax.value_and_grad(node)(jnp.asarray(.3))
    np.testing.assert_allclose(value, 2 * (np.cos(.3) + 3), atol=2e-6, rtol=0)
    np.testing.assert_allclose(gradient, -2 * np.sin(.3), atol=2e-6, rtol=0)
    assert node.last_metadata["postprocessing_order"] == [1, 0]


def test_jax_cancel_merge_compile_and_qwc_preserve_live_source_chain():
    jax, jnp = framework()
    def circuit(tape, x):
        tape.x(0); tape.x(0)
        tape.ry(jnp.sin(x), 0); tape.ry(2 * x, 0)
        return tape.expval(Hamiltonian([(.7, PauliZ(0)), (.2, PauliX(0))]))
    node = TransformProgram([cancel_inverses, merge_rotations, compile(basis_set={"RY", "RZ", "CX"}),
                             split_non_commuting])(QNode(circuit, 1, interface="jax"))
    angle = np.sin(.3) + .6
    expected = (-.7 * np.sin(angle) + .2 * np.cos(angle)) * (2 + np.cos(.3))
    np.testing.assert_allclose(jax.grad(node)(jnp.asarray(.3)), expected, atol=2e-6, rtol=0)
    assert node.last_metadata["transform_count"] == 4


def test_jax_deferred_reused_wire_gradients_use_real_record_ancilla():
    jax, jnp = framework()
    def circuit(tape, x):
        tape.ry(x, 0)
        record = tape.measure(0)
        tape.h(0)
        tape.cond(record, lambda branch: branch.x(1))
        return tape.expval(PauliZ(1))
    node = split_non_commuting(defer_measurements(QNode(circuit, 2, interface="jax", diff_method="parameter-shift")))
    value, gradient = jax.value_and_grad(node)(jnp.asarray(.3))
    np.testing.assert_allclose(value, np.cos(.3), atol=2e-6, rtol=0)
    np.testing.assert_allclose(gradient, -np.sin(.3), atol=2e-6, rtol=0)
    assert node.last_metadata["deferred_measurements"][0]["ancilla_count"] == 1


def test_jax_record_only_probability_gradient_survives_measured_wire_change():
    jax, jnp = framework()
    def circuit(tape, x):
        tape.ry(x, 0)
        record = tape.measure(0)
        tape.h(0)
        return tape.probs(records=[record])
    node = defer_measurements(QNode(circuit, 1, interface="jax", diff_method="parameter-shift"))
    np.testing.assert_allclose(jax.grad(lambda x: node(x)["1"])(jnp.asarray(.3)), .5 * np.sin(.3), atol=2e-6, rtol=0)


def test_jax_serializable_native_circuit_parameter_reconstruction():
    jax, jnp = framework()
    theta = Parameter("theta")
    node = QNode.from_circuit(Circuit(1).ry(theta * 2, 0), PauliZ(0), interface="jax")
    np.testing.assert_allclose(jax.grad(node)(jnp.asarray(.3)), -2 * np.sin(.6), atol=2e-6, rtol=0)


def test_jax_fresh_coefficient_primals_are_not_rebound_into_stale_grouping():
    jax, jnp = framework()
    def circuit(tape, x):
        tape.ry(.4, 0)
        return tape.expval(Hamiltonian([(x, PauliX(0)), (x * x, PauliZ(0))]))
    node = split_non_commuting(QNode(circuit, 1, interface="jax"))
    for x in [.1, -.6, 0.]:
        value, gradient = jax.value_and_grad(node)(jnp.asarray(x))
        np.testing.assert_allclose(value, x * np.sin(.4) + x * x * np.cos(.4), atol=2e-6, rtol=0)
        np.testing.assert_allclose(gradient, np.sin(.4) + 2 * x * np.cos(.4), atol=2e-6, rtol=0)


def test_jax_nested_input_pytree_uses_each_leaf_and_keeps_unused_gradient_zero():
    jax, jnp = framework()
    def circuit(tape, values):
        tape.ry(values["angles"][0] + 2 * values["angles"][1], 0)
        return tape.expval(PauliZ(0))
    node = split_non_commuting(QNode(circuit, 1, interface="jax"))
    values = {"angles": [jnp.asarray(.2), jnp.asarray(.3)], "unused": jnp.asarray(.4)}
    result = jax.grad(node)(values)
    np.testing.assert_allclose(result["angles"], -np.sin(.8) * np.array([1., 2.]), atol=2e-6, rtol=0)
    assert result["unused"] == 0


def test_jax_template_arrays_and_nontrainable_inputs_remain_immutable():
    jax, jnp = framework()
    def circuit(tape, weights, bits):
        templates.BasisEmbedding(bits, [0, 1]).apply(tape)
        templates.AngleEmbedding(weights, [0, 1], rotation="Y").apply(tape)
        return tape.expval(PauliZ(0).tensor(PauliZ(1)))
    node = QNode(circuit, 2, interface="jax")
    values = jnp.asarray([.2, .3]); before = np.array(values)
    bits = [1, 0]
    result = jax.grad(lambda x: node(x, bits))(values)
    np.testing.assert_allclose(result, [np.sin(.2) * np.cos(.3), np.cos(.2) * np.sin(.3)], atol=2e-6, rtol=0)
    np.testing.assert_array_equal(values, before)
    assert bits == [1, 0]


def test_jax_native_adjoint_and_parameter_shift_are_both_actually_selected():
    jax, jnp = framework()
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.expval(PauliZ(0))
    for method in ("adjoint", "parameter-shift"):
        node = split_non_commuting(QNode(circuit, 1, interface="jax", diff_method=method))
        np.testing.assert_allclose(jax.grad(node)(jnp.asarray(.3)), -np.sin(.3), atol=2e-6, rtol=0)
        assert node.last_metadata["gradient_method"] == method


def test_jax_analytic_variance_derivative_is_not_mean_derivative():
    jax, jnp = framework()
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.var(PauliZ(0))
    node = QNode(circuit, 1, interface="jax", diff_method="parameter-shift")
    np.testing.assert_allclose(jax.grad(node)(jnp.asarray(.3)), np.sin(.6), atol=2e-6, rtol=0)


def test_jax_native_density_device_uses_native_shift_not_statevector_adjoint():
    jax, jnp = framework()
    from quantumbridge import DensityMatrixDevice
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.expval(PauliZ(0))
    node = QNode(circuit, 1, interface="jax", device=DensityMatrixDevice())
    np.testing.assert_allclose(jax.grad(node)(jnp.asarray(.3)), -np.sin(.3), atol=2e-6, rtol=0)
    assert node.last_metadata["gradient_method"] == "parameter-shift"
