# Prompt for Codex - Stage 7.2 Next Actions

**Date**: 2026-06-06
**From**: OpenClaw (QuantumBridge 24-hour R&D Chief of Staff)
**To**: Codex (Code Implementation Agent)

---

## Context

You are working on **QuantumBridge SDK Stage 7.2 Full Function Installed Coverage Expansion**.

**Current branch**: `p2/ecosystem-full-coverage-planning`
**Current status**:
- ✅ Level 0 (Inventory) ~95% complete
- ✅ Level 1 (Passthrough scaffold) created for all ecosystem packages
- ✅ Level 2 (Result Adapter scaffold) created for all ecosystem packages
- ❌ **BLOCKER**: Test failures in `qiskit-experiments` and `qiskit-addons`
- ⚠️ **WARNING**: Many adapters are scaffolds without clear labeling

**Your mission**: Fix blockers, clearly label scaffolds, and prepare for PR split.

---

## Task 1: Fix Test Failures (🔴 Critical - Do TODAY)

### Problem

2 test files are failing:

1. **`tests/compat_qiskit_experiments/test_experiments_availability.py`**
   - Test: `test_qiskit_experiments_dependency_inventory_and_version`
   - Test: `test_qiskit_experiments_public_classes_or_clear_error`
   - **Error**: `assert list_public_api_inventory()` returns empty list

2. **`tests/compat_qiskit_addons/test_addons_availability.py`**
   - Test: `test_qiskit_addons_dependency_inventory_and_version`
   - Test: `test_qiskit_addons_imports_or_clear_errors`
   - **Error**: `assert list_public_api_inventory()` returns empty list

### Root Cause (Hypothesis)

The inventory scripts (`scripts/inventory_qiskit_experiments_api.py`, `scripts/inventory_qiskit_addons_api.py`) are not correctly generating the inventory JSON files.

### Your Actions

1. **Debug inventory script for `qiskit-experiments`**:
   ```bash
   cd /Users/avalok/work/QuantumBridge
   python scripts/inventory_qiskit_experiments_api.py
   ```
   - Check if `docs/compat/inventory/qiskit_experiments_inventory.json` is created
   - Check if the JSON file is non-empty
   - Check if `list_public_api_inventory()` can read it

2. **Debug inventory script for `qiskit-addons`**:
   ```bash
   cd /Users/avalok/work/QuantumBridge
   python scripts/inventory_qiskit_addons_api.py
   ```
   - Same checks as above

3. **Fix the inventory scripts** so they generate valid, non-empty JSON files.

4. **Run tests again**:
   ```bash
   pytest -q -rs tests/compat_qiskit_experiments/ tests/compat_qiskit_addons/
   ```
   - Expected: All tests PASS or SKIP (not FAIL)

5. **If package not installed**, test should SKIP with reason:
   ```python
   @pytest.mark.skipif(not EXPERIMENTS.dependency_available(), reason="qiskit-experiments not installed")
   def test_qiskit_experiments_dependency_inventory_and_version():
       ...
   ```

---

## Task 2: Clearly Label Scaffolds (🔴 Critical - Do TODAY)

### Problem

Many adapter files in `quantumbridge/compat/*/` are **scaffolds** (empty frameworks) but are not clearly labeled. This may mislead users into thinking they have full functionality.

### Files to Update

Add `warnings.warn()` to these scaffold adapters:

1. **`quantumbridge/compat/qiskit_finance/result_adapter.py`**
2. **`quantumbridge/compat/qiskit_finance/applications_adapter.py`**
3. **`quantumbridge/compat/qiskit_machine_learning/result_adapter.py`**
4. **`quantumbridge/compat/qiskit_machine_learning/dataset_adapter.py`**
5. **`quantumbridge/compat/qiskit_machine_learning/regressor_adapter.py`**
6. **`quantumbridge/compat/qiskit_optimization/result_adapter.py`**
7. **`quantumbridge/compat/qiskit_optimization/applications_adapter.py`**
8. **`quantumbridge/compat/qiskit_dynamics/result_adapter.py`**
9. **`quantumbridge/compat/qiskit_experiments/result_adapter.py`**
10. **`quantumbridge/compat/qiskit_experiments/rb_adapter.py`**
11. **`quantumbridge/compat/qiskit_metal/result_adapter.py`**
12. **`quantumbridge/compat/qiskit_nature/result_adapter.py`** (partially implemented, label as "partial")

