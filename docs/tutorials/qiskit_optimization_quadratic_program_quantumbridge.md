# Qiskit Optimization QuadraticProgram with QuantumBridge

This tutorial shows QuantumBridge's Stage 9B native educational optimization path. It does not copy Qiskit Optimization tutorial code and does not replace Qiskit Optimization.

## Native Minimal Problem

```python
from quantumbridge.compat.qiskit_optimization import (
    add_binary_vars,
    add_linear_constraint,
    create_quadratic_program_native,
    set_minimize,
    solve_quadratic_program_bruteforce_native,
)

problem = create_quadratic_program_native("demo")
add_binary_vars(problem, ("x0", "x1", "x2"))
set_minimize(
    problem,
    linear={"x0": -1.0, "x1": -0.7, "x2": -0.25},
    quadratic={("x0", "x1"): 0.35, ("x1", "x2"): 0.15},
)
add_linear_constraint(problem, {"x0": 1, "x1": 1, "x2": 1}, "==", 2, name="budget")

result = solve_quadratic_program_bruteforce_native(problem)
print(result.assignment)
print(result.objective_value)
```

Expected native result:

```text
{"x0": 1, "x1": 1, "x2": 0}
-1.35
```

## QUBO and Ising Metadata

```python
from quantumbridge.compat.qiskit_optimization import (
    quadratic_program_to_ising_metadata,
    quadratic_program_to_qubo_metadata,
)

qubo = quadratic_program_to_qubo_metadata(problem, penalty=5.0)
ising = quadratic_program_to_ising_metadata(problem, penalty=5.0)
```

The metadata is intended for compatibility, inspection, and later bridge work. It is not a production optimizer output contract.

## Optional Upstream Exact Path

If `qiskit-optimization` and `qiskit-algorithms` are installed, QuantumBridge can convert the native minimal problem to an upstream `QuadraticProgram` and call `MinimumEigenOptimizer` with `NumPyMinimumEigensolver`.

If those optional packages are missing, the adapter reports that clearly and does not pretend the upstream path is available.

## Run the Example

```bash
python3 examples/qiskit_optimization_quadratic_program_quantumbridge.py
```

## Boundaries

This Stage 9B tutorial does not provide:

- complete Qiskit Optimization replacement
- production portfolio or operations research workflows
- cloud access
- token access
- hardware execution
- IBM or Qiskit endorsement
