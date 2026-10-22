# Stage 12-B P4-U3 Native Standard Gate Checkpoint

Status: IN_PROGRESS / PARTIAL. Full independent Qiskit/PennyLane functional
replacement remains ACTIVE / INCOMPLETE. This does not close U3, U4/U5, P4
or full SDK parity. Start HEAD:a0231673121a0d44a38c12ccba45876d87f7a357;
previous runtime commit e2e60554abff49a54600ed1c8fda385bec293e83. Effective
GLOBAL baseline30511/33474=91.14835394634642%, exclusions68.

## Received Task And Real Implementation

The actually read owner-authorized U3 task is preserved in
stage12_b_p4u3_standard_gate_return_error_execution_prompt.md. No Studio,
Router, push/fetch/authentication/TLS/token/cloud/hardware/vendor/tag/release,
history rewrite or third-party source/test inspection occurs in this batch.

The native standard registry contains23 concrete classes: RXGate, RYGate,
RZGate, PhaseGate, UGate, HGate, XGate, YGate, ZGate, SwapGate, CRXGate,
CRYGate, CRZGate, CPhaseGate, CXGate, CYGate, CZGate, CHGate, CSwapGate,
CCXGate, CCZGate, CUGate and UnitaryGate. This is an object inventory, not
a count of SDK functions completed. Shared family methods implement actual
construction/validation, copy/frozen ownership, inverse/control/power,
binding, coherent definitions, matrix and native Circuit execution.

- The existing native Gate/ControlledGate architecture, compiler recipes,
  ParameterList, symbolic ASTs, devices and derivatives are reused. Exact
  registered types are admitted; foreign subclasses are not generally admitted.
- Parameterized constructors retain original symbolic templates and real
  repeatable mutation. Failed changes remain atomic. Owned frozen defaults
  expose mutable=False; to_mutable and named copy create independent objects.
  They do not imitate private upstream singleton subclasses or global identity.
- Actual generic numeric power returns UnitaryGate. Annotation lowering uses
  a structural integer-power path so an MPS operation does not densify merely
  to match a public return class. Existing repeat/decomposition limits remain.
- CUGate has four independently bindable parameters and controlled gamma,
  including open controls; CCX/CCZ merge integer control-state bit order.
  Native Instruction label/name/base_class/mutable fields and the num_clbits
  keyword alias are real fields. Legacy positional definition arguments stay.
- Explicit standard_gate records carry native class identity in IR. A generic
  custom Gate named rx cannot become RXGate. Definitions/width/parameters and
  base structures are validated. Redundant human expression rendering is
  excluded from canonical signatures, while executable AST/UUIDs remain.
- Standard QPY class headers restore actual native standard objects. Numeric
  matrix parameters use published n/.npy records; headers, dtype, shape, byte
  length and shared numeric limits precede materialization, with no pickle.
  Two-qubit complex asymmetric matrices test actual bilateral bit order.
  Builtin object/definition work is admitted before binding constructors.
- Known canonical standard QASM forms emit real language gates, preserving
  coherent RZ/phase semantics instead of introducing lossy custom declarations.
  Unknown/custom identity still cannot be fabricated from an operation name.
- CircuitError marks standard-angle contract failures without swallowing
  native causes or resource exceptions. Physical finite-real admission stays
  stronger than unsafe/partially-mutating observed public behavior.

## Actual Red And Green Evidence

Prefixes below are independent .log/.exit receipts under /tmp/qb-stage12b-.

- U3 initial outside-suite6failed/5passed was moved/extended into controlled
  tests. p4u3-owned-red:51failed/5passed/exit1; first-native:56passed/exit0.
- integration-focus:1221passed/3xfailed/exit0 on the early implementation.
- formats-red:56failed/105passed/exit1, including foreign constructor hooks
  and unsupported actual standard/QPY types. Explicit admission and actual
  standard binary records repaired those paths; formats-recovery left one
  genuine Unitary matrix-vs-scalar IR invocation mismatch.
- format-derivatives exposed two RZ IR signature failures. Independent probe
  /tmp/qb-stage12b-p4u3-signature-probe.py showed only human rendering changed
  2 to2.0 while executable AST/UUIDs remained identical. Canonical signatures
  now compare actual AST, not redundant display text; second-derivatives:
  175passed/exit0. Forged type/changed executable definitions still reject.
