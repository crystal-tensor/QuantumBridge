# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Observable and IR conversions must admit known outputs before allocation."""

import gc

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliY
from quantumbridge.devices.density_matrix_device import DensityMatrixDevice
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.array_ownership import native_storage_bytes
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.ir.qb_ir import _matrix_to_ir, matrix_from_ir
from quantumbridge.operators import Pauli, SparsePauliOperator
from quantumbridge.utils.math import observable_matrix, validate_observable_matrix


@pytest.mark.parametrize("kind", ["pauli_string", "hamiltonian", "pauli"])
def test_dense_pauli_output_denied_before_any_matrix_factory(kind, monkeypatch):
    width = 5
    observable = PauliY(1) if kind == "pauli_string" else Hamiltonian([(.3, PauliX(0)), (.7, PauliY(1))])
    if kind == "pauli":observable = Pauli("IYIXZ")
    ledger = Ledger(Limits(max_total_memory_bytes=16*(1 << (2*width))-1))
    def forbidden(*args, **kwargs):pytest.fail("Dense observable allocation preceded its byte reservation")
    for name in ("zeros", "empty", "kron"):monkeypatch.setattr(np, name, forbidden)
    with ResourceScope(ledger), pytest.raises(MemoryError):
        if kind == "pauli":observable.to_matrix()
        else:observable_matrix(observable, width)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_observable_dtype_conversion_denied_before_numpy_coercion(monkeypatch):
    source = np.eye(8, dtype=np.float32)[:, ::-1]
    ledger = Ledger(Limits(max_total_memory_bytes=16*source.size-1))
    def forbidden(*args, **kwargs):pytest.fail("Observable dtype conversion happened before admission")
    monkeypatch.setattr(np, "asarray", forbidden)
    monkeypatch.setattr(np, "empty", forbidden)
    with ResourceScope(ledger), pytest.raises(MemoryError):
        observable_matrix(source, 3)


def test_observable_validation_scratch_denies_before_comparison(monkeypatch):
    source = np.eye(8, dtype=complex)
    ledger = Ledger(Limits(max_total_memory_bytes=100))
    monkeypatch.setattr(np, "allclose", lambda *a, **k: pytest.fail("Unreserved observable comparison workspace"))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Unreserved validation allocation"))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        DensityMatrixDevice._observable(source, 3)


def test_ir_complex_conversion_denied_before_any_component_array(monkeypatch):
    value = {"real": [[1., 0.], [0., 1.]], "imag": [[0., .2], [-.2, 0.]]}
    ledger = Ledger(Limits(max_total_memory_bytes=63))
    def forbidden(*args, **kwargs):pytest.fail("IR component conversion preceded output reservation")
    monkeypatch.setattr(np, "asarray", forbidden)
    monkeypatch.setattr(np, "empty", forbidden)
    with ResourceScope(ledger), pytest.raises(MemoryError):matrix_from_ir(value)


def test_strided_real_ir_export_denied_before_complex_dtype_copy(monkeypatch):
    value = np.arange(24., dtype=np.float32).reshape(4, 6)[:, ::2]
    ledger = Ledger(Limits(max_total_memory_bytes=16*value.size-1))
    def forbidden(*args, **kwargs):pytest.fail("Strided export dtype copy preceded reservation")
    monkeypatch.setattr(np, "asarray", forbidden)
    monkeypatch.setattr(np, "empty", forbidden)
    with ResourceScope(ledger), pytest.raises(MemoryError):_matrix_to_ir(value)


