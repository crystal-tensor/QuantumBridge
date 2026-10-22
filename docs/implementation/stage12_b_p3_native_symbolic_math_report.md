# Stage 12-B P3 Native Symbolic Mathematics

Status: IMPLEMENTED / BOUNDED LOCAL ACCEPTANCE PASSED. Highest full-core replacement
goal remains ACTIVE / INCOMPLETE. This report is not full class/SDK parity.

## Starting State And Publication

- Starting local main HEAD: 0ef945242b0950b30e4fdf5e4e32f028e2033f75.
- Cached origin/main: 45fe338fc0f02de9c19e0af89723755952e5fc98, 0 behind/35 ahead.
  This is not a fresh remote observation. No fetch, push or new-SHA CI claim.
- Local code commit and ending SHA are recorded by the subsequent publication
  receipt after the scoped commit. No prior commit is rewritten, and no
  branch/PR, tag or release is created.
- Existing five tracked Studio modifications and all untracked Router/Studio
  artifacts remain protected and excluded from controlled source snapshots.
- Previous goal turn was progress: actual P2 implementation plus terminal
  same-runtime gates and local commits, not an unexecuted status restatement.

## Native Implementation

| Capability | Current evidence and boundary |
| --- | --- |
| sin/cos/tan/exp/log | Native immutable AST, bind, symbolic first/second/mixed calculus, complex scalar principal branches, analytic and public comparisons |
| arcsin/arccos/arctan | Native real supported domains and explicit complex arguments; analytic derivatives and trace second rules; real endpoint singular derivatives reject |
| abs/sign | Native real piecewise calculus with zero guards; complex abs forward supported, its ordinary real derivative rejects complex arguments; sign complex unsupported |
| conjugate | Native scalar conjugation, real-parameter derivative convention, public numerical checks |
| subs/assign | Atomic name/UUID validation; simultaneous original-reference replacement; assign accepts numbers, subs requires symbolic replacements |
| bind/bind_all | Numeric-only public bind plus native string keys/allow_partial; full bind returns native scalar, NOT identical public return ABI |
| gradient | Independent recursive AST chain/product/quotient/power/unary rules, not SymPy or upstream differentiation; constant gradients stay expressions for repeated calls |
| numeric/is_real/is_symbol | Syntactic parameters retained for zero/cancellation; supported nonstrict mathematical-zero proof; unknown reality remains None |
| sympify | Optional outward SymPy expression only, UUID loss documented, no reverse untrusted graph injection |
| Resource limits | Nodes/depth/parameters, substitution count, power/integer/magnitude, derivative lineage, cumulative nested scoped work, transport bytes; not measured Python heap/RSS |
| Circuit/Instruction/phase | Actual partial/formal mapping, reuse, inverse/power, full complex Operator/state/density and bound coherent control |
| Native derivatives | Existing parameter-shift/adjoint plus nonlinear preprocessing; independent analytic Jacobian, mixed Hessian and streamed HVP |
| Framework graphs | Actual Torch/Autograd/JAX/TF first and second graphs from native symbolic circuit; guarded nonsmooth derivative nodes require native real trace |
| Compiler | Existing native basis pass preserves function parameters and full phase; compiled reconstruction dispatches existing native/framework math |
| IR | Typed function AST, UUID/vector identity, complex scalar literal codec, aggregate parameter nodes and pre-recursion depth bounds |
| QASM3 | Real parser/lowerer/exporter function subset and loop-local scope; sign/conjugate/guarded derivative functions remain Unsupported |
| QPY v13 | Published unary replay and complex literal encoding, bilateral scalar function and nested derivative/substitution public payload tests; no private JSON payload |
| State/MPS | Actual state/density execution and SDK-free MPS roundtrip example assertions |

## Red And Recovery Evidence

All paths below have complete `.log` and independent `.exit` siblings.

- Initial wrong runner invocations attempted to execute a directory, did not
  run tests and are not functional reds. Corrected
  `/tmp/qb-stage12b-p3-red-initial-v2`: six genuine missing sin/subs failures,
  exit 1. The first recovery has 110 passed / exit 0.
- `/tmp/qb-stage12b-p3-integration-1`: 165 passed / 14 optional skips / exit 0.
- `/tmp/qb-stage12b-p3-main-symbolic-1`: 160 passed / exit 0.
- `/tmp/qb-stage12b-p3-broad-sdkfree-1`: 1475 passed / 276 skips / one failure,
  187.63 seconds / exit 1. Old malformed-QPY setup constructed an identity
  collision now rejected earlier. Constructor guard retained; raw illegal
  separate operations still prove writer rejection. Recovery exits 0.