- public-source-red:23failed/251passed/exit1. Actual failures include Phase
  name phase versus public p,12 complex-angle exception-class mismatches,
  nine coherent QASM2 export failures and matrix-controlled QPY definitions.
  public-source-recovery:274passed/exit0 after actual native repairs.
- extra public probes produced168 actual observations per version, not168
  native parity passes. extra-return-red:28failed/80passed/exit1. CUGate,
  CCX/CCZ dependencies, controlled mutability and Z.power phase semantics
  repaired these; extra-return-recovery:108passed/73deselected/exit0.
- broad-focus:1failed/1847passed/3xfailed/exit1. This exposed a real shared
  QPY budget regression: a new standard constructor could bind before the
  low expansion limit rejected. shared-budget-recovery independently verifies
  the unchanged original guard test exits0. Its separate invocation matters:
  the earlier -k remaining_108 invocation deselected that guard test.
- broad-260:1570passed/3xfailed/exit0 is an earlier candidate FOCUS, not final
  frozen FULL evidence. focused-cov:1599passed/3xfailed/exit0; later candidate
  focus:1613passed/3xfailed/exit0. These are FOCUS, not global coverage.
- label-copy-red:2failed/exit1: missing real Instruction label field and frozen
  named-copy mutation. Actual native fields/owned mutable named copies repair
  these; last-native-focus:1622passed/3xfailed/6warnings/25.16s/exit0.
- The SDK-free native_standard_gate_contracts.py example executes real native
  return types, copy/mutation, controlled gamma, standard QPY and analytic
  Jacobian/Hessian/HVP, exits0 and explicitly states full parity incomplete.
- An independent frozen-R1 guard then exposed a real writer defect:
  p4u3-shared-numeric-probe:1failed/exit1. Individual NumPy values were bounded
  but their encoded element totals were not shared across records/circuits.
  This invalidates R1 as final acceptance. Its healthy driver/active child were
  deliberately terminated only because of this confirmed missing contract,
  not because of a quiet/long-running test. R1 partial passes remain diagnostic,
  not final evidence. The guard is migrated into controlled tests; writer
  numeric admission now shares one budget through recursive records/circuits,
  and matrix-controlled dense export checks numeric work before conversion.
  A fresh exact R2 snapshot must run every final gate; no R1 FULL is reused.
- r2-repair-focus:1625passed/3xfailed/6warnings/28.05s/exit0, including
  shared numeric admission across records and circuits and rejection before
  matrix-controlled dense conversion. No R1 child remains running.

The new tests directly cover full complex matrices,23 concrete class paths,
four-way annotated behavior, parameter/vector/copy lifetimes, foreign hooks,
strict matrix quotas and retained views, real bilateral formats, native
Jacobian/Hessian/HVP, controlled-phase derivatives,100-wire MPS no-dense and
actual Torch/Autograd/JAX/TF gradients. Runtime frameworks remain optional.

## Actual Public Behavior

Actual Qiskit2.4.1/2.6.0 observations agree on the measured outcomes. Generic
control omitted/None/False returns ControlledGate; True returns annotation.
Generic numeric power omitted/None/False returns UnitaryGate; True annotation.
RX/RY/RZ inverse/power remain their rotation classes under all4 choices;
control returns CRX/CRY/CRZ, even annotated=True. Phase behaves similarly.
UGate control returns CUGate; CX/CZ control returns CCX/CCZ. Z.power returns
PhaseGate. X.control and CX.control return mutable controlled objects while
several other standard control/inverse paths retain frozen public defaults.
Do not infer any of this from deprecation warning text.

Public observations are /tmp/qb-stage12b-p4u3-public241/public260 (60 each),
and extra-public241/extra-public260 (168 each, includes the previous60).
Controlled tests make actual public calls independently; these counts are
not additive numbers of SDK functions or complete SDK API parity.

## Final Frozen Gates

R2 is the final runtime snapshot. All27 independent child .log/.exit pairs
under /tmp/qb-stage12b-p4u3-r2- terminated0; the serial driver also terminated0.
The separate final-audit receipt terminates0. No R1 FULL is reused.