### Example Fix

```python
# At top of result_adapter.py
import warnings
warnings.warn(
    f"This {__file__} is a SCAFFOLD adapter. "
    "Full implementation is not yet available. "
    "This adapter only provides the Result schema wrapper.",
    UserWarning,
    stacklevel=2
)
```

### Your Actions

1. Add `warnings.warn("Scaffold adapter...")` to ALL scaffold adapters listed above.
2. For partially implemented adapters (like `qiskit_nature/result_adapter.py`), use:
   ```python
   warnings.warn("Partial adapter - some features may not work", UserWarning)
   ```
3. Commit changes with message: `fix: clearly label scaffold adapters with warnings`.

---

## Task 3: Verify Inventory JSON Files (🔴 Critical - Do TODAY)

### Problem

Some inventory JSON files in `docs/compat/inventory/*.json` may be:
- Empty (`[]` or `{}`)
- Malformed (invalid JSON)
- Missing required fields

### Your Actions

1. **Run ALL inventory scripts**:
   ```bash
   cd /Users/avalok/work/QuantumBridge
   python scripts/inventory_qiskit_core_api.py
   python scripts/inventory_qiskit_aer_api.py
   python scripts/inventory_qiskit_finance_api.py
   python scripts/inventory_qiskit_optimization_api.py
   python scripts/inventory_qiskit_machine_learning_api.py
   python scripts/inventory_qiskit_nature_api.py
   python scripts/inventory_qiskit_algorithms_api.py
   python scripts/inventory_qiskit_dynamics_api.py
   python scripts/inventory_qiskit_experiments_api.py
   python scripts/inventory_qiskit_metal_api.py
   python scripts/inventory_qiskit_addons_api.py
   python scripts/inventory_pennylane_full_api.py
   ```

2. **Check all generated JSON files** are non-empty:
   ```bash
   ls -la docs/compat/inventory/*.json
   # Every file should be >100 bytes
   ```

3. **Validate JSON format** (optional but recommended):
   ```bash
   python -c "
   import json, os
   inv_dir = 'docs/compat/inventory'
   for f in os.listdir(inv_dir):
       if f.endswith('.json'):
           with open(os.path.join(inv_dir, f)) as fp:
               data = json.load(fp)
               assert 'inventory' in data or isinstance(data, list), f'{f} missing inventory key'
   print('All inventory JSONs valid')
   "
   ```

4. **Commit any fixes** to inventory scripts or JSON files.

---

## Task 4: Update `__init__.py` Exports (🔴 Critical - Do TODAY)

### Problem

New adapter modules (like `quantumbridge/compat/qiskit_algorithms/result_adapter.py`) may not be exported in their `__init__.py`, causing import errors.

### Your Actions

1. **Check all `__init__.py` files** in `quantumbridge/compat/*/` exist and export adapters:
   ```bash
   cat quantumbridge/compat/qiskit_algorithms/__init__.py
   cat quantumbridge/compat/qiskit_finance/__init__.py
   cat quantumbridge/compat/qiskit_machine_learning/__init__.py
   # ... etc.
   ```

2. **If `__init__.py` is missing or incomplete**, update it to export the adapter classes. Example:
   ```python
   # quantumbridge/compat/qiskit_algorithms/__init__.py
   from .result_adapter import AlgorithmsResult
   from .eigensolver_adapter import EigensolverAdapter
   # ... other adapters
   ```

3. **Test imports**:
   ```bash
   cd /Users/avalok/work/QuantumBridge
   python -c "
   from quantumbridge.compat.qiskit_algorithms import AlgorithmsResult
   print('Import successful')
   "
   ```

4. **Commit fixes** to `__init__.py` files.

---

## Task 5: Update README to Clearly Label Scaffolds (🟡 Warning - Do This Week)

### Problem

Current `README.md` says:
> "Level 2 Adapter: selected upstream objects convert into QuantumBridge schemas"

But for many packages, Level 2 is just a **scaffold** without actual conversion functionality.

### Your Actions

1. **Edit `README.md`** to add a clear warning table:

