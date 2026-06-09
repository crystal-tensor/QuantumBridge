# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Optimization was copied.

import pytest

from quantumbridge.compat.qiskit_optimization import (
    add_binary_vars,
    create_quadratic_program_native,
    dependency_available,
    native_to_upstream_quadratic_program,
    set_minimize,
    solve_quadratic_program_exact_upstream,
    validate_optimization_dependencies,
)


def _problem():
    problem = create_quadratic_program_native("upstream")
    add_binary_vars(problem, ("x", "y"))
    set_minimize(problem, linear={"x": -1.0, "y": 2.0})
    return problem


def test_upstream_dependency_report_is_clear():
    report = validate_optimization_dependencies()

    assert "available" in report
    assert "qiskit_optimization" in report["modules"]
    assert "qiskit_algorithms" in report["modules"]


def test_native_to_upstream_runs_or_raises_clear_import_error():
    problem = _problem()
    if dependency_available():
        upstream = native_to_upstream_quadratic_program(problem)
        assert upstream.name == "upstream"
    else:
        with pytest.raises(ImportError, match="qiskit-optimization"):
            native_to_upstream_quadratic_program(problem)


def test_upstream_exact_runs_if_available_or_skips_clearly():
    problem = _problem()
    report = validate_optimization_dependencies()
    if not report["available"]:
        with pytest.raises(ImportError, match="optional upstream packages"):
            solve_quadratic_program_exact_upstream(problem)
        return

    result = solve_quadratic_program_exact_upstream(problem)
    assert result.feasible
    assert result.assignment == {"x": 1, "y": 0}
