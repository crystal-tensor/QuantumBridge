# Independent behavior scenarios derived from classical/quantum semantics.

import json
import numpy as np
import pytest

from quantumbridge import (Circuit, Parameter, StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice,
    StabilizerDevice, MatrixProductState, ExecutionLimits, Backend, DensityMatrixBackend,
    MatrixProductStateBackend, BackendSamplerV2, BackendEstimatorV2, Result, UnsupportedFeature, transpile)
from quantumbridge.core.classical import UInt, Bool, bit, register, literal, variable, cast, ClassicalExecutionError
from quantumbridge.core.control_flow import ControlBlock, validate_control_flow
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.noise import AmplitudeDampingChannel, BitFlipChannel, NoiseModel, ReadoutError
from quantumbridge.qml import QNode
from quantumbridge.utils.math import PauliX, PauliZ


def assert_all_devices(circuit, expected):
    for device in (StatevectorDevice(), DensityMatrixDevice(), MatrixProductStateDevice(), StabilizerDevice()):
        assert device.run(circuit).probabilities() == pytest.approx(expected, abs=1e-12)


def test_true_branch_really_executes_quantum_gate():
    c = Circuit(1, 1).if_else(True, Circuit(1, 1).x(0)).measure(0, 0)
    assert_all_devices(c, {"1": 1})


def test_false_branch_does_not_execute_true_body():
    c = Circuit(1, 1).if_else(False, Circuit(1, 1).z(0), Circuit(1, 1).x(0)).measure(0, 0)
    assert_all_devices(c, {"1": 1})


def test_false_branch_without_else_is_noop():
    c = Circuit(1, 1).if_test(False, Circuit(1, 1).x(0)).measure(0, 0)
    assert_all_devices(c, {"0": 1})


def test_bit_condition_reads_current_recorded_measurement():
    c = Circuit(2, 2).x(0).measure(0, 0).if_else(bit(0), Circuit(2, 2).x(1)).measure(1, 1)
    assert_all_devices(c, {"11": 1})


def test_register_condition_uses_little_first_listed_bit():
    c = Circuit(1, 3).store(register([2, 0]), 1).if_else(register([2, 0]) == 1, Circuit(1, 3).x(0)).measure(0, 1)
    assert_all_devices(c, {"011": 1})


def test_nested_if_and_else_take_only_the_selected_path():
    body = Circuit(1, 1).if_else(False, Circuit(1, 1).h(0), Circuit(1, 1).x(0))
    c = Circuit(1, 1).if_else(True, body, Circuit(1, 1).h(0)).measure(0, 0)
    assert_all_devices(c, {"1": 1})


def test_condition_is_evaluated_once_before_body_overwrites_it():
    body = Circuit(1, 1).store(bit(0), 1).x(0).store(bit(0), 0).x(0)
    c = Circuit(1, 1).if_else(bit(0) == 0, body, Circuit(1, 1).x(0)).measure(0, 0)
    assert_all_devices(c, {"0": 1})


def test_for_even_and_odd_iteration_parity():
    even = Circuit(1, 1).for_loop(range(4), Circuit(1, 1).x(0)).measure(0, 0)
    odd = Circuit(1, 1).for_loop((2, 5, 8), Circuit(1, 1).x(0)).measure(0, 0)
    assert_all_devices(even, {"0": 1})
    assert_all_devices(odd, {"1": 1})


def test_empty_for_never_enters_body():
    c = Circuit(1, 1).for_loop((), Circuit(1, 1).x(0)).measure(0, 0)
    assert_all_devices(c, {"0": 1})


def test_loop_variable_accumulates_into_captured_outer_storage():
    c = Circuit(1, 1)
    total = c.add_var("total", UInt(4), 0)
    index = variable("i", UInt(4))
    c = c.for_loop(range(4), Circuit(1, 1).store(total, total + index), variable=index)
    c = c.if_else(total == 6, Circuit(1, 1).x(0)).measure(0, 0)
    assert_all_devices(c, {"1": 1})


def test_loop_parameter_binds_quantum_rotations_without_leaking():
    index, theta = Parameter("i"), Parameter("theta")
    c = Circuit(1).for_loop(range(3), index, Circuit(1).ry(index * .2 + theta, 0))
    assert c.parameters == (theta,)
    bound = c.bind({theta: .1})
    expected = np.array([np.cos(.45), np.sin(.45)])
    for device in (StatevectorDevice(), DensityMatrixDevice(), MatrixProductStateDevice()):
        np.testing.assert_allclose(device.density_matrix(bound), np.outer(expected, expected), atol=1e-12)
    with pytest.raises(UnsupportedFeature): StabilizerDevice().run(bound)


