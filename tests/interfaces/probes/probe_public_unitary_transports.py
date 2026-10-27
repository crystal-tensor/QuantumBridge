# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Installed SDKs are public behavioral oracles, never runtime dependencies."""

import io

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator as NativeOperator
from quantumbridge.core.standard_gates import UnitaryGate as NativeUnitaryGate
from quantumbridge.core.errors import CircuitError as NativeCircuitError
from quantumbridge.serialization import qpy_dumps, qpy_loads
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.ir.qb_ir import IRProgram


WIRES = ((2,), (0, 1), (1, 0), (3, 1), (0, 3))


@pytest.mark.parametrize("wires", WIRES)
@pytest.mark.parametrize("form", ["array", "gate", "operator", "append", "circuit_operator"])
@pytest.mark.parametrize("path", ["source", "compiled", "ir", "native_qpy", "native_to_public_qpy", "public_to_native_qpy"])
def test_same_public_matrix_call_has_complete_complex_state_parity(wires, form, path, record_property):
    from qiskit import QuantumCircuit, qpy
    from qiskit.quantum_info import Statevector, Operator
    from qiskit.circuit.library import UnitaryGate

    rng = np.random.default_rng(6112 + len(wires))
    size = 1 << len(wires)
    matrix, _ = np.linalg.qr(rng.normal(size=(size, size)) + 1j * rng.normal(size=(size, size)))

    def build(circuit_type, gate_type, operator_type):
        source = circuit_type(4, global_phase=.23)
        source.h(0)
        source.ry(.31, 1)
        source.rx(-.43, 3)
        if form == "circuit_operator":
            body = circuit_type(len(wires))
            body.ry(.41, 0)
            if len(wires) == 2: body.cx(0, 1)
            body.unitary(matrix, list(range(len(wires))))
            obj = operator_type(body)
        else: obj = matrix if form == "array" else gate_type(matrix) if form in ("gate", "append") else operator_type(matrix)
        if form == "append": source.append(obj, list(wires))
        else: source.unitary(obj, list(wires), label="same-input")
        source.cx(0, 2)
        return source

    native = build(qb.QuantumCircuit, NativeUnitaryGate, NativeOperator)
    public = build(QuantumCircuit, UnitaryGate, Operator)
    order = [int(f"{index:04b}"[::-1], 2) for index in range(16)]
    expected = np.asarray(Statevector.from_instruction(public).data)[order]
    if path == "compiled":
        native = qb.transpile(native, basis_gates=["h", "rx", "ry", "rz", "sx", "cx", "unitary"], optimization_level=1)
    elif path == "ir": native = circuit_from_ir(IRProgram.from_json(native.to_ir().to_json()))
    elif path in ("native_qpy", "native_to_public_qpy"):
        payload = qpy_dumps(native, version=13)
        assert b"_public_matrix_basis" not in payload
        if path == "native_qpy": native = qpy_loads(payload)[0]
        else:
            transported = qpy.load(io.BytesIO(payload))[0]
            np.testing.assert_allclose(np.asarray(Statevector.from_instruction(transported).data)[order],
                expected, atol=3e-12, rtol=0)
    elif path == "public_to_native_qpy":
        stream = io.BytesIO()
        qpy.dump(public, stream, version=13)
        native = qpy_loads(stream.getvalue())[0]
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(native), expected, atol=3e-12, rtol=0)
    np.testing.assert_allclose(qb.MatrixProductStateDevice(cutoff=0, max_bond_dim=16)
        .matrix_product_state(native).statevector(), expected, atol=3e-12, rtol=0)
    record_property("public_input_matrix_transformed", False)
    record_property("public_input_qargs_transformed", False)


@pytest.mark.parametrize("factory", ["public_method", "raw_constructor"])
@pytest.mark.parametrize("entry,modifier", [(entry, modifier) for entry in ("append", "unitary")
    for modifier in ("copy", "inverse", "repeat", "integer", "fractional", "open", "closed", "annotated")
    if entry == "append" or modifier != "annotated"])
