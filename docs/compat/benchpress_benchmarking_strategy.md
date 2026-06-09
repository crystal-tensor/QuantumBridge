# Benchpress / Benchmarking Compatibility Strategy

**Status**: Stage 10B clean-room executable slice

QuantumBridge provides a local educational benchmark layer for small
QuantumBridge-owned workloads. It does not copy Benchpress source, benchmark
methodology, tutorial prose, website text, UI, or branding.

## Supported Stage 10B Workflows

- local benchmark case registry
- default benchmark suites
- deterministic benchmark runner
- pass/fail metrics for small workloads
- JSON and Markdown reports
- optional upstream Benchpress dependency boundary

Default suites cover basic circuits, simulators, algorithms, finance /
optimization, chemistry, QML, mitigation, backend mock execution, and bridge
workflows.

## Upstream Boundary

If an optional Benchpress package is installed separately, QuantumBridge records
dependency and version metadata. Stage 10B does not run official Benchpress
benchmarks by default and does not claim upstream parity.

## Non-goals

- full Benchpress replacement
- official benchmark output
- production performance ranking
- cloud access
- token access
- real hardware access
- official IBM, Qiskit, or Benchpress endorsement
