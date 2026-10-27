# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Standard QPY13 typed control owners and independent native execution math."""

import io
import numpy as np
import pytest

from quantumbridge import (QuantumCircuit, Parameter, StatevectorDevice, DensityMatrixDevice,
    MatrixProductStateDevice, StabilizerDevice, ForLoopOp)
from quantumbridge.serialization import qpy_dumps, qpy_loads


def program(cls, parameter, kind):
    circuit = cls(3, 3, name="control_"+kind)
    if kind == "if":
        circuit.x(2)
        circuit.measure(2, 1)
        with circuit.if_test((circuit.clbits[1], 1), label="choose") as otherwise:
            circuit.x(0)
        with otherwise:
            circuit.h(0)
        circuit.measure(0, 2)
    elif kind == "for":
        angle, index = parameter("angle"), parameter("index")
        with circuit.for_loop(range(3), index, label="iterate"):
            circuit.ry(angle+index*0.2, 2)
    elif kind == "while":
        circuit.x(2)
        circuit.measure(2, 1)
        with circuit.while_loop((circuit.clbits[1], 1), label="until_zero"):
            circuit.reset(2)
            circuit.measure(2, 1)
    elif kind == "switch":
        with circuit.switch(circuit.cregs[0], label="select") as case:
            with case(0):
                circuit.x(2)
            with case(1, 2):
                circuit.h(0)
            with case(case.DEFAULT):
                circuit.z(1)
    else:
        with circuit.for_loop(range(3)):
            with circuit.if_test((circuit.clbits[1], 0)):
                circuit.continue_loop()
            circuit.x(2)
            circuit.break_loop()
        circuit.x(0)
    return circuit


def assert_math(circuit, kind, device_type=StatevectorDevice):
    expected = np.zeros(8, complex)
    if kind == "for":
        assert len(circuit.parameters) == 1
        circuit = circuit.assign_parameters({next(iter(circuit.parameters)): 0.1})
        expected[[0, 1]] = [np.cos(0.45), np.sin(0.45)]
    else:
        expected[{"if": 5, "while": 0, "switch": 1, "jump": 4}[kind]] = 1
    np.testing.assert_allclose(device_type().density_matrix(circuit), np.outer(expected, expected.conj()), atol=1e-13, rtol=0)


def control_types(circuit):
    return [(item.operation.base_class.__name__, len(getattr(item.operation, "blocks", ())),
             [circuit.find_bit(bit).index for bit in item.qubits],
             [circuit.find_bit(bit).index for bit in item.clbits],
             [control_types(body) for body in getattr(item.operation, "blocks", ())])
            for item in circuit.data if item.operation.name in
            {"if_else", "for_loop", "while_loop", "switch_case", "break_loop", "continue_loop"}]


@pytest.mark.parametrize("kind", ["if", "for", "while", "switch", "jump"])
def test_native_standard_control_records_roundtrip_types_binding_and_math(kind):
    source = program(QuantumCircuit, Parameter, kind)
    restored = qpy_loads(qpy_dumps(source))[0]
    assert type(restored) is QuantumCircuit
    assert control_types(restored) == control_types(source)
    assert [p.uuid for p in restored.parameters] == [p.uuid for p in source.parameters]
    if kind == "for":
        owner = restored.data[0].operation
        assert type(owner) is ForLoopOp and type(owner.params[0]) is range
        assert owner.params[1].uuid in {p.uuid for p in owner.blocks[0].parameters}
    assert_math(restored, kind)


@pytest.mark.parametrize("device_type", [StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice, StabilizerDevice])
def test_decoded_feedforward_reaches_four_existing_devices(device_type):
    source = program(QuantumCircuit, Parameter, "if")
    restored = qpy_loads(qpy_dumps(source))[0]
    assert_math(restored, "if", device_type)
    assert device_type().run_shots(restored, shots=3).counts() == {"011": 3}


