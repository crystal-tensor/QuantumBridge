# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.

from itertools import repeat

import numpy as np
import pytest

from quantumbridge import StatevectorDevice
from quantumbridge.core import Circuit, Operation, Parameter
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.diff.qnode_engine import AngleRecorder
from quantumbridge.diff.compiled_parameters import record_compiled_parameters
from quantumbridge.diff.trace import Dual
from quantumbridge.qml.tape import Tape
from quantumbridge.transforms import (TransformProgram, TransformLimits, TransformError,
                                      execute_transform, split_hamiltonian, merge_rotations)
from quantumbridge.utils.math import Hamiltonian, PauliString, PauliX, PauliZ


H = Hamiltonian([(.7, PauliZ(0)), (.2, PauliX(1)), (-.1, PauliZ(0).tensor(PauliZ(1)))])


def program(theta=.41, *, observable=H, shots=None):
    tape = Tape(2, shots=shots, seed=17)
    tape.ry(theta, 0)
    tape.ry(.13, 0)
    tape.rx(-.2, 1)
    tape.cx(0, 1)
    tape.h(1)
    tape.expval(observable)
    return tape


def identity(tape):
    return (tape.copy(),), lambda results: results[0]


class CountingDevice(StatevectorDevice):
    def __init__(self):
        super().__init__()
        self.calls = []

    def expectation(self, circuit, observable):
        self.calls.append((circuit.copy(), observable))
        return super().expectation(circuit, observable)


def test_identity_is_one_real_execution_with_original_output():
    tape, device = program(), CountingDevice()
    value, metadata = execute_transform(tape, identity, device, return_metadata=True)
    assert value == pytest.approx(StatevectorDevice().expectation(tape.circuit, H), abs=1e-12)
    assert len(device.calls) == metadata["executed_tape_count"] == 1
    assert metadata["transform_count"] == 1
    assert metadata["executions"][0]["execution_id"]


def test_one_to_three_executes_actual_distinct_term_circuits():
    tape, device = program(), CountingDevice()
    before = tape.circuit.to_ir().to_json()
    tapes, postprocess = split_hamiltonian(tape)
    assert len(tapes) == 3
    # Deliberately synthetic values prove the postprocessor actually uses inputs.
    assert postprocess((2., 3., 5.)) == pytest.approx(1.5)
    value, metadata = execute_transform(tape, split_hamiltonian, device, return_metadata=True)
    expected = StatevectorDevice().expectation(tape.circuit, H)
    assert abs(value - expected) <= 1e-10
    assert len(device.calls) == metadata["executed_tape_count"] == 3
    assert all(isinstance(observable, PauliString) for _, observable in device.calls)
    assert len({id(circuit) for circuit, _ in device.calls}) == 3
    assert len({item["execution_id"] for item in metadata["executions"]}) == 3
    assert tape.circuit.to_ir().to_json() == before


def test_composition_merges_each_child_and_only_executes_three():
    tape, device = program(), CountingDevice()
    transforms = TransformProgram([split_hamiltonian, merge_rotations])
    tapes, processor = transforms(tape)
    assert len(tapes) == 3
    assert all(len(child.circuit.operations) == 4 for child in tapes)
    assert all(child.circuit.operations[0].params == pytest.approx((.54,)) for child in tapes)
    value, metadata = execute_transform(tape, transforms, device, return_metadata=True)
    assert value == pytest.approx(StatevectorDevice().expectation(tape.circuit, H), abs=1e-12)
    assert len(device.calls) == 3
    assert metadata["postprocessing_order"] == [1, 0]
    assert [item["output_tape_count"] for item in metadata["stages"]] == [3, 3]
    assert processor((2., 3., 5.)) == pytest.approx(1.5)


