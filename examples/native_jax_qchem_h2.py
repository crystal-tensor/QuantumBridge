# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""One geometry-derived native H2 Hamiltonian, real JAX VQE updates."""

from quantumbridge import qchem
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram, merge_rotations, split_non_commuting


def main():
    import jax
    import jax.numpy as jnp
    problem = qchem.molecular_hamiltonian_native(qchem.Molecule(["H", "H"], [(0, 0, 0), (0, 0, 1.4)], unit="bohr"))
    def circuit(tape, theta):
        tape.x(0); tape.x(1)
        qchem.apply_fermionic_excitation(tape, theta, [0, 1, 2, 3])
        return tape.expval(problem.hamiltonian)
    reference = QNode(circuit, 4)
    node = TransformProgram([merge_rotations, split_non_commuting])(QNode(circuit, 4, interface="jax"))
    theta = jnp.asarray(.3)
    evaluate = jax.value_and_grad(node)
    energy, gradient = evaluate(theta)
    tolerance = 3e-6 if theta.dtype == jnp.float32 else 2e-10
    assert abs(float(energy) - reference(.3)) < tolerance
    assert abs(float(gradient) - reference.gradient(.3)) < tolerance
    initial = float(energy)
    for _ in range(4):
        _, derivative = evaluate(theta)
        theta = theta - .3 * derivative
    final, _ = evaluate(theta)
    assert float(final) < initial - .01
    receipt = {"geometry": "H2 1.4 bohr / native Gaussian-RHF-JW", "initial_energy": initial,
               "initial_gradient": float(gradient), "final_theta": float(theta), "final_energy": float(final),
               "qwc_children": node.last_metadata["executed_tape_count"], "transform_count": node.last_metadata["transform_count"]}
    print(receipt)
    print("One fixed-geometry integral/SCF construction; not differentiable HF or a general VQE convergence guarantee.")
    return receipt


if __name__ == "__main__":
    main()
