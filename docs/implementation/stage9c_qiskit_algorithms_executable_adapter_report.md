# Stage 9C Qiskit Algorithms Executable Adapter Report

Status: implemented pending final validation
Main start HEAD: `974d753872586994ee1fc9fa1fefc5b9a6c80d39`
Scope: Qiskit Algorithms executable slice for QuantumBridge ecosystem parity.

## Summary

Stage 9C promotes the Qiskit Algorithms lane from inventory / passthrough
scaffold toward executable proof. It adds small, deterministic, clean-room
native workflows for VQE, QAOA-compatible MaxCut, and Grover search, plus
optional local upstream passthrough smoke paths when `qiskit-algorithms` is
installed.

The implementation is educational and intentionally limited. It is not a full
Qiskit Algorithms replacement, not production algorithm software, and not an
IBM or Qiskit endorsement.

## IBM Quantum Ecosystem Clean-Room Parity Alignment

This stage is the Algorithms slice of QuantumBridge's IBM Quantum Ecosystem
clean-room parity program.

- It covers minimal executable VQE, QAOA, and Grover workflows.
- It provides optional upstream passthrough paths when the local optional
  dependency is installed.
- It provides QuantumBridge-native educational paths that do not require cloud,
  tokens, real hardware, or copied upstream source.
- Results use QuantumBridge algorithm result schemas with warnings,
  provenance, unsupported reasons, and production-readiness flags.
- It does not copy IBM Quantum Ecosystem page text, UI, branding, screenshots,
  icons, or source code.
- It does not imply IBM, Qiskit, PennyLane, or third-party project endorsement.

Future parity work must expand beyond this slice through independently tested
project slices, not by cloning IBM's website or third-party implementation
details.

## Added Capabilities

Native VQE:
- two-qubit Pauli Hamiltonian example;
- RX/RY linear-entangler ansatz descriptor;
- deterministic grid-search evaluation;
- finite eigenvalue estimate;
- optimal parameters;
- statevector probabilities.

Native QAOA:
- small MaxCut problem schema;
- MaxCut objective helper;
- exact brute-force verification path for educational QAOA-compatible output;
- best bitstring and cut value;
- cost-Hamiltonian metadata.

Native Grover:
- marked-bitstring oracle metadata;
- 2-4 qubit statevector simulation path;
- one or more marked bitstrings;
- probability distribution;
- top measurement.

Upstream passthrough:
- dependency report for `qiskit_algorithms`, `qiskit`, and optional
  `qiskit_aer`;
- local VQE/QAOA/Grover smoke paths when compatible upstream packages are
  installed;
- clear unsupported results when dependencies or APIs are unavailable.

## Files

Code:
- `quantumbridge/compat/qiskit_algorithms/algorithms_native.py`
- `quantumbridge/compat/qiskit_algorithms/vqe_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/qaoa_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/grover_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/result_adapter.py`
- `quantumbridge/compat/qiskit_algorithms/warnings.py`
- `quantumbridge/compat/qiskit_algorithms/examples.py`
- `quantumbridge/schema/algorithms_results.py`

Examples:
- `examples/qiskit_algorithms_vqe_quantumbridge.py`
- `examples/qiskit_algorithms_qaoa_quantumbridge.py`
- `examples/qiskit_algorithms_grover_quantumbridge.py`

Tests:
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

## Validation

Final validation must include:

```bash
python3 -m py_compile quantumbridge/compat/qiskit_algorithms/*.py quantumbridge/schema/*.py examples/qiskit_algorithms_vqe_quantumbridge.py examples/qiskit_algorithms_qaoa_quantumbridge.py examples/qiskit_algorithms_grover_quantumbridge.py
python3 examples/qiskit_algorithms_vqe_quantumbridge.py
python3 examples/qiskit_algorithms_qaoa_quantumbridge.py
python3 examples/qiskit_algorithms_grover_quantumbridge.py
pytest -q -rs tests/compat_qiskit_algorithms
pytest -q -rs tests/compat_qiskit_optimization
pytest -q -rs tests/compat_qiskit_finance
pytest -q -rs tests/ecosystem
pytest -q -rs
pytest --cov=quantumbridge
bash scripts/run_local_matrix.sh
git diff --check
```

## Boundaries

- No release.
- No tag.
- No vendored third-party source.
- No `site-packages`, wheel, dist-info, egg-info, or venv upload.
- No IBM Cloud access.
- No token reads or credential storage.
- No real hardware access.
- No UI implementation.
- No full replacement claim.
- No production parity claim.

## Next Step

Stage 9D should harden Qiskit Nature executable chemistry workflows such as H2
and LiH, while continuing the ecosystem parity pattern: executable proof,
example, tests, result schema, warnings, provenance, and visualization
readiness.
