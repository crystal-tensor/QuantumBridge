# Stage 12-B P4-U1 Annotation QPY Checkpoint

Status: IN_PROGRESS / PARTIAL. Highest full Qiskit/PennyLane replacement
goal remains ACTIVE / INCOMPLETE. No Studio work, cloud/hardware submission,
authentication, token access, push, tag or release in this batch.

## Scope

Build on main HEAD 4c97d31ceea1594080cc2d4379a84e7df5e08ed8 and P4-T
implementation 8e6ef77328c7924b4f996ab0d93da5b709ae7346. Reuse the existing
native codec and operation/derivative engines. Independently implement QPY
v13 custom `a` and typed `m` records; retain actual AnnotatedOperation rather
than pre-resolving to a Gate. Base operations include standard Gate class
records, executable custom Gate/ControlledGate and unitary Instruction
definitions, nested annotations, open control states, labels where native
objects represent them, and symbolic base parameters/phase/UUID/vector data.
No public SDK is imported by the native codec. Reference:
https://quantum.cloud.ibm.com/docs/en/api/qiskit/qpy.

## Actual Red/Green Evidence

Initial two real positive requirements failed in both public target versions
before implementation. Owned first red prefix:
`/tmp/qb-stage12b-p4u-owned-red`, exit1, 2 failed.
Reverse decoding then passed; native-to-public circuit parameter indexing
remained red. Public-to-public v13 roundtrips reproduce that index loss in
both 2.4.1 and 2.6.0. The base object retains its real parameters and UUID;
the enclosing loaded public circuit reports none. Two strict expected
failures keep that direct contract visible for native and public producers.
The positive symbolic public binding test explicitly reappends the restored
object through the public API; this is NOT proof that the original loaded
circuit supports direct binding. Numeric bound native bytes are also loaded
and evaluated directly by the public Operator, without reappend.

Expanded tests contain13 independent native roundtrip cases and26 actual
bilateral scenarios: inverse, integer/fractional power, coherent phase,
ordered/nested modifiers, controlled custom/Instruction bases, standard-name
collision, symbolic vector sin/exp, noncontiguous wires, two control bits and
empty definitions. Independent MSB-ordered complex matrices check the full
operator, not probabilities alone. Multi-control state1 uses q0=1,q1=0;
the initial independent oracle's reversed-bit block was corrected after both
real public versions and native execution agreed on the control-bit order.

Adversarial coverage includes15 malformed binary variants, aggregate
multi-circuit definition/parameter/instruction/depth/work limits, cycle and
forward-reference resolution, object ownership, private metadata rejection,
and symbolic/inexact modifier-power rejection. A separate real expansion
budget red (prefix `/tmp/qb-stage12b-p4u-expansion-red`, exit1) exposed missing
writer admission for definition operations. The writer now admits cumulative
definition and modifier work before emitting/copying those definitions.
Instruction structural metadata duplicated from the definition is transported
through that standard definition; unrelated per-object metadata still rejects.

Actual QPY roundtrip -> native QNode -> analytic Jacobian/Hessian/HVP and
compiler basis conversion are tested. A 100-wire MPS value/gradient test
patches all relevant dense matrix/state entry points to fail if called.
SDK-free examples now include real QPY and vector sin/exp gradients.

Main and alternate focused tests after the runtime repair:
`/tmp/qb-stage12b-p4u-final-focus-241` and
`/tmp/qb-stage12b-p4u-final-focus-260-r2`: each627 passed,3 xfailed,exit0.
The third existing expected failure is the earlier public QASM2 custom
name-collision export defect. Warnings include public unused vector elements;
the unused vector owner slots are not claimed to preserve public identity.
An alternate focused coverage attempt (without the `-r2` suffix) failed at
collection with13 NumPy reimport errors after targeting an eager-imported
module for coverage. This is recorded as exit2, NOT a pass. The normal
alternate focused invocation terminated0; no package reinstall was performed.

## Frozen Regression

Frozen input tree:25be9ef6f33bf20ff0bd45e86c662abdcc79e9a8.
Actual source folder:
`/var/folders/c1/gs7_18954qx7td5_t_lnmf4c0000gn/T/qb-stage12b-p4t-foundation-gldre4dq/source`.
Production tree:da4f8eede5fb2849192d7087c33bda8b8335b046;
tests:7fd53c3468df9434ad05c357d90a804be5877509;
examples:41fa7cd51283bfbb15a074ef3afc3aead007d295.
The historical helper's p4t folder prefix does not make this old P4-T code;
the exact input/runtime hashes identify this new P4-U1 snapshot.

Serial driver session39868, helper `/tmp/qb-stage12b-p4u1-gates.py`, receipts
prefix `/tmp/qb-stage12b-p4u1-r1-`. The driver and all19 child tasks actually
terminated0. Completed results:

- compileall:exit0; controlled legal:4 passed/exit0.
- SDK-free FULL:4188 passed,775 skipped,6 warnings,253.59s,exit0.
- Main2.4.1/PL.44.1 FULL with explicit global coverage:5183 passed,5 skipped,
  6 xfailed,63 warnings,1475.67s,exit0.
