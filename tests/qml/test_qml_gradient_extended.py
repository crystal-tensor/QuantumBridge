# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from math import cos, pi, sin

import numpy as np
import pytest

from quantumbridge import Circuit, PauliZ, StatevectorDevice, parameter_shift
from quantumbridge.qml import QNode, angle_embedding, basic_entangler
from quantumbridge.transforms import finite_difference


def test_qml_templates_and_gradient_methods_agree():
    circuit = angle_embedding(Circuit(2), [0.1, 0.2])
    basic_entangler(circuit, [0.3, 0.4])
    assert [op.name for op in circuit.operations] == ["ry", "ry", "ry", "ry", "cx"]

    device = StatevectorDevice()

    def objective(params):
        return device.expectation(Circuit(1).ry(params[0], 0), PauliZ(0))

    theta = pi / 4
    ps = parameter_shift(objective, np.array([theta]))[0]
    fd = finite_difference(objective, np.array([theta]))[0]
    assert abs(ps + sin(theta)) < 1e-7
    assert abs(ps - fd) < 1e-5


def test_qnode_callable_and_invalid_parameter_shape():
    def program(tape, theta):
        tape.ry(theta, 0)
        return tape.expval(PauliZ(0))

    assert abs(QNode(program, 1)(0.4) - cos(0.4)) < 1e-10
    with pytest.raises(TypeError):
        angle_embedding(Circuit(1), [object()])

