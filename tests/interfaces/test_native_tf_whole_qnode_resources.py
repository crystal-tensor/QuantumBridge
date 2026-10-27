# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Structural whole-plan admission is testable even without TensorFlow."""

import builtins

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.qml import QNode
from quantumbridge.interfaces.tensorflow_whole_execution import TensorFlowStatevectorPlan


def make_plan(**options):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    source = qb.QuantumCircuit(2)
    source.h(0)
    source.append(qb.Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(0.5, annotated=True), (1,))
    node = QNode.from_circuit(source, qb.PauliZ(1), max_diff=2, **options)
    return node._construct((np.array([0.37, 0.82]),), {}), source


@pytest.fixture
def no_execution(monkeypatch):
    from quantumbridge.interfaces.tensorflow_native_execution import TensorFlowLocalOperator
    original = builtins.__import__
    def forbidden(*args, **kwargs):
        pytest.fail("Whole-plan admission reached a dangerous execution entry")
    def no_framework(name, *args, **kwargs):
        if name.split(".")[0] in {"tensorflow", "qiskit", "pennylane"}:
            forbidden()
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", no_framework)
    monkeypatch.setattr(TensorFlowLocalOperator, "__call__", forbidden)
    monkeypatch.setattr(qb.StatevectorDevice, "statevector", forbidden)


@pytest.mark.parametrize("field", ["max_input_parameters", "max_output_elements", "max_parameter_graph_nodes", "max_postprocessing_nodes", "max_memory_bytes", "max_adjoint_operations", "max_total_tapes", "max_derivative_order"])
def test_whole_higher_order_budget_refuses_before_any_tensor_or_device_update(field, no_execution):
    plan, source = make_plan(higher_order_limits=HigherOrderLimits(**{field: 1}))
    if field == "max_output_elements":
        plan.requests = [*plan.requests, *plan.requests]
    before = source.to_ir().to_json()
    with pytest.raises(MemoryError, match=field):
        TensorFlowStatevectorPlan(plan)
    assert source.to_ir().to_json() == before


def test_device_combined_memory_limit_is_not_replaced_by_tensorflow_allocator(no_execution):
    plan, _ = make_plan(device=qb.StatevectorDevice(max_memory_mb=0.001))
    with pytest.raises(MemoryError, match="max_memory_mb"):
        TensorFlowStatevectorPlan(plan)


@pytest.mark.parametrize("field", ["max_total_memory_bytes", "max_derivative_work", "max_total_tapes"])
def test_static_parent_scope_refuses_with_zero_consumed_execution(field, no_execution):
    from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
    from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    plan, source = make_plan()
    before = source.to_ir().to_json()
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(**{field: 0}))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        TensorFlowStatevectorPlan(plan)
    receipt = ledger.receipt()
    assert receipt["consumed_tapes"] == receipt["consumed_shots"] == receipt["consumed_derivative_work"] == receipt["live_memory_bytes"] == 0
    assert source.to_ir().to_json() == before


def test_complete_support_check_refuses_an_unsupported_operation_before_tf_import(no_execution):
    plan, _ = make_plan()
    plan.circuit.rxx(0.3, 0, 1)
    from quantumbridge.core.classical import UnsupportedFeature
    with pytest.raises(UnsupportedFeature, match="unvalidated TF operation"):
        TensorFlowStatevectorPlan(plan)


def test_plan_identity_accepts_existing_valid_numpy_resource_scalars(no_execution):
    plan, _ = make_plan(higher_order_limits=HigherOrderLimits(max_input_parameters=np.int64(128)),
        device=qb.StatevectorDevice(max_qubits=np.int64(4), max_memory_mb=np.float32(1024)))
    work = TensorFlowStatevectorPlan(plan).work
    assert len(work["compiled_plan_identity"]) == 64
    assert work["host_quantum_calls"] == work["device_updates"] == 0
