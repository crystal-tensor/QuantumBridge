# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Algorithms was copied.

from quantumbridge.compat.qiskit_algorithms import (
    build_maxcut_problem_native,
    maxcut_objective_value,
    qaoa_cost_hamiltonian_metadata,
    run_qaoa_native_maxcut,
    solve_maxcut_bruteforce_native,
)


def test_native_qaoa_maxcut_actually_runs():
    edges = ((0, 1), (1, 2), (2, 0))
    result = run_qaoa_native_maxcut(edges, num_nodes=3, p=1)
    assert result.algorithm == "QAOA"
    assert result.mode == "native_minimal"
    assert result.bitstring is not None
    assert result.objective_value == 2.0
    assert result.probabilities
    assert result.validate()


def test_native_qaoa_helpers_return_maxcut_metadata():
    problem = build_maxcut_problem_native(((0, 1),), num_nodes=2)
    assert maxcut_objective_value("01", problem["edges"]) == 1
    exact = solve_maxcut_bruteforce_native(problem["edges"], problem["num_nodes"])
    assert exact["best_value"] == 1
    metadata = qaoa_cost_hamiltonian_metadata(problem["edges"], problem["num_nodes"])
    assert metadata["problem_type"] == "maxcut"
    assert metadata["terms"]
