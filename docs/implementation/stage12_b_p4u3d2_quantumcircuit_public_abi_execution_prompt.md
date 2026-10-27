# Stage 12-B P4-U3D2 Execution Prompt

Native QuantumCircuit Public ABI, CircuitInstruction / InstructionSet And Standard Bit-Graph Interchange

Status: ACTUALLY RECEIVED STAGE-INTERNAL TASK / NOT IMPLEMENTATION OR ACCEPTANCE.
This normalized transcription preserves all16 sections actually received.
It continues the entire existing U3D scope, not U4 or a reduced final goal.

## Actual Reading And Architecture Decision

Conversation: "Claude 代码泄漏与应对",
6a20d458-a76c-83ea-9b49-f8f0caedb3cf. Actual uncommitted foundation progress,
failures/repairs, RUNNING session80159 and the public/fluent return conflict
were sent. read_thread confirms completed source message
8a6532ab-1a19-4b8b-b7ab-758f348af39a, but only returns a content reference.
Actual Chrome rendering was read: later view AX534-1127 covers sections6-15
and completed-answer controls; scrolled view AX534-1174 covers the rest of
section0 through9; top view AX534-856 covers the complete review and start.
Together these cover the review and all16 sections. The earlier interrupted
stream was not treated as complete.

The collaborator supports a real native QuantumCircuit public class while
preserving fluent Circuit, but only with one authoritative operation store,
the same operation/parameter owners, resource limits and execution engines.
append and x/h builders return Circuit in the native extension but
InstructionSet in the public ABI; CircuitInstruction is a data context, not
the same object as an InstructionSet handle. Prefer a subclass or controlled
thin native class after actual code audit; do not synchronize two mutable
Circuit instances or introduce another simulator/compiler.

This is report-based guidance, not independent source/remote-CI review.
Foundation remains IN_PROGRESS. Standard noncanonical QPY/QASM Unsupported
cannot count as working interoperability; genuine standard records remain
required. At dispatch80159 was RUNNING; it subsequently naturally terminated
exit0 with1982passed/3xfailed/5warnings, so its initial wait condition is now
satisfied. That is development FOCUS, not frozen FULL acceptance.

## 0. Execution Conditions

Start from actual b443430 plus the existing uncommitted Bit/Register/zero-
width foundation. Recheck actual HEAD/worktree and retain that development.
Wait for80159 naturally and repair any real failure before new reds; do not
claim the unfrozen foundation passed FULL. This batch requires real native
QuantumCircuit public ABI, preserved fluent Circuit, CircuitInstruction,
InstructionSet, public builders/append broadcasting, from_instructions,
zero-width boundaries, supported standard QPYv13 bit/register records and
native IR/definition/parameter/lifetime protection. Full independent native
Qiskit/PennyLane replacement remains ACTIVE / INCOMPLETE.

## 1. Audit One Authoritative Store

Read Circuit construction/append/x/h/cx/rz/measure/reset, operations and
measurements, classical scopes, Bit graph, ParameterList/live owner views,
IR/QPY, Compiler, QNode and Statevector/Density/MPS. Determine the actual
authoritative storage. Never keep a second mutable operation list synchronized
through callbacks. First write three genuine architecture reds:

1. Circuit(1).append(XGate(),[0]) is its owner; QuantumCircuit(1).append
   returns InstructionSet and leaves one real public.data context.
2. QuantumCircuit.h(0) feeds native Operator and the independent Hadamard
   matrix without conversion into a detached Circuit instance.
3. Legal mutable Gate ownership through both entrances follows independently
   measured copy=True/False rules, invalidates caches, feeds current owners
   into QNode/Compiler and keeps data/execution equal without another store.

The concrete public class decides returns. No global compatibility toggle,
call-stack inference or unstable outward type. Audit builder call chains so
InstructionSet returns do not break internal fluent compiler assumptions.

## 2. Public Construction And Strict Native Admission

Observe actual2.4.1/2.6.0 constructor signatures/outcomes, including integer
widths, quantum/classical Registers, bit inputs and empty construction.
Illustrative QuantumCircuit(qubit0,qubit1) must first be observed; examples
are not proof that every illustrated form is legal. Cover actual supported
Qubit/Clbit/Register forms, widths/identity, names, full global phase, safe
metadata, invalid type/errors, zero width and typed variable declarations.
Reject foreign copy/iteration hooks before execution. Define auditable exact
native type sets and safe inheritance rules: no duck typing by names, but do
not accidentally reject legitimate native Ancilla/Qubit/Clbit variants by
requiring every valid object to have the exact base type.

