# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual public SDK comparisons for native typed control instructions."""

import numpy as np
import pytest

from quantumbridge import QuantumCircuit, Parameter, StatevectorDevice
from quantumbridge.core import control_flow_operations as native

public_sdk = pytest.importorskip("qiskit")
public = pytest.importorskip("qiskit.circuit.controlflow")
PublicParameter = pytest.importorskip("qiskit.circuit").Parameter


def owner(kind, module, cls, parameter):
    body, alternate = cls(1, 1), cls(1, 1)
    symbol = parameter("angle")
    body.ry(symbol, 0)
    alternate.x(0)
    condition = (body.clbits[0], 1)
    args = {
        "IfElseOp": (condition, body, alternate),
        "ForLoopOp": (range(3), symbol, body),
        "WhileLoopOp": (condition, body),
        "SwitchCaseOp": (body.clbits[0], [(0, body), (module.CASE_DEFAULT, alternate)]),
        "BreakLoopOp": (1, 1),
        "ContinueLoopOp": (1, 1),
    }
    return getattr(module, kind)(*args[kind], label="branch"), symbol


def describe(operation, module):
    return (type(operation).__name__, operation.name, operation.base_class.__name__,
            operation.num_qubits, operation.num_clbits, operation.label,
            isinstance(operation, module.ControlFlowOp), operation.definition is None,
            [(block.num_qubits, block.num_clbits, dict(block.count_ops()))
             for block in getattr(operation, "blocks", ())],
            len(operation.params), hasattr(operation, "blocks"))


@pytest.mark.parametrize("kind", ["IfElseOp", "ForLoopOp", "WhileLoopOp", "SwitchCaseOp", "BreakLoopOp", "ContinueLoopOp"])
def test_real_public_owner_types_params_blocks_and_copy(kind):
    expected, pp = owner(kind, public, public_sdk.QuantumCircuit, PublicParameter)
    got, np_ = owner(kind, native, QuantumCircuit, Parameter)
    assert describe(got, native) == describe(expected, public)
    for operation, symbol in ((expected, pp), (got, np_)):
        assert operation.params is operation.params
        copied = operation.copy()
        assert type(copied) is type(operation) and copied is not operation
        for original, clone in zip(getattr(operation, "blocks", ()), getattr(copied, "blocks", ())):
            assert original is not clone
            assert list(clone.parameters)[0].uuid == symbol.uuid if clone.parameters else True
        if kind == "ForLoopOp":
            assert type(operation.params[0]) is range
            operation.params[0] = range(2)
            assert tuple(operation.params[0]) == (0, 1)
        if kind == "IfElseOp":
            replacement = operation.blocks[1]
            operation.params[0] = replacement
            assert operation.blocks[0] is replacement


def built(cls, kind):
    circuit = cls(4, 3)
    if kind == "if":
        with circuit.if_test((circuit.clbits[1], 1)) as otherwise:
            circuit.x(2)
            circuit.x(0)
        with otherwise:
            circuit.z(3)
    elif kind == "while":
        with circuit.while_loop((circuit.clbits[1], 1)):
            circuit.x(2)
            circuit.measure(2, 2)
    elif kind == "for":
        with circuit.for_loop(range(3)):
            circuit.x(2)
            circuit.x(0)
    elif kind == "switch":
        with circuit.switch(circuit.clbits[1]) as case:
            with case(0):
                circuit.x(2)
            with case(case.DEFAULT):
                circuit.z(3)
    else:
        with circuit.for_loop(range(3)):
            with circuit.if_test((circuit.clbits[1], 0)):
                circuit.break_loop()
            circuit.x(2)
    return circuit


def contexts(circuit):
    return [(type(item.operation).__name__ if isinstance(item.operation, (native.ControlFlowOp,
             native.BreakLoopOp, native.ContinueLoopOp, public.ControlFlowOp,
             public.BreakLoopOp, public.ContinueLoopOp)) else item.operation.name, item.operation.name,
             [circuit.find_bit(bit).index for bit in item.qubits],
             [circuit.find_bit(bit).index for bit in item.clbits],
             [contexts(block) for block in getattr(item.operation, "blocks", ())])
            for item in circuit.data]


@pytest.mark.parametrize("kind", ["if", "while", "for", "switch", "nested_jump"])
def test_actual_builder_resource_order_widths_and_nested_contexts(kind):
    got, expected = built(QuantumCircuit, kind), built(public_sdk.QuantumCircuit, kind)
    if kind != "switch":
        assert contexts(got) == contexts(expected)
        return
    # Switch builds a resource union, whose iteration order is not a stable
    # SDK contract. Compare every case instruction on actual parent wires.
    def cases(circuit):
        context = circuit.data[0]
        assert (context.operation.num_qubits, context.operation.num_clbits) == (2, 1)
        assert {circuit.find_bit(bit).index for bit in context.qubits} == {2, 3}
        assert [circuit.find_bit(bit).index for bit in context.clbits] == [1]
        return [[(item.operation.name, [circuit.find_bit(context.qubits[block.find_bit(bit).index]).index
                  for bit in item.qubits]) for item in block.data] for block in context.operation.blocks]
    assert cases(got) == cases(expected) == [[("x", [2])], [("z", [3])]]


def test_actual_conditional_compose_maps_public_condition_and_real_execution():
    for cls in (public_sdk.QuantumCircuit, QuantumCircuit):
        source = cls(2, 2)
        with source.if_test((source.clbits[0], 1)):
            source.x(1)
        destination = cls(3, 3)
        destination.x(2)
        destination.measure(2, 1)
        destination.compose(source, [2, 0], [1, 2], inplace=True)
        conditional = destination.data[-1].operation
        assert conditional.condition == (destination.clbits[1], 1)
        if cls is QuantumCircuit:
            destination.measure(0, 2)
            assert StatevectorDevice().run_shots(destination, shots=4).counts() == {"011": 4}
            np.testing.assert_allclose(StatevectorDevice().density_matrix(destination)[5, 5], 1, atol=1e-14)


@pytest.mark.parametrize("kind", ["IfElseOp", "ForLoopOp", "WhileLoopOp", "SwitchCaseOp"])
def test_public_owner_replacement_width_failure_preserves_params(kind):
    for module, cls, parameter in ((public, public_sdk.QuantumCircuit, PublicParameter),
                                    (native, QuantumCircuit, Parameter)):
        operation, _ = owner(kind, module, cls, parameter)
        previous = operation.params
        values = list(previous)
        position = 2 if kind == "ForLoopOp" else 0
        values[position] = cls(2, 1)
        if kind == "SwitchCaseOp":
            operation.params = values
            assert operation.blocks[0].num_qubits == 2 and operation.num_qubits == 1
        else:
            with pytest.raises(Exception) as error:
                operation.params = values
            assert type(error.value).__name__ == "CircuitError"
            assert operation.params is previous
