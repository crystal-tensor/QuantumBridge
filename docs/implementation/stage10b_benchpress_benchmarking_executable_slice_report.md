# Stage 10B Benchpress Benchmarking Executable Slice Report

## Scope

Stage 10B adds a clean-room local benchmarking layer for QuantumBridge executable
slices. The layer is implemented in `quantumbridge.compat.benchpress` and uses
QuantumBridge-owned workloads from previous stages.

## Implemented

- benchmark case model and validation
- default benchmark registry
- deterministic benchmark runner
- basic circuit, simulator, algorithms, finance / optimization, chemistry,
  QML, mitigation, backend, and bridge suites
- benchmark metrics helpers
- JSON and Markdown report writers
- optional upstream Benchpress boundary
- benchmark result schemas
- examples and tests

## Validation Targets

- `pytest -q -rs tests/compat_benchpress`
- full `pytest -q -rs`
- `pytest --cov=quantumbridge`
- `bash scripts/run_local_matrix.sh`
- `git diff --check`

## Validation Results

- `python3 -m py_compile quantumbridge/compat/benchpress/*.py quantumbridge/schema/*.py examples/benchpress_*_quantumbridge.py`: passed
- `python3 examples/benchpress_basic_suite_quantumbridge.py`: passed
- `python3 examples/benchpress_algorithms_suite_quantumbridge.py`: passed
- `python3 examples/benchpress_backend_suite_quantumbridge.py`: passed
- `python3 examples/benchpress_full_smoke_suite_quantumbridge.py`: passed
- `pytest -q -rs tests/compat_benchpress`: 18 passed
- related compatibility suites: 298 passed, 15 skipped
- full `pytest -q -rs`: 465 passed, 33 skipped
- `pytest --cov=quantumbridge`: 465 passed, 33 skipped, total coverage 85%
- `bash scripts/run_local_matrix.sh`: passed, including `benchpress-compat`
- `git diff --check`: passed

`gh run list --branch main --limit 5` could not be checked locally because the
GitHub CLI is not authenticated in this environment. The owner should confirm
the pushed main workflow in GitHub Actions.

## Boundaries

This stage is not a full Benchpress replacement, not official benchmark output,
not production performance ranking, and does not access cloud services, tokens,
or real hardware. No IBM, Qiskit, or Benchpress source, prose, UI, branding, or
methodology was copied.