def test_for_loop_restores_preexisting_loop_variable():
    c = Circuit(1, 1)
    index = c.add_var("i", UInt(4), 7)
    c = c.for_loop(range(3), Circuit(1, 1).x(0), variable=index)
    c = c.if_else(index == 7, Circuit(1, 1).x(0)).measure(0, 0)
    assert_all_devices(c, {"0": 1})


def test_nested_for_loops_execute_cartesian_iteration_counts():
    inner = Circuit(1, 1).for_loop(range(2), Circuit(1, 1).x(0))
    c = Circuit(1, 1).for_loop(range(3), inner).measure(0, 0)
    assert_all_devices(c, {"0": 1})


def test_while_store_counter_stops_at_runtime_bound():
    c = Circuit(1, 1)
    counter = c.add_var("n", UInt(3), 0)
    c = c.while_loop(counter < 3, Circuit(1, 1).x(0).store(counter, counter + 1)).measure(0, 0)
    assert_all_devices(c, {"1": 1})
    record = MatrixProductStateDevice().run_shots(c, shots=4, memory=True).metadata()["classical_memory"]
    assert [next(iter(store["variables"].values()))["value"] for store in record] == [3] * 4


def test_while_false_condition_skips_body_completely():
    c = Circuit(1, 1).while_loop(False, Circuit(1, 1).x(0)).measure(0, 0)
    assert_all_devices(c, {"0": 1})


def test_runtime_measurement_condition_controls_while_termination():
    c = Circuit(1, 1).store(bit(0), 1)
    c = c.while_loop(bit(0), Circuit(1, 1).x(0).measure(0, 0))
    assert_all_devices(c, {"0": 1})


def test_break_exits_loop_and_skips_remaining_body_instructions():
    c = Circuit(1, 1)
    n = c.add_var("n", UInt(3), 0)
    body = Circuit(1, 1).store(n, n + 1).if_else(n == 2, Circuit(1, 1).break_loop()).x(0)
    c = c.while_loop(n < 5, body).measure(0, 0)
    assert_all_devices(c, {"1": 1})


def test_continue_skips_body_tail_but_runs_next_loop_iteration():
    c = Circuit(1, 1)
    n = c.add_var("n", UInt(3), 0)
    body = Circuit(1, 1).store(n, n + 1).if_else((n & 1) == 1, Circuit(1, 1).continue_loop()).x(0)
    c = c.while_loop(n < 4, body).measure(0, 0)
    assert_all_devices(c, {"0": 1})


def test_break_only_exits_the_innermost_loop():
    inner = Circuit(1, 1).for_loop(range(8), Circuit(1, 1).x(0).break_loop().x(0))
    c = Circuit(1, 1).for_loop(range(3), inner).measure(0, 0)
    assert_all_devices(c, {"1": 1})


def test_switch_multi_value_case_has_no_fallthrough():
    c = Circuit(1, 2).store(register([0, 1]), 2)
    c = c.switch(register([0, 1]), {(0, 2): Circuit(1, 2).x(0), 1: Circuit(1, 2).h(0)}, Circuit(1, 2).h(0)).measure(0, 0)
    assert_all_devices(c, {"11": 1})


def test_switch_default_and_unmatched_no_default():
    c = Circuit(1, 1).switch(literal(3), {1: Circuit(1, 1).h(0)}, Circuit(1, 1).x(0)).measure(0, 0)
    assert_all_devices(c, {"1": 1})
    c = Circuit(1, 1).switch(literal(3), {1: Circuit(1, 1).x(0)}).measure(0, 0)
    assert_all_devices(c, {"0": 1})


def test_nested_switch_and_loop_obey_break_signal():
    body = Circuit(1, 1).switch(literal(0), {0: Circuit(1, 1).x(0).break_loop()}).x(0)
    c = Circuit(1, 1).for_loop(range(5), body).measure(0, 0)
    assert_all_devices(c, {"1": 1})


def test_local_variables_do_not_escape_block_scope():
    body = Circuit(1, 1)
    local = body.add_var("local", UInt(2), 1)
    c = Circuit(1, 1).if_else(True, body).if_else(local == 1, Circuit(1, 1).x(0))
    with pytest.raises(ClassicalExecutionError, match="lexical"): DensityMatrixDevice().run(c)


