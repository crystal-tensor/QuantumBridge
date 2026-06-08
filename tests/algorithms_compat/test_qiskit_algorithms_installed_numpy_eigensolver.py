# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import math
import numpy as np
import pytest

from quantumbridge.algorithms.adapters import QiskitAlgorithmsAdapter


def test_qiskit_algorithms_installed_numpy_minimum_eigensolver_wraps_schema():
    pytest.importorskip("qiskit_algorithms", reason="optional dependency unavailable: qiskit-algorithms")

    from qiskit.quantum_info import SparsePauliOp
    from qiskit_algorithms.minimum_eigensolvers import NumPyMinimumEigensolver

    upstream_result = NumPyMinimumEigensolver().compute_minimum_eigenvalue(SparsePauliOp.from_list([("Z", 1.0)]))
    qb_result = QiskitAlgorithmsAdapter().wrap_result(upstream_result, "NumPyMinimumEigensolver")

    assert math.isfinite(float(np.real(upstream_result.eigenvalue)))
    assert qb_result.validate_schema()
    assert qb_result.to_dict()["provenance"]["mode"] == "Upstream Passthrough"
    assert qb_result.metadata()["upstream_result_type"] == "NumPyMinimumEigensolverResult"
