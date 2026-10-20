# Stage 11O-B4 Native QWC And Shot Allocation

Date: 2026-10-20. Starting local HEAD:
`d8d87417db55b359db590e0ebbe61af9bac2ce14`.

The full Qiskit/PennyLane replacement objective remains active and incomplete.
This checkpoint implements real native Pauli grouping, joint samples and shot
allocation, not B5 transformed gradients, B6 defer_measurements or full public
transform parity. Existing 11M/11N/11O-C/11O-A/B1/B2/B3 history is preserved.
No Studio/Router work, token/cloud/hardware call, vendoring, release, tag or
history rewriting is performed.

## Red Tests And Actual Joint Sampling

The first two independently authored tests failed with a missing native
`split_non_commuting` import before implementation. They now verify:

- XX and YY commute as complete matrices but are not QWC; they require separate
  local-basis groups.
- X0 and X0 Z1 share an X0/Z1 basis. After RY(pi/3) on q0 with q1 in zero, one
  actual native Device.sample call produces a joint bitstring buffer. The two
  word eigenvalues are identical for every shot, not merely close in mean.

`quantumbridge/qml/pauli_group.py` implements validated native joint measurement
and immutable result arrays. The existing ExecutionPlan invokes it; no second
quantum interpreter or upstream runtime is introduced. Per group and partition
metadata records actual execution IDs, basis, source word indices/coefficients,
allocated shots, raw joint bitstrings, derived eigenvalues, means, covariance
and per-source expectation contributions/group variances/standard errors.
The word samples are never drawn independently then relabelled as shared.
Analytic evaluation has no bitstrings, no sample call and distinct provenance;
it computes actual Pauli expectations and product moments instead.

Statevector, density/noise, dynamic feedback and native MPS sampling are tested.
For MPS groups, the old separate resource-only trajectory probe is not run:
the sampling API returns memory but no resource receipt, so that metadata is
explicitly unavailable. No extra unaccounted shot job is hidden as bookkeeping,
and no 100-qubit transformed gradient claim is made here.

## Grouping And Reconstruction

`split_non_commuting` dispatches through the existing native transform protocol
to Tape, QNode or explicitly configured native callable. It supports native
Pauli expectation sums and individual Pauli variances. Deterministic bounded
first-fit grouping supports `qwc`, `wires`, `None` and `default`; default is QWC
for the all-Pauli subset. It is not guaranteed minimum graph coloring.
`wires` requires disjoint nonidentity supports on fresh input.

Identity terms become offsets, canonical repeated words share measurement,
original source positions and coefficients are retained, and nested dict/list/
tuple outputs reconstruct in order. Pauli variance and its expectation reuse
the same group memory. Finite Pauli variance is the empirical population
variance, not an unbiased estimator of population variance.

Unsupported measurement kinds, opaque/non-Pauli observables, local measurement
shot/seed overrides and variance of a Hamiltonian sum reject explicitly.
Trainable coefficients and full public operator/capture protocols remain open.

## Shot Contract

| Policy | Implemented physical work |
| --- | --- |
| None | Each group receives the complete parent shots for every partition |
| uniform | Parent shots are a shared total; equal floor shares and ordered remainder |
| weighted | Shared total with group coefficient L1 weights; floor shares and ordered remainder |

For distributed policies, each shot-vector partition/copy is independently
conserved. `[100, (200, 2)]` with weights 1/3/1 gives group shot vectors
20/40/40, 60/120/120, 20/40/40: total physical shots are exactly 100/200/200.
Groups and partitions receive independent child seed streams. Repeating an
explicit seed replays the experiment's values/memory but creates new actual
execution IDs. The deterministic allocation `seed` parameter does not override
the Tape/QNode measurement seed.

Weighted groups whose combined contribution is zero are elided; all-zero and
identity-only results execute no measurement. Uniform/None retain zero terms.
Insufficient samples for a nonzero effective group raise before device work.
Random/custom allocation is explicitly unsupported, not substituted.

A typed complete sibling allocation receipt is required before TransformProgram
accepts changed child shots. Arbitrary user transforms still cannot change
shot shapes without this validation. Physical shot work is counted once per
joint group, not multiplied by the number of word statistics. Group count,
expansion work, circuit copies, coefficient structure, joint sample storage,
covariance storage and total shots are bounded before execution. Direct group
measurement also validates its own storage budget before sampling/expectations.

## Statistics

Each group has empirical covariance from its shared samples, including all
off-diagonal terms. For coefficient vector c, group energy variance is
c.T covariance c. The source expectation standard error sums independent-group
variance-of-mean contributions using ddof=1 covariance divided by group shots.
One-shot uncertainty is unknown (`None`), not falsely zero. Analytic covariance
is calculated from actual commuting Pauli products and has no sampling error.

Tests show positive covariance increases energy uncertainty versus an incorrect
independent-term formula, and anticorrelated equal terms cancel energy and
uncertainty exactly. Across incompatible groups, the reported sum of group
variances is not the full quantum Hamiltonian variance; metadata states this.
Standard errors are statistical estimates, not certified hardware confidence
intervals or systematic-noise/truncation error bounds. Uncertainty of the
nonlinear variance estimator is not implemented.

## Public API Evidence And Differences

