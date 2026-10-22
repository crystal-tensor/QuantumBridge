# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Compare native Hessian and streamed HVP with a separate analytic formula."""

import json
import numpy as np

from quantumbridge import PauliZ
from quantumbridge.qml import QNode
from native_symbolic_circuit_gradient import build, reference


def main():
    _, circuit = build()
    node = QNode.from_circuit(circuit, PauliZ(0).tensor(PauliZ(1)), diff_method="adjoint", max_diff=2)
    point, direction = np.array([.4, -.2]), np.array([.4, -.2])
    _, _, expected = reference(point)
    hessian = node.compute_hessian(point)
    hvp = node.compute_hvp(direction, point)
    np.testing.assert_allclose(hessian, expected, atol=6e-10, rtol=0)
    np.testing.assert_allclose(hvp, expected@direction, atol=6e-10, rtol=0)
    print(json.dumps({"hessian": hessian.tolist(), "hvp": hvp.tolist()}))


if __name__ == "__main__": main()
