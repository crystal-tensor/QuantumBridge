# Stage 8 Ecosystem Fusion Master Plan

**Version**: v0.1  
**Date**: 2026-06-09  
**Status**: Stage 8A planning and interface hardening  

## 1. Goal

Stage 8 defines how QuantumBridge will coordinate Qiskit, PennyLane,
Quafu/pyquafu, QOS-UQCI, and the future QuantumBridge Studio experience without
claiming to replace any upstream project.

The stage is intentionally split into planning, contract hardening, inventory,
and narrow implementation slices. Stage 8A only establishes the architecture,
adapter contracts, schema expectations, governance boundaries, and test gates.

## 2. Non-Replacement Position

QuantumBridge is not a replacement for Qiskit, PennyLane, Quafu, QOS-UQCI, or
any upstream runtime. It is a bridge layer that can:

- discover optional upstream dependencies;
- expose public API inventory;
- pass through selected upstream objects when the package is installed;
- wrap results in QuantumBridge schemas with provenance and warnings;
- define compatibility paths between supported intermediate representations.

QuantumBridge must not claim full replacement, official endorsement, production
parity, or hardware/runtime equivalence.

## 3. Integration Model

QuantumBridge uses optional dependencies plus adapters plus schema wrappers.
This keeps the core SDK installable without heavy ecosystem packages and avoids
forcing incompatible dependency stacks into one environment.

| Layer | Responsibility |
| --- | --- |
| Optional dependency | Upstream package installed by the user or by a lane-specific extra. |
| Adapter | Dependency checks, public API lookup, passthrough, warnings, provenance. |
| Schema wrapper | Stable QuantumBridge result envelope for downstream tools. |
| Capability level | Explicit label for inventory, passthrough, schema, or native subset. |
| Test lane | Verifies installed, unavailable, advisory, and offline-only behavior. |

## 4. Ecosystem Roles

| Ecosystem | Role | Boundary |
| --- | --- | --- |
| Qiskit core | Circuit, transpiler, primitives, quantum information bridge. | Optional dependency, no full Qiskit replacement. |
| Qiskit Aer | Simulator and noise model bridge. | Optional; production equivalence not claimed. |
| Qiskit Nature / Algorithms | Chemistry and algorithm passthrough/adapters. | Optional chemistry-compatible lane. |
| Qiskit Finance / Optimization / ML | Domain adapters and result schemas. | Not production finance, optimization, or ML. |
| Qiskit Dynamics / Experiments | Advisory and installed-environment smoke paths. | No lab or calibration production claim. |
| Qiskit Metal | Advisory chip-design inventory. | Not EM simulation or fabrication support. |
| Qiskit Runtime | Offline-only metadata and adapter planning. | No IBM Cloud access, token reads, or credential storage. |
| PennyLane | Differentiable quantum programming, QNode, tape, operations, transforms. | Optional dependency, not a PennyLane replacement. |
| Quafu / pyquafu | Chinese ecosystem compatibility path and backend result planning. | Separate NumPy <2 lane, no cloud token storage. |
| QOS-UQCI | Canonical UQCI IR compatibility planning. | External optional project, no runtime or hardware claim. |
| QuantumBridge Studio | Future visual workflow layer. | Planning only until adapter contracts stabilize. |

## 5. Stage Split

| Stage | Scope | Output |
| --- | --- | --- |
| 8A | Ecosystem fusion planning and interface hardening. | Master plan, contracts, risk docs, light tests. |
| 8B | PennyLane full API inventory and adapter contracts. | Runtime inventory, optional dependency checks, generic passthrough, schema wrappers, basic metadata adapters, minimal bridge scaffolds. |
| 8C | PennyLane operation / measurement / QNode / tape bridge. | Narrow bridge slices with provenance. |
| 8D | Qiskit ecosystem adapter contract hardening. | Consistent adapter functions and warnings. |
| 8E | Qiskit / PennyLane bidirectional IR bridge. | Reviewed conversion paths and roundtrip tests. |
| 8F | Quafu / pyquafu compatibility. | Offline adapters, NumPy lane docs, result wrapper. |
| 8G | QOS-UQCI compatibility. | UQCI IR planning, mock backend, no hardware access. |
| 8H | QuantumBridge Studio product planning. | Product spec, information architecture, API contract. |
| 8I | Release candidate gate. | Release readiness review, no automatic tag. |

## 6. Direct-Push Mainline Workflow

The current owner instruction is to use direct push to `main`, not PRs. Direct
pushes must still be small, documented, and verified before and after push.

Required gates:

1. Sync `main` with `git pull --ff-only origin main`.
2. Inspect `git status` and do not include unrelated drafts.
3. Keep the change limited to the active stage.
4. Run local tests before push.
5. Push `main` directly only after tests pass.
6. Confirm the latest GitHub Actions `main` run is green.
7. Do not create tags or releases unless explicitly authorized.

If the project later re-enables external contributor PRs, the same scope,
tests, risk, and non-goal sections should be required in the PR body.

## 7. Test Strategy

Stage 8 keeps optional dependency tests lane-specific.

| Test type | Purpose |
| --- | --- |
| Core pytest | Ensure Stage 8 planning does not break core SDK. |
| Coverage run | Track coverage drift from contract additions. |
| Local matrix | Exercise optional dependency unavailable and installed paths. |
| Contract tests | Verify capability levels, result envelope fields, warnings, provenance. |
| Inventory tests | Ensure public API inventory uses introspection, not copied source. |
| Offline runtime tests | Confirm runtime/cloud adapters do not read tokens or contact cloud APIs. |

## 8. Risks

| Risk | Mitigation |
| --- | --- |
| False replacement claims | Required non-goal language in docs and warnings. |
| Dependency conflicts | Separate extras and constraints, especially chemistry vs quafu. |
| Upstream API drift | Inventory snapshots and version-provenance fields. |
| Runtime credential exposure | Offline-only adapters, environment variable policy, no storage. |
| UI overreach | Studio remains planning-only until contracts stabilize. |
| Legal attribution gaps | THIRD_PARTY_NOTICES and migration ledger review gates. |

## 9. Non-Goals

Stage 8A does not:

- implement full Qiskit or PennyLane coverage;
- implement product UI;
- connect to IBM Runtime, Quafu Cloud, QOS, UQCI hardware, or real devices;
- store tokens or credentials;
- vendor third-party source code;
- create a release or tag;
- claim full replacement or production parity.

## 10. Release Preconditions

Before any Stage 8 release candidate:

1. main CI must be green after the final Stage 8I gate.
2. Adapter contracts must be documented and tested.
3. Advisory and offline-only ecosystems must be labeled in README and docs.
4. THIRD_PARTY_NOTICES and source migration ledger must be reviewed.
5. No vendored dependency artifacts may be present.
6. Owner must explicitly authorize tag and release creation.

## 6.1 Stage 8B Implementation Snapshot

Stage 8B adds the first executable PennyLane full API bridge foundation:

- runtime full public API inventory and generated feature coverage matrix;
- optional dependency reporting without auto-install, token reads, or network
  access;
- generic public-object passthrough and safe object description;
- PennyLane result schema wrappers with provenance and warnings;
- basic operation, measurement, QNode, and tape metadata adapters;
- minimal PennyLane-to-QuantumBridge IR, Qiskit circuit, and QOS-UQCI job-spec
  scaffolds.

Stage 8B remains bounded. It does not claim full native PennyLane support,
production equivalence, QOS-UQCI runtime execution, real cloud access, hardware
access, release readiness, or UI implementation.
