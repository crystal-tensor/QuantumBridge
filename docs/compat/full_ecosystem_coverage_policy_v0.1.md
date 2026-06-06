# QuantumBridge Full Ecosystem Coverage Policy v0.1

Status: Stage 7 planning
Branch: p2/ecosystem-full-coverage-planning
Scope: optional dependency inventory, passthrough, adapter scaffold, and native-core boundary

## Purpose

QuantumBridge uses ecosystem coverage to make mature upstream quantum workflows usable through QuantumBridge schemas and review gates. Coverage does not mean full replacement, full parity, official endorsement, or native reimplementation of upstream projects.

## Coverage Levels

| Level | Name | Meaning | Production claim |
| --- | --- | --- | --- |
| 0 | Inventory | QuantumBridge records public names, package presence, and compatibility risk. | No |
| 1 | Passthrough | QuantumBridge imports and exposes an upstream object when the optional dependency is installed. | No |
| 2 | Adapter | QuantumBridge converts selected upstream objects into QuantumBridge IR, Result, Hamiltonian, Solver, or Backend schemas. | No |
| 3 | Native subset | QuantumBridge independently implements a reviewed subset that is strategically core to QuantumBridge. | No broad parity |
| 4 | Production equivalent | Not promised for Stage 7. Requires separate legal, technical, and domain review. | Not in scope |

## Integration Modes

- Upstream Passthrough: call the upstream package and wrap results with provenance.
- Adapter Integration: convert public upstream objects into QuantumBridge schemas.
- Native Core: independently implement core QuantumBridge capabilities such as IR, result schema, QASM parser, compiler passes, and QoS backend routing.
- Source Port with Attribution: allowed only by explicit review, with copyright, license, NOTICE, and migration ledger records.

## Stage 7 Boundary

Stage 7 may add package-specific adapter scaffolds, inventory scripts, coverage matrix output, optional dependency extras, constraints files, tests, and review documents. Stage 7 must not vendor third-party source, claim upstream feature ownership, or force incompatible optional dependency groups into a single environment.

## Required Provenance

Every ecosystem adapter result must include:

- upstream package name;
- installed upstream version when available;
- QuantumBridge dependency extra;
- integration mode;
- coverage level;
- no-vendored-source policy marker;
- explicit `official_endorsement: false`.

## Dependency Isolation

Optional dependency lanes must remain separate when package constraints conflict. A missing optional dependency is a valid inventory outcome and must produce a clear ImportError or a skipped/smoke test, not a misleading native fallback.

## Native Core Priority

QuantumBridge native work remains focused on IR, compiler, QASM grammar parser, result schema, backend/QoS routing, deterministic simulator subsets, and carefully reviewed conversion schemas.
