# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Gate, channel, CSR and snapshot admission precedes numerical factories."""

import gc

import numpy as np
import pytest

from quantumbridge import Circuit
from quantumbridge.core.classical import ClassicalStore
from quantumbridge.devices.execution import prepare_program
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.control_flow_engine import Branch
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.operators import Pauli
from quantumbridge.simulator.snapshots import SnapshotContext
from quantumbridge.utils.math import validate_kraus_operators


def test_gate_validation_rejects_before_identity_or_workspace_factory(monkeypatch):
    import quantumbridge.utils.math as math
    circuit, matrix = Circuit(1).x(0), np.eye(2, dtype=complex)
    monkeypatch.setattr(math, "gate_matrix", lambda *a, **k: matrix)
    def forbidden(*a, **k):pytest.fail("Gate validation allocated before admission")
    monkeypatch.setattr(np, "eye", forbidden)
    monkeypatch.setattr(np, "empty", forbidden)
    ledger = Ledger(Limits(max_total_memory_bytes=0))
    with ResourceScope(ledger), pytest.raises(MemoryError):prepare_program(circuit)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_kraus_group_rejects_before_first_copy_or_validation_factory(monkeypatch):
    operators = (np.eye(2, dtype=complex), np.zeros((2, 2), complex))
    def forbidden(*a, **k):pytest.fail("Kraus matrices allocated before group admission")
    monkeypatch.setattr(np, "array", forbidden)
    monkeypatch.setattr(np, "empty", forbidden)
    ledger = Ledger(Limits(max_total_memory_bytes=127))
    with ResourceScope(ledger), pytest.raises(MemoryError):validate_kraus_operators(operators)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_sparse_csr_rejects_all_three_buffers_before_scipy(monkeypatch):
    sparse = pytest.importorskip("scipy.sparse")
    monkeypatch.setattr(sparse, "csr_matrix", lambda *a, **k: pytest.fail("CSR constructor preceded admission"))
    # The scalar Pauli's old dense buffer fits (16); CSR needs 16+4+8.
    ledger = Ledger(Limits(max_total_memory_bytes=27))
    with ResourceScope(ledger), pytest.raises(MemoryError):Pauli("").to_matrix(sparse=True)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_dense_snapshot_aggregation_rejects_before_retained_buffer_factory(monkeypatch):
    circuit = Circuit(1).save_probabilities(label="p")
    context = SnapshotContext(circuit, "statevector")
    branch = Branch(np.array([1., 0.], complex), ClassicalStore(0))
    def forbidden(*a, **k):pytest.fail("Snapshot aggregation allocated before admission")
    monkeypatch.setattr(np, "zeros_like", forbidden)
    monkeypatch.setattr(np, "empty", forbidden)
    ledger = Ledger(Limits(max_total_memory_bytes=0))
    with ResourceScope(ledger), pytest.raises(MemoryError):context.observe(circuit.operations[0], branch, None)
    assert context.cells == {} and context.bytes == 0
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("dimension", [1, 2, 4, 8])
def test_unitary_validation_uses_only_column_arena_and_preserves_tolerance(dimension, monkeypatch):
    from quantumbridge.utils.math import validate_unitary_matrix
    rng = np.random.default_rng(7)
    matrix, _ = np.linalg.qr(rng.normal(size=(dimension, dimension))+1j*rng.normal(size=(dimension, dimension)))
    cases = [matrix, matrix[::-1, :], matrix*.9, matrix*(1+1e-8)]
    invalid = matrix.copy();invalid[0, 0] = np.inf
    cases.append(invalid)
    expected = [np.all(np.isfinite(value)) and np.allclose(value.conj().T@value, np.eye(dimension), atol=1e-10, rtol=0) for value in cases]
    ledger = Ledger()
    with monkeypatch.context() as patch:
        patch.setattr(np, "eye", lambda *a, **k: pytest.fail("Dense validation identity"))
        patch.setattr(np, "allclose", lambda *a, **k: pytest.fail("Hidden allclose arrays"))
        with ResourceScope(ledger):
            assert [validate_unitary_matrix(value) for value in cases] == expected
            assert validate_unitary_matrix(matrix[:, :-1]) is False
    receipt = ledger.receipt()
    assert receipt["live_memory_bytes"] == 0
    assert receipt["observed_array_bytes"]["isometry_validation_workspace"] == 33*dimension


