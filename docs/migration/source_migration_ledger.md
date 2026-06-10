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
| `quantumbridge/information/*` | Statevector, DensityMatrix, and Operator native quantum-information wrappers | Native Implementation | API naming only where compatibility docs mention Qiskit | No | N/A | N/A | No | No | Native linear algebra wrappers; no upstream source copied | N/A | Yes | Yes | Pending | Low |
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
| `quantumbridge/compat/qiskit_aer/*` | Qiskit Aer inventory, passthrough scaffold, and educational native simulator/noise subset | Adapter Integration / Native Subset | API names only | No | N/A | Apache-2.0 dependency | No | No | Optional Aer objects plus independently implemented small statevector, qasm-counts, and simple sampling-noise workflows; no Aer parity or production simulator claim | N/A | Yes | Yes | Stage 9F partial executable | Medium |
| `quantumbridge/compat/mitiq/*` | Mitiq optional dependency metadata plus educational native ZNE/readout mitigation subset | Adapter Integration / Native Subset | API names only through optional ecosystem context | No | N/A | Upstream dependency if installed separately | No | No | Optional Mitiq dependency detection plus independently implemented small zero-noise extrapolation and readout calibration-matrix workflows; no Mitiq parity, production error-mitigation, or hardware calibration claim | N/A | Yes | Yes | Stage 9G partial executable | Medium |
| `quantumbridge/schema/error_mitigation_results.py` | Error mitigation result envelopes | Native Implementation | No | No | N/A | N/A | No | No | QuantumBridge-owned schemas for native ZNE, readout mitigation, upstream passthrough, and comparison results | N/A | Yes | Yes | Stage 9G partial executable | Low |
| `quantumbridge/compat/pennylane_qiskit/*` | PennyLane-Qiskit optional dependency metadata plus educational native bidirectional bridge subset | Adapter Integration / Native Subset | API names only through optional ecosystem context | No | N/A | Upstream dependency if installed separately | No | No | Optional PennyLane-Qiskit dependency detection plus independently implemented Qiskit/PennyLane bridge workflows; no plugin parity, production parity, cloud, token, or hardware claim | N/A | Yes | Yes | Stage 9H partial executable | Medium |
| `quantumbridge/schema/pennylane_qiskit_bridge_results.py` | PennyLane-Qiskit bridge result envelopes | Native Implementation | No | No | N/A | N/A | No | No | QuantumBridge-owned schemas for native bridge, upstream passthrough, IR summary, execution, and equivalence results | N/A | Yes | Yes | Stage 9H partial executable | Low |
| `quantumbridge/compat/qiskit_runtime/*` | Qiskit IBM Runtime inventory and passthrough scaffold | Adapter Integration | API names only | No | N/A | Upstream dependency | No | No | Optional runtime/backend/job dependency lane; no credentials or service emulation | N/A | Yes | Inventory smoke | Pending | High |
| `quantumbridge/compat/qiskit_finance/*` | Qiskit Finance inventory, passthrough scaffold, FinanceResult wrapper, and educational native portfolio subset | Adapter Integration / Native Subset | API names only | No | N/A | Upstream dependency | No | No | Optional finance objects plus independently implemented deterministic mean-variance exact enumeration; no production finance claims | N/A | Yes | Yes | Pending | High |
| `quantumbridge/compat/qiskit_optimization/*` | Qiskit Optimization inventory, passthrough scaffold, and educational native QuadraticProgram subset | Adapter Integration / Native Subset | API names only | No | N/A | Upstream dependency | No | No | Optional optimization objects plus independently implemented small binary QuadraticProgram exact enumeration; no parity or production optimizer claim | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/qiskit_algorithms/*` | Qiskit Algorithms inventory, passthrough scaffold, and educational native VQE/QAOA/Grover subset | Adapter Integration / Native Subset | API names only | No | N/A | Upstream dependency | No | No | Optional algorithms objects plus independently implemented small VQE, QAOA-compatible MaxCut, and Grover educational workflows; no parity or production algorithm claim | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/qiskit_nature/*` | Qiskit Nature inventory, passthrough scaffold, and educational native H2/LiH chemistry subset | Adapter Integration / Native Subset | API names only | No | N/A | Upstream dependency | No | No | Optional chemistry objects plus independently implemented small molecular problem metadata, qubit Hamiltonians, and exact diagonalization; no parity, production chemistry, or materials claim | N/A | Yes | Yes | Pending | High |
| `quantumbridge/ecosystem/catalog.py` | Clean-room ecosystem project catalog schema | Native Implementation | Public project names only | Public project names only | N/A | N/A | No | No | Manual catalog schema for compatibility targets; no website scraping or copied project-card text | N/A | Yes | Yes | Pending | Medium |
| `quantumbridge/compat/qiskit_machine_learning/*` | Qiskit Machine Learning inventory, passthrough scaffold, and educational native QML subset | Adapter Integration / Native Subset | API names only | No | N/A | Upstream dependency | No | No | Optional ML objects plus independently implemented toy quantum kernel, kernel classifier, QNN forward, and QNN classifier; no production ML or high-risk decision claims | N/A | Yes | Yes | Stage 9E partial executable | High |
| `quantumbridge/compat/qiskit_experiments/*` | Qiskit Experiments inventory and passthrough scaffold | Adapter Integration | API names only | No | N/A | Upstream dependency | No | No | Optional experiments objects; no lab workflow guarantees | N/A | Yes | Inventory smoke | Pending | High |
| `quantumbridge/compat/qiskit_experiments/*_native.py` | Stage 9I educational offline Rabi/T1/Ramsey workflows | Clean-room implementation | Public concept names only | No | N/A | QuantumBridge native | No | No | Synthetic data and educational fitting only; no hardware calibration | N/A | Yes | Native tests and examples | Complete | Medium |
| `quantumbridge/compat/qiskit_dynamics/*_native.py` | Stage 9I educational offline one-qubit dynamics workflows | Clean-room implementation | Public concept names only | No | N/A | QuantumBridge native | No | No | Z precession, Rabi drive, dephasing metadata only; no production dynamics | N/A | Yes | Native tests and examples | Complete | Medium |
| `quantumbridge/compat/mqt/*` | Stage 9J MQT Core/DDSIM/QMAP clean-room compatibility slice | Clean-room implementation / optional upstream boundary | Public project and package names only | No | N/A | QuantumBridge native; upstream optional if installed separately | No | No | Core-like circuit dict/QASM, DDSIM-like simulation metadata, and QMAP-like routing; no full MQT, decision-diagram, optimal-mapper, or production parity claim | N/A | Yes | Native tests and examples | Complete | Medium |
| `quantumbridge/schema/mqt_results.py` | Stage 9J MQT compatibility result envelopes | Native Implementation | Public project names only | No | N/A | QuantumBridge native | No | No | QuantumBridge-owned schemas for native MQT Core-like, DDSIM-like, QMAP-like, upstream passthrough, routing, and comparison results | N/A | Yes | Yes | Complete | Low |
| `quantumbridge/compat/torchquantum/*` | Stage 9K TorchQuantum/PyTorch-style QML clean-room compatibility slice | Clean-room implementation / optional upstream boundary | Public project and package names only | No | N/A | QuantumBridge native; torch and TorchQuantum optional if installed separately | No | No | Tensor adapters, native educational quantum layer, batch forward, deterministic toy classifier training, optional torch tensor path, and optional TorchQuantum upstream boundary; no full TorchQuantum/PyTorch or production QML claim | N/A | Yes | Native tests and examples | Complete | Medium |
| `quantumbridge/schema/torchquantum_results.py` | Stage 9K TorchQuantum compatibility result envelopes | Native Implementation | Public project names only | No | N/A | QuantumBridge native | No | No | QuantumBridge-owned schemas for tensor, layer, batch, training, classifier, upstream passthrough, and comparison results | N/A | Yes | Yes | Complete | Low |
| `quantumbridge/compat/qos_uqci/*` | Stage 10A QOS-UQCI clean-room backend executable slice | Clean-room implementation / optional upstream boundary | Public project and package names only | No | N/A | QuantumBridge native; QOS-UQCI optional if installed separately | No | No | UQCI IR, job spec, DeviceSpec, CalSet, Manifest, OpenQASM artifact, offline mock runtime, and optional upstream boundary; no production runtime, cloud, token, hardware, or endorsement claim | N/A | Yes | Native tests and examples | Complete | Medium |
| `quantumbridge/compat/quafu/*` | Stage 10A Quafu / pyquafu clean-room backend executable slice | Clean-room implementation / optional upstream boundary | Public project and package names only | No | N/A | QuantumBridge native; pyquafu optional if installed separately | No | No | Quafu-compatible payload, job spec, offline mock backend, and optional pyquafu boundary; no full pyquafu replacement, production backend, cloud, token, hardware, or endorsement claim | N/A | Yes | Native tests and examples | Complete | Medium |
| `quantumbridge/schema/backend_results.py` | Stage 10A backend compatibility result envelopes | Native Implementation | Public project names only | No | N/A | QuantumBridge native | No | No | QuantumBridge-owned schemas for QOS-UQCI mock runtime, Quafu mock backend, and upstream passthrough results | N/A | Yes | Yes | Complete | Low |
| `quantumbridge/compat/benchpress/*` | Stage 10B Benchpress / benchmarking clean-room executable slice | Clean-room implementation / optional upstream boundary | Public project and package names only | No | N/A | QuantumBridge native; Benchpress optional if installed separately | No | No | Local benchmark registry, runner, suites, metrics, JSON / Markdown reports, and optional upstream boundary; no official benchmark or production performance ranking claim | N/A | Yes | Native tests and examples | Complete | Medium |
| `quantumbridge/schema/benchmark_results.py` | Stage 10B benchmark result envelopes | Native Implementation | Public project names only | No | N/A | QuantumBridge native | No | No | QuantumBridge-owned schemas for benchmark case, suite, comparison, and upstream passthrough results | N/A | Yes | Yes | Complete | Low |
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
- `quantumbridge/providers/__init__.py`
- `quantumbridge/providers/backend.py`
- `quantumbridge/providers/exceptions.py`
- `quantumbridge/providers/job.py`
- `quantumbridge/providers/options.py`
- `quantumbridge/providers/provider.py`
- `quantumbridge/core/circuit.py`
- `quantumbridge/core/operations.py`
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
- `quantumbridge/compat/qiskit_aer/aer_upstream_adapter.py`
- `quantumbridge/compat/qiskit_aer/circuit_execution_adapter.py`
- `quantumbridge/compat/qiskit_aer/examples.py`
- `quantumbridge/compat/qiskit_aer/noise_adapter.py`
- `quantumbridge/compat/qiskit_aer/qasm_simulator_adapter.py`
- `quantumbridge/compat/qiskit_aer/simulator_native.py`
- `quantumbridge/compat/qiskit_aer/statevector_simulator_adapter.py`
- `quantumbridge/compat/qiskit_aer/warnings.py`
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
- `quantumbridge/compat/qiskit_algorithms/algorithms_native.py`
- `quantumbridge/compat/qiskit_algorithms/examples.py`
- `quantumbridge/compat/qiskit_algorithms/grover_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/minimum_eigensolver_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/optimizer_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/qaoa_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/result_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/vqe_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/warnings.py`
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
- `quantumbridge/schema/aer_results.py`
- `quantumbridge/compat/qiskit_runtime/result_adapter.py`
- `quantumbridge/compat/qiskit_addons/result_adapter.py`
- `quantumbridge/compat/pennylane_full/result_adapter.py`

Stage 7.2 source port count remains zero.

## Stage 11A quantum_info native parity path registration

The following files are independently implemented QuantumBridge native
linear-algebra and operator modules. They use public compatibility names such
as Qiskit `quantum_info` only as API targets. No upstream source, tests,
documentation prose, comments, or error strings were copied.

- `quantumbridge/information/operator.py`
- `quantumbridge/information/channels.py`
- `quantumbridge/information/clifford.py`
- `quantumbridge/information/metrics.py`
- `quantumbridge/information/random.py`
- `quantumbridge/operators/pauli_list.py`
- `quantumbridge/compat/qiskit_core/quantum_info_adapter.py`
- `tests/compat_qiskit_core/test_quantum_info_native.py`

Stage 11A source port count remains zero.

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

## Stage 9D exact path registration

The following Stage 9D Qiskit Nature chemistry files mention upstream package
names only for optional dependency discovery, provenance, warnings, schema
metadata, or passthrough comparison labels. They are independently implemented
and copy no upstream source, tests, documentation prose, examples, comments,
error strings, wheels, dist-info, egg-info, site-packages trees, or virtual
environments.

- `quantumbridge/compat/qiskit_nature/chemistry_native.py`
- `quantumbridge/compat/qiskit_nature/__init__.py`
- `quantumbridge/compat/qiskit_nature/result_adapter.py`
- `quantumbridge/schema/chemistry_results.py`
- `quantumbridge/schema/__init__.py`
- `examples/qiskit_nature_h2_quantumbridge.py`
- `examples/qiskit_nature_lih_quantumbridge.py`
- `tests/compat_qiskit_nature/test_h2_native_workflow.py`
- `tests/compat_qiskit_nature/test_lih_native_workflow.py`
- `tests/compat_qiskit_nature/test_qubit_hamiltonian_exact_solver.py`
- `tests/compat_qiskit_nature/test_chemistry_result_schema.py`
- `tests/compat_qiskit_nature/test_h2_upstream_passthrough.py`
- `tests/compat_qiskit_nature/test_lih_upstream_passthrough.py`
- `tests/compat_qiskit_nature/test_chemistry_no_cloud_no_token.py`
- `tests/compat_qiskit_nature/test_chemistry_warnings_provenance.py`
- `tests/compat_qiskit_nature/test_chemistry_examples.py`

Stage 9D source port count remains zero.

## Stage 9E exact path registration

The following Stage 9E files mention Qiskit Machine Learning, IBM Quantum
Ecosystem, or ecosystem project names only for optional dependency,
compatibility target, clean-room catalog, provenance, warning, test, or
documentation purposes. They are independently implemented and copy no upstream
source, tests, documentation prose, website text, UI, screenshots, icons, logos,
error strings, wheels, dist-info, egg-info, site-packages trees, or virtual
environments.

- `quantumbridge/compat/qiskit_machine_learning/qml_dataset_native.py`
- `quantumbridge/compat/qiskit_machine_learning/feature_map_native.py`
- `quantumbridge/compat/qiskit_machine_learning/quantum_kernel_native.py`
- `quantumbridge/compat/qiskit_machine_learning/kernel_classifier_native.py`
- `quantumbridge/compat/qiskit_machine_learning/qnn_native.py`
- `quantumbridge/compat/qiskit_machine_learning/qnn_classifier_native.py`
- `quantumbridge/compat/qiskit_machine_learning/upstream_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/examples.py`
- `quantumbridge/compat/qiskit_machine_learning/warnings.py`
- `quantumbridge/schema/ml_results.py`
- `examples/qiskit_ml_quantum_kernel_quantumbridge.py`
- `examples/qiskit_ml_kernel_classifier_quantumbridge.py`
- `examples/qiskit_ml_qnn_classifier_quantumbridge.py`
- `tests/compat_qiskit_machine_learning/test_qml_dataset_native.py`
- `tests/compat_qiskit_machine_learning/test_quantum_feature_map_native.py`
- `tests/compat_qiskit_machine_learning/test_quantum_kernel_native.py`
- `tests/compat_qiskit_machine_learning/test_kernel_classifier_native.py`
- `tests/compat_qiskit_machine_learning/test_qnn_forward_native.py`
- `tests/compat_qiskit_machine_learning/test_qnn_classifier_native.py`
- `tests/compat_qiskit_machine_learning/test_ml_result_schema.py`
- `tests/compat_qiskit_machine_learning/test_ml_upstream_passthrough.py`
- `tests/compat_qiskit_machine_learning/test_ml_no_cloud_no_token.py`
- `tests/compat_qiskit_machine_learning/test_ml_warnings_provenance.py`
- `tests/compat_qiskit_machine_learning/test_ml_examples.py`

Stage 9E source port count remains zero.

## Stage 9C exact path registration

The following Stage 9C files mention Qiskit Algorithms, IBM Quantum Ecosystem,
or ecosystem project names only for optional dependency, compatibility target,
clean-room catalog, provenance, warning, test, or documentation purposes. They
are independently implemented and copy no upstream source, tests,
documentation prose, website text, UI, screenshots, icons, logos, error
strings, wheels, dist-info, egg-info, site-packages trees, or virtual
environments.

- `quantumbridge/compat/qiskit_algorithms/algorithms_native.py`
- `quantumbridge/compat/qiskit_algorithms/vqe_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/qaoa_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/grover_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/examples.py`
- `quantumbridge/compat/qiskit_algorithms/eigensolver_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/optimizer_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/result_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/warnings.py`
- `quantumbridge/schema/algorithms_results.py`
- `quantumbridge/ecosystem/catalog.py`
- `examples/qiskit_algorithms_vqe_quantumbridge.py`
- `examples/qiskit_algorithms_qaoa_quantumbridge.py`
- `examples/qiskit_algorithms_grover_quantumbridge.py`
- `tests/compat_qiskit_algorithms/test_vqe_native.py`
- `tests/compat_qiskit_algorithms/test_qaoa_native.py`
- `tests/compat_qiskit_algorithms/test_grover_native.py`
- `tests/compat_qiskit_algorithms/test_algorithms_result_schema.py`
- `tests/compat_qiskit_algorithms/test_vqe_upstream_passthrough.py`
- `tests/compat_qiskit_algorithms/test_qaoa_upstream_passthrough.py`
- `tests/compat_qiskit_algorithms/test_grover_upstream_passthrough.py`
- `tests/compat_qiskit_algorithms/test_algorithms_no_cloud_no_token.py`
- `tests/compat_qiskit_algorithms/test_algorithms_warnings_provenance.py`
- `tests/compat_qiskit_algorithms/test_algorithms_examples.py`
- `tests/ecosystem/test_ecosystem_catalog_schema.py`
- `docs/implementation/stage9c_qiskit_algorithms_executable_adapter_report.md`
- `docs/tutorials/qiskit_algorithms_vqe_quantumbridge.md`
- `docs/tutorials/qiskit_algorithms_qaoa_quantumbridge.md`
- `docs/tutorials/qiskit_algorithms_grover_quantumbridge.md`
- `docs/roadmap/ibm_quantum_ecosystem_clean_room_parity_master_plan.md`
- `docs/compat/ecosystem/ibm_quantum_ecosystem_project_catalog_schema.md`
- `docs/compat/ecosystem/ibm_quantum_ecosystem_project_catalog_seed.md`
- `docs/legal/ibm_quantum_ecosystem_clean_room_boundary.md`

Stage 9C source port count remains zero.

## Stage 9G source-file coverage path index

The following Stage 9G files are explicitly indexed for ledger completeness
tests because their clean-room comments or adapter text mention upstream
projects while stating that no upstream source was copied:

- `quantumbridge/compat/mitiq/__init__.py`
- `quantumbridge/compat/mitiq/executor_adapter.py`
- `quantumbridge/compat/mitiq/examples.py`
- `quantumbridge/compat/mitiq/readout_mitigation_native.py`
- `quantumbridge/compat/mitiq/warnings.py`
- `quantumbridge/compat/mitiq/zne_native.py`

Stage 9G source port count remains zero.

## Stage 9H source-file coverage path index

The following Stage 9H files are explicitly indexed for ledger completeness
tests because their clean-room comments or adapter text mention upstream
projects while stating that no upstream source was copied:

- `quantumbridge/compat/pennylane_qiskit/__init__.py`
- `quantumbridge/compat/pennylane_qiskit/bridge_native.py`
- `quantumbridge/compat/pennylane_qiskit/dependency.py`
- `quantumbridge/compat/pennylane_qiskit/examples.py`
- `quantumbridge/compat/pennylane_qiskit/upstream_adapter.py`
- `quantumbridge/compat/pennylane_qiskit/warnings.py`
- `quantumbridge/schema/pennylane_qiskit_bridge_results.py`
- `examples/pennylane_qiskit_qiskit_to_pennylane_quantumbridge.py`
- `examples/pennylane_qiskit_pennylane_to_qiskit_quantumbridge.py`
- `examples/pennylane_qiskit_bridge_equivalence_quantumbridge.py`

Stage 9H source port count remains zero.

## Stage 9I Source Inventory

The following Stage 9I files are clean-room QuantumBridge implementations or
optional dependency boundaries; no upstream source, prose, wheels, dist-info,
egg-info, site-packages trees, or virtual environments were copied:

- `quantumbridge/compat/qiskit_experiments/dependency.py`
- `quantumbridge/compat/qiskit_experiments/warnings.py`
- `quantumbridge/compat/qiskit_experiments/calibration_fit_native.py`
- `quantumbridge/compat/qiskit_experiments/experiment_data_native.py`
- `quantumbridge/compat/qiskit_experiments/rabi_experiment_native.py`
- `quantumbridge/compat/qiskit_experiments/t1_experiment_native.py`
- `quantumbridge/compat/qiskit_experiments/ramsey_experiment_native.py`
- `quantumbridge/compat/qiskit_experiments/experiments_upstream_adapter.py`
- `quantumbridge/compat/qiskit_experiments/examples.py`
- `quantumbridge/compat/qiskit_dynamics/dependency.py`
- `quantumbridge/compat/qiskit_dynamics/warnings.py`
- `quantumbridge/compat/qiskit_dynamics/hamiltonian_model_native.py`
- `quantumbridge/compat/qiskit_dynamics/time_evolution_native.py`
- `quantumbridge/compat/qiskit_dynamics/single_qubit_dynamics_native.py`
- `quantumbridge/compat/qiskit_dynamics/dynamics_upstream_adapter.py`
- `quantumbridge/compat/qiskit_dynamics/examples.py`
- `quantumbridge/schema/experiments_results.py`
- `quantumbridge/schema/dynamics_results.py`

Stage 9I source port count remains zero.

## Stage 9J Source Inventory

The following Stage 9J files are clean-room QuantumBridge implementations or
optional dependency boundaries; no upstream source, prose, wheels, dist-info,
egg-info, site-packages trees, or virtual environments were copied:

- `quantumbridge/compat/mqt/__init__.py`
- `quantumbridge/compat/mqt/dependency.py`
- `quantumbridge/compat/mqt/core_adapter.py`
- `quantumbridge/compat/mqt/ddsim_adapter.py`
- `quantumbridge/compat/mqt/qmap_adapter.py`
- `quantumbridge/compat/mqt/routing_native.py`
- `quantumbridge/compat/mqt/mapping_native.py`
- `quantumbridge/compat/mqt/decision_diagram_metadata.py`
- `quantumbridge/compat/mqt/upstream_adapter.py`
- `quantumbridge/compat/mqt/result_adapter.py`
- `quantumbridge/compat/mqt/warnings.py`
- `quantumbridge/compat/mqt/examples.py`
- `quantumbridge/schema/mqt_results.py`
- `examples/mqt_core_like_circuit_quantumbridge.py`
- `examples/mqt_ddsim_like_simulation_quantumbridge.py`
- `examples/mqt_qmap_like_routing_quantumbridge.py`

Stage 9J source port count remains zero.

## Stage 9K Source Inventory

The following Stage 9K files are clean-room QuantumBridge implementations or
optional dependency boundaries; no upstream source, prose, model weights,
wheels, dist-info, egg-info, site-packages trees, or virtual environments were
copied:

- `quantumbridge/compat/torchquantum/__init__.py`
- `quantumbridge/compat/torchquantum/dependency.py`
- `quantumbridge/compat/torchquantum/tensor_adapter.py`
- `quantumbridge/compat/torchquantum/qml_dataset_native.py`
- `quantumbridge/compat/torchquantum/quantum_layer_native.py`
- `quantumbridge/compat/torchquantum/training_native.py`
- `quantumbridge/compat/torchquantum/torch_adapter.py`
- `quantumbridge/compat/torchquantum/upstream_adapter.py`
- `quantumbridge/compat/torchquantum/result_adapter.py`
- `quantumbridge/compat/torchquantum/warnings.py`
- `quantumbridge/compat/torchquantum/examples.py`
- `quantumbridge/schema/torchquantum_results.py`
- `examples/torchquantum_like_layer_quantumbridge.py`
- `examples/torchquantum_like_batch_forward_quantumbridge.py`
- `examples/torchquantum_like_classifier_quantumbridge.py`

Stage 9K source port count remains zero.

## Stage 10A Source Inventory

The following Stage 10A files are clean-room QuantumBridge implementations or
optional dependency boundaries; no QOS-UQCI, Quafu, pyquafu, IBM, Qiskit,
PennyLane, MQT, Mitiq, TorchQuantum, PyTorch, wheels, dist-info, egg-info,
site-packages trees, or virtual environments were copied:

- `quantumbridge/compat/qos_uqci/__init__.py`
- `quantumbridge/compat/qos_uqci/dependency.py`
- `quantumbridge/compat/qos_uqci/uqci_ir_adapter.py`
- `quantumbridge/compat/qos_uqci/job_spec.py`
- `quantumbridge/compat/qos_uqci/devicespec_adapter.py`
- `quantumbridge/compat/qos_uqci/calset_adapter.py`
- `quantumbridge/compat/qos_uqci/manifest_adapter.py`
- `quantumbridge/compat/qos_uqci/openqasm_bridge.py`
- `quantumbridge/compat/qos_uqci/mock_runtime.py`
- `quantumbridge/compat/qos_uqci/upstream_adapter.py`
- `quantumbridge/compat/qos_uqci/result_adapter.py`
- `quantumbridge/compat/qos_uqci/warnings.py`
- `quantumbridge/compat/qos_uqci/examples.py`
- `quantumbridge/compat/quafu/__init__.py`
- `quantumbridge/compat/quafu/dependency.py`
- `quantumbridge/compat/quafu/payload_adapter.py`
- `quantumbridge/compat/quafu/job_adapter.py`
- `quantumbridge/compat/quafu/mock_backend.py`
- `quantumbridge/compat/quafu/upstream_adapter.py`
- `quantumbridge/compat/quafu/result_adapter.py`
- `quantumbridge/compat/quafu/warnings.py`
- `quantumbridge/compat/quafu/examples.py`
- `quantumbridge/schema/backend_results.py`
- `examples/qos_uqci_bell_job_quantumbridge.py`
- `examples/qos_uqci_mock_runtime_quantumbridge.py`
- `examples/quafu_bell_payload_quantumbridge.py`
- `examples/quafu_mock_backend_quantumbridge.py`

Stage 10A source port count remains zero.

## Stage 10B Source Inventory

The following Stage 10B files are clean-room QuantumBridge implementations or
optional dependency boundaries; no IBM, Qiskit, Benchpress, QOS-UQCI, Quafu,
pyquafu, PennyLane, MQT, Mitiq, TorchQuantum, PyTorch, wheels, dist-info,
egg-info, site-packages, or virtual environments are vendored:

- `quantumbridge/compat/benchpress/__init__.py`
- `quantumbridge/compat/benchpress/benchmark_case.py`
- `quantumbridge/compat/benchpress/benchmark_registry.py`
- `quantumbridge/compat/benchpress/benchmark_runner.py`
- `quantumbridge/compat/benchpress/benchmark_suites.py`
- `quantumbridge/compat/benchpress/dependency.py`
- `quantumbridge/compat/benchpress/examples.py`
- `quantumbridge/compat/benchpress/metrics.py`
- `quantumbridge/compat/benchpress/reporting.py`
- `quantumbridge/compat/benchpress/result_adapter.py`
- `quantumbridge/compat/benchpress/upstream_adapter.py`
- `quantumbridge/compat/benchpress/warnings.py`
- `quantumbridge/schema/benchmark_results.py`
- `examples/benchpress_*_quantumbridge.py`
- `tests/compat_benchpress/*`
- `docs/compat/benchpress_benchmarking_strategy.md`
- `docs/implementation/stage10b_benchpress_benchmarking_executable_slice_report.md`
- `docs/tutorials/benchpress_*_quantumbridge.md`

Stage 10B source port count remains zero.

## Stage 10C Source Inventory

The following Stage 10C files are clean-room QuantumBridge implementations or
local backend API documentation; no IBM, Qiskit, PennyLane, Benchpress,
QOS-UQCI, Quafu, MQT, Mitiq, TorchQuantum, PyTorch, FastAPI, wheels,
dist-info, egg-info, site-packages, or virtual environments are vendored:

- `quantumbridge/studio/__init__.py`
- `quantumbridge/studio/api_models.py`
- `quantumbridge/studio/catalog_service.py`
- `quantumbridge/studio/workflow_registry.py`
- `quantumbridge/studio/workflow_inputs.py`
- `quantumbridge/studio/execution_service.py`
- `quantumbridge/studio/result_store.py`
- `quantumbridge/studio/export_service.py`
- `quantumbridge/studio/benchmark_service.py`
- `quantumbridge/studio/provenance_service.py`
- `quantumbridge/studio/warning_service.py`
- `quantumbridge/studio/local_router.py`
- `quantumbridge/studio/fastapi_adapter.py`
- `quantumbridge/studio/warnings.py`
- `quantumbridge/studio/examples.py`
- `examples/studio_catalog_api_quantumbridge.py`
- `examples/studio_workflow_execution_quantumbridge.py`
- `examples/studio_benchmark_api_quantumbridge.py`
- `examples/studio_export_api_quantumbridge.py`
- `tests/studio/*`
- `docs/studio/*`
- `docs/implementation/stage10c_quantumbridge_studio_backend_api_slice_report.md`
- `docs/tutorials/studio_*_quantumbridge.md`

Stage 10C source port count remains zero.

## Stage 10D Source Inventory

The following Stage 10D files are clean-room QuantumBridge implementations,
generated local seed data from QuantumBridge-owned APIs, or local frontend
prototype documentation. No IBM, Qiskit, PennyLane, Benchpress, QOS-UQCI,
Quafu, MQT, Mitiq, TorchQuantum, PyTorch, React, Vite, Carbon, wheels,
dist-info, egg-info, site-packages, `node_modules`, build outputs, copied UI,
copied prose, logos, or virtual environments are vendored:

- `examples/studio_generate_frontend_seed_data_quantumbridge.py`
- `studio/package.json`
- `studio/index.html`
- `studio/src/main.js`
- `studio/src/App.js`
- `studio/src/api/studioClient.js`
- `studio/src/api/mockStudioClient.js`
- `studio/src/api/localJsonClient.js`
- `studio/src/components/Badge.js`
- `studio/src/components/Card.js`
- `studio/src/components/ExportPanel.js`
- `studio/src/components/Header.js`
- `studio/src/components/JsonViewer.js`
- `studio/src/components/Layout.js`
- `studio/src/components/ProvenancePanel.js`
- `studio/src/components/ResultPanel.js`
- `studio/src/components/Sidebar.js`
- `studio/src/components/WarningPanel.js`
- `studio/src/pages/BenchmarksPage.js`
- `studio/src/pages/CatalogPage.js`
- `studio/src/pages/ExecutePage.js`
- `studio/src/pages/ExportsPage.js`
- `studio/src/pages/ResultsPage.js`
- `studio/src/pages/WorkflowDetailPage.js`
- `studio/src/pages/WorkflowsPage.js`
- `studio/src/styles/globals.css`
- `studio/scripts/smoke-check.mjs`
- `studio/src/data/sampleCatalog.json`
- `studio/src/data/sampleWorkflows.json`
- `studio/src/data/sampleResults.json`
- `studio/src/data/sampleBenchmarkReport.json`
- `studio/src/data/seedData.js`
- `docs/implementation/stage10d_quantumbridge_studio_frontend_prototype_report.md`
- `docs/studio/frontend_prototype_v0.1.md`
- `docs/studio/frontend_local_data_contract_v0.1.md`
- `docs/studio/frontend_security_boundary_v0.1.md`
- `docs/tutorials/studio_frontend_local_prototype_quantumbridge.md`

Stage 10D source port count remains zero.

## Stage 10E Source Inventory

The following Stage 10E files are clean-room QuantumBridge implementations,
generated local seed data from QuantumBridge-owned APIs, or local integration
hardening documentation. No IBM, Qiskit, PennyLane, Benchpress, QOS-UQCI,
Quafu, MQT, Mitiq, TorchQuantum, PyTorch, React, Vite, Carbon, wheels,
dist-info, egg-info, site-packages, `node_modules`, build outputs, copied UI,
copied prose, logos, or virtual environments are vendored:

- `quantumbridge/studio/frontend_contract.py`
- `quantumbridge/studio/__main__.py`
- `quantumbridge/studio/export_service.py`
- `examples/studio_generate_frontend_seed_data_quantumbridge.py`
- `studio/src/api/studioClient.js`
- `studio/src/api/mockStudioClient.js`
- `studio/src/api/localJsonClient.js`
- `studio/src/pages/BenchmarksPage.js`
- `studio/src/pages/CatalogPage.js`
- `studio/src/pages/ExecutePage.js`
- `studio/src/pages/ExportsPage.js`
- `studio/src/pages/ResultsPage.js`
- `studio/src/pages/WorkflowDetailPage.js`
- `studio/src/pages/WorkflowsPage.js`
- `studio/src/styles/globals.css`
- `studio/scripts/smoke-check.mjs`
- `studio/src/data/sampleCatalog.json`
- `studio/src/data/sampleWorkflows.json`
- `studio/src/data/sampleWorkflowDetails.json`
- `studio/src/data/sampleResults.json`
- `studio/src/data/sampleBenchmarkReport.json`
- `studio/src/data/sampleExports.json`
- `studio/src/data/studioSchemaVersion.json`
- `studio/src/data/seedData.js`
- `tests/studio/test_backend_frontend_contract_coverage.py`
- `tests/studio/test_frontend_seed_contract.py`
- `tests/studio/test_frontend_seed_no_branding_no_secrets.py`
- `tests/studio/test_studio_cli.py`
- `docs/implementation/stage10e_studio_backend_frontend_integration_hardening_report.md`
- `docs/studio/backend_frontend_contract_v0.1.md`
- `docs/studio/studio_cli_contract_v0.1.md`
- `docs/tutorials/studio_generate_seed_and_execute_workflow_quantumbridge.md`

Stage 10E source port count remains zero.
