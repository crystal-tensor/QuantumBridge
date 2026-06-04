# Stage 6.2 Upstream Verification Implementation Report

## 1. New / Modified Files

New tests:

- `tests/chemistry/test_h2_installed_workflow.py`
- `tests/chemistry/test_lih_installed_workflow.py`
- `tests/chemistry/test_h2o_installed_workflow.py`
- `tests/chemistry/test_pyscf_driver_installed.py`
- `tests/chemistry/test_qiskit_nature_driver_installed.py`
- `tests/chemistry/test_openfermion_adapter_installed.py`
- `tests/algorithms_compat/test_qiskit_algorithms_installed_vqe.py`
- `tests/algorithms_compat/test_qiskit_algorithms_installed_qaoa.py`
- `tests/algorithms_compat/test_qiskit_algorithms_installed_numpy_eigensolver.py`
- `tests/algorithms_compat/test_qiskit_algorithms_installed_optimizers.py`

Modified files:

- `.github/workflows/test-matrix.yml`
- `README.md`
- `pyproject.toml`
- `scripts/run_local_matrix.sh`
- `scripts/inventory_qiskit_nature_api.py`
- `scripts/inventory_qiskit_algorithms_api.py`
- `docs/compat/qiskit_nature_public_api_inventory.md`
- `docs/compat/qiskit_nature_feature_parity_matrix.md`
- `docs/compat/qiskit_algorithms_public_api_inventory.md`
- `docs/compat/qiskit_algorithms_feature_parity_matrix.md`

New reports:

- `docs/review/stage6_2_upstream_verification_v0.1.md`
- `docs/implementation/stage6_2_upstream_verification_report.md`

## 2. Installed Optional Dependencies

Installed successfully in the `python3` 3.12.6 environment:

- `qiskit 2.4.1`
- `qiskit_nature 0.8.0`
- `qiskit_algorithms 0.4.0`
- `pyscf 2.13.1`
- `openfermion 1.7.1`
- `numpy 2.4.6`
- `scipy 1.17.1`

## 3. Failed Optional Dependencies

No final optional dependency remained failed.

Initial failure:

- `python3 -m pip install -e '.[chemistry]'` failed during OpenFermion wheel download because of `IncompleteRead`.

Resolution:

- Extras were split and installed separately:
  - `.[qiskit-nature]`
  - `.[algorithms]`
  - `.[pyscf]`
  - `.[openfermion]`

Dependency conflict:

- `pyquafu 0.4.5` requires `numpy<2.0.0,>=1.20.3`; installed chemistry stack resolved to `numpy 2.4.6`.

Pin suggestion:

- Use isolated virtual environments for optional chemistry verification.
- Review whether `numpy<2` should be pinned for any environment that must include `pyquafu`.

## 4. Qiskit Nature Inventory Result

`python3 scripts/inventory_qiskit_nature_api.py` passed with real `qiskit_nature` import.

Generated:

- `docs/compat/qiskit_nature_public_api_inventory.md`
- `docs/compat/qiskit_nature_feature_parity_matrix.md`

The inventory marks APIs as `Inventory only` plus a planned mode such as `Adapter`, `Upstream Passthrough`, or `Planned`. No upstream source or documentation prose was copied.

## 5. Qiskit Algorithms Inventory Result

`python3 scripts/inventory_qiskit_algorithms_api.py` passed with real `qiskit_algorithms` import.

Generated:

- `docs/compat/qiskit_algorithms_public_api_inventory.md`
- `docs/compat/qiskit_algorithms_feature_parity_matrix.md`

The inventory includes VQE, QAOA, NumPyMinimumEigensolver, NumPyEigensolver, SamplingVQE, VQD, AdaptVQE, Grover, amplitude estimation, optimizers, gradients, and result classes where exposed by the installed package.

## 6. PySCF Driver Verification Result

`tests/chemistry/test_pyscf_driver_installed.py` passed.

Verified:

- Real PySCF H2 molecule construction.
- QuantumBridge `PySCFDriverAdapter` returns `DriverResult`.
- Provenance records `Upstream Passthrough` and `pyscf`.

## 7. OpenFermion Verification Result

`tests/chemistry/test_openfermion_adapter_installed.py` passed.

Verified:

- Real OpenFermion `FermionOperator` construction.
- Conversion into QuantumBridge `FermionicOp`.

