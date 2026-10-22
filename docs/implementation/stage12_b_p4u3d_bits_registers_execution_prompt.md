# Stage 12-B P4-U3D Execution Prompt

Native Bit/Register Model, CircuitInstruction, InstructionSet And Zero-Width Core Contracts

Status: ACTUALLY RECEIVED TASK / NOT IMPLEMENTATION OR ACCEPTANCE.
This normalized English transcription preserves the review and all17 task
sections actually received from the owner-authorized collaboration. Observe
real public outcomes first; the requested APIs are not thereby implemented.

## Reading Evidence And Checkpoint Review

Conversation: "Claude 代码泄漏与应对",
6a20d458-a76c-83ea-9b49-f8f0caedb3cf. The actual implementation SHA
2bb61619d15831992364ff81d3ba87b333234a54, full R1 receipts and equality
proofs were sent. read_thread confirms completed source message
bfa40935-90e3-4e62-8c70-74bccaefd765 but supplies only a content reference.
The actual rendered body was read at Chrome AX610-1273 (later sections3-16
and completed-answer controls), then AX612-1267 after scrolling (review and
sections0-10). The interrupted partial stream was not treated as complete.

The report-based review accepts only the U3C supported local checkpoint:
31 children/driver/final audit/snapshot audit0; SDK-free/main/alternate FULL
4646/6055/6053passed; JAX/TF1485/1487passed; Torch/Autograd452passed;
original28-section matrix0 in SDK-free scope; GLOBAL91.34108013033072%,
exclusions68 unchanged; reported frozen/staged/committed runtime equality.
No new confirmed blocker requires withdrawing that checkpoint. No independent
unpushed-source or new-SHA remote-CI inspection occurred. Remote CI remains
NOT_VERIFIED. U3C/U3/P4/full SDK remain INCOMPLETE.

Unavailable optional dependencies in the actual matrix are not validated
industry/hardware support. Three key risks remain: Bit identity cannot be
integer index equality; InstructionSet must reference real executable inserted
instructions; zero-width, empty, classical-only, repeat-zero and scalar-phase
Circuits have distinct construction/conversion/execution semantics.

## 0. Baseline And Objective

Start from actual local checkpoint2bb61619d15831992364ff81d3ba87b333234a54,
allowing a normal documentation-only follow-up with identical runtime. Verify
actual HEAD; do not assume it was pushed. Continue P4-U3, not U4 or Studio.
Advance the integer-wire execution model into real native public Bit,
Register and Instruction object protocols. Priority:

1. Bit, Qubit, Clbit and AncillaQubit.
2. QuantumRegister, ClassicalRegister and AncillaRegister.
3. CircuitInstruction and InstructionSet.
4. QuantumCircuit.append, add_bits, add_register and find_bit.
5. Zero quantum/classical widths and empty Circuits.
6. Remaining from_instructions, copy_empty_like, to_instruction/to_gate contracts.
7. Real dynamic/measurement/control/phase/serialization integration.
8. Actual dual-version public differentials and final regressions.

Public2.4 documentation motivates distinct bit identity, register aliases,
instruction handles and mapping contracts, not integer-only placeholders.
Do not rewrite accepted ControlBlock, Gate, ParameterList, Composer, Compiler,
QNode, Device or AD engines.

## 1. Actual Public Contract Observations First

Independently run public Qiskit2.4.1 and2.6.0 APIs. Record actual signatures,
positional/keyword rules, return types/identities, mutability, error classes,
post-mutation Circuit state, copy/alias, QPY roundtrip and full complex matrix
or classical state when needed. At least60 independent public scenarios per
version, including Qubit(), Clbit(), QuantumRegister(2,"q"),
ClassicalRegister(2,"c"), add_bits, add_register, find_bit, append,
copy_empty_like and to_instruction.

Actually observe CircuitInstruction/InstructionSet structure, indexing,
iteration, modification and legacy conditional interfaces. Documentation alone
cannot establish every return contract. Write native reds only for measured
differences; do not invent failures in already-correct behavior.

## 2. Real Native Bit Identity

Implement Bit -> Qubit -> AncillaQubit, and Bit -> Clbit. Cover standalone
bits, Circuit registration, references from Registers, identity separate from
position, real find_bit index and all register memberships, copy/compose
mapping, cross-Circuit lifetime and illegal cross-type references.

Do not model all identity with Qubit(index=0) numeric equality. Independently
construct q0=Qubit() and q1=Qubit(), assert q0 is not q1, then add both to a
Circuit and verify distinct positions and register memberships. Identity must
not change when later Registers are added.

## 3. Registers And Aliases

