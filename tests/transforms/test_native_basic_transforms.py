# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.

from itertools import repeat
import numpy as np
import pytest

from quantumbridge import StatevectorDevice, qchem, templates
from quantumbridge.core import Circuit, Instruction, Operation, Parameter
from quantumbridge.core.classical import UnsupportedFeature, bit
from quantumbridge.compiler import Target, CouplingMap
from quantumbridge.compiler.limits import CompilationLimits
from quantumbridge.compiler.decomposition import GateDecompositionPass
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.qml.tape import Tape
from quantumbridge.transforms import (TransformProgram, TransformLimits, TransformError,
    execute_transform, merge_rotations, cancel_inverses, decompose, compile, split_to_single_terms)
from quantumbridge.utils.math import Hamiltonian, PauliString, PauliX, PauliZ


def terminal(circuit):
    tape = Tape(circuit.num_qubits)
    tape.circuit = circuit
    tape.expval(PauliZ(0))
    return tape


def matrix(circuit):
    return Operator.from_circuit(circuit).data


@pytest.mark.parametrize("name", ["x","y","z","h","cx","cy","cz","ch","swap","ccx","cswap"])
def test_actual_adjacent_self_inverse_gates_cancel(name):
    circuit = Circuit(3)
    wires = [0] if name in {"x","y","z","h"} else [0,1] if name not in {"ccx","cswap"} else [0,1,2]
    getattr(circuit,name)(*wires)
    getattr(circuit,name)(*wires)
    circuit.global_phase = .29
    transformed = cancel_inverses(terminal(circuit))[0][0]
    assert transformed.circuit.operations == []
    assert transformed.circuit.global_phase == .29
    np.testing.assert_allclose(matrix(circuit),matrix(transformed.circuit),atol=1e-12)


@pytest.mark.parametrize("name,inverse", [("s","sdg"),("t","tdg"),("sx","sxdg")])
def test_actual_inverse_dagger_pairs_cancel(name,inverse):
    circuit = Circuit(1)
    getattr(circuit,name)(0)
    getattr(circuit,inverse)(0)
    out = cancel_inverses(terminal(circuit))[0][0]
    assert not out.circuit.operations
    np.testing.assert_allclose(matrix(circuit),matrix(out.circuit),atol=1e-12)


@pytest.mark.parametrize("name", ["rx","ry","rz","phase","crx","cry","crz","cp","rxx","ryy","rzz"])
def test_numeric_and_native_symbolic_inverse_rotations(name):
    theta = Parameter("theta")
    wires = [0] if name in {"rx","ry","rz","phase"} else [0,1]
    for angle in [.37,theta]:
        circuit = Circuit(2)
        getattr(circuit,name)(angle,*wires)
        getattr(circuit,name)(-angle,*wires)
        out = cancel_inverses(terminal(circuit))[0][0]
        assert out.circuit.operations == []
        bound = circuit.bind({theta:.37}) if circuit.parameters else circuit
        np.testing.assert_allclose(matrix(bound),matrix(out.circuit),atol=1e-12)


@pytest.mark.parametrize("boundary", ["barrier","measure","reset","store","condition","control","unknown"])
def test_cancellation_cannot_cross_side_effect_or_runtime_boundary(boundary):
    tape = Tape(1)
    tape.x(0)
    if boundary == "barrier": tape.circuit.barrier()
    elif boundary == "measure": tape.measure(0)
    elif boundary == "reset": tape.reset(0)
    elif boundary == "store": tape.circuit.operations.append(Operation("store",(),metadata={"directive":True}))
    elif boundary == "condition":
        tape.circuit.num_bits = 1
        tape.circuit.z(0).c_if(0,1)
    elif boundary == "control":
        tape.circuit.num_bits = 1
        tape.cond(bit(0),lambda branch:branch.z(0))
    else: tape.circuit.append("opaque_side_effect",[0],metadata={"unknown_effect":True})
    tape.x(0)
    tape.expval(PauliZ(0))
    child = cancel_inverses(tape)[0][0]
    assert sum(op.name == "x" for op in child.circuit.operations) == 2
    assert len(child.circuit.measurements) == len(tape.circuit.measurements)


