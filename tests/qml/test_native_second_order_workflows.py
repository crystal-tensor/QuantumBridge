# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Real non-dense MPS and fixed-geometry molecular ansatz second derivatives.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliZ, MatrixProductStateDevice, StatevectorDevice, DensityMatrixDevice, qchem
from quantumbridge.information.matrix_product_state import MatrixProductState
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram, merge_rotations, split_non_commuting, defer_measurements


def test_100_qubit_mps_actual_hessian_and_hvp_forbid_all_dense_paths(monkeypatch):
    def forbidden(*unused, **kwargs): raise AssertionError("Dense expansion forbidden in actual second-order MPS execution")
    for target, name in [(StatevectorDevice, "statevector"), (DensityMatrixDevice, "density_matrix"),
                         (MatrixProductState, "statevector"), (MatrixProductState, "reduced_density_matrix")]:
        monkeypatch.setattr(target, name, forbidden)
    def circuit(t, angle):
        t.h(0)
        for wire in range(99): t.cx(wire, wire+1)
        t.ry(angle, 99)
        return t.expval(Hamiltonian([(1., PauliZ(0).tensor(PauliZ(99))), (.2, PauliZ(0))]))
    device = MatrixProductStateDevice(max_memory_mb=2, max_bond_dim=4, cutoff=0)
    node = TransformProgram((merge_rotations, split_non_commuting))(QNode(circuit, 100, device=device, max_diff=2))
    value, hessian = node.execute_and_compute_hessian(.3)
    np.testing.assert_allclose([value, hessian, node.compute_hvp(.4, .3)], [np.cos(.3), -np.cos(.3), -.4*np.cos(.3)], atol=1e-10)
    metadata = node.last_metadata
    receipts = metadata["second_order_executions"][0]["second_order_evaluations"]
    assert len(receipts) == 8 and metadata["second_shifted_evaluation_count"] == 4
    assert metadata["total_physical_shots"] == 0
    for receipt in receipts:
        resources = receipt["partitions"][0]["resources"]
        assert resources["max_bond_observed"] == 2
        assert resources["max_tensor_bytes"] < 2*1024*1024
        assert resources["max_discarded_weight"] == resources["max_truncations"] == 0


def test_coherent_deferred_second_derivative_runs_actual_child():
    def circuit(t, angle):
        t.ry(angle, 0)
        record = t.measure(0)
        t.cond(record, lambda child: child.x(1))
        return t.expval(PauliZ(1))
    node = defer_measurements(QNode(circuit, 2, max_diff=2))
    np.testing.assert_allclose(node.compute_hessian(.37), -np.cos(.37), atol=1e-11)
    assert node.last_metadata["deferred_measurements"]
    assert node.last_metadata["second_order_executions"][0]["second_shifted_evaluation_count"] > 0


@pytest.fixture(scope="module")
def fixed_h2():
    problem = qchem.molecular_hamiltonian_native(qchem.Molecule(["H", "H"], [(0, 0, 0), (0, 0, 1.4)], unit="bohr"))
    matrix = problem.hamiltonian.matrix()
    def reference(angle):
        # The independently specified two-determinant excitation subspace.
        a, d, b = matrix[12, 12].real, matrix[3, 3].real, matrix[12, 3].real
        value = (a+d)/2+(a-d)*np.cos(angle)/2+b*np.sin(angle)
        first = -(a-d)*np.sin(angle)/2+b*np.cos(angle)
        second = -(a-d)*np.cos(angle)/2-b*np.sin(angle)
        return value, first, second
    def circuit(t, angle):
        t.x(0); t.x(1)
        qchem.apply_fermionic_excitation(t, angle, [0, 1, 2, 3])
        return t.expval(problem.hamiltonian)
    return circuit, reference


def test_native_fixed_h2_hessian_hvp_and_real_regularized_newton_updates(fixed_h2, monkeypatch):
    circuit, reference = fixed_h2
    def forbidden(*unused, **kwargs): raise AssertionError("Fixed molecular geometry/integrals rebuilt during ansatz derivatives")
    monkeypatch.setattr(qchem, "molecular_hamiltonian_native", forbidden)
    node = TransformProgram((merge_rotations, split_non_commuting))(QNode(circuit, 4, max_diff=2))
    unsplit = QNode(circuit, 4, max_diff=2)
    angle, initial = .3, reference(.3)[0]
    for iteration in range(3):
        value, second = node.execute_and_compute_hessian(angle)
        first = node.gradient(angle)
        np.testing.assert_allclose([value, first, second], reference(angle), atol=2e-10, rtol=0)
        if iteration == 0:
            np.testing.assert_allclose([unsplit.compute_hessian(angle), node.compute_hvp(.4, angle)], [second, .4*second], atol=2e-10)
        angle -= np.clip(first/max(float(second), .1), -.3, .3)
    assert node(angle) < initial-.01


def test_tensorflow_fixed_h2_true_second_derivative_without_scf_rebuild(fixed_h2, monkeypatch):
    tf = pytest.importorskip("tensorflow")
    circuit, reference = fixed_h2
    def forbidden(*unused, **kwargs): raise AssertionError("Framework derivative rebuilt molecular integrals")
    monkeypatch.setattr(qchem, "molecular_hamiltonian_native", forbidden)
    node = TransformProgram((merge_rotations, split_non_commuting))(QNode(circuit, 4, interface="tf", max_diff=2))
    angle = tf.Variable(.3, dtype=tf.float64)
    with tf.GradientTape() as outer:
        with tf.GradientTape() as inner:
            value = node(angle)
        first = inner.gradient(value, angle)
    second = outer.gradient(first, angle)
    np.testing.assert_allclose([value, first, second], reference(.3), atol=2e-10, rtol=0)
    assert 0 < node.last_metadata["shifted_evaluation_count"] < 1000
