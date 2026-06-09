# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Optimization was copied.

from quantumbridge.compat.qiskit_optimization import (
    add_binary_vars,
    add_linear_constraint,
    create_quadratic_program_native,
    set_minimize,
    solve_quadratic_program_bruteforce_native,
)


def test_bruteforce_solver_returns_feasible_best_solution():
    problem = create_quadratic_program_native("solve")
    add_binary_vars(problem, ("x0", "x1", "x2"))
    set_minimize(
        problem,
        linear={"x0": -1.0, "x1": -0.7, "x2": -0.25},
        quadratic={("x0", "x1"): 0.35, ("x1", "x2"): 0.15},
    )
    add_linear_constraint(problem, {"x0": 1, "x1": 1, "x2": 1}, "==", 2)

    result = solve_quadratic_program_bruteforce_native(problem)

    assert result.feasible
    assert result.assignment == {"x0": 1, "x1": 1, "x2": 0}
    assert result.objective_value == -1.35
    assert len(result.samples) == 8
    assert all(sum(row.values()) == 2 for row in result.feasible_assignments)


def test_infeasible_problem_is_reported_without_fake_solution():
    problem = create_quadratic_program_native("infeasible")
    add_binary_vars(problem, ("x", "y"))
    add_linear_constraint(problem, {"x": 1, "y": 1}, "==", 3)

    result = solve_quadratic_program_bruteforce_native(problem)

    assert not result.feasible
    assert result.assignment == {}
    assert result.unsupported_reason == "no feasible binary assignment"
