# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Preserve actual standard class records, not identity guessed from names."""

import io
import numpy as np
import pytest
import quantumbridge as qb
import quantumbridge.circuit_library as library
from quantumbridge.information import Operator
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.serialization import qpy_dumps, qpy_loads


CASES = [("RXGate", (.3,)), ("RYGate", (.3,)), ("RZGate", (.3,)),
    ("PhaseGate", (.3,)), ("UGate", (.3, .2, -.1)), ("HGate", ()),
    ("XGate", ()), ("YGate", ()), ("ZGate", ()), ("CXGate", ()),
    ("CZGate", ()), ("SwapGate", ()), ("CRXGate", (.3,)),
    ("CRYGate", (.3,)), ("CRZGate", (.3,)), ("UnitaryGate", (np.diag([1, 1j]),)),
    ("CCXGate", ()), ("CCZGate", ()), ("CUGate", (.3, .2, -.1, .17))]


def ir_copy(circuit): return circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))


@pytest.mark.parametrize("name,args", CASES)
@pytest.mark.parametrize("format", ["ir", "qpy"])
def test_standard_type_and_math_survive_native_formats(name, args, format):
    gate = getattr(library, name)(*args)
    source = qb.Circuit(gate.num_qubits).append(gate, range(gate.num_qubits))
    restored = ir_copy(source) if format == "ir" else qpy_loads(qpy_dumps(source))[0]
    actual = restored.operations[0].metadata["gate"]
    assert type(actual) is type(gate)
    assert actual.base_class is gate.base_class
    np.testing.assert_allclose(Operator(restored).data, Operator(source).data, atol=4e-13, rtol=0)


@pytest.mark.parametrize("name,args", CASES)
@pytest.mark.parametrize("direction", ["native_to_public", "public_to_native"])
def test_real_bilateral_public_qpy_class_fields_and_coherent_math(name, args, direction):
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit, qpy
    from qiskit.circuit import library as public
    from qiskit.quantum_info import Operator as PublicOperator
    native, upstream = getattr(library, name)(*args), getattr(public, name)(*args)
    if direction == "native_to_public":
        source = qb.Circuit(native.num_qubits).append(native, range(native.num_qubits))
        result = qpy.load(io.BytesIO(qpy_dumps(source)))[0]
        assert result.data[0].operation.base_class.__name__ == native.base_class.__name__
        expected, actual = Operator(source).data, PublicOperator(result).reverse_qargs().data
    else:
        source = QuantumCircuit(upstream.num_qubits)
        source.append(upstream, range(upstream.num_qubits))
        output = io.BytesIO()
        qpy.dump(source, output, version=13)
        result = qpy_loads(output.getvalue())[0]
        assert result.operations[0].metadata["gate"].base_class.__name__ == upstream.base_class.__name__
        expected, actual = PublicOperator(source).reverse_qargs().data, Operator(result).data
    np.testing.assert_allclose(actual, expected, atol=4e-13, rtol=0)


def test_generic_gate_named_rx_does_not_forge_a_specialized_native_ir_identity():
    gate = qb.Gate("rx", 1, [.3], definition=qb.Circuit(1).ry(.3, 0))
    result = ir_copy(qb.Circuit(1).append(gate, [0]))
    assert type(result.operations[0].metadata["gate"]) is qb.Gate


@pytest.mark.parametrize("name", ["RXGate", "RYGate", "RZGate"])
def test_open_control_standard_qpy_restores_real_state_and_type(name):
    gate = getattr(library, name)(.3).control(1, ctrl_state=0)
    source = qb.Circuit(2).append(gate, [0, 1])
    result = qpy_loads(qpy_dumps(source))[0]
    restored = result.operations[0].metadata["gate"]
    assert type(restored) is type(gate) and restored.ctrl_state == 0
    np.testing.assert_allclose(Operator(result).data, Operator(source).data, atol=4e-13, rtol=0)


