# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Twenty actual Keras SGD updates through native QWC child derivatives."""

from quantumbridge import Hamiltonian, PauliX, PauliZ
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def main():
    import tensorflow as tf
    def circuit(t, x):
        t.ry(x, 0)
        return t.expval(Hamiltonian([(.7, PauliZ(0)), (.2, PauliX(0))]))
    node = split_non_commuting(QNode(circuit, 1, interface="tf", diff_method="parameter-shift"))
    x = tf.Variable(1., dtype=tf.float64)
    optimizer = tf.keras.optimizers.SGD(learning_rate=.2)
    trace = []
    for _ in range(20):
        with tf.GradientTape() as tape:
            energy = node(x)
        derivative = tape.gradient(energy, x)
        derivative_receipt = dict(node.last_metadata)
        trace.append({"theta": float(x), "energy": float(energy), "native_gradient": float(derivative)})
        optimizer.apply_gradients([(derivative, x)])
    final = float(node(x))
    assert final < trace[0]["energy"]-.5 and int(optimizer.iterations) == 20
    receipt = {"initial_energy": trace[0]["energy"], "final_energy": final, "final_theta": float(x),
               "updates": 20, "trace": trace, "qwc_children": node.last_metadata["executed_tape_count"],
               "native_postprocessing_derivative": derivative_receipt["native_postprocessing_derivative"]}
    print(receipt)
    return receipt


if __name__ == "__main__":
    main()
