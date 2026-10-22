# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Definition transport, independent mathematics and public binary oracles."""

import io

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.information import Operator
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.serialization.qpy import qpy_dumps, qpy_loads


def ir_roundtrip(circuit):
    return circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))


def nested_circuit():
    p, q = qb.Parameter("p"), qb.Parameter("q")
    inner = qb.Circuit(1, name="inner").rx(p.sin(), 0)
    inner.global_phase = p/7
    outer = qb.Circuit(2, name="outer").append(inner.to_gate({p: q}), [1]).ry(q*q, 0)
    outer.global_phase = q/5
    circuit = qb.Circuit(3, name="transport").h(1).append(outer.to_gate(label="block"), [2, 0])
    return circuit, q


def expected_nested(value):
    x = np.array([[0, 1], [1, 0]], complex)
    rx = np.cos(np.sin(value)/2)*np.eye(2)-1j*np.sin(np.sin(value)/2)*x
    angle = value*value/2
    ry = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    h = np.array([[1, 1], [1, -1]])/np.sqrt(2)
    return np.exp(1j*value*(1/7+1/5))*np.kron(np.kron(rx, h), ry)


@pytest.mark.parametrize("roundtrip", [ir_roundtrip, lambda c: qpy_loads(qpy_dumps(c))[0]], ids=["ir", "qpy13"])
def test_primitive_name_collision_does_not_replace_definition(roundtrip):
    circuit = qb.Circuit(1).append(qb.Circuit(1, name="h").x(0).to_gate(), [0])
    restored = roundtrip(circuit)
    assert isinstance(restored.operations[0].metadata["gate"], qb.Gate)
    np.testing.assert_allclose(Operator(restored).data, [[0, 1], [1, 0]], atol=1e-13)


@pytest.mark.parametrize("roundtrip", [ir_roundtrip, lambda c: qpy_loads(qpy_dumps(c))[0]], ids=["ir", "qpy13"])
def test_nested_symbolic_phase_identity_and_noncontiguous_wires(roundtrip):
    source, q = nested_circuit()
    restored = roundtrip(source)
    assert restored.parameters == (q,)
    gate = restored.operations[1].metadata["gate"]
    assert gate.label == "block" and "gate" in gate.definition.operations[0].metadata
    bound = restored.assign_parameters({q: .37})
    np.testing.assert_allclose(Operator(bound).data, expected_nested(.37), atol=2e-13)
    np.testing.assert_allclose(Operator(roundtrip(source.assign_parameters({q: .37}))).data,
                               expected_nested(.37), atol=2e-13)


def test_actual_public_qpy_loads_native_custom_gate():
    qiskit = pytest.importorskip("qiskit")
    from qiskit import qpy
    from qiskit.quantum_info import Operator as PublicOperator
    source, q = nested_circuit()
    public = qpy.load(io.BytesIO(qpy_dumps(source)))[0]
    assert next(iter(public.parameters)).uuid.hex == q.uuid.replace("-", "")
    raw = PublicOperator(public.assign_parameters({next(iter(public.parameters)): .37})).data
    order = [int(f"{i:03b}"[::-1], 2) for i in range(8)]
    np.testing.assert_allclose(raw[np.ix_(order, order)], expected_nested(.37), atol=2e-13)
    assert qiskit.__version__


def test_actual_native_loads_public_qpy_custom_gate():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit, qpy
    from qiskit.circuit import Parameter
    p = Parameter("theta")
    inner = QuantumCircuit(1, name="h")
    inner.rx(p.sin(), 0)
    inner.global_phase = p/7
    circuit = QuantumCircuit(1)
    circuit.append(inner.to_gate(label="public custom"), [0])
    stream = io.BytesIO()
    qpy.dump(circuit, stream, version=13)
    restored = qpy_loads(stream.getvalue())[0]
    parameter, = restored.parameters
    assert parameter.uuid.replace("-", "") == p.uuid.hex
    gate = restored.operations[0].metadata["gate"]
    assert gate.label == "public custom"
    x = np.array([[0, 1], [1, 0]], complex)
    angle = np.sin(.37)/2
    expected = np.exp(1j*.37/7)*(np.cos(angle)*np.eye(2)-1j*np.sin(angle)*x)
    np.testing.assert_allclose(Operator(restored.assign_parameters({parameter: .37})).data, expected, atol=2e-13)


