# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.

import numpy as np
import pytest

from quantumbridge import StatevectorDevice
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram, merge_rotations, split_hamiltonian
from quantumbridge.utils.math import Hamiltonian, PauliX, PauliZ
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.qml.tape import Tape
from quantumbridge.transforms import transform, NativeTransform


H = Hamiltonian([(.7, PauliZ(0)), (.2, PauliX(1)), (-.1, PauliZ(0).tensor(PauliZ(1)))])


class CountingDevice(StatevectorDevice):
    def __init__(self):
        super().__init__()
        self.executed_angles = []

    def expectation(self, circuit, observable):
        self.executed_angles.append(tuple(operation.params for operation in circuit.operations))
        return super().expectation(circuit, observable)


def test_same_transformed_qnode_rebinds_current_input_and_keeps_original_independent():
    builds, device = [], CountingDevice()
    def circuit(tape, theta):
        builds.append(theta)
        tape.ry(theta, 0)
        tape.ry(2*theta, 0)
        tape.h(1)
        tape.cx(0, 1)
        return tape.expval(H)
    original = QNode(circuit, 2, device=device)
    program = TransformProgram([split_hamiltonian, merge_rotations])
    first = program.execute_qnode(original, .2)
    first_ids = [item["execution_id"] for item in program.last_metadata["executions"]]
    second = program.execute_qnode(original, .7)
    second_ids = [item["execution_id"] for item in program.last_metadata["executions"]]
    assert builds == [.2, .7]
    assert first != second
    assert first == pytest.approx(.7*np.cos(.6)+.2, abs=1e-12)
    assert second == pytest.approx(.7*np.cos(2.1)+.2, abs=1e-12)
    assert len(device.executed_angles) == 6
    assert [angles[0][0] for angles in device.executed_angles] == pytest.approx([.6]*3+[2.1]*3)
    assert set(first_ids).isdisjoint(second_ids)
    assert original.last_metadata == {}
    assert original(.2) == pytest.approx(first, abs=1e-12)
    assert original(.7) == pytest.approx(second, abs=1e-12)
    assert len(device.executed_angles) == 8


def test_transform_object_dispatch_chains_without_mutating_original_program():
    def circuit(tape, x):
        tape.ry(x, 0)
        tape.ry(2*x, 0)
        return tape.expval(PauliZ(0))
    original = QNode(circuit, 1)
    first = merge_rotations(original)
    second = split_hamiltonian(first)
    assert original.transform_program is None
    assert len(first.transform_program.transforms) == 1
    assert len(second.transform_program.transforms) == 2
    for value in [.2, .7, -.3]:
        assert second(value) == pytest.approx(original(value), abs=1e-12)
        assert first(value) == pytest.approx(original(value), abs=1e-12)
    assert second.last_metadata["source_gate_parameter_count"] == 2
    assert second.last_metadata["gate_parameter_count"] == 1


def test_kwargs_nonlinear_shared_parameters_nested_measurements_and_slices():
    seen = []
    @transform
    def observe(tape):
        seen.append(tape.copy())
        return (tape,), lambda values:values[0]
    def circuit(tape, *, theta, scale=2):
        tape.ry(np.sin(theta), 0)
        tape.ry(scale*theta, 0)
        return {"energy": tape.expval(H), "local": [tape.expval(PauliZ(0))]}
    original = QNode(circuit, 2)
    transformed = TransformProgram([split_hamiltonian, merge_rotations, observe])(original)
    for theta in [.2, .7]:
        value = transformed(theta=theta, scale=2)
        expected = original(theta=theta, scale=2)
        assert value["energy"] == pytest.approx(expected["energy"], abs=1e-12)
        assert value["local"][0] == pytest.approx(expected["local"][0], abs=1e-12)
        assert value["local"][0] == pytest.approx(np.cos(np.sin(theta)+2*theta), abs=1e-12)
        assert transformed.last_metadata["executed_tape_count"] == 4
        assert [row["gate_angle_slice"] for row in transformed.last_metadata["executions"]] == [(0,1),(1,2),(2,3),(3,4)]
        assert transformed.last_metadata["stages"][0]["parent_child_slices"] == [(0,4)]
    assert len(seen) == 8
    assert all(len(tape.circuit.parameters) == 2 for tape in seen)


