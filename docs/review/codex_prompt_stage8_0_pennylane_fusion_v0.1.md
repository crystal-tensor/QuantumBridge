# Codex Prompt: Stage 8.0 PennyLane Full Fusion Implementation

**Date**: 2026-06-06  
**From**: OpenClaw (QuantumBridge 24-hour R&D Chief of Staff)  
**To**: Codex (Code Implementation Agent)  

---

## Context

You are working on **QuantumBridge SDK Stage 8.0 PennyLane Full Fusion**.

**Current branch**: `p2/pennylane-full-fusion` (create if not exists)  
**Base commit**: d43eff1 (Stage 7.4 merge readiness gate)  
**Goal**: Implement Phase P1 (Passthrough) for PennyLane Full Fusion.

**Critical constraints**:
1. ❌ DO NOT copy PennyLane source code
2. ❌ DO NOT vendor `pennylane/`, `site-packages/`, `wheel/`, `dist-info/`, `egg-info/`
3. ✅ PennyLane is **optional dependency only**
4. ❌ DO NOT claim "QuantumBridge is PennyLane official project"
5. ❌ DO NOT claim "full PennyLane replacement"
6. ❌ DO NOT claim "production-equivalent parity"
7. ✅ All capabilities MUST be labeled by Level (0-4)
8. ✅ All results MUST include provenance
9. ✅ Must be compatible with Qiskit interop
10. ✅ Must be compatible with QOS/QuantumOS (experimental)

---

## Your Task: Phase P1 (Passthrough - Batch 1)

### P1.1: Infrastructure

**Files to create**:

#### 1. `quantumbridge/compat/pennylane_full/__init__.py`

```python
# This file is independently implemented for QuantumBridge SDK.
# No source code from PennyLane or Xanadu was copied.
"""QuantumBridge PennyLane Full Fusion Adapter."""

from .dependency import dependency_available, get_version
from .inventory import list_public_apis
from .warnings import warn_scaffold, warn_advisory, warn_experimental

__all__ = [
    "dependency_available",
    "get_version",
    "list_public_apis",
    "warn_scaffold",
    "warn_advisory",
    "warn_experimental",
]
```

#### 2. `quantumbridge/compat/pennylane_full/dependency.py`

```python
# This file is independently implemented for QuantumBridge SDK.
# No source code from PennyLane or Xanadu was copied.
"""PennyLane dependency check."""

import warnings

def dependency_available() -> bool:
    """Check if pennylane is installed."""
    try:
        import pennylane  # noqa: F401
        return True
    except ImportError:
        return False

def get_version() -> str:
    """Get installed pennylane version."""
    try:
        import pennylane as qml
        return qml.__version__
    except ImportError:
        return "not_installed"

def require_pennylane(func_name: str):
    """Decorator to require pennylane."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not dependency_available():
                warnings.warn(
                    f"Function '{func_name}' requires pennylane. "
                    "Install with: pip install quantumbridge-sdk[pennylane]",
                    UserWarning,
                    stacklevel=2
                )
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

#### 3. `quantumbridge/compat/pennylane_full/inventory.py`

```python
# This file is independently implemented for QuantumBridge SDK.
# No source code from PennyLane or Xanadu was copied.
"""PennyLane public API inventory loader."""

import json
import os

INVENTORY_DIR = os.path.join(
    os.path.dirname(__file__),
    "../../docs/compat/inventory"
)

def list_public_apis(module: str = "pennylane") -> list:
    """
    Load public API inventory for a PennyLane module.
    
    Args:
        module: Module name (e.g., "pennylane", "pennylane.operations")
    
    Returns:
        List of API names
    """
    inventory_file = os.path.join(
        INVENTORY_DIR,
        f"{module.replace('.', '_')}_inventory.json"
    )
    
    if not os.path.exists(inventory_file):
        return []
    
    with open(inventory_file, "r") as f:
        data = json.load(f)
        return data.get("inventory", [])
```

#### 4. `quantumbridge/compat/pennylane_full/warnings.py`

```python
# This file is independently implemented for QuantumBridge SDK.
# No source code from PennyLane or Xanadu was copied.
"""Centralized warnings for PennyLane fusion."""

import warnings

