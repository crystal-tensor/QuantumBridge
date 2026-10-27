# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Gate matrices keep phase; Clifford tableaux represent projective unitaries."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.standard_gates import UnitaryGate
from quantumbridge.information import Operator, Clifford


def reverse(width):
    return [int(format(index, f"0{width}b")[::-1], 2) for index in range(1 << width)]


def embed(matrix, wires, width):
    size = 1 << width
    output = np.zeros((size, size), complex)
    for column in range(size):
        local = sum(((column >> (width - 1 - wire)) & 1) << (len(wires) - 1 - offset)
            for offset, wire in enumerate(wires))
        for target in range(len(matrix)):
            row = column
            for offset, wire in enumerate(wires):
                mask = 1 << (width - 1 - wire)
                row = (row & ~mask) | (((target >> (len(wires) - 1 - offset)) & 1) * mask)
            output[row, column] = matrix[target, local]
    return output


def circuit_matrix(circuit):
    single = {"h": np.array([[1, 1], [1, -1]]) / np.sqrt(2),
        "s": np.diag([1, 1j]), "sdg": np.diag([1, -1j]),
        "x": np.array([[0, 1], [1, 0]]), "z": np.diag([1, -1])}
    multiple = {"cx": np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]),
        "cz": np.diag([1, 1, 1, -1]), "swap": np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])}
    result = np.eye(1 << circuit.num_qubits, dtype=complex)
    for operation in circuit.operations:
        matrix = single[operation.name] if operation.name in single else multiple[operation.name]
        result = embed(matrix, operation.wires, circuit.num_qubits) @ result
    return np.exp(1j * float(circuit.global_phase)) * result


def circuits(width):
    from qiskit import QuantumCircuit
    native, public = qb.QuantumCircuit(width, global_phase=.17), QuantumCircuit(width, global_phase=.17)
    for circuit in (native, public):
        circuit.h(0)
        circuit.s(width - 1)
        circuit.cx(0, width - 1)
        circuit.cz(width - 1, 0)
        circuit.swap(0, 1)
        circuit.sdg(1)
    return native, public


@pytest.mark.parametrize("width", [2, 3])
@pytest.mark.parametrize("raw", [False, True])
@pytest.mark.parametrize("derivation", ["base", "inverse", "power", "fractional", "repeat"])
def test_actual_gate_constructor_preserves_existing_complex_matrix_source(width, raw, derivation):
    from qiskit.quantum_info import Operator as QO
    from qiskit.circuit.library import UnitaryGate as QU
    native, public = circuits(width)
    matrix = circuit_matrix(native)
    a, b = (UnitaryGate(matrix), QU(matrix)) if raw else (native.to_gate(), public.to_gate())
    if derivation != "base":
        method, argument = ("power", .37) if derivation == "fractional" else ("power", 2) if derivation == "power" \
            else ("repeat", 2) if derivation == "repeat" else ("inverse", None)
        a, b = (getattr(value, method)() if argument is None else getattr(value, method)(argument) for value in (a, b))
    actual, reference = Operator(a), QO(b)
    np.testing.assert_allclose(actual.as_qiskit_operator().data, reference.data, atol=4e-12, rtol=0)
    assert actual.__dict__.get("_public_matrix_basis") == (None if raw else "native")


def projective_representative(matrix):
    """Fix each Clifford's own phase, not a fitted phase between two answers."""
    pivot = next(value for value in matrix[:, 0] if abs(value) > 1e-10)
    return matrix * (pivot.conjugate() / abs(pivot))


@pytest.mark.parametrize("width", [2, 3, 4])
@pytest.mark.parametrize("raw", [False, True])
@pytest.mark.parametrize("factory", ["constructor", "to_operator"])
@pytest.mark.parametrize("derivation", ["base", "copy", "adjoint", "conjugate", "power"])
def test_clifford_operator_construction_keeps_proven_source_and_exact_synthesis_phase(width, raw, factory, derivation):
    from qiskit.quantum_info import Clifford as QC, Operator as QO
    native, public = circuits(width)
    owner = Clifford(native)
    actual_public = QC(public)
    if raw:
        owner = Clifford(owner.tableau.copy())
        actual_public = QC(owner.tableau.copy())
    if derivation != "base":
        owner = owner.power(2) if derivation == "power" else getattr(owner, derivation)()
        actual_public = actual_public.power(2) if derivation == "power" else getattr(actual_public, derivation)()
    # Native synthesis fixes an exact phase independently of Qiskit's synthesis.
    high = circuit_matrix(owner.to_circuit())
    np.testing.assert_allclose(owner.to_matrix(), high, atol=3e-13, rtol=0)
    expected = high if raw else high[np.ix_(reverse(width), reverse(width))]
    # Projective Clifford equality is explicit. Operator matrices below retain
    # the full phase of the actual native synthesis, including after copies.
    reference = QO(actual_public).data
    np.testing.assert_allclose(projective_representative(expected), projective_representative(reference), atol=4e-12, rtol=0)
    before = owner.tableau.copy()
    result = Operator(owner) if factory == "constructor" else owner.to_operator()
    assert result.data.shape == high.shape
    np.testing.assert_allclose(result.data, high, atol=3e-13, rtol=0)
    assert result.__dict__.get("_public_matrix_basis") == (None if raw else "native")
    converted = result.as_qiskit_operator()
    np.testing.assert_allclose(converted.data, expected, atol=3e-13, rtol=0)
    for method in ("copy", "adjoint", "conjugate", "transpose", "power"):
        derived = result.power(2) if method == "power" else getattr(result, method)()
        target = expected @ expected if method == "power" else expected.conj().T if method == "adjoint" \
            else expected.conj() if method == "conjugate" else expected.T if method == "transpose" else expected
        np.testing.assert_allclose(derived.as_qiskit_operator().data, target, atol=4e-12, rtol=0)
    np.testing.assert_array_equal(owner.tableau, before)


