# P2 Upstream Integration Strategy v0.1

Status: Planning route update  
Date: 2026-06-04  
Branch: `p2/planning`

P2 is not a full native rewrite of Qiskit, PennyLane, Qiskit Nature, Qiskit
Algorithms, PySCF, OpenFermion, or related upstream projects.

QuantumBridge should use upstream projects as optional dependencies when that is
the correct engineering choice, then expose QuantumBridge-owned boundaries for
IR, Hamiltonian, Result, Solver, Backend, QASM, compiler, noise, and QOS.

## 1. Route Principles

- Use upstream mature functionality through optional dependencies.
- Convert upstream objects into QuantumBridge objects at adapter boundaries.
- Implement native code only for QuantumBridge core control surfaces.
- Record all upstream-facing work in license, attribution, notice, and migration
  records.
- Do not claim upstream behavior as QuantumBridge-original functionality.
- Do not claim full replacement of Qiskit, PennyLane, Qiskit Nature, Qiskit
  Algorithms, PySCF, or OpenFermion.
- Do not imply official endorsement from upstream projects or their sponsors.

## 2. Implementation Modes

| Mode | Description | Default P2 use |
| --- | --- | --- |
| A. Upstream Passthrough | Directly call upstream package functionality and wrap results as QuantumBridge objects. | Chemistry drivers, algorithm solvers, optimizers, advanced simulation, optional workflows. |
| B. Adapter Integration | Convert upstream objects to/from QuantumBridge IR, Hamiltonian, Result, Solver, or Backend objects. | Object boundaries and interoperability. |
| C. Native Core | Implement QuantumBridge-owned control-plane and data-plane primitives. | IR, QASM grammar subset, result schema, compiler, QOS backend, selected native noise semantics. |
| D. Source Port with Attribution | Copy or migrate Apache-2.0 source only after explicit approval and attribution review. | Last resort only. |

## 3. Upstream Candidate Packages

| Package | P2 posture | Notes |
| --- | --- | --- |
| Qiskit | Optional dependency / adapter integration | Existing P1 adapter remains optional. |
| PennyLane | Optional dependency / adapter integration | Existing P1 adapter remains optional. |
| Qiskit Nature | Optional dependency / upstream passthrough + adapter integration | Candidate for chemistry workflows and Hamiltonian conversion. |
| Qiskit Algorithms | Optional dependency / upstream passthrough + adapter integration | Candidate for algorithm workflow wrappers. |
| PySCF | Optional dependency / upstream passthrough | Candidate driver/backend for molecular data when used through reviewed workflows. |
| OpenFermion | Optional dependency / adapter integration | Candidate operator/chemistry object bridge after review. |
| Qiskit Aer | Optional dependency / backend adapter candidate | Not first-batch implementation. |

## 4. Native Core Boundary

Native implementation is preferred only where QuantumBridge needs stable control:

- QuantumBridge IR
- result schema and JSON serialization
- QASM subset grammar/parser/export contract
- compiler pass contracts and selected native rewrites
- QOS/backend abstraction
- selected small noise semantics where needed for deterministic tests
- legal/attribution automation

## 5. Chemistry / Algorithms Direction

P2 should support common workflows by passthrough/adapters, not native chemistry
rewrites.

Initial workflow targets:

- H2
- LiH
- H2O

Expected flow:

1. Call upstream driver/mapper/solver where installed.
2. Convert Hamiltonian/operator data into QuantumBridge-owned representation.
3. Execute or wrap solver/algorithm result as a QuantumBridge Result/Solver
   object.
4. Serialize output with the P2 result schema.
5. Record dependency, license, attribution, and ledger entries.

## 6. Source Port Rule

Source porting is not a default strategy. It requires:

- written necessity statement
- license compatibility review
- retained copyright and license notices
- NOTICE update where required
- source migration ledger entry
- modification notes
- reviewer approval before code is copied

## 7. Public Wording Rule

Docs and release notes must say:

- `optional dependency`
- `adapter integration`
- `upstream passthrough`
- `not full feature parity`
- `not an official upstream project`

Docs and release notes must not say:

- `complete replacement`
- `full compatibility`
- `official Qiskit/PennyLane/Nature/Algorithms support`
- `QuantumBridge-native chemistry stack` unless native code actually exists and
  is reviewed as such
