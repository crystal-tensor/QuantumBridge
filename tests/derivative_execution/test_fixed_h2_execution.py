# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""One geometry/integral/RHF/JW build, then real multi-interface derivatives."""

from importlib import import_module

import numpy as np
import pytest

from quantumbridge import qchem
from quantumbridge.execution import DerivativeExecutionRequest as Request, UnifiedExecutionLimits as Limits
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram, merge_rotations, split_non_commuting


@pytest.fixture(scope="module")
def fixed_problem():
    molecular = import_module("quantumbridge.chemistry.molecular_hamiltonian")
    scf = import_module("quantumbridge.chemistry.scf")
    counts = dict(integrals=0, rhf=0, fermionic=0, jw=0)
    mapper = molecular.JordanWignerMapper.map
    with pytest.MonkeyPatch.context() as patch:
        for target, name, key in ((scf, "molecular_integrals", "integrals"),
                (molecular, "run_restricted_hartree_fock", "rhf"),
                (molecular, "build_fermionic_hamiltonian", "fermionic"),
                (molecular.JordanWignerMapper, "map", "jw")):
            original = getattr(target, name)
            def counted(*args, _key=key, _original=original, **kwargs):
                counts[_key] += 1
                return _original(*args, **kwargs)
            patch.setattr(target, name, counted)
        problem = qchem.molecular_hamiltonian_native(qchem.Molecule(["H", "H"], [(0, 0, 0), (0, 0, 1.4)], unit="bohr"))
        assert counts == dict(integrals=1, rhf=1, fermionic=1, jw=1)
        # Ansatz excitation generators also use JW, but do not rebuild the
        # geometry-dependent molecular Hamiltonian being counted here.
        patch.setattr(molecular.JordanWignerMapper, "map", mapper)
        def forbidden(*a, **k): pytest.fail("fixed geometry chemistry was rebuilt during ansatz differentiation")
        for target, name in ((qchem, "molecular_hamiltonian_native"), (scf, "molecular_integrals"),
                (molecular, "run_restricted_hartree_fock"), (molecular, "build_fermionic_hamiltonian")):
            patch.setattr(target, name, forbidden)
        matrix = problem.hamiltonian.matrix()
        def reference(angle):
            a, d, b = matrix[12, 12].real, matrix[3, 3].real, matrix[12, 3].real
            return ((a+d)/2+(a-d)*np.cos(angle)/2+b*np.sin(angle),
                -(a-d)*np.sin(angle)/2+b*np.cos(angle),
                -(a-d)*np.cos(angle)/2-b*np.sin(angle))
        def circuit(t, angle):
            t.x(0); t.x(1)
            qchem.apply_fermionic_excitation(t, angle, [0, 1, 2, 3])
            return t.expval(problem.hamiltonian)
        yield circuit, reference, counts


def make_node(circuit, interface="numpy", transformed=True):
    node = QNode(circuit, 4, interface=interface, max_diff=2, diff_method="adjoint",
        unified_limits=Limits() if interface in {"numpy", "torch", "autograd"} else None)
    return TransformProgram((merge_rotations, split_non_commuting))(node) if transformed else node


def assert_receipt(receipt):
    assert receipt["live_memory_bytes"] == receipt["active_tapes"] == receipt["consumed_shots"] == 0
    assert receipt["consumed_tapes"] > 0 and receipt["consumed_derivative_work"] > 0
    assert receipt["total_reserved_memory_bytes"] == receipt["total_released_memory_bytes"]


def test_fixed_h2_device_and_native_qnode_reuse_one_build_for_multiple_directions(fixed_problem):
    circuit, reference, counts = fixed_problem
    energy, _, second = reference(.3)
    for transformed in (False, True):
        node = make_node(circuit, transformed=transformed)
        for direction in (.4, -.2):
            result = node.device.execute_derivatives(Request(node, (.3,), method="second_adjoint",
                derivative_order=2, derivative_kind="hvp", tangent=direction))
            np.testing.assert_allclose([result.value, result.derivative], [energy, direction*second], atol=2e-10)
            assert_receipt(result.receipt)
            np.testing.assert_allclose(node.compute_hvp(direction, .3), direction*second, atol=2e-10)
            assert_receipt(node.last_metadata["unified_resource_receipt"])
    assert counts == dict(integrals=1, rhf=1, fermionic=1, jw=1)


