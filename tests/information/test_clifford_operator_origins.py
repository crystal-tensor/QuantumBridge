# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Native/literal source closure with the existing projective Clifford phase."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.information import Operator, Clifford


def source(width=2):
    return qb.Circuit(width).h(0).s(width - 1).cx(0, width - 1).cz(width - 1, 0).swap(0, 1).sdg(1)


def reverse(matrix):
    width = len(matrix).bit_length() - 1
    order = [int(format(i, f"0{width}b")[::-1], 2) for i in range(len(matrix))]
    return matrix[np.ix_(order, order)]


def projective(matrix):
    pivot = next(value for value in matrix[:, 0] if abs(value) > 1e-10)
    return matrix * pivot.conjugate() / abs(pivot)


def public_radix_matrix(matrix, dims):
    from itertools import product
    order = [0] * len(matrix)
    for digits in product(*(range(dim) for dim in dims)):
        native = public = 0
        for digit, dim in zip(digits, dims):native = native * dim + digit
        for digit, dim in zip(reversed(digits), reversed(dims)):public = public * dim + digit
        order[public] = native
    return matrix[np.ix_(order, order)]


@pytest.mark.parametrize("raw", [False, True])
@pytest.mark.parametrize("method", ["compose", "front", "tensor"])
def test_homogeneous_clifford_algebra_preserves_its_actual_coordinate_origin(raw, method):
    first, second = Clifford(source()), Clifford(qb.Circuit(2).s(0).h(1).cx(1, 0))
    if raw:first, second = Clifford(first.tableau.copy()), Clifford(second.tableau.copy())
    a, b = first.to_matrix(), second.to_matrix()
    result = first.compose(second, front=True) if method == "front" else getattr(first, method)(second)
    expected = a @ b if method == "front" else b @ a if method == "compose" else np.kron(a, b)
    np.testing.assert_allclose(projective(result.to_matrix()), projective(expected), atol=4e-13, rtol=0)
    actual = result.to_operator()
    assert actual.__dict__.get("_public_matrix_basis") == (None if raw else "native")
    # Tableau products may choose a different synthesis phase. Once an Operator
    # is created, its entire matrix phase must survive every coordinate export.
    np.testing.assert_array_equal(actual.data, result.to_matrix())
    np.testing.assert_array_equal(actual.as_qiskit_operator().data, actual.data if raw else reverse(actual.data))


@pytest.mark.parametrize("method", ["compose", "tensor"])
def test_mixed_native_literal_clifford_products_cannot_launder_origin(method):
    native = Clifford(source())
    literal = Clifford(native.tableau.copy())
    product = getattr(native, method)(literal)
    assert product.__dict__["_public_matrix_basis"] == "unresolved"
    with pytest.raises(UnsupportedFeature):product.to_operator().as_qiskit_operator()


@pytest.mark.parametrize("factory", [Clifford, Clifford.from_operator])
@pytest.mark.parametrize("mode", ["native", "public", "literal"])
def test_operator_source_clifford_factory_retains_proven_numeric_frame(factory, mode):
    original = Operator(source(3))
    owner = original if mode == "native" else original.as_qiskit_operator() if mode == "public" else Operator(original.data.copy())
    result = factory(owner)
    matrix = result.to_matrix()
    np.testing.assert_allclose(projective(matrix), projective(owner.data), atol=4e-13, rtol=0)
    operator = result.to_operator()
    assert operator.__dict__.get("_public_matrix_basis") == ("native" if mode == "native" else None)
    np.testing.assert_array_equal(operator.as_qiskit_operator().data, reverse(matrix) if mode == "native" else matrix)


def test_public_operator_to_instruction_roundtrip_preserves_full_phase_and_basis():
    owner = Operator(source(3)).as_qiskit_operator()
    expected = owner.data.copy()
    instruction = owner.to_instruction(label="public-operator")
    result = Operator(instruction).as_qiskit_operator()
    np.testing.assert_array_equal(result.data, expected)
    np.testing.assert_array_equal(owner.data, expected)


def test_proved_hybrid_operator_instruction_reuses_single_native_normalization():
    from quantumbridge.core.standard_gates import UnitaryGate
    matrix = np.kron(np.array([[0, 1], [1, 0]], complex), np.eye(2))
    owner = Operator(qb.AnnotatedOperation(UnitaryGate(matrix), qb.ControlModifier(2, 1)))
    expected = owner.as_qiskit_operator().data
    np.testing.assert_array_equal(Operator(owner.to_instruction()).as_qiskit_operator().data, expected)


def test_clifford_tableau_cannot_recover_discarded_circuit_global_phase():
    circuit = source(3)
    phase_shifted = circuit.copy()
    phase_shifted.global_phase = .431
    first, second = Clifford(circuit), Clifford(phase_shifted)
    np.testing.assert_array_equal(first.tableau, second.tableau)
    np.testing.assert_array_equal(first.to_matrix(), second.to_matrix())
    assert not np.allclose(Operator(circuit).data, Operator(phase_shifted).data)


@pytest.mark.parametrize("native", [False, True])
def test_zero_width_clifford_operator_preserves_its_factory_origin(native):
    owner = Clifford(qb.Circuit(0)) if native else Clifford.identity(0)
    for result in (owner.to_operator(), Operator(owner)):
        np.testing.assert_array_equal(result.data, [[1]])
        assert result.__dict__.get("_public_matrix_basis") == ("native" if native else None)
        np.testing.assert_array_equal(result.as_qiskit_operator().data, [[1]])


@pytest.mark.parametrize("dims", [(4,), (2, 4), (4, 2)])
@pytest.mark.parametrize("factory", [Clifford, Clifford.from_operator])
def test_native_mixed_radix_operator_enters_clifford_in_its_declared_public_matrix_frame(dims, factory):
    from math import prod
    width = prod(dims).bit_length() - 1
    owner = Operator(source(width)).reshape(dims, dims)
    before = owner.data.copy()
    declared = owner.as_qiskit_operator().data
    np.testing.assert_array_equal(declared, public_radix_matrix(before, dims))
    result = factory(owner)
    actual = result.to_operator().as_qiskit_operator()
    np.testing.assert_allclose(projective(actual.data), projective(declared), atol=4e-13, rtol=0)
    assert result.__dict__.get("_public_matrix_basis") is None
    np.testing.assert_array_equal(actual.data, result.to_matrix())
    np.testing.assert_array_equal(owner.data, before)
    assert owner.input_dims() == dims and owner.output_dims() == dims


@pytest.mark.parametrize("entry", [lambda value: Operator.from_circuit(value), Clifford.from_circuit])
def test_foreign_gate_definition_property_refused_before_access(entry):
    from quantumbridge.core.gates import Gate
    class Foreign(Gate):
        @property
        def definition(self):pytest.fail("Foreign gate definition was read")
    with pytest.raises((ValueError, TypeError)):entry(object.__new__(Foreign))