@pytest.mark.parametrize("direction", ["native_to_public", "public_to_native"])
def test_asymmetric_two_qubit_unitary_parameters_reverse_wire_order_exactly(direction):
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit, qpy
    from qiskit.circuit.library import UnitaryGate
    from qiskit.quantum_info import Operator as PublicOperator
    # A complex phased permutation is asymmetric under bit reversal.
    matrix = np.eye(4, dtype=complex)[[1, 2, 3, 0]]*np.exp(1j*np.array([.1, .2, -.3, .4]))
    order = [0, 2, 1, 3]
    if direction == "native_to_public":
        source = qb.Circuit(2).append(library.UnitaryGate(matrix), [0, 1])
        result = qpy.load(io.BytesIO(qpy_dumps(source)))[0]
        actual = PublicOperator(result).reverse_qargs().data
    else:
        source = QuantumCircuit(2)
        source.append(UnitaryGate(matrix[np.ix_(order, order)]), [0, 1])
        stream = io.BytesIO()
        qpy.dump(source, stream, version=13)
        actual = Operator(qpy_loads(stream.getvalue())[0]).data
    np.testing.assert_allclose(actual, matrix, atol=2e-13, rtol=0)


@pytest.mark.parametrize("axis", ["RXGate", "RYGate", "RZGate"])
@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
@pytest.mark.parametrize("format", ["ir", "qpy"])
def test_specialized_uuid_vector_and_symbolic_function_hessian_hvp_chain(axis, method, format):
    from quantumbridge.qml import QNode
    p = qb.ParameterVector("angles", 2)[1]
    gate = getattr(library, axis)(.3)
    gate.params[0] = 2*p+p.sin()
    source = qb.Circuit(1)
    if axis == "RZGate": source.h(0)
    source.append(gate, [0])
    restored = ir_copy(source) if format == "ir" else qpy_loads(qpy_dumps(source))[0]
    assert restored.parameters == (p,)
    output = qb.PauliX(0) if axis == "RZGate" else qb.PauliZ(0)
    node = QNode.from_circuit(restored, output, diff_method=method, max_diff=2)
    x = .3
    f, df, ddf = 2*x+np.sin(x), 2+np.cos(x), -np.sin(x)
    hessian = -np.cos(f)*df*df-np.sin(f)*ddf
    assert node(x) == pytest.approx(np.cos(f), abs=2e-12)
    assert node.compute_jacobian(x) == pytest.approx(-np.sin(f)*df, abs=2e-10)
    assert node.compute_hessian(x) == pytest.approx(hessian, abs=4e-10)
    assert node.compute_hvp(.3, x) == pytest.approx(.3*hessian, abs=4e-10)


@pytest.mark.parametrize("name,args", CASES[:12])
@pytest.mark.parametrize("format", ["qasm2", "qasm3"])
def test_standard_objects_export_real_source_without_losing_coherent_phase(name, args, format):
    from quantumbridge.serialization import qasm2_dumps, qasm2_loads, qasm3_dumps, qasm3_loads
    dump, load = (qasm2_dumps, qasm2_loads) if format == "qasm2" else (qasm3_dumps, qasm3_loads)
    gate = getattr(library, name)(*args)
    source = qb.Circuit(gate.num_qubits).append(gate, range(gate.num_qubits))
    restored = load(dump(source))
    np.testing.assert_allclose(Operator(restored).data, Operator(source).data, atol=5e-13, rtol=0)


def test_matrix_control_and_annotation_use_owned_matrix_parameters_not_scalar_arguments():
    gate = library.UnitaryGate(np.diag([1, 1j])).control(1, ctrl_state=0)
    gate.params[0] = np.diag([1, -1j])
    source = qb.Circuit(2).append(qb.AnnotatedOperation(gate, qb.InverseModifier()), [0, 1])
    expected = np.diag([1, 1j, 1, 1])
    np.testing.assert_allclose(Operator(source).data, expected, atol=4e-13, rtol=0)
    for restored in (ir_copy(source), qpy_loads(qpy_dumps(source))[0]):
        np.testing.assert_allclose(Operator(restored).data, expected, atol=4e-13, rtol=0)


@pytest.mark.parametrize("shape,dtype,error", [((2, 2), "O", "unsupported"),
    ((-1, 2), "c16", "invalid"), ((2,), "c16", "unsupported"),
    ((8192, 8192), "c16", "elements"), ((4, 4), "c16", "truncated")])
def test_numpy_qpy_headers_reject_before_materializing_matrix(shape, dtype, error, monkeypatch):
    from quantumbridge.serialization.qpy import Reader
    from quantumbridge.serialization import SerializationLimits, SerializationError
    stream = io.BytesIO()
    np.lib.format.write_array_header_1_0(stream, {"descr": np.dtype(dtype).str, "fortran_order": False, "shape": shape})
    payload = stream.getvalue()
    def forbidden(*args, **kwargs): pytest.fail("Matrix materialized before validating header, bounds and payload length.")
    monkeypatch.setattr(np, "frombuffer", forbidden)
    with pytest.raises((SerializationError, ValueError)):
        Reader(payload, SerializationLimits()).value(b"n", len(payload))


