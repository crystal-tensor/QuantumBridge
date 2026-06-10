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

## Stage 9G Mitiq optional ecosystem

Stage 9G adds optional Mitiq dependency detection and independently
implemented educational native error-mitigation workflows. Mitiq remains an
upstream project and is not vendored into this repository.

Usage mode: optional dependency detection, upstream passthrough metadata,
QuantumBridge result-schema wrapping, warnings, provenance, and independently
implemented native educational ZNE/readout workflows.

Source port status: no Mitiq source files, tests, documentation prose, comments,
error strings, wheels, dist-info, egg-info, site-packages trees, or virtual
environments were copied into QuantumBridge.

## Stage 9H PennyLane-Qiskit optional ecosystem

Stage 9H adds optional PennyLane-Qiskit plugin dependency detection and
independently implemented educational native bidirectional bridge workflows.
PennyLane-Qiskit remains an optional upstream package and is not required by
the native Stage 9H examples.

Implemented by QuantumBridge:

- Qiskit circuit to QuantumBridge IR to PennyLane executable spec;
- PennyLane operation/tape/QNode metadata to QuantumBridge IR to Qiskit circuit;
- bidirectional Bell-state equivalence proof over QuantumBridge's native simulator;
- result schemas, warnings, provenance, and no-cloud/no-token metadata.

Source port status: no PennyLane-Qiskit, Qiskit, PennyLane, IBM, or Xanadu
source files, tests, documentation prose, comments, error strings, wheels,
dist-info, egg-info, site-packages trees, virtual environments, or vendored
package artifacts were copied into QuantumBridge.

## Stage 9I Qiskit Experiments and Dynamics offline slices

Stage 9I adds clean-room Qiskit Experiments and Qiskit Dynamics offline
educational executable slices. They use public package names and optional
dependency detection only. They do not copy IBM, Qiskit, Qiskit Experiments,
Qiskit Dynamics, tutorial prose, UI, branding, or source code, and they do not
claim hardware calibration, production dynamics, full replacement, or production
parity.

## Stage 9J MQT Core / DDSIM / QMAP compatibility slice

Stage 9J adds clean-room MQT Core-like, DDSIM-like, and QMAP-like educational
compatibility workflows. MQT ecosystem packages remain optional upstream
dependencies for local passthrough metadata only. The native Stage 9J examples
do not require upstream MQT packages.

No MQT source code, tutorial implementation, website text, UI, branding,
wheels, dist-info, egg-info, site-packages trees, virtual environments, or
vendored package artifacts are copied into QuantumBridge. Project and package
names are used only to identify optional compatibility targets.

The native subset is not a full MQT Core, DDSIM, or QMAP replacement, not a
decision-diagram simulator parity claim, not optimal mapping software, not
production compiler/simulator/mapper parity, and not endorsed by MQT maintainers
or IBM.

## Stage 9K TorchQuantum / PyTorch-style QML compatibility slice

Stage 9K adds clean-room TorchQuantum-like educational QML workflows for a
native quantum layer, tensor/batch forward execution, deterministic toy
classifier training, optional torch tensor interop when PyTorch is installed,
and optional upstream TorchQuantum boundary metadata when installed separately.

No TorchQuantum or PyTorch source code, tutorial implementation, website text,
UI, branding, model weights, wheels, dist-info, egg-info, site-packages trees,
virtual environments, or vendored package artifacts are copied into
QuantumBridge.

The native subset is not a full TorchQuantum replacement, not a full PyTorch
replacement, not production QML training, not for high-risk automated decisions,
and not endorsed by TorchQuantum, PyTorch, IBM, or Qiskit maintainers.

## Stage 10A QOS-UQCI / Quafu backend compatibility slice

Stage 10A adds clean-room offline QOS-UQCI and Quafu-compatible backend
workflows. It uses public project/package names only and QuantumBridge-owned
job specs, payloads, mock runtime/backend execution, result schemas, examples,
and tests.

No QOS-UQCI, Quafu, or pyquafu source code, tutorial implementation, website
text, UI, branding, wheels, dist-info, egg-info, site-packages trees, virtual
environments, or vendored package artifacts are copied into QuantumBridge.

