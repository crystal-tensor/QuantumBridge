# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from math import cos
import warnings

import pytest

from quantumbridge import Circuit
from quantumbridge.compat.pennylane_adapter import (
    PennyLaneDeviceAdapter,
    circuit_and_observable_from_pennylane_tape,
    circuit_to_pennylane_callable,
    observable_from_pennylane,
)
from quantumbridge.qml import QNode
from quantumbridge.utils.math import PauliZ

qml = pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")


def test_pennylane_adapter_realistic_workflow():
    def program(tape, theta):
        tape.ry(theta, 0)
        return tape.expval(PauliZ(0))

    assert abs(QNode(program, 1)(0.2) - cos(0.2)) < 1e-10

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        obs = qml.PauliZ(0)
        script = qml.tape.QuantumScript([qml.RY(0.2, wires=0)], [qml.expval(obs)])

    bridged_obs = observable_from_pennylane(obs)
    circuit, tape_obs = circuit_and_observable_from_pennylane_tape(script)
    executable = circuit_to_pennylane_callable(circuit, tape_obs)
    adapter_value = PennyLaneDeviceAdapter(bridged_obs).run(Circuit(1).ry(0.2, 0))

    assert bridged_obs.terms == ((0, "Z"),)
    assert tape_obs.terms == ((0, "Z"),)
    assert abs(float(executable()) - cos(0.2)) < 1e-10
    assert abs(float(adapter_value) - cos(0.2)) < 1e-10
