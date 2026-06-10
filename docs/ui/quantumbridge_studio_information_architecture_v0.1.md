# QuantumBridge Studio Information Architecture v0.1

## Stage 10C Backend Information Architecture

The first backend API slice organizes Studio data around catalog projects,
workflows, input schemas, executions, results, exports, benchmarks, warnings,
and provenance.

The architecture is local-only and backend-only. It prepares future frontend
screens without implementing UI components or copying third-party UI/branding.

## Stage 10D Frontend Information Architecture

The Stage 10D prototype adds Catalog, Workflows, Workflow Detail, Execute,
Benchmarks, Results, and Exports views. Each view is backed by generated Stage
10C local seed data and exposes clean-room warnings and provenance.

**Version**: v0.1  
**Date**: 2026-06-09  
**Status**: Stage 8A planning only  

## 1. Boundary

This document plans the information architecture for QuantumBridge Studio. It
does not implement Next.js, React, frontend code, cloud access, hardware access,
or product release assets.

Studio depends on stable QuantumBridge adapter contracts, result schemas,
capability levels, warnings, and provenance.

## 2. Navigation Map

| Area | Purpose | Required backend contract |
| --- | --- | --- |
| Ecosystem Explorer | Browse installed, advisory, and unavailable ecosystems. | Inventory, dependency, warnings, provenance. |
| All Projects Catalog | Browse QuantumBridge clean-room ecosystem compatibility targets. | Ecosystem catalog schema, capability levels, warnings, provenance. |
| Circuit Builder | Build and inspect circuits visually. | QuantumBridge IR and QASM import/export. |
| QASM Lab | Edit QASM, parse AST, roundtrip. | QASM parser/exporter and validation. |
| Simulator Lab | Run local simulators and optional Aer paths. | Backend/result schema and provenance. |
| Chemistry Lab | Explore chemistry workflows. | Chemistry lane, optional dependency status. |
| Algorithms Lab | Explore VQE/QAOA/eigensolvers. | Algorithms adapters and result schemas. |
| Finance Lab | Explore finance examples. | Advisory finance warnings and result schema. |
| Optimization Lab | Explore optimization examples. | Optional optimization adapter status. |
| Machine Learning Lab | Explore QNN/kernel workflows. | Optional ML adapter status. |
| PennyLane Lab | Explore QNode, tape, operations, gradients. | PennyLane full adapter contract. |
| Quafu Backend Lab | Explore pyquafu compatibility planning. | Quafu dependency lane and no-token policy. |
| QOS-UQCI Lab | Explore UQCI IR/bundle compatibility. | UQCI IR contract and mock backend status. |
| Result Center | Inspect results, warnings, provenance, JSON. | Ecosystem result contract. |
| Code Generator | Export Python, QASM, IR, or bundle snippets. | Stable schema serializers. |

## 3. Global UI States

Each page must be able to show:

- installed;
- unavailable;
- advisory-only;
- offline-only;
- scaffold-only;
- unsupported with reason;
- warning count;
- provenance available;
- no official endorsement;
- no production parity claim.

## 4. Release Boundary

Stage 8A does not publish a Studio product version. It only defines the future
navigation, backend contracts, and warnings model.

## 5. Ecosystem Parity Experience

The All Projects Catalog is a QuantumBridge-owned experience inspired by the
need to discover ecosystem capabilities, not a copy of IBM Quantum Ecosystem.
It should expose:

- category filters;
- search;
- capability level and executable workflow status;
- install extra and dependency availability;
- provenance and legal boundary notes;
- native/upstream comparison readiness;
- visualization readiness.

No IBM UI, branding, text, iconography, screenshots, or endorsement should be
used.
