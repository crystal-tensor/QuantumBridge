# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from math import pi

import numpy as np
import pytest

from quantumbridge import Circuit, StatevectorDevice


def test_statevector_extended_gate_correctness_and_normalization():
    device = StatevectorDevice()
    cases = [
        Circuit(1).h(0),
        Circuit(1).x(0),
        Circuit(1).rx(pi / 5, 0),
        Circuit(1).ry(pi / 5, 0),
        Circuit(1).rz(pi / 5, 0),
        Circuit(2).h(0).cx(0, 1),
        Circuit(2).x(0).cz(0, 1),
    ]
    for circuit in cases:
        state = device.statevector(circuit)
        assert abs(np.vdot(state, state) - 1.0) < 1e-10


def test_statevector_ghz_state_probabilities():
    circuit = Circuit(3).h(0).cx(0, 1).cx(1, 2)
    probs = StatevectorDevice().probabilities(circuit)
    assert abs(probs["000"] - 0.5) < 1e-12
    assert abs(probs["111"] - 0.5) < 1e-12


def test_invalid_gate_dimension_and_invalid_qubit_index():
    with pytest.raises(ValueError, match="shape"):
        Circuit(1).unitary(np.eye(4), [0])
    with pytest.raises(ValueError, match="outside"):
        Circuit(1).h(2)

