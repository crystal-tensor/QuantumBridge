# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual installed-SDK construction differentials, including complete phases."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator, Statevector, DensityMatrix
from probe_operator_composition_public_parity import local_embedding, bit_reversal


def circuit_pair(width):
    from qiskit import QuantumCircuit
    native, public = qb.QuantumCircuit(width, global_phase=.13), QuantumCircuit(width, global_phase=.13)
    for circuit in (native, public):
        circuit.h(0)
        circuit.ry(.41, width - 1)
        if width > 1:circuit.cx(0, width - 1)
        circuit.rz(.27, 0)
        circuit.ry(-.3, 0)
        circuit.s(width - 1)
    return native, public


@pytest.mark.parametrize("width", [1, 2, 3, 4])
@pytest.mark.parametrize("factory", ["state", "density"])
def test_actual_sdk_state_derived_operator_conversion(width, factory):
    from qiskit.quantum_info import Statevector as QS, DensityMatrix as QD
    native, public = circuit_pair(width)
    state, reference = Statevector.from_instruction(native), QS.from_instruction(public)
    order = [int(format(i, f"0{width}b")[::-1], 2) for i in range(1 << width)]
    np.testing.assert_allclose(state.data[order], reference.data, atol=2e-14, rtol=0)
    if factory == "density":
        state, reference = DensityMatrix.from_statevector(state), QD(reference)
    operator, expected = state.to_operator(), reference.to_operator()
    np.testing.assert_allclose(operator.as_qiskit_operator().data, expected.data, atol=2e-14, rtol=0)


@pytest.mark.parametrize("width", [1, 2, 3, 4])
@pytest.mark.parametrize("factory", ["constructor", "from_circuit", "gate", "matrix"])
def test_actual_sdk_circuit_gate_and_literal_construction_sources(width, factory):
    from qiskit.quantum_info import Operator as QO
    native, public = circuit_pair(width)
    if factory == "constructor":actual, expected = Operator(native), QO(public)
    elif factory == "from_circuit":actual, expected = Operator.from_circuit(native), QO.from_circuit(public)
    elif factory == "gate":actual, expected = Operator(native.to_gate()), QO(public.to_gate())
    else:
        data = QO(public).data
        actual, expected = Operator(data), QO(data)
    np.testing.assert_allclose(actual.as_qiskit_operator().data, expected.data, atol=2e-14, rtol=0)
    assert actual.input_dims() == expected.input_dims()
    assert actual.output_dims() == expected.output_dims()


@pytest.mark.parametrize("factory", ["state", "density"])
@pytest.mark.parametrize("mode", ["native", "qiskit"])
@pytest.mark.parametrize("path", ["source", "compiler", "json_ir", "qpy13", "detached_json_ir", "detached_qpy13"])
def test_state_derived_reflection_arithmetic_and_actual_public_execution(factory, mode, path):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector as QS
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.ir.qb_ir import IRProgram
    from quantumbridge.serialization import qpy_dumps, qpy_loads

    native, public = circuit_pair(2)
    source = Statevector.from_instruction(native)
    if factory == "density":source = DensityMatrix.from_statevector(source)
    projector = source.to_operator()
    vector = QS.from_instruction(public).data
    expected_matrix = np.eye(4) - 2 * np.outer(vector, vector.conj())
    if mode == "native":
        reflection = (Operator(np.eye(4)).as_native_operator()
            - 2 * projector.as_native_operator()).as_qiskit_operator()
    else:
        reflection = Operator(np.eye(4)).as_qiskit_operator() - 2 * projector.as_qiskit_operator()
    np.testing.assert_allclose(reflection.data, expected_matrix, atol=2e-14, rtol=0)
    actual, reference = qb.QuantumCircuit(4, global_phase=.23), QuantumCircuit(4, global_phase=.23)
    for circuit in (actual, reference):
        circuit.h(0)
        circuit.ry(.31, 1)
        circuit.rx(-.43, 3)
    initial = QS.from_instruction(reference).data
    # A state projector is not unitary. Its Householder reflection is, with
    # full amplitudes checked against an independent local embedding.
    expected = local_embedding(expected_matrix, (3, 1), 4) @ initial
    actual.unitary(reflection, [3, 1])
    reference.unitary(expected_matrix, [3, 1])
    np.testing.assert_allclose(QS.from_instruction(reference).data, expected, atol=2e-14, rtol=0)
    if path == "compiler":
        actual = qb.transpile(actual, basis_gates=["h", "rx", "ry", "rz", "sx", "cx", "unitary"], optimization_level=1)
    elif "json_ir" in path:actual = circuit_from_ir(IRProgram.from_json(actual.to_ir().to_json()))
    elif "qpy13" in path:
        payload = qpy_dumps(actual, version=13)
        assert b"_public_matrix_basis" not in payload
        actual = qpy_loads(payload)[0]
    if path.startswith("detached"):
        owner = actual.operations[-1].metadata["gate"]
        actual = qb.QuantumCircuit(4, global_phase=.23)
        actual.h(0)
        actual.ry(.31, 1)
        actual.rx(-.43, 3)
        actual.append(owner, [3, 1])
    expected = expected[bit_reversal(4)]
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(actual), expected, atol=4e-13, rtol=0)
    np.testing.assert_allclose(qb.MatrixProductStateDevice(cutoff=0, max_bond_dim=16)
        .matrix_product_state(actual).statevector(), expected, atol=4e-13, rtol=0)


