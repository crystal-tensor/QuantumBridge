# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""One native Gaussian/RHF/JW H2 construction, real TensorFlow optimization."""

import numpy as np
from quantumbridge import qchem
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram, merge_rotations, split_non_commuting


def main():
    import tensorflow as tf
    problem = qchem.molecular_hamiltonian_native(qchem.Molecule(["H", "H"], [(0, 0, 0), (0, 0, 1.4)], unit="bohr"))
    def circuit(tape, theta):
        tape.x(0); tape.x(1)
        qchem.apply_fermionic_excitation(tape, theta, [0, 1, 2, 3])
        return tape.expval(problem.hamiltonian)
    reference = QNode(circuit, 4)
    node = TransformProgram([merge_rotations, split_non_commuting])(QNode(circuit, 4, interface="tf"))
    x = tf.Variable(.3, dtype=tf.float64)
    optimizer = tf.keras.optimizers.SGD(learning_rate=.3)
    trace = []
    for _ in range(5):
        with tf.GradientTape() as recording:
            energy = node(x)
        derivative = recording.gradient(energy, x)
        trace.append({"theta": float(x), "energy": float(energy), "native_gradient": float(derivative)})
        if len(trace) == 1:
            np.testing.assert_allclose([energy, derivative], [reference(.3), reference.gradient(.3)], atol=2e-10)
        if len(trace) < 5:
            optimizer.apply_gradients([(derivative, x)])
    assert trace[-1]["energy"] < trace[0]["energy"]-.01
    receipt = {"geometry": "H2 1.4 bohr / native Gaussian-RHF-JW", "initial_energy": trace[0]["energy"],
               "initial_gradient": trace[0]["native_gradient"], "final_theta": float(x), "final_energy": trace[-1]["energy"],
               "qwc_children": node.last_metadata["executed_tape_count"], "transform_count": node.last_metadata["transform_count"],
               "updates": int(optimizer.iterations), "trace": trace}
    print(receipt)
    print("One fixed-geometry SCF construction; not differentiable Hartree-Fock or a general ground-state convergence guarantee.")
    return receipt


if __name__ == "__main__":
    main()
