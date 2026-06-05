# PennyLane Full Coverage Strategy

Status: Stage 7 planning  
Detailed companion: `docs/compat/strategy/pennylane_full_coverage_strategy.md`

## Scope

PennyLane operations, measurements, QNode, devices, tapes, transforms, gradients, qchem, templates, resources, qnn/qaoa/qcut/shadows/data/math surfaces, interfaces, Catalyst planning, and plugin inventory.

## Non-goals

No full PennyLane replacement, no full plugin ecosystem parity, no official endorsement, no production qchem claim, and no vendored PennyLane source.

## Optional Dependency

PennyLane is installed through `pennylane` or `pennylane-full`; plugin dependencies remain separate user-managed environments.

## Inventory Status

Stage 7 generates PennyLane full-ecosystem JSON and Markdown matrices from runtime public-name introspection.

## Adapter Status

New full-ecosystem modules are Level 0/1 scaffolds. Existing P1 observable/tape support remains the small Level 2 subset.

## Native Status

Native work stays limited to QuantumBridge core abstractions, not PennyLane's full runtime.

## Unsupported Status

Full plugin execution, Catalyst integration, TensorFlow parity, full qchem workflows, and all transform/device behavior are unsupported.

## Tests

Smoke tests cover category inventory, QNode smoke execution when installed, schema wrapping, provenance, and unsupported warnings.

## Legal / Attribution

PennyLane remains an upstream project. QuantumBridge uses the name only for compatibility and attribution.

## Risk

High-risk areas are plugin version drift, qchem domain assumptions, interface backends, and transform semantics.