def test_fixed_h2_torch_true_double_backward_has_shared_native_receipt(fixed_problem):
    torch = pytest.importorskip("torch")
    circuit, reference, _ = fixed_problem
    node = make_node(circuit, "torch")
    point = torch.tensor(.3, dtype=torch.float64, requires_grad=True)
    value = node(point)
    first = torch.autograd.grad(value, point, create_graph=True)[0]
    second = torch.autograd.grad(.4*first, point)[0]
    np.testing.assert_allclose([value.detach(), first.detach(), second], np.array(reference(.3))*[1, 1, .4], atol=2e-10)
    assert_receipt(node.last_metadata["unified_resource_receipt"])


def test_fixed_h2_autograd_true_double_backward_has_shared_native_receipt(fixed_problem):
    autograd = pytest.importorskip("autograd")
    circuit, reference, _ = fixed_problem
    node = make_node(circuit, "autograd")
    first = autograd.grad(node)
    product = autograd.grad(lambda angle: .4*first(angle))(.3)
    np.testing.assert_allclose(product, .4*reference(.3)[2], atol=2e-10)
    assert_receipt(node.last_metadata["unified_resource_receipt"])


def test_fixed_h2_jax_real_compiled_hvp_and_budget_status(fixed_problem):
    jax, jnp = pytest.importorskip("jax"), pytest.importorskip("jax.numpy")
    circuit, reference, _ = fixed_problem
    node = make_node(circuit, "jax")
    product = jax.jit(lambda x: jax.jvp(jax.grad(node), (x,), (jnp.asarray(.4, dtype=x.dtype),))[1])(jnp.asarray(.3))
    np.testing.assert_allclose(product, .4*reference(.3)[2], atol=3e-6)
    node.unified_limits = Limits(max_derivative_work=1)
    failed, status = jax.jit(lambda x: node.jax_hvp_with_status(jnp.asarray(.4, dtype=x.dtype), x))(jnp.asarray(.3))
    assert int(status) == 3 and np.isnan(failed)
    node.unified_limits = Limits()
    recovered, status = jax.jit(lambda x: node.jax_hvp_with_status(jnp.asarray(.4, dtype=x.dtype), x))(jnp.asarray(.3))
    assert int(status) == 0
    np.testing.assert_allclose(recovered, product, atol=3e-6)


def test_fixed_h2_tensorflow_true_nested_tape_and_function_status(fixed_problem):
    tf = pytest.importorskip("tensorflow")
    circuit, reference, _ = fixed_problem
    node = make_node(circuit, "tf")
    point = tf.Variable(.3, dtype=tf.float64)
    with tf.GradientTape() as outer:
        with tf.GradientTape() as inner: value = node(point)
        first = inner.gradient(value, point)
        directional = .4*first
    product = outer.gradient(directional, point)
    np.testing.assert_allclose(product, .4*reference(.3)[2], atol=2e-10)
    node.unified_limits = Limits(max_derivative_work=1)
    failed, status = tf.function(lambda x: node.tensorflow_hvp_with_status(tf.constant(.4, tf.float64), x), autograph=False)(tf.constant(.3, tf.float64))
    assert int(status) == 3 and np.isnan(failed)
    node.unified_limits = Limits()
    recovered, status = tf.function(lambda x: node.tensorflow_hvp_with_status(tf.constant(.4, tf.float64), x), autograph=False)(tf.constant(.3, tf.float64))
    assert int(status) == 0
    np.testing.assert_allclose(recovered, product, atol=2e-10)
