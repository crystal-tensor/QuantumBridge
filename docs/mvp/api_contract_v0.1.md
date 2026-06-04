# QuantumBridge SDK API Contract v0.1

Status: Draft  
Date: 2026-06-04  
Source basis: `functional_spec_v0.1.md`, `mvp_scope_v0.1.md`, and independently authored MVP architecture.  

This document defines interface contracts and usage sketches only. It contains no SDK implementation code.

## 1. API contract principles

- APIs use generic quantum computing vocabulary where necessary.
- API names and examples are independently authored for QuantumBridge.
- The contract favors small, explicit objects over hidden global state.
- MVP APIs must be stable enough for behavior tests, but may be refined before public release.
- Error messages must be written later in QuantumBridge wording and must not copy any third-party messages.

## 2. Package-level concepts

Primary concepts:

- `Circuit`: ordered quantum program description.
- `Parameter`: named symbolic scalar for later binding.
- `Operation`: value-like description of a gate or abstract operation.
- `Measurement`: value-like description of a requested measurement output.
- `StatevectorDevice`: exact pure-state execution device.
- `ShotSampler`: finite-shot sampler over a probability distribution or circuit execution.
- `Result`: serialization-ready execution or algorithm output.
- `Observable`: Hermitian quantity to evaluate.
- `Hamiltonian`: weighted sum of observables.
- `parameter_shift`: gradient method for supported scalar expectation objectives.
- `run_vqe`: MVP VQE orchestration contract.
- `run_qaoa`: MVP QAOA orchestration contract.

## 3. Circuit API

Constructor contract:

```text
Circuit(num_qubits, num_bits=0, name=None, metadata=None)
```

Behavior:

- Creates a circuit with fixed quantum and classical storage sizes.
- Quantum wires are addressed by non-negative integer indices in MVP.
- Classical bits are addressed by non-negative integer indices in MVP.
- The circuit initially has no operations and no measurements.

Required methods:

| Method | Contract |
| --- | --- |
| `x(q)` | Append X on one quantum wire |
| `y(q)` | Append Y on one quantum wire |
| `z(q)` | Append Z on one quantum wire |
| `h(q)` | Append H on one quantum wire |
| `s(q)` | Append S on one quantum wire |
| `t(q)` | Append T on one quantum wire |
| `rx(theta, q)` | Append RX with numeric or named parameter |
| `ry(theta, q)` | Append RY with numeric or named parameter |
| `rz(theta, q)` | Append RZ with numeric or named parameter |
| `phase(theta, q)` | Append phase rotation with numeric or named parameter |
| `cx(control, target)` | Append controlled-X over two distinct wires |
| `cz(control, target)` | Append controlled-Z over two distinct wires |
| `swap(a, b)` | Append SWAP over two distinct wires |
| `unitary(matrix, wires, name=None)` | Append custom unitary with explicit target wires |
| `measure(q, bit=None)` | Declare computational-basis measurement |
| `copy()` | Return an independent circuit value |
| `compose(other, wire_map=None, bit_map=None)` | Return or create composed circuit under explicit mapping |
| `bind(mapping)` | Bind parameters to numeric values |
| `to_ir()` | Return QuantumBridge IR draft object |
| `to_openqasm()` | Export supported circuit subset as text |
| `metrics()` | Return width, operation counts, measurement counts, and simple depth estimate |

Usage sketch:

```text
Create a two-qubit circuit with two classical bits.
Append H on wire 0.
Append CX from wire 0 to wire 1.
Measure wire 0 into bit 0 and wire 1 into bit 1.
Run the circuit on a statevector device or shot sampler.
```

## 4. Gate / Operation API

Operation contract:

```text
Operation(name, targets, controls=None, parameters=None, metadata=None)
```

Required fields:

- `name`: QuantumBridge operation identifier from the supported MVP set or custom unitary label.
- `targets`: ordered quantum wire references.
- `controls`: ordered quantum wire references, empty for ordinary gates.
- `parameters`: numeric values or named parameters.
- `metadata`: optional dictionary for user labels, source notes, or export hints.

Validation rules:

- Wires must exist in the parent circuit.
- A wire may not appear twice in the same operation role set.
- Operation arity must match the operation definition.
- Custom unitary matrix dimensions must match target wire count.
- Parameterized gates must be bound to numeric scalar values before numeric execution.

MVP operation names:

- `x`, `y`, `z`, `h`, `s`, `t`
- `rx`, `ry`, `rz`, `phase`
- `cx`, `cz`, `swap`
- `unitary`

## 5. Measurement API

Measurement contract:

```text
Measurement(kind, wires=None, bits=None, observable=None, metadata=None)
```

MVP measurement kinds:

- `state`: final statevector where supported.
- `probability`: exact probabilities over all or selected wires.
- `sample`: shot samples or counts.
- `expectation`: scalar expectation for an observable.
- `computational`: explicit wire-to-bit measurement stored in a circuit.

Circuit measurement method:

```text
measure(q, bit=None)
```

Behavior:

- If `bit` is provided, the measurement maps quantum wire `q` to classical bit `bit`.
- If `bit` is omitted, MVP may allocate the next available classical bit only if classical storage exists and the rule is documented.
- Measurements are readout requests; statevector simulation may still compute exact state before readout unless a future non-unitary measurement model is introduced.

## 6. Device API

Statevector device contract:

```text
StatevectorDevice(max_qubits=None, precision="complex128", metadata=None)
```

