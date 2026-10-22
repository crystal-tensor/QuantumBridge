# Stage 12-B P4-T Native Annotation Development Checkpoint

Status: PARTIAL / IN PROGRESS. P4-T, original P4 acceptance and independent
full Qiskit/PennyLane replacement remain INCOMPLETE / ACTIVE. This report is
not a functional-completion percentage, a remote CI result or upstream review.

## Baseline And Protected State

Local branch main; input HEAD e7b9e324cbf90d791d4f8733b8fd7d00dc48c38c.
Previous tested implementation2857901187e9bd30b6f0f81ca71f44b9cc6f9229.
No fetch, push, authentication/token/TLS change, cloud/hardware request, tag,
release, vendor operation, history rewrite or Studio implementation in this batch.
Existing tracked Studio modifications and untracked Router/Studio/output and
other user files remain outside the owned staging set and controlled snapshot.

The dirty worktree legal check actually exits1: 1 failed /3 passed, exclusively
because pre-existing untracked quantumbridge/router/core.py has no ledger
entry. Its ownership/source history is not inferred and attribution is not
invented. The controlled frozen legal check actually exits0:4 passed.

## Implemented Native Slice

- Native AnnotatedOperation, Modifier, InverseModifier, ControlModifier and
  PowerModifier. AnnotatedOperation is deliberately neither Gate nor Instruction.
- Constructor borrows the supplied native base and explicit modifier list;
  Circuit append/copy take owned snapshots. Copy, structural equality, base
  parameters, native dependency enumeration, assignment and chained modifiers.
- Ordered deferred representation, including nested annotations, open/multiple
  controls and symbolic base parameters/phase. The representation does not
  synthesize or cache a resolved definition at construction.
- resolve_annotated_operation(op,target=None,limits=None) uses the existing
  Gate inverse/control/power engine and native compiler. Symbolic power
  dependencies can be represented and bound; unresolved symbolic exponents
  explicitly reject at resolution. Supported numeric fractional powers retain
  the existing bounded principal spectral rule, not arbitrary symbolic powers.
- Gate.inverse/control/power(annotated=True) produce native annotations.
  Circuit append, binding, from_instruction, inverse, selected decomposition,
  native lowering, Operator, Statevector and DensityMatrix accept this slice.
- Existing compiler/QNode quantum derivative execution is reused. Independent
  first-order, Hessian and streamed HVP checks; four optional framework checks;
  an actual100-wire MPS test forbids Gate/dense-state/density materialization.
- Native IR carries real base type, nested definitions, ordered typed modifiers,
  ctrl_state, parameters/AST/UUID/vector identity, labels and full phase.
  Instruction metadata phase is encoded/bound; omitted default phase is not
  gratuitously added on decode. Expression display strings are not equality
  authority. Vector root UUID/index identity is retained, not a promise that
  distinct owned base snapshots share one mutable Python vector owner.
- Native standard_gate_definition and standard_gate_object reuse existing
  compiler recipes for31 registered standard names. Symbolic/numeric tests
  compare full complex operators, inverses, controls and1/2-layer decomposition.
  SX's pi/4 phase and controlled relative phase are explicitly tested.
- Logical validation counts aggregate operations/definitions across annotation
  and Gate graphs; cycle/depth/work/control/matrix and atomic append guards.
  Managed intake refuses foreign modifier/base callbacks and owned storage is
  released. This is not an arbitrary process RSS or universal SDK allocator bound.
- Native Aer retains explicit named composite-noise rejection for deferred
  nodes. Unsupported generator gradients remain explicit, not silent finite
  differences or noiseless fallback.

The31 standard names are id,H,X,Y,Z,S,Sdg,T,Tdg,SX,SXdg,RX,RY,RZ,Phase,p,u1,
U,u2,u3,CX,CZ,SWAP,CRX,CRY,CRZ,CP,cphase,RXX,RYY,RZZ (case-normalized native
names; aliases are not counted as distinct mathematical functions).

## Actual Reds And Repairs

The first test run exited1 with5 failures: native annotations/modifiers and
Gate annotated=True paths did not exist. Those5 pass after implementation.
Independent tests retain control/power structure without asserting false
matrix noncommutation. Reversed nested open-control states have genuinely
different independently derived8x8 operators.

