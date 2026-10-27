# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Clifford matrix factories admit owners before synthesis or array callbacks."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
import gc

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.gate_limits import GateCircuitLimits, gate_circuit_scope
from quantumbridge.execution import UnifiedResourceLedger as Ledger, UnifiedExecutionLimits as Limits
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import Clifford, Operator
from test_clifford_operator_origins import source


@pytest.mark.parametrize("factory", [Operator, Clifford.to_operator, Clifford.to_matrix])
@pytest.mark.parametrize("field", ["origin", "width", "shape", "dtype", "foreign_buffer", "nonsymplectic"])
@pytest.mark.parametrize("managed", [False, True])
def test_forged_clifford_owner_refuses_before_callbacks_and_allocation(factory, field, managed, monkeypatch):
    class Foreign:
        def __eq__(self, other):pytest.fail("Foreign origin compared")
        def __array__(self, *a, **k):pytest.fail("Foreign tableau converted")
    owner = Clifford(source())
    if field == "origin":object.__setattr__(owner, "_public_matrix_basis", Foreign())
    elif field == "width":owner.num_qubits = True
    elif field == "shape":owner.tableau = owner.tableau[:2]
    elif field == "dtype":owner.tableau = owner.tableau.astype(object)
    elif field == "foreign_buffer":owner.tableau = Foreign()
    else:owner.tableau[:] = False
    fields = owner.__dict__.copy()
    ledger = Ledger()
    with ResourceScope(ledger) if managed else nullcontext():
        with monkeypatch.context() as patch:
            patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Invalid Clifford allocated"))
            with pytest.raises((ValueError, TypeError)):factory(owner)
    assert ledger.receipt()["peak_memory_bytes"] == 0
    assert all(owner.__dict__[key] is value for key, value in fields.items())


@pytest.mark.parametrize("factory", [Operator, Clifford.to_operator, Clifford.to_matrix])
def test_foreign_clifford_subclass_never_dispatches_its_array_or_tableau_property(factory):
    class Foreign(Clifford):
        @property
        def tableau(self):pytest.fail("Foreign tableau property")
        def __array__(self, *a, **k):pytest.fail("Foreign Clifford __array__")
    with pytest.raises((ValueError, TypeError)):factory(object.__new__(Foreign))


@pytest.mark.parametrize("factory", [Operator, Clifford.to_operator, Clifford.to_matrix])
def test_clifford_output_preflight_and_dense_cap_precede_synthesis(factory, monkeypatch):
    owner = Clifford(source())
    ledger = Ledger(Limits(max_total_memory_bytes=255))
    with monkeypatch.context() as patch:
        patch.setattr(Clifford, "to_circuit", lambda *a: pytest.fail("Denied Clifford synthesized"))
        with ResourceScope(ledger), pytest.raises(MemoryError):factory(owner)
        with gate_circuit_scope(GateCircuitLimits(max_matrix_dimension=2)), pytest.raises(MemoryError):factory(owner)
    assert ledger.receipt()["peak_memory_bytes"] == 0


def test_clifford_work_equal_and_one_below_are_checked_before_dense_copy(monkeypatch):
    owner = Clifford.identity(1)
    work = owner.tableau.size
    with gate_circuit_scope(GateCircuitLimits(max_decomposition_work=work)):
        np.testing.assert_array_equal(owner.to_matrix(), np.eye(2))
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Overwork Clifford allocated"))
        with gate_circuit_scope(GateCircuitLimits(max_decomposition_work=work - 1)), pytest.raises(MemoryError):owner.to_operator()


def test_clifford_actual_workspace_peak_exact_and_one_below_release_every_temporary():
    owner = Clifford(source())
    expected = owner.to_matrix()
    measured = Ledger()
    with ResourceScope(measured):first = owner.to_operator()
    peak = measured.receipt()["peak_memory_bytes"]
    assert measured.receipt()["live_memory_bytes"] == expected.nbytes
    assert peak > expected.nbytes
    del first
    gc.collect()
    assert measured.receipt()["live_memory_bytes"] == 0
    exact = Ledger(Limits(max_total_memory_bytes=peak))
    with ResourceScope(exact):accepted = owner.to_operator()
    np.testing.assert_array_equal(accepted.data, expected)
    assert exact.receipt()["peak_memory_bytes"] == peak
    denied = Ledger(Limits(max_total_memory_bytes=peak - 1))
    try:
        with ResourceScope(denied):owner.to_operator()
    except MemoryError:pass
    else:pytest.fail("One-below actual workspace peak unexpectedly succeeded")
    gc.collect()
    assert denied.receipt()["live_memory_bytes"] == 0
    assert denied.receipt()["total_reserved_memory_bytes"] == denied.receipt()["total_released_memory_bytes"]
    with ResourceScope(denied):recovered = Clifford.identity(0).to_operator()
    assert recovered.data.shape == (1, 1)


