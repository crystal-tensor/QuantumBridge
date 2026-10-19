# Stage 11F Native Clifford And Stabilizer Execution

Date: 2026-10-19

## Scope And Architecture

The former Clifford class wrapped a dense Operator. Its direct constructor
accepted non-Clifford unitaries and offered no tableau or stabilizer-state
execution. This slice replaces it with a signed binary symplectic tableau,
using the preceding phase-aware native Pauli algebra. It is shared core
infrastructure for the existing four industry categories and 19 subdomains;
it does not add Studio functionality.

The native runtime uses NumPy and QuantumBridge, not Qiskit/PennyLane. No
upstream source or tests were copied. Installed Qiskit is a test oracle only.

## Implemented Behavior

- Clifford construction from binary tableaus, native circuits/instructions,
  Pauli operators, labels, signed-generator dictionaries and explicit dense
  unitary matrices, with symplectic/Clifford validation.
- Tableau views, signed labels, dimensions, copy and dictionary roundtrips.
- Composition, subsystem embedding, adjoint, transpose, conjugation, tensor
  products and positive-integer powers.
- Polynomial-size native Clifford circuit synthesis by reducing conjugate
  generator pairs to the identity and reversing the elementary gates.
- Pauli and PauliList Clifford evolution in both Heisenberg and Schrodinger
  frames, preserving complex phases and Qiskit-style subsystem order.
- Pure StabilizerState construction from independent generators, consistency
  and redundancy checks, optional completion of underconstrained generators.
- Clifford state evolution, conjugation, tensor products, Pauli/sparse-Pauli
  expectations, computational-basis probabilities, projective measurements,
  reset and seeded shot sampling.
- Uniform random Clifford generation: choose symplectic generator pairs
  uniformly from each remaining nondegenerate complement, then choose
  independent generator signs. This is not a shallow-random-circuit proxy.
- Explicit dense statevector, preparation-operator and density-matrix
  conversions, outside the polynomial-memory execution path.

## Contracts And Migration

- A tableau has shape (2n, 2n+1): X-generator images followed by Z-generator
  images, X columns, Z columns and final sign bit. It describes U P U-dagger.
- Symplectic columns, stabilizer qargs and Pauli qargs use little-endian
  subsystem positions. Native Circuit wire 0 remains the leftmost wire;
  circuit conversion reverses wire positions explicitly.
- Clifford compose now follows the Qiskit convention: a.compose(b) is b*a,
  a.dot(b) is a*b, and front=True selects the latter. The old dense wrapper
  inherited the native Operator convention; callers should use keywords.
- The Clifford array constructor consumes a binary tableau. Use from_matrix
  or from_operator for real-valued unitary matrices. The old dense wrapper's
  acceptance of arbitrary non-Clifford matrices was incorrect and is removed.
- Clifford global phase is not represented. Synthesized matrices are
  equivalent up to global phase, not necessarily elementwise identical.
- StabilizerState.to_operator returns its preparation Clifford unitary, as
  observed in Qiskit. Use to_density_matrix for the state projector and
  to_statevector for its ket. sample_memory returns a NumPy string array.
- Native seed reproducibility is tested. Identical random Clifford tableaus
  or sampled bitstreams for the same seed across different SDKs are not
  promised. Underconstrained completion may choose a different valid state.
- Zero-qubit tableaus and dense identity/state conversions work. Native
  Circuit/Instruction still require positive width, so zero-qubit circuit
  synthesis is not supported. State dimensions reflect the physical qubit
  count rather than copying Qiskit 2.6.0's observed empty dims metadata.

## Verification

The native and optional parity tests verify tableaus, generator signs,
composition/subsystem order, tensor products, inverses, powers, synthesis and
matrix equivalence for random one- through four-qubit Cliffords. State tests
compare probabilities, Pauli/sparse-Pauli expectations, tensor/evolution and
dense state fidelity against installed Qiskit 2.6.0. Measurement tests require
valid collapse to the sampled basis state, source-state preservation, reset
and seed reproducibility. All 24 one-qubit Clifford elements are reached.

A 64-qubit GHZ test blocks both Clifford.to_matrix and Operator.from_circuit
while exercising construction, native circuit synthesis roundtrip,
probabilities, X parity, sampling and reset. Its tableau occupies 16,512 bytes.
A separate 16-qubit random synthesis/inverse test also blocks dense conversion.
The runnable example is:

```bash
python -m examples.native_clifford_stabilizer_quantumbridge
```

Clean tracked-tree regression results:

| Check | Result |
| --- | --- |
| Core-only environment, no Qiskit/PennyLane | 582 passed, 73 optional skips |
| Installed ecosystem full suite | 719 passed, 4 skips |
| Explicit pytest-cov measurement | 85.07% overall statement coverage |
| Clifford / StabilizerState statement coverage | 94.99% / 99.56% |
| Focused Qiskit 2.6.0 / PennyLane 0.42.3 environment | 136 passed |
| Local matrix script | Exit 0; all available profiles passed |
| Additional Qiskit-generated Clifford inputs | 125 synthesis, inverse and stabilizer reconstructions passed |
| Native 64-qubit example without upstream SDKs | Exit 0; X parity 1, two GHZ outcomes, exact synthesis roundtrip |

Validation used a clean archive with the staged change, excluding unrelated
Router/Studio worktree changes. The installed suite's four skips concern
pyquafu's NumPy environment requirement, absent Qiskit Dynamics and absent
Qiskit Optimization. The matrix skips unavailable optional packages. Its
existing coverage-plugin detection skipped coverage, so coverage was measured
explicitly in a separate successful full-suite invocation. Statement coverage
is not a percentage of Qiskit/PennyLane API parity.

## Remaining Boundaries

This is not complete quantum_info, Aer or PennyLane parity. General noisy
stabilizer simulation, Aer Backend/Job/save-instruction integration, classical
control-flow execution and non-Clifford simulation are not provided here.
Clifford specialized linear-function/permutation constructors, layout
application, every synthesis strategy and exact upstream error types remain
outside this slice. Mid-circuit measurements are not accepted as a Clifford
unitary; use the state measurement API explicitly.

Tableau storage is quadratic. Gate evolution, measurement, expectations and
synthesis are polynomial; materializing all nonzero output probabilities can
still take exponential time/output space for broad distributions. Explicit
statevector/operator/density conversions are also exponential. This is not
a claim of efficient simulation of arbitrary quantum circuits.

No token is read, no hardware job is submitted, and no new Quafu hardware
result is claimed. Synthesized native circuits can be passed to an existing
backend path, subject to its gate, size and permission limits.

## References

- [Qiskit Clifford API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/2.2/qiskit.quantum_info.Clifford)
- [Qiskit StabilizerState API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.StabilizerState)
- [Aaronson and Gottesman, Improved Simulation of Stabilizer Circuits](https://arxiv.org/abs/quant-ph/0406196)

These are mathematical/API references, not source ports.