def test_configured_transform_and_explicit_native_callable_dispatch():
    @transform
    def scale_output(tape, factor):
        return (tape,), lambda values:factor*values[0]
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.expval(PauliZ(0))
    fn = scale_output(factor=2, qnode_options={"num_qubits":1})(circuit)
    assert isinstance(fn, QNode)
    assert fn(.2) == pytest.approx(2*np.cos(.2))
    program = TransformProgram([scale_output(factor=3)])
    other = program(circuit, qnode_options={"num_qubits":1})
    assert other(.7) == pytest.approx(3*np.cos(.7))
    tape = Tape(1)
    tape.expval(PauliZ(0))
    assert scale_output(tape, 2)[1]((.3,)) == .6


def test_explicit_dispatch_rejects_missing_or_conflicting_device_configuration():
    with pytest.raises(TypeError, match="qnode_options"): merge_rotations(lambda tape:None)
    with pytest.raises(TypeError): NativeTransform(3)
    tape = Tape(1)
    tape.expval(PauliZ(0))
    with pytest.raises(TypeError): merge_rotations(tape,qnode_options={"num_qubits":1})
    with pytest.raises(TypeError): TransformProgram()(tape,qnode_options={"num_qubits":1})
    node = QNode(lambda tape:tape.expval(PauliZ(0)),1)
    with pytest.raises(TypeError): merge_rotations(node,qnode_options={"num_qubits":1})


def test_shots_seed_partitions_local_override_and_repeated_calls():
    from dataclasses import replace
    def circuit(tape, theta):
        tape.ry(theta, 0)
        request = tape.expval(H)
        request = replace(request, shots=17, seed=8)
        tape.measurements[-1] = request
        return (request, tape.expval(PauliZ(0)))
    original = QNode(circuit, 2, shots=[30,(50,2)], seed=11)
    transformed = split_hamiltonian(original)
    first = transformed(.2)
    first_ids = [row["execution_id"] for row in transformed.last_metadata["executions"]]
    assert transformed(.2) == first
    assert len(first) == 3 and all(len(part) == 2 for part in first)
    second_ids = [row["execution_id"] for row in transformed.last_metadata["executions"]]
    assert set(first_ids).isdisjoint(second_ids)
    assert [part["shots"] for part in transformed.last_metadata["executions"][0]["partitions"]] == [30,50,50]
    assert transformed.last_metadata["executions"][0]["partitions"][0]["measurements"][0]["shots"] == 17


def test_native_symbolic_circuit_qnode_rebinds_after_transform():
    from quantumbridge.core import Circuit, Parameter
    parameter = Parameter("theta")
    original = QNode.from_circuit(Circuit(1).ry(parameter,0).ry(parameter/2,0), PauliZ(0))
    node = merge_rotations(original)
    assert node(.2) == pytest.approx(np.cos(.3))
    assert node(.7) == pytest.approx(np.cos(1.05))


def test_transformed_numpy_qnode_derivatives_use_native_chain_rule():
    node = merge_rotations(QNode(lambda tape,x:(tape.ry(x,0),tape.expval(PauliZ(0)))[1],1))
    assert node.gradient(.2) == pytest.approx(-np.sin(.2),abs=1e-12)
    plan = node._construct((.2,),{})
    value,jacobian,_ = plan.jacobian(plan.recorder.native_values())
    assert value == pytest.approx(np.cos(.2),abs=1e-12)
    np.testing.assert_allclose(jacobian,[[-np.sin(.2)]],atol=1e-12)
    with pytest.raises(ValueError, match="shape"):
        plan.evaluate([])


def test_live_torch_and_autograd_are_not_silently_detached_even_numpy_interface():
    torch = pytest.importorskip("torch")
    node = merge_rotations(QNode(lambda tape,x:(tape.ry(x,0),tape.expval(PauliZ(0)))[1],1,interface="numpy"))
    with pytest.raises(UnsupportedFeature, match="VJP"):
        node(torch.tensor(.2,requires_grad=True))