- `/tmp/qb-stage12b-p3-framework-calculus-1`: module-specific coverage source
  imports caused NumPy re-import collection errors, exit 2; not a passing run.
  Root-package coverage recovery exits 0; no global environment was changed.
- `/tmp/qb-stage12b-p3-framework-calculus-2`: four actual framework cases
  passed, 6.36 seconds, exit 0; not just import or interface metadata.
- `/tmp/qb-stage12b-p3-rootcov-symbolic`: 220 passed, 4.87 seconds, exit 0;
  focused-only coverage (NOT global acceptance) records parameters 444/495,
  limits 41/44. More tests/runtime edits followed; final coverage must rerun.
- `/tmp/qb-stage12b-p3-qpy-nested-observation`: 52 passed / exit 0, including
  actual public nested derivative/substitution payload and loop source.
- All five new examples terminate exit 0 with explicit `PYTHONPATH=.` in
  their `-v2` receipts. Initial plain script launches imported a previously
  available package lacking sin, not the edited checkout; do not count them
  as implementation proof or hide this import-origin distinction.

## Public Observations And Differences

`docs/compat/stage12_b_p3_parameter_expression_contracts.json` retains all
110 literal outcomes per installed version (2.4.1 and 2.6.0). Calls/signatures
are implementation references; no upstream source lookup or source/test port
is used. Incidental SDK traceback frames are disclosed below. The 33 optional
elementary scenarios additionally compare native values/supported gradients
with the actual public objects. Both versions lack sqrt as a method. Public
sign gradient rejects; native explicitly supports only nonzero real regions
with zero guards. Full bind scalar return, constant gradient expression
return, string-key extension and error/limit ABI are disclosed differences.
Neither this JSON nor matching numerical focuses imply complete parity.

## Pre-Acceptance Repairs And Invalidated Runs

Additional actual defects were discovered before acceptance:

- R2 frozen tree f534deeda90951037e313755db2b50b18ea4a7f2 has SDK-free FULL
  3863 passed / 611 skips / 5 warnings / 243.97 seconds / exit 0. Its main FULL
  was deliberately interrupted after a new, confirmed Torch abs/sign zero
  derivative red required runtime changes. Fresh child PID/parent/pytest
  command were verified before SIGINT; driver and main gate terminated exit 2.
  R2 is NOT final acceptance; no old/new runtime results are combined.
- `/tmp/qb-stage12b-p3-framework-nonsmooth-red`: two genuine DID_NOT_RAISE
  failures. New interface rules preserve legal forwards, reject zero/boundary
  derivatives and retain nonzero first/second derivatives on four frameworks.
- TF graph-only first attempts (`framework-domain-recovery-2` and `-3`)
  finished four failed / 36 passed: a gradient override in the tracing tape
  did not preserve the guard into the second derivative. An isolated function
  boundary plus stateless guarded IdentityN rules repairs this without
  per-request payload registration. Recovery `-4` has 47 passed / 141 deselected
  / 4.84 seconds / exit 0; all singular-domain negative assertions remain.
- `/tmp/qb-stage12b-p3-numpy-integer-red`: one true integer wraparound failure,
  3000000**3 returned np.int64(8553255926290448384). Native numeric leaves and
  bindings now normalize Integral values to budget-checked Python integers.
- Specification correction: `/tmp/qb-stage12b-p3-vector-alias-red`,
  `qpy-vector-alias-red`, and the first public-alias attempts used an incorrect
  assumption that scalar/vector subclasses with matching displayed names and
  UUIDs should merge. Existing literal P2 public probes in BOTH versions say
  equality is false. The temporary unification/canonicalization was removed;
  original distinct-kind identity remains. Corrected tests assert distinct
  kinds and reject ambiguous native display-name or QPY namespaces, not a
  manufactured equality contract. These are specification failures, NOT
  claimed production defects. Public can encode some mixed-kind circuits that
  native intentionally rejects; this remains an explicit Partial boundary.
- Direct live JAX nested JVP/domain and TF graph guard focuses complete at
  `/tmp/qb-stage12b-p3-framework-domain-recovery-5`: 44 passed / 5.61 seconds /
  exit 0. TF graph first/second guards use isolated function boundaries and at
  most eight process-wide name/code-only rules, without request payloads.
- Public exception test failures can print SDK traceback frames. These are
  retained diagnostic outputs, not implementation references; no source
  lookup, source/test port or vendored SDK code is used. Corrected public-edge
  tests capture specified exceptions and focuses use short tracebacks.
- A separate 70-digit Decimal Taylor-series/exp oracle ran on R2 and checks
  f, two first derivatives and three Hessian components at three points.
  The repaired final runtime must rerun that check too. It is an independent
  host verifier, not production SymPy/upstream differentiation.
