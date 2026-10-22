# Stage 12-B P4-S Custom Gate Interchange Development

Status: IN PROGRESS / PARTIAL. Original P4 and the independent full
Qiskit/PennyLane replacement/parity goal remain INCOMPLETE / ACTIVE. Starting
local HEAD: 7a7740e7500b7d0c5bc5569fea06dad5897d399f. At the start P4 changes were
uncommitted and the normal index empty. Scoped checkpoint identity is recorded
after verification below. No Studio/Router edits, push, PR, cloud/hardware,
token/auth/TLS work, vendor, tag, release or history rewrite. No remote CI claim.

## Actual Implementation

- Existing IR serializes actual native Gate/ControlledGate records, definitions,
  full symbolic AST/UUID/vector elements, nested phase, labels, controlled base
  and open-control state. Decoding validates record type/width/namespace before
  publishing an owned Gate; the definition wins over primitive name dispatch.
- Standard QPY v13 CUSTOM_DEFINITIONS and CUSTOM_INSTRUCTION records use native
  binary readers/writers with circuit subpayloads, per-invocation local names,
  labels/parameters, g/c type distinction and base-instruction records. Public
  APIs are only comparison oracles; no public codec is delegated to at runtime.
  The closed-control stored definition is distinct from the object's ctrl_state.
- QASM2/3 export emits safe local identifiers and dependency-ordered gate
  declarations with formal/local wires, expressions and representable phase.
  Native parsing now preserves unitary custom Gate hierarchy; existing source
  directive/barrier paths stay non-Gate composition. Existing compiler/state/
  density/MPS/derivative paths are reused, not a second evaluator.
- ControlledGate binding now retains its actual owned definition and display
  name instead of silently replacing it with a fresh base-only synthesis.
- Aggregate definition/instruction/depth limits, early source-copy admission,
  QPY payload/reference/expansion limits, native record validation and cycle
  checks reject malformed inputs. Logical structure/transport budgets do not
  claim Python allocator or total process RSS measurement.

Protocol references: https://quantum.cloud.ibm.com/docs/en/api/qiskit/qpy and
https://openqasm.com/language/gates.html. Only published specifications and
literal installed public calls were used, not upstream implementation/tests.

## Actual Reds And Recoveries

- `/tmp/qb-stage12b-p4s-first-red`: six actual failures, including IR name
  collision/nested definitions and both public QPY directions. First recovery
  passes all six. A subsequent -k ir invocation also selected qpy via the word
  wires: its QPY failure is not an additional IR defect.
- First wider preflight: one test-only nonexistent qb.Operator reference and
  four JAX float32 errors because the required JAX_ENABLE_X64 environment flag
  was omitted. Fixed the test import and reran with the declared x64 environment;
  no tolerance relaxation. Later aggregate IR depth red exposed an off-by-one;
  fixed before the development snapshot.
- QASM red demonstrates missing declarations. Recoveries exposed a test-only
  parameter collision with default register q, then reserved keyword angle;
  corrected the test parameter to theta. An older flattened-op assertion now
  checks retained Gate structure plus lowered operations, preserving mathematics.
- The first public QASM2 reverse test found actual upstream loss: custom Gate
  named h with X definition exports as plain h, without its definition. Both
  public self-roundtrip and native import then produce H. This one case is
  XFAIL with the exact behavior asserted; it is NOT an interop match.
- The first SDK-free example used a vector tangent with a scalar trainable
  input and correctly failed the existing HVP shape contract. The example now
  supplies scalar tangent .3; native derivative behavior was not weakened.

## Pre-Freeze Evidence

Main and alternate public focuses each: 67 passed, 1 observed upstream XFAIL,
exit0, before the last three resource/malformed-phase tests. Twenty distinct
QPY directional scenarios per version compare to independent complex matrices;
they are not twenty numerical points or self-roundtrips. Public QASM checks
cover real bound declaration imports/exports; the known QASM2 loss is separate.
Main emits two documented QPY warnings for unused vector elements; only used
element identity and vector metadata are claimed, not public unused identities.

SDK-free example succeeds after the tangent correction. IR/QASM3/QPY maximum
full-operator errors are respectively 1.24e-16, 1.57e-16, 1.24e-16. All three
produce gradient -0.0892271885152293 and HVP -0.067149129146642, matching
independently coded derivatives of cos((sin(theta)+2theta)/6).

Current/final snapshot gate results will be recorded below only after actual
process termination. Pre-freeze results are not reused as final acceptance.

The first frozen input tree 2a6de20721498ad08f0d87f0c4c3f1b5b77c5a0b fails
SDK-free FULL: 1 failed / 3981 passed / 715 skipped / 5 warnings, exit1,
257.74 seconds. The real failure is existing generated-H2 transform compilation:
internal pass comparison inherited the external transport expression-depth48
limit from the new encoder. Internal comparison now explicitly uses the existing
native symbolic construction depth128, while external IR JSON retains depth48.
A focused regression checks this distinction without raising wire-format limits.
That failed snapshot's driver stops before main/alternate FULL, not claimed run.

