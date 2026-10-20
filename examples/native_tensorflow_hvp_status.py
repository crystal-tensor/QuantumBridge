# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Optional CPU TensorFlow query: runtime derivative outcome, not NaN alone."""

import json


def main():
    import tensorflow as tf
    from quantumbridge import PauliZ
    from quantumbridge.qml import QNode
    def circuit(t, x):
        t.ry(x[0], 0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, interface="tf", max_diff=2, diff_method="adjoint")
    compiled = tf.function(lambda x: node.tensorflow_hvp_with_status(tf.ones_like(x), x), autograph=False)
    rows = []
    for point in (.3, float("nan"), .7):
        product, status = compiled(tf.constant([point], tf.float64))
        rows.append({"input": None if point != point else point, "status": int(status),
            "hvp": None if int(status) else product.numpy().tolist()})
    print(json.dumps(rows, indent=2))
    return rows


if __name__ == "__main__":
    main()
