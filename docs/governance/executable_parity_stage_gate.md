# Executable Parity Stage Gate

Status: Stage 9G governance baseline

This gate defines when a QuantumBridge ecosystem lane may move from inventory,
passthrough, or schema coverage to a documented executable subset.

## Promotion Criteria

An executable subset must include:

- a QuantumBridge-owned implementation path or a clearly labeled optional
  upstream passthrough path;
- at least one runnable example;
- result schemas with warnings and provenance;
- unsupported metadata for missing optional dependencies;
- no cloud, token, credential, or hardware access unless explicitly approved;
- tests for native behavior, unavailable dependency behavior, warnings,
  provenance, and serialization;
- README, matrix, risk, third-party notice, and migration-ledger updates.

## Non-Goals

Promotion to an executable subset does not imply:

- full upstream replacement;
- production equivalence;
- official upstream endorsement;
- copied upstream source or documentation;
- release readiness.

## Stage 9D Application

Qiskit Nature is promoted only for educational H2 and LiH exact-diagonalization
workflows. Production chemistry, molecular design, materials band-gap
calculation, and full Qiskit Nature parity remain out of scope.

## Stage 9E Application

Qiskit Machine Learning is promoted only for educational toy-dataset quantum
kernel, kernel classifier, QNN forward, and QNN classifier workflows. Production
ML, high-risk automated decisions, training-performance guarantees, and full
Qiskit Machine Learning parity remain out of scope.

## Stage 9F Application

Qiskit Aer-style support is promoted only for educational small-circuit
statevector, qasm-style counts, and simple sampling-noise workflows. Production
simulation, Aer noise-model parity, cloud execution, token handling, and full
Qiskit Aer parity remain out of scope.

## Stage 9G Application

Mitiq / error mitigation is promoted only for educational native zero-noise
extrapolation and readout-mitigation workflows over small simulated circuits.
Production error mitigation, hardware calibration parity, cloud execution,
token handling, hardware access, and full Mitiq parity remain out of scope.

## Stage 9H Application

PennyLane-Qiskit is promoted only for an educational bidirectional basic-gate
bridge and Bell-state equivalence proof. Full plugin replacement, full Qiskit
or PennyLane parity, advanced device/transform/gradient semantics, cloud
execution, token handling, hardware access, and production parity remain out of
scope.

## Stage 9I Application

Qiskit Experiments and Qiskit Dynamics are promoted only for deterministic
educational offline workflows: Rabi, T1, Ramsey, Z precession, Rabi drive, and
dephasing metadata. Hardware calibration, production experiment analysis,
production dynamics simulation, full upstream replacement, cloud execution,
token handling, and hardware access remain out of scope.

## Stage 9J Application

MQT Core / DDSIM / QMAP compatibility is promoted only for educational
clean-room workflows: Core-like circuit dictionaries and QASM subset artifacts,
DDSIM-like small-circuit simulation with decision-diagram-inspired metadata,
and QMAP-like greedy routing with SWAP insertion and execution comparison.
Full MQT replacement, decision-diagram parity, optimal mapping, production
compiler/simulator/mapper parity, official endorsement, cloud execution, token
handling, and hardware access remain out of scope.

## Stage 9K Application

TorchQuantum / PyTorch-style QML compatibility is promoted only for educational
TensorLike adapters, native small-circuit quantum layer forward passes,
deterministic toy classifier training, optional torch tensor interoperability,
optional upstream TorchQuantum boundary metadata, schema serialization,
warnings, provenance, examples, and tests.

Full TorchQuantum replacement, PyTorch replacement, production QML training,
high-risk automated decision support, official endorsement, cloud execution,
token handling, and hardware access remain out of scope.

## Stage 10A Application

QOS-UQCI and Quafu compatibility is promoted only for offline mock backend
execution. The accepted executable proof is QuantumBridge IR converted to
QOS-UQCI job specs and Quafu-compatible payloads, then executed through
QuantumBridge local simulation with result schemas, warnings, and provenance.

Production QOS runtime, production backend execution, real cloud submission,
token handling, real hardware access, and official endorsement claims are
excluded.

## Stage 10B Application

Benchpress / benchmarking compatibility is promoted only for deterministic
local validation benchmarks over QuantumBridge-owned educational workloads. The
accepted executable proof is a benchmark registry, default suites, runner,
metrics, result schemas, JSON / Markdown reports, examples, and tests.

Full Benchpress replacement, official benchmark claims, production performance
ranking, cloud execution, token handling, real hardware access, and official
endorsement claims are excluded.
