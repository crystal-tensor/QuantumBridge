# Stage 12-B P4-U Received Execution Prompt

Status: RECEIVED / NOT STARTED. P4-T R3 regressions are still running when
this task is received. Start P4-U only after all R3 gates actually terminate
successfully, exact tested runtime equality is verified and the owned P4-T
checkpoint is normally committed locally. If R3 fails, repair and fully rerun
R3 first. P4-T/P4/full SDK replacement are not declared complete here.

## Provenance And Actual Reading

Authorized ChatGPT conversation "Claude 代码泄漏与应对",
6a20d458-a76c-83ea-9b49-f8f0caedb3cf. Interim report user message
c48bac52-09c7-4a26-9d0f-73e941b370f8; completed assistant message
921b8ae6-e45c-4bc4-a172-91a85a0969ac, content reference12. Backend metadata
initially lagged; Chrome visibly showed the report and reply. The first reply
view exposed only an abbreviated long text node. After actual markdown render,
the full accessibility body was24020 characters. Overlapping readings0-10000,
9000-16800 and16500-end cover the complete review and all10 task sections,
including code blocks. No inference from an unread content reference or resend.
An attempted temporary TextEdit extraction yielded an empty file and was NOT
used as evidence; its owned empty window was closed. This is a faithful
normalized transcription, not evidence of implementation or acceptance.

## Received Stage Review

Keep IN_PROGRESS / PARTIAL; R3 full regressions and submission are unfinished.
The report describes real native annotation/modifier/resolution/standard
definition/execution/derivative red-green work, but the collaborator has not
independently inspected uncommitted source or remote CI. Three substantive
remaining risks: missing QPY annotation object interoperability; mutable params,
validate_parameter and standard return-class/error ABI; and public deferred
nonunitary construction versus native early rejection. Do not permit illegal
unitary lowering merely to align construction timing. The report establishes
no new blocking defect requiring R3 to stop: named-noise and NumPy power-budget
reds are repaired and belong in the frozen tests, whose final outcomes govern.

## 1. Priority

P4-U1: standard QPY v13 Annotation/Modifier native bilateral interchange.
P4-U2: Gate/Instruction/AnnotatedOperation parameter mutation and validation.
P4-U3: standard return types, public results and error contracts.
P4-U4: dynamic/empty circuits and remaining composite/resource boundaries.
P4-U5: original P4 examples and complete joint acceptance. The first two have
highest priority for replacement of real upstream calls, not only execution
of QuantumBridge's private object family.

## 2. P4-U1: Real QPY v13 Records

First actual red A: p=Parameter("p"), base=Circuit(1).rz(p,0),
base.global_phase=p/3, op=AnnotatedOperation(base.to_gate(),
[InverseModifier(),ControlModifier(1,ctrl_state=0),PowerModifier(2)]).
Native writer must produce standard v13 binary that public2.4.1 and2.6.0
qpy.load actually read, preserving modifier order/count/state/power, base
definition and parameters. Bind and compare an independent complete complex
matrix. Do not pre-resolve to an ordinary Gate to fake object preservation.

Red B: public AnnotatedOperation -> public qpy.dump(version=13) -> native
reader -> real native AnnotatedOperation -> bind/resolve/Operator. Decode
typed records, not names. Implement the exact target v13 published record
layout; do not transplant newer annotation header fields into v13.

Cover inverse/control/power, nested annotations, multiple modifiers, ctrl_state,
symbolic ParameterExpression, vector elements, custom Gate and standard base,
phase, multiple-circuit files, illegal modifier type, truncated/corrupt bytes
and version mismatch. Where v13 cannot represent a particular object losslessly,
retain Unsupported with an exact format reason. No private JSON/sidecar posing
as a standard QPY field. At least12 independent native binary tests and12 real
bilateral public interchange scenarios. Public documentation/data contracts
and public APIs only; no upstream implementation or test source copying.

## 3. P4-U2: Real Parameter Mutation And Validation

Measure and implement supported gate.params, assignment, validate_parameter,
copy, annotated.params and annotated.validate_parameter. Do not break existing
managed copies, definition ownership, caches or lifetimes. Updates must be
atomic; real rotation angles cannot silently accept complex values; UUID/vector
identity is retained, bound updates invalidate affected caches and one object's
mutation cannot contaminate copies. Annotation parameters delegate to its base.

A checked proxy for mutable public lists is permitted; returning a temporary
list(tuple_params) is not real mutable semantics. Exercise assignment, in-place
changes and recovery. Required negatives: g2=g1.copy();g2.params[0]=.5 leaves
g1 unchanged. g.params=[.2,complex(0,1)] failure leaves the prior params and
definition unchanged. g.params[0]=new_parameter affects actual later matrix,
Circuit binding and expression dependency behavior.

## 4. P4-U3: Literal Public Return And Error ABI

