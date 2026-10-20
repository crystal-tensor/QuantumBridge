# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Optional public-API oracles only; no upstream implementation/test imports."""

import numpy as np
import pytest
qml = pytest.importorskip("pennylane")

from quantumbridge import Circuit, templates, qchem
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.qml.tape import Tape
from quantumbridge.transforms import (TransformProgram, cancel_inverses, merge_rotations,
    decompose, compile, split_to_single_terms, execute_transform)
from quantumbridge.utils.math import Hamiltonian, PauliString, PauliX, PauliZ
from quantumbridge.core.classical import UnsupportedFeature


def native_tape(circuit, observable=None):
    tape = Tape(circuit.num_qubits)
    tape.circuit = circuit
    tape.expval(PauliZ(0) if observable is None else observable)
    return tape


def compare_matrix(native, public, width):
    np.testing.assert_allclose(Operator.from_circuit(native.circuit).data,
                              qml.matrix(public,wire_order=list(range(width))),atol=3e-12,rtol=0)


def phase_preserving_oracle(function,tape,width,keyword):
    # The public transform may drop GlobalPhase if it is excluded from its
    # target basis. Keep it and independently verify the oracle input/output.
    children,_ = function(tape,**{keyword:{"RX","RY","RZ","CNOT","GlobalPhase"}})
    np.testing.assert_allclose(qml.matrix(children[0],wire_order=list(range(width))),
                              qml.matrix(tape,wire_order=list(range(width))),atol=3e-12,rtol=0)
    return children[0]


def test_public_split_has_one_tape_three_measurements_not_three_tapes():
    native = native_tape(Circuit(2).ry(.2,0),Hamiltonian([(.7,PauliZ(0)),(.2,PauliX(1)),(-.1,PauliZ(0).tensor(PauliZ(1)))]))
    public = qml.tape.QuantumScript([qml.RY(.2,0)],[qml.expval(.7*qml.Z(0)+.2*qml.X(1)-.1*qml.Z(0)@qml.Z(1))])
    children, process = split_to_single_terms(native)
    tapes, oracle = qml.transforms.split_to_single_terms(public)
    assert len(children) == len(tapes) == 1
    assert len(children[0].measurements) == len(tapes[0].measurements) == 3
    assert process(((.3,.4,.5),)) == pytest.approx(oracle(((.3,.4,.5),)),abs=1e-12)
    assert execute_transform(native,split_to_single_terms) == pytest.approx(oracle(qml.execute(tapes,qml.device("default.qubit",wires=2))),abs=1e-12)


def test_public_identity_duplicate_and_zero_terms_have_identical_measurement_rules():
    tape = Tape(2)
    tape.expval(Hamiltonian([(1.,PauliZ(0)),(2.,PauliString([])),(0.,PauliX(1)),(1.,PauliZ(0))]))
    tape.expval(PauliZ(0))
    public = qml.tape.QuantumScript([], [qml.expval(qml.Z(0)+2*qml.Identity(0)+0*qml.X(1)+qml.Z(0)),qml.expval(qml.Z(0))])
    children, process = split_to_single_terms(tape)
    tapes, oracle = qml.transforms.split_to_single_terms(public)
    assert len(children) == len(tapes) == 1
    assert len(children[0].measurements) == len(tapes[0].measurements) == 2
    np.testing.assert_allclose(process(((.3,.4),)),oracle(((.3,.4),)),atol=1e-12)


def test_public_constant_identity_uses_one_empty_measurement_script():
    tape = native_tape(Circuit(1),Hamiltonian([(2.,PauliString([]))]))
    public = qml.tape.QuantumScript([], [qml.expval(2*qml.Identity(0))])
    children, process = split_to_single_terms(tape)
    tapes, oracle = qml.transforms.split_to_single_terms(public)
    assert len(children) == len(tapes) == 1
    assert not children[0].measurements and not tapes[0].measurements
    assert process(((),)) == oracle(((),)) == 2.


def test_public_noncommuting_measurements_are_not_qwc_grouped_by_single_terms():
    tape = native_tape(Circuit(1).ry(.3,0),Hamiltonian([(1.,PauliX(0)),(.7,PauliZ(0))]))
    public = qml.tape.QuantumScript([qml.RY(.3,0)],[qml.expval(qml.X(0)+.7*qml.Z(0))])
    tapes, process = qml.transforms.split_to_single_terms(public)
    children, _ = split_to_single_terms(tape)
    assert len(children) == len(tapes) == 1 and len(children[0].measurements) == 2
    assert execute_transform(tape,split_to_single_terms) == pytest.approx(process(qml.execute(tapes,qml.device("default.qubit",wires=1))),abs=1e-12)