- `/tmp/qb-stage12b-p3-repair-prefreeze-main`: 364 passed / 14.65 seconds /
  exit 0 after the real interface/integer repairs. Focused module coverage is
  parameters 458/498 (91.97%), limits 55/55, interface guard 75/81 (92.59%).
  These are not whole-repository acceptance percentages. Direct live JAX
  guarded-JVP checks were then added before the repaired final freeze.
- The reproduced plain-script import origin is
  `/private/tmp/qb-clean-JeYCEF/quantumbridge/__init__.py`; checkout examples
  and final gates therefore use explicit PYTHONPATH and record actual origins.
- R3 frozen tree 0c943dda1d2c57fd1a0ada89e68851cb6deb3e80 was not accepted:
  its SDK-free FULL was intentionally interrupted after two further actual
  binding regressions were proven. Driver and SDK gate terminated exit 2,
  after verifying child PID/parent/command. `/tmp/qb-stage12b-p3-binding-budget-red`
  has two true failures: internal resolution scanned unrelated circuit-wide
  bindings and the new default magnitude rejected previously finite 1.5e308.
  Resolution now looks up referenced identities only, with local substitution
  checks; default numeric magnitude is the finite double maximum, and default
  parameter/substitution counts retain the existing 100000-node envelope.
- `/tmp/qb-stage12b-p3-derivative-lineage-red`: three genuine budget failures;
  identity assign/subs/bind reset derivative lineage. Replacement/simplification
  now preserve the order without mutating borrowed originals. Existing AST
  replacements are checked before admission to a stricter symbolic scope.
  Repaired focuses pass; all final immutable-source gates must rerun on R4.

The repaired final controlled snapshot includes all owned new paths and
excludes unrelated user files. All final gates below use that same production,
tests and examples runtime; the original matrix generates inventory metadata
inside its temporary checkout, not in the user's checkout or staged files.
Earlier interrupted/failing receipts remain distinct from final acceptance.

P2's 90.66067992302759% line-coverage baseline and 68 exclusions are not lowered
or replaced by focused coverage. Optional missing Finance/Optimization/ML/
Dynamics/Metal/Experiments/Addons, existing pip conflicts and dirty Router
legal failure must be freshly distinguished from controlled test results.
No xfail, tolerance, coverage exclusion or dependency installation was added
to make the new implementation pass.

## Final Immutable Runtime And Terminal Gates

Final input Git tree: `d2204131731a8e943987222ac2719ec5b0b1e8cd`.
Checkout: `/tmp/qb-stage12b-p3-r4-final.14peIt/source` (resolved under
`/private/tmp`). Runtime subtrees:

- production: `7698e318ae01eaa45272d7d8cb140f7083f052a3`;
- tests: `df3c402c7a811769828af4e265f02cf4065e73b1`;
- examples: `c5e8d6d57e99e7669e34564f4747643bff92db5b`.

All 1083 controlled runtime files match that tree in the frozen and working
checkouts. Final metadata-only reporting changes do not alter tested runtime.
Driver session 95935 terminated exit 0, not yielded/running. The 38 child
receipts have prefix `/tmp/qb-stage12b-p3-r4-final-`, each with independent
`.exit` and complete `.log`; audit receipt adds `audit` to that prefix.

| Gate | Actual terminal result |
| --- | --- |
| SDK-free FULL | 3875 passed, 654 skipped, 5 warnings, 244.20 s; exit 0 |
| Main FULL, explicit --cov=quantumbridge | 4752 passed, 5 skipped, 3 xfailed, 57 warnings, 1396.20 s; exit 0 |
| Alternate FULL | 4750 passed, 5 skipped, 5 xfailed, 49 warnings, 477.09 s; exit 0 |
| Independent JAX 0.12 | 857 passed, 199 skipped, 33.32 s; exit 0 |
| Independent TensorFlow | 879 passed, 182 skipped, 45.65 s; exit 0 |
| Torch/Autograd focused | 64 passed, 1010 deselected, 14.18 s; exit 0 |
| Original run_local_matrix.sh | All 28 sections reached, terminal exit 0; two additional FULL runs and explicit coverage included |
| Compile | quantumbridge, tests and examples compile; exit 0 |
| Controlled legal | 4 passed; exit 0 |
| Privacy/offline | 49 passed across 17 files; exit 0 |
| P2 public probes and execution examples | Both SDK versions and main/SDK-free examples; exit 0 |
| P3 public probes | Actual 2.4.1 and 2.6.0, 110 literal outcomes each; exit 0 |
| Five P3 examples | Actual main and SDK-free execution, ten terminal exit-0 receipts |
| Acceptance audit | 38 receipts, five frozen import origins, public records, matrix and coverage checked; exit 0 |

