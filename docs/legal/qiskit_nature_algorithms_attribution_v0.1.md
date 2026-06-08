# Qiskit Nature / Algorithms Attribution v0.1

Status: P2 attribution policy  
Date: 2026-06-04  

QuantumBridge may use Qiskit Nature, Qiskit Algorithms, PySCF, and OpenFermion
as optional dependencies. These integrations are adapter or upstream passthrough
work unless a separate source-port review explicitly says otherwise.

## 1. Qiskit Nature Attribution

Qiskit Nature is an optional upstream dependency for chemistry workflows and
Hamiltonian/operator conversion. QuantumBridge must not claim Qiskit Nature
functionality as QuantumBridge-native functionality.

## 2. Qiskit Algorithms Attribution

Qiskit Algorithms is an optional upstream dependency for selected algorithm
workflows. QuantumBridge adapters wrap upstream behavior and result objects.

## 3. PySCF Attribution

PySCF may be used as an optional upstream driver for molecular data workflows.
Any PySCF-backed output must record provenance metadata.

## 4. OpenFermion Attribution

OpenFermion may be used as an optional upstream object bridge for fermionic or
operator data. Adapter behavior must be documented as optional.

## 5. Adapter-only Policy

Adapters convert upstream objects into QuantumBridge IR, Hamiltonian, Result,
Solver, or Backend objects. Adapter files must update the source migration
ledger.

## 6. Upstream Passthrough Policy

Passthrough code directly calls installed upstream packages and wraps the
result. It must record package provenance and must not be described as native.

## 7. Source Port Policy

Source ports are a last resort. They require explicit approval, retained
copyright notices, license text, NOTICE updates where required, and modification
notes.

## 8. Trademark Wording

Use neutral phrases such as `optional adapter for selected workflows`. Do not
state or imply official support, certification, endorsement, or full
compatibility.

## 9. Commercial Release Caution

Before any commercial release, repeat license, notice, dependency, and trademark
review for every optional integration.