Implement QuantumRegister, ClassicalRegister, AncillaRegister, size/name,
index/slice/iteration/membership, Circuit.qregs/cregs, add_register and
add_bits. Test partially overlapping Registers; a new Register containing
existing Circuit bits; duplicate add_bits rejection; duplicate bits inside a
Register; Qubit/Clbit mismatch; empty and zero-length Registers; negative
index/slice; memberships after Circuit.copy; compose mapping; native IR/QPY.

Actually distinguish public add_register's allowed aliases of existing bits
from add_bits duplicate-insertion rules. They are not one interchangeable API.

## 4. Real CircuitInstruction Data

Implement CircuitInstruction(operation,qubits,clbits) as actual native data:
operation/qubits/clbits, replace, copy, public iteration/unpacking, equality,
native storage, Circuit.data and mutable operation parameter lifetimes.
Circuit.data modification must affect what Compiler/Device actually execute,
not merely a detached, cosmetically correct list.

## 5. Real InstructionSet And Append

Implement actual observable handles for handles=qc.append(gate,[q0]). Verify
the measured public InstructionSet return, references to actual inserted
instructions, multiple handles after broadcasting, len/iteration/indexing,
later modification, invalid qargs/cargs, copy=True/False, custom Gate,
nonunitary Instruction and legal ControlBlock references.

Do not blindly add obsolete c_if behavior when a target version rejects it.
Protect existing copy=False live owner references; handles cannot bypass
parameter validation or resource admission.

## 6. Append Broadcasting And Wire Maps

Cover int, Qubit/Clbit, Register, slice, iterable/nested iterable, broadcasting,
duplicate qargs, wrong bit type, negative/out-of-range indices, overlapping
qargs/cargs, noncontiguous maps, control-target ordering and measurement
classical mapping. Record actual accepted outcomes and CircuitError/TypeError
per version. Use at least one independently constructed two-qubit complex
matrix oracle; verify dynamic measurements with actual classical trajectories.

## 7. Distinct Zero-Width And Empty Core Contracts

This is a required genuine implementation priority. Distinguish:

- 0qubits/0clbits; 0qubits/Nclbits; Nqubits/0clbits.
- Nqubits/Mclbits with no operations.
- Zero-width Instruction and zero-width Gate.
- Zero-operation Circuit and phase-only Circuit.
- Typed variable-only Circuit.
- Zero-width repeat, empty compose/tensor/inverse.

Observe construction, repeat, conversion, serialization and execution in both
public versions first. Do not assume every zero-width Gate valid or every
zero-width Circuit invalid. For mathematically valid zero-qubit unitaries,
check scalar-unitary/global phase semantics. Distinguish invalid library
objects from valid objects unsupported by a particular Device. Zero dimensions
cannot cause negative allocations, empty-array accidents or budget bypasses.

## 8. from_instructions And copy_empty_like

Observe QuantumCircuit.from_instructions with ordinary Instruction lists,
CircuitInstruction lists, explicit qubits/clbits, registerless bits, classical
operands, empty input, illegal duplicate bits and mutable Gates. Observe
copy_empty_like name/register semantics. Reuse U3C typed scope for vars_mode:
preserve/capture/drop variables, input/local/capture distinctions, scope-only
Circuits and ControlBlock subcircuits. Actual mode names/defaults come from
the target public version; do not invent a second Var/Stretch implementation.

## 9. to_instruction And to_gate

Actually support Circuit -> to_instruction -> append -> execute. Verify
quantum/classical widths, retained definition/formal parameters, name/label,
full phase, measurement/reset, zero width, typed variables, controlled
conversion, native IR and QPYv13. to_gate remains strictly unitary:
to_instruction's nonunitary support cannot make measurement/reset a Gate.
Typed scopes unrepresentable by a standard format remain explicit Unsupported.

## 10. Mathematics And Existing Devices

Bit/Register objects must enter the actual existing execution engines, not
live only in a separate surface identity table. Three required end-to-end paths:

1. Qubit/Clbit/Register -> append -> CircuitInstruction -> native compiler -> Statevector/Density/MPS.
2. ClassicalRegister/measurement -> InstructionSet -> dynamic ControlBlock -> actual classical trace/counts.
3. Parameterized Gate/bit aliases -> compose -> IR/QPY -> QNode -> Jacobian/Hessian/HVP.

Protect complete coherent phase, open controls,100-wire MPS without dense
materialization, and real Torch/Autograd/JAX/TF first/second derivatives.

## 11. Resource And Atomic Failure Counterexamples

At least: enormous Register size; excessive/duplicate bits; illegal aliases;
iterables exceeding work budgets; malicious __iter__/__copy__ types; malformed
CircuitInstruction; stale InstructionSet handles; stale bit ownership; deeply
nested Instructions; shared ParameterVector across Circuits; cross-record QPY
numeric limits; bit graph cycles; illegal classical scope; invalid zero-width
conversion; failure halfway through inplace append.

