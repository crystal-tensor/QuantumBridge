# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit was copied.

import numpy as np
import pytest

qiskit_quantum_info = pytest.importorskip("qiskit.quantum_info")

from quantumbridge.information import (  # noqa: E402
    Chi,
    Choi,
    Kraus,
    Operator,
    PTM,
    Stinespring,
    SuperOp,
    average_gate_fidelity,
    gate_error,
    process_fidelity,
)


def _operators(gamma=0.2):
    return [
        np.diag([1, np.sqrt(1 - gamma)]),
        np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex),
    ]


def test_all_native_channel_representations_match_qiskit():
    upstream = qiskit_quantum_info.Kraus(_operators())
    native = Kraus(_operators())
    pairs = (
        (qiskit_quantum_info.SuperOp, SuperOp),
        (qiskit_quantum_info.Choi, Choi),
        (qiskit_quantum_info.PTM, PTM),
        (qiskit_quantum_info.Chi, Chi),
        (qiskit_quantum_info.Stinespring, Stinespring),
    )

    for upstream_type, native_type in pairs:
        np.testing.assert_allclose(
            native_type(native).data,
            upstream_type(upstream).data,
            atol=1e-12,
        )


def test_native_channel_algebra_matches_qiskit():
    x_matrix = np.array([[0, 1], [1, 0]], dtype=complex)
    h_matrix = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    upstream_x = qiskit_quantum_info.SuperOp(qiskit_quantum_info.Operator(x_matrix))
    upstream_h = qiskit_quantum_info.SuperOp(qiskit_quantum_info.Operator(h_matrix))
    native_x = SuperOp(Operator(x_matrix))
    native_h = SuperOp(Operator(h_matrix))

    for method in ("compose", "dot", "tensor", "expand"):
        np.testing.assert_allclose(
            getattr(native_x, method)(native_h).data,
            getattr(upstream_x, method)(upstream_h).data,
            atol=1e-12,
        )

    upstream_noise = qiskit_quantum_info.SuperOp(qiskit_quantum_info.Kraus(_operators()))
    native_noise = SuperOp(Kraus(_operators()))
    for method in ("adjoint", "conjugate", "transpose"):
        np.testing.assert_allclose(
            getattr(native_noise, method)().data,
            getattr(upstream_noise, method)().data,
            atol=1e-12,
        )


def test_native_channel_fidelity_metrics_match_qiskit():
    upstream = qiskit_quantum_info.Kraus(_operators())
    native = Kraus(_operators())

    assert process_fidelity(native) == pytest.approx(
        qiskit_quantum_info.process_fidelity(upstream),
        abs=1e-12,
    )
    assert average_gate_fidelity(native) == pytest.approx(
        qiskit_quantum_info.average_gate_fidelity(upstream),
        abs=1e-12,
    )
    assert gate_error(native) == pytest.approx(
        qiskit_quantum_info.gate_error(upstream),
        abs=1e-12,
    )


def test_generalized_channel_and_arithmetic_match_qiskit():
    left = (
        np.array([[1, 0], [0, 0.5]], dtype=complex),
        np.array([[0, 0.2], [0, 0]], dtype=complex),
    )
    right = (
        np.array([[1, 0], [0, 0.3]], dtype=complex),
        np.array([[0, 0.4], [0, 0]], dtype=complex),
    )
    upstream = qiskit_quantum_info.Kraus((left, right))
    native = Kraus((left, right))

    np.testing.assert_allclose(
        SuperOp(native).data,
        qiskit_quantum_info.SuperOp(upstream).data,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        SuperOp(Stinespring(native)).data,
        qiskit_quantum_info.SuperOp(qiskit_quantum_info.Stinespring(upstream)).data,
        atol=1e-12,
    )

    upstream_identity = qiskit_quantum_info.Kraus(
        qiskit_quantum_info.Operator(np.eye(2))
    )
    native_identity = Kraus(Operator(np.eye(2)))
    for upstream_result, native_result in (
        (upstream_identity + upstream_identity, native_identity + native_identity),
        (0.5 * upstream_identity, 0.5 * native_identity),
        (upstream_identity @ upstream_identity, native_identity @ native_identity),
    ):
        np.testing.assert_allclose(
            SuperOp(native_result).data,
            qiskit_quantum_info.SuperOp(upstream_result).data,
            atol=1e-12,
        )
