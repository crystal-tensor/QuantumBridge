#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Optimization was copied.
"""Run a QuantumBridge-native educational QuadraticProgram example."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from quantumbridge.compat.qiskit_optimization import (
    add_binary_vars,
    add_linear_constraint,
    compare_optimization_results,
    create_quadratic_program_native,
    quadratic_program_to_ising_metadata,
    quadratic_program_to_qubo_metadata,
    set_minimize,
    solve_quadratic_program_bruteforce_native,
    solve_quadratic_program_exact_upstream,
    validate_optimization_dependencies,
    wrap_native_optimization_result,
)


def build_problem():
    """Build a small binary quadratic program with a budget constraint."""

    problem = create_quadratic_program_native("stage9b_demo")
    add_binary_vars(problem, ("x0", "x1", "x2"))
    set_minimize(
        problem,
        linear={"x0": -1.0, "x1": -0.7, "x2": -0.25},
        quadratic={("x0", "x1"): 0.35, ("x1", "x2"): 0.15},
        constant=0.0,
    )
    add_linear_constraint(problem, {"x0": 1, "x1": 1, "x2": 1}, "==", 2, name="budget")
    return problem


def main() -> None:
    problem = build_problem()
    native = solve_quadratic_program_bruteforce_native(problem)
    print("native result:")
    print(wrap_native_optimization_result(native).to_json())
    print("qubo metadata:")
    print(quadratic_program_to_qubo_metadata(problem, penalty=5.0))
    print("ising metadata:")
    print(quadratic_program_to_ising_metadata(problem, penalty=5.0))

    dependency_report = validate_optimization_dependencies()
    print("upstream dependency report:")
    print(dependency_report)
    upstream = None
    if dependency_report["available"]:
        upstream = solve_quadratic_program_exact_upstream(problem)
        print("upstream exact result:")
        print(upstream.to_json())
    else:
        print("upstream exact result: unavailable; optional qiskit-optimization/qiskit-algorithms not installed")

    print("native/upstream comparison:")
    print(compare_optimization_results(native, upstream).to_json())
    for warning in native.warnings:
        print(f"warning: {warning}")


if __name__ == "__main__":
    main()
