# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent published-v13 records, including legacy recursive replay."""

import struct
from uuid import UUID

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.serialization import (
    FormatValidationError, SerializationLimits, qpy_dumps, qpy_loads,
)


ZERO = bytes(16)
IDS = {name: UUID(int=index + 100) for index, name in enumerate(("p", "q", "r"))}


def scalar(name):
    raw = name.encode()
    return struct.pack("!H16s", len(raw), IDS[name].bytes) + raw


def record(op, left=b"n", lhs=ZERO, right=b"n", rhs=ZERO):
    return struct.pack("!Bc16sc16s", op, left, lhs, right, rhs)


def integer(value):
    return bytes(8) + struct.pack("!q", value)


def expression(records, names=("p", "q", "r")):
    replay = b"".join(records)
    symbols = b"".join(struct.pack("!ccQ", b"p", b"p", 0) + scalar(name)
                       for name in names)
    return struct.pack("!QQ", len(names), len(replay)) + replay + symbols


def circuit_bytes(expr):
    # A complete RX circuit from the public format specification, not either
    # implementation's writer. The parameter payload is the variable fixture.
    return b"".join((
        struct.pack("!6sBBBBQc", b"QISKIT", 13, 1, 3, 0, 1, b"p"), b"q",
        struct.pack("!HcHIIQIQI", 5, b"f", 8, 1, 0, 2, 1, 1, 0),
        b"probe", struct.pack("!d", 0.), b"{}",
        struct.pack("!c?IH?", b"q", True, 1, 1, True), b"q", struct.pack("!q", 0),
        struct.pack("!Q", 0),
        struct.pack("!HHHIIBHqII", 6, 0, 1, 1, 0, 0, 0, 0, 0, 0),
        b"RXGate", struct.pack("!cI", b"q", 0), struct.pack("!cQ", b"e", len(expr)), expr,
        struct.pack("!H", 0), struct.pack("!ciiiIi", b"\x00", -1, -1, -1, 0, -1),
    ))


def recursive_records(start=b"s", stop=b"e", side="left"):
    marker = lambda kind: record(255, kind) if side == "left" else record(255, right=kind)
    return [
        record(4, b"p", IDS["r"].bytes, b"i", integer(2)),
        marker(start),
        record(0, b"p", IDS["p"].bytes, b"p", IDS["q"].bytes),
        record(3, right=b"i", rhs=integer(2)),
        marker(stop), record(0),
    ]


@pytest.mark.parametrize("side", ["left", "right"])
def test_recursive_v13_replay_preserves_uuid_ast_and_bound_full_matrix(side):
    payload = circuit_bytes(expression(recursive_records(side=side)))
    restored = qpy_loads(payload)[0]
    assert [(p.name, p.uuid) for p in restored.parameters] == [
        (name, str(IDS[name])) for name in ("p", "q", "r")]
    p, q, r = restored.parameters
    assert restored.operations[0].params[0] == r**2 + (p + q)/2
    for point in ((.17, -.38, .51), (-.21, .43, -.62)):
        angle = point[2]**2 + (point[0] + point[1])/2
        expected = np.array([[np.cos(angle/2), -1j*np.sin(angle/2)],
                             [-1j*np.sin(angle/2), np.cos(angle/2)]])
        bound = restored.assign_parameters(dict(zip(restored.parameters, point)))
        np.testing.assert_allclose(Operator(bound).data, expected, atol=3e-15, rtol=0)
        rewritten = qpy_loads(qpy_dumps(restored))[0]
        assert rewritten.parameters == restored.parameters
        np.testing.assert_allclose(Operator(rewritten.bind(dict(zip(restored.parameters, point)))).data,
                                   expected, atol=3e-15, rtol=0)


def test_v13_gradient_replay_uses_parameter_uuid_not_display_sort_order():
    records = [record(5, b"p", IDS["p"].bytes),
               record(2, right=b"p", rhs=IDS["q"].bytes),
               record(13, right=b"p", rhs=IDS["p"].bytes)]
    restored = qpy_loads(circuit_bytes(expression(records, ("q", "p"))))[0]
    assert [(p.name, p.uuid) for p in restored.parameters] == [
        (name, str(IDS[name])) for name in ("p", "q")]
    value = restored.operations[0].params[0].bind({"p": .31, "q": -.42})
    assert value == pytest.approx(-.42*np.cos(.31), abs=2e-15)


