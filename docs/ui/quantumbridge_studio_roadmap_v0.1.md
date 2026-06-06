# QuantumBridge Studio Roadmap v0.1

**Version**: v0.1 (Planning Stage)
**Date**: 2026-06-06
**Status**: Draft
**Owner**: OpenClaw (QuantumBridge 24-hour R&D Chief of Staff)

---

## 1. Overview

This document outlines the **roadmap** for QuantumBridge Studio development. It covers the timeline, milestones, and priorities for each development stage.

---

## 2. Development Principles

1. **MVP First** - Ship minimum viable product, then iterate
2. **Read-only Explorer First** - Safe, low-risk entry point
3. **No Production Claims** - Clearly label experimental features
4. **No Token Storage** - Security by design
5. **Adapter-based** - UI doesn't bind directly to upstream packages
6. **Provenance by Default** - Every result traceable

---

## 3. Development Stages

### Stage UI-0: Product Spec & Planning

**Timeline**: Week 1-2
**Priority**: P0 (Critical)

**Deliverables**:
- [x] Product Spec (`docs/ui/quantumbridge_studio_product_spec_v0.1.md`)
- [x] Information Architecture (`docs/ui/quantumbridge_studio_information_architecture_v0.1.md`)
- [x] Wireframe Plan (`docs/ui/quantumbridge_studio_wireframe_plan_v0.1.md`)
- [x] API Contract (`docs/ui/quantumbridge_studio_api_contract_v0.1.md`)
- [x] Roadmap (`docs/ui/quantumbridge_studio_roadmap_v0.1.md`)

**Milestone**: UI planning complete
**Status**: ✅ In Progress (2026-06-06)

---

### Stage UI-1: Read-only Ecosystem Explorer

**Timeline**: Week 3-4
**Priority**: P1 (High)

**Deliverables**:
- [ ] Frontend scaffolding (Next.js + TypeScript)
- [ ] Ecosystem Explorer page
- [ ] API inventory viewer
- [ ] Coverage matrix viewer
- [ ] Status badges (Installed/Scaffold/Not Available)
- [ ] Coverage level badges (L0/L1/L2/L3)

**Features**:
1. **Ecosystem Tree View**
   - Qiskit Core → circuit, transpiler, quantum_info, etc.
   - Qiskit Aer → AerSimulator, noise models, etc.
   - PennyLane → operations, measurements, QNode, etc.

2. **Function Search & Filter**
   - Search by name
   - Filter by Level 0/1/2/3
   - Filter by Installed/Scaffold/Not Available

3. **Function Detail View**
   - Function signature
   - Description
   - Example code
   - Provenance info

**Milestone**: User can browse all APIs without writing code
**Status**: 🔴 Not Started

---

### Stage UI-2: Circuit Builder + QASM Lab + Simulator MVP

**Timeline**: Week 5-8
**Priority**: P1 (High)

**Deliverables**:
- [ ] Circuit Builder with drag-and-drop
- [ ] Gate palette (H, X, Y, Z, RX, RY, RZ, CX, CZ, SWAP, Measure)
- [ ] QASM Lab with syntax highlighting
- [ ] Basic Simulator Lab (Statevector, Density Matrix, Sampler)
- [ ] Result visualization (Histogram, Statevector, Bloch sphere)

**Features**:
1. **Circuit Builder**
   - Drag gates from palette to canvas
   - Connect qubits with wires
   - Set parameters for parameterized gates
   - Preview QASM/IR in real-time

2. **QASM Lab**
   - Monaco Editor with syntax highlighting
   - QASM → Circuit conversion
   - Circuit → QASM conversion
   - Error diagnostics

3. **Simulator Lab**
   - Select simulator (QB native or Aer)
   - Configure shots/seed
   - Run simulation
   - View results (Histogram, Statevector, Bloch sphere)

**Milestone**: User can build circuits and run simulations
**Status**: 🔴 Not Started

---

### Stage UI-3: Chemistry + Algorithms MVP

**Timeline**: Week 9-12
**Priority**: P2 (Medium)

**Deliverables**:
- [ ] Molecule builder (H2, LiH, H2O)
- [ ] H2 workflow (VQE, bond scan)
- [ ] Algorithm Lab (VQE, QAOA, Grover)
- [ ] Convergence plots
- [ ] Energy curve visualization

**Features**:
1. **Chemistry Lab**
   - XYZ input or molecule library
   - Basis selection (STO-3G, 6-31G)
   - Driver selection (PySCF, Qiskit Nature)
   - Hamiltonian viewer
   - VQE execution
   - Bond scan and energy curve

