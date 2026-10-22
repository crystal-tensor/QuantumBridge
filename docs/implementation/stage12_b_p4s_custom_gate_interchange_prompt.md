# Stage 12-B P4-S Received Task

Source: authorized ChatGPT conversation "Claude 代码泄漏与应对", conversation
6a20d458-a76c-83ea-9b49-f8f0caedb3cf, assistant message
d35cbe20-6ff3-426b-aee3-8c46b4ce5638, replying to progress message
e1a0f8e7-1688-4c0e-811f-551f41da9937. Read through Chrome accessibility after
the prior loading failure recovered. Overlapping views covered all 181 direct
content items, sections 0-18, including the final execution decision. The
following is a normalized task transcription, not a claim of completed work.

## 0. Objective

Continue original P4 on actual HEAD 7a7740e with existing uncommitted Gate code.
R3 is development evidence, not final acceptance. Full independent native
Qiskit/PennyLane replacement/parity remains ACTIVE / INCOMPLETE. Prioritize
executable, bindable, controllable, differentiable custom Gate/ControlledGate
definition transport through the existing IR, OpenQASM2/3 and standard QPY v13.
Reuse native Gate, state/density/MPS, parameters and derivative engines.

## 1. Three Actual Reds Before Production Edits

A: Gate named h with definition X must stay X after each format roundtrip;
deterministic safe renaming may resolve standard-format name conflicts.
B: nested Inner(p): RX(sin(p)), phase p/7; Outer(q): Inner(q), RY(q*q), phase
q/5, on noncontiguous three-wire mappings. Check UUID/formal mapping, partial
and complete binding, full complex matrix, inverse, controls and Jacobian/HVP.
C: actual native QPY writer -> public qpy.load and public qpy.dump(version=13)
-> native loader, checking bound full operators, not just a magic header.

## 2. Existing Native IR

Preserve Gate/Instruction distinction, name/label, quantum/classical widths,
formal parameters/UUID/vector elements, definition/phase/nesting, control state,
wire mappings and limits. Validate widths, parameter references and recursion
before publishing objects. Keep same-name different definitions distinct;
prevent stale caches and alias lifetime errors. Preserve existing symbolic AST.
No pickle/eval/exec or recovery of arbitrary executable Python objects.

## 3. OpenQASM2

Real gate declarations, dependency order, nested definitions, formal/actual
parameters, wire remapping and safe identifiers; native and public qasm2.loads
math checks. Reject unrepresentable internal global phase by default. Never
silently remove phase from coherent controls or claim private comments are
standard semantic fields.

## 4. OpenQASM3

Extend the existing parser/exporter for declarations, local wires, nested
definitions/expressions, supported gphase, invocations, safe collision handling
and supported controlled constructions. Native and available public import/
export checks. Preserve existing standard/dialect U/U3 phase distinctions.
Explicitly reject unsupported annotations, dynamic definitions and opaque data.

## 5. Standard QPY v13

Use public CUSTOM_DEFINITIONS/header/instruction specifications, flag/length/
type/control/reference/parameter/version fields. Implement native writer and
reader, not SDK delegation or private bytes. Check both public directions for
single/nested/multiple gates, duplicate display names, labels, numeric/symbolic/
vector params, phase, controls, multiple circuits and malformed payloads. Record
specific unsupported standard records honestly.

## 6. Identity And Names

Distinguish display name, definition identity, formal parameter identity,
actual argument and serialization-local identifier. Never merge name=g/X and
name=g/Z. Verified safe renaming or strict rejection is allowed; changed quantum
semantics are not.

## 7. Reuse Execution

Restored Gates use existing append/decompose/Statevector/Density/MPS/Operator,
Stage11L compiler, Stage11K/P-C derivatives and P3 expressions. Required chains:
custom Gate -> IR -> partial bind -> operator/state/density;
custom Gate -> QASM3 -> compiler -> native device;
parameterized custom Gate -> QPY -> native QNode -> shift/adjoint/HVP.

## 8. Independent Mathematics

