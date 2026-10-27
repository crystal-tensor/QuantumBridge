# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Explicit full-call wire-parity probe; failures are not supported-domain PASS."""

import numpy as np
import pytest

import quantumbridge as qb


@pytest.mark.parametrize("local_width", [1, 2])
def test_identical_public_unitary_call_matches_installed_sdk_after_global_basis_conversion(local_width):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    rng = np.random.default_rng(4051 + local_width)
    dimension = 1 << local_width
    matrix, _ = np.linalg.qr(rng.normal(size=(dimension, dimension))
        + 1j * rng.normal(size=(dimension, dimension)))
    wires = [3] if local_width == 1 else [3, 1]

    def build(kind):
        circuit = kind(4, global_phase=.23)
        circuit.h(0)
        circuit.ry(.3, 1)
        circuit.unitary(matrix, wires)
        circuit.cx(0, 2)
        return circuit

    actual = qb.StatevectorDevice().statevector(build(qb.QuantumCircuit))
    public = np.asarray(Statevector.from_instruction(build(QuantumCircuit)).data)
    # Convert only the external global bit order, not the local matrix/qargs.
    order = [int(f"{index:04b}"[::-1], 2) for index in range(16)]
    np.testing.assert_allclose(actual, public[order], atol=2e-12, rtol=0)