@pytest.mark.parametrize("label", ["II", "XY", "YZ", "ZX", "YY", "-iXY", "iYZ", "-ZZ"])
def test_native_pauli_dense_phase_wire_order_and_view_lifetime(label):
    bases = {"I": np.eye(2), "X": np.array([[0, 1], [1, 0]]),
        "Y": np.array([[0, -1j], [1j, 0]]), "Z": np.diag([1, -1])}
    phases = {"": 1, "-": -1, "i": 1j, "-i": -1j}
    prefix, body = label[:-2], label[-2:]
    expected = phases[prefix]*np.kron(bases[body[0]], bases[body[1]])
    ledger = Ledger()
    with ResourceScope(ledger):actual = Pauli(label).to_matrix()
    np.testing.assert_array_equal(actual, expected)
    view = actual[::-1, ::2]
    del actual
    assert ledger.receipt()["live_memory_bytes"] == 16*16
    del view
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_native_sparse_complex_sum_and_empty_observable_keep_width():
    operator = SparsePauliOperator([("XY", .3+.2j), ("ZI", -.7j)])
    expected = operator.matrix()
    ledger = Ledger()
    with ResourceScope(ledger):
        actual = observable_matrix(operator, 2)
        empty = observable_matrix(SparsePauliOperator([]), 3)
    np.testing.assert_allclose(actual, expected, atol=1e-15)
    np.testing.assert_array_equal(empty, np.zeros((8, 8)))
    assert ledger.receipt()["live_memory_bytes"] == actual.nbytes+empty.nbytes
    del actual, empty
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("rtol", [0, 1e-5])
def test_explicit_validation_arena_matches_numpy_and_releases(rtol):
    matrix = np.array([[.3, .2+.4j], [.2-.4j, -.7]], complex)
    ledger = Ledger()
    with ResourceScope(ledger):
        assert validate_observable_matrix(matrix, 1, rtol=rtol)
        matrix[0, 1] += .1j
        assert not validate_observable_matrix(matrix, 1, rtol=rtol)
        matrix[0, 0] = np.inf
        assert not validate_observable_matrix(matrix, 1, rtol=rtol)
    receipt = ledger.receipt()
    assert receipt["live_memory_bytes"] == 0
    assert receipt["observed_array_bytes"]["observable_validation_workspace"] == 33*4
    assert receipt["total_reserved_memory_bytes"] == receipt["total_released_memory_bytes"]


def test_ir_strides_components_views_and_repeated_aliases_have_one_new_root():
    source = np.arange(24., dtype=np.float32).reshape(4, 6)[:, ::2]
    ledger = Ledger()
    with ResourceScope(ledger):actual = matrix_from_ir({"real": source, "imag": source})
    np.testing.assert_array_equal(actual, source+1j*source)
    assert ledger.receipt()["live_memory_bytes"] == actual.nbytes == native_storage_bytes(actual)
    real_view = actual.real[::-1]
    del actual
    assert ledger.receipt()["live_memory_bytes"] == 16*source.size
    del real_view
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_managed_conversion_never_dispatches_opaque_array_or_matrix_hooks():
    from quantumbridge.core.classical import UnsupportedFeature
    from quantumbridge.execution.array_reservations import numeric_array
    calls = []
    class Opaque:
        def __array__(self, *a, **k):calls.append("array");raise AssertionError()
        def to_matrix(self, *a, **k):calls.append("matrix");raise AssertionError()
    with ResourceScope(Ledger()), pytest.raises(UnsupportedFeature):numeric_array(Opaque())
    with ResourceScope(Ledger()), pytest.raises(UnsupportedFeature):observable_matrix(Opaque(), 2)
    assert calls == []


def test_ir_malformed_shapes_cycles_and_complex_components_fail_before_allocating(monkeypatch):
    cyclic = [];cyclic.append(cyclic)
    invalid = [{"real": [[1., 0.]], "imag": [[0.], [0.]]},
        {"real": [1+1j], "imag": [0.]}, cyclic]
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Malformed IR allocated a buffer"))
    for value in invalid:
        with ResourceScope(Ledger()), pytest.raises(ValueError):matrix_from_ir(value)


def test_complex_mps_tolist_export_is_not_a_fabricated_array_copy(monkeypatch):
    from quantumbridge.information import MatrixProductState
    state = MatrixProductState.zero(2)
    state._tensors[0] = state._tensors[0][:, ::-1]
    ledger = Ledger(Limits(max_total_memory_bytes=0))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("MPS tolist allocated ndarray"))
    monkeypatch.setattr(np, "asarray", lambda *a, **k: pytest.fail("MPS tolist coerced ndarray"))
    with ResourceScope(ledger):payload = state.to_dict()
    assert payload["tensors"][0]["real"][0][1][0] == 1
    assert ledger.receipt()["live_memory_bytes"] == 0
