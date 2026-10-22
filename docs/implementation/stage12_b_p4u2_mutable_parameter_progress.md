# Stage 12-B P4-U2 Mutable Parameter Checkpoint

Status: VERIFIED SUPPORTED-SUBSET CHECKPOINT / PARTIAL. The full independent Qiskit/PennyLane
functional replacement goal remains ACTIVE / INCOMPLETE. This work does
not close original P4-U/P4, dedicated standard class ABI or all SDK APIs.

## Starting Evidence And Scope

Start HEAD:ccaa377bd6085480fe8883085d05bc112503742c; previous implementation
ed79a81c1c675947f98c285ba578191422c57247. Previous valid explicit FULL line
coverage:30160/33126=91.04630803598381%, exclusions68. No push, fetch,
authentication/TLS/token access, cloud/hardware submission, vendor payload,
tag/release, history rewrite or Studio/Router changes in this batch.

This implements the actually received U2 continuation recorded in
stage12_b_p4u1_review_and_p4u2_continuation.md. The original4 failed/1 passed
requirements were moved and extended into controlled tests. No upstream
implementation or test source is inspected/copied. Public references are
the official Gate/Instruction/AnnotatedOperation APIs linked in the migration
ledger and installed public2.4.1/2.6.0 calls, not their private implementation.

## Native Implementation

- ParameterList is a live MutableSequence proxy backed by its owner's
  immutable canonical tuple. Indexed/sliced assignment, insert/append/extend,
  remove/pop/clear/reverse/sort and in-place operations validate the complete
  candidate before committing once. Detached copies/concatenation/repetition
  are bounded lists. Views are not stored on the owner, avoiding owner/view
  cycles; a retained view intentionally retains its owner's storage.
- Generic Instruction.validate_parameter preserves arbitrary payload identity;
  Gate validation accepts native real scalar/symbolic values, rejects complex
  scalar/known-complex expression and nonfinite physical angles. Annotation
  validation/params delegate to the borrowed base. Managed updates reject
  foreign owner/payload/index/sort callbacks before invocation or state change.
- A native owned ParameterBindingPlan retains original formal slots and an
  executable Circuit template. Repeated numeric/symbolic updates, alias checks,
  parameter_map, copy, assign_parameters, controlled/open-control bases and
  standard definition recipes update real computation rather than only a list.
  Independent numeric constants are never matched to a parameter by value.
- Native IR has an explicit optional typed parameter_binding record containing
  formals and a Circuit template. It restores future mutation after binding,
  validates widths/namespace/alias consistency and compares the rebound
  executable definition. Corruption, nonunitary templates and inconsistent
  actual definitions reject. Shared vector/depth/definition budgets are reused.
  Fingerprints/equality exclude private binding records to avoid recursive
  history expansion and accidental comparison of private slot UUIDs.
- The new owned Instruction definition path exposed an existing strict-copy
  initialization bug: hashed Parameter members could be reconstructed before
  their cloned fields existed. The shared native copier now primes audited
  native fields, replaces every field with the owned copy, and only then
  returns. Resource preflight and foreign-copy rejection remain active; no
  unmanaged deepcopy fallback was introduced. Direct set/dict/expression/vector
  and retained-array lifetime checks accompany the repair.

## Actual Red/Green Evidence

Receipt prefixes below identify complete .log/.exit files in /tmp.

- p4u2-owned-red:28 failed/1 passed/exit1; live mutation/validation absent.
- first-recovery:one real primitive-controlled lineage failure, plus5 JAX
  float32 harness failures because x64 was omitted. Later invocations always
  set JAX_ENABLE_X64=True; no numerical tolerance was weakened.
- second-recovery:6 regressions from checking primitive-name arity before
  attaching a custom definition; constructor ordering repaired, preserving
  custom h/X-name semantics. third-recovery:594 passed/3 xfailed/exit0.
- managed-red:3 real foreign value/post-init callback failures; pre-admission
  repaired them. factory-red:11 numeric recipe lineage failures plus a hostile
  metaclass equality failure; explicit recipe slots/exact-type checks repaired.