Validate before committing state, with no foreign callbacks or half-mutated
Circuits. Preserve managed graph/matrix preflight; no permissive fallback.

## 12. Actual Serialization Interoperability

Native IR retains Bit identity, Register membership, instruction bit operands,
controlled/nonunitary definitions, Parameter UUID/vector, typed classical
scope and recoverable copy/alias semantics.

Independently verify QPYv13 standard quantum/classical Registers, registerless
bits, representable multi-register aliases, CircuitInstruction, custom Gate,
custom Instruction, measurements and representable zero-width cases. Use
public qpy.dump/load in both versions for bilateral tests. Unimplemented typed
Var/Stretch headers, classical custom Instruction and arbitrary metadata stay
explicit Unsupported, not fake standard interoperability. QASM2/3 retains
lossless-or-reject rules.

## 13. Tests

Suggested modules:

```text
tests/circuit/test_native_bit_identity.py
tests/circuit/test_native_register_contracts.py
tests/circuit/test_native_circuitinstruction.py
tests/circuit/test_native_instructionset_append.py
tests/circuit/test_native_append_broadcasting.py
tests/circuit/test_native_zero_width.py
tests/circuit/test_native_from_instructions.py
tests/circuit/test_native_copy_empty_like.py
tests/serialization/test_native_bits_registers_roundtrip.py
tests/compat/test_qiskit_bits_registers_public_differential.py
```

Independent scenario targets:15 bit/register identities;12 aliases/memberships;
15 CircuitInstruction/InstructionSet;15 append/broadcast;15 zero-width;
10 from_instructions/copy_empty_like;12 IR/QPY;12 mathematical/dynamic/AD;
15 resource/error counterexamples; at least60 actual public outcomes per
version. Test counts are not implemented SDK function counts. Run actual reds
before fixing production code.

## 14. Development And Final Gates

Run affected FOCUS during development. Final gates must use one frozen runtime
and the existing controlled sequential-resource approach:

- python3 -m compileall -q quantumbridge.
- SDK-free FULL; main Qiskit2.4.1/PL0.44.1 FULL.
- Alternate Qiskit2.6.0/PL0.42.3 FULL.
- Independent JAX/TF FOCUS; Torch/Autograd FOCUS.
- Both public differentials; H2/Aer/MPS.
- Whole-package pytest --cov=quantumbridge.
- Actual original bash scripts/run_local_matrix.sh.
- All new SDK-free numeric examples.
- Controlled legal; no-vendor/no-token; actual import origins.
- Frozen/worktree/staged/actual committed runtime equality.

Original matrix executed segments and SDK-free unavailable/not-executed
optional dependencies remain separate. Valid GLOBAL baseline is
91.34108013033072%, exclusions68 cannot increase. No test deletion, increased
skip or weakened numeric tolerances to obtain green. Actual new correctness
failure invalidates affected old frozen acceptance; repair, refreeze, rerun.
RUNNING, FOCUS and old snapshot results are not final FULL passes.

## 15. SDK-Free Examples

At least two new examples with actual numerical/state assertions:

1. Real QuantumRegister/ClassicalRegister -> append/broadcast -> measurement
   -> native execution -> verified bit mapping/counts and InstructionSet.
2. Bit/Register identity -> custom parameterized Gate -> compose -> IR/QPY
   -> Operator/Jacobian/HVP; separately verify zero-width contracts.

Printing interface inventories is not an executable numeric example.

## 16. Git, Final Report And Continuation

Only normal scoped local commits, never git add dot. Protect user-owned
Studio/Router tracked/untracked changes; never invent Router attribution.
No push/fetch/auth/TLS/token/cloud/hardware/vendor/PR/tag/release/history
rewrite in this batch. Suggested supported checkpoint title:
`feat: implement native circuit bit register and instruction contracts`.
Partial subsets must be named truthfully; U3D/U3/P4 remain PARTIAL.

Final report: new native Bit/Register/CircuitInstruction/InstructionSet APIs
and behavior; actual two-version observations; genuine reds/repairs; concrete
zero-width/empty executable range; append broadcasting/aliases/copy/ownership;
from_instructions/copy_empty_like/to_instruction; dynamic execution/full
complex matrices/derivatives/HVP/MPS; IR/QPY/QASM bilateral scope and explicit
Unsupported; three FULLs; four frameworks and skips; GLOBAL/exclusions;
actual original28-section matrix scope; frozen/staged/commit equality; local
SHA and truthful remote CI; remaining U3 gaps, especially classical QPY
headers, typed declarations, further builders, duration and runtime inputs.

After U3D audit remaining actual U3 public gaps, not automatic U4. Do not
shrink the final objective to these tests or use coverage as functionality.
Independent native Qiskit/PennyLane full functional parity/full replacement
stays ACTIVE / INCOMPLETE.
