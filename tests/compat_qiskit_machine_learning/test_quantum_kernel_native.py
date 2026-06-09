import numpy as np

from quantumbridge.compat.qiskit_machine_learning import (
    compute_quantum_kernel_matrix,
    compute_state_fidelity,
    make_xor_dataset,
    run_quantum_kernel_native,
)


def test_state_fidelity_identity():
    assert compute_state_fidelity([1, 0], [1, 0]) == 1.0


def test_quantum_kernel_matrix_shape_symmetry_and_diagonal():
    x_values, _ = make_xor_dataset()
    matrix = compute_quantum_kernel_matrix(x_values)

    assert matrix.shape == (4, 4)
    assert np.allclose(matrix, matrix.T)
    assert np.allclose(np.diag(matrix), np.ones(4))


def test_run_quantum_kernel_native_schema():
    result = run_quantum_kernel_native()

    assert result.validate() is True
    assert result.workflow == "quantum_kernel_native"
    assert result.production_ready is False
    assert result.kernel_matrix
