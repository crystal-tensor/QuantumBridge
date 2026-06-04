# P2 Execution Plan v0.1

Status: P2 planning review document, updated for upstream integration route  
Date: 2026-06-04  
Branch: `p2/planning`

This plan authorizes planning review only. It does not authorize P2
implementation, does not modify SDK code, and does not expand Qiskit,
PennyLane, Qiskit Nature, Qiskit Algorithms, PySCF, or OpenFermion parity
claims.

## 1. P2 Overall Goal

P2 is an integration-led expansion, not a full native rewrite.

QuantumBridge should use mature upstream projects as optional dependencies where
that is the safest and fastest path, then wrap upstream results into
QuantumBridge-owned abstractions such as IR, Hamiltonian, Result, Solver, and
Backend.

P2 goals:

- build a complete public API inventory for Qiskit Nature and Qiskit Algorithms
- identify common chemistry and algorithm workflows that should be supported by
  adapter integration or upstream passthrough
- make small molecule workflows such as H2, LiH, and H2O run through upstream
  drivers and return QuantumBridge result/schema objects
- strengthen QuantumBridge native core areas: QASM, compiler, result schema,
  noise, and QOS/backend abstractions
- maintain license, attribution, notice, and migration-ledger discipline for all
  upstream-facing work

## 2. Implementation Modes

P2 work must classify every feature into one of four modes:

| Mode | Meaning | P2 use |
| --- | --- | --- |
| A. Upstream Passthrough | Directly call an installed upstream package and wrap the output as a QuantumBridge result. | Prefer for mature chemistry, algorithms, simulation, optimization, and solver workflows. |
| B. Adapter Integration | Convert upstream objects into QuantumBridge IR, Hamiltonian, Result, Solver, or Backend objects. | Prefer for interoperability boundaries. |
| C. Native Core | Implement QuantumBridge-owned infrastructure where control and stability matter. | Use for IR, QASM subset grammar, result schema, compiler passes, QOS backend abstractions, and selected native noise behavior. |
| D. Source Port with Attribution | Copy or migrate Apache-2.0 source only when truly necessary, preserving copyright, license, notices, and modification records. | Last resort only; requires explicit review before any code is copied. |

## 3. P2 Non-goals

P2 does not target:

- full native rewrite of Qiskit
- full native rewrite of PennyLane
- full native rewrite of Qiskit Nature
- full native rewrite of Qiskit Algorithms
- full native rewrite of PySCF or OpenFermion
- full feature parity with any upstream project
- official endorsement from IBM, Qiskit, Xanadu, PennyLane, PySCF, or
  OpenFermion maintainers
- production readiness
- full OpenQASM 2.0 or OpenQASM 3 support
- full transpiler ecosystem
- full autodiff framework integration

## 4. P2 / P1 RC Boundary

The P1 RC baseline is frozen at:

- tag: `v0.1.0-p1-rc1`
- commit: `bbd4bbca5c5a04ad009504874b14c8e9387b52c0`
- CI run: `26938623406`

P2 work must not mutate the P1 tag, retag the release, rewrite P1 release
notes, or reinterpret P1 unsupported features as supported. P2 changes must be
documented as P2 behavior and developed on P2 branches.

## 5. P2 First Batch

The first P2 batch should combine upstream inventory, adapter design, and native
core hardening:

| Priority | Area | Mode | Purpose | Start condition |
| --- | --- | --- | --- | --- |
| P2-A | Qiskit Nature / Qiskit Algorithms public API inventory | Planning | Build a complete inventory and classify APIs by passthrough, adapter, native core, defer, or no-go. | Inventory template accepted. |
| P2-B | Result schema / JSON serialization | Native Core | Define versioned QuantumBridge result serialization and compatibility rules. | Schema design accepted. |
| P2-C | Chemistry workflow adapters for H2, LiH, H2O | Upstream Passthrough + Adapter Integration | Use upstream drivers/solvers where available and wrap outputs as QuantumBridge Hamiltonian/Result/Solver objects. | Dependency/legal review accepted. |
| P2-D | QASM grammar-based parser | Native Core | Replace the P1 regex subset parser with an owned grammar-based parser for the documented subset. | Grammar design accepted. |
| P2-E | Compiler pass expansion | Native Core | Add reviewed native passes for routing/layout/decomposition/optimization planning. | Pass invariants and equivalence tests accepted. |
| P2-F | Noise execution path | Native Core first, upstream optional later | Move from metadata-only noise toward small, seeded noisy execution behavior. | Noise semantics accepted. |
| P2-G | PennyLane operation/template coverage | Adapter Integration + Upstream Passthrough | Expand selected optional PennyLane bridge coverage without parity claims. | Coverage list and unsupported cases accepted. |
| P2-H | QOS backend abstraction | Native Core + Adapter Integration | Define backend capability, queue/status, execution metadata, and adapter boundaries. | Backend contract accepted. |

