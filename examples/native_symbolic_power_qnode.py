# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""SDK-free branch-correct power, actual device execution and second derivatives."""

import cmath
import sys

import numpy as np

from quantumbridge import Circuit, Parameter, QuantumCircuit, PauliX, PauliZ
from quantumbridge.circuit_library import CRYGate
from quantumbridge.devices import (
    StatevectorDevice,
    DensityMatrixDevice,
    MatrixProductStateDevice,
)
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.diff import HigherOrderLimits


def main():
    point = 7.3
    p = Parameter("p")
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.append(CRYGate(p).power(0.5, annotated=True), [0, 1])
    phase = cmath.phase(cmath.exp(-0.5j * point)) / 2
    reference = np.array([np.cos(phase), 0.25 * np.sin(phase), -0.0625 * np.cos(phase)])
    for device in (
        StatevectorDevice(),
        DensityMatrixDevice(),
        MatrixProductStateDevice(),
    ):
        node = QNode.from_circuit(circuit, PauliX(0), device=device, max_diff=2)
        observed = np.array(
            [node(point), node.compute_jacobian(point), node.compute_hessian(point)]
        )
        np.testing.assert_allclose(observed, reference, atol=5e-11, rtol=0)
        assert abs(node.compute_hvp(0.7, point) - 0.7 * reference[2]) < 5e-11
        print(type(device).__name__, "value / Jacobian / Hessian:", observed.tolist())
    node = QNode.from_circuit(circuit, PauliX(0))
    plan = node._construct((point,), {})
    bound = plan.circuit.bind(
        dict(zip(plan.recorder.parameters, plan.recorder.native_values()))
    )
    y = np.array([[0, -1j], [1j, 0]])
    powered = np.cos(phase) * np.eye(2) + 1j * np.sin(phase) * y
    expected = np.eye(4, dtype=complex)
    expected[2:, 2:] = powered
    expected = expected @ np.kron(np.array([[1, 1], [1, -1]]) / np.sqrt(2), np.eye(2))
    error = float(np.max(abs(Operator(bound).data - expected)))
    assert error < 3e-12
    print("Complete complex-operator max error:", error)
    moving = QuantumCircuit(1)
    body = Circuit(1).ry(-p, 0).rz(p * p + 0.4, 0).ry(p, 0)
    moving.append(body.to_gate().power(0.5, annotated=True), [0])
    node = QNode.from_circuit(moving, PauliZ(0), max_diff=2, diff_method="adjoint")
    point = 1.3
    a = -0.5 * cmath.phase(cmath.exp(-0.5j * (point * point + 0.4)))
    s, c, t, u = np.sin(point), np.cos(point), np.sin(a), np.cos(a)
    da, dda = 0.5 * point, 0.5
    expected = [
        1 - 2 * s * s * t * t,
        -4 * (s * c * t * t + s * s * t * u * da),
        -4
        * (
            (c * c - s * s) * t * t
            + 4 * s * c * t * u * da
            + s * s * ((u * u - t * t) * da * da + t * u * dda)
        ),
    ]
    observed = [node(point), node.compute_jacobian(point), node.compute_hessian(point)]
    np.testing.assert_allclose(observed, expected, atol=8e-10, rtol=0)
    assert abs(node.compute_hvp(0.7, point) - 0.7 * expected[2]) < 8e-10
    print(
        "Moving eigenprojectors, native adjoint value / Jacobian / Hessian:", observed
    )
    q = Parameter("q")
    mixed = QuantumCircuit(1)
    mixed.append(Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(0.5, annotated=True), [0])
    node = QNode.from_circuit(mixed, PauliZ(0), max_diff=2, diff_method="adjoint")
    point, direction = np.array([0.37, 0.82]), np.array([0.4, -0.3])
    # Independent SU(2) formulas and a 70-digit test-only oracle agree.
    expected_gradient = np.array([-0.09587771262192446, -0.001833354627611443])
    expected_hessian = np.array(
        [
            [-0.2557749545208615, -0.009787820286360958],
            [-0.009787820286360958, -0.002486864050485896],
        ]
    )
    np.testing.assert_allclose(node(point), 0.9822051865077258, atol=8e-12, rtol=0)
    np.testing.assert_allclose(
        node.compute_jacobian(point), expected_gradient, atol=8e-11, rtol=0
    )
    np.testing.assert_allclose(
        node.compute_hessian(point), expected_hessian, atol=2e-9, rtol=0
    )
    node.higher_order_limits = HigherOrderLimits(max_hessian_elements=1)
    product = node.compute_hvp(direction, point)
    np.testing.assert_allclose(product, expected_hessian @ direction, atol=2e-9, rtol=0)
    assert node.last_metadata["hvp_streamed"]
    print("Two-parameter mixed Hessian reference:", expected_hessian.tolist())
    print(
        "Actual direction-only HVP, full Hessian budget limited to one element:",
        np.asarray(product).tolist(),
    )
    assert "qiskit" not in sys.modules and "pennylane" not in sys.modules
    print(
        "No Qiskit / PennyLane import; no cloud access. Full SDK replacement remains incomplete."
    )


if __name__ == "__main__":
    main()
