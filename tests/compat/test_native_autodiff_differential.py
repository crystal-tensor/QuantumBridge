# Public API black-box comparisons; no upstream implementation or tests copied.

import json
import numpy as np
import pytest

from quantumbridge import PauliX, PauliY, PauliZ, Hamiltonian, DensityMatrixDevice, MatrixProductStateDevice
from quantumbridge.qml import QNode


SCENARIOS = ("rx_z", "ry_z", "rz_y", "phase_x", "shared", "scaled", "nonlinear",
             "controlled", "probabilities", "variance", "fixed_noise", "dynamic", "hamiltonian", "mps")


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_native_gradient_matches_public_pennylane_behavior(scenario):
    qml = pytest.importorskip("pennylane")
    theta = .47
    native_device = DensityMatrixDevice() if scenario == "fixed_noise" else MatrixProductStateDevice() if scenario == "mps" else None
    width = 3 if scenario == "mps" else 2 if scenario in {"controlled", "dynamic"} else 1
    def program(tape, angle):
        if scenario == "rx_z": tape.rx(angle, 0)
        elif scenario == "ry_z": tape.ry(angle, 0)
        elif scenario == "rz_y": tape.h(0); tape.rz(angle, 0)
        elif scenario == "phase_x": tape.h(0); tape.phase(angle, 0)
        elif scenario == "shared": tape.ry(angle, 0); tape.ry(angle, 0)
        elif scenario == "scaled": tape.ry(2 * angle, 0)
        elif scenario == "nonlinear": tape.ry(np.sin(angle), 0)
        elif scenario == "controlled": tape.h(0); tape.cry(angle, 0, 1)
        elif scenario == "dynamic":
            tape.ry(angle, 0); outcome = tape.measure(0)
            tape.cond(outcome, lambda branch: branch.ry(angle, 1))
        else:
            tape.ry(angle, 0)
            if scenario == "fixed_noise": tape.amplitude_damping(.3, 0)
            if scenario == "mps": tape.cx(0, 1); tape.cx(1, 2)
        if scenario == "probabilities": return tape.probs([0])
        if scenario == "variance": return tape.var(PauliZ(0))
        observable = PauliY(0) if scenario == "rz_y" else PauliX(0) if scenario in {"phase_x", "controlled"} else PauliZ(width - 1)
        if scenario == "hamiltonian": observable = Hamiltonian([(.3, PauliX(0)), (.7, PauliZ(0))])
        return tape.expval(observable)
    reference_device = qml.device("default.mixed" if scenario == "fixed_noise" else "default.qubit", wires=width + int(scenario == "dynamic"))
    @qml.qnode(reference_device, interface="autograd", diff_method="parameter-shift")
    def reference(angle):
        if scenario == "rx_z": qml.RX(angle, wires=0)
        elif scenario == "ry_z": qml.RY(angle, wires=0)
        elif scenario == "rz_y": qml.Hadamard(wires=0); qml.RZ(angle, wires=0)
        elif scenario == "phase_x": qml.Hadamard(wires=0); qml.PhaseShift(angle, wires=0)
        elif scenario == "shared": qml.RY(angle, wires=0); qml.RY(angle, wires=0)
        elif scenario == "scaled": qml.RY(2 * angle, wires=0)
        elif scenario == "nonlinear": qml.RY(qml.numpy.sin(angle), wires=0)
        elif scenario == "controlled": qml.Hadamard(wires=0); qml.CRY(angle, wires=[0, 1])
        elif scenario == "dynamic":
            qml.RY(angle, wires=0); outcome = qml.measure(0)
            qml.cond(outcome, qml.RY)(angle, wires=1)
        else:
            qml.RY(angle, wires=0)
            if scenario == "fixed_noise": qml.AmplitudeDamping(.3, wires=0)
            if scenario == "mps": qml.CNOT(wires=[0, 1]); qml.CNOT(wires=[1, 2])
        if scenario == "probabilities": return qml.probs(wires=[0])
        if scenario == "variance": return qml.var(qml.PauliZ(0))
        if scenario == "hamiltonian": observable = .3 * qml.PauliX(0) + .7 * qml.PauliZ(0)
        else: observable = qml.PauliY(0) if scenario == "rz_y" else qml.PauliX(0) if scenario in {"phase_x", "controlled"} else qml.PauliZ(width - 1)
        return qml.expval(observable)
    parameter = qml.numpy.array(theta, requires_grad=True)
    automatic_gradient = None
    if scenario == "dynamic":
        automatic_gradient = float(qml.jacobian(reference)(parameter))
        reference = qml.defer_measurements(reference)
    upstream = np.asarray(qml.jacobian(reference)(parameter), dtype=float)
    node = QNode(program, width, device=native_device)
    actual = node.jacobian(theta, method="parameter-shift")
    if isinstance(actual, dict): actual = list(actual.values())
    actual = np.asarray(actual)
    expected = {
        "rz_y": np.cos(theta), "shared": -2 * np.sin(2 * theta), "scaled": -2 * np.sin(2 * theta),
        "nonlinear": -np.sin(np.sin(theta)) * np.cos(theta), "controlled": -.5 * np.sin(theta / 2),
        "probabilities": np.array([-.5, .5]) * np.sin(theta), "variance": np.sin(2 * theta),
        "fixed_noise": -.7 * np.sin(theta), "dynamic": -(1 - np.cos(theta)) * np.sin(theta),
        "hamiltonian": .3 * np.cos(theta) - .7 * np.sin(theta),
    }.get(scenario, -np.sin(theta))
    difference = float(np.max(np.abs(actual - upstream)))
    record = {"scenario": scenario, "operation_measurement": scenario, "method": "native parameter-shift",
              "expected": np.asarray(expected).tolist(), "native": actual.tolist(), "upstream": upstream.tolist(),
              "absolute_difference": difference, "relative_difference": difference / max(1e-15, float(np.max(np.abs(upstream)))),
              "tolerance": 1e-8, "pennylane_version": qml.__version__, "status": "pass" if difference < 1e-8 else "fail"}
    if scenario == "dynamic":
        central = float((reference(parameter + 1e-5) - reference(parameter - 1e-5)) / 2e-5)
        record.update(automatic_public_gradient=automatic_gradient, explicit_deferred_gradient=float(upstream), public_forward_central_difference=central)
        np.testing.assert_allclose(actual, central, atol=1e-8)
    print(json.dumps(record, sort_keys=True))
    np.testing.assert_allclose(actual, expected, atol=1e-8, rtol=1e-8)
    np.testing.assert_allclose(actual, upstream, atol=1e-8, rtol=1e-8)
    if native_device is None and scenario not in {"dynamic"}:
        adjoint = node.jacobian(theta, method="adjoint")
        if isinstance(adjoint, dict): adjoint = list(adjoint.values())
        np.testing.assert_allclose(adjoint, upstream, atol=1e-8, rtol=1e-8)