- coverage-json:exit0;30160/33126=91.04630803598381%, excluded68 unchanged.
  qpy.py575/608=94.57236842105263%. These are line coverage, not feature parity.
- Alternate2.6.0/PL.42.3 FULL:5181 passed,5 skipped,8 xfailed,51 warnings,
  511.73s,exit0.
- Independent JAX focused:497 passed,133 skipped,1 warning,4.58s,exit0.
- Independent TensorFlow focused:497 passed,133 skipped,1 warning,5.45s,exit0.
  These are focused tests, not FULL environment suites.
- Final main/alternate public/native focuses:each627 passed,3 xfailed;
  9.05s/8.93s,6/2 warnings,each exit0. Main FULL includes actual available
  Torch/Autograd interface tests; this is not independent framework FULL.
- Four SDK-free examples each exit0: native_custom_gate_interchange,
  native_annotated_gate, native_gate_modifier_gradient,
  native_standard_gate_decomposition. All contain real numerical assertions.
- Five actual import-origin/version checks each exit0 and point to this
  frozen source. No global package installs or dependency upgrades performed.

Previous valid explicit full coverage baseline was30029/32997 =
91.00524290086977%. No exclusion increase or focus-as-global substitution.
Independent receipt/origin/coverage audit
`/tmp/qb-stage12b-p4u1-final-audit` terminated0, confirming all19 receipts,
five actual origins and coverage at or above the prior baseline. Exact
frozen/worktree/staged equality is checked before the normal local commit;
the post-commit SHA/identity is reported separately without amending history.
Additional review guard/probe evidence is in
stage12_b_p4u1_review_and_p4u2_continuation.md; those external focused checks
are not added to the original frozen FULL test count or global coverage.

The separate dirty working-tree legal invocation
`/tmp/qb-stage12b-p4u1-dirty-worktree-legal` still terminates1 with1 failed /
3 passed, solely the pre-existing unowned quantumbridge/router/core.py
missing attribution entry. It is not a new controlled-source regression;
its source was not copied, removed, staged or falsely attributed in this batch.
The original28-section local matrix and remaining P4-U tasks are not yet
accepted by this checkpoint. Five original P4 examples/joint acceptance,
mutable parameter-list validation, literal standard return/error ABI and
dynamic/empty contracts still need completion before P4 closure.

## Boundaries

- QPY version13 only; no private JSON/sidecar field pretending to be QPY.
- Symbolic modifier exponent has no standard v13 double representation;
  explicit UnsupportedFeature. Inexact large integer exponents also reject.
- Public circuit parameter-index roundtrip defect remains an explicit gap.
- Native standalone custom Instruction object identity cannot survive its
  current eager append path; top-level `i` records reject, unitary bases work.
- Nonunitary bases, arbitrary object metadata, annotation labels and native
  Instruction labels not represented in the object protocol reject.
- Dedicated standard return classes, mutable params and full SDK parity are
  not supplied by this binary-codec checkpoint.
- No newly verified remote GitHub state/CI. Cached origin/main is not live
  remote evidence. Protected Router/Studio dirt must not be staged/reverted.

## Local Checkpoint Identity

Normal local implementation commit:
ed79a81c1c675947f98c285ba578191422c57247,
`feat: support native QPY annotated operation interchange`.
Its complete tree is b7fbff0deb454d5c395970a856a2b12addea726f. Nine exact
owned paths;910 insertions/92 deletions including tests and reports, not
a function count. No amend/rebase/reset/force or global identity change.

`/tmp/qb-stage12b-p4u1-staged-audit` terminated0. It compared1136 controlled
runtime blobs in the ACTUAL frozen source folder, current working files,
staged tree and tested Git input. Commit tree equals that exact staged tree;
production/tests/examples subtrees equal the frozen hashes above, with
scripts/requirements unchanged. Runtime manifest SHA256:
1f59c4b597858a3939f90cd58cb4e53eb7d8742a0fb474ffa1181729538952d7.
Staged patch SHA256:
583588829e3f3d9af13a05a242155cac18c53a5d07050a7af5cae932cd40efd0.
Protected paths staged=false; no new cloud/auth/vendor artifacts.

After commit, only pre-existing protected Studio/Router/other unowned dirt
remained. Main is42 commits ahead of cached origin/main, behind0; this is
not live remote verification. No push or new-SHA remote CI claim. Any later
checkpoint identity/received-task report update changes documentation only,
not the already tested runtime. All required execution sessions terminated.

Final result message5e10b249-5add-4bb0-8ebd-d09045cecdc9 received completed
ChatGPT reply d9ad068a-7fa5-432b-afd0-83d39bb26b1f. Its full actual rendered
body/table/continuation was read. Report-based supported U1 checkpoint
confirmation, no newly reported blocker, immediate U2 mutation/validation
implementation next. This does not independently certify unpushed source,
remote CI, complete P4-U/P4 or full SDK parity. The faithful normalized
received continuation is in stage12_b_p4u1_review_and_p4u2_continuation.md.