Additional real reds found IR equality wrongly comparing expression display
text, default phase insertion, symbolic Instruction phase metadata encoding,
and the wrong QASM rejection type before format preflight. These were repaired.
The test originally demanded a single mutable Python vector owner even across
already-distinct source snapshots; it was corrected to the actual UUID/root/
index ownership contract, not used to claim alias preservation.

A4-framework run without JAX_ENABLE_X64 failed the JAX float64 oracle because
the runtime truncated inputs to float32. With the required x64 environment,
the same strict tolerance passes; no tolerance or production math was relaxed.

Adversarial Aer review produced a real red: named annotation noise did not
raise, so lowering could drop its execution boundary. The new node is now
covered by the existing explicit unsupported boundary guard. R1 frozen testing
was deliberately stopped after verified owned pytest PID2765 received SIGTERM;
child receipt-15, driver exit241. R1 is obsolete/NOT PASS, not accepted evidence.

A later NumPy scalar admission probe found a real float32 integer-power red:
the Python-only numeric type predicate reached repeat before its work-budget
check. Native Real scalar admission now includes NumPy reals; five scalar
cases prohibit entry to repeat and pass the same budget assertion. The
combined recovery is363 passed/1 xfailed/4 warnings/7.93s exit0. The added
float32 case also exposes an existing numeric-magnitude comparison warning;
it is not silenced. R2 main FULL was deliberately terminated at verified
owned pytest PID3129, child-15/driver241, after its completed SDK-free FULL.
R2 is obsolete/NOT FINAL, not a same-runtime acceptance result for R3.

## Formats And Public ABI Boundaries

QASM2/3 and the native QPY subset reject unresolved annotations, including when
QASM metadata loss is allowed. Explicit resolve-to-Gate followed by existing
standard export/import passes executable mathematics and changes object type;
it is not unresolved object preservation. No private JSON is emitted as QPY.
The public QPY specification documents annotation records from v11, with
modifier records. Actual public v13 dump/load retains annotations; our decoder
explicitly rejects them. This is missing native implementation, not absence
from the standard. Existing bilateral P4-S custom g/c records remain tested.

Native standard Gate builders are not the specialized Qiskit standard classes,
their return-class overrides, singleton/mutable/list ABI or full public API.
Actual public tests separate generic Gate control True/False/None from RX
standard inverse/power overrides. Fresh actual2.4.1/2.6.0 probes show omitted/
False/None generic control all return ControlledGate in both versions and
native R2; True returns an annotation. The native default signature False vs
publicNone and explicitNone deprecation warning are still different contracts,
not an observed default-return mismatch. Public annotation validate_parameter
exists and native still lacks it; public deferred nonunitary construction also
differs from native early rejection. ABI probe logs are
/tmp/qb-stage12b-p4t-abi241.log and /tmp/qb-stage12b-p4t-abi260.log, both exit0.
Native annotation parameters include symbolic modifier dependencies as an
extension; public params remains the base parameter list. Arbitrary foreign
Operation protocols and nonunitary bases are not admitted by this native slice.

Primary behavioral references, inspected as public documentation only:
- https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.AnnotatedOperation
- https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.Gate
- https://quantum.cloud.ibm.com/docs/en/api/qiskit/qpy

Installed2.4.1/2.6.0 public APIs are optional black-box oracles; no upstream
implementation/test source is read or copied. Production native execution does
not import or delegate to Qiskit/PennyLane. Source ports remain zero.

## Immutable Evidence

Final R3 frozen input tree2b31b8acd496f623e4a9d4e3bedcc16da52889c8.
Source /var/folders/c1/gs7_18954qx7td5_t_lnmf4c0000gn/T/qb-stage12b-p4t-foundation-2fo8_mbp/source.
Production subtree457939423658eecf9c3e275548308afda91beb5a.
Tests subtree171c0110a65b1c43d89d4e2b50e297cccfbe3ca3.
Examples subtree9cd0f3ba79636f6728f0cc70aa1b8daa9d60ca2b.
Only HEAD plus the exact24 owned paths is frozen; report-only later edits are
not runtime changes. Five actual imported origins were verified against this
same resolved snapshot path.

Serial gate driver /tmp/qb-stage12b-p4t-foundation-gates.py SHA256
189b8585a8f3c28aa3db0c9a831b9b1ac8f9e647cc5d44656f9d335510974f8d.
Mechanical private-index freeze helper /tmp/qb-stage12b-p4t-freeze.py SHA256
5141b901130be87f9d0a9520ddd192514462c8bef99dc0810a91d94ba918501a.
Receipts/log prefix /tmp/qb-stage12b-p4t-foundation-r3-.
PYTHONPATH=., JAX_ENABLE_X64=True, OMP_NUM_THREADS=1,
OPENBLAS_NUM_THREADS=1; existing Python3.12 environments reused unchanged.

