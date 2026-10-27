# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent coherent-deferral proofs against native dynamic execution."""

import numpy as np
import pytest

from quantumbridge import DensityMatrixDevice, StatevectorDevice, MatrixProductStateDevice, Circuit
from quantumbridge.qml import QNode
from quantumbridge.qml.tape import Tape
from quantumbridge.core.classical import UnsupportedFeature, bit, cast, UInt
from quantumbridge.core.control_flow import ExecutionLimits
from quantumbridge.transforms import DeferLimits, TransformProgram, TransformLimits, TransformError
from quantumbridge.utils.math import PauliX, PauliY, PauliZ, Hamiltonian
import quantumbridge.transforms as transforms


def same(actual, expected):
    if isinstance(expected, dict):
        assert tuple(actual) == tuple(expected)
        for key in expected: same(actual[key], expected[key])
    elif isinstance(expected, (tuple, list)):
        assert type(actual) is type(expected) and len(actual) == len(expected)
        for left, right in zip(actual, expected): same(left, right)
    else:
        np.testing.assert_allclose(actual, expected, atol=2e-12, rtol=0)


def compare(builder, width=2, args=(), **options):
    original = QNode(builder, width, device=DensityMatrixDevice(), **options)
    deferred = transforms.defer_measurements(QNode(builder, width, **options))
    same(deferred(*args), original(*args))
    return deferred


def raw(builder, width=2):
    tape = Tape(width)
    tape.set_output(builder(tape))
    return tape


def test_reused_measured_wire_keeps_its_old_record_and_reduced_mixed_state():
    def dynamic(tape):
        tape.h(0)
        record = tape.measure(0)
        tape.h(0)
        tape.cond(record, lambda branch: branch.x(1))
        return {"probs": tape.probs([0, 1]), "density": tape.density_matrix([0, 1])}

    def naive(tape):
        tape.h(0)
        tape.h(0)
        tape.cx(0, 1)
        return tape.probs([0, 1])

    reference = QNode(dynamic, 2, device=DensityMatrixDevice())()
    assert reference["probs"] == pytest.approx(dict.fromkeys(("00", "01", "10", "11"), .25))
    assert QNode(naive, 2)()["00"] == pytest.approx(1.)
    node = transforms.defer_measurements(QNode(dynamic, 2, device=StatevectorDevice()))
    actual = node()
    assert actual["probs"] == pytest.approx(reference["probs"], abs=1e-12)
    np.testing.assert_allclose(actual["density"], reference["density"], atol=1e-12)
    child = node._construct((), {}).prepared.tapes[0]
    assert child.circuit.num_qubits == 3
    assert not child.circuit.has_structured_control_flow
    assert not any(operation.name in {"measure", "reset"} for operation in child.circuit.operations)


def test_single_measurement_controls_x_without_reusing_the_wire():
    def circuit(t):
        t.ry(.73, 0)
        m = t.measure(0)
        t.cond(m, lambda b: b.x(1))
        return t.expval(PauliZ(1)), t.density_matrix([1])
    node = compare(circuit)
    assert node.last_metadata["deferred_measurements"][0]["ancilla_count"] == 1


def test_zero_condition_and_else_unitaries_preserve_reduced_density():
    def circuit(t):
        t.h(0)
        m = t.measure(0)
        t.cond(m == 0, lambda b: b.ry(.4, 1), lambda b: b.h(1))
        return t.density_matrix([1, 0]), t.expval(PauliX(1))
    compare(circuit)


def test_inverted_bit_condition_and_complex_y_branch_are_not_lost():
    def circuit(t):
        t.ry(.6, 0)
        m = t.measure(0)
        t.cond(~m, lambda b: b.y(1), lambda b: b.rz(.8, 1))
        return t.density_matrix([0, 1])
    compare(circuit)


def test_two_independent_measurements_keep_distinct_record_wires():
    def circuit(t):
        t.ry(.5, 0)
        first = t.measure(0)
        t.h(0)
        second = t.measure(0)
        t.cond(first, lambda b: b.x(1))
        t.cond(second, lambda b: b.z(1))
        return t.probs([1], records=(first, second)), t.density_matrix([0, 1])
    records = compare(circuit).last_metadata["deferred_measurements"][0]["records"]
    assert [row["ancilla"] for row in records] == [2, 3]
    assert len({row["measurement_id"] for row in records}) == 2


def test_boolean_conditions_join_records_from_different_measured_wires():
    def circuit(t):
        t.h(0)
        t.ry(.62, 1)
        a, b = t.measure(0), t.measure(1)
        t.cond(a ^ b, lambda branch: branch.x(2))
        t.cond(a & b, lambda branch: branch.h(2))
        return t.probs([2], records=(b, a)), t.density_matrix([2])
    compare(circuit, 3)


def test_one_record_is_reused_by_multiple_conditioned_operations():
    def circuit(t):
        t.h(0)
        m = t.measure(0)
        t.cond(m, lambda b: b.x(1))
        t.cond(m, lambda b: b.ry(.31, 1))
        t.cond(m, lambda b: b.rz(.21, 1))
        return t.density_matrix([1])
    dependencies = compare(circuit).last_metadata["deferred_measurements"][0]["control_dependencies"]
    assert len(dependencies) == 3
    assert all(row["record_conditions"] == ((0, 1),) for row in dependencies)