@pytest.mark.parametrize("format", ["ir", "qpy"])
def test_same_display_name_different_definitions_remain_distinct(format):
    source = qb.Circuit(1)
    source.append(qb.Circuit(1, name="g").x(0).to_gate(), [0])
    source.append(qb.Circuit(1, name="g").z(0).to_gate(), [0])
    restored = ir_roundtrip(source) if format == "ir" else qpy_loads(qpy_dumps(source))[0]
    assert [op.metadata["gate"].name for op in restored.operations] == ["g", "g"]
    np.testing.assert_allclose(Operator(restored).data, [[0, 1], [-1, 0]], atol=1e-13)


@pytest.mark.parametrize("format", ["ir", "qpy"])
def test_vector_identity_partial_binding_and_definition_copy_lifetime(format):
    vector = qb.ParameterVector("angles", 3)
    p, q = vector[0], vector[2]
    definition = qb.Circuit(1, name="vector").rx(p, 0).rz(q.exp(), 0)
    definition.global_phase = q/5
    source = qb.Circuit(1).append(definition.to_gate(), [0])
    roundtrip = ir_roundtrip if format == "ir" else lambda c: qpy_loads(qpy_dumps(c))[0]
    restored = roundtrip(source)
    assert restored.parameters == (p, q)
    assert all(isinstance(value, qb.ParameterVectorElement) for value in restored.parameters)
    partial = restored.assign_parameters({p: .2})
    assert partial.parameters == (q,)
    phi = np.exp(.3)/2
    rz = np.diag([np.exp(-1j*phi), np.exp(1j*phi)])
    rx = np.array([[np.cos(.1), -1j*np.sin(.1)], [-1j*np.sin(.1), np.cos(.1)]])
    expected = np.exp(1j*.3/5)*rz@rx
    np.testing.assert_allclose(Operator(partial.assign_parameters({q: .3})).data, expected, atol=1e-13)
    copied = restored.copy()
    copied.operations[0].metadata["gate"].definition.x(0)
    assert len(restored.operations[0].metadata["gate"].definition.operations) == 2
    assert len(source.operations[0].metadata["gate"].definition.operations) == 2


@pytest.mark.parametrize("format", ["ir", "qpy"])
@pytest.mark.parametrize("state", [0, 1])
def test_controlled_custom_gate_keeps_phase_control_state_and_native_type(format, state):
    p = qb.Parameter("angle")
    body = qb.Circuit(1, name="phase-sensitive").rz(p.sin(), 0)
    body.global_phase = p/7
    controlled = body.to_gate(label="base").control(ctrl_state=state, label="controlled")
    source = qb.Circuit(2).append(controlled, [0, 1])
    restored = ir_roundtrip(source) if format == "ir" else qpy_loads(qpy_dumps(source))[0]
    gate = restored.operations[0].metadata["gate"]
    assert type(gate) is qb.ControlledGate and gate.ctrl_state == state
    assert gate.label == "controlled" and gate.base_gate.label == "base"
    expected = np.eye(4, dtype=complex)
    block = np.exp(1j*.37/7)*np.diag(np.exp(1j*np.array([-1, 1])*np.sin(.37)/2))
    expected[state*2:state*2+2, state*2:state*2+2] = block
    np.testing.assert_allclose(Operator(restored.assign_parameters({p: .37})).data, expected, atol=1e-13)


def test_ir_multi_control_primitive_descriptor_and_complex_unitary():
    matrix = np.array([[1, 1j], [1j, 1]])/np.sqrt(2)
    source = qb.Circuit(3).append(qb.Circuit(1).unitary(matrix, [0]).to_gate().control(2, ctrl_state=1), [0, 1, 2])
    restored = ir_roundtrip(source)
    expected = np.eye(8, dtype=complex)
    expected[4:6, 4:6] = matrix
    np.testing.assert_allclose(Operator(restored).data, expected, atol=1e-13)