Qiskit Aer is not a first-batch implementation item. It may be reviewed as an
optional upstream passthrough/backend adapter after the first-batch contracts are
stable.

## 6. P2 Second Batch

The second batch should begin only after first-batch review evidence exists or a
first-batch item is intentionally deferred:

- Qiskit Aer optional adapter design review
- OpenFermion optional bridge review
- PySCF optional driver bridge review
- visualization placeholder removal
- packaging and sdist/wheel content checks
- examples policy
- benchmark plan
- API stability level documentation
- versioning and release process documentation

## 7. Deferred Tasks

Temporarily defer:

- Qiskit Aer adapter implementation
- native quantum chemistry implementation
- native molecular integral generation
- production visualization
- hardware/cloud providers
- full OpenQASM grammar
- OpenQASM 3
- framework-native autodiff deep integration
- performance claims and production benchmarks
- any source port not explicitly approved by review

## 8. P2 Risks

Key risks:

- accidentally implying QuantumBridge owns upstream functionality
- accidentally implying full upstream replacement or official endorsement
- hidden dependence on third-party parser grammar, tests, docs, comments, or
  error messages
- missing license, notice, attribution, or migration-ledger records for upstream
  integrations
- breaking P1 result compatibility without schema versioning
- compiler rewrites that are not behavior-preserving
- noisy execution with unclear qubit ordering or random seed semantics
- optional dependency failures in CI
- PennyLane bridge expansion drifting into unsupported plugin behavior
- chemistry workflow tests becoming too slow or environment-sensitive
- public API churn without stability labels

## 9. P2 Acceptance Standards

P2 acceptance requires:

- every implemented task maps to a P2 issue ID
- every task declares its implementation mode
- every task has a design source document
- every public behavior has tests
- all optional dependency behavior is isolated to extras
- all upstream-facing docs retain optional adapter/passthrough wording
- source migration ledger is updated for every upstream-facing file
- local and remote CI pass
- P1 RC tag remains reproducible
- release notes clearly distinguish P2 from P1 RC

## 10. P2 CI Requirements

P2 CI must retain the P1 matrix:

- `core-only`
- `qiskit-extra`
- `pennylane-extra`
- `dev`

Potential P2 extras must be added only after review:

- `qiskit-nature`
- `qiskit-algorithms`
- `pyscf`
- `openfermion`
- `qiskit-aer`

Additional P2 CI expectations:

- dev profile continues to run coverage
- result schema tests run in core-only
- QASM parser tests run in core-only
- compiler pass tests run in core-only
- native noise execution tests run in core-only unless an optional dependency is
  added
- upstream chemistry/algorithm workflow tests run only in their optional extras
- PennyLane expansion tests run in `pennylane-extra`
- optional dependency unavailable cases remain explicit

Do not weaken CI to make P2 pass.

## 11. Public API Change Permission

P2 may modify public API only under review.

Allowed:

- adding clearly experimental APIs
- adding versioned serialization fields
- adding parser entry points with documented subset boundaries
- adding compiler/noise/QOS APIs marked experimental
- adding adapter constructors for upstream objects
- adding result wrappers for upstream passthrough outputs

Not allowed without explicit review:

- removing P1 APIs
- changing P1 result semantics without compatibility handling
- renaming optional adapter functions
- presenting experimental APIs as stable
- claiming upstream passthrough behavior as QuantumBridge-native behavior

## 12. New Optional Dependency Permission

P2 may introduce a new optional dependency only after review.

Requirements:

- dependency must be extra-only
- license and attribution impact must be documented
- CI install path must be isolated
- source migration ledger must be updated
- base package must remain installable without the dependency
- docs must state whether behavior is upstream passthrough or adapter
  integration

Candidate optional dependencies include Qiskit Nature, Qiskit Algorithms, PySCF,
OpenFermion, and Qiskit Aer. None is automatically approved for implementation
by this plan.