@pytest.mark.parametrize("coefficient,expected", [(0,0.), (1,1.), (3,3), (-3,-3)])
@pytest.mark.parametrize("order", [1,2])
def test_v13_scalar_gradient_replay_retains_internal_order_without_fake_symbols(coefficient,expected,order):
    records = [record(2,b"p",IDS["p"].bytes,b"i",integer(coefficient))]
    records += [record(13,right=b"p",rhs=IDS["p"].bytes)]*order
    circuit = qpy_loads(circuit_bytes(expression(records,("p",))))[0]
    assert not circuit.parameters
    angle = circuit.operations[0].params[0]
    assert angle.numeric() == (expected if order == 1 else 0.)
    assert angle._derivative_order == order
    assert not angle.parameters
    rewritten = qpy_loads(qpy_dumps(circuit))[0]
    np.testing.assert_allclose(Operator(circuit).data,Operator(rewritten).data,atol=3e-15,rtol=0)


@pytest.mark.parametrize("kind", ["scalar", "expression"])
def test_conflicting_names_for_one_binary_uuid_are_not_silently_split(kind):
    p, q = qb.Parameter("p", IDS["p"]), qb.Parameter("q", IDS["q"])
    source = qb.Circuit(1).rx(p, 0).ry(q if kind == "scalar" else q.sin(), 0)
    payload = qpy_dumps(source)
    assert payload.count(IDS["q"].bytes) >= 1
    malformed = payload.replace(IDS["q"].bytes, IDS["p"].bytes)
    with pytest.raises(FormatValidationError, match="identit|UUID"):
        qpy_loads(malformed)
    restored = qpy_loads(payload)[0]
    assert restored.parameters == source.parameters


@pytest.mark.parametrize("records", [
    [record(255, b"e")],
    [record(255, b"s"), record(0, b"p", IDS["p"].bytes, b"i", integer(1))],
    [record(255, b"s"), record(255, b"e")],
    [record(255, b"s", b"x" + bytes(15)), record(255, b"e")],
    [record(255, b"s", right=b"e")],
])
def test_malformed_recursive_sequences_fail_and_do_not_pollute_later_loads(records):
    with pytest.raises(FormatValidationError):
        qpy_loads(circuit_bytes(expression(records)))
    valid = circuit_bytes(expression([record(0, b"p", IDS["p"].bytes, b"i", integer(1))], ("p",)))
    assert qpy_loads(valid)[0].parameters[0].uuid == str(IDS["p"])


def test_recursive_depth_is_admitted_before_nested_arithmetic():
    records = [record(255, b"s")]*4 + [record(0, b"p", IDS["p"].bytes, b"i", integer(1))]
    records += [record(255, b"e")]*4
    from quantumbridge.serialization import ResourceLimitError
    with pytest.raises(ResourceLimitError, match="depth"):
        qpy_loads(circuit_bytes(expression(records, ("p",))),
                  limits=SerializationLimits(max_symbolic_expression_depth=3))


def test_same_vector_uuid_with_conflicting_declared_sizes_refuses_before_second_allocation(monkeypatch):
    vector = qb.ParameterVector("v", 4)
    payload = qpy_dumps(qb.Circuit(1).rx(vector[1], 0).ry(vector[1].sin(), 0))
    original = struct.pack("!HQ16sQ", 1, 4, UUID(vector[1].uuid).bytes, 1) + b"v"
    assert payload.count(original) == 2
    offset = payload.rindex(original)
    malformed = payload[:offset] + original[:2] + struct.pack("!Q", 5) + original[10:] + payload[offset+len(original):]
    original_resize, allocated = qb.ParameterVector.resize, []
    def resize(owner, size):
        if size:
            allocated.append(size)
            assert allocated == [4], "Conflicting vector record allocated a second owner"
        return original_resize(owner, size)
    monkeypatch.setattr(qb.ParameterVector, "resize", resize)
    with pytest.raises(FormatValidationError, match="UUID identity"):
        qpy_loads(malformed)
    assert allocated == [4]


