# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""A 100-wire low-entanglement transformed gradient with dense APIs forbidden."""

from unittest.mock import patch
import numpy as np
from quantumbridge import StatevectorDevice,templates
from quantumbridge.devices import MatrixProductStateDevice,DensityMatrixDevice
from quantumbridge.information.matrix_product_state import MatrixProductState
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram,merge_rotations,split_non_commuting
from quantumbridge.utils.math import Hamiltonian,PauliZ


def main():
    def forbidden(*args,**kwargs):
        raise AssertionError("Dense expansion forbidden in this native MPS proof")
    def circuit(tape,theta):
        tape.h(0)
        for wire in range(99): tape.cx(wire,wire+1)
        templates.AngleEmbedding([theta],[99],rotation="Y").apply(tape)
        return tape.expval(Hamiltonian([(1.,PauliZ(0).tensor(PauliZ(99))),(.2,PauliZ(0))]))
    device = MatrixProductStateDevice(max_memory_mb=2,max_bond_dim=4,cutoff=0)
    node = TransformProgram([merge_rotations,split_non_commuting])(QNode(circuit,100,device=device,diff_method="parameter-shift"))
    with patch.object(StatevectorDevice,"statevector",forbidden), patch.object(DensityMatrixDevice,"density_matrix",forbidden), \
         patch.object(MatrixProductState,"statevector",forbidden), patch.object(MatrixProductState,"reduced_density_matrix",forbidden):
        energy,gradient = node.execute_and_compute_derivatives(.3)
    assert abs(energy-np.cos(.3)) < 1e-11 and abs(gradient+np.sin(.3)) < 1e-10
    resources = node.last_metadata["executions"][0]["partitions"][0]["resources"]
    print({"energy":energy,"native_gradient":gradient,"analytic_gradient":-np.sin(.3),
           "peak_bond":resources["max_bond_observed"],"tensor_bytes":resources["max_tensor_bytes"],
           "discarded_weight":resources["max_discarded_weight"],"truncations":resources["max_truncations"],
           "shifted_evaluations":node.last_metadata["shifted_evaluation_count"],
           "actual_transform_count":node.last_metadata["transform_count"],
           "physical_shots":node.last_metadata["total_physical_shots"],"limits":device.state_options})
    print("This is a low-entanglement proof, not arbitrary 100-qubit efficiency or a truncation error bound.")


if __name__ == "__main__":
    main()