def warn_scaffold(feature_name: str):
    """Warn that a feature is scaffold only."""
    warnings.warn(
        f"{feature_name} is a SCAFFOLD adapter. "
        "Full implementation is not yet available. "
        "This adapter only provides the Result schema wrapper.",
        UserWarning,
        stacklevel=2
    )

def warn_advisory(feature_name: str, reason: str = ""):
    """Warn that a feature is advisory (not production)."""
    msg = f"{feature_name} is ADVISORY."
    if reason:
        msg += f" {reason}"
    msg += " Not for production use."
    warnings.warn(msg, UserWarning, stacklevel=2)

def warn_experimental(feature_name: str):
    """Warn that a feature is experimental."""
    warnings.warn(
        f"{feature_name} is EXPERIMENTAL. "
        "API may change. Use at your own risk.",
        UserWarning,
        stacklevel=2
    )

def warn_not_implemented(feature_name: str):
    """Warn that a feature is not implemented."""
    warnings.warn(
        f"{feature_name} is NOT IMPLEMENTED yet. "
        "See docs/roadmap/pennylane_fusion_execution_plan_v0.1.md",
        UserWarning,
        stacklevel=2
    )

def warn_qubit_ordering():
    """Warn about qubit ordering difference."""
    warnings.warn(
        "PennyLane and Qiskit have OPPOSITE qubit ordering. "
        "PennyLane wire 0 = Qiskit qubit (N-1). "
        "Wire indices are flipped during conversion.",
        UserWarning,
        stacklevel=2
    )

def warn_unsupported_operation(op_name: str, source: str = "PennyLane"):
    """Warn that an operation is not supported."""
    warnings.warn(
        f"Operation '{op_name}' from {source} is not supported in this adapter. "
        "Skipping or using passthrough.",
        UserWarning,
        stacklevel=2
    )
```

---

### P1.2: Operations Passthrough

**File to create**: `quantumbridge/compat/pennylane_full/operations_adapter.py`

```python
# This file is independently implemented for QuantumBridge SDK.
# No source code from PennyLane or Xanadu was copied.
"""PennyLane operations passthrough adapter."""

import warnings
from .dependency import dependency_available, require_pennylane
from .warnings import warn_scaffold, warn_unsupported_operation

# Level 1: Passthrough - import and expose PennyLane operations directly
SUPPORTED_GATES = [
    "H", "X", "Y", "Z",
    "RX", "RY", "RZ",
    "CNOT", "CZ", "SWAP",
    "CRX", "CRY", "CRZ",
    "PhaseShift", "U1", "U2", "U3",
    # ... 80 total
]

class OperationsAdapter:
    """PennyLane operations adapter (Level 1 passthrough)."""
    
    def __init__(self):
        warn_scaffold("OperationsAdapter")
        self._check_dependency()
    
    def _check_dependency(self):
        if not dependency_available():
            raise ImportError(
                "PennyLane not installed. "
                "Install with: pip install quantumbridge-sdk[pennylane]"
            )
    
    def get_gate(self, gate_name: str):
        """Get PennyLane gate function by name."""
        import pennylane as qml
        
        if gate_name not in SUPPORTED_GATES:
            warn_unsupported_operation(gate_name)
            return None
        
        return getattr(qml, gate_name, None)
    
    def list_gates(self) -> list:
        """List all supported gates."""
        return SUPPORTED_GATES.copy()

# Convenience function
def get_operations_adapter() -> OperationsAdapter:
    """Get operations adapter instance."""
    return OperationsAdapter()
```

---

### P1.3: Measurements Passthrough

**File to create**: `quantumbridge/compat/pennylane_full/measurements_adapter.py`

```python
# This file is independently implemented for QuantumBridge SDK.
# No source code from PennyLane or Xanadu was copied.
"""PennyLane measurements passthrough adapter."""

import warnings
from .dependency import dependency_available
from .warnings import warn_scaffold

SUPPORTED_MEASUREMENTS = [
    "state", "probs", "sample",
    "counts", "expval", "var",
    "density_matrix", "vn_entropy",
    "mutual_info", "classical_shadow",
    # ... 25 total
]

