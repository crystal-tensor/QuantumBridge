# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Real public control owners, live blocks and existing native execution."""

import numpy as np
import pytest

from quantumbridge import Circuit, Clbit, Parameter, QuantumCircuit, StatevectorDevice
from quantumbridge.core.control_flow_operations import (ControlFlowOp, IfElseOp, ForLoopOp,
    WhileLoopOp, SwitchCaseOp, BreakLoopOp, ContinueLoopOp, CASE_DEFAULT)
from quantumbridge.core.errors import CircuitError
from quantumbridge.core.operations import Instruction


def test_actual_control_types_blocks_params_copy_and_parameter_identity():
    body = QuantumCircuit(1, 1)
    angle = Parameter("angle")
    body.ry(angle, 0)
    conditional = IfElseOp((body.clbits[0], 1), body)
    assert isinstance(conditional, ControlFlowOp) and isinstance(conditional, Instruction)
    assert conditional.base_class is IfElseOp and conditional.definition is None
    assert conditional.blocks == (body,) and conditional.params == [body, None]
    assert conditional.params is conditional.params
    copied = conditional.copy()
    assert type(copied) is IfElseOp and copied.blocks[0] is not body
    assert copied.blocks[0].parameters[0].uuid == angle.uuid
    assert not isinstance(BreakLoopOp(1, 1), ControlFlowOp)
    assert not isinstance(ContinueLoopOp(1, 1), ControlFlowOp)
    assert not hasattr(BreakLoopOp(1, 1), "blocks")
    with pytest.raises(CircuitError):
        IfElseOp((body.clbits[0], 1), body, QuantumCircuit(2, 1))
    with pytest.raises(CircuitError):
        ForLoopOp(range(2), 0.3, body)


def test_circuit_data_control_owner_and_body_mutations_reach_real_execution():
    circuit = QuantumCircuit(2, 2)
    circuit.x(0)
    circuit.measure(0, 0)
    with circuit.if_test((circuit.clbits[0], 1)):
        circuit.x(1)
    circuit.measure(1, 1)
    owner = circuit.data[2].operation
    assert type(owner) is IfElseOp and owner is circuit.data[2].operation
    assert owner.condition == (circuit.clbits[0], 1)
    assert StatevectorDevice().run_shots(circuit, shots=3).counts() == {"11": 3}
    owner.blocks[0].x(owner.blocks[0].qubits[0])
    assert StatevectorDevice().run_shots(circuit, shots=3).counts() == {"10": 3}
    owner.condition = (circuit.clbits[0], 0)
    replacement = owner.blocks[0].copy_empty_like()
    replacement.x(0)
    owner.params[0] = replacement
    assert StatevectorDevice().run_shots(circuit, shots=3).counts() == {"10": 3}


def test_builder_minimal_resources_follow_first_use_and_union_both_branches():
    circuit = QuantumCircuit(4, 3)
    with circuit.if_test((circuit.clbits[1], 1)) as otherwise:
        circuit.x(2)
        circuit.x(0)
    with otherwise:
        circuit.z(3)
    context = circuit.data[0]
    assert type(context.operation) is IfElseOp
    assert [circuit.find_bit(bit).index for bit in context.qubits] == [2, 0, 3]
    assert [circuit.find_bit(bit).index for bit in context.clbits] == [1]
    assert [(body.num_qubits, body.num_clbits) for body in context.operation.blocks] == [(3, 1), (3, 1)]


def test_explicit_control_owners_append_bind_copy_and_compose_keep_semantics():
    body = QuantumCircuit(1, 1)
    angle, index = Parameter("angle"), Parameter("i")
    body.ry(angle+index*0.2, 0)
    loop = ForLoopOp(range(3), index, body)
    circuit = QuantumCircuit(3, 2)
    circuit.append(loop, [2], [1], copy=False)
    assert circuit.data[0].operation is loop
    assert tuple(circuit.parameters) == (angle,)
    bound = circuit.assign_parameters({angle: 0.1})
    assert type(bound.data[0].operation) is ForLoopOp
    expected = np.array([np.cos(0.45), np.sin(0.45)])
    np.testing.assert_allclose(StatevectorDevice().density_matrix(bound)[np.ix_([0, 1], [0, 1])], np.outer(expected, expected), atol=1e-14)
    copied = bound.copy()
    assert copied.data[0].operation is not bound.data[0].operation
    loop_bound = copied.data[0].operation
    loop_bound.params[0] = range(2)
    np.testing.assert_allclose(StatevectorDevice().density_matrix(copied)[0, 0], np.cos(0.2)**2, atol=1e-14)
    destination = QuantumCircuit(4, 3)
    destination.compose(bound, qubits=[3, 0, 1], clbits=[2, 0], inplace=True)
    assert type(destination.data[0].operation) is ForLoopOp
    assert not destination.parameters
    expected_state = np.zeros(16)
    expected_state[[0, 4]] = expected
    np.testing.assert_allclose(StatevectorDevice().density_matrix(destination), np.outer(expected_state, expected_state), atol=1e-14)


