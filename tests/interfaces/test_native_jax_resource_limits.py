# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.

import os
import subprocess
import sys

import numpy as np
import pytest

from quantumbridge import PauliZ, StatevectorDevice, UnsupportedFeature
from quantumbridge.interfaces.jax_autodiff import JAXBridgeLimits
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def node_with(**options):
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.expval(PauliZ(0))
    return QNode(circuit, 1, interface="jax", **options)


def test_bridge_limits_validate_types_and_input_before_quantum_execution(monkeypatch):
    jnp = pytest.importorskip("jax.numpy")
    with pytest.raises(ValueError): JAXBridgeLimits(max_input_elements=False)
    with pytest.raises(ValueError): JAXBridgeLimits(max_output_elements=0)
    def forbidden(*a, **kw): raise AssertionError("must reject before quantum execution")
    monkeypatch.setattr(StatevectorDevice, "expectation", forbidden)
    node = QNode(lambda t, x: t.expval(PauliZ(0)), 1, interface="jax", jax_limits=JAXBridgeLimits(max_input_elements=2))
    with pytest.raises(MemoryError, match="max_input_elements"): node(jnp.ones(3))
    with pytest.raises(TypeError, match="JAXBridgeLimits"): node_with(jax_limits={})(jnp.asarray(.2))


def test_parameter_and_jacobian_limits_reject_before_allocation(monkeypatch):
    jnp = pytest.importorskip("jax.numpy")
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    monkeypatch.setattr(ExecutionPlan, "evaluate", lambda *a, **kw: pytest.fail("preflight must not execute"))
    def circuit(tape, x):
        tape.ry(x[0], 0)
        tape.rz(x[1], 0)
        return tape.expval(PauliZ(0))
    for limits, field in [(JAXBridgeLimits(max_parameter_elements=1), "max_parameter_elements"),
                          (JAXBridgeLimits(max_jacobian_elements=3), "max_jacobian_elements")]:
        node = QNode(circuit, 1, interface="jax", jax_limits=limits)
        with pytest.raises(MemoryError, match=field): node(jnp.asarray([.2, .3]))


def test_output_storage_limit_precedes_probability_array_allocation():
    jnp = pytest.importorskip("jax.numpy")
    node = QNode(lambda t, x: t.probs(), 16, interface="jax", jax_limits=JAXBridgeLimits(max_output_elements=4))
    with pytest.raises(MemoryError, match="max_output_elements"): node(jnp.asarray(.3))


def test_vmap_and_callback_logical_expansion_limits():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    for limits, field in [(JAXBridgeLimits(max_vmap_batch=2), "max_vmap_batch"),
                          (JAXBridgeLimits(max_callback_executions=2), "max_callback_executions")]:
        node = node_with(jax_limits=limits)
        with pytest.raises(MemoryError, match=field): jax.vmap(node)(jnp.asarray([.1, .2, .3]))


def test_unsupported_derivative_measurement_and_complex_contracts():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    with pytest.raises(UnsupportedFeature, match="Complex"): node_with()(jnp.asarray(.3 + .2j))
    with pytest.raises(UnsupportedFeature, match="float32/float64"): node_with()(jnp.asarray(.3, dtype=jnp.float16))
    with pytest.raises(UnsupportedFeature): node_with(diff_method="finite-diff")(jnp.asarray(.2))
    with pytest.raises(UnsupportedFeature, match="diff_method"):
        node_with(gradient_kwargs={"method": "finite-diff"})(jnp.asarray(.2))
    for step in (False, 0., float("nan")):
        with pytest.raises(ValueError, match="finite positive"):
            node_with(gradient_kwargs={"step": step})(jnp.asarray(.2))
    with pytest.raises(UnsupportedFeature): node_with(max_diff=2)(jnp.asarray(.2))
    with pytest.raises(UnsupportedFeature): jax.grad(jax.grad(node_with()))(jnp.asarray(.2))
    with pytest.raises(UnsupportedFeature): QNode(lambda t, x: t.state(), 1, interface="jax")(jnp.asarray(.2))
    with pytest.raises(UnsupportedFeature, match="native vector/density/MPS"):
        node_with(device=object())(jnp.asarray(.2))


def test_array_gate_and_trainable_python_cast_do_not_detach():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    with pytest.raises(UnsupportedFeature, match="scalar"): node_with()(jnp.asarray([.2, .3]))
    def cast(tape, x):
        tape.ry(float(x), 0)
        return tape.expval(PauliZ(0))
    with pytest.raises((TypeError, ValueError)): jax.grad(QNode(cast, 1, interface="jax"))(jnp.asarray(.2))


