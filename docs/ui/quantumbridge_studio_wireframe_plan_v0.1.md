# QuantumBridge Studio Wireframe Plan v0.1

**Version**: v0.1 (Planning Stage)
**Date**: 2026-06-06
**Status**: Draft
**Owner**: OpenClaw (QuantumBridge 24-hour R&D Chief of Staff)

---

## 1. Overview

This document describes the **wireframe plan** for QuantumBridge Studio. It provides a structural blueprint for the UI layout, navigation, and component hierarchy.

---

## 2. Global Layout

### 2.1 Desktop Layout (Primary)

```
┌──────────────────────────────────────────────────────────────┐
│ [Logo] QuantumBridge Studio          [Settings] [Help] [User] │  ← Top Bar
├────────┬─────────────────────────────────────────────────────┤
│        │ [Breadcrumb: Home > Circuit Builder]                 │
│ [Nav]  ├────────────────────────────┬────────────────────────┤
│        │                            │                        │
│ 🏠 Home│    [Main Content Area]     │   [Right Panel]        │
│ 🌐 Eco│                            │   - Configuration      │
│ ⚡ Circ│                            │   - Parameters         │
│ 📝 QASM│                            │   - Properties         │
│ ⚙️ Comp│                           │                        │
│ 💻 Sim │                            │                        │
│ 🧪 Chem│                            │                        │
│ 🧠 Algo│                            │                        │
│ 💰 Fin │                            │                        │
│ 📊 Opt │                            │                        │
│ 🤖 ML  │                            │                        │
│ 🌊 Dyn │                            │                        │
│ 🔬 Exp │                            │                        │
│ 🔧 Meta│                            │                        │
│ 🎯 PL  │                            │                        │
│ 🖥️ Back│                            │                        │
│ 📈 Res │                            │                        │
│ 📚 Doc │                            │                        │
├────────┴────────────────────────────┴────────────────────────┤
│ [Status Bar: Job: Idle | Backend: QB Statevector | v0.1.0]  │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Mobile Layout (Secondary)

```
┌──────────────────────────────┐
│ [☰] QuantumBridge Studio [☰]│  ← Top Bar (collapsible)
├──────────────────────────────┤
│ [Tab: Circuit] [Tab: Sim]    │  ← Tab Navigation
├──────────────────────────────┤
│                              │
│   [Main Content Area]        │
│   (Full width)               │
│                              │
│                              │
├──────────────────────────────┤
│ [Run] [Save] [Export]        │  ← Action Bar
└──────────────────────────────┘
```

---

## 3. Wireframes by Module

### 3.1 Home Dashboard

```
┌─────────────────────────────────────────────────────┐
│ Home Dashboard                                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ ✅ Qiskit    │  │ ✅ PennyLane│  │ ⚠️ Aer      │ │
│  │ Core 2.4.1  │  │ 0.44.1     │  │ 0.17.2     │ │
│  │ L0✅ L1✅ L2✅│ │ L0✅ L1✅ L2✅│ │ L0✅ L1✅ L2⚠│ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ ❌ Finance  │  │ ❌ Optim    │  │ ❌ ML       │ │
│  │ Not Install│  │ Not Install│  │ Not Install│ │
│  │ L0✅ L1⬜ L2⬜│ │ L0✅ L1⬜ L2⬜│ │ L0✅ L1⬜ L2⬜│ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
│                                                     │
│  Recent Jobs                                         │
│  ┌────────────────────────────────────────────────┐ │
│  │ Bell State  | ✅ Completed | 2026-06-06 10:00│ │
│  │ VQE H2      | ⏳ Running    | 2026-06-06 09:30│ │
│  │ MaxCut 4    | ❌ Failed     | 2026-06-06 09:00│ │
│  └────────────────────────────────────────────────┘ │
│                                                     │
│  Quick Start                                        │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐    │
│  │Bell  │ │VQE   │ │QAOA  │ │Grover│ │GHZ   │    │
│  │State │ │H2    │ │3-Node│ │4-Qbit│ │State │    │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘    │
└─────────────────────────────────────────────────────┘
```

### 3.2 Ecosystem Explorer

```
┌─────────────────────────────────────────────────────┐
│ Ecosystem Explorer            [🔍 Search...      ] │
├──────────┬──────────────────────────────────────────┤
│ Tree     │ Function List                            │
│          │ ┌──────────────────────────────────────┐ │
│ ▼ Qiskit │ │ Name          | Level | Installed  │ │
│   ▼ Core │ │ QuantumCircuit | L1 ✅ | ✅         │ │
│     circ │ │ QuantumRegister| L1 ✅ | ✅         │ │
│     tran │ │ ClassicalReg.  | L1 ✅ | ✅         │ │
│     q_info│ │ ...                               │ │
│     prim │ ├──────────────────────────────────────┤ │
│   ▼ Aer  │ │ Detail: QuantumCircuit                │ │
│     sim  │ │ ┌──────────────────────────────────┐ │ │
│     noise│ │ │ qiskit.circuit.QuantumCircuit      │ │ │
│   ▼ Nat  │ │ │                                     │ │ │
│     driv │ │ │ Create a quantum circuit.            │ │ │
│     prob │ │ │                                     │ │ │
│   ▶ Algo │ │ │ [Generate Code] [Copy]             │ │ │
│   ▶ Fin  │ │ └──────────────────────────────────┘ │ │
│ ▼ PL     │                                          │
│   ▼ Ops │ │                                        │ │
│   ▶ Meas│ │                                        │ │
├──────────┴──────────────────────────────────────────┤
│ Filter: [Level 0] [Level 1] [Level 2] [Level 3]     │
│         [Installed] [Not Installed] [All]           │
└─────────────────────────────────────────────────────┘
```

### 3.3 Circuit Builder

```
┌─────────────────────────────────────────────────────┐
│ Circuit Builder                      [Run] [Save]    │
├──────┬──────────────────────────────────┬───────────┤
│ Gates│ Circuit Canvas                   │ Config    │
│      │                                  │           │
│ 1Q   │ q0 ──[H]──[RX(θ)]──[CX]──M──  │ Qubits: 3 │
│ [H]  │                  │              │ Bits: 2  │
│ [X]  │ q1 ───────────────┼──M───────  │           │
│ [Y]  │ q2 ───────────────[X]─────────  │ Params:   │
│ [Z]  │                                  │ θ = 0.0  │
│ [RX] │ c0 ══════════════════          │           │
│ [RY] │ c1 ══════════════════          │           │
│ [RZ] │                                  │ Depth: 3  │
│ [S]  │                                  │ Gates: 5  │
│ [T]  │                                  │ 2Q Gates:1│
│      │                                  │           │
│ 2Q   │                                  │ Export:   │
│ [CX] │                                  │ [QASM]    │
│ [CZ] │                                  │ [Python]  │
│ [SWAP│                                  │ [IR]      │
│      │                                  │           │
│ Meas │                                  │           │
│ [M]  │                                  │           │
├──────┴──────────────────────────────────┴───────────┤
│ Preview: OPENQASM 2.0;                              │
│ include "qelib1.inc";                                │
│ qreg q[3]; creg c[2];                                │
│ h q[0]; rx(0.0) q[0]; cx q[0],q[1]; measure q[0]; │
└─────────────────────────────────────────────────────┘
```

### 3.4 Simulator Lab

```
┌─────────────────────────────────────────────────────┐
│ Simulator Lab                         [Run] [Export]│
├──────────────────────────┬──────────────────────────┤
│ Circuit                  │ Configuration             │
│ ┌──────────────────────┐ │                           │
│ │ q0 ──[H]──[CX]──M── │ │ Simulator:               │
│ │ q1 ────────────[X]── │ │ [✅] QB Statevector      │
│ └──────────────────────┘ │ [ ] QB Density Matrix     │
│                          │ [ ] QB Sampler            │
│ Results                  │ [ ] Aer Simulator (✅)    │
│ ┌──────────────────────┐ │                           │
│ │ Histogram             │ │ Shots: [1024]            │
│ │ 00: ████████ 512     │ │ Seed:  [42]             │
│ │ 11: ████████ 512     │ │                           │
│ │ 01:                  │ │ Noise Model:             │
│ │ 10:                  │ │ [ ] None                  │
│ └──────────────────────┘ │ [ ] Depolarizing          │
│                          │     Error: [0.001]        │
│ Statevector              │                           │
│ |00⟩: 0.707 + 0.000i    │                           │
│ |11⟩: 0.000 + 0.707i    │ [▶ Run Simulation]        │
├──────────────────────────┴──────────────────────────┤
│ Status: ✅ Completed | Backend: QB Statevector      │
│         | Shots: 1024 | Duration: 0.003s            │
└─────────────────────────────────────────────────────┘
```

### 3.5 Chemistry Lab

```
┌─────────────────────────────────────────────────────┐
│ Chemistry Lab                    [Run] [Export]       │
├──────────────────────────┬──────────────────────────┤
│ Molecule Configuration    │ Hamiltonian Info          │
│                          │                           │
│ Molecule: [H2 ▼]        │ Terms: 4                  │
│ XYZ Input:               │ Qubits: 2                 │
│ H  0.0  0.0  0.37       │ Pauli:                    │
│ H  0.0  0.0 -0.37       │ II + ... + ZZ             │
│                          │                           │
│ Basis: [STO-3G ▼]       │ ─────────────────────     │
│ Charge: [0]              │ Energy Curve              │
│ Spin: [1]                │ Energy                     │
│                          │  -1.15 ──●               │
│ Driver:                  │  -1.10 ──                 │
│ [✅] PySCF (✅)          │  -1.05 ──                 │
│ [ ] Qiskit Nature (✅)   │  -1.00 ──                 │
│ [ ] OpenFermion (❌)     │  0.7 0.8 0.9 1.0          │
│                          │       Bond Length          │
│ Mapping:                 │                           │
│ [JW ▼]  Jordan-Wigner   │ ─────────────────────     │
│ [ ] Parity              │ Solver:                   │
│ [ ] Bravyi-Kitaev       │ [VQE ▼]                   │
│                          │ Ansatz: [UCCSD ▼]         │
│ ⚠️ Experimental chem    │ Optimizer: [COBYLA ▼]     │
│ Not for production use   │ Max iter: [100]           │
├──────────────────────────┴──────────────────────────┤
│ [▶ Generate Hamiltonian] [▶ Run VQE] [Export Notebook]│
└─────────────────────────────────────────────────────┘
```

### 3.6 Algorithms Lab

```
┌─────────────────────────────────────────────────────┐
│ Algorithms Lab                      [Run] [Export]     │
├──────────────────────────┬──────────────────────────┤
│ Algorithm Setup          │ Results                    │
│                          │                           │
│ Algorithm:               │ Status: ✅ Completed      │
│ [VQE ▼]                  │ Duration: 12.3s            │
│                          │                           │
│ Hamiltonian Source:      │ Minimum Eigenvalue:        │
│ [Manual Input ▼]         │ E = -1.137                 │
│ [ ] Chemistry Lab        │                           │
│ [ ] File Upload           │ Optimal Parameters:        │
│                          │ θ₀ = 0.123                │
│ Pauli Strings:           │ θ₁ = 0.456                │
│ II: 0.5, XZ: -0.5, ... │                           │
│                          │ Convergence:               │
│ Ansatz:                  │ Energy                    │
│ [EfficientSU2 ▼]         │  0 ──●                     │
│ Reps: [2]                │ -0.5 ──●──●                │
│                          │ -1.0 ──●──●──●             │
│ Optimizer:               │ -1.5 ───────────           │
│ [COBYLA ▼]               │ 0   5   10   15 20        │
│                          │       Iteration            │
│ Max Iterations: [200]    │                           │
│ Convergence Tol: [1e-6]  │                           │
├──────────────────────────┴──────────────────────────┤
│ [▶ Run Algorithm] [Export as Python] [Export Notebook]│
└─────────────────────────────────────────────────────┘
```

### 3.7 Result Center

```
┌─────────────────────────────────────────────────────┐
│ Result Center              [Compare] [Delete]        │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Filter: [All] [Circuit] [Algorithm] [Chem] [Opt]   │
│ Status: [All] [Completed] [Failed] [Running]       │
│                                                     │
│ ┌────────────────────────────────────────────────┐ │
│ │ ID          │ Type      │ Status  │ Date        │ │
│ │ job_001     │ circuit   │ ✅      │ 2026-06-06  │ │
│ │ job_002     │ algorithm│ ✅      │ 2026-06-06  │ │
│ │ job_003     │ chemistry│ ⏳      │ 2026-06-06  │ │
│ └────────────────────────────────────────────────┘ │
│                                                     │
│ ──────── Selected: job_001 ────────                 │
│                                                     │
│ Result Schema:                                      │
│ {                                                   │
│   "job_id": "job_001",                              │
│   "status": "completed",                            │
│   "backend": { "name": "QB Statevector" },         │
│   "output": { "counts": {"00": 512, "11": 512} }   │
│   "provenance": {                                   │
│     "upstream_package": null,                       │
│     "adapter_name": "quantumbridge_native",         │
│     "adapter_level": 3,                            │
│     "official_endorsement": false                   │
│   }                                                 │
│ }                                                   │
│                                                     │
│ [Export JSON] [Rerun] [View Circuit]                 │
└─────────────────────────────────────────────────────┘
```

---

## 4. Component Hierarchy

### 4.1 Reusable Components

| Component | Description | Used In |
|---|---|---|
| **CoverageBadge** | Shows Level 0/1/2/3 with color | Ecosystem Explorer, Home |
| **StatusBadge** | Shows Installed/Scaffold/Not Available | Home, Ecosystem Explorer |
| **CoverageLevelLegend** | Explains Level 0-4 | Ecosystem Explorer footer |
| **HistogramChart** | Counts visualization | Simulator Lab, Result Center |
| **BlochSphere** | Single-qubit state | Simulator Lab |
| **ConvergencePlot** | Energy/loss vs iteration | Algorithms Lab, Chemistry Lab |
| **CircuitCanvas** | Drag-drop circuit builder | Circuit Builder |
| **CodeEditor** | Monaco-based code editor | QASM Lab |
| **ASTViewer** | Tree view of parsed QASM | QASM Lab |
| **PassPipelineView** | Visual pass manager | Compiler Lab |
| **MoleculeViewer** | 3D molecule visualization | Chemistry Lab |
| **HamiltonianViewer** | Pauli string display | Chemistry Lab, Algorithms Lab |
| **ChipDesignCanvas** | Qubit/coupler placement | Metal Lab |
| **BackendPropertiesTable** | Backend info table | Backend/Runtime Lab |
| **ProvenanceCard** | Shows upstream source info | Result Center, all Labs |
| **WarningBanner** | "Not production" warning | Finance Lab, ML Lab, etc. |
| **ExportMenu** | Dropdown: Python/QASM/JSON/Notebook | All Labs |
| **JobStatusBar** | Bottom bar with job status | All Labs |
| **BreadcrumbNav** | Navigation path | All pages |

### 4.2 Component Props (Key Examples)

**CoverageBadge**:
```typescript
interface CoverageBadgeProps {
  level: 0 | 1 | 2 | 3 | 4;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}
```

**StatusBadge**:
```typescript
interface StatusBadgeProps {
  status: 'installed' | 'scaffold' | 'not-available' | 'advisory' | 'unsupported';
  showLabel?: boolean;
}
```

**WarningBanner**:
```typescript
interface WarningBannerProps {
  message: string;
  type: 'experimental' | 'advisory' | 'not-production' | 'no-fabrication';
  dismissible?: boolean;
}
```

---

## 5. Interaction Patterns

### 5.1 Drag-and-Drop (Circuit Builder)

```
[Gate Palette] --drag--> [Circuit Canvas]
  User drags gate icon    Gate appears on selected qubit track
  from left panel         at drop position
```

### 5.2 Code Generation Flow

```
[User clicks "Generate Code"]
  ↓
[Backend receives request]
  ↓
[QuantumBridge IR generated from visual circuit]
  ↓
[IR converted to Python code]
  ↓
[Python code displayed in code editor]
  ↓
[User copies or exports]
```

### 5.3 Simulation Flow

```
[User clicks "Run"]
  ↓
[Frontend validates circuit]
  ↓
[API request to backend]
  ↓
[Backend executes via QuantumBridge adapter]
  ↓
[Result stored in result store]
  ↓
[Frontend polls/fetches result]
  ↓
[Result displayed in visualization]
```

### 5.4 Filter/Search Flow

```
[User types in search box]
  ↓
[Frontend filters function list in real-time]
  ↓
[User clicks on function]
  ↓
[Detail panel shows function info]
  ↓
[User clicks "Generate Code"]
  ↓
[Code displayed]
```

---

## 6. Responsive Behavior

| Screen Width | Layout | Navigation |
|---|---|---|
| > 1200px | Full 3-column (sidebar + main + config) | Left sidebar always visible |
| 768-1200px | 2-column (main + config) | Sidebar collapsible |
| < 768px | Single column | Bottom tab navigation |

---

## 7. Accessibility

| Element | ARIA | Keyboard |
|---|---|---|
| Navigation links | `aria-label`, `aria-current` | Tab, Enter |
| Gate palette | `role="toolbar"`, `aria-label` | Arrow keys, Enter |
| Circuit canvas | `role="application"`, `aria-roledescription` | Arrow keys, Space |
| Coverage badges | `aria-label="Level 2 Adapter"` | Tab |
| Status badges | `aria-label="Installed"` | Tab |
| Warning banners | `role="alert"` | Tab, Escape to dismiss |
| Charts | SVG with `aria-label`, `role="img"` | Tab to navigate |
| Code editor | Monaco's built-in accessibility | Standard editor shortcuts |

---

## 8. Design Tokens

### 8.1 Color System

```css
:root {
  /* Coverage Levels */
  --level-0: #9CA3AF; /* Gray - Inventory */
  --level-1: #60A5FA; /* Blue - Passthrough */
  --level-2: #34D399; /* Green - Adapter */
  --level-3: #FBBF24; /* Gold - Native */
  --level-4: #F87171; /* Red - Not promised */

  /* Status */
  --status-installed: #34D399;
  --status-scaffold: #FBBF24;
  --status-not-available: #9CA3AF;
  --status-advisory: #FB923C;
  --status-unsupported: #F87171;

  /* Action */
  --primary: #3B82F6;
  --danger: #EF4444;
  --success: #10B981;
  --warning: #F59E0B;
}
```

### 8.2 Typography

```css
:root {
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-display: 'Inter', system-ui, sans-serif;
}
```

### 8.3 Spacing

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
}
```

---

## 9. Animation & Transitions

| Interaction | Animation | Duration |
|---|---|---|
| Page transition | Fade + slide | 200ms |
| Sidebar collapse | Width transition | 300ms ease |
| Gate drag | Drop shadow + scale | 150ms |
| Result display | Fade in | 300ms |
| Warning banner | Slide down | 200ms |
| Loading spinner | Rotate | 1s linear infinite |
| Histogram bar | Grow from bottom | 500ms ease-out |

---

## 10. Error States

| Error | Display | Recovery |
|---|---|---|
| Package not installed | Yellow banner + StatusBadge(❌) | Link to install docs |
| Circuit invalid | Red border + error message | Fix in Circuit Builder |
| Simulation failed | Red result card + error message | Fix circuit, retry |
| Backend unavailable | Red banner | Switch backend |
| Token required | Red banner | "QuantumBridge does not store tokens" |

---

**Document Version**: v0.1
**Last Updated**: 2026-06-06
**Author**: OpenClaw (QuantumBridge 24-hour R&D Chief of Staff)