@pytest.mark.parametrize("axis", ["rx", "ry", "rz"])
def test_conditional_rotation_uses_real_controlled_unitaries(axis):
    def circuit(t, angle):
        t.h(0)
        t.h(1)
        m = t.measure(0)
        t.cond(m, lambda b: getattr(b, axis)(angle, 1))
        return t.density_matrix([1]), t.expval(PauliY(1))
    compare(circuit, args=(.43,))


def test_nested_record_conditions_and_existing_controlled_gate_lower_coherently():
    def circuit(t):
        t.h(0)
        t.h(1)
        a, b = t.measure(0), t.measure(1)
        t.cond(a, lambda branch: branch.cond(b, lambda nested: nested.cx(1, 2)))
        return t.density_matrix([2]), t.probs([2], records=(a, b))
    compare(circuit, 3)


@pytest.mark.parametrize("axis", ["rx", "ry", "rz"])
def test_multicontrol_rotation_projectors_keep_complex_density_and_phase(axis):
    def circuit(t, angle):
        t.h(0)
        t.h(1)
        t.h(2)
        a, b = t.measure(0), t.measure(1)
        t.cond(a & b, lambda branch: getattr(branch, axis)(angle, 2))
        return t.density_matrix([2]), t.expval(PauliY(2))
    compare(circuit, 3, (.41,))


def test_default_terminal_wire_selection_does_not_leak_new_ancillas():
    def circuit(t):
        t.h(0)
        t.measure(0)
        return t.probs(), t.density_matrix()
    node = compare(circuit)
    probabilities, density = node()
    assert len(probabilities) == 4 and density.shape == (4, 4)


def test_nested_outputs_and_ordered_logical_wires_survive_deferral():
    def circuit(t):
        t.h(1)
        m = t.measure(1)
        t.cond(m, lambda b: b.ry(.7, 0))
        return {"ordered": [t.probs([1, 0]), (t.expval(PauliZ(0)), t.density_matrix([0]))]}
    compare(circuit)


def test_record_probabilities_and_conditioned_distributions_use_terminal_ancilla_reads():
    def circuit(t):
        t.ry(.8, 0)
        m = t.measure(0)
        t.h(0)
        t.cond(m, lambda b: b.x(1))
        return t.probs(records=m), t.probs([1], records=m)
    node = compare(circuit)
    marginal, joint = node()
    assert joint["01"] == joint["10"] == 0.
    assert joint["00"] == pytest.approx(marginal["0"])
    assert joint["11"] == pytest.approx(marginal["1"])


@pytest.mark.parametrize("device", [StatevectorDevice(), DensityMatrixDevice(), MatrixProductStateDevice()])
def test_original_record_measurements_use_existing_native_dynamic_engine(device):
    def circuit(t):
        t.h(0)
        m = t.measure(0)
        t.cond(m, lambda b: b.x(1))
        return t.probs([1], records=m)
    assert QNode(circuit, 2, device=device)() == pytest.approx({"00": .5, "01": 0., "10": 0., "11": .5})


def test_joint_finite_samples_keep_record_quantum_correlations_and_seed_replay():
    def circuit(t):
        t.h(0)
        m = t.measure(0)
        t.h(0)
        t.cond(m, lambda b: b.x(1))
        return t.sample([1], records=m)
    original = QNode(circuit, 2, shots=503, seed=12)
    node = transforms.defer_measurements(QNode(circuit, 2, shots=503, seed=12))
    for samples in (original(), node()):
        assert len(samples) == 503 and set(samples) <= {"00", "11"}
        assert abs(samples.count("11") / 503 - .5) < .1
    assert node() == node()
    assert node.last_metadata["executions"][0]["partitions"][0]["physical_shots"] == 503


def test_counts_and_sampled_record_probabilities_preserve_shot_vector_partitions():
    def circuit(t):
        t.h(0)
        m = t.measure(0)
        t.cond(m, lambda b: b.x(1))
        return t.counts([1], records=m), t.probs(records=m)
    for node in (QNode(circuit, 2, shots=[100, (200, 2)], seed=19),
                 transforms.defer_measurements(QNode(circuit, 2, shots=[100, (200, 2)], seed=19))):
        value = node()
        assert len(value) == 3
        for (counts, probabilities), shots in zip(value, (100, 200, 200)):
            assert sum(counts.values()) == shots and set(counts) <= {"00", "11"}
            assert sum(probabilities.values()) == pytest.approx(1.)
            assert abs(probabilities["1"] - .5) < .2


def test_static_branch_and_source_global_phase_match_the_full_coherent_purification():
    def circuit(t):
        t.circuit.global_phase = .21
        t.h(0)
        m = t.measure(0)
        def branch(b):
            b.circuit.global_phase = .37
            b.h(1)
        t.cond(m, branch)
        return t.probs([0, 1])
    tape = raw(circuit)
    child = transforms.defer_measurements(tape)[0][0].circuit
    reference = Circuit(3).h(0).cx(0, 2).append("ch", (2, 1)).phase(.37, 2)
    reference.global_phase = .21
    np.testing.assert_allclose(StatevectorDevice().statevector(child), StatevectorDevice().statevector(reference), atol=1e-12)
    compare(circuit)