def test_finite_shots_require_seed_and_preflight_total_derivative_budget():
    jnp = pytest.importorskip("jax.numpy")
    with pytest.raises(UnsupportedFeature, match="seed"): node_with(shots=100)(jnp.asarray(.2))
    node = node_with(shots=100, seed=7, jax_limits=JAXBridgeLimits(max_total_shots=300))
    with pytest.raises(MemoryError, match="max_total_shots"): node(jnp.asarray(.2))


def test_transform_tape_limit_precedes_child_quantum_execution():
    jnp = pytest.importorskip("jax.numpy")
    from quantumbridge import Hamiltonian, PauliX
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.expval(Hamiltonian([(1., PauliX(0)), (1., PauliZ(0))]))
    node = split_non_commuting(QNode(circuit, 1, interface="jax", jax_limits=JAXBridgeLimits(max_transform_tapes=1)))
    with pytest.raises(MemoryError, match="max_transform_tapes"): node(jnp.asarray(.2))


def test_jit_nonfinite_status_is_explicit_and_valid_inputs_recover():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    node = node_with()
    evaluate = jax.jit(node.jax_with_status)
    for invalid in (float("nan"), float("inf")):
        value, status = evaluate(jnp.asarray(invalid))
        assert np.isnan(value) and status == 1
    value, status = evaluate(jnp.asarray(.2))
    assert status == 0
    np.testing.assert_allclose(value, np.cos(.2), atol=2e-6, rtol=0)
    _, status_gradient = jax.value_and_grad(lambda x: node.jax_with_status(x)[1])(jnp.asarray(.2))
    assert status_gradient == 0


def test_callback_failures_return_specific_status_without_raising_in_jit(monkeypatch):
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    for failure, code in [(UnsupportedFeature("injected_runtime"), 2), (MemoryError("injected_budget"), 3),
                          (RuntimeError("injected_failure"), 4)]:
        def fail(*args, **kwargs): raise failure
        with monkeypatch.context() as patch:
            patch.setattr(StatevectorDevice, "expectation", fail)
            value, status = jax.jit(node_with().jax_with_status)(jnp.asarray(.2))
            assert np.isnan(value) and status == code


def test_x64_configuration_is_never_changed_by_quantumbridge_import():
    pytest.importorskip("jax")
    script = """
import jax
before = jax.config.x64_enabled
from quantumbridge.qml import QNode
from quantumbridge import PauliZ
import jax.numpy as jnp
def circuit(t, x):
    t.ry(x, 0)
    return t.expval(PauliZ(0))
x = jnp.asarray(.3)
value, gradient = jax.value_and_grad(QNode(circuit, 1, interface='jax'))(x)
assert jax.config.x64_enabled == before
assert str(value.dtype) == ('float64' if before else 'float32')
assert gradient.dtype == value.dtype
print('x64', before, 'value', value, 'gradient', gradient)
"""
    for setting in ("0", "1"):
        result = subprocess.run([sys.executable, "-c", script], env={**os.environ, "JAX_ENABLE_X64": setting},
                                capture_output=True, text=True, check=False)
        assert result.returncode == 0, result.stdout + result.stderr


def test_mutable_rng_and_nondifferentiable_integer_inputs_do_not_gain_fake_gradients():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    with pytest.raises(UnsupportedFeature, match="immutable"):
        node_with(shots=100, seed=np.random.default_rng(3))(jnp.asarray(.2))
    for value in (jnp.asarray(1), jnp.asarray(True)):
        with pytest.raises(TypeError): jax.grad(node_with())(value)


def test_postselection_is_rejected_statically_before_jit_callback_creation():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    def circuit(tape, x):
        tape.ry(x, 0)
        tape.measure(0)
        tape.circuit.operations[-1].metadata["postselect"] = 1
        return tape.expval(PauliZ(0))
    with pytest.raises(UnsupportedFeature, match="postselect"):
        jax.jit(QNode(circuit, 1, interface="jax"))(jnp.asarray(.2))


def test_unrecorded_live_global_phase_cannot_leak_a_tracer_into_host_callback():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    def circuit(tape, x):
        # Inject a malformed native source past Circuit's normal setter guard.
        tape.circuit.metadata["global_phase"] = x
        return tape.expval(PauliZ(0))
    with pytest.raises(UnsupportedFeature, match="parameter recording"):
        jax.jit(QNode(circuit, 1, interface="jax"))(jnp.asarray(.2))
