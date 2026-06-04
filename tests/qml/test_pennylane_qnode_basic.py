# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from math import cos

import pytest

from quantumbridge import Circuit
from quantumbridge.compat.pennylane_adapter import PennyLaneDeviceAdapter, circuit_to_pennylane_callable, ir_to_pennylane_callable
from quantumbridge.qml import QNode
from quantumbridge.utils.math import PauliZ


def test_qnode_like_wrapper_returns_expectation():
    def program(tape, theta):
        tape.ry(theta, 0)
        return tape.expval(PauliZ(0))

    qnode = QNode(program, num_qubits=1)
    assert abs(qnode(0.3) - cos(0.3)) < 1e-10


def test_circuit_to_pennylane_executable_form():
    pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")
    executable = circuit_to_pennylane_callable(Circuit(1).ry(0.3, 0), PauliZ(0))
    assert abs(float(executable()) - cos(0.3)) < 1e-10


def test_ir_to_pennylane_executable_form():
    pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")
    executable = ir_to_pennylane_callable(Circuit(1).ry(0.3, 0).to_ir(), PauliZ(0))
    assert abs(float(executable()) - cos(0.3)) < 1e-10


def test_pennylane_device_adapter_runs_circuit():
    pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")
    value = PennyLaneDeviceAdapter(PauliZ(0)).run(Circuit(1).ry(0.3, 0))
    assert abs(float(value) - cos(0.3)) < 1e-10
