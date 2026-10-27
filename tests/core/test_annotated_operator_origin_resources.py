# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Existing annotation matrix storage and foreign-owner admission survive origin tracking."""

import gc

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.gate_limits import GateCircuitLimits, gate_circuit_scope
from quantumbridge.core.standard_gates import UnitaryGate
from quantumbridge.execution import UnifiedResourceLedger as Ledger, UnifiedExecutionLimits as Limits
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information.operator import _operator_matrix_origin


def source():
    return qb.AnnotatedOperation(qb.Circuit(2).h(0).s(1).cx(0, 1).to_gate(), qb.InverseModifier())


def test_matrix_origin_qualification_does_not_compare_foreign_basis():
    class Foreign(str):
        def __eq__(self, value):pytest.fail("Foreign basis compared")
    gate = UnitaryGate(np.eye(4))
    object.__setattr__(gate, "_public_matrix_basis", Foreign("native"))
    with pytest.raises((TypeError, ValueError)):_operator_matrix_origin(gate, from_matrix=True)


def test_foreign_annotation_owner_and_illegal_modifier_are_rejected():
    class Foreign(qb.AnnotatedOperation):
        @property
        def base_op(self):pytest.fail("Foreign annotation property read")
    with pytest.raises((TypeError, ValueError)):
        qb.AnnotatedOperation.to_matrix(object.__new__(Foreign))
    operation = source()
    operation.modifiers = [object()]
    with pytest.raises(TypeError):operation.to_matrix()


def test_native_annotation_matrix_limit_precedes_output_factory(monkeypatch):
    operation = source()
    with gate_circuit_scope(GateCircuitLimits(max_matrix_dimension=2)), monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Overlimit annotation matrix allocated"))
        with pytest.raises(MemoryError):operation.to_matrix()


def test_annotation_matrix_lifetime_failure_atomicity_and_recovery():
    operation = source()
    before = operation.base_op.definition.to_ir().to_json()
    ledger = Ledger()
    with ResourceScope(ledger):result = operation.to_matrix()
    peak = ledger.receipt()["peak_memory_bytes"]
    view = result.data[:, 0]
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 256
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    for budget, succeeds in ((peak - 1, False), (peak, True)):
        current = Ledger(Limits(max_total_memory_bytes=budget))
        if succeeds:
            with ResourceScope(current):recovered = operation.to_matrix()
            assert recovered.__dict__["_public_matrix_basis"] == "native"
            del recovered
        else:
            try:
                with ResourceScope(current):operation.to_matrix()
            except MemoryError:pass
            else:pytest.fail("Measured peak-minus-one annotation budget was admitted")
        gc.collect()
        assert current.receipt()["live_memory_bytes"] == 0
    assert operation.base_op.definition.to_ir().to_json() == before
