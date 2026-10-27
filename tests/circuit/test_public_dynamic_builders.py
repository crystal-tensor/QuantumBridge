# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Public lexical construction feeding the existing native dynamic interpreter."""

import numpy as np
import pytest

from quantumbridge import (Circuit, ClassicalRegister, Clbit, DensityMatrixDevice, ExecutionLimits,
                           MatrixProductStateDevice, Parameter, QuantumCircuit, StabilizerDevice, StatevectorDevice)
from quantumbridge.core.errors import CircuitError
from quantumbridge.execution.control_flow_engine import DynamicExecutionEngine
from quantumbridge.execution.derivative_status import ResourceLimitError
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits


@pytest.mark.parametrize("device_type", [StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice, StabilizerDevice])
def test_measured_feedforward_uses_same_shot_and_else_is_only_one_branch(device_type):
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.measure(0, 0)
    with circuit.if_test((circuit.clbits[0], 1)) as otherwise:
        circuit.x(1)
    with otherwise:
        circuit.z(1)
    circuit.measure(1, 1)
    result = device_type().run_shots(circuit, shots=128, seed=17)
    assert set(result.counts()) == {"00", "11"} and sum(result.counts().values()) == 128
    np.testing.assert_allclose(device_type().density_matrix(circuit), np.diag([0.5, 0, 0, 0.5]), atol=1e-14)


def test_loop_contexts_bind_index_and_nested_break_continue_execute_real_paths():
    circuit = QuantumCircuit(1, 1)
    with circuit.for_loop(range(3)) as index:
        circuit.ry(index*0.2, 0)
    assert not circuit.parameters
    expected = np.array([np.cos(0.3), np.sin(0.3)])
    np.testing.assert_allclose(StatevectorDevice().density_matrix(circuit), np.outer(expected, expected), atol=1e-14)
    circuit = QuantumCircuit(1, 1)
    with circuit.for_loop(range(4)):
        circuit.x(0)
        with circuit.if_test((circuit.clbits[0], 0)):
            circuit.continue_loop()
        circuit.x(0)
    with circuit.for_loop(range(9)):
        circuit.x(0)
        circuit.break_loop()
        circuit.x(0)
    circuit.measure(0, 0)
    assert StatevectorDevice().run_shots(circuit, shots=3).counts() == {"1": 3}


def test_while_uses_overwritten_classical_value_and_nested_switch_default():
    circuit = QuantumCircuit(2, 2)
    circuit.x(0)
    circuit.measure(0, 0)
    with circuit.while_loop((circuit.clbits[0], 1)):
        circuit.reset(0)
        circuit.measure(0, 0)
    with circuit.switch(circuit.clbits[0]) as case:
        with case(1):
            circuit.h(1)
        with case(case.DEFAULT):
            with circuit.if_test((circuit.clbits[0], 0)):
                circuit.x(1)
    circuit.measure(1, 1)
    assert StatevectorDevice().run_shots(circuit, shots=5).counts() == {"01": 5}


def test_register_condition_and_explicit_noncontiguous_body_mapping():
    condition_register = ClassicalRegister(2, "condition")
    circuit = QuantumCircuit(3)
    circuit.add_register(condition_register)
    circuit.x(0)
    circuit.measure(0, condition_register[0])
    true_body, false_body = QuantumCircuit(1), QuantumCircuit(1)
    true_body.x(0)
    false_body.h(0)
    circuit.if_else((condition_register, 1), true_body, false_body, [2], [])
    circuit.measure(2, condition_register[1])
    assert StatevectorDevice().run_shots(circuit, shots=4).counts() == {"11": 4}


def test_builder_exception_restores_authoritative_store_and_captured_handle():
    circuit = QuantumCircuit(1, 1)
    circuit.z(0)
    with pytest.raises(RuntimeError, match="abort"):
        with circuit.if_test((circuit.clbits[0], 1)):
            circuit.h(0)
            raise RuntimeError("abort")
    assert circuit.count_ops() == {"z": 1}
    with circuit.if_test((circuit.clbits[0], 0)):
        handle = circuit.x(0)
    assert handle.instructions[0].name == "x"
    handle.inverse()
    circuit.measure(0, 0)
    assert StatevectorDevice().run_shots(circuit, shots=2).counts() == {"1": 2}


def test_foreign_bit_invalid_else_and_jump_are_rejected_without_mutation():
    circuit = QuantumCircuit(1, 1)
    with pytest.raises(CircuitError):
        circuit.if_test((Clbit(), 1))
    with pytest.raises(CircuitError):
        circuit.break_loop()
    assert circuit.count_ops() == {}
    with circuit.if_test((circuit.clbits[0], 1)) as otherwise:
        circuit.x(0)
    circuit.z(0)
    with pytest.raises(CircuitError):
        with otherwise:
            circuit.x(0)


def test_nested_builder_parameter_uuid_preserves_nonloop_free_symbols():
    circuit = QuantumCircuit(1, 1)
    angle, index = Parameter("angle"), Parameter("i")
    with circuit.for_loop(range(3), index):
        with circuit.if_test((circuit.clbits[0], 0)):
            circuit.ry(angle+index*0.2, 0)
    assert tuple(circuit.parameters) == (angle,)
    bound = circuit.assign_parameters({angle: 0.1})
    expected = np.array([np.cos(0.45), np.sin(0.45)])
    np.testing.assert_allclose(StatevectorDevice().density_matrix(bound), np.outer(expected, expected), atol=1e-14)


