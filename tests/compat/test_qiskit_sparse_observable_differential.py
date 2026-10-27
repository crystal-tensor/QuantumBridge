# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Public SDK contracts with independent matrix and bidirectional CSR checks."""

import numpy as np
import pytest

from quantumbridge import SparseObservable
from quantumbridge.primitives import ObservablesArray

PublicArray = pytest.importorskip("qiskit.primitives").ObservablesArray
PublicSparse = pytest.importorskip("qiskit.quantum_info").SparseObservable
SparsePauliOp = pytest.importorskip("qiskit.quantum_info").SparsePauliOp


def matrix(label):
    axes = {"I": np.eye(2), "X": np.array([[0, 1], [1, 0]]),
            "Y": np.array([[0, -1j], [1j, 0]]), "Z": np.diag([1, -1])}
    for plus, minus, axis in (("+", "-", "X"), ("r", "l", "Y"), ("0", "1", "Z")):
        axes[plus], axes[minus] = (axes["I"] + axes[axis])/2, (axes["I"] - axes[axis])/2
    result = np.ones((1, 1), complex)
    for char in label:
        result = np.kron(result, axes[char])
    return result


def public_matrix(value):
    return SparsePauliOp.from_sparse_observable(value).to_matrix()


def transfer(value, cls):
    return cls.from_raw_parts(value.num_qubits, *(getattr(value, field)[:] for field in
        ("coeffs", "bit_terms", "indices", "boundaries")))


def test_complex_projector_csr_and_terms_round_trip_in_both_directions():
    terms = [("XIZ", 2j), ("+1r", -0.5), ("III", 3)]
    native, public = SparseObservable.from_list(terms), PublicSparse.from_list(terms)
    for field in ("coeffs", "bit_terms", "indices", "boundaries"):
        np.testing.assert_array_equal(getattr(native, field)[:], getattr(public, field)[:])
    expected = sum(coefficient*matrix(label) for label, coefficient in terms)
    np.testing.assert_allclose(transfer(public, SparseObservable).to_matrix(), expected, atol=1e-14)
    np.testing.assert_allclose(public_matrix(transfer(native, PublicSparse)), expected, atol=1e-14)
    for left, right in zip(native, public):
        assert (left.num_qubits, left.coeff, left.bit_labels()) == (right.num_qubits, right.coeff, right.bit_labels())
        np.testing.assert_array_equal(left.indices, right.indices)
        assert not left.indices.flags.writeable and not right.indices.flags.writeable


@pytest.mark.parametrize("left", "IXYZ+-rl01")
@pytest.mark.parametrize("right", "IXYZ+-rl01")
def test_all_single_factor_products_match_public_and_independent_math(left, right):
    a, b = SparseObservable(left), SparseObservable(right)
    pa, pb = PublicSparse(left), PublicSparse(right)
    for front in (False, True):
        result, reference = a.compose(b, front=front), pa.compose(pb, front=front)
        expected = matrix(left) @ matrix(right) if front else matrix(right) @ matrix(left)
        np.testing.assert_allclose(result.to_matrix(), expected, atol=1e-14)
        np.testing.assert_allclose(result.to_matrix(), public_matrix(reference), atol=1e-14)
        np.testing.assert_allclose(public_matrix(transfer(result, PublicSparse)), expected, atol=1e-14)


@pytest.mark.parametrize("method", ["adjoint", "transpose", "conjugate", "as_paulis"])
def test_multiqubit_complex_projector_operations(method):
    terms = [("rl1", 2j), ("+YZ", -0.5+0.3j)]
    native, public = SparseObservable.from_list(terms), PublicSparse.from_list(terms)
    source = sum(coefficient*matrix(label) for label, coefficient in terms)
    expected = {"adjoint": source.conj().T, "transpose": source.T,
                "conjugate": source.conj(), "as_paulis": source}[method]
    np.testing.assert_allclose(getattr(native, method)().to_matrix(), expected, atol=1e-14)
    np.testing.assert_allclose(public_matrix(getattr(public, method)()), expected, atol=1e-14)


def ownership(cls, sparse):
    source = sparse("IZ")
    array = cls([[source], [sparse("XI")]], copy=False)
    first = array.slice((0, 0))
    assert isinstance(first, sparse) and first is array.slice((0, 0))
    first.coeffs[0] = 3
    copied = array.sparse_observables_array(copy=True)
    copied[0, 0].coeffs[0] = 9
    array.reshape(-1).slice(1).coeffs[0] = -2
    raw = array.sparse_observables_array(copy=False)
    raw[1, 0] = sparse("IY")
    return (array.tolist(), source.to_sparse_list(), array[0, 0],
            [item.shape for item in array], array.reshape(-1).shape)


