# Stage 9J MQT Core / DDSIM / QMAP Compatibility Slice Report

Status: implemented locally; push pending final validation.

## Scope

Stage 9J adds a clean-room educational MQT compatibility slice:

- MQT Core-like circuit dictionaries and QuantumBridge IR roundtrip.
- MQT Core-like QASM subset export/import.
- DDSIM-like statevector and counts execution over QuantumBridge native simulation.
- Decision-diagram-inspired metadata.
- QMAP-like topology validation, greedy CNOT routing, SWAP insertion, mapping cost, and original-vs-mapped execution comparison.
- Optional upstream MQT package boundary helpers.

## Non-Goals

This stage does not claim full MQT Core replacement, full DDSIM replacement,
decision-diagram parity, full QMAP replacement, optimal mapping, production
compiler/simulator/mapper parity, official endorsement, cloud access, token
reads, hardware access, UI implementation, release readiness, or tag readiness.

## Executable Proof

The native examples are:

- `examples/mqt_core_like_circuit_quantumbridge.py`
- `examples/mqt_ddsim_like_simulation_quantumbridge.py`
- `examples/mqt_qmap_like_routing_quantumbridge.py`

The targeted test suite is `tests/compat_mqt`.

## Legal Boundary

No MQT, IBM, Qiskit, or third-party source files, documentation prose, UI,
branding, wheels, dist-info, egg-info, site-packages trees, virtual
environments, or vendored package artifacts were copied. Public project names
are used only to identify optional compatibility targets.

## Validation

Final validation must record:

- `python3 -m py_compile quantumbridge/compat/mqt/*.py quantumbridge/schema/*.py examples/mqt_core_like_circuit_quantumbridge.py examples/mqt_ddsim_like_simulation_quantumbridge.py examples/mqt_qmap_like_routing_quantumbridge.py`
- `python3 examples/mqt_core_like_circuit_quantumbridge.py`
- `python3 examples/mqt_ddsim_like_simulation_quantumbridge.py`
- `python3 examples/mqt_qmap_like_routing_quantumbridge.py`
- `pytest -q -rs tests/compat_mqt`
- full related suites, full pytest, coverage, local matrix, and `git diff --check`.
