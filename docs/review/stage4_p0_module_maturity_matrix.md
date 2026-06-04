# Stage 4 P0 Module Maturity Matrix

Status: Acceptance hardening review  
Date: 2026-06-04  

| Module | Status | Evidence | Tests | Risk | P1 Action |
|---|---|---|---|---|---|
| `quantumbridge.core` | partially implemented | Circuit, Operation, Parameter, Measurement support P0 gates and measurements | Basic gates, QASM, adapter tests | Medium | Add registers, composition edge cases, richer validation |
| `quantumbridge.ir` | partially implemented | QB IR represents P0 operations/measurements | Qiskit roundtrip, QASM tests | Medium | Add observables/execution metadata and schema validation |
| `quantumbridge.devices` | partially implemented | StatevectorDevice and ShotSampler execute P0 subset | Statevector, sampler, primitives tests | Medium | Add backend validation reports and non-unitary behavior boundaries |
| `quantumbridge.results` | partially implemented | Result stores state/probabilities/counts/expectations/metadata | Serialization and adapter tests | Low | Add JSON method and result schema version |
| `quantumbridge.diff` | partially implemented | Parameter-shift helper works for scalar objectives | Parameter-shift tests | Medium | Add circuit-aware eligibility checks |
| `quantumbridge.algorithms` | partially implemented | VQE and QAOA small-case loops | VQE/QAOA tests | Medium | Improve optimizers and convergence controls |
| `quantumbridge.compat.qiskit_adapter` | optional dependency bridge | Real Qiskit object conversion when Qiskit installed; skip if unavailable | Qiskit realistic tests | Medium | Expand operation coverage and version matrix |
| `quantumbridge.compat.pennylane_adapter` | optional dependency bridge | Real PennyLane observable/tape/executable subset when PennyLane installed; skip if unavailable | PennyLane realistic tests when installed; skips in bare pytest env | Medium | Expand measurements and operation coverage |
| `quantumbridge.compat.qasm_adapter` | partially implemented | Native OpenQASM-style subset parser | Strict QASM roundtrip tests | Medium | Replace regex subset with grammar-backed parser |
| `quantumbridge.operators` | partially implemented | Pauli, PauliString, SparsePauliOperator basics | Operator/Hamiltonian extended tests | Medium | Add simplification, multiplication over strings, sparse matrix conversion |
| `quantumbridge.information` | partially implemented | Statevector, DensityMatrix, partial trace, fidelity, entropy | Extended information tests | Medium | Add validation for all shapes and mixed-state operations |
| `quantumbridge.primitives` | partially implemented | Sampler and Estimator wrappers over native devices | Extended primitive tests | Low | Add batched primitive API |
| `quantumbridge.qml` | partially implemented | QNode-like wrapper, Tape, templates | QML/gradient tests | Medium | Add richer recording and measurement model |
| `quantumbridge.interfaces` | partially implemented | NumPy/Torch/JAX conversion helpers; JAX optional | Interface tests; JAX unavailable path tested | Low | Add framework-native gradient integration |
| `quantumbridge.providers` | lightweight foundation | Backend/Job/Provider local wrappers | Provider adapter test | Medium | Add backend properties, async job states, adapter backends |
| `quantumbridge.compiler` | lightweight foundation | PassManager, CouplingMap, Target, helper functions | Import/header only in current P0 | Medium | Add actual passes and dedicated tests |
| `quantumbridge.visualization.text_drawer` | lightweight foundation | Simple text drawer | Not directly tested in P0 hardening | Low | Add layout-aware text drawer tests |
| `quantumbridge.visualization.mpl_drawer` | placeholder | Raises `NotImplementedError` and is explicitly deferred | Not tested | Low | Implement or keep excluded from P0 public API |
| `quantumbridge.legal` | partially implemented | Attribution file validator | Attribution automation tests | Low | Generate notices from ledger automatically |

## Summary

No module is production ready. P0 modules are suitable as an internal baseline and demos with clear subset disclaimers. Stage 5 begins controlled P1 expansion for QASM, gates/operators, compiler, and noise while preserving the P0 subset disclaimer. Compiler and visualization remain limited; matplotlib drawing is an explicit placeholder.

See also: `docs/review/stage5_p1_module_maturity_matrix.md`.
