# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual public construction/error boundaries and independent trajectory math."""

import numpy as np
import pytest

from quantumbridge import QuantumCircuit, Parameter, StatevectorDevice, StatevectorSampler, StatevectorEstimator
from quantumbridge.core.errors import CircuitError

PublicCircuit = pytest.importorskip("qiskit").QuantumCircuit
PublicParameter = pytest.importorskip("qiskit.circuit").Parameter
PublicSampler = pytest.importorskip("qiskit.primitives").StatevectorSampler
PublicEstimator = pytest.importorskip("qiskit.primitives").StatevectorEstimator


def feedforward(cls, initial):
    circuit = cls(2, 2)
    if initial == "h":
        circuit.h(0)
    elif initial == "x":
        circuit.x(0)
    circuit.measure(0, 0)
    with circuit.if_test((circuit.clbits[0], 1)) as otherwise:
        circuit.x(1)
    with otherwise:
        circuit.z(1)
    circuit.measure(1, 1)
    return circuit


@pytest.mark.parametrize("initial", ["h", "x", "id"])
def test_public_valid_conditional_construction_and_native_exact_ensemble(initial):
    public, native = feedforward(PublicCircuit, initial), feedforward(QuantumCircuit, initial)
    assert public.data[-2].operation.name == "if_else"
    node = next(op.metadata["control_node"] for op in native.operations if "control_node" in op.metadata)
    assert node.kind == "if" and len(node.bodies) == 2
    expected = np.diag([0.5, 0, 0, 0.5]) if initial == "h" else np.diag([0, 0, 0, 1] if initial == "x" else [1, 0, 0, 0])
    np.testing.assert_allclose(StatevectorDevice().density_matrix(native), expected, atol=1e-14)
    shots = StatevectorDevice().run_shots(native, shots=128, seed=17).counts()
    assert sum(shots.values()) == 128 and set(shots) <= {"00", "11"}


@pytest.mark.parametrize("primitive", ["sampler", "estimator"])
def test_public_reference_dynamic_refusal_is_separate_from_native_device_execution(primitive):
    public, native = feedforward(PublicCircuit, "h"), feedforward(QuantumCircuit, "h")
    public_primitive = PublicSampler() if primitive == "sampler" else PublicEstimator()
    native_primitive = StatevectorSampler() if primitive == "sampler" else StatevectorEstimator()
    with pytest.raises(Exception) as reference:
        public_primitive.run([public] if primitive == "sampler" else [(public, "ZZ")]).result()
    with pytest.raises(Exception) as actual:
        native_primitive.run([native] if primitive == "sampler" else [(native, "ZZ")]).result()
    assert type(actual.value).__name__ == type(reference.value).__name__ == "QiskitError"


@pytest.mark.parametrize("explicit", [False, True])
def test_for_context_actual_parameter_uuid_and_bound_rotation_math(explicit):
    public, native = PublicCircuit(1), QuantumCircuit(1)
    pp, np_ = PublicParameter("index"), Parameter("index")
    with public.for_loop(range(3), pp if explicit else None) as p:
        public.ry(p*0.2, 0)
    with native.for_loop(range(3), np_ if explicit else None) as parameter:
        native.ry(parameter*0.2, 0)
    assert public.data[0].operation.name == "for_loop" and not public.parameters
    node = native.operations[0].metadata["control_node"]
    assert not native.parameters and node.data["parameter"] is parameter
    if explicit:
        assert node.data["parameter"].uuid == np_.uuid
    expected = np.array([np.cos(0.3), np.sin(0.3)])
    np.testing.assert_allclose(StatevectorDevice().density_matrix(native), np.outer(expected, expected), atol=1e-14)


def test_exception_context_rolls_back_and_late_else_matches_actual_public_rejection():
    for cls in (PublicCircuit, QuantumCircuit):
        circuit = cls(1, 1)
        with pytest.raises(RuntimeError):
            with circuit.if_test((circuit.clbits[0], 1)):
                circuit.x(0)
                raise RuntimeError("abort")
        assert circuit.count_ops() == {}
        with circuit.if_test((circuit.clbits[0], 1)) as otherwise:
            circuit.x(0)
        circuit.z(0)
        with pytest.raises(Exception) as error:
            with otherwise:
                circuit.x(0)
        assert type(error.value).__name__ == "CircuitError"


@pytest.mark.parametrize("kind", ["while", "switch", "if"])
def test_explicit_body_requires_actual_public_quantum_and_classical_operand_lists(kind):
    def execute(cls):
        circuit, body = cls(1, 1), cls(1)
        body.x(0)
        if kind == "while":
            return circuit.while_loop((circuit.clbits[0], 1), body)
        if kind == "switch":
            return circuit.switch(circuit.clbits[0], [(0, body)])
        return circuit.if_test((circuit.clbits[0], 1), body)
    with pytest.raises(Exception) as reference:
        execute(PublicCircuit)
    with pytest.raises(CircuitError):
        execute(QuantumCircuit)
    assert type(reference.value).__name__ == "CircuitError"
