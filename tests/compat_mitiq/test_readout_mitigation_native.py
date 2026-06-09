import numpy as np
import pytest

from quantumbridge.compat.mitiq import (
    apply_readout_error_to_counts,
    bell_circuit,
    build_single_qubit_readout_calibration_matrix,
    build_tensor_product_readout_matrix,
    mitigate_readout_counts,
    normalize_counts_to_probabilities,
    run_readout_mitigation_native,
)
from quantumbridge.schema.error_mitigation_results import ReadoutMitigationResult


def test_readout_calibration_matrix_is_valid_column_stochastic():
    matrix = build_single_qubit_readout_calibration_matrix(0.1, 0.2)
    arr = np.asarray(matrix)

    assert arr.shape == (2, 2)
    assert arr[:, 0].sum() == pytest.approx(1.0)
    assert arr[:, 1].sum() == pytest.approx(1.0)


def test_tensor_product_readout_matrix_shape():
    matrix = build_tensor_product_readout_matrix(3, 0.05, 0.05)

    assert len(matrix) == 8
    assert len(matrix[0]) == 8


def test_readout_noisy_counts_and_mitigated_probabilities_are_generated():
    result = run_readout_mitigation_native(bell_circuit(), shots=128, seed=9)

    assert isinstance(result, ReadoutMitigationResult)
    assert result.validate() is True
    assert sum(result.raw_counts.values()) == 128
    assert sum(result.noisy_counts.values()) == 128
    assert sum(result.mitigated_probabilities.values()) == pytest.approx(1.0)
    assert result.production_ready is False
    assert result.metadata["hardware_calibration"] is False


def test_readout_mitigation_helpers_are_deterministic_with_seed():
    first = apply_readout_error_to_counts({"0": 10}, 0.2, 0.1, shots=10, seed=1)
    second = apply_readout_error_to_counts({"0": 10}, 0.2, 0.1, shots=10, seed=1)
    matrix = build_single_qubit_readout_calibration_matrix(0.2, 0.1)
    mitigated = mitigate_readout_counts(first, matrix, ["0", "1"])

    assert first == second
    assert normalize_counts_to_probabilities({"0": 3, "1": 1}) == {"0": 0.75, "1": 0.25}
    assert sum(mitigated.values()) == pytest.approx(1.0)
