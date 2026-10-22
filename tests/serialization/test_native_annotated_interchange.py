# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Lossless native annotations and explicit standard-format boundaries."""

import io
import struct

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.information import Operator
from quantumbridge.serialization import (
    qasm2_dumps, qasm2_loads, qasm3_dumps, qasm3_loads, qpy_dumps, qpy_loads,
    SerializationLimits, UnsupportedFeature, ResourceLimitError,
)


def roundtrip(circuit): return circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))


def phase_modifier_matrix(value):
    result = np.eye(4, dtype=complex)
    result[:2, :2] = np.diag(np.exp(1j*value*np.array([1/3, -5/3])))
    return result


def test_native_qpy_annotation_really_restores_public_structure_and_phase():
    pytest.importorskip("qiskit")
    from qiskit import qpy
    from qiskit.circuit import AnnotatedOperation
    from qiskit.quantum_info import Operator as PublicOperator
    p = qb.Parameter("p")
    body = qb.Circuit(1).rz(p, 0)
    body.global_phase = p/3
    op = qb.AnnotatedOperation(body.to_gate(), [qb.InverseModifier(), qb.ControlModifier(1, 0), qb.PowerModifier(2)])
    source = qb.Circuit(2).append(op, [0, 1])
    restored = qpy.load(io.BytesIO(qpy_dumps(source)))[0]
    annotation = restored.data[0].operation
    assert isinstance(annotation, AnnotatedOperation)
    assert [type(value).__name__ for value in annotation.modifiers] == ["InverseModifier", "ControlModifier", "PowerModifier"]
    assert annotation.modifiers[1].ctrl_state == 0
    parameter, = annotation.params
    assert parameter.uuid.hex == p.uuid.replace("-", "")
    # Both target public releases lose the circuit parameter index on their
    # own QPY v13 annotation roundtrip. Reappend through the public API only
    # for binding; a separate strict xfail records that unrepaired ABI gap.
    from qiskit import QuantumCircuit
    rebound = QuantumCircuit(2)
    rebound.append(annotation, [0, 1])
    actual = PublicOperator(rebound.assign_parameters({parameter: .4})).data
    np.testing.assert_allclose(actual[np.ix_([0, 2, 1, 3], [0, 2, 1, 3])], phase_modifier_matrix(.4), atol=3e-13)
    bound = source.assign_parameters({p: .4})
    actual = PublicOperator(qpy.load(io.BytesIO(qpy_dumps(bound)))[0]).data
    np.testing.assert_allclose(actual[np.ix_([0, 2, 1, 3], [0, 2, 1, 3])], phase_modifier_matrix(.4), atol=3e-13)


def test_public_qpy_annotation_really_restores_native_structure_and_phase():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit, qpy
    from qiskit.circuit import Parameter, AnnotatedOperation, InverseModifier, ControlModifier, PowerModifier
    p = Parameter("p")
    body = QuantumCircuit(1)
    body.rz(p, 0)
    body.global_phase = p/3
    op = AnnotatedOperation(body.to_gate(), [InverseModifier(), ControlModifier(1, 0), PowerModifier(2)])
    source = QuantumCircuit(2)
    source.append(op, [0, 1])
    stream = io.BytesIO()
    qpy.dump(source, stream, version=13)
    restored = qpy_loads(stream.getvalue())[0]
    annotation = restored.operations[0].metadata["annotated_operation"]
    assert type(annotation) is qb.AnnotatedOperation
    assert [type(value).__name__ for value in annotation.modifiers] == ["InverseModifier", "ControlModifier", "PowerModifier"]
    assert annotation.modifiers[1].ctrl_state == 0
    parameter, = restored.parameters
    assert parameter.uuid.replace("-", "") == p.uuid.hex
    np.testing.assert_allclose(Operator(restored.assign_parameters({parameter: .4})).data, phase_modifier_matrix(.4), atol=3e-13)


