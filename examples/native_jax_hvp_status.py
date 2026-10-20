# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Optional CPU JAX query: current-input native HVP status under JIT."""

import json


def main():
    import jax
    import jax.numpy as jnp
    from quantumbridge import PauliZ
    from quantumbridge.qml import QNode
    def circuit(t, x):
        t.ry(x[0], 0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, interface="jax", max_diff=2, diff_method="adjoint")
    compiled = jax.jit(lambda x: node.jax_hvp_with_status(jnp.ones_like(x), x))
    rows = []
    for point in (.3, float("nan"), .7):
        product, status = compiled(jnp.array([point], dtype=jnp.float32))
        rows.append({"input": None if point != point else point, "status": int(status),
            "hvp": None if int(status) else product.tolist()})
    print(json.dumps(rows, indent=2))
    return rows


if __name__ == "__main__":
    main()
