# QuantumBridge Algorithm Design v0.1

Status: Draft  
Date: 2026-06-04  
Source basis: `functional_spec_v0.1.md`, MVP scope, public VQE/QAOA concepts, and independently authored QuantumBridge design.  

This document is design-only and contains no SDK implementation code.

## 1. Algorithm MVP goals

MVP algorithms should demonstrate that QuantumBridge can combine:

- Circuit construction.
- Hamiltonian expectation.
- Parameter binding.
- Parameter-shift gradients.
- A minimal optimizer loop.
- Traceable result serialization.

The goal is not state-of-the-art performance. The goal is a clean, mathematically inspectable design that supports small examples and behavior tests.

## 2. Hamiltonian 表示方式

MVP Hamiltonian:

- A finite weighted sum of supported observables.
- Each term has a real coefficient.
- Each observable is Identity, PauliX, PauliY, PauliZ, or a tensor product of these over selected wires.

Semantic form:

```text
H = sum_i c_i O_i
```

where:

- `c_i` is a real scalar.
- `O_i` is a supported Hermitian observable.

Expectation:

```text
E(theta) = <psi(theta)|H|psi(theta)>
         = sum_i c_i <psi(theta)|O_i|psi(theta)>
```

Hamiltonian metadata:

- Name or label.
- Term count.
- Wire set.
- Source note, such as "user-provided" or "MaxCut construction".

## 3. Optimizer MVP 设计

Required optimizer:

- Simple gradient descent.

Optimizer contract:

- Accept current parameters.
- Accept scalar objective value.
- Accept gradient values when available.
- Return next parameters and optimizer metadata.

Design parameters:

- Learning rate.
- Maximum steps.
- Absolute objective-change tolerance.
- Gradient norm tolerance.
- Optional parameter clipping or bounds are deferred.

Optimizer trace entry:

- Step index.
- Parameters before or after update.
- Objective value.
- Gradient values when used.
- Stop reason when the run ends.

Deferred optimizers:

- Adam.
- SPSA.
- Natural gradient.
- Quantum natural gradient.
- Second-order optimizers.

## 4. VQE MVP 设计

VQE objective:

```text
minimize E(theta) = <psi(theta)|H|psi(theta)>
```

Inputs:

- Hamiltonian.
- Ansatz contract that maps numeric parameters to a Circuit.
- Initial parameter vector.
- Statevector device.
- Optimizer settings.
- Optional callback.

Execution semantics:

1. Bind current parameters into the ansatz circuit.
2. Validate circuit on StatevectorDevice.
3. Compute exact Hamiltonian expectation.
4. Compute gradient through parameter-shift when optimizer requires it.
5. Update parameters.
6. Record trace.
7. Stop after max steps or tolerance.

Result fields:

- `algorithm`: VQE.
- `final_energy`.
- `final_parameters`.
- `best_energy`.
- `best_parameters`.
- `steps_completed`.
- `trace`.
- `hamiltonian_summary`.
- `device_metadata`.
- `gradient_metadata`.
- `stop_reason`.

MVP behavior target:

- One-qubit Hamiltonian `Z` with an `RY` ansatz can approach energy near `-1`.

## 5. QAOA MVP 设计

MVP problem:

- Unweighted MaxCut on a small undirected graph.

Graph input:

- Node labels may be integers or strings, but MVP implementation may normalize them to a stable internal order.
- Edges are unordered pairs.
- Self-loops are rejected.
- Duplicate edges are ignored or rejected according to documented validation.

Cost objective:

For an edge `(i, j)`, a cut contributes `1` when endpoint bit values differ and `0` when they match.

The MaxCut expected value can be represented through a Pauli-Z cost expression:

```text
C_ij = (1 - Z_i Z_j) / 2
C = sum_edges C_ij
```

QAOA parameters:

- Cost angles: one per layer or shared according to selected MVP convention.
- Mixer angles: one per layer or shared according to selected MVP convention.
- Depth `p` is a positive integer.

QAOA circuit semantics:

- Prepare an equal superposition over graph nodes.
- Alternate cost phase operations and mixer rotations for `p` layers.
- Evaluate expected cut value or equivalent energy under a documented sign convention.

MVP recommendation:

- Optimize expected cut value directly as a maximization objective, or minimize negative expected cut value. The result metadata must state which sign convention is used.

Result fields:

- `algorithm`: QAOA.
- `objective`: MaxCut.
- `final_value`.
- `final_parameters`.
- `best_value`.
- `best_parameters`.
- `depth`.
- `graph_summary`.
- `trace`.
- `stop_reason`.

MVP behavior target:

- Two-node MaxCut should approach expected cut value near `1`.
- A small triangle graph should exceed a random baseline in a smoke test under loose tolerance.

## 6. Objective function semantics

Objective functions must be:

- Scalar-valued.
- Deterministic on exact statevector device.
- Parameterized by a numeric vector or named mapping.
- Traceable through parameter metadata.

VQE objective:

- Minimization of Hamiltonian expectation.

QAOA objective:

- Maximization of expected MaxCut value or minimization of its negative.
- Sign convention must be stored in result metadata.

## 7. Callback design

Callback contract:

- Called at most once per optimization step.
- Receives a record containing step index, parameters, objective value, gradient when available, and metadata.
- Callback return value does not affect control flow in MVP unless a future stop-signal design is added.

Callback safety:

- Exceptions raised by callback should either propagate or be wrapped in QuantumBridge-authored diagnostics; MVP implementation must document the chosen behavior.

## 8. Logging and checkpoint pre-design

MVP logging:

- Algorithm result includes in-memory trace.
- No file logging is required.

Checkpoint placeholder:

- Result metadata reserves optional checkpoint records.
- Production checkpoint writing is deferred.

Trace size:

- MVP examples are small, so full trace storage is acceptable.
- Future versions may add trace sampling or streaming callbacks.

## 9. Clean-room risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Algorithm examples accidentally resemble third-party tutorials | Use original small Hamiltonians and graph examples |
| Optimizer API resembles common libraries | Keep contract generic and minimal |
| QAOA sign convention ambiguity | Document sign convention in result metadata and tests |
| VQE convergence tests become brittle | Use small analytic targets and loose, behavior-level thresholds |

## 10. Clean-room rationale

VQE and QAOA are public algorithmic concepts described in open literature and education materials. This document defines QuantumBridge MVP behavior without copying any third-party source implementation, tests, examples, comments, or documentation prose.