def test_typed_container_aliases_deep_copies_iteration_and_scalar_dicts():
    assert ownership(ObservablesArray, SparseObservable) == ownership(PublicArray, PublicSparse)
    native, public = ObservablesArray.coerce_observable("-Z"), PublicArray.coerce_observable("-Z")
    assert isinstance(native, SparseObservable) and isinstance(public, PublicSparse)
    assert native.to_sparse_list() == public.to_sparse_list()


@pytest.mark.parametrize("layout,width", [([2, 1, 0], 3), ([4, 0, 2], 5), (None, 6)])
def test_layout_outputs_match_actual_public_csr_and_array_contract(layout, width):
    rows = [("XIZ", 0.5), ("Y+I", -0.2)]
    native, public = SparseObservable.from_list(rows), PublicSparse.from_list(rows)
    got, expected = native.apply_layout(layout, width), public.apply_layout(layout, width)
    assert got.to_sparse_list() == expected.to_sparse_list()
    np.testing.assert_allclose(got.to_matrix(), public_matrix(expected), atol=1e-14)
    array = ObservablesArray([[native]]).apply_layout(layout, width)
    reference = PublicArray([[public]]).apply_layout(layout, width)
    assert array.shape == reference.shape and array.tolist() == reference.tolist()


@pytest.mark.parametrize("case", ["duplicate", "negative", "shrinking", "bad_width", "bad_label", "imaginary", "empty"])
def test_public_invalid_inputs_have_matching_exception_categories(case):
    def execute(sparse, array):
        if case == "duplicate":
            return sparse("XZ").apply_layout([0, 0])
        if case == "negative":
            return sparse("XZ").apply_layout([-1, 0])
        if case == "shrinking":
            return sparse("XZ").apply_layout([1, 0], 1)
        if case == "bad_width":
            return sparse.from_list([("X", 1), ("ZZ", 2)])
        if case == "bad_label":
            return sparse("AB")
        if case == "imaginary":
            return array(sparse.from_list([("Z", 1j)]))
        return array(sparse.zero(2))
    with pytest.raises(Exception) as reference:
        execute(PublicSparse, PublicArray)
    with pytest.raises(type(reference.value)):
        execute(SparseObservable, ObservablesArray)


@pytest.mark.parametrize("qargs", [[0, 2], [2, 0]])
@pytest.mark.parametrize("front", [False, True])
def test_noncontiguous_composition_has_independent_basis_embedding(qargs, front):
    rows = [("rIZ", 0.7j), ("X+I", -0.2)]
    others = [("l1", 0.3), ("YX", -0.4j)]
    native, other = SparseObservable.from_list(rows), SparseObservable.from_list(others)
    reference = PublicSparse.from_list(rows).compose(PublicSparse.from_list(others), qargs=qargs, front=front)
    a = sum(coefficient*matrix(label) for label, coefficient in rows)
    b = sum(coefficient*matrix(label) for label, coefficient in others)
    embedded = np.zeros((8, 8), complex)
    for source in range(8):
        column = sum(((source >> wire) & 1) << index for index, wire in enumerate(qargs))
        for row in range(4):
            target = source
            for index, wire in enumerate(qargs):
                target = (target & ~(1 << wire)) | (((row >> index) & 1) << wire)
            embedded[target, source] = b[row, column]
    expected = a @ embedded if front else embedded @ a
    actual = native.compose(other, qargs=qargs, front=front)
    np.testing.assert_allclose(actual.to_matrix(), expected, atol=2e-14)
    np.testing.assert_allclose(public_matrix(reference), expected, atol=2e-14)


def test_tensor_expand_evolve_and_native_legacy_pauli_boundary():
    from qiskit.quantum_info import Pauli as PublicPauli
    from quantumbridge.operators import Pauli, SparsePauliOperator

    native, public = SparseObservable("rl"), PublicSparse("rl")
    for method in ("tensor", "expand"):
        result = getattr(native, method)(SparseObservable("X0"))
        reference = getattr(public, method)(PublicSparse("X0"))
        expected = np.kron(matrix("rl"), matrix("X0")) if method == "tensor" else np.kron(matrix("X0"), matrix("rl"))
        np.testing.assert_allclose(result.to_matrix(), expected, atol=1e-14)
        np.testing.assert_allclose(public_matrix(reference), expected, atol=1e-14)
    np.testing.assert_allclose(native.evolve(Pauli("-iXY")).to_matrix(),
                               public_matrix(public.evolve(PublicPauli("-iXY"))), atol=1e-14)
    # Existing native SparsePauliOperator uses q0-first dense labels. It is
    # not silently renamed or treated as a public little-endian SparsePauliOp.
    legacy = SparsePauliOperator([("XZ", 2j)])
    converted = SparseObservable.from_sparse_pauli_op(legacy)
    np.testing.assert_allclose(converted.to_matrix(), 2j*matrix("ZX"), atol=1e-14)