@pytest.mark.parametrize("kind", ["if", "for", "while", "switch", "jump"])
def test_actual_public_four_direction_qpy_control_interoperability(kind):
    public = pytest.importorskip("qiskit")
    from qiskit import qpy
    from qiskit.circuit import Parameter as PublicParameter
    native_source = program(QuantumCircuit, Parameter, kind)
    public_source = program(public.QuantumCircuit, PublicParameter, kind)
    stream = io.BytesIO()
    qpy.dump(public_source, stream, version=13)
    public_back = qpy.load(io.BytesIO(stream.getvalue()))[0]
    public_native = qpy_loads(stream.getvalue())[0]
    native_public = qpy.load(io.BytesIO(qpy_dumps(native_source)))[0]
    assert control_types(public_back) == control_types(public_source)
    assert control_types(public_native) == control_types(public_source)
    assert control_types(native_public) == control_types(native_source)
    assert_math(public_native, kind)
    assert_math(qpy_loads(qpy_dumps(public_native))[0], kind)
    assert [str(p.uuid) for p in public_back.parameters] == [str(p.uuid) for p in public_source.parameters]
    assert [p.uuid for p in public_native.parameters] == [str(p.uuid) for p in public_source.parameters]


def variables_program(cls, classical):
    circuit = cls(3, 2, name="scoped")
    flag = circuit.add_var("flag", True)
    with circuit.if_test(flag):
        local = circuit.add_var("local", False)
        circuit.store(local, True)
        with circuit.if_test(local):
            circuit.x(2)
    with circuit.if_test((circuit.clbits[1], 0)):
        circuit.store(flag, classical.logical_not(flag) if hasattr(classical, "logical_not") else classical.logic_not(flag))
    with circuit.if_test(flag):
        circuit.x(0)
    return circuit, flag


@pytest.mark.parametrize("device_type", [StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice, StabilizerDevice])
def test_scoped_var_standard_records_preserve_uuid_and_real_classical_updates(device_type):
    from quantumbridge.core import classical
    source, flag = variables_program(QuantumCircuit, classical)
    restored = qpy_loads(qpy_dumps(source))[0]
    assert restored.data[0].operation.base_class.__name__ == "Store"
    assert restored.get_var("flag").var == flag.var
    conditional = restored.data[2].operation
    assert list(conditional.blocks[0].iter_captured_vars())[0] is restored.get_var("flag")
    with pytest.raises(KeyError):
        restored.get_var("local")
    np.testing.assert_allclose(device_type().density_matrix(restored), np.diag([0, 1, 0, 0, 0, 0, 0, 0]), atol=1e-13, rtol=0)
    result = device_type().run_shots(restored, shots=3, memory=True)
    assert all(row["variables"][str(flag.var)]["value"] is False for row in result.metadata()["classical_memory"])


def test_actual_public_var_scope_four_direction_and_store_type():
    public = pytest.importorskip("qiskit")
    from qiskit import qpy
    from qiskit.circuit.classical import expr
    from quantumbridge.core import classical
    native, native_flag = variables_program(QuantumCircuit, classical)
    upstream, public_flag = variables_program(public.QuantumCircuit, expr)
    stream = io.BytesIO()
    qpy.dump(upstream, stream, version=13)
    for source in (qpy_loads(stream.getvalue())[0], qpy_loads(qpy_dumps(native))[0]):
        np.testing.assert_allclose(StatevectorDevice().density_matrix(source)[1, 1], 1, atol=1e-13)
        assert source.data[0].operation.base_class.__name__ == "Store"
        back = qpy.load(io.BytesIO(qpy_dumps(source)))[0]
        assert back.data[0].operation.base_class.__name__ == "Store"
        assert str(back.get_var("flag").var) == source.get_var("flag").value[0]
    assert qpy_loads(stream.getvalue())[0].get_var("flag").value[0] == str(public_flag.var)
    assert str(qpy.load(io.BytesIO(qpy_dumps(native)))[0].get_var("flag").var) == str(native_flag.var)