@pytest.mark.parametrize("format", ["ir", "qpy"])
@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
def test_restored_gate_actual_jacobian_hessian_and_hvp(format, method):
    from quantumbridge.qml import QNode
    p, q = qb.Parameter("p"), qb.Parameter("q")
    angle = p.sin()+q*p*p
    body = qb.Circuit(1, name="differentiable").rz(angle, 0)
    body.global_phase = angle/3
    source = qb.Circuit(2).h(0).append(body.to_gate().control(), [0, 1])
    restored = ir_roundtrip(source) if format == "ir" else qpy_loads(qpy_dumps(source))[0]
    node = QNode.from_circuit(restored, qb.PauliX(0), diff_method=method, max_diff=2)
    point = np.array([.4, -.2])
    p, q = point
    value = np.sin(p)+q*p*p
    gradient = np.array([np.cos(p)+2*q*p, p*p])
    hessian = np.array([[-np.sin(p)+2*q, 2*p], [2*p, 0]])
    expected_first = -np.sin(value/6)*gradient/6
    expected_second = -np.cos(value/6)*np.outer(gradient, gradient)/36-np.sin(value/6)*hessian/6
    assert node(point) == pytest.approx(np.cos(value/6), abs=2e-12)
    np.testing.assert_allclose(node.compute_jacobian(point), expected_first, atol=1e-10, rtol=0)
    np.testing.assert_allclose(node.compute_hessian(point), expected_second, atol=2e-10, rtol=0)
    direction = np.array([.3, -.2])
    np.testing.assert_allclose(node.compute_hvp(direction, point), expected_second@direction, atol=2e-10, rtol=0)


@pytest.mark.parametrize("state", [0, 1])
def test_actual_bilateral_public_controlled_qpy(state):
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit, qpy
    from qiskit.circuit import Parameter
    from qiskit.quantum_info import Operator as PublicOperator
    p = qb.Parameter("p")
    body = qb.Circuit(1, name="g").rz(p, 0)
    body.global_phase = p/7
    native = qb.Circuit(2).append(body.to_gate().control(ctrl_state=state), [0, 1])
    public_restored = qpy.load(io.BytesIO(qpy_dumps(native)))[0]
    order = [0, 2, 1, 3]
    expected = np.eye(4, dtype=complex)
    expected[2*state:2*state+2, 2*state:2*state+2] = np.exp(1j*.37/7)*np.diag(np.exp(1j*np.array([-1, 1])*.37/2))
    actual = PublicOperator(public_restored.assign_parameters({next(iter(public_restored.parameters)): .37})).data
    np.testing.assert_allclose(actual[np.ix_(order, order)], expected, atol=1e-13)
    p = Parameter("p")
    body = QuantumCircuit(1, name="g")
    body.rz(p, 0)
    body.global_phase = p/7
    public = QuantumCircuit(2)
    public.append(body.to_gate().control(ctrl_state=state, annotated=False), [0, 1])
    stream = io.BytesIO()
    qpy.dump(public, stream, version=13)
    restored = qpy_loads(stream.getvalue())[0]
    assert type(restored.operations[0].metadata["gate"]) is qb.ControlledGate
    np.testing.assert_allclose(Operator(restored.bind({"p": .37})).data, expected, atol=1e-13)


def test_qpy_definition_counts_accumulate_across_all_circuits():
    from quantumbridge.serialization import SerializationLimits, ResourceLimitError
    gate = qb.Circuit(1, name="g").x(0).to_gate()
    source = qb.Circuit(1).append(gate, [0])
    payload = qpy_dumps([source, source])
    for operation in (lambda: qpy_dumps([source, source], limits=SerializationLimits(max_custom_definitions=1)),
                      lambda: qpy_loads(payload, limits=SerializationLimits(max_custom_definitions=1))):
        with pytest.raises(ResourceLimitError): operation()


def test_ir_definition_counts_and_operations_are_aggregate():
    from quantumbridge.serialization import SerializationLimits, ResourceLimitError
    source, _ = nested_circuit()
    data = source.to_ir().to_dict()
    for limits in (SerializationLimits(max_custom_definitions=1), SerializationLimits(max_instructions=3),
                   SerializationLimits(max_nesting_depth=1), SerializationLimits(max_parameter_nodes=2)):
        with pytest.raises(ResourceLimitError): source.to_ir().to_json(serialization_limits=limits)
        with pytest.raises(ResourceLimitError): IRProgram.from_dict(data, serialization_limits=limits)