def test_three_stages_reconstruct_in_reverse_not_forward_order():
    events = []
    def fanout(tape):
        def process(values):
            events.append("fanout")
            return values[0] + 10 * values[1]
        return (tape.copy(), tape.copy()), process
    def scaled(label, factor):
        def transform(tape):
            def process(values):
                events.append(label)
                return factor * values[0]
            return (tape.copy(),), process
        return transform
    prepared = TransformProgram([fanout, scaled("middle", 2), scaled("last", 3)]).prepare(program())
    assert prepared.processing_fn((1., 4.)) == 246.
    assert events == ["last", "last", "middle", "middle", "fanout"]


def test_nested_result_structure_and_repeated_requests():
    tape = program()
    first = tape.measurements[0]
    second = tape.expval(PauliX(1))
    tape.set_output({"energy": first, "nested": [second, (first,)]})
    value, metadata = execute_transform(tape, split_hamiltonian, return_metadata=True)
    energy = StatevectorDevice().expectation(tape.circuit, H)
    assert value["energy"] == pytest.approx(energy)
    assert isinstance(value["nested"], list) and isinstance(value["nested"][1], tuple)
    assert value["nested"][1][0] == pytest.approx(energy)
    assert value["nested"][0] == pytest.approx(StatevectorDevice().expectation(tape.circuit, PauliX(1)))
    assert metadata["executed_tape_count"] == 7


def test_identity_duplicate_zero_terms_and_wire_order():
    hamiltonian = Hamiltonian([(.3, PauliString([])), (.7, PauliZ(0)),
                              (-.2, PauliZ(0)), (0., PauliX(1)),
                              (-.1, PauliString([(1, "X"), (0, "Z")]))])
    tape, device = program(observable=hamiltonian), CountingDevice()
    value, metadata = execute_transform(tape, split_hamiltonian, device, return_metadata=True)
    assert value == pytest.approx(StatevectorDevice().expectation(tape.circuit, hamiltonian), abs=1e-12)
    assert metadata["executed_tape_count"] == len(device.calls) == 4
    assert device.calls[-1][1].terms == ((1, "X"), (0, "Z"))


@pytest.mark.parametrize("hamiltonian", [Hamiltonian([]), Hamiltonian([(0., PauliZ(0))])])
def test_constant_zero_needs_no_fake_execution(hamiltonian):
    device = CountingDevice()
    value, metadata = execute_transform(program(observable=hamiltonian), split_hamiltonian, device, return_metadata=True)
    assert value == 0 and metadata["executed_tape_count"] == 0 and device.calls == []


@pytest.mark.parametrize("shots", [None, 20, [20, (30, 2)]])
def test_preserves_shots_and_partition_metadata(shots):
    value, metadata = execute_transform(program(shots=shots), split_hamiltonian, return_metadata=True)
    partitions = [20, 30, 30] if isinstance(shots, list) else [shots]
    assert all([part["shots"] for part in item["partitions"]] == partitions for item in metadata["executions"])
    if isinstance(shots, list):
        assert isinstance(value, tuple) and len(value) == 3
    else:
        assert isinstance(value, float)
    seeds = [item["partitions"][0]["seed"] for item in metadata["executions"]]
    assert len(set(seeds)) == 3


def test_shot_vector_and_measurement_tuple_are_not_confused():
    tape = program(shots=[20, 30])
    first = tape.measurements[0]
    second = tape.expval(PauliZ(0))
    tape.set_output((first, {"other": second}))
    value = execute_transform(tape, TransformProgram([split_hamiltonian, merge_rotations]))
    assert isinstance(value, tuple) and len(value) == 2
    assert all(isinstance(part, tuple) and isinstance(part[1], dict) for part in value)


def test_request_local_shots_preserved_and_total_budget_preflight():
    from dataclasses import replace
    tape = program()
    tape.measurements[0] = replace(tape.measurements[0], shots=11, seed=9)
    value, metadata = execute_transform(tape, split_hamiltonian, return_metadata=True)
    assert isinstance(value, float)
    assert all(item["partitions"][0]["measurements"][0] == {"kind": "expval", "shots": 11, "seed": 9} for item in metadata["executions"])
    device = CountingDevice()
    with pytest.raises(MemoryError, match="max_total_shots"):
        execute_transform(tape, split_hamiltonian, device, limits=TransformLimits(max_total_shots=32))
    assert device.calls == []


