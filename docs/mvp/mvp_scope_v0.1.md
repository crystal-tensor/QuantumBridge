# QuantumBridge SDK MVP Scope v0.1

Status: Draft  
Date: 2026-06-04  
Source basis: `docs/clean_room_spec/functional_spec_v0.1.md`, public quantum computing mathematics, and independently authored QuantumBridge architecture notes.  

This document is design-only. It contains no SDK implementation code and does not copy source code, tests, comments, error messages, directory structure, or documentation prose from Qiskit, PennyLane, or related projects.

## 1. MVP 目标

MVP v0.1 should prove that QuantumBridge can support a coherent end-to-end quantum workflow with a small, independently designed surface:

- Build circuits with declared quantum and classical storage.
- Add a compact set of standard unitary gates and measurements.
- Bind numeric values to named parameters.
- Execute circuits on a local statevector simulator.
- Produce exact probabilities and shot-based samples.
- Evaluate Pauli and Hamiltonian expectation values.
- Compute parameter-shift gradients for supported rotation gates.
- Run small VQE and QAOA examples with deterministic, inspectable behavior tests.
- Export supported circuits to an OpenQASM text subset for interchange.
- Maintain clean-room evidence for every design and implementation step.

The MVP is a correctness and architecture milestone, not a performance or ecosystem-completeness milestone.

## 2. MVP 非目标

MVP v0.1 does not include:

- Hardware provider integration or real-device job submission.
- Full compiler, routing, layout, scheduling, or noise-aware optimization.
- Density matrix simulation.
- Noise simulation.
- Distributed, GPU, tensor-network, or high-performance simulation.
- Full OpenQASM import.
- Full OpenQASM feature coverage.
- Full automatic differentiation framework integration.
- Full QML template library.
- Full optimizer suite.
- Drop-in compatibility with any third-party SDK.
- Replication of third-party internal architecture, naming patterns, tests, examples, or error text.

## 3. MVP 用户场景

### Scenario 1: Small circuit inspection

A user creates a one- or two-qubit circuit, runs it on an exact statevector device, and inspects amplitudes and probabilities.

Required outcome:

- The user can verify simple textbook states such as `H|0>` and Bell states.

### Scenario 2: Shot sampling

A user takes an exactly simulated probability distribution and asks for finite-shot samples with a fixed seed.

Required outcome:

- Counts sum to the requested shots.
- Deterministic states produce deterministic counts.
- Balanced states produce statistically reasonable counts under documented tolerances.

### Scenario 3: Expectation value

A user evaluates a Pauli observable or small Hamiltonian on the final state of a circuit.

Required outcome:

- `Z` expectation after `RY(theta)` matches `cos(theta)` within numerical tolerance.
- Hamiltonian expectation equals the weighted sum of term expectations.

### Scenario 4: Gradient-backed objective

A user defines a scalar expectation objective and differentiates it with parameter-shift.

Required outcome:

- The gradient for supported rotation gates matches independent analytic formulas on small cases.

### Scenario 5: Small VQE

A user minimizes a one- or two-qubit Hamiltonian with a small parameterized ansatz.

Required outcome:

- The energy trace moves toward a known low-energy region.
- The result records final parameters, final energy, and optimization metadata.

### Scenario 6: Small QAOA

A user encodes a small MaxCut graph and runs shallow QAOA.

Required outcome:

- The objective is computed from an independently defined graph-cost Hamiltonian.
- A smoke test exceeds a random baseline or reaches a known small-instance target under loose tolerance.

### Scenario 7: OpenQASM export

A user exports a supported circuit with numeric parameters and measurements.

Required outcome:

- The text represents declared storage, supported gates, numeric parameters, and measurement mapping using the selected export subset.

## 4. MVP 必须实现的功能

### Core circuit model

- Circuit creation with `num_qubits`, optional `num_bits`, optional name, and optional metadata.
- Ordered operation append semantics.
- Measurement declarations from quantum wires to classical bits.
- Parameter objects and binding maps.
- Circuit copy and simple composition.
- Circuit validation for wire bounds, duplicate measurement targets where relevant, supported operation arity, and bound numeric parameters before execution.

