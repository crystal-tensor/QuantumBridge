# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""QC2 public-call math reds, independent of native Operator multiplication."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator as NativeOperator


def unitary(width, seed):
    rng = np.random.default_rng(seed)
    size = 1 << width
    value, _ = np.linalg.qr(rng.normal(size=(size, size))
        + 1j * rng.normal(size=(size, size)))
    return value * np.exp(.17j)


def bit_reversal(width):
    return [sum(((i >> k) & 1) << (width - 1 - k) for k in range(width))
        for i in range(1 << width)]


def public_data(value):
    data = value.data
    if getattr(value, "_public_matrix_basis", None) == "native":
        order = bit_reversal(value.num_qubits)
        return data[np.ix_(order, order)]
    return data


def local_embedding(matrix, wires, width):
    """Local bit k maps to global wires[k], by explicit basis indices."""
    result = np.zeros((1 << width, 1 << width), dtype=np.complex128)
    for column in range(1 << width):
        local_column = sum(((column >> wire) & 1) << k for k, wire in enumerate(wires))
        for local_row in range(len(matrix)):
            row = column
            for k, wire in enumerate(wires):
                row = (row & ~(1 << wire)) | (((local_row >> k) & 1) << wire)
            result[row, column] = matrix[local_row, local_column]
    return result


def source(kind, width, seed, circuit_type, operator_type):
    matrix = unitary(width, seed)
    if kind == "raw":
        return operator_type(matrix)
    body = circuit_type(width, global_phase=.13)
    body.ry(.41, 0)
    if width > 1:
        body.cx(0, width - 1)
    body.unitary(matrix, list(range(width)))
    return operator_type.from_circuit(body) if kind == "from_circuit" else operator_type(body)


ORIGINS = [("raw", "raw"), ("circuit", "circuit"), ("raw", "circuit"),
    ("circuit", "raw"), ("from_circuit", "raw")]


@pytest.mark.parametrize("origins", ORIGINS)
@pytest.mark.parametrize("method", ["compose", "front", "dot", "tensor", "expand"])
def test_actual_public_operator_arithmetic_same_call_has_independent_math(origins, method):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator

    native = [source(kind, 2, seed, qb.QuantumCircuit, NativeOperator)
        for kind, seed in zip(origins, (10401, 10402))]
    public = [source(kind, 2, seed, QuantumCircuit, Operator)
        for kind, seed in zip(origins, (10401, 10402))]
    a, b = (item.data for item in public)
    for actual, reference in zip(native, public):
        np.testing.assert_allclose(public_data(actual), reference.data, atol=3e-12, rtol=0)
    expected = b @ a if method == "compose" else a @ b if method in ("front", "dot") \
        else np.kron(a, b) if method == "tensor" else np.kron(b, a)
    def calculate(first, second):
        return first.compose(second, front=True) if method == "front" else getattr(first, method)(second)
    np.testing.assert_allclose(calculate(*public).data, expected, atol=3e-12, rtol=0)
    np.testing.assert_allclose(public_data(calculate(*native)), expected, atol=3e-12, rtol=0)


@pytest.mark.parametrize("origins", ORIGINS)
@pytest.mark.parametrize("method", ["compose", "front", "dot"])
@pytest.mark.parametrize("wires", [(2, 0), (0, 2)])
def test_actual_noncontiguous_operator_composition_uses_public_subsystem_indices(origins, method, wires):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator

    native = [source(kind, width, seed, qb.QuantumCircuit, NativeOperator)
        for kind, width, seed in zip(origins, (3, 2), (10403, 10404))]
    public = [source(kind, width, seed, QuantumCircuit, Operator)
        for kind, width, seed in zip(origins, (3, 2), (10403, 10404))]
    a, b = (item.data for item in public)
    embedded = local_embedding(b, wires, 3)
    expected = embedded @ a if method == "compose" else a @ embedded
    def calculate(first, second):
        return first.compose(second, qargs=wires, front=True) if method == "front" \
            else getattr(first, method)(second, qargs=wires)
    np.testing.assert_allclose(calculate(*public).data, expected, atol=3e-12, rtol=0)
    np.testing.assert_allclose(public_data(calculate(*native)), expected, atol=3e-12, rtol=0)


@pytest.mark.parametrize("method", ["compose", "tensor", "expand"])
@pytest.mark.parametrize("entry", ["unitary", "append"])
def test_derived_circuit_operator_executes_on_public_circuit(method, entry):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator, Statevector

    states = []
    for kind, operator, upstream in ((qb.QuantumCircuit, NativeOperator, False),
            (QuantumCircuit, Operator, True)):
        a = source("circuit", 2, 10405, kind, operator)
        b = source("circuit", 2, 10406, kind, operator)
        value = getattr(a, method)(b)
        receiver = kind(6, global_phase=.23)
        receiver.h(0)
        receiver.ry(.31, 1)
        receiver.rx(-.43, 5)
        wires = [5, 1] if method == "compose" else [5, 1, 4, 2]
        getattr(receiver, entry)(value, wires)
        states.append(np.asarray(Statevector.from_instruction(receiver).data) if upstream
            else qb.StatevectorDevice().statevector(receiver))
    np.testing.assert_allclose(states[0], states[1][bit_reversal(6)], atol=3e-12, rtol=0)