def test_native_parameters_survive_transform_and_execute_with_bindings():
    theta = Parameter("theta")
    tape = program(theta)
    tapes, _ = TransformProgram([split_hamiltonian, merge_rotations])(tape)
    assert all(theta in child.circuit.parameters for child in tapes)
    assert tape.circuit.operations[0].params == (theta,)
    value = execute_transform(tape, TransformProgram([split_hamiltonian, merge_rotations]), bindings={theta: .41})
    assert value == pytest.approx(StatevectorDevice().expectation(program().circuit, H), abs=1e-12)


def test_nonlinear_shared_parameter_graph_is_retained_for_future_gradient_plan():
    recorder = AngleRecorder()
    tape = Tape(1, recorder)
    x = Dual(.31, [1.])
    tape.ry(x.sin(), 0)
    tape.ry(2*x, 0)
    tape.expval(PauliZ(0))
    children, _ = merge_rotations(tape)
    _, recovered = record_compiled_parameters(children[0].circuit, recorder)
    assert recovered.angles[0].value == pytest.approx(np.sin(.31)+.62)
    assert recovered.angles[0].derivative[0] == pytest.approx(np.cos(.31)+2)
    assert len(recorder.angles) == 2


def test_torch_nonleaf_graph_copy_and_merging_without_claiming_quantum_vjp():
    torch = pytest.importorskip("torch")
    x = torch.tensor(.31, dtype=torch.float64, requires_grad=True)
    tape = Tape(1)
    tape.ry(torch.sin(x), 0)
    tape.ry(2*x, 0)
    tape.expval(PauliZ(0))
    child = merge_rotations(tape)[0][0]
    child.circuit.operations[0].params[0].backward()
    assert x.grad.item() == pytest.approx(np.cos(.31)+2)
    assert tape.circuit.operations[0].params[0].grad_fn is not None
    with pytest.raises(UnsupportedFeature, match="B1"):
        execute_transform(tape, merge_rotations)


def test_user_transform_mutation_cannot_change_input_owned_structure():
    tape = program()
    tape.circuit.operations[0].metadata["nested"] = {"x": [1]}
    def mutate(source):
        source.circuit.operations[0].metadata["nested"]["x"].append(2)
        source.circuit.x(0)
        return (source,), lambda results: results[0]
    execute_transform(tape, mutate)
    assert len(tape.circuit.operations) == 5
    assert tape.circuit.operations[0].metadata["nested"]["x"] == [1]


def test_duplicate_child_references_receive_independent_owned_copies():
    def duplicate(source):
        return (source, source), lambda results: results[0] + results[1]
    children, _ = TransformProgram([duplicate])(program())
    children[0].circuit.x(0)
    assert len(children[1].circuit.operations) == 5


@pytest.mark.parametrize("boundary", ["measure", "reset", "barrier", "condition", "store", "control"])
def test_rotation_merge_never_crosses_dynamic_or_directive_boundaries(boundary):
    from quantumbridge.core.classical import bit
    tape = Tape(1)
    tape.ry(.2, 0)
    if boundary == "measure": tape.measure(0)
    elif boundary == "reset": tape.reset(0)
    elif boundary == "barrier": tape.circuit.barrier()
    elif boundary == "condition":
        tape.circuit.num_bits = 1
        tape.circuit.x(0).c_if(0, 1)
    elif boundary == "store":
        tape.circuit.operations.append(Operation("store", (), metadata={"directive": True}))
    else:
        tape.circuit.num_bits = 1
        tape.cond(bit(0), lambda branch: branch.x(0))
    tape.ry(.3, 0)
    tape.expval(PauliZ(0))
    child = merge_rotations(tape)[0][0]
    assert [op.params[0] for op in child.circuit.operations if op.name == "ry"] == [.2, .3]
    assert len(child.circuit.measurements) == len(tape.circuit.measurements)