@pytest.mark.parametrize("kind", ["gate", "instruction", "nested", "controlled", "definition_annotation"])
def test_ir_preserves_real_base_types_order_labels_phase_and_uuid(kind):
    vector = qb.ParameterVector("angles", 3)
    p, k = vector[0], vector[2]
    body = qb.Circuit(1, name="h").rz(p.sin(), 0)
    body.global_phase = p/3
    base = body.to_instruction() if kind == "instruction" else body.to_gate(label="base")
    if kind == "controlled": base = base.control(1, ctrl_state=0)
    if kind == "nested": base = qb.AnnotatedOperation(base, qb.InverseModifier())
    if kind == "definition_annotation":
        base = qb.Circuit(1).append(qb.AnnotatedOperation(base, qb.InverseModifier()), [0]).to_gate()
    operation = qb.AnnotatedOperation(base, [qb.ControlModifier(1, 0), qb.PowerModifier(k), qb.InverseModifier()])
    source = qb.Circuit(operation.num_qubits).append(operation, range(operation.num_qubits))
    restored = roundtrip(source)
    result = restored.operations[0].metadata["annotated_operation"]
    assert type(result.base_op) is type(base) and result == operation
    assert result.modifiers == operation.modifiers
    assert restored.parameters == source.parameters
    assert all(type(item) is qb.ParameterVectorElement for item in restored.parameters)
    # UUID/root/index identity survives owned snapshots. Constructor borrowing
    # does not promise a shared mutable Python vector owner across base copies.
    assert restored.parameters[0].vector._root_uuid == restored.parameters[1].vector._root_uuid
    assert len(restored.parameters[0].vector) == len(restored.parameters[1].vector) == 3
    bound = restored.assign_parameters({p: .37, k: 2})
    if kind == "instruction":
        assert bound.operations[0].metadata["annotated_operation"].base_op.metadata["global_phase"] == pytest.approx(.37/3)
    expected = Operator(source.assign_parameters({p: .37, k: 2})).data
    np.testing.assert_allclose(Operator(bound).data, expected, atol=3e-13)
    result.modifiers.clear()
    assert len(source.operations[0].metadata["annotated_operation"].modifiers) == 3


@pytest.mark.parametrize("field,value", [("type", "bad"), ("base_kind", "foreign"),
    ("modifiers", [{"type": "inverse", "extra": 1}]), ("modifiers", [{"type": "control", "num_ctrl_qubits": 1, "ctrl_state": 2}]),
    ("modifiers", [{"type": "power", "power": {"expression": "eval('bad')"}}])])
def test_ir_rejects_malformed_annotation_records(field, value):
    source = qb.Circuit(1).append(qb.AnnotatedOperation(qb.Gate("x", 1), []), [0]).to_ir().to_dict()
    source["instructions"][0]["metadata"]["annotated_operation"][field] = value
    with pytest.raises((ValueError, TypeError)): IRProgram.from_dict(source)


def test_ir_aggregate_modifier_and_definition_depth_limits():
    op = qb.AnnotatedOperation(qb.Gate("x", 1), [qb.InverseModifier()]*3)
    source = qb.Circuit(1).append(op, [0]).append(op, [0])
    payload = source.to_ir().to_dict()
    for operation in (lambda: source.to_ir().to_dict(serialization_limits=SerializationLimits(max_gate_expansion=5)),
            lambda: IRProgram.from_dict(payload, serialization_limits=SerializationLimits(max_gate_expansion=5))):
        with pytest.raises(ResourceLimitError): operation()
    nested = qb.AnnotatedOperation(op, [])
    source = qb.Circuit(1).append(nested, [0])
    with pytest.raises(ResourceLimitError): source.to_ir().to_dict(serialization_limits=SerializationLimits(max_nesting_depth=2))


@pytest.mark.parametrize("dump", [qasm2_dumps, qasm3_dumps])
def test_standard_object_preservation_rejects_unresolved_annotation(dump):
    source = qb.Circuit(1).append(qb.AnnotatedOperation(qb.Gate("rx", 1, [.3]), qb.InverseModifier()), [0])
    with pytest.raises(UnsupportedFeature): dump(source)
    if dump is not qpy_dumps:
        with pytest.raises(UnsupportedFeature): dump(source, allow_metadata_loss=True)


@pytest.mark.parametrize("format", ["qasm2", "qasm3", "qpy"])
def test_explicit_resolve_to_gate_keeps_valid_format_mathematics_not_annotation_type(format):
    operation = qb.AnnotatedOperation(qb.Gate("rx", 1, [.3]), [qb.InverseModifier(), qb.ControlModifier(1, 0)])
    resolved = qb.resolve_annotated_operation(operation)
    source = qb.Circuit(2).append(resolved, [0, 1])
    dump, load = {"qasm2": (qasm2_dumps, qasm2_loads), "qasm3": (qasm3_dumps, qasm3_loads), "qpy": (qpy_dumps, lambda b: qpy_loads(b)[0])}[format]
    restored = load(dump(source))
    assert all("annotated_operation" not in item.metadata for item in restored.operations)
    expected = np.eye(4, dtype=complex)
    expected[:2, :2] = [[np.cos(.15), 1j*np.sin(.15)], [1j*np.sin(.15), np.cos(.15)]]
    np.testing.assert_allclose(Operator(restored).data, expected, atol=3e-13)


