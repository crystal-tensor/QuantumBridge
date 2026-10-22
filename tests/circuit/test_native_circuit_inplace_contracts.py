# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Real mutation, isolation, positional defaults and inverse execution."""

import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.core import GateCircuitLimits, gate_circuit_scope


@pytest.mark.parametrize("front", [False, True])
@pytest.mark.parametrize("inplace", [False, True])
def test_compose_public_positional_front_inplace_returns_and_real_order(front, inplace):
    source = qb.Circuit(1).rx(.2, 0)
    other = qb.Circuit(1).ry(.3, 0)
    before, operand = Operator(source).data, Operator(other).data
    result = source.compose(other, [0], [], front, inplace)
    assert (result is None) is inplace
    expected = before @ operand if front else operand @ before
    np.testing.assert_allclose(Operator(source if inplace else result).data, expected, atol=3e-13, rtol=0)
    if not inplace: np.testing.assert_array_equal(Operator(source).data, before)


@pytest.mark.parametrize("failure", ["wire", "parameter", "budget"])
def test_failed_inplace_compose_keeps_the_entire_original_valid(failure):
    p = qb.Parameter("p")
    source = qb.Circuit(2, name="source").rx(p, 0)
    before = source.to_ir().to_json()
    if failure == "wire":
        with pytest.raises(ValueError): source.compose(qb.Circuit(2).cx(0, 1), [0, 0], inplace=True)
    elif failure == "parameter":
        with pytest.raises(ValueError): source.compose(qb.Circuit(2).ry(qb.Parameter("p"), 1), inplace=True)
    else:
        with gate_circuit_scope(GateCircuitLimits(max_total_operations=1)), pytest.raises(MemoryError):
            source.compose(qb.Circuit(2).x(1), inplace=True)
    assert source.to_ir().to_json() == before


def test_inplace_binding_updates_instruction_and_control_block_without_fluent_return():
    p = qb.ParameterVector("p", 2)[1]
    inner = qb.Circuit(1).ry(2*p+p.sin(), 0).to_instruction().repeat(2)
    body = qb.Circuit(1, 1).append(inner, [0])
    source = qb.Circuit(1, 1).if_else(True, body)
    copied = source.assign_parameters({p: .3})
    assert source.parameters == (p,) and not copied.parameters
    assert source.assign_parameters({p: .4}, inplace=True) is None
    assert not source.parameters
    child = source.operations[0].metadata["control_node"].bodies[0]
    owner = child.operations[0].metadata["instruction_object"]
    assert owner.params == pytest.approx([.4])
    assert owner.definition.operations[0].params == pytest.approx([2*.4+np.sin(.4)])


@pytest.mark.parametrize("annotated", [False, True])
def test_circuit_inverse_has_real_deferred_gate_and_noncontiguous_full_complex_math(annotated):
    p = qb.Parameter("p")
    body = qb.Circuit(2, name="body").ry(p, 0).cx(0, 1)
    body.global_phase = 2*p
    repeated = body.to_instruction().repeat(2).assign_parameters({p: .3})
    source = qb.Circuit(3, name="source").append(qb.Circuit.from_instruction(repeated).to_gate(), [2, 0])
    inverse = source.inverse(annotated=annotated)
    assert inverse.name == "source_dg"
    if annotated: assert type(inverse.operations[0].metadata["annotated_operation"]) is qb.AnnotatedOperation
    c, s = np.cos(.15), np.sin(.15)
    rotation = np.array([[c, -s], [s, c]])
    cx = np.eye(4)[[0, 1, 3, 2]]
    local = np.exp(.6j)*cx @ np.kron(rotation, np.eye(2))
    local = (local @ local).conj().T
    expected = np.zeros((8, 8), dtype=complex)
    for column in range(8):
        bits = [(column >> (2-wire)) & 1 for wire in range(3)]
        for value in range(4):
            out = [value & 1, bits[1], value >> 1]
            row = out[0]*4+out[1]*2+out[2]
            expected[row, column] = local[value, bits[2]*2+bits[0]]
    np.testing.assert_allclose(Operator(inverse).data, expected, atol=6e-13, rtol=0)


def test_instruction_constructor_safe_alias_and_conflict_do_not_guess_old_definition_position():
    owner = qb.Instruction("i", 1, num_bits=1, label="display")
    assert owner.num_clbits == 1 and owner.label == "display"
    with pytest.raises(TypeError): qb.Instruction("i", 1, 0, [], num_bits=0)
    with pytest.raises(TypeError): qb.Instruction("i", 1, 0, [], qb.Circuit(1))


def test_zero_width_instruction_can_be_staged_without_claiming_zero_width_execution():
    owner = qb.Instruction("i", 0, 0, [])
    assert owner.num_qubits == 0 and owner.copy().num_qubits == 0
    with pytest.raises(qb.UnsupportedFeature): owner.repeat(2)
