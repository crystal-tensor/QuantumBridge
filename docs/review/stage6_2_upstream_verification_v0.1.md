# Stage 6.2 Upstream Installed-Environment Verification v0.1

## Scope

Stage 6.2 verifies that selected Stage 6.1 optional adapters work in a real installed environment. It does not add large P2 features, does not enter P3, does not claim full upstream parity, and does not rewrite Qiskit Nature or Qiskit Algorithms natively.

Branch: `p2/dual-track-expansion`

Base Stage 6.1 commit: `7f579b586327c6474462f10ef5d65c83598be4d7`

## Environment

- Python command used for installed verification: `python3`
- Python version: `3.12.6`
- `python` command status: unavailable on this macOS host; it triggers the Command Line Tools installer prompt.
- Installed upstream versions:
  - `qiskit`: `2.4.1`
  - `qiskit_nature`: `0.8.0`
  - `qiskit_algorithms`: `0.4.0`
  - `pyscf`: `2.13.1`
  - `openfermion`: `1.7.1`
  - `numpy`: `2.4.6`
  - `scipy`: `1.17.1`

## Dependency Installation

Successful:

- `python3 -m pip install -e '.[qiskit-nature]'`
- `python3 -m pip install -e '.[algorithms]'`
- `python3 -m pip install -e '.[pyscf]'`
- `python3 -m pip install -e '.[openfermion]'`

Initial `python3 -m pip install -e '.[chemistry]'` failed during the first attempt because the OpenFermion wheel download was interrupted by an `IncompleteRead` network error. The extra was then split as required, and all individual upstream dependency groups installed successfully.

Dependency conflict observed:

- `pyquafu 0.4.5 requires numpy<2.0.0,>=1.20.3`, while Qiskit Nature / OpenFermion resolution installed `numpy 2.4.6`.

Recommended pin strategy for CI or isolated developer environments:

- Use a dedicated virtual environment for Stage 6.2 optional chemistry verification.
- If `pyquafu` must coexist, split it into a separate extra or pin chemistry extras to a NumPy version compatible with both dependency families after a resolver review.

## Capability Table

| Capability | Status | Evidence | Test | Dependency | Level |
|---|---|---|---|---|---|
| Qiskit Nature | Real import, runtime public API inventory, PySCFDriver-backed H2 problem construction, and QuantumBridge driver-result wrapper verified | `qiskit_nature 0.8.0`; generated inventory docs; H2 driver tests passed | `tests/chemistry/test_qiskit_nature_driver_installed.py`, `tests/chemistry/test_h2_installed_workflow.py`, `tests/compat_inventory/test_qiskit_nature_inventory_generated.py` | `qiskit-nature`, `pyscf` | Level 2 |
| Qiskit Algorithms | Real import, VQE/QAOA/NumPyMinimumEigensolver upstream execution, optimizer adapter smoke, QuantumBridge Result schema wrapper verified | `qiskit_algorithms 0.4.0`; algorithm tests passed | `tests/algorithms_compat/test_qiskit_algorithms_installed_*.py` | `qiskit-algorithms` | Level 2 |
| PySCF driver | Real H2 PySCF molecule construction and QuantumBridge DriverResult wrapping verified | `pyscf 2.13.1`; H2 molecule build test passed | `tests/chemistry/test_pyscf_driver_installed.py` | `pyscf` | Level 2 |
| OpenFermion | Real small `FermionOperator` conversion into QuantumBridge `FermionicOp` verified | `openfermion 1.7.1`; conversion test passed | `tests/chemistry/test_openfermion_adapter_installed.py` | `openfermion` | Level 2 |
| H2 workflow | Qiskit Nature driver generated electronic problem; mapped to qubit Hamiltonian; QuantumBridge exact solver and VQE chemistry solver returned finite numbers | `tests/chemistry/test_h2_installed_workflow.py`: 2 tests passed | `tests/chemistry/test_h2_installed_workflow.py` | `qiskit-nature`, `pyscf`, `qiskit-algorithms` for broader environment | Level 2 / Level 3 native subset |
| LiH workflow | Installed-environment smoke workflow records provenance; not a production chemistry calculation | LiH smoke test passed | `tests/chemistry/test_lih_installed_workflow.py` | `qiskit-nature`, `pyscf` | Level 1 |
| H2O workflow | Installed-environment smoke workflow records provenance; not a production chemistry calculation | H2O smoke test passed | `tests/chemistry/test_h2o_installed_workflow.py` | `qiskit-nature`, `pyscf` | Level 1 |
| Band gap / materials | Not implemented | Materials roadmap only; no code path or test claims support | N/A | N/A | Level 0 |

