# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Real managed eager calls, not trace-time Python side-effect accounting."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
from quantumbridge.qml import QNode

tf = pytest.importorskip("tensorflow")


def make_node(**options):
    source = qb.QuantumCircuit(1)
    theta, phi = qb.ParameterVector("angles", 2)
    body = qb.Circuit(1).ry(theta, 0).rz(phi, 0)
    source.append(body.to_gate().power(0.5, annotated=True), (0,))
    return QNode.from_circuit(source, qb.PauliZ(0), interface="tensorflow", max_diff=2, **options), source


def forbid_host(monkeypatch):
    from quantumbridge.interfaces.native_host import NativeHostKernel
    def forbidden(*a, **k):
        pytest.fail("Managed tensor execution used a host quantum callback")
    monkeypatch.setattr(NativeHostKernel, "run", forbidden)
    monkeypatch.setattr(NativeHostKernel, "run_second", forbidden)
    monkeypatch.setattr(tf, "numpy_function", forbidden)
    monkeypatch.setattr(tf, "py_function", forbidden)


def test_real_eager_value_vjp_and_hvp_share_the_existing_parent_ledger(monkeypatch):
    forbid_host(monkeypatch)
    node, source = make_node()
    before = source.to_ir().to_json()
    point = tf.constant([0.37, 0.], tf.float64)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        with tf.autodiff.ForwardAccumulator(point, tf.constant([0.4, 0.], tf.float64)) as forward:
            with tf.GradientTape() as reverse:
                reverse.watch(point)
                value = node(point)
            gradient = reverse.gradient(value, point)
        product = forward.jvp(gradient)
    np.testing.assert_allclose(value, np.cos(0.37/2), atol=2e-12, rtol=0)
    np.testing.assert_allclose(gradient, [-0.5*np.sin(0.37/2), 0.], atol=2e-12, rtol=0)
    np.testing.assert_allclose(product, [-0.1*np.cos(0.37/2), 0.], atol=2e-12, rtol=0)
    receipt = ledger.receipt()
    assert receipt["consumed_derivative_work"] > 0
    assert receipt["consumed_tapes"] > 0
    assert receipt["consumed_shots"] == receipt["live_memory_bytes"] == 0
    assert source.to_ir().to_json() == before


def test_repeated_eager_calls_really_charge_more_than_the_first_trace(monkeypatch):
    forbid_host(monkeypatch)
    node, _ = make_node()
    point = tf.constant([0.37, 0.], tf.float64)
    ledger = UnifiedResourceLedger()
    counts = []
    with ResourceScope(ledger):
        for _ in range(3):
            node(point)
            counts.append(ledger.receipt()["consumed_derivative_work"])
    assert 0 < counts[0] < counts[1] < counts[2]
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("field", ["max_total_memory_bytes", "max_total_tapes", "max_derivative_work"])
def test_unified_limits_refuse_before_the_first_tensor_quantum_update(field, monkeypatch):
    from quantumbridge.interfaces.tensorflow_whole_execution import TensorFlowStatevectorPlan
    def forbidden(*a, **k):
        pytest.fail("Zero-budget request reached quantum tensor execution")
    monkeypatch.setattr(TensorFlowStatevectorPlan, "values", forbidden)
    node, source = make_node(unified_limits=UnifiedExecutionLimits(**{field: 0}))
    before = source.to_ir().to_json()
    with pytest.raises(MemoryError):
        node(tf.constant([0.37, 0.], tf.float64))
    assert source.to_ir().to_json() == before


def test_unified_limits_use_native_tensor_execution_in_eager_mode(monkeypatch):
    forbid_host(monkeypatch)
    node, _ = make_node(unified_limits=UnifiedExecutionLimits())
    value = node(tf.constant([0.37, 0.], tf.float64))
    np.testing.assert_allclose(value, np.cos(0.37/2), atol=2e-12, rtol=0)
    assert node.last_metadata["tensor_resource_contract"]["controlled_execution"] == "LEDGER_ACCOUNTED"
    assert node.last_metadata["tensor_resource_receipt"]["consumed_derivative_work"] > 0


def test_nested_same_ledger_scope_is_not_a_separate_tf_account(monkeypatch):
    forbid_host(monkeypatch)
    ledger = UnifiedResourceLedger()
    node, _ = make_node()
    point = tf.constant([0.37, 0.], tf.float64)
    with ResourceScope(ledger):
        node(point)
        before = ledger.receipt()["consumed_derivative_work"]
        with ResourceScope(ledger):
            node(point)
        assert ledger.receipt()["consumed_derivative_work"] > before
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_managed_concrete_function_remains_explicitly_unsupported_not_trace_charged():
    node, _ = make_node(unified_limits=UnifiedExecutionLimits())
    graph = tf.function(node, autograph=False, jit_compile=False)
    with pytest.raises(UnsupportedFeature, match="graph"):
        graph(tf.constant([0.37, 0.], tf.float64))