### Gate and operation model

Required unitary gates:

- Single-qubit: X, Y, Z, H, S, T, RX, RY, RZ, Phase.
- Two-qubit: CX, CZ, SWAP.
- Custom unitary: explicit matrix with declared target wires and validation requirements.

Deferred from MVP even if named in broader spec:

- CY, iSWAP, CCX, gate power, general decomposition, and controlled-generation helper.

### Measurement model

- Computational-basis measurement.
- State output.
- Probability output.
- Counts output.
- Expectation output for supported observables.

### Device and result model

- Exact statevector device.
- Shot sampler based on statevector probabilities.
- Result object containing available fields, metadata, and serialization-ready data.

### Observables

- Identity, PauliX, PauliY, PauliZ.
- Tensor-product Pauli words for small systems.
- Hamiltonian as a weighted sum of supported observables.

### Differentiation

- Parameter-shift gradient for RX, RY, and RZ expectation objectives under the standard Pauli-generator rotation convention.
- Scalar objective gradients over one or more parameters.
- Gradient metadata describing method, shifts, and unsupported parameters.

### Algorithms

- Minimal gradient descent optimizer.
- VQE loop for small Hamiltonians and user-provided ansatz contract.
- QAOA loop for small unweighted MaxCut graphs.
- Callback and trace hooks as design-stable extension points.

### OpenQASM export

- Export for supported MVP gates, numeric rotation parameters, declarations, and measurements.
- Clear unsupported-feature diagnostics authored by QuantumBridge.

### Tests and records

- Behavior tests from independent mathematics.
- Clean-room review record for implementation tasks.
- Dependency and license notes before release.

## 5. MVP 明确不实现的功能

- Hardware backend API beyond abstract capability fields.
- Asynchronous remote job queue behavior.
- Noise channels and readout-error simulation.
- Device calibration ingestion.
- Coupling maps and routing.
- Basis decomposition pass pipeline.
- Tensor-network IR execution.
- Sparse Hamiltonian acceleration.
- Hermitian observable matrix generality beyond small custom validation.
- Higher-order gradients.
- Finite-difference fallback as a production feature.
- Adjoint differentiation or backpropagation.
- JAX/Torch autograd adapters.
- Full QML layers such as embeddings and reusable ansatz libraries.
- Production checkpoint file management.

## 6. MVP 验收标准

MVP v0.1 is accepted when:

- The implemented public behavior matches the API contract and design documents in `docs/mvp/`.
- Every source file created in implementation phase includes the required clean-room header.
- All behavior tests listed in `behavior_test_plan_v0.1.md` pass.
- Statevector outputs match independent mathematical expectations within documented tolerances.
- Shot sampling tests pass with fixed seeds and statistical tolerances.
- Parameter-shift tests match analytic gradients for supported cases.
- VQE and QAOA smoke tests produce expected qualitative outcomes on small cases.
- OpenQASM export tests pass for supported circuits and reject unsupported circuits safely.
- Result serialization produces deterministic, JSON-compatible structures for supported result fields.
- Clean-room stage review reports no unresolved high-severity concern.

## 7. MVP 与后续版本的边界

### v0.1 establishes

- Public object vocabulary.
- Statevector and sampling semantics.
- Qubit ordering and measurement conventions.
- Minimal observable and gradient contracts.
- Algorithm result contracts.
- OpenQASM export subset.
- Behavior test provenance pattern.

### v0.2 candidates

- Additional gates: CY, iSWAP, CCX, controlled-operation helper.
- Circuit inverse for a broader gate set.
- Basic compiler pass framework and metrics.
- Finite-difference gradient fallback.
- More robust optimizer options.
- OpenQASM import subset.

### v0.3+ candidates

- Density matrix simulation.
- Noise simulation.
- JAX/Torch integration.
- QML layer library.
- Hardware backend adapters.
- Routing and layout.
- Tensor-network execution.

## 8. Clean-room Boundary Statement

This scope is intentionally defined from QuantumBridge's first-stage specification and general quantum computing principles. It does not require or permit source-level knowledge of any existing SDK.

