# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Ordinary/default native dispatch must never select experimental handles."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.circuit_library import CRYGate
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.qml import QNode
from test_native_tf_managed_cached_execution import CASE, make_node, tf


def source_node(case, method):
    if case == "moving_projector":
        node, _ = make_node()
        node.diff_method = method
        return node, np.array(CASE["point"]), np.array(CASE["outputs"]), np.array(CASE["jacobian"])
    p = qb.Parameter("angle")
    source = qb.QuantumCircuit(2 if case in {"controlled_gate", "fixed_projector"} else 1)
    if case == "fixed_projector":
        source.h(0)
        source.append(CRYGate(p, ctrl_state=0).power(0.5, annotated=True), (0, 1))
        observables = (qb.PauliX(0),)
        expected, gradient = [np.cos(0.37/4)], [-np.sin(0.37/4)/4]
    else:
        gate = qb.Circuit(1).ry(p, 0).to_gate()
        if case == "controlled_gate":
            source.x(0)
            source.append(gate.control(1), (0, 1))
        elif case == "generic_gate":
            source.append(gate, (0,))
        else:
            source.ry(p, 0)
        target = source.num_qubits-1
        observables = (qb.PauliZ(target), qb.PauliX(target)) if case == "multi_output" else (qb.PauliZ(target),)
        expected, gradient = [np.cos(0.37), np.sin(0.37)][:len(observables)], [-np.sin(0.37), np.cos(0.37)][:len(observables)]
    first_builder = QNode.from_circuit(source, observables[0]).fn
    def program(tape, point):
        first = first_builder(tape, point)
        return (first, tape.expval(observables[1])) if len(observables) == 2 else first
    return QNode(program, source.num_qubits, interface="tensorflow", diff_method=method, max_diff=2), np.array(0.37), np.array(expected), np.array(gradient)


def forbid_experimental_selection(monkeypatch):
    from quantumbridge.interfaces.tensorflow_managed import ManagedTensorFlowQNode
    from quantumbridge.interfaces.tensorflow_inline import TraceInlineTensorFlowQNode
    def forbidden(*args, **kwargs):
        pytest.fail("Default dispatch selected an explicitly compiled experimental/inline handle")
    for cls in (ManagedTensorFlowQNode, TraceInlineTensorFlowQNode):
        monkeypatch.setattr(cls, "__init__", forbidden)
    monkeypatch.setattr(ManagedTensorFlowQNode, "_invoke", forbidden)


@pytest.mark.parametrize("case", ["ordinary_rotation", "generic_gate", "controlled_gate", "fixed_projector", "moving_projector", "multi_output"])
@pytest.mark.parametrize("method", ["best", "adjoint", "parameter-shift"])
def test_actual_default_dispatch_keeps_its_existing_math_and_method(case, method, monkeypatch):
    forbid_experimental_selection(monkeypatch)
    node, point, expected, jacobian = source_node(case, method)
    point = tf.constant(point, tf.float64)
    if case == "moving_projector" and method == "parameter-shift":
        from quantumbridge.interfaces.native_host import NativeHostKernel
        monkeypatch.setattr(NativeHostKernel, "run", lambda *a, **k: pytest.fail("Illegal method executed quantum work"))
        with pytest.raises(UnsupportedFeature, match="shift"):
            node(point)
        return
    with tf.GradientTape(persistent=True) as reverse:
        reverse.watch(point)
        values = tf.reshape(tf.stack(tf.nest.flatten(node(point))), (-1,))
    weighted = reverse.gradient(values, point, output_gradients=tf.ones_like(values))
    np.testing.assert_allclose(weighted, np.sum(jacobian, axis=0), atol=8e-11, rtol=0)
    if case != "moving_projector":
        assert node.last_metadata["gradient_method"] == ("adjoint" if method == "best" else method)
    derivative = reverse.jacobian(values, point)
    np.testing.assert_allclose(values, expected, atol=8e-12, rtol=0)
    np.testing.assert_allclose(derivative, jacobian, atol=8e-11, rtol=0)
    assert "execution_capability" not in node.last_metadata
    if case in {"ordinary_rotation", "generic_gate", "multi_output"} and method == "parameter-shift":
        assert node.last_metadata["shifted_evaluation_count"] == 2
        assert node.last_metadata["gradient_physical_shots"] == 0


@pytest.mark.parametrize("case", ["ordinary_rotation", "generic_gate", "controlled_gate", "fixed_projector", "moving_projector", "multi_output"])
def test_backprop_is_not_falsely_advertised_as_an_existing_native_simulator_path(case, monkeypatch):
    forbid_experimental_selection(monkeypatch)
    node, point, _, _ = source_node(case, "backprop")
    from quantumbridge.interfaces.native_host import NativeHostKernel
    monkeypatch.setattr(NativeHostKernel, "run", lambda *a, **k: pytest.fail("Unsupported backprop executed"))
    with pytest.raises(UnsupportedFeature, match="backprop"):
        node(tf.constant(point, tf.float64))
