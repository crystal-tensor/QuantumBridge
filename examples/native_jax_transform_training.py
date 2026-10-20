# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""JAX optimizer updates through native QWC child execution/postprocessing."""

from quantumbridge import Hamiltonian, PauliX, PauliZ
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def main():
    import jax
    import jax.numpy as jnp
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.expval(Hamiltonian([(.7, PauliZ(0)), (.2, PauliX(0))]))
    node = split_non_commuting(QNode(circuit, 1, interface="jax", diff_method="parameter-shift"))
    theta = jnp.asarray(1.)
    initial = float(node(theta))
    energy_and_gradient = jax.value_and_grad(node)
    for _ in range(12):
        _, gradient = energy_and_gradient(theta)
        theta = theta - .2 * gradient
    final, _ = energy_and_gradient(theta)
    assert float(final) < initial - .5
    receipt = {"initial_energy": initial, "final_energy": float(final), "final_theta": float(theta),
               "qwc_children": node.last_metadata["executed_tape_count"],
               "native_postprocessing_derivative": node.last_metadata["native_postprocessing_derivative"]}
    print(receipt)
    return receipt


if __name__ == "__main__":
    main()
