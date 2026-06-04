# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.algorithms.adapters import QiskitAlgorithmsAdapter


def test_qiskit_algorithms_installed_optimizer_adapter_lists_two_optimizers():
    pytest.importorskip("qiskit_algorithms", reason="optional dependency unavailable: qiskit-algorithms")

    from qiskit_algorithms.optimizers import COBYLA, SPSA

    optimizers = [COBYLA(maxiter=1), SPSA(maxiter=1)]
    statuses = [QiskitAlgorithmsAdapter().optimizer(type(opt).__name__) for opt in optimizers]

    assert [status["algorithm"] for status in statuses] == ["COBYLA", "SPSA"]
    assert all(status["dependency"] == "qiskit-algorithms" for status in statuses)
