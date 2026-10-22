# Stage 12-B P4 Native Gate And Circuit Work In Progress

Status: IN PROGRESS / PARTIAL, not final P4 acceptance. Highest independent
Qiskit/PennyLane full replacement/full functional parity goal stays ACTIVE /
INCOMPLETE. No Studio work, cloud/hardware/token use, vendor, tag, release,
history rewrite, push or remote CI claim. Protected user files are unchanged.

## Native Code Progress

Starting local HEAD 7a7740e7500b7d0c5bc5569fea06dad5897d399f. Gate/ControlledGate
are actual native Instruction subclasses with owned validated definitions;
Gate append retains hierarchy, and decompose(reps) expands one level rather
than hiding an already flattened instruction list. Bounded lowering feeds
existing Statevector/Density/MPS, compiler and recorded derivative engines.
No second IR, simulator, Parameter or gradient system is introduced.

Implemented structural paths: to_gate full parameter maps; copy/name/label/
definition validation; direct formal parameter reassignment; simultaneous
binding and preserved ControlledGate type; inverse/integer power/repeat;
bounded numerical principal spectral powers; open/multiple controls; unbound
symbolic controlled phase; tensor quantum/classical mappings; Circuit repeat
including explicit nonunitary/directive paths; nested control-body lowering.

Construction rejects measurements/reset/Kraus/classical state/dynamic control/
directives/unknown nonunitary operations as Gates, without ignoring them.
Checks include cycles, mutated width/namespace, primitive parameter arity,
count/depth/work/repeat/matrix limits, ownership and managed array copies.
Logical construction budgets are not Python heap/RSS bounds. Fractional solver
workspace in managed scopes explicitly rejects rather than claiming allocation
control; generic controlled primitives have explicit missing gradient recipes.

## Actual Early Tests

- `/tmp/qb-stage12b-p4-first-red`: 8 genuine missing-to_gate failures, exit 1,
  including nonunitary rejection and symbolic controlled phase requirements.
- First recovery: wrong existing traversal helper name caused 3 failures / 5
  passed; corrected to append_item, then 8 passed. No upstream code port.
- Adversarial recovery1: one genuine new formal-namespace validation failure,
  plus one misplaced test assertion NameError (test setup, not a production
  defect). Both are retained and separately classified; recovery2 35 passed.
- Nested control-body test exposed a real copied-object-ID lookup bug (1 failed,
  57 passed). Lowering now replaces explicit original body fields before native
  node reconstruction; recovery5 has 58 passed. Managed state/copy tests bring
  the next SDK-free focus to 61 passed.
- Actual public focuses on Qiskit2.4.1 and2.6.0: 69 passed each, exit 0,
  including complete complex control/tensor comparisons with explicit native
  wire-major versus public little-endian bit permutation.
- `/tmp/qb-stage12b-p4-framework-first`: 85 passed, exit 0. Sixteen new actual
  Torch/Autograd/JAX/TF first/second graph cases use native Gate lowering;
  the two interface families are controlled phase and unbound unitary phase.
- `/tmp/qb-stage12b-p4-broad-sdkfree1`: 2080 passed, 198 skipped, 2 warnings,
  180.49 seconds, exit 0 across core/compiler/serialization/qml/devices/
  information. More runtime edits followed; this is NOT final frozen acceptance.
- First immutable foundation tree 0b774066bca72fa26a66733fba427e7e5a399594:
  SDK-free FULL 3936 passed / 678 skipped / 5 warnings / 246.50 seconds / exit 0.
  A later actual iterator-admission red proves Gate consumed all 20 values
  before checking max_gate_parameters=2. Bounded max+1 intake repairs it.
  This and stricter managed native-type admission require a new runtime freeze;
  the earlier FULL is NOT reused as final evidence for the repaired source.
- `/tmp/qb-stage12b-p4-final-preflight`: 88 passed / 4.64 seconds / exit 0,
  including real framework graphs and managed foreign-callback rejection.
- Second foundation tree 6e355e82465c7908f090387f385560a85f6e6361 completes all
  15 development gates, including SDK-free FULL 3939 passed / 678 skipped /
  5 warnings / 245.70 seconds and main focus 1069 passed / 28.47 seconds.
  Focused gates.py coverage 325/356 (91.2921%), limits31/33 (93.9394%);
  global focused coverage is only 47%, NOT full-repository acceptance coverage.
  Subsequent name-dispatch audit finds additional entrypoints needing native
  Gate lowering (tableau, structured engine and optional adapters). Those later
  changes require another regression snapshot; this R2 result is not reused.
- `/tmp/qb-stage12b-p4-entrypoints-final`: 97 passed / 5.05 seconds / exit 0,
  including custom names colliding with primitive gates across all six native
  Aer methods, tableau/Clifford and optional installed public adapters. Named
  instruction-noise boundaries on composite definitions explicitly reject
  until their semantics are implemented, rather than silently losing noise.