def test_parameterized_branch_phase_is_preserved_without_binding_away_its_graph():
    from quantumbridge.core import Parameter
    phase = Parameter("phase")
    def circuit(t):
        t.h(0)
        m = t.measure(0)
        def branch(b):
            b.circuit.global_phase = phase
            b.x(1)
        t.cond(m, branch)
        return t.probs([0, 1])
    child = transforms.defer_measurements(raw(circuit))[0][0].circuit
    assert phase in child.parameters
    for value in (-.4, .2, 1.7):
        reference = Circuit(3).h(0).cx(0, 2).cx(2, 1).phase(value, 2)
        np.testing.assert_allclose(StatevectorDevice().statevector(child.bind({phase: value})), StatevectorDevice().statevector(reference), atol=1e-12)


def test_bounded_opaque_unitary_is_controlled_without_global_matrix_expansion():
    def circuit(t):
        t.h(0)
        m = t.measure(0)
        t.cond(m, lambda b: b.circuit.unitary(np.array([[0, 1j], [1j, 0]]), [1]))
        return t.density_matrix([1])
    compare(circuit)


@pytest.mark.parametrize("name,arity,angles", [
    ("id", 1, ()), ("h", 1, ()), ("x", 1, ()), ("y", 1, ()), ("z", 1, ()),
    ("s", 1, ()), ("sdg", 1, ()), ("t", 1, ()), ("tdg", 1, ()),
    ("sx", 1, ()), ("sxdg", 1, ()), ("u3", 1, (.4, .7, -.2)),
    ("phase", 1, (.43,)), ("rx", 1, (.43,)), ("ry", 1, (.43,)), ("rz", 1, (.43,)),
    ("cx", 2, ()), ("cy", 2, ()), ("cz", 2, ()), ("ch", 2, ()),
    ("crx", 2, (.43,)), ("cry", 2, (.43,)), ("crz", 2, (.43,)),
    ("cphase", 2, (.43,)), ("global_phase", 1, (.43,)),
    ("csx", 2, ()), ("csxdg", 2, ()), ("swap", 2, ()), ("ccx", 3, ()), ("cswap", 3, ()),
    ("rxx", 2, (.43,)), ("ryy", 2, (.43,)), ("rzz", 2, (.43,)),
])
def test_controlled_lowering_matches_complete_complex_unitary_without_phase_alignment(name, arity, angles):
    from quantumbridge.utils.math import gate_matrix
    width = arity + 1
    def circuit(t):
        t.ry(.37, 0)
        for wire in range(1, width):
            t.ry(.3 + wire * .1, wire)
            t.rz(.2, wire)
        m = t.measure(0)
        t.cond(m, lambda b: b.circuit.append(name, range(1, width), params=angles))
        return t.probs(list(range(width)))
    source = raw(circuit, width)
    child = transforms.defer_measurements(source)[0][0].circuit
    reference = Circuit(width + 1)
    reference.operations = list(source.circuit.operations[:-1])
    reference.cx(0, width)
    matrix = gate_matrix(name, angles)
    dimension = len(matrix)
    exact_controlled = np.block([[np.eye(dimension), np.zeros_like(matrix)], [np.zeros_like(matrix), matrix]])
    reference.unitary(exact_controlled, [width] + list(range(1, width)))
    np.testing.assert_allclose(StatevectorDevice().statevector(child), StatevectorDevice().statevector(reference), atol=2e-12, rtol=0)


def test_native_compiler_routes_record_ancilla_and_restores_output_layout():
    from quantumbridge.compiler import Target
    target = Target(3, basis_gates=("rx", "ry", "rz", "cx"), coupling_map=((0, 1), (1, 0), (1, 2), (2, 1)))
    def circuit(t):
        t.h(0)
        m = t.measure(0)
        t.h(0)
        t.cond(m, lambda b: b.x(1))
        return t.probs([0, 1])
    node = TransformProgram((transforms.defer_measurements, transforms.compile(target=target)))(QNode(circuit, 2))
    same(node(), QNode(circuit, 2)())
    assert node.last_metadata["deferred_measurements"][0]["transformed_wires"] == 3


def test_deferral_is_fresh_and_does_not_mutate_source_tape_or_ancilla_mapping():
    def circuit(t):
        t.h(0)
        t.measure(0)
        t.measure(1)
        return t.probs([1])
    tape = raw(circuit)
    first = transforms.defer_measurements(tape, ancilla_wires=(3, 2))[0][0]
    second = transforms.defer_measurements(tape)[0][0]
    assert tape.circuit.num_qubits == 2 and len(tape.circuit.measurements) == 2
    assert first.circuit.metadata["deferred_measurements"]["records"][0]["ancilla"] == 3
    assert second.circuit.metadata["deferred_measurements"]["records"][0]["ancilla"] == 2


