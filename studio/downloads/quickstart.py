# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Offline QuantumBridge quickstart. Run: python quickstart.py"""
import math
from quantumbridge import Circuit, StatevectorDevice, PauliZ
from quantumbridge.qml import NativeQNode

circuit = Circuit(2).h(0).cx(0, 1)
device = StatevectorDevice()
probabilities = device.probabilities(circuit)
counts = device.counts(circuit, shots=1024, seed=7)
assert math.isclose(probabilities["00"], 0.5, abs_tol=1e-12)
assert math.isclose(probabilities["11"], 0.5, abs_tol=1e-12)
assert set(counts) <= {"00", "11"}
assert sum(counts.values()) == 1024
print("Bell probabilities:", probabilities)
print("Local counts:", counts)

def program(tape, theta):
    tape.ry(theta, 0)
    return tape.expval(PauliZ(0))

node = NativeQNode(program, 1, diff_method="adjoint")
value, gradient = node.execute_and_compute_derivatives(0.4)
assert math.isclose(value, math.cos(0.4), abs_tol=1e-10)
assert math.isclose(gradient, -math.sin(0.4), abs_tol=1e-10)
print("Expectation:", value, "Gradient:", gradient)
print("PASS: native simulation only; no cloud tasks.")
