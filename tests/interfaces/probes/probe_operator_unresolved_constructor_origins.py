# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Open source-origin differentials, never included in green gate statistics."""

import numpy as np
import pytest

from quantumbridge.information import Operator, Kraus
from quantumbridge.core.annotated_operation import AnnotatedOperation, InverseModifier
from probe_operator_construction_parity import circuit_pair
from probe_operator_composition_public_parity import bit_reversal


@pytest.mark.parametrize("consumer", ["annotation", "channel"])
def test_native_derived_operator_source_is_not_raw_literal(consumer):
    from qiskit.quantum_info import Operator as QO, Kraus as QK, SuperOp as QS
    from qiskit.circuit import AnnotatedOperation as QA, InverseModifier as QI
    native, public = circuit_pair(2)
    if consumer == "annotation":
        actual = AnnotatedOperation(native.to_gate(), InverseModifier()).to_matrix()
        expected = QA(public.to_gate(), QI()).to_matrix()
        native_matrix = Operator(native).data.conj().T
    else:
        actual, expected = Kraus(native).to_operator(), QO(public)
        native_matrix = Operator(native).data
    # Prove native numbers first. The open assertion is the subsequent public
    # representation; no probability or arbitrary-phase comparison hides it.
    np.testing.assert_allclose(actual.data, native_matrix, atol=2e-14, rtol=0)
    order = bit_reversal(2)
    np.testing.assert_allclose(native_matrix[np.ix_(order, order)], expected.data, atol=2e-14, rtol=0)
    if consumer == "channel":
        # Kraus decompositions may choose a different global phase. Compare
        # the complete linear map, not two differently gauged Kraus matrices.
        converted = actual.as_qiskit_operator().data
        independent = np.kron(expected.data.conj(), expected.data)
        np.testing.assert_allclose(QS(QK(public)).data, independent, atol=2e-14, rtol=0)
        np.testing.assert_allclose(np.kron(converted.conj(), converted), independent, atol=2e-14, rtol=0)
    else:
        np.testing.assert_allclose(actual.as_qiskit_operator().data, expected.data, atol=2e-14, rtol=0)
