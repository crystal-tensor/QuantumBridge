# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent sparse data, complex matrices, layout and allocation contracts."""
import gc
import numpy as np
import pytest

from quantumbridge import SparseObservable
from quantumbridge.compiler import Layout
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits


IDENTITY = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.diag([1, -1]).astype(complex)
LOCAL = {"I": IDENTITY, "X": X, "Y": Y, "Z": Z,
         "+": (IDENTITY+X)/2, "-": (IDENTITY-X)/2, "r": (IDENTITY+Y)/2,
         "l": (IDENTITY-Y)/2, "0": (IDENTITY+Z)/2, "1": (IDENTITY-Z)/2}


def dense(rows):
    result = None
    for label, coefficient in rows:
        matrix = np.ones((1, 1), complex)
        for char in label:
            matrix = np.kron(matrix, LOCAL[char])
        result = coefficient*matrix if result is None else result+coefficient*matrix
    return result


def test_public_sparse_raw_schema_and_term_snapshot():
    value = SparseObservable.from_list([("XIZ", 2j), ("+1r", -0.5), ("III", 3)])
    assert value.num_qubits == 3 and value.num_terms == len(value) == 3
    np.testing.assert_array_equal(value.bit_terms[:], [1, 2, 11, 5, 10])
    np.testing.assert_array_equal(value.indices[:], [0, 2, 0, 1, 2])
    np.testing.assert_array_equal(value.boundaries[:], [0, 2, 5, 5])
    assert (value.coeffs[:].dtype, value.indices[:].dtype, value.boundaries[:].dtype) == (np.complex128, np.uint32, np.uint64)
    term = value[0]
    assert isinstance(term, SparseObservable.Term) and term.bit_labels() == "ZX"
    assert term.coeff == 2j and not term.indices.flags.writeable
    value.coeffs[0] = 7
    assert term.coeff == 2j and value.coeffs[0] == 7
    copied = value.coeffs[:]
    copied[0] = 10
    assert value.coeffs[0] == 7
    np.testing.assert_allclose(term.to_observable().to_matrix(), dense([("XIZ", 2j)]), atol=0, rtol=0)


def test_constructor_raw_roundtrip_sparse_sort_and_term_reconstruction():
    value = SparseObservable.from_sparse_list([("ZX", [2, 0], 1.5j), ("r", [1], -0.4)], 3)
    assert value.to_sparse_list() == [("XZ", [0, 2], 1.5j), ("r", [1], -0.4+0j)]
    rebuilt = SparseObservable.from_raw_parts(3, value.coeffs[:], value.bit_terms[:], value.indices[:], value.boundaries[:])
    assert rebuilt == value == SparseObservable.from_terms(list(value))
    np.testing.assert_allclose(value.to_matrix(), dense([("ZIX", 1.5j), ("IrI", -0.4)]), atol=0, rtol=0)
    for bad_indices in ([1, 0], [0, 0], [0, 3]):
        with pytest.raises(ValueError):
            SparseObservable.from_raw_parts(3, [1], [2, 1], bad_indices, [0, 2])


def test_sparse_arithmetic_and_projector_expansion_match_independent_complex_matrices():
    left = SparseObservable.from_list([("r+", 0.7j), ("IZ", 0.5)])
    right = SparseObservable.from_list([("X1", -0.4), ("ZI", 0.3j)])
    a, b = dense([("r+", 0.7j), ("IZ", 0.5)]), dense([("X1", -0.4), ("ZI", 0.3j)])
    for actual, expected in [(left+right, a+b), (left-right, a-b), (2j*left, 2j*a),
                             (left.adjoint(), a.conj().T), (left.conjugate(), a.conj()),
                             (left.transpose(), a.T), (left.compose(right), b@a),
                             (left.compose(right, front=True), a@b)]:
        np.testing.assert_allclose(actual.to_matrix(), expected, atol=3e-14, rtol=0)
    np.testing.assert_allclose(left.as_paulis().to_matrix(), a, atol=3e-14, rtol=0)
    np.testing.assert_allclose(left.tensor(SparseObservable("Y")).to_matrix(), np.kron(a, Y), atol=3e-14, rtol=0)
    np.testing.assert_allclose(left.expand(SparseObservable("Y")).to_matrix(), np.kron(Y, a), atol=3e-14, rtol=0)
    assert SparseObservable("Z").commutes(SparseObservable("Z"))
    assert not SparseObservable("Z").commutes(SparseObservable("X"))


