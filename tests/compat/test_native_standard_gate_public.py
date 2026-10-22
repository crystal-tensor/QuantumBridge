# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Literal public object calls, separate from native mathematical checks."""

import numpy as np
import pytest
import quantumbridge as qb
import quantumbridge.circuit_library as library
from quantumbridge.information import Operator


@pytest.mark.parametrize("name,args", [("RXGate", (.37,)), ("RYGate", (.37,)),
    ("RZGate", (.37,)), ("PhaseGate", (.37,)), ("UGate", (.37, .19, -.23)),
    ("HGate", ()), ("XGate", ()), ("YGate", ()), ("ZGate", ()),
    ("CXGate", ()), ("CZGate", ()), ("SwapGate", ())])
def test_twelve_public_standard_constructor_base_name_mutability_and_quantum_execution(name, args):
    pytest.importorskip("qiskit")
    from qiskit.circuit import library as public
    from qiskit.quantum_info import Operator as PublicOperator
    left, right = getattr(library, name)(*args), getattr(public, name)(*args)
    assert left.base_class.__name__ == right.base_class.__name__
    assert left.name == right.name
    assert (left.num_qubits, left.num_clbits, left.mutable, left.label) == (right.num_qubits, right.num_clbits, right.mutable, right.label)
    np.testing.assert_allclose(Operator(left).data, PublicOperator(right).reverse_qargs().data, atol=3e-13, rtol=0)


@pytest.mark.parametrize("name", ["generic", "RXGate", "RYGate", "RZGate"])
@pytest.mark.parametrize("method", ["control", "inverse", "power"])
@pytest.mark.parametrize("mode", ["omitted", None, False, True])
def test_forty_eight_actual_default_and_explicit_public_method_contracts(name, method, mode):
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit
    from qiskit.circuit import library as public
    from qiskit.quantum_info import Operator as PublicOperator
    if name == "generic":
        body = qb.Circuit(1, name="comparison").rx(.37, 0)
        body.global_phase = .13
        upstream = QuantumCircuit(1, name="comparison")
        upstream.rx(.37, 0)
        upstream.global_phase = .13
        left, right = body.to_gate(), upstream.to_gate()
    else: left, right = getattr(library, name)(.37), getattr(public, name)(.37)
    kwargs = {} if mode == "omitted" else {"annotated": mode}
    args = (1,) if method == "control" else (2,) if method == "power" else ()
    left, right = getattr(left, method)(*args, **kwargs), getattr(right, method)(*args, **kwargs)
    assert type(left).__name__ == type(right).__name__
    assert left.name == right.name
    assert getattr(left, "label", None) == getattr(right, "label", None)
    assert left.num_qubits == right.num_qubits and left.num_clbits == right.num_clbits
    np.testing.assert_allclose(Operator(left).data, PublicOperator(right).reverse_qargs().data, atol=5e-13, rtol=0)


@pytest.mark.parametrize("name", ["RXGate", "RYGate", "RZGate", "PhaseGate"])
@pytest.mark.parametrize("value", [1j, complex(.2, 0), np.complex128(.2)])
def test_standard_invalid_angle_has_the_same_exception_class_name_and_constructor_stage(name, value):
    pytest.importorskip("qiskit")
    from qiskit.circuit import library as public
    errors = []
    for module in (library, public):
        with pytest.raises(Exception) as caught: getattr(module, name)(value)
        errors.append(type(caught.value).__name__)
    assert errors == ["CircuitError", "CircuitError"]


@pytest.mark.parametrize("name,args", [("PhaseGate", (.37,)), ("UGate", (.37, .19, -.23)),
    ("HGate", ()), ("XGate", ()), ("YGate", ()), ("ZGate", ()),
    ("CXGate", ()), ("CZGate", ()), ("SwapGate", ())])
@pytest.mark.parametrize("method", ["control", "inverse", "power"])
@pytest.mark.parametrize("mode", ["omitted", None, False, True])
def test_remaining_108_actual_standard_method_returns_and_mutability(name, args, method, mode):
    pytest.importorskip("qiskit")
    from qiskit.circuit import library as public
    from qiskit.quantum_info import Operator as PublicOperator
    left, right = getattr(library, name)(*args), getattr(public, name)(*args)
    kwargs = {} if mode == "omitted" else {"annotated": mode}
    call_args = (1,) if method == "control" else (2,) if method == "power" else ()
    left, right = getattr(left, method)(*call_args, **kwargs), getattr(right, method)(*call_args, **kwargs)
    # Public private singleton subclasses are not imitated: safe owned native
    # objects expose the actual public base class and frozen/mutable contract.
    assert getattr(left, "base_class", type(left)).__name__ == getattr(right, "base_class", type(right)).__name__
    assert getattr(left, "mutable", None) == getattr(right, "mutable", None)
    assert left.name == right.name
    np.testing.assert_allclose(Operator(left).data, PublicOperator(right).reverse_qargs().data, atol=5e-13, rtol=0)


def test_public_instruction_label_name_and_copy_are_real_object_fields():
    pytest.importorskip("qiskit")
    from qiskit.circuit import Instruction
    for kind in (qb.Instruction, Instruction):
        owner = kind("payload", 1, 0, [.3], label="first")
        copied = owner.copy(name="second")
        copied.label = "changed"
        assert owner.name == "payload" and owner.label == "first"
        assert copied.name == "second" and copied.label == "changed"
        assert copied.base_class is kind and copied.mutable


def test_named_frozen_gate_copy_becomes_owned_mutable_without_changing_original():
    pytest.importorskip("qiskit")
    from qiskit.circuit.library import HGate
    for kind in (library.HGate, HGate):
        owner = kind()
        copied = owner.copy(name="changed")
        assert copied.mutable and copied.name == "changed"
        assert not owner.mutable and owner.name == "h"


def test_circuit_instruction_label_does_not_replace_its_public_name():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit
    for kind in (qb.Circuit, QuantumCircuit):
        result = kind(1, name="block").to_instruction(label="display")
        assert result.name == "block" and result.label == "display"
