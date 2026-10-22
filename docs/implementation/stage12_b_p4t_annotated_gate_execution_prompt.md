# Stage 12-B P4-T Received Execution Prompt

Status: RECEIVED / NOT IMPLEMENTED by this document. Original P4/P4-S
requirements and independent full SDK replacement goal remain ACTIVE /
INCOMPLETE. This is a normalized transcription of the complete received task,
not an acceptance report or an independently reviewed upstream specification.

Source: authorized ChatGPT conversation "Claude 代码泄漏与应对", conversation
6a20d458-a76c-83ea-9b49-f8f0caedb3cf. User report message
2c7b7ee3-e4e9-47fb-9ef6-d8ba6d3d3cb4; completed assistant message
a75b6f9d-752e-43c6-9a4a-589978c2ac55, content reference13. Initially Chrome
showed an interrupted connection; the body then actually loaded. Overlapping
accessibility views40-140 and0-100 covered all140 direct content items, review
and sections1-17. Gate method code in section7 was separately read without
truncation. No report resend, regeneration or unread-reference inference.

## Received Review And Priority

P4-S is a real supported native custom-definition interchange subset, not
P4-S DONE or P4 DONE. The collaborator explicitly bases its judgment only on
the execution report; it has not independently inspected unpushed2857901 or
new-SHA GitHub Actions. No demonstrated blocking issue is identified in that
report. Prioritize native AnnotatedOperation/modifiers/resolution and standard
gate definitions rather than expanding QPY format coverage indefinitely.

## 1. Baseline And Scope

Local main code checkpoint2857901187e9bd30b6f0f81ca71f44b9cc6f9229. Implement
AnnotatedOperation; InverseModifier, ControlModifier, PowerModifier; deferred
ordered composition and actual resolution; standard gate definitions; existing
Circuit/Compiler/GradientEngine/IR integration; supported QASM/QPY paths;
two-public-version mathematics/resource/error validation. Reuse existing Gate,
ControlledGate, custom definitions and QPY codec. No Studio, Capture expansion,
cloud/hardware/auth/token work.

## 2. First Actual Red: Preserve Modifier Order

The initially illustrated control-then-power versus power-then-control of
RX(.37) with the same control state and integer power does NOT itself prove
different matrices: ideal unitary coherent controls and integer powers can
commute in that setting. Do not invent a mathematically false expected result.
Independently derive genuinely distinct legal constructions using different
control nesting/open states, relative phase and/or applicability/type/wire/
parameter constraints, or test retention of distinct ordered structures and
serialization without asserting unequal matrices. Never exchange, merge or
eliminate arbitrary modifiers merely by assuming commutation.

## 3. Second Actual Red: Deferred Symbolic Controlled Phase

Construct p, base Circuit(1).rz(p,0), global_phase=p/3, base.to_gate(), then
AnnotatedOperation(gate,[ControlModifier(num_ctrl_qubits=1)]). Creation must not
require binding or float(p). Keep structured modifier objects and p UUID. Bind
p=.4, resolve, execute Statevector and compare full complex controlled matrix
diag(I,exp(i*p/3)*RZ(p)) to an independent block oracle. Also test supported open
control states; phase cannot be discarded as though still globally invisible.

## 4. Native AnnotatedOperation

Reuse native Operation/Instruction/Gate architecture. Provide
AnnotatedOperation(base_op,modifiers), InverseModifier(),
ControlModifier(num_ctrl_qubits,ctrl_state=None), PowerModifier(power).
Implement base_op, modifiers, num_qubits, num_clbits, params, name, copy,
structural equality, parameter binding, definition resolution, executable
lowering and resource validation. Modifiers are not inert strings.

## 5. Resolution

Provide resolve_annotated_operation(op,target=None,limits=None). Apply the
defined modifier order, retaining base parameters, UUID/vector identity and
global phase. Correct ctrl_state endian/wires, nested AnnotatedOperation,
inverse-controlled semantics and verified integer powers. Fractional powers
use existing supported spectral/rotation rules; unsupported combinations reject.
Even mathematically justified simplifications such as two inverse modifiers
must not destroy inspectable/serializable original unresolved structure.

## 6. Standard Native Definitions

Reuse existing correct recipes; fill actual missing definitions for H, X/Y/Z,
S/Sdg, T/Tdg, SX/SXdg, RX/RY/RZ, Phase, U/U2/U3, CX/CZ/SWAP, CRX/CRY/CRZ,
CP, RXX/RYY/RZZ. Validate exact full complex unitary and global phase, inverse,
one-level/nested/controlled decomposition, bound/unbound parameters, wire endian
and resource bounds. SX versus RX(pi/2) needs its nontrivial phase; probability
comparison is insufficient.

## 7. Gate Method Integration And Public ABI

Support existing Gate.control(...,annotated=True), inverse(annotated=True) and
power(exponent,annotated=True) appropriately. Actually measure public2.4.1 and
2.6.0 return types. Do not assume every standard gate returns AnnotatedOperation
when annotated=True; some return known concrete gates. Separate True, False,
None, symbolic parameters, multiple controls and unsupported synthesis. Native
extensions may remain but are not automatically public Qiskit parity.