def test_public_variance_probs_and_expval_reconstruction_order():
    tape = Tape(2)
    tape.ry(.3,0)
    tape.var(PauliZ(0))
    tape.probs([1,0])
    tape.expval(Hamiltonian([(1.,PauliZ(0)),(1.,PauliX(1))]))
    public = qml.tape.QuantumScript([qml.RY(.3,0)],[qml.var(qml.Z(0)),qml.probs([1,0]),qml.expval(qml.Z(0)+qml.X(1))])
    children, _ = split_to_single_terms(tape)
    tapes, process = qml.transforms.split_to_single_terms(public)
    assert len(children[0].measurements) == len(tapes[0].measurements) == 4
    actual, expected = execute_transform(tape,split_to_single_terms), process(qml.execute(tapes,qml.device("default.qubit",wires=2)))
    assert actual[0] == pytest.approx(expected[0],abs=1e-12)
    np.testing.assert_allclose(list(actual[1].values()),expected[1],atol=1e-12)
    assert actual[2] == pytest.approx(expected[2],abs=1e-12)


def test_public_variance_of_sum_is_rejected_not_split_as_linear_expectation():
    tape = Tape(2)
    tape.var(Hamiltonian([(1.,PauliZ(0)),(1.,PauliX(1))]))
    with pytest.raises(UnsupportedFeature): split_to_single_terms(tape)
    with pytest.raises(RuntimeError):
        qml.transforms.split_to_single_terms(qml.tape.QuantumScript([],[qml.var(qml.Z(0)+qml.X(1))]))


def test_public_shot_vector_partition_and_measurement_axes():
    tape = Tape(2,shots=[10,(20,2)],seed=7)
    tape.expval(Hamiltonian([(.7,PauliZ(0)),(.2,PauliZ(1)),(-.1,PauliZ(0).tensor(PauliZ(1)))]))
    tape.expval(PauliZ(0))
    public = qml.tape.QuantumScript([], [qml.expval(.7*qml.Z(0)+.2*qml.Z(1)-.1*qml.Z(0)@qml.Z(1)),qml.expval(qml.Z(0))],shots=[10,(20,2)])
    children, process = split_to_single_terms(tape)
    tapes, oracle = qml.transforms.split_to_single_terms(public)
    assert len(children[0].measurements) == len(tapes[0].measurements) == 3
    raw = (((.3,.4,.5),(.6,.7,.8),(.9,.1,.2)),)
    np.testing.assert_allclose(process(raw),oracle(raw),atol=1e-12)
    np.testing.assert_allclose(execute_transform(tape,split_to_single_terms),oracle(qml.execute(tapes,qml.device("default.qubit",wires=2,seed=7))),atol=1e-12)


def test_public_transformed_qnode_repeated_inputs_have_current_binding():
    def circuit(tape,theta):
        tape.ry(np.sin(theta),0)
        tape.ry(2*theta,0)
        return tape.expval(Hamiltonian([(1.,PauliZ(0)),(.3,PauliX(0))]))
    node = split_to_single_terms(merge_rotations(QNode(circuit,1)))
    @qml.qnode(qml.device("default.qubit",wires=1))
    def oracle(theta):
        qml.RY(np.sin(theta),0)
        qml.RY(2*theta,0)
        return qml.expval(qml.Z(0)+.3*qml.X(0))
    public = qml.transforms.split_to_single_terms(qml.transforms.merge_rotations(oracle))
    for theta in [.2,.7,-.3]:
        assert node(theta) == pytest.approx(public(theta),abs=1e-12)


def test_public_cancel_fixed_inverse_pairs_complete_unitary():
    tape = native_tape(Circuit(2).h(0).h(0).s(1).sdg(1).cx(0,1).cx(0,1))
    public = qml.tape.QuantumScript([qml.Hadamard(0),qml.Hadamard(0),qml.S(1),qml.adjoint(qml.S)(1),qml.CNOT([0,1]),qml.CNOT([0,1])],[])
    child = cancel_inverses(tape)[0][0]
    tapes,_ = qml.transforms.cancel_inverses(public)
    assert child.circuit.operations == [] and not tapes[0].operations
    compare_matrix(child,tapes[0],2)


def test_public_cancel_barrier_conservatively_preserves_physics():
    tape = native_tape(Circuit(1).x(0).barrier().x(0))
    public = qml.tape.QuantumScript([qml.X(0),qml.Barrier(0),qml.X(0)],[])
    tapes,_ = qml.transforms.cancel_inverses(public)
    child = cancel_inverses(tape)[0][0]
    assert len(child.circuit.operations) == 3
    compare_matrix(child,tapes[0],1)


