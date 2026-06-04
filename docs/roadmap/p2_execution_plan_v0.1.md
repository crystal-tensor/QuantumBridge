# P2 Execution Plan v0.1

Status: P2 planning review document  
Date: 2026-06-04  
Branch: `p2/planning`

This plan authorizes planning review only. It does not authorize P2
implementation, does not modify SDK code, and does not expand Qiskit or
PennyLane parity claims.

## 1. P2 Overall Goal

P2 should turn the P1 release-candidate baseline into a more robust experimental
SDK by hardening serialization, parsing, compiler behavior, noise execution,
and selected optional PennyLane bridge coverage.

The P2 goal is controlled depth, not broad parity. Each P2 feature must be
specified, tested, reviewed, and kept within QuantumBridge-owned behavior.

## 2. P2 Non-goals

P2 does not target:

- full Qiskit feature parity
- full PennyLane feature parity
- full OpenQASM 2.0 or OpenQASM 3 support
- production readiness
- hardware/cloud provider integration
- production visualization
- full transpiler ecosystem
- full autodiff framework integration
- Qiskit Aer parity
- official endorsement from IBM, Qiskit, Xanadu, or PennyLane

## 3. P2 / P1 RC Boundary

The P1 RC baseline is frozen at:

- tag: `v0.1.0-p1-rc1`
- commit: `bbd4bbca5c5a04ad009504874b14c8e9387b52c0`
- CI run: `26938623406`

P2 work must not mutate the P1 tag, retag the release, rewrite P1 release
notes, or reinterpret P1 unsupported features as supported. P2 changes must be
documented as P2 behavior and developed on P2 branches.

## 4. P2 First Batch

The first P2 batch should be:

| Priority | Area | Purpose | Start condition |
| --- | --- | --- | --- |
| P2-A | QASM grammar-based parser | Replace the P1 regex subset parser with an owned grammar-based parser for the documented subset. | Grammar design accepted. |
| P2-B | Result schema / JSON serialization | Define versioned result serialization and compatibility rules. | Schema design accepted. |
| P2-C | Compiler pass expansion | Add reviewed native passes for routing/layout/decomposition/optimization planning. | Pass invariants and equivalence tests accepted. |
| P2-D | Noise execution path | Move from metadata-only noise toward small, seeded noisy execution behavior. | Noise semantics accepted. |
| P2-E | PennyLane operation/template coverage | Expand selected optional PennyLane bridge coverage without parity claims. | Coverage list and unsupported cases accepted. |

Qiskit Aer is not part of the first priority batch.

## 5. P2 Second Batch

The second batch should begin only after P2-A through P2-E have review evidence
or are intentionally deferred:

- Qiskit Aer optional adapter design review
- visualization placeholder removal
- packaging and sdist/wheel content checks
- examples policy
- benchmark plan
- API stability level documentation
- versioning and release process documentation

## 6. Deferred Tasks

Temporarily defer:

- Qiskit Aer adapter implementation
- production visualization
- hardware/cloud providers
- full OpenQASM grammar
- OpenQASM 3
- framework-native autodiff deep integration
- qchem workflows
- performance claims and production benchmarks

## 7. P2 Risks

Key risks:

- accidental full-parity claims
- hidden dependence on third-party parser grammar, tests, docs, comments, or
  error messages
- breaking P1 result compatibility without schema versioning
- compiler rewrites that are not behavior-preserving
- noisy execution with unclear qubit ordering or random seed semantics
- optional dependency failures in CI
- PennyLane bridge expansion drifting into unsupported plugin behavior
- public API churn without stability labels
- legal/trademark ambiguity around upstream project names

## 8. P2 Acceptance Standards

P2 acceptance requires:

- every implemented task maps to a P2 issue ID
- every task has a design source document
- every public behavior has tests
- all optional dependency behavior is isolated to extras
- all upstream-facing docs retain optional adapter wording
- local and remote CI pass
- P1 RC tag remains reproducible
- release notes clearly distinguish P2 from P1 RC

