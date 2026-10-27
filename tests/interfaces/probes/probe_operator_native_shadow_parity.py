# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Native and public branches have separate oracles and pass statistics."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator as NativeOperator
from probe_operator_composition_public_parity import source, ORIGINS, local_embedding


def calculate(a, b, method, qargs=None):
    if method == "front":return a.compose(b, qargs=qargs, front=True)
    if method == "matmul":return a @ b
    return getattr(a, method)(b) if qargs is None else getattr(a, method)(b, qargs=qargs)


def native_embedding(data, wires, width):
    dims = (2,) * width
    result = np.zeros((1 << width, 1 << width), complex)
    for column in range(len(result)):
        digits = list(np.unravel_index(column, dims))
        local_column = np.ravel_multi_index(tuple(digits[pos] for pos in wires), (2,) * len(wires))
        for local_row in range(len(data)):
            row_digits = digits.copy()
            for pos, digit in zip(wires, np.unravel_index(local_row, (2,) * len(wires))):
                row_digits[pos] = digit
            result[np.ravel_multi_index(tuple(row_digits), dims), column] = data[local_row, local_column]
    return result


@pytest.mark.parametrize("origins", ORIGINS)
@pytest.mark.parametrize("method", ["compose", "front", "dot", "matmul", "tensor", "expand"])
def test_default_native_explicit_native_and_public_shadow_have_separate_proved_math(origins, method):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator

    native = [source(kind, 2, seed, qb.QuantumCircuit, NativeOperator)
        for kind, seed in zip(origins, (12201, 12202))]
    public = [source(kind, 2, seed, QuantumCircuit, Operator)
        for kind, seed in zip(origins, (12201, 12202))]
    a, b = (item.data for item in native)
    expected_native = b @ a if method == "front" else np.kron(a, b) if method == "tensor" \
        else np.kron(b, a) if method == "expand" else a @ b
    legacy = calculate(*native, method)
    selected = calculate(*(item.as_native_operator() for item in native), method)
    np.testing.assert_allclose(legacy.data, expected_native, atol=4e-12, rtol=0)
    np.testing.assert_allclose(selected.data, expected_native, atol=4e-12, rtol=0)
    assert selected.input_dims() == legacy.input_dims() and selected.output_dims() == legacy.output_dims()

    a, b = (item.data for item in public)
    expected_public = b @ a if method == "compose" else np.kron(a, b) if method == "tensor" \
        else np.kron(b, a) if method == "expand" else a @ b
    explicit = calculate(*(item.as_qiskit_operator() for item in native), method)
    np.testing.assert_allclose(calculate(*public, method).data, expected_public, atol=4e-12, rtol=0)
    np.testing.assert_allclose(explicit.data, expected_public, atol=4e-12, rtol=0)


@pytest.mark.parametrize("origins", ORIGINS)
@pytest.mark.parametrize("method", ["compose", "front", "dot"])
@pytest.mark.parametrize("wires", [(2, 0), (0, 2)])
def test_subsystem_shadow_does_not_confuse_native_high_and_public_low_qargs(origins, method, wires):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator

    native = [source(kind, width, seed, qb.QuantumCircuit, NativeOperator)
        for kind, width, seed in zip(origins, (3, 2), (12203, 12204))]
    public = [source(kind, width, seed, QuantumCircuit, Operator)
        for kind, width, seed in zip(origins, (3, 2), (12203, 12204))]
    a, b = (item.data for item in native)
    embedded = native_embedding(b, wires, 3)
    native_expected = embedded @ a if method == "front" else a @ embedded
    legacy = calculate(*native, method, wires)
    explicit_native = calculate(*(item.as_native_operator() for item in native), method, wires)
    np.testing.assert_allclose(legacy.data, native_expected, atol=4e-12, rtol=0)
    np.testing.assert_allclose(explicit_native.data, native_expected, atol=4e-12, rtol=0)

    a, b = (item.data for item in public)
    embedded = local_embedding(b, wires, 3)
    public_expected = embedded @ a if method == "compose" else a @ embedded
    explicit_public = calculate(*(item.as_qiskit_operator() for item in native), method, wires)
    np.testing.assert_allclose(calculate(*public, method, wires).data, public_expected, atol=4e-12, rtol=0)
    np.testing.assert_allclose(explicit_public.data, public_expected, atol=4e-12, rtol=0)


@pytest.mark.parametrize("incoming,outgoing", [((2, 3), (2, 3)), ((2, 2), (3, 2)), ((3, 2), (2, 3))])
def test_explicit_native_physical_basis_maps_to_sdk_operator_on_unequal_partitions(incoming, outgoing):
    from qiskit.quantum_info import Operator

    rng = np.random.default_rng(12205)
    data = rng.normal(size=(int(np.prod(outgoing)), int(np.prod(incoming))))
    data = data + 1j * rng.normal(size=data.shape)
    native = NativeOperator(data, incoming, outgoing).as_native_operator()
    public = native.as_qiskit_operator()
    # Public bit positions identify the same physical subsystems; reversed
    # data coordinates are computed independently with C/F radix indexing.
    expected = np.empty_like(data)
    for row in range(len(data)):
        target_row = np.ravel_multi_index(np.unravel_index(row, outgoing), outgoing, order="F")
        for column in range(data.shape[1]):
            target_column = np.ravel_multi_index(np.unravel_index(column, incoming), incoming, order="F")
            expected[target_row, target_column] = data[row, column]
    reference = Operator(expected, input_dims=incoming, output_dims=outgoing)
    np.testing.assert_array_equal(public.data, reference.data)
    assert public.input_dims() == reference.input_dims()
    assert public.output_dims() == reference.output_dims()
    np.testing.assert_array_equal(public.as_native_operator().data, data)
