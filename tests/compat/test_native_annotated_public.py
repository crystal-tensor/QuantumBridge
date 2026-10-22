# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Public calls only; no upstream implementation or test imports."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator

SPECS = [[], [("i",)], [("p", -3)], [("p", 0)], [("p", 2)], [("p", .5)],
    [("c", 1, 0)], [("c", 1, 1)], [("c", 2, 1)], [("c", 2, 2)],
    [("i",), ("c", 1, 1)], [("c", 1, 1), ("i",)], [("c", 1, 0), ("p", -2)],
    [("p", 3), ("c", 1, 0)], [("c", 1, 0), ("c", 1, 1)], [("c", 1, 1), ("c", 1, 0)],
    [("i",), ("i",)], [("p", 2), ("i",), ("c", 1, 0)],
    [("c", 2, 1), ("p", 2)], [("i",), ("p", 2), ("c", 1, 0), ("i",)]]


@pytest.mark.parametrize("spec", SPECS)
def test_twenty_public_ordered_modifier_scenarios(spec):
    pytest.importorskip("qiskit")
    from qiskit.circuit import AnnotatedOperation, InverseModifier, ControlModifier, PowerModifier
    from qiskit.circuit.library import RXGate
    native_types = {"i": qb.InverseModifier, "c": qb.ControlModifier, "p": qb.PowerModifier}
    public_types = {"i": InverseModifier, "c": ControlModifier, "p": PowerModifier}
    native = qb.AnnotatedOperation(qb.Gate("rx", 1, [.37]), [native_types[item[0]](*item[1:]) for item in spec])
    public = AnnotatedOperation(RXGate(.37), [public_types[item[0]](*item[1:]) for item in spec])
    assert public.name == native.name and public.num_qubits == native.num_qubits and public.num_clbits == 0
    assert [type(item).__name__ for item in public.modifiers] == [type(item).__name__ for item in native.modifiers]
    raw = public.to_matrix().data
    order = [int(f"{index:0{native.num_qubits}b}"[::-1], 2) for index in range(len(raw))]
    np.testing.assert_allclose(Operator(native).data, raw[np.ix_(order, order)], atol=3e-12)


@pytest.mark.parametrize("state", [0, 1])
def test_public_symbolic_controlled_phase_uuid_and_native_matrix(state):
    from uuid import UUID
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit
    from qiskit.circuit import Parameter, AnnotatedOperation, ControlModifier
    from qiskit.quantum_info import Operator as PublicOperator
    p = qb.Parameter("p")
    q = Parameter("p", uuid=UUID(p.uuid))
    body = qb.Circuit(1).rz(p, 0)
    body.global_phase = p/3
    public_body = QuantumCircuit(1)
    public_body.rz(q, 0)
    public_body.global_phase = q/3
    public = QuantumCircuit(2)
    public.append(AnnotatedOperation(public_body.to_gate(), ControlModifier(1, state)), [0, 1])
    native = qb.Circuit(2).append(qb.AnnotatedOperation(body.to_gate(), qb.ControlModifier(1, state)), [0, 1])
    assert public.parameters[0].uuid.hex == p.uuid.replace("-", "")
    actual = PublicOperator(public.assign_parameters({q: .4})).data
    np.testing.assert_allclose(Operator(native.bind({p: .4})).data, actual[np.ix_([0, 2, 1, 3], [0, 2, 1, 3])], atol=3e-13)


@pytest.mark.parametrize("mode", [True, False, None])
def test_public_generic_gate_control_flag_and_standard_return_class_boundaries(mode):
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit
    from qiskit.circuit import AnnotatedOperation
    from qiskit.circuit.library import RXGate, CXGate
    body = QuantumCircuit(1)
    body.rx(.3, 0)
    generic = body.to_gate()
    result = generic.control(1, annotated=mode)
    native = qb.Circuit(1).rx(.3, 0).to_gate().control(1, annotated=mode)
    assert isinstance(result, AnnotatedOperation) == isinstance(native, qb.AnnotatedOperation)
    # Public standard subclasses override generic Gate methods. Native generic
    # Gate/definition builders do not claim that distinct class-return ABI.
    assert not isinstance(RXGate(.3).inverse(annotated=mode), AnnotatedOperation)
    assert not isinstance(RXGate(.3).power(2, annotated=mode), AnnotatedOperation)
    assert isinstance(CXGate().control(1, annotated=False).num_qubits, int)