- Input tree:b6374819d826685d3741c7c1c1a1abc5709a1c54.
- Production:d4da5d0a48b123c51e8bd3d9e962fff3a2b5ec77.
- Tests:c95920d9e55797d51fffb066374de45a32f5d1d5.
- Examples:27a82b8688a381b4bc1aa237da27e6bd5120b008.
- Actual source:/private/var/folders/c1/gs7_18954qx7td5_t_lnmf4c0000gn/T/qb-stage12b-p4t-foundation-3tw0g7g5/source.

| Gate | Actual final result | Exit |
| --- | --- | --- |
| Compile / legal | compile success /4passed | 0 /0 |
| Circuit / serialization / compiler |52passed /511passed3xfailed /141passed |0 /0 /0 |
| QML / devices |122passed /94passed |0 /0 |
| SDK-free FULL |4473passed1036skipped6warnings;260.21s |0 |
| Main FULL |5728passed5skipped7xfailed64warnings;1443.31s |0 |
| Alternate FULL |5726passed5skipped9xfailed52warnings;508.72s |0 |
| Independent JAX FOCUS |1258passed370skipped1warning;11.06s |0 |
| Independent TF FOCUS |1260passed368skipped1warning;17.86s |0 |
| Torch / Autograd FOCUS |398passed1skipped;71.10s |0 |
| Public2.4.1 /2.6.0 FOCUS |1625passed3xfailed each;27.39s /27.96s |0 /0 |
| Six SDK-free executable examples |six separate terminal receipts |six0 |
| Actual runtime import origins |five separate terminal receipts |five0 |

GLOBAL=30944/33929=91.20221639305609%, above the effective
91.14835394634642% baseline. Exclusions remain68. This is whole-package line
coverage, not SDK feature coverage. standard_gates.py covers258/258 lines;
QPY652/693, IR406/422. No Router appears in the frozen coverage file set.
No new xfail, exclusion, deleted failing test or mathematical tolerance
relaxation is introduced by the three new test modules.

Actual Python is3.12.6 in all five environments. Main imports NumPy2.4.6,
Qiskit2.4.1, Aer0.17.2, PennyLane0.44.1, JAX0.7.1, TF2.21.0,
Torch2.12.0 and Autograd1.8.0. Alternate imports Qiskit2.6.0,
PennyLane0.42.3, JAX0.6.2 and Autograd1.9.1 with the other versions unchanged.
The SDK-free environment imports NumPy2.5.4 and none of the SDKs/four AD
frameworks. Independent JAX0.12.0 and TF2.21.0 environments import NumPy2.5.4,
no SDKs and no other AD frameworks. Every actual QuantumBridge import resolves
to the same frozen R2 source, not the working tree or installed SDK code.

Working-tree legal receipt r2-dirty-legal is separately1failed/3passed/exit1,
solely the existing untracked quantumbridge/router/core.py missing from the
source ledger. Frozen legal is4passed/exit0. No invented Router attribution
is added. Scoped frozen/worktree/stage/commit equality must pass before the
normal local implementation commit; its post-staging receipt is recorded in
the documentary follow-up. No new push or remote CI is verified.

The original28-section matrix and full original P4 acceptance remain NOT_RUN
at this supported standard-gate checkpoint; full U3 remains incomplete.

## Additional Next-U3 Evidence

During R2, runtime code stayed unchanged. Independent public-only boundary
probes instruction-boundary241/260 each terminated0 with43 structured records.
The next-abi-evidence comparison terminates0:42 executable observations agree
after excluding version/generated Circuit names; the signature record stays
separate. These are observations, not43 completed functions.

Actual repeat rejects0,-1,1.5 with CircuitError, but accepts positive integral
float, bool and NumPy integer inputs in both public versions. Opaque and
measured Instruction annotated inverse construction is deferred; ordinary
inverse rejects with CircuitError. Circuit.compose/assign_parameters return
None for inplace=True; Circuit.inverse appends _dg to the returned name.
The independent instruction-boundaries-reds receipt is6failed/exit1 on R2:
two inplace return mismatches, one inverse-name mismatch and three invalid
repeat cases. These extend, not replace, the previous4failed/2passed probe;
three invalid-repeat scenarios are not three different missing functions.
They are explicitly unfinished U3 requirements outside the supported standard
gate checkpoint, not green native parity tests. An untyped AST caller inventory
is only an aid; its one consumed result is a Pauli call, not a Circuit proof.
Public Instruction.control/power remain absent and are not missing APIs.

