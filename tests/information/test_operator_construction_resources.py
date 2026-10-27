# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Admission and storage lifetime at the existing native state factories."""

from concurrent.futures import ThreadPoolExecutor
import gc
from math import prod

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.gate_limits import GateCircuitLimits, gate_circuit_scope
from quantumbridge.execution import UnifiedResourceLedger as Ledger, UnifiedExecutionLimits as Limits
from quantumbridge.execution.array_ownership import storage_ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import Statevector, DensityMatrix


def state(dims=(2, 2)):
    vector = np.arange(1, prod(dims) + 1) + 1j * np.arange(prod(dims), 0, -1)
    return Statevector(vector / np.linalg.norm(vector), dims=dims)


@pytest.mark.parametrize("dims", [(2, 2), (2, 3)])
def test_projector_exact_and_minus_one_budget_are_prior_and_recoverable(dims, monkeypatch):
    owner = state(dims)
    amount = 16 * prod(dims) ** 2
    failed = Ledger(Limits(max_total_memory_bytes=amount - 1))
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Denied projector allocated"))
        with ResourceScope(failed), pytest.raises(MemoryError):owner.to_operator()
    assert failed.receipt()["live_memory_bytes"] == 0
    ledger = Ledger(Limits(max_total_memory_bytes=2 * amount))
    with ResourceScope(ledger):
        operator = owner.to_operator()
        assert ledger.receipt()["live_memory_bytes"] == amount
        public = operator.as_qiskit_operator()
        assert ledger.receipt()["live_memory_bytes"] == 2 * amount
    assert storage_ledger(operator.data) is storage_ledger(public.data) is ledger
    views = operator.data[:, 0], public.data[:, 0]
    del operator, public
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 2 * amount
    del views
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    with ResourceScope(failed):recovered = state((2,)).to_operator()
    assert recovered.data.shape == (2, 2)


@pytest.mark.parametrize("dims", [(2, 2), (3, 2)])
def test_density_alias_and_public_snapshot_have_distinct_allocation_contracts(dims):
    density = DensityMatrix.from_statevector(state(dims))
    amount = density.data.nbytes
    ledger = Ledger(Limits(max_total_memory_bytes=amount))
    with ResourceScope(ledger):
        operator = density.to_operator()
        assert ledger.receipt()["live_memory_bytes"] == 0
        public = operator.as_qiskit_operator()
        assert ledger.receipt()["live_memory_bytes"] == amount
    assert np.shares_memory(operator.data, density.data)
    snapshot = public.data.copy()
    density.data[0, 1] += .2j
    assert operator.data[0, 1] == density.data[0, 1]
    np.testing.assert_array_equal(public.data, snapshot)
    assert not np.shares_memory(public.data, density.data)


@pytest.mark.parametrize("density", [False, True])
@pytest.mark.parametrize("field", ["data", "dims", "shape", "dtype"])
@pytest.mark.parametrize("managed", [False, True])
def test_forged_state_fields_refuse_before_callbacks_and_allocations(density, field, managed, monkeypatch):
    from contextlib import nullcontext
    class Foreign:
        def __iter__(self):pytest.fail("Foreign dimensions iterated")
        def __array__(self, *a, **k):pytest.fail("Foreign data converted")
    class ForeignArray(np.ndarray):
        @property
        def dtype(self):pytest.fail("Foreign array property read")
    owner = state()
    if density:owner = DensityMatrix.from_statevector(owner)
    if field == "dims":owner._dims = Foreign()
    elif field == "data":owner.data = ForeignArray(owner.data.shape, complex)
    elif field == "shape":owner._dims = (2, 2, 2)
    else:owner.data = np.empty(owner.data.shape, dtype=object)
    ledger = Ledger()
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Invalid owner allocated"))
        with ResourceScope(ledger) if managed else nullcontext():
            with pytest.raises((TypeError, ValueError)):owner.to_operator()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("density", [False, True])
def test_state_origin_dimension_work_limits_precede_matrix_work(density, monkeypatch):
    owner = state()
    if density:owner = DensityMatrix.from_statevector(owner)
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Overwork factory allocated"))
    with gate_circuit_scope(GateCircuitLimits(max_decomposition_work=15)), pytest.raises(MemoryError):
        owner.to_operator()


def test_readonly_projectors_construct_concurrently_with_one_output_each():
    owner = state((2, 3))
    owner.data.flags.writeable = False
    expected = np.outer(owner.data, owner.data.conj())
    amount = expected.nbytes
    parent = Ledger(Limits(max_total_memory_bytes=4 * amount))
    children = [Ledger(parent=parent) for _ in range(4)]
    def execute(ledger):
        with ResourceScope(ledger):return owner.to_operator()
    with ThreadPoolExecutor(max_workers=2) as pool:results = list(pool.map(execute, children))
    assert parent.receipt()["live_memory_bytes"] == 4 * amount
    for result in results:
        np.testing.assert_array_equal(result.data, expected)
        assert storage_ledger(result.data) in children
    del result, results
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == 0


def test_projector_numeric_failure_does_not_publish_or_retain_output(monkeypatch):
    owner = state()
    ledger = Ledger()
    with monkeypatch.context() as patch:
        patch.setattr(np, "multiply", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("projector fault")))
        try:
            with ResourceScope(ledger):owner.to_operator()
        except RuntimeError as error:assert str(error) == "projector fault"
        else:pytest.fail("Numerical injection was not reached")
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    with ResourceScope(ledger):result = owner.to_operator()
    np.testing.assert_array_equal(result.data, np.outer(owner.data, owner.data.conj()))


@pytest.mark.parametrize("density", [False, True])
def test_nonunitary_projector_cannot_be_published_as_a_quantum_gate(density):
    owner = state()
    if density:owner = DensityMatrix.from_statevector(owner)
    operator = owner.to_operator()
    circuit = qb.QuantumCircuit(2)
    for value in (operator, operator.as_qiskit_operator()):
        with pytest.raises(ValueError):circuit.unitary(value, [0, 1])
        assert len(circuit.data) == 0
