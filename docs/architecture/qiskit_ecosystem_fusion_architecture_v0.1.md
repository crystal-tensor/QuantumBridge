# Qiskit Ecosystem Fusion Architecture v0.1

**Version**: v0.1  
**Date**: 2026-06-09  
**Status**: Stage 8A planning  

## 1. Position

QuantumBridge is not a Qiskit replacement. It provides optional dependency
adapters, inventory, passthrough, schema wrappers, warnings, and provenance for
selected Qiskit ecosystem packages.

No official IBM, Qiskit, or package maintainer endorsement is claimed.

## 2. Covered Ecosystems

| Package | Stage 8 role | Boundary |
| --- | --- | --- |
| Qiskit core | Circuit, transpiler, primitives, quantum_info, result bridge. | Optional dependency, no complete parity claim. |
| Qiskit Aer | Simulator and noise model adapter path. | Not production-equivalent simulation validation. |
| Qiskit Nature | Chemistry problem, driver, mapping, result bridge. | Optional chemistry lane, not production chemistry. |
| Qiskit Algorithms | VQE, QAOA, eigensolver, optimizer bridge. | Optional algorithms lane, not full algorithm parity. |
| Qiskit Finance | Portfolio/data-provider result wrappers. | Not production finance or trading. |
| Qiskit Optimization | Quadratic program and optimizer bridge. | Not production optimization. |
| Qiskit Machine Learning | QNN, kernel, classifier/regressor wrappers. | Not production ML. |
| Qiskit Dynamics | Advisory dynamics model/solver bridge. | Not lab-grade dynamics validation. |
| Qiskit Experiments | Advisory experiment/calibration inventory. | Not calibration or lab operations support. |
| Qiskit Metal | Advisory design inventory. | Not chip fabrication, EM simulation, or layout signoff. |
| Qiskit IBM Runtime | Offline-only runtime metadata planning. | No IBM Cloud access, token reads, or credential storage. |
| Qiskit Addons | Inventory/advisory unless installed and verified. | No production addon support claim. |

## 3. Adapter Contract per Ecosystem

Every Qiskit ecosystem adapter should converge on this surface:

1. `dependency_available`;
2. `get_upstream_version`;
3. `list_public_api_inventory`;
4. `get_public_object`;
5. `passthrough_class`;
6. `passthrough_function`;
7. `wrap_result`;
8. `to_quantumbridge_schema`;
9. `get_provenance`;
10. `unsupported(reason)`;
11. `get_warnings`;
12. tests for installed and unavailable environments.

## 4. Data Flow

```text
User code
  -> QuantumBridge adapter
  -> optional Qiskit ecosystem dependency
  -> upstream object/result
  -> QuantumBridge result/schema wrapper
  -> provenance + warnings
```

## 5. Runtime and Credential Policy

Qiskit Runtime support is offline-only in this stage.

- Do not access IBM Cloud.
- Do not read tokens.
- Do not write credentials.
- Do not infer account status.
- Do not claim runtime execution support.

Future runtime work must introduce an explicit security review and token
handling policy before any cloud path is enabled.

## 6. Domain Boundaries

Finance, optimization, chemistry, machine learning, experiments, dynamics, and
chip design remain adapter/scaffold/advisory domains unless a later reviewed
stage proves a narrower production-quality subset. Documentation and warnings
must make this clear.

## 7. Tests

Required tests:

- dependency available/unavailable paths;
- import smoke;
- public API inventory smoke;
- passthrough object lookup;
- result wrapper schema validation;
- warnings and provenance;
- offline-only runtime behavior;
- advisory package `continue-on-error` behavior in workflow matrix where
  appropriate.
