# Source Migration Ledger

Status: Stage 7 ecosystem planning update
Date: 2026-06-05

This ledger records implementation mode and upstream source status for the current P1 release-candidate baseline. Current work uses Native Implementation, Adapter Integration, and Upstream Dependency. No new upstream source migration was introduced during Stage 5.5. No Source Port with Attribution was performed.

| QuantumBridge file | Feature | Mode | Referenced Qiskit? | Referenced PennyLane? | Original project path | Original license | Copied code? | Modified code? | Modification notes | Copyright retained? | THIRD_PARTY_NOTICES updated? | Tests? | Reviewer | Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `quantumbridge/compat/qiskit_adapter.py` | Qiskit circuit import/export, IR bridge, counts Result adapter | Adapter Integration | API only | No | N/A | Apache-2.0 dependency | No | No | Converts public Qiskit objects to/from QuantumBridge Circuit/IR and adapts counts mappings to Result | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/pennylane_adapter.py` | PennyLane observable, tape, and executable subset bridge | Adapter Integration | No | API only | N/A | Apache-2.0 dependency | No | No | Converts public PennyLane observables/tapes and builds a minimal executable form from QuantumBridge circuits or IR | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/__init__.py` | Compatibility adapter exports | Adapter Integration | API naming only | API naming only | N/A | Apache-2.0 dependencies | No | No | Re-exports QuantumBridge adapter functions | N/A | Yes | Import coverage | Pending | Low |
| `quantumbridge/__init__.py` | Top-level optional adapter exports | Adapter Integration | API naming only | No | N/A | Apache-2.0 dependency | No | No | Re-exports adapter functions for user convenience | N/A | Yes | Import coverage | Pending | Low |
| `quantumbridge/legal/attribution.py` | Attribution file validation | Native Implementation | Filename/check only | Filename/check only | N/A | N/A | No | No | Checks required license and notice files exist | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/compat/qasm_adapter.py` | OpenQASM subset import | Native Implementation | No | No | N/A | N/A | No | No | Native parser for QuantumBridge supported subset | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/operators/*` | Pauli and sparse Pauli-like operators | Native Implementation | No | No | N/A | N/A | No | No | Native data structures | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/information/*` | Statevector and DensityMatrix | Native Implementation | No | No | N/A | N/A | No | No | Native linear algebra wrappers | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/primitives/*` | Sampler and Estimator | Native Implementation | No | No | N/A | N/A | No | No | Native wrappers over QuantumBridge device/runtime | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/qml/*` | QNode/Tape/templates | Native Implementation | No | Conceptual workflow only | N/A | N/A | No | No | Native minimal QML API | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/interfaces/*` | NumPy/Torch/JAX interfaces | Adapter Integration | No | No | N/A | Various optional dependencies | No | No | Optional array conversion adapters | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/providers/*` | Backend/Job/Provider | Native Implementation | No | No | N/A | N/A | No | No | Native provider abstraction | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/compiler/*` | Compiler placeholders | Native Implementation | No | No | N/A | N/A | No | No | Minimal native pass/coupling/target abstractions | N/A | Yes | Not P0 tested | Pending | Low |
| `quantumbridge/visualization/*` | Text drawer | Native Implementation | No | No | N/A | N/A | No | No | Minimal native text visualization | N/A | Yes | Not P0 tested | Pending | Low |
| `quantumbridge/legal/*` | Attribution validation automation | Native Implementation | No | No | N/A | N/A | No | No | Checks required notice, ledger, and license files exist | N/A | Yes | Yes | Pending | Low |
| `quantumbridge/qasm/*` | P2 grammar-based QASM subset parser/exporter | Native Core | No | No | N/A | N/A | No | No | QuantumBridge-owned lexer/parser/AST for documented subset | N/A | Yes | P2 tests | Pending | Medium |
| `quantumbridge/schema/*` | P2 result schema and JSON serialization | Native Core | No | No | N/A | N/A | No | No | Versioned QuantumBridge result payload schema | N/A | Yes | P2 tests | Pending | Low |
| `quantumbridge/chemistry/*` | P2 chemistry native models and optional adapters | Native Core / Adapter Integration / Upstream Passthrough | API only where optional | No | N/A | Optional upstream dependencies | No | No | Molecule/FermionicOp/JW native subset; Qiskit Nature, PySCF, OpenFermion adapters require optional packages | N/A | Yes | P2 tests | Pending | High |
| `quantumbridge/algorithms/adapters/*` | Qiskit Algorithms optional adapter | Upstream Passthrough | API only | No | N/A | Optional qiskit-algorithms dependency | No | No | Calls/wraps installed upstream algorithms only when available | N/A | Yes | P2 tests | Pending | High |
| `scripts/inventory_qiskit_nature_api.py` | Qiskit Nature public API runtime inventory | Upstream API inventory | Runtime public API only | No | N/A | Optional qiskit-nature dependency | No | No | Uses Python introspection of installed package; does not copy source or docs | N/A | Yes | Inventory tests | Pending | Medium |
| `scripts/inventory_qiskit_algorithms_api.py` | Qiskit Algorithms public API runtime inventory | Upstream API inventory | Runtime public API only | No | N/A | Optional qiskit-algorithms dependency | No | No | Uses Python introspection of installed package; does not copy source or docs | N/A | Yes | Inventory tests | Pending | Medium |
| `quantumbridge/noise/*` | P1 basic noise channels and error model | Native Implementation | No | No | N/A | N/A | No | No | Native BitFlip, PhaseFlip, Depolarizing, ReadoutError, NoiseModel metadata | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compiler/*` | P1 compiler PassManager and basic passes | Native Implementation | No | No | N/A | N/A | No | No | Native PassResult, analysis passes, cancellation pass, merge placeholder | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/ecosystem/*` | Optional ecosystem dependency/version/inventory/provenance registry | Native Implementation | Public package names only | Public package names only | N/A | N/A | No | No | Independently implemented registry for optional dependency introspection and result provenance | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/qiskit_core/*` | Qiskit core inventory and passthrough scaffold | Adapter Integration | API names only | No | N/A | Apache-2.0 dependency | No | No | Lazy imports public Qiskit modules when installed and wraps metadata | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/qiskit_aer/*` | Qiskit Aer inventory and passthrough scaffold | Adapter Integration | API names only | No | N/A | Apache-2.0 dependency | No | No | Optional Aer and noise-model dependency lane | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/qiskit_runtime/*` | Qiskit IBM Runtime inventory and passthrough scaffold | Adapter Integration | API names only | No | N/A | Upstream dependency | No | No | Optional runtime/backend/job dependency lane; no credentials or service emulation | N/A | Yes | Inventory smoke | Pending | High |
| `quantumbridge/compat/qiskit_finance/*` | Qiskit Finance inventory, passthrough scaffold, FinanceResult wrapper, and educational native portfolio subset | Adapter Integration / Native Subset | API names only | No | N/A | Upstream dependency | No | No | Optional finance objects plus independently implemented deterministic mean-variance exact enumeration; no production finance claims | N/A | Yes | Yes | Pending | High |
| `quantumbridge/compat/qiskit_optimization/*` | Qiskit Optimization inventory, passthrough scaffold, and educational native QuadraticProgram subset | Adapter Integration / Native Subset | API names only | No | N/A | Upstream dependency | No | No | Optional optimization objects plus independently implemented small binary QuadraticProgram exact enumeration; no parity or production optimizer claim | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/qiskit_machine_learning/*` | Qiskit Machine Learning inventory and passthrough scaffold | Adapter Integration | API names only | No | N/A | Upstream dependency | No | No | Optional ML objects; no training or accuracy claims | N/A | Yes | Yes | Pending | High |
| `quantumbridge/compat/qiskit_experiments/*` | Qiskit Experiments inventory and passthrough scaffold | Adapter Integration | API names only | No | N/A | Upstream dependency | No | No | Optional experiments objects; no lab workflow guarantees | N/A | Yes | Inventory smoke | Pending | High |
| `quantumbridge/compat/qiskit_addons/*` | Qiskit Addons inventory and passthrough scaffold | Adapter Integration | API names only | No | N/A | Upstream dependency | No | No | Optional addons inventory; no source migration | N/A | Yes | Inventory smoke | Pending | High |
| `quantumbridge/compat/pennylane_full/*` | PennyLane full ecosystem inventory and passthrough scaffold | Adapter Integration | No | API names only | N/A | Apache-2.0 dependency | No | No | Optional PennyLane modules; no full plugin parity claim | N/A | Yes | Yes | Pending | High |
| `scripts/inventory_*_api.py` | Runtime public-name inventory generation | Native Implementation | Public package names only | Public package names only | N/A | N/A | No | No | Generates QuantumBridge JSON/Markdown matrices from runtime introspection | N/A | Yes | Yes | Pending | Medium |

## Source port summary

- Qiskit source files copied: 0.
- PennyLane source files copied: 0.
- Qiskit ecosystem source files copied during Stage 7: 0.
- PennyLane ecosystem source files copied during Stage 7: 0.
- Files requiring upstream copyright headers beyond notices: none in current P0.

## Stage 6.1 source-file coverage path index

The following paths are explicitly indexed for ledger completeness tests because
their headers or adapter text mention upstream projects while stating that no
upstream source was copied:

- `quantumbridge/__init__.py`
- `quantumbridge/algorithms/__init__.py`
- `quantumbridge/algorithms/adapters/__init__.py`
- `quantumbridge/algorithms/adapters/qiskit_algorithms_adapter.py`
- `quantumbridge/algorithms/amplitude.py`
- `quantumbridge/algorithms/eigensolvers.py`
- `quantumbridge/algorithms/gradients.py`
- `quantumbridge/algorithms/grover.py`
- `quantumbridge/algorithms/minimum_eigensolvers.py`
- `quantumbridge/algorithms/optimizers.py`
- `quantumbridge/chemistry/__init__.py`
- `quantumbridge/chemistry/adapters/__init__.py`
- `quantumbridge/chemistry/adapters/openfermion_adapter.py`
- `quantumbridge/chemistry/adapters/pyscf_adapter.py`
- `quantumbridge/chemistry/adapters/qiskit_nature_adapter.py`
- `quantumbridge/chemistry/ansatz.py`
- `quantumbridge/chemistry/drivers.py`
- `quantumbridge/chemistry/fermion.py`
- `quantumbridge/chemistry/integrals.py`
- `quantumbridge/chemistry/mappings.py`
- `quantumbridge/chemistry/molecule.py`
- `quantumbridge/chemistry/qubit_hamiltonian.py`
- `quantumbridge/chemistry/result.py`
- `quantumbridge/chemistry/second_quantized.py`
- `quantumbridge/chemistry/solvers.py`
- `quantumbridge/compat/__init__.py`
- `quantumbridge/compat/pennylane_adapter.py`
- `quantumbridge/compat/qiskit_adapter.py`
- `quantumbridge/compiler/config.py`
- `quantumbridge/compiler/report.py`
- `quantumbridge/legal/attribution.py`
- `quantumbridge/noise/execution.py`
- `quantumbridge/qasm/__init__.py`
- `quantumbridge/qasm/ast.py`
- `quantumbridge/qasm/errors.py`
- `quantumbridge/qasm/exporter.py`
- `quantumbridge/qasm/importer.py`
- `quantumbridge/qasm/lexer.py`
- `quantumbridge/qasm/parser.py`
- `quantumbridge/qasm/tokens.py`
- `quantumbridge/qasm/visitor.py`
- `quantumbridge/schema/__init__.py`
- `quantumbridge/schema/errors.py`
- `quantumbridge/schema/result_schema.py`
- `quantumbridge/schema/serialization.py`
- `quantumbridge/schema/validation.py`

## Stage 7 exact path registration

The following implementation files mention upstream package names for optional dependency, attribution, or adapter metadata purposes. Each file is independently implemented and copies no upstream source, tests, comments, errors, or documentation text.

- `quantumbridge/ecosystem/__init__.py`
- `quantumbridge/ecosystem/capability.py`
- `quantumbridge/ecosystem/dependency.py`
- `quantumbridge/ecosystem/provenance.py`
- `quantumbridge/ecosystem/registry.py`
- `quantumbridge/compat/qiskit_core/__init__.py`
- `quantumbridge/compat/qiskit_core/circuit_adapter.py`
- `quantumbridge/compat/qiskit_core/primitives_adapter.py`
- `quantumbridge/compat/qiskit_core/quantum_info_adapter.py`
- `quantumbridge/compat/qiskit_core/result_adapter.py`
- `quantumbridge/compat/qiskit_core/transpiler_adapter.py`
- `quantumbridge/compat/qiskit_aer/__init__.py`
- `quantumbridge/compat/qiskit_aer/aer_adapter.py`
- `quantumbridge/compat/qiskit_aer/noise_adapter.py`
- `quantumbridge/compat/qiskit_runtime/__init__.py`
- `quantumbridge/compat/qiskit_runtime/backend_adapter.py`
- `quantumbridge/compat/qiskit_runtime/job_adapter.py`
- `quantumbridge/compat/qiskit_runtime/runtime_adapter.py`
- `quantumbridge/compat/qiskit_finance/__init__.py`
- `quantumbridge/compat/qiskit_finance/applications_adapter.py`
- `quantumbridge/compat/qiskit_finance/circuits_adapter.py`
- `quantumbridge/compat/qiskit_finance/data_provider_adapter.py`
- `quantumbridge/compat/qiskit_finance/portfolio_examples.py`
- `quantumbridge/compat/qiskit_finance/portfolio_native.py`
- `quantumbridge/compat/qiskit_finance/portfolio_optimization_adapter.py`
- `quantumbridge/compat/qiskit_finance/portfolio_result.py`
- `quantumbridge/compat/qiskit_finance/uncertainty_adapter.py`
- `quantumbridge/compat/qiskit_optimization/__init__.py`
- `quantumbridge/compat/qiskit_optimization/converter_adapter.py`
- `quantumbridge/compat/qiskit_optimization/converters_adapter.py`
- `quantumbridge/compat/qiskit_optimization/minimum_eigen_optimizer_adapter.py`
- `quantumbridge/compat/qiskit_optimization/optimizer_adapter.py`
- `quantumbridge/compat/qiskit_optimization/quadratic_program_adapter.py`
- `quantumbridge/compat/qiskit_optimization/quadratic_program_native.py`
- `quantumbridge/compat/qiskit_optimization/quadratic_program_result.py`
- `quantumbridge/compat/qiskit_optimization/warnings.py`
- `quantumbridge/compat/qiskit_machine_learning/__init__.py`
- `quantumbridge/compat/qiskit_machine_learning/classifier_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/kernel_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/qnn_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/torch_connector_adapter.py`
- `quantumbridge/compat/qiskit_experiments/__init__.py`
- `quantumbridge/compat/qiskit_experiments/calibration_adapter.py`
- `quantumbridge/compat/qiskit_experiments/experiments_adapter.py`
- `quantumbridge/compat/qiskit_experiments/tomography_adapter.py`
- `quantumbridge/compat/qiskit_addons/__init__.py`
- `quantumbridge/compat/qiskit_addons/aqc_adapter.py`
- `quantumbridge/compat/qiskit_addons/mpf_adapter.py`
- `quantumbridge/compat/qiskit_addons/obp_adapter.py`
- `quantumbridge/compat/qiskit_addons/sqd_adapter.py`
- `quantumbridge/compat/pennylane_full/__init__.py`
- `quantumbridge/compat/pennylane_full/device_adapter.py`
- `quantumbridge/compat/pennylane_full/gradients_adapter.py`
- `quantumbridge/compat/pennylane_full/measurement_adapter.py`
- `quantumbridge/compat/pennylane_full/operations_adapter.py`
- `quantumbridge/compat/pennylane_full/plugin_adapter.py`
- `quantumbridge/compat/pennylane_full/qchem_adapter.py`
- `quantumbridge/compat/pennylane_full/qnode_adapter.py`
- `quantumbridge/compat/pennylane_full/resource_adapter.py`
- `quantumbridge/compat/pennylane_full/templates_adapter.py`
- `quantumbridge/compat/pennylane_full/transforms_adapter.py`

## Stage 7.2 exact path registration

The following files are independently implemented adapter/schema modules. They reference upstream package names or public object names only. No upstream source, tests, documentation, comments, or error strings were copied.

- `quantumbridge/schema/__init__.py`
- `quantumbridge/schema/ecosystem_results.py`
- `quantumbridge/compat/qiskit_nature/__init__.py`
- `quantumbridge/compat/qiskit_nature/nature_adapter.py`
- `quantumbridge/compat/qiskit_nature/driver_adapter.py`
- `quantumbridge/compat/qiskit_nature/problem_adapter.py`
- `quantumbridge/compat/qiskit_nature/openfermion_adapter.py`
- `quantumbridge/compat/qiskit_nature/result_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/__init__.py`
- `quantumbridge/compat/qiskit_algorithms/eigensolver_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/minimum_eigensolver_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/amplitude_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/grover_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/optimizer_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/gradient_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/result_adapter.py`
- `quantumbridge/compat/qiskit_dynamics/__init__.py`
- `quantumbridge/compat/qiskit_dynamics/solver_adapter.py`
- `quantumbridge/compat/qiskit_dynamics/model_adapter.py`
- `quantumbridge/compat/qiskit_dynamics/signal_adapter.py`
- `quantumbridge/compat/qiskit_dynamics/backend_adapter.py`
- `quantumbridge/compat/qiskit_dynamics/result_adapter.py`
- `quantumbridge/compat/qiskit_metal/__init__.py`
- `quantumbridge/compat/qiskit_metal/design_adapter.py`
- `quantumbridge/compat/qiskit_metal/component_adapter.py`
- `quantumbridge/compat/qiskit_metal/renderer_adapter.py`
- `quantumbridge/compat/qiskit_metal/simulation_adapter.py`
- `quantumbridge/compat/qiskit_metal/result_adapter.py`
- `quantumbridge/compat/qiskit_finance/result_adapter.py`
- `quantumbridge/compat/qiskit_optimization/applications_adapter.py`
- `quantumbridge/compat/qiskit_optimization/result_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/regressor_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/dataset_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/result_adapter.py`
- `quantumbridge/compat/qiskit_experiments/rb_adapter.py`
- `quantumbridge/schema/optimization_results.py`
- `quantumbridge/compat/qiskit_experiments/result_adapter.py`
- `quantumbridge/compat/qiskit_aer/result_adapter.py`
- `quantumbridge/compat/qiskit_runtime/result_adapter.py`
- `quantumbridge/compat/qiskit_addons/result_adapter.py`
- `quantumbridge/compat/pennylane_full/result_adapter.py`

Stage 7.2 source port count remains zero.

## Stage 8A exact path registration

The following Stage 8A contract file mentions upstream package names only to
define independent QuantumBridge adapter metadata, provenance, and warnings.
No upstream source, tests, documentation prose, comments, or error strings were
copied.

- `quantumbridge/compat/contracts.py`

Stage 8A source port count remains zero.

## Stage 8B exact path registration

The following Stage 8B PennyLane full API inventory, adapter, bridge, and schema
files mention upstream package names only for optional dependency discovery,
public API introspection, provenance, warnings, schema metadata, or conversion
scaffold labels. They are independently implemented and copy no upstream
source, tests, documentation prose, comments, or error strings.

- `quantumbridge/compat/pennylane_full/data_adapter.py`
- `quantumbridge/compat/pennylane_full/dependency.py`
- `quantumbridge/compat/pennylane_full/interface_adapter.py`
- `quantumbridge/compat/pennylane_full/inventory.py`
- `quantumbridge/compat/pennylane_full/io_adapter.py`
- `quantumbridge/compat/pennylane_full/kernels_adapter.py`
- `quantumbridge/compat/pennylane_full/math_adapter.py`
- `quantumbridge/compat/pennylane_full/measurements_adapter.py`
- `quantumbridge/compat/pennylane_full/observables_adapter.py`
- `quantumbridge/compat/pennylane_full/operations_adapter.py`
- `quantumbridge/compat/pennylane_full/passthrough.py`
- `quantumbridge/compat/pennylane_full/qaoa_adapter.py`
- `quantumbridge/compat/pennylane_full/qcut_adapter.py`
- `quantumbridge/compat/pennylane_full/qiskit_bridge.py`
- `quantumbridge/compat/pennylane_full/qnn_adapter.py`
- `quantumbridge/compat/pennylane_full/qnode_adapter.py`
- `quantumbridge/compat/pennylane_full/qos_uqci_bridge.py`
- `quantumbridge/compat/pennylane_full/registry.py`
- `quantumbridge/compat/pennylane_full/result_adapter.py`
- `quantumbridge/compat/pennylane_full/shadows_adapter.py`
- `quantumbridge/compat/pennylane_full/tape_adapter.py`
- `quantumbridge/compat/pennylane_full/warnings.py`
- `quantumbridge/schema/pennylane_results.py`

Stage 8B source port count remains zero.

## Stage 8D exact path registration

The following Stage 8D Qiskit ecosystem adapter contract, schema, inventory,
and test files mention upstream package names only for optional dependency
discovery, runtime public API introspection, passthrough metadata, provenance,
warnings, schema metadata, or unsupported/advisory labels. They are
independently implemented and copy no upstream source, tests, documentation
prose, comments, or error strings.

- `quantumbridge/compat/qiskit_common.py`
- `quantumbridge/compat/qiskit_contract_helpers.py`
- `quantumbridge/compat/qiskit_adapter.py`
- `quantumbridge/compat/qiskit_core/__init__.py`
- `quantumbridge/compat/qiskit_core/circuit_adapter.py`
- `quantumbridge/compat/qiskit_aer/__init__.py`
- `quantumbridge/compat/qiskit_nature/__init__.py`
- `quantumbridge/compat/qiskit_algorithms/__init__.py`
- `quantumbridge/compat/qiskit_finance/__init__.py`
- `quantumbridge/compat/qiskit_optimization/__init__.py`
- `quantumbridge/compat/qiskit_machine_learning/__init__.py`
- `quantumbridge/compat/qiskit_dynamics/__init__.py`
- `quantumbridge/compat/qiskit_experiments/__init__.py`
- `quantumbridge/compat/qiskit_metal/__init__.py`
- `quantumbridge/compat/qiskit_runtime/__init__.py`
- `quantumbridge/compat/qiskit_addons/__init__.py`
- `quantumbridge/schema/qiskit_results.py`
- `scripts/qiskit_inventory_common.py`
- `scripts/inventory_qiskit_core_api.py`
- `scripts/inventory_qiskit_aer_api.py`
- `scripts/inventory_qiskit_nature_api.py`
- `scripts/inventory_qiskit_algorithms_api.py`
- `scripts/inventory_qiskit_finance_api.py`
- `scripts/inventory_qiskit_optimization_api.py`
- `scripts/inventory_qiskit_machine_learning_api.py`
- `scripts/inventory_qiskit_dynamics_api.py`
- `scripts/inventory_qiskit_experiments_api.py`
- `scripts/inventory_qiskit_metal_api.py`
- `scripts/inventory_qiskit_ibm_runtime_api.py`
- `scripts/inventory_qiskit_addons_api.py`
- `tests/compat_qiskit_core/test_qiskit_core_contract.py`
- `tests/compat_qiskit_aer/test_qiskit_aer_contract.py`
- `tests/compat_qiskit_nature/test_qiskit_nature_contract.py`
- `tests/compat_qiskit_algorithms/test_qiskit_algorithms_contract.py`
- `tests/compat_qiskit_finance/test_qiskit_finance_contract.py`
- `tests/compat_qiskit_optimization/test_qiskit_optimization_contract.py`
- `tests/compat_qiskit_machine_learning/test_qiskit_ml_contract.py`
- `tests/compat_qiskit_dynamics/test_qiskit_dynamics_contract.py`
- `tests/compat_qiskit_experiments/test_qiskit_experiments_contract.py`
- `tests/compat_qiskit_metal/test_qiskit_metal_advisory_contract.py`
- `tests/compat_qiskit_runtime/test_qiskit_runtime_offline_contract.py`
- `tests/compat_qiskit_addons/test_qiskit_addons_contract.py`
- `tests/ecosystem/test_qiskit_ecosystem_contract_coverage.py`
- `tests/ecosystem/test_qiskit_result_schema.py`
- `tests/ecosystem/test_qiskit_no_vendor_no_token.py`

Stage 8D generated inventory JSON and coverage matrix Markdown files under
`docs/compat/inventory/` and `docs/compat/matrix/` contain public API names,
capability metadata, warnings, risk labels, and provenance notes only. They do
not contain upstream implementation source or vendored dependency artifacts.

Stage 8D source port count remains zero.