@pytest.mark.parametrize("corruption", ["width", "params", "classical", "type", "unknown", "nonunitary", "phase", "cycle"])
def test_ir_rejects_corrupt_gate_records_before_publishing(corruption):
    from quantumbridge.serialization import SerializationError
    source, _ = nested_circuit()
    data = source.to_ir().to_dict()
    record = data["instructions"][1]["metadata"]["gate"]
    if corruption == "width": record["num_qubits"] += 1
    elif corruption == "params": record["params"] = []
    elif corruption == "classical": record["num_clbits"] = 1
    elif corruption == "type": record["type"] = "executable_python"
    elif corruption == "unknown": record["module"] = "arbitrary"
    elif corruption == "nonunitary": record["definition"]["instructions"][1]["op"] = "reset"
    elif corruption == "phase": record["definition"]["metadata"]["global_phase"] = float("nan")
    else: record["definition"] = data
    with pytest.raises((ValueError, TypeError, SerializationError)): IRProgram.from_dict(data)
    assert source.operations[1].metadata["gate"].num_qubits == 2


def test_qpy_nested_custom_bytes_are_bounded_and_not_private_json():
    from quantumbridge.serialization import SerializationLimits, SerializationError, ResourceLimitError
    from quantumbridge.serialization.qpy import Reader, FILE_HEADER, CIRCUIT_HEADER, REGISTER, CUSTOM_INSTRUCTION
    source, _ = nested_circuit()
    payload = qpy_dumps(source)
    reader = Reader(payload, SerializationLimits())
    reader.unpack(FILE_HEADER)
    reader.take(1)
    header = reader.unpack(CIRCUIT_HEADER)
    reader.take(header[0]+header[2]+header[5])
    for _ in range(header[6]):
        register = reader.unpack(REGISTER)
        reader.take(register[3]+8*register[2])
    assert reader.unpack("!Q") == (1,)
    offset = reader.pos
    entry = reader.unpack(CUSTOM_INSTRUCTION)
    assert entry[1] == b"g" and entry[4] and entry[5] > 0
    assert b'"parameter_ast"' not in payload and b'"instructions"' not in payload
    for position in (offset+1, offset+CUSTOM_INSTRUCTION.size+entry[0], len(payload)-1):
        with pytest.raises(SerializationError): qpy_loads(payload[:position])
    for field, value in ((1, b"?"), (3, 1), (5, 2**63), (6, 1)):
        fields = list(entry)
        fields[field] = value
        corrupt = payload[:offset]+CUSTOM_INSTRUCTION.pack(*fields)+payload[offset+CUSTOM_INSTRUCTION.size:]
        with pytest.raises(SerializationError): qpy_loads(corrupt)
    with pytest.raises(ResourceLimitError): qpy_loads(payload, limits=SerializationLimits(max_instructions=3))
    with pytest.raises(ResourceLimitError): qpy_dumps(source, limits=SerializationLimits(max_instructions=3))


@pytest.mark.parametrize("version", [2, 3])
def test_qasm_real_declaration_preserves_standard_name_collision(version):
    from quantumbridge.serialization import qasm2_dumps, qasm2_loads, qasm3_dumps, qasm3_loads
    source = qb.Circuit(1).append(qb.Circuit(1, name="h").x(0).to_gate(), [0])
    dump, load = (qasm2_dumps, qasm2_loads) if version == 2 else (qasm3_dumps, qasm3_loads)
    text = dump(source)
    assert "gate qb_gate_" in text
    restored = load(text)
    assert "gate" in restored.operations[0].metadata
    np.testing.assert_allclose(Operator(restored).data, [[0, 1], [1, 0]], atol=1e-13)


