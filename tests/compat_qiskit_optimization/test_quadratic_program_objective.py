# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Optimization was copied.

from quantumbridge.compat.qiskit_optimization import (
    add_binary_vars,
    create_quadratic_program_native,
    evaluate_objective,
    set_maximize,
    set_minimize,
)


def test_minimize_objective_evaluates_correctly():
    problem = create_quadratic_program_native("objective")
    add_binary_vars(problem, ("x", "y"))
    set_minimize(problem, linear={"x": 1.5, "y": -1.0}, quadratic={("x", "y"): 0.25}, constant=2.0)

    assert evaluate_objective(problem, {"x": 1, "y": 1}) == 2.75
    assert evaluate_objective(problem, (0, 1)) == 1.0


def test_maximize_objective_keeps_declared_sense():
    problem = create_quadratic_program_native("maximize")
    add_binary_vars(problem, ("x", "y"))
    set_maximize(problem, linear={"x": 2.0, "y": 1.0}, quadratic={("x", "y"): -0.5})

    assert problem.objective.sense == "maximize"
    assert evaluate_objective(problem, {"x": 1, "y": 1}) == 2.5