Pre-freeze combined actual focus:358 passed,1 xfailed,3 warnings,7.15s,exit0.
The xfail is the previously observed public QASM2 custom h/X export loss;
it is not counted as parity. Pre-freeze new native-only151 passed/1 skipped
and new public/IR44 passed are historical smaller selections, not new totals.

R3 driver session63896 terminated exit0. All18 child receipts independently
exist and are0; no process is still RUNNING. Final audit independently exits0
at /tmp/qb-stage12b-p4t-foundation-r3-final-audit.log/.exit. Its helper
/tmp/qb-stage12b-p4t-foundation-audit.py SHA256 is
220e04a9444cf27bba46e8f6e97bc8cde9428d5765e455a42f171facbfbf474e.

| Final R3 gate | Actual result | Seconds | Exit |
| --- | --- | --- | --- |
| compileall | completed | - | 0 |
| controlled legal | 4 passed | - | 0 |
| SDK-free FULL | 4148 passed,745 skipped,6 warnings | 255.66 | 0 |
| main FULL + explicit coverage | 5115 passed,5 skipped,4 xfailed,61 warnings | 1468.46 | 0 |
| coverage-json | completed | - | 0 |
| alternate FULL | 5113 passed,5 skipped,6 xfailed,51 warnings | 486.01 | 0 |
| independent JAX focus | 278 passed,86 skipped,1 warning | 3.27 | 0 |
| independent TF focus | 278 passed,86 skipped,1 warning | 4.63 | 0 |
| main public/native combined focus | 363 passed,1 xfailed,4 warnings | 7.60 | 0 |
| alternate public/native combined focus | 363 passed,1 xfailed,2 warnings | 7.25 | 0 |
| three SDK-free numeric examples | each completed assertions | - | 0 each |
| five actual import origins | each points to R3 frozen source | - | 0 each |

No skips/xfails are compatibility matches. Main/alternate skips include
pyquafu0.4.5 requiring NumPy<2, two missing Dynamics cases, missing
Optimization and a missing-installation contract. Existing public semantic
xfails remain visible, including the P4-S custom h/X source loss. The native
float32 magnitude-comparison warning is not filtered. No dependency was
installed/upgraded and no current pip-check success is claimed.

All environments actually use Python3.12.6. Main: NumPy2.4.6, Qiskit2.4.1,
Aer.17.2, PennyLane.44.1, JAX.7.1, TF2.21, Torch2.12, Autograd1.8.
Alternate: NumPy2.4.6, Qiskit2.6, Aer.17.2, PL.42.3, JAX.6.2, TF2.21,
Torch2.12, AG1.9.1. SDK-free: NumPy2.5.4 and no upstream quantum SDK or
four AD frameworks. Independent JAX: NumPy2.5.4/JAX.12, no quantum SDK or
other AD frameworks. Independent TF: NumPy2.5.4/TF2.21, no quantum SDK or
other AD frameworks. The last two ran FOCUS, not FULL suites.

Explicit global coverage30029/32997=91.00524290086977%, above the previous
29623/32616=90.82352219769439%, exclusions68 unchanged. No new exclusion or
deleted failure is used. These are line coverage, not functional parity. The
standard_gates.py whole file is59/72=81.9444%, including legacy factory paths;
annotation188/192=97.9167%, Gate383/410=93.4146%, IR343/355=96.6197%.
The4 new test files contribute190 collected cases in the main environment,
including parameterizations/aliases: not190 SDK functions or full acceptance.
The original28-section local matrix remains NOT_RUN for this development
checkpoint, distinct from these actual three FULL/two FOCUS environments.

## Scoped Git Proof

