# PennyLane Fusion Execution Plan v0.1

**Version**: v0.1  
**Date**: 2026-06-06  
**Owner**: OpenClaw (QuantumBridge 24-hour R&D Chief of Staff)  

---

## Overview

Phased execution plan for PennyLane Full Fusion into QuantumBridge.

**Constraint**: PennyLane is optional dependency only. No source code copying. No vendor packages.

---

## Phase P0: Inventory (DONE ✅)

**Status**: Completed in Stage 7.2  
**Deliverable**: 444 PennyLane APIs inventoried in `docs/compat/inventory/pennylane_*.json`

### Acceptance Criteria
- [x] All PennyLane modules inventoried
- [x] JSON format with function name, module, signature
- [x] Total API count documented

---

## Phase P1: Passthrough

**Goal**: Import and re-expose PennyLane functions through QuantumBridge entry points  
**Level**: Level 1  
**Effort**: 2-3 days (Codex)  
**Blockers**: None

### P1.1: Core Infrastructure

| Task | File | Description | Acceptance |
|---|---|---|---|
| Dependency check | `dependency.py` | Check if pennylane installed, version, interfaces | `dependency_available()` returns bool |
| Top-level init | `__init__.py` | Re-export core APIs via `from quantumbridge.compat.pennylane_full import qnode, device, execute` | Import works |
| Inventory loader | `inventory.py` | Load inventory JSON, provide `list_public_apis(module)` | Returns API list |
| Warnings module | `warnings.py` | Centralized warning messages for PennyLane fusion | `warn_scaffold()`, `warn_advisory()` |

### P1.2: Operations Passthrough

| Task | File | Description | Acceptance |
|---|---|---|---|
| Gate registry | `operations_adapter.py` | Map 80 PennyLane gates → QuantumBridge Op enum | All standard gates mapped |
| Observable registry | `observables_adapter.py` | Map 30 PennyLane observables | Z, X, Y, Hamiltonian mapped |
| Measurement registry | `measurements_adapter.py` | Map 25 measurement types | state, probs, expval, counts mapped |
| Custom op passthrough | `operations_adapter.py` | Allow user-defined operations | Custom ops work |

### P1.3: Core Modules Passthrough

| Task | File | Description | Acceptance |
|---|---|---|---|
| QNode wrapper | `qnode_adapter.py` | Wrap `pennylane.qnode` with warning | `@qnode()` decorator works |
| Device factory | `device_adapter.py` | Wrap `pennylane.device` with warning | `device("default.qubit")` works |
| Tape passthrough | `tape_adapter.py` | Re-export QuantumScript | `QuantumScript` accessible |
| Template registry | `templates_adapter.py` | Re-export 40+ templates | Template names listed |
| Math/Numpy | `math_adapter.py` | Re-export pennylane.math | Math functions accessible |

### P1.4: Tests

| Task | File | Description | Acceptance |
|---|---|---|---|
| Dependency test | `test_pennylane_dependency.py` | Test `dependency_available()` | PASS or SKIP |
| Operations test | `test_pennylane_operations.py` | Test gate passthrough | 30+ gates work |
| QNode test | `test_pennylane_qnode.py` | Test QNode wrapper | Bell state works |
| Device test | `test_pennylane_device.py` | Test device factory | default.qubit works |
| Template test | `test_pennylane_templates.py` | Test template list | All templates listed |

### P1 Acceptance Criteria
- [ ] All 80 standard gates accessible via QuantumBridge
- [ ] QNode decorator works and produces correct results
- [ ] Device factory works for default.qubit
- [ ] All tests PASS or SKIP gracefully
- [ ] Warnings emitted for scaffold features
- [ ] No source code copied from PennyLane
- [ ] PennyLane remains optional dependency

---

## Phase P2: Schema Adapter

**Goal**: Convert PennyLane results to QuantumBridge schema  
**Level**: Level 2  
**Effort**: 3-4 days (Codex)  
**Blockers**: P1 must complete first  
**Dependencies**: `quantumbridge/schema/pennylane_results.py`