@pytest.mark.parametrize("method", ["copy", "adjoint", "integer", "fractional"])
def test_circuit_operator_derivations_match_actual_sdk_with_global_phase(method):
    from qiskit.quantum_info import Operator as QO
    native, public = circuit_pair(3)
    actual, expected = Operator(native), QO(public)
    if method == "integer":actual, expected = actual.power(2), expected.power(2)
    elif method == "fractional":actual, expected = actual.power(.37), expected.power(.37)
    else:actual, expected = getattr(actual, method)(), getattr(expected, method)()
    np.testing.assert_allclose(actual.as_qiskit_operator().data, expected.data, atol=3e-13, rtol=0)


@pytest.mark.parametrize("label", ["HS", "SX", "IHS"])
def test_clifford_matrix_producer_is_public_literal_not_blanket_native(label):
    from qiskit.quantum_info import Clifford as QC
    from quantumbridge.information import Clifford
    actual, expected = Clifford.from_label(label), QC.from_label(label)
    operator = actual.to_operator()
    np.testing.assert_allclose(operator.data, expected.to_matrix(), atol=2e-14, rtol=0)
    np.testing.assert_allclose(operator.as_qiskit_operator().data, expected.to_matrix(), atol=2e-14, rtol=0)
    assert operator.__dict__.get("_public_matrix_basis") is None


@pytest.mark.parametrize("label", ["XY", "YZI", "IXY"])
def test_pauli_and_sparse_producers_keep_literal_sdk_matrix(label):
    from qiskit.quantum_info import Pauli as QP, SparsePauliOp as QSP
    from quantumbridge.operators import Pauli, SparsePauliOperator
    matrix = Pauli(label).to_matrix()
    np.testing.assert_array_equal(matrix, QP(label).to_matrix())
    sparse = SparsePauliOperator.from_list([(label, .3 + .7j)])
    operator = sparse.to_operator()
    np.testing.assert_array_equal(operator.data, QSP.from_list([(label, .3 + .7j)]).to_matrix())
    np.testing.assert_array_equal(operator.as_qiskit_operator().data, operator.data)
    assert operator.__dict__.get("_public_matrix_basis") is None


def test_raw_channel_random_and_metric_consumers_do_not_depend_on_origin_guessing():
    from quantumbridge.information import Kraus, SuperOp, Choi, random_unitary, random_hermitian, process_fidelity
    from qiskit.quantum_info import Kraus as QK, SuperOp as QS, Choi as QC, Operator as QO
    unitary = random_unitary(4, seed=12403)
    np.testing.assert_allclose(unitary.data.conj().T @ unitary.data, np.eye(4), atol=2e-14, rtol=0)
    matrix = unitary.data.copy()
    raw = Kraus([matrix])
    np.testing.assert_allclose(raw.to_operator().as_qiskit_operator().data, matrix, atol=2e-14, rtol=0)
    np.testing.assert_allclose(SuperOp(raw).data, QS(QK([matrix])).data, atol=2e-14, rtol=0)
    np.testing.assert_allclose(Choi(raw).data, QC(QK([matrix])).data, atol=2e-14, rtol=0)
    expected = abs(np.trace(matrix)) ** 2 / 16
    assert process_fidelity(unitary) == pytest.approx(expected, abs=2e-14)
    hermitian = random_hermitian(4, seed=12404)
    np.testing.assert_array_equal(hermitian.data, hermitian.data.conj().T)
    np.testing.assert_array_equal(hermitian.as_qiskit_operator().data, QO(hermitian.data).data)