Public behavioral references are the
[documented split_non_commuting API](https://docs.pennylane.ai/en/stable/code/api/pennylane.transforms.split_non_commuting.html)
and independently authored installed-API probes. No upstream implementation or
test file is opened/copied, and no private SDK helper is used. Production is
SDK-free. Public differential tests execute on both PL 0.44.1 and 0.42.3.

- Both versions agree on tested fresh-input Pauli/default/QWC/wires/None,
  identity/duplicate/zero, analytic results, and undistributed shot vectors.
- 0.42.3 has no shot_dist parameter. The tests assert its actual TypeError,
  rather than pretending allocation is supported or counting a skip as parity.
- 0.44.1 agrees on tested scalar uniform/weighted integer allocation. It
  flattens a distributed shot vector into one total; native partition
  preservation is an explicit extension/difference.
- In insufficient budgets 0.44.1 may omit zero-shot groups, including nonzero
  contributions. Native code rejects this rather than returning a biased
  result. Weighted zero-contribution handling also differs in some rounding
  cases; no universal exact upstream parity is claimed.
- Public transforms can cache grouping on a Hamiltonian object. Early probing
  reused such an object and wrongly suggested a wires exception. Fresh-object
  tests exposed and corrected that assumption; native grouping does not mutate
  the source Hamiltonian or promise public cache-object behavior.

The native fermionic excitation exp(theta/2*(A-A.dagger)) has the opposite sign
to public DoubleExcitation(theta). The H2 differential first proves complete
complex-unitary equality to DoubleExcitation(-theta), then compares actual
grouped energies. No phase alignment, weakened tolerance, copied implementation
or fixed-Hamiltonian lookup is used.

## Verification

The final production/test snapshot is
`/tmp/qb-stage11ob4-final-heWUXy`, built from tracked HEAD plus only this batch's
staged changes, without unrelated user Studio/Router files. This batch adds 46
independently authored native test functions (51 cases) and 15 public differential
functions (16 cases). Focused new main tests pass all 67 cases. Earlier
preflight counts are superseded by the final resource/input-guard revision.

| Gate | Final measured result |
| --- | --- |
| Main full with explicit package coverage | 1754 passed / 4 skipped, 49 warnings; 54.73 seconds |
| SDK-free full, without Qiskit/PennyLane/Torch/Autograd/PySCF | 1437 passed / 131 skipped, 5 warnings; 14.23 seconds |
| Alternate full, PL 0.42.3 and no Torch/PySCF | 1709 passed / 49 skipped, 8 warnings; 17.57 seconds |
| Explicit package coverage | 21717 / 24389 statements = 89.04424125630408%; 68 unchanged excluded lines; prior baseline 88.92533842704094% |
| Full local matrix and embedded coverage | Exit 0; core/dev full runs each 1754 passed / 4 skipped; actual embedded coverage 1754 / 4 and 24389 statements / 2672 missing |
| SDK-free example, compileall and legal/privacy checks | Example and compileall exit 0; 9 focused legal/no-vendor/no-token/privacy checks passed |

The new joint-measurement module has 100% line coverage, QWC grouping/allocation
97.8021978021978%, and the shared batch program 97.59450171821305%. No numerical
tolerance or exclusion was weakened. Main versions are Python 3.12.6, NumPy
2.4.6, Qiskit 2.4.1 / Aer 0.17.2, PennyLane 0.44.1, Torch 2.12.0, Autograd 1.8.0
and PySCF 2.13.1. The alternate has NumPy 2.5.4, Qiskit 2.6.0 / Aer 0.17.2,
PennyLane 0.42.3 / Autograd 1.9.1, no Torch/PySCF. Both isolated pip checks are
clean. Existing global WeasyPrint/tinycss2 and pyquafu/NumPy conflicts remain
unchanged; no dependency/environment changes were made. JAX/TF are absent and
no end-to-end support for them is claimed.

An additional SDK-free randomized mathematical probe generated 100 independent
four-qubit Pauli Hamiltonians/circuits and executed all four grouping modes.
All 400 analytic reconstructions matched direct native expectation, with
maximum absolute energy error 8.881784197001252e-16. This is extra evidence,
not a claim of optimal grouping or exhaustive public API coverage.

The actual geometry-derived H2 Hamiltonian is measured using native
fermionic-excitation preparation and weighted joint groups with 20001 total
shots: actual group sample counts are 18079/481/481/480/480. The measured energy
is -1.06857396248403, the analytic reference -1.0649835352618404, and the
standard error 0.004216980776791754. Separate public H2 energy reconstruction
executes on both SDK versions.
The SDK-free example prints original terms, groups, basis, actual IDs, sample
counts, allocation, energy/reference, standard error and physical shot totals.
Its three partitions physically use exactly 1001/2001/2001 shots, with two
independent local-basis groups and six distinct actual sampling execution IDs.

Logs: `/tmp/qb-stage11ob4-coverage.log`,
`/tmp/qb-stage11ob4-full-coverage.json`, `/tmp/qb-stage11ob4-sdkfree.log`,
`/tmp/qb-stage11ob4-alternate.log`, `/tmp/qb-stage11ob4-matrix.log`.
Unavailable optional extras are explicitly not executed; passing the matrix
does not prove full ecosystem coverage. All gate processes completed.

## Remaining Work And Publication

B5 transformed native Jacobian/VJP, framework backward integration and the
100-qubit MPS+Template+Transform derivative proof remain unimplemented. Existing
ordinary QNode gradients are not reused as proof; transformed live bindings and
derivative calls still reject. B6 deferred-measurement semantics and final
Stage 11O integration are also open. General observables, measurement kinds,
all allocation strategies, public protocols, JAX/TF and complete SDK parity
remain incomplete.

A further red counterexample found that a framework input used only as a
Hamiltonian coefficient could bypass the old gate-angle guard and be converted
to float by a builder. Transformed QNode inputs are now checked before builder
execution; the test proves that the unsupported graph is rejected without
calling that builder. This is a guard, not implemented coefficient gradients.

Only scoped B4 files are staged/committed. No push or new-SHA remote CI receipt
is claimed. The origin/main tracking value is stale, not current remote proof;
the existing workflow OAuth/network publication limitation is not bypassed or
repeatedly retried. User Studio/Router changes remain untouched and unstaged.