def test_numpy_writer_rejects_byte_limit_before_wire_permutation_copy(monkeypatch):
    import quantumbridge.serialization.qpy as codec
    from quantumbridge.serialization import SerializationLimits, ResourceLimitError
    matrix = np.eye(2, dtype=complex)
    def forbidden(*args, **kwargs): pytest.fail("QPY matrix copied before its byte bound.")
    monkeypatch.setattr(codec, "_unitary_wire_order", forbidden)
    with pytest.raises(ResourceLimitError): codec._parameter_value(matrix, SerializationLimits(max_input_bytes=63))


def test_forged_standard_ir_type_cannot_change_an_executable_definition():
    source = qb.Circuit(1).append(library.RXGate(.3), [0])
    data = source.to_ir().to_dict()
    data["instructions"][0]["metadata"]["gate"]["standard_gate"] = "RYGate"
    with pytest.raises(ValueError, match="actual executable"): IRProgram.from_dict(data)


@pytest.mark.parametrize("state", [0, 1])
@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
@pytest.mark.parametrize("format", ["ir", "qpy"])
def test_controlled_u_phase_symbolic_second_derivative_survives_formats_and_lowering(state, method, format):
    from quantumbridge.qml import QNode
    p = qb.Parameter("p")
    source = qb.Circuit(2).h(0).append(library.CUGate(p*p, .2, -.1, 2*p+p.sin(), ctrl_state=state), [0, 1])
    restored = ir_copy(source) if format == "ir" else qpy_loads(qpy_dumps(source))[0]
    node = QNode.from_circuit(restored.lowered(), qb.PauliX(0), diff_method=method, max_diff=2)
    x = .3
    a, da, dda = x*x/2, x, 1
    b, db, ddb = 2*x+np.sin(x), 2+np.cos(x), -np.sin(x)
    first = -np.sin(a)*da*np.cos(b)-np.cos(a)*np.sin(b)*db
    second = -(np.cos(a)*da*da+np.sin(a)*dda)*np.cos(b)+2*np.sin(a)*da*np.sin(b)*db-np.cos(a)*(np.cos(b)*db*db+np.sin(b)*ddb)
    assert node(x) == pytest.approx(np.cos(a)*np.cos(b), abs=3e-12)
    assert node.compute_jacobian(x) == pytest.approx(first, abs=3e-10)
    assert node.compute_hessian(x) == pytest.approx(second, abs=5e-10)
    assert node.compute_hvp(.3, x) == pytest.approx(.3*second, abs=5e-10)


@pytest.mark.parametrize("separate_circuits", [False, True])
def test_qpy_numeric_element_admission_is_shared_across_records_and_circuits(separate_circuits):
    from quantumbridge.serialization import SerializationLimits, ResourceLimitError
    first = qb.Circuit(1).append(library.UnitaryGate(np.eye(2)), [0])
    source = [first, first.copy()] if separate_circuits else first.compose(first)
    with pytest.raises(ResourceLimitError):
        qpy_dumps(source, limits=SerializationLimits(max_numeric_elements=5))
    payload = qpy_dumps(source, limits=SerializationLimits(max_numeric_elements=8))
    restored = qpy_loads(payload, limits=SerializationLimits(max_numeric_elements=8))
    assert len(restored) == (2 if separate_circuits else 1)
    for circuit in restored: np.testing.assert_allclose(Operator(circuit).data, np.eye(2), atol=2e-13, rtol=0)


def test_matrix_controlled_export_checks_numeric_dimension_work_before_dense_conversion(monkeypatch):
    from quantumbridge.serialization import SerializationLimits, ResourceLimitError
    source = qb.Circuit(2).append(library.UnitaryGate(np.eye(2)).control(1), [0, 1])
    def forbidden(*args, **kwargs): pytest.fail("Controlled matrix export densified before numeric admission.")
    monkeypatch.setattr(qb.Gate, "to_matrix", forbidden)
    with pytest.raises(ResourceLimitError):
        qpy_dumps(source, limits=SerializationLimits(max_numeric_elements=5))