def test_qasm3_nested_definitions_keep_symbolic_local_phase_and_compiler_execution():
    from quantumbridge.serialization import qasm3_dumps, qasm3_loads
    from quantumbridge.compiler import transpile
    source, q = nested_circuit()
    source = source.assign_parameters({q: qb.Parameter("theta")})
    with pytest.warns(UserWarning): text = qasm3_dumps(source, allow_metadata_loss=True)
    assert text.count("gate qb_gate_") == 2 and "gphase(" in text
    restored = qasm3_loads(text)
    gate = restored.operations[1].metadata["gate"]
    assert "gate" in gate.definition.operations[0].metadata
    compiled = transpile(restored.bind({"theta": .37}), basis_gates=["rx", "ry", "rz", "h", "cx"], optimization_level=0)
    np.testing.assert_allclose(Operator(compiled).data, expected_nested(.37), atol=2e-13)
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(restored.bind({"theta": .37})), expected_nested(.37)[:, 0], atol=2e-13)


def test_qasm2_custom_internal_phase_remains_lossless_rejection():
    from quantumbridge.serialization import qasm2_dumps, UnsupportedFeature
    body = qb.Circuit(1, name="with_phase").x(0)
    body.global_phase = .3
    source = qb.Circuit(1).append(body.to_gate(), [0])
    with pytest.raises(UnsupportedFeature, match="global_phase"):
        qasm2_dumps(source, allow_metadata_loss=True)


PUBLIC_CASES = ("standard_name", "duplicate_names", "nested_calls", "vector_element",
                "phase_only", "noncontiguous", "labels", "bound_repeat", "open_control", "partial_binding")


def public_case(case, native):
    if native:
        Circuit, Parameter, ParameterVector = qb.Circuit, qb.Parameter, qb.ParameterVector
    else:
        from qiskit import QuantumCircuit as Circuit
        from qiskit.circuit import Parameter, ParameterVector
    p = Parameter("theta")
    t = .37
    x = np.array([[0, 1], [1, 0]], complex)
    z = np.diag([1, -1])
    def rx(a): return np.cos(a/2)*np.eye(2)-1j*np.sin(a/2)*x
    def ry(a): return np.array([[np.cos(a/2), -np.sin(a/2)], [np.sin(a/2), np.cos(a/2)]])
    if case == "standard_name":
        body = Circuit(1, name="h")
        body.x(0)
        expected = x
    elif case == "duplicate_names":
        circuit = Circuit(1)
        for method in ("x", "z"):
            body = Circuit(1, name="g")
            getattr(body, method)(0)
            circuit.append(body.to_gate(), [0])
        return circuit, z@x
    elif case == "nested_calls":
        inner = Circuit(1, name="inner")
        inner.rx(p, 0)
        body = Circuit(1, name="outer")
        body.append(inner.to_gate(), [0])
        body.append(inner.to_gate(), [0])
        expected = rx(2*t)
    elif case == "vector_element":
        p = ParameterVector("v", 3)[2]
        body = Circuit(1, name="vector")
        body.rx(p, 0)
        expected = rx(t)
    elif case == "phase_only":
        body = Circuit(1, name="phase")
        body.global_phase = p/7
        expected = np.exp(1j*t/7)*np.eye(2)
    elif case == "noncontiguous":
        body = Circuit(2, name="permuted")
        body.cx(0, 1)
        circuit = Circuit(3)
        circuit.append(body.to_gate(), [2, 0])
        expected = np.zeros((8, 8))
        for col in range(8): expected[col^((col&1)<<2), col] = 1
        return circuit, expected
    elif case == "labels":
        body = Circuit(1, name="labelled")
        body.ry(.3, 0)
        circuit = Circuit(1)
        circuit.append(body.to_gate(label="display label"), [0])
        return circuit, ry(.3)
    elif case == "bound_repeat":
        body = Circuit(1, name="repeat")
        body.rx(p, 0)
        circuit = Circuit(1)
        circuit.append(body.to_gate(), [0])
        circuit.append(body.to_gate(), [0])
        return circuit.assign_parameters({p: .31}), rx(.62)
    elif case == "open_control":
        body = Circuit(1, name="controlled")
        body.rz(p, 0)
        body.global_phase = p/7
        circuit = Circuit(2)
        circuit.append(body.to_gate().control(ctrl_state=0, annotated=False), [0, 1])
        expected = np.eye(4, dtype=complex)
        expected[:2, :2] = np.exp(1j*t/7)*np.diag(np.exp(1j*np.array([-1, 1])*t/2))
        return circuit, expected
    elif case == "partial_binding":
        q = Parameter("phi")
        body = Circuit(1, name="partial")
        body.ry(p, 0)
        body.rz(q, 0)
        circuit = Circuit(1)
        circuit.append(body.to_gate(), [0])
        return circuit.assign_parameters({p: .2}), np.diag(np.exp(1j*np.array([-1, 1])*t/2))@ry(.2)
    else: raise AssertionError("Unknown independent public scenario.")
    circuit = Circuit(1)
    circuit.append(body.to_gate(), [0])
    return circuit, expected


