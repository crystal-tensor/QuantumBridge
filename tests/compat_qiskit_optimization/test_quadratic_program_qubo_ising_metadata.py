# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Optimization was copied.

from quantumbridge.compat.qiskit_optimization import (
    add_binary_vars,
    add_linear_constraint,
    create_quadratic_program_native,
    quadratic_program_to_ising_metadata,
    quadratic_program_to_qubo_metadata,
    set_minimize,
)


def test_qubo_metadata_generated():
    problem = create_quadratic_program_native("qubo")
    add_binary_vars(problem, ("x", "y"))
    set_minimize(problem, linear={"x": 1.0}, quadratic={("x", "y"): -2.0}, constant=0.5)
    add_linear_constraint(problem, {"x": 1, "y": 1}, "==", 1)

    metadata = quadratic_program_to_qubo_metadata(problem, penalty=4.0)

    assert metadata["format"] == "qubo-metadata-v0.1"
    assert metadata["variables"] == ["x", "y"]
    assert metadata["penalty_applied"]
    assert {"left": "x", "right": "y", "coefficient": 6.0} in metadata["quadratic"]


def test_ising_metadata_generated():
    problem = create_quadratic_program_native("ising")
    add_binary_vars(problem, ("x", "y"))
    set_minimize(problem, linear={"x": 1.0, "y": -1.0}, quadratic={("x", "y"): 0.5})

    metadata = quadratic_program_to_ising_metadata(problem)

    assert metadata["format"] == "ising-metadata-v0.1"
    assert "offset" in metadata
    assert set(metadata["h"]) == {"x", "y"}
    assert metadata["j"] == [{"left": "x", "right": "y", "coefficient": 0.125}]