def test_kraus_workspace_admitted_with_whole_group_before_any_copy(monkeypatch):
    operators = (np.eye(2, dtype=complex), np.zeros((2, 2), complex))
    ledger = Ledger(Limits(max_total_memory_bytes=128+66-1))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Kraus copied before scratch admission"))
    with ResourceScope(ledger), pytest.raises(MemoryError):validate_kraus_operators(operators)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_kraus_phase_strides_copies_lifetime_and_failure_recovery():
    p = .23
    source = (np.array([[1, 0], [0, np.sqrt(1-p)]], complex),
              np.array([[0, np.sqrt(p)], [0, 0]], complex))
    source = tuple((1j*value).T.copy().T for value in source)
    ledger = Ledger(Limits(max_total_memory_bytes=260))
    with ResourceScope(ledger):
        copied = validate_kraus_operators(source)
        assert ledger.receipt()["live_memory_bytes"] == 128
        for actual, expected in zip(copied, source):
            np.testing.assert_array_equal(actual, expected)
            assert not np.shares_memory(actual, expected)
        with pytest.raises(MemoryError):validate_kraus_operators(source)
        view = copied[0][:, 1:]
        del copied, actual
        gc.collect()
        assert ledger.receipt()["live_memory_bytes"] == 64
        del view
        gc.collect()
        recovered = validate_kraus_operators(source)
        del recovered
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_kraus_bad_shapes_and_opaque_protocol_never_enter_factories(monkeypatch):
    from quantumbridge.core.classical import UnsupportedFeature
    class Opaque:
        def __array__(self, *a, **k):pytest.fail("Opaque Kraus protocol executed")
        def __iter__(self):pytest.fail("Opaque Kraus sequence executed")
    inputs = [([], ValueError), (([[1, 0]],), ValueError), ((Opaque(),), UnsupportedFeature), (Opaque(), UnsupportedFeature)]
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Malformed Kraus allocation"))
    for operators, error in inputs:
        with ResourceScope(Ledger()), pytest.raises(error):validate_kraus_operators(operators)