def test_merge_preserves_measurement_positions_and_global_phase():
    tape = Tape(1)
    tape.circuit.global_phase = .19
    tape.ry(.1, 0)
    tape.ry(.2, 0)
    tape.measure(0)
    tape.ry(.3, 0)
    tape.ry(.4, 0)
    tape.expval(PauliZ(0))
    child = merge_rotations(tape)[0][0]
    assert child.circuit.global_phase == .19
    assert child.circuit.measurements[0].metadata["operation_index"] == 1
    assert tape.circuit.measurements[0].metadata["operation_index"] == 2
    assert [op.params[0] for op in child.circuit.operations] == pytest.approx([.3, .7])


@pytest.mark.parametrize("axis", ["rx", "ry", "rz", "phase"])
def test_merged_matrix_preserves_complete_unitary(axis):
    from quantumbridge.information import Operator
    tape = Tape(1)
    tape.circuit.global_phase = -.4
    getattr(tape, axis)(.24, 0)
    getattr(tape, axis)(-.73, 0)
    tape.expval(PauliZ(0))
    child = merge_rotations(tape)[0][0]
    np.testing.assert_allclose(Operator.from_circuit(tape.circuit).data, Operator.from_circuit(child.circuit).data, atol=1e-12)


@pytest.mark.parametrize("observable", [np.eye(4), object(), Hamiltonian([(float("nan"), PauliZ(0))]),
                                      Hamiltonian([(1., PauliString([(0,"X"),(0,"Z")]))]),
                                      Hamiltonian([(0., PauliZ(2))])])
def test_invalid_observable_rejected_even_zero_coefficient(observable):
    with pytest.raises((UnsupportedFeature, ValueError)):
        split_hamiltonian(program(observable=observable))


def test_variance_is_not_incorrectly_split_as_linear_expectation():
    tape = Tape(2)
    tape.var(H)
    with pytest.raises(UnsupportedFeature): split_hamiltonian(tape)


def test_no_terminal_measurement_explicitly_rejected():
    with pytest.raises(ValueError, match="terminal"):
        execute_transform(Tape(1), identity)


@pytest.mark.parametrize("transform", [lambda tape: None, lambda tape: ([], None), lambda tape: ([object()], lambda r:r)])
def test_bad_protocol_exposes_stage_context(transform):
    with pytest.raises(TransformError, match="stage 0.*parent 0"):
        execute_transform(program(), transform)


def test_execution_and_postprocessing_failures_expose_context():
    def broken(source):
        def fail(_): raise ValueError("deliberate postprocess failure")
        return (source,), fail
    with pytest.raises(TransformError, match="postprocessing stage 0"):
        execute_transform(program(), broken)
    class BrokenDevice(CountingDevice):
        def expectation(self, circuit, observable): raise ValueError("deliberate device failure")
    with pytest.raises(TransformError, match="execution child 0"):
        execute_transform(program(), identity, BrokenDevice())


def test_unbound_parameters_and_changed_shots_reject_before_execution():
    device = CountingDevice()
    with pytest.raises(ValueError, match="unbound"):
        execute_transform(program(Parameter("p")), split_hamiltonian, device)
    def alter_shots(tape):
        tape.shots = 5
        return (tape,), lambda r:r[0]
    with pytest.raises(TransformError, match="shot"):
        execute_transform(program(), alter_shots, device)
    assert device.calls == []


@pytest.mark.parametrize("kwargs", [{"max_tapes":2}, {"max_operations_per_tape":4},
                                  {"max_total_operations":12}, {"max_expansion_steps":10}])
def test_resource_limits_fail_before_any_child_execution(kwargs):
    device = CountingDevice()
    with pytest.raises(MemoryError):
        execute_transform(program(), split_hamiltonian, device, limits=TransformLimits(**kwargs))
    assert device.calls == []


def test_transform_and_generator_expansion_are_bounded():
    with pytest.raises(MemoryError, match="max_transforms"):
        TransformProgram(repeat(identity), limits=TransformLimits(max_transforms=2))
    consumed = []
    def expand(tape):
        def children():
            for index in range(100):
                consumed.append(index)
                yield tape
        return children(), lambda results:results[0]
    with pytest.raises(MemoryError, match="max_tapes"):
        TransformProgram([expand], limits=TransformLimits(max_tapes=2))(program())
    assert len(consumed) == 3


