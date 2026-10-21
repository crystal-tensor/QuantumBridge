# C3-R2 Native State And Result Progress

Date: 2026-10-21. Status: PARTIAL, not final R2/C3 acceptance.
Starting local commit: `89bd0f161dea5b653d2b61137265de4bb6ca4ce6`.
Full independent Qiskit/PennyLane replacement remains ACTIVE / INCOMPLETE.
This report does not replace the bounded full R2 execution spec.

## Actual Functional Changes

- Statevector.from_label now implements the native X/Y eigenstates `+`, `-`,
  `r`, `l`, their tensor products and the zero-qubit empty label, in addition
  to computational-basis labels. Independent complex amplitude tests and six
  optional public Qiskit comparisons exercise actual native execution.
- Statevector.reset is now implemented. No qargs resets to the canonical
  ground state; an explicit subset performs native measurement and bit reset,
  preserving the collapsed state phase, wire order and unselected amplitudes.
  Empty qargs returns an independent unchanged copy. Five public Qiskit reset
  scenarios explicitly translate native leftmost-wire numbering.
- Statevector.sample_counts accepts explicit subsystem qargs as well as the
  existing seed keyword. The previous positional integer seed is retained.
  This is not a claim that all upstream signatures or RNG objects exist.
- Statevector/DensityMatrix copies, conjugation, tensor products, reversal,
  measure and categorical sampling use prior known numerical-buffer admission.
  DensityMatrix.from_statevector owns conversion/conjugate/outer-product arrays.
- Result.statevector()/density_matrix() create independently owned defensive
  copies, including outside a ResourceScope when the source has an actual
  storage account. An explicit new scope charges its own account instead.
  Escaped user views remain valid after Result/Job destruction.

These functions use the existing native runtime and NumPy, not an installed
quantum SDK as an execution engine. No second simulator was added.

## Ownership And Sampling Boundaries

The shared ndarray-root registry holds weak provenance, not a new global
budget. Each real destination has its own reservation; views retain existing
root storage and do not allocate/charge another copy. The existing MPS private
registry names still refer to this shared implementation. Source and destination
accounts release only when their actual storage roots lose all views.

Categorical sampling admits probability and CDF float buffers, uniforms and
intp outcomes before the first factory. Uniforms fill an admitted destination;
inverse-CDF search fills a separately pre-reserved outcome buffer. Confirmed
completed shots are consumed before Python formatting, so later formatting
failure cannot refund real completed samples. Unknown bit-generator, iterator,
Python container and allocator workspace remains unavailable, not measured RSS.

## Red/Fix Evidence

All log prefixes below have separate `.log` and `.exit` receipts in `/tmp`.

| Receipt prefix | Actual result / interpretation |
| --- | --- |
| qb-stage11pc3r2-state-initial-red | Initial 45 failures; NOT authoritative admission proof: lazy NumPy random import contaminated 16 factory-spy cases |
| qb-stage11pc3r2-state-baseline-red | Corrected eager-RNG fixture run on explicit pre-R2 runtime export: 43 failed, 2 deselected; actual pre-fix state/factory/sampling/API gaps |
| qb-stage11pc3r2-state-first-recovery | 136 passed; corrected fixture, native states plus information/MPS/ownership regressions |
| qb-stage11pc3r2-result-initial-red | 18 failed, 2 passed; 16 existing-API ownership/admission/protocol gaps, plus two new fill-failure injections not reachable in the old implementation |
| qb-stage11pc3r2-state-result-green | Invocation error: nonexistent tests/results directory, exit 4, no tests ran; not a failed runtime regression |
| qb-stage11pc3r2-state-result-recovery | 186 passed after Result fix and expanded mathematical/lifetime scenarios |
| qb-stage11pc3r2-state-result-positive | 237 passed, 1 real public differential failure: explicit full-qargs reset incorrectly discarded the collapsed global phase |
| qb-stage11pc3r2-state-result-positive-recovery | 238 passed after correcting explicit reset; includes all new state/Result tests, information, providers, schema and relevant ownership regressions |

The two postprocessing-failure state tests patch a newly introduced real
formatter; they are new fault-injection regressions, not pre-existing API reds.
The reset differential correction changes the implementation and independent
phase/shot expectations; it does not weaken the public array comparison.

## Frozen Partial Validation

The frozen source tree is `ab57997ba1db83ec8bdb0c0f978cfd6792ac3ce0`, exported
to `/tmp/qb-stage11pc3r2-state-result-frozen.v4GugJ/source` using an independent
Git index. It contains baseline tracked files plus only the six runtime files,
two test files and R2 spec listed for this partial batch. User Studio/Router
changes are not included. Documentation results are recorded after the export;
the production/test source is unchanged while these gates run.

- SDK-free FULL: exit 0, 2266 passed / 413 skipped / 5 warnings, 236.78s;
  receipt qb-stage11pc3r2-state-result-sdkfree-full.
- Main FULL: exit 0, 2902 passed / 5 skipped / 3 existing public-oracle xfails /
  57 warnings, 452.23s; receipt qb-stage11pc3r2-state-result-main-full.
- Main skips disclose incompatible pyquafu/NumPy, unavailable Dynamics and
  Optimization, and the missing-JAX-installation negative scenario. These are
  not executed passing optional paths. Existing public xfails are not removed.
- Main coverage and alternate/framework/compile/legal/privacy checks are not
  final R2 receipts for this snapshot.
- No fresh full 28-section matrix yet. Prior R1 receipts are historical only.
- Coverage baseline remains 90.17352569642976%, exclusions 68; no fresh R2
  coverage is claimed until the new complete run is measured.

## Remaining Work And Non-Claims

R2 P1 Operator arithmetic/equiv/deepcopy/from_label/reversal and supported
Pauli/Clifford conversions were not included in this P0/Result frozen tree.
Subsequent P1 implementation and focused evidence are recorded separately in
the Operator/Channel progress report. Existing controlled
tensor/expand/power must not be presented as newly fixed failures.
R2 P2 bool tableau/synthesis/compose/inverse and 100-qubit dense rejection with
continued non-dense operation remain open. The old dense-device aggregate
allowance has NOT been removed: this partial batch is not sufficient evidence
to retire it safely. All final full R2 gates remain required after P1/P2.

State objects still lack the complete upstream dimensions, object-level RNG,
arithmetic, observable, general-map and full public API contracts. Complete
QNode/device/operations/transforms/circuit/compiler/algorithm/qchem/industry and
real remote service functionality remains in the core parity ledger. Core
function work, not coverage alone or inventory, remains the highest objective.
Studio stays last. No cloud/hardware/token/TLS/auth/vendor changes occurred.

No new commit or push is claimed for this partial batch. The actual Git index
is kept separate from validation. The earlier workflow authorization problem
was not retried or bypassed. No force/reset/rebase/amend, tag or release.
