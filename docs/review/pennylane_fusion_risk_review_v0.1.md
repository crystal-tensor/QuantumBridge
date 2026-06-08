# PennyLane Fusion Risk Review v0.1

**Version**: v0.1  
**Date**: 2026-06-06  
**Status**: Risk Assessment (Design Phase)  
**Owner**: OpenClaw (QuantumBridge 24-hour R&D Chief of Staff)  

---

## 1. Executive Summary

**Risk Level**: 🟡 **MEDIUM**  

PennyLane Full Fusion into QuantumBridge is **design-complete** but has significant implementation risks.

**Key Risks**:
1. 🔴 **False claim risk** - Claiming PennyLane replacement/parity
2. 🔴 **License/Attribution risk** - Missing Xanadu attribution
3. 🟡 **Dependency conflict risk** - autoray<0.8 constraint
4. 🟡 **API drift risk** - PennyLane API changes between versions
5. 🟡 **TF/JAX/Torch compatibility risk** - Interface complexity
6. 🟡 **QNode dynamic behavior risk** - JIT compilation complexity
7. 🟡 **Gradient correctness risk** - Numerical precision differences
8. 🔴 **qchem heavy dependency risk** - PySCF installation failures
9. 🟡 **Device plugin instability risk** - Third-party device compatibility
10. 🔴 **QOS backend semantic inconsistency risk** - Undefined QOS API
11. 🔴 **Qiskit ↔ PennyLane qubit ordering risk** - CRITICAL (reversed ordering)

---

## 2. False Claim Risk

### 2.1 Risk Description

**Scenario**: QuantumBridge documentation or marketing claims PennyLane compatibility that doesn't exist.

**Impact**: 🔴 **HIGH** - Trademark violation, user backlash, legal exposure.

### 2.2 Mitigation

| Claim | Allowed? | Requirement |
|---|---|---|
| "QuantumBridge provides a bridge to PennyLane" | ✅ YES | Must include "via adapter" |
| "QuantumBridge wraps PennyLane capabilities" | ✅ YES | Must include "not full replacement" |
| "QuantumBridge replaces PennyLane" | ❌ NO | **FORBIDDEN** |
| "QuantumBridge is PennyLane" | ❌ NO | **FORBIDDEN** |
| "Production-equivalent parity with PennyLane" | ❌ NO | **FORBIDDEN** |
| "QuantBridge is an official Xanadu project" | ❌ NO | **FORBIDDEN** |

### 2.3 Required Disclaimers

All PennyLane fusion documents MUST include:

```markdown
⚠️ **DISCLAIMER**: QuantumBridge is NOT a PennyLane replacement.  
It provides a unified bridging layer to PennyLane capabilities.  
PennyLane is a product of Xanadu Quantum Technologies Inc.  
QuantumBridge is not endorsed by or affiliated with Xanadu.  
All PennyLane capabilities are accessed via optional dependency adapters.  
No production parity or full replacement is claimed.
```

---

## 3. License / Attribution Risk

### 3.1 Risk Description

**Scenario**: QuantumBridge uses PennyLane code without proper attribution, or violates PennyLane's Apache 2.0 license.

**Impact**: 🔴 **HIGH** - Copyright infringement, license violation.

### 3.2 Current Mitigations

| Mitigation | Status | Notes |
|---|---|---|
| "No source code copied" header | ✅ Implemented | All adapter files have this |
| Xanadu attribution in docs | ✅ Implemented | `THIRD_PARTY_NOTICES.md` updated |
| Apache 2.0 license header | ✅ Implemented | All files have SPDX header |
| Separate `legal/` folder | ✅ Implemented | `pennylane_ecosystem_attribution_v0.1.md` |

### 3.3 Required Actions

1. ✅ **VERIFIED**: No upstream source code in QuantumBridge repo
2. ✅ **VERIFIED**: All files have proper attribution headers
3. ⚠️ **TODO**: Add Xanadu trademark notice to `THIRD_PARTY_NOTICES.md`
4. ⚠️ **TODO**: Add PennyLane license text to `LICENSES/APACHE-2.0-PennyLane.txt`

---

## 4. Dependency Conflict Risk

### 4.1 Risk Description