@pytest.mark.parametrize("device", ["statevector", "mps"])
@pytest.mark.parametrize("partial", [False, True])
def test_recursive_identity_partial_binding_compiler_and_actual_ad(device, partial):
    from quantumbridge.compiler import native_transpile
    from quantumbridge.qml import QNode
    restored = qpy_loads(circuit_bytes(expression(recursive_records())))[0]
    p, q, r = restored.parameters
    before = restored.to_ir().to_json()
    # Copy/compose must retain the executable operands, not just the displayed
    # circuit parameter set. Binding a copy must not mutate the decoded source.
    working = qb.Circuit(1).compose(restored.copy()).decompose()
    assert working.parameters == restored.parameters
    if partial:
        working = working.assign_parameters({r: .51})
        assert working.parameters == (p, q)
    compiled = native_transpile(working, basis_gates=["rz", "sx", "cx"], optimization_level=0)
    assert compiled.parameters == working.parameters
    point = np.array([.17, -.38] if partial else [.17, -.38, .51])
    angle = .51**2 + (point[0]+point[1])/2
    df = np.array([.5, .5] if partial else [.5, .5, 1.02])
    hf = np.zeros((len(point), len(point)))
    if not partial: hf[2, 2] = 2
    expected_gradient = -np.sin(angle)*df
    expected_hessian = -np.cos(angle)*np.outer(df, df)-np.sin(angle)*hf
    direction = np.array([.3, -.2] if partial else [.3, -.2, .4])
    executor = qb.StatevectorDevice() if device == "statevector" else qb.MatrixProductStateDevice(max_bond_dim=2, cutoff=0)
    node = QNode.from_circuit(compiled, qb.PauliZ(0), device=executor, max_diff=2)
    assert node(point) == pytest.approx(np.cos(angle), abs=3e-13)
    np.testing.assert_allclose(node.compute_jacobian(point), expected_gradient, atol=2e-10, rtol=0)
    np.testing.assert_allclose(node.compute_jvp(direction, point), expected_gradient@direction, atol=2e-10, rtol=0)
    np.testing.assert_allclose(node.compute_vjp(.7, point), .7*expected_gradient, atol=2e-10, rtol=0)
    np.testing.assert_allclose(node.compute_hessian(point), expected_hessian, atol=4e-10, rtol=0)
    np.testing.assert_allclose(node.compute_hvp(direction, point), expected_hessian@direction, atol=4e-10, rtol=0)
    bound = compiled.assign_parameters(dict(zip(compiled.parameters, point)))
    expected = np.array([[np.cos(angle/2), -1j*np.sin(angle/2)],
                         [-1j*np.sin(angle/2), np.cos(angle/2)]])
    np.testing.assert_allclose(Operator(bound).data, expected, atol=3e-13, rtol=0)
    assert restored.to_ir().to_json() == before


def test_replay_aggregate_record_admission_precedes_arithmetic(monkeypatch):
    from quantumbridge.core.parameters import ParameterExpression
    from quantumbridge.serialization import ResourceLimitError
    from quantumbridge.serialization.qpy import Reader
    payload = circuit_bytes(expression([record(0, b"p", IDS["p"].bytes, b"i", integer(1))], ("p",)))
    called = []
    original = ParameterExpression.__add__
    def add(owner, other):
        called.append(True)
        return original(owner, other)
    monkeypatch.setattr(ParameterExpression, "__add__", add)
    with pytest.raises(ResourceLimitError, match="max_parameter_nodes"):
        qpy_loads(payload, limits=SerializationLimits(max_parameter_nodes=1))
    assert not called
    # Two separate expression values share one aggregate read account.
    expr = expression([record(0, b"p", IDS["p"].bytes, b"i", integer(1))], ("p",))
    reader = Reader(expr+expr, SerializationLimits(max_parameter_nodes=3))
    reader.value(b"e", len(expr))
    called.clear()
    with pytest.raises(ResourceLimitError, match="max_parameter_nodes"):
        reader.value(b"e", len(expr))
    assert not called