## 8. Actual Native Execution

Three actual chains: ParameterExpression -> Gate -> annotation -> bind ->
resolve -> native Operator/Statevector; Composite -> inverse/control/power
modifiers -> native compiler/device; annotated parameterized Gate -> native
operations -> existing QNode shift/adjoint -> Hessian/streamed HVP. Independent
mathematical oracles must not share the native decomposition evaluator.

## 9. IR And Standard Format Boundaries

IR preserves base operation, ordered modifiers, parameters/UUID/vector,
ctrl_state, phase and nesting as real structure. For QASM2/3 use proven legal
gate lowering where syntax cannot preserve modifier objects; never claim the
object type survived in default lossless object-preservation mode. Unsupported
symbolic fractional powers reject. First verify QPY v13's actual published
annotation type/version support; only write real supported records. Otherwise
explicitly choose validated Gate lowering and disclose structural changes, or
reject. No private JSON masquerading as QPY. Preserve P4-S bilateral custom
definition interop.

## 10. Resource And Error Cases

Test invalid control count/state, nested/open controls, unbound symbolic power,
unsupported fractional power, nonunitary base, recursive definitions, modifier
depth overflow, controlled matrix allocation overflow, identity collisions,
phase loss, unsupported serialization, stale resolved definition, order errors
and missing generator gradients. Admit budgets before expansion/matrix creation.
No dense state/density fallback for large MPS workflows.

## 11. Required Behavioral Evidence

At least15 annotation construction/type cases,15 resolution cases,15 standard
definition cases,10 parameter/phase/control cases,8 gradient/Hessian/HVP cases,
10 IR/compiler/QASM/QPY cases,12 resource/error cases and20 public differential
scenarios on each of2.4.1 and2.6.0. Use independent complex matrices, controlled
blocks/tensor contraction and per-gate Statevector checks. Public calls only;
no reading/copying upstream internal implementation or tests.

## 12. Code And SDK-Free Examples

Suggested annotation/modifier/standard-definition/resolution modules and tests
are organizational suggestions, not a mandate to create a second circuit
package when existing core patterns suffice. Add executable examples
examples/native_annotated_gate.py, examples/native_gate_modifier_gradient.py,
examples/native_standard_gate_decomposition.py. Each contains real numerical
assertions, not only a printed object structure.

## 13. Preserve Existing Systems

Protect P2 UUID/vector identity, P3 symbolic math/substitution/derivatives,
P4 Gate/ControlledGate, P4-S custom/QPY records, compiler phase, QNode gradients,
100-wire non-dense MPS, state/density, QASM2/3, Aer noise and structured dynamic
ControlBlock. Nonunitary/dynamic/noisy scenarios cannot silently become noiseless
unitary execution to fit a generic modifier API.

## 14. P4-T Acceptance

Demonstrate construction/binding/resolution, ordered identity and symbolic
controlled phase, real standard definitions, supported Gate annotation methods,
actual native operators/states/density and derivatives, IR roundtrip/compiler,
valid format lowering or explicit Unsupported, two-version public comparison
and resource/atomic-failure behavior. Partial checkpoint is permitted only with
accurate scope and PARTIAL status; no P4-T/P4/full SDK completion claim.

## 15. Original P4 Still Required

Complete original five SDK-free examples, mutable/list/error/return ABI,
dynamic/empty-circuit contracts, aggregate/managed-copy/transport limits and
remaining Gate/Circuit signature differences. Final same-runtime five-environment
acceptance, original28-section local matrix and joint P4 review remain required.
P4-T focus does not substitute for all P4 acceptance.

## 16. Gates And Git

First compileall and focused circuit/compiler/serialization/qml/devices plus
diff check. Final original P4: SDK-free/main2.4.1/PL.44.1/alternate2.6/PL.42.3
FULL, independent JAX/TF and Torch/Autograd, explicit coverage, original
bash scripts/run_local_matrix.sh, public modifier comparisons, legal/privacy/
no-vendor/no-token and numeric examples. New baseline90.82352219769439%; do not
add exclusions, delete failures or label focus coverage global. Keep actual
logs/exits and frozen/staged/commit subtree equality. Scoped local commits only,
no git add ., no user Studio/Router/history changes, no unauthorized push,
credentials/TLS/force/tag/release. Suggested subject for genuinely implemented
scope: feat: implement native annotated gate modifiers and definitions.

## 17. Reporting And Continuation

Report actual annotation/modifier APIs, deferred execution, controlled symbolic
phase/full matrices, independent multi-modifier math, standard definitions,
identity/copy/lifecycle, first/second/HVP derivatives, compiler/IR/source/QPY,
both public versions, five environments, coverage/matrix, protected files and
Git/CI facts, remaining P4 public behavior and next native target. Clearly
separate added P4-T capabilities, complete original P4 acceptance and full SDK
parity. Highest goal remains NO / ACTIVE / INCOMPLETE. Start symbolic controlled
phase/order reds, then resolution/definitions, mathematics/derivatives/public
checks. After P4-T, finish P4 ABI/dynamic/resources/full gates before P5; do not
stay indefinitely at a few local Gate interfaces.