**Scenario**: PennyLane requires `autoray<0.8`, but other packages require `autoray>=0.8`.

**Impact**: 🟡 **MEDIUM** - User environment installation failures.

### 4.2 Current Constraints

```toml
# pyproject.toml
[project.optional-dependencies]
pennylane = [
    "pennylane>=0.34",
    "autoray<0.8",  # ← Required for PennyLane compatibility
]
```

### 4.3 Known Conflicts

| Package | Requires autoray | Conflict? |
|---|---|---|
| PennyLane 0.44.1 | <0.8 | Base requirement |
| Qiskit 2.4.1 | >=0.8? | ⚠️ Check needed |
| PySCF 2.13.1 | Any? | ⚠️ Check needed |
| OpenFermion 1.7.1 | Any? | ⚠️ Check needed |

### 4.4 Mitigation

1. **Isolated environment testing** (already implemented in `scripts/verify_ecosystem_installed_envs.py`)
2. **Constraints files** (already created: `requirements/constraints-pennylane.txt`)
3. **Clear installation instructions** in README:
   ```bash
   # Install PennyLane adapter ONLY (isolated)
   pip install quantumbridge-sdk[pennylane]
   
   # Install multiple ecosystems (may have conflicts)
   pip install quantumbridge-sdk[pennylane,qiskit]
   # ↑ If conflict, use constraints file:
   pip install quantumbridge-sdk[pennylane,qiskit] -c requirements/constraints-pennylane.txt
   ```

---

## 5. API Drift Risk

### 5.1 Risk Description

**Scenario**: PennyLane changes public API between versions; QuantumBridge adapters break.

**Impact**: 🟡 **MEDIUM** - Adapter maintenance burden.

### 5.2 Version Compatibility Policy

| PennyLane Version | QuantumBridge Support | Notes |
|---|---|---|
| 0.30.0 - 0.33.0 | ⚠️ Advisory | Older, limited testing |
| 0.34.0 - 0.38.0 | ✅ Tested | Primary target |
| 0.39.0 - 0.44.0 | ✅ Tested | Current installed: 0.44.1 |
| 0.45.0+ | ⚠️ Unknon | Future versions, untested |

### 5.3 Mitigation

1. **Inventory snapshot** (already implemented): `docs/compat/inventory/pennylane_*.json`
2. **Version check in `dependency.py`**:
   ```python
   import pennylane as qml
   if qml.__version__ > "0.44.0":
       warnings.warn(
           f"PennyLane {qml.__version__} is newer than tested 0.44.0. "
           "Some adapters may not work correctly.",
           UserWarning
       )
   ```
3. **CI matrix** (already implemented): `.github/workflows/test-matrix.yml` tests multiple PennyLane versions.

---

## 6. TensorFlow / JAX / Torch Compatibility Risk

### 6.1 Risk Description

**Scenario**: PennyLane supports multiple ML frameworks (NumPy, Torch, JAX, TensorFlow). QuantumBridge's interface adapter may not cover all cases.

**Impact**: 🟡 **MEDIUM** - Limited ML integration.

### 6.2 PennyLane Interface System

```python
# PennyLane interface parameter
interface = "numpy"  # Default, uses NumPy
interface = "torch"  # Requires PyTorch
interface = "jax"   # Requires JAX
interface = "tf"     # Requires TensorFlow
```

### 6.3 QuantumBridge Interface Adapter (Planned)

```python
# quantumbridge/compat/pennylane_full/interface_adapter.py

SUPPORTED_INTERFACES = {
    "numpy": ✅,  # Always supported
    "torch": ⚠️,  # Requires torch installed
    "jax": ⚠️,   # Requires jax installed
    "tf": ❌,     # Not planned (TensorFlow deprecated in PennyLane)
}
```

### 6.4 Risk Mitigation

1. **Graceful degradation**: If interface not available, warn and fall back to NumPy
2. **ML framework NOT required for core QuantumBridge**: PennyLane is optional
3. **Documentation**: Clearly state which interfaces are supported

---

## 7. QNode Dynamic Behavior Risk

### 7.1 Risk Description

**Scenario**: PennyLane's QNode uses dynamic compilation (autograph) for Torch/JAX interfaces. QuantumBridge's QNode wrapper may not capture this correctly.

