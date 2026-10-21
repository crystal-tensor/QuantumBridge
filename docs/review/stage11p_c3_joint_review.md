# Stage 11P-C3 Bounded Joint Review

Date: 2026-10-21. Overall C3 status: PARTIAL, not COMPLETE.
Full independent Qiskit/PennyLane replacement: ACTIVE / INCOMPLETE.

## Basis And Checkpoint

This is a finite classification of current source and recorded execution
evidence, with report-based feedback from the owner's designated ChatGPT
conversation. It is not an independent external source audit or whole-SDK
acceptance. The review ends without requiring an unbounded allocator project.

- R1 local baseline: 89bd0f161dea5b653d2b61137265de4bb6ca4ce6.
- R2 local code checkpoint: b1d345b3731276f5f2721cb42c2397d98981ac5c.
- R2 tested source tree: 85b2c716a8bb24fdf4a79de969ec5eb295ce1e09.
- Exactly 23 R2 paths were staged, checked and committed normally. Committed
  production/tests/examples match the tested tree (Git diff exit 0).
- User Studio/Router changes remain outside the checkpoint. No push, history
  rewrite, tag/release, vendoring, token/auth/TLS or cloud/hardware work occurred.
- New-SHA remote CI: NOT_VERIFIED. Local ahead counts use cached origin/main,
  not a fresh remote ancestry proof. Prior workflow OAuth refusal was not retried.
- Git used its existing automatically configured local identity and emitted a
  warning. No identity configuration or amend was performed.

Fresh v2 receipts, not old candidate passes, establish this checkpoint:

| Gate | Actual result |
| --- | --- |
| SDK-free FULL | 2399 passed / 420 skipped; exit 0 |
| Main FULL with coverage | 3042 passed / 5 skipped / 3 existing public-oracle xfailed; exit 0 |
| Alternate FULL | 3040 passed / 5 skipped / 5 existing public-oracle xfailed; exit 0 |
| Independent JAX 0.12 | 844 passed / 168 optional-framework skips; exit 0 |
| Independent TF 2.21 | 866 passed / 151 optional-framework skips; exit 0 |
| Torch/Autograd focus | 46 passed / 984 unrelated deselected; exit 0 |
| Actual 28-section matrix | All headers reached, final shell exit 0; seven absent-dependency subsets NOT_EXECUTED |
| Independent main and matrix full coverage | Both 27456/30388 = 90.35145452152166%; missing 2932, excluded 68 |
| Compile / legal / privacy-security | Exit 0 / 4 passed / 49 passed with one existing bridge warning |
| Five environment origins | All import the final private export; versions recorded |
| pip check | SDK-free/JAX/TF exit 0; main/alternate retain known conflicts, exit 1 |

Main/alternate are mixed user/system-package environments, not hermetic clean
stacks. Existing pyquafu NumPy<2 versus NumPy 2.4.6 and WeasyPrint/tinycss2
conflicts remain unresolved. Full raw logs/exits, durations, environment origins,
matrix section results, v1 invalidation and corrected red/green chronology are
in the [R2 Tableau report](../implementation/stage11p_c3_r2_tableau_progress.md).
All needed test and matrix processes finished before the local code commit.
Line coverage is not a fraction of SDK functions implemented.

An additional post-review legal check against the entire dirty working folder
(`qb-stage11pc3r2-post-review-legal`, exit 1; 1 failed / 3 passed) finds the
pre-existing untracked `quantumbridge/router/core.py` missing from its source
ledger. That file was outside the R2 export/checkpoint and was not modified or
audited here. The committed R2 ledger already lacks that path; the review's
status-only edits did not remove it. This workspace-wide failure is disclosed,
not hidden by changing the test or declaring unreviewed Router attribution.
Scoped R2 legal results above do not certify the user's separate Router files.
The later documentation-only review snapshot e199f7bbb95b7193ac43469742d8ff8de2e12edf
preserves exactly b1d345b production/tests/examples (diff exit 0) and excludes
the same user files. Its scoped legal recheck
`qb-stage11pc3-post-review-scoped-legal.log/.exit` passes all four tests, exit 0.
This does not turn the separately disclosed workspace Router failure green.

## Classification

Verified Native applies only to the explicitly tested contract, not an entire
class, module, device family or arbitrary workload. A class with verified
subcontracts may still be Partial Native overall.