@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
def test_first_deferred_gradient_is_computed_on_the_actual_coherent_child(method):
    def circuit(t, angle):
        t.ry(angle, 0)
        m = t.measure(0)
        t.cond(m, lambda b: b.x(1))
        return t.expval(PauliZ(1))
    node = transforms.defer_measurements(QNode(circuit, 2, diff_method=method))
    assert node.gradient(.37) == pytest.approx(-np.sin(.37), abs=1e-12)
    assert node.gradient(.37) == pytest.approx(QNode(circuit, 2, diff_method="parameter-shift").gradient(.37), abs=1e-12)
    assert node.last_metadata["gradient_method"] == method
    assert node.last_metadata["postprocessing_chain_rule"]


def test_conditional_angle_gradient_includes_shared_nonlinear_source_chain():
    def circuit(t, angle, *, offset):
        t.ry(angle, 0)
        m = t.measure(0)
        t.cond(m, lambda b: b.ry(np.sin(angle) + offset, 1))
        return t.expval(PauliZ(1))
    x, offset = .37, .2
    expected = -.5*np.sin(x)*(1-np.cos(np.sin(x)+offset)) - .5*(1-np.cos(x))*np.sin(np.sin(x)+offset)*np.cos(x)
    node = transforms.defer_measurements(QNode(circuit, 2))
    assert node.gradient(x, offset=offset) == pytest.approx(expected, abs=1e-12)


def test_torch_backward_reaches_deferred_gate_angles_and_coefficient_slots():
    torch = pytest.importorskip("torch")
    def circuit(t, x):
        t.ry(x, 0)
        m = t.measure(0)
        t.cond(m, lambda b: b.x(1))
        return t.expval(Hamiltonian([(x, PauliZ(1))]))
    node = transforms.split_non_commuting(transforms.defer_measurements(QNode(circuit, 2)))
    x = torch.tensor(.37, dtype=torch.float64, requires_grad=True)
    node(x).backward()
    assert x.grad.item() == pytest.approx(np.cos(.37)-.37*np.sin(.37), abs=1e-12)
    assert node.last_metadata["native_vjp"]


def test_autograd_keyword_gradient_is_not_borrowed_from_original_dynamic_node():
    autograd = pytest.importorskip("autograd")
    import autograd.numpy as anp
    def circuit(t, x, *, offset):
        t.ry(anp.sin(x)+offset, 0)
        m = t.measure(0)
        t.cond(m, lambda b: b.x(1))
        return t.expval(PauliZ(1))
    node = transforms.defer_measurements(QNode(circuit, 2))
    assert autograd.grad(lambda x: node(x, offset=.2))(.37) == pytest.approx(-np.sin(np.sin(.37)+.2)*np.cos(.37), abs=1e-12)


def test_multitape_defer_and_qwc_nested_vjp_preserve_original_output_order():
    def circuit(t, x):
        t.ry(x, 0)
        m = t.measure(0)
        t.cond(m, lambda b: b.x(1))
        return {"z": t.expval(PauliZ(1)), "x": [t.expval(PauliX(1))]}
    node = TransformProgram((transforms.split_to_single_terms, transforms.defer_measurements, transforms.split_non_commuting))(QNode(circuit, 2))
    assert node.compute_vjp({"z": 2., "x": [3.]}, .37) == pytest.approx(-2*np.sin(.37), abs=1e-12)
    assert len(node.last_metadata["deferred_measurements"]) == 2


def test_record_probability_gradient_is_a_real_deferred_observable_derivative():
    def circuit(t, x):
        t.ry(x, 0)
        m = t.measure(0)
        t.h(0)
        return t.probs(records=m)
    node = transforms.defer_measurements(QNode(circuit, 1))
    same(node.jacobian(.37), {"0": -.5*np.sin(.37), "1": .5*np.sin(.37)})


def test_torch_gradcheck_and_vector_cotangent_follow_deferred_controlled_rotations():
    torch = pytest.importorskip("torch")
    def circuit(t, x):
        t.ry(x[0], 0)
        m = t.measure(0)
        t.cond(m, lambda b: b.ry(x[1], 1))
        return (t.expval(PauliZ(1)), t.expval(PauliX(1)))
    node = transforms.defer_measurements(QNode(circuit, 2, diff_method="adjoint"))
    x = torch.tensor([.37, .4], dtype=torch.float64, requires_grad=True)
    assert torch.autograd.gradcheck(node, (x,))
    outputs = node(x)
    actual = torch.autograd.grad(outputs, x, grad_outputs=(torch.tensor(2.), torch.tensor(3.)))[0]
    p = .5*(1-np.cos(.37))
    expected = [.5*np.sin(.37)*(2*(np.cos(.4)-1)+3*np.sin(.4)), p*(-2*np.sin(.4)+3*np.cos(.4))]
    np.testing.assert_allclose(actual.detach().numpy(), expected, atol=1e-12)


def test_raw_parameter_binding_and_callable_dispatch_use_the_same_coherent_execution():
    from quantumbridge.core import Parameter
    parameter = Parameter("theta")
    def circuit(t, angle):
        t.ry(angle, 0)
        m = t.measure(0)
        t.cond(m, lambda b: b.x(1))
        return t.expval(PauliZ(1))
    tape = raw(lambda t: circuit(t, parameter))
    value, metadata = transforms.execute_transform(tape, transforms.defer_measurements,
        bindings={parameter: .37}, return_metadata=True)
    assert value == pytest.approx(np.cos(.37), abs=1e-12)
    assert metadata["deferred_measurements"][0]["ancilla_count"] == 1
    configured = transforms.defer_measurements(qnode_options={"num_qubits": 2})(circuit)
    assert configured.gradient(.37) == pytest.approx(-np.sin(.37), abs=1e-12)