## 13. Aer Adapter Permission

Aer adapter implementation is not in the first priority batch.

P2 may continue Aer planning and dependency-policy review. Implementation is
allowed only after:

- legal/trademark review
- optional dependency CI plan
- minimal behavior design
- no-parity-claim wording review
- explicit approval to begin an Aer issue

If implemented later, Aer should be treated as upstream passthrough or backend
adapter integration, not as a native QuantumBridge simulator rewrite.

## 14. Noisy Execution Permission

Noisy execution is a first-batch candidate as P2-F.

Allowed scope:

- small native noisy sampling path where QuantumBridge needs stable semantics
- seeded deterministic tests
- bit-flip, phase-flip, depolarizing, and readout-error behavior if the design
  accepts them
- optional upstream passthrough only after dependency review

Not allowed:

- Aer-level noise model parity
- pulse noise
- hardware calibration import
- vague statistical behavior without tolerances

## 15. QASM Grammar Parser Permission

QASM grammar parser is a first-batch native core item as P2-D.

Allowed scope:

- QuantumBridge-owned grammar for the supported subset
- parser diagnostics owned by QuantumBridge
- round-trip tests against QuantumBridge exporter behavior
- explicit unsupported syntax errors

Not allowed:

- copying external grammar files
- copying external tests or diagnostics
- claiming full OpenQASM support
- adding OpenQASM 3 support in P2-D

## 16. PennyLane Template Expansion Permission

PennyLane operation/template expansion is allowed as P2-G after scope review.

Allowed:

- selected operations
- selected observables
- small template bridges
- installed-environment tests
- upstream passthrough where PennyLane owns the operation semantics

Not allowed:

- full PennyLane plugin compatibility
- full autodiff stack replacement
- qchem coverage unless routed through a separate optional dependency review
- claims of complete PennyLane compatibility

## 17. Chemistry / Algorithms Permission

Qiskit Nature and Qiskit Algorithms work begins with public API inventory, not
implementation.

Allowed after inventory review:

- upstream passthrough for mature drivers, mappers, solvers, optimizers, or
  algorithm workflows
- adapter integration into QuantumBridge Hamiltonian, Result, Solver, and
  Backend objects
- H2, LiH, and H2O workflow tests where dependencies are installed and runtime
  is CI-safe

Not allowed:

- native rewrite of chemistry stacks
- copying chemistry algorithm source
- claiming QuantumBridge originates upstream chemistry or algorithm outputs
- making heavy chemistry dependencies mandatory for core install

## 18. Module Test Requirements

| Module area | Required tests |
| --- | --- |
| API inventory | Completeness checklist, classification by implementation mode, unsupported/no-go records. |
| QASM parser | Grammar acceptance/rejection, diagnostics, round-trip subset behavior. |
| Result schema | JSON round-trip, schema version checks, metadata preservation, compatibility tests. |
| Chemistry adapters | Optional-dependency installed tests for H2/LiH/H2O where feasible, object conversion checks, skipped-unavailable behavior. |
| Algorithms adapters | Optional-dependency installed tests for selected workflows, result wrapping checks, unsupported workflow diagnostics. |
| Compiler | Pass invariants, property-set behavior, circuit equivalence, unsupported no-op cases. |
| Noise | Seeded behavior, statistical tolerance, probability sanity checks, metadata preservation. |
| QOS backend | Capability reporting, job/status metadata, adapter boundaries, failure states. |
| PennyLane bridge | Installed-environment tests, unsupported operation diagnostics, observable/template conversion checks. |
| Optional dependencies | Install-path tests and skip/report behavior when unavailable. |
| Legal/attribution | Notice, license, ledger, and public wording checks for every upstream-facing change. |

## 19. P2 Release Gate

P2 release requires:

- all selected P2 issues closed or explicitly deferred
- all upstream-facing features classified by implementation mode
- local full test suite pass
- remote GitHub Actions matrix pass
- optional dependency CI evidence for selected upstream integrations
- coverage result recorded
- release notes drafted
- legal/trademark review complete
- source migration ledger updated
- P1 RC reproducibility confirmed
- no unsupported full-parity, originality, endorsement, or production-readiness
  claims

P2 release must be a separate pre-release or release-candidate decision and must
not overwrite `v0.1.0-p1-rc1`.
