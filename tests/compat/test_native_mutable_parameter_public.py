# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual public parameter calls, with explicit return/error ABI boundaries."""

from uuid import UUID

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator


@pytest.mark.parametrize("axis", ["rx", "ry", "rz"])
@pytest.mark.parametrize("action", ["index", "slice", "replace", "copy", "symbolic", "annotation"])
def test_eighteen_actual_parameter_mutation_quantum_execution_scenarios(axis, action):
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit
    from qiskit.circuit import Parameter, AnnotatedOperation, InverseModifier
    from qiskit.circuit.library import RXGate, RYGate, RZGate
    from qiskit.quantum_info import Operator as PublicOperator
    public = {"rx": RXGate, "ry": RYGate, "rz": RZGate}[axis](.3)
    native = qb.Gate(axis, 1, [.3])
    original_native, original_public = native, public
    if action == "copy": native, public = native.copy(), public.copy()
    elif action == "annotation":
        native, public = qb.AnnotatedOperation(native, qb.InverseModifier()), AnnotatedOperation(public, InverseModifier())
    if action == "symbolic":
        p = qb.Parameter("p")
        q = Parameter("p", uuid=UUID(p.uuid))
        native.params[0], public.params[0] = 2*p+p.sin(), 2*q+q.sin()
        left, right = qb.Circuit(1).append(native, [0]), QuantumCircuit(1)
        right.append(public, [0])
        assert left.parameters[0].uuid.replace("-", "") == right.parameters[0].uuid.hex
        native, public = left.assign_parameters({p: .4}), right.assign_parameters({q: .4})
    elif action == "replace": native.params, public.params = [.5], [.5]
    elif action == "slice": native.params[:], public.params[:] = [.5], [.5]
    else: native.params[0], public.params[0] = .5, .5
    np.testing.assert_allclose(Operator(native).data, PublicOperator(public).data, atol=2e-13, rtol=0)
    if action == "copy": assert original_native.params == original_public.params == [.3]
    # Native generic Gate is not the specialized public RX/RY/RZ class.
    # These tests prove parameter/math behavior, not dedicated return-class ABI.


@pytest.mark.parametrize("value", [1, .3, True, np.int64(2), np.float32(.3), np.float64(.4)])
def test_actual_gate_validation_numeric_values_and_scalar_return_types(value):
    pytest.importorskip("qiskit")
    from qiskit.circuit import Gate
    native, public = qb.Gate("g", 1).validate_parameter(value), Gate("g", 1, []).validate_parameter(value)
    assert type(native) is type(public) and native == public


@pytest.mark.parametrize("value", [1j, "payload", [1, 2], np.array([1., 2.])])
def test_actual_generic_instruction_validate_preserves_payload_identity(value):
    pytest.importorskip("qiskit")
    from qiskit.circuit import Instruction
    assert qb.Instruction("g", 1).validate_parameter(value) is value
    assert Instruction("g", 1, 0, []).validate_parameter(value) is value


@pytest.mark.parametrize("value", [1j, complex(.3, 0), np.complex128(.3), None])
def test_invalid_parameter_rejection_preserves_values_but_error_class_abi_differs(value):
    pytest.importorskip("qiskit")
    from qiskit.circuit import Gate, CircuitError
    native, public = qb.Gate("g", 1, [.3]), Gate("g", 1, [.3])
    with pytest.raises((TypeError, ValueError)): native.validate_parameter(value)
    with pytest.raises(CircuitError): public.validate_parameter(value)
    assert native.params == public.params == [.3]


@pytest.mark.xfail(strict=True, reason="Observed public generic Gate indexed params mutation leaves its definition unbound; native must retain stronger actual execution semantics")
def test_public_generic_gate_direct_index_mutation_rebinds_its_actual_definition():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit
    from qiskit.circuit import Parameter
    from qiskit.quantum_info import Operator as PublicOperator
    p = Parameter("p")
    body = QuantumCircuit(1)
    body.rx(p, 0)
    gate = body.to_gate()
    gate.params[0] = .5
    expected = np.array([[np.cos(.25), -1j*np.sin(.25)], [-1j*np.sin(.25), np.cos(.25)]])
    np.testing.assert_allclose(PublicOperator(gate).data, expected, atol=1e-13)


def test_public_partial_assignment_corruption_is_not_copied_by_native_atomic_updates():
    pytest.importorskip("qiskit")
    from qiskit.circuit import Gate, CircuitError
    native, public = qb.Gate("g", 1, [.3]), Gate("g", 1, [.3])
    with pytest.raises((TypeError, ValueError)): native.params = [.2, 1j]
    with pytest.raises(CircuitError): public.params = [.2, 1j]
    assert native.params == [.3]
    assert public.params == [.2], "Retain the actual target-version behavior, not an imagined atomic public setter."
