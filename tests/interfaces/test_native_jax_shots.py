# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def sampled(shots=2001, seed=17, distribution=None):
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.expval(Hamiltonian([(.7, PauliX(0)), (.2, PauliZ(0))]))
    return split_non_commuting(shot_dist=distribution)(QNode(circuit, 1, interface="jax", diff_method="parameter-shift", shots=shots, seed=seed))


def test_eager_sampled_gradients_are_seed_reproducible_real_estimates():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    node = sampled()
    a = jax.value_and_grad(node)(jnp.asarray(.37))
    b = jax.value_and_grad(node)(jnp.asarray(.37))
    np.testing.assert_array_equal(a, b)
    np.testing.assert_allclose(a, [.7 * np.sin(.37) + .2 * np.cos(.37), .7 * np.cos(.37) - .2 * np.sin(.37)], atol=.06, rtol=0)
    assert node.last_metadata["gradient_semantics"] == "finite-shot estimate"
    assert node.last_metadata["total_physical_shots"] == 8 * 2001


def test_shifted_sampling_seeds_and_group_streams_are_independent():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    node = sampled()
    jax.grad(node)(jnp.asarray(.37))
    groups = node.last_metadata["gradient_executions"]
    all_shift_seeds = [run["root_seed"] for child in groups for run in child["gradient_evaluations"] if run["kind"] == "shift"]
    assert len(all_shift_seeds) == len(set(all_shift_seeds)) == 4
    assert groups[0]["partitions"][0]["seed"] != groups[1]["partitions"][0]["seed"]


def test_shot_vectors_and_uniform_total_allocation_preserve_all_partitions():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    node = sampled(shots=[1000, (2000, 2)], distribution="uniform")
    values = node(jnp.asarray(.37))
    assert len(values) == 3
    gradient = jax.grad(lambda x: sum(node(x)))(jnp.asarray(.37))
    np.testing.assert_allclose(gradient, 3 * (.7 * np.cos(.37) - .2 * np.sin(.37)), atol=.12, rtol=0)
    assert node.last_metadata["total_physical_shots"] == 4 * 5000
    assert all(len(child["partitions"]) == 3 for child in node.last_metadata["gradient_executions"])


def test_explicit_distinct_seeds_change_sampling_without_hidden_state():
    pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    nodes = [sampled(shots=101, seed=seed) for seed in (17, 18, 19)]
    values = [float(node(jnp.asarray(.37))) for node in nodes]
    assert len(set(values)) > 1
    for node, value in zip(nodes, values): assert float(node(jnp.asarray(.37))) == value


def test_seeded_sampled_jit_is_pure_reproducible_and_matches_eager_contract():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    node = sampled(shots=1001)
    x = jnp.asarray(.37)
    eager = jax.value_and_grad(node)(x)
    compiled = jax.jit(jax.value_and_grad(node))
    np.testing.assert_array_equal(compiled(x), eager)
    np.testing.assert_array_equal(compiled(x), compiled(x))
    assert "not guaranteed" in node.last_metadata["jit_callback_execution_count"]


def test_jit_snapshots_shot_partitions_and_allocation_configuration():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    partitions = [101, 201]
    node = sampled(shots=partitions, distribution="uniform")
    evaluate = jax.jit(node)
    first = evaluate(jnp.asarray(.3))
    partitions[:] = [3001]
    node.transform_program.transforms[0].options["shot_dist"] = "weighted"
    second = evaluate(jnp.asarray(.3))
    assert len(first) == len(second) == 2
    np.testing.assert_array_equal(first, second)
