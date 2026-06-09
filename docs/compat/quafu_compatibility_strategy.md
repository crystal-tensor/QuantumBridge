# Quafu / pyquafu Compatibility Strategy

**Version**: v0.1  
**Date**: 2026-06-09  
**Status**: Stage 10A offline executable slice

## 1. Position

pyquafu is an optional dependency. QuantumBridge must not require pyquafu in the
core SDK environment and must not claim official Quafu endorsement or production
backend support.

## 2. Dependency Lane

pyquafu currently requires a NumPy <2 environment. QuantumBridge chemistry lanes
use NumPy 2.x for Qiskit Nature, Qiskit Algorithms, PySCF, and OpenFermion.

Therefore:

- `quafu` / `quafu-compatible` uses `numpy<2` and `pyquafu`;
- `chemistry` / `chemistry-compatible` uses NumPy 2.x;
- QuantumBridge does not require all optional dependencies to coexist in one
  environment.

## 3. Planned Adapter Set

| Adapter | Purpose | Stage |
| --- | --- | --- |
| backend adapter | Offline backend metadata and capability warnings. | 8F |
| circuit adapter | Convert supported QuantumBridge circuit subset to pyquafu form. | 8F |
| job adapter | Offline job descriptor and mock lifecycle. | 8F |
| result adapter | Wrap pyquafu-like results in QuantumBridge schema. | 8F |
| dependency adapter | Version and NumPy lane checks. | 8F |
| warnings | No-token, no-cloud, no-production warnings. | 8F |

Stage 10A implements the offline subset as `quantumbridge.compat.quafu` with a
Quafu-compatible payload, job spec, mock backend, result schema, examples, and
tests.

## 4. Token and Cloud Policy

Stage 8A and 8F must not access a real Quafu cloud backend.

Allowed:

- environment-variable name planning;
- mock backend;
- offline result schema tests;
- clear unsupported reasons.

Forbidden:

- token storage;
- reading tokens outside an explicitly reviewed future runtime stage;
- real cloud calls;
- hardware access;
- official endorsement claims.

## 5. Constraints

The `requirements/constraints-quafu.txt` file is the lane-specific constraints
source. It must remain separate from chemistry constraints.

## 6. Non-Goals

- No full pyquafu replacement.
- No production backend support.
- No real cloud access.
- No token storage.
- No official endorsement claim.