The independent nonlinear phase oracle uses f=sin(p)+q*p^2 and observable
cos(f/6), with separately coded Jacobian/Hessian/HVP at three points and two
native methods. Control state tests enumerate computational basis blocks.
Tensor tests use independent Kronecker products, not two native shared paths.
The 100-wire GHZ test forbids StatevectorDevice.statevector,
DensityMatrixDevice.density_matrix, MPS.statevector and Gate.to_matrix;
native MPS expectation and parameter-shift match a separate analytic formula.

## Remaining Required Work

This is not an acceptance shortcut. Still required: definition-aware standard
complete IR/QASM/QPY custom Gate records and broader bilateral interop; native
annotation objects; full mutable Gate/public error/return/list ABI; standard
primitive definition decomposition; full dynamic/composition/empty-circuit
contracts; complete aggregate construction/transport resource admission;
remaining required independent scenarios/examples; final five-environment
FULL/focus, explicit coverage above 90.7832066365959% with unchanged exclusions,
per-file new-module coverage, original complete 28-section matrix, legal/privacy/
no-vendor and staged/committed runtime equality. Earlier P3 results are not reused.

At R3, definition-bearing Gate IR/source export and QPY custom records rejected.
Later P4-S adds real native IR, QASM declarations and standard QPY v13 custom
records, with supported paths tested bidirectionally against both public SDKs.
See stage12_b_p4s_custom_gate_interchange_report.md for that later snapshot;
R3 results below do not certify newer runtime changes. Unsupported opaque/
nonunitary/generic-control protocol branches remain explicit. Annotated
operations and symbolic fractional powers still reject; full Gate/Circuit and
all-SDK parity are NO.

Current work remains uncommitted while P4 development continues. The next action
is finish required native Gate structure/interchange contracts and revalidate
the final runtime, not declare P4 or the highest goal complete.

## Current Development Snapshot Regression

Input tree `d5136e8a8455d77d0f6072191ea87bd32a94ece6`, temporary checkout
`/tmp/qb-stage12b-p4-foundation-r3.FVrury/source`. Production subtree
`4c6698751ec5fc8dd55973a9f9bf819658339d6d`, tests
`c80967f60ec985333dfe8e1dd4c644fb1dc3350e`, examples unchanged from P3.
All 1086 controlled runtime files exactly match the working checkout.
Development driver session61802 terminated exit0, with 15 independent child
log/exit receipts at `/tmp/qb-stage12b-p4-foundation-r3-`.

| Development gate | Actual result, all exit0 |
| --- | --- |
| SDK-free FULL | 3947 passed, 679 skipped, 5 warnings, 245.98 s |
| Main focused core/compiler/serialization/devices/resources | 1078 passed, 1 warning, 30.18 s |
| Alternate new Gate focus | 97 passed, 5.17 s |
| Independent JAX new Gate focus | 76 passed, 21 missing-dependency skips, 1.36 s |
| Independent TF new Gate focus | 76 passed, 21 missing-dependency skips, 1.90 s |
| Compile/legal | compileall succeeds; controlled legal4 passed |
| Public calls | 41 literal public outcomes per version, separately retained |
| Origins | five actual interpreters import the frozen checkout |

Main focus includes actual Torch/Autograd/JAX/TF graphs, not SDK-free skips.
Focused new-module coverage: gates325/356=91.2921%, limits31/33=93.9394%.
The focused full-package total is 15557/32230=48.2687%, excluded68 unchanged;
this is NOT a new global FULL coverage result and does not satisfy final P4
full-suite/matrix acceptance. Main/alternate FULL and original full matrix are
still NOT_RUN for this development snapshot. The prior P3 baseline is historical.

Both frozen Git-path no-vendor and scoped credential-pattern scans have no
matches (rg exit1, not failed tests). No secrets were printed. Fresh dirty
whole-worktree legal result is 1 failed / 3 passed, exit1, solely user-owned
quantumbridge/router/core.py missing attribution; it is not staged/reverted or
given fake attribution. Controlled snapshot legal passes separately.
Normal index remains empty; no new P4 commit, push, tag, release or remote CI.
The development driver SHA256 is
903c8718ed512136705abe98979f9c4e8f545ee10742c3101bbb78e567fed5ff.

## Later P4-S Development Checkpoint

The later custom-definition interop work is recorded in
stage12_b_p4s_custom_gate_interchange_report.md, not certified by the historical
R3 foundation results above. Current production057ab292/tests9f351370 have
SDK-free/main/alternate FULL3988/4925/4923 passed, with separately disclosed
skips/xfails/warnings. Full main coverage90.8235%, excluded68; both new core
modules exceed90%. Original complete matrix is NOT_RUN, annotations/ABI/other
original P4 requirements remain pending. This remains a bounded partial
development checkpoint, not P4 DONE or full SDK replacement.
