# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Run real native standard objects, control phases and higher derivatives."""

import numpy as np
from quantumbridge import Circuit, Parameter, PauliX
from quantumbridge.circuit_library import RXGate, CUGate, UnitaryGate
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.serialization import qpy_dumps, qpy_loads


p = Parameter("theta")
rotation = RXGate(.3)
copied = rotation.copy()
copied.params[0] = .7
assert rotation.params == [.3]
assert type(copied.inverse()).__name__ == "RXGate"
assert type(copied.control(1, annotated=True)).__name__ == "CRXGate"
numeric = Circuit(1).rx(.3, 0).to_gate().power(2)
assert type(numeric) is UnitaryGate
expected = np.array([[np.cos(.3), -1j*np.sin(.3)], [-1j*np.sin(.3), np.cos(.3)]])
np.testing.assert_allclose(Operator(numeric).data, expected, atol=2e-13, rtol=0)

source = Circuit(2).h(0).append(CUGate(.4, .2, -.1, p), [0, 1])
restored = qpy_loads(qpy_dumps(source))[0]
assert type(restored.operations[1].metadata["gate"]) is CUGate
node = QNode.from_circuit(restored, PauliX(0), max_diff=2)
x, scale = .3, np.cos(.2)
assert abs(node(x)-scale*np.cos(x)) < 3e-12
assert abs(node.compute_jacobian(x)+scale*np.sin(x)) < 2e-10
assert abs(node.compute_hessian(x)+scale*np.cos(x)) < 4e-10
assert abs(node.compute_hvp(.3, x)+.3*scale*np.cos(x)) < 4e-10
print("Native standard return types, owned mutation, coherent CU phase, QPY and Jacobian/Hessian/HVP passed.")
print("Full Qiskit/PennyLane functional parity remains incomplete.")
