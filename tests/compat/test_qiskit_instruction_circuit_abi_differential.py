# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual installed public ABI and bilateral QPY, without upstream source ports."""

import io
import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps, qpy_loads


def public():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit, qpy
    from qiskit.circuit import Instruction
    return QuantumCircuit, Instruction, qpy


def describe(owner):
    return (type(owner).__name__, owner.name, getattr(owner, "label", None), owner.num_qubits,
        owner.num_clbits, tuple(str(value) for value in owner.params))


def outcome(call):
    try: return ("value", describe(call()))
    except Exception as exc: return ("error", type(exc).__name__)


@pytest.mark.parametrize("nq,nc", [(0, 0), (1, 0), (1, 1), (True, 0), (1, True),
    (-1, 0), (1, -1), (1.0, 0), (1, 1.0), (np.int64(1), 0)])
@pytest.mark.parametrize("label", [None, "", "display"])
def test_actual_instruction_constructor_positional_fields_and_errors(nq, nc, label):
    _, Instruction, _ = public()
    assert outcome(lambda: qb.Instruction("source", nq, nc, [], label)) == outcome(lambda: Instruction("source", nq, nc, [], label))


@pytest.mark.parametrize("kind", ["defined", "opaque", "measure"])
@pytest.mark.parametrize("mode", ["omitted", None, False, True])
def test_actual_instruction_inverse_return_and_construction_error_protocol(kind, mode):
    QuantumCircuit, Instruction, _ = public()
    if kind == "defined":
        native = qb.Circuit(1, name="source").rx(.3, 0).to_instruction(label="display")
        source = QuantumCircuit(1, name="source")
        source.rx(.3, 0)
        upstream = source.to_instruction(label="display")
    else:
        native, upstream = (factory(kind, 1, int(kind == "measure"), [.3] if kind == "opaque" else [], "display") for factory in (qb.Instruction, Instruction))
    kwargs = {} if mode == "omitted" else {"annotated": mode}
    assert outcome(lambda: native.inverse(**kwargs)) == outcome(lambda: upstream.inverse(**kwargs))


@pytest.mark.parametrize("kind", ["defined", "opaque", "measure"])
@pytest.mark.parametrize("n", [0, -1, 1.5, 1, 2, 2.0, True, np.int64(2), np.nan, np.inf, "2", 2+0j])
def test_actual_instruction_repeat_counts_errors_return_and_definition(kind, n):
    QuantumCircuit, Instruction, _ = public()
    if kind == "defined":
        native = qb.Circuit(1, name="source").rx(.3, 0).h(0).to_instruction(label="display")
        source = QuantumCircuit(1, name="source")
        source.rx(.3, 0)
        source.h(0)
        upstream = source.to_instruction(label="display")
    else:
        native, upstream = (factory(kind, 1, int(kind == "measure"), [.3] if kind == "opaque" else [], "display") for factory in (qb.Instruction, Instruction))
    assert outcome(lambda: native.repeat(n)) == outcome(lambda: upstream.repeat(n))
    if isinstance(n, (int, float, np.integer)) and np.isfinite(n) and n > 0 and int(n) == n:
        left, right = native.repeat(n), upstream.repeat(n)
        assert len(left.definition.operations) == len(right.definition.data) == int(n)


@pytest.mark.parametrize("format_direction", ["native_to_public", "public_to_native"])
@pytest.mark.parametrize("opaque", [False, True])
def test_actual_bilateral_qpy_instruction_records_keep_type_label_and_definition(opaque, format_direction):
    QuantumCircuit, Instruction, qpy = public()
    from qiskit.quantum_info import Operator as PublicOperator
    native = qb.Instruction("opaque", 1, 0, [.3], "display") if opaque else qb.Circuit(1, name="source").rx(.3, 0).h(0).to_instruction(label="display")
    body = QuantumCircuit(1, name="source")
    body.rx(.3, 0)
    body.h(0)
    upstream = Instruction("opaque", 1, 0, [.3], "display") if opaque else body.to_instruction(label="display")
    if format_direction == "native_to_public":
        source = qb.Circuit.from_instruction(native.repeat(2))
        restored = qpy.load(io.BytesIO(qpy_dumps(source)))[0]
        assert len(restored.data) == 2
        for item in restored.data: assert item.operation.base_class is Instruction and item.operation.label == "display"
        if not opaque: np.testing.assert_allclose(PublicOperator(restored).data, Operator(source).data, atol=5e-13, rtol=0)
    else:
        source = QuantumCircuit(1)
        source.append(upstream, [0])
        source.append(upstream, [0])
        stream = io.BytesIO()
        qpy.dump(source, stream, version=13)
        restored = qpy_loads(stream.getvalue())[0]
        assert len(restored.operations) == 2
        for item in restored.operations:
            actual = item.metadata["instruction_object"]
            assert type(actual) is qb.Instruction and actual.label == "display" and actual.name == upstream.name
        if not opaque: np.testing.assert_allclose(Operator(restored).data, PublicOperator(source).data, atol=5e-13, rtol=0)


@pytest.mark.parametrize("reps", [0, -1, 1.5, 2, 2.0, True, np.int64(2)])
def test_circuit_repeat_is_not_instruction_repeat(reps):
    QuantumCircuit, _, _ = public()
    native = qb.Circuit(1, name="source").rx(.3, 0)
    upstream = QuantumCircuit(1, name="source")
    upstream.rx(.3, 0)
    def circuit_outcome(owner):
        try:
            result = owner.repeat(reps)
            return ("value", result.name, len(result.operations) if isinstance(result, qb.Circuit) else len(result.data))
        except Exception as exc: return ("error", type(exc).__name__)
    assert circuit_outcome(native) == circuit_outcome(upstream)


@pytest.mark.parametrize("name", ["source", "source_dg"])
@pytest.mark.parametrize("count", [1, 2, 3])
def test_actual_repeated_circuit_inverse_names(name, count):
    QuantumCircuit, _, _ = public()
    native, upstream = qb.Circuit(1, name=name), QuantumCircuit(1, name=name)
    for _ in range(count): native, upstream = native.inverse(), upstream.inverse()
    assert native.name == upstream.name


@pytest.mark.parametrize("inverse", [False, True])
def test_actual_public_qpy_reads_controlled_sx_dependencies_without_a_fabricated_inverse_class(inverse):
    _, _, qpy = public()
    from qiskit.quantum_info import Operator as PublicOperator
    source = qb.Circuit(2).append("csxdg" if inverse else "csx", [1], controls=[0])
    restored = qpy.load(io.BytesIO(qpy_dumps(source)))[0]
    assert restored.data[0].operation.name == ("csxdg" if inverse else "csx")
    np.testing.assert_allclose(PublicOperator(restored).reverse_qargs().data, Operator(source).data, atol=4e-13, rtol=0)