def test_mid_decode_failure_does_not_publish_or_mutate_existing_parameter_owners(monkeypatch):
    import gc
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    payload = circuit_bytes(expression(recursive_records()))
    existing = qpy_loads(payload)[0]
    before = existing.to_ir().to_json()
    original = qb.ParameterExpression.__add__
    def fail(owner, other):
        raise RuntimeError("injected replay construction failure")
    ledger = UnifiedResourceLedger()
    with monkeypatch.context() as patch:
        patch.setattr(qb.ParameterExpression, "__add__", fail)
        with ResourceScope(ledger), pytest.raises(RuntimeError, match="injected"):
            qpy_loads(payload)
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    assert existing.to_ir().to_json() == before
    assert qb.ParameterExpression.__add__ is original
    recovered = qpy_loads(payload)[0]
    assert recovered.parameters == existing.parameters


@pytest.mark.parametrize("corruption", ["unknown_uuid", "duplicate_symbol", "truncated_record", "invalid_opcode",
                                      "nonzero_padding", "huge_count", "huge_replay", "missing_symbol"])
def test_malformed_identity_and_replay_records_are_typed_and_recoverable(corruption):
    from quantumbridge.serialization import SerializationError
    replay = [record(0, b"p", IDS["p"].bytes, b"i", integer(1))]
    payload = expression(replay, ("p",))
    if corruption == "unknown_uuid": payload = expression([record(0, b"p", ZERO, b"i", integer(1))], ("p",))
    elif corruption == "duplicate_symbol": payload = expression(replay, ("p", "p"))
    elif corruption == "truncated_record": payload = payload[:8]+struct.pack("!Q", 34)+payload[16:50]+payload[51:]
    elif corruption == "invalid_opcode": payload = expression([record(250, b"p", IDS["p"].bytes)], ("p",))
    elif corruption == "nonzero_padding": payload = expression([record(0, b"p", IDS["p"].bytes, b"i", b"x"+integer(1)[1:])], ("p",))
    elif corruption == "huge_count": payload = struct.pack("!Q", 1 << 63)+payload[8:]
    elif corruption == "huge_replay": payload = payload[:8]+struct.pack("!Q", 35*(1 << 40))+payload[16:]
    elif corruption == "missing_symbol": payload = expression(replay, ())
    with pytest.raises(SerializationError):qpy_loads(circuit_bytes(payload))
    recovered = qpy_loads(circuit_bytes(expression(replay, ("p",))))[0]
    assert recovered.parameters[0].uuid == str(IDS["p"])


def test_reconstructed_ast_size_is_bounded_before_binary_construction(monkeypatch):
    from quantumbridge.serialization import ResourceLimitError
    records = [record(0, b"p", IDS["p"].bytes, b"p", IDS["p"].bytes)]
    records += [record(2, right=b"p", rhs=IDS["p"].bytes)]*5
    original, calls = qb.ParameterExpression.__mul__, []
    def multiply(left, right):
        calls.append(True)
        assert len(calls) <= 4, "Overbudget result AST entered binary construction"
        return original(left, right)
    monkeypatch.setattr(qb.ParameterExpression, "__mul__", multiply)
    with pytest.raises(ResourceLimitError, match="max_parameter_nodes"):
        qpy_loads(circuit_bytes(expression(records, ("p",))), limits=SerializationLimits(max_parameter_nodes=12))
    assert len(calls) == 4


def test_native_sparse_vector_restores_entire_root_and_shared_occurrences():
    vector = qb.ParameterVector("v", 12)
    source = qb.Circuit(1).rx(vector[10], 0).ry(vector[2].sin()+vector[10], 0)
    restored = qpy_loads(qpy_dumps(source))[0]
    low, high = restored.parameters
    assert [low.index, high.index] == [2, 10]
    assert low.vector is high.vector
    assert low.vector._root_uuid == vector._root_uuid
    assert [p.uuid for p in low.vector] == [p.uuid for p in vector]
    assert restored.operations[0].params[0] is high
    leaves = restored.operations[1].params[0].parameters
    assert any(p is high for p in leaves) and any(p is low for p in leaves)