The native subset is not production QOS runtime support, not production Quafu
backend support, does not access cloud services, does not read tokens, does not
execute real hardware, and is not endorsed by QOS-UQCI or Quafu maintainers.

## Stage 10B Benchpress / Benchmarking compatibility slice

Stage 10B adds a clean-room local benchmarking adapter for QuantumBridge-owned
small educational workloads. It provides a benchmark case registry, local
runner, default suites, result schemas, JSON / Markdown reports, and optional
upstream Benchpress boundary metadata when installed separately.

No IBM, Qiskit, or Benchpress source code, tutorial implementation, website
text, UI, branding, benchmark methodology, wheels, dist-info, egg-info,
site-packages trees, virtual environments, or vendored package artifacts are
copied into QuantumBridge.

The native subset is not a full Benchpress replacement, not official benchmark
output, not a production performance ranking system, does not access cloud
services, does not read tokens, does not execute real hardware, and is not
endorsed by IBM, Qiskit, or Benchpress maintainers.

## Stage 10C QuantumBridge Studio backend API slice

Stage 10C adds a QuantumBridge-owned local backend API layer for future Studio
experiences. It provides catalog, workflow registry, input schema, local
execution, result store, export, benchmark, provenance/warning, and REST-like
local router services. It does not implement a frontend UI, does not start a
production server, and does not open network ports.

No IBM, Qiskit, PennyLane, Benchpress, QOS-UQCI, Quafu, MQT, Mitiq,
TorchQuantum, PyTorch, FastAPI, or other third-party source code, website text,
tutorial prose, UI, branding, wheels, dist-info, egg-info, site-packages trees,
or virtual environments are copied into QuantumBridge. Project and package
names are used only to identify optional compatibility targets.

This backend API slice is not an official service, not endorsed by upstream
maintainers, not a full replacement, not production API software, and does not
access cloud services, tokens, credentials, or real hardware.

## Stage 10D QuantumBridge Studio frontend prototype

Stage 10D adds a QuantumBridge-owned static local frontend prototype over the
Stage 10C backend API seed data. Its UI, layout, CSS, local data client, and
smoke checks are independently implemented for QuantumBridge.

No IBM, Qiskit, PennyLane, Benchpress, QOS-UQCI, Quafu, MQT, Mitiq,
TorchQuantum, PyTorch, FastAPI, React, Vite, Carbon, or other third-party
source code, website text, tutorial prose, UI, branding, logos, wheels,
dist-info, egg-info, site-packages trees, `node_modules`, build outputs, or
virtual environments are copied into QuantumBridge. Project and package names
are used only to identify optional compatibility targets.

This frontend prototype is not an official service, not endorsed by upstream
maintainers, not a full replacement, not production UI software, and does not
access cloud services, tokens, credentials, or real hardware.

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

## Stage 9E Qiskit Machine Learning native QML subset

Stage 9E adds independently implemented educational quantum-kernel, kernel
classifier, QNN forward, and QNN classifier workflows. The implementation uses
QuantumBridge-native circuits, NumPy math, deterministic toy datasets, and
optional runtime introspection of installed `qiskit-machine-learning` objects.

No Qiskit Machine Learning source code, tutorial implementation, IBM website
copy, IBM branding, model weights, training data, wheels, dist-info,
site-packages, or virtual environments are vendored. Project and package names
are used only to identify optional compatibility targets.

This subset is not a full Qiskit Machine Learning replacement, not production
machine learning software, and not intended for high-risk automated decisions.

## IBM Quantum Ecosystem clean-room parity planning

Stage 9C-Revision adds a QuantumBridge-owned ecosystem parity plan and catalog
schema. It uses public project names only for compatibility identification and
does not copy IBM Quantum Ecosystem website text, layout, images, icons,
branding, screenshots, or source. QuantumBridge is independent and does not
claim IBM, Qiskit, PennyLane, Azure Quantum, MQT, Mitiq, TorchQuantum, or other
third-party endorsement.