### P2.1: Result Schema

| Task | File | Description | Acceptance |
|---|---|---|---|
| Base schema | `schema/pennylane_results.py` | PennyLaneResult dataclass | Validated fields |
| QNode result | `schema/pennylane_results.py` | QNodeResult subclass | Includes provenance |
| Measurement result | `schema/pennylane_results.py` | MeasurementResult | Counts, probs, state |
| Gradient result | `schema/pennylane_results.py` | GradientResult | Gradient values |
| QChem result | `schema/pennylane_results.py` | QChemResult | Hamiltonian data |
| QNN result | `schema/pennylane_results.py` | QNNResult | Predictions |
| Device result | `schema/pennylane_results.py` | DeviceResult | Capabilities |
| Serialization | `schema/pennylane_results.py` | to_dict/to_json/from_dict | Round-trip works |

### P2.2: Result Wrappers

| Task | File | Description | Acceptance |
|---|---|---|---|
| QNode wrapper | `qnode_adapter.py` | Wrap QNode result in QNodeResult schema | Provenance included |
| Measurement wrapper | `measurements_adapter.py` | Wrap measurement in MeasurementResult | Correct data mapping |
| Gradient wrapper | `gradients_adapter.py` | Wrap gradient in GradientResult | Method tagged |
| Transform wrapper | `transforms_adapter.py` | Wrap transform in TransformResult | Transform chain logged |
| QChem wrapper | `qchem_adapter.py` | Wrap chemistry result | Hamiltonian included |
| QNN wrapper | `qnn_adapter.py` | Wrap QML result | Predictions included |
| Template wrapper | `templates_adapter.py` | Wrap template circuit | Template name tagged |
| Resource wrapper | `resource_adapter.py` | Wrap resource estimate | Gate count, depth |

### P2.3: IR Bridge

| Task | File | Description | Acceptance |
|---|---|---|---|
| Tape → IR | `tape_adapter.py` | `tape_to_ir()` function | All ops mapped |
| IR → Tape | `tape_adapter.py` | `ir_to_tape()` function | Round-trip correct |
| IR dataclass | `tape_adapter.py` | `QuantumBridgeIR` definition | Validated |

### P2.4: Specialized Adapters

| Task | File | Description | Acceptance |
|---|---|---|---|
| Gradient adapter | `gradients_adapter.py` | param_shift, backprop, finite_diff | 3 methods work |
| Transform adapter | `transforms_adapter.py` | compile, cancel_inverses, merge_rot | 5 transforms work |
| QChem adapter | `qchem_adapter.py` | molecular_hamiltonian, hf_state | H2 workflow works |
| QAOA adapter | `qaoa_adapter.py` | QAOA cost/ansatz layers | MaxCut works |
| QNN adapter | `qnn_adapter.py` | SamplerQNN, EstimatorQNN | Basic QNN works |
| Kernel adapter | `kernels_adapter.py` | QuantumKernel, kernel_matrix | Kernel computed |
| IO adapter | `io_adapter.py` | Save/load circuits | Round-trip works |
| Interface adapter | `interface_adapter.py` | NumPy/Torch/JAX/TF detection | Interface detected |
| Resource adapter | `resource_adapter.py` | Gate count, depth, wire count | Resources estimated |
| Plugin adapter | `plugin_adapter.py` | List available plugins | Plugin names listed |

### P2.5: Tests

| Task | File | Description | Acceptance |
|---|---|---|---|
| Result schema test | `test_pennylane_result_schema.py` | Test all 12 result types | PASS |
| IR round-trip test | `test_pennylane_tape_ir.py` | Tape → IR → Tape | Correct |
| Gradient test | `test_pennylane_gradients.py` | Test 3 gradient methods | Correct values |
| Transform test | `test_pennylane_transforms.py` | Test 5 transforms | Correct output |
| QChem test | `test_pennylane_qchem.py` | Test H2 workflow | Correct energy |
| QNN test | `test_pennylane_qnn.py` | Test basic QNN | Predictions valid |
| Provenance test | `test_pennylane_provenance.py` | All results have provenance | Fields populated |
| Serialization test | `test_pennylane_serialization.py` | to_json/from_dict round-trip | Correct |