Actually probe public2.4.1 and2.6.0: Gate.control(True/False/None),
inverse(True/False), power(True/False), RX/RY/RZ specialized return classes,
generic Gate returns, annotation base/modifiers/params, copy, repeat,
Circuit.decompose/to_gate, inplace=True results, invalid values and errors.
Distinguish mathematical equivalence, public type, returned object behavior,
error timing and exception class. Matrix equality is not full API parity.
Prioritize behavior affecting real callers. Unsupported dedicated standard
classes remain explicit ABI gaps, not claims that a generic Gate is identical.
At least20 public differential scenarios, tested in both target versions.

## 5. P4-U4: Dynamic, Empty And Resource Contracts

Close original P4 empty Circuit->Gate/Instruction, empty repeat/tensor,
zero-power Gate, annotated empty definition, measured/reset/control-flow
Circuit.repeat, safe dynamic-body decomposition, nonunitary Gate rejection,
nested custom Gate/annotation, inherited budgets, managed copy lifetimes,
multi-layer decomposition and QASM/QPY lossless-or-reject boundaries.
Reuse existing ControlBlock; do not statically execute a runtime branch.
Measure legal public method semantics individually for nonunitary circuits;
do not indiscriminately reject all Circuit methods because it has measurement.

Retain negatives: custom h/X name collision, symbolic coherent phase,
unsupported named noise cannot become noiseless, NumPy float32 integer
power/repeat admission, nonunitary gate identity,100-wire non-dense MPS and
dangerously shared mutable definitions.

## 6. Actual Mathematics And Integration

Parameterized Custom Gate -> Annotation -> real native QPY v13 roundtrip ->
bind/resolve -> native Operator -> native QNode -> Jacobian/Hessian/HVP.
Also annotation -> existing compiler -> Target basis/routing -> native
Statevector/DensityMatrix/MPS. Use full independent complex matrices, coherent
phase and open-control mathematics. Preserve P2 UUID/vector, P3 symbolic math,
P4-S custom definitions,11K-11P-C2 derivatives/HVP, Aer noise guards,100-qubit
MPS, H2 molecular Hamiltonian and earlier QASM2/3/QPY bilateral interop.
New ABI changes must fix regressions rather than delete old failing tests.

## 7. Original P4 Finish

Return to the original P4 acceptance and five actual SDK-free examples:
native_custom_gate.py, native_circuit_decomposition.py,
native_circuit_tensor_repeat.py, native_controlled_phase_gate.py and
native_gate_gradient_hvp.py under examples/. Reuse genuinely equivalent
existing examples; do not create duplicate content only to match filenames.
All contain real numerical assertions. At least one full chain: vector +
sin/exp -> custom Gate -> annotation -> native QPY v13 roundtrip ->
append/decompose/control -> native Statevector/Operator -> gradient/HVP.
If a combination is unrepresentable, use a genuinely supported object for
the positive example and a separate rejection test; never claim all objects
roundtrip just because one supported case does.

## 8. Final Gates

Only begin after R3 final success and P4-T commit. From final frozen P4-U
runtime: compileall; focused actual circuit/core, serialization, compiler,
qml and devices; pytest -q -rs; explicit pytest --cov=quantumbridge;
bash scripts/run_local_matrix.sh; git diff --check. Use actual existing
test paths; suggested tests/circuit is not a mandate for a second package.
Also SDK-free FULL, main2.4.1/PL.44.1 FULL, alternate2.6/PL.42.3 FULL,
independent JAX/TF focused, Torch/Autograd focused, public QPY bilateral,
all original P4 examples, legal/privacy/no-vendor/no-token and staged scanning.
Save independent exit codes/full logs and frozen/staged/commit equality.
Baseline90.82352219769439% until a valid final R3 FULL coverage updates it.
No new exclusions, deleting failures or focus coverage labeled as global.

## 9. Git And Ownership

P4-T unsubmitted code is not published source. Finish R3; verify real terminal
states; match runtime/staging; scoped local P4-T commit; only then P4-U.
After all P4-U tests, scoped local commit. No push without normal authorization
and reliable remote state. No reset/rebase/amend/force, workflow deletion,
credentials/TLS/token reading, vendor/tag/release or user Studio/Router edits.
Old GitHub CI does not establish a new local SHA has passed remotely.

## 10. Final Reporting

Report actual R3 states/counts/exits and P4-T SHA; P4-U native functionality;
real bilateral QPY annotation interchange; real mutable params/validation;
standard return/error matches and gaps; mathematics/derivatives/compiler/MPS;
whether all original P4 requirements are met; five environments/full matrix/
coverage; local SHA and separately verified remote/new CI state; remaining
Gate/Circuit APIs; and full Qiskit/PennyLane parity status. Only full original
P4 requirements can close P4; otherwise PARTIAL. Highest goal stays ACTIVE /
INCOMPLETE. Even complete P4 is one core area, not the whole SDK. After P4,
continue P5 classical builders/remaining core APIs, not Studio.