def test_dynamic_control_steps_charge_one_existing_unified_account_and_keep_failed_work():
    circuit = Circuit(1).for_loop(range(2), Circuit(1).x(0))
    exact = UnifiedResourceLedger(UnifiedExecutionLimits(max_derivative_work=4))
    with ResourceScope(exact):
        assert DynamicExecutionEngine(StatevectorDevice(), circuit).shots(1).counts() == {"0": 1}
    assert exact.receipt()["consumed_derivative_work"] == 4
    assert exact.receipt()["consumed_shots"] == 1
    parent = UnifiedResourceLedger(UnifiedExecutionLimits(max_derivative_work=3))
    child = UnifiedResourceLedger(parent=parent)
    with ResourceScope(child), pytest.raises(ResourceLimitError, match="derivative_work"):
        DynamicExecutionEngine(StatevectorDevice(), circuit).shots(1)
    assert child.receipt()["consumed_derivative_work"] == parent.receipt()["consumed_derivative_work"] == 3
    assert child.receipt()["consumed_shots"] == 0
    infinite = Circuit(1).while_loop(True, Circuit(1))
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_derivative_work=2))
    device = StatevectorDevice(execution_limits=ExecutionLimits(max_loop_iterations=5))
    with ResourceScope(ledger), pytest.raises(ResourceLimitError, match="derivative_work"):
        DynamicExecutionEngine(device, infinite).shots(1)
    assert ledger.receipt()["consumed_derivative_work"] == 2


def test_builder_free_parameters_compile_and_ir_round_trip_with_real_measurement_feedback():
    from quantumbridge import transpile
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.ir.qb_ir import IRProgram

    circuit = QuantumCircuit(2, 2)
    angle = Parameter("angle")
    circuit.x(0)
    circuit.measure(0, 0)
    with circuit.if_test((circuit.clbits[0], 1)):
        with circuit.for_loop(range(3)) as index:
            circuit.ry(angle+index*0.2, 1)
    circuit.measure(1, 1)
    restored = circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    assert tuple(p.uuid for p in restored.parameters) == (angle.uuid,)
    bound = restored.bind({restored.parameters[0]: 0.1})
    mapped = Circuit(4, 3).compose(bound, qubits=[3, 1], clbits=[2, 0])
    compiled = transpile(mapped, optimization_level=2)
    expected = {"001": np.cos(0.45)**2, "101": np.sin(0.45)**2}
    for current in (mapped, compiled):
        probabilities = {}
        for _, bits, _, weight in DynamicExecutionEngine(StatevectorDevice(), current).branches():
            label = "".join(map(str, bits))
            probabilities[label] = probabilities.get(label, 0) + weight
        labels = [format(index, "03b") for index in range(8)]
        np.testing.assert_allclose([probabilities.get(label, 0) for label in labels],
                                   [expected.get(label, 0) for label in labels], atol=1e-13, rtol=0)


def test_builder_local_identifiers_do_not_escape_and_outer_capture_keeps_identity():
    from quantumbridge.core import classical as classical

    circuit = QuantumCircuit(1, 1)
    outer = circuit.add_var("outer", True)
    with circuit.if_test(outer):
        local = circuit.add_var("local", False)
        circuit.store(local, True)
        with circuit.if_test(local):
            circuit.x(0)
    assert circuit.get_var("outer") is outer
    with pytest.raises(KeyError):
        circuit.get_var("local")
    circuit.measure(0, 0)
    result = StatevectorDevice().run_shots(circuit, shots=2, memory=True)
    assert result.counts() == {"1": 2}
    assert all(local.value[0] not in item["variables"] for item in result.metadata()["classical_memory"])
    with pytest.raises(classical.ClassicalExecutionError):
        with circuit.if_test(local):
            circuit.x(0)


def test_builder_bit_addition_is_atomic_and_parent_phase_is_preserved():
    circuit = QuantumCircuit(1, 1, global_phase=0.3)
    with pytest.raises(CircuitError):
        with circuit.if_test((circuit.clbits[0], 0)):
            circuit.add_bits([Clbit()])
    assert circuit.num_clbits == 1 and len(circuit.operations) == 0
    assert circuit.global_phase == 0.3


def test_lowered_context_circuit_qasm3_round_trip_keeps_feedforward_and_loop_parameter():
    from quantumbridge.serialization import qasm3_dumps, qasm3_loads

    circuit = QuantumCircuit(2, 2)
    angle = Parameter("angle")
    circuit.x(0)
    circuit.measure(0, 0)
    with circuit.if_test((circuit.clbits[0], 1)):
        with circuit.for_loop(range(3)) as index:
            circuit.ry(angle+index*0.2, 1)
    circuit.measure(1, 1)
    # The existing exporter requires explicit permission to omit a Circuit's
    # nonsemantic name, which has no standard OpenQASM field.
    restored = qasm3_loads(qasm3_dumps(circuit.assign_parameters({angle: 0.1}).lowered(), allow_metadata_loss=True))
    expected = np.zeros((4, 4), complex)
    vector = np.array([np.cos(0.45), np.sin(0.45)])
    expected[2:, 2:] = np.diag(vector**2)
    np.testing.assert_allclose(StatevectorDevice().density_matrix(restored), expected, atol=1e-13, rtol=0)
