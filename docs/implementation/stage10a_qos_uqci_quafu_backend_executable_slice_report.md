# Stage 10A QOS-UQCI / Quafu Backend Executable Slice Report

## Summary

Stage 10A adds clean-room offline backend compatibility slices for QOS-UQCI and
Quafu / pyquafu. The slice converts QuantumBridge circuits / IR into
QOS-UQCI-style job specs and Quafu-compatible payloads, runs them through
QuantumBridge offline mock backends, and returns serializable QuantumBridge
backend result schemas.

## Scope

- QuantumBridge IR -> QOS-UQCI clean-room IR
- QOS-UQCI job spec validation
- QOS-UQCI DeviceSpec / CalSet / Manifest metadata
- QOS-UQCI OpenQASM compatibility artifact
- QOS-UQCI offline mock runtime
- QuantumBridge IR -> Quafu-compatible payload
- Quafu job spec validation
- Quafu offline mock backend
- Optional upstream package boundary metadata for QOS-UQCI and pyquafu

## Non-Goals

- No production QOS runtime
- No production Quafu backend
- No real cloud submission
- No token or credential read
- No real hardware access
- No official QOS-UQCI or Quafu endorsement claim
- No full replacement or production parity claim

## Validation Plan

Required validation includes py_compile, all Stage 10A examples, the new
`tests/compat_qos_uqci` and `tests/compat_quafu` suites, related ecosystem
tests, full pytest, coverage, the local matrix, and `git diff --check`.

## Studio Readiness

The result schemas and examples are Studio-ready for future visualization of
offline job specs, payloads, counts, probabilities, warnings, and provenance.
No UI implementation is included in this stage.