def test_postprocessing_structure_and_depth_limits():
    def expand_result(tape):
        return (tape,), lambda results: np.zeros(30)
    with pytest.raises(MemoryError, match="max_postprocessing_nodes"):
        execute_transform(program(), expand_result, limits=TransformLimits(max_postprocessing_nodes=20))
    tape = program()
    tree = tape.measurements[0]
    for _ in range(8): tree = [tree]
    tape.set_output(tree)
    with pytest.raises(MemoryError, match="max_structure_depth"):
        TransformProgram([], limits=TransformLimits(max_structure_depth=4))(tape)


def test_empty_program_and_processor_result_count_checks():
    tape = program()
    prepared = TransformProgram().prepare(tape)
    assert prepared.processing_fn((.3,)) == .3
    with pytest.raises(ValueError, match="count"):
        prepared.processing_fn(())
    children, process = split_hamiltonian(tape)
    with pytest.raises(ValueError, match="count"): process((.1,))


@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_limits_validation(value):
    with pytest.raises(ValueError): TransformLimits(max_tapes=value)


def test_set_output_rejects_unrecorded_requests_constants_and_empty_trees():
    tape, other = program(), program()
    for tree in ([], 2, other.measurements[0]):
        with pytest.raises((TypeError, ValueError)): tape.set_output(tree)


def test_legacy_layer_migration_warns_and_retains_explicit_old_alternative():
    from quantumbridge.qml import basic_entangler_layers, hardware_efficient_ansatz
    from quantumbridge.templates import BasicEntanglerLayers
    weights = [[.2, .3, .4]]
    modern, legacy = Circuit(3), Circuit(3)
    with pytest.warns(FutureWarning, match="RY/open-chain"):
        basic_entangler_layers(modern, weights)
    hardware_efficient_ansatz(legacy, weights)
    assert [op.name for op in modern.operations] == ["rx"]*3+["cx"]*3
    assert [op.name for op in legacy.operations] == ["ry"]*3+["cx"]*2
    explicit = BasicEntanglerLayers(weights, wires=range(3)).to_circuit()
    assert explicit.operations == modern.operations


def test_long_rotation_chain_and_unknown_metadata_are_not_dropped():
    from dataclasses import replace
    tape = Tape(1)
    for angle in (.1, .2, .3, .4, .5): tape.ry(angle, 0)
    tape.expval(PauliZ(0))
    child = merge_rotations(tape)[0][0]
    assert len(child.circuit.operations) == 1
    assert child.circuit.operations[0].params == pytest.approx((1.5,))
    tape.circuit.operations[1] = replace(tape.circuit.operations[1], metadata={"custom_semantics": {"retain":True}})
    child = merge_rotations(tape)[0][0]
    assert child.circuit.operations[1].metadata == {"custom_semantics": {"retain":True}}
    assert len(child.circuit.operations) == 3


def test_explicit_child_seed_override_and_source_seed_reproducibility():
    def seeded(tape):
        tape.seed = 8
        return identity(tape)
    _, metadata = execute_transform(program(shots=10), seeded, return_metadata=True)
    assert metadata["executions"][0]["partitions"][0]["seed"] == 8
    first = execute_transform(program(shots=[10, 20]), split_hamiltonian)
    second = execute_transform(program(shots=[10, 20]), split_hamiltonian)
    assert first == second


def test_generated_molecular_hamiltonian_split_matches_unsplit_energy():
    from quantumbridge import qchem
    molecule = qchem.Molecule(["H", "H"], [(0,0,0), (0,0,1.4)], unit="bohr")
    problem = qchem.molecular_hamiltonian_native(molecule)
    tape = Tape(4)
    tape.x(0)
    tape.x(1)
    qchem.apply_fermionic_excitation(tape, .21, [0,1,2,3])
    tape.expval(problem.hamiltonian)
    value, metadata = execute_transform(tape, TransformProgram([split_hamiltonian, merge_rotations]), return_metadata=True)
    expected = StatevectorDevice().expectation(tape.circuit, problem.hamiltonian.to_quantumbridge())
    assert value == pytest.approx(expected, abs=1e-11)
    assert metadata["executed_tape_count"] == len(problem.hamiltonian.terms)
    assert metadata["executed_tape_count"] > 3


