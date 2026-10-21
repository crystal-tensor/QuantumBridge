# C3-R2 Operator And Channel Progress

Date: 2026-10-21. Status: PARTIAL R2, not final C3 acceptance.
Local HEAD remains `89bd0f161dea5b653d2b61137265de4bb6ca4ce6`.
Full independent Qiskit/PennyLane replacement remains ACTIVE / INCOMPLETE.
The owner-authorized ChatGPT conversation received the actual P0/Result partial
report and returned the completed bounded P1/P2 continuation now in the spec.
This collaboration is based on reported evidence, not an independent audit.

## Actual Changes

- Native Operator reflected addition/subtraction and matrix multiplication now
  implement supported equal-shape numeric matrix operations. Scalar multiply/
  divide and forward matrix addition/subtraction reuse one admitted ufunc
  destination. NumPy matrix-left expressions defer to the native reflected
  method; this is not complete arbitrary NumPy ufunc dispatch.
- Standard I/X/Y/Z labels (including existing lowercase acceptance and empty
  zero-qubit identity) fill one admitted dense Pauli permutation/phase matrix.
  Invalid labels reject before allocation. No SDK source/engine is used.
- Qubit reversal fills a copied destination without allocating a dense
  permutation or intermediate matrix products. Operator copy/conjugate/adjoint
  and matrix export retain real destination ownership, including a source's
  existing account outside an active scope.
- Operator.equiv uses a largest-component phase pivot and scalar comparisons,
  not full abs/argwhere/phase-multiplied matrices. Scaled scalar comparisons
  avoid overflow and preserve the existing 1e-5 relative / caller absolute
  tolerance. Nonfinite matrices are not phase equivalent. A tiny first entry
  perturbed within absolute tolerance no longer determines an unstable phase.
- Operator and all six Channel deepcopy hooks use the existing audited native
  field copier, not constructors or foreign deepcopy/reduce hooks. The caller's
  memo is shared, preserving repeated objects, array aliases and standard versus
  generalized channel sides. All known group layouts validate and admit before
  the first copy under a scope. Each new root retains an independent lease.
  Without a scope, arrays follow actual source accounts if present; unknown
  foreign object fields reject before custom copying.

The persistent configuration copier still requires an explicit account for its
public strict mode. Its existing audited traversal is reused by native object
copy hooks; this is not a new simulator, object hierarchy or budget manager.
Hidden Python/NumPy iterator/BLAS workspace is not a strict RSS guarantee.

## Actual Red/Green Receipts

Each prefix has complete `.log` and independent `.exit` files in `/tmp`.

| Prefix | Terminal result |
| --- | --- |
| qb-stage11pc3r2-operator-copy-initial-red | 26 failed / 2 passed, including three real tiny-pivot nontrivial-phase counterexamples, nonfinite equivalence, ndarray deepcopy dispatch, real root/memo/lifetime and foreign-protocol gaps |
| qb-stage11pc3r2-operator-copy-first-fix | 113 passed with native information/configuration/persistent-copy/ownership regressions |
| qb-stage11pc3r2-operator-algebra-initial-red | 22 failed / 34 passed: labels/reversal/arithmetic output admission, reflected matrix APIs and retained roots |
| qb-stage11pc3r2-operator-algebra-first-fix | 333 passed, including state/Result and existing channel evolution checks |
| qb-stage11pc3r2-operator-algebra-expanded | 348 passed after shared caller memo/group preflight/invalid-label/strided-copy/extreme-scale scenarios |

The new Operator/Channel test file has 71 cases, including three optional public
Qiskit global-phase oracles. Existing tensor/expand/power are regression-tested,
not falsely reported as new red fixes. Independent Pauli matrices/tensor order,
complex arithmetic, generalized map semantics and view lifetimes are tested.

## Validation And Remaining Scope

The first P1 frozen tree `4f35db7b1cf1ab6c15af46a8f6d53029ee6e5462` exposed a
real broader regression: independent JAX focus had 1 failed / 778 passed /
164 skipped (36.48s), exit 1. The new group admission had unintentionally
changed the existing persistent-pool partial-copy failure contract: its error
still owns an already copied 64-byte root until the traceback dies. The test
was not weakened. Whole-group preflight was scoped to native object copy hooks
only; the persistent copier retains its existing per-copy admission/lifetime.

The recovered frozen tree `1518430ddf94bc9f2b9791a30195f99b0e6aeeb1` is exported
at `/tmp/qb-stage11pc3r2-operator-recovery.3pgMXV/source` using a separate Git
index, excluding user dirt. Production and all three new test files match the
working files. Updated documentation receipts can differ from that export.