def test_actual_public_matrix_owner_modifier_matches_sdk(modifier, factory, entry):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import UnitaryGate
    from qiskit.quantum_info import Statevector

    rng = np.random.default_rng(7171)
    matrix, _ = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))

    def build(kind):
        if factory == "raw_constructor":
            owner = (NativeUnitaryGate if kind is qb.QuantumCircuit else UnitaryGate)(matrix)
        else:
            body = kind(2)
            body.unitary(matrix, [0, 1])
            owner = body.data[0].operation
        if modifier == "copy": owner = owner.copy()
        elif modifier == "inverse": owner = owner.inverse()
        elif modifier == "repeat": owner = owner.repeat(2)
        elif modifier == "integer": owner = owner.power(2)
        elif modifier == "fractional": owner = owner.power(.37)
        else: owner = owner.control(1, ctrl_state=0 if modifier == "open" else 1, annotated=modifier == "annotated")
        source = kind(4, global_phase=.23)
        source.h(0)
        source.ry(.51, 1)
        source.ry(-.74, 2)
        wires = [2, 3, 1] if modifier in ("open", "closed", "annotated") else [3, 1]
        if entry == "append": source.append(owner, wires)
        else: source.unitary(owner, wires)
        return source

    from qiskit.circuit.exceptions import CircuitError as PublicCircuitError
    try:
        expected = np.asarray(Statevector.from_instruction(build(QuantumCircuit)).data)
    except PublicCircuitError as error:
        assert entry == "unitary" and modifier in ("repeat", "open", "closed")
        assert "to_matrix not defined" in str(error)
        with pytest.raises(NativeCircuitError, match="to_matrix not defined"):
            build(qb.QuantumCircuit)
        return
    order = [int(f"{index:04b}"[::-1], 2) for index in range(16)]
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(build(qb.QuantumCircuit)),
        expected[order], atol=3e-12, rtol=0)


@pytest.mark.parametrize("entry", ["append", "operator_from_circuit"])
def test_independent_public_entries_match_actual_sdk_without_input_conversion(entry):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import UnitaryGate
    from qiskit.quantum_info import Statevector, Operator

    rng = np.random.default_rng(8181)
    matrix, _ = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))
    states = []
    for kind, gate, operator, upstream in ((qb.QuantumCircuit, NativeUnitaryGate, NativeOperator, False),
            (QuantumCircuit, UnitaryGate, Operator, True)):
        source = kind(4, global_phase=.23)
        source.h(0)
        source.ry(.31, 1)
        if entry == "append": source.append(gate(matrix), [3, 1])
        else:
            body = kind(2)
            body.ry(.41, 0)
            body.cx(0, 1)
            body.unitary(matrix, [0, 1])
            source.unitary(operator(body), [3, 1])
        state = np.asarray(Statevector.from_instruction(source).data) if upstream else qb.StatevectorDevice().statevector(source)
        states.append(state)
    order = [int(f"{index:04b}"[::-1], 2) for index in range(16)]
    np.testing.assert_allclose(states[0], states[1][order], atol=3e-12, rtol=0)


@pytest.mark.parametrize("derived", ["from_circuit", "copy", "power", "adjoint", "transpose", "conjugate", "reverse_qargs"])
def test_proven_circuit_operator_derivations_preserve_actual_public_input_math(derived):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector, Operator

    rng = np.random.default_rng(9494)
    matrix, _ = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))
    states = []
    for kind, operator, upstream in ((qb.QuantumCircuit, NativeOperator, False), (QuantumCircuit, Operator, True)):
        body = kind(2, global_phase=.07)
        body.ry(.41, 0)
        body.cx(0, 1)
        body.unitary(matrix, [0, 1])
        value = operator.from_circuit(body) if derived == "from_circuit" else operator(body)
        if derived == "power": value = value.power(.37, branch_cut_rotation=0)
        elif derived != "from_circuit": value = getattr(value, derived)()
        source = kind(4, global_phase=.23)
        source.h(0)
        source.ry(.31, 1)
        source.unitary(value, [3, 1])
        states.append(np.asarray(Statevector.from_instruction(source).data) if upstream
            else qb.StatevectorDevice().statevector(source))
    order = [int(f"{index:04b}"[::-1], 2) for index in range(16)]
    np.testing.assert_allclose(states[0], states[1][order], atol=3e-12, rtol=0)