@pytest.mark.parametrize("device_type", [StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice, StabilizerDevice])
def test_standard_decoded_stochastic_feedback_keeps_complex_ensemble_and_correlations(device_type):
    source = QuantumCircuit(3, 3, name="coherent_branches")
    source.h(2)
    source.measure(2, 1)
    with source.if_test((source.clbits[1], 1)) as otherwise:
        source.h(0)
        source.s(0)
    with otherwise:
        source.x(0)
    restored = qpy_loads(qpy_dumps(source))[0]
    vector = np.zeros(8, complex)
    vector[[1, 5]] = [1/np.sqrt(2), 1j/np.sqrt(2)]
    expected = 0.5*np.outer(vector, vector.conj())
    expected[4, 4] += 0.5
    np.testing.assert_allclose(device_type().density_matrix(restored), expected, atol=1e-13, rtol=0)
    restored.measure(0, 2)
    from quantumbridge.execution.control_flow_engine import DynamicExecutionEngine
    probabilities = {}
    for _, bits, _, weight in DynamicExecutionEngine(device_type(), restored).branches():
        label = "".join(map(str, bits))
        probabilities[label] = probabilities.get(label, 0)+weight
    labels = [format(index, "03b") for index in range(8)]
    expected_probabilities = {"001": 0.5, "010": 0.25, "011": 0.25}
    np.testing.assert_allclose([probabilities.get(label, 0) for label in labels],
                               [expected_probabilities.get(label, 0) for label in labels], atol=1e-13, rtol=0)


def test_qpy_loop_range_is_not_capped_by_default_runtime_iteration_policy():
    from quantumbridge import ExecutionLimits
    source = QuantumCircuit(1)
    with source.for_loop(range(1001)):
        source.x(0)
    restored = qpy_loads(qpy_dumps(source))[0]
    assert restored.data[0].operation.params[0] == range(1001)
    device = StatevectorDevice(execution_limits=ExecutionLimits(max_loop_iterations=1002))
    np.testing.assert_allclose(device.density_matrix(restored)[1, 1], 1, atol=1e-13)


@pytest.mark.parametrize("scope", ["local", "input", "capture"])
def test_real_variable_table_preserves_scope_instead_of_metadata_sidecar(scope):
    import json
    from quantumbridge import Circuit
    from quantumbridge.core import classical as ce
    from quantumbridge.serialization.qpy import FILE_HEADER, CIRCUIT_HEADER
    source = Circuit(1)
    if scope == "local":
        source.add_uninitialized_var(ce.Var.new("a", ce.Bool()))
    elif scope == "input":
        source.add_input("a", ce.Bool())
    else:
        source.add_capture(ce.Var.new("a", ce.Bool()))
    source.metadata = json.loads(json.dumps(source.metadata))
    payload = qpy_dumps(source)
    assert CIRCUIT_HEADER.unpack_from(payload, FILE_HEADER.size+1)[-1] == 1
    restored = qpy_loads(payload)[0]
    from quantumbridge.core.classical_scope import entries
    actual, mode, ordered = entries(restored)[0]
    assert mode == scope and not ordered and actual.var == source.get_var("a").var
    assert "classical_scope" not in restored.metadata


@pytest.mark.parametrize("scope", ["local", "input", "capture"])
def test_actual_public_reads_real_scope_only_variable_records(scope):
    public = pytest.importorskip("qiskit")
    from qiskit import qpy
    from quantumbridge.core import classical as ce
    source = QuantumCircuit(1)
    variable = ce.Var.new("a", ce.Bool())
    if scope == "local":
        source.add_uninitialized_var(variable)
    elif scope == "input":
        source.add_input(variable)
    else:
        source.add_capture(variable)
    restored = qpy.load(io.BytesIO(qpy_dumps(source)))[0]
    assert type(restored) is public.QuantumCircuit
    assert str(restored.get_var("a").var) == str(variable.var)
    iterator = {"local": restored.iter_declared_vars, "input": restored.iter_input_vars,
                "capture": restored.iter_captured_vars}[scope]
    assert [var.name for var in iterator()] == ["a"]