@pytest.mark.parametrize("case", PUBLIC_CASES)
@pytest.mark.parametrize("direction", ["native_to_public", "public_to_native"])
def test_twenty_distinct_bilateral_public_qpy_scenarios(case, direction):
    pytest.importorskip("qiskit")
    from qiskit import qpy
    from qiskit.quantum_info import Operator as PublicOperator
    source, expected = public_case(case, direction == "native_to_public")
    if direction == "native_to_public":
        restored = qpy.load(io.BytesIO(qpy_dumps(source)))[0]
        parameters = tuple(restored.parameters)
        if parameters: restored = restored.assign_parameters({p: .37 for p in parameters})
        raw = PublicOperator(restored).data
        order = [int(f"{i:0{source.num_qubits}b}"[::-1], 2) for i in range(1<<source.num_qubits)]
        actual = raw[np.ix_(order, order)]
    else:
        stream = io.BytesIO()
        qpy.dump(source, stream, version=13)
        restored = qpy_loads(stream.getvalue())[0]
        if restored.parameters: restored = restored.assign_parameters({p: .37 for p in restored.parameters})
        actual = Operator(restored).data
    np.testing.assert_allclose(actual, expected, atol=2e-13, rtol=0)


@pytest.mark.parametrize("version", [2, 3])
@pytest.mark.parametrize("case", ["standard_name", "duplicate_names", "nested_calls"])
@pytest.mark.parametrize("direction", ["native_to_public", "public_to_native"])
def test_bilateral_public_qasm_declarations(version, case, direction):
    pytest.importorskip("qiskit")
    import warnings
    from qiskit import qasm2, qasm3
    from qiskit.quantum_info import Operator as PublicOperator
    from quantumbridge.serialization import qasm2_dumps, qasm2_loads, qasm3_dumps, qasm3_loads
    source, expected = public_case(case, direction == "native_to_public")
    if source.parameters: source = source.assign_parameters({p: .37 for p in source.parameters})
    dump, load, public = (qasm2_dumps, qasm2_loads, qasm2) if version == 2 else (qasm3_dumps, qasm3_loads, qasm3)
    if direction == "native_to_public":
        if version == 3: pytest.importorskip("qiskit_qasm3_import", reason="Public QASM3 importer is an optional uninstalled environment component.")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            text = dump(source, allow_metadata_loss=True)
        restored = public.loads(text)
        actual = PublicOperator(restored).data
    else:
        text = public.dumps(source)
        restored = load(text)
        actual = Operator(restored).data
        if version == 2 and case == "standard_name" and not np.allclose(actual, expected, atol=2e-13, rtol=0):
            own_roundtrip = PublicOperator(public.loads(text)).data
            np.testing.assert_allclose(actual, own_roundtrip, atol=2e-13, rtol=0)
            assert "gate " not in text
            pytest.xfail("Observed public qasm2.dumps serializes custom h/X as plain h, losing its definition even for public self-roundtrip; not counted as interop match.")
    np.testing.assert_allclose(actual, expected, atol=2e-13, rtol=0)


def test_source_definition_cache_retains_distinct_live_objects():
    from quantumbridge.serialization import qasm3_dumps, qasm3_loads
    source = qb.Circuit(1)
    expected = np.eye(2)
    for i in range(12):
        body = qb.Circuit(1, name="same")
        body.rx(.1*(i+1), 0)
        outer = qb.Circuit(1, name="outer").append(body.to_gate(), [0])
        source.append(outer.to_gate(), [0])
        a = .1*(i+1)/2
        expected = (np.cos(a)*np.eye(2)-1j*np.sin(a)*np.array([[0, 1], [1, 0]]))@expected
    text = qasm3_dumps(source)
    assert text.count("gate qb_gate_") == 24
    np.testing.assert_allclose(Operator(qasm3_loads(text)).data, expected, atol=1e-13)