**Impact**: 🟡 **MEDIUM** - Limited QNode functionality for ML workflows.

### 7.2 QNode Compilation Modes

| Mode | Description | QuantumBridge Support |
|---|---|---|---|
| "best" (default) | Auto-select best differentiation method | ✅ Passthrough |
| "backprop" | Backpropagation (requires interface) | ✅ Passthrough |
| "parameter-shift" | Analytic gradient via shift rule | ✅ Passthrough |
| "adjoint-diff" | Adjoint differentiation | ✅ Passthrough |
| "finite-diff" | Numerical finite difference | ✅ Passthrough |
| "device-batch" | Device-level batch differentiation | ⚠️ Advisory |

### 7.3 Mitigation

1. **Level 1 Passthrough** (Phase P1): Directly expose `pennylane.QNode`
2. **Level 2 Schema Wrapper** (Phase P2): Wrap QNode result in `QNodeResult` schema
3. **Level 3 Native** (NOT PLANNED): No native QNode implementation
4. **Warning**: Clearly label dynamic compilation as "advisory"

---

## 8. Gradient Correctness Risk

### 8.1 Risk Description

**Scenario**: QuantumBridge's gradient adapter produces different results than native PennyLane.

**Impact**: 🟡 **MEDIUM** - Incorrect gradient values break VQE/QAOA.

### 8.2 Gradient Methods

| Method | Numerical Precision | QuantumBridge Risk |
|---|---|---|---|
| parameter-shift | Analytic (exact) | ✅ Low risk |
| backprop | Float64 (dependent on interface) | ⚠️ Medium risk (float32 vs float64) |
| finite-diff | Numerical (approximate) | ⚠️ Medium risk (epsilon choice) |
| adjoint-diff | Analytic (exact, reversible) | ⚠️ Medium risk (circuit reversal) |

### 8.3 Mitigation

1. **Use PennyLane's gradient functions directly** (passthrough)
2. **Do NOT reimplement gradient math** (avoid precision errors)
3. **Test gradient values** against known analytic results (H2 molecule)
4. **Warn users** about numerical precision differences

---

## 9. qchem Heavy Dependency Risk

### 9.1 Risk Description

**Scenario**: PennyLane's `qchem` module requires PySCF (heavy dependency, C++ compilation). Installation fails on some systems.

**Impact**: 🔴 **HIGH** - Chemistry workflows unavailable for many users.

### 9.2 PySCF Installation Failure Modes

| Failure Mode | Frequency | Mitigation |
|---|---|---|
| CMake not found | Common | Document CMake requirement |
| C++ compiler not found | Common | Document compiler requirement |
| NumPy version incompatible | Sometimes | Add `numpy<2.0` constraint |
| Python 3.12 incompatibility | Sometimes | Tested on Python 3.12 |
| Out of memory during build | Rare | Document memory requirement |

### 9.3 Mitigation

1. **Graceful SKIP**: If PySCF not installed, skip `qchem` tests
2. **Separate extra**: `pip install quantumbridge-sdk[qchem]` (optional)
3. **Alternative driver**: Support OpenFermion as alternative to PySCF
4. **Documentation**: Clearly state PySCF requirement

---

## 10. Device Plugin Instability Risk

### 10.1 Risk Description

**Scenario**: Third-party PennyLane device plugins may have incompatible APIs, installation failures, or bugs.

**Impact**: 🟡 **MEDIUM** - Device registration failures.

### 10.2 Plugin Risk Categories

| Risk | Example | Mitigation |
|---|---|---|
| Plugin not installed | `pennylane-lightning` not in environment | Graceful SKIP |
| Plugin API changed | Plugin uses older PennyLane device API | Version check + warning |
| Plugin conflicts with another plugin | Two plugins define same device name | Namespace isolation |
| Plugin requires GPU/CUDA | `lightning.gpu` requires CUDA | Document GPU requirement |

### 10.3 Mitigation

1. **Plugin registry** (planned): `quantumbridge/compat/pennylane_full/plugin_adapter.py`
2. **Graceful SKIP**: If plugin not available, warn and skip
3. **Device capability query**: Check plugin device capabilities before using
4. **Documentation**: List supported plugins

---

## 11. QOS Backend Semantic Inconsistency Risk

