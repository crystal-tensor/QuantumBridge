# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Runtime checks and static local admission, not full Device/AD accounting."""

import math

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.core.gate_limits import GateCircuitLimits, gate_circuit_scope
from quantumbridge.interfaces.tensorflow_native_execution import TensorFlowLocalOperator
from quantumbridge.qml import QNode

tf = pytest.importorskip("tensorflow")


def make_kernel(*, primitive=None, modifiers=(), control=None, bind=False):
    p, q = qb.ParameterVector("angles", 2)
    body = qb.Circuit(1).rx(p, 0).rz(q, 0)
    if primitive is not None:
        name, values = primitive
        if values is None:
            values = (p*q,)
        body.append(name, (0,), params=values)
    operation = body.to_gate().power(0.5, annotated=True)
    for kind, value in modifiers:
        operation = operation.inverse() if kind == "inverse" else operation.power(value, annotated=True)
    width = 1
    if control is not None:
        width += control[0]
        operation = operation.control(control[0], ctrl_state=control[1])
    source = qb.QuantumCircuit(width)
    source.append(operation, range(width))
    if bind:
        source = source.assign_parameters({q: 0.82})
    point = np.array([0.37] if bind else [0.37, 0.82])
    plan = QNode.from_circuit(source, qb.PauliZ(width-1), max_diff=2)._construct((point,), {})
    return TensorFlowLocalOperator(plan, 0), plan, point, source


@pytest.mark.parametrize("bad", ["nan", "inf", "cut"])
def test_one_concrete_graph_checks_each_runtime_point_without_retracing(bad):
    kernel, _, point, _ = make_kernel()
    fn = tf.function(kernel, input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False, jit_compile=False)
    first = fn(tf.constant(point, tf.float64))
    invalid = [float("nan"), 0.82] if bad == "nan" else [0.37, float("inf")] if bad == "inf" else [0., 2*math.pi]
    with pytest.raises(tf.errors.InvalidArgumentError, match="Nonfinite|branch/cubic"):
        fn(tf.constant(invalid, tf.float64))
    np.testing.assert_array_equal(fn(tf.constant(point, tf.float64)), first)
    assert fn.experimental_get_tracing_count() == 1


@pytest.mark.parametrize("bad", [tf.constant([0.37], tf.float64), tf.constant([0.37, 0.82], tf.float32), tf.constant([[0.37, 0.82]], tf.float64)])
def test_invalid_inputs_refuse_before_matrix_allocation(bad, monkeypatch):
    kernel, _, _, _ = make_kernel()
    monkeypatch.setattr(tf, "eye", lambda *a, **k: pytest.fail("Invalid shape/dtype allocated a local matrix"))
    with pytest.raises(ValueError, match="static float64"):
        kernel(bad)


@pytest.mark.parametrize("field,value", [("max_matrix_dimension", 4), ("max_decomposition_work", 1)])
def test_reused_kernel_rechecks_tightened_construction_limits(field, value, monkeypatch):
    kernel, _, point, source = make_kernel()
    before = source.to_ir().to_json()
    vector = tf.constant(point, tf.float64)
    monkeypatch.setattr(tf, "eye", lambda *a, **k: pytest.fail("Over-budget local matrix allocation"))
    with gate_circuit_scope(GateCircuitLimits(**{field: value})), pytest.raises(MemoryError, match=field):
        kernel(vector)
    assert source.to_ir().to_json() == before


def test_current_memory_scope_rejects_before_local_tensor_allocation(monkeypatch):
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
    from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
    kernel, _, point, source = make_kernel()
    before = source.to_ir().to_json()
    vector = tf.constant(point, tf.float64)
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=0))
    monkeypatch.setattr(tf, "eye", lambda *a, **k: pytest.fail("Over-budget TF allocation"))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        kernel(vector)
    receipt = ledger.receipt()
    assert receipt["consumed_tapes"] == receipt["consumed_shots"] == receipt["consumed_derivative_work"] == receipt["live_memory_bytes"] == 0
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("primitive", [("x", ()), ("y", ()), ("z", ()), ("h", ()), ("id", ()), ("s", ()), ("sdg", ()), ("t", ()), ("tdg", ()), ("sx", ()), ("sxdg", ()), ("p", (0.19,)), ("u1", (0.19,)), ("u2", (0.19, -0.27)), ("u3", (0.43, 0.19, -0.27)), ("u", (0.43, 0.19, -0.27)), ("global_phase", (0.19,))])
def test_fixed_primitive_determinant_phase_matches_independent_scalar_spectrum(primitive):
    from quantumbridge.utils.math import gate_matrix
    kernel, _, point, _ = make_kernel(primitive=primitive)
    p, q = point
    rx = np.array([[np.cos(p/2), -1j*np.sin(p/2)], [-1j*np.sin(p/2), np.cos(p/2)]])
    rz = np.diag([np.exp(-0.5j*q), np.exp(0.5j*q)])
    name, values = primitive
    local = np.exp(1j*values[0])*np.eye(2) if name == "global_phase" else gate_matrix(name, values)
    full = local @ rz @ rx
    eigenvalues, vectors = np.linalg.eig(full)
    expected = vectors @ np.diag(np.exp(0.5j*np.angle(eigenvalues))) @ np.linalg.inv(vectors)
    np.testing.assert_allclose(kernel(tf.constant(point, tf.float64)), expected, atol=2e-12, rtol=0)