### P2 Acceptance Criteria
- [ ] All 12 result types implemented
- [ ] All results include provenance
- [ ] All results include warnings (if applicable)
- [ ] Tape → IR → Tape round-trip correct
- [ ] Gradient methods return correct values
- [ ] 5 transform methods work
- [ ] H2 chemistry workflow produces correct energy
- [ ] All tests PASS or SKIP gracefully
- [ ] No source code copied

---

## Phase P3: IR Bridge

**Goal**: Full IR conversion between PennyLane ↔ Qiskit  
**Level**: Level 2-3  
**Effort**: 2-3 days (Codex)  
**Blockers**: P2 must complete first  
**Dependencies**: `qiskit_bridge.py`

### P3.1: PennyLane ↔ Qiskit Bridge

| Task | File | Description | Acceptance |
|---|---|---|---|
| Wire order adapter | `qiskit_bridge.py` | Handle wire ordering difference | Both directions correct |
| Op name mapping | `qiskit_bridge.py` | PennyLane op → Qiskit gate | 50+ ops mapped |
| Measurement mapping | `qiskit_bridge.py` | PennyLane measurement → Qiskit | Counts, probs mapped |
| Parameter binding | `qiskit_bridge.py` | Parameters preserved across conversion | Correct values |
| Custom unitary | `qiskit_bridge.py` | QubitUnitary → UnitaryGate | Matrix preserved |
| PennyLane → Qiskit | `qiskit_bridge.py` | Full circuit conversion | Circuit equivalent |
| Qiskit → PennyLane | `qiskit_bridge.py` | Full circuit conversion | Circuit equivalent |
| Hamiltonian bridge | `qiskit_bridge.py` | PennyLane Hamiltonian ↔ Qiskit SparsePauliOp | Correct mapping |
| Observable bridge | `qiskit_bridge.py` | PennyLane Observable ↔ Qiskit Pauli | Correct mapping |
| Unsupported op handling | `qiskit_bridge.py` | Warn for unsupported ops | Warning emitted |

### P3.2: Tests

| Task | File | Description | Acceptance |
|---|---|---|---|
| Wire order test | `test_wire_order.py` | Test both directions | Correct |
| Op mapping test | `test_op_mapping.py` | Test 50+ ops | Correct |
| Round-trip test | `test_qiskit_roundtrip.py` | PL → QBIR → Qiskit → QBIR → PL | Correct |
| Hamiltonian test | `test_hamiltonian_bridge.py` | PL Hamiltonian → Qiskit SparsePauliOp | Correct |
| Measurement test | `test_measurement_bridge.py` | PL measurement → Qiskit | Correct |
| Unsupported test | `test_unsupported_ops.py` | Test warning for unsupported | Warning emitted |

### P3 Acceptance Criteria
- [ ] 50+ ops mapped between PennyLane ↔ Qiskit
- [ ] Wire ordering correct both directions
- [ ] Parameter binding preserved
- [ ] Hamiltonian conversion correct
- [ ] All unsupported ops emit warnings
- [ ] All tests PASS or SKIP

---

## Phase P4: Qiskit Bridge

**Goal**: Full cross-framework compatibility  
**Level**: Level 2-3  
**Effort**: 1-2 days (Codex)  
**Blockers**: P3 must complete first

### P4.1: End-to-End Scenarios

| Scenario | Description | Acceptance |
|---|---|---|
| PL QNode → Qiskit Circuit | Convert PennyLane circuit to Qiskit | Circuit equivalent |
| Qiskit Circuit → PL QNode | Convert Qiskit circuit to PennyLane | QNode executable |
| PL Hamiltonian → Qiskit | Convert to SparsePauliOp | Correct |
| Qiskit SparsePauliOp → PL | Convert to PennyLane Observable | Correct |
| PL gradient → Qiskit | Gradient info preserved | Gradient values match |
| Shared optimizer | Use PennyLane optimizer with Qiskit circuit | Converges |

