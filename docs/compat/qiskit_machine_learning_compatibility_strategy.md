# Qiskit Machine Learning Compatibility Strategy

Status: Stage 7 planning
Detailed companion: `docs/compat/strategy/qiskit_machine_learning_compatibility_strategy.md`

## Scope

Neural networks, SamplerQNN, EstimatorQNN, TorchConnector, kernels, classifiers, datasets, losses, and optimizer integration surfaces.

## Non-goals

No production ML training, accuracy, dataset, or model governance claim.

## Optional Dependency

Install with `.[qiskit-machine-learning]`.

## Inventory Status

Current local environment records dependency-not-installed placeholders; remote extra CI should validate installed inventory.

## Adapter Status

Level 0/1 scaffold only.

## Native Status

No native Qiskit ML clone.

## Unsupported Status

Training loops, model persistence, production inference, and full Torch integration are unsupported.

## Tests

Tests cover EstimatorQNN/SamplerQNN, kernels, classifiers, TorchConnector lane, result wrapper, provenance, and unsupported warnings.

## Legal / Attribution

Qiskit Machine Learning remains upstream. No source is vendored.

## Risk

High due to optional ML backend stacks, Torch compatibility, and API drift.
