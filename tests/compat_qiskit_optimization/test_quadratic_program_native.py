# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Optimization was copied.

from quantumbridge.compat.qiskit_optimization import (
    add_binary_var,
    add_binary_vars,
    create_quadratic_program_native,
    native_quadratic_program_from_dict,
    native_quadratic_program_to_dict,
)


def test_binary_variables_can_be_created():
    problem = create_quadratic_program_native("vars")
    add_binary_var(problem, "x")
    add_binary_vars(problem, ("y", "z"))

    assert problem.variable_names == ("x", "y", "z")
    assert problem.validate()


def test_native_quadratic_program_round_trips():
    problem = create_quadratic_program_native("roundtrip")
    add_binary_vars(problem, ("x", "y"))
    payload = native_quadratic_program_to_dict(problem)
    restored = native_quadratic_program_from_dict(payload)

    assert restored.name == "roundtrip"
    assert restored.variable_names == ("x", "y")
