import math

import numpy as np

from quantumbridge.compat.qiskit_nature import build_h2_problem, build_lih_problem, run_h2_native, run_lih_native


def test_exact_diagonalization_matches_h2_matrix_minimum():
    problem = build_h2_problem()
    values = np.linalg.eigvalsh(problem.hamiltonian.matrix(problem.qubit_count))
    result = run_h2_native()

    assert math.isclose(result.electronic_energy, float(np.min(values)), rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(
        result.ground_state_energy,
        result.electronic_energy + result.nuclear_repulsion_energy,
        rel_tol=0.0,
        abs_tol=1e-12,
    )


def test_exact_diagonalization_matches_lih_matrix_minimum():
    problem = build_lih_problem()
    values = np.linalg.eigvalsh(problem.hamiltonian.matrix(problem.qubit_count))
    result = run_lih_native()

    assert math.isclose(result.electronic_energy, float(np.min(values)), rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(
        result.ground_state_energy,
        result.electronic_energy + result.nuclear_repulsion_energy,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
