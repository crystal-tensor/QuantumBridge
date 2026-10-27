# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Explicit public arithmetic must not replace legacy default-parity reds."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator


def matrix(size, seed):
    rng = np.random.default_rng(seed)
    value, _ = np.linalg.qr(rng.normal(size=(size, size)) + 1j * rng.normal(size=(size, size)))
    return value * np.exp(.17j)


def embed(data, qargs, dims, local_dims):
    """Independent little-radix digits, including unequal subsystem sizes."""
    size = int(np.prod(dims))
    def digits(index, radices):
        result = []
        for radix in radices:
            index, digit = divmod(index, radix)
            result.append(digit)
        return result
    def index(values, radices):
        value, stride = 0, 1
        for digit, radix in zip(values, radices):
            value += digit * stride
            stride *= radix
        return value
    result = np.zeros((size, size), complex)
    for column in range(size):
        incoming = digits(column, dims)
        local_column = index([incoming[pos] for pos in qargs], local_dims)
        for local_row in range(len(data)):
            outgoing = incoming.copy()
            for pos, digit in zip(qargs, digits(local_row, local_dims)):
                outgoing[pos] = digit
            result[index(outgoing, dims), column] = data[local_row, local_column]
    return result


@pytest.mark.parametrize("method", ["compose", "front", "dot", "matmul", "tensor", "expand"])
def test_explicit_public_full_width_arithmetic_and_unchanged_native_default(method):
    a, b = matrix(4, 11101), matrix(4, 11102)
    first, second = Operator(a), Operator(b)
    np.testing.assert_allclose(first.compose(second).data, a @ b, atol=3e-12, rtol=0)
    public, other = first.as_qiskit_operator(), second.as_qiskit_operator()
    assert type(public) is Operator and public.arithmetic_convention == "qiskit"
    expected = b @ a if method == "compose" else np.kron(a, b) if method == "tensor" \
        else np.kron(b, a) if method == "expand" else a @ b
    result = public.compose(other, front=True) if method == "front" else public @ other \
        if method == "matmul" else getattr(public, method)(other)
    assert result.arithmetic_convention == "qiskit"
    np.testing.assert_allclose(result.data, expected, atol=3e-12, rtol=0)
    np.testing.assert_array_equal(first.data, a)
    np.testing.assert_array_equal(second.data, b)


@pytest.mark.parametrize("dims,qargs", [((2, 2, 2), (2, 0)), ((2, 2, 2), (0, 2)),
    ((2, 3, 2), (2, 1)), ((2, 3, 2), (1, 0))])
@pytest.mark.parametrize("front", [False, True])
def test_explicit_public_mapped_mixed_radix_matches_independent_digit_embedding(dims, qargs, front):
    local_dims = tuple(dims[pos] for pos in qargs)
    a, b = matrix(int(np.prod(dims)), 11103), matrix(int(np.prod(local_dims)), 11104)
    first = Operator(a, dims[::-1], dims[::-1]).as_qiskit_operator()
    other = Operator(b, local_dims[::-1], local_dims[::-1]).as_qiskit_operator()
    embedded = embed(b, qargs, dims, local_dims)
    expected = a @ embedded if front else embedded @ a
    result = first.compose(other, qargs=qargs, front=front)
    assert result.input_dims() == dims and result.output_dims() == dims
    np.testing.assert_allclose(result.data, expected, atol=4e-12, rtol=0)


@pytest.mark.parametrize("method", ["tensor", "expand"])
def test_public_tensor_factor_order_and_dimension_order_are_independent(method):
    first = Operator(matrix(6, 11105), (3, 2), (3, 2)).as_qiskit_operator()
    second = Operator(matrix(4, 11106), (2, 2), (2, 2)).as_qiskit_operator()
    result = getattr(first, method)(second)
    left, right = (first, second) if method == "tensor" else (second, first)
    np.testing.assert_allclose(result.data, np.kron(left.data, right.data), atol=3e-12, rtol=0)
    assert result.input_dims() == right.input_dims() + left.input_dims()
    assert result.output_dims() == right.output_dims() + left.output_dims()


def test_public_conversion_is_owned_idempotent_and_convention_is_immutable():
    source = Operator(matrix(4, 11107))
    before = source.data.copy()
    view = source.as_qiskit_operator()
    assert not np.shares_memory(view.data, source.data)
    second = view.as_qiskit_operator()
    np.testing.assert_array_equal(second.data, before)
    assert second.arithmetic_convention == "qiskit"
    with pytest.raises(AttributeError):
        view._arithmetic_convention = "native"
    with pytest.raises(AttributeError):
        view.arithmetic_convention = "native"
    for derived in (view.copy(), view.transpose(), view.conjugate(), view.adjoint(), view.power(.37)):
        assert derived.arithmetic_convention == "qiskit"
    view.data[0, 0] = .9
    np.testing.assert_array_equal(source.data, before)
    np.testing.assert_array_equal(second.data, before)


@pytest.mark.parametrize("origins", [("raw", "raw"), ("circuit", "circuit"),
    ("raw", "circuit"), ("circuit", "raw"), ("from_circuit", "raw")])
@pytest.mark.parametrize("method", ["compose", "tensor", "expand"])
def test_public_mode_mixed_source_matrix_provenance_is_not_call_convention(origins, method):
    def source(origin, seed):
        raw = matrix(4, seed)
        if origin == "raw":
            return Operator(raw), raw
        body = qb.QuantumCircuit(2, global_phase=.13)
        body.unitary(raw, [0, 1])
        native = Operator.from_circuit(body) if origin == "from_circuit" else Operator(body)
        return native, raw * np.exp(.13j)
    first, a = source(origins[0], 11108)
    second, b = source(origins[1], 11109)
    public, other = first.as_qiskit_operator(), second.as_qiskit_operator()
    np.testing.assert_allclose(public.data, a, atol=3e-12, rtol=0)
    np.testing.assert_allclose(other.data, b, atol=3e-12, rtol=0)
    result = getattr(public, method)(other)
    expected = b @ a if method == "compose" else np.kron(a, b) if method == "tensor" else np.kron(b, a)
    np.testing.assert_allclose(result.data, expected, atol=3e-12, rtol=0)


@pytest.mark.parametrize("method", ["compose", "tensor", "expand"])
def test_mixed_arithmetic_conventions_require_explicit_selection(method):
    from quantumbridge.core.classical import UnsupportedFeature
    first, second = Operator(matrix(4, 11110)), Operator(matrix(4, 11111)).as_qiskit_operator()
    for a, b in ((first, second), (second, first)):
        with pytest.raises(UnsupportedFeature) as error:
            getattr(a, method)(b)
        assert error.value.feature == "operator_arithmetic_convention"