def test_cancellation_is_recursive_but_never_commutes_unproved_operations():
    circuit = Circuit(1).x(0).h(0).h(0).x(0)
    assert cancel_inverses(terminal(circuit))[0][0].circuit.operations == []
    assert len(cancel_inverses(terminal(circuit),recursive=False)[0][0].circuit.operations) == 2
    assert len(cancel_inverses(terminal(Circuit(1).x(0).h(0).x(0)))[0][0].circuit.operations) == 3
    with pytest.raises(TypeError): cancel_inverses(terminal(circuit),recursive=2)


@pytest.mark.parametrize("name", ["h","s","sdg","t","sx","sxdg","ry","u","rxx","ryy","rzz","crx","cry","crz","cp","swap","cz"])
def test_decomposition_preserves_full_complex_unitary_and_phase(name):
    circuit = Circuit(2)
    if name == "u": circuit.u(.23,-.41,.67,0)
    elif name in {"rx","ry"}: getattr(circuit,name)(.37,0)
    elif name in {"rxx","ryy","rzz","crx","cry","crz","cp"}: getattr(circuit,name)(.37,0,1)
    elif name in {"swap","cz"}: getattr(circuit,name)(0,1)
    else: getattr(circuit,name)(0)
    circuit.global_phase = -.23
    child = decompose(terminal(circuit),gate_set={"RX","RZ","CNOT"})[0][0]
    assert all(op.name in {"rx","rz","cx"} for op in child.circuit.operations)
    np.testing.assert_allclose(matrix(child.circuit),matrix(circuit),atol=2e-12,rtol=0)


def test_decompose_actual_templates_and_explicit_named_wire_order():
    layer = templates.StronglyEntanglingLayers(np.arange(12).reshape(2,2,3)/10, wires=["right","left"])
    qft = templates.QFT([0,1])
    circuit = Circuit(3)
    layer.apply(circuit,wire_map={"right":2,"left":0})
    qft.apply(circuit,wire_map={0:2,1:0})
    tape = terminal(circuit)
    child = decompose(tape,gate_set={"RX","RZ","CNOT"})[0][0]
    np.testing.assert_allclose(matrix(child.circuit),matrix(circuit),atol=2e-12)


def test_recursive_native_custom_definitions_keep_parameter_ast_and_global_phase():
    theta, phi, x = Parameter("theta"), Parameter("phi"), Parameter("x")
    inner = Circuit(1).phase(phi,0)
    inner.global_phase = phi/3
    outer = Circuit(1).append("inner_custom",[0],params=[theta/2]).ry(theta,0)
    outer.global_phase = .19
    tape = terminal(Circuit(2).append("outer_custom",[1],params=[x]))
    out = decompose(tape,gate_set={"RX","RZ","CNOT"},definitions={"outer_custom":outer,"inner_custom":inner})[0][0]
    assert out.circuit.parameters == (x,)
    expected = Circuit(2).phase(.2,1).ry(.4,1)
    expected.global_phase = .19+.2/3
    np.testing.assert_allclose(matrix(out.circuit.bind({x:.4})),matrix(expected),atol=1e-12)
    assert tape.circuit.operations[0].name == "outer_custom"


def test_registered_template_and_instruction_are_actual_native_decompositions():
    template = templates.QFT([0,1])
    instruction = Circuit(1).h(0).phase(.2,0).to_instruction("inner")
    source = Circuit(2).append("qft_custom",[1,0]).append("instruction_custom",[1])
    child = decompose(terminal(source),definitions={"qft_custom":template,"instruction_custom":instruction})[0][0]
    expected = Circuit(2)
    template.apply(expected,wire_map={0:1,1:0})
    expected.h(1).phase(.2,1)
    np.testing.assert_allclose(matrix(child.circuit),matrix(expected),atol=1e-12)


def test_decomposition_cycle_and_size_and_work_budgets_reject_before_execution():
    recursive = Circuit(1).append("recursive_custom",[0])
    with pytest.raises(UnsupportedFeature,match="recursively"):
        decompose(terminal(recursive),definitions={"recursive_custom":recursive})
    with pytest.raises(MemoryError):
        decompose(terminal(Circuit(1).h(0)),gate_set={"rx","rz"},limits=TransformLimits(max_operations_per_tape=2))
    with pytest.raises(MemoryError):
        decompose(terminal(Circuit(1).h(0)),gate_set={"rx","rz"},limits=TransformLimits(max_expansion_steps=2))
    with pytest.raises(MemoryError):
        GateDecompositionPass({"rx","rz"}).run(Circuit(1).h(0),max_operations=1)
    with pytest.raises(ValueError):
        GateDecompositionPass().run(Circuit(1),max_operations=0)