```markdown
## ⚠️ Scaffold Advisory

The following adapters are **scaffolds only** (Level 1 Passthrough + Level 2 Result Schema wrapper).
They do NOT perform full input conversion, behavioral parity, or production-equivalent functionality.

| Package | Adapter Status | Notes |
|---|---|---|
| qiskit-finance | 🟡 Scaffold | Result schema only |
| qiskit-optimization | 🟡 Scaffold | Result schema only |
| qiskit-machine-learning | 🟡 Scaffold | Result schema only |
| qiskit-dynamics | 🟡 Scaffold | Result schema only |
| qiskit-experiments | 🟡 Scaffold | Result schema only |
| qiskit-metal | 🟡 Scaffold | Result schema only |

**Installed & partially implemented**:
- qiskit-aer ✅ (Result schema works)
- qiskit-nature ✅ (ChemistryResult works)
- qiskit-algorithms ✅ (AlgorithmsResult works)
- pennylane-full ✅ (PennyLaneResult works)
```

2. **Commit README update** with message: `docs: clearly label scaffold adapters in README`.

---

## Task 6: Split Stage 7 into Separate PRs (🟡 Warning - Do This Week)

### Problem

Stage 7 scope is too large (full ecosystem coverage). It should be split into smaller, focused PRs.

### Your Actions (Coordinate with OpenClaw)

1. **OpenClaw will create separate branches**:
   - `p2/ecosystem-qiskit-core-aer` (Qiskit Core + Aer)
   - `p2/ecosystem-finance-optimization-ml` (Finance + Optimization + ML)
   - `p2/ecosystem-dynamics-experiments-metal` (Dynamics + Experiments + Metal)
   - `p2/ecosystem-pennylane-full` (PennyLane Full)
   - `p2/ui-planning` (UI docs)
   - `p2/issue-backlog` (Issue backlog)

2. **You (Codex) will cherry-pick commits** into appropriate branches.

3. **Create separate PRs** for each branch.

---

## Task 7: Add More Tests (🟢 Advisory - Do Next Week)

### Problem

Many ecosystem packages have **skip tests** (because package not installed) but no **actual functionality tests** for installed packages.

### Your Actions

1. **For installed packages** (qiskit-aer, qiskit-nature, qiskit-algorithms, pennylane):
   - Add tests that actually **call the adapter** and verify it returns a valid `QuantumBridge Result` object.

2. **Example test for `qiskit-aer`**:
   ```python
   def test_aer_result_adapter_returns_valid_result():
       if not AER.dependency_available():
           pytest.skip("qiskit-aer not installed")

       # Create a fake Aer result
       fake_aer_result = {"counts": {"00": 512, "11": 512}}

       # Call adapter
       qb_result = AER.to_quantumbridge_result(fake_aer_result)

       # Verify
       assert isinstance(qb_result, Result)
       assert qb_result.counts_data == {"00": 512, "11": 512}
   ```

3. **Run tests**:
   ```bash
   pytest -q -rs tests/compat_qiskit_aer/ tests/compat_qiskit_nature/ tests/compat_qiskit_algorithms/
   ```

---

## Acceptance Criteria

You are done when:

1. ✅ **ALL tests pass** (or skip gracefully):
   ```bash
   pytest -q -rs tests/
   ```
   - Zero failures.

2. ✅ **ALL scaffold adapters have `warnings.warn()`**

3. ✅ **ALL inventory JSON files are non-empty and valid**

4. ✅ **ALL `__init__.py` files export adapters correctly**

5. ✅ **README clearly labels scaffolds**

6. ✅ **Changes committed** to `p2/ecosystem-full-coverage-planning` branch.

---

## Important Notes

1. **DO NOT modify `v0.1.0-p1-rc1` tag**.
2. **DO NOT copy third-party source code** into this repo.
3. **DO NOT claim production readiness** for scaffold adapters.
4. **DO NOT merge PR** without OpenClaw review.
5. **DO commit frequently** with clear commit messages.

---

## Deliverables

When you finish, provide OpenClaw with:

1. **Commit hash** of your fixes.
2. **Test output** showing all tests pass (or skip).
3. **List of scaffold adapters** you labeled.
4. **Any inventory JSON files** you fixed.

---

**End of Prompt**
