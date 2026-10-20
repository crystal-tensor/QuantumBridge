# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Actual sampling, independent seeds and bounded execution contracts.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ, StatevectorDevice, UnsupportedFeature
from quantumbridge.interfaces import TensorFlowBridgeLimits
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def framework(): return pytest.importorskip("tensorflow")


def sampled(shots=2001, seed=17, distribution=None, **options):
    def circuit(t, x):
        t.ry(x, 0)
        return t.expval(Hamiltonian([(.7, PauliX(0)), (.2, PauliZ(0))]))
    return split_non_commuting(shot_dist=distribution)(QNode(circuit, 1, interface="tf", diff_method="parameter-shift", shots=shots, seed=seed, **options))


def value_grad(node):
    tf = framework()
    x = tf.Variable(.37, dtype=tf.float64)
    with tf.GradientTape() as recording:
        value = node(x)
        loss = tf.add_n(list(value)) if isinstance(value, tuple) else value
    return value, recording.gradient(loss, x)


def test_real_finite_shot_value_and_gradient_are_estimates():
    node = sampled()
    value, grad = value_grad(node)
    np.testing.assert_allclose([value, grad], [.7*np.sin(.37)+.2*np.cos(.37), .7*np.cos(.37)-.2*np.sin(.37)], atol=.06, rtol=0)
    assert node.last_metadata["gradient_semantics"] == "finite-shot estimate"
    assert node.last_metadata["observed_physical_shots"] == 10*2001
    assert node.last_metadata["forward_execution"]["forward_physical_shots"] == 2*2001
    assert node.last_metadata["gradient_physical_shots"] == 8*2001


def test_seed_repeated_calls_are_reproducible_not_shared_mutable_rng():
    node = sampled(shots=101)
    first, second = value_grad(node), value_grad(node)
    np.testing.assert_array_equal(first, second)
    values = [float(value_grad(sampled(shots=101, seed=seed))[0]) for seed in [17, 18, 19]]
    assert len(set(values)) > 1


def test_shift_group_streams_are_distinct_and_receipted():
    node = sampled()
    value_grad(node)
    executions = node.last_metadata["gradient_executions"]
    seeds = [run["root_seed"] for child in executions for run in child["gradient_evaluations"] if run["kind"] == "shift"]
    assert len(seeds) == len(set(seeds)) == 4
    assert executions[0]["partitions"][0]["seed"] != executions[1]["partitions"][0]["seed"]


def test_uniform_shot_vector_preserves_all_partitions_and_work():
    node = sampled(shots=[1000, (2000, 2)], distribution="uniform")
    values, grad = value_grad(node)
    assert len(values) == 3
    np.testing.assert_allclose(grad, 3*(.7*np.cos(.37)-.2*np.sin(.37)), atol=.12, rtol=0)
    assert node.last_metadata["observed_physical_shots"] == 5*5000
    assert all(len(x["partitions"]) == 3 for x in node.last_metadata["gradient_executions"])


def test_weighted_qwc_allocation_conserves_actual_shots():
    node = sampled(shots=2001, distribution="weighted")
    _, grad = value_grad(node)
    np.testing.assert_allclose(grad, .7*np.cos(.37)-.2*np.sin(.37), atol=.1, rtol=0)
    assert node.last_metadata["observed_physical_shots"] == 5*2001


def test_graph_sampling_matches_eager_and_has_no_trace_work_receipt():
    tf = framework()
    node = sampled(shots=501)
    eager = value_grad(node)
    @tf.function(input_signature=[tf.TensorSpec((), tf.float64)], autograph=False)
    def execute(x):
        with tf.GradientTape() as tape:
            tape.watch(x)
            value = node(x)
        return value, tape.gradient(value, x)
    np.testing.assert_array_equal(execute(tf.constant(.37, tf.float64)), eager)
    assert node.last_metadata["trace_configuration_only"]
    assert "observed_physical_shots" not in node.last_metadata


def test_sampling_seed_and_forward_plus_backward_budget_are_preflighted(monkeypatch):
    tf = framework()
    monkeypatch.setattr(StatevectorDevice, "sample", lambda *a, **k: pytest.fail("sampling before preflight"))
    with pytest.raises(UnsupportedFeature, match="seed"):
        sampled(seed=None)(tf.constant(.3))
    with pytest.raises(MemoryError, match="max_total_shots"):
        sampled(shots=100, tensorflow_limits=TensorFlowBridgeLimits(max_total_shots=900))(tf.constant(.3))