class MeasurementsAdapter:
    """PennyLane measurements adapter (Level 1 passthrough)."""
    
    def __init__(self):
        warn_scaffold("MeasurementsAdapter")
        self._check_dependency()
    
    def _check_dependency(self):
        if not dependency_available():
            raise ImportError("PennyLane not installed.")
    
    def get_measurement(self, meas_name: str):
        """Get PennyLane measurement function."""
        import pennylane as qml
        
        if meas_name not in SUPPORTED_MEASUREMENTS:
            warnings.warn(f"Measurement '{meas_name}' not supported.")
            return None
        
        return getattr(qml, meas_name, None)
    
    def list_measurements(self) -> list:
        """List all supported measurements."""
        return SUPPORTED_MEASUREMENTS.copy()
```

---

### P1.4: Device Passthrough

**File to create**: `quantumbridge/compat/pennylane_full/device_adapter.py`

```python
# This file is independently implemented for QuantumBridge SDK.
# No source code from PennyLane or Xanadu was copied.
"""PennyLane device passthrough adapter."""

import warnings
from .dependency import dependency_available
from .warnings import warn_scaffold, warn_advisory

SUPPORTED_DEVICES = [
    "default.qubit",
    "default.mixed",
    # "lightning.qubit",  # ⚠️ Advisory: requires CUDA
]

class DeviceAdapter:
    """PennyLane device adapter (Level 1 passthrough)."""
    
    def __init__(self):
        warn_scaffold("DeviceAdapter")
        self._check_dependency()
    
    def _check_dependency(self):
        if not dependency_available():
            raise ImportError("PennyLane not installed.")
    
    def create_device(self, device_name: str, wires: int, **kwargs):
        """Create PennyLane device."""
        import pennylane as qml
        
        if device_name not in SUPPORTED_DEVICES:
            warnings.warn(f"Device '{device_name}' not in supported list.")
        
        if device_name == "lightning.qubit":
            warn_advisory(
                "lightning.qubit",
                "Requires CUDA. May fail on CPU-only systems."
            )
        
        return qml.device(device_name, wires=wires, **kwargs)
    
    def list_devices(self) -> list:
        """List all supported devices."""
        return SUPPORTED_DEVICES.copy()
```

---

## Action Items (Execute in Order)

### Step 1: Create Branch

```bash
cd /Users/avalok/work/QuantumBridge
git checkout -b p2/pennylane-full-fusion
git push -u origin p2/pennylane-full-fusion
```

### Step 2: Create Adapter Files

Create these files (use code skeletons above):
1. `quantumbridge/compat/pennylane_full/__init__.py`
2. `quantumbridge/compat/pennylane_full/dependency.py`
3. `quantumbridge/compat/pennylane_full/inventory.py`
4. `quantumbridge/compat/pennylane_full/warnings.py`
5. `quantumbridge/compat/pennylane_full/operations_adapter.py`
6. `quantumbridge/compat/pennylane_full/measurements_adapter.py`
7. `quantumbridge/compat/pennylane_full/device_adapter.py`

### Step 3: Create Tests

Create test files:

#### `tests/compat_pennylane_full/test_dependency.py`

```python
import pytest
from quantumbridge.compat.pennylane_full.dependency import dependency_available, get_version

def test_dependency_available():
    """Test dependency check."""
    result = dependency_available()
    assert isinstance(result, bool)

def test_get_version():
    """Test version retrieval."""
    version = get_version()
    assert isinstance(version, str)
```

#### `tests/compat_pennylane_full/test_operations_passthrough.py`

```python
import pytest
from quantumbridge.compat.pennylane_full.operations_adapter import OperationsAdapter, SUPPORTED_GATES

@pytest.mark.skipif(
    not pytest.importorskip("pennylane"),
    reason="pennylane not installed"
)
def test_operations_adapter_init():
    """Test adapter initialization."""
    adapter = OperationsAdapter()
    assert adapter is not None

@pytest.mark.skipif(
    not pytest.importorskip("pennylane"),
    reason="pennylane not installed"
)
def test_list_gates():
    """Test listing gates."""
    adapter = OperationsAdapter()
    gates = adapter.list_gates()
    assert len(gates) > 0
    assert "H" in gates
