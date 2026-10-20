# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native defer/QWC derivatives with real finite-shot work accounting."""

import numpy as np
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram, defer_measurements, split_non_commuting
from quantumbridge.utils.math import Hamiltonian, PauliX, PauliZ


def main():
    def circuit(t, theta):
        t.ry(theta, 0)
        record = t.measure(0)
        t.h(0)
        t.cond(record, lambda branch: branch.x(1))
        return t.expval(Hamiltonian([(.7, PauliZ(1)), (.2, PauliX(0))]))
    program = TransformProgram((defer_measurements, split_non_commuting))
    node = program(QNode(circuit, 2))
    energy, gradient = node.execute_and_compute_derivatives(.37)
    assert abs(energy - .9*np.cos(.37)) < 1e-12
    assert abs(gradient + .9*np.sin(.37)) < 1e-12
    assert abs(node.compute_vjp(2., .37) - 2*gradient) < 1e-12
    sampled = program(QNode(circuit, 2, shots=[100, (200, 2)], seed=17, diff_method="parameter-shift"))
    estimates = sampled.jacobian(.37)
    assert max(abs(value - gradient) for value in estimates) < .3
    assert sampled.last_metadata["gradient_physical_shots"] == 2000
    print({"analytic_energy": energy, "native_gradient": gradient,
           "sampled_partition_gradients": estimates,
           "actual_derivative_physical_shots": sampled.last_metadata["gradient_physical_shots"],
           "path": node.last_metadata["differentiation_path"]})
    print("Sampled gradients are estimates; energy SE is not a gradient error bound. Reset/postselection remain unsupported.")


if __name__ == "__main__":
    main()
