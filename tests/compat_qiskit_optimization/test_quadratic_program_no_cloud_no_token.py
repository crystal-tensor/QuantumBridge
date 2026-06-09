# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Optimization was copied.

from quantumbridge.compat.qiskit_optimization import (
    add_binary_vars,
    create_quadratic_program_native,
    set_minimize,
    solve_quadratic_program_bruteforce_native,
)


def test_native_solver_records_no_cloud_token_or_hardware_access():
    problem = create_quadratic_program_native("offline")
    add_binary_vars(problem, ("x", "y"))
    set_minimize(problem, linear={"x": -1.0})

    result = solve_quadratic_program_bruteforce_native(problem)

    assert result.provenance["cloud_access"] is False
    assert result.provenance["token_access"] is False
    assert result.provenance["hardware_access"] is False
    assert "not a full Qiskit Optimization replacement" in " ".join(result.warnings)
    assert "production" in " ".join(result.warnings)
