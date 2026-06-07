# P2 Dual-track Expansion Plan v0.1

Status: Stage 6.1 implementation guide
Date: 2026-06-04
Branch: `p2/dual-track-expansion`

## 1. P2 Overall Goal

P2 advances QuantumBridge on two tracks: core SDK hardening and optional
upstream compatibility adapters. It is not a full native rewrite of Qiskit,
PennyLane, Qiskit Nature, Qiskit Algorithms, PySCF, or OpenFermion.

## 2. Track A: Core SDK P2

- grammar-based QASM subset parser
- result schema v0.2 and JSON serialization
- compiler pass expansion
- minimal noisy execution path
- PennyLane operation/template coverage through optional adapter boundaries

## 3. Track B: Nature / Algorithms / Chemistry Compatibility

- public API inventory for Qiskit Nature and Qiskit Algorithms
- optional dependency adapters and upstream passthrough wrappers
- native minimal Molecule, FermionicOp, Jordan-Wigner, chemistry result, and
  exact diagonalization support
- H2 native minimal workflow plus LiH/H2O educational examples

## 4. P2 Non-goals

- production release
- full feature parity
- full native chemistry rewrite
- full OpenQASM 3
- Qiskit Aer parity
- official upstream endorsement

## 5. P2 / P1 RC Boundary

P1 RC remains frozen at `v0.1.0-p1-rc1`. P2 work must happen on P2 branches and
must not mutate the tag.

## 6. Native Capabilities

Native Core is reserved for QuantumBridge IR/control surfaces, QASM subset,
schema, compiler, QOS/backend abstractions, minimal noise semantics, and small
chemistry data structures.

## 7. Adapter Capabilities

Qiskit Nature, Qiskit Algorithms, PySCF, OpenFermion, Qiskit, and PennyLane are
optional dependencies. Adapter behavior must record provenance.

## 8. Inventory-only Capabilities

Full Qiskit Nature and Qiskit Algorithms public APIs are inventory targets in
P2. Inventory coverage does not mean executable support.

## 9. Unsupported Capabilities

Unsupported in P2: production materials prediction, real band gap prediction,
full Aer noise, pulse noise, hardware calibration import, and complete upstream
replacement.

## 10. Avoiding Full Replacement Claims

Use wording such as `optional compatibility adapters for selected workflows`.
Do not say full replacement, full compatibility, official support, or native
rewrite of upstream packages.

## 11. P2 Release Gate

P2 release requires local tests, remote CI, optional dependency evidence where
used, coverage, release notes, legal/trademark review, and updated migration
ledger.

## 12. Test Requirements

Every native feature needs native tests. Every optional adapter needs installed
or skipped-unavailable tests with clear reasons. Skip is not capability proof.

## 13. Legal / License / Trademark Requirements

All upstream-facing changes must update third-party notices and source migration
ledger. Source ports require explicit attribution review before copying code.
