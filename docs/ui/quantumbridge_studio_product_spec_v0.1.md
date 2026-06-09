# QuantumBridge Studio Product Specification v0.1

**Version**: v0.1 (Planning Stage)
**Date**: 2026-06-06
**Status**: Draft
**Owner**: OpenClaw (QuantumBridge 24-hour R&D Chief of Staff)

---

## 1. Executive Summary

QuantumBridge Studio is a **visual frontend** for QuantumBridge SDK that enables users to interact with quantum computing workflows **without writing code**. It provides a graphical interface to build circuits, run simulations, explore ecosystem capabilities, and export workflows as Python code or QASM.

Stage 8A note: this is a product planning document only. It does not implement
frontend code, connect to real cloud tokens, access real hardware, or publish a
product release.

### Key Value Propositions

1. **No-code quantum computing** - Build and run quantum circuits visually
2. **Ecosystem exploration** - Browse Qiskit/PennyLane/QuantumBridge APIs
3. **Workflow export** - Generate Python code, QASM, or JSON from visual workflows
4. **Provenance tracking** - All results traceable to upstream packages
5. **Transparent dependency status** - Clear visibility of what's installed vs. scaffold

### Core Principles

1. ❌ **Never hide optional dependency status** - Users must know what's available
2. ❌ **Never claim production-grade** - Clearly label experimental features
3. ✅ **Based on QuantumBridge schema** - UI doesn't directly bind to upstream packages
4. ✅ **Backend via adapter** - All calls go through QuantumBridge adapters
5. ✅ **Provenance by default** - All results include source tracking
6. ✅ **Exportable workflows** - Every workflow can be exported as code
7. ✅ **Contract-gated UI** - UI work waits for stable adapter and result contracts

---

## 2. Product Vision

### 2.1 Target Users

| User Type | Description | Primary Use Case |
|---|---|---|
| **Quantum Researchers** | PhD students, postdocs | Experiment with quantum algorithms, compare simulators |
| **Software Engineers** | Developers new to quantum | Learn quantum programming, prototype workflows |
| **Data Scientists** | ML/AI practitioners | Explore QML algorithms, integrate with ML pipelines |
| **Educators** | Professors, instructors | Create teaching materials, demonstrate concepts |
| **Hobbyists** | Quantum enthusiasts | Learn and experiment without coding |

### 2.2 Non-Target Users

| User Type | Reason |
|---|---|
| Production quantum engineers | Not production-grade |
| Hardware calibration specialists | No hardware integration |
| Financial traders | Not production finance |
| Materials scientists | No band gap workflows |

### 2.3 Long-term Vision

**Year 1**: Visual circuit builder + simulator lab
**Year 2**: Full ecosystem coverage (Qiskit/PennyLane)
**Year 3**: Team collaboration + cloud integration
**Year 4**: Enterprise features + commercial packaging

---

## 3. Core Modules

### 3.1 Home Dashboard

**Purpose**: Central hub for users to understand their environment and recent activity.

**Features**:
1. **Installed Ecosystem Status**:
   - Green checkmark: ✅ Installed and tested
   - Yellow warning: ⚠️ Scaffold only
   - Red X: ❌ Not installed
   - Click to see details (version, coverage level, tests)

2. **Available Adapters**:
   - List of all ecosystem adapters
   - Filter by: Installed / Scaffold / Not Available
   - Click to see adapter details (Level 0/1/2/3, API count)

3. **CI/Version Info**:
   - Current QuantumBridge version
   - Last CI run status
   - Last inventory update

4. **Recent Jobs**:
   - Last 10 jobs (circuit, algorithm, simulation)
   - Status: Success / Failed / Running
   - Click to view results

5. **Quick Start**:
   - Pre-built examples: Bell State, VQE, QAOA, etc.
   - Click to open in Circuit Builder or Algorithm Lab

### 3.2 Ecosystem Explorer

**Purpose**: Browse and search all available APIs across Qiskit/PennyLane/QuantumBridge.

**Features**:
1. **Tree View**:
   - Qiskit Core → circuit, transpiler, quantum_info, etc.
   - Qiskit Aer → AerSimulator, noise models, etc.
   - Qiskit Nature → drivers, problems, mappers, etc.
   - PennyLane → operations, measurements, QNode, etc.
   - QuantumBridge → core, algorithms, primitives, etc.

2. **Search**:
   - Search by function name (e.g., "VQE", "HGate", "statevector")
   - Filter by: Level 0/1/2/3, Installed/Scaffold