Required methods:

| Method | Contract |
| --- | --- |
| `validate(circuit)` | Return or raise validation outcome for supported MVP behavior |
| `run(circuit, parameters=None, measurements=None)` | Execute supported circuit and return Result |
| `state(circuit, parameters=None)` | Return final statevector through Result or direct exact-state contract |
| `probabilities(circuit, wires=None, parameters=None)` | Return exact probabilities |
| `expectation(circuit, observable, parameters=None)` | Return scalar expectation |
| `properties()` | Return supported operations, precision, and capability metadata |

Shot sampler contract:

```text
ShotSampler(shots, seed=None, base_device=None, metadata=None)
```

Required behavior:

- Uses exact probabilities from the base statevector execution unless supplied a compatible probability distribution.
- Returns counts and empirical probabilities.
- Honors seed for deterministic testability.

## 7. Result API

Result fields:

- `kind`: execution, sample, expectation, algorithm, or export.
- `statevector`: optional complex state representation.
- `probabilities`: optional probability mapping.
- `counts`: optional bitstring-count mapping.
- `expectations`: optional scalar or named expectation mapping.
- `parameters`: optional parameter bindings.
- `metadata`: device, shots, seed, warnings, timing placeholders, and provenance notes.
- `trace`: optional optimizer or algorithm trace.

Required accessors:

| Accessor | Contract |
| --- | --- |
| `statevector()` | Return exact state if present |
| `probabilities()` | Return exact or empirical probabilities with metadata distinction |
| `counts()` | Return counts if present |
| `expectation_values()` | Return expectation values if present |
| `metadata()` | Return metadata mapping |
| `to_dict()` | Return serialization-ready mapping |
| `to_json()` | Return JSON text for supported field types |

Serialization rule:

- Complex amplitudes must use an explicit JSON-compatible representation, such as pairs or structured real/imag records. The exact representation is fixed in `ir_design_v0.1.md` and result tests.

## 8. Differentiation API

Parameter-shift contract:

```text
parameter_shift(objective, parameters, shift=pi/2, method_options=None)
```

Inputs:

- `objective`: scalar callable contract that accepts numeric parameter values and returns an expectation-like scalar.
- `parameters`: one scalar value, a list of scalar values, or a named mapping.
- `shift`: default shift for supported Pauli-generator rotations.
- `method_options`: optional metadata such as selected parameter indices and device mode.

Outputs:

- Numeric gradient in the same parameter shape when practical.
- Gradient metadata including method name, shift amount, evaluated parameter identifiers, and unsupported parameter notes.

MVP support:

- RX, RY, RZ parameters in scalar expectation objectives.
- Exact statevector objectives by default.

## 9. VQE API

VQE contract:

```text
run_vqe(hamiltonian, ansatz, initial_parameters, device, optimizer=None, steps=None, callback=None, options=None)
```

Inputs:

- `hamiltonian`: weighted sum of supported observables.
- `ansatz`: user-provided circuit-construction contract that accepts parameter values and returns a circuit.
- `initial_parameters`: numeric starting values.
- `device`: compatible device for expectation evaluation.
- `optimizer`: MVP optimizer contract, defaulting to a simple gradient descent design.
- `steps`: maximum optimization steps.
- `callback`: optional observation hook.
- `options`: tolerances, learning rate, gradient method, and metadata.

Outputs:

- Result with final energy, final parameters, objective trace, optimizer metadata, and optional callback metadata.

## 10. QAOA API

QAOA contract:

```text
run_qaoa(graph_edges, depth, initial_parameters, device, optimizer=None, objective="maxcut", callback=None, options=None)
```

Inputs:

- `graph_edges`: list of two-node edges for a small unweighted graph.
- `depth`: positive integer layer count.
- `initial_parameters`: numeric angles for cost and mixer layers.
- `device`: compatible statevector device.
- `optimizer`: MVP optimizer contract.
- `objective`: MVP supports MaxCut only.
- `callback`: optional observation hook.
- `options`: learning rate, steps, seed, and trace options.

Outputs:

- Result with final objective estimate, final parameters, cut-value metadata, and trace.

## 11. OpenQASM export API

Export contract:

```text
circuit.to_openqasm(version="2-compatible-subset", include_measurements=True, parameter_mode="numeric")
```

Behavior:

- Export declared quantum and classical storage.
- Export supported MVP gates.
- Export numeric rotation angles.
- Export measurement mappings when present and requested.
- Reject unsupported gates or unbound parameters unless the selected mode explicitly supports symbolic text.

Output:

- Text plus optional export metadata in a Result-like export record when requested by future API.

## 12. API example use sketches

Bell-state sketch:

```text
Circuit with 2 quantum wires and 2 classical bits.
Apply H to wire 0.
Apply CX from wire 0 to wire 1.
Measure both wires.
Run with ShotSampler(shots=1000, seed=7).
Read counts from Result.
```

Gradient sketch:

```text
Create Parameter named theta.
Create one-qubit circuit with RY(theta).
Define expectation of PauliZ on wire 0 through StatevectorDevice.
Call parameter_shift over theta.
Expect the result to match -sin(theta) for this case.
```

VQE sketch:

```text
Create Hamiltonian with one PauliZ term.
Provide an ansatz contract using one RY parameter.
Run VQE with an exact statevector device and simple gradient descent.
Inspect final energy and trace.
```

These are usage sketches only, not implementation code.