def test_opaque_definition_requires_complete_phase_proof_and_fresh_names():
    x = matrix(Circuit(1).x(0))
    definition = Circuit(1).x(0)
    definition.global_phase = .3
    circuit = Circuit(1).append("opaque_custom",[0],metadata={"matrix":x})
    with pytest.raises(ValueError,match="global phase"):
        decompose(terminal(circuit),definitions={"opaque_custom":definition})
    circuit.operations = [Operation("opaque_custom",(0,),metadata={"matrix":np.exp(.3j)*x})]
    child = decompose(terminal(circuit),definitions={"opaque_custom":definition})[0][0]
    np.testing.assert_allclose(matrix(child.circuit),np.exp(.3j)*x,atol=1e-12)
    with pytest.raises(ValueError,match="fresh"):
        decompose(terminal(Circuit(1).x(0)),definitions={"x":Circuit(1).h(0)})


@pytest.mark.parametrize("definition", [object(),Instruction("opaque",1),Circuit(2),Circuit(1,1).measure(0,0)])
def test_bad_native_definitions_reject(definition):
    tape = terminal(Circuit(1).append("custom",[0]))
    with pytest.raises((TypeError,ValueError,UnsupportedFeature)):
        decompose(tape,definitions={"custom":definition})


def test_unknown_gate_and_unknown_definition_side_effects_reject():
    with pytest.raises(UnsupportedFeature): decompose(terminal(Circuit(1).append("unknown",[0])))
    tape = terminal(Circuit(1).append("custom",[0],metadata={"side_effect":True}))
    with pytest.raises(UnsupportedFeature,match="side effects"):
        decompose(tape,definitions={"custom":Circuit(1).x(0)})
    with pytest.raises(TypeError): decompose(tape,definitions=[("custom",Circuit(1))])
    with pytest.raises(MemoryError): decompose(terminal(Circuit(1).x(0)),gate_set=repeat("rx"))
    with pytest.raises(TypeError): decompose(terminal(Circuit(1).x(0)),gate_set=[object()])
    with pytest.raises(ValueError): decompose(terminal(Circuit(1).x(0)),gate_set=[])


def test_compile_native_target_routing_and_parameterized_qnode_execution():
    target = Target(3,("rx","rz","h","cx"),CouplingMap.from_line(3))
    def circuit(tape, x):
        tape.ry(np.sin(x),0)
        tape.cx(0,2)
        return {"energy":tape.expval(PauliZ(0).tensor(PauliZ(2)))}
    original = QNode(circuit,3)
    transformed = compile(original,target=target,optimization_level=2)
    for theta in [.2,.7]:
        assert transformed(theta)["energy"] == pytest.approx(original(theta)["energy"],abs=1e-12)
    plan = transformed._construct((.7,),{})
    assert plan.child_plans[0].circuit.metadata["initial_layout"] == {0:0,1:1,2:2}
    assert all(op.name in target.basis_gates for op in plan.child_plans[0].circuit.operations)


def test_compile_cannot_silently_apply_nonidentity_layout_or_ancilla_growth():
    tape = terminal(Circuit(2).h(0).cx(0,1))
    with pytest.raises(UnsupportedFeature,match="identity layout"):
        compile(tape,initial_layout=[1,0])
    with pytest.raises(UnsupportedFeature,match="equal width"):
        compile(tape,target=Target(3,("h","cx")))
    with pytest.raises(TypeError): compile(tape,compilation_limits=object())
    with pytest.raises(ValueError): compile(tape,limits=TransformLimits(max_operations_per_tape=10),compilation_limits=CompilationLimits())


def test_compile_full_complex_matrix_phase_and_terminal_result_map():
    tape = terminal(Circuit(2).h(0).phase(.37,1).cx(0,1).ry(.21,0))
    tape.circuit.global_phase = .42
    second = tape.probs([1,0])
    tape.set_output({"z":tape.measurements[0],"p":[second]})
    child = compile(tape,basis_set={"rz","sx","cx"},optimization_level=2)[0][0]
    np.testing.assert_allclose(matrix(child.circuit),matrix(tape.circuit),atol=2e-12)
    result = execute_transform(tape,compile(basis_set={"rz","sx","cx"},optimization_level=2))
    assert result["z"] == pytest.approx(StatevectorDevice().expectation(tape.circuit,PauliZ(0)),abs=1e-12)
    assert list(result["p"][0]) == ["00","01","10","11"]


