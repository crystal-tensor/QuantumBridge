# pennylane Coverage Matrix

## Stage 11H Native Mixed-State Execution

Native QNode now accepts DensityMatrixDevice, inline CPTP channels, state and
reduced-density outputs, expectation/variance, seeded samples and shadows.
Optional default.mixed comparisons validate complex density matrices and
observables, including the corrected standard PhaseDamping parameterization.

Evidence: tests/qml/test_mixed_qnode_native.py and
tests/devices/test_density_matrix_device.py. This is not a complete PennyLane
device factory, plugin, capture, shot-vector or autodifferentiation protocol.
The matrix below remains a historical public-name inventory, not proof of parity.

## Historical Inventory

Generated from runtime public-name introspection. No upstream source, tests, comments, or documentation text is copied.

- Installed: True
- Upstream version: 0.44.1
- Inventory generated: true
- Public API count: 19
- QuantumBridge coverage level: 0

| Upstream Package | Module | Public API | Type | QuantumBridge Level | Mode | Dependency Extra | Test | Risk | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pennylane | pennylane.devices | DefaultClifford | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | DefaultGaussian | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | DefaultMixed | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | DefaultQubit | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | DefaultQutrit | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | DefaultQutritMixed | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | Device | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | DeviceCapabilities | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | ExecutionConfig | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | LegacyDevice | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | LegacyDeviceFacade | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | MCMConfig | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | NullQubit | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | QubitDevice | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | QutritDevice | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | ReferenceQubit | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | Tracker | class | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | device | function | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| pennylane | pennylane.devices | refresh_devices | function | 0 | Inventory/Passthrough scaffold | pennylane-full | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
