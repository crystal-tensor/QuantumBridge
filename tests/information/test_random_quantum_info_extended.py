# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import numpy as np

from quantumbridge.information import (
    Operator,
    pauli_basis,
    random_hermitian,
    random_quantum_channel,
)


def test_random_hermitian_is_seeded_hermitian_and_optionally_traceless():
    matrix = random_hermitian(4, seed=11)
    traceless = random_hermitian(4, traceless=True, seed=11)

    np.testing.assert_allclose(matrix.data, matrix.data.conj().T, atol=1e-12)
    np.testing.assert_allclose(matrix.data, random_hermitian(4, seed=11).data, atol=1e-12)
    np.testing.assert_allclose(traceless.data, traceless.data.conj().T, atol=1e-12)
    assert abs(np.trace(traceless.data)) < 1e-12
    assert isinstance(matrix, Operator)


def test_pauli_basis_order_and_weight_order():
    assert pauli_basis(2).to_labels() == [
        "II",
        "IX",
        "IY",
        "IZ",
        "XI",
        "XX",
        "XY",
        "XZ",
        "YI",
        "YX",
        "YY",
        "YZ",
        "ZI",
        "ZX",
        "ZY",
        "ZZ",
    ]
    weighted = pauli_basis(2, weight=True)
    assert weighted.to_labels()[:7] == ["II", "IX", "IY", "IZ", "XI", "YI", "ZI"]


def test_random_quantum_channel_is_seeded_cptp_with_requested_dimensions_and_rank():
    channel = random_quantum_channel(2, 4, rank=2, seed=7)
    repeated = random_quantum_channel(2, 4, rank=2, seed=7)

    assert channel.dim == (2, 4)
    assert channel.data.shape == (8, 2)
    assert len(channel.to_kraus().data) == 2
    assert channel.is_cptp()
    np.testing.assert_allclose(channel.data, repeated.data, atol=1e-12)