def test_control_depth_boolean_width_and_conditional_side_effects_are_bounded():
    def nested(t):
        a = t.measure(0)
        b = t.measure(1)
        t.cond(a, lambda branch: branch.cond(b, lambda child: child.x(0)))
        return t.probs([0])
    with pytest.raises(MemoryError, match="max_transform_depth"):
        transforms.defer_measurements(raw(nested), defer_limits=DeferLimits(max_transform_depth=1))
    def boolean(t):
        a, b = t.measure(0), t.measure(1)
        t.cond(a & b, lambda branch: branch.x(0))
        return t.probs([0])
    with pytest.raises(MemoryError, match="max_controls"):
        transforms.defer_measurements(raw(boolean), defer_limits=DeferLimits(max_controls=1))
    tape = raw(lambda t: (t.measure(0), t.probs([0]))[1])
    tape.circuit.append("x", [1], metadata={"condition": {"bits": [0], "value": 1}, "requires_zero_input": True})
    with pytest.raises(UnsupportedFeature, match="conditional_gate_metadata"):
        transforms.defer_measurements(tape)


def test_ancilla_aliases_gaps_and_capacity_fail_before_execution():
    tape = raw(lambda t: (t.measure(0), t.probs([0]))[1])
    for wires in ((0,), (3,), (True,), (), (2, 2)):
        with pytest.raises(ValueError, match="Ancilla"):
            transforms.defer_measurements(tape, ancilla_wires=wires)
    with pytest.raises(MemoryError, match="max_ancillas"):
        transforms.defer_measurements(tape, max_ancillas=0)
    for capacity in (-1, True, 1.5):
        with pytest.raises(ValueError): transforms.defer_measurements(tape, max_ancillas=capacity)


def test_device_target_width_and_instruction_limits_include_record_wires():
    def circuit(t):
        t.h(0)
        m = t.measure(0)
        t.cond(m, lambda b: b.x(1))
        return t.expval(PauliZ(1))
    with pytest.raises(ValueError, match="additional device wires"):
        transforms.defer_measurements(QNode(circuit, 2, device=StatevectorDevice(max_qubits=2)))()
    with pytest.raises(MemoryError, match="execution limits"):
        transforms.defer_measurements(QNode(circuit, 2, device=StatevectorDevice(execution_limits=ExecutionLimits(max_instruction_executions=2))))()
    from quantumbridge.compiler import Target
    with pytest.raises((ValueError, TransformError)):
        TransformProgram((transforms.defer_measurements, transforms.compile(target=Target(2, basis_gates=("h", "cx")))))(QNode(circuit, 2))()


def test_measurement_count_depth_and_transformed_expansion_limits_preflight():
    def two(t):
        t.measure(0)
        t.measure(1)
        return t.probs([0])
    with pytest.raises(MemoryError, match="max_mid_measurements"):
        transforms.defer_measurements(raw(two), defer_limits=DeferLimits(max_mid_measurements=1))
    def expanded(t):
        m = t.measure(0)
        t.cond(m, lambda b: b.h(1))
        return t.probs([1])
    with pytest.raises(MemoryError, match="max_controlled_gate_expansion"):
        transforms.defer_measurements(raw(expanded), defer_limits=DeferLimits(max_controlled_gate_expansion=1))
    with pytest.raises(MemoryError, match="max_transformed_operations"):
        transforms.defer_measurements(raw(expanded), defer_limits=DeferLimits(max_transformed_operations=1))
    with pytest.raises(MemoryError, match="max_operations_per_tape"):
        transforms.defer_measurements(raw(expanded), limits=TransformLimits(max_operations_per_tape=2))


def test_reset_and_all_postselection_forms_are_explicitly_unsupported():
    def reset(t):
        t.measure(0, reset=True)
        return t.probs([0])
    with pytest.raises(UnsupportedFeature, match="nonunitary"):
        transforms.defer_measurements(raw(reset))
    for postselect in (0, 1):
        tape = raw(lambda t: (t.measure(0), t.probs([0]))[1])
        tape.circuit.measurements[0].metadata["postselect"] = postselect
        with pytest.raises(UnsupportedFeature, match="postselection"):
            transforms.defer_measurements(tape)
    with pytest.raises(UnsupportedFeature, match="postselection"):
        transforms.defer_measurements(raw(lambda t: t.probs([0])), allow_postselect=True)


def test_noisy_feedback_and_nonzero_ancilla_initialization_are_rejected():
    from quantumbridge.noise import NoiseModel
    def circuit(t):
        t.measure(0)
        return t.probs([0])
    for device in (DensityMatrixDevice(noise_model=NoiseModel()),
                   MatrixProductStateDevice(noise_model=NoiseModel()),
                   DensityMatrixDevice(initial_state=np.diag([1., 0., 0., 0.]))):
        with pytest.raises(UnsupportedFeature, match="noisy_device"):
            transforms.defer_measurements(QNode(circuit, 2, device=device))()


