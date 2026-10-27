# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Explicit native migration preserves legacy math, not default SDK parity."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator


def matrix(rows, columns=None, seed=12001):
    columns = rows if columns is None else columns
    rng = np.random.default_rng(seed)
    value = rng.normal(size=(rows, columns)) + 1j * rng.normal(size=(rows, columns))
    if rows == columns:
        value, _ = np.linalg.qr(value)
    return value * np.exp(.17j)


def reverse_matrix_axes(data, incoming, outgoing):
    """Independent mixed-radix basis permutation, row and column separately."""
    result = np.empty_like(data)
    for row in range(data.shape[0]):
        row_digits = np.unravel_index(row, outgoing)
        target_row = np.ravel_multi_index(row_digits[::-1], outgoing[::-1])
        for column in range(data.shape[1]):
            col_digits = np.unravel_index(column, incoming)
            target_column = np.ravel_multi_index(col_digits[::-1], incoming[::-1])
            result[target_row, target_column] = data[row, column]
    return result


@pytest.mark.parametrize("incoming,outgoing", [((2, 2), (2, 2)), ((2, 3), (2, 3)),
    ((3, 2), (2, 3)), ((2, 2), (3, 2)), ((), ())])
def test_native_entry_owns_identical_legacy_numeric_data_and_is_idempotent(incoming, outgoing):
    data = matrix(int(np.prod(outgoing)), int(np.prod(incoming)))
    source = Operator(data, incoming, outgoing)
    native = source.as_native_operator()
    assert type(native) is Operator and native.arithmetic_convention == "native"
    assert native.input_dims() == incoming and native.output_dims() == outgoing
    assert not np.shares_memory(native.data, source.data)
    np.testing.assert_array_equal(native.data, data)
    again = native.as_native_operator()
    assert not np.shares_memory(again.data, native.data)
    np.testing.assert_array_equal(again.data, data)
    assert again.input_dims() == incoming and again.output_dims() == outgoing
    with pytest.raises(AttributeError):
        native._arithmetic_convention = "qiskit"


@pytest.mark.parametrize("incoming,outgoing", [((2, 2), (2, 2)), ((2, 3), (2, 3)),
    ((3, 2), (2, 3)), ((2, 2), (3, 2)), ((), ())])
def test_native_public_native_conversion_has_proved_general_subsystem_coordinates(incoming, outgoing):
    data = matrix(int(np.prod(outgoing)), int(np.prod(incoming)))
    native = Operator(data, incoming, outgoing).as_native_operator()
    public = native.as_qiskit_operator()
    expected = reverse_matrix_axes(data, incoming, outgoing)
    assert public.input_dims() == incoming and public.output_dims() == outgoing
    np.testing.assert_array_equal(public.data, expected)
    restored = public.as_native_operator()
    np.testing.assert_array_equal(restored.data, data)
    assert restored.input_dims() == incoming and restored.output_dims() == outgoing
    assert restored.arithmetic_convention == "native"


@pytest.mark.parametrize("method", ["compose", "front", "dot", "matmul", "tensor", "expand"])
@pytest.mark.parametrize("mixed_radix", [False, True])
def test_explicit_native_arithmetic_is_same_legacy_matrix_math_and_provenance(method, mixed_radix):
    dims = (2, 3) if mixed_radix else (2, 2)
    size = int(np.prod(dims))
    a, b = matrix(size, seed=12002), matrix(size, seed=12003)
    first, second = Operator(a, dims, dims), Operator(b, dims, dims)
    def calculate(x, y):
        if method == "front": return x.compose(y, front=True)
        if method == "matmul": return x @ y
        return getattr(x, method)(y)
    legacy = calculate(first, second)
    native = calculate(first.as_native_operator(), second.as_native_operator())
    expected = b @ a if method == "front" else np.kron(a, b) if method == "tensor" \
        else np.kron(b, a) if method == "expand" else a @ b
    np.testing.assert_allclose(legacy.data, expected, atol=3e-12, rtol=0)
    np.testing.assert_allclose(native.data, expected, atol=3e-12, rtol=0)
    assert native.input_dims() == legacy.input_dims()
    assert native.output_dims() == legacy.output_dims()
    assert native.arithmetic_convention == "native"
    public = native.as_qiskit_operator()
    np.testing.assert_allclose(public.data, reverse_matrix_axes(expected, native.input_dims(), native.output_dims()), atol=3e-12, rtol=0)


@pytest.mark.parametrize("derived", ["copy", "transpose", "conjugate", "adjoint", "power"])
def test_native_derivations_keep_explicit_contract_and_public_conversion(derived):
    native = Operator(matrix(4)).as_native_operator()
    value = native.power(.37, branch_cut_rotation=0) if derived == "power" else getattr(native, derived)()
    assert value.arithmetic_convention == "native"
    assert value.__dict__["_arithmetic_convention"] == "native"
    public = value.as_qiskit_operator()
    np.testing.assert_allclose(public.data, reverse_matrix_axes(value.data, (2, 2), (2, 2)), atol=3e-12, rtol=0)


def test_native_circuit_operator_and_physical_gate_agree_across_explicit_views():
    body = qb.Circuit(2).ry(.41, 0).cx(0, 1).unitary(matrix(4), [1, 0])
    original = Operator.from_circuit(body)
    native = original.as_native_operator()
    np.testing.assert_array_equal(native.data, original.data)
    public = native.as_qiskit_operator()
    receiver = qb.QuantumCircuit(2)
    receiver.unitary(public, [0, 1])
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(receiver), native.data[:, 0], atol=3e-12, rtol=0)


def test_legacy_raw_public_selection_is_not_reinterpreted_as_explicit_native_origin():
    data = matrix(4)
    raw = Operator(data)
    np.testing.assert_array_equal(raw.as_qiskit_operator().data, data)
    explicit = raw.as_native_operator()
    np.testing.assert_array_equal(explicit.as_qiskit_operator().data, reverse_matrix_axes(data, (2, 2), (2, 2)))
    np.testing.assert_array_equal(raw.data, data)


@pytest.mark.parametrize("count", [0, 1, 2])
def test_native_tensorpower_internal_seed_does_not_depend_on_implicit_convention(count):
    data = matrix(4)
    native = Operator(data).as_native_operator()
    result = native.tensorpower(count)
    expected = np.ones((1, 1), complex)
    for _ in range(count):expected = np.kron(expected, data)
    np.testing.assert_allclose(result.data, expected, atol=3e-12, rtol=0)
    assert result.__dict__["_arithmetic_convention"] == "native"
    assert result.input_dims() == (2,) * (count * 2)
