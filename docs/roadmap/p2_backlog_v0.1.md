# P2 Backlog v0.1

Status: Planning only, updated for upstream integration route
Date: 2026-06-04

This backlog does not authorize P2 implementation. P2 is not a full native
rewrite of Qiskit, PennyLane, Qiskit Nature, Qiskit Algorithms, PySCF, or
OpenFermion.

## P2-A: Qiskit Nature / Qiskit Algorithms Public API Inventory

Goal: inventory public APIs and classify them by implementation mode.

Scope:

- Qiskit Nature public API inventory
- Qiskit Algorithms public API inventory
- classification as upstream passthrough, adapter integration, native core,
  source-port candidate, defer, or no-go
- dependency/license/CI risk notes

Non-goals:

- implementing the adapters during inventory
- claiming full compatibility
- copying upstream source or tests

Tests:

- inventory completeness checklist
- classification review checklist
- no-code review gate

Risks:

- underestimating dependency complexity
- mistaking inventory coverage for feature implementation
- unclear attribution strategy

## P2-B: Result Schema / JSON Serialization

Goal: define versioned QuantumBridge result serialization that can wrap native
and upstream passthrough outputs.

Scope:

- versioned JSON-compatible schema
- metadata namespace rules
- upstream provenance fields
- counts/probabilities/statevector/expectation/energy/optimizer fields
- compatibility policy

Tests:

- round-trip serialization
- unknown metadata preservation
- schema version validation
- upstream provenance field checks

## P2-C: Chemistry / Algorithms Workflow Adapters

Goal: support common workflows through optional upstream dependencies and
QuantumBridge result/schema wrappers.

Scope:

- H2 workflow
- LiH workflow
- H2O workflow
- Hamiltonian/operator conversion into QuantumBridge objects
- solver/algorithm result wrapping
- optional dependency skip behavior

Non-goals:

- native chemistry rewrite
- native molecular integral generation
- full Qiskit Nature or Qiskit Algorithms compatibility
- mandatory chemistry dependencies

Tests:

- installed-environment workflow tests where CI-safe
- skipped-unavailable behavior
- object conversion tests
- result schema round-trip checks

## P2-D: QASM Grammar-Based Parser

Goal: replace the P1 regex-oriented subset parser with a QuantumBridge-owned
grammar-based parser for an explicit subset.

Scope:

- grammar definition owned by QuantumBridge
- parser diagnostics owned by QuantumBridge
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

## P2-E: Compiler Pass Expansion

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

## P2-F: Noise Execution Path

Current state: P1 has noise channel objects and sampler metadata only.

P2 candidate:

- implement native small noisy sampling where QuantumBridge needs stable
  semantics
- support bit-flip, phase-flip, depolarizing, and readout error behavior if the
  design accepts them
- consider upstream passthrough only after optional dependency review

Non-goals:

- Aer-level noise model parity
- pulse noise
- hardware calibration noise import

Tests:

- deterministic seeded sampling
- probability sanity checks
- statistical tolerances
- metadata preservation

## P2-G: PennyLane Operation / Template Coverage

Scope:

- more one- and two-qubit operations
- more Pauli observables
- simple template bridges
- upstream passthrough where PennyLane owns semantics
- interface compatibility boundaries

Non-goals:

- full PennyLane plugin compatibility
- full autodiff stack replacement
- qchem coverage through PennyLane without separate review

Tests:

- installed PennyLane environment tests
- unsupported operation diagnostics
- observable conversion checks
- small executable bridge checks

## P2-H: QOS Backend Abstraction

Scope:

- backend capability reporting
- queue/status metadata
- job lifecycle states
- adapter boundaries for upstream and native backends
- result provenance fields

Non-goals:

- real cloud provider integration
- SLA claims
- production scheduling guarantees

Tests:

- backend capability serialization
- job state transitions
- adapter error paths
- provenance preservation

## P2-I: Qiskit Aer Optional Adapter

Decision: candidate for later P2 planning, not first-batch implementation.

Enter implementation only if:

- legal review accepts optional Aer dependency language
- adapter boundary remains optional and non-endorsed
- minimal execution behavior is documented
- CI install path is stable

Do not enter if:

- Aer dependency creates unstable CI behavior
- tests require full Qiskit parity
- public docs imply official Qiskit/Aer endorsement

Minimum future implementation:

- upstream passthrough/backend adapter only
- no Aer source port
- result conversion back to QuantumBridge Result

## P2-J: Visualization

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
