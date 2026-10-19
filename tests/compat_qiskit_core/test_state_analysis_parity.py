# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit was copied.

import numpy as np
import pytest

qiskit_quantum_info = pytest.importorskip("qiskit.quantum_info")

from quantumbridge.information import (  # noqa: E402
    DensityMatrix,
    Operator,
    anti_commutator,
    commutator,
    concurrence,
    double_commutator,
    entanglement_of_formation,
    entropy,
    mutual_information,
    negativity,
    schmidt_decomposition,
    shannon_entropy,
)


def _random_state(seed=7):
    rng = np.random.default_rng(seed)
    vector = rng.normal(size=4) + 1j * rng.normal(size=4)
    return vector / np.linalg.norm(vector)


def test_state_analysis_metrics_match_qiskit():
    vector = _random_state()
    native_rho = DensityMatrix.from_statevector(vector)
    upstream_rho = qiskit_quantum_info.DensityMatrix(vector)

    for native_value, upstream_value in (
        (entropy(native_rho), qiskit_quantum_info.entropy(upstream_rho)),
        (
            mutual_information(native_rho),
            qiskit_quantum_info.mutual_information(upstream_rho),
        ),
        (concurrence(native_rho), qiskit_quantum_info.concurrence(upstream_rho)),
        (
            entanglement_of_formation(native_rho),
            qiskit_quantum_info.entanglement_of_formation(upstream_rho),
        ),
        (negativity(native_rho, [0]), qiskit_quantum_info.negativity(upstream_rho, [0])),
        (
            shannon_entropy([0.2, 0.3, 0.5]),
            qiskit_quantum_info.shannon_entropy([0.2, 0.3, 0.5]),
        ),
    ):
        assert native_value == pytest.approx(upstream_value, abs=1e-12)


def test_schmidt_decomposition_matches_qiskit():
    vector = _random_state()
    native = schmidt_decomposition(vector, [0])
    upstream = qiskit_quantum_info.schmidt_decomposition(
        qiskit_quantum_info.Statevector(vector),
        [0],
    )

    assert len(native) == len(upstream)
    for native_term, upstream_term in zip(native, upstream):
        assert native_term[0] == pytest.approx(upstream_term[0], abs=1e-12)
        np.testing.assert_allclose(native_term[1].data, upstream_term[1].data, atol=1e-12)
        np.testing.assert_allclose(native_term[2].data, upstream_term[2].data, atol=1e-12)


def test_operator_algebra_helpers_match_qiskit():
    native = [Operator.from_label(label) for label in ("X", "Y", "Z")]
    upstream = [qiskit_quantum_info.Operator(item.data) for item in native]

    for native_value, upstream_value in (
        (commutator(native[0], native[1]), qiskit_quantum_info.commutator(upstream[0], upstream[1])),
        (
            anti_commutator(native[0], native[1]),
            qiskit_quantum_info.anti_commutator(upstream[0], upstream[1]),
        ),
        (
            double_commutator(*native),
            qiskit_quantum_info.double_commutator(*upstream),
        ),
        (
            double_commutator(*native, commutator=False),
            qiskit_quantum_info.double_commutator(*upstream, commutator=False),
        ),
    ):
        np.testing.assert_allclose(native_value.data, upstream_value.data, atol=1e-12)
