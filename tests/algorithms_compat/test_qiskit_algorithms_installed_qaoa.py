# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import math
import numpy as np
import pytest

from quantumbridge.algorithms.adapters import QiskitAlgorithmsAdapter


def test_qiskit_algorithms_installed_qaoa_wraps_quantumbridge_result_schema():
    pytest.importorskip("qiskit_algorithms", reason="optional dependency unavailable: qiskit-algorithms")

    from qiskit.primitives import StatevectorSampler
    from qiskit.quantum_info import SparsePauliOp
    from qiskit_algorithms.minimum_eigensolvers import QAOA
    from qiskit_algorithms.optimizers import COBYLA

    upstream = QAOA(StatevectorSampler(), COBYLA(maxiter=3), reps=1, initial_point=np.array([0.1, 0.2]))
    upstream_result = upstream.compute_minimum_eigenvalue(SparsePauliOp.from_list([("ZZ", 1.0)]))
    qb_result = QiskitAlgorithmsAdapter().wrap_result(upstream_result, "QAOA")

    assert math.isfinite(float(np.real(upstream_result.eigenvalue)))
    assert qb_result.validate_schema()
    assert qb_result.to_dict()["provenance"]["dependency"] == "qiskit-algorithms"
    assert qb_result.metadata()["upstream_result_type"] == "SamplingVQEResult"