def test_dynamic_execution_matches_without_cross_measurement_merges():
    tape = Tape(1)
    tape.ry(.2, 0)
    tape.ry(.3, 0)
    measured = tape.measure(0)
    tape.cond(measured, lambda branch: branch.x(0))
    tape.ry(.1, 0)
    tape.ry(.2, 0)
    tape.expval(PauliZ(0))
    original = execute_transform(tape, identity)
    merged = execute_transform(tape, merge_rotations)
    assert merged == pytest.approx(original, abs=1e-12)


def test_direct_dual_execution_is_explicitly_unsupported():
    tape = program(Dual(.3, [1.]))
    with pytest.raises(UnsupportedFeature, match="B1"):
        execute_transform(tape, identity)


def test_shot_override_has_real_per_child_samples_and_metadata():
    result, metadata = execute_transform(program(), split_hamiltonian, shots=[7, 11], seed=6, return_metadata=True)
    assert isinstance(result, tuple) and len(result) == 2
    assert all([part["shots"] for part in item["partitions"]] == [7,11] for item in metadata["executions"])


def test_invalid_limits_invalid_stage_and_invalid_source():
    with pytest.raises(TypeError): TransformProgram(limits=object())
    with pytest.raises(TypeError): TransformProgram([3])
    with pytest.raises(TypeError): execute_transform(object(), identity)


def test_cyclic_control_body_and_excessive_nesting_are_bounded():
    from quantumbridge.core.classical import bit
    tape = Tape(1)
    tape.circuit.num_bits = 1
    tape.cond(bit(0), lambda child: child.x(0))
    tape.expval(PauliZ(0))
    body = tape.circuit.operations[0].metadata["control_node"].bodies[0]
    body.operations.append(tape.circuit.operations[0])
    with pytest.raises(ValueError, match="Cyclic"):
        TransformProgram([identity])(tape)


def test_processor_cannot_mutate_input_tape_through_captured_reference():
    source = program()
    def capture(tape):
        def process(results):
            tape.circuit.x(0)
            return results[0]
        return (tape,), process
    prepared = TransformProgram([capture]).prepare(source)
    prepared.processing_fn((.2,))
    assert len(source.circuit.operations) == 5


def test_shot_vector_split_processor_checks_partition_count():
    _, processor = split_hamiltonian(program(shots=[2, 3]))
    with pytest.raises(ValueError, match="partition"):
        processor((1., 2., 3.))


def test_structural_output_budget_prevents_nested_stage_growth_before_execution():
    tape = program()
    first = tape.measurements[0]
    tape.set_output([first] * 40)
    device = CountingDevice()
    with pytest.raises(MemoryError, match="max_postprocessing_nodes"):
        execute_transform(tape, identity, device, limits=TransformLimits(max_postprocessing_nodes=20))
    assert device.calls == []


def test_framework_global_phase_and_parameter_bindings_cannot_silently_detach():
    torch = pytest.importorskip("torch")
    x = torch.tensor(.2, dtype=torch.float64, requires_grad=True)
    tape = program()
    with pytest.raises(TypeError, match="global_phase"):
        tape.circuit.global_phase = torch.sin(x)
    # A custom transform can write metadata directly; do not let that bypass
    # the normal Circuit setter's existing trainable-phase rejection.
    tape.circuit.metadata["global_phase"] = torch.sin(x)
    with pytest.raises(UnsupportedFeature, match="B1"):
        execute_transform(tape, identity)
    tape = program(Parameter("p"))
    with pytest.raises(UnsupportedFeature, match="numeric bindings"):
        execute_transform(tape, identity, bindings={"p": x})