### P4 Acceptance Criteria
- [ ] 6 end-to-end scenarios work
- [ ] No data loss in conversion
- [ ] Provenance preserved across frameworks

---

## Phase P5: QOS Bridge

**Goal**: Experimental QOS bridge for PennyLane  
**Level**: Level 0-1  
**Effort**: 1 day (Codex)  
**Blockers**: None (scaffold only)  
**Status**: ⚠️ EXPERIMENTAL

### P5.1: QOS Bridge (Scaffold Only)

| Task | File | Description | Acceptance |
|---|---|---|---|
| QOSDevice scaffold | `qos_bridge.py` | Scaffold QOS device | Class exists, warns |
| IR → QOS job | `qos_bridge.py` | Scaffold conversion | Function exists, warns |
| QOS result schema | `qos_bridge.py` | Scaffold result wrapper | Class exists, warns |
| Capability reporting | `qos_bridge.py` | Scaffold capabilities() | Returns empty dict |

### P5 Acceptance Criteria
- [ ] QOSDevice class exists
- [ ] Warnings emitted: "EXPERIMENTAL", "QOS backend not implemented"
- [ ] No real QOS API calls
- [ ] All scaffold features clearly labeled

---

## Phase P6: UI Readiness

**Goal**: Prepare for QuantumBridge Studio integration  
**Level**: Planning only  
**Effort**: 1 day (OpenClaw)  
**Blockers**: P2 must complete first

### P6.1: UI Design Documents

| Document | Description | Acceptance |
|---|---|---|
| API Explorer spec | PennyLane API browser | Document exists |
| QNode Builder spec | Visual QNode builder | Document exists |
| Template Browser spec | Template gallery | Document exists |
| Gradient Lab spec | Gradient visualization | Document exists |
| QChem Lab spec | Chemistry workflow | Document exists |
| QNN Lab spec | ML workflow | Document exists |
| Device Selector spec | Device comparison | Document exists |
| PL ↔ Qiskit Converter | Cross-framework converter | Document exists |
| Result Viewer spec | Unified result viewer | Document exists |

### P6 Acceptance Criteria
- [ ] 9 UI design documents exist
- [ ] All documents clearly label "planning only, no implementation"
- [ ] No UI code written

---

## Phase Dependencies

```
P0 (Inventory) ──► P1 (Passthrough) ──► P2 (Schema) ──► P3 (IR Bridge) ──► P4 (Qiskit Bridge)
                                                                          │
P5 (QOS Scaffold) ◄─────────────────────────────────────────────────────────┘
                                                                          │
P6 (UI Planning) ◄────────────────────────────────────────────────────────┘
```

---

## Timeline Estimate

| Phase | Effort | Duration | Dependencies |
|---|---|---|---|
| P0 | Codex | ✅ DONE | None |
| P1 | Codex | 2-3 days | P0 |
| P2 | Codex | 3-4 days | P1 |
| P3 | Codex | 2-3 days | P2 |
| P4 | Codex | 1-2 days | P3 |
| P5 | Codex | 1 day | P2 (scaffold) |
| P6 | OpenClaw | 1 day | P2 (planning) |
| **Total** | | **10-14 days** | Sequential |

---

## Blocked Items

| Item | Blocker | Resolution |
|---|---|---|
| PR #2 merge | Scaffold warnings not added | Codex: add warnings first |
| QOS backend | Does not exist | Scaffold only, no real API |
| PennyLane Catalyst JIT | Different compilation model | Not supported |
| Lightning GPU | Requires CUDA | Advisory only |

---

**Document Version**: v0.1  
**Last Updated**: 2026-06-06  
**Author**: OpenClaw (QuantumBridge 24-hour R&D Chief of Staff)