@pytest.mark.parametrize("factory", ["constructor", "from_operator"])
@pytest.mark.parametrize("mode", ["native", "public", "literal"])
def test_actual_operator_source_clifford_conversion_keeps_its_frame(factory, mode):
    from qiskit.quantum_info import Clifford as QC
    native, _ = circuits(3)
    original = Operator(native)
    owner = original if mode == "native" else original.as_qiskit_operator() if mode == "public" else Operator(original.data.copy())
    actual = Clifford(owner) if factory == "constructor" else Clifford.from_operator(owner)
    reference = QC.from_matrix(owner.data)
    np.testing.assert_allclose(projective_representative(actual.to_matrix()),
        projective_representative(reference.to_matrix()), atol=4e-12, rtol=0)
    result = actual.to_operator()
    expected = actual.to_matrix()
    if mode == "native":expected = expected[np.ix_(reverse(3), reverse(3))]
    np.testing.assert_allclose(result.as_qiskit_operator().data, expected, atol=4e-12, rtol=0)


def test_actual_explicit_public_operator_instruction_roundtrip_has_unchanged_input_and_phase():
    from qiskit.quantum_info import Operator as QO
    native, public = circuits(3)
    actual, reference = Operator(native).as_qiskit_operator(), QO(public)
    np.testing.assert_allclose(actual.data, reference.data, atol=4e-12, rtol=0)
    native_instruction, public_instruction = actual.to_instruction(), reference.to_instruction()
    np.testing.assert_allclose(Operator(native_instruction).as_qiskit_operator().data,
        QO(public_instruction).data, atol=4e-12, rtol=0)


@pytest.mark.parametrize("dims", [(4,), (2, 4), (4, 2)])
def test_actual_from_operator_mixed_radix_source_keeps_declared_public_matrix(dims):
    from math import prod
    from qiskit.quantum_info import Clifford as QC, Operator as QO
    width = prod(dims).bit_length() - 1
    body, _ = circuits(width)
    source = Operator(body).reshape(dims, dims)
    declared = source.as_qiskit_operator()
    reference = QC.from_operator(QO(declared.data, input_dims=declared.input_dims(), output_dims=declared.output_dims()))
    result = Clifford.from_operator(source).to_operator().as_qiskit_operator()
    np.testing.assert_allclose(projective_representative(result.data),
        projective_representative(reference.to_operator().data), atol=4e-12, rtol=0)


@pytest.mark.parametrize("kind", ["gate", "native_clifford", "literal_clifford"])
@pytest.mark.parametrize("entry", ["unitary", "append", "instruction"])
@pytest.mark.parametrize("path", ["source", "compiler", "json_ir", "qpy13", "detached_json_ir", "detached_qpy13"])
def test_gate_clifford_public_transport_keeps_native_synthesis_phase(kind, entry, path):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator as QO, Statevector as QS
    from qiskit.circuit.library import UnitaryGate as QU
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.ir.qb_ir import IRProgram
    from quantumbridge.serialization import qpy_dumps, qpy_loads
    body, public_body = circuits(2)
    if kind == "gate":
        owner = Operator(body.to_gate())
        expected = QO(public_body.to_gate()).data
    else:
        clifford = Clifford(body)
        if kind == "literal_clifford":clifford = Clifford(clifford.tableau.copy())
        exact = circuit_matrix(clifford.to_circuit())
        expected = exact if kind == "literal_clifford" else exact[np.ix_(reverse(2), reverse(2))]
        owner = Operator(clifford)
    selected = owner.as_qiskit_operator()
    np.testing.assert_allclose(selected.data, expected, atol=4e-12, rtol=0)
    actual, reference = qb.QuantumCircuit(5, global_phase=.23), QuantumCircuit(5, global_phase=.23)
    for circuit in (actual, reference):
        circuit.h(0)
        circuit.ry(.31, 1)
        circuit.rx(-.43, 3)
        circuit.h(4)
    wires = [4, 1]
    if entry == "unitary":actual.unitary(selected, wires)
    elif entry == "append":actual.append(UnitaryGate(selected.data), wires)
    else:actual.append(selected.to_instruction(), wires)
    reference.append(QU(expected), wires)
    if path == "compiler":actual = qb.transpile(actual, basis_gates=["h", "rx", "ry", "rz", "sx", "cx", "unitary"], optimization_level=1)
    elif "json_ir" in path:
        payload = actual.to_ir().to_json()
        assert "_public_matrix_basis" not in payload
        actual = circuit_from_ir(IRProgram.from_json(payload))
    elif "qpy13" in path:
        payload = qpy_dumps(actual, version=13)
        assert b"_public_matrix_basis" not in payload
        actual = qpy_loads(payload)[0]
    if path.startswith("detached"):
        operation = actual.operations[-1]
        gate = operation.metadata.get("gate", operation.metadata.get("instruction_object"))
        assert gate is not None
        actual = qb.QuantumCircuit(5, global_phase=.23)
        actual.h(0)
        actual.ry(.31, 1)
        actual.rx(-.43, 3)
        actual.h(4)
        actual.append(gate, wires)
    expected_state = QS.from_instruction(reference).data[reverse(5)]
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(actual), expected_state, atol=4e-12, rtol=0)
    np.testing.assert_allclose(qb.MatrixProductStateDevice(cutoff=0, max_bond_dim=32)
        .matrix_product_state(actual).statevector(), expected_state, atol=4e-12, rtol=0)
