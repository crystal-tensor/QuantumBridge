# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""One owned permutation buffer for the bounded annotation representation."""

from concurrent.futures import ThreadPoolExecutor
import gc

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.standard_gates import UnitaryGate
from quantumbridge.execution import UnifiedResourceLedger as Ledger, UnifiedExecutionLimits as Limits
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import Operator


def source():
    matrix = np.array([[1, 1, 1, 1], [1, 1j, -1, -1j],
        [1, -1, 1, -1], [1, -1j, -1, 1j]], complex) / 2
    annotation = qb.AnnotatedOperation(UnitaryGate(matrix), [qb.InverseModifier(), qb.ControlModifier(2, 1)])
    return Operator(annotation)


@pytest.mark.parametrize("method", ["as_qiskit_operator", "as_native_operator", "copy", "adjoint"])
def test_hybrid_exact_and_minus_one_budgets_admit_one_owned_output(method, monkeypatch):
    owner = source()
    amount = owner.data.nbytes
    failed = Ledger(Limits(max_total_memory_bytes=amount - 1))
    with ResourceScope(failed), monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Denied hybrid permutation allocated"))
        with pytest.raises(MemoryError):getattr(owner, method)()
    assert failed.receipt()["live_memory_bytes"] == 0
    ledger = Ledger(Limits(max_total_memory_bytes=amount))
    with ResourceScope(ledger):result = getattr(owner, method)()
    assert ledger.receipt()["live_memory_bytes"] == amount
    assert not np.shares_memory(owner.data, result.data)
    view = result.data[:, 0]
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == amount
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("field", ["width_zero", "width_foreign", "basis", "shape", "dims", "dtype", "stale_descriptor"])
@pytest.mark.parametrize("method", ["as_qiskit_operator", "as_native_operator", "copy", "power", "unitary"])
def test_forged_hybrid_descriptor_refuses_before_copy_or_callback(field, method, monkeypatch):
    class Foreign:
        def __index__(self):pytest.fail("Foreign hybrid width converted")
        def __eq__(self, value):pytest.fail("Foreign hybrid basis compared")
    owner = source()
    if field == "width_zero":object.__setattr__(owner, "_literal_target_width", 0)
    elif field == "width_foreign":object.__setattr__(owner, "_literal_target_width", Foreign())
    elif field == "basis":owner._public_matrix_basis = Foreign()
    elif field == "shape":owner.data = np.eye(8, dtype=complex)
    elif field == "dims":owner._input_dims = (4, 4)
    elif field == "dtype":owner.data = np.eye(16, dtype=float)
    else:owner._public_matrix_basis = None
    ledger = Ledger()
    circuit = qb.QuantumCircuit(4)
    with ResourceScope(ledger), monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Forged hybrid origin allocated"))
        with pytest.raises((ValueError, TypeError)):
            if method == "unitary":circuit.unitary(owner, range(4))
            elif method == "power":owner.power(2)
            else:getattr(owner, method)()
    assert ledger.receipt()["live_memory_bytes"] == 0 and len(circuit.data) == 0


def test_hybrid_descriptor_is_readonly_and_implicit_mixed_arithmetic_cannot_launder_it():
    from quantumbridge.core.classical import UnsupportedFeature
    owner = source()
    with pytest.raises(AttributeError):owner._literal_target_width = 1
    with pytest.raises(UnsupportedFeature):owner + Operator(np.eye(16))
    with pytest.raises(UnsupportedFeature):owner.reverse_qargs().as_qiskit_operator()
    with pytest.raises(UnsupportedFeature):owner.reshape((4, 4), (4, 4)).as_qiskit_operator()


@pytest.mark.parametrize("payload", ["foreign_array", "object_dtype"])
def test_hybrid_raw_gate_source_is_qualified_before_definition_or_matrix_callbacks(payload, monkeypatch):
    class Foreign:
        def __complex__(self):pytest.fail("Foreign gate coefficient converted")
        @property
        def shape(self):pytest.fail("Foreign gate matrix shape read")
    gate = UnitaryGate(np.eye(4))
    operation = qb.AnnotatedOperation(gate, qb.ControlModifier(1))
    data = np.full((4, 4), Foreign(), dtype=object) if payload == "object_dtype" else Foreign()
    object.__setattr__(gate, "_params", (data,))
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Invalid hybrid source allocated"))
        with pytest.raises((TypeError, ValueError)):operation.to_matrix()


def test_hybrid_readonly_concurrent_conversion_and_idempotent_public_selection():
    owner = source()
    owner.data.flags.writeable = False
    before = owner.data.copy()
    expected = owner.as_qiskit_operator().data.copy()
    amount = owner.data.nbytes
    parent = Ledger(Limits(max_total_memory_bytes=3 * amount))
    children = [Ledger(parent=parent) for _ in range(3)]
    def execute(ledger):
        with ResourceScope(ledger):return owner.as_qiskit_operator()
    with ThreadPoolExecutor(max_workers=3) as pool:results = list(pool.map(execute, children))
    for result in results:np.testing.assert_array_equal(result.data, expected)
    assert parent.receipt()["live_memory_bytes"] == 3 * amount
    del result, results
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == 0
    np.testing.assert_array_equal(owner.data, before)
    public = owner.as_qiskit_operator()
    np.testing.assert_array_equal(public.as_qiskit_operator().data, expected)
    np.testing.assert_array_equal(owner.as_native_operator().as_qiskit_operator().data, expected)


def test_hybrid_permutation_failure_releases_output_and_preserves_readonly_source(monkeypatch):
    import importlib
    module = importlib.import_module("quantumbridge.information.operator")
    owner = source()
    owner.data.flags.writeable = False
    before = owner.data.copy()
    ledger = Ledger()
    with monkeypatch.context() as patch:
        patch.setattr(module, "_bits_to_index", lambda *a: (_ for _ in ()).throw(RuntimeError("permutation fault")))
        try:
            with ResourceScope(ledger):owner.as_qiskit_operator()
        except RuntimeError as error:assert str(error) == "permutation fault"
        else:pytest.fail("Permutation injection was not reached")
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    np.testing.assert_array_equal(owner.data, before)
    with ResourceScope(ledger):recovered = owner.as_qiskit_operator()
    assert recovered.arithmetic_convention == "qiskit"
