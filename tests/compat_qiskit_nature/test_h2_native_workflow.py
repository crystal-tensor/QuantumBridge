import math

from quantumbridge.compat.qiskit_nature import build_h2_problem, run_h2_native
from quantumbridge.schema.chemistry_results import H2WorkflowResult


def test_h2_native_workflow_actually_runs():
    result = run_h2_native()

    assert isinstance(result, H2WorkflowResult)
    assert result.workflow == "h2_native_exact"
    assert result.mode == "native_minimal"
    assert result.native_implementation is True
    assert result.production_ready is False
    assert result.qubit_count == 2
    assert result.particle_count == 2
    assert len(result.pauli_terms) >= 5
    assert math.isfinite(result.ground_state_energy)
    assert math.isfinite(result.electronic_energy)
    assert result.metadata["materials_band_gap"] is False


def test_h2_problem_metadata_is_vqe_ready():
    problem = build_h2_problem()
    assert problem.formula == "H2"
    assert problem.qubit_count == 2
    assert problem.hamiltonian.matrix(problem.qubit_count).shape == (4, 4)
