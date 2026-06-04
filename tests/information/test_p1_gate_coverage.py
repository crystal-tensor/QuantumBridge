# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from math import pi

import numpy as np

from quantumbridge import Circuit, StatevectorDevice


def test_s_t_phase_and_swap_gate_behavior():
    device = StatevectorDevice()
    np.testing.assert_allclose(device.statevector(Circuit(1).x(0).s(0)), [0, 1j], atol=1e-12)
    np.testing.assert_allclose(device.statevector(Circuit(1).x(0).t(0)), [0, np.exp(1j * pi / 4)], atol=1e-12)
    np.testing.assert_allclose(device.statevector(Circuit(1).x(0).phase(pi / 3, 0)), [0, np.exp(1j * pi / 3)], atol=1e-12)
    probs = device.probabilities(Circuit(2).x(0).swap(0, 1))
    assert probs["01"] == 1.0