def test_noncontiguous_idle_wire_layout_has_independent_matrix_meaning():
    value = SparseObservable.from_list([("XIZ", 2), ("YII", 0.5)])
    mapped = value.apply_layout([4, 0, 2], num_qubits=5)
    assert mapped.to_sparse_list() == [("XZ", [2, 4], 2+0j), ("Y", [2], 0.5+0j)]
    np.testing.assert_allclose(mapped.to_matrix(), dense([("ZIXII", 2), ("IIYII", 0.5)]), atol=0, rtol=0)
    assert value.apply_layout(Layout([4, 0, 2]), num_qubits=5) == mapped
    np.testing.assert_allclose(value.apply_layout([2, 1, 0]).to_matrix(), dense([("ZIX", 2), ("IIY", 0.5)]), atol=0, rtol=0)
    with pytest.raises(ValueError):
        value.apply_layout([0, 0, 1])
    with pytest.raises(OverflowError):
        value.apply_layout([-1, 0, 1])


def test_sparse_storage_and_term_views_keep_real_leases_after_owner_deletion():
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        value = SparseObservable("XIZ")
        term = value[0]
        view = memoryview(term.indices)
        assert ledger.receipt()["live_memory_bytes"] > 0
    del value, term
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 8
    assert view.tolist() == [0, 2]
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_sparse_group_exact_one_below_and_huge_projector_expansion_preflight(monkeypatch):
    # One term, two factors: complex coefficient + uint8 factors + uint32
    # indices + two uint64 boundaries = 42 bytes, acquired before allocation.
    for cap, allowed in [(42, True), (41, False)]:
        ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=cap))
        with ResourceScope(ledger):
            if allowed:
                value = SparseObservable("XIZ")
                assert ledger.receipt()["live_memory_bytes"] == 42
                del value
            else:
                calls = []
                original = np.empty
                with monkeypatch.context() as patch:
                    patch.setattr(np, "empty", lambda *a, **k: (calls.append(1), original(*a, **k))[1])
                    with pytest.raises(MemoryError):
                        SparseObservable("XIZ")
                assert calls == []
    value = SparseObservable.from_sparse_list([("+"*40, list(range(40)), 1)], 1000000)
    assert value.num_qubits == 1000000
    with pytest.raises(MemoryError):
        value.as_paulis()


def test_projector_products_remain_qubit_sparse_without_pauli_expansion():
    value = SparseObservable.from_sparse_list([("+"*40, list(range(40)), 1)], 1000000)
    product = value.compose(value)
    assert product == value
    complement = SparseObservable.from_sparse_list([("-", [0], 1)], 1)
    # Compose on a noncontiguous single qubit with orthogonal eigenprojectors.
    assert value.compose(complement, qargs=[17]).num_terms == 0


def test_from_terms_stops_stream_at_budget_and_rejects_opaque_field_indices():
    term, consumed = SparseObservable("Z")[0], []

    def stream():
        for index in range(1000):
            consumed.append(index)
            yield term

    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=80))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        SparseObservable.from_terms(stream())
    assert consumed == [0, 1, 2] and ledger.receipt()["live_memory_bytes"] == 0

    class OpaqueIndex:
        def __array__(self, *args, **kwargs):
            raise AssertionError("Opaque index must not allocate or execute")

    with pytest.raises(TypeError):
        term.to_observable().indices[OpaqueIndex()]


def test_term_integer_contract_and_empty_pauli_width():
    assert SparseObservable.zero(5).pauli_bases().shape == (0, 5)
    for bits, indices, exception in (([2.5], [0], TypeError), ([2], [0.1], TypeError),
                                      ([-1], [0], ValueError), ([2], [-1], OverflowError)):
        with pytest.raises(exception):
            SparseObservable.Term(1, 1, bits, indices)