- public-241 first:one real np.float64 return-type mismatch; actual public
  keeps float64 while float32 converts to float. Corrected without casting
  away complex data. public-241-r2/public-260 each81 passed/1 xfailed/exit0.
- ir-lineage-red:5 real post-reload mutation failures; typed native IR records
  repair them. parameter-map-red:2 real expression-slot failures; original
  Circuit formals now survive mapped Gate/Instruction conversion.
- final-candidate-focus:21 existing composite-circuit failures expose strict
  hash initialization, plus one newly authored width-corruption test used a
  nonexistent top-level width key. The latter now mutates the actual
  registers.quantum.size field; no production schema rule was weakened.
  strict-hash-red independently reproduces the Parameter.name AttributeError.
  hash-recovery:1234 passed/4 xfailed/exit0 after the native shared repair.
- list-read-red exposes missing concatenation; actual bounded list read
  operators implemented. focused-cov:1240 passed/4 xfailed/6 warnings/35.07s,
  exit0. This is FOCUS, NOT global coverage. The new helper's focused line
  coverage was233/243; dirty-worktree overall focus coverage is not an SDK
  completion/global coverage result.
- broad-260:1240 passed/4 xfailed/2 warnings/22.72s/exit0. Later extra guard
  focus:194 passed/3 xfailed/exit0. Broad SDK-free focus is recorded separately.

All prefixes begin /tmp/qb-stage12b-. Public compatibility tests include18
actual RX/RY/RZ index/slice/replacement/copy/symbolic/annotation execution
scenarios, scalar return types, generic payload identity, rejection and
explicit error-class differences. A strict public-only expected failure
retains the observed generic public Gate mutation leaving its symbolic
definition unbound. Native execution is independently checked instead of
copying that defect. Public partial invalid setter corruption is likewise
recorded, while native invalid assignment preserves the previous state.

Integration includes vector sin/exp/UUID, independent complex phase matrices,
mutated Gate -> standard QPY -> native QNode -> analytic Jacobian/Hessian/HVP,
and100-wire MPS values/gradients with dense entry points patched to fail.
The SDK-free example native_mutable_gate_parameters.py also executes native
IR copy/mutation and the explicit symbolic QPY/second-derivative chain.

## Actual Frozen Gates

Exact17 owned paths were frozen from HEAD plus this change using a private
index. Protected untracked Router/Studio files were not copied into the
controlled source. Input tree:c31d12120f74de197aa79273888da2307363f2c0;
production99fe620904ca89a367e2cd7d92fdb839a3f6bc80;
testsa1dc7f70d3c51593940a41ce5c6809937696ffca;
examplesb9dbe0a612f49467f5575cb697cc0ad1f422275c.
Source:/var/folders/c1/gs7_18954qx7td5_t_lnmf4c0000gn/T/qb-stage12b-p4t-foundation-n3h6z1qw/source.
The historical p4t directory prefix is not the runtime identity; the hashes
above identify this U2 snapshot. Only documentary receipts changed afterward.

Driver session77771 terminated0. All20 independent child .log/.exit receipts
with prefix /tmp/qb-stage12b-p4u2-r1- are terminal0:

| Gate | Actual Result |
| --- | --- |
| compile | exit0 |
| controlled legal | 4passed, exit0 |
| SDK-free FULL | 4263passed/809skipped/6warnings/258.21s, exit0 |
| main FULL, Qiskit2.4.1/PennyLane0.44.1 | 5291passed/5skipped/7xfailed/63warnings/1468.87s, exit0 |
| explicit main coverage JSON | exit0 |
| alternate FULL, Qiskit2.6.0/PennyLane0.42.3 | 5289passed/5skipped/9xfailed/51warnings/513.75s, exit0 |
| independent JAX FOCUS | 1047passed/203skipped/1warning/8.55s, exit0 |
| independent TF FOCUS | 1049passed/201skipped/1warning/12.00s, exit0 |
| public241/native/resource FOCUS | 1246passed/4xfailed/6warnings/25.67s, exit0 |
| public260/native/resource FOCUS | 1246passed/4xfailed/2warnings/25.84s, exit0 |
| five SDK-free examples | each exit0 |
| five actual import-origin probes | each exit0 |