def test_public_decompose_controlled_rotation_and_wire_order():
    tape = native_tape(Circuit(3).crx(.37,2,0).cp(.2,0,1).swap(2,1))
    public = qml.tape.QuantumScript([qml.CRX(.37,wires=[2,0]),qml.ControlledPhaseShift(.2,wires=[0,1]),qml.SWAP([2,1])],[])
    oracle = phase_preserving_oracle(qml.transforms.decompose,public,3,"gate_set")
    compare_matrix(decompose(tape,gate_set={"RX","RZ","CNOT"})[0][0],oracle,3)


def test_public_decompose_template_matrices_are_not_only_probability_equal():
    data = np.arange(12).reshape(2,2,3)/10
    circuit = Circuit(2)
    templates.StronglyEntanglingLayers(data,[1,0]).apply(circuit)
    templates.QFT([1,0]).apply(circuit)
    public = qml.tape.QuantumScript([qml.StronglyEntanglingLayers(data,wires=[1,0]),qml.QFT([1,0])],[])
    oracle = phase_preserving_oracle(qml.transforms.decompose,public,2,"gate_set")
    compare_matrix(decompose(native_tape(circuit),gate_set={"RX","RZ","CNOT"})[0][0],oracle,2)


def test_public_compile_and_native_target_compiler_preserve_complete_matrix():
    tape = native_tape(Circuit(2).h(0).phase(.2,1).cx(0,1).ry(.37,0).rz(-.1,1))
    public = qml.tape.QuantumScript([qml.Hadamard(0),qml.PhaseShift(.2,1),qml.CNOT([0,1]),qml.RY(.37,0),qml.RZ(-.1,1)],[])
    oracle = phase_preserving_oracle(qml.transforms.compile,public,2,"basis_set")
    compare_matrix(compile(tape,basis_set={"RX","RZ","CNOT"},optimization_level=2)[0][0],oracle,2)


def test_public_merge_rotation_chain_complex_unitary():
    tape = native_tape(Circuit(2).rx(.2,1).rx(.3,1).rz(.1,0).rz(-.4,0))
    public = qml.tape.QuantumScript([qml.RX(.2,1),qml.RX(.3,1),qml.RZ(.1,0),qml.RZ(-.4,0)],[])
    tapes,_ = qml.transforms.merge_rotations(public)
    compare_matrix(merge_rotations(tape)[0][0],tapes[0],2)


def test_public_custom_definition_global_phase_is_retained():
    definition = Circuit(1).h(0)
    definition.global_phase = .3
    unitary = Operator.from_circuit(definition).data
    tape = native_tape(Circuit(1).append("phase_custom",[0],metadata={"matrix":unitary}))
    public = qml.tape.QuantumScript([qml.QubitUnitary(unitary,wires=[0])],[])
    oracle = phase_preserving_oracle(qml.transforms.decompose,public,1,"gate_set")
    compare_matrix(decompose(tape,gate_set={"RX","RZ","CNOT"},definitions={"phase_custom":definition})[0][0],oracle,1)


def test_public_generated_h2_hamiltonian_real_template_transform_workflow():
    molecule = qchem.Molecule(["H","H"],[(0,0,0),(0,0,1.4)],unit="bohr")
    problem = qchem.molecular_hamiltonian_native(molecule)
    coefficients, observables = [], []
    for coefficient,pauli in problem.hamiltonian.terms:
        coefficients.append(coefficient)
        operands = [{"X":qml.X,"Y":qml.Y,"Z":qml.Z}[label](wire) for wire,label in pauli.terms if label != "I"]
        observables.append(qml.prod(*operands) if operands else qml.Identity(0))
    hamiltonian = qml.Hamiltonian(coefficients,observables)
    def circuit(tape,weights):
        tape.x(0)
        tape.x(1)
        templates.StronglyEntanglingLayers(weights,range(4)).apply(tape)
        return tape.expval(problem.hamiltonian)
    native = TransformProgram([cancel_inverses,decompose(gate_set={"RX","RZ","CNOT"}),split_to_single_terms])(QNode(circuit,4))
    @qml.qnode(qml.device("default.qubit",wires=4))
    def oracle(weights):
        qml.X(0)
        qml.X(1)
        qml.StronglyEntanglingLayers(weights,wires=range(4))
        return qml.expval(hamiltonian)
    public = qml.transforms.split_to_single_terms(oracle)
    for scale in [.1,.2]:
        data = np.arange(12).reshape(1,4,3)*scale
        assert native(data) == pytest.approx(public(data),abs=2e-11)