| Scope | Classification | Evidence And Boundary |
| --- | --- | --- |
| Native derivative requests and cumulative work/shots | Verified Native, bounded | Actual Device work, limits, partial-shot failure and recovery; not all plugin protocols |
| Torch/Autograd supported graphs and copies | Verified Native, bounded | Real first/second derivatives, retained graph snapshots and last-root release; opaque foreign graph allocation is not covered |
| JAX/TF explicit CPU query/status and persistent snapshots | Verified Native, bounded | Actual JIT/graph callbacks and runtime failure status; not quantum XLA/GPU or general whole-graph budgeting |
| State/density Pauli labels, reset, scoped samples and copies | Verified Native, bounded | Complex mathematics, measurement phase, quotas, completed samples and escaped views; complete state API remains Partial Native |
| Operator and six channel representations | Partial Native overall | Verified native scoped algebra, stable phase comparison and shared-memo independent deep copies; complete dimensions/conversion/API contracts remain open |
| Clifford/Tableau and stabilizer execution | Verified Native for tested subset | Signed Pauli conjugation, compose/front/qargs, adjoint, GF(2), synthesis and real 100-qubit non-dense execution; not full SDK API/performance parity |
| Direct Device density return storage | Verified Native, bounded | Pure and actual mid-circuit ensemble outputs retain real roots and reject quotas before output work; not complete Device allocation closure |
| MPS | Partial Native overall | Verified supported local tensors/snapshots and 100-wire low-entanglement no-dense cases; arbitrary entanglement efficiency and every internal allocation are not established |
| Result/Snapshot | Partial Native overall | Verified existing native state/density/MPS defensive-copy contracts; arbitrary metadata, foreign object graphs and complete SDK schemas are not established |
| Ordinary JAX/TF unified whole-graph limits | Unsupported | Explicit existing boundary; per-query success does not establish cross-callback graph accounting |
| GPU/XLA/portable graph/plugin/full SDK contracts | Unsupported or Unverified by specific interface | Do not infer support from CPU host callbacks or optional imports |
| Real Quafu/QOS/IBM hardware and new-SHA remote CI | Unverified | Offline tests and local commits are not authenticated cloud execution or remote CI evidence |
| Universal Python/BLAS/LAPACK/framework allocator RSS ceiling | Unverified; no such guarantee | Explicit ndarray admission is not measured process RSS or all hidden workspace |

The 100-qubit tableau case is actual native CPU execution, not physical-cloud
proof. Likewise, fixed-geometry H2 derivatives are not differentiable SCF or a
complete chemistry platform. Inventory/passthrough/schema adapters are not
classified as native function implementation.

## Residual Ownership And Verification Conditions

These are bounded follow-ups, not authorization to expand allocator work
indefinitely before functional development.

| Residual | Follow-Up Scope | Condition For Closing The Stated Gap |
| --- | --- | --- |
| Known native state expectation and density purity intermediates | quantumbridge.information | Audit the actual working arrays when implementing the bounded function; add mathematical and before-factory quota/lifetime evidence |
| Old dense aggregate overlap | execution/diff ownership | Identify each replaceable role and test double-charge removal; preserve protection for unproven workspace, never subtract arbitrary bytes |
| General MPS/native metadata scratch | devices/execution | Explicit per-path contract and actual allocation/release failures; do not generalize one 100-wire example |
| Ordinary JAX/TF graph-wide ownership | interfaces/diff | Trace-safe real graph/callback lifecycle and shared-budget tests; remain Unsupported until implemented |
| Foreign callback and hidden numerical workspace | interface/plugin contracts | Observable validated admission or explicit unsupported/unavailable status; do not invent RSS measurements |
| Full state/API behavior | Stage 12-A quantum information | Real public signature/behavior gap, native red/fix, independent math, optional public differential and composed-call/error/resource tests |
| Cloud and publication | owner-authorized integration lane | Separate genuine authenticated hardware and exact-SHA remote CI receipts; no authorization or TLS bypass |

Concrete known native examples remain in Statevector.expectation_value and
DensityMatrix.expectation_value/purity. They are not relabeled as unknown
external work merely to claim C3 closure. The legacy eight-state dense allowance
remains because its overlapping roles are not individually proven replaceable.

## Decision And Next Functional Work

The finite joint classification review is complete; C3 remains PARTIAL. The
bounded R2 local checkpoint is valid within its disclosed test/environment
limits. This does not complete the highest full functional replacement goal.

Primary development now moves to Stage 12-A actual state APIs, not new allocator
subprojects. Read-only public Qiskit 2.4.1 probes already show:

- from_int(1, (2,4)) loses explicit dimensions natively; (3,2) is rejected.
- Both native state classes lack object seed and add/subtract. DensityMatrix
  also lacks scalar arithmetic; Statevector lacks its public purity method.
- Probability/sample containers and DensityMatrix.dim differ from public APIs.
  Native wire/bit ordering and existing caller contracts must not be silently
  broken. Recheck public Qiskit 2.6 and choose explicit compatibility boundaries.
- Tensor/expand/evolve already exist; verify and extend real missing behaviors,
  not duplicate working functions. Neither public state class has variance();
  absence of that name is not a genuine missing public method.

Order: P0 composite dimensions and their propagation; P1 RNG/seed; P2 arithmetic;
P3 purity and probability containers. SDK-free native mathematics must perform
the work. An upstream SDK passthrough, schema-only wrapper, mock or silent
fallback is not an implementation. Each new functional batch needs fresh tests
on its own source; the R2 receipts do not accept Stage 12 changes. Studio and
Capture remain outside the current batch.
