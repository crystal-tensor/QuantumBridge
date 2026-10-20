# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native gate/coefficient chain rules through actual QWC child execution."""

import numpy as np
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram,merge_rotations,split_non_commuting
from quantumbridge.utils.math import Hamiltonian,PauliX,PauliZ


def main():
    def circuit(tape,theta):
        tape.ry(np.sin(theta),0)
        tape.ry(2*theta,0)
        return tape.expval(Hamiltonian([(theta,PauliX(0)),(theta*theta,PauliZ(0))]))
    node = TransformProgram([merge_rotations,split_non_commuting])(QNode(circuit,1))
    theta = .37
    energy,gradient = node.execute_and_compute_derivatives(theta)
    angle = np.sin(theta)+2*theta
    expected = (np.sin(angle)+2*theta*np.cos(angle)+
                (theta*np.cos(angle)-theta*theta*np.sin(angle))*(np.cos(theta)+2))
    assert abs(gradient-expected) < 1e-12
    assert abs(node.compute_vjp(2.,theta)-2*expected) < 1e-12
    print({"theta":theta,"energy":energy,"native_gradient":gradient,"analytic_gradient":expected,
           "child_tapes":node.last_metadata["executed_tape_count"],"transform_count":node.last_metadata["transform_count"],
           "coefficient_slots":node.last_metadata["processing_parameter_count"],
           "gradient_method":node.last_metadata["gradient_method"],"path":node.last_metadata["differentiation_path"]})


if __name__ == "__main__":
    main()