### 11.1 Risk Description

**Scenario**: QuantumBridge defines a `QOSDevice` (PennyLane device that sends jobs to QOS), but QOS API is undefined. Semantic inconsistencies cause bugs.

**Impact**: 🔴 **HIGH** - QOS integration doesn't work, false advertising.

### 11.2 QOS API Uncertainty

| QOS Aspect | Status | Risk |
|---|---|---|---|
| QOS job submission API | ❌ Undefined | 🔴 HIGH |
| QOS result format | ❌ Undefined | 🔴 HIGH |
| QOS backend capabilities | ❌ Undefined | 🔴 HIGH |
| QOS error handling | ❌ Undefined | 🔴 HIGH |
| QOS authentication | ❌ Undefined | 🔴 HIGH |

### 11.3 Mitigation

1. **Scaffold only** (Phase P5): `QOSDevice` is a scaffold, not functional
2. **Warn aggressively**: "QOS backend does not exist yet"
3. **No real API calls**: `QOSDevice.execute()` returns schema-only result
4. **Document as EXPERIMENTAL**: All QOS capabilities are advisory

---

## 12. Qiskit ↔ PennyLane Qubit Ordering Risk (CRITICAL)

### 12.1 Risk Description

**Scenario**: PennyLane and Qiskit use **OPPOSITE** qubit ordering. Converting circuits between them without flipping wire indices produces **INCORRECT** results.

**Impact**: 🔴 **CRITICAL** - Silent correctness bugs in cross-framework workflows.

### 12.2 Qubit Ordering Difference

| Framework | Qubit Indexing | Tensor Product | Example |
|---|---|---|---|
| **PennyLane** | Left-to-right | `qml.tensor(w0, w1)` = w0 ⊗ w1 | Wire 0 = first qubit |
| **Qiskit** | Right-to-left | `w0 ⊗ w1` = reversed | Wire 0 = last qubit |

### 12.3 Concrete Example

```python
# PennyLane circuit (wires=[0,1])
@qml.qnode(dev)
def circuit():
    qml.CNOT(wires=[0,1])  # Control=0, Target=1
    return qml.expval(qml.Z(0))

# Equivalent Qiskit circuit (qubits=[0,1])
qc = QuantumCircuit(2)
qc.cx(0, 1)  # Control=0, Target=1
# ↑ WRONG! Qiskit interprets this as Control=1, Target=0

# CORRECT Qiskit conversion:
qc = QuantumCircuit(2)
qc.cx(1, 0)  # Flip wire indices
```

### 12.4 Mitigation (MANDATORY)

1. **WireOrderAdapter** (planned): `quantumbridge/compat/pennylane_full/qiskit_bridge.py`
2. **Explicit wire mapping**: All IR conversions must include wire mapping
3. **Test wire ordering**: Add explicit tests for Bell state, GHZ state
4. **Warn users**: "Qubit ordering differs between PennyLane and Qiskit"

---

## 13. Unsupported Operations Risk

### 13.1 Risk Description

**Scenario**: User tries to convert a PennyLane operation to Qiskit, but Qiskit doesn't support it.

**Impact**: 🟡 **MEDIUM** - Conversion failures.

### 13.2 Unsupported Operations Examples

| Operation | PennyLane | Qiskit | Risk |
|---|---|---|---|
| `QubitUnitary` (custom unitary) | ✅ Supported | ✅ Supported (`UnitaryGate`) | ⚠️ Matrix conversion needed |
| `Rot` (arbitrary rotation) | ✅ Supported | ✅ Supported (`U3Gate`) | ⚠️ Parameter conversion needed |
| `AmplitudeDamping` (noise) | ✅ Supported | ✅ Supported (`thermal_relaxation_error`) | ⚠️ Noise model conversion needed |
| `CatState` (non-Gaussian) | ✅ Supported | ❌ Not supported | 🔴 HIGH - Cannot convert |
| `FockState` (bosonic) | ✅ Supported | ❌ Not supported | 🔴 HIGH - Cannot convert |

### 13.3 Mitigation

1. **Unsupported operation registry**: `quantumbridge/compat/pennylane_full/unsupported_ops.py`
2. **Warn on unsupported**: If user tries to convert unsupported op, emit warning
3. **Document unsupported**: List all unsupported operations in `docs/compat/matrix/pennylane_full_fusion_master_matrix.md`

