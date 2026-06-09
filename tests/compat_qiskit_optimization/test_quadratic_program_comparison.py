# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Optimization was copied.

from dataclasses import replace

from quantumbridge.compat.qiskit_optimization import (
    add_binary_vars,
    compare_optimization_results,
    create_quadratic_program_native,
    set_minimize,
    solve_quadratic_program_bruteforce_native,
)


def test_native_and_upstream_comparison_when_upstream_missing():
    problem = create_quadratic_program_native("comparison")
    add_binary_vars(problem, ("x", "y"))
    set_minimize(problem, linear={"x": -1.0, "y": 0.5})
    native = solve_quadratic_program_bruteforce_native(problem)

    comparison = compare_optimization_results(native, None)

    assert comparison.metadata["upstream_available"] is False
    assert comparison.metadata["native_upstream_agree"] is False
    assert comparison.assignment == {"x": 1, "y": 0}


def test_native_and_upstream_comparison_can_agree():
    problem = create_quadratic_program_native("comparison_agree")
    add_binary_vars(problem, ("x", "y"))
    set_minimize(problem, linear={"x": -1.0, "y": 0.5})
    native = solve_quadratic_program_bruteforce_native(problem)
    upstream_like = replace(native, path="qiskit-optimization-upstream")

    comparison = compare_optimization_results(native, upstream_like)

    assert comparison.metadata["upstream_available"] is True
    assert comparison.metadata["native_upstream_agree"] is True
