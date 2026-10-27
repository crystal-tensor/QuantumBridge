# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""New matrix payloads share the existing owner and bounded execution contracts."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
from quantumbridge.interfaces.tensorflow_mps_execution import TensorFlowMPSPlan
from quantumbridge.qml import QNode
from quantumbridge.utils.math import gate_matrix
from test_native_tf_mps_exact_closure import POINT, fixture, tf
from test_native_tf_mps_resource_contract import request


@pytest.fixture(scope="module")
def compiled():
    source, node = fixture(4, 2, interface="tensorflow")
    node.higher_order_limits = HigherOrderLimits(max_hessian_elements=1)
    return source, node, node.compile_tensorflow(
        input_signature=[tf.TensorSpec((2,), tf.float64)])


@pytest.mark.parametrize("kind", ["value", "jvp", "hvp"])
@pytest.mark.parametrize("field,key", [
    ("max_total_memory_bytes", "required_memory_bytes"),
    ("max_derivative_work", "first_call_work"),
    ("max_total_tapes", "logical_evaluations")])
@pytest.mark.parametrize("difference", [0, -1])
def test_fixed_matrix_equal_and_one_below_budget(compiled, kind, field, key,
        difference, monkeypatch):
    _, node, handle = compiled
    options = {"tangent": tf.constant([.4, -.3], tf.float64)} if kind != "value" else {}
    query = request(node, kind, **options)
    work = handle.estimate(query)
    parent = UnifiedResourceLedger(UnifiedExecutionLimits(**{field: work[key] + difference}))
    child = UnifiedResourceLedger(parent=parent)
    if difference:
        monkeypatch.setattr(handle, "_run_graph",
            lambda *args: pytest.fail("A refused fixed-matrix plan executed"))
    with ResourceScope(child):
        if difference:
            with pytest.raises(MemoryError):
                handle.execute(query)
        else:
            result = handle.execute(query)
            assert np.isfinite(result.value).all()
    for ledger in (parent, child):
        receipt = ledger.receipt()
        assert receipt["live_memory_bytes"] == receipt["reserved_derivative_work"] == 0
        assert receipt["consumed_derivative_work"] == (0 if difference else work["first_call_work"])
        assert receipt["consumed_tapes"] == (0 if difference else work["logical_evaluations"])


def test_fixed_matrix_snapshot_identity_and_source_independence(compiled, monkeypatch):
    source, node, handle = compiled
    query = request(node)
    expected = np.array(handle.execute(query).value)
    operation = next(op for op in source.operations if op.name == "unitary")
    with monkeypatch.context() as patch:
        patch.setitem(operation.metadata, "matrix", np.eye(4, dtype=complex))
        np.testing.assert_allclose(handle.execute(query).value, expected, atol=2e-12, rtol=0)
    index = next(i for i, op in enumerate(handle._whole._circuit.operations) if op.name == "unitary")
    with monkeypatch.context() as patch:
        patch.setitem(handle._whole._fixed, index, np.eye(4, dtype=complex))
        patch.setattr(handle, "_run_graph", lambda *args: pytest.fail("A modified snapshot ran"))
        with pytest.raises(UnsupportedFeature, match="identity"):
            handle.execute(query)
    np.testing.assert_allclose(handle.execute(query).value, expected, atol=2e-12, rtol=0)