## 8. H2 Workflow Result

`tests/chemistry/test_h2_installed_workflow.py` passed.

Verified:

- Qiskit Nature `PySCFDriver` constructs an `ElectronicStructureProblem`.
- Jordan-Wigner mapper creates a qubit operator.
- QuantumBridge wraps the qubit Hamiltonian.
- QuantumBridge exact diagonalization returns a finite total energy.
- QuantumBridge VQE chemistry solver returns a finite total energy.
- Provenance is present.

## 9. LiH Workflow Result

`tests/chemistry/test_lih_installed_workflow.py` passed.

Verified:

- Installed Qiskit Nature / PySCF LiH smoke path can construct a driver object.
- QuantumBridge adapter records LiH molecule provenance.

This is not a production LiH chemistry result.

## 10. H2O Workflow Result

`tests/chemistry/test_h2o_installed_workflow.py` passed.

Verified:

- Installed Qiskit Nature / PySCF H2O smoke path can construct a driver object.
- QuantumBridge adapter records H2O molecule provenance.

This is not a production H2O chemistry result.

## 11. Algorithms Adapter Result

`tests/algorithms_compat` passed.

Verified:

- Qiskit Algorithms VQE executes with installed upstream primitives and optimizer.
- Qiskit Algorithms QAOA executes with installed upstream primitives and optimizer.
- NumPyMinimumEigensolver executes and returns a numeric result.
- COBYLA and SPSA optimizer classes are imported and represented through adapter status.
- Adapter-wrapped results validate against QuantumBridge Result schema.
- Upstream passthrough provenance is recorded.

## 12. Test Results

Targeted installed-environment tests:

- `python3 -m pytest -q -rs tests/chemistry`: `18 passed`.
- `python3 -m pytest -q -rs tests/algorithms_compat`: `10 passed`, `5 warnings`.
- `python3 -m pytest -q -rs tests/compat_inventory`: `2 passed`.

Full suite:

- `python3 -m pytest -q -rs`: `125 passed`, `5 warnings`.

Local matrix:

- `bash scripts/run_local_matrix.sh`: passed.

## 13. Skipped Tests

No tests skipped in the installed Python 3.12 environment after optional dependencies were installed.

## 14. Coverage

`python3 -m pytest --cov=quantumbridge`:

- `125 passed`
- `5 warnings`
- total coverage `86%`

## 15. CI Matrix Status

Updated matrix profiles:

- `core-only`
- `qiskit-extra`
- `pennylane-extra`
- `dev`
- `chemistry-core`
- `chemistry-extra`
- `qiskit-nature-extra`
- `algorithms-extra`
- `openfermion-extra`

Remote GitHub Actions still needs to run after the Stage 6.2 commit is pushed.

## 16. Can We Say "Qiskit Nature Adapter Is Available"?

Yes, with boundaries.

Allowed wording:

- Qiskit Nature adapter smoke workflows are available when optional dependencies are installed.
- H2 driver and Hamiltonian wrapping were verified in Stage 6.2.

Not allowed:

- Full Qiskit Nature parity.
- Production chemistry support.

## 17. Can We Say "Qiskit Algorithms Adapter Is Available"?

Yes, with boundaries.

Allowed wording:

- Qiskit Algorithms adapter smoke workflows are available for installed VQE, QAOA, NumPyMinimumEigensolver, and selected optimizers.

Not allowed:

- Full Qiskit Algorithms parity.
- Native replacement of upstream algorithms.

## 18. Can We Say "Classical Chemistry Driver Is Available"?

Yes, at smoke / adapter level.

Allowed wording:

- PySCF-backed driver smoke and Qiskit Nature-backed H2 problem construction are verified when optional dependencies are installed.

Not allowed:

- Production-grade classical chemistry driver stack.
- Validated chemistry accuracy for LiH/H2O.

## 19. Recommend P2 Review?

Yes, after this Stage 6.2 commit is pushed and remote expanded CI is checked.

## 20. Recommend v0.2.0-alpha1?

Not yet.

Recommended gates before alpha:

- Create or update the PR once GitHub authentication is available.
- Run remote expanded CI matrix.
- Review NumPy / pyquafu dependency conflict.
- Review upstream attribution and license notice wording.
- Confirm public documentation does not imply full parity, official endorsement, production chemistry, or materials band-gap support.