def test_clifford_owned_source_and_output_parent_child_lifetimes_are_distinct():
    parent = Ledger()
    child = Ledger(parent=parent)
    with ResourceScope(parent):owner = Clifford(source())
    source_bytes = owner.tableau.nbytes
    assert parent.receipt()["live_memory_bytes"] == source_bytes
    with ResourceScope(child):result = Operator(owner)
    assert child.receipt()["live_memory_bytes"] == result.data.nbytes
    assert parent.receipt()["live_memory_bytes"] == source_bytes + result.data.nbytes
    view = result.data[:, 0]
    del result
    gc.collect()
    assert child.receipt()["live_memory_bytes"] == 256
    del view
    gc.collect()
    assert child.receipt()["live_memory_bytes"] == 0
    assert parent.receipt()["live_memory_bytes"] == source_bytes
    del owner
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == 0


def test_clifford_readonly_concurrent_synthesis_and_source_mutation_are_independent():
    owner = Clifford(source())
    expected, before = owner.to_matrix(), owner.tableau.copy()
    owner.tableau.flags.writeable = False
    parent = Ledger()
    children = [Ledger(parent=parent) for _ in range(3)]
    def execute(ledger):
        with ResourceScope(ledger):return owner.to_operator()
    with ThreadPoolExecutor(max_workers=3) as pool:results = list(pool.map(execute, children))
    assert parent.receipt()["live_memory_bytes"] == 3 * expected.nbytes
    for index, item in enumerate(results):
        np.testing.assert_array_equal(item.data, expected)
        assert children[index].receipt()["live_memory_bytes"] == expected.nbytes
    np.testing.assert_array_equal(owner.tableau, before)
    owner.tableau.flags.writeable = True
    owner.tableau[:, -1] ^= True
    for item in results:np.testing.assert_array_equal(item.data, expected)
    del item, results
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == 0


def test_clifford_synthesis_fault_releases_output_and_preserves_source(monkeypatch):
    owner = Clifford(source())
    before = owner.tableau.copy()
    original = Operator.from_circuit
    ledger = Ledger()
    def fail(cls, circuit):
        result = original(circuit)
        assert ledger.receipt()["live_memory_bytes"] >= result.data.nbytes
        raise RuntimeError("Clifford synthesis output fault")
    with monkeypatch.context() as patch:
        patch.setattr(Operator, "from_circuit", classmethod(fail))
        try:
            with ResourceScope(ledger):owner.to_operator()
        except RuntimeError as error:assert str(error) == "Clifford synthesis output fault"
        else:pytest.fail("Synthesis fault was not reached")
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    np.testing.assert_array_equal(owner.tableau, before)
    with ResourceScope(ledger):recovered = owner.to_operator()
    assert recovered.__dict__["_public_matrix_basis"] == "native"


def test_public_operator_instruction_snapshot_and_gate_factory_cost_are_accounted(monkeypatch):
    owner = Operator(source()).as_qiskit_operator()
    amount = owner.data.nbytes
    denied = Ledger(Limits(max_total_memory_bytes=amount - 1))
    with ResourceScope(denied), monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Denied instruction snapshot allocated"))
        with pytest.raises(MemoryError):owner.to_instruction()
    measured = Ledger()
    with ResourceScope(measured):instruction = owner.to_instruction()
    peak = measured.receipt()["peak_memory_bytes"]
    assert measured.receipt()["live_memory_bytes"] == amount
    assert peak > amount
    assert not np.shares_memory(owner.data, instruction.params[0])
    exact = Ledger(Limits(max_total_memory_bytes=peak))
    with ResourceScope(exact):accepted = owner.to_instruction()
    assert exact.receipt()["peak_memory_bytes"] == peak
    assert exact.receipt()["live_memory_bytes"] == amount
    np.testing.assert_array_equal(accepted.params[0], instruction.params[0])
    below = Ledger(Limits(max_total_memory_bytes=peak - 1))
    try:
        with ResourceScope(below):owner.to_instruction()
    except MemoryError:pass
    else:pytest.fail("One-below gate construction peak unexpectedly succeeded")
    gc.collect()
    assert below.receipt()["live_memory_bytes"] == 0


def test_clifford_invalid_partition_and_readonly_origin_before_matrix_copy(monkeypatch):
    owner = Clifford(source())
    with pytest.raises(AttributeError):owner._public_matrix_basis = "unresolved"
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Invalid Clifford partition allocated"))
        with pytest.raises((ValueError, TypeError)):Operator(owner, input_dims=(4,))


