# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""TensorFlow classical preprocessing, native quantum parameter-shift."""

import numpy as np
from quantumbridge import PauliZ
from quantumbridge.qml import QNode


def main():
    import tensorflow as tf
    def circuit(tape, x):
        tape.ry(tf.sin(x)+2*x, 0)
        return tape.expval(PauliZ(0))
    node = QNode(circuit, 1, interface="tf", diff_method="parameter-shift")
    x = tf.Variable(.37, dtype=tf.float64)
    with tf.GradientTape() as recording:
        value = node(x)
    gradient = recording.gradient(value, x)
    angle = np.sin(.37)+.74
    np.testing.assert_allclose([value, gradient], [np.cos(angle), -np.sin(angle)*(np.cos(.37)+2)], atol=1e-11)
    receipt = {"value": float(value), "native_gradient": float(gradient), "dtype": value.dtype.name,
               "method": node.last_metadata["gradient_method"], "quantum_engine": "QuantumBridge native CPU"}
    print(receipt)
    return receipt


if __name__ == "__main__":
    main()