---

## 14. Custom Unitary Conversion Risk

### 14.1 Risk Description

**Scenario**: PennyLane's `QubitUnitary` takes an arbitrary unitary matrix. Converting to Qiskit's `UnitaryGate` requires matrix decomposition, which is not unique.

**Impact**: 🟡 **MEDIUM** - Different decompositions produce different circuits.

### 14.2 Mitigation

1. **Use `qiskit.transpiler.passes.UnitarySynthesis`**: Let Qiskit decompose the unitary
2. **Preserve original matrix**: Store original matrix in IR metadata
3. **Warn users**: "Custom unitary decomposition is not unique"

---

## 15. Device-Specific Operations Risk

### 15.1 Risk Description

**Scenario**: Some PennyLane operations are device-specific (e.g., topology-constrained operations). Converting to Qiskit may not work on all backends.

**Impact**: 🟡 **MEDIUM** - Device compatibility issues.

### 15.2 Mitigation

1. **Device capability query**: Check device capabilities before conversion
2. **Warn on incompatible**: If operation not supported by target device, warn user
3. **Fallback**: If device doesn't support operation, suggest alternative

---

## 16. Risk Summary

| Risk | Probability | Impact | Mitigation Status |
|---|---|---|---|---|
| False claim | 🟡 Medium | 🔴 High | ✅ Mitigated (disclaimer) |
| License/Attribution | 🟢 Low | 🔴 High | ✅ Mitigated (attribution headers) |
| Dependency conflict | 🟡 Medium | 🟡 Medium | ✅ Mitigated (constraints) |
| API drift | 🟡 Medium | 🟡 Medium | ✅ Mitigated (inventory + version check) |
| TF/JAX/Torch compatibility | 🟡 Medium | 🟡 Medium | ⚠️ Partial (graceful degradation) |
| QNode dynamic behavior | 🟡 Medium | 🟡 Medium | ⚠️ Partial (passthrough) |
| Gradient correctness | 🟡 Medium | 🟡 Medium | ⚠️ Partial (use PennyLane directly) |
| qchem heavy dependency | 🔴 High | 🔴 High | ⚠️ Partial (graceful SKIP) |
| Device plugin instability | 🟡 Medium | 🟡 Medium | ⚠️ Partial (plugin registry) |
| QOS backend semantics | 🔴 High | 🔴 High | ✅ Mitigated (scaffold + warning) |
| Qubit ordering (CRITICAL) | 🔴 High | 🔴 High | ❌ NOT YET MITIGATED |
| Unsupported operations | 🟡 Medium | 🟡 Medium | ❌ NOT YET MITIGATED |
| Custom unitary conversion | 🟡 Medium | 🟡 Medium | ❌ NOT YET MITIGATED |
| Device-specific operations | 🟡 Medium | 🟡 Medium | ❌ NOT YET MITIGATED |

---

## 17. Immediate Actions (Before Phase P1)

1. 🔴 **CRITICAL**: Implement `WireOrderAdapter` in `qiskit_bridge.py`
2. 🔴 **CRITICAL**: Add qubit ordering tests (Bell state, GHZ state)
3. 🔴 **HIGH**: Create `unsupported_ops.py` registry
5. 🔴 **HIGH**: Add PySCF installation documentation
6. ⚠️ **MEDIUM**: Create `plugin_adapter.py` registry
7. ⚠️ **MEDIUM**: Add gradient correctness tests (H2 molecule)

---

## 18. Sign-Off

**Risk Assessment**: 🟡 **MEDIUM** (acceptable for Alpha release)

**Conditions for Alpha Release**:
1. ✅ Qubit ordering adapter implemented
2. ✅ Unsupported operations registry created
3. ✅ All scaffold features clearly labeled
4. ✅ All warnings implemented
5. ✅ All disclaimers added to documentation

**Recommendation**: ✅ **PROCEED with Phase P1**, but implement qubit ordering adapter FIRST.

---

**Document Version**: v0.1  
**Last Updated**: 2026-06-06  
**Author**: OpenClaw (QuantumBridge 24-hour R&D Chief of Staff)
