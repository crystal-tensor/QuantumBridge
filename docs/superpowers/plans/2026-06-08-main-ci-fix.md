# Main CI Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore `main` branch install/test matrix behavior after the PR #1 and PR #2 merge sequence regressed CI-critical files.

**Architecture:** Recover the packaging and local-matrix entrypoints by merging the known-good Stage 7 and Stage 6 definitions into the current tracked files, then remove the global pytest collection collision caused by duplicate test basenames. Keep advisory semantics unchanged and avoid any new feature work.

**Tech Stack:** Python, setuptools, pytest, GitHub Actions matrix workflow, shell script matrix runner

---

### Task 1: Restore packaging metadata

**Files:**
- Modify: `/Users/avalok/work/QuantumBridge/pyproject.toml`

- [ ] Rebuild `pyproject.toml` from the pre-regression Stage 7 version and merge back the Stage 6 chemistry / algorithms / openfermion / quafu extras.
- [ ] Keep `tool.setuptools.packages.find.include = ["quantumbridge*"]` so editable installs do not try to package `LICENSES/`.
- [ ] Preserve Stage 7 extras used by the workflow: `qiskit-aer`, `qiskit-finance`, `qiskit-optimization`, `qiskit-machine-learning`, `qiskit-dynamics`, `qiskit-experiments`, `qiskit-runtime`, `qiskit-addons`, `pennylane-full`.
- [ ] Preserve Stage 6 extras used by the workflow and docs: `chemistry`, `algorithms`, `openfermion`, `qiskit-nature`, `quafu`.
- [ ] Restore pytest config and the `slow` marker registration.

### Task 2: Restore local matrix runner

**Files:**
- Modify: `/Users/avalok/work/QuantumBridge/scripts/run_local_matrix.sh`

- [ ] Restore the Stage 7 local matrix shell runner content.
- [ ] Merge in the Stage 6 P2 lanes that belong on `main`: `chemistry-core`, `chemistry-extra`, `qiskit-nature-p2-extra`, `algorithms-extra`, `openfermion-extra`.
- [ ] Keep advisory ecosystems advisory in messaging only; do not change workflow semantics here.

### Task 3: Remove pytest collection collision

**Files:**
- Modify: `/Users/avalok/work/QuantumBridge/tests/compat_qiskit_nature/`

- [ ] Rename the compatibility test file with the duplicate basename `test_chemistry_result_schema.py` to a unique pytest-discoverable filename.
- [ ] Do not change test behavior; only eliminate module-name collision during global collection.

### Task 4: Verify and report

**Files:**
- Create: `/Users/avalok/work/QuantumBridge/docs/review/stage7_7_main_ci_failure_diagnosis_v0.1.md`

- [ ] Run `pytest -q -rs`.
- [ ] Run `pytest --cov=quantumbridge`.
- [ ] Run `bash scripts/run_local_matrix.sh`.
- [ ] Summarize the latest GitHub Actions run, failing jobs, root cause, applied fix, remaining risks, and readiness for the next review gate.
