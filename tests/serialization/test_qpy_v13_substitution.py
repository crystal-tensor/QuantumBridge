# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent v13 name-keyed substitution records, not resolved-AST stand-ins."""

import struct
from uuid import UUID

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.serialization import qpy_dumps, qpy_loads, SerializationError, SerializationLimits
from tests.serialization.test_qpy_v13_parameter_replay import (
    ZERO, IDS, record, integer, scalar, circuit_bytes,
)


def parameter(name, identity):
    raw = name.encode()
    return struct.pack("!H16s", len(raw), identity.bytes) + raw


def vector(index, length=12):
    return struct.pack("!HQ16sQ", 1, length, UUID(int=1000+index).bytes, index)+b"v"


SYMBOLS = [(b"p", scalar(name)) for name in ("p", "q", "r")]


def expression(records, symbols=None):
    symbols = SYMBOLS if symbols is None else symbols
    replay = b"".join(records)
    return (struct.pack("!QQ", len(symbols), len(replay))+replay
            + b"".join(struct.pack("!ccQ", kind, kind, 0)+value for kind, value in symbols))


def substitution(entries, *, size=None, padding=bytes(8)):
    # v13 uses an 8-byte leading length for u, unlike numeric i/f operands.
    mapping = struct.pack("!Q", len(entries))+b"".join(
        struct.pack("!HcH", len(key), kind, len(value))+key+value
        for key, kind, value in entries)
    return record(15, b"u", struct.pack("!Q", len(mapping) if size is None else size)+padding)+mapping


def case_records(case):
    p, q, r = (IDS[name].bytes for name in ("p", "q", "r"))
    base = [record(4, b"p", q, b"i", integer(2)), record(0, b"p", p)]
    symbols, expected_names = SYMBOLS, ("q", "r")
    value = scalar("r")
    if case == "single":
        entries = [(b"p", b"p", value)]
        numeric = lambda q, r: r+q*q
    elif case == "simultaneous":
        entries = [(b"p", b"p", scalar("q")), (b"q", b"p", scalar("p"))]
        expected_names = ("p", "q")
        numeric = lambda p, q: q+p*p
    elif case == "sequential":
        return base+[substitution([(b"p", b"p", scalar("q"))]),
                     substitution([(b"q", b"p", scalar("r"))])], symbols, ("r",), lambda r: r+r*r
    elif case in {"nested", "gradient", "recursive", "partial"}:
        value = expression([record(5, b"p", r)], [(b"p", scalar("r"))])
        entries = [(b"p", b"e", value)]
        numeric = lambda q, r: np.sin(r)+q*q
    elif case == "constant_expression":
        value = expression([record(0, b"f", bytes(8)+struct.pack("!d", .21), b"i", integer(0))], [])
        entries = [(b"p", b"e", value)]
        expected_names = ("q",)
        numeric = lambda q: .21+q*q
    elif case == "same_name_new_uuid":
        value = parameter("p", UUID(int=4000))
        entries = [(b"p", b"p", value)]
        expected_names = ("p", "q")
        numeric = lambda p, q: p+q*q
    elif case == "vector":
        symbols = [(b"v", vector(i)) for i in (10, 2)]
        base = [record(5, b"p", UUID(int=1002).bytes),
                record(4, b"p", UUID(int=1010).bytes, b"i", integer(2)), record(0)]
        entries = [(b"v[2]", b"v", vector(10))]
        expected_names = ("v[10]",)
        numeric = lambda x: np.sin(x)+x*x
    else: raise AssertionError(case)
    records = base+[substitution(entries)]
    if case == "gradient":
        records.append(record(13, right=b"p", rhs=r))
        expected_names, numeric = ("q", "r"), lambda q, r: np.cos(r)
    if case == "recursive":
        records = [record(255, b"s"), *records, record(255, b"e"),
                   record(2, right=b"i", rhs=integer(2))]
        numeric = lambda q, r: 2*(np.sin(r)+q*q)
    return records, symbols, expected_names, numeric