def test_single_term_contract_one_tape_unique_measurements_and_weighted_processing():
    z, x = PauliZ(0), PauliX(1)
    tape = Tape(2)
    tape.ry(.3,0)
    first = tape.expval(Hamiltonian([(1.,z),(2.,PauliString([])),(0.,x),(1.,z)]))
    second = tape.expval(z)
    tape.set_output({"energy":first,"other":[second,first]})
    children, process = split_to_single_terms(tape)
    assert len(children) == 1 and len(children[0].measurements) == 2
    assert [request.observable for request in children[0].measurements] == [z,x]
    assert process(((3.,7.),)) == {"energy":8.,"other":[3.,8.]}
    value, metadata = execute_transform(tape,split_to_single_terms,return_metadata=True)
    assert value["energy"] == pytest.approx(2+2*np.cos(.3))
    assert metadata["executed_tape_count"] == 1
    assert len(metadata["executions"][0]["partitions"][0]["measurements"]) == 2


def test_constant_identity_retains_one_empty_measurement_tape_without_fake_device_calls():
    tape = Tape(1,shots=[5,10])
    tape.expval(Hamiltonian([(2.,PauliString([]))]))
    children, processor = split_to_single_terms(tape)
    assert len(children) == 1 and children[0].measurements == []
    assert processor((((),()),)) == (2.,2.)
    value, metadata = execute_transform(tape,split_to_single_terms,return_metadata=True)
    assert value == (2.,2.)
    assert metadata["executed_tape_count"] == 1
    assert all(not item["measurements"] for item in metadata["executions"][0]["partitions"])


def test_single_term_split_preserves_direct_variance_probs_and_deduplicates_by_kind():
    tape = Tape(2)
    tape.ry(.4,0)
    var1 = tape.var(PauliZ(0))
    prob = tape.probs([1,0])
    energy = tape.expval(Hamiltonian([(1.,PauliZ(0)),(.3,PauliX(1))]))
    var2 = tape.var(PauliZ(0))
    tape.set_output((var1,{"prob":prob,"energy":energy},var2))
    children, _ = split_to_single_terms(tape)
    assert len(children[0].measurements) == 4
    result = execute_transform(tape,split_to_single_terms)
    assert result[0] == pytest.approx(np.sin(.4)**2)
    assert result[2] == result[0]
    assert result[1]["energy"] == pytest.approx(np.cos(.4))
    bad = Tape(2)
    bad.var(Hamiltonian([(1.,PauliZ(0)),(1.,PauliX(1))]))
    with pytest.raises(UnsupportedFeature,match="expectation"):
        split_to_single_terms(bad)


def test_shot_vector_splitting_keeps_measurement_and_partition_axes_distinct():
    tape = Tape(2,shots=[10,(20,2)],seed=5)
    tape.ry(.4,0)
    first = tape.expval(Hamiltonian([(1.,PauliZ(0)),(.3,PauliX(1))]))
    second = tape.expval(PauliZ(0))
    tape.set_output((first,[second]))
    out, metadata = execute_transform(tape,split_to_single_terms,return_metadata=True)
    assert len(out) == 3 and all(isinstance(part[1],list) for part in out)
    assert [part["shots"] for part in metadata["executions"][0]["partitions"]] == [10,20,20]
    assert execute_transform(tape,split_to_single_terms) == out


def test_split_result_errors_invalid_terms_and_cumulative_work_budget():
    tape = Tape(2)
    tape.expval(Hamiltonian([(1.,PauliZ(0)),(.3,PauliX(1))]))
    _, process = split_to_single_terms(tape)
    with pytest.raises(ValueError): process(())
    with pytest.raises(ValueError): process(((1.,),))
    tape.expval(Hamiltonian([(1.,PauliZ(0)),(.3,PauliX(1))]))
    with pytest.raises(MemoryError): split_to_single_terms(tape,limits=TransformLimits(max_expansion_steps=3))
    for hamiltonian in [Hamiltonian([(float("nan"),PauliZ(0))]),Hamiltonian([(0.,PauliZ(2))]),Hamiltonian([(1.,PauliString([(0,"X"),(0,"Y")]))])]:
        invalid = Tape(2)
        invalid.expval(hamiltonian)
        with pytest.raises(ValueError): split_to_single_terms(invalid)


