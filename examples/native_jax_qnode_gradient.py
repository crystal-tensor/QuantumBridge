# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Real JAX preprocessing and native parameter-shift quantum derivatives."""

import numpy as np
from quantumbridge import PauliZ
from quantumbridge.qml import QNode


def main():
    import jax
    import jax.numpy as jnp
    def circuit(tape, x):
        tape.ry(jnp.sin(x) + 2 * x, 0)
        return tape.expval(PauliZ(0))
    node = QNode(circuit, 1, interface="jax", diff_method="parameter-shift")
    theta = jnp.asarray(.37)
    value, gradient = jax.value_and_grad(node)(theta)
    angle = np.sin(.37) + .74
    tolerance = 2e-6 if theta.dtype == jnp.float32 else 1e-11
    assert abs(float(value) - np.cos(angle)) < tolerance
    assert abs(float(gradient) + np.sin(angle) * (np.cos(.37) + 2)) < tolerance
    receipt = {"value": float(value), "native_gradient": float(gradient), "dtype": str(value.dtype),
               "method": node.last_metadata["gradient_method"], "quantum_engine": "QuantumBridge native CPU"}
    print(receipt)
    return receipt


if __name__ == "__main__":
    main()