def test_uninitialized_reads_fail_only_when_executed():
    c = Circuit(1, 1)
    value = c.add_var("pending", UInt(2))
    with pytest.raises(ClassicalExecutionError, match="initialization"):
        DensityMatrixDevice().run(c.if_else(value == 1, Circuit(1, 1).x(0)))
    c = c.if_else(False, Circuit(1, 1).if_else(value == 1, Circuit(1, 1).x(0))).measure(0, 0)
    assert_all_devices(c, {"0": 1})


def test_bell_measurement_feedforward_is_nonselective_not_a_pure_state():
    c = Circuit(2, 1).h(0).cx(0, 1).measure(0, 0).if_else(bit(0), Circuit(2, 1).x(1))
    expected = np.diag([.5, 0, .5, 0])
    for device in (StatevectorDevice(), DensityMatrixDevice(), MatrixProductStateDevice(), StabilizerDevice()):
        np.testing.assert_allclose(device.density_matrix(c), expected, atol=1e-12)
    assert MatrixProductStateDevice().run(c).matrix_product_state() is None


def test_conditional_channel_retains_mixed_initial_state_semantics():
    c = Circuit(1, 1).if_else(True, Circuit(1, 1).channel(AmplitudeDampingChannel(.4), [0]))
    d = DensityMatrixDevice(initial_state=np.diag([.2, .8]))
    np.testing.assert_allclose(d.density_matrix(c), np.diag([.52, .48]), atol=1e-12)
    np.testing.assert_allclose(d.reduced_density_matrix(c, []), [[1]], atol=1e-12)


def test_json_roundtrip_preserves_nested_blocks_and_parameter_asts():
    index, theta = Parameter("i"), Parameter("theta")
    c = Circuit(1, 1)
    n = c.add_var("counter", UInt(3), 0)
    body = Circuit(1, 1).ry(index * theta, 0).store(n, n + 1)
    c = c.for_loop(range(3), index, body).if_else(n == 3, Circuit(1, 1).x(0)).measure(0, 0)
    restored = circuit_from_ir(IRProgram.from_json(c.to_ir().to_json()))
    np.testing.assert_allclose(DensityMatrixDevice().density_matrix(c.bind({theta: .3})), DensityMatrixDevice().density_matrix(restored.bind({"theta": .3})), atol=1e-12)
    node = c.operations[0].metadata["control_node"]
    assert ControlBlock.from_json(node.to_json()).kind == "declare"
    assert Result.from_json(DensityMatrixDevice().run(c.bind({theta: .3})).to_json()).probabilities()


def test_compose_and_instruction_remap_nested_quantum_and_classical_resources():
    child = Circuit(1, 1).store(bit(0), 1).for_loop(range(3), Circuit(1, 1).if_else(bit(0), Circuit(1, 1).x(0))).measure(0, 0)
    composed = Circuit(3, 3).compose(child, qubits=[2], clbits=[1])
    appended = Circuit(3, 3).append(child.to_instruction(), [2], clbits=[1])
    for circuit in (composed, appended):
        assert_all_devices(circuit, {"010": 1})
        np.testing.assert_allclose(DensityMatrixDevice().probabilities(circuit)["001"], 1, atol=1e-12)


def test_analytic_and_shot_branch_budgets_are_not_confused():
    c = Circuit(2, 2).if_else(True, Circuit(2, 2).h(0).h(1).measure_all())
    d = MatrixProductStateDevice(execution_limits=ExecutionLimits(max_branches=2))
    with pytest.raises(ClassicalExecutionError, match="max_branches"): d.run(c)
    assert sum(d.run_shots(c, shots=12, seed=4).counts().values()) == 12


def test_infinite_loop_and_instruction_and_shot_budgets_fail_explicitly():
    c = Circuit(1).while_loop(True, Circuit(1))
    with pytest.raises(ClassicalExecutionError, match="max_loop_iterations"):
        DensityMatrixDevice(execution_limits=ExecutionLimits(max_loop_iterations=3)).run(c)
    with pytest.raises(ClassicalExecutionError, match="instruction budget"):
        MatrixProductStateDevice(execution_limits=ExecutionLimits(max_instruction_executions=2)).run(Circuit(1).for_loop(range(4), Circuit(1).x(0)))
    with pytest.raises(ValueError, match="max_shots"):
        StatevectorDevice(execution_limits=ExecutionLimits(max_shots=2)).run_shots(Circuit(1).if_else(True, Circuit(1)), shots=3)