def test_qpy_expansion_budget_rejects_before_formal_binding_copy(monkeypatch):
    from quantumbridge.serialization import SerializationLimits, ResourceLimitError
    source, _ = nested_circuit()
    payload = qpy_dumps(source)
    def forbidden(*args, **kwargs): raise AssertionError("Over-budget binding copy must not run.")
    monkeypatch.setattr(qb.Circuit, "assign_parameters", forbidden)
    with pytest.raises(ResourceLimitError): qpy_loads(payload, limits=SerializationLimits(max_gate_expansion=1))


def test_source_preflight_limits_nested_copies_before_normalization(monkeypatch):
    from quantumbridge.serialization import SerializationLimits, ResourceLimitError, qasm3_dumps
    import quantumbridge.serialization.control_normalization as normalization
    source, _ = nested_circuit()
    def forbidden(*args, **kwargs): raise AssertionError("Over-budget source normalization must not run.")
    monkeypatch.setattr(normalization, "normalize_source_control", forbidden)
    with pytest.raises(ResourceLimitError): qasm3_dumps(source, limits=SerializationLimits(max_custom_definitions=1))


def test_ir_definition_budget_is_shared_across_control_block_bodies():
    from quantumbridge.serialization import SerializationLimits, ResourceLimitError
    gate = qb.Circuit(1, name="local").x(0).to_gate()
    body = qb.Circuit(1).append(gate, [0])
    source = qb.Circuit(1).if_else(True, body, body)
    data = source.to_ir().to_dict()
    restored = circuit_from_ir(IRProgram.from_dict(data))
    assert len(restored.operations[0].metadata["control_node"].bodies) == 2
    limits = SerializationLimits(max_custom_definitions=1)
    with pytest.raises(ResourceLimitError): source.to_ir().to_dict(serialization_limits=limits)
    with pytest.raises(ResourceLimitError): IRProgram.from_dict(data, serialization_limits=limits)


def test_ir_rejects_recursive_control_body_graph():
    from quantumbridge.serialization import SerializationError
    source = qb.Circuit(1).if_else(True, qb.Circuit(1).x(0))
    source.operations[0].metadata["control_node"].data["body"] = source
    with pytest.raises((ValueError, SerializationError)): source.to_ir().to_dict()


def test_internal_compiler_snapshot_uses_native_symbolic_not_transport_depth():
    from quantumbridge.compiler.pass_manager import _comparison_snapshot
    from quantumbridge.serialization import ResourceLimitError
    p = qb.Parameter("theta")
    phase = p
    for _ in range(60): phase = phase+.001
    circuit = qb.Circuit(1).rx(p, 0)
    circuit.global_phase = phase
    assert _comparison_snapshot(circuit)
    with pytest.raises(ResourceLimitError): circuit.to_ir().to_json()


def test_imported_gate_rejects_bound_complex_rotation_before_execution():
    from quantumbridge.serialization import SerializationError
    source = qb.Circuit(1).append(qb.Circuit(1, name="rotation").rx(.2, 0).to_gate(), [0])
    data = source.to_ir().to_dict()
    body = data["instructions"][0]["metadata"]["gate"]["definition"]
    body["instructions"][0]["params"] = [{"parameter_complex": [1., 2.]}]
    with pytest.raises((ValueError, TypeError, SerializationError)): IRProgram.from_dict(data)


def test_to_gate_checks_bound_primitive_parameters_not_only_zero_placeholders():
    with pytest.raises((ValueError, TypeError)): qb.Circuit(1).rx(1+2j, 0).to_gate()


def test_to_gate_rejects_bound_complex_phase_ast():
    body = qb.Circuit(1).x(0)
    body.global_phase = qb.ParameterExpression("const", (1j,))
    with pytest.raises(ValueError, match="must be real"): body.to_gate()
