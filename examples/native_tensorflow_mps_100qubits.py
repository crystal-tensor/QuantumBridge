# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual TensorFlow derivative of a 100-wire, non-dense native MPS."""

from unittest.mock import patch
import numpy as np
from quantumbridge import StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice, templates
from quantumbridge.information.matrix_product_state import MatrixProductState
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram, merge_rotations, split_non_commuting
from quantumbridge.utils.math import Hamiltonian, PauliZ


def main():
    import tensorflow as tf
    def forbidden(*args, **kwargs): raise AssertionError("Dense expansion forbidden")
    def circuit(tape, theta):
        tape.h(0)
        for wire in range(99): tape.cx(wire, wire+1)
        templates.AngleEmbedding([theta], [99], rotation="Y").apply(tape)
        return tape.expval(Hamiltonian([(1., PauliZ(0).tensor(PauliZ(99))), (.2, PauliZ(0))]))
    device = MatrixProductStateDevice(max_memory_mb=2, max_bond_dim=4, cutoff=0)
    node = TransformProgram([merge_rotations, split_non_commuting])(
        QNode(circuit, 100, device=device, interface="tf", diff_method="parameter-shift"))
    x = tf.Variable(.3, dtype=tf.float64)
    with patch.object(StatevectorDevice, "statevector", forbidden), patch.object(DensityMatrixDevice, "density_matrix", forbidden), \
         patch.object(MatrixProductState, "statevector", forbidden), patch.object(MatrixProductState, "reduced_density_matrix", forbidden):
        with tf.GradientTape() as tape:
            energy = node(x)
        gradient = tape.gradient(energy, x)
    np.testing.assert_allclose([energy, gradient], [np.cos(.3), -np.sin(.3)], atol=1e-10)
    resources = node.last_metadata["executions"][0]["partitions"][0]["resources"]
    receipt = {"logical_wires": 100, "energy": float(energy), "native_gradient": float(gradient),
               "peak_bond": resources["max_bond_observed"], "tensor_bytes": resources["max_tensor_bytes"],
               "discarded_weight": resources["max_discarded_weight"], "truncations": resources["max_truncations"],
               "shifted_evaluations": node.last_metadata["shifted_evaluation_count"],
               "transform_count": node.last_metadata["transform_count"], "method": "matrix_product_state",
               "physical_shots": node.last_metadata["observed_physical_shots"], "limits": device.state_options}
    print(receipt)
    print("Low-entanglement example only; tensor storage excludes workspace and is not an arbitrary-circuit efficiency guarantee.")
    return receipt


if __name__ == "__main__":
    main()