## 9. P2 CI Requirements

P2 CI must retain the P1 matrix:

- `core-only`
- `qiskit-extra`
- `pennylane-extra`
- `dev`

Additional P2 CI expectations:

- dev profile continues to run coverage
- QASM parser tests run in core-only
- result schema tests run in core-only
- compiler pass tests run in core-only
- noise execution tests run in core-only unless an optional dependency is added
- PennyLane expansion tests run in `pennylane-extra`
- optional dependency unavailable cases remain explicit

Do not weaken CI to make P2 pass.

## 10. Public API Change Permission

P2 may modify public API only under review.

Allowed:

- adding clearly experimental APIs
- adding versioned serialization fields
- adding parser entry points with documented subset boundaries
- adding compiler/noise APIs marked experimental

Not allowed without explicit review:

- removing P1 APIs
- changing P1 result semantics without compatibility handling
- renaming optional adapter functions
- presenting experimental APIs as stable

## 11. New Optional Dependency Permission

P2 may introduce a new optional dependency only after review.

Requirements:

- dependency must be extra-only
- license and attribution impact must be documented
- CI install path must be isolated
- source migration ledger must be updated
- base package must remain installable without the dependency

No new optional dependency is automatically approved by this plan.

## 12. Aer Adapter Permission

Aer adapter implementation is not in the first priority batch.

P2 may continue Aer planning and dependency-policy review. Implementation is
allowed only after:

- legal/trademark review
- optional dependency CI plan
- minimal behavior design
- no-parity-claim wording review
- explicit approval to begin an Aer issue

## 13. Noisy Execution Permission

Noisy execution is in the first priority batch as P2-D.

Allowed scope:

- small native noisy sampling path
- seeded deterministic tests
- bit-flip, phase-flip, depolarizing, and readout-error behavior if the design
  accepts them

Not allowed:

- Aer-level noise model parity
- pulse noise
- hardware calibration import
- vague statistical behavior without tolerances

## 14. QASM Grammar Parser Permission

QASM grammar parser is the first P2 priority as P2-A.

Allowed scope:

- QuantumBridge-owned grammar for the supported subset
- parser diagnostics owned by QuantumBridge
- round-trip tests against QuantumBridge exporter behavior
- explicit unsupported syntax errors

Not allowed:

- copying external grammar files
- copying external tests or diagnostics
- claiming full OpenQASM support
- adding OpenQASM 3 support in P2-A

## 15. PennyLane Template Expansion Permission

PennyLane operation/template expansion is allowed as P2-E after scope review.

Allowed:

- selected operations
- selected observables
- small template bridges
- installed-environment tests

Not allowed:

- full PennyLane plugin compatibility
- full autodiff stack replacement
- qchem coverage
- claims of complete PennyLane compatibility

## 16. Module Test Requirements

| Module area | Required tests |
| --- | --- |
| QASM parser | Grammar acceptance/rejection, diagnostics, round-trip subset behavior. |
| Result schema | JSON round-trip, schema version checks, metadata preservation, compatibility tests. |
| Compiler | Pass invariants, property-set behavior, circuit equivalence, unsupported no-op cases. |
| Noise | Seeded behavior, statistical tolerance, probability sanity checks, metadata preservation. |
| PennyLane bridge | Installed-environment tests, unsupported operation diagnostics, observable/template conversion checks. |
| Optional dependencies | Install-path tests and skip/report behavior when unavailable. |
| Legal/attribution | Notice, license, ledger, and public wording checks for any upstream-facing changes. |

## 17. P2 Release Gate

P2 release requires:

- all selected P2 issues closed or explicitly deferred
- local full test suite pass
- remote GitHub Actions matrix pass
- coverage result recorded
- release notes drafted
- legal/trademark review complete
- source migration ledger updated
- P1 RC reproducibility confirmed
- no unsupported full-parity or production-readiness claims

P2 release must be a separate pre-release or release-candidate decision and must
not overwrite `v0.1.0-p1-rc1`.
