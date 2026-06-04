# P2 Start Plan v0.1

Status: P2 planning branch opened, no P2 implementation started  
Date: 2026-06-04  
Branch: `p2/planning`

QuantumBridge P2 must preserve the frozen P1 RC baseline
`v0.1.0-p1-rc1`. This document is a planning entry point only.

## 1. P2 Must Not Develop Directly From Main

P2 work must not be committed directly to `main`. The `main` branch should keep
the P1 RC freeze records and stable release-candidate baseline intact.

All P2 planning and implementation work must start from explicit P2 branches,
beginning with:

- `p2/planning`

Any later implementation branch should be derived intentionally and reviewed
before merge.

## 2. P2 First Priority

The first P2 priority is to convert the accepted P2 backlog into scoped issues
with owners, acceptance criteria, and review gates.

Initial planning focus:

- grammar-based QASM parser design
- optional Qiskit Aer adapter decision
- compiler pass expansion design
- PennyLane coverage boundaries
- result schema/versioning policy

## 3. P2 Deferred / Not Yet Started

Do not start the following until issue scope and review gate are accepted:

- QASM parser implementation
- Aer adapter implementation
- broader PennyLane operation/template implementation
- real noisy execution path
- production visualization
- full compiler routing/layout/decomposition stack
- public API stability guarantees

## 4. P2 Issue Groups

P2 issue groups should follow the existing backlog:

- QASM grammar parser
- Qiskit Aer optional adapter
- compiler pass expansion
- PennyLane operation/template coverage
- noise execution path
- result schema and serialization
- visualization
- CI, coverage, packaging, legal, trademark, docs, examples, benchmarks,
  versioning, and release process

## 5. P2 Development Order

Recommended order:

1. Confirm P1 RC tag and release notes are accepted.
2. Convert P2 backlog into GitHub issues.
3. Assign owners and reviewers.
4. Approve design documents for the first P2 issue group.
5. Implement one isolated P2 issue at a time.
6. Run local and remote CI for every branch.
7. Require review before merging any P2 work.

## 6. P2 Review Gate

Every P2 implementation task must include:

- explicit issue ID
- design source document
- supported behavior and non-goals
- tests based on QuantumBridge-owned behavior
- optional dependency boundary review, where applicable
- legal/trademark review for upstream-facing adapter changes
- CI evidence before merge

## 7. P1 RC Baseline Protection

P2 must not mutate, retag, or reinterpret `v0.1.0-p1-rc1`.

The P1 RC baseline remains:

- tag: `v0.1.0-p1-rc1`
- commit: `bbd4bbca5c5a04ad009504874b14c8e9387b52c0`
- GitHub Actions run: `26938623406`

If P2 introduces breaking changes, they must be documented as P2 behavior and
must not be backdated into P1 RC documentation.