def test_kraus_nonunitary_matrices_snapshots_and_undefined_full_state_fail():
    def invalid(t, kind):
        t.measure(0)
        if kind == "kraus": t.kraus([np.eye(2)], [1])
        if kind == "matrix": t.circuit.append("nonunitary", [1], metadata={"matrix": np.diag([1., .5])})
        if kind == "snapshot": t.circuit.save_statevector()
        return t.state() if kind == "state" else t.probs([0])
    for kind in ("kraus", "matrix", "snapshot", "state"):
        with pytest.raises(UnsupportedFeature): transforms.defer_measurements(raw(lambda t: invalid(t, kind)))
    tape = raw(lambda t: (t.measure(0), t.expval(np.eye(4)))[1])
    with pytest.raises(UnsupportedFeature, match="dense_observable"):
        transforms.defer_measurements(tape)


def test_unsupported_loops_store_arithmetic_and_undefined_values_do_not_silently_run():
    def undefined(t):
        from quantumbridge import Clbit
        t.circuit.add_bits([Clbit()])
        t.cond(bit(0), lambda b: b.x(1))
        return t.probs([1])
    with pytest.raises(UnsupportedFeature, match="undefined_measurement"):
        transforms.defer_measurements(raw(undefined))
    def loop(t):
        m = t.measure(0)
        t.circuit.while_loop(m, Circuit(2, 1).x(1), inplace=True)
        return t.probs([1])
    with pytest.raises(UnsupportedFeature, match="dynamic_loops"):
        transforms.defer_measurements(raw(loop))
    def arithmetic(t):
        m = t.measure(0)
        t.cond((cast(m, UInt(3)) + 1) == 2, lambda b: b.x(1))
        return t.probs([1])
    with pytest.raises(UnsupportedFeature, match="classical_arithmetic"):
        transforms.defer_measurements(raw(arithmetic))
    def store(t):
        m = t.measure(0)
        t.circuit.store(m, 1)
        return t.probs([1])
    with pytest.raises(UnsupportedFeature, match="classical_store"):
        transforms.defer_measurements(raw(store))


def test_record_shadowing_duplicate_ids_and_conditional_measurements_are_rejected():
    tape = raw(lambda t: (t.measure(0), t.probs([0]))[1])
    tape.circuit.measure(1, 0)
    with pytest.raises(UnsupportedFeature, match="shadowing"):
        transforms.defer_measurements(tape)
    tape = raw(lambda t: (t.measure(0), t.measure(1), t.probs([0]))[2])
    for measurement in tape.circuit.measurements: measurement.metadata["measurement_id"] = "duplicate"
    with pytest.raises(UnsupportedFeature, match="identity_alias"):
        transforms.defer_measurements(tape)
    def conditional(t):
        m = t.measure(0)
        t.cond(m, lambda b: b.measure(1))
        return t.probs([1])
    with pytest.raises(UnsupportedFeature, match="inside_conditional"):
        transforms.defer_measurements(raw(conditional))


def test_unmapped_record_requests_and_controlled_opaque_parameter_graphs_reject():
    from quantumbridge.core import Parameter
    tape = raw(lambda t: (t.measure(0), t.probs(records=bit(4)))[1])
    with pytest.raises(UnsupportedFeature, match="terminal_records"):
        transforms.defer_measurements(tape)
    def opaque(t):
        m = t.measure(0)
        t.cond(m, lambda b: b.circuit.append("opaque", [1], params=(Parameter("x"),), metadata={"matrix": np.eye(2)}))
        return t.probs([1])
    with pytest.raises(UnsupportedFeature, match="parameterized_opaque"):
        transforms.defer_measurements(raw(opaque))
    def unsupported(t):
        m = t.measure(0)
        t.cond(m, lambda b: b.circuit.append("not_a_supported_gate", [1]))
        return t.probs([1])
    with pytest.raises(UnsupportedFeature, match="algebraic decomposition"):
        transforms.defer_measurements(raw(unsupported))


def test_sampling_and_opaque_control_matrix_budgets_apply_before_allocation():
    def sampled(t):
        m = t.measure(0)
        return t.sample([1], shots=100, records=m)
    with pytest.raises(MemoryError, match="max_sample_values"):
        transforms.defer_measurements(raw(sampled), limits=TransformLimits(max_sample_values=100))
    def opaque(t):
        m = t.measure(0)
        t.cond(m, lambda b: b.circuit.unitary(np.eye(4), [1, 2]))
        return t.probs([1])
    with pytest.raises(MemoryError, match="max_matrix_qubits"):
        transforms.defer_measurements(raw(opaque, 3), defer_limits=DeferLimits(max_matrix_qubits=2))


def test_invalid_deferral_configuration_and_postprocessor_result_count_are_checked():
    tape = raw(lambda t: t.probs([0]))
    with pytest.raises(TypeError): transforms.defer_measurements(tape, defer_limits={})
    with pytest.raises(TypeError): transforms.defer_measurements(tape, allow_postselect=1)
    with pytest.raises(ValueError): DeferLimits(max_controls=True)
    _, process = transforms.defer_measurements(tape)
    with pytest.raises(ValueError): process(())
    with pytest.raises(ValueError): process((1., 2.))