def test_annotation_real_compiler_basis_and_native_state_execution():
    from quantumbridge.compiler import native_transpile
    operation = qb.AnnotatedOperation(qb.Gate("ry", 1, [.3]), [qb.InverseModifier(), qb.ControlModifier(1)])
    source = qb.Circuit(2).h(0).append(operation, [0, 1])
    compiled = native_transpile(roundtrip(source), basis_gates=["rz", "sx", "cx"], optimization_level=0)
    assert {item.name for item in compiled.operations} <= {"rz", "sx", "cx"}
    np.testing.assert_allclose(Operator(compiled).data, Operator(source).data, atol=3e-13)


def test_public_qpy13_annotation_records_restore_a_real_native_object():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit, qpy
    from qiskit.circuit import AnnotatedOperation, ControlModifier
    from qiskit.circuit.library import RXGate
    circuit = QuantumCircuit(2)
    circuit.append(AnnotatedOperation(RXGate(.3), ControlModifier(1)), [0, 1])
    stream = io.BytesIO()
    qpy.dump(circuit, stream, version=13)
    restored = qpy.load(io.BytesIO(stream.getvalue()))[0]
    assert isinstance(restored.data[0].operation, AnnotatedOperation)
    native = qpy_loads(stream.getvalue())[0]
    assert type(native.operations[0].metadata["annotated_operation"]) is qb.AnnotatedOperation
    expected = np.eye(4, dtype=complex)
    expected[2:, 2:] = [[np.cos(.15), -1j*np.sin(.15)], [-1j*np.sin(.15), np.cos(.15)]]
    np.testing.assert_allclose(Operator(native).data, expected, atol=1e-13)


@pytest.mark.parametrize("writer", ["native", "public"])
@pytest.mark.xfail(strict=True, reason="Public 2.4.1/2.6.0 QPY v13 load loses annotation circuit parameter index, including public-produced bytes")
def test_public_qpy13_symbolic_annotation_circuit_parameter_index(writer):
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit, qpy
    from qiskit.circuit import Parameter, AnnotatedOperation, InverseModifier
    if writer == "native":
        p = qb.Parameter("p")
        source = qb.Circuit(1).append(qb.AnnotatedOperation(qb.Gate("rx", 1, [p]), qb.InverseModifier()), [0])
        payload = qpy_dumps(source)
    else:
        from qiskit.circuit.library import RXGate
        p = Parameter("p")
        source = QuantumCircuit(1)
        source.append(AnnotatedOperation(RXGate(p), InverseModifier()), [0])
        output = io.BytesIO()
        qpy.dump(source, output, version=13)
        payload = output.getvalue()
    restored = qpy.load(io.BytesIO(payload))[0]
    assert len(restored.parameters) == len(source.parameters) == 1


QPY_CASES = ["inverse", "power", "fractional", "open_phase", "ordered", "nested",
    "controlled_base", "instruction_base", "collision", "vector", "noncontiguous", "two_controls", "empty"]


def embed_matrix(matrix, targets, width):
    result = np.zeros((1 << width, 1 << width), complex)
    for column in range(1 << width):
        bits = [(column >> (width-1-wire)) & 1 for wire in range(width)]
        inner_column = sum(bits[wire] << (len(targets)-1-index) for index, wire in enumerate(targets))
        for inner_row in range(len(matrix)):
            output = bits.copy()
            for index, wire in enumerate(targets): output[wire] = (inner_row >> (len(targets)-1-index)) & 1
            row = sum(bit << (width-1-wire) for wire, bit in enumerate(output))
            result[row, column] = matrix[inner_row, inner_column]
    return result


