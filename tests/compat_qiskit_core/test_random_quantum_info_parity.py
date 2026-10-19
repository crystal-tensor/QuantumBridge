# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit was copied.

import numpy as np
import pytest

qiskit_quantum_info = pytest.importorskip("qiskit.quantum_info")

from quantumbridge.information import (  # noqa: E402
    pauli_basis,
    random_hermitian,
    random_quantum_channel,
)


def test_random_hermitian_seeded_values_match_qiskit():
    for traceless in (False, True):
        np.testing.assert_allclose(
            random_hermitian(4, traceless=traceless, seed=11).data,
            qiskit_quantum_info.random_hermitian(
                4,
                traceless=traceless,
                seed=11,
            ).data,
            atol=1e-12,
        )


def test_pauli_basis_orders_match_qiskit():
    for weight in (False, True):
        assert pauli_basis(2, weight=weight).to_labels() == (
            qiskit_quantum_info.pauli_basis(2, weight=weight).to_labels()
        )


def test_random_quantum_channel_contract_matches_qiskit():
    native = random_quantum_channel(2, 4, rank=2, seed=11)
    upstream = qiskit_quantum_info.random_quantum_channel(2, 4, rank=2, seed=11)

    assert native.dim == upstream.dim == (2, 4)
    assert native.data.shape == upstream.data.shape == (8, 2)
    assert len(native.to_kraus().data) == len(qiskit_quantum_info.Kraus(upstream).data) == 2
    assert native.is_cptp()
    assert upstream.is_cptp()