## 3. CircuitInstruction And Executable Data

Implement CircuitInstruction(operation,qubits,clbits), operation/qubits/clbits,
replace, copy, and actual verified public params/name/is_control_flow
properties. Distinguish read-only/replacement contexts from mutation of
already inserted data. Actually observe in both versions: assigning a context
operation; replace returning a new object; data[index] assignment; and
InstructionSet updates of inserted operations. Do not make all context
attribute assignments live Circuit writes just to imitate linkage.

Required red: obtain ci=public.data[0], replacement=ci.replace(operation=ZGate()),
verify replacement.operation.name=="z" and the exact measured effect (or no
effect) on the original Circuit. Do not assume replace mutates its owner.

## 4. InstructionSet Real Handles

Public append/builders return actual native InstructionSet. Implement observed
contexts, qargs/cargs, add, supported inverse/modification, lifetime/stale-
handle checks, broadcast multi-operation handles and safe changes to the real
store. A handle is not an arbitrary writable pointer.

Initial red: qc=QuantumCircuit(2); handle=qc.x([0,1]); handle is InstructionSet;
len(qc.data)==2; native execution proves both inserted operations without a
reconstructed Circuit. Protect indices, bit identity, copies (old handles
cannot alter the copy), stale/replaced objects and atomic failure. Native
Circuit.x remains fluent and returns self.

## 5. Standard Builders' Return Policy

Actually observe at least30 independent builders in each public version.
Audit x/y/z/h/s/sdg/t/tdg/sx/sxdg, rx/ry/rz/p/u, cx/cy/cz/swap,
crx/cry/crz/cp/ccx, the actual public doubly-controlled-Z method spelling,
measure/reset/barrier/delay. The received display "cc z" is not permission
to invent a method name; observe the real API.

Do not merely wrap append and declare completeness: broadcasts differ;
single/multiple operands differ; measurement has classical operands; barrier
has variable quantum arity; delay has real duration/unit semantics; dynamic
contexts may restrict broadcasting; handles must match actual inserted data.

## 6. Atomic Append Broadcasting

Use the existing real Bit/Register graph for scalar int, Qubit/Clbit,
Register, slice, iterable/list/nested supported groups, noncontiguous maps,
control/target order, different qargs/cargs arities, duplicates, bounds, mixed
bit types and invalid broadcasting. Build a bounded validated insertion plan
and commit once; a bad second broadcast cannot leave a first insertion.
No bypass of max_circuit_bits, operation budgets or Parameter owner admission.

## 7. from_instructions And Circuit.data

Implement observed QuantumCircuit.from_instructions forms with actual
Instruction/CircuitInstruction operands. Retain operation objects, bits and
register memberships, classical scope, parameter graph, labels, phase,
mutable ownership, dynamic blocks and zero widths where supported.

data is a controlled executable sequence, not a detached snapshot. Observe
then implement supported index/iteration/slice/setitem/append/insert/pop/
clear/assignment behavior. Do not assume every listed mutation is public-
supported. Every supported data mutation preserves budgets, bit identity and
atomic validation.

## 8. Continue True Zero-Width Semantics

Complete zero-width Instruction construction/repeat/Circuit/context, empty
InstructionSet, no-op builders, empty copy/compose/inverse, zero-width QPY,
classical-only and typed-scope-only Circuits, global-phase-only coherent
control. Separately classify legal construction, insertion, serialization,
unitary Gate conversion and each Device's execution. Construction support
does not force every Device to execute an object. Scalar U=exp(i*phase)
must retain its phase in the full controlled complex matrix, not become I.

## 9. Genuine Standard QPYv13 Bit/Register Records

Implement records in the existing codec, never a metadata sidecar. Study and
implement supported quantum/classical Registers, loose bits, memberships,
aliases, circuit bit order, multi-register cases, legal labels/names, zero
width, measurement and custom Gate/Instruction operands.

Four initial genuine reds:

1. Native -> QPYv13 dump -> public qpy.load -> actual public memberships.
2. Public qpy.dump(version=13) -> native load -> native find_bit/membership.
3. Same numeric indices but different alias graphs cannot collapse to one
   structure after serialization.
4. Restored binding/complete Operator/measure/counts/dynamic execution, not
   just register counts.

Distinguish logical identity expressible by the format from unportable Python
is/address identity and unsupported complex sharing. Python object addresses
are not a QPY preservation target. Preserve CUSTOM_DEFINITIONS, Annotation
a/m, custom Instruction i, standard Gate class, matrix n/.npy, aggregate
max_numeric_elements, truncated/forged-length rejection, no-pickle/no-vendor.
Noncanonical graphs still not encodable remain explicit Unsupported, never
silently renamed or dropped; Unsupported is not function completion.