@pytest.mark.parametrize("label", ["", "X", "Y", "-iXYZ", "iYZY", "-YYX"])
def test_sparse_csr_roots_phase_order_and_user_view_lifetime(label, monkeypatch):
    pytest.importorskip("scipy.sparse")
    import quantumbridge.utils.math as math
    expected = Pauli(label).to_matrix()
    ledger = Ledger()
    monkeypatch.setattr(math, "_pauli_dense", lambda *a, **k: pytest.fail("CSR took a dense fallback"))
    with ResourceScope(ledger):result = Pauli(label).to_matrix(sparse=True)
    np.testing.assert_array_equal(result.toarray(), expected)
    data, indices, indptr = result.data, result.indices, result.indptr
    amount = data.nbytes+indices.nbytes+indptr.nbytes
    assert ledger.receipt()["live_memory_bytes"] == amount
    del result
    view = data[::2]
    del data, indices, indptr
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == expected.shape[0]*16
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("kind", ["probabilities", "density_matrix", "expectation_value", "expectation_value_variance"])
def test_snapshot_managed_aggregation_matches_old_public_schema(kind):
    from quantumbridge.simulator.snapshots import decode
    circuit = Circuit(2)
    options = {"observable": Pauli("YZ")} if kind.startswith("expectation") else {}
    getattr(circuit, "save_"+kind)(label="s", **options)
    rng = np.random.default_rng(4)
    state = rng.normal(size=4)+1j*rng.normal(size=4);state /= np.linalg.norm(state)
    legacy, managed = SnapshotContext(circuit, "statevector"), SnapshotContext(circuit, "statevector")
    for phase, weight in ((1., .3), (1j, .7)):
        legacy.observe(circuit.operations[0], Branch(phase*state, ClassicalStore(0), weight=weight), None)
    expected = legacy.metadata()["saved_snapshots"]
    ledger = Ledger()
    with ResourceScope(ledger):
        for phase, weight in ((1., .3), (1j, .7)):
            managed.observe(circuit.operations[0], Branch(phase*state, ClassicalStore(0), weight=weight), None)
        actual = managed.metadata()["saved_snapshots"]
    assert set(actual["s"]) == set(expected["s"])
    np.testing.assert_allclose(decode(actual)["s"], decode(expected)["s"], atol=1e-14, rtol=0)
    assert ledger.receipt()["live_memory_bytes"] == managed.cells[("s", "")]["value"].nbytes
    del managed
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_snapshot_overbudget_update_keeps_old_cell_then_recovers():
    circuit = Circuit(1).save_probabilities(label="p")
    context = SnapshotContext(circuit, "statevector")
    branch = Branch(np.array([1., 0.], complex), ClassicalStore(0))
    ledger = Ledger(Limits(max_total_memory_bytes=64))
    with ResourceScope(ledger):
        context.observe(circuit.operations[0], branch, None)
        first = context.cells[("p", "")]
        from quantumbridge.execution.array_ownership import retained_array
        held = retained_array(ledger, "test_live_array", (3,), float)
        with pytest.raises(MemoryError):context.observe(circuit.operations[0], branch, None)
        assert context.cells[("p", "")] is first and first["weight"] == 1
        del held, first
        gc.collect()
        context.observe(circuit.operations[0], branch, None)
        assert context.cells[("p", "")]["weight"] == 2
    del context
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("representation", ["Kraus", "SuperOp", "Choi", "PTM", "Chi", "Stinespring"])
def test_cptp_validation_rejects_before_choi_or_eigen_factory(representation, monkeypatch):
    import quantumbridge.information as information
    source = information.Kraus([np.eye(2, dtype=complex)])
    channel = getattr(information, representation)(source)
    def forbidden(*a, **k):pytest.fail("CPTP validation allocated before admission")
    monkeypatch.setattr(np.linalg, "eigvalsh", forbidden)
    monkeypatch.setattr(np, "empty", forbidden)
    ledger = Ledger(Limits(max_total_memory_bytes=0))
    with ResourceScope(ledger), pytest.raises(MemoryError):channel.is_cptp()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("representation", ["Kraus", "SuperOp", "Choi", "PTM", "Chi", "Stinespring"])
def test_cptp_native_representations_preserve_public_numerical_judgments(representation):
    import quantumbridge.information as information
    p = .37
    source = information.Kraus([np.array([[1, 0], [0, np.sqrt(1-p)]], complex),
        np.array([[0, np.sqrt(p)], [0, 0]], complex)])
    channel = getattr(information, representation)(source)
    expected = [channel.is_cp(), channel.is_tp(), channel.is_cptp()]
    expected_choi = channel.to_choi().data
    from quantumbridge.information.channels import _validation_choi
    ledger = Ledger()
    with ResourceScope(ledger):
        choi = _validation_choi(channel)
        np.testing.assert_allclose(choi, expected_choi, atol=1e-14, rtol=0)
        assert [channel.is_cp(), channel.is_tp(), channel.is_cptp()] == expected == [True, True, True]
        del choi
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("scale", [0., .7, 1., 1+1e-8, -1.])
def test_cptp_nonpositive_trace_and_tolerance_match_legacy(scale):
    from quantumbridge.information import Kraus, Choi
    channel = Choi(Kraus([np.eye(2)]))
    channel.data *= scale
    expected = [channel.is_cp(atol=1e-10, rtol=0), channel.is_tp(atol=1e-10, rtol=0), channel.is_cptp(atol=1e-10, rtol=0)]
    ledger = Ledger()
    with ResourceScope(ledger):
        assert [channel.is_cp(atol=1e-10, rtol=0), channel.is_tp(atol=1e-10, rtol=0), channel.is_cptp(atol=1e-10, rtol=0)] == expected
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("representation", ["Kraus", "SuperOp", "Choi", "Stinespring"])
def test_rectangular_and_generalized_kraus_cp_tp_match_legacy(representation):
    import quantumbridge.information as information
    # Native rectangular maps are not restricted to qubit square dimensions.
    matrix = np.array([[1, 0], [0, 1], [0, 0]], complex)
    source = information.Kraus([matrix])
    channel = getattr(information, representation)(source)
    expected = [channel.is_cp(), channel.is_tp(), channel.is_cptp()]
    with ResourceScope(Ledger()):
        assert [channel.is_cp(), channel.is_tp(), channel.is_cptp()] == expected


