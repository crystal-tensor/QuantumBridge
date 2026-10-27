# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Complete phase-sensitive public annotation construction differentials."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.core.standard_gates import UnitaryGate
from probe_operator_construction_parity import circuit_pair
from probe_operator_composition_public_parity import bit_reversal


@pytest.mark.parametrize("method", ["inverse", "power", "control", "inverse_control"])
@pytest.mark.parametrize("raw", [False, True])
def test_annotation_matrix_origin_tracks_actual_resolved_source(raw, method):
    from qiskit.circuit import AnnotatedOperation as QA, InverseModifier as QI, PowerModifier as QP, ControlModifier as QC
    from qiskit.circuit.library import UnitaryGate as QU
    native, public = circuit_pair(2)
    if raw:
        matrix = np.array([[1, 1, 1, 1], [1, 1j, -1, -1j],
            [1, -1, 1, -1], [1, -1j, -1, 1j]], complex) / 2
        base, reference = UnitaryGate(matrix), QU(matrix)
    else:base, reference = native.to_gate(), public.to_gate()
    mods = {"inverse": [qb.InverseModifier()], "power": [qb.PowerModifier(.37)],
        "control": [qb.ControlModifier(1, 0)],
        "inverse_control": [qb.InverseModifier(), qb.ControlModifier(1, 0)]}[method]
    public_mods = {"inverse": [QI()], "power": [QP(.37)], "control": [QC(1, 0)],
        "inverse_control": [QI(), QC(1, 0)]}[method]
    actual = qb.AnnotatedOperation(base, mods).to_matrix()
    expected = QA(reference, public_mods).to_matrix().data
    # Legacy native matrix values are not rewritten by provenance repair.
    np.testing.assert_allclose(actual.data, qb.resolve_annotated_operation(
        qb.AnnotatedOperation(base, mods)).to_matrix(), atol=2e-14, rtol=0)
    if raw and "control" in method:
        assert actual.__dict__["_public_matrix_basis"] == "hybrid"
        assert actual.__dict__["_literal_target_width"] == 2
    np.testing.assert_allclose(actual.as_qiskit_operator().data, expected, atol=3e-13, rtol=0)
    if not raw:
        order = bit_reversal(actual.num_qubits)
        np.testing.assert_allclose(actual.data[np.ix_(order, order)], expected, atol=3e-13, rtol=0)
    elif "control" not in method:assert actual.__dict__.get("_public_matrix_basis") is None
    for derived in (actual.copy(), actual.adjoint(), actual.power(2)):
        assert derived.__dict__.get("_public_matrix_basis") == actual.__dict__.get("_public_matrix_basis")