def annotation_case(kind, public=False):
    if public:
        from qiskit import QuantumCircuit as Circuit
        from qiskit.circuit import AnnotatedOperation as Annotation, InverseModifier as Inverse, ControlModifier as Control, PowerModifier as Power, ParameterVector
        from qiskit.circuit.library import RXGate, RYGate, RZGate
    else:
        Circuit, Annotation, Inverse, Control, Power, ParameterVector = qb.Circuit, qb.AnnotatedOperation, qb.InverseModifier, qb.ControlModifier, qb.PowerModifier, qb.ParameterVector
        RXGate = lambda p: qb.Gate("rx", 1, [p])
        RYGate = lambda p: qb.Gate("ry", 1, [p])
        RZGate = lambda p: qb.Gate("rz", 1, [p])
    angle, phase = .37, 0.
    x = np.array([[0, 1], [1, 0]], complex)
    rx = lambda a: np.cos(a/2)*np.eye(2)-1j*np.sin(a/2)*x
    rz = lambda a: np.diag(np.exp(1j*np.array([-1, 1])*a/2))
    ry = lambda a: np.array([[np.cos(a/2), -np.sin(a/2)], [np.sin(a/2), np.cos(a/2)]])
    base, matrix, modifiers, targets, values = RXGate(angle), rx(-angle), [Inverse()], [0], {}
    if kind == "power": base, matrix, modifiers = RYGate(angle), ry(2*angle), [Power(2)]
    elif kind == "fractional": base, matrix, modifiers = RZGate(angle), rz(angle/2), [Power(.5)]
    elif kind in {"open_phase", "ordered", "controlled_base", "instruction_base", "vector"}:
        if kind == "vector":
            vector = ParameterVector("angles", 3)
            angle, phase = vector[0].sin()+vector[2].exp(), vector[2]/7
            values = {vector[0]: .21, vector[2]: -.3}
        else: phase = angle/3
        body = Circuit(1, name="phase-base")
        body.rz(angle, 0)
        body.global_phase = phase
        base = body.to_gate(label="base-label")
        numeric = np.sin(.21)+np.exp(-.3) if kind == "vector" else angle
        numeric_phase = -.3/7 if kind == "vector" else phase
        block = np.exp(1j*numeric_phase)*rz(numeric)
        if kind == "instruction_base":
            base = body.to_instruction()
            matrix = block.conj().T
        elif kind == "controlled_base":
            base = base.control(ctrl_state=0, annotated=False) if public else base.control(ctrl_state=0)
            matrix, targets = np.eye(4, dtype=complex), [0, 1]
            matrix[:2, :2] = block.conj().T
        elif kind == "vector": matrix = block.conj().T
        else:
            modifiers = [Inverse(), Control(1, 0), Power(2)] if kind == "ordered" else [Control(1, 0)]
            matrix, targets = np.eye(4, dtype=complex), [0, 1]
            matrix[:2, :2] = np.linalg.matrix_power(block.conj().T, 2) if kind == "ordered" else block
    elif kind == "nested":
        base = Annotation(base, [Inverse()])
        modifiers = [Control(1, 0), Power(2)]
        matrix, targets = np.eye(4, dtype=complex), [0, 1]
        matrix[:2, :2] = rx(-2*angle)
    elif kind == "collision":
        body = Circuit(1, name="h")
        body.x(0)
        base, matrix = body.to_gate(), x
    elif kind == "noncontiguous":
        modifiers, targets = [Control(1, 0), Inverse()], [2, 0]
        matrix = np.eye(4, dtype=complex)
        matrix[:2, :2] = rx(-angle)
    elif kind == "two_controls":
        modifiers, targets = [Control(2, 1)], [0, 1, 2]
        matrix = np.eye(8, dtype=complex)
        # ctrl_state uses little-endian control bits: state 1 opens q1,
        # closes q0, hence the native MSB-ordered |100>, |101> block.
        matrix[4:6, 4:6] = rx(angle)
    elif kind == "empty": base, matrix = Circuit(1, name="empty").to_gate(), np.eye(2)
    operation = Annotation(base, modifiers)
    width = max(targets)+1
    circuit = Circuit(width, name="annotation-"+kind)
    circuit.append(operation, targets)
    return circuit, embed_matrix(matrix, targets, width), values


def assert_annotation_structure(actual, expected):
    assert type(actual).__name__ == type(expected).__name__ == "AnnotatedOperation"
    assert actual.num_qubits == expected.num_qubits
    assert len(actual.modifiers) == len(expected.modifiers)
    for left, right in zip(actual.modifiers, expected.modifiers):
        assert type(left).__name__ == type(right).__name__
        if hasattr(right, "ctrl_state"):
            assert (left.num_ctrl_qubits, left.ctrl_state) == (right.num_ctrl_qubits, right.ctrl_state)
        if hasattr(right, "power"): assert left.power == right.power
    if type(expected.base_op).__name__ == "AnnotatedOperation": assert_annotation_structure(actual.base_op, expected.base_op)
    else:
        assert actual.base_op.name == expected.base_op.name
        assert actual.base_op.num_qubits == expected.base_op.num_qubits
        assert getattr(actual.base_op, "label", None) == getattr(expected.base_op, "label", None)