2. **Algorithms Lab**
   - Algorithm selection (VQE, QAOA, Grover)
   - Ansatz selection
   - Optimizer selection
   - Parameter history
   - Convergence plot

**Warning**: "Experimental chemistry. Not for production use."
**Status**: 🔴 Not Started

---

### Stage UI-4: Finance/Optimization/ML Labs

**Timeline**: Week 13-16
**Priority**: P2 (Medium)

**Deliverables**:
- [ ] Finance Lab (portfolio optimization, option pricing)
- [ ] Optimization Lab (MaxCut, TSP, Knapsack)
- [ ] Machine Learning Lab (QNN, QSVC, VQC)
- [ ] TorchConnector status display

**Features**:
1. **Finance Lab**
   - Portfolio optimization
   - Option pricing (Amplitude Estimation)
   - Data provider (Yahoo Finance)
   - Result dashboard

2. **Optimization Lab**
   - QuadraticProgram builder
   - Problem library (MaxCut, TSP, Knapsack)
   - Converter chain visualization
   - Solution display

3. **ML Lab**
   - QNN builder (SamplerQNN, EstimatorQNN)
   - Kernel methods (QSVC)
   - VQC workflow
   - Training curves

**Warning**: "Experimental finance/ML. Not for production use."
**Status**: 🔴 Not Started

---

### Stage UI-5: Runtime/Backend/Result Center

**Timeline**: Week 17-20
**Priority**: P3 (Lower)

**Deliverables**:
- [ ] Backend/Runtime Lab
- [ ] Job monitor
- [ ] Result Center (all results)
- [ ] Schema viewer
- [ ] JSON/CSV export
- [ ] Provenance explorer
- [ ] Compare runs

**Features**:
1. **Backend Lab**
   - Local backend (QB native)
   - Aer backend (if installed)
   - Quafu backend (if installed)
   - IBM Runtime adapter (offline-only, no token storage)

2. **Result Center**
   - All results list (filterable)
   - Result detail view
   - Schema viewer
   - Provenance info
   - Export (JSON, CSV)
   - Reproducibility (rerun with same parameters)

3. **Job Monitor**
   - Active jobs
   - Job status (pending/running/completed/failed)
   - Job history

**Status**: 🔴 Not Started

---

### Stage UI-6: Team/Cloud/Productization

**Timeline**: Week 21-24+
**Priority**: P4 (Future)

**Deliverables**:
- [ ] User accounts and authentication
- [ ] Project management
- [ ] Team sharing and collaboration
- [ ] Real-time collaboration (CRDT)
- [ ] Cloud backend execution
- [ ] Reports and analytics
- [ ] Documentation portal
- [ ] Commercial packaging

**Features**:
1. **Team Features**
   - User accounts (email/password, SSO)
   - Project workspaces
   - Team sharing
   - Access control (viewer/editor/admin)

2. **Cloud Features**
   - Cloud backend execution
   - GPU acceleration
   - Distributed simulation
   - Job queue with priority

3. **Commercial Features**
   - Usage reports
   - SLA guarantees (future)
   - Support tiers (future)

**Status**: 🔴 Not Started

---

## 4. Technology Stack

### 4.1 Frontend

| Component | Technology | Version |
|---|---|---|
| Framework | Next.js | 14+ |
| Language | TypeScript | 5+ |
| UI Library | shadcn/ui | latest |
| Styling | Tailwind CSS | 3+ |
| Circuit Canvas | React Flow | 11+ |
| Code Editor | Monaco Editor | 0.47+ |
| Charts | Plotly / ECharts | latest |
| State | Zustand | latest |

### 4.2 Backend

| Component | Technology | Version |
|---|---|---|
| Framework | FastAPI | 0.110+ |
| Language | Python | 3.9+ |
| Runtime | Uvicorn | latest |
| Job Queue | Celery | 5+ |
| Database | SQLite → PostgreSQL | - / 15+ |
| File Storage | Local → S3 | - / (future) |

### 4.3 DevOps

| Component | Technology | Version |
|---|---|---|
| Container | Docker | 24+ |
| CI/CD | GitHub Actions | - |
| Hosting | Local → Vercel/AWS | - |

---

## 5. Milestones

### 5.1 Short-term Milestones (Q3 2026)

| Date | Milestone | Description |
|---|---|---|
| 2026-07-01 | **UI-0 Complete** | All planning docs done |
| 2026-07-15 | **UI-1 Alpha** | Read-only Ecosystem Explorer |
| 2026-08-01 | **UI-2 Alpha** | Circuit Builder MVP |