def test_typed_sparse_estimator_broadcast_and_precision_match_public_and_math():
    from qiskit import QuantumCircuit
    from qiskit.circuit import Parameter as PublicParameter
    from qiskit.primitives import StatevectorEstimator as PublicEstimator
    from quantumbridge import Circuit, Parameter, StatevectorEstimator

    theta, phi = Parameter("theta"), Parameter("phi")
    public_theta, public_phi = PublicParameter("theta"), PublicParameter("phi")
    circuit = Circuit(3).ry(theta, 2).rz(phi, 2)
    reference = QuantumCircuit(3)
    reference.ry(public_theta, 2)
    reference.rz(public_phi, 2)
    t, p = np.array([[0.1, 0.3], [0.5, -0.7]]), np.array([[0.2, -0.4], [0.6, 0.8]])
    values = np.stack([t if parameter == theta else p for parameter in circuit.parameters], axis=-1)
    public_values = np.stack([t if parameter == public_theta else p for parameter in reference.parameters], axis=-1)
    rows = [[("ZII", 0.7), ("III", -0.1)], [("XII", -0.4)], [("YII", 0.3)]]
    observables = ObservablesArray([[[SparseObservable.from_list(terms)]] for terms in rows])
    public_observables = PublicArray([[[PublicSparse.from_list(terms)]] for terms in rows])
    mean = np.stack([0.7*np.cos(t)-0.1, -0.4*np.sin(t)*np.cos(p), 0.3*np.sin(t)*np.sin(p)])
    for precision in (0, 0.03):
        got = StatevectorEstimator(seed=17).run([(circuit, observables, values)], precision=precision).result()[0]
        expected = PublicEstimator(seed=17).run([(reference, public_observables, public_values)], precision=precision).result()[0]
        assert got.data.evs.shape == expected.data.evs.shape == (3, 2, 2)
        np.testing.assert_allclose(got.data.evs, expected.data.evs, atol=3e-14, rtol=0)
        np.testing.assert_allclose(got.data.evs, mean if not precision else np.random.default_rng(17).normal(mean, precision), atol=3e-14, rtol=0)
        np.testing.assert_array_equal(got.data.stds, expected.data.stds)


def test_zero_point_wide_projector_pub_does_not_materialize_state_or_labels():
    from qiskit import QuantumCircuit
    from qiskit.circuit import Parameter as PublicParameter
    from qiskit.primitives import StatevectorEstimator as PublicEstimator
    from quantumbridge import Circuit, Parameter, StatevectorEstimator

    circuit = Circuit(64).ry(Parameter("theta"), 0)
    public_circuit = QuantumCircuit(64)
    public_circuit.ry(PublicParameter("theta"), 0)
    observable = SparseObservable.from_sparse_list([("+", [0], 1)], 64)
    reference = PublicSparse.from_sparse_list([("+", [0], 1)], 64)
    got = StatevectorEstimator().run([(circuit, observable, np.empty((0, 1)))]).result()[0]
    expected = PublicEstimator().run([(public_circuit, reference, np.empty((0, 1)))]).result()[0]
    assert got.data.evs.shape == expected.data.evs.shape == (0,)


def test_empty_pauli_bases_preserve_actual_width():
    got, expected = SparseObservable.zero(5).pauli_bases(), PublicSparse.zero(5).pauli_bases()
    assert got.shape == expected.shape == (0, 5)
    assert got.to_labels() == expected.to_labels() == []


@pytest.mark.parametrize("bits,wires", [([2.5], [0]), ([2], [0.1]), ([-1], [0]), ([2], [-1])])
def test_term_constructor_rejects_lossy_integer_conversion_like_public(bits, wires):
    with pytest.raises(Exception) as reference:
        PublicSparse.Term(1, 1, bits, wires)
    with pytest.raises(type(reference.value)):
        SparseObservable.Term(1, 1, bits, wires)
