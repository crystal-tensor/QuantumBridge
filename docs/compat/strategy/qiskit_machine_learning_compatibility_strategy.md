# Qiskit Machine Learning Compatibility Strategy

Status: Stage 7 planning
Mode: optional dependency and adapter scaffold

## Goal

QuantumBridge will inventory QNN, kernel, classifier, and Torch connector surfaces from Qiskit Machine Learning and prepare result wrappers with provenance metadata.

## Initial Coverage

Stage 7 is inventory/passthrough only. Training loops, accuracy claims, dataset handling, and production ML workflows are not implemented.

## Future Adapter Candidates

- QNN result schema wrapping;
- kernel matrix result normalization;
- classifier metadata and prediction result wrappers;
- Torch connector dependency lane review.

## Risk Controls

Optional ML dependencies must stay isolated from core install. Tests must validate adapter contracts and dependency handling, not reproduce upstream tests.
