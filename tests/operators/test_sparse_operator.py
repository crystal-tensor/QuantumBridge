# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge import Circuit, StatevectorDevice
from quantumbridge.operators import SparsePauliOperator


def test_sparse_operator_to_hamiltonian_expectation():
    op = SparsePauliOperator([("Z", 1.0)])
    value = StatevectorDevice().expectation(Circuit(1), op.to_hamiltonian())
    assert abs(value - 1.0) < 1e-12