3. **Function Detail View**:
   - Function signature
   - Description
   - Example code
   - Installed status
   - Provenance (which upstream package, which adapter)
   - One-click "Generate Code" button

4. **Coverage Level Indicator**:
   - Level 0 (Inventory): Gray badge
   - Level 1 (Passthrough): Blue badge
   - Level 2 (Adapter): Green badge
   - Level 3 (Native): Gold badge
   - Unsupported: Red badge

### 3.3 Circuit Builder

**Purpose**: Visually construct quantum circuits using drag-and-drop gates.

**Features**:
1. **Gate Palette**:
   - Single-qubit gates: H, X, Y, Z, RX, RY, RZ, S, T
   - Two-qubit gates: CX, CZ, SWAP
   - Multi-qubit gates: CCX (limited support)
   - Measurement: Measure, Measure All

2. **Circuit Canvas**:
   - Horizontal tracks = qubits
   - Drag gates onto tracks
   - Connect gates with wires
   - Resize qubits, add/remove qubits

3. **Parameter Support**:
   - Add parameters to gates (e.g., θ for RX(θ))
   - Bind parameters later

4. **Circuit Preview**:
   - Real-time text/ASCII preview
   - Depth / gate count statistics

5. **Export Options**:
   - Export as QASM 2.0
   - Export as QuantumBridge IR
   - Export as Python code (QuantumBridge)
   - Export as Python code (Qiskit)
   - Export as Python code (PennyLane)

6. **Import Options**:
   - Import from QASM
   - Import from QuantumBridge IR
   - Import from Python code (limited)

### 3.4 QASM Lab

**Purpose**: Edit and visualize QASM code with syntax highlighting and AST inspection.

**Features**:
1. **QASM Editor**:
   - Syntax highlighting
   - Line numbers
   - Error highlighting
   - Auto-complete (basic)

2. **AST Visualization**:
   - Parse QASM into AST
   - Visual tree view of AST nodes
   - Click node to highlight code

3. **Roundtrip Testing**:
   - QASM → Circuit → QASM
   - Verify semantic equivalence

4. **Error Diagnostics**:
   - Parse errors with line/column
   - Runtime errors during simulation

5. **Conversion Tools**:
   - QASM → Circuit (visual)
   - Circuit → QASM (code)

### 3.5 Compiler Lab

**Purpose**: Visualize and control quantum circuit compilation/transpilation.

**Features**:
1. **Pass Manager View**:
   - List of available passes
   - Drag to create pass sequence
   - Visual pass pipeline

2. **Compilation Options**:
   - Layout selection (trivial, dense, noise_adaptive)
   - Routing selection (basic, stochastic, sabre)
   - Basis gate selection
   - Optimization level (0-3)

3. **Before/After Comparison**:
   - Side-by-side circuit view
   - Depth comparison
   - Gate count comparison
   - Two-qubit gate count

4. **Fidelity Estimation**:
   - Theoretical fidelity estimate (if backend provided)
   - Error rate visualization

5. **Export**:
   - Export compiled circuit as QASM
   - Export as Python code with pass manager

### 3.6 Simulator Lab

**Purpose**: Run quantum circuits on simulators and visualize results.

**Features**:
1. **Simulator Selection**:
   - QuantumBridge Statevector Simulator
   - QuantumBridge Density Matrix Simulator
   - QuantumBridge Sampler
   - Qiskit Aer Simulator (if installed)

2. **Noise Model** (if Aer installed):
   - Select noise model
   - Configure error rates
   - Readout error

3. **Execution Options**:
   - Shots (for sampler)
   - Seed (for reproducibility)
   - Backend selection

4. **Result Visualization**:
   - Histogram (counts)
   - Statevector display (real/imag)
   - Bloch sphere (single qubit)
   - Probability table

5. **Result Export**:
   - Export as JSON
   - Export as Python code

### 3.7 Chemistry Lab

**Purpose**: Build and run quantum chemistry workflows.

**Features**:
1. **Molecule Builder**:
   - XYZ input (text)
   - Molecule library (H2, LiH, H2O, etc.)
   - 3D visualization (if possible)

2. **Basis Selection**:
   - STO-3G, 6-31G, etc.
   - PySCF integration (if installed)

3. **Driver Selection**:
   - PySCF (if installed)
   - Qiskit Nature driver (if installed)
   - OpenFermion (if installed)

4. **Mapping**:
   - Jordan-Wigner
   - Parity
   - Bravyi-Kitaev

