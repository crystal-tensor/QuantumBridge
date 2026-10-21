# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native saved MPS tensors retain their actual account and storage lifetime."""

import gc
import weakref

import numpy as np
import pytest

from quantumbridge import Circuit
from quantumbridge.core.classical import ClassicalStore
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.array_ownership import native_storage_bytes
from quantumbridge.execution.control_flow_engine import Branch
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import MatrixProductState
from quantumbridge.providers import MatrixProductStateBackend
from quantumbridge.results import Result
from quantumbridge.simulator import NativeAerSimulator
from quantumbridge.simulator.limits import AerExecutionLimits
from quantumbridge.simulator.snapshots import SnapshotContext


def test_saved_native_view_outlives_backend_job_result_without_dense(monkeypatch):
    monkeypatch.setattr(MatrixProductState, "statevector", lambda *a, **k: pytest.fail("Dense snapshot expansion"))
    ledger, backend = Ledger(), MatrixProductStateBackend(max_bond_dim=2)
    circuit = Circuit(3).h(0).cx(0, 1).save_matrix_product_state(label="before").x(2)
    with ResourceScope(ledger):
        job = backend.run(circuit)
        result = job.result()
    saved = result.matrix_product_state("before")
    assert saved.expectation_pauli("IIZ") == pytest.approx(1.)
    exported = saved.tensors
    view = exported[1][:, ::-1, :]
    expected, reference = view.copy(), weakref.ref(exported[1])
    retained = native_storage_bytes(view)
    del saved, exported, backend, job, result
    gc.collect()
    np.testing.assert_array_equal(view, expected)
    assert reference() is not None
    assert ledger.receipt()["live_memory_bytes"] == retained
    del view
    gc.collect()
    assert reference() is None and ledger.receipt()["live_memory_bytes"] == 0


def test_pershot_save_denies_second_native_copy_before_array_allocation(monkeypatch):
    state = MatrixProductState.zero(2)
    circuit = Circuit(2).save_matrix_product_state(pershot=True)
    item = circuit.operations[0]
    context = SnapshotContext(circuit, "matrix_product_state", finite_shots=True)
    ledger = Ledger(Limits(max_total_memory_bytes=state.tensor_bytes*2-1))
    branch = Branch(state, ClassicalStore(0))
    with ResourceScope(ledger):
        context.observe(item, branch, None)
        assert ledger.receipt()["live_memory_bytes"] == state.tensor_bytes
        with monkeypatch.context() as patch:
            patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Snapshot copied before cumulative reservation"))
            with pytest.raises(MemoryError):
                context.observe(item, branch, None)
    assert len(context.cells[("matrix_product_state", "")]["value"]) == 1
    del context
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_labeled_native_copy_rejects_all_tensors_before_allocating(monkeypatch):
    backend, owner = MatrixProductStateBackend(), Ledger()
    with ResourceScope(owner):
        result = backend.run(Circuit(2).save_matrix_product_state()).result()
    before = owner.receipt()["live_memory_bytes"]
    limited = Ledger(Limits(max_total_memory_bytes=63))
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Partial native snapshot export allocated"))
        with ResourceScope(limited), pytest.raises(MemoryError):
            result.matrix_product_state("matrix_product_state")
    assert limited.receipt()["live_memory_bytes"] == 0
    assert owner.receipt()["live_memory_bytes"] == before