def test_failed_eager_attempt_releases_reservations_but_not_spent_planned_work():
    ledger = UnifiedResourceLedger()
    node, _ = make_node()
    with ResourceScope(ledger):
        with pytest.raises(tf.errors.InvalidArgumentError):
            node(tf.constant([float("nan"), 0.], tf.float64))
        failed = ledger.receipt()
        assert failed["consumed_derivative_work"] > 0
        assert failed["consumed_tapes"] == 0
        assert failed["reserved_derivative_work"] == 0
        value = node(tf.constant([0.37, 0.], tf.float64))
        np.testing.assert_allclose(value, np.cos(0.37/2), atol=2e-12, rtol=0)
        assert ledger.receipt()["consumed_tapes"] > 0
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_eager_deferred_gradient_keeps_its_original_ledger_after_scope_exit():
    ledger = UnifiedResourceLedger()
    node, _ = make_node()
    point = tf.constant([0.37, 0.], tf.float64)
    with tf.GradientTape() as reverse:
        reverse.watch(point)
        with ResourceScope(ledger):
            value = node(point)
    before = ledger.receipt()["consumed_derivative_work"]
    gradient = reverse.gradient(value, point)
    np.testing.assert_allclose(gradient, [-0.5*np.sin(0.37/2), 0.], atol=2e-12, rtol=0)
    assert ledger.receipt()["consumed_derivative_work"] > before
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_deferred_derivative_cannot_bypass_an_unrelated_active_scope():
    owner, foreign = UnifiedResourceLedger(), UnifiedResourceLedger()
    node, _ = make_node()
    point = tf.constant([0.37, 0.], tf.float64)
    with tf.GradientTape() as reverse:
        reverse.watch(point)
        with ResourceScope(owner):
            value = node(point)
    before = owner.receipt()["consumed_derivative_work"]
    with ResourceScope(foreign), pytest.raises(UnsupportedFeature, match="unrelated"):
        reverse.gradient(value, point)
    assert owner.receipt()["consumed_derivative_work"] == before
    assert foreign.receipt()["consumed_derivative_work"] == 0


def test_parent_and_child_unified_caps_share_one_cumulative_tree():
    parent = UnifiedResourceLedger()
    node, _ = make_node(unified_limits=UnifiedExecutionLimits())
    with ResourceScope(parent):
        node(tf.constant([0.37, 0.], tf.float64))
    child = node.last_metadata["tensor_resource_receipt"]
    assert 0 < child["consumed_derivative_work"] == parent.receipt()["consumed_derivative_work"]
    assert child["live_memory_bytes"] == parent.receipt()["live_memory_bytes"] == 0


def test_two_actual_concurrent_nodes_cannot_overreserve_the_shared_workspace(monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from quantumbridge.interfaces.tensorflow_whole_execution import TensorFlowStatevectorPlan
    node, _ = make_node()
    point = tf.constant([0.37, 0.], tf.float64)
    node(point)
    memory = node.last_metadata["tensor_plan_work"]["workspace_bytes"]
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=memory*3//2))
    entered, release = Event(), Event()
    evaluate = TensorFlowStatevectorPlan.values
    def held(self, values):
        entered.set()
        assert release.wait(30), "The test must release the held real execution"
        return evaluate(self, values)
    monkeypatch.setattr(TensorFlowStatevectorPlan, "values", held)
    def first():
        with ResourceScope(ledger):
            return node(point)
    with ThreadPoolExecutor(max_workers=1) as workers:
        pending = workers.submit(first)
        try:
            assert entered.wait(30), "The first actual request did not reach admitted execution"
            with ResourceScope(ledger), pytest.raises(MemoryError):
                make_node()[0](point)
        finally:
            release.set()
        np.testing.assert_allclose(pending.result(timeout=30), np.cos(0.37/2), atol=2e-12, rtol=0)
    receipt = ledger.receipt()
    assert receipt["live_memory_bytes"] == receipt["reserved_derivative_work"] == 0
    assert receipt["consumed_tapes"] == 1


@pytest.mark.parametrize("kind", ["cotangent", "direction"])
def test_nonfinite_derivative_seed_is_a_real_runtime_failure(kind):
    node, _ = make_node()
    point = tf.constant([0.37, 0.], tf.float64)
    if kind == "cotangent":
        with tf.GradientTape() as reverse:
            reverse.watch(point)
            value = node(point)
        with pytest.raises(tf.errors.InvalidArgumentError, match="Nonfinite"):
            reverse.gradient(value, point, output_gradients=tf.constant(float("inf"), tf.float64))
    else:
        with pytest.raises(tf.errors.InvalidArgumentError, match="Nonfinite"):
            with tf.autodiff.ForwardAccumulator(point, tf.constant([float("nan"), 0.], tf.float64)):
                with tf.GradientTape() as reverse:
                    reverse.watch(point)
                    value = node(point)
                reverse.gradient(value, point)


def test_mutable_metadata_cannot_reduce_a_deferred_derivative_reservation():
    node, _ = make_node()
    point = tf.constant([0.37, 0.], tf.float64)
    ledger = UnifiedResourceLedger()
    with tf.GradientTape() as reverse:
        reverse.watch(point)
        with ResourceScope(ledger):
            value = node(point)
    before = ledger.receipt()["consumed_derivative_work"]
    node.last_metadata["tensor_plan_work"]["planned_work"] = 0
    node.last_metadata["tensor_plan_work"]["workspace_bytes"] = 0
    reverse.gradient(value, point)
    assert ledger.receipt()["consumed_derivative_work"] > before
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_eight_parameter_two_output_streamed_hvp_does_not_request_full_hessian(monkeypatch):
    from quantumbridge.diff import HigherOrderLimits
    parameters = qb.ParameterVector("eight", 8)
    body = qb.Circuit(1)
    for index, parameter in enumerate(parameters):
        (body.rx if index % 2 else body.rz)(parameter, 0)
    source = qb.QuantumCircuit(1)
    source.append(body.to_gate().power(0.5, annotated=True), (0,))
    point, direction = np.linspace(-0.3, 0.4, 8), np.linspace(0.2, -0.1, 8)
    limits = HigherOrderLimits(max_hessian_elements=1)
    expected = []
    for observable in (qb.PauliZ(0), qb.PauliX(0)):
        native = QNode.from_circuit(source, observable, max_diff=2, diff_method="adjoint", higher_order_limits=limits)
        expected.append(native.compute_hvp(direction, point))
    builder = QNode.from_circuit(source, qb.PauliZ(0)).fn
    def program(tape, values):
        return builder(tape, values), tape.expval(qb.PauliX(0))
    node = QNode(program, 1, interface="tensorflow", max_diff=2, higher_order_limits=limits)
    forbid_host(monkeypatch)
    def forbidden(*a, **k):
        pytest.fail("A directional rule requested a complete Hessian")
    monkeypatch.setattr(QNode, "compute_hessian", forbidden)
    monkeypatch.setattr(tf.GradientTape, "jacobian", forbidden)
    x, d = tf.constant(point, tf.float64), tf.constant(direction, tf.float64)
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_derivative_work=1_000_000_000))
    with ResourceScope(ledger):
        with tf.autodiff.ForwardAccumulator(x, d) as forward:
            with tf.GradientTape() as reverse:
                reverse.watch(x)
                result = tf.stack(node(x))
            gradient = reverse.gradient(result, x, output_gradients=tf.constant([0.7, -0.2], tf.float64))
        actual = forward.jvp(gradient)
    np.testing.assert_allclose(actual, np.array(expected).T @ [0.7, -0.2], atol=2e-9, rtol=0)
    assert ledger.receipt()["consumed_derivative_work"] > 0