5. **Hamiltonian Viewer**:
   - Display Hamiltonian as Pauli strings
   - Number of terms, number of qubits

6. **Solver Selection**:
   - VQE
   - Exact solver (NumPy)
   - QAOA (for specific problems)

7. **Energy Curve**:
   - Bond length scan
   - Plot energy vs. bond length
   - Compare to classical reference

8. **Smoke Tests**:
   - H2 smoke test
   - LiH smoke test
   - H2O smoke test

9. **Warning**:
   - "This is experimental chemistry. Not for production use."

### 3.8 Algorithms Lab

**Purpose**: Configure and run quantum algorithms.

**Features**:
1. **Algorithm Selection**:
   - VQE
   - QAOA
   - Grover
   - Amplitude Estimation
   - NumPyMinimumEigensolver (classical)

2. **Algorithm Configuration**:
   - Ansatz selection
   - Optimizer selection (COBYLA, SPSA, L-BFGS-B, etc.)
   - Max iterations
   - Convergence criteria

3. **Hamiltonian Input**:
   - Manual Pauli string input
   - Import from Chemistry Lab
   - Load from file

4. **Execution**:
   - Run algorithm
   - Real-time parameter history
   - Convergence plot

5. **Results**:
   - Minimum eigenvalue
   - Optimal parameters
   - Optimal state
   - Execution time

6. **Export**:
   - Export as Python code
   - Export as notebook

### 3.9 Finance Lab

**Purpose**: Explore quantum finance workflows.

**Features**:
1. **Portfolio Optimization**:
   - Asset selection
   - Expected returns
   - Covariance matrix
   - Risk factor

2. **Option Pricing**:
   - European call/put
   - Amplitude estimation

3. **Credit Risk**:
   - Probability distribution

4. **Data Provider**:
   - Yahoo Finance (if available)
   - Manual input

5. **Warning**:
   - "This is experimental finance. Not for production trading."

### 3.10 Optimization Lab

**Purpose**: Build and solve optimization problems.

**Features**:
1. **QuadraticProgram Builder**:
   - Variable definition (binary, integer, continuous)
   - Objective function
   - Constraints

2. **Problem Library**:
   - MaxCut
   - TSP
   - Knapsack

3. **Converter Chain**:
   - Linear equality to penalty
   - Integer to binary
   - Inequality to equality

4. **Solver Selection**:
   - QAOA
   - VQE
   - Classical solvers (CPLEX, if available)

5. **Solution Visualization**:
   - Variable assignments
   - Objective value
   - Constraint satisfaction

### 3.11 Machine Learning Lab

**Purpose**: Build and train quantum machine learning models.

**Features**:
1. **QNN Builder**:
   - SamplerQNN
   - EstimatorQNN
   - Ansatz selection

2. **Kernel Methods**:
   - QSVC
   - Quantum kernel visualization

3. **VQC (Variational Quantum Classifier)**:
   - Ansatz
   - Optimizer
   - Loss function

4. **TorchConnector**:
   - Integration status
   - PyTorch version (if installed)

5. **Dataset Upload**:
   - CSV upload
   - sklearn datasets (iris, wine, etc.)

6. **Training**:
   - Training curve
   - Accuracy
   - Loss

7. **Prediction**:
   - Test input
   - Prediction output

8. **Warning**:
   - "This is experimental ML. Not for production models."

### 3.12 Dynamics Lab

**Purpose**: Simulate quantum dynamics.

**Features**:
1. **Hamiltonian Model**:
   - Time-dependent Hamiltonian
   - Signal definition

2. **Lindblad Model**:
   - Dissipators
   - Open system dynamics

3. **Solver Controls**:
   - Time span
   - Solver method
   - Tolerances

4. **Time Evolution Plot**:
   - State trajectory
   - Probability evolution

5. **Warning**:
   - "Advisory mode. No control-system claim."

### 3.13 Experiments Lab

**Purpose**: Design and analyze quantum experiments.

**Features**:
1. **Tomography**:
   - State tomography
   - Process tomography

2. **Randomized Benchmarking**:
   - RB sequence generation
   - Analysis

3. **Calibration Data Viewer**:
   - If calibration data available

4. **Warning**:
   - "Offline-only. No hardware calibration claim."

### 3.14 Metal Lab

**Purpose**: Design superconducting qubit chips (advisory only).

**Features**:
1. **Chip Design Canvas**:
   - Qubit placement
   - Resonator placement
   - Coupler placement

2. **Component Library**:
   - Transmon qubits
   - CPW resonators
   - Couplers