@pytest.mark.parametrize("kind", QPY_CASES)
def test_native_annotation_qpy_roundtrip_structure_and_independent_complex_matrix(kind):
    source, expected, values = annotation_case(kind)
    payload = qpy_dumps(source)
    assert payload[:7] == b"QISKIT\r" and b'"parameter_ast"' not in payload
    restored = qpy_loads(payload)[0]
    actual, original = (c.operations[0].metadata["annotated_operation"] for c in (restored, source))
    assert_annotation_structure(actual, original)
    assert restored.parameters == source.parameters
    np.testing.assert_allclose(Operator(restored.assign_parameters(values)).data, expected, atol=5e-13)
    copied = restored.copy()
    copied.operations[0].metadata["annotated_operation"].modifiers.clear()
    assert actual.modifiers and original.modifiers


@pytest.mark.parametrize("kind", QPY_CASES)
@pytest.mark.parametrize("direction", ["native_to_public", "public_to_native"])
def test_actual_bilateral_annotation_qpy_scenarios(kind, direction):
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit, qpy
    from qiskit.quantum_info import Operator as PublicOperator
    source, expected, values = annotation_case(kind, public=direction == "public_to_native")
    if direction == "native_to_public":
        result = qpy.load(io.BytesIO(qpy_dumps(source)))[0]
        actual = result.data[0].operation
        assert_annotation_structure(actual, source.operations[0].metadata["annotated_operation"])
        if values:
            rebound = QuantumCircuit(result.num_qubits)
            rebound.append(actual, [result.find_bit(w).index for w in result.data[0].qubits])
            native_ids = {p.uuid.replace("-", ""): v for p, v in values.items()}
            assert {p.uuid.hex for p in rebound.parameters} == set(native_ids)
            result = rebound.assign_parameters({p: native_ids[p.uuid.hex] for p in rebound.parameters})
        matrix = PublicOperator(result).data
        order = [int(f"{i:0{result.num_qubits}b}"[::-1], 2) for i in range(1 << result.num_qubits)]
        np.testing.assert_allclose(matrix[np.ix_(order, order)], expected, atol=5e-13)
    else:
        output = io.BytesIO()
        qpy.dump(source, output, version=13)
        result = qpy_loads(output.getvalue())[0]
        actual = result.operations[0].metadata["annotated_operation"]
        assert_annotation_structure(actual, source.data[0].operation)
        assert {p.uuid.replace("-", "") for p in result.parameters} == {p.uuid.hex for p in source.parameters}
        public_ids = {p.uuid.hex: v for p, v in values.items()}
        bound = result.assign_parameters({p: public_ids[p.uuid.replace("-", "")] for p in result.parameters})
        np.testing.assert_allclose(Operator(bound).data, expected, atol=5e-13)


def primitive_annotation_bytes():
    source = qb.Circuit(2).append(qb.AnnotatedOperation(qb.Gate("rx", 1, [.37]), [qb.ControlModifier(1, 0)]), [0, 1])
    return qpy_dumps(source)


def binary_offsets(payload):
    # Independent published v13 structs, not the decoder under test.
    file_header, circuit_header = struct.Struct("!6sBBBBQc"), struct.Struct("!HcHIIQIQI")
    register, custom, instruction = struct.Struct("!c?IH?"), struct.Struct("!HcII?QIIQ"), struct.Struct("!HHHIIBHqII")
    pos = file_header.size+1
    header = circuit_header.unpack_from(payload, pos)
    pos += circuit_header.size+header[0]+header[2]+header[5]
    for _ in range(header[6]):
        fields = register.unpack_from(payload, pos)
        pos += register.size+fields[3]+8*fields[2]
    count, = struct.unpack_from("!Q", payload, pos)
    assert count == 1
    pos += 8
    record_offset = pos
    record = custom.unpack_from(payload, pos)
    base_offset = pos+custom.size+record[0]+record[5]
    invocation = base_offset+record[8]
    fields = instruction.unpack_from(payload, invocation)
    modifier = invocation+instruction.size+fields[0]+fields[1]+5*(fields[3]+fields[4])
    return record_offset, record, base_offset, invocation, modifier


@pytest.mark.parametrize("corruption", ["definition_flag", "definition_length", "width", "classical", "control",
    "base_width", "base_unknown", "modifier_type", "modifier_size", "zero_controls", "control_state", "power_nan", "scalar_modifier", "cycle", "truncated"])