### 5.2 Medium-term Milestones (Q4 2026)

| Date | Milestone | Description |
|---|---|---|
| 2026-10-01 | **UI-3 Beta** | Chemistry + Algorithms Labs |
| 2026-11-01 | **UI-4 Beta** | Finance/Optimization/ML Labs |
| 2026-12-01 | **UI-5 Beta** | Result Center + Job Monitor |

### 5.3 Long-term Milestones (2027+)

| Date | Milestone | Description |
|---|---|---|
| 2027-Q1 | **v0.2.0** | Production-ready MVP |
| 2027-Q2 | **v0.3.0** | Team features |
| 2027-Q3 | **v1.0.0** | Stable release |

---

## 6. Dependencies & Blockers

### 6.1 Internal Dependencies

| Feature | Depends On |
|---|---|
| Circuit Builder | QuantumBridge Circuit IR |
| Simulator Lab | QuantumBridge Sampler/Estimator |
| Chemistry Lab | Qiskit Nature adapter |
| Algorithms Lab | QuantumBridge VQE/QAOA |
| Result Center | All Labs |

### 6.2 External Dependencies

| Package | Used By | Status |
|---|---|---|
| qiskit | Aer, Nature, Algorithms | ✅ Available |
| qiskit-aer | Simulator Lab | ✅ Available |
| pennylane | PennyLane Lab | ✅ Available |
| pyscf | Chemistry Lab | ⚠️ Inventory needed |
| torch | ML Lab | ⚠️ Optional |

### 6.3 Blockers

| Blocker | Impact | Resolution |
|---|---|---|
| QuantumBridge Circuit IR incomplete | Circuit Builder | Complete IR spec first |
| Adapter Layer incomplete | All Labs | Implement Level 2 adapters |
| No test coverage for UI | Production | Add E2E tests |

---

## 7. Resource Estimates

### 7.1 Development Effort

| Stage | Estimated Effort | Team Size |
|---|---|---|
| UI-0 (Planning) | 1 week | 1 person |
| UI-1 (Explorer) | 2 weeks | 1-2 people |
| UI-2 (Circuit MVP) | 4 weeks | 2 people |
| UI-3 (Chemistry) | 4 weeks | 1-2 people |
| UI-4 (Finance/ML) | 4 weeks | 1-2 people |
| UI-5 (Result Center) | 4 weeks | 1 person |
| UI-6 (Team/Cloud) | 8+ weeks | 2-3 people |

### 7.2 Infrastructure Costs (Monthly)

| Service | MVP | Team | Cloud |
|---|---|---|---|
| Compute | $0 (local) | $50 | $500 |
| Storage | $0 (local) | $10 | $100 |
| Database | $0 (SQLite) | $25 | $200 |
| CDN | $0 | $10 | $50 |
| **Total** | **$0** | **$95** | **$850** |

---

## 8. Success Metrics

### 8.1 User Engagement

| Metric | Target (6 months) | Target (12 months) |
|---|---|---|
| Monthly Active Users | 100 | 1,000 |
| Daily Active Users | 20 | 200 |
| Average Session Duration | 15 min | 20 min |
| Circuits Built per User | 10 | 50 |
| Jobs Submitted per User | 50 | 200 |

### 8.2 Technical Quality

| Metric | Target |
|---|---|
| Test Coverage | > 80% |
| Accessibility Score (Lighthouse) | > 90 |
| Performance Score (Lighthouse) | > 90 |
| Uptime | > 99.5% |
| Crash-free Sessions | > 99% |

### 8.3 User Satisfaction

| Metric | Target |
|---|---|
| NPS Score | > 50 |
| User Rating | > 4.0/5.0 |
| Feature Request Ratio | < 0.5 (vs bug reports) |
| Support Ticket Volume | < 10/week |

---

## 9. Open Questions

1. **What is the target audience for v1.0?**
   - Quantum researchers? Students? Hobbyists? Enterprise?

2. **Should we support real hardware backends?**
   - IBM Quantum? Rigetti? IonQ?
   - What about token management?

3. **Should we monetize?**
   - Freemium model? Subscription? Enterprise license?

4. **Should we open-source?**
   - Frontend? Backend? Both?
   - What about the adapter layer?

5. **What is the timeline for v1.0?**
   - 6 months? 12 months? 18 months?

---

## 10. Change Log

| Date | Version | Changes |
|---|---|---|
| 2026-06-06 | v0.1 | Initial draft |

---

**Document Version**: v0.1
**Last Updated**: 2026-06-06
**Author**: OpenClaw (QuantumBridge 24-hour R&D Chief of Staff)