CASES = ["single", "simultaneous", "sequential", "nested", "constant_expression",
         "gradient", "recursive", "vector", "same_name_new_uuid"]


@pytest.mark.parametrize("case", CASES)
def test_v13_substitution_is_actual_replay_with_identity_and_full_math(case):
    from quantumbridge.information import Operator
    records, symbols, names, numeric = case_records(case)
    restored = qpy_loads(circuit_bytes(expression(records, symbols)))[0]
    assert tuple(p.name for p in restored.parameters) == names
    if case == "same_name_new_uuid":
        assert restored.parameters[0].uuid == str(UUID(int=4000))
        assert restored.parameters[0].uuid != str(IDS["p"])
    elif case == "vector":
        item, = restored.parameters
        assert item.index == 10 and item.uuid == str(UUID(int=1010))
        assert len(item.vector) == 12 and item.vector._root_uuid == str(UUID(int=1000))
    else:
        assert [(p.name, p.uuid) for p in restored.parameters] == [(name, str(IDS[name])) for name in names]
    for values in ((.17, -.38, .51)[:len(names)], (-.21, .43, -.62)[:len(names)]):
        angle = numeric(*values)
        expected = [[np.cos(angle/2), -1j*np.sin(angle/2)], [-1j*np.sin(angle/2), np.cos(angle/2)]]
        bound = restored.assign_parameters(dict(zip(restored.parameters, values)))
        np.testing.assert_allclose(Operator(bound).data, expected, atol=4e-15, rtol=0)
        rewritten = qpy_loads(qpy_dumps(restored))[0]
        assert rewritten.parameters == restored.parameters
        np.testing.assert_allclose(Operator(rewritten.bind(dict(zip(restored.parameters, values)))).data,
                                   expected, atol=4e-15, rtol=0)


def phase_circuit(expr):
    payload = circuit_bytes(expr)
    fmt = struct.Struct("!HcHIIQIQI")
    header = list(fmt.unpack_from(payload, 20))
    offset = 20+fmt.size+header[0]
    header[1], header[2] = b"e", len(expr)
    return payload[:20]+fmt.pack(*header)+payload[20+fmt.size:offset]+expr+payload[offset+8:]


@pytest.mark.parametrize("device", ["statevector", "mps"])
@pytest.mark.parametrize("partial", [False, True])
def test_substitution_global_phase_compiler_and_actual_derivatives(device, partial):
    from quantumbridge.compiler import native_transpile
    from quantumbridge.qml import QNode
    from quantumbridge.information import Operator
    records, symbols, _, _ = case_records("nested")
    records.append(record(3, right=b"i", rhs=integer(7)))
    source = qpy_loads(phase_circuit(expression(records, symbols)))[0]
    # Both the gate and its coherent phase contain the substitution; the gate
    # angle here is f/7 as encoded, and the global phase is exactly the same.
    before = source.to_ir().to_json()
    q, r = source.parameters
    working = qb.Circuit(1).compose(source.copy()).decompose()
    if partial: working = working.assign_parameters({q: .17})
    point = np.array([-.38] if partial else [.17, -.38])
    f = (np.sin(-.38)+.17**2)/7
    df = np.array([np.cos(-.38)])/7 if partial else np.array([.34, np.cos(-.38)])/7
    hf = np.array([[-np.sin(-.38)]])/7 if partial else np.diag([2, -np.sin(-.38)])/7
    gradient = -np.sin(f)*df
    hessian = -np.cos(f)*np.outer(df, df)-np.sin(f)*hf
    direction = np.array([.3] if partial else [.3, -.2])
    compiled = native_transpile(working, basis_gates=["rz", "sx", "cx"], optimization_level=0)
    executor = qb.StatevectorDevice() if device == "statevector" else qb.MatrixProductStateDevice(max_bond_dim=2, cutoff=0)
    node = QNode.from_circuit(compiled, qb.PauliZ(0), max_diff=2, device=executor)
    np.testing.assert_allclose(node(point), np.cos(f), atol=3e-13, rtol=0)
    np.testing.assert_allclose(node.compute_jacobian(point), gradient, atol=2e-10, rtol=0)
    np.testing.assert_allclose(node.compute_jvp(direction, point), gradient@direction, atol=2e-10, rtol=0)
    np.testing.assert_allclose(node.compute_vjp(.7, point), .7*gradient, atol=2e-10, rtol=0)
    np.testing.assert_allclose(node.compute_hessian(point), hessian, atol=4e-10, rtol=0)
    np.testing.assert_allclose(node.compute_hvp(direction, point), hessian@direction, atol=4e-10, rtol=0)
    expected = np.exp(1j*f)*np.array([[np.cos(f/2), -1j*np.sin(f/2)], [-1j*np.sin(f/2), np.cos(f/2)]])
    np.testing.assert_allclose(Operator(compiled.bind(dict(zip(compiled.parameters, point)))).data,
                               expected, atol=3e-13, rtol=0)
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("corruption", ["short_length", "huge_length", "padding", "rhs", "huge_count",
    "truncated_value", "trailing", "duplicate", "utf8", "unknown_key", "numeric", "matrix", "bad_inner"])