def test_annotation_qpy_rejects_malformed_binary_records(corruption):
    from quantumbridge.serialization import SerializationError
    payload = primitive_annotation_bytes()
    offset, record, base, invocation, modifier = binary_offsets(payload)
    custom, instruction, value, mod = (struct.Struct(s) for s in ("!HcII?QIIQ", "!HHHIIBHqII", "!cQ", "!cIId"))
    def replace_bytes(position, count, replacement):
        nonlocal payload
        payload = payload[:position]+replacement+payload[position+count:]
    if corruption in {"definition_flag", "definition_length", "width", "classical", "control"}:
        fields = list(record)
        index, item = {"definition_flag": (4, True), "definition_length": (5, 2**63), "width": (2, 3), "classical": (3, 1), "control": (6, 1)}[corruption]
        fields[index] = item
        replace_bytes(offset, custom.size, custom.pack(*fields))
    elif corruption == "base_width":
        fields = list(instruction.unpack_from(payload, base))
        fields[3] = 2
        replace_bytes(base, instruction.size, instruction.pack(*fields))
    elif corruption == "base_unknown": replace_bytes(base+instruction.size, 6, b"ZZGate")
    elif corruption == "modifier_type": replace_bytes(modifier+value.size, 1, b"?")
    elif corruption == "modifier_size": replace_bytes(modifier, value.size, value.pack(b"m", 2**63))
    elif corruption == "zero_controls": replace_bytes(modifier+value.size, mod.size, mod.pack(b"c", 0, 0, 0.))
    elif corruption == "control_state": replace_bytes(modifier+value.size, mod.size, mod.pack(b"c", 1, 2, 0.))
    elif corruption == "power_nan": replace_bytes(modifier+value.size, mod.size, mod.pack(b"p", 0, 0, float("nan")))
    elif corruption == "scalar_modifier": replace_bytes(modifier, value.size+mod.size, value.pack(b"f", 8)+struct.pack("<d", .2))
    elif corruption == "cycle":
        key = payload[offset+custom.size:offset+custom.size+record[0]]
        replacement = instruction.pack(len(key), 0, 0, 2, 0, 0, 0, 0, 0, 0)+key
        replace_bytes(base, record[8], replacement)
        fields = list(record)
        fields[8] = len(replacement)
        replace_bytes(offset, custom.size, custom.pack(*fields))
    else: payload = payload[:-1]
    with pytest.raises(SerializationError): qpy_loads(payload)


@pytest.mark.parametrize("limits", [SerializationLimits(max_custom_definitions=1), SerializationLimits(max_gate_expansion=1),
    SerializationLimits(max_parameter_nodes=1), SerializationLimits(max_nesting_depth=1), SerializationLimits(max_instructions=1)])
def test_annotation_qpy_limits_are_aggregate_across_multi_circuit_files(limits):
    source, _, _ = annotation_case("nested")
    payload = qpy_dumps([source, source])
    for action in (lambda: qpy_dumps([source, source], limits=limits), lambda: qpy_loads(payload, limits=limits)):
        with pytest.raises(ResourceLimitError): action()


def test_annotation_qpy_multi_circuit_names_do_not_alias_modifiers_or_definitions():
    first, expected_first, _ = annotation_case("collision")
    second, expected_second, _ = annotation_case("empty")
    result = qpy_loads(qpy_dumps([first, second]))
    np.testing.assert_allclose(Operator(result[0]).data, expected_first, atol=1e-13)
    np.testing.assert_allclose(Operator(result[1]).data, expected_second, atol=1e-13)
    result[0].operations[0].metadata["annotated_operation"].base_op.definition.z(0)
    assert len(result[1].operations[0].metadata["annotated_operation"].base_op.definition.operations) == 0


def test_annotation_qpy_gate_expansion_limit_applies_before_encoding_a_definition():
    body = qb.Circuit(1).x(0).z(0)
    source = qb.Circuit(1).append(qb.AnnotatedOperation(body.to_gate(), []), [0])
    payload = qpy_dumps(source)
    limits = SerializationLimits(max_gate_expansion=1)
    for action in (lambda: qpy_dumps(source, limits=limits), lambda: qpy_loads(payload, limits=limits)):
        with pytest.raises(ResourceLimitError): action()