def test_all_basic_transforms_actual_qnode_and_geometry_generated_h2():
    molecule = qchem.Molecule(["H","H"],[(0,0,0),(0,0,1.4)],unit="bohr")
    problem = qchem.molecular_hamiltonian_native(molecule)
    def circuit(tape, theta):
        tape.x(0)
        tape.x(0)
        tape.x(0)
        tape.x(1)
        qchem.apply_fermionic_excitation(tape,theta,[0,1,2,3])
        return tape.expval(problem.hamiltonian)
    original = QNode(circuit,4)
    node = TransformProgram([cancel_inverses,decompose(gate_set={"RX","RZ","CNOT"}),
            compile(basis_set={"RX","RZ","CNOT"}),split_to_single_terms,merge_rotations])(original)
    for angle in [.1,.3]:
        value = node(angle)
        assert value == pytest.approx(original(angle),abs=2e-11)
        reference = original._construct((angle,),{})
        bound = reference.circuit.bind(dict(zip(reference.recorder.parameters,reference.recorder.native_values())))
        state = StatevectorDevice().statevector(bound)
        assert value == pytest.approx(np.vdot(state,problem.hamiltonian.matrix()@state).real,abs=2e-11)
        assert node.last_metadata["executed_tape_count"] == 1
        assert node.last_metadata["postprocessing_order"] == [4,3,2,1,0]


def test_dynamic_decomposition_keeps_lexical_phase_and_ordered_measurement():
    tape = Tape(1)
    tape.h(0)
    measured = tape.measure(0)
    tape.cond(measured,lambda branch:(branch.phase(.3,0),branch.h(0)))
    tape.expval(PauliZ(0))
    actual = execute_transform(tape,decompose(gate_set={"RX","RZ","CNOT"}))
    expected = execute_transform(tape,TransformProgram())
    assert actual == pytest.approx(expected,abs=1e-12)
    child = decompose(tape,gate_set={"RX","RZ","CNOT"})[0][0]
    branch = next(op.metadata["control_node"].bodies[0] for op in child.circuit.operations if "control_node" in op.metadata)
    assert abs(branch.global_phase) > .1
    assert child.circuit.measurements[0].metadata["operation_index"] > 1
    assert tape.circuit.measurements[0].metadata["operation_index"] == 1


def test_decomposition_output_budget_is_shared_across_control_bodies():
    tape = Tape(1)
    tape.circuit.num_bits = 1
    tape.cond(bit(0),lambda branch:branch.h(0))
    tape.cond(bit(0),lambda branch:branch.h(0))
    tape.expval(PauliZ(0))
    with pytest.raises(MemoryError,match="max_operations"):
        decompose(tape,gate_set={"RX","RZ","CNOT"},limits=TransformLimits(max_operations_per_tape=6))


@pytest.mark.parametrize("invalid",[2*np.eye(2),np.diag([1+1e-7,1])])
def test_opaque_definition_cannot_smuggle_nonunitary_matrix_as_a_basis_leaf(invalid):
    body = Circuit(1).append("opaque_leaf",[0],metadata={"matrix":invalid})
    source = terminal(Circuit(1).append("wrapper_custom",[0],metadata={"matrix":invalid}))
    with pytest.raises(ValueError,match="unitary"):
        decompose(source,gate_set={"opaque_leaf"},definitions={"wrapper_custom":body})


@pytest.mark.parametrize("function",[merge_rotations,cancel_inverses,decompose,compile,split_to_single_terms])
def test_structural_transforms_accept_unmeasured_tapes_without_fake_measurements(function):
    source = Tape(2)
    source.ry(.2,0)
    source.ry(.3,0)
    source.h(1)
    children, _ = function(source)
    assert len(children) == 1 and not children[0].measurements
    np.testing.assert_allclose(matrix(children[0].circuit),matrix(source.circuit),atol=2e-12)
    assert source.output_tree is None and not source.measurements
    assert TransformProgram([function])(source)[0][0].measurements == []
    with pytest.raises(ValueError,match="terminal measurements"):
        execute_transform(source,function)
