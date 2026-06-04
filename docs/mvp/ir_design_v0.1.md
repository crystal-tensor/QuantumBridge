# QuantumBridge IR Design v0.1

Status: Draft  
Date: 2026-06-04  
Source basis: `functional_spec_v0.1.md`, MVP scope, public OpenQASM interchange concepts, and independently authored QuantumBridge design.  

This document is design-only. It contains no SDK implementation code and does not copy any existing project's IR structure.

## 1. IR design goals

QuantumBridge IR v0.1 is a compact, versioned, serialization-ready representation used to move a circuit between:

- Core Circuit API.
- Statevector Device validation and execution.
- Shot Sampler probability source.
- Observable and expectation evaluation.
- OpenQASM export.
- Behavior tests and result provenance.

The IR should be explicit enough to avoid hidden global state, but small enough that MVP implementation remains inspectable.

## 2. IR non-goals

IR v0.1 does not attempt to represent:

- Full hardware scheduling.
- Full classical computation.
- Dynamic circuits.
- Full compiler pass annotations.
- Noise operations.
- Tensor-network execution graphs.
- Full OpenQASM language coverage.
- Any third-party internal intermediate representation.

## 3. Core IR objects

### 3.1 Program

Program is the top-level object.

Required fields:

- `ir_version`: version string such as `qb-ir-v0.1`.
- `program_id`: optional user or generated identifier.
- `name`: optional user-facing name.
- `registers`: quantum and classical storage descriptions.
- `parameters`: declared named parameters.
- `instructions`: ordered unitary or abstract operations.
- `measurements`: explicit measurement requests.
- `observables`: optional observable definitions used by expectation requests.
- `execution`: optional execution request metadata such as shots and seed.
- `metadata`: user and system metadata.

### 3.2 Register

Quantum register fields:

- `kind`: quantum.
- `size`: non-negative integer.
- `labels`: optional per-wire labels.

Classical register fields:

- `kind`: classical.
- `size`: non-negative integer.
- `labels`: optional per-bit labels.

MVP design uses a single flat quantum storage and a single flat classical storage. Named sub-registers are deferred.

### 3.3 Parameter

Parameter fields:

- `name`: QuantumBridge parameter name.
- `value`: optional numeric scalar.
- `domain`: optional numeric domain hint.
- `metadata`: optional notes.

Rules:

- Unbound parameters may exist in IR.
- Numeric execution requires all operation parameters that affect simulation to be bound.
- Numeric OpenQASM export requires all exported numeric angles to be bound unless symbolic export mode is later introduced.

### 3.4 Instruction

Instruction fields:

- `op`: operation identifier from QuantumBridge MVP operation set.
- `targets`: ordered quantum wire indices.
- `controls`: ordered quantum wire indices.
- `params`: ordered numeric values or parameter references.
- `matrix_ref`: optional custom unitary reference.
- `metadata`: optional labels, tags, or export hints.

Supported MVP instructions:

- `x`, `y`, `z`, `h`, `s`, `t`
- `rx`, `ry`, `rz`, `phase`
- `cx`, `cz`, `swap`
- `unitary`

Instruction validation:

- Target and control indices must refer to declared quantum wires.
- Controls and targets must be disjoint.
- Arity must match the operation.
- Parameter count and parameter types must match the operation.
- Custom unitary matrix reference must resolve to a matrix compatible with target count before execution.

### 3.5 Measurement

Measurement fields:

- `kind`: computational, probability, sample, state, expectation.
- `wires`: selected quantum wires, optional for full-register requests.
- `bits`: selected classical bits when applicable.
- `observable_id`: reference for expectation measurement.
- `metadata`: optional notes.

Computational measurement:

- Maps selected quantum wires to selected classical bits.
- Does not imply non-unitary collapse during exact statevector evolution in MVP unless a future execution mode states otherwise.

### 3.6 Observable

Observable fields:

- `id`: unique within the IR program.
- `kind`: identity, pauli_x, pauli_y, pauli_z, pauli_word, or hamiltonian.
- `wires`: quantum wire indices.
- `terms`: weighted observable references for Hamiltonian.
- `coefficient`: numeric scalar for terms where relevant.
- `metadata`: optional notes.

Hamiltonian representation:

- A Hamiltonian is a list of weighted terms.
- Each term has a real coefficient and a supported observable.
- MVP Hamiltonian coefficients are numeric real values.

### 3.7 Execution request

Execution fields:

- `mode`: statevector, sample, expectation, algorithm, or export.
- `shots`: optional positive integer for sampling.
- `seed`: optional deterministic random seed.
- `requested_outputs`: state, probabilities, counts, expectation values, metadata.

Execution request is optional because a Circuit-to-IR conversion may describe a program without deciding how it will be run.

## 4. Expressing gates, parameters, measurements, bits, shots, and observables

### 4.1 Gates

Each gate is an Instruction with:

- `op` for gate identity.
- `targets` for acted-on wires.
- `controls` for controlled behavior.
- `params` for angles or references.

MVP does not encode decompositions in IR. A future compiler layer may add decomposition records or transformed programs.

### 4.2 Parameters

Parameters are referenced by name or stable parameter identifier. A parameter reference in an instruction points to a declaration in the `parameters` section.

Binding behavior:

- Circuit binding produces an IR with numeric parameter values resolved for bound names.
- Partial binding is allowed for design-time IR but not for numeric simulation.

### 4.3 Measurements and classical bits

Computational measurements map quantum wires to classical bits. If no classical bits are declared, probability and state requests may still be represented, but count-producing measurement requires either declared bits or an explicit output convention.

MVP recommendation:

- For `sample` mode, if no classical bits are declared, samples are returned as bitstrings over measured quantum wires.
- For explicit circuit measurements, classical bit count must cover requested mappings.

### 4.4 Shots

Shots are execution metadata, not a circuit property. The same circuit may be run exactly or sampled with different shot counts.

### 4.5 Observables

Expectation requests reference observables. Observables are separate from unitary instructions so that the same circuit can be evaluated against multiple quantities.

## 5. IR 与 Circuit 的关系

Circuit is user-facing and ergonomic. IR is explicit and serialization-ready.

Conversion from Circuit to IR:

- Copies declared wire counts.
- Converts each operation into an ordered instruction.
- Converts each measurement into a measurement record.
- Declares parameters discovered in operations.
- Carries user metadata where safe.

Conversion from IR to Circuit:

- Deferred for MVP except for internal validation experiments.
- Future conversion must reject unsupported IR records rather than guessing.

## 6. IR 与 Device 的关系

Device may accept a Circuit directly or receive IR produced from a Circuit. The statevector device validates:

- IR version compatibility.
- Supported operation set.
- Bound numeric parameters.
- Wire counts within device limit.
- Measurement kinds it can produce.
- Observable support for expectation requests.

Device must not mutate IR. Results reference IR metadata or program ID for traceability.

## 7. IR 与 OpenQASM 的关系

OpenQASM export is an output projection from QuantumBridge IR.

Supported export concepts:

- Quantum storage declaration.
- Classical storage declaration.
- Supported MVP gates.
- Numeric rotation parameters.
- Computational-basis measurements.

Unsupported export concepts in MVP:

- Custom unitary matrix export unless a future named-gate format is explicitly defined.
- Unbound parameter export in numeric mode.
- Dynamic classical conditions.
- Hardware timing, noise, or calibration metadata.

Export rule:

- If IR contains unsupported export records, export fails with a QuantumBridge-authored serialization diagnostic. It must not silently omit operations.

## 8. IR serialization draft

Preferred serialization shape:

```text
{
  "ir_version": "qb-ir-v0.1",
  "name": "optional-name",
  "registers": {
    "quantum": {"size": 2, "labels": ["q0", "q1"]},
    "classical": {"size": 2, "labels": ["c0", "c1"]}
  },
  "parameters": [
    {"name": "theta", "value": null}
  ],
  "instructions": [
    {"op": "h", "targets": [0], "controls": [], "params": []},
    {"op": "cx", "targets": [1], "controls": [0], "params": []}
  ],
  "measurements": [
    {"kind": "computational", "wires": [0], "bits": [0]},
    {"kind": "computational", "wires": [1], "bits": [1]}
  ],
  "observables": [],
  "execution": {"mode": "sample", "shots": 1000, "seed": 7},
  "metadata": {}
}
```

The shape above is a design sketch, not implementation code.

## 9. Versioning

IR records must include a version. MVP implementation may reject unknown major/minor versions. Future versions should preserve stable behavior through explicit migration rules rather than implicit interpretation.

## 10. Clean-room rationale

This IR is independently described around QuantumBridge's MVP handoff needs. It is not a reproduction of any existing SDK's IR, graph structure, circuit serialization, or compiler representation.