def test_annotation_qpy_instruction_metadata_is_not_silently_lost():
    body = qb.Circuit(1, name="original").x(0)
    body.global_phase = .3
    base = body.to_instruction()
    base.metadata["opaque_per_object_value"] = "not-in-definition"
    source = qb.Circuit(1).append(qb.AnnotatedOperation(base, []), [0])
    with pytest.raises(UnsupportedFeature, match="metadata"): qpy_dumps(source)


@pytest.mark.parametrize("power", [qb.Parameter("power"), 2**53+1])
def test_annotation_qpy_unrepresentable_modifier_power_is_explicitly_unsupported(power):
    operation = qb.AnnotatedOperation(qb.Gate("rx", 1, [.3]), qb.PowerModifier(power))
    with pytest.raises(UnsupportedFeature, match="float64"):
        qpy_dumps(qb.Circuit(1).append(operation, [0]))


@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
def test_annotation_qpy_actual_jacobian_hessian_hvp_and_compiler(method):
    from quantumbridge.qml import QNode
    from quantumbridge.compiler import native_transpile
    p, q = qb.ParameterVector("angles", 2)
    angle = p.sin()+q*p*p
    body = qb.Circuit(1).rz(angle, 0)
    body.global_phase = angle/3
    operation = qb.AnnotatedOperation(body.to_gate(), [qb.ControlModifier(1, 0), qb.PowerModifier(2)])
    source = qb.Circuit(2).h(0).append(operation, [0, 1])
    restored = qpy_loads(qpy_dumps(source))[0]
    node = QNode.from_circuit(restored, qb.PauliX(0), diff_method=method, max_diff=2)
    point = np.array([.4, -.2])
    p, q = point
    f, df = np.sin(p)+q*p*p, np.array([np.cos(p)+2*q*p, p*p])
    hf = np.array([[-np.sin(p)+2*q, 2*p], [2*p, 0]])
    gradient = -np.sin(f/3)*df/3
    hessian = -np.cos(f/3)*np.outer(df, df)/9-np.sin(f/3)*hf/3
    assert node(point) == pytest.approx(np.cos(f/3), abs=2e-12)
    np.testing.assert_allclose(node.compute_jacobian(point), gradient, atol=2e-10, rtol=0)
    np.testing.assert_allclose(node.compute_hessian(point), hessian, atol=4e-10, rtol=0)
    direction = np.array([.3, -.2])
    np.testing.assert_allclose(node.compute_hvp(direction, point), hessian@direction, atol=4e-10, rtol=0)
    bound = restored.assign_parameters(dict(zip(restored.parameters, point)))
    compiled = native_transpile(bound, basis_gates=["rz", "sx", "cx"], optimization_level=0)
    assert {op.name for op in compiled.operations} <= {"rz", "sx", "cx"}
    np.testing.assert_allclose(Operator(compiled).data, Operator(bound).data, atol=3e-13)


def test_annotation_qpy_100_wire_mps_never_allocates_dense_matrices(monkeypatch):
    from quantumbridge.qml import QNode
    from quantumbridge.information.matrix_product_state import MatrixProductState
    def forbidden(*args, **kwargs): raise AssertionError("Dense expansion forbidden.")
    for kind, method in [(qb.Gate, "to_matrix"), (qb.StatevectorDevice, "statevector"),
            (qb.DensityMatrixDevice, "density_matrix"), (MatrixProductState, "statevector")]:
        monkeypatch.setattr(kind, method, forbidden)
    p = qb.Parameter("p")
    leaf = qb.AnnotatedOperation(qb.Gate("ry", 1, [p.sin()+2*p]), [qb.InverseModifier(), qb.PowerModifier(2)])
    body = qb.Circuit(100).h(0)
    for wire in range(99): body.cx(wire, wire+1)
    body.append(leaf, [99])
    source = qb.Circuit(100).append(qb.AnnotatedOperation(body.to_gate(), []), range(100))
    restored = qpy_loads(qpy_dumps(source))[0]
    node = QNode.from_circuit(restored, qb.PauliZ(0).tensor(qb.PauliZ(99)),
        device=qb.MatrixProductStateDevice(max_memory_mb=2, max_bond_dim=4, cutoff=0), diff_method="parameter-shift")
    x = .3
    angle = -2*(np.sin(x)+2*x)
    assert node(x) == pytest.approx(np.cos(angle), abs=3e-12)
    assert node.compute_jacobian(x) == pytest.approx(2*np.sin(angle)*(np.cos(x)+2), abs=3e-11)