@pytest.mark.parametrize("power", [-1, .5, -.3, 2])
def test_corrected_four_public_power_entries_match_sdk_with_unchanged_raw_input(power):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import UnitaryGate
    from qiskit.quantum_info import Statevector, Operator

    phases = np.array([.2, -.7, 1.3, -2.1])
    basis = np.exp(2j * np.pi * np.outer(np.arange(4), np.arange(4)) / 4) / 2
    matrix = basis @ np.diag(np.exp(1j * phases)) @ basis.conj().T
    states = []
    for kind, gate, operator, upstream in ((qb.QuantumCircuit, NativeUnitaryGate, NativeOperator, False),
            (QuantumCircuit, UnitaryGate, Operator, True)):
        raw = operator(matrix).power(power, branch_cut_rotation=0).data
        source = kind(2)
        source.ry(.31, 0)
        source.append(gate(raw), [0, 1])
        states.append(np.asarray(Statevector.from_instruction(source).data) if upstream
            else qb.StatevectorDevice().statevector(source))
    np.testing.assert_allclose(states[0], states[1][[0, 2, 1, 3]], atol=3e-12, rtol=0)


@pytest.mark.parametrize("repeat", [False, True])
def test_literal_unitary_operator_is_not_mislabelled_as_a_native_circuit_matrix(repeat):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import UnitaryGate
    from qiskit.quantum_info import Statevector, Operator

    matrix = np.diag(np.exp(1j * np.array([.1, .3, .7, -.2])))
    states = []
    for kind, gate, operator, upstream in ((qb.QuantumCircuit, NativeUnitaryGate, NativeOperator, False),
            (QuantumCircuit, UnitaryGate, Operator, True)):
        owner = gate(matrix)
        if repeat: owner = owner.repeat(2)
        source = kind(2)
        source.h(0)
        source.h(1)
        source.unitary(operator(owner), [0, 1])
        states.append(np.asarray(Statevector.from_instruction(source).data) if upstream
            else qb.StatevectorDevice().statevector(source))
    np.testing.assert_allclose(states[0], states[1][[0, 2, 1, 3]], atol=3e-12, rtol=0)


@pytest.mark.parametrize("path", ["qpy", "ir_json"])
@pytest.mark.parametrize("modifier", ["source", "copy", "inverse", "power", "repeat", "open", "closed"])
def test_detached_restored_owner_derivation_matches_actual_sdk(path, modifier):
    from qiskit import QuantumCircuit, qpy
    from qiskit.quantum_info import Statevector

    rng = np.random.default_rng(9696)
    matrix, _ = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))
    native = qb.QuantumCircuit(2)
    native.unitary(matrix * np.exp(.17j), [0, 1], label="detached-origin")
    payload = qpy_dumps(native)
    external = qpy.load(io.BytesIO(payload))[0]
    restored = qpy_loads(payload)[0] if path == "qpy" else circuit_from_ir(
        IRProgram.from_json(native.to_ir().to_json()))
    states = []
    for kind, owner, upstream in ((qb.QuantumCircuit, restored.operations[0].metadata["gate"], False),
            (QuantumCircuit, external.data[0].operation, True)):
        if modifier == "copy": owner = owner.copy()
        elif modifier == "inverse": owner = owner.inverse()
        elif modifier == "power": owner = owner.power(.37)
        elif modifier == "repeat": owner = owner.repeat(2)
        elif modifier in ("open", "closed"): owner = owner.control(1, ctrl_state=int(modifier == "closed"))
        source = kind(4, global_phase=.23)
        source.h(1)
        source.ry(.31, 0)
        source.h(3)
        source.append(owner, [0, 3, 1] if owner.num_qubits == 3 else [3, 1])
        states.append(np.asarray(Statevector.from_instruction(source).data) if upstream
            else qb.StatevectorDevice().statevector(source))
    order = [int(f"{index:04b}"[::-1], 2) for index in range(16)]
    np.testing.assert_allclose(states[0], states[1][order], atol=3e-12, rtol=0)