@pytest.mark.parametrize("modifiers", [(("inverse", None),), (("power", 2.),), (("power", -3.),), (("inverse", None), ("power", -2.))])
def test_modifier_order_after_fractional_power_matches_native_frechet_value_and_directions(modifiers):
    from quantumbridge.diff.matrix_power_jet import matrix_power_directions
    kernel, plan, point, _ = make_kernel(modifiers=modifiers)
    operation = plan.circuit.lowered().operations[0]
    expected = matrix_power_directions(point, operation.metadata, [0.4, -0.3], [-0.2, 0.6])
    point = tf.constant(point, tf.float64)
    with tf.autodiff.ForwardAccumulator(point, tf.constant([-0.2, 0.6], tf.float64)) as outer:
        with tf.autodiff.ForwardAccumulator(point, tf.constant([0.4, -0.3], tf.float64)) as inner:
            matrix = kernel(point)
        first = inner.jvp(matrix)
    for actual, reference in [(matrix, expected[0]), (first, expected[1]), (outer.jvp(first), expected[3])]:
        assert actual is not None
        np.testing.assert_allclose(actual, reference, atol=3e-10, rtol=0)


@pytest.mark.parametrize("control", [(2, "01"), (2, "10"), (2, "00"), (2, "11")])
def test_multibit_open_control_uses_existing_little_endian_control_state(control):
    from quantumbridge.diff.matrix_power_jet import matrix_power_value
    kernel, plan, point, _ = make_kernel(control=control)
    operation = plan.circuit.lowered().operations[0]
    expected = matrix_power_value(point, operation.metadata)
    np.testing.assert_allclose(kernel(tf.constant(point, tf.float64)), expected, atol=2e-12, rtol=0)


def test_partial_binding_keeps_existing_plan_parameter_identity():
    from quantumbridge.diff.matrix_power_jet import matrix_power_value
    kernel, plan, point, _ = make_kernel(bind=True)
    operation = plan.circuit.lowered().operations[0]
    assert kernel.input_size == len(kernel.source_parameter_uuids) == 1
    expected = matrix_power_value(point, operation.metadata)
    np.testing.assert_allclose(kernel(tf.constant(point, tf.float64)), expected, atol=2e-12, rtol=0)


def test_repeated_principal_fractional_power_is_explicitly_unvalidated():
    with pytest.raises(UnsupportedFeature, match="Sequential principal fractional"):
        make_kernel(modifiers=(("power", 0.5),))


def test_parameter_dependent_determinant_phase_preserves_both_complex_mixed_terms():
    from quantumbridge.diff.matrix_power_jet import matrix_power_directions
    kernel, plan, point, _ = make_kernel(primitive=("p", None))
    operation = plan.circuit.lowered().operations[0]
    expected = matrix_power_directions(point, operation.metadata, [0.4, -0.3], [-0.2, 0.6])
    point = tf.constant(point, tf.float64)
    with tf.autodiff.ForwardAccumulator(point, tf.constant([-0.2, 0.6], tf.float64)) as outer:
        with tf.autodiff.ForwardAccumulator(point, tf.constant([0.4, -0.3], tf.float64)) as inner:
            matrix = kernel(point)
        first = inner.jvp(matrix)
    for actual, reference in [(matrix, expected[0]), (first, expected[1]), (outer.jvp(first), expected[3])]:
        assert actual is not None
        np.testing.assert_allclose(actual, reference, atol=3e-10, rtol=0)


def test_owned_kernel_is_not_changed_by_later_source_or_plan_mutation():
    kernel, plan, point, source = make_kernel()
    vector = tf.constant(point, tf.float64)
    before = kernel(vector)
    source.operations.clear()
    plan.circuit.operations.clear()
    np.testing.assert_array_equal(kernel(vector), before)