def test_live_autograd_has_a_real_nonzero_transformed_derivative():
    autograd = pytest.importorskip("autograd")
    node = merge_rotations(QNode(lambda tape,x:(tape.ry(x,0),tape.expval(PauliZ(0)))[1],1))
    assert autograd.grad(node)(.2) == pytest.approx(-np.sin(.2),abs=1e-12)


def test_dynamic_global_phase_and_mid_circuit_measurement_order_preserved():
    def circuit(tape, x):
        tape.circuit.global_phase = .37
        tape.ry(x,0)
        tape.ry(x/2,0)
        measured = tape.measure(0)
        tape.cond(measured, lambda branch:branch.x(0))
        tape.ry(.1,0)
        return {"z":tape.expval(PauliZ(0))}
    original = QNode(circuit,1)
    transformed = merge_rotations(original)
    for x in [.2,.7]: assert transformed(x)["z"] == pytest.approx(original(x)["z"], abs=1e-12)
    plan = transformed._construct((.2,),{})
    assert plan.child_plans[0].circuit.global_phase == .37
    assert plan.child_plans[0].circuit.measurements[0].metadata["operation_index"] == 1


def test_changing_child_batch_width_keeps_old_closures_and_new_results_independent():
    def circuit(tape,x):
        tape.ry(x,0)
        terms = [(1.,PauliZ(0)),(.2,PauliX(0))]
        if x > .4:
            terms.append((.3,PauliZ(1)))
        return tape.expval(Hamiltonian(terms))
    original = QNode(circuit,2)
    node = split_hamiltonian(original)
    saved = node._construct((.2,),{})
    first = saved.evaluate(saved.recorder.native_values())
    for value, width in [(.7,3),(.2,2),(.9,3)]:
        assert node(value) == pytest.approx(original(value),abs=1e-12)
        assert node.last_metadata["executed_tape_count"] == width
    assert saved.evaluate(saved.recorder.native_values()) == first
    assert len(saved.child_plans) == 2


def test_transform_added_gate_does_not_mutate_the_source_angle_recorder():
    from quantumbridge.diff.qnode_engine import AngleRecorder
    @transform
    def append_constant(tape):
        tape.ry(.1,0)
        return (tape,),lambda results:results[0]
    recorder = AngleRecorder()
    source = Tape(1,recorder)
    source.ry(.2,0)
    source.expval(PauliZ(0))
    child = append_constant(source)[0][0]
    assert len(source.circuit.operations) == len(recorder.angles) == 1
    assert child.circuit.operations[-1].params == (.1,)
    def circuit(tape,x):
        tape.ry(x,0)
        tape.ry(2*x,0)
        return tape.expval(PauliZ(0))
    node = append_constant(QNode(circuit,1))
    assert node(.2) == pytest.approx(np.cos(.7),abs=1e-12)
    assert node.last_metadata["source_gate_parameter_count"] == 2


def test_direct_custom_dispatch_cannot_mutate_source_owned_metadata():
    @transform
    def mutate(tape):
        tape.circuit.metadata["data"]["values"].append(2)
        return (tape,),lambda values:values[0]
    source = Tape(1)
    source.circuit.metadata["data"] = {"values":[1]}
    source.expval(PauliZ(0))
    child = mutate(source)[0][0]
    assert source.circuit.metadata["data"]["values"] == [1]
    assert child.circuit.metadata["data"]["values"] == [1,2]


@pytest.mark.parametrize("module",["jaxlib.xla_extension","tensorflow.python.framework.ops"])
def test_unsupported_framework_objects_reject_before_numeric_conversion(module):
    def forbidden(_): raise AssertionError("A framework object must not be silently converted.")
    value = type("FrameworkValue",(),{"__module__":module,"__float__":forbidden})()
    node = merge_rotations(QNode(lambda tape,x:(tape.ry(x,0),tape.expval(PauliZ(0)))[1],1,interface="numpy"))
    with pytest.raises(UnsupportedFeature,match="VJP"):
        node(value)