@pytest.mark.parametrize("kind", ["gate", "standard", "controlled", "annotation", "instruction_annotation"])
def test_native_ir_retains_rebinding_lineage_after_numeric_binding(kind):
    from quantumbridge.circuit_library import standard_gate_object
    p = qb.Parameter("p")
    body = qb.Circuit(1).rx(p, 0)
    base = standard_gate_object("rx", .2) if kind == "standard" else body.to_instruction() if kind == "instruction_annotation" else body.to_gate()
    if kind != "standard": base.params[0] = .2
    if kind == "controlled": base = base.control(ctrl_state=0)
    annotated = kind in {"annotation", "instruction_annotation"}
    operation = qb.AnnotatedOperation(base, qb.InverseModifier()) if annotated else base
    source = qb.Circuit(operation.num_qubits).append(operation, range(operation.num_qubits))
    restored = roundtrip(source)
    recovered = restored.operations[0].metadata["annotated_operation" if annotated else "gate"]
    recovered.params[0] = .7
    a = -.35 if annotated else .35
    block = np.array([[np.cos(a), -1j*np.sin(a)], [-1j*np.sin(a), np.cos(a)]])
    expected = np.eye(4, dtype=complex) if kind == "controlled" else block
    if kind == "controlled": expected[:2, :2] = block
    np.testing.assert_allclose(Operator(recovered).data, expected, atol=2e-13)
    assert base.params == (.2,), "Reloaded mutation must not change the source object."


@pytest.mark.parametrize("corruption", ["extra", "arity", "non_parameter", "width", "value", "nonunitary"])
def test_native_ir_rejects_corrupt_parameter_binding_templates(corruption):
    p = qb.Parameter("p")
    gate = qb.Circuit(1).rx(p, 0).to_gate().assign_parameters({p: .2})
    data = qb.Circuit(1).append(gate, [0]).to_ir().to_dict()
    binding = data["instructions"][0]["metadata"]["gate"]["parameter_binding"]
    if corruption == "extra": binding["module"] = "arbitrary"
    elif corruption == "arity": binding["formals"] = []
    elif corruption == "non_parameter": binding["formals"] = [.3]
    elif corruption == "width": binding["definition"]["registers"]["quantum"]["size"] = 2
    elif corruption == "value": binding["definition"]["instructions"][0]["params"] = [.8]
    else: binding["definition"]["instructions"][0]["op"] = "reset"
    with pytest.raises((ValueError, TypeError)): IRProgram.from_dict(data)


def test_zero_phase_controlled_gate_binding_template_roundtrip_stays_mutable():
    p = qb.Parameter("p")
    body = qb.Circuit(1).rz(p, 0)
    body.global_phase = p/3
    gate = body.to_gate().assign_parameters({p: 0.}).control(ctrl_state=0)
    restored = roundtrip(qb.Circuit(2).append(gate, [0, 1]))
    gate = restored.operations[0].metadata["gate"]
    gate.params[0] = .4
    expected = np.eye(4, dtype=complex)
    expected[:2, :2] = np.exp(.4j/3)*np.diag(np.exp(1j*np.array([-1, 1])*.2))
    np.testing.assert_allclose(gate.to_matrix(), expected, atol=1e-13)


@pytest.mark.parametrize("numeric", [False, True])
def test_ir_serialization_does_not_silently_drop_edited_definition_lineage(numeric):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    gate = qb.Circuit(1).rx(p, 0).to_gate()
    gate.params[0] = .5 if numeric else q
    gate.definition.rz(.5, 0)
    circuit = qb.Circuit(1).append(gate, [0])
    if numeric:
        with pytest.raises(ValueError, match="stale parameter binding lineage"): circuit.to_ir().to_json()
    else:
        restored = roundtrip(circuit).operations[0].metadata["gate"]
        restored.params[0] = .7
        expected = np.diag(np.exp(1j*np.array([-1, 1])*.25))@np.array([[np.cos(.35), -1j*np.sin(.35)], [-1j*np.sin(.35), np.cos(.35)]])
        np.testing.assert_allclose(restored.to_matrix(), expected, atol=1e-13)


def test_ir_rejects_conflicting_duplicate_formal_bindings():
    p = qb.Parameter("p")
    gate = qb.Gate("shared", 1, [p, p], definition=qb.Circuit(1).rx(p, 0))
    gate.params[:] = [.2, .2]
    data = qb.Circuit(1).append(gate, [0]).to_ir().to_dict()
    record = data["instructions"][0]["metadata"]["gate"]
    record["params"][1] = .7
    with pytest.raises(ValueError, match="Conflicting repeated binding"): IRProgram.from_dict(data)