def test_saved_dense_data_user_view_outlives_context_and_result():
    from quantumbridge.results import Result
    circuit = Circuit(1).save_statevector(label="s", pershot=True)
    context = SnapshotContext(circuit, "statevector", finite_shots=True)
    state = np.array([1., 1j], complex)/np.sqrt(2)
    branch, ledger = Branch(state, ClassicalStore(0)), Ledger()
    with ResourceScope(ledger):
        context.observe(circuit.operations[0], branch, None)
        result = Result(metadata_data=context.metadata())
        exported = result.data("s")
        view = exported[0][1:]
    np.testing.assert_array_equal(state, context.cells[("s", "")]["value"][0])
    state[:] = 0
    del result, context, exported
    gc.collect()
    assert view[0] == pytest.approx(1j/np.sqrt(2))
    assert ledger.receipt()["live_memory_bytes"] == 32
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_generalized_complex_channel_validation_preserves_cp_and_tp():
    from quantumbridge.information import Kraus, SuperOp, Choi, Stinespring
    left = np.array([[1, .2j], [.1, .7]], complex)
    right = np.array([[1, -.3], [.4j, .6]], complex)
    source = Kraus(([left], [right]))
    for cls in (Kraus, SuperOp, Choi, Stinespring):
        channel = cls(source)
        expected = [channel.is_cp(), channel.is_tp(), channel.is_cptp()]
        with ResourceScope(Ledger()):
            assert [channel.is_cp(), channel.is_tp(), channel.is_cptp()] == expected


def test_nonfinite_and_opaque_channel_validation_does_not_dispatch_foreign_hooks():
    from quantumbridge.information import Kraus, Choi
    from quantumbridge.core.classical import UnsupportedFeature
    from quantumbridge.information.channels import _validation_choi
    channel = Choi(Kraus([np.eye(2)]));channel.data[0, 0] = np.nan
    class Opaque:
        def to_choi(self):pytest.fail("Foreign channel conversion executed")
    with ResourceScope(Ledger()):
        assert not channel.is_cp()
        with pytest.raises(UnsupportedFeature):_validation_choi(Opaque())


@pytest.mark.parametrize("method", ["statevector", "density_matrix"])
def test_density_snapshot_permuted_wires_and_noncontiguous_input_match_legacy(method):
    rng = np.random.default_rng(11)
    vector = rng.normal(size=8)+1j*rng.normal(size=8);vector /= np.linalg.norm(vector)
    state = vector if method == "statevector" else np.outer(vector, vector.conj())
    state = state[::-1] if method == "statevector" else state[::-1, ::-1]
    circuit = Circuit(3).save_density_matrix([2, 0], label="rho")
    legacy, managed = SnapshotContext(circuit, method), SnapshotContext(circuit, method)
    expected = legacy._density(state, (2, 0))
    with ResourceScope(Ledger()):actual = managed._density(state, (2, 0))
    np.testing.assert_allclose(actual, expected, atol=1e-14, rtol=0)
