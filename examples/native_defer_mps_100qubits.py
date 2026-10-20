# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""A real 101-wire coherent record for a 100-wire dynamic MPS experiment."""

from unittest.mock import patch
import numpy as np
from quantumbridge import StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice, templates
from quantumbridge.information.matrix_product_state import MatrixProductState
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram, defer_measurements, merge_rotations, split_non_commuting
from quantumbridge.utils.math import PauliZ


def main():
    def forbidden(*args, **kwargs): raise AssertionError("Dense expansion forbidden")
    def circuit(t, theta):
        t.h(0)
        for wire in range(99): t.cx(wire, wire + 1)
        record = t.measure(0)
        t.h(0)
        t.cond(record, lambda branch: branch.x(99))
        templates.AngleEmbedding([theta], [99], rotation="Y").apply(t)
        return t.expval(PauliZ(99))
    device = MatrixProductStateDevice(max_qubits=101, max_memory_mb=2, max_bond_dim=4, cutoff=0)
    node = TransformProgram((defer_measurements, merge_rotations, split_non_commuting))(QNode(circuit, 100, device=device, diff_method="parameter-shift"))
    with patch.object(StatevectorDevice, "statevector", forbidden), patch.object(DensityMatrixDevice, "density_matrix", forbidden), \
         patch.object(MatrixProductState, "statevector", forbidden), patch.object(MatrixProductState, "reduced_density_matrix", forbidden):
        energy, gradient = node.execute_and_compute_derivatives(.3)
    assert abs(energy - np.cos(.3)) < 1e-11 and abs(gradient + np.sin(.3)) < 1e-10
    receipt = node.last_metadata["deferred_measurements"][0]
    resources = node.last_metadata["executions"][0]["partitions"][0]["resources"]
    print({"original_wires": receipt["logical_wires"], "actual_wires": receipt["transformed_wires"],
           "ancillas": receipt["ancilla_count"], "energy": energy, "native_gradient": gradient,
           "peak_bond": resources["max_bond_observed"], "tensor_bytes": resources["max_tensor_bytes"],
           "discarded_weight": resources["max_discarded_weight"], "truncations": resources["max_truncations"],
           "shifted_evaluations": node.last_metadata["shifted_evaluation_count"],
           "actual_transform_count": node.last_metadata["transform_count"],
           "actual_physical_shots": node.last_metadata["total_physical_shots"], "limits": device.state_options})
    print("Low-entanglement proof only. Tensor storage excludes peak SVD workspace; simulator capacity is not hardware capacity.")


if __name__ == "__main__":
    main()
