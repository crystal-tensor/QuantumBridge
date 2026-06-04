# QuantumBridge Simulator Design v0.1

Status: Draft  
Date: 2026-06-04  
Source basis: `functional_spec_v0.1.md`, public linear algebra for quantum states and measurements, and independently authored QuantumBridge MVP scope.  

This document is design-only and contains no SDK implementation code.

## 1. Statevector simulator mathematical semantics

The MVP statevector simulator represents an `n`-qubit pure state as a complex vector with `2^n` amplitudes:

```text
|psi> = sum_x alpha_x |x>
```

where:

- `x` ranges over all `n`-bit computational-basis strings.
- `alpha_x` is a complex amplitude.
- The normalized state satisfies `sum_x |alpha_x|^2 = 1` within numerical tolerance.

Initial state:

- Unless otherwise specified, the initial state is `|0...0>`.
- The amplitude of `|0...0>` is `1`.
- All other amplitudes are `0`.

Operation evolution:

- Supported gates are unitary matrices.
- Gates are applied in circuit order.
- A one-qubit gate applies the corresponding 2 by 2 matrix to the selected wire.
- A two-qubit gate applies the corresponding 4 by 4 matrix to the selected ordered wire pair.
- Custom unitary applies an explicitly supplied matrix to its target wires after validation.

## 2. Supported minimum gate set

MVP statevector execution supports:

| Gate | Arity | Parameterized | Notes |
| --- | --- | --- | --- |
| X | 1 | No | Pauli X |
| Y | 1 | No | Pauli Y |
| Z | 1 | No | Pauli Z |
| H | 1 | No | Hadamard |
| S | 1 | No | Quarter-turn phase gate |
| T | 1 | No | Eighth-turn phase gate |
| RX | 1 | Yes | Rotation about X axis |
| RY | 1 | Yes | Rotation about Y axis |
| RZ | 1 | Yes | Rotation about Z axis |
| Phase | 1 | Yes | Relative phase on `|1>` basis component |
| CX | 2 | No | Controlled X |
| CZ | 2 | No | Controlled Z |
| SWAP | 2 | No | Exchanges two wires |
| Custom unitary | k | Optional | Matrix must be unitary within tolerance |

The exact matrix definitions must be taken from standard quantum computing linear algebra during implementation and documented in module design records.

## 3. Qubit ordering convention

MVP adopts one explicit QuantumBridge convention:

- Wire indices increase from left to right in displayed bitstrings.
- Basis label `|q0 q1 ... q(n-1)>` corresponds to the user-facing wire order.
- Counts bitstrings use the same user-facing order.
- Probability keys use the same bitstring order.

Indexing into the internal amplitude vector must be documented during implementation. Behavior tests must define expected results using the user-facing bitstring order above, so users do not need to infer internal memory layout.

Example convention:

- For two wires, user-facing bitstrings are `00`, `01`, `10`, `11`.
- A CX from wire 0 to wire 1 maps `|10>` to `|11>`.
- A Bell circuit with H on wire 0 and CX from 0 to 1 produces probability on `00` and `11`.

## 4. Measurement convention

Computational-basis measurement:

- Measurement probabilities are `P(x) = |alpha_x|^2`.
- A measurement over all wires returns a distribution over all `n`-bit strings.
- A measurement over selected wires returns the marginal distribution over those wires in selected order.

Circuit measurements:

- Explicit `measure(q, bit)` maps quantum wire `q` to classical bit `bit`.
- Counts from a circuit with explicit classical bits use classical bit order.
- Counts from a sampler without classical storage use measured quantum-wire order.

Collapse:

- MVP exact statevector execution computes final pre-measurement state and then derives probabilities or samples.
- MVP does not model mid-circuit collapse or conditional behavior.
- Mid-circuit measurement is outside MVP.

## 5. Shot-based sampler behavior

The sampler turns a probability distribution into finite-shot counts.

Inputs:

- Circuit or probability distribution.
- Positive integer `shots`.
- Optional random seed.
- Optional selected wires or measurement map.

Outputs:

- Counts mapping bitstrings to non-negative integer counts.
- Empirical probabilities derived from counts.
- Metadata containing shots, seed, source distribution type, and ordering convention.

Rules:

- Counts must sum exactly to `shots`.
- With a fixed seed, output must be deterministic for the same implementation and runtime assumptions.
- Deterministic distributions must produce deterministic counts.
- Statistical tests must use loose tolerances appropriate for finite samples rather than exact equality on random distributions.

## 6. Expectation value calculation semantics

For a normalized state `|psi>` and Hermitian observable `O`, exact expectation is:

```text
E = <psi|O|psi>
```

For a Hamiltonian:

```text
H = sum_i c_i O_i
E(H) = sum_i c_i E(O_i)
```

MVP observables:

- Identity.
- PauliX.
- PauliY.
- PauliZ.
- Tensor products of Pauli observables.
- Hamiltonian as weighted sum.

Shot-estimated expectations:

- Deferred for MVP unless a simple Pauli-Z sample estimate is explicitly added later.
- MVP acceptance relies on exact statevector expectation.

## 7. Numeric error tolerance

Recommended MVP tolerances:

- Statevector amplitude comparisons: absolute tolerance `1e-10` for exact small circuits.
- Probability sums: absolute tolerance `1e-12` for exact probabilities.
- Expectation values: absolute tolerance `1e-10` for exact simulator tests.
- Gradient values: absolute tolerance `1e-7` for parameter-shift tests on small circuits.
- Unitarity validation: implementation may use tolerance around `1e-10`, documented in code design record.
- Sampling distribution tests: use probabilistic bands, such as Bell counts within 40 percent to 60 percent for each expected state at 1000 shots, unless a tighter statistically justified criterion is chosen.

These values are design defaults and may be adjusted if implementation records justify the change.

## 8. Validation behavior

The simulator must reject:

- Unsupported operation names.
- Missing parameter bindings.
- Non-numeric execution parameters.
- Out-of-range wires.
- Duplicate wires in an operation where not meaningful.
- Custom matrices with incompatible shape.
- Custom matrices that are not unitary within tolerance.
- Measurement requests unsupported in MVP.

Diagnostics must be independently authored in QuantumBridge wording.

## 9. Result behavior

The simulator result may contain:

- Final statevector.
- Exact probabilities.
- Counts, if sampled.
- Expectation values, if requested.
- Metadata: device name, supported gate set version, precision, shot count, seed, ordering convention, and warnings.

Result serialization must preserve enough information to reconstruct real and imaginary parts of amplitudes without relying on language-specific complex-number serialization.

## 10. Clean-room rationale

The simulator design is based on standard quantum mechanics: statevectors, unitary evolution, Born-rule probabilities, and Hermitian expectation values. It does not use or require source-level knowledge of any existing SDK.