def test_substitution_malformed_records_are_typed_and_recoverable(corruption):
    from quantumbridge.serialization import UnsupportedFeature
    base = [record(0, b"p", IDS["p"].bytes, b"p", IDS["q"].bytes)]
    entry = (b"p", b"p", scalar("r"))
    encoded = substitution([entry])
    error = SerializationError
    if corruption == "short_length": encoded = substitution([entry], size=7)
    elif corruption == "huge_length": encoded = substitution([entry], size=(1 << 63))
    elif corruption == "padding": encoded = substitution([entry], padding=b"x"+bytes(7))
    elif corruption == "rhs": encoded = encoded[:18]+b"p"+encoded[19:]
    elif corruption == "huge_count": encoded = encoded[:35]+struct.pack("!Q", 1 << 63)+encoded[43:]
    elif corruption == "truncated_value": encoded = encoded[:-1]
    elif corruption == "trailing":
        encoded = substitution([entry]);encoded = encoded[:2]+struct.pack("!Q", len(encoded)-35+1)+encoded[10:]+b"!"
    elif corruption == "duplicate": encoded = substitution([entry, entry])
    elif corruption == "utf8": encoded = substitution([(b"\xff", b"p", scalar("r"))])
    elif corruption == "unknown_key": encoded = substitution([(b"r", b"p", scalar("p"))])
    elif corruption == "numeric": encoded = substitution([(b"p", b"f", struct.pack("<d", .2))]);error=UnsupportedFeature
    elif corruption == "matrix": encoded = substitution([(b"p", b"n", b"not-an-array")]);error=UnsupportedFeature
    elif corruption == "bad_inner": encoded = substitution([(b"p", b"e", expression([record(0)], []))])
    with pytest.raises(error): qpy_loads(circuit_bytes(expression(base+[encoded])))
    valid = circuit_bytes(expression(*case_records("single")[:2]))
    assert tuple(p.name for p in qpy_loads(valid)[0].parameters) == ("q", "r")


def test_substitution_count_limit_precedes_replacement_value_construction(monkeypatch):
    from quantumbridge.serialization import ResourceLimitError
    from quantumbridge.serialization.qpy import Reader
    calls = []
    original = Reader.parameter
    def parameter(reader):
        calls.append(True)
        return original(reader)
    # The mapping count is corrupt; no replacement parameter may be allocated.
    records, symbols, _, _ = case_records("single")
    encoded = records[-1]
    records[-1] = encoded[:35]+struct.pack("!Q", 10000)+encoded[43:]
    monkeypatch.setattr(Reader, "parameter", parameter)
    with pytest.raises(ResourceLimitError):
        qpy_loads(circuit_bytes(expression(records, symbols)), limits=SerializationLimits(max_parameter_nodes=16))
    assert len(calls) <= len(symbols)