def test_input_output_and_jacobian_budgets_precede_simulation(monkeypatch):
    tf = framework()
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    monkeypatch.setattr(ExecutionPlan, "evaluate", lambda *a, **k: pytest.fail("execution before preflight"))
    with pytest.raises(MemoryError, match="max_input_elements"):
        sampled(tensorflow_limits=TensorFlowBridgeLimits(max_input_elements=1))(tf.ones(2))
    node = QNode(lambda t, x: t.probs(), 16, interface="tf", tensorflow_limits=TensorFlowBridgeLimits(max_output_elements=4))
    with pytest.raises(MemoryError, match="max_output_elements"): node(tf.constant(.3))
    def circuit(t, x):
        t.ry(x[0], 0); t.rz(x[1], 0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, interface="tf", tensorflow_limits=TensorFlowBridgeLimits(max_jacobian_elements=3))
    with pytest.raises(MemoryError, match="max_jacobian_elements"): node(tf.ones(2))


def test_transform_child_limit_precedes_simulation():
    tf = framework()
    with pytest.raises(MemoryError, match="max_transform_tapes"):
        sampled(tensorflow_limits=TensorFlowBridgeLimits(max_transform_tapes=1))(tf.constant(.3))


def test_batch_callback_and_shot_budgets_are_explicit():
    tf = framework()
    for field in ["max_batch_size", "max_callback_executions"]:
        node = sampled(tensorflow_limits=TensorFlowBridgeLimits(**{field: 2}))
        with pytest.raises(MemoryError, match=field): node.tensorflow_batch(tf.ones(3))
    with pytest.raises(MemoryError, match="max_total_shots"):
        sampled(shots=100, tensorflow_limits=TensorFlowBridgeLimits(max_total_shots=1500)).tensorflow_batch(tf.ones(2))


def test_repeated_persistent_backward_is_bounded_before_more_sampling():
    tf = framework()
    node = sampled(shots=100, tensorflow_limits=TensorFlowBridgeLimits(max_callback_executions=2))
    x = tf.Variable(.3)
    with tf.GradientTape(persistent=True) as tape:
        value = node(x)
    assert tape.gradient(value, x) is not None
    with pytest.raises(MemoryError, match="max_callback_executions"): tape.gradient(value, x)


def test_runtime_transform_growth_rechecks_bridge_limits_before_execution(monkeypatch):
    tf = framework()
    from quantumbridge.transforms import transform
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    @transform
    def variable_children(tape):
        coefficient = tape.measurements[0].observable.terms[0][0]
        children = (tape, tape.copy()) if coefficient.value < .5 else (tape,)
        return children, lambda results: sum(results)
    def circuit(t, x):
        return t.expval(Hamiltonian([(x, PauliZ(0))]))
    node = split_non_commuting(variable_children(QNode(circuit, 1, interface="tf", tensorflow_limits=TensorFlowBridgeLimits(max_transform_tapes=1))))
    monkeypatch.setattr(ExecutionPlan, "evaluate", lambda *a, **k: pytest.fail("runtime growth must reject before quantum work"))
    with pytest.raises(MemoryError, match="max_transform_tapes"): node(tf.constant(.3))


def test_runtime_transform_growth_rechecks_shots_before_any_sampling(monkeypatch):
    tf = framework()
    from quantumbridge.transforms import transform
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    @transform
    def variable_children(tape):
        coefficient = tape.measurements[0].observable.terms[0][0]
        children = (tape, tape.copy()) if coefficient.value < .5 else (tape,)
        return children, lambda results: sum(results)
    def circuit(t, x):
        return t.expval(Hamiltonian([(x, PauliZ(0))]))
    node = split_non_commuting(variable_children(QNode(circuit, 1, interface="tf", shots=100, seed=7,
                                  tensorflow_limits=TensorFlowBridgeLimits(max_total_shots=550))))
    monkeypatch.setattr(ExecutionPlan, "evaluate", lambda *a, **k: pytest.fail("runtime shot growth must reject before execution"))
    with pytest.raises(MemoryError, match="max_total_shots"): node(tf.constant(.3))


def test_actual_cumulative_shots_bound_repeated_dynamic_backward_calls():
    tf = framework()
    from quantumbridge.transforms import transform
    @transform
    def variable_children(tape):
        coefficient = tape.measurements[0].observable.terms[0][0]
        children = (tape, tape.copy()) if coefficient.value < .5 else (tape,)
        return children, lambda results: sum(results)
    def circuit(t, x):
        return t.expval(Hamiltonian([(x, PauliZ(0))]))
    node = split_non_commuting(variable_children(QNode(circuit, 1, interface="tf", shots=100, seed=7,
                                  tensorflow_limits=TensorFlowBridgeLimits(max_total_shots=1100))))
    x = tf.Variable(.3, dtype=tf.float64)
    with tf.GradientTape(persistent=True) as tape:
        value = node(x)
    np.testing.assert_allclose(tape.gradient(value, x), 2., atol=1e-11)
    np.testing.assert_allclose(tape.gradient(value, x), 2., atol=1e-11)
    assert node.last_metadata["observed_physical_shots"] == 1000
    with pytest.raises(MemoryError, match="cumulative max_total_shots"): tape.gradient(value, x)
