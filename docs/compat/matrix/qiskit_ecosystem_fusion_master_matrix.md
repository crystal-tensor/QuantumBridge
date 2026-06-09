# Qiskit Ecosystem Fusion Master Matrix v0.1

**Version**: v0.1  
**Date**: 2026-06-09  
**Status**: Stage 8D adapter contract matrix

## Capability Levels

| Level | Meaning |
| --- | --- |
| 0 | Inventory only. |
| 1 | Upstream passthrough. |
| 2 | QuantumBridge schema adapter. |
| 3 | QuantumBridge native subset. |
| 4 | Production equivalent; not promised. |

## Matrix

| Ecosystem | API group | Inventory status | Level 0 | Level 1 | Level 2 | Level 3 | Required adapter functions | Tests | Risk | Next stage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qiskit core | circuit / transpiler / primitives / quantum_info | Existing matrices present | Yes | Partial | Partial | Native core subset exists | dependency, version, inventory, object lookup, passthrough, wrap, schema, provenance, warnings | core + qiskit-extra | Medium | 8D |
| Qiskit Aer | simulator / noise | Existing matrices present | Yes | Partial | Partial | No | same contract | qiskit-aer-extra | Medium | 8D |
| Qiskit Nature | drivers / problems / mappers | Existing matrices present | Yes | Partial | Partial | No | same contract | qiskit-nature-extra, chemistry | High | 8D |
| Qiskit Algorithms | VQE / QAOA / eigensolvers / optimizers | Existing matrices present | Yes | Partial | Partial | Native algorithm subset exists | same contract | qiskit-algorithms-extra, algorithms | Medium | 8D |
| Qiskit Finance | applications / data providers / uncertainty | Existing matrices present | Yes | Partial | Partial | No | same contract | qiskit-finance-extra | High | 8D |
| Qiskit Optimization | quadratic program / converters / optimizers | Existing matrices present | Yes | Partial | Partial | No | same contract | qiskit-optimization-extra | High | 8D |
| Qiskit Machine Learning | QNN / kernels / classifiers / regressors | Existing matrices present | Yes | Partial | Partial | No | same contract | qiskit-machine-learning-extra | High | 8D |
| Qiskit Dynamics | models / signals / solver / backend | Existing matrices present | Yes | Advisory | Advisory | No | same contract plus advisory warnings | qiskit-dynamics-extra | High | 8D |
| Qiskit Experiments | experiments / calibration / tomography / RB | Existing matrices present | Yes | Advisory | Advisory | No | same contract plus advisory warnings | qiskit-experiments-extra | High | 8D |
| Qiskit Metal | design / components / renderers / simulation | Existing matrices present | Yes | Advisory | Advisory | No | same contract plus chip-design disclaimer | qiskit-metal-extra | High | 8D |
| Qiskit Runtime | backend / job / result / runtime | Existing matrices present | Yes | Offline-only | Offline-only | No | same contract plus no-token policy | qiskit-runtime-extra | High | 8D |
| Qiskit Addons | sqd / mpf / aqc / obp | Existing matrices present | Yes | Advisory | Advisory | No | same contract plus addon warnings | qiskit-addons-extra | Medium | 8D |

## Stage 8D Inventory Snapshot

Generated inventory files live under `docs/compat/inventory/`. They are runtime
public-name snapshots and copy no upstream source.

| Ecosystem | Records | Level 0 | Level 1 | Level 2 | Level 3 | Unsupported | Advisory | Offline-only | Local dependency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Qiskit core | 311 | 311 | 0 | 0 | 0 | 0 | No | No | qiskit 2.4.1 |
| Qiskit Aer | 24 | 24 | 0 | 0 | 0 | 0 | No | No | qiskit-aer 0.17.2 |
| Qiskit Nature | 221 | 221 | 0 | 0 | 0 | 0 | No | No | qiskit-nature 0.8.0 |
| Qiskit Algorithms | 145 | 145 | 0 | 0 | 0 | 0 | No | No | qiskit-algorithms 0.4.0 |
| Qiskit Finance | 4 | 4 | 0 | 0 | 0 | 4 | No | No | not installed |
| Qiskit Optimization | 5 | 5 | 0 | 0 | 0 | 5 | No | No | not installed |
| Qiskit Machine Learning | 6 | 6 | 0 | 0 | 0 | 6 | No | No | not installed |
| Qiskit Dynamics | 6 | 6 | 0 | 0 | 0 | 6 | Yes | No | not installed |
| Qiskit Experiments | 4 | 4 | 0 | 0 | 0 | 4 | Yes | Yes | not installed |
| Qiskit Metal | 5 | 5 | 0 | 0 | 0 | 5 | Yes | No | not installed |
| Qiskit Runtime | 3 | 3 | 0 | 0 | 0 | 3 | Yes | Yes | not installed |
| Qiskit Addons | 4 | 4 | 0 | 0 | 0 | 4 | Yes | No | not installed |

## Required Function Checklist

Each row exposes or documents:

- `capability_level`;
- `production_ready`;
- `native_implementation`;
- `upstream_required`;
- `dependency_available`;
- `get_upstream_version`;
- `get_dependency_report`;
- `list_public_api_inventory`;
- `get_public_object`;
- `passthrough_class`;
- `passthrough_call`;
- `wrap_result`;
- `to_quantumbridge_schema`;
- `get_provenance`;
- `unsupported(reason)`;
- warnings;
- tests.

## Non-Goals

- No native replacement for Qiskit.
- No production-equivalence claim.
- No IBM Cloud access.
- No token reads or credential storage.
- No production finance, ML, optimization, chemistry, experiments, dynamics,
  or chip design claim.