Independent dense construction/tensor contraction, full complex phase-sensitive
comparisons, noncontiguous wires, open controlled blocks and nesting. Keep P4
tolerances. Check both bind-before and bind-after roundtrip paths.

## 9. Parameters And Derivatives

Preserve UUID/vector identity, partial/simultaneous binding, sin/cos/exp, phase,
trainable/nontrainable distinctions, compiled reconstruction and Jacobian/
Hessian/streamed HVP. No silent finite-difference fallback for missing controlled
generator rules. Legal decomposition may reuse existing native derivatives.

## 10. Resource/Adversarial Inputs

Cumulative depth/definitions/operations/bytes/parameter nodes/work/repeated
definitions/nested QPY/QASM recursion/copies/references in existing limits.
Test recursion/mutual recursion, duplicate conflicts, invalid wire width/formal
params, truncated/forged lengths, unknown types, unsupported controls, explosion,
malicious identifiers/version, nonunitary imported gates, alias lifetime and
invalid nested phase. Reject before over-budget generation; inputs unchanged.

## 11. Public Differential Checks

Existing Qiskit2.4.1 and2.6.0 environments, at least20 meaningful custom-format
interop scenarios separately per version. Distinguish QB->QB, QB->public and
public->QB. Public importer failures are not matches. Only public API/format
specification; no reading/porting upstream implementation or tests.

## 12. Tests

Suggested native custom gate IR/QASM2/QASM3/QPY13/limits tests, roundtrip
execution/gradient tests and public differential tests. At least15 IR,12 QASM,
15 QPY,10 binding/gradient and12 adversarial cases, without inflating counts by
simple numeric parameter grids.

## 13. SDK-Free Example

examples/native_custom_gate_interchange.py: nested parameterized Gate, IR/QASM3/
QPY roundtrips, binding, full complex operator, native gradient/HVP, mathematical
errors and explicit unsupported boundaries. Public oracle is separate optional
execution, never required by native codec.

## 14. P4-S Acceptance

Actual definition/name/nesting/UUID/vector/phase fidelity, representable QASM2/3,
standard QPY custom binary records, bilateral public loading, native states and
derivatives, compiler/limits integration and preserved P4 Gate regressions.
Without real QPY bilateral interop P4-S is not passed.

## 15. Original P4 Remains

After P4-S, finish annotations/modifiers, standard primitive decomposition,
mutable/copy/return/error ABI, dynamic/empty contracts, aggregate budgets, five
original SDK-free examples, original math/public cases and final five-environment
gates. P4-S is not all P4 or full SDK completion.

## 16. Verification

First compileall and serialization/circuit/compiler/qml/devices focused tests,
git diff --check. Final original P4 still requires SDK-free/main/alternate FULL,
independent JAX/TF and Torch/Autograd focus, coverage baseline90.7832066365959%
without exclusion growth, complete original28-section local matrix, examples,
legal/privacy/no-vendor/no-token and two-environment public interop. One frozen
runtime, complete logs/independent exits/import origins/staged/commit hashes.

## 17. Git/User Files

Keep local main, no branch/PR. Scope staging; no git add ., Studio/Router edits,
reset/rebase/amend/force, auth/TLS changes, workflow deletion, token transmission,
vendor/tag/release/unauthorized push. Original P4 complete -> normal scoped
commit. Accurate partial checkpoint permitted without P4 DONE. Remote new-SHA
CI not verified.

## 18. Reporting

Report starting/ending SHA, actual P4-S and each format range, real QPY records
and both public versions/directions, name conflicts/nesting/phase/identity,
bind order, operator/states/derivatives/compiler/MPS/limits, original P4 gaps,
actual terminal gates/coverage/matrix and commit/push/CI facts. Answer whether
real standard-supported restoration, bilateral QPY, identity/phase/control/
derivatives, original P4 complete and full SDK parity. Final SDK answer remains
NO / ACTIVE / INCOMPLETE. Begin three reds, then finish native interop, then
continue original P4; no fake completion.