def test_record_measurement_requests_reject_aliases_expressions_and_oversized_outputs():
    t = Tape(2)
    m = t.measure(0)
    with pytest.raises(ValueError, match="aliases"): t.probs(records=(m, m))
    with pytest.raises(TypeError, match="bit references"): t.sample(records=m == 0)
    def unbound(t): return t.probs(records=bit(4))
    with pytest.raises(ValueError, match="outside"): QNode(unbound, 2)()
    from itertools import repeat
    with pytest.raises(MemoryError, match="16 bits"): t.probs(records=repeat(m))
    with pytest.raises(ValueError, match="Ancilla"):
        transforms.defer_measurements(raw(lambda t: (t.measure(0), t.probs([0]))[1]), ancilla_wires=repeat(2))


def test_measurement_dependent_gate_angles_and_oversized_classical_storage_reject():
    def circuit(t):
        m = t.measure(0)
        t.circuit.ry(m, 1)
        return t.probs([1])
    with pytest.raises(UnsupportedFeature, match="measurement_dependent_gate_parameter"):
        transforms.defer_measurements(raw(circuit))
    def too_wide(t):
        m = t.measure(0)
        t.circuit.num_bits = 100001
        return t.probs(records=m)
    with pytest.raises(MemoryError, match="max_circuit_bits"):
        QNode(too_wide, 2)()


def test_invalid_logical_output_wire_cannot_become_a_valid_new_record_ancilla():
    for kind in ("probs", "observable"):
        def circuit(t):
            t.measure(0)
            return t.probs([2]) if kind == "probs" else t.expval(PauliZ(2))
        with pytest.raises(ValueError, match="outside"):
            transforms.defer_measurements(raw(circuit))


def test_malformed_control_body_cannot_capture_a_new_record_wire():
    from quantumbridge.core.control_flow import ControlBlock
    tape = raw(lambda t: (t.measure(0), t.probs([0]))[1])
    body = Circuit(3, 1).x(2)
    tape.circuit.append("control_flow", (), metadata={"control_node": ControlBlock("if", {
        "condition": bit(0), "body": body, "alternate": None})})
    with pytest.raises(ValueError, match="resource map"):
        transforms.defer_measurements(tape)


def test_reapplying_deferral_keeps_the_original_record_resource_receipt():
    tape = raw(lambda t: (t.measure(0), t.probs([0]))[1])
    first = transforms.defer_measurements(tape)[0][0]
    second = transforms.defer_measurements(first)[0][0]
    assert first.circuit.metadata["deferred_measurements"] == second.circuit.metadata["deferred_measurements"]
    assert second.circuit.num_qubits == 3 and not second.circuit.measurements


def test_explicit_unsupported_derivative_methods_never_fall_back_after_deferral():
    def circuit(t, x):
        t.ry(x, 0)
        m = t.measure(0)
        t.cond(m, lambda b: b.x(1))
        return t.expval(PauliZ(1))
    with pytest.raises(UnsupportedFeature, match="backprop"):
        transforms.defer_measurements(QNode(circuit, 2, diff_method="backprop")).gradient(.37)
    with pytest.raises(UnsupportedFeature, match="Adjoint"):
        transforms.defer_measurements(QNode(circuit, 2, device=MatrixProductStateDevice(), diff_method="adjoint")).gradient(.37)


class SampleSpy(StatevectorDevice):
    def __init__(self):
        super().__init__()
        self.calls = []

    def sample(self, circuit, wires=None, shots=1, seed=None, parameters=None):
        result = super().sample(circuit, wires, shots, seed, parameters)
        self.calls.append((shots, seed, tuple(result)))
        return result


@pytest.mark.parametrize("policy", [None, "uniform", "weighted"])
def test_defer_qwc_allocation_and_gradient_receipts_count_actual_joint_samples(policy):
    def circuit(t, x):
        t.ry(x, 0)
        m = t.measure(0)
        t.h(0)
        t.cond(m, lambda b: b.x(1))
        return t.expval(Hamiltonian([(1., PauliZ(1)), (.3, PauliX(1))]))
    spy = SampleSpy()
    node = transforms.split_non_commuting(transforms.defer_measurements(QNode(circuit, 2, device=spy, shots=301, seed=31, diff_method="parameter-shift")), shot_dist=policy)
    assert abs(node.gradient(.37) + np.sin(.37)) < .25
    expected = 2408 if policy is None else 1204
    assert sum(row[0] for row in spy.calls) == node.last_metadata["gradient_physical_shots"] == expected
    assert len(node.last_metadata["deferred_measurements"]) == 2
    assert all(row["ancilla_count"] == 1 and row["transformed_wires"] == 3 for row in node.last_metadata["deferred_measurements"])
    groups = [part["joint_measurements"][0] for child in node.last_metadata["gradient_executions"]
              for run in child["gradient_evaluations"] for part in run.get("partitions", ())]
    assert len({row["execution_id"] for row in groups}) == len(spy.calls)
    assert all(row["joint_sample_calls"] == 1 and len(row["bitstrings"]) == row["shots"] for row in groups)