def test_fixed_matrix_runtime_failure_and_concurrent_parent_release(compiled, monkeypatch):
    _, node, handle = compiled
    query = request(node)
    work = handle.estimate(query)
    ledger = UnifiedResourceLedger()
    with monkeypatch.context() as patch:
        def fail(*args):
            raise RuntimeError("injected fixed-matrix execution")
        patch.setattr(handle, "_run_graph", fail)
        with ResourceScope(ledger), pytest.raises(RuntimeError, match="injected"):
            handle.execute(query)
    receipt = ledger.receipt()
    assert receipt["consumed_tapes"] == 0
    assert receipt["live_memory_bytes"] == receipt["reserved_derivative_work"] == 0
    parent = UnifiedResourceLedger(UnifiedExecutionLimits(
        max_total_memory_bytes=work["required_memory_bytes"] * 3 // 2))
    child = UnifiedResourceLedger(parent=parent)
    entered, release = Event(), Event()
    execute = handle._run_graph

    def held(*args):
        entered.set()
        assert release.wait(30)
        return execute(*args)

    def invoke():
        with ResourceScope(child):
            return handle.execute(query)

    monkeypatch.setattr(handle, "_run_graph", held)
    with ThreadPoolExecutor(max_workers=2) as workers:
        first = workers.submit(invoke)
        try:
            assert entered.wait(30)
            with pytest.raises(MemoryError):
                workers.submit(invoke).result(timeout=20)
        finally:
            release.set()
        assert np.isfinite(first.result(timeout=30).value).all()
    for account in (parent, child):
        receipt = account.receipt()
        assert receipt["live_memory_bytes"] == receipt["reserved_derivative_work"] == 0
        assert receipt["consumed_tapes"] == 1
        assert receipt["consumed_derivative_work"] == work["first_call_work"]


def test_exact_representation_retains_bonds_after_physical_disentangling(record_property):
    states, dimensions = [], []
    for repetitions in (1, 2):
        source = qb.Circuit(4).h(0)
        for _ in range(repetitions):
            source.unitary(gate_matrix("cx"), (0, 3))
        node = QNode.from_circuit(source, qb.PauliZ(3), max_diff=2,
            device=qb.MatrixProductStateDevice(max_bond_dim=4, cutoff=0))
        plan = node._construct((), {})
        tensor = TensorFlowMPSPlan(plan)
        chain, scale = tensor.chain(tf.constant(plan.recorder.native_values(), tf.float64))
        result = chain[0]
        for site in chain[1:]:
            result = tf.tensordot(result, site, axes=([-1], [0]))
        state = np.asarray(tf.reshape(result, (-1,)) * scale)
        reference = qb.StatevectorDevice().statevector(source)
        np.testing.assert_allclose(state, reference, atol=2e-12, rtol=0)
        states.append(state)
        dimensions.append(max(site.shape[-1] for site in chain))
        assert dimensions[-1] == tensor.work["mps_bond_bound"]
    ranks = [np.linalg.matrix_rank(state.reshape(2, -1), tol=1e-10) for state in states]
    assert ranks == [2, 1]
    assert dimensions[1] >= dimensions[0] > 1
    record_property("physical_schmidt_ranks", str(ranks))
    record_property("observed_representation_bonds", str(dimensions))
    # Identity index splits preserve AD, not optimal Schmidt compression.
    source, native = fixture(4, 2)
    plan = native._construct((POINT,), {})
    cap = TensorFlowMPSPlan(plan).work["mps_bond_bound"]
    native.device.state_options["max_bond_dim"] = cap - 1
    with pytest.raises(MemoryError, match="bond"):
        TensorFlowMPSPlan(plan)
    assert source.num_qubits == 4


@pytest.mark.parametrize("matrix", [np.eye(3), np.full((4, 4), np.nan),
    np.full((4, 4), np.inf), np.zeros((4, 4))])
def test_invalid_fixed_payload_cannot_reach_tensor_execution(matrix, monkeypatch):
    _, native = fixture(4, 2)
    plan = native._construct((POINT,), {})
    operation = next(op for op in plan.circuit.operations if op.name == "unitary")
    monkeypatch.setitem(operation.metadata, "matrix", matrix)
    monkeypatch.setattr(TensorFlowMPSPlan, "chain",
        lambda *args: pytest.fail("An invalid fixed payload allocated tensors"))
    with pytest.raises(ValueError, match="fixed primitive|unitar|matrix|finite"):
        TensorFlowMPSPlan(plan)


def test_local_matrix_history_and_ad_storage_are_admitted_before_fixed_allocation(monkeypatch):
    from quantumbridge.interfaces import tensorflow_whole_execution

    estimates = []
    for repetitions in (1, 7):
        p, q = qb.ParameterVector("history", 2)
        source = qb.Circuit(2)
        source.append(qb.Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(.5, annotated=True), (1,))
        for _ in range(repetitions):
            source.unitary(gate_matrix("sx"), (0,))
        node = QNode.from_circuit(source, qb.PauliZ(1), max_diff=2,
            device=qb.MatrixProductStateDevice(max_bond_dim=4, cutoff=0))
        plan = node._construct((POINT,), {})
        tensor = TensorFlowMPSPlan(plan)
        estimates.append(tensor.work)
    for key in ("operator_storage_bytes_bound", "tensor_evolution_bytes_bound", "workspace_bytes"):
        assert estimates[1][key] > estimates[0][key]
    node.higher_order_limits = HigherOrderLimits(max_memory_bytes=1)
    monkeypatch.setattr(tensorflow_whole_execution, "gate_matrix",
        lambda *args: pytest.fail("Rejected history allocated a fixed matrix"))
    with pytest.raises(MemoryError, match="max_memory_bytes"):
        TensorFlowMPSPlan(plan)