```

#### `tests/compat_pennylane_full/test_measurements_passthrough.py`

```python
import pytest
from quantumbridge.compat.pennylane_full.measurements_adapter import MeasurementsAdapter, SUPPORTED_MEASUREMENTS

@pytest.mark.skipif(
    not pytest.importorskip("pennylane"),
    reason="pennylane not installed"
)
def test_measurements_adapter_init():
    """Test adapter initialization."""
    adapter = MeasurementsAdapter()
    assert adapter is not None

@pytest.mark.skipif(
    not pytest.importorskip("pennylane"),
    reason="pennylane not installed"
)
def test_list_measurements():
    """Test listing measurements."""
    adapter = MeasurementsAdapter()
    measurements = adapter.list_measurements()
    assert len(measurements) > 0
    assert "state" in measurements
```

### Step 4: Update `pyproject.toml`

Add PennyLane optional dependency:

```toml
[project.optional-dependencies]
pennylane = [
    "pennylane>=0.34",
    "autoray<0.8",  # Required for PennyLane
]
```

### Step 5: Run Tests

```bash
cd /Users/avalok/work/QuantumBridge
python -m pytest tests/compat_pennylane_full/ -v --tb=short
```

**Expected**: All tests PASS or SKIP (if PennyLane not installed).

### Step 6: Commit and Push

```bash
cd /Users/avalok/work/QuantumBridge
git add quantumbridge/compat/pennylane_full/ tests/compat_pennylane_full/
git add pyproject.toml
git commit -m "feat: add PennyLane Full Fusion P1 passthrough adapters

- Add dependency/inventory/warnings infrastructure
- Add operations/measurements/devices passthrough adapters
- Add tests for all adapters
- All adapters labeled as scaffold (warn_scaffold)
- PennyLane is optional dependency only
- No source code copied from PennyLane
- No vendorized packages
- Compatible with Qiskit interop (planned)
- Compatible with QOS/QuantumOS (experimental)

See docs/architecture/pennylane_fusion_architecture_v0.1.md"
git push origin p2/pennylane-full-fusion
```

---

## Acceptance Criteria (You Are Done When)

1. ✅ **ALL files created** (7 adapter files + 3 test files)
2. ✅ **ALL tests pass** (or skip gracefully if PennyLane not installed)
3. ✅ **ALL adapters have `warn_scaffold()`** (clear labeling)
4. ✅ **ALL warnings centralized** in `warnings.py`
5. ✅ **PennyLane is optional dependency** (install via `pip install quantumbridge-sdk[pennylane]`)
6. ✅ **NO source code copied** from PennyLane
7. ✅ **NO vendorized packages** (`site-packages/`, `wheel/`, etc.)
8. ✅ **Commit message references architecture doc**
9. ✅ **Branch pushed to remote**

---

## What NOT to Do (DO NOT)

1. ❌ Do NOT implement Level 2 (schema adapter) yet
2. ❌ Do NOT implement Level 3 (native subset) yet
3. ❌ Do NOT implement IR bridge (Tape ↔ IR ↔ Qiskit) yet
4. ❌ Do NOT implement QOS bridge (experimental) yet
5. ❌ Do NOT copy PennyLane source code
6. ❌ Do NOT vendor PennyLane packages
7. ❌ Do NOT claim production parity
8. ❌ Do NOT add UI implementation

---

## Next Steps After P1 (For Future Prompts)

**P2 (Schema Adapter)**:
- Implement `result_adapter.py` with `PennyLaneResult` schema
- Implement `qnode_adapter.py` schema wrapper
- Implement `tape_adapter.py` (Tape ↔ IR conversion)

**P3 (IR Bridge)**:
- Implement `qiskit_bridge.py` (PennyLane ↔ Qiskit conversion)
- Handle wire ordering difference (CRITICAL)

**P4 (QOS Bridge)**:
- Implement `qos_bridge.py` (scaffold only, experimental)

---

## Deliverables (What to Provide to OpenClaw)

When you finish, provide OpenClaw with:

1. ✅ **Commit hash** of your changes
2. ✅ **Test output** (showing all tests pass or skip)
3. ✅ **List of created files** (adapter files + test files)
4. ✅ **Confirmation** that no source code was copied
5. ✅ **Confirmation** that all adapters have `warn_scaffold()`

---

**End of Prompt**
