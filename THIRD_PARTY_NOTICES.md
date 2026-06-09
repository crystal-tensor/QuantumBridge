# Third-party Notices

Status: Stage 8D adapter contract update
Date: 2026-06-09

QuantumBridge is an independent project. References to Qiskit and PennyLane are for attribution, compatibility, and optional adapter documentation only and do not imply endorsement.

## Qiskit attribution

Qiskit is an open-source quantum computing SDK distributed under Apache License 2.0.

- Local license copy: `LICENSES/QISKIT_LICENSE.txt`
- Current local package used for adapter tests: `qiskit==2.4.1`
- Current QuantumBridge usage mode: Adapter Integration and Upstream Dependency only.
- Source port status: No Qiskit source files have been copied into QuantumBridge in the current Stage 4 implementation.

## PennyLane attribution

PennyLane is an open-source quantum programming framework distributed under Apache License 2.0.

- Local license copy: `LICENSES/PENNYLANE_LICENSE.txt`
- Current local package used for adapter tests: `PennyLane==0.44.1`
- Current QuantumBridge usage mode: Adapter Integration and Upstream Dependency only.
- Source port status: No PennyLane source files have been copied into QuantumBridge in the current Stage 4 implementation.

## Apache License 2.0

The Apache License 2.0 text is stored at:

- `LICENSES/Apache-2.0.txt`

## Migrated source record table

| QuantumBridge module | Upstream project | Original path | License | Mode | Modification notes |
| --- | --- | --- | --- | --- | --- |
| None in current Stage 4 implementation | N/A | N/A | N/A | N/A | No source port performed |

Future source ports must add a row here and update `docs/migration/source_migration_ledger.md`.

## Qiskit ecosystem optional packages

QuantumBridge Stage 7 may optionally depend on Qiskit ecosystem packages for inventory, passthrough, adapter integration, and result wrapping. These packages remain upstream projects and are not vendored into this repository.

Packages covered by Stage 7 planning include:

- Qiskit core;
- Qiskit Aer;
- Qiskit IBM Runtime;
- Qiskit Finance;
- Qiskit Optimization;
- Qiskit Machine Learning;
- Qiskit Experiments;
- Qiskit Addons.

Usage mode: optional dependency, public API inventory, passthrough scaffold, and selected adapter integration. Source port status: no Stage 7 Qiskit ecosystem source files were copied into QuantumBridge.

## PennyLane ecosystem optional packages

QuantumBridge Stage 7 may optionally depend on PennyLane and PennyLane ecosystem plugins for inventory, passthrough, adapter integration, and result wrapping. These packages remain upstream projects and are not vendored into this repository.

Usage mode: optional dependency, public API inventory, passthrough scaffold, and selected adapter integration. Source port status: no Stage 7 PennyLane ecosystem source files were copied into QuantumBridge.

## Stage 6.1 optional upstream integrations

P2 planning and implementation introduces optional dependency routes for:

- Qiskit Nature
- Qiskit Algorithms
- PySCF
- OpenFermion

These packages are not vendored into QuantumBridge. QuantumBridge uses them only
when installed through optional extras and records behavior as Adapter
Integration or Upstream Passthrough unless a separate source-port review
explicitly approves otherwise.

QuantumBridge does not claim that upstream functionality is QuantumBridge
original work. QuantumBridge is not endorsed by IBM, Qiskit, Xanadu, PennyLane,
PySCF, or OpenFermion maintainers.

## Stage 7.2 additional optional ecosystems

Stage 7.2 adds optional inventory, passthrough, and result-schema adapters for Qiskit Nature, Qiskit Algorithms, Qiskit Dynamics, Qiskit Metal, PySCF, and OpenFermion, and expands the existing Finance, Optimization, Machine Learning, Experiments, Aer, and PennyLane coverage.

These upstream packages are not distributed inside QuantumBridge. Each package is installed into an isolated optional environment for verification. Qiskit Metal coverage is advisory and does not imply chip fabrication or electromagnetic simulation capability.

## Stage 8D Qiskit ecosystem adapter contracts

Stage 8D hardens optional adapter contracts for:

- Qiskit core;
- Qiskit Aer;
- Qiskit Nature;
- Qiskit Algorithms;
- Qiskit Finance;
- Qiskit Optimization;
- Qiskit Machine Learning;
- Qiskit Dynamics;
- Qiskit Experiments;
- Qiskit Metal;
- Qiskit IBM Runtime;
- Qiskit Addons.

Usage mode: optional dependency discovery, runtime public API inventory,
upstream passthrough where installed, QuantumBridge result-schema wrapping,
warnings, provenance, unsupported metadata, and environment validation.

Source port status: no Stage 8D Qiskit ecosystem source files, tests,
documentation prose, comments, error strings, wheels, dist-info, egg-info,
site-packages trees, or virtual environments were copied into QuantumBridge.

Runtime support is offline-only. QuantumBridge does not access IBM Cloud, read
tokens, store credentials, or submit jobs. Qiskit Metal support is advisory
only and does not provide chip fabrication, external electromagnetic
simulation, or layout signoff capability.

## Stage 9B Qiskit Optimization native subset

Stage 9B adds an independently implemented educational native binary
`QuadraticProgram` subset for small optimization examples. Qiskit Optimization
remains an optional upstream dependency for passthrough execution when
installed; no upstream source files, wheels, dist-info, egg-info, site-packages
trees, virtual environments, documentation prose, or examples were copied.

The native subset is not a full Qiskit Optimization replacement, not production
optimization software, and not endorsed by IBM or Qiskit maintainers.

## Stage 9C Qiskit Algorithms native subset

Stage 9C adds independently implemented educational native VQE, QAOA-compatible
MaxCut, and Grover workflows for small examples. Qiskit Algorithms remains an
optional upstream dependency for local passthrough execution when installed; no
upstream source files, wheels, dist-info, egg-info, site-packages trees,
virtual environments, documentation prose, website text, or examples were
copied.

The native subset is not a full Qiskit Algorithms replacement, not production
algorithm software, and not endorsed by IBM or Qiskit maintainers.

## Stage 9D Qiskit Nature native chemistry subset

Stage 9D adds independently implemented educational H2 and LiH chemistry
workflows with small QuantumBridge-owned qubit Hamiltonians and local exact
diagonalization. Qiskit Nature, PySCF, and OpenFermion remain optional upstream
dependencies for local passthrough or comparison paths when installed; no
upstream source files, wheels, dist-info, egg-info, site-packages trees,
virtual environments, documentation prose, website text, or examples were
copied.

The native subset is not a full Qiskit Nature replacement, not production
quantum chemistry, not molecular design software, not a materials band-gap
workflow, and not endorsed by IBM or Qiskit maintainers.

## IBM Quantum Ecosystem clean-room parity planning

Stage 9C-Revision adds a QuantumBridge-owned ecosystem parity plan and catalog
schema. It uses public project names only for compatibility identification and
does not copy IBM Quantum Ecosystem website text, layout, images, icons,
branding, screenshots, or source. QuantumBridge is independent and does not
claim IBM, Qiskit, PennyLane, Azure Quantum, MQT, Mitiq, TorchQuantum, or other
third-party endorsement.
