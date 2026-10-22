# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual public Instruction and Circuit contracts, not Gate-inferred rules."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.errors import CircuitError
from quantumbridge.information import Operator


def defined():
    return qb.Circuit(1, name="defined").rx(qb.Parameter("p"), 0).to_instruction(label="display")


def test_public_fifth_positional_argument_is_label_not_executable_definition():
    owner = qb.Instruction("i", 1, 0, [], "display")
    assert owner.label == "display" and owner.definition is None


def test_unitary_instruction_default_inverse_has_real_gate_return_type():
    assert type(defined().inverse()) is qb.Gate


def test_unitary_instruction_explicit_annotated_inverse_is_really_deferred():
    owner = defined()
    result = owner.inverse(annotated=True)
    assert type(result) is qb.AnnotatedOperation and result.base_op is owner


def test_generic_instruction_repeat_is_real_with_owned_definition():
    owner = qb.Instruction("opaque", 1, 0, [.3])
    result = owner.repeat(2)
    assert type(result) is qb.Instruction and len(result.definition.operations) == 2


@pytest.mark.parametrize("n", [0, -1, 1.5])
def test_instruction_repeat_invalid_count_raises_circuit_error(n):
    with pytest.raises(CircuitError):
        qb.Instruction("opaque", 1, 0, [.3]).repeat(n)


def test_public_compose_inplace_returns_none_and_modifies_owner():
    source = qb.Circuit(1)
    result = source.compose(qb.Circuit(1).x(0), inplace=True)
    assert result is None and len(source.operations) == 1
    np.testing.assert_allclose(Operator(source).data, [[0, 1], [1, 0]], atol=2e-13, rtol=0)


def test_public_assign_parameters_inplace_returns_none_and_binds_owner():
    p = qb.Parameter("p")
    source = qb.Circuit(1).rx(p, 0)
    assert source.assign_parameters({p: .3}, inplace=True) is None
    assert not source.parameters and source.operations[0].params == (.3,)


def test_public_circuit_inverse_return_name_records_the_adjoint():
    source = qb.Circuit(1, name="source").rx(.3, 0)
    result = source.inverse()
    assert result.name == "source_dg" and source.name == "source"


def test_keyword_classical_width_and_label_copy_already_work():
    owner = qb.Instruction("opaque", 1, num_clbits=1, params=[], label="display")
    copied = owner.copy(name="other")
    assert copied.label == "display" and copied.num_clbits == 1
    assert owner.name == "opaque" and copied.name == "other"


def test_existing_native_instruction_inverse_still_has_correct_quantum_math():
    owner = qb.Circuit(1).rx(.3, 0).to_instruction()
    np.testing.assert_allclose(Operator(owner).data @ Operator(owner.inverse()).data,
        np.eye(2), atol=3e-13, rtol=0)
