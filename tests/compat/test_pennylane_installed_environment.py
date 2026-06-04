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
    observable_from_pennylane,
)
from quantumbridge.qml import QNode
from quantumbridge.utils.math import PauliZ

qml = pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")


def test_pennylane_installed_environment_rx_ry_rz_observable_and_tape():
    def program(tape, theta):
        tape.rx(theta, 0)
        tape.ry(theta, 0)
        tape.rz(theta, 0)
        return tape.expval(PauliZ(0))

    value = QNode(program, 1)(0.2)
    assert isinstance(value, float)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        obs = qml.PauliZ(0)
        script = qml.tape.QuantumScript([qml.RX(0.2, 0), qml.RY(0.2, 0), qml.RZ(0.2, 0)], [qml.expval(obs)])

    circuit, bridged = circuit_and_observable_from_pennylane_tape(script)
    assert [op.name for op in circuit.operations] == ["rx", "ry", "rz"]
    assert observable_from_pennylane(obs).terms == ((0, "Z"),)
    assert bridged.terms == ((0, "Z"),)
    assert abs(float(PennyLaneDeviceAdapter(PauliZ(0)).run(Circuit(1).ry(0.2, 0))) - cos(0.2)) < 1e-10


def test_pennylane_adapter_exception_path_is_clear():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        obs = qml.Hadamard(0)
    with pytest.raises(ValueError, match="does not support"):
        observable_from_pennylane(obs)