Level definitions:

- Level 0: inventory only.
- Level 1: upstream passthrough works.
- Level 2: adapter returns QuantumBridge schema.
- Level 3: native subset works.
- Level 4: production equivalent, not promised by P2.

## Inventory Results

Qiskit Nature:

- `python3 scripts/inventory_qiskit_nature_api.py` passed.
- `docs/compat/qiskit_nature_public_api_inventory.md` regenerated from installed-package runtime introspection.
- `docs/compat/qiskit_nature_feature_parity_matrix.md` regenerated from installed-package runtime introspection.

Qiskit Algorithms:

- `python3 scripts/inventory_qiskit_algorithms_api.py` passed.
- `docs/compat/qiskit_algorithms_public_api_inventory.md` regenerated from installed-package runtime introspection.
- `docs/compat/qiskit_algorithms_feature_parity_matrix.md` regenerated from installed-package runtime introspection.

No upstream source code or documentation prose was copied into these inventory files.

## Test Results

Installed-environment targeted tests:

- `python3 -m pytest -q -rs tests/chemistry`: `18 passed`.
- `python3 -m pytest -q -rs tests/algorithms_compat`: `10 passed`, with upstream deprecation/sparse warnings.
- `python3 -m pytest -q -rs tests/compat_inventory`: `2 passed`.

Full installed-environment suite:

- `python3 -m pytest -q -rs`: `125 passed`, `5 warnings`.
- `python3 -m pytest --cov=quantumbridge`: `125 passed`, `5 warnings`, coverage `86%`.

Local matrix:

- `bash scripts/run_local_matrix.sh`: passed.
- `qiskit-extra`: `5 passed`.
- `pennylane-extra`: `9 passed`.
- `chemistry-core`: `5 passed`.
- `chemistry-extra`: `30 passed`.
- `qiskit-nature-extra`: `5 passed`.
- `algorithms-extra`: `10 passed`.
- `openfermion-extra`: `1 passed`.

Skipped tests:

- No tests skipped in the installed Python 3.12 environment after optional dependencies were installed.

## PR Status

Requested PR target: `p2/dual-track-expansion` into `main`.

PR creation status:

- `gh` is installed but not logged in.
- GitHub connector PR creation returned `403 Resource not accessible by integration`.
- PR creation is blocked in the current automation environment and requires user action or CLI authentication.

Recommended manual PR URL:

`https://github.com/crystal-tensor/QuantumBridge/pull/new/p2/dual-track-expansion`

## CI Matrix Status

`.github/workflows/test-matrix.yml` was updated to include:

- `chemistry-core`
- `chemistry-extra`
- `qiskit-nature-extra`
- `algorithms-extra`
- `openfermion-extra`

The `qiskit-nature-extra` and `algorithms-extra` jobs run their respective inventory scripts before tests.

Remote GitHub Actions still needs to run on the pushed branch or PR.

## Conclusion

Stage 6.2 confirms that the selected optional upstream adapters are usable in an installed local environment at smoke / adapter level. It is now fair to say:

- Qiskit Nature adapter smoke workflows are available when `qiskit-nature` and supporting dependencies are installed.
- Qiskit Algorithms adapter smoke workflows are available when `qiskit-algorithms` is installed.
- PySCF and OpenFermion adapter smoke workflows are available when their extras are installed.
- H2 is truly runnable at the Stage 6.2 adapter/native-subset level.

It is not fair to say:

- Full Qiskit Nature parity.
- Full Qiskit Algorithms parity.
- Production-grade chemistry.
- Real LiH/H2O chemistry accuracy.
- Materials band-gap support.

Recommendation: enter P2 Review after remote expanded CI passes. Do not publish `v0.2.0-alpha1` until PR review, remote CI, and dependency conflict review are complete.
