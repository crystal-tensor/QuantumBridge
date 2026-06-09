# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Optimization was copied.

from quantumbridge.compat.qiskit_optimization import (
    add_binary_vars,
    create_quadratic_program_native,
    set_minimize,
    solve_quadratic_program_bruteforce_native,
    wrap_native_optimization_result,
)
from quantumbridge.schema.optimization_results import BruteForceOptimizationResult


def test_result_to_dict_json_from_dict_validate():
    problem = create_quadratic_program_native("schema")
    add_binary_vars(problem, ("x", "y"))
    set_minimize(problem, linear={"x": -1.0, "y": 1.0})
    native = solve_quadratic_program_bruteforce_native(problem)

    wrapped = wrap_native_optimization_result(native)
    payload = wrapped.to_dict()
    restored = BruteForceOptimizationResult.from_dict(payload)

    assert wrapped.validate()
    assert restored.validate()
    assert restored.assignment == {"x": 1, "y": 0}
    assert '"mode": "native_minimal"' in wrapped.to_json()
    assert not wrapped.production_ready
    assert wrapped.native_implementation
