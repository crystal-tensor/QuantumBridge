# Stage 11P-C3-R2 Execution Spec

Status: IN PROGRESS. Recorded after the completed, authorized ChatGPT reply
in "Claude code disclosure and response", 2026-10-21. This is a faithful
operational transcription, not an independent source audit or acceptance.
The full original reply is in the owner's authorized conversation:
https://chatgpt.com/c/6a20d458-a76c-83ea-9b49-f8f0caedb3cf

## Baseline And Objective

- Preserve local checkpoint `89bd0f161dea5b653d2b61137265de4bb6ca4ce6` and history.
- Full native Qiskit/PennyLane functional replacement remains ACTIVE/INCOMPLETE.
- R1/C3 stays PARTIAL where known uncontrolled native paths remain.
- Limit this batch to existing native quantum information objects. Do not
  create a second simulator or object hierarchy. No Capture or Studio.
- This is the last high-priority core-object resource batch before joint C3
  review and a return to genuinely missing core function implementation.
  Do not expand this into ownership of every Python allocator operation.

## P0: Statevector And DensityMatrix

First persist actual allocation-before-admission reds for Statevector copy,
tensor, probability/sampling buffers, measure and reset; DensityMatrix copy,
from_statevector and sampling/measurement buffers. Verify actual repository
method names first: report absent APIs, not fabricated executed calls.

Reuse ResourceScope and ArrayOwnership. Compute shape/dtype/bytes before
allocation. Real copies own independent leases; views do not double-charge.
Preserve collapse, normalization and wire order. Failed sampling retains
confirmed completed shots. No implicit dense fallback bypasses admission.

## P1: Operator And QuantumChannel

Audit actual reds for Operator.from_label, tensor/expand/power and reversed
multiplication, arithmetic/equiv, Operator.__deepcopy__,
_QuantumChannel.__deepcopy__, and supported Pauli/Clifford matrix paths.
Do not invent a red for methods already controlled by Task 3E.

Admit matrix outputs, products, tensor intermediates and validation arrays
before factories. Equiv preserves global phase. Cover complex dtype, strided
arrays and large inputs. Reject foreign custom copy protocols before dispatch.
Preserve existing operator/channel mathematics.

## P2: Clifford And Tableau

Audit bool tableau arrays, stabilizer synthesis, tableau-to-statevector,
Clifford compose/inverse and large expansion. A 100-qubit tableau request for
the full statevector must reject before exponential allocation. Large native
Clifford/tableau simulation itself must still execute; do not disable it just
to avoid expansion. Unknown Python/LAPACK workspace stays unavailable.

## P3: Result Copies And Old Allowance

Control Result.statevector() and Result.density_matrix() defensive copies.
Reserve before allocation; returned buffers retain leases through their last
owners; repeated access neither loses nor double-charges real storage;
Result/Job destruction does not invalidate escaped user arrays.

Retire only proven replaced components of the old dense-device aggregate
allowance. Keep unproven external workspace in a separate conservative budget.
Do not remove the whole old guard and leave a protection gap.

## Required Evidence

At least 25 independent state/density scenarios, 20 Operator/Channel scenarios,
10 Clifford/tableau scenarios and 10 Result/failure-recovery scenarios.
Include actual valid-overbudget-valid recovery and factory spies proving no
allocation before rejection. Independent mathematical oracles cover norm,
density PSD/trace, global phase, tensor order, tableau, measurement probability
and CPTP semantics. Optional public Qiskit/PennyLane APIs are differential
oracles only, never native execution engines.

## Final Gates

Freeze final sources, then run compileall, FULL pytest, FULL coverage and the
real complete 28-section local matrix, with independent shell exit receipts.
Also run SDK-free/main/alternate FULL, independent JAX/TF, Torch/Autograd focus,
100-qubit MPS no-dense, native H2 second derivatives, legal/privacy/no-vendor/
no-token, pip check, diff-check and tested-source/commit equality.

Exact coverage baseline: 90.17352569642976%; exclusions must not increase from
68. Coverage is not API function completion. Missing optional dependencies,
known pip conflicts and unexecuted subsets remain explicit.

## Git And Delivery

Stage only batch-owned files for an ordinary local checkpoint after gates.
Preserve user Studio/Router changes. No history rewrite, force/reset/rebase/
amend, tags, releases or vendoring. No push until the owner restores workflow
authorization; no auth/TLS changes, token reads, cloud or real hardware calls.

Report actual native API results, each red/fix, prior admission and retained
bytes versus unknown workspace, mathematical regressions, differential
behavior, Result lifetime, 100-qubit expansion rejection, all full/framework
gates, exact coverage/matrix exit, local SHA, real push/CI status, remaining C3
resource gaps and the genuinely missing core APIs. Do not relax tests or
budgets to declare completion while known native allocation gaps remain.

