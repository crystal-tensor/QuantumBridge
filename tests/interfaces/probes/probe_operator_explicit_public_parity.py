# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Opt-in public results are separate from the original default-call reds."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator as NativeOperator
from quantumbridge.core.standard_gates import UnitaryGate as NativeUnitaryGate
from quantumbridge.serialization import qpy_dumps, qpy_loads
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.ir.qb_ir import IRProgram
from probe_operator_composition_public_parity import source, bit_reversal, local_embedding, ORIGINS


def calculate(first, second, method, qargs=None):
    if method == "front":
        return first.compose(second, qargs=qargs, front=True)
    if method == "matmul":
        return first @ second
    return getattr(first, method)(second) if qargs is None else getattr(first, method)(second, qargs=qargs)


@pytest.mark.parametrize("origins", ORIGINS)
@pytest.mark.parametrize("method", ["compose", "front", "dot", "matmul", "tensor", "expand"])
def test_explicit_public_mode_matches_same_original_matrix_inputs_and_sdk(origins, method):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator

    native = [source(kind, 2, seed, qb.QuantumCircuit, NativeOperator).as_qiskit_operator()
        for kind, seed in zip(origins, (10401, 10402))]
    public = [source(kind, 2, seed, QuantumCircuit, Operator)
        for kind, seed in zip(origins, (10401, 10402))]
    for actual, expected in zip(native, public):
        np.testing.assert_allclose(actual.data, expected.data, atol=3e-12, rtol=0)
    actual, expected = calculate(*native, method), calculate(*public, method)
    np.testing.assert_allclose(actual.data, expected.data, atol=3e-12, rtol=0)
    assert actual.input_dims() == expected.input_dims()
    assert actual.output_dims() == expected.output_dims()


@pytest.mark.parametrize("origins", ORIGINS)
@pytest.mark.parametrize("method", ["compose", "front", "dot"])
@pytest.mark.parametrize("wires", [(2, 0), (0, 2)])
def test_explicit_public_noncontiguous_arithmetic_matches_actual_sdk_and_embedding(origins, method, wires):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator

    native = [source(kind, width, seed, qb.QuantumCircuit, NativeOperator).as_qiskit_operator()
        for kind, width, seed in zip(origins, (3, 2), (10403, 10404))]
    public = [source(kind, width, seed, QuantumCircuit, Operator)
        for kind, width, seed in zip(origins, (3, 2), (10403, 10404))]
    a, b = (item.data for item in public)
    embedded = local_embedding(b, wires, 3)
    expected = embedded @ a if method == "compose" else a @ embedded
    np.testing.assert_allclose(calculate(*public, method, wires).data, expected, atol=3e-12, rtol=0)
    np.testing.assert_allclose(calculate(*native, method, wires).data, expected, atol=3e-12, rtol=0)


@pytest.mark.parametrize("dims,wires", [((2, 3, 2), (2, 1)), ((2, 3, 2), (1, 0))])
@pytest.mark.parametrize("front", [False, True])
def test_explicit_public_mixed_radix_matches_sdk_dimensions_and_data(dims, wires, front):
    from qiskit.quantum_info import Operator

    local_dims = tuple(dims[pos] for pos in wires)
    matrices = []
    for radices, seed in ((dims, 11103), (local_dims, 11104)):
        rng = np.random.default_rng(seed)
        size = int(np.prod(radices))
        data, _ = np.linalg.qr(rng.normal(size=(size, size)) + 1j * rng.normal(size=(size, size)))
        matrices.append(data * np.exp(.17j))
    a, b = matrices
    native = NativeOperator(a, dims[::-1], dims[::-1]).as_qiskit_operator().compose(
        NativeOperator(b, local_dims[::-1], local_dims[::-1]).as_qiskit_operator(), qargs=wires, front=front)
    public = Operator(a, dims, dims).compose(Operator(b, local_dims, local_dims), qargs=wires, front=front)
    embedded = np.zeros_like(a)
    for column in range(len(a)):
        digits = list(np.unravel_index(column, dims, order="F"))
        local_column = np.ravel_multi_index(tuple(digits[pos] for pos in wires), local_dims, order="F")
        for local_row in range(len(b)):
            outgoing = digits.copy()
            for pos, digit in zip(wires, np.unravel_index(local_row, local_dims, order="F")):
                outgoing[pos] = digit
            row = np.ravel_multi_index(tuple(outgoing), dims, order="F")
            embedded[row, column] = b[local_row, local_column]
    expected = a @ embedded if front else embedded @ a
    np.testing.assert_allclose(public.data, expected, atol=4e-12, rtol=0)
    np.testing.assert_allclose(native.data, expected, atol=4e-12, rtol=0)
    assert native.input_dims() == public.input_dims()
    assert native.output_dims() == public.output_dims()


@pytest.mark.parametrize("origins", ORIGINS)
@pytest.mark.parametrize("method", ["compose", "tensor", "expand"])
@pytest.mark.parametrize("entry", ["unitary", "append_gate"])
@pytest.mark.parametrize("path", ["source", "compiler", "json_ir", "qpy", "detached_qpy", "detached_json_ir"])
def test_public_arithmetic_outputs_survive_real_circuit_execution_and_transports(origins, method, entry, path):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator, Statevector
    from qiskit.circuit.library import UnitaryGate

    def build(kind, operator, gate, native):
        a, b = [source(origin, 2, seed, kind, operator)
            for origin, seed in zip(origins, (10405, 10406))]
        if native:
            a, b = a.as_qiskit_operator(), b.as_qiskit_operator()
        value = getattr(a, method)(b)
        receiver = kind(6, global_phase=.23)
        receiver.h(0)
        receiver.ry(.31, 1)
        receiver.rx(-.43, 5)
        wires = [5, 1] if method == "compose" else [5, 1, 4, 2]
        if entry == "append_gate":
            receiver.append(gate(value.data), wires)
        else:
            receiver.unitary(value, wires)
        return receiver, value

    actual, value = build(qb.QuantumCircuit, NativeOperator, NativeUnitaryGate, True)
    public, expected_value = build(QuantumCircuit, Operator, UnitaryGate, False)
    np.testing.assert_allclose(value.data, expected_value.data, atol=3e-12, rtol=0)
    expected = np.asarray(Statevector.from_instruction(public).data)[bit_reversal(6)]
    if path == "compiler":
        actual = qb.transpile(actual, basis_gates=["h", "rx", "ry", "rz", "sx", "cx", "unitary"], optimization_level=1)
    elif path in ("json_ir", "detached_json_ir"):
        actual = circuit_from_ir(IRProgram.from_json(actual.to_ir().to_json()))
    elif path in ("qpy", "detached_qpy"):
        payload = qpy_dumps(actual, version=13)
        assert b"_arithmetic_convention" not in payload
        actual = qpy_loads(payload)[0]
    if path.startswith("detached"):
        restored_owner = actual.operations[-1].metadata["gate"]
        replacement = qb.QuantumCircuit(6, global_phase=.23)
        replacement.h(0)
        replacement.ry(.31, 1)
        replacement.rx(-.43, 5)
        replacement.append(restored_owner, [5, 1] if method == "compose" else [5, 1, 4, 2])
        actual = replacement
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(actual), expected, atol=4e-12, rtol=0)
    np.testing.assert_allclose(qb.MatrixProductStateDevice(cutoff=0, max_bond_dim=64)
        .matrix_product_state(actual).statevector(), expected, atol=4e-12, rtol=0)
