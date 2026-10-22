# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Lossless native annotations and explicit standard-format boundaries."""

import io

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


@pytest.mark.parametrize("dump", [qasm2_dumps, qasm3_dumps, qpy_dumps])
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


def test_public_qpy13_has_annotation_records_but_native_decoder_explicitly_rejects_them():
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
    with pytest.raises(UnsupportedFeature): qpy_loads(stream.getvalue())
