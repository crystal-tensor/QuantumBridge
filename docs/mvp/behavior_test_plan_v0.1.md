# QuantumBridge MVP Behavior Test Plan v0.1

Status: Draft  
Date: 2026-06-04  
Source basis: `functional_spec_v0.1.md`, MVP design documents, and independent quantum computing mathematics.  

This document is design-only. Tests described here must be independently implemented later and must not copy Qiskit or PennyLane tests, fixtures, comments, error messages, or documentation examples.

## 1. Test provenance rule

Every behavior test implemented in stage three must state:

- QuantumBridge design document section used.
- Mathematical or public-standard basis.
- Input circuit or object.
- Expected output.
- Numeric tolerance or statistical tolerance.

## 2. Numeric conventions

Default exact tolerances:

- State amplitudes: absolute tolerance `1e-10`.
- Probabilities: absolute tolerance `1e-12`.
- Expectation values: absolute tolerance `1e-10`.
- Gradients: absolute tolerance `1e-7`.

Sampling tolerances:

- Counts must sum exactly to shots.
- Probabilistic frequencies use loose statistical bands chosen before implementation.
- Fixed seed is required for deterministic behavior tests.

Qubit-order convention:

- User-facing bitstrings list wire 0 first, then wire 1, through wire `n-1`.

## 3. Required behavior tests

### T01: H on zero state

Input:

- One-qubit circuit.
- Initial state `|0>`.
- Apply H on wire 0.
- Request final state and probabilities.

Expected output:

- State amplitudes equivalent to `(1/sqrt(2))|0> + (1/sqrt(2))|1>`.
- Probabilities: `0` has `0.5`, `1` has `0.5`.

Mathematical basis:

- Standard Hadamard action on computational basis.

### T02: X on zero state

Input:

- One-qubit circuit.
- Initial state `|0>`.
- Apply X on wire 0.

Expected output:

- Final state is `|1>`.
- Probability for bitstring `1` is `1`.

Mathematical basis:

- Pauli X flips computational-basis states.

### T03: CX Bell state

Input:

- Two-qubit circuit.
- Apply H on wire 0.
- Apply CX with control wire 0 and target wire 1.
- Request probabilities and sampled counts with `shots = 1000`, fixed seed.

Expected output:

- Exact probabilities: `00` is `0.5`, `11` is `0.5`, all others `0`.
- Sample counts contain only or overwhelmingly `00` and `11` depending on sampler exactness and no-noise assumption.
- Counts sum to `1000`.

Mathematical basis:

- Entangling circuit creates `(1/sqrt(2))(|00> + |11>)` under the documented wire-order convention.

### T04: RY(theta) expectation

Input:

- One-qubit circuit.
- Apply `RY(theta)` on wire 0.
- Observable: PauliZ on wire 0.
- Use test values such as `theta = 0`, `pi/3`, `pi/2`, and `pi`.

Expected output:

- Expectation value equals `cos(theta)` within tolerance.

Mathematical basis:

- Rotation about Y axis followed by Z expectation on initial `|0>`.

### T05: Parameter-shift gradient

Input:

- Same objective as T04.
- Differentiate with respect to `theta`.
- Test values such as `theta = 0`, `pi/4`, `pi/2`.

Expected output:

- Gradient equals `-sin(theta)` within tolerance.
- At `theta = 0`, gradient near `0`.
- At `theta = pi/2`, gradient near `-1`.

Mathematical basis:

- Parameter-shift rule for supported Pauli-generator rotation and analytic derivative of `cos(theta)`.

### T06: Shot sampling deterministic state

Input:

- One-qubit circuit.
- Apply X on wire 0.
- Measure or sample with `shots = 100`.

Expected output:

- Counts: bitstring `1` has count `100`.
- No other bitstring has positive count.

Mathematical basis:

- Deterministic computational-basis state has probability one on its basis label.

### T07: Shot sampling balanced state

Input:

- One-qubit circuit.
- Apply H on wire 0.
- Sample with `shots = 1000`, fixed seed.

Expected output:

- Counts sum to `1000`.
- Bitstrings `0` and `1` both appear within predeclared statistical bands, such as 40 percent to 60 percent.

Mathematical basis:

- Born rule for equal superposition.

### T08: Hamiltonian expectation sum

Input:

- One-qubit circuit with `RY(theta)`.
- Hamiltonian `0.5 * Z + 0.25 * Identity`.

Expected output:

- Expectation equals `0.5 * cos(theta) + 0.25`.

Mathematical basis:

- Linearity of expectation values.

### T09: Simple VQE

Input:

- Hamiltonian: PauliZ on one qubit.
- Ansatz: one RY angle on one qubit.
- Initial parameter not already at optimum.
- Exact statevector device.
- Gradient descent optimizer with fixed settings.

Expected output:

- Final energy is lower than initial energy.
- Final energy is near `-1` under loose MVP tolerance.
- Result includes final parameters, final energy, trace, and stop reason.

Mathematical basis:

- Minimum eigenvalue of PauliZ is `-1`.

### T10: Simple QAOA two-node MaxCut

Input:

- Graph with one edge connecting two nodes.
- Depth `p = 1`.
- Fixed initial parameters and optimizer settings.
- Exact statevector device.

Expected output:

- Expected cut value improves from the initial value or reaches a value near the known maximum under loose tolerance.
- Result includes graph summary, depth, final parameters, final value, and trace.

Mathematical basis:

- Two-node MaxCut has maximum cut value `1`.

### T11: QAOA triangle smoke test

Input:

- Triangle graph with three edges.
- Depth `p = 1`.
- Fixed initial parameters and optimizer settings.

Expected output:

- Final expected cut value exceeds a random baseline for the graph under a documented loose tolerance, or shows objective improvement from initialization.

Mathematical basis:

- MaxCut cost equals sum of edge disagreement indicators.

### T12: OpenQASM export simple measured circuit

Input:

- Two-qubit Bell circuit with two classical bits and measurements.
- Export using MVP numeric mode.

Expected output:

- Export text declares quantum and classical storage.
- Export text contains supported H and CX gate records.
- Export text contains measurement mappings.
- Text does not omit operations silently.

Mathematical or public-standard basis:

- Public OpenQASM-style interchange concepts for storage, gates, and measurement.

### T13: OpenQASM export rejects unsupported custom unitary

Input:

- Circuit containing a custom unitary without a supported export representation.
- Request OpenQASM export.

Expected output:

- Export fails with a QuantumBridge-authored serialization diagnostic.
- No partial export is returned as successful.

Mathematical or design basis:

- Serialization safety requirement from `ir_design_v0.1.md`.

### T14: Result serialization

Input:

- Run a Bell circuit on StatevectorDevice and ShotSampler.
- Convert result to dictionary and JSON-compatible text.

Expected output:

- Serialized result includes metadata, probabilities, optional counts, and statevector representation.
- Complex amplitudes are represented in an explicit JSON-compatible structure.
- Repeated serialization of the same result is deterministic.

Design basis:

- Result API contract and simulator result behavior.

### T15: Parameter binding validation

Input:

- Circuit with `RY(theta)` where `theta` is unbound.
- Attempt numeric statevector execution.

Expected output:

- Execution is rejected with QuantumBridge-authored parameter-binding diagnostic.

Design basis:

- Numeric execution requires bound parameters.

### T16: Unsupported gradient validation

Input:

- Objective containing a custom unitary parameter or unsupported parameterized operation.
- Request parameter-shift gradient.

Expected output:

- Gradient request is rejected with QuantumBridge-authored gradient diagnostic.
- Metadata identifies unsupported gradient scope when practical.

Design basis:

- `gradient_design_v0.1.md` supported and unsupported gradient rules.

## 4. Clean-room test implementation rules

- Do not copy third-party tests or fixtures.
- Do not assert third-party error strings.
- Do not reuse third-party example circuits unless they are universal textbook examples and are independently written here.
- Keep tests small and analytically inspectable.
- Prefer exact formulas over external SDK comparison.
- Tests must never require Qiskit or PennyLane as an oracle.

## 5. Coverage map

| Requirement | Tests |
| --- | --- |
| H on `|0>` | T01 |
| X on `|0>` | T02 |
| CX Bell state | T03 |
| RY expectation | T04 |
| Parameter-shift gradient | T05, T16 |
| Shot sampling | T06, T07 |
| Simple VQE | T09 |
| Simple QAOA | T10, T11 |
| OpenQASM export | T12, T13 |
| Result serialization | T14 |
| Parameter binding | T15 |