def test_conditional_pershot_saves_keep_real_groups_and_defensive_copies():
    circuit = Circuit(1, 1).h(0).phase(.31, 0).save_matrix_product_state(label="before")
    circuit = circuit.measure(0, 0).if_test((0, 1), Circuit(1, 1).x(0))
    circuit.save_matrix_product_state(label="after", pershot=True, conditional=True)
    ledger = Ledger()
    with ResourceScope(ledger):
        result = MatrixProductStateBackend().run(circuit, shots=12, seed_simulator=7, memory=True).result()
    groups = result.matrix_product_state("after")
    assert set(groups) == {"0x0", "0x1"}
    assert {format(int(key, 16), "b"): len(states) for key, states in groups.items()} == result.counts()
    for states in groups.values():
        for state in states:assert state.expectation_pauli("Z") == pytest.approx(1.)
    first = next(iter(groups.values()))[0]
    first.apply(np.array([[0, 1], [1, 0]], complex), [0])
    untouched = result.matrix_product_state("after")
    assert all(state.expectation_pauli("Z") == pytest.approx(1.) for states in untouched.values() for state in states)
    roots = [state._tensors for state in result.mps_snapshots["after"]["0x0"]+result.mps_snapshots["after"]["0x1"]]
    roots.append(result.mps_snapshots["before"]._tensors)
    assert result.metadata()["snapshot_native_tensor_bytes"] == native_storage_bytes(roots)
    assert result.data("before")["tensors"][0]["imag"][0][1][0] != 0
    del groups, first, states, state, untouched, roots, result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_repeated_serialized_data_preserves_schema_without_native_copy_or_charge(monkeypatch):
    ledger = Ledger()
    with ResourceScope(ledger):
        result = MatrixProductStateBackend().run(Circuit(1).h(0).phase(.2, 0).save_state(label="saved")).result()
    before = ledger.receipt()["live_memory_bytes"]
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Serialized MPS data allocated a native tensor"))
        for _ in range(4):
            payload = result.data()
            assert payload["saved"]["format"] == "quantumbridge.mps.v1"
            payload["saved"]["tensors"][0]["real"][0][0][0] = 99
    assert result.data("saved")["tensors"][0]["real"][0][0][0] == pytest.approx(1/np.sqrt(2))
    assert ledger.receipt()["live_memory_bytes"] == before
    restored = Result.from_json(result.to_json())
    assert restored.data() == result.data()
    with pytest.raises(KeyError, match="native MPS"):
        restored.matrix_product_state("saved")


def test_shared_snapshot_roots_survive_another_result_release():
    ledger = Ledger()
    with ResourceScope(ledger):
        original = MatrixProductStateBackend().run(Circuit(2).save_matrix_product_state()).result()
    shared = Result(mps_snapshots=dict(original.mps_snapshots))
    amount = native_storage_bytes(original.mps_snapshots["matrix_product_state"]._tensors)
    del original
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == amount
    view = shared.mps_snapshots["matrix_product_state"]._tensors[0][:, :, :]
    retained = native_storage_bytes(view)
    del shared
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == retained
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_conditional_group_overflow_is_transactional_before_native_copy(monkeypatch):
    state = MatrixProductState.zero(1)
    circuit = Circuit(1, 1).save_matrix_product_state(pershot=True, conditional=True)
    context = SnapshotContext(circuit, "matrix_product_state", AerExecutionLimits(max_conditional_groups=1), finite_shots=True)
    branch, ledger = Branch(state, ClassicalStore(1)), Ledger()
    with ResourceScope(ledger):
        context.observe(circuit.operations[0], branch, None)
        before = ledger.receipt()["live_memory_bytes"]
        branch.store.bits[0] = 1
        with monkeypatch.context() as patch:
            patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Group failure allocated snapshot"))
            with pytest.raises(MemoryError, match="max_conditional_groups"):
                context.observe(circuit.operations[0], branch, None)
    assert set(context.cells) == {("matrix_product_state", "0x0")}
    assert context.groups == {("matrix_product_state", "0x0")}
    assert ledger.receipt()["live_memory_bytes"] == before
    del context
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_failed_snapshot_transfer_releases_when_error_owners_die(monkeypatch):
    ledger = Ledger()
    def failed(*a, **k):raise RuntimeError("injected snapshot transfer failure")
    with monkeypatch.context() as patch:
        patch.setattr(SnapshotContext, "native_mps_snapshots", failed)
        with ResourceScope(ledger):
            job = MatrixProductStateBackend().run(Circuit(2).save_matrix_product_state())
    assert job.status == "ERROR"
    assert ledger.receipt()["live_memory_bytes"] > 0
    del job
    gc.collect()
    receipt = ledger.receipt()
    assert receipt["live_memory_bytes"] == 0
    assert receipt["total_reserved_memory_bytes"] == receipt["total_released_memory_bytes"]


def test_native_aer_exposes_same_non_dense_labeled_result_path(monkeypatch):
    monkeypatch.setattr(MatrixProductState, "statevector", lambda *a, **k: pytest.fail("Aer expanded MPS snapshot"))
    circuit = Circuit(100).h(0)
    for wire in range(99):circuit.cx(wire, wire+1)
    circuit.save_matrix_product_state(label="ghz").z(99)
    ledger = Ledger()
    with ResourceScope(ledger):
        envelope = NativeAerSimulator("matrix_product_state", shots=None).run(circuit).result()
    saved = envelope.results[0].matrix_product_state("ghz")
    assert saved.peak_bond_dimension == 2
    assert saved.expectation_pauli("X"*100) == pytest.approx(1.)
    assert envelope.results[0].mps.expectation_pauli("X"*100) == pytest.approx(-1.)
    assert envelope.data()["ghz"]["peak_bond_dimension"] == 2
    del saved, envelope
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
