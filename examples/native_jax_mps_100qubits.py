# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""JAX first derivative of a real 100-wire native non-dense MPS circuit."""

from unittest.mock import patch
import numpy as np
from quantumbridge import StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice, templates
from quantumbridge.information.matrix_product_state import MatrixProductState
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram, merge_rotations, split_non_commuting
from quantumbridge.utils.math import Hamiltonian, PauliZ


def main():
    import jax
    import jax.numpy as jnp
    def forbidden(*args, **kwargs): raise AssertionError("Dense expansion forbidden")
    def circuit(tape, theta):
        tape.h(0)
        for wire in range(99): tape.cx(wire, wire + 1)
        templates.AngleEmbedding([theta], [99], rotation="Y").apply(tape)
        return tape.expval(Hamiltonian([(1., PauliZ(0).tensor(PauliZ(99))), (.2, PauliZ(0))]))
    device = MatrixProductStateDevice(max_memory_mb=2, max_bond_dim=4, cutoff=0)
    node = TransformProgram([merge_rotations, split_non_commuting])(
        QNode(circuit, 100, device=device, interface="jax", diff_method="parameter-shift"))
    with patch.object(StatevectorDevice, "statevector", forbidden), patch.object(DensityMatrixDevice, "density_matrix", forbidden), \
         patch.object(MatrixProductState, "statevector", forbidden), patch.object(MatrixProductState, "reduced_density_matrix", forbidden):
        energy, gradient = jax.value_and_grad(node)(jnp.asarray(.3))
    tolerance = 2e-6 if energy.dtype == jnp.float32 else 1e-10
    assert abs(float(energy) - np.cos(.3)) < tolerance
    assert abs(float(gradient) + np.sin(.3)) < tolerance
    resources = node.last_metadata["executions"][0]["partitions"][0]["resources"]
    receipt = {"logical_wires": 100, "energy": float(energy), "native_gradient": float(gradient),
               "peak_bond": resources["max_bond_observed"], "tensor_bytes": resources["max_tensor_bytes"],
               "discarded_weight": resources["max_discarded_weight"], "truncations": resources["max_truncations"],
               "shifted_evaluations": node.last_metadata["shifted_evaluation_count"],
               "transform_count": node.last_metadata["transform_count"], "method": "matrix_product_state",
               "physical_shots": node.last_metadata["total_physical_shots"], "limits": device.state_options}
    print(receipt)
    print("Eager actual native receipts. Low-entanglement example; tensor bytes exclude peak workspace and do not bound arbitrary circuits.")
    return receipt


if __name__ == "__main__":
    main()