After this bounded batch, request joint C3 review with explicit allocator/RSS
limits, then prioritize Stage 12 Core Function Parity Closure using the core
parity ledger. The highest goal remains real native function behavior and
mathematical correctness, not increasing coverage alone. Studio stays last.

## Completed Follow-Up: P1/P2 Continuation

The completed authorized ChatGPT reply after the P0/Result partial report
confirmed the same bounded scope, not R2/C3 final acceptance or source audit.
Its operational requirements are recorded here without overriding the owner.

1. Wait for the current main FULL terminal result and record failures, skips,
   warnings and actual exit. A focused run is not FULL. Then continue P1
   without requesting another authorization.
2. P1: standard Pauli/identity labels, wire/tensor order and invalid inputs;
   reverse arithmetic radd/rsub/rmul and supported matrix combinations; phase
   equivalence without false positive/negative results; Operator and Channel
   deepcopy with the caller's shared memo, independent roots and lifetimes.
   Establish real phase-equivalence and deepcopy-before-admission reds first.
   Complex128/strides/zero-qubit identity/numerical boundaries and actual
   valid-overbudget-valid recovery are required. Already controlled
   tensor/expand/power receive regression tests, not duplicate implementations.
3. P2: bool storage, compose/inverse, generator updates, supported synthesis
   intermediate arrays and dense expansion preflight. A 100-qubit tableau
   must keep executing supported non-dense stabilizer operations while its
   full statevector request rejects before exponential arrays. Test Clifford
   identities, phase, Pauli conjugation, measurement and small-state oracles.
4. Old allowance: remove only proven duplicate charges. Preserve existing
   protection for unproven workspaces; distinguish owned/reserved/observed/
   unavailable and do not claim strict process RSS.
5. Run the full final frozen R2 gates listed above, preserve complete logs,
   environment versions and real exits; mark unavailable optional lanes
   NOT_EXECUTED. The exact coverage/exclusion baseline is unchanged.
6. Only after the complete local gates, stage accumulated R2-owned files for
   an ordinary local commit. Preserve user files/history and authorization
   restrictions. Report actual new APIs, math/public differential results,
   lifetime/100-qubit/allowance evidence, all gates, commit and remote status,
   and still-missing core APIs. Then request joint C3 review and move to actual
   Stage 12 core function closure instead of unbounded allocator expansion.

Main FULL subsequently completed exit 0 for the P0/Result snapshot; its exact
receipt is in that partial report. Newer P1 sources require their own evidence.

## Completed Follow-Up: P2 Functional And Allocation Closure

After receiving the actual recovered P1 results, the authorized conversation
returned this bounded next segment. It accepts continued P2 work based on the
reported evidence only, not final R2/C3 acceptance or an independent audit.
Committed HEAD remains 89bd0f1; the latest P1 tested tree is
1518430ddf94bc9f2b9791a30195f99b0e6aeeb1. Preserve P0/P1 and user changes.

- Audit real repository signatures first. Use Clifford.adjoint for the inverse;
  do not invent Clifford.inverse or attach a nonexistent statevector method to
  the wrong class. Reuse existing Clifford/Stabilizer objects and backends.
- P2-A: reproduce actual bool-tableau copies or intermediate factories before
  low-budget rejection. Audit stabilizer/destabilizer storage, phase bits, row
  operations, measurement updates and generator conversion. Admit shape/bytes
  first; views reuse roots, genuine copies own independent leases. Existing
  Result-held tableau storage, where actually present, retains its last-owner
  lifetime. Failed temporary buffers release.
- P2-B: actual compose qargs/front/order/phase, adjoint as a genuine inverse,
  Pauli conjugation C P C-dagger, generator anticommutation/symplectic structure,
  and existing executable synthesis/decomposition with operand mapping. Work
  on the tableau itself, not a dense-state fallback. Probability-only tests
  cannot establish signed Pauli correctness: also compare symplectic matrices,
  phase bits and small complete complex matrices.
- P2-C: execute supported 100-qubit compose/adjoint/measurement/generator
  operations while full dense expansion rejects before an exponential array
  factory. Existing already-correct preflight is a regression, not a fabricated
  red. Allocation spies and independent 1-5 qubit dense mathematical oracles
  must demonstrate the boundary; do not disable large-tableau simulation.
- P2-D: identify old dense aggregate components already covered by real array
  admission. Remove a duplicate only with an explicit double-charge test.
  Preserve protection for unproven BLAS/LAPACK/synthesis workspace or identify
  it as unavailable. Distinguish owned/reserved/observed/unavailable; no strict
  process RSS claim or blanket deletion of the old dense guard.
