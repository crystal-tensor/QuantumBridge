# Third-party Notices

Status: Stage 7 planning update  
Date: 2026-06-05  

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

## Stage 7.2 additional optional ecosystems

Stage 7.2 adds optional inventory, passthrough, and result-schema adapters for Qiskit Nature, Qiskit Algorithms, Qiskit Dynamics, Qiskit Metal, PySCF, and OpenFermion, and expands the existing Finance, Optimization, Machine Learning, Experiments, Aer, and PennyLane coverage.

These upstream packages are not distributed inside QuantumBridge. Each package is installed into an isolated optional environment for verification. Qiskit Metal coverage is advisory and does not imply chip fabrication or electromagnetic simulation capability.