Second development freeze 65da9666e2a0748bd1934f1f2eb024f15b1c1d4d passes
SDK-free FULL:3985 passed/715 skipped/5 warnings/257.43 s/exit0. A separate
actual two-case red then proves bound complex rotation angles were admitted as
Gates before execution rejected them. Validation now uses real bound parameters
and only substitutes placeholders for genuinely unbound symbolic arguments;
bound complex phase ASTs also reject. The widened recovery has587 passed/1
public XFAIL/2 warnings/8.53 s/exit0, before adding the bound phase case.
The obsolete R2 main FULL is deliberately terminated on its verified owned
pytest PID after this source change; child receipt -15, driver241, NOT_COMPLETED.
Alternate FULL and remaining R2 gates were not started. These are not failures
of the repaired source, not passing FULL results and not reused for new runtime.

## Explicit Remaining Boundaries

P4-S is not marked complete. More required independent IR/binding/resource
scenarios and complete final same-runtime gates remain. Supported QPY c records
are limited to definitions representable by existing standard primitive records;
generic native_controlled descriptors, opaque matrices, custom nonunitary
Instruction records and wider/newer QPY protocols remain Unsupported. No private
JSON or sidecar masquerades as a standard QPY field.

Review identified an aggregate-limit boundary: existing ControlBlock._encode/
_decode started separate IRProgram codec contexts for its circuit bodies.
Those transitions now share the existing context and vector/parameter counters,
including depth/cycle admission. A two-branch limit test and mutated recursive
control-body test exercise the repair. The focused H2/serialization/core/compiler
recovery has 585 passed / 1 observed public XFAIL / 2 warnings, exit0,8.21 s.
This repair requires a new frozen runtime; the earlier failed FULL is not reused.

QASM2 cannot retain general internal global phase and rejects it even with
metadata loss enabled. Source cannot preserve arbitrary parameter UUID/vector
identity, labels, object classes or source names: safe local declaration names
preserve executable semantics, not full object ABI. Explicit metadata loss is
required where supported; existing invalid/reserved source parameter identifiers
still reject. Bound phase-free public QASM tests do not certify every unbound
symbolic phase/dynamic language branch. Generic controls/modifiers remain partial.

Original P4 annotations, full mutable/error/return ABI, standard primitive
definitions, dynamic/empty-circuit contracts, remaining aggregate/managed copy
contracts, five original examples and the final full matrix/coverage gates are
not completed by this work. Full Qiskit/PennyLane core API replacement is NO.

## Final Development Snapshot Results

Input tree `2b6b31592c3a7588988e3b9c6881fa0ee00fb5e6`, controlled checkout
`/tmp/qb-stage12b-p4s-foundation-r3.RCfRkA/source`. Production subtree
`057ab2921f1a1e09ac10334e7dbe6d68877c524d`, tests
`9f351370ab6cf7d23a75324e87dd99e268c72c85`, examples
`1447cb7f549a3ab672fd017efb1a715df5f62f09`.
All1088 controlled runtime files match the working checkout. After freeze only
report metadata changes are permitted; earlier failed/interrupted snapshots are
not reused. Session28371 actually terminated exit0, all16 child receipts exit0,
with logs and independent exits at `/tmp/qb-stage12b-p4s-foundation-r3-`.

| Actual gate | Result |
| --- | --- |
| SDK-free FULL |3988 passed,715 skipped,5 warnings,258.05 s,exit0|
| Main FULL with explicit coverage |4925 passed,5 skipped,4 xfailed,59 warnings,1456.71 s,exit0|
| Alternate FULL |4923 passed,5 skipped,6 xfailed,49 warnings,505.03 s,exit0|
| Independent JAX focus |117 passed,57 missing-dependency skips,2.05 s,exit0|
| Independent TF focus |117 passed,57 missing-dependency skips,2.66 s,exit0|
| Main public custom-format focus |76 passed,1 observed public XFAIL,2 warnings,.53 s,exit0|
| Alternate public custom-format focus |76 passed,1 observed public XFAIL,.54 s,exit0|
| Compile and controlled legal |compileall succeeds,legal4 passed,exit0|
| SDK-free executable example |complex operator/gradient/HVP math checks pass,exit0|
| Five import origins |all five resolve to the controlled checkout,exit0|

The main FULL includes the actual existing four-framework graph regressions,
H2 parameter-shift/adjoint Hessian/HVP/Newton and TensorFlow second derivatives;
the slow H2 cases were retained, not skipped. Missing modules in isolated
framework environments remain skips, not claimed framework execution.

Full main line coverage is29623/32616=90.82352219769439%, with68 excluded lines
unchanged, above the historical90.7832066365959% baseline. New core Gate module
341/372=91.6667%, limits31/33=93.9394%. Existing IR274/287=95.4704%, QPY445/479=
92.9019%, source exporter276/284=97.1831%, lowerer333/346=96.2428%.
This coverage is not a functional completeness percentage.

The separate whole dirty-workspace legal check is1 failed/3 passed/exit1, solely
user-owned quantumbridge/router/core.py missing ledger attribution. It is not
staged, reverted or given an unsupported source attribution. Controlled legal
passes separately. Frozen tracked-path vendor scan and scoped credential-pattern
scan have no matches (rg exit1 means no matches). Git diff --check succeeds.
No remote CI or dependency-install change is claimed.

The original28-section local matrix is NOT_RUN for this P4 development tree;
original P4 examples/annotations/ABI and remaining parity work are still required.
These16 development gates do not make original P4 or the highest goal complete.
Driver SHA256:
dd01f9bd8a5a65298b31cf53c5434f95f4a5342726007dfa51491f4d8bbf4432.
