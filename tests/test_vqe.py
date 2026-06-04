# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/behavior_test_plan_v0.1.md.

import numpy as np

from quantumbridge import Circuit, Hamiltonian, PauliZ, StatevectorDevice, run_vqe


def test_simple_vqe_reduces_pauli_z_energy():
    hamiltonian = Hamiltonian([(1.0, PauliZ(0))])
    device = StatevectorDevice()

    def ansatz(params):
        return Circuit(1).ry(params[0], 0)

    initial = np.array([0.2])
    initial_energy = device.expectation(ansatz(initial), hamiltonian)
    result = run_vqe(hamiltonian, ansatz, initial, device=device, steps=40, learning_rate=0.25)
    assert result.metadata()["final_energy"] < initial_energy
    assert result.metadata()["best_energy"] < -0.9