@pytest.mark.parametrize("factory", [Operator, Operator.from_circuit, Clifford.from_circuit])
@pytest.mark.parametrize("field", ["definition", "width", "matrix_dtype"])
def test_gate_source_owner_admission_precedes_definition_or_numeric_callbacks(factory, field, monkeypatch):
    from quantumbridge.core.standard_gates import UnitaryGate
    class Foreign:
        def __eq__(self, other):pytest.fail("Foreign gate width compared")
        def __array__(self, *a, **k):pytest.fail("Foreign gate numeric conversion")
        @property
        def operations(self):pytest.fail("Foreign definition operations read")
    gate = source().to_gate()
    if field == "definition":object.__setattr__(gate, "_definition", Foreign())
    elif field == "width":object.__setattr__(gate, "num_qubits", Foreign())
    else:
        gate = UnitaryGate(np.eye(4))
        payload = np.empty((4, 4), dtype=object)
        for index in range(payload.size):payload.flat[index] = Foreign()
        object.__setattr__(gate, "_params", (payload,))
    ledger = Ledger()
    with ResourceScope(ledger), monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Forged gate source allocated"))
        with pytest.raises((ValueError, TypeError)):factory(gate)
    assert ledger.receipt()["peak_memory_bytes"] == 0


@pytest.mark.parametrize("dims", [(4,), (2, 4), (4, 2)])
def test_mixed_radix_clifford_normalization_is_owned_bounded_and_released(dims, monkeypatch):
    from math import prod
    owner = Operator(source(prod(dims).bit_length() - 1)).reshape(dims, dims)
    before = owner.data.copy()
    amount = owner.data.nbytes
    denied = Ledger(Limits(max_total_memory_bytes=amount - 1))
    with ResourceScope(denied), monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Denied mixed-radix normalization allocated"))
        with pytest.raises(MemoryError):Clifford.from_operator(owner)
    assert denied.receipt()["peak_memory_bytes"] == 0
    measured = Ledger()
    with ResourceScope(measured):result = Clifford.from_operator(owner)
    peak = measured.receipt()["peak_memory_bytes"]
    assert measured.receipt()["live_memory_bytes"] == result.tableau.nbytes
    assert peak > amount
    exact = Ledger(Limits(max_total_memory_bytes=peak))
    with ResourceScope(exact):accepted = Clifford.from_operator(owner)
    np.testing.assert_array_equal(accepted.tableau, result.tableau)
    below = Ledger(Limits(max_total_memory_bytes=peak - 1))
    try:
        with ResourceScope(below):Clifford.from_operator(owner)
    except MemoryError:pass
    else:pytest.fail("One-below mixed-radix construction peak unexpectedly succeeded")
    gc.collect()
    assert below.receipt()["live_memory_bytes"] == 0
    np.testing.assert_array_equal(owner.data, before)
    assert owner.input_dims() == owner.output_dims() == dims
    assert result.__dict__.get("_public_matrix_basis") is None


def test_mixed_radix_source_parent_child_charge_and_readonly_concurrency():
    parent = Ledger()
    with ResourceScope(parent):owner = Operator(source()).reshape((4,), (4,))
    source_bytes = owner.data.nbytes
    assert parent.receipt()["live_memory_bytes"] == source_bytes
    before = owner.data.copy()
    owner.data.flags.writeable = False
    children = [Ledger(parent=parent) for _ in range(3)]
    def execute(ledger):
        with ResourceScope(ledger):return Clifford.from_operator(owner)
    with ThreadPoolExecutor(max_workers=3) as pool:results = list(pool.map(execute, children))
    amount = results[0].tableau.nbytes
    assert parent.receipt()["live_memory_bytes"] == source_bytes + 3 * amount
    for index, item in enumerate(results):
        assert children[index].receipt()["live_memory_bytes"] == amount
        assert item.__dict__.get("_public_matrix_basis") is None
    np.testing.assert_array_equal(owner.data, before)
    del item, results
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == source_bytes
    owner = None
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("case", ["nonbinary_total", "rectangular", "mismatched_partitions", "nonfinite"])
def test_invalid_native_mixed_radix_source_refuses_before_normalization_allocation(case, monkeypatch):
    if case == "nonbinary_total":owner = Operator(np.eye(6), (2, 3), (2, 3)).as_native_operator()
    elif case == "rectangular":owner = Operator(np.ones((2, 4)), (4,), (2,)).as_native_operator()
    elif case == "mismatched_partitions":owner = Operator(np.eye(4), (4,), (2, 2)).as_native_operator()
    else:
        owner = Operator(source()).reshape((4,), (4,))
        owner.data[0, 0] = np.nan
    ledger = Ledger()
    with ResourceScope(ledger), monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Invalid mixed-radix input allocated"))
        with pytest.raises(ValueError):Clifford.from_operator(owner)
    assert ledger.receipt()["peak_memory_bytes"] == 0


def test_non_clifford_mixed_radix_unitary_rejects_and_releases_temporary_frame():
    owner = Operator(qb.Circuit(2).ry(.37, 0)).reshape((4,), (4,))
    before = owner.data.copy()
    ledger = Ledger()
    with ResourceScope(ledger), pytest.raises(ValueError):Clifford.from_operator(owner)
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    np.testing.assert_array_equal(owner.data, before)