def test_depth_scoping_and_malformed_ir_are_rejected():
    c = Circuit(1)
    for _ in range(4): c = Circuit(1).if_else(True, c)
    with pytest.raises(ValueError, match="max_control_depth"):
        DensityMatrixDevice(execution_limits=ExecutionLimits(max_control_depth=2)).run(c)
    with pytest.raises(ValueError): validate_control_flow(Circuit(1).break_loop())
    with pytest.raises(ValueError): ControlBlock.from_dict({"version": "bad", "kind": "if", "data": {}})
    with pytest.raises(UnsupportedFeature): ControlBlock("unknown", {})
    with pytest.raises(ValueError): IRProgram.from_dict({"ir_version": "wrong"})
    with pytest.raises(UnsupportedFeature): transpile(c)
    with pytest.raises(UnsupportedFeature): c.depth()


def test_native_qnode_measure_cond_terminal_path_is_callable():
    def program(tape):
        tape.h(0)
        outcome = tape.measure(0)
        tape.cond(outcome, lambda branch: branch.x(1))
        return tape.expval(PauliZ(0)), tape.probs([1]), tape.density_matrix([0, 1])
    for device in (StatevectorDevice(), DensityMatrixDevice(), MatrixProductStateDevice()):
        ev, probs, matrix = QNode(program, 2, device=device)()
        assert ev == pytest.approx(0, abs=1e-12)
        assert probs == pytest.approx({"0": .5, "1": .5})
        np.testing.assert_allclose(matrix, np.diag([.5, 0, 0, .5]), atol=1e-12)


def test_backend_jobs_v2_dynamic_registers_and_exact_estimators():
    c = Circuit(2, 1).h(0).measure(0, 0).if_else(bit(0), Circuit(2, 1).x(1)).reset(0)
    for backend in (Backend(), DensityMatrixBackend(), MatrixProductStateBackend()):
        sampled = BackendSamplerV2(backend, options={"seed_simulator": 8}).run([c], shots=20).result()[0]
        assert sum(sampled.data.meas.get_counts().values()) == 20
        assert sampled.metadata["execution_metadata"][0]["dynamic_control_flow"] is True
        estimated = BackendEstimatorV2(backend).run([(c, [PauliZ(0), PauliZ(1)])], precision=0).result()[0]
        np.testing.assert_allclose(estimated.data.evs, [1, 0], atol=1e-12)


def test_hundred_qubit_mps_measurement_feedforward_never_expands_dense_state(monkeypatch):
    def forbidden(*args, **kwargs): pytest.fail("Dense simulation/expansion attempted")
    monkeypatch.setattr(MatrixProductState, "statevector", forbidden)
    monkeypatch.setattr(StatevectorDevice, "statevector", forbidden)
    monkeypatch.setattr(DensityMatrixDevice, "density_matrix", forbidden)
    c = Circuit(100, 2).h(0)
    for wire in range(99): c.cx(wire, wire + 1)
    c.measure(0, 0)
    c.if_else(bit(0), Circuit(100, 2).x(99), inplace=True).measure(99, 1)
    result = MatrixProductStateDevice(max_memory_mb=2).run_shots(c, shots=12, seed=9, memory=True)
    assert set(result.counts()) <= {"00", "10"}
    assert sum(result.counts().values()) == 12
    assert result.metadata()["max_bond_observed"] == 2


def test_readout_noise_controls_real_branch_choice():
    model = NoiseModel().add_readout_error(0, ReadoutError(1, 0))
    c = Circuit(2, 2).measure(0, 0).if_else(bit(0), Circuit(2, 2).x(1)).measure(1, 1)
    for device in (DensityMatrixDevice(noise_model=model), MatrixProductStateDevice(noise_model=model)):
        assert device.run_shots(c, shots=5, seed=3).counts() == {"11": 5}


def test_quantum_samples_and_counts_follow_dynamic_final_state():
    c = Circuit(2, 1).h(0).measure(0, 0).if_else(bit(0), Circuit(2, 1).x(1)).reset(0)
    for device in (StatevectorDevice(), DensityMatrixDevice(), MatrixProductStateDevice(), StabilizerDevice()):
        samples = device.sample(c, wires=[0, 1], shots=40, seed=4)
        assert set(samples) <= {"00", "01"}
        assert len(samples) == 40
        assert sum(device.counts(c, wires=[1], shots=10, seed=7).values()) == 10
    assert StatevectorDevice().variance(c, PauliZ(0)) == pytest.approx(0, abs=1e-12)


