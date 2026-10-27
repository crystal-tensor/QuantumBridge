# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Admission and storage lifetime for the explicit arithmetic convention."""

import gc
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.core.gate_limits import GateCircuitLimits, gate_circuit_scope
from quantumbridge.execution import UnifiedResourceLedger as Ledger, UnifiedExecutionLimits as Limits, ResourceLimitError
from quantumbridge.execution.resource_context import ResourceScope


def owner():
    return Operator(np.array([[1, 1, 1, 1], [1, 1j, -1, -1j],
        [1, -1, 1, -1], [1, -1j, -1, 1j]], complex) / 2).as_qiskit_operator()


@pytest.mark.parametrize("method", ["compose", "tensor", "expand", "as_qiskit_operator"])
def test_owned_output_memory_denial_is_before_allocation_and_recovery_is_real(method, monkeypatch):
    a, b = owner(), owner()
    expected = b.data @ a.data if method == "compose" else np.kron(a.data, b.data) \
        if method in ("tensor", "expand") else a.data.copy()
    amount = expected.nbytes
    rejected = Ledger(Limits(max_total_memory_bytes=amount - 1))
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Denied arithmetic reached allocation"))
        with ResourceScope(rejected), pytest.raises(ResourceLimitError):
            getattr(a, method)() if method == "as_qiskit_operator" else getattr(a, method)(b)
    assert rejected.receipt()["live_memory_bytes"] == 0
    ledger = Ledger(Limits(max_total_memory_bytes=amount))
    with ResourceScope(ledger):
        result = getattr(a, method)() if method == "as_qiskit_operator" else getattr(a, method)(b)
    np.testing.assert_allclose(result.data, expected, atol=3e-12, rtol=0)
    assert ledger.receipt()["live_memory_bytes"] == amount
    escaped = result.data[:, :1]
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == amount
    del escaped
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("method", ["tensor", "expand"])
def test_raw_dtype_conversion_and_tensor_output_are_admitted_together(method, monkeypatch):
    a, raw = owner(), np.eye(4, dtype=float)
    ledger = Ledger(Limits(max_total_memory_bytes=4096 + 256 - 1))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Known combined denial reached conversion"))
    with ResourceScope(ledger), pytest.raises(ResourceLimitError):
        getattr(a, method)(raw)
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("method", ["tensor", "expand"])
def test_tensor_dimension_cap_is_before_numeric_factory(method, monkeypatch):
    a, b = owner(), owner()
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Oversize tensor reached allocation"))
    with gate_circuit_scope(GateCircuitLimits(max_matrix_dimension=8)), pytest.raises(MemoryError):
        getattr(a, method)(b)


def test_work_cap_is_enforced_before_product_allocation(monkeypatch):
    a, b = owner(), owner()
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Overwork product reached allocation"))
    with gate_circuit_scope(GateCircuitLimits(max_decomposition_work=20)), pytest.raises(MemoryError):
        a.compose(b)


@pytest.mark.parametrize("qargs", [(0, 0), (2,), (-1,), (True,), (.5,)])
def test_bad_subsystem_indices_are_atomic_before_allocation(qargs, monkeypatch):
    a, b = owner(), Operator(np.eye(2)).as_qiskit_operator()
    before = a.data.copy()
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Bad qargs reached allocation"))
    with pytest.raises(ValueError):
        a.compose(b, qargs=qargs)
    np.testing.assert_array_equal(a.data, before)


@pytest.mark.parametrize("managed", [False, True])
@pytest.mark.parametrize("method", ["compose", "tensor", "expand"])
def test_foreign_operand_protocols_never_run(method, managed):
    from contextlib import nullcontext
    calls = []
    class Foreign:
        def __array__(self, *a, **k):
            calls.append("array")
            raise AssertionError("Foreign protocol ran")
    class ForeignOperator(Operator):
        @property
        def data(self):
            calls.append("data")
            raise AssertionError("Foreign property ran")
        def tensor(self, other):
            calls.append("tensor")
            raise AssertionError("Foreign tensor ran")
    a = owner()
    for other in (Foreign(), object.__new__(ForeignOperator)):
        ledger = Ledger()
        with ResourceScope(ledger) if managed else nullcontext():
            with pytest.raises((ValueError, TypeError)):
                getattr(a, method)(other)
        assert not calls and ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("method", ["as_qiskit_operator", "copy", "transpose", "adjoint", "power"])
@pytest.mark.parametrize("field", ["data", "dims", "basis", "mode"])
def test_forged_public_owner_is_qualified_before_derived_reads(method, field):
    calls = []
    class Foreign:
        def __getattr__(self, key):
            calls.append("getattr:" + key)
            raise AssertionError("Foreign owner field ran")
        def __iter__(self):
            calls.append("iter")
            raise AssertionError("Foreign owner iteration ran")
    class ForeignOrigin(str):
        def __eq__(self, other):
            calls.append("eq")
            raise AssertionError("Foreign origin equality ran")
    a = owner()
    if field == "data": a.data = Foreign()
    elif field == "dims": a._input_dims = Foreign()
    elif field == "basis": a._public_matrix_basis = ForeignOrigin("native")
    else: object.__setattr__(a, "_arithmetic_convention", ForeignOrigin("qiskit"))
    ledger = Ledger()
    with ResourceScope(ledger), pytest.raises((ValueError, TypeError)):
        getattr(a, method)(.37) if method == "power" else getattr(a, method)()
    assert calls == [] and ledger.receipt()["live_memory_bytes"] == 0


def test_nonunitary_public_result_is_not_published_as_a_circuit_gate():
    value = Operator(np.diag([1., 2., 1., 1.])).as_qiskit_operator().compose(owner())
    circuit = qb.QuantumCircuit(3)
    circuit.h(0)
    before = circuit.to_ir().to_json()
    ledger = Ledger()
    with ResourceScope(ledger), pytest.raises(ValueError):
        circuit.unitary(value, [2, 0])
    assert circuit.to_ir().to_json() == before
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_concurrent_readonly_arithmetic_shares_parent_cap_and_releases_children():
    a, b = owner(), owner()
    a.data.flags.writeable = b.data.flags.writeable = False
    before = a.data.copy(), b.data.copy()
    parent = Ledger(Limits(max_total_memory_bytes=256 * 8))
    children = [Ledger(parent=parent) for _ in range(6)]
    def calculate(ledger):
        with ResourceScope(ledger):
            return a.compose(b)
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(calculate, children))
    assert parent.receipt()["live_memory_bytes"] == 6 * 256
    for result in results:
        np.testing.assert_allclose(result.data, before[1] @ before[0], atol=3e-12, rtol=0)
    np.testing.assert_array_equal(a.data, before[0])
    np.testing.assert_array_equal(b.data, before[1])
    del result, results
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == 0
    assert all(child.receipt()["live_memory_bytes"] == 0 for child in children)
