# Stage 5 P1 Entry Gate v0.1

Status: Accepted for controlled P1 expansion  
Date: 2026-06-04  

## 1. P0 Acceptance Review summary

Stage 4 P0 hardening concluded that QuantumBridge is an experimental P0 subset suitable as an internal SDK baseline, not as a full Qiskit or PennyLane replacement.

## 2. Why P1 can start

- P0 core tests pass.
- Qiskit optional adapter tests execute when Qiskit is available.
- PennyLane adapter tests skip clearly when PennyLane is unavailable.
- Legal attribution files and source migration ledger exist.
- Packaging metadata and optional extras exist.

## 3. Capabilities that cannot be claimed externally

- Full Qiskit parity.
- Full PennyLane parity.
- Full OpenQASM grammar.
- Full compiler/transpiler.
- Full Aer/noise model.
- Full qchem or plugin ecosystem.
- Production hardware provider support.

## 4. P1 entry risks

- PennyLane is unavailable in the current bare test environment.
- Compiler and visualization are still not production ready.
- QASM parser remains subset-based.
- Noise support is basic and metadata-oriented.

## 5. P0 leftovers P1 must address first

- CI dependency matrix.
- PennyLane installed-environment test coverage.
- QASM parser robustness.
- Compiler pass testability.
- Basic noise/error model.

## 6. PennyLane optional tests skip reason

PennyLane tests skip with `optional dependency unavailable: pennylane` in the current bare environment. The adapter code remains optional and tests are ready to execute when the extra is installed.

## 7. Qiskit optional tests passing scope

Qiskit tests cover basic circuit import/export, IR roundtrip, parameterized gate, measurement, and counts result adaptation.

## 8. Recommendation

Proceed to Stage 5 P1 controlled expansion. Do not proceed to P2 until P1 review confirms the expanded subset is stable.

