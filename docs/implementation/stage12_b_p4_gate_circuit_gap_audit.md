# Stage 12-B P4 Gate/Circuit Gap Audit

Starting local main HEAD: 7a7740e7500b7d0c5bc5569fea06dad5897d399f; previous
tested CODE c5a9f90164087fabb2a2df0b53e9fd75f7d3e8f5. Previous goal turn was
progress: actual P3 code, terminal final gates and normal scoped commits.
Cached origin/main is not live remote evidence. No push or authorization retry.
The existing Studio/Router changes are protected, not part of this batch.

## Authoritative Starting Code

Instruction is an existing frozen native data object, not a unitary promise.
Its circuit definitions may include measurements/classical state. Circuit
append eagerly expands every Instruction definition; this cannot implement
observable one-level custom Gate decomposition. There is no native Gate class
or Circuit.to_gate/decompose/repeat/tensor at the starting CODE. Existing
compose/inverse/integer power, UUID/vector/formal parameter mapping and native
math/derivative/device engines are real and reused, not rewritten.

Circuit.control constructs numerical matrices and rejects unbound symbolic
phase. This is distinct from a symbolic Gate control with deferred binding.
QPY v13 explicitly rejects custom instruction records. IR/source export has no
native Gate graph record. Existing parser gate definitions lower to primitive
operations; they are not a complete owned Gate lifecycle/structure contract.

## Current Native Work

An independent unitary Gate subclass, ControlledGate and validated owned
definition graph now reuse Operation/Circuit. Gate append preserves a real
node, not an inventory entry or hidden flattened layer list. Circuit.decompose
expands exactly one layer per repetition; lower performs bounded execution
expansion through the same structure. Identity/formal params/phase are preserved
into existing native devices, Compiler and recorded quantum derivatives.
Circuit.repeat and tensor operate on real structure and classical wire maps.
Public tensor qubits put the other circuit first; native state matrices remain
wire-major, so raw native matrices use the corresponding reversed bit convention.

Implemented execution boundaries include nonunitary/dynamic Gate rejection,
copy ownership, namespace/width revalidation after definition mutation,
simultaneous parameter binding, integer powers, bounded numerical principal
fractional powers, controls/open ctrl_state and symbolic relative global phase.
Generic controlled primitives have explicit missing derivative-recipe rejection;
the implemented single-control rotation/phase paths reuse native recipes.

## Public Evidence And Remaining P4 Work

Actual public Qiskit 2.4.1/2.6.0 probes use public constructors/methods only.
Both reject classical bits/reset/barrier/delay in to_gate. Circuit.repeat at
negative/zero returns empty, while Gate.repeat rejects those counts. Both
accept bool counts; native rejects them explicitly. Full parameter_map keys
are required, including numeric/expression replacements. Public annotated
objects are not Gate/Instruction. These differences must not be guessed away.
Primary references: [Gate API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.Gate)
and public QuantumCircuit calls. No upstream implementation/test source ports.

P4 is IN PROGRESS, not accepted as complete. Remaining required work includes
standard primitive definition decomposition, full annotation object contracts,
complete Gate mutable params/return/error ABI, full Gate definition-aware IR/QASM
and broader custom QPY records, dynamic composition, empty zero-width circuits,
shared construction/transport budgets and the entire final five-environment/
coverage/original-matrix acceptance. Later P4-S implements owned Gate IR,
supported source declarations and standard QPY v13 g/c records with actual
public bilateral tests. Unsupported format branches still reject. The new
source writer safely renames custom declarations, retaining name-collision
semantics; a separate public QASM2 exporter loss remains an observed failure.
See stage12_b_p4s_custom_gate_interchange_report.md for current evidence and
remaining format boundaries. Earlier R3 was before these changes.
Do not use P3 coverage or earlier mixed-runtime focuses as this batch's final
acceptance, and do not infer full class/SDK parity from current tests.

## P4-T Development Checkpoint

Native ordered annotations/resolution,31 standard definition accessors, actual
native state/derivative execution and structured annotation IR are now added.
They close supported parts of the earlier gaps, not original P4 or full SDK
acceptance. See stage12_b_p4t_annotated_operation_report.md for the frozen
runtime and terminal development gates. Native QPY annotation records still
reject, even though public QPY v11+ specifies them. Explicit source/QPY Gate
lowering changes unresolved object structure and must not be called lossless.

Fresh public2.4.1/2.6.0 ABI calls against the R2 snapshot, logs
/tmp/qb-stage12b-p4t-abi241.log and /tmp/qb-stage12b-p4t-abi260.log, actually show:

| Contract | Public2.4.1 and2.6.0 | Native R2 |
| --- | --- | --- |
| Generic control omitted /False /None | ControlledGate | ControlledGate |
| Generic control True | AnnotatedOperation | AnnotatedOperation |
| Generic control annotated signature default | None; explicitNone warns | False; not full warning/signature ABI |
| Annotation params | base mutable list | base tuple /explicit replacement |
| Annotation validate_parameter(.4) | returns float | missing AttributeError |
| RX standard inverse/power annotated=True | concrete RXGate | native builder returns generic annotation |
| Annotation construction over reset | constructs deferred object | rejects nonunitary base early |

These literal probes use public methods/introspection only, not upstream
implementation or tests. Public documentation deprecation language is not
substituted for the measured default return class. The new native31-name
definition builder is not a family of specialized public standard subclasses.
Shared mutable Python ParameterVector owner identity across independent base
copies is not promised; UUID/root/index identity and execution binding are tested.
Remaining mutable/list/signature/error behavior, validate_parameter, arbitrary
Operation compatibility and complete P4 acceptance are still substantive work.