## 10. Native IR, QASM, Execution And AD

Reuse native IR bit_graph version1; no duplicate IR. The public QuantumCircuit
must directly enter Compiler, Statevector, Density, MPS, dynamic runtime,
QNode, derivatives and supported IR/QPY/QASM paths. Three real closed loops:

1. Public builders -> InstructionSet -> native Compiler -> Operator/Statevector.
2. Public measurement -> ClassicalRegister/CircuitInstruction -> four-device
   dynamic execution -> independently expected classical trace.
3. ParameterVector/custom Gate -> QPY/IR -> bind -> Jacobian/Hessian/streamed
   HVP ->100-wire MPS without dense conversion.

Execute all four AD frameworks. QASM's representable native bit/register
subset must emit real declarations; unrepresentable aliases/typed scopes
must explicitly reject.

## 11. Resource And Lifetime Reds

At least: huge Registers, max_circuit_bits, foreign callback-bearing bits,
over-budget iterable, duplicate bits/alias conflicts/graph cycles, stale
InstructionSet, modification after data snapshots, Gate mutation after public
copy=True and copy=False, shared ParameterVector lifetime, malformed QPY
Registers/forged bit refs/duplicate group IDs, zero-width phase export,
partial-failure broadcasting, managed copy before preflight, retained NumPy
matrix views and duplicate coherent phase. Monkeypatch/instrumentation must
actually prove rejection before dangerous allocation/conversion.

## 12. Tests And Actual Public Differentials

Retain the103 public observation scenarios and63 native/public foundation
cases. Suggested new independent scenarios:15 constructors;20 contexts/data;
20 InstructionSet/append;20 builders/broadcast;12 from_instructions;
15 zero-width;15 bilateral QPY;12 actual math/phase/dynamic/AD;
15 resource counterexamples. These are scenario targets, not implemented
function counts. No upstream implementation/test copying; use real public
outcomes and independent mathematical oracles.

## 13. Two SDK-Free Numeric Examples

- examples/native_public_quantumcircuit.py: public native QuantumCircuit ->
  QuantumRegister/ClassicalRegister -> InstructionSet/measurement -> actual
  native Device -> exact expected counts.
- examples/native_bit_register_qpy_gradient.py: real representable aliases ->
  custom parameterized Gate -> QPYv13 -> bind -> native Operator/Jacobian/HVP
  -> independent analytic result. Reject unsupported structures separately;
  never discard identity to display success.

## 14. Final Complete Gates

80159 is development FOCUS only. After implementation, freeze one final
runtime and run existing bounded sequential gates: SDK-free FULL; main
Qiskit2.4.1/PennyLane0.44.1 FULL; alternate2.6.0/0.42.3 FULL; independent
JAX/TF FOCUS; Torch/Autograd FOCUS; Compiler/QNode/IR/QPY; H2/Aer/MPS;
both public differentials; explicit GLOBAL; original unchanged
scripts/run_local_matrix.sh; all SDK-free numeric examples; compileall;
controlled legal; credential/vendor checks; actual import origins; actual
frozen/worktree/staged/committed runtime equality.

Matrix SDK-free unavailable/not-executed optional dependencies stay explicit.
GLOBAL minimum91.34108013033072%, exclusions68 cannot increase. A new real
correctness failure requires repair and refreeze; old failed snapshots' FULL
results cannot be reused. No new acceptance from FOCUS or RUNNING output.

## 15. Local Git And Final Report

Only normal scoped local commits of owned source/tests/examples/reports.
No git add dot, reset/rebase/amend/force, Studio/Router edits, auth/TLS/token,
quantum cloud/hardware calls, vendor, unauthorized push, PR/tag/release.
Suggested title: feat: add native quantum circuit public instruction contracts.
Partial checkpoints must remain honestly partial, never U3D DONE.

Final report separates fluent compatibility; real public returns; a single
authoritative store; actual CircuitInstruction/InstructionSet; accurate append/
broadcast; zero-width validity/execution; bilateral QPY; shared IR/Device/AD;
real tests/coverage/matrix; unimplemented public core APIs; and original U3/
P4/full parity completeness. Final architecture: keep fluent Circuit, add real
native QuantumCircuit public ABI, share storage and all execution systems.
Do not convert into another Circuit on each execution or overturn verified
fluent returns for superficial compatibility. Full goal remains ACTIVE /
INCOMPLETE.
