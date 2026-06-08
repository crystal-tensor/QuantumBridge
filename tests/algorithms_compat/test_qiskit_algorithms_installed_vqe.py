# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import math
import numpy as np
import pytest

from quantumbridge.algorithms.adapters import QiskitAlgorithmsAdapter


def test_qiskit_algorithms_installed_vqe_wraps_quantumbridge_result_schema():
    pytest.importorskip("qiskit_algorithms", reason="optional dependency unavailable: qiskit-algorithms")

    from qiskit import QuantumCircuit
    from qiskit.circuit import Parameter
    from qiskit.primitives import StatevectorEstimator
    from qiskit.quantum_info import SparsePauliOp
    from qiskit_algorithms.minimum_eigensolvers import VQE
    from qiskit_algorithms.optimizers import COBYLA

    theta = Parameter("theta")
    ansatz = QuantumCircuit(1)
    ansatz.ry(theta, 0)
    upstream = VQE(StatevectorEstimator(), ansatz, COBYLA(maxiter=3), initial_point=np.array([0.1]))
    upstream_result = upstream.compute_minimum_eigenvalue(SparsePauliOp.from_list([("Z", 1.0)]))
    qb_result = QiskitAlgorithmsAdapter().wrap_result(upstream_result, "VQE")

    assert math.isfinite(float(np.real(upstream_result.eigenvalue)))
    assert qb_result.validate_schema()
    assert qb_result.to_dict()["provenance"]["dependency"] == "qiskit-algorithms"
    assert qb_result.metadata()["upstream_result_type"] == "VQEResult"