Final staging/commit equality is checked separately after terminal tests.
Only27 explicitly owned paths were staged:24 original frozen paths plus
the P4-T report, P4 gap audit update and received P4-U prompt. Protected
Studio/Router and unrelated files are not staged. The staged/runtime audit
helper /tmp/qb-stage12b-p4t-staged-audit.py SHA256 is
a03d84713d92f7cb447de71776af44be3a51ef0877dfa4908a1cedc09a21ba43.
The staging audit actually terminated exit0, receipt/log
/tmp/qb-stage12b-p4t-staged-final.exit/.log. All1136 controlled runtime files
matched their frozen blob and working-tree hash; quantumbridge/tests/examples/
scripts/requirements subtrees also matched. No protected paths were staged.
The exact staged tree6fab89f36da1b761003ad151f36c02eb779064a7 equals the
committed code tree. The audited staged patch SHA256 is
3ca0ddf936b3dce3754e12af8bdeb418e9e2b8a41e0cbafb24ea76dac625dcae.

Normal local code checkpoint8e6ef77328c7924b4f996ab0d93da5b709ae7346,
subject "feat: add native annotated gate modifiers and definitions", records
27 files/1726 insertions/25 deletions. Documentation and parameterized tests
are not SDK function counts. The automatic committer-identity notice did not
cause a global configuration change or amend. This checkpoint is local only.
A subsequent documentation-only checkpoint records these outcomes and the
received next task; runtime subtrees must remain identical to this tested code.
No remote SHA/CI verification is implied; cached origin/main is not live
evidence. All original protected dirt remains present.

## Completion And Next Work

Three SDK-free examples contain actual numerical assertions:
examples/native_annotated_gate.py,
examples/native_gate_modifier_gradient.py,
examples/native_standard_gate_decomposition.py.

P4-T is a substantial native supported slice, not DONE. Missing native QPY
annotation records, standard specialized class/mutable/list/return ABI,
arbitrary Operation integration and remaining aggregate/serialization/managed
edge cases require follow-up. Original P4's five examples, complete lifecycle/
dynamic/empty/signature contracts, original28-section local matrix and joint
acceptance remain required. The original full matrix has NOT_RUN in this batch;
do not relabel these frozen development regressions as that matrix. No Stage8,
Studio, cloud/hardware or unrelated ecosystem implementation was started.

Highest independent full Qiskit/PennyLane replacement remains NO / ACTIVE /
INCOMPLETE. No percentage is inferred from inventory, passthrough, coverage or
successful examples. Preserve current boundaries and finish P4 contracts and
acceptance before treating the next core area as complete.

## Authorized Collaborator Reply

An interim report, explicitly disclosing R3 RUNNING and unsubmitted code, was
sent to the existing authorized ChatGPT conversation. User message
c48bac52-09c7-4a26-9d0f-73e941b370f8 received completed assistant reply
921b8ae6-e45c-4bc4-a172-91a85a0969ac (content reference12). Its entire rendered
24020-character accessibility body was actually read through overlapping
chunks, not inferred from a reference or the earlier truncated text node.
The collaborator's review is based on the report, not independent inspection
of unsubmitted source or remote CI. It identifies QPY object transport,
mutable/validation/return ABI and deferred nonunitary construction as real
remaining gaps, and no new report-proven blocker requiring R3 interruption.
The normalized complete next task is
stage12_b_p4u_annotation_qpy_abi_execution_prompt.md. Its explicit prerequisite
is all R3 terminal success, tested/staged runtime equality and scoped local
P4-T commit. P4-U implementation has NOT STARTED before those conditions.

After all prerequisites actually passed, the final report and local code SHA
were sent as user message1e39ef85-5e3d-4e3f-b545-7833628528b4. Completed
assistant reply2c148481-71ea-4a9a-9dc5-e039e4e4c856 (reference0) was actually
read in Chrome, including its complete table and four-step continuation.
It confirms the report-based local R3 checkpoint, no new reported blocker,
91.0052% line baseline and original matrix NOT_RUN. It explicitly retains
P4-T/P4/full SDK PARTIAL, no independent unpushed source/remote CI review, and
directs starting P4-U1 without rerunning unchanged R3 as a startup prerequisite.

P4-U1 has now started with baseline probes ONLY, no native implementation:
/tmp/test_qb_stage12b_p4u_initial_reds.py requires real unresolved annotation
object preservation in both QPY directions. Both2.4.1 and2.6.0 actually produce
2 failures, exit1; logs /tmp/qb-stage12b-p4u-initial-reds-241.log/.exit and
/tmp/qb-stage12b-p4u-initial-reds-260.log/.exit. Native writer rejects annotated;
native reader rejects the standard custom annotation type at byte193. These
are intentional next-task missing-feature reds, not R3 failures or implemented
QPY support. Production/test runtime in the checkpoint is unchanged.