- Add at least 10 independent tableau/Clifford mathematical scenarios and 8
  resource/lifetime scenarios: wrong composition order, inverse phase, lost
  signed Pauli, invalid qargs, nonsymplectic data, incorrect generator pairing,
  pre-budget bool factory, last surviving view, a later operation exceeding
  budget, 100-qubit expansion and valid-overbudget-valid recovery. Preserve
  optional public Qiskit 2.4.1/2.6 black-box tests; no source/test ports.
- After P2 and the bounded allowance audit, freeze final R2 code and perform
  all original full gates, including true coverage and complete 28-section
  matrix with real exits. Old FULL or current P1 focus is not final P2 proof.
  No added exclusions beyond the original 68; exact historical coverage
  baseline remains 90.17352569642976%.
- Only after those gates, stage R2-owned files and create an ordinary local
  commit. Preserve history/user Studio/Router; no token/auth/TLS/cloud/hardware,
  push without restored workflow authorization, vendor, force/reset/rebase/
  amend, tag/release. Report all actual APIs, red/green, lifetimes, mathematics,
  100-qubit result, allowance rationale, full gates, commit, real remote status
  and remaining function gaps. Keep R2/C3 PARTIAL for known uncontrolled paths
  without expanding this batch indefinitely. Then joint C3 review and actual
  Stage 12 core-function closure; Studio stays last.

P2 is the next implementation segment, not completed by the P1 focused gates.

## Completed Follow-Up: Final Gates And Stage 12 Preparation

The P2 report and frozen candidate 6cc46f8d1cb9ee3a4b537fd3458ea045413d9597
were sent to the authorized conversation. Its completed reply requires the
following finite continuation, based on reported evidence, not a source audit:

1. Await the actual live main FULL coverage terminal receipt; fix real failures
   and refreeze if necessary. Complete all same-tree SDK-free/main/alternate
   FULL, independent JAX/TF, Torch/Autograd focus, true full coverage, complete
   28-section matrix, compile/legal/privacy/security/no-token/no-vendor, pip and
   five-environment import-origin gates. Keep raw logs/exits and production/
   tests/examples equality. Preserve the exact coverage/exclusion baseline;
   mark unavailable optional lanes NOT_EXECUTED and disclose existing conflicts.
2. Only after final gates pass, stage R2-owned files for an ordinary local
   checkpoint, preserving user files/history. Compare committed code/tests/
   examples to the tested source. No push before restored workflow OAuth and
   fresh fast-forward verification; no credential/TLS changes, token reads,
   cloud/hardware, force/reset/rebase/amend, tag/release or vendor.
3. Jointly review C3/R1/R2 using Verified native, Partial native, Unsupported,
   and Unverified classifications. Include actual device derivatives, MPS,
   JAX/TF, state/density/operator/channel/Clifford, Result/Snapshot and ledger
   evidence. Retain known native resource gaps and external allocator/RSS
   limits; C3 remains PARTIAL if its full criteria are not met.
4. After joint review, prepare bounded Stage 12 genuine API gaps from current
   source signatures and public behavior, prioritizing state RNG/dimensions/
   arithmetic/observables/general maps, then Operator/Channel, Circuit,
   PennyLane Tape/QNode/transforms and devices/compiler. Verify rather than
   infer missing functions by names. Each real gap requires native red/fix,
   mathematical oracle and optional public differential tests. Upstream SDK
   execution, passthrough, mocks/skips or file/test/coverage counts are not
   completion. Deliver the first bounded function plan without Capture/Studio.
5. Report all exact gates, mathematics, local SHA/real remote status, C3
   complete/incomplete classifications and Stage 12 priorities. R2 quality
   gates do not imply full C3 acceptance or complete SDK replacement. Stop
   expanding allocator work indefinitely and return to actual core functions.

## Completed Follow-Up: Empty-Complex Recovery And V2 Gates

The genuine managed empty-complex regression, interrupted v1 FULL, eight red
cases, minimal dtype correction, 393 passing focused cases and corrected tree
`85b2c716a8bb24fdf4a79de969ec5eb295ce1e09` were sent to the owner's designated
conversation. Its completed reply was fully read. It confirms the correction
based on the report only, not independent source review, and requires:

1. Finish this same v2 tree's SDK-free FULL, main FULL with explicit coverage,
   alternate FULL, independent JAX 0.12/TF 2.21, Torch/Autograd, the actual full
   28-section matrix with shell exit, compile/legal/privacy/security/no-token/
   no-vendor, five environment versions/import origins/pip and production/test/
   example equality. Keep exact baseline 90.17352569642976% and 68 exclusions.
   Disclose all failures/skips/xfails/unavailable dependencies and pip conflicts.
   Real regressions require saved red, minimal correction, new freeze and
   required gates; never reuse another candidate's pass as final evidence.
