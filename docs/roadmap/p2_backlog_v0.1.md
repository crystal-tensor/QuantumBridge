# P2 Backlog v0.1

Status: Planning only  
Date: 2026-06-04  

This backlog does not authorize P2 implementation. QuantumBridge remains a P1
release-candidate subset until the P1 RC gate is accepted.

## P2-A: QASM Grammar-Based Parser

Goal: replace the P1 regex-oriented subset parser with a grammar-based parser
for an explicit OpenQASM 2.0 subset.

Scope:

- grammar definition owned by QuantumBridge
- parser diagnostics
- round-trip tests for supported statements
- unsupported statement rejection tests

Non-goals:

- full OpenQASM 2.0 coverage
- OpenQASM 3 support
- copying external grammar implementations

Tests:

- declaration parsing
- gate invocation parsing
- indexed and whole-register measurement
- comments, includes, barriers
- malformed input diagnostics

Risks:

- accidental over-claiming of OpenQASM compatibility
- grammar drift from exporter behavior
- hidden dependency on third-party grammar source

## P2-B: Qiskit Aer Optional Adapter

Decision: candidate for P2 planning, not approved for implementation yet.

Enter P2 if:

- P1 RC remote CI passes
- legal review accepts optional Aer dependency language
- adapter boundary remains optional and non-endorsed
- minimal execution behavior is documented

Do not enter if:

- Aer dependency creates unstable CI behavior
- tests require full Qiskit parity
- public docs imply official Qiskit/Aer endorsement

Minimum implementation:

- optional import boundary
- simple statevector/sampler delegation for supported QuantumBridge circuits
- result conversion back to QuantumBridge `Result`

Test strategy:

- installed-environment tests
- skipped tests when Aer is unavailable
- numerical checks against QuantumBridge-supported math cases

## P2-C: Compiler Pass Expansion

Scope:

- routing planning for coupling-map constrained circuits
- initial layout selection
- decomposition planning for unsupported native gates
- local optimization passes
- depth reduction heuristics
- two-qubit gate optimization

Non-goals:

- full transpiler ecosystem
- hardware-vendor calibration integration
- copying pass structures or names from external projects

Tests:

- pass ordering
- property-set behavior
- circuit equivalence for safe rewrites
- no-op behavior for unsupported rewrites

## P2-D: PennyLane Operation / Template Coverage

Scope:

- more one- and two-qubit operations
- more Pauli observables
- simple template bridges
- interface compatibility boundaries

Non-goals:

- full PennyLane plugin compatibility
- full autodiff stack replacement
- qchem coverage

Tests:

- installed PennyLane environment tests
- unsupported operation diagnostics
- observable conversion checks
- small executable bridge checks

## P2-E: Noise Execution Path

Current state: P1 has noise channel objects and sampler metadata only.

P2 candidate:

- implement real noisy sampling for a small set of channels
- support bit-flip, phase-flip, depolarizing, and readout error behavior

Non-goals:

- Aer-level noise model parity
- pulse noise
- hardware calibration noise import

Tests:

- deterministic seeded sampling
- probability sanity checks
- metadata preservation

## P2-F: Result Schema / Serialization

Scope:

- versioned JSON-compatible schema
- metadata namespace rules
- counts/probabilities/statevector/expectation fields
- backward compatibility policy

Tests:

- round-trip serialization
- unknown metadata preservation
- schema version validation

## P2-G: Visualization

Scope:

- text drawer completion
- matplotlib drawer decision
- placeholder removal plan

Non-goals:

- production visual editor
- web UI
- copying external drawer layouts

Tests:

- text output snapshot owned by QuantumBridge
- graceful fallback when matplotlib is unavailable
- docs that mark visualization as experimental
