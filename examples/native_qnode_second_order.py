# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free exact Hessian and streamed HVP with an actual QWC child."""

import json
import numpy as np

from quantumbridge import Hamiltonian, PauliX, PauliZ
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def main():
    def circuit(t, x):
        t.ry(np.sin(x[0])+2*x[1], 0)
        return t.expval(Hamiltonian([(.7+.1*x[0], PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1)))]))
    node = split_non_commuting(QNode(circuit, 2, max_diff=2))
    x, direction = np.array([.37, .2]), np.array([.4, -.3])
    value, hessian = node.execute_and_compute_hessian(x)
    product = node.compute_hvp(direction, x)
    np.testing.assert_allclose(product, hessian @ direction, atol=1e-11)
    receipt = {"value": value, "hessian": hessian.tolist(), "hvp": product.tolist(),
               "hvp_streamed": node.last_metadata["hvp_streamed"],
               "second_shifted_evaluations": node.last_metadata["second_shifted_evaluation_count"],
               "physical_shots": node.last_metadata["total_physical_shots"]}
    print(json.dumps(receipt, indent=2))
    return receipt


if __name__ == "__main__":
    main()