All five interpreters are Python 3.12.6. Actual origins/version logs are the
`versions-{main,alternate,sdkfree,jax012,tf}` receipts. Main uses Qiskit 2.4.1,
PennyLane 0.44.1, Aer 0.17.2, NumPy 2.4.6, JAX 0.7.1, TF 2.21.0, Torch 2.12.0,
Autograd 1.8.0. Alternate uses Qiskit 2.6.0, PennyLane 0.42.3, JAX 0.6.2 and
Autograd 1.9.1. SDK-free has none of these SDKs/frameworks. Independent JAX and
TF environments have only their respective framework and no quantum SDKs.

Main and matrix JSON totals AND every per-file record are identical:
28781/31703 lines = **90.7832066365959%**, missing 2922, excluded 68. This is
above 90.66067992302759%, not a functional parity percentage. New/expanded
core modules: parameters 475/515 (92.2330%), limits 56/56 (100%), symbolic
interface guards 75/81 (92.5926%). No exclusions were added.

Independent 70-digit Decimal Taylor/exp oracle checks f, two first derivatives
and three Hessian components at three points; final receipt
`/tmp/qb-stage12b-p3-r4-high-precision` exits 0, maximum absolute error
1.3322676295501878e-15. This is separate from public SDK comparisons.
Additional alternate focus: 214 passed, exit 0.

Known limitations are NOT converted to successes:

- Finance, Optimization, Machine Learning, Dynamics, Metal, Experiments and
  Addons are NOT_EXECUTED as installed-environment subsets. Inventory records,
  SDK-free fallback tests and original advisory policy do not prove them.
- Main/alternate pip checks each exit 1 for exactly the two pre-existing
  WeasyPrint 68.1/tinycss2 1.4.0 and pyquafu 0.4.5/NumPy 2.4.6 conflicts.
  SDK-free/JAX/TF pip checks exit 0. No dependency environment was changed.
- Whole dirty checkout legal test freshly has 1 failed / 3 passed, exit 1:
  user-owned `quantumbridge/router/core.py` lacks a source ledger entry.
  Receipt `/tmp/qb-stage12b-p3-worktree-legal-final` is separate from controlled
  legal 4 passed. That Router is not staged, reverted or given fake attribution.
- Frozen Git path no-vendor scan has zero output and rg exit 1 (NO MATCHES),
  not a failed test. No site-packages/wheel/dist-info/egg-info/venv paths added.
- Existing xfails remain disclosed. Neither skips nor xfails imply parity.

SHA256 of temporary reproducibility tools (not production SDK dependencies):

| Tool | SHA256 |
| --- | --- |
| Independent high-precision oracle | 06519623b8717b59daba82adb1aca6fa37a658c199d1ca3f6baa9190ffbbfe92 |
| P3 final driver | 055cdbdfcf0d0689509094d2247564ccb4cbd5f531e74a9b114019d83e99b9a9 |
| Reused original 26-gate driver | fcca7ca309345912e06a30094ddc7bbb02b0e59cd74130f89edcb3990dbb66f6 |
| Receipt/coverage/public audit | 1ed1f2b2e53810d25afe56b276ea6108a0df45cc3078cc920a4975be65a7a46b |
| Independent-exit command runner | e04371807ab7d2745e65a5cef1626ea7dd5dca1c01adf44389850b94f9f3fb3c |

Publication remains `local_commits_ready=true` only after scoped commit;
`remote_pushed=false`, `remote_ci_verified=false`. Cached origin/main is not
live remote state; no denied authorization is retried or TLS/auth bypassed.

## Remaining Scope

Complete ParameterExpression public ABI parity is NO: native constructor and
return protocols differ, full assumption/branch/error/simplification behavior
is not proven, optional SymPy cannot preserve UUIDs, real sign/nonsmooth
contracts are explicit subsets, and QPY/QASM versions/functions/replay variants
remain incomplete. Symbolic coherent control before binding remains an
existing unsupported path; controlled *bound* phase matrices are tested.
Forged scalar/vector parameters sharing displayed name and UUID remain distinct
kinds; ambiguous mixed-kind QPY imports reject instead of merging identities.
Complete Qiskit/PennyLane replacement is NO / ACTIVE / INCOMPLETE. Gate/to_gate/
decompose/repeat and wider Circuit/classical builders, quantum information,
Primitives V2/provider jobs, full compiler/target/scheduling, remaining Aer,
QNode/devices/plugins, templates/transforms/qchem/interfaces and industry
ecosystems remain separate required work. No Studio work, cloud/hardware,
credential use, production certification or remote CI completion is claimed.

Next action after scoped commit is one result report to the authorized ChatGPT
conversation and a request for the next actual native-core implementation
prompt. P4 Circuit/Gate remaining API is a candidate, not an implemented result.
