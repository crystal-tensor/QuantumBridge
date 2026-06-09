# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Optimization was copied.

from quantumbridge.compat.qiskit_optimization import (
    add_binary_vars,
    add_linear_constraint,
    create_quadratic_program_native,
    is_feasible,
)


def test_equality_constraint_works():
    problem = create_quadratic_program_native("eq")
    add_binary_vars(problem, ("x", "y", "z"))
    add_linear_constraint(problem, {"x": 1, "y": 1, "z": 1}, "==", 2, name="budget")

    assert is_feasible(problem, {"x": 1, "y": 1, "z": 0})
    assert not is_feasible(problem, {"x": 1, "y": 1, "z": 1})


def test_inequality_constraints_work():
    problem = create_quadratic_program_native("ineq")
    add_binary_vars(problem, ("x", "y"))
    add_linear_constraint(problem, {"x": 1, "y": 2}, "<=", 2)
    add_linear_constraint(problem, {"x": 1, "y": 1}, ">=", 1)

    assert is_feasible(problem, {"x": 1, "y": 0})
    assert not is_feasible(problem, {"x": 0, "y": 0})
    assert not is_feasible(problem, {"x": 1, "y": 1})