def test_defer_qwc_analytic_covariance_matches_the_original_dynamic_observables():
    def circuit(t, x):
        t.ry(x, 0)
        m = t.measure(0)
        t.h(0)
        t.cond(m, lambda b: b.x(1))
        return t.expval(Hamiltonian([(1., PauliZ(1)), (.2, PauliX(0))]))
    original = transforms.split_non_commuting(QNode(circuit, 2))
    deferred = transforms.split_non_commuting(transforms.defer_measurements(QNode(circuit, 2)))
    assert deferred(.37) == pytest.approx(original(.37), abs=1e-12)
    group = deferred.last_metadata["executions"][0]["partitions"][0]["joint_measurements"][0]
    np.testing.assert_allclose(group["means"], [np.cos(.37)]*2, atol=1e-12)
    np.testing.assert_allclose(group["covariance"], np.full((2, 2), np.sin(.37)**2), atol=1e-12)


def test_defer_qwc_shot_vector_gradient_keeps_each_partition_and_real_work():
    def circuit(t, x):
        t.ry(x, 0)
        m = t.measure(0)
        t.cond(m, lambda b: b.x(1))
        return t.expval(PauliZ(1))
    spy = SampleSpy()
    node = transforms.split_non_commuting(transforms.defer_measurements(QNode(circuit, 2, device=spy, shots=[100, (200, 2)], seed=17, diff_method="parameter-shift")))
    derivative = node.jacobian(.37)
    assert len(derivative) == 3 and max(abs(value + np.sin(.37)) for value in derivative) < .3
    assert sum(row[0] for row in spy.calls) == node.last_metadata["gradient_physical_shots"] == 2000


def test_hundred_qubit_deferred_mps_template_gradient_uses_101_real_wires_no_dense(monkeypatch):
    from quantumbridge import templates
    from quantumbridge.information.matrix_product_state import MatrixProductState
    def forbidden(*args, **kwargs): raise AssertionError("Dense expansion forbidden")
    for target, name in ((StatevectorDevice, "statevector"), (DensityMatrixDevice, "density_matrix"),
                         (MatrixProductState, "statevector"), (MatrixProductState, "reduced_density_matrix")):
        monkeypatch.setattr(target, name, forbidden)
    def circuit(t, x):
        t.h(0)
        for wire in range(99): t.cx(wire, wire + 1)
        m = t.measure(0)
        t.h(0)
        t.cond(m, lambda b: b.x(99))
        templates.AngleEmbedding([x], [99], rotation="Y").apply(t)
        return t.expval(PauliZ(99))
    device = MatrixProductStateDevice(max_qubits=101, max_memory_mb=2, max_bond_dim=4, cutoff=0)
    node = TransformProgram((transforms.defer_measurements, transforms.merge_rotations, transforms.split_non_commuting))(QNode(circuit, 100, device=device, diff_method="parameter-shift"))
    energy, gradient = node.execute_and_compute_derivatives(.3)
    assert energy == pytest.approx(np.cos(.3), abs=1e-11)
    assert gradient == pytest.approx(-np.sin(.3), abs=1e-10)
    receipt = node.last_metadata["deferred_measurements"][0]
    assert (receipt["logical_wires"], receipt["transformed_wires"], receipt["ancilla_count"]) == (100, 101, 1)
    resources = node.last_metadata["executions"][0]["partitions"][0]["resources"]
    assert resources["max_bond_observed"] <= 4 and resources["max_discarded_weight"] == 0
    assert resources["max_tensor_bytes"] < 20000 and resources["max_truncations"] == 0
    assert node.last_metadata["shifted_evaluation_count"] == 2
    assert node.last_metadata["transform_count"] == 3 and node.last_metadata["total_physical_shots"] == 0


@pytest.fixture(scope="module")
def native_h2():
    from quantumbridge import qchem
    return qchem.molecular_hamiltonian_native(qchem.Molecule(["H", "H"], [(0, 0, 0), (0, 0, 1.4)], unit="bohr"))


def test_geometry_h2_defer_qwc_gradient_reuses_integrals_and_matches_dynamic_energy(native_h2, monkeypatch):
    from quantumbridge import qchem
    def forbidden(*args, **kwargs): raise AssertionError("Fixed-geometry integrals rebuilt in child/gradient")
    monkeypatch.setattr(qchem, "molecular_hamiltonian_native", forbidden)
    def circuit(t, x):
        t.x(0)
        t.x(1)
        qchem.apply_fermionic_excitation(t, x, [0, 1, 2, 3])
        m = t.measure(0)
        t.h(0)
        t.cond(m, lambda b: b.ry(.2, 2))
        return t.expval(native_h2.hamiltonian)
    original = QNode(circuit, 4, diff_method="parameter-shift")
    node = transforms.split_non_commuting(transforms.defer_measurements(QNode(circuit, 4)))
    assert node(.3) == pytest.approx(original(.3), abs=2e-11)
    assert node.gradient(.3) == pytest.approx(original.gradient(.3), abs=2e-10)
    first, x = node(.3), .3
    for _ in range(2): x -= .2 * node.gradient(x)
    assert node(x) < first - 1e-4
    assert node(x) == pytest.approx(original(x), abs=2e-11)