Explicit GLOBAL coverage is30511/33474=91.14835394634642%, exclusions68,
above previous91.04630803598381%. New instruction_parameters helper240/243;
operations115/141; gates383/403; annotation191/195; nativeIR372/384;
array_ownership221/236; standard recipes63/76. This is line coverage, not
the percentage of SDK functions implemented. JSON receipt:
/tmp/qb-stage12b-p4u2-r1-coverage.json. Independent final audit
/tmp/qb-stage12b-p4u2-final-audit.log/.exit terminates0, checks all20 terminal
receipts, exact actual package origins, baseline and unchanged exclusions.

Actual probes import QuantumBridge from the frozen source in all5 environments.
Python3.12.6; main/alternate NumPy2.4.6, SDK-free/JAX/TF NumPy2.5.4.
Main uses JAX0.7.1/TF2.21/Torch2.12/Autograd1.8; alternate JAX0.6.2/
TF2.21/Torch2.12/Autograd1.9.1. Independent JAX0.12 and TF2.21 environments
have no Qiskit/PennyLane/Aer; SDK-free has none of those or four AD packages.
All invocations use PYTHONPATH=., JAX_ENABLE_X64=True and one BLAS/OMP thread.
Examples cover custom interchange, annotation, modifier gradients, standard
decomposition and mutable Gate execution. These five are not a claim that
the original P4 five-example contract has been jointly accepted.

Fresh dirty-worktree legal probe /tmp/qb-stage12b-p4u2-dirty-worktree-legal
terminates1:1failed/3passed, solely unowned quantumbridge/router/core.py
missing in the source migration ledger. No attribution was invented to hide
it. The controlled-source legal4passed result does not describe that dirt.

The original28-section matrix and original P4 joint acceptance remain
NOT_RUN at this development checkpoint. No in-progress process is passed.
Staged/actual-frozen equality and local commit receipt are recorded separately
after this documentary update; no runtime changes followed the frozen runs.

## Actually Read Collaboration Review

Owner-authorized conversation "Claude 代码泄漏与应对",
6a20d458-a76c-83ea-9b49-f8f0caedb3cf. Interim report user
9511c94f-4310-471e-98cc-43f135456478 received completed reply
52e158dc-b8b1-4277-a42b-56fe3ff3a024, reference0. The complete actual rendered
Chrome reply/table/instructions were read at AX elements1320-1410; backend
metadata was confirmed separately. An unread content reference was not used
as an execution instruction or evidence of reading.

Report-based review found no newly established blocker, directed keeping
healthy frozen FULL processes running, then scoped local commit only after
all receipts and equality checks. It explicitly preserves cross-object
dependency consistency, stable hash identities and original symbolic formal
templates instead of numeric guessing. The collaborator has not independently
reviewed unpushed code or remote CI. The directed next stage is U3 dedicated
return/error ABI, then U4 dynamic/empty contracts and U5 joint acceptance.

## Remaining Boundaries

- The proxy is not a literal list; reference identity and exact error-class
  ABI are not claimed identical. Dedicated public RX/RY/RZ and other standard
  return classes remain U3 work, not supplied by standard_gate_object.
- Generic public indexed mutation can leave its definition stale; public
  invalid assignment can partially corrupt its list. Native remains stronger
  and atomic instead of deliberately copying those bugs.
- A user-edited already-numeric definition cannot be reparameterized by
  guessing which equal constants were formerly arguments. Ambiguous mutation
  rejects; native IR rejects stale lineage. Fresh symbolic edits can rebase.
- Native IR preserves declared editable lineage. Standard QPY v13 preserves
  the tested current object structure/math, not every private editable history
  of a numeric generic Gate. A public generic stale-definition QPY self-roundtrip
  was also observed not to repair that bug. No private JSON sidecar is passed
  off as a standard QPY annotation/parameter field.
- Native zero-qubit/dynamic/remaining composite contracts, complete original
  examples and28-section matrix still need U4/U5. Full SDK parity is incomplete.
- Existing unowned Router missing-ledger failure must not be hidden with
  invented attribution. Only controlled-source legal gates can be called green.
