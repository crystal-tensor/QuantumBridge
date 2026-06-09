import math

from quantumbridge.compat.qiskit_nature import build_lih_problem, run_lih_native
from quantumbridge.schema.chemistry_results import LiHWorkflowResult


def test_lih_native_workflow_actually_runs():
    result = run_lih_native()

    assert isinstance(result, LiHWorkflowResult)
    assert result.workflow == "lih_native_exact"
    assert result.mode == "native_minimal"
    assert result.native_implementation is True
    assert result.production_ready is False
    assert result.qubit_count == 4
    assert result.particle_count == 4
    assert len(result.pauli_terms) >= 8
    assert math.isfinite(result.ground_state_energy)
    assert math.isfinite(result.electronic_energy)
    assert result.metadata["materials_band_gap"] is False


def test_lih_problem_metadata_is_small_and_deterministic():
    problem = build_lih_problem()
    assert problem.formula == "LiH"
    assert problem.qubit_count == 4
    assert problem.hamiltonian.matrix(problem.qubit_count).shape == (16, 16)