def test_cached_mixed_graph_rechecks_every_runtime_input_without_claiming_python_accounting():
    import math
    node, source = make_node()
    before = source.to_ir().to_json()
    @tf.function(input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False, jit_compile=False)
    def graph(point):
        with tf.autodiff.ForwardAccumulator(point, tf.constant([0.4, 0.], tf.float64)) as forward:
            with tf.GradientTape() as reverse:
                reverse.watch(point)
                value = node(point)
                loss = (value-0.3)**2
            gradient = reverse.gradient(loss, point)
        return value, gradient, forward.jvp(gradient)
    point = tf.constant([0.37, 0.], tf.float64)
    reference = graph(point)
    value, gradient = np.cos(0.37/2), -0.5*np.sin(0.37/2)
    np.testing.assert_allclose(reference[0], value, atol=2e-12, rtol=0)
    np.testing.assert_allclose(reference[1], [2*(value-0.3)*gradient, 0.], atol=2e-12, rtol=0)
    np.testing.assert_allclose(reference[2], [0.4*(2*gradient**2-0.5*(value-0.3)*value), 0.], atol=2e-9, rtol=0)
    for invalid in ([float("nan"), 0.], [float("inf"), 0.], [0., 2*math.pi]):
        with pytest.raises(tf.errors.InvalidArgumentError):
            graph(tf.constant(invalid, tf.float64))
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        final = graph(point)
    for actual, expected in zip(final, reference):
        np.testing.assert_array_equal(actual, expected)
    assert graph.experimental_get_tracing_count() == 1
    assert source.to_ir().to_json() == before
    assert ledger.receipt()["consumed_derivative_work"] == 0
    assert node.last_metadata["tensor_resource_contract"]["controlled_execution"] == "OUT_OF_SCOPE"


def test_managed_async_mode_refuses_instead_of_committing_queued_work(monkeypatch):
    from quantumbridge.interfaces.tensorflow_whole_execution import TensorFlowStatevectorPlan
    node, _ = make_node()
    ledger = UnifiedResourceLedger()
    monkeypatch.setattr(tf.config.experimental, "get_synchronous_execution", lambda: False)
    def forbidden(*a, **k):
        pytest.fail("An unsupported asynchronous request reached quantum execution")
    monkeypatch.setattr(TensorFlowStatevectorPlan, "values", forbidden)
    with ResourceScope(ledger), pytest.raises(UnsupportedFeature, match="synchronous"):
        node(tf.constant([0.37, 0.], tf.float64))
    assert ledger.receipt()["consumed_tapes"] == ledger.receipt()["consumed_derivative_work"] == 0
