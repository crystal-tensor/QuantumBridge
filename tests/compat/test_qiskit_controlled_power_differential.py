# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Observed public objects and coherent matrices, with explicit upstream defects."""

import cmath

import numpy as np
import pytest

import quantumbridge as qb
import quantumbridge.circuit_library as native
from quantumbridge.information import Operator


@pytest.mark.parametrize("name", ["CRXGate", "CRYGate", "CRZGate"])
@pytest.mark.parametrize("angle", [.31, 7.3, -9.1])
@pytest.mark.parametrize("state", [0, 1])
@pytest.mark.parametrize("power", [-1, .5, -.3, 2])
@pytest.mark.parametrize("annotated", [False, True])
def test_actual_controlled_power_return_class_and_complex_matrix(name, angle, state, power, annotated, record_property):
    pytest.importorskip("qiskit")
    from qiskit.circuit import library as public
    from qiskit.quantum_info import Operator as PublicOperator
    source = getattr(native, name)(angle, label="source", ctrl_state=state)
    upstream = getattr(public, name)(angle, label="source", ctrl_state=state)
    result = source.power(power, annotated=annotated)
    expected = upstream.power(power, annotated=annotated)
    observed_class = expected.base_class.__name__ if hasattr(expected, "base_class") else type(expected).__name__
    assert type(result).__name__ == observed_class
    if not annotated:
        assert result.label == expected.label
        assert result.mutable == expected.mutable
    np.testing.assert_allclose(Operator(result).data, PublicOperator(expected).reverse_qargs().data, atol=3e-12, rtol=0)
    record_property("classification", "IMPLEMENTED_AND_TESTED")


@pytest.mark.parametrize("name", ["CRXGate", "CRYGate", "CRZGate"])
@pytest.mark.parametrize("power", [2, .5])
def test_symbolic_controlled_power_observed_exception_stage_and_deferred_binding(name, power):
    qiskit = pytest.importorskip("qiskit")
    from qiskit.circuit import Parameter, library as public
    from qiskit.quantum_info import Operator as PublicOperator
    left, right = qb.Parameter("angle"), Parameter("angle")
    source, upstream = getattr(native, name)(left, ctrl_state=0), getattr(public, name)(right, ctrl_state=0)
    for gate in (source, upstream):
        with pytest.raises(TypeError):
            gate.power(power, annotated=False)
    circuit, reference = qb.QuantumCircuit(2), qiskit.QuantumCircuit(2)
    circuit.append(source.power(power, annotated=True), [0, 1])
    reference.append(upstream.power(power, annotated=True), [0, 1])
    actual = circuit.assign_parameters({left: 7.3})
    expected = reference.assign_parameters({right: 7.3})
    np.testing.assert_allclose(Operator(actual).data, PublicOperator(expected).reverse_qargs().data, atol=3e-12, rtol=0)


@pytest.mark.parametrize("power", [-1, .5, 2])
@pytest.mark.parametrize("annotated", [False, True])
def test_observed_public_controlled_phase_power_loses_open_control_but_native_keeps_the_correct_block(power, annotated, record_property):
    pytest.importorskip("qiskit")
    from qiskit.circuit.library import CPhaseGate
    from qiskit.quantum_info import Operator as PublicOperator
    source = native.CPhaseGate(.31, ctrl_state=0)
    result = source.power(power, annotated=annotated)
    public = CPhaseGate(.31, ctrl_state=0).power(power, annotated=annotated)
    assert type(result).__name__ == public.base_class.__name__ == "CPhaseGate"
    assert result.ctrl_state == 0 and public.ctrl_state == 1
    expected_open = np.diag([1., cmath.exp(.31j*power), 1., 1.])
    expected_closed = np.diag([1., 1., 1., cmath.exp(.31j*power)])
    np.testing.assert_allclose(Operator(result).data, expected_open, atol=5e-13, rtol=0)
    np.testing.assert_allclose(PublicOperator(public).reverse_qargs().data, expected_closed, atol=5e-13, rtol=0)
    record_property("classification", "OBSERVED_UPSTREAM_DEFECT; native intentionally preserves open-control semantics, not bug-for-bug parity")


@pytest.mark.parametrize("name", ["XGate", "YGate", "ZGate", "HGate", "IGate", "SwapGate"])
def test_fixed_inverse_observed_label_mutability_and_specialized_class(name):
    pytest.importorskip("qiskit")
    from qiskit.circuit import library as public
    result = getattr(native, name)(label="source").inverse(annotated=True)
    reference = getattr(public, name)(label="source").inverse(annotated=True)
    assert (result.base_class.__name__, result.label, result.mutable) == (reference.base_class.__name__, reference.label, reference.mutable)


@pytest.mark.parametrize("annotated", [False, True])
def test_unitary_inverse_observed_specialized_class_for_each_annotation_flag(annotated):
    pytest.importorskip("qiskit")
    from qiskit.circuit.library import UnitaryGate
    result = native.UnitaryGate(np.diag([1., 1j]), label="source").inverse(annotated=annotated)
    reference = UnitaryGate(np.diag([1., 1j]), label="source").inverse(annotated=annotated)
    assert type(result).__name__ == reference.base_class.__name__ == "UnitaryGate"
    np.testing.assert_allclose(result.to_matrix(), reference.to_matrix(), atol=5e-13, rtol=0)