## Remaining Contracts

- Generic Instruction positional arguments still include native definition/
  metadata fields instead of the public fifth positional label. Actual
  Qiskit2.4.1/2.6.0 probes each made44 observations: defined unitary inverse
  returns Gate by default and AnnotatedOperation with annotated=True; repeat
  exists; Instruction.control and Instruction.power are absent in both
  versions and must not be invented as missing public APIs. An independent
  next-contract probe has4failed/2passed: positional label, inverse return,
  annotated inverse and repeat remain U3 work, outside this green checkpoint.
- Native owned frozen objects do not implement private singleton identity;
  definition recipes are phase-exact but not canonical upstream layout ABI.
  Dedicated return behavior beyond the measured standard paths remains audit
  work, not all possible multi-control/power signatures declared complete.
- UnitaryGate enforces valid unitary execution even with check_input=False;
  arbitrary replacement of its matrix-derived definition is not implemented.
  Generic symbolic integer powers remain a native structural extension;
  unbound fractional/managed spectral powers and nonunitary staged objects
  are explicitly bounded/unsupported, not full public construction parity.
- Arbitrary matrix QASM synthesis is not implied by standard IR/QPY matrix
  interchange. QASM still rejects unresolved annotation objects. Standard
  QPY does not promise arbitrary editable private history or fix upstream
  annotation circuit-index loss.
- Full empty/dynamic/nonunitary constructor contracts remain U4; original
  five-example and28-section joint acceptance remains U5. Do not enter U4
  or claim U3 complete merely because this supported checkpoint is green.
- Existing unowned Router missing-ledger dirty-worktree failure is separate
  from controlled-source legal gates; never hide it with invented attribution.

## Local Commit And Actually Read Continuation

Implementation commit:a23c40e9030eb685c2f41fd5b4d1021db1ca9343 on local main,
25 scoped paths. Its actual tree7a70ad0a10267d4f80b3e722221f7d09d122253c
equals the audited staged tree. Separate snapshot-audit terminates0 and
checks1146 actual frozen/worktree/stage runtime blobs. Runtime manifest
SHA256:3cc539bafa1ac6c2d6a87a3abea228b0e173b7b6e7be254b54d04f1288a247e2.
No protected path is staged; all five runtime subtrees match R2. The commit
uses normal local history; the automatic Git identity/amend suggestion was
not acted on. Cached origin/main showed0behind/46ahead at this implementation
commit; that is not a fresh remote query or new-SHA remote CI verification.

The final implementation report was sent to the owner-authorized ChatGPT
conversation. Its complete rendered review and U3B sections0-11 were actually
read in Chrome (virtualized items28-128 then0-100, with overlap and completed
answer controls). It accepts this supported checkpoint based on the report,
not independent unpushed-source or remote-CI inspection. It requests continued
Instruction/Circuit ABI work, not U4 or full-project completion.

The reply initially mislabeled three Instruction.repeat error tests as Circuit
tests. Independent separate-repeat241/260 probes then each produced7 actual
records/exit0: public Circuit.repeat(0/-1) returns empty Circuits;1.5 and2.0
raise TypeError; True and NumPy integer inputs are accepted with their literal
observed names. This differs from Instruction.repeat's CircuitError/integral
float behavior. The evidence was sent back; the complete correction/table and
completed-answer state were actually read at Chrome AX515-699. Corrected
classification is7 Instruction plus3 Circuit red cases, still10 scenarios,
not10 missing functions. No runtime code changed during this clarification.

The corrected complete task is preserved in
stage12_b_p4u3b_instruction_circuit_abi_execution_prompt.md. It is a received
continuation, not completed implementation. GLOBAL baseline for future runtime
changes is91.20221639305609%, exclusions68. This documentary follow-up does
not alter the tested production/tests/examples/scripts/requirements runtime.