3. **Renderer Status**:
   - GDS renderer (if available)
   - Simulation interface (if available)

4. **Export**:
   - Design metadata (JSON)
   - GDS file (if renderer available)

5. **Warning**:
   - "Advisory mode. No fabrication capability claim. No EM solver validation."

### 3.15 PennyLane Lab

**Purpose**: Work with PennyLane workflows.

**Features**:
1. **QNode Builder**:
   - Circuit definition
   - Device selection
   - Interface selection (NumPy, Torch, JAX, TensorFlow)

2. **Template Browser**:
   - Browse PennyLane templates
   - Insert into QNode

3. **QChem Workflow**:
   - Molecule definition
   - Hamiltonian generation

4. **Gradients**:
   - Gradient method selection
   - Parameter shift
   - Backprop

5. **Transforms**:
   - Apply transforms to QNode
   - Compile transforms

6. **Device Selector**:
   - default.qubit
   - lightning.qubit (if installed)
   - Other plugins (if installed)

7. **Result Schema**:
   - PennyLaneResult wrapper
   - Provenance tracking

### 3.16 Backend / Runtime Lab

**Purpose**: Manage backends and runtime jobs.

**Features**:
1. **Local Backends**:
   - QuantumBridge Simulator
   - Qiskit Aer (if installed)
   - Quafu (if installed)

2. **IBM Runtime Adapter**:
   - Adapter status (scaffold/Level 1)
   - No token storage
   - No real connection

3. **Job Monitor**:
   - List of jobs
   - Status (pending/running/completed/failed)
   - Results

4. **Backend Properties**:
   - Backend name
   - Number of qubits
   - Coupling map
   - Basis gates
   - Error rates

5. **Warning**:
   - "No token storage. Offline only."

### 3.17 Result Center

**Purpose**: View and manage all results from jobs.

**Features**:
1. **Result List**:
   - All results
   - Filter by: job type, status, date

2. **Result Detail View**:
   - JSON schema viewer
   - Provenance information
   - Warnings

3. **Export**:
   - Export as JSON
   - Export as CSV (if applicable)

4. **Reproducibility**:
   - View job parameters
   - View circuit
   - View seed
   - Rerun job

5. **Compare Runs**:
   - Select two results
   - Side-by-side comparison

### 3.18 Documentation / Code Generator

**Purpose**: Generate code and documentation from workflows.

**Features**:
1. **Workflow → Python**:
   - Generate Python script
   - Option: QuantumBridge / Qiskit / PennyLane

2. **Workflow → Notebook**:
   - Generate Jupyter notebook
   - Include markdown cells with explanations

3. **Workflow → CLI**:
   - Generate CLI script
   - Argument parsing

4. **API Docs**:
   - Browse API documentation
   - Search by function name

5. **Examples**:
   - Example workflows
   - Copy-paste ready

6. **Tutorials**:
   - Interactive tutorials
   - Step-by-step guides

---

## 4. User Flows

### 4.1 Beginner Flow: Build and Run a Bell State

1. Open Home Dashboard
2. Click "Bell State" in Quick Start
3. Circuit Builder opens with pre-built Bell State circuit
4. Click "Run" button
5. Select simulator (default: QuantumBridge Statevector)
6. View results in Simulator Lab (histogram)
7. Click "Export as Python" to get code
8. Copy code to clipboard

### 4.2 Intermediate Flow: VQE for H2

1. Open Chemistry Lab
2. Select "H2" from molecule library
3. Select basis (STO-3G)
4. Select driver (PySCF, if installed)
5. Click "Generate Hamiltonian"
6. View Hamiltonian in Hamiltonian Viewer
7. Click "Run VQE"
8. Algorithms Lab opens with VQE configured
9. Select optimizer (COBYLA)
10. Click "Run"
11. View convergence plot
12. View minimum energy
13. Click "Export as Notebook"

### 4.3 Advanced Flow: Custom Circuit + Transpilation

1. Open Circuit Builder
2. Drag gates to build custom circuit
3. Click "Compile"
4. Compiler Lab opens
5. Select passes (layout → routing → optimization)
6. Click "Compile"
7. View before/after comparison
8. Click "Run on Aer"
9. Select noise model
10. Run simulation
11. View results with noise

---

## 5. Data Schemas

### 5.1 Result Schema

All results in QuantumBridge Studio must conform to the QuantumBridge Result schema:

```json
{
  "job_id": "string",
  "job_type": "circuit | algorithm | chemistry | optimization | ml",
  "status": "pending | running | completed | failed",
  "created_at": "ISO 8601 timestamp",
  "completed_at": "ISO 8601 timestamp | null",
  "backend": {
    "name": "string",
    "version": "string",
    "provider": "QuantumBridge | Qiskit | PennyLane"
  },
  "input": {
    "circuit": "JSON representation",
    "parameters": "dict"
  },
  "output": {
    "counts": "dict | null",
    "statevector": "array | null",
    "probabilities": "dict | null",
    "eigenvalue": "float | null",
    "optimal_parameters": "array | null"
  },
  "provenance": {
    "upstream_package": "string",
    "upstream_version": "string",
    "adapter_name": "string",
    "adapter_level": "0 | 1 | 2 | 3",
    "official_endorsement": false
  },
  "warnings": ["string"],
  "metadata": {}
}
```

### 5.2 Workflow Schema

Workflows are serializable representations of user actions:

```json
{
  "workflow_id": "string",
  "name": "string",
  "created_at": "ISO 8601 timestamp",
  "steps": [
    {
      "step_id": "string",
      "step_type": "build_circuit | compile | run | analyze",
      "input": {},
      "output": {},
      "config": {}
    }
  ],
  "export_options": {
    "python_quantumbridge": true,
    "python_qiskit": false,
    "python_pennylane": false,
    "qasm": true
  }
}
```

---

## 6. Technical Constraints

### 6.1 Frontend Constraints

- Must be web-based (browser)
- No installation required (except backend server)
- Responsive design (desktop priority, mobile secondary)
- Accessible (WCAG 2.1 AA)

### 6.2 Backend Constraints

- Must run locally (no cloud dependency for MVP)
- Must not store tokens or secrets
- Must respect optional dependency status
- Must fail gracefully when dependencies missing

### 6.3 Performance Constraints

- Circuit rendering: < 100ms for 50 qubits
- Job submission: < 1s for small circuits
- Result visualization: < 500ms for 10k shots

### 6.4 Security Constraints

- No arbitrary code execution from UI
- No external network calls (except optional: data providers)
- No persistent storage of sensitive data
- All results are local

---

## 7. Success Metrics

### 7.1 User Engagement

- Daily Active Users (DAU)
- Time spent per session
- Number of jobs submitted
- Number of workflows exported

### 7.2 Technical Quality

- Test coverage > 80%
- Zero critical security vulnerabilities
- Lighthouse score > 90
- Accessibility score > 90

### 7.3 User Satisfaction

- NPS score > 50
- User feedback rating > 4.0/5.0
- Feature request vs. bug report ratio < 0.5

---

## 8. Roadmap

| Phase | Timeline | Milestones |
|---|---|---|
| **UI-0** | Week 1-2 | Product spec, IA, wireframes, API contract |
| **UI-1** | Week 3-4 | Read-only Ecosystem Explorer |
| **UI-2** | Week 5-8 | Circuit Builder + QASM Lab + Simulator Lab |
| **UI-3** | Week 9-12 | Chemistry Lab + Algorithms Lab |
| **UI-4** | Week 13-16 | Finance/Optimization/ML Labs |
| **UI-5** | Week 17-20 | Backend/Runtime/Result Center |
| **UI-6** | Week 21-24 | Team features, cloud integration, productization |

---

## 9. Open Questions

1. **Monaco vs. CodeMirror** for QASM editor?
2. **React Flow vs. custom canvas** for Circuit Builder?
3. **FastAPI vs. Flask** for backend?
4. **SQLite vs. Postgres** for result storage?
5. **Docker sandbox for user code execution?**
6. **Real-time collaboration (multi-user editing)?**
7. **Version control integration (Git)?**

---

## 10. Appendix

### 10.1 Glossary

| Term | Definition |
|---|---|
| **Level 0** | Inventory only (public API names) |
| **Level 1** | Passthrough (import and expose upstream object) |
| **Level 2** | Adapter (convert to QuantumBridge schema) |
| **Level 3** | Native subset (independent implementation) |
| **Scaffold** | Framework without actual implementation |

### 10.2 References

- [QuantumBridge SDK Documentation](../README.md)
- [Full Ecosystem Coverage Policy](../compat/full_ecosystem_coverage_policy_v0.1.md)
- [Qiskit Documentation](https://qiskit.org/documentation/)
- [PennyLane Documentation](https://pennylane.ai/qml/)

---

**Document Version**: v0.1
**Last Updated**: 2026-06-06
**Author**: OpenClaw (QuantumBridge 24-hour R&D Chief of Staff)