def test_switch_and_while_owners_have_real_case_and_condition_objects():
    circuit = QuantumCircuit(1, 1)
    body, fallback = QuantumCircuit(1, 1), QuantumCircuit(1, 1)
    body.x(0)
    switch = SwitchCaseOp(circuit.clbits[0], [(0, body), (CASE_DEFAULT, fallback)])
    assert switch.blocks == (body, fallback)
    assert switch.cases()[0] is body and switch.cases()[CASE_DEFAULT] is fallback
    assert list(switch.cases_specifier()) == [((0,), body), ((CASE_DEFAULT,), fallback)]
    circuit.append(switch, [0], [0])
    circuit.measure(0, 0)
    assert StatevectorDevice().run_shots(circuit, shots=2).counts() == {"1": 2}
    assert WhileLoopOp((Clbit(), 0), QuantumCircuit(1)).definition is None
    legacy = Circuit(1, 1).if_else(True, Circuit(1, 1).x(0)).measure(0, 0)
    assert StatevectorDevice().run_shots(legacy, shots=2).counts() == {"1": 2}


def test_invalid_control_append_and_live_cycle_are_rejected_before_mutation():
    circuit, body = QuantumCircuit(2, 1), QuantumCircuit(1)
    foreign = IfElseOp((Clbit(), 1), body)
    with pytest.raises(CircuitError, match="foreign"):
        circuit.append(foreign, [0], [])
    assert len(circuit.data) == 0
    owner = ForLoopOp(range(2), None, body)
    circuit.append(owner, [1], [], copy=False)
    owner.params[2].operations.append(circuit.operations[0])
    with pytest.raises(CircuitError, match="Cyclic"):
        _ = circuit.parameters


def test_escaped_true_and_false_handles_still_mutate_the_actual_blocks():
    circuit = QuantumCircuit(3, 2)
    with circuit.if_test((circuit.clbits[1], 0)) as otherwise:
        true_handle = circuit.rx(0.2, 2)
    owner = circuit.data[0].operation
    true_body = owner.blocks[0]
    with otherwise:
        false_handle = circuit.rx(0.7, 0)
    assert circuit.data[0].operation is owner and owner.blocks[0] is true_body
    true_handle.inverse()
    false_handle.inverse()
    expected = np.zeros(8, dtype=complex)
    expected[[0, 1]] = [np.cos(0.1), 1j*np.sin(0.1)]
    np.testing.assert_allclose(StatevectorDevice().density_matrix(circuit),
                               np.outer(expected, expected.conj()), atol=1e-14)


def test_legacy_append_and_public_direct_compose_keep_loop_execution():
    body = QuantumCircuit(1)
    index = Parameter("index")
    body.ry(0.2*index, 0)
    owner = ForLoopOp(range(3), index, body)
    legacy = Circuit(3).append(owner, [2])
    public = QuantumCircuit(3)
    public.compose(owner, qubits=[2], clbits=[], inplace=True)
    assert type(public.data[0].operation) is ForLoopOp
    expected = np.array([np.cos(0.3), np.sin(0.3)])
    for circuit in (legacy, public):
        np.testing.assert_allclose(StatevectorDevice().density_matrix(circuit)[np.ix_([0, 1], [0, 1])],
                                   np.outer(expected, expected), atol=1e-14)


def test_control_definition_work_admission_is_atomic_before_ir_encoding():
    from quantumbridge.core import GateCircuitLimits, gate_circuit_scope
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
    body = QuantumCircuit(1)
    for _ in range(4):
        body.x(0)
    owner, circuit = ForLoopOp(range(2), None, body), QuantumCircuit(1)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger), gate_circuit_scope(GateCircuitLimits(max_total_operations=3)), pytest.raises(MemoryError):
        circuit.append(owner, [0], [])
    assert len(circuit.data) == 0 and ledger.receipt()["consumed_shots"] == 0


def test_switch_live_setter_invalid_width_refuses_before_first_shot():
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
    circuit, body = QuantumCircuit(1, 1), QuantumCircuit(1, 1)
    owner = SwitchCaseOp(circuit.clbits[0], [(0, body)])
    circuit.append(owner, [0], [0], copy=False)
    owner.params = [QuantumCircuit(2, 1)]
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger), pytest.raises(CircuitError):
        StatevectorDevice().run_shots(circuit, shots=2)
    assert ledger.receipt()["consumed_shots"] == 0


def test_compose_rewrites_captured_variable_identity_in_live_blocks():
    from quantumbridge.core import classical as expr
    source = QuantumCircuit(1, 1)
    variable = source.add_var("flag", True)
    with source.if_test(variable):
        source.x(0)
    replacement = expr.Var.new("replacement", expr.Bool())
    target = QuantumCircuit(2, 2)
    target.compose(source, [1], [1], var_remap={variable: replacement}, inplace=True)
    owner = target.data[1].operation
    assert owner.condition.value[0] == replacement.value[0]
    assert list(owner.blocks[0].iter_captured_vars())[0].value[0] == replacement.value[0]
    np.testing.assert_allclose(StatevectorDevice().density_matrix(target)[1, 1], 1, atol=1e-14)