def test_end_of_stream_noise_is_executed_once_and_not_once_per_loop_body():
    c = Circuit(1, 1).for_loop(range(2), Circuit(1, 1).x(0)).measure(0, 0)
    model = NoiseModel().add_channel(BitFlipChannel(1))
    for device in (DensityMatrixDevice(noise_model=model), MatrixProductStateDevice(noise_model=model), StabilizerDevice(noise_model=model)):
        assert device.run(c).probabilities() == pytest.approx({"1": 1})
        assert device.run_shots(c, shots=4).counts() == {"1": 4}


def test_selective_kraus_branches_remain_normalized_in_vector_and_mps():
    c = Circuit(1, 1).if_else(True, Circuit(1, 1).x(0).channel(AmplitudeDampingChannel(.4), [0]))
    for device in (StatevectorDevice(), MatrixProductStateDevice()):
        np.testing.assert_allclose(device.density_matrix(c), np.diag([.4, .6]), atol=1e-12)
        sampled = device.run_shots(c, shots=800, seed=4)
        assert sampled.probabilities().get("0", 0) == pytest.approx(.4, abs=.055)
    with pytest.raises(UnsupportedFeature, match="Kraus"):
        StabilizerDevice().run(c)


def test_tableau_accepts_explicit_clifford_mixture_kraus():
    operators = BitFlipChannel(.3).kraus()
    c = Circuit(1, 1).if_else(True, Circuit(1, 1).kraus(operators, [0])).measure(0, 0)
    assert StabilizerDevice().run(c).probabilities() == pytest.approx({"0": .7, "1": .3})


def test_existing_gate_conditions_are_honored_inside_structured_bodies():
    body = Circuit(1, 1).x(0).c_if(0, 1)
    c = Circuit(1, 1).for_loop(range(2), body).measure(0, 0)
    assert_all_devices(c, {"0": 1})
    conditioned_store = Circuit(1, 1).store(bit(0), 1).c_if(0, 1)
    c = Circuit(1, 1).compose(conditioned_store).measure(0, 0)
    assert_all_devices(c, {"0": 1})


def test_illegal_conditions_case_duplicates_and_loop_values_fail_validation():
    for circuit in (Circuit(1).while_loop(True, Circuit(1).break_loop()).break_loop(),
        Circuit(1).switch(literal(1), [(1, Circuit(1)), (1, Circuit(1))]),
        Circuit(1).for_loop([1.5], Circuit(1))):
        with pytest.raises((ValueError, TypeError)): DensityMatrixDevice().run(circuit)
    with pytest.raises(TypeError): Circuit(1).while_loop(literal(1), Circuit(1))
    with pytest.raises(ValueError): DensityMatrixDevice().run(Circuit(1).for_loop(range(1001), Circuit(1)))


def test_shot_and_loop_storage_isolation_uses_fresh_runtime_initializers():
    c = Circuit(1, 1)
    n = c.add_var("n", UInt(3), 0)
    local_body = Circuit(1, 1)
    local = local_body.add_var("fresh_each_time", UInt(2), 0)
    local_body.store(local, local + 1).store(n, n + cast(local, UInt(3)))
    c = c.for_loop(range(3), local_body).if_else(n == 3, Circuit(1, 1).x(0)).measure(0, 0)
    for device in (StatevectorDevice(), DensityMatrixDevice(), MatrixProductStateDevice()):
        result = device.run_shots(c, shots=6, seed=4, memory=True)
        assert result.counts() == {"1": 6}
        assert all(len(item["variables"]) == 1 for item in result.metadata()["classical_memory"])


def test_malformed_gate_resources_and_unsupported_operations_never_silently_pass():
    with pytest.raises(ValueError, match="Reset"):
        DensityMatrixDevice().run(Circuit(2).if_else(True, Circuit(2).append("reset", [0, 1])))
    with pytest.raises(UnsupportedFeature):
        DensityMatrixDevice().run(Circuit(1).if_else(True, Circuit(1).append("unknown_gate", [0])))
    with pytest.raises(MemoryError):
        StatevectorDevice(max_memory_mb=1).run_shots(Circuit(20).if_else(True, Circuit(20)), shots=1)


def test_vector_analytic_branch_memory_is_guarded_but_trajectories_fit():
    circuit = Circuit(8, 3).if_else(True, Circuit(8, 3).h(0).h(1).h(2))
    for wire in range(3): circuit.measure(wire, wire)
    device = StatevectorDevice(max_memory_mb=.1)
    with pytest.raises(MemoryError, match="branches exceed max_memory_mb"):
        device.run(circuit)
    assert sum(device.run_shots(circuit, shots=3, seed=4).counts().values()) == 3