| Prefix | Recovered frozen P1 result |
| --- | --- |
| qb-stage11pc3r2-operator-independent-jax-recovery | 779 passed / 164 skipped, 36.11s, exit 0 |
| qb-stage11pc3r2-operator-independent-tf | 801 passed / 147 skipped, 48.96s, exit 0 |
| qb-stage11pc3r2-operator-main-framework-focus | 960 passed / 1 skipped, 113.48s, exit 0 |
| qb-stage11pc3r2-operator-alternate-focus | 290 passed, 6.48s, exit 0 |
| qb-stage11pc3r2-operator-sdkfree-focus | 274 passed / 16 skipped, 1.11s, exit 0 |
| qb-stage11pc3r2-operator-compile | compileall, exit 0 |
| qb-stage11pc3r2-operator-legal | 5 passed, 0.12s, exit 0 |
| qb-stage11pc3r2-operator-privacy | 52 passed / 1 existing optional-adapter warning, 2.21s, exit 0 |

Both independent environments run tests/derivative_execution and
tests/interfaces, without Qiskit/PennyLane installed. Missing frameworks and
14 public quantum-SDK oracle scenarios are explicitly skipped, not executed.
The main focus runs the same derivative/interface directories, including
Torch/Autograd and installed JAX/TF. Alternate/SDK-free focus runs the three new
test files plus information/providers/schema and persistent storage/protocol
tests. SDK-free skips 14 SDK oracle cases and 2 TensorFlow scenarios. None of
these focused scopes is advertised as a newer FULL run. The earlier P0/Result
FULL results (SDK-free 2266 passed;
main 2902 passed) apply to their earlier frozen source tree, NOT these newer
Operator/Channel changes. No fresh P1/R2 full coverage, three-environment final
FULL or full matrix is claimed yet. Baseline remains 90.17352569642976% with
68 exclusions, not a function coverage percentage.

Fresh environment metadata and pip receipts use prefixes
qb-stage11pc3r2-operator-versions-{main,alternate,sdkfree,jax,tf} and matching
pip prefixes. Every version/origin helper exits 0 and resolves QuantumBridge
from the recovered frozen source. All use Python 3.12.6.

| Environment | Public runtime versions | pip check |
| --- | --- | --- |
| main | NumPy 2.4.6, Qiskit 2.4.1, Aer 0.17.2, PennyLane 0.44.1, JAX 0.7.1, TF 2.21.0, Torch 2.12.0, Autograd 1.8.0 | exit 1, existing two conflicts |
| alternate | NumPy 2.4.6, Qiskit 2.6.0, Aer 0.17.2, PennyLane 0.42.3, JAX 0.6.2, TF 2.21.0, Torch 2.12.0, Autograd 1.9.1 | exit 1, same conflicts |
| SDK-free | NumPy 2.5.4; no Qiskit/Aer/PennyLane or four AD frameworks | exit 0 |
| independent JAX | NumPy 2.5.4, JAX 0.12.0; no quantum SDKs/other AD frameworks | exit 0 |
| independent TF | NumPy 2.5.4, TF 2.21.0; no quantum SDKs/other AD frameworks | exit 0 |

Main/alternate import some installed oracle/framework packages from user/system
site-packages; they are not all-in-one isolated clean dependency stacks.
Unchanged conflicts are pyquafu 0.4.5 requiring NumPy <2 versus 2.4.6 and
WeasyPrint 68.1 requiring tinycss2 >=1.5 versus 1.4. Dependencies were not
changed to hide these failures. Scoped key/private-key filename-only scanning
has no matches (rg exit 1 means no matches), diff-check exits 0, and no vendor
directories/artifacts were added in the owned batch. Nothing reads a token.

P2 bool-tableau/generator/compose/inverse/synthesis and 100-qubit continued
non-dense execution versus guarded dense expansion remain required. Supported
Pauli/Clifford conversion paths need the joint P2 evidence. Old dense aggregate
allowance is still retained; no unsupported removal occurred. General Operator
dimensions, non-Pauli label families, all public signatures/operations and
complete SDK APIs remain open.

Only batch-owned files are used for validation. User Studio/Router changes
remain untouched. No subagents, vendor, tag/release, cloud/hardware/token or
auth/TLS changes. No new commit/push or new-SHA remote CI is claimed before the
complete R2 gates. Continue P2 and the bounded allowance audit, then final R2
gates and joint C3 review before Stage 12 actual missing core functions.

The recovered P1 results were subsequently sent to the owner-designated
"Claude code disclosure and response" ChatGPT conversation. Its completed
reply confirmed the finite P2-A/B/C/D scope, real Clifford.adjoint signature,
10 mathematical plus 8 resource scenarios and final R2 gates. That operational
prompt is recorded in the R2 execution spec. No P2 implementation or final
R2/C3 approval is claimed by that reply.