2. Only after all required gates, stage the cumulative scoped R2 files, compare
   the tested source, and make an ordinary local commit with actual SHA. Keep
   user Studio/Router changes. No amend/reset/rebase/force, unauthorized push,
   OAuth/auth/TLS changes, tokens, cloud/hardware, tags/releases or vendoring.
   New-SHA remote CI remains NOT_VERIFIED without actual evidence.
3. Perform one finite C3/R1/R2 joint review covering Device, state/density,
   Operator/Channel, Clifford/Tableau, MPS, Result, JAX/TF and derivatives.
   Classify Verified Native / Partial Native / Unsupported / Unverified.
   Known native allocation gaps remain PARTIAL; unknown Python/BLAS/LAPACK
   workspace is not a strict RSS bound. Review does not automatically close C3.
4. Then shift primary development to bounded Stage 12 Statevector/DensityMatrix
   actual functionality: reproducible RNG/seed, dimensions/subsystem qargs,
   arithmetic/tensor/expand, expectation/variance, general operator/channel
   evolve, and measure/reset/sample input/output/error boundaries. Inspect real
   signatures and public behavior first, record per-function Supported / Partial
   / Missing / Unsupported / Unverified, require genuine red/native fix/math
   and optional black-box public differential tests. No SDK passthrough/wrapper/
   mock execution, repeated implementation of already-correct APIs or entire-SDK
   single batch. Deliver callable functions and correct numerical/API behavior,
   not only inventory, scaffolds or increased line coverage.
5. Report the actual final test tree, counts/coverage/matrix exit/local SHA,
   joint review gaps and first real Stage 12 functions. If gates are unfinished,
   report intermediate progress only. Do not open more C3 allocator subprojects.
   Full independent native Qiskit/PennyLane replacement stays ACTIVE/INCOMPLETE.

## Completed Follow-Up: V2 Full Results And Stage 12-A Order

After the v2 SDK-free/main/alternate FULL, coverage, framework, short-gate and
environment results were sent, the owner's designated conversation completed
another reply. It is report-based, not an independent source audit. It requires:

1. Wait for the already-running real 28-section matrix to terminate naturally;
   do not restart duplicates. Keep every header, section result and actual shell
   exit. Export its full coverage JSON and compare with main FULL 27456/30388.
   Recheck production/tests/examples against v2 tree
   85b2c716a8bb24fdf4a79de969ec5eb295ce1e09. Real failures require preserved red,
   minimal correction, refreeze and fresh necessary gates, not borrowed passes.
2. After all required same-tree gates, stage only R2 files, preserve user Studio/
   Router dirt, compare staged sources/tests/examples, make a normal local commit
   and report its actual SHA. Recheck after commit. No amend/reset/rebase/force,
   tag/release/vendor, token reads, OAuth/TLS changes or cloud/hardware. Without
   owner-restored authorization and fresh fast-forward proof, do not push. New
   SHA remote CI stays NOT_VERIFIED.
3. Perform a finite C3/R1/R2 joint classification review: Verified Native,
   Partial Native, Unsupported, Unverified. Cover Device derivatives, MPS,
   state/density, Operator/Channel, Clifford/Tableau, Result/Snapshot and the
   four framework interfaces. Preserve dense aggregate/external allocator/
   Python heap/framework graph boundaries. Line coverage is not API parity.
   Joint review may finish without forcing C3 COMPLETE; carry residuals with
   explicit ownership and verification criteria, then move to real core APIs.
4. Stage 12-A first audits actual native signatures and installed Qiskit
   2.4.1/2.6 public behavior, not private implementation or test source. Order:
   P0 composite subsystem dimensions for state/density from_int, dims/dim/
   num_qubits/qargs, and propagation through tensor/expand/evolve/partial trace/
   measure/sample; do not flatten nonbinary subsystems into qubits.
   P1 object seed/RNG, explicit-call seed precedence, reproducibility, stream
   advancement and existing integer positional-seed compatibility.
   P2 actual public Statevector add/subtract and DensityMatrix scalar arithmetic,
   preserving complex dtype/dims/zero states/errors/return classes.
   P3 actual Statevector.purity and probabilities/sample container/order/qargs/
   dimension contracts, including DensityMatrix.dim. Do not invent a public
   variance method or duplicate already-correct tensor/expand/evolve paths.
5. Every bounded functional group requires a real API gap, pre-fix failure,
   independent native implementation, mathematical oracle, public black-box
   differential, composed calls, error/resource bounds and tested-source/commit
   equality. No SDK passthrough/wrapper/mock/silent fallback as native execution.
   Stage 12 changes need their own fresh gates; C3-R2 passes cannot accept them.
6. Report matrix/coverage, R2 SHA, C3 classifications and residuals, exact public
   signatures, per-function red/green/math/differential proof and genuine remote
   state. Actual callable core functionality is the primary development metric;
   resource limits remain necessary constraints, not an infinite subproject.
   Full replacement stays ACTIVE/INCOMPLETE; no Capture/Studio work.
