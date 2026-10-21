# Stage 11P-C3-R1 Resource Ownership Progress

## Current Task 3E Gate, Channel And Evolution Progress

### Latest Frozen Checkpoint

Final test-source tree `66b10f4898fd679a6152d458032acd089d972cf6`, unchanged
production subtree `146842eb7a450b97f51c0971dfb1a787881cf842`, export
`/tmp/qb-stage11pc3r1-native-e-coverage-final.GQfo2c/source`. HEAD plus 85
explicit R1 paths was frozen with a separate index. Actual Git index remains
unstaged. Working/exported production, tests and examples match that index;
later report-only edits do not change the tested runtime or test source.
This latest checkpoint supersedes the earlier development-only pending
statements below; those are retained as actual chronological evidence.

Fresh gates on this final tree, each prefix under `/tmp/` beginning
`qb-stage11pc3r1-native-e-final2-`, each with complete `.log/.exit`:

| Gate | Actual result | Suffix |
| --- | --- | --- |
| SDK-free FULL | 2155 passed, 402 missing-optional skips, 5 warnings; 243.47s; exit 0 | `sdkfree-full` |
| Main FULL coverage | 2780 passed, 5 skipped, 3 declared public-oracle xfails, 57 warnings; 1360.55s; exit 0 | `main-coverage-full` |
| Alternate FULL | 2778 passed, 5 skipped, 5 declared public-oracle xfails, 49 warnings; 442.30s; exit 0 | `alternate-full` |
| Independent JAX 0.12 | 600 passed, 150 missing-other-framework skips; 32.18s; exit 0 | `jax012` |
| Independent TensorFlow 2.21 | 622 passed, 133 missing-other-framework/SciPy skips; 42.65s; exit 0 | `tf` |
| Torch/Autograd focus | 46 passed, 722 unrelated deselections; 14.43s; exit 0 | `torch-autograd` |
| Compileall | exit 0 | `compile` |
| Legal/source notices | 4 passed; 0.12s; exit 0 | `legal` |
| Privacy/offline/no-token/security | 49 passed, one existing warning; 1.56s; exit 0 | `privacy` |

Final full coverage JSON `/tmp/qb-stage11pc3r1-native-e-final2-coverage.json`
records 27126/30082 = **90.17352569642976%**, missing 2956, excluded 68.
It exceeds the exact 90.08806827841818% baseline without exclusions or tolerance
changes. This is a fresh full run, not the development union below. It remains
code line coverage, not SDK function completion.

The real complete 28-section local matrix completed on this final tree at
`qb-stage11pc3r1-native-e-final2-full-matrix.log/.exit`, shell exit **0**.
All 28 headers and the final OpenFermion section are present. This is the
actual script, not a focused/reduced replacement. Every lane uses the main
environment; the core-only section name does not mean that environment lacked
SDKs. The genuinely SDK-free FULL gate is recorded separately above.

| Matrix section | Actual result |
| --- | --- |
| core-only | 2780 passed/5 skipped/3 xfailed/57 warnings; 439.91s |
| qiskit-extra | 5 passed |
| pennylane-extra | 9 passed |
| qiskit-aer-extra | 146 passed |
| qiskit-finance-extra | dependency unavailable; NOT executed |
| qiskit-optimization-extra | dependency unavailable; NOT executed |
| qiskit-machine-learning-extra | dependency unavailable; NOT executed |
| qiskit-nature-extra | 21 passed |
| qiskit-algorithms-extra | 26 passed |
| qiskit-dynamics-extra | dependency unavailable; advisory subset NOT executed |
| qiskit-metal-extra | dependency unavailable; advisory subset NOT executed |
| qiskit-runtime-extra | 5 passed; offline/no-token contracts, not hardware |
| qiskit-experiments-extra | dependency unavailable; NOT executed |
| qiskit-addons-extra | dependencies unavailable; NOT executed |
| pennylane-full-extra | 44 passed; not full SDK functional parity |
| mqt-compat | 15 passed |
| torchquantum-compat | 17 passed |
| qos-uqci-compat | 11 passed; not hardware proof |
| quafu-compat | 15 passed; offline, not real cloud or a clean pyquafu stack |
| benchpress-compat | 19 passed |
| studio-backend-api | 33 existing baseline tests; no Studio changes |
| ecosystem-inventory | 27 passed; name inventory is not numerical function coverage |
| dev | FULL 2780 passed/5 skipped/3 xfailed; 438.39s; FULL --cov same counts, 1343.89s |
| chemistry-core | 5 passed |
| chemistry-extra | 30 passed |
| qiskit-nature-p2-extra | 5 passed |
| algorithms-extra | 10 passed |
| openfermion-extra | 1 passed |

After the script's real terminal exit, a separate export from its coverage
database completed with exit 0 (`native-e-final2-matrix-coverage-export`).
`/tmp/qb-stage11pc3r1-native-e-final2-matrix-coverage.json` independently
records 27126/30082 = 90.17352569642976%, missing 2956, excluded 68, identical
to the standalone final FULL coverage. The seven missing optional subsets
are NOT labeled passed. Inventory scripts regenerate inventory/matrix docs
inside the private export; this is not a claim those generated docs stayed
byte-identical or were copied into the user's working tree.

Fresh `native-e-final2-versions-{main,alternate,sdkfree,jax012,tf}` and matching
`pip-*` receipts record imports from the final export. Python is 3.12.6 in all
five environments. Main NumPy/Qiskit/Aer/PennyLane/JAX/TF/Torch/Autograd:
2.4.6/2.4.1/0.17.2/0.44.1/0.7.1/2.21/2.12/1.8. Alternate changes Qiskit to
2.6, PennyLane to 0.42.3, JAX to 0.6.2 and Autograd to 1.9.1. Main/alternate
include disclosed user/system-package origins, not hermetic all-in-one stacks.
SDK-free and independent JAX 0.12/TF 2.21 use NumPy 2.5.4 without upstream
quantum SDKs; SDK-free has none of the four classical AD frameworks.
OPENBLAS/OMP threads are 1 and JAX x64 is enabled. SDK-free/JAX/TF pip exit 0;
main/alternate pip exit 1 for the unchanged pyquafu NumPy<2 versus 2.4.6 and
WeasyPrint 68.1/tinycss2 1.4 conflicts. No dependency/auth changes conceal them.

Final scoped filename-only credential/private-key scans of all 85 owned paths
had no matches or vendored/site-packages/venv/wheel/dist-info/egg-info paths.
This does not certify the user's unrelated files. Working and exported
production/tests/examples still match the frozen index; diff-check passes.
All needed pytest/matrix/coverage-export processes are terminal. At the final
gate receipt, actual index was unstaged and HEAD was 71f211d. Task 3E's completed
coordination prompt explicitly allows a normal R1-only local checkpoint after
these gates. That limited checkpoint is recorded separately by Git, without
amend/force/reset/rebase, and its exact hash is in the final execution result.
This is not R1 acceptance, a push or a remote-CI claim. User Studio/Router dirt
must remain excluded; the persistent known pip conflicts are disclosed above.
R1/C3 remains PARTIAL because unlisted state/tableau/Operator paths still lack
complete site ownership; full native Qiskit/PennyLane replacement remains
ACTIVE/INCOMPLETE. No Studio/Capture/cloud/hardware/token work occurred.

Concrete remaining audit sites include public Statevector copy/sample/measure/
tensor/reset helpers; DensityMatrix copy/sample/measure/from_statevector;
Operator from_label/tensorpower/reverse/arithmetic/equiv/deepcopy;
_QuantumChannel.__deepcopy__; Clifford/tableau bool buffers and synthesis;
Result.statevector()/density_matrix() defensive copies; and retirement of
uncertified portions of the old dense-device aggregate allowance. Known
explicit output ownership here is not universal native allocator closure.

### Development History

Current code is newer than the Task 3D frozen tree below. This is development
progress, not final R1 acceptance or full Qiskit/PennyLane functional parity.
The completed Task 3D coordination reply authorized this slice. No upstream
quantum engine, implementation/test source port, cloud/token or Studio work
is introduced. User Studio/Router changes remain untouched and excluded.

Actual independent development receipts under `/tmp/`, each with `.log/.exit`:

- `qb-stage11pc3r1-gate-e-corrected-red`: 43 failures, including gate factories,
  Circuit.unitary conversion, valid stacked Kraus admission, QuantumError
  products/canonical Choi, dense evolution/reset and dense tableau preflight.
  The earlier compose spy was strengthened to detect actual ndarray matmul,
  rather than passing because a later constructor happened to reject.
- `qb-stage11pc3r1-gate-e-channel-evolution-red`: 17 failures: six public
  channel representations' conversion factories, direct state dtype copies,
  density reset/initialization and linear-map evolution.
- `qb-stage11pc3r1-gate-e-power-red`: two failures. Reserving only the final
  matrix_power output did not own its explicit NumPy product intermediates.
- `qb-stage11pc3r1-gate-e-ensemble-noise-red`: three failures. Weighted
  stabilizer noise bypassed admission; Aer vector ensemble called unowned
  outer products and density ensemble output had no surviving root lease.
- `qb-stage11pc3r1-gate-e-ensemble-noise-recovery`: 144 passed. Independent
  analytic gate matrices cover phase, controlled phase/wires, U rotations,
  Pauli-pair rotations, DCX/ECR/iSWAP and controlled permutations. Numeric
  strided ndarray subclasses do not dispatch foreign hooks; stack aliases
  produce separate real copies, with valid/fail/valid recovery. Six channel
  representations, generalized and rectangular qubit maps, both compose
  orders, tensor/adjoint/arithmetic, negative integer powers, reset, noise
  families and surviving user views have actual numerical/lifetime checks.
- `qb-stage11pc3r1-gate-e-derivative-broad-recovery`: 1108 passed, one skipped,
  one failed. The failure assumed all reservation categories remained in the
  4096-entry ring after new gate/evolution observations. The actual 64-shared
  second-adjoint result and cumulative-work equality passed. The test now
  observes actual reservation events directly, retaining the same category
  assertion; the bounded ledger contract is unchanged, not enlarged or hidden.
- `qb-stage11pc3r1-gate-e-positive-final`: 197 passed, 0.84s, including builtin
  noise channels, negative/zero powers, pre-factory power rejection,
  eigendecomposition group denial/exception recovery/root-view lifetime, the
  corrected 64-shared reservation assertion and existing lifecycle tests.
- `qb-stage11pc3r1-gate-e-kraus-group-red`: four actual failures. Public Kraus
  stacks, paired generalized stacks and native defensive copies allocated
  before whole conversion-group admission; generalized numeric ndarray
  subclasses dispatched their foreign iterator. Actual copies are now
  preflighted together, matching complex buffers still borrow, and both
  generalized groups are inspected as base numeric arrays before iteration.
  `qb-stage11pc3r1-gate-e-kraus-group-recovery`: 243 passed, 1.40s.

Intermediate tree `a54a607a1fed55416c1a461bf5aed3ab45356018` passed SDK-free
FULL: 2136 passed/402 skipped/5 warnings, 238.08s, exit 0 at prefix
`qb-stage11pc3r1-native-e-clean-sdkfree-full`. The later Kraus group fix
invalidated that tree as final Task 3E evidence. Its in-progress main coverage
run was deliberately stopped with SIGTERM; independent runner receipt
`qb-stage11pc3r1-native-e-clean-main-coverage-full.exit` is -15, NOT passed.
This was a source-change restart, not a timeout or concealed red. A new
source export and all required fresh final gates must follow.

Tree `91c131ad6bb681f5b89245e3a9b5bdf1b4c453f6`, production subtree
`146842eb7a450b97f51c0971dfb1a787881cf842`, exported to
`/tmp/qb-stage11pc3r1-native-e-final.LafGEn/source`, then completed:

- SDK-free FULL: 2140 passed/402 skipped/5 warnings, 238.32s, exit 0.
- Main FULL coverage: 2765 passed/5 skipped/3 declared public-oracle xfails/
  57 warnings, 1332.82s, exit 0. Exact coverage was 27055/30082 =
  89.93750415530883%, missing 3027, excluded 68. The display rounded this to
  90, but it FAILS the exact 90.08806827841818% baseline. No alternate,
  independent-framework or complete matrix gate was started by that pipeline
  after the failed coverage threshold. This is not a fully green final tree.
- Compileall exit 0; legal 4 passed/0.11s; privacy/offline/no-token/security
  49 passed/one existing warning/1.48s. Prefix for these receipts:
  `/tmp/qb-stage11pc3r1-native-e-final-`, each with `.log/.exit`.

Tests were added without further runtime changes or exclusions: public native
Operator algebra/exports and circuit phase, actual native Operator/Circuit
channel constructors, raw/generalized Stinespring matrices, density validity/
pure-state eigenvector lifetime and malformed gate/Kronecker guards.
`qb-stage11pc3r1-native-e-coverage-recovery-focus`: 175 passed, 3.90s, exit 0.
The development union of old full executed-line sets with these focused tests
covers 71 additional statements: 27126/30082 = 90.17352569642976%, excluded 68.
This is an explicit development calculation across matching production source,
NOT a new full coverage run. Fresh full-source gates remain required.

Five fresh version/import-origin receipts on the 91c131a export confirm native
imports from that export. Versions match Task 3D's disclosed environments.
SDK-free/JAX/TF pip checks exit 0; main/alternate exit 1 for the same pyquafu
NumPy<2 versus 2.4.6 and WeasyPrint/tinycss2 conflicts. No package/auth changes
were made. The actual index is still unstaged; no commit/push or remote CI.

Some intermediate commands are deliberately not final evidence: one broad
command named a nonexistent tests/control_flow directory and exited 4 without
running tests; an early positive test assumed non-qubit DensityMatrix output,
reversed a private projection return pair and constructed Operator(Operator)
although that legacy constructor accepts a matrix. Those fixtures were fixed
without expanding or weakening production contracts. A prior accidental
indent in control-flow projection was repaired before the 387/435-test green
development gates. All such results remain distinguishable in their logs.

Known gate outputs and custom-unitary conversion use existing numeric
preallocation and column validation. Controlled/DCX coexistence is admitted
before the first component factory. Matching numeric metadata buffers are
borrowed, not charged as imaginary copies. Builtin Kraus noise matrices,
defensive exports and QuantumError compose/tensor use independent group
leases. Canonical Choi/eigh outputs, native channel conversions and explicit
SVD/eigen reconstruction outputs have real root ownership. Integer powers
reuse existing owned matrix products, not opaque matrix_power intermediates.

Dense state/density evolution, initialization, reset/projection, linear-map
gate/channel action and analytic Aer ensemble outputs now own their explicit
conversion, conjugate, contraction and accumulation arrays. No new simulator
is added; the existing native formulas and tolerances remain in use. Full
backing roots remain charged while user slices survive their parent Results.
Dense tableau requests preflight the final vector before synthesis, but the
tableau engine's internal bool scratch/copies are NOT thereby certified.

Remaining scope is explicit: general Statevector/DensityMatrix sampling,
copy/measure/tensor helpers, unrelated Operator methods, full Clifford/tableau
internals and other unlisted native routines still need site-level audits.
The old dense-device conservative allowance is not proof of those owners.
NumPy/BLAS/LAPACK internal workspace and Python/JSON heap remain unavailable,
not measured process RSS. Three-environment FULL, coverage (baseline
90.08806827841818%, 68 exclusions), independent frameworks and the complete
28-section matrix must still run on a fresh final Task 3E source export.
No staging/commit/push, remote-CI result or complete replacement is claimed.

## Current Task 3D Native Validation Progress

The Task 3C report was delivered to the authorized ChatGPT conversation
"Claude 代码泄漏与应对". Its completed report-based reply authorized Task 3D:
gate/Kraus/CPTP, CSR, then non-MPS snapshot allocation closure before final
frozen-source gates. It was not an independent audit or acceptance. Full
Qiskit/PennyLane functional replacement remains ACTIVE/INCOMPLETE.

Actual initial red: `/tmp/qb-stage11pc3r1-validation-d-initial-red.log/.exit`,
four failures, exit 1: gate identity/Gram scratch, Kraus copies, CSR constructor,
and dense snapshot aggregation all reached allocation before unified admission.
Additional six native-representation CPTP reds:
`qb-stage11pc3r1-validation-d-cptp-red`, exit 1. No exception expectations or
physical tolerances were weakened to make these reds green.

Native unitarity/trace-preserving validation uses a `33*d` uint8 arena for
two contiguous complex128 columns and one bool finite mask. Scalar column
inner products compare to identity entries with the previous atol/rtol; no
dense Gram/identity scratch. All Kraus defensive copies (`16*k*d*d`) and
the validation arena are reserved together before the first allocation.
Copies own independent roots and escaping views retain each full root lease.
Known numeric builtin containers are inspected before conversion; opaque
foreign conversion/sequence protocols reject without dispatch.

Native Kraus/SuperOp/Choi/PTM/Chi/Stinespring CP/TP checks reuse their existing
representation mathematics. Choi and basis conversion destinations, explicit
Hermitian scratch and eigvalsh outputs reserve before their factories. The
TP partial trace is a scalar reduction, with no allocated identity or trace
matrix. These are bounded paths around existing native numerical routines,
not a second simulator or an upstream SDK implementation.

Pauli sparse output constructs one-nonzero-per-row CSR directly, with no dense
fallback. Complex data, integer indices and row pointers reserve as a group
before NumPy/SciPy calls; each distinct root has its own lease. Matching index
dtypes and copy=False are followed by actual storage-sharing checks. Signed
basis-permutation algebra is shared with dense Pauli construction and snapshot
moments, preserving complex Y/global phases and wire order.

Non-MPS snapshot numerical copies, probability/reduced-density buffers,
moment outputs and cumulative aggregates use owned buffers. Updates are
transactional: failed group/transport/memory checks do not replace prior cells
or counters. Raw defensive outputs transfer to cells without a second copy;
metadata preserves the old public encoded schema, including scalar 0d arrays.
Result.data decoding remains controlled by the Task 3C path; user numerical
views retain the import root after context/Result destruction. MPS amplitude
selection uses native contractions without dense fallback.

NumPy/SciPy/LAPACK internals, Python scalar/container/JSON heap remain explicitly
unavailable, not observed total process memory. General gate constructors,
unrelated channel algebra/construction, tableau-to-statevector expansion and
other full-engine allocations are not certified by these scoped contracts.
R1/C3 remains PARTIAL while those known paths or final gates remain open.

Working-source intermediate gates (each prefix under /tmp with log/exit):
`validation-d-four-green`: 4 passed; `validation-d-positive`: 22 passed;
`validation-d-core-broad`: 963 passed, one warning, 80.41s;
`validation-d-cptp-first-fix`: passed;
`validation-d-numerical`: 141 passed, 1.16s. These were sequential development
checkpoints, not evidence for a later frozen final tree. New/old frozen gates
must be distinguished. No staging/commit/push or remote-CI claim is made.
User Studio/Router changes remain untouched and excluded.

### Task 3D Frozen Source And Remaining Work

Frozen tree `bd31b55c4f1459eb3629e207eee13153502dbd89`, production subtree
`3c09319bad9e6f2bcd5a9c79a6fe7cd65848b9af`, export
`/tmp/qb-stage11pc3r1-validation-d-validate.KAh1Mi/source`. HEAD plus 75
explicitly owned paths was frozen through a separate index. Actual index
remains unstaged. Later report-only edits do not alter tested runtime/tests.
Working and exported production/tests/examples in the explicit frozen index
compared equal to the tree. Unrelated untracked Router content is intentionally
excluded; this is not a claim to have tested every dirty file in the workspace.
Filename-only credential/private-key scans of those 75 paths had no matches;
no owned path includes vendored/site-packages/venv/wheel/dist-info/egg-info
content. This is a scoped scan, not a claim about the user's unrelated files.

Fresh SDK-free FULL gate:
`/tmp/qb-stage11pc3r1-validation-d-clean-sdkfree-full.log/.exit`,
1980 passed, 402 missing-optional-dependency skips, 5 warnings, 237.43s,
exit 0. Seven additional skips relative to Task 3C are SciPy-dependent new
CSR tests; missing SDK/framework/SciPy paths are not verified parity.
The last development focus before freezing passed 210 tests, 1.51s,
`qb-stage11pc3r1-validation-d-final-focus`. Main full coverage is a separate
fresh gate; old Task 3C coverage/matrix cannot validate this new tree.

Main FULL coverage completed at
`/tmp/qb-stage11pc3r1-validation-d-clean-main-coverage-full.log/.exit`:
2605 passed, 5 skipped, 3 previously declared public-oracle xfails, 57 warnings,
1067.75s, exit 0. The longer runtime is retained, not replaced with an older
or targeted gate's timing. Full --cov=quantumbridge JSON at
`/tmp/qb-stage11pc3r1-validation-d-clean-coverage.json` records
26494/29409 covered statements = 90.08806827841818%, 2915 missing and 68
excluded lines. This exceeds the Task 3C 90.03744546360232% baseline without
adding exclusions. It is code line coverage, NOT SDK function completion.

Additional frozen-source gates, all exit 0, each prefix under /tmp with full
log and independent exit receipt:

| Gate | Result | Prefix suffix after `qb-stage11pc3r1-validation-d-clean-` |
| --- | --- | --- |
| Alternate FULL | 2603 passed, 5 skipped, 5 declared public-oracle xfails, 49 warnings; 351.31s | `alternate-full` |
| Independent JAX 0.12 derivative/interfaces | 425 passed, 150 missing-other-framework skips; 24.39s | `jax012` |
| Independent TensorFlow 2.21 derivative/interfaces | 447 passed, 133 missing-other-framework/SciPy skips; 28.96s | `tf` |
| Torch/Autograd focused | 46 passed, 547 unrelated deselections; 11.25s | `torch-autograd` |
| Compileall | exit 0 | `compile` |
| Legal/source notices | 4 passed; 0.14s | `legal` |
| No-cloud/no-token/security | 47 passed, one existing warning; 1.62s | `privacy` |

One orchestration cell attempted to notify an empty compile log and raised
`notify expects non-empty text` after the actual compiler had already exited
0. Its preceding JAX/TF/Torch and compile receipts were recovered without
rerunning them; remaining legal/privacy commands then completed normally.
This was not a native compiler/test failure or a lost running test process.

Fresh `versions-{main,alternate,sdkfree,jax012,tf}` and matching `pip-*`
receipts confirm QuantumBridge imports from this frozen export. All use
Python 3.12.6. Main has NumPy 2.4.6/Qiskit 2.4.1/Aer 0.17.2/PennyLane 0.44.1/
JAX 0.7.1/TF 2.21/Torch 2.12/Autograd 1.8; alternate has Qiskit 2.6,
PennyLane 0.42.3/JAX 0.6.2/Autograd 1.9.1, otherwise the same named versions.
Those two environments include user/system-package origins, explicitly
recorded in their version logs. SDK-free, independent JAX 0.12 and TF 2.21
use NumPy 2.5.4 with no Qiskit/Aer/PennyLane; SDK-free has none of the four
classical autodiff frameworks, and each independent environment has only its
named framework. OPENBLAS/OMP threads are 1 and JAX x64 is enabled.

SDK-free/JAX/TF pip checks exit 0. Main/alternate pip checks exit 1 with the
same two prior conflicts: pyquafu 0.4.5 requires NumPy <2 but 2.4.6 is present;
WeasyPrint 68.1 requires tinycss2 >=1.5 but 1.4 is present. No packages were
changed to conceal these conflicts. They are not a newly green dependency
environment, cloud/hardware proof or evidence of pyquafu compatibility.

### Completed Task 3D Matrix

The actual complete `bash scripts/run_local_matrix.sh` finished on the same
frozen source, not a reduced/focused replacement. Final independent receipt:
`/tmp/qb-stage11pc3r1-validation-d-clean-full-matrix.log/.exit`, shell exit 0.
All 28 section headers are present. The script's core-only name does not mean
this main environment lacked SDKs; the genuinely SDK-free FULL gate is
recorded separately above. Each matrix section used the main environment,
not a freshly dependency-resolved isolated environment per lane.

| Section | Actual result |
| --- | --- |
| core-only | 2605 passed, 5 skipped, 3 xfailed; 347.97s |
| qiskit-extra | 5 passed |
| pennylane-extra | 9 passed |
| qiskit-aer-extra | 146 passed |
| qiskit-finance-extra | dependency unavailable; subset NOT executed |
| qiskit-optimization-extra | dependency unavailable; subset NOT executed |
| qiskit-machine-learning-extra | dependency unavailable; subset NOT executed |
| qiskit-nature-extra | 21 passed |
| qiskit-algorithms-extra | 26 passed |
| qiskit-dynamics-extra | dependency unavailable; advisory subset NOT executed |
| qiskit-metal-extra | dependency unavailable; advisory subset NOT executed |
| qiskit-runtime-extra | 5 passed, offline/no-token contracts only |
| qiskit-experiments-extra | dependency unavailable; subset NOT executed |
| qiskit-addons-extra | dependencies unavailable; subset NOT executed |
| pennylane-full-extra | 44 passed, not full SDK functional parity |
| mqt-compat | 15 passed |
| torchquantum-compat | 17 passed |
| qos-uqci-compat | 11 passed, not real-hardware proof |
| quafu-compat | 15 passed, not real-cloud proof or a clean pyquafu dependency stack |
| benchpress-compat | 19 passed |
| studio-backend-api | 33 existing baseline tests passed; no Studio implementation/change |
| ecosystem-inventory | 27 passed, inventories are not numerical function coverage |
| dev | FULL 2605 passed/5 skipped/3 xfailed, 347.45s; FULL --cov 2605 passed/5 skipped/3 xfailed, 1068.16s |
| chemistry-core | 5 passed |
| chemistry-extra | 30 passed |
| qiskit-nature-p2-extra | 5 passed |
| algorithms-extra | 10 passed |
| openfermion-extra | 1 passed |

The final matrix coverage database was separately exported after the script
completed to `/tmp/qb-stage11pc3r1-validation-d-matrix-coverage.json`. It
independently records 26494/29409 = 90.08806827841818%, 2915 missing,
68 excluded, identical to the separate full-main coverage gate. The coverage
export process completed with exit 0 before its JSON was inspected.
The seven unavailable optional ecosystem subsets are not relabeled passed.
All working/exported frozen-index runtime/tests/examples comparisons and
diff-checks still exit 0 after these gates. No needed pytest/matrix process
remains running. Report-only changes after freezing do not change code.

Known unclosed sites from source inspection, not hidden by aggregate estimates:

- `utils/math.py::gate_matrix`, `_controlled_one_qubit_matrix`, `_u_matrix`:
  gate constructors still contain array/diag/Kronecker/scale/metadata-dtype
  outputs before individual unified leases. The new validator only owns its
  own validation workspace; it does not retroactively own a gate factory.
- `core/circuit.py::unitary` and other public construction validators still
  have conversion/Gram/identity scratch outside this scoped dispatch fix.
- `noise/channels.py` and `noise/quantum_error.py` still have independent
  Kraus factories/copies and general compose/tensor/canonical-Choi algebra.
- General adjoint/dense state operations, reset branches and density/channel
  evolution include additional outputs outside the current audit.
- `SnapshotContext._vector` for stabilizer still delegates tableau-to-dense
  expansion; that engine's internal allocation contract is not certified.
- Managed Kraus validation currently admits explicit builtin list/tuple
  groups. Its generic iterable/stacked-ndarray input compatibility is narrower
  than the legacy no-scope path and remains a follow-up admission-contract
  gap, not a claim that all native numeric input forms are already supported.

The complete local matrix is now verified, but a qualified commit, remote CI
and R1/C3 acceptance are not claimed. Known allocation/admission gaps above
keep this R1 slice PARTIAL. Full replacement stays ACTIVE/INCOMPLETE. Prior
Task 3C green receipts below remain historical evidence only.

### Completed Coordination And Next Scope

The complete Task 3D report, including all actual green/red receipts, seven
unexecuted optional matrix subsets, persistent pip conflicts, uncommitted Git
state and explicit remaining allocation/admission gaps, was delivered to the
authorized ChatGPT conversation "Claude 代码泄漏与应对". Its completed reply
was read in full, including both virtualized parts of the execution prompt.
This is report-based coordination, not independent source audit.

The reply agrees to continue fixing known gaps before requesting R1/C3 joint
acceptance and a limited local commit. Next Task 3E order: native gate
constructors; QuantumError/Kraus legitimate numeric admission (including
stacked ndarray); channel/Choi algebra; dense evolution/reset/tableau; then
fresh frozen-source full gates. It requires real red-green evidence, no
tolerance weakening, coverage baseline 90.08806827841818%, no increase from
68 exclusions and actual 28-section matrix exit. User Studio/Router remain
excluded; no push/auth/TLS/force/reset/rebase/amend/tag/release/token/cloud/
hardware work is authorized by that prompt. Capture/Studio remain deferred.
This report does not claim Task 3E implementation has already occurred.
Full Qiskit/PennyLane functional replacement remains ACTIVE/INCOMPLETE.

## Prior Task 3C Allocation Progress

Current source is newer than the Task 3B tree below. Full SDK replacement and
R1/C3 remain PARTIAL. This slice follows the completed report-based ChatGPT
Task 3C prompt; no independent code audit or final acceptance is claimed.

Actual red receipts under `/tmp/`, each with `.log/.exit`:

- `qb-stage11pc3r1-observable-ir-initial-red`: six failures. Known Pauli/
  Hamiltonian dense output, dtype conversion, IR component conversion and
  strided real IR export entered factories before unified reservation.
- `qb-stage11pc3r1-observable-ir-validation-red`: seven failures, including
  those same six and a new Hermitian validation scratch admission failure.
- `qb-stage11pc3r1-result-decode-initial-red`: three failures. Result state
  import and snapshot decode coerced before admission; density import owned
  no retained numerical root.
- `qb-stage11pc3r1-json-bounds-initial-red`: three failures, three unrelated
  deselections. Oversized text reached the decoder; excessive depth/labels
  reached numerical conversion. These are structure/transport failures, not
  fabricated observations of Python process-memory allocation.

Known numerical fixes use the existing ResourceScope/ledger/root leases.
Dense native Pauli matrices fill a signed basis permutation in one reserved
complex destination, preserving phase and wire ordering. Managed known native
Hamiltonian, SparsePauliOperator, Operator and QubitHamiltonian paths remain;
opaque foreign factories reject before dispatch (or fail prior byte preflight).
Numeric buffer/builtin-container conversion validates shape/dtype first and
fills one owned result without full real/imag/astype intermediates. Matching
complex ndarray inputs borrow their actual storage; genuine copies own roots.
Hermitian checks use one explicitly reserved 33-bytes-per-entry arena, not
unbudgeted conjugate/allclose arrays. Native physical algorithms are not
replaced by a second simulator or an upstream SDK fallback.

Result imports now own one destination for a vector or complete density
matrix. Snapshot array decode owns its actual real/complex destination and
finite-validation mask. Returned arrays/views retain leases after Result
destruction. Existing MPS tolist/export is tested with ndarray factories
forbidden: it does not create a numeric copy, so none is falsely charged.
Its logical exported scalar count is bounded before list materialization.

Existing standard JSON encoder/decoder wrappers now apply configurable
SerializationLimits: 16 MiB input/output UTF-8 transport, 256 JSON nesting depth,
100000 nodes, 1048576 numeric elements, 1024 saved labels by default. Result,
IRProgram and native Aer envelopes reuse these wrappers. Resource serialization
errors map to existing derivative RESOURCE_LIMIT, not generic runtime failure.
Decoded structure checks precede numerical import; output chunks are bounded
before joining. Python containers, decoder strings and hidden iterator/
allocator memory remain unavailable, not a measured or strict RSS bound.
JSON imports still do not reconstruct the native saved-MPS map.

Intermediate green prefixes: observable-ir-first-fix 314 passed;
result-decode-first-fix 169 passed; observable-ir-positive 133 passed;
json-bounds-first-fix 348 passed. The first broad gate had 1049 passed,
one skip and one actual regression: the managed whitelist omitted native
QubitHamiltonian and rejected H2 second adjoint. Its native controlled matrix
path was added without weakening tests/tolerances; observable-h2-recovery
then passed 63 tests. These working-source gates are not frozen-source final
full/coverage/matrix evidence.

Known other allocation sites remain, including general gate-unitarity/CPTP
validation, sparse CSR conversions and non-MPS snapshot aggregation. Their
older aggregate allowances are not relabeled individual-root proof. Final
gates/acceptance, full independent SDK parity and remote CI remain unproven.
No commit/push, auth/TLS/token/cloud/hardware/vendor, Studio/Router, tag/release
or history rewrite is performed in this slice.

### Initial Frozen Run Exposed Compiler Policy Regression

Initial Task 3C tree `0f7c556e17b0360712ecfd0cca18411a4e810e62`, production
`af593a2ad317b731bad89cef09120f9482b61537`, export
`/tmp/qb-stage11pc3r1-observable-json-validate.eLmSHI/source`, is NOT accepted.
Its SDK-free full run at `qb-stage11pc3r1-observable-clean-sdkfree-full`
has 1937 passed, 395 skipped, one regression; 225.55s; exit 1. The original
H2 compile/decompose workflow exceeded the newly applied JSON depth policy.
Main full coverage on that old tree was deliberately interrupted after this
confirmed failure: 1843 passed/5 skipped/3 xfailed; 165.58s; exit 2, not a
completed coverage gate. Its actual wrapper/test PIDs were confirmed terminal;
no old process was restarted merely because an observation timed out.

An initial correction separating semantic depth 32 from JSON physical depth
256 still failed the same valid internal compiler workflow (json-depth-recovery:
226 passed/one failure). The actual boundary was internal pass mutation
comparison using the public transport exporter. PassManager now preserves its
old canonical standard-JSON comparison over structured IR directly, without
requiring a wire-format export. AnalysisPass mutation protection remains,
including float/int metadata representation changes. Compiler comparison
Python heap is explicitly unavailable, not relabeled an owned-array bound.
No old H2 workflow assertion or numerical tolerance was weakened. External
JSON depth/byte/node/element/label checks remain active and configurable.
Fresh corrected-source gates are required; the initial frozen receipts above
do not validate that later runtime correction.

### Corrected Frozen Task 3C Evidence

Tree: `aa70c8eb092b77cf94f3202d9c812ee48aaff078`.
Production subtree: `9b0cc3ebde2eeee76d881805b067060e48f6845d`.
Export: `/tmp/qb-stage11pc3r1-observable-json-b-validate.lWNUDo/source`.
HEAD plus 72 explicitly owned paths was frozen through a separate index; the
actual index remains unstaged. User Studio/Router changes were excluded.
After all gates, working and exported production/tests/examples compare equal
to this tree. Later edits to this report do not change tested runtime/tests.

All prefixes below are under `/tmp/` with complete `.log` and independent
`.exit`. Unlike the earlier scoped Task 3B gates, all three main environments
here ran FULL pytest. Missing dependencies and declared public-oracle xfails
are not counted as functional parity or numerical successes.

| Gate | Actual result, exit 0 | Prefix |
| --- | --- | --- |
| SDK-free FULL | 1939 passed, 395 optional skips, 5 warnings; 225.33s | `qb-stage11pc3r1-observable-b-clean-sdkfree-full` |
| Main FULL with coverage | 2557 passed, 5 skips, 3 declared public-oracle xfails, 57 warnings; 871.45s | `qb-stage11pc3r1-observable-b-clean-main-coverage-full` |
| Alternate FULL | 2555 passed, 5 skips, 5 declared public-oracle xfails, 49 warnings; 327.34s | `qb-stage11pc3r1-observable-b-clean-alternate-full` |
| Independent JAX 0.12 derivative/interfaces | 377 passed, 150 missing-framework skips; 19.03s | `qb-stage11pc3r1-observable-b-clean-jax012` |
| Independent TF 2.21 derivative/interfaces | 406 passed, 126 missing-framework skips; 23.83s | `qb-stage11pc3r1-observable-b-clean-tf` |
| Compileall | exit 0 | `qb-stage11pc3r1-observable-b-clean-compile` |
| Legal/source ledger | 5 passed; 0.12s | `qb-stage11pc3r1-observable-b-clean-legal` |
| Privacy/security | 32 passed; 0.28s | `qb-stage11pc3r1-observable-b-clean-privacy` |

The full main command included --cov=quantumbridge, not a targeted coverage
subset. Exact JSON totals at
`/tmp/qb-stage11pc3r1-observable-b-clean-coverage.json`: 26209/29109 covered
statements = 90.03744546360232%, 2900 missing, 68 excluded lines. This exceeds
89.98831320607714% without adding exclusions. It is line coverage, not a
function-parity percentage or proof of all native allocation paths.

Main coverage was slow but actually completed. Its live session was resumed
without restarting the test process; CPU activity was verified during the
quiet interval. Intermediate polling-script termination did not stop the
underlying verified test session; the session was drained to exit 0. The old
failed-tree main interruption above is separate and not substituted for this
completed gate.

Fresh version/import-origin prefixes:
`qb-stage11pc3r1-observable-b-clean-versions-<environment>`, where environment
is main/alternate/sdkfree/jax012/tf. All five exit 0 and import QB from the
corrected export. Python 3.12.6 throughout; main NumPy 2.4.6, Qiskit 2.4.1,
Aer 0.17.2, PennyLane 0.44.1, JAX 0.7.1, TF 2.21, Torch 2.12, Autograd 1.8.
Alternate Qiskit 2.6, PennyLane 0.42.3, JAX 0.6.2, Autograd 1.9.1;
other listed versions match. Main/alternate have disclosed user/system imports,
not strict SDK-free isolation. SDK-free/JAX/TF use NumPy 2.5.4 and no quantum
SDKs; SDK-free lacks all four frameworks. JAX x64 was enabled; frozen gates
set OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1.

Pip prefixes: `qb-stage11pc3r1-observable-b-clean-pip-<environment>`.
SDK-free/JAX/TF exit 0. Main/alternate exit 1 for unchanged conflicts:
pyquafu 0.4.5 requires NumPy <2 (installed 2.4.6); WeasyPrint 68.1 requires
tinycss2 >=1.5 (installed 1.4). No dependency/environment change hides these.

The complete 28-section local matrix has NOT been rerun on this tree. Its
receipt remains required for final R1 acceptance, together with closure of
known remaining native allocation sites. Prior tree matrix results are not
new-source evidence. No local commit/push or exact-SHA remote CI is claimed;
HEAD remains 71f211d. R1/C3 and full independent SDK parity remain PARTIAL.

## Current Task 3B Snapshot And Shot Progress

This source is newer than the scoped MPS foundation tree below. Task 3B,
R1/C3 and full native Qiskit/PennyLane replacement remain PARTIAL. The authorized
ChatGPT coordination reply continued native snapshot ownership and partial-shot
failure work based on our report, not an independent source audit or acceptance.

Two actual initial snapshot reds are retained at
`/tmp/qb-stage11pc3r1-snapshot-initial-red.log/.exit`: no labeled native MPS
extraction existed; pershot saves retained serialized Python data but zero
native tensor storage. This is an API gap and a native ownership gap, not
evidence that old serialized dicts were dangling ndarray views.

Live SaveMPS/SaveState now stores a genuine defensive MPS copy in the existing
SnapshotContext. All tensor-copy reservations are acquired before the first
array allocation. Each new root retains its own lease. Transport/group limits
are checked before copying; context cells/groups/bytes commit only a successful
save. Repeated raw saves replace their old owner; pershot saves keep distinct
copies. Context to ExecutionRecords/Result is a reference transfer, not a
second array allocation or charge. Backend/Job delegate the same native engine.

`Result.matrix_product_state(label)` extends the existing final-state accessor
with labeled native copies and matching conditional/pershot nesting. User tensor
views keep real roots alive after Device/Job/Result destruction. Existing
`Result.data()` and JSON still return their serialized dict/list structure;
repeated MPS data access allocates no native tensors. JSON round trips preserve
complex data but do not reconstruct native snapshot-map ownership: asking a
JSON-loaded Result for that native label explicitly raises KeyError. General
JSON/decode/import scratch and Python heap are not claimed controlled.
`snapshot_native_tensor_bytes` observes distinct currently retained roots;
the historical `snapshot_storage_bytes` is peak encoded transport bytes, not
Python heap, total retained process memory or RSS.

Actual intermediate snapshot gates: first fix 111 passed; expanded focus
190 passed/one test failure, then 191 passed after correcting that fixture to
use if_test's returned Circuit (its default is not inplace). No native physics
or tolerance changed to hide that test error. Prefixes respectively
`qb-stage11pc3r1-snapshot-first-fix`, `...-snapshot-lifetime-focus` and
`...-snapshot-lifetime-corrected`, each under `/tmp/` with `.log/.exit`.

Two further genuine reds at
`/tmp/qb-stage11pc3r1-mps-partial-shots-initial-red.log/.exit` show two completed
MPS measurements/dynamic trajectories wrongly reported zero after the third
fails. Explicit completion boundaries now consume one reserved shot after its
complete sample. Existing whole-buffer meters consume only the remainder;
nested Device/dynamic Result meters share the ticket without charging twice.
Signature binding handles sample(wires, shots), run_shots(circuit, shots) and
engine.shots(shots) using their real argument contracts. Failed trajectories
mark additional internal partial work unavailable, never fabricated zero or N.
Runtime/resource/numerical Kraus errors preserve known completed work; ordinary
status classification and traceback detachment remain the existing mechanisms.

The first shot-fix gate passed 168 tests. Expanded tests cover noisy recovery,
direct shot-cap rejection before state allocation, postprocessing after all
shots and nested-meter conservation. This is scoped progress, not final full
pytest/coverage/matrix evidence. General observable/IR/validation scratch,
remaining specified failure cases, serialization budgets and final gates remain
open. Snapshot derivative requests stay Unsupported; snapshot saves and native
100-wire HVP are tested separately, not an invented supported combined path.
No commit/push, current-SHA remote CI, Studio, cloud/hardware/token/vendor,
tag/release or authentication/TLS/history changes are claimed.

### Frozen Task 3B Intermediate Evidence

Tree: `acce8ac02689cf9cd1c0792fbf75f27238129a7b`.
Production subtree: `f4f341d5e5a5f64078087c2dce1fa6b55599ddf9`.
Export: `/tmp/qb-stage11pc3r1-snapshot-validate.aiOqyt/source`.
The separate index contains HEAD plus 59 explicitly owned paths; actual index
remains unstaged. Export and working production/tests/examples compare equal
after all gates. Later report edits do not change tested runtime/tests.

Each prefix below is under `/tmp/` with a complete `.log` and independent
`.exit`. All these gates exit 0. Broad means derivative execution/interfaces,
devices/circuit/Aer compatibility/providers; only main is a full project run.

| Gate | Actual result | Prefix |
| --- | --- | --- |
| SDK-free broad | 511 passed, 245 optional skips, 1 warning; 10.81s | `qb-stage11pc3r1-snapshot-clean-sdkfree` |
| Main installed FULL | 2520 passed, 5 skipped, 3 declared public-oracle xfails, 57 warnings; 342.54s | `qb-stage11pc3r1-snapshot-clean-main-full` |
| Alternate installed broad | 803 passed, 1 skip, 2 declared public-oracle xfails, 2 warnings; 68.56s | `qb-stage11pc3r1-snapshot-clean-alternate` |
| Independent JAX 0.12, derivative/interfaces | 340 passed, 150 missing-framework skips; 21.11s | `qb-stage11pc3r1-snapshot-clean-jax012` |
| Independent TF 2.21, derivative/interfaces | 369 passed, 126 missing-framework skips; 26.92s | `qb-stage11pc3r1-snapshot-clean-tf` |
| Compileall | exit 0 | `qb-stage11pc3r1-snapshot-clean-compile` |
| Legal/source ledger | 5 passed; 0.13s | `qb-stage11pc3r1-snapshot-clean-legal` |
| Privacy/security | 32 passed; 0.30s | `qb-stage11pc3r1-snapshot-clean-privacy` |

Main full warnings include declared scaffold notices, SDK deprecations,
SciPy/PySCF notices and existing QNode/template warnings. Warnings, dependency
skips and public-oracle xfails are not counted as native function parity.
Four-framework, H2 and 100-wire regressions are included in main full/broad;
their successes are not a new claim of supported snapshot derivatives.

Fresh version/import-origin receipts use
`qb-stage11pc3r1-snapshot-clean-versions-<environment>` for main, alternate,
sdkfree, jax012 and tf. All five exit 0 and import QB from the frozen export.
Runtime versions/import caveats match the foundation table below. JAX x64 and
OPENBLAS_NUM_THREADS=1/OMP_NUM_THREADS=1 were set for these frozen gates.
Fresh pip receipts use `qb-stage11pc3r1-snapshot-clean-pip-<environment>`:
SDK-free/JAX/TF exit 0. Main/alternate exit 1 for unchanged pyquafu 0.4.5
versus NumPy 2.4.6 and WeasyPrint 68.1 versus tinycss2 1.4 conflicts; no
environment change hides these. User/system imports remain disclosed.

No fresh SDK-free/alternate FULL, full coverage or complete 28-section matrix
is claimed for this tree. They are required after remaining Task 3B allocation
closure, not replaced with the older tree's receipts. Filename-only common
credential/private-key scanning found no match in the 59 owned paths; path
inventory contains no vendor/site-packages/venv/wheel/metadata directory.
`git diff --check` passes; HEAD is unchanged and no push was attempted.

These results were actually sent to the authorized ChatGPT conversation and
its completed Task 3C prompt was read, including the code block's remaining
sections. It requests real observable-conversion/validation reds, then strided
JSON export/import allocation closure and final gates. Only initial source
inspection of those sites follows this checkpoint; no Task 3C red/fix or
completed final acceptance is claimed. The next-site audit is recorded in the
allocation audit. The goal remains active/incomplete.

## Current Task 3 Foundation

This working source is newer than the Task 1/2 frozen tree below. No older
full-suite, coverage or matrix receipt validates these MPS runtime changes.
Task 3, R1/C3 and full independent SDK functional replacement remain PARTIAL.

Two genuine pre-fix failures are retained in
`/tmp/qb-stage11pc3r1-mps-initial-red.log/.exit`: contraction ran although its
valid two-site intermediate exceeded remaining memory; SVD ran without space
for all U/S/Vh outputs alongside existing tensors/input. The fixtures explicitly
reserve their caller-owned inputs, not as newly allocated operation outputs.

`execution/mps_arrays.py` supplies allocation boundaries around the existing
NumPy QR/SVD/contraction algorithms, not another MPS simulator. Constructor and
tensor copies, reduced QR/SVD outputs, strided reshape copies, contractions,
Schmidt statistics/updates, normalization, conjugates, reduction environments
and dense returned outputs reserve before allocation. Individual root leases
keep a truncated U view's full real storage alive. Known packing is explicit;
hidden linalg/BLAS/iterator workspace remains unavailable, not zero or RSS.

A weak root/account index holds no strong ndarray, ledger, state or graph.
Defensive MPS Result/tensor copies outside callbacks can use the actual source
account. Mutable tensors from outside an active account are copied into it
before modification, not silently declared already owned. No global mutable
execution budget is introduced; weak index/account collection is tested.

Public gate failures restore tensors, center and truncation metadata; split
commits only complete updates. A second-SWAP failure/retry test preserves input
and permits a later valid call. Concurrent requests independently copy one
source, retain only their outputs and leave that source unchanged. Native
Result exports keep leases after Device/Result deletion; this does not certify
serialized snapshots.

Actual common MPS execution no longer holds the old `12*stored` tensor allowance
on top of explicit native roots. Full conservative admission estimates remain;
execution keeps the old external-only `128*(2*estimated_max_bond)**2` allowance.
It is a conservative policy, not a proof of LAPACK process-memory peaks.
Non-MPS workspace policy is unchanged. Kraus products, trajectory/dynamic choice
probabilities, global-phase matrices, ensemble density accumulation and dense
moment products use controlled buffers. Native physics and RNG order remain.

Actual intermediate receipts under `/tmp`, all with independent exits:

- `qb-stage11pc3r1-mps-first-fix`: 33 passed.
- `qb-stage11pc3r1-mps-reductions`: 37 passed.
- `qb-stage11pc3r1-mps-ownership-focus`: 58 passed, one new lifecycle failure
  because outside-scope mutable inputs were not adopted. Adoption/weak metadata
  fixed that actual boundary; the all-live-root assertion was not weakened.
- `qb-stage11pc3r1-mps-adoption-focus`: 59 passed.
- `qb-stage11pc3r1-mps-common-broad`: exit 4, wrong directory, no tests;
  corrected `qb-stage11pc3r1-mps-common-broad-corrected`: 629 passed/one skip.
- `qb-stage11pc3r1-mps-runtime-ownership`: 181 passed, including native
  Result/view, concurrency, weak-index lifetime and Kraus cap tests.
- `qb-stage11pc3r1-mps-foundation-broad`: 781 passed/one conditional skip;
  60.51s; exit 0, before final ensemble/global-phase/dense-moment edits.

### Frozen MPS Foundation Evidence

Tree: `905b1a16b37c01878db20e8ad043ce04a4623e5f`.
Production subtree: `fad9431eb8cf554345e66f575e894ad8c9a4b246`.
Export: `/tmp/qb-stage11pc3r1-mps-foundation-validate.PgbCTC/source`.
The separate validation index contains HEAD plus 54 explicitly owned paths;
the actual index remains unstaged and excludes user Studio/Router changes.
Export and working production/tests/examples compare equal to this tree after
these gates. Reports may subsequently change without changing tested runtime.

These are scoped regression gates, NOT full project suites. The broad scope is
derivative execution, interfaces, devices, circuit and Qiskit Aer compatibility;
independent framework runs cover derivative execution and interfaces only.
Each prefix is under `/tmp/` with complete `.log` and independent `.exit`.

| Gate | Actual result | Prefix |
| --- | --- | --- |
| SDK-free broad | 487 passed, 245 missing-optional skips, 1 existing warning; 9.93s; exit 0 | `qb-stage11pc3r1-mps-clean-sdkfree` |
| Main installed broad | 781 passed, 1 conditional skip, 2 existing warnings; 61.18s; exit 0 | `qb-stage11pc3r1-mps-clean-main` |
| Alternate installed broad | 779 passed, 1 skip, 2 declared public-oracle xfails, 2 existing warnings; 60.48s; exit 0 | `qb-stage11pc3r1-mps-clean-alternate` |
| Independent JAX 0.12 | 322 passed, 150 missing-framework skips; 18.23s; exit 0 | `qb-stage11pc3r1-mps-clean-jax012` |
| Independent TF 2.21 | 351 passed, 126 missing-framework skips; 22.68s; exit 0 | `qb-stage11pc3r1-mps-clean-tf` |
| Compileall | exit 0 | `qb-stage11pc3r1-mps-clean-compile` |
| Legal/source ledger | 5 passed; exit 0 | `qb-stage11pc3r1-mps-clean-legal` |
| Privacy/security | 32 passed; exit 0 | `qb-stage11pc3r1-mps-clean-privacy` |

Version/import-origin receipts use `qb-stage11pc3r1-mps-clean-versions-` plus
main/alternate/sdkfree/jax012/tf. All exit 0 and import QuantumBridge from this
export. Python is 3.12.6; main NumPy 2.4.6, Qiskit 2.4.1, Aer 0.17.2,
PennyLane 0.44.1, JAX 0.7.1, TF 2.21, Torch 2.12, Autograd 1.8.
Alternate uses Qiskit 2.6, PennyLane 0.42.3, JAX 0.6.2, Autograd 1.9.1.
Main/alternate include disclosed user/system imports, not SDK-free isolation.
SDK-free and independent JAX/TF use NumPy 2.5.4 and lack quantum SDKs;
SDK-free also lacks all four frameworks. Independent JAX x64 was enabled.
Pip receipts use `qb-stage11pc3r1-mps-clean-pip-<environment>`: SDK-free/JAX/TF
exit 0; main/alternate exit 1 for unchanged pyquafu/NumPy and
WeasyPrint/tinycss2 conflicts. No dependency changes hide these conflicts.

No new full coverage or complete 28-section local matrix was run for this
foundation tree. Earlier full-suite and coverage evidence is historical only.

Still required: complete serialized/pershot/conditional snapshot and Job/context ownership,
all specified partial-shot/noise failures, conversion/validation scratch audit
and final R1 full coverage/matrix/three-environment gates. Ordinary graph-wide
and strict process RSS budgets are not newly supported. No Task 3 acceptance,
commit, push, remote CI, cloud/hardware/token or Studio work is claimed.

## Current Task 1 And Task 2 Development

Current uncommitted source is newer than the frozen persistent-storage tree
below. Its old full-suite/coverage receipts do not validate this new runtime.
R1/C3 and full independent Qiskit/PennyLane parity remain partial.

Persistent copying now audits opaque slots, dataclasses, custom reduction,
deepcopy/container protocols, mutable callable captures and Tensor/Variable
objects before dispatch. Unknown foreign protocols reject without execution.
Controlled native instance dictionaries and exact builtin/numeric data use an
alias memo; native constructors/copy hooks are not called. Verified immutable
captures can be borrowed. Function module globals and later callback allocation
are explicitly outside that snapshot: this is not a universal Python sandbox.

Ordinary TF uses public function-boundary/IdentityN gradient overrides with
payload-free global rules. Graphs own callback payloads; weak indexes do not
own graphs/kernels. Actual tests cover eager/persistent/nested tapes, compiled
and nested functions, retained ConcreteFunctions, changed inputs, gradients and
second derivatives, shared immutable kernels, concurrent calls and failed-cap
then valid reuse. Native quantum work still uses existing run/run_second/Device
algorithms. Static private per-callback limits are not a public graph-wide
budget; ordinary JAX/TF unified graph limits remain explicitly unsupported.
Ordinary TF preserves its existing status 0-4 contract, not the explicit
derivative query's distinct numerical-failure code 5.

Flattening now writes strided leaves directly to one pre-reserved float64
destination. Reconstruction first attempts a view-only shape change; a real
copy reserves before allocating. Last surviving roots/views retain leases.
The old additional three-payload framework flatten reservation is removed.
Packed directions use this path; ordinary native Jacobian mapping reserves
its classical map/output and explicit matmul workspace. Recursive root and
flatten visitors no longer keep arrays in otherwise unreachable closure cycles;
production does not force GC. Ordinary selected Jacobians already write to
pre-reserved columns; supported public argument layouts use basic slices. The
internal Device selection path now also distinguishes those views from an
independently owned reordered/repeated column result. Its copy reserves first;
unsupported index/mask protocols reject. Not all NumPy indexing is certified.

Actual new receipts under `/tmp`, each with `.log` and `.exit`:

- `qb-stage11pc3r1-foreign-protocol-initial-red`: nine pre-fix failures;
  `qb-stage11pc3r1-foreign-meta-slice-initial-red`: three more.
- `qb-stage11pc3r1-tf-ordinary-lifetime-corrected-red`: two real compiled-graph
  lifetime failures, two passing eager cases. The initial four-failure draft
  had two incorrect eager expectations; it is not evidence of four leaks.
- Direct PyFunc/IdentityN rules without the function boundary produced missing
  or zero gradients. A generic custom-gradient primitive had correct math but
  remained lifetime-red. Neither rejected prototype is the current code.
- `qb-stage11pc3r1-tf-task1-broad`: 437 passed, one conditional skip, exit 0.
- `qb-stage11pc3r1-tree-initial-red`: nine pre-fix failures;
  `qb-stage11pc3r1-tree-direction-host-red`: two more.
- `qb-stage11pc3r1-tree-first-fix`: ten lifetime regressions; after removing
  closure retention, `qb-stage11pc3r1-tree-lifetime-fix`: 446 passed/one skip.
- `qb-stage11pc3r1-tree-mapped-broad`: 447 passed/one skip, one changed lifetime
  expectation. Raising APIs retain debugging tracebacks and the owned tangent.
  Its test now checks those live bytes and conservation, then actual release
  after dropping the exception, not a false zero while a real owner survives.
- `qb-stage11pc3r1-task12-broad`: 450 passed, one conditional skip; 43.70s;
  exit 0. This remains a focused working-tree gate, not final R1 acceptance.
- `qb-stage11pc3r1-advanced-index-red`: two genuine pre-fix failures, proving an
  independent advanced-index root was uncharged and low caps did not reject.
- `qb-stage11pc3r1-tree-index-final-focus`: 452 passed, one skip; 47.70s; exit 0.
  Seven selection/legacy-shape cases were added subsequently;
  `qb-stage11pc3r1-tree-index-positive` then passes all 22 tree tests.

Intermediate export `37bc261adaed2b96b06913d2eff665befea302a2` passed SDK-free
full: 1845 passed, 395 skipped; 219.80s; exit 0. It exposed NumPy 2.5 shape
assignment deprecations. Current code uses public reshape(copy=False) on
NumPy >=2.1, retaining a shape-only legacy branch for older versions. That
fallback is unit-tested, not a claimed real NumPy 1.x environment run.
Subsequent fixes/indexing work require a newer frozen export for final source
validation; the intermediate SDK-free result is not substituted for it.

### New Frozen Task 1/2 Source Evidence

Tree: `9d6bd5c083a6bc706419e093c9112955c51cda76`.
Production subtree: `53e2111a77aa7d3c31bcdf6482f41116a7e13a81`.
Export: `/tmp/qb-stage11pc3r1-task12b-validate.OB2Ibb/source`.
Separate index: 48 explicitly owned paths plus committed HEAD. The actual Git
index is unstaged; user Studio/Router edits were not included or edited.
After all gates, export and working production/tests/examples both compare
equal to this tree. Subsequent edits update reports only, not tested runtime.

Every prefix below is under `/tmp/` with complete `.log` and independent `.exit`.

| Gate | Actual result | Prefix |
| --- | --- | --- |
| SDK-free full | 1854 passed, 395 optional skips; 224.74s; exit 0 | `qb-stage11pc3r1-task12b-clean-sdkfree` |
| Main installed full | 2472 passed, 5 skipped, 3 existing public oracle xfails; 316.79s; exit 0 | `qb-stage11pc3r1-task12b-clean-main` |
| Alternate installed full | 2470 passed, 5 skipped, 5 existing public oracle xfails; 314.32s; exit 0 | `qb-stage11pc3r1-task12b-clean-alternate` |
| Independent JAX 0.12, derivative/interfaces | 292 passed, 150 missing-framework skips; 15.92s; exit 0 | `qb-stage11pc3r1-task12b-clean-jax012` |
| Independent TF, derivative/interfaces | 321 passed, 126 missing-framework skips; 19.61s; exit 0 | `qb-stage11pc3r1-task12b-clean-tf` |
| Four-framework derivative/interfaces | 459 passed, 1 conditional skip; 46.88s; exit 0 | `qb-stage11pc3r1-task12b-clean-frameworks` |
| Compileall | exit 0 | `qb-stage11pc3r1-task12b-clean-compile` |
| Legal | 4 passed; exit 0 | `qb-stage11pc3r1-task12b-clean-legal` |
| Privacy/security | 32 passed; exit 0 | `qb-stage11pc3r1-task12b-clean-privacy` |

NumPy 2.5's shape-assignment deprecation no longer appears in the new SDK-free
full log (five unrelated existing warnings remain). Public oracle xfails and
dependency skips are not counted as numerical successes or implemented parity.

Version/import-origin prefixes are `qb-stage11pc3r1-task12b-clean-versions-`
plus main/alternate/sdkfree/jax012/tf. All five exit 0 and import QB from the
export. Python is 3.12.6. Main: NumPy 2.4.6, Qiskit 2.4.1, Aer 0.17.2,
PennyLane 0.44.1, JAX 0.7.1, TF 2.21, Torch 2.12, Autograd 1.8.
Alternate: Qiskit 2.6, PennyLane 0.42.3, JAX 0.6.2, Autograd 1.9.1;
otherwise the same listed versions. Main/alternate have disclosed user/system
imports, not SDK-free isolation. SDK-free and independent JAX/TF use NumPy
2.5.4 with no quantum SDKs; SDK-free also lacks all four frameworks. JAX x64
was enabled. Independent JAX is 0.12, independent TF is 2.21.

Pip prefixes use `qb-stage11pc3r1-task12b-clean-pip-<environment>`.
SDK-free/JAX/TF exit 0. Main/alternate exit 1 with the same existing conflicts:
pyquafu 0.4.5 needs NumPy <2 but has 2.4.6; WeasyPrint 68.1 needs tinycss2
>=1.5 but has 1.4. No environments/dependencies were changed to hide these.

This is intermediate Task 1/2 evidence, not final R1 acceptance. New true full
coverage and the complete 28-section matrix have not been rerun for this tree;
the older 89.98831320607714% and matrix receipts below are baseline only.
Final gates must follow the remaining MPS QR/SVD/contraction site work. Existing
aggregate reservations and unavailable LAPACK peaks are not complete
per-allocation/RSS bounds. No commit, push, current-SHA remote CI, Studio,
cloud/hardware/credential/vendor/tag/release work is claimed. HEAD remains
`71f211dc2c106fdb675603d112c80dc2c334423e`; R1/C3 and full parity remain open.

The complete execution report was actually sent to the authorized ChatGPT
conversation, and the completed Task 3 reply (sections 0-15 plus final decision)
was read through the normal UI. This is report-based coordination, not an
independent source audit. It continues native MPS contraction/QR/SVD ownership
with two real initial failure tests, then physical/numerical regressions and
fresh final R1 gates. An initial source inventory is now recorded in the
allocation audit; no MPS runtime fix or Task 3 red test is claimed yet.

## Previously Frozen Persistent Storage Slice

Current uncommitted progress adds an explicit, optionally caller-shared
PersistentStoragePool. It uses the existing resource ledger/array ownership
machinery rather than a second quantum engine. Known copied numeric ndarray
roots reserve before copying, become readonly, and release only after their
last real owner/view dies. Tested foreign plain-object custom copy protocols
and ndarray subclasses are rejected; arbitrary container/closure/reduction
protocols are not certified by this slice. The construction cap is separate from
execution request limits; tracing does not install an implicit ResourceScope or perform
quantum execution. A lightweight source description replaces repeated kernel
construction while differentiating the classical parameter map.

Resident admission precedes native Device work. It counts each root once per
request, shares ancestor caps, and releases on every exit without freeing the
persistent storage or refunding cumulative work/shots. Independent simultaneous
requests charge the same immutable physical root separately; they do not claim
two physical allocations. New-allocation receipt fields describe reservations,
not exact RSS/BLAS/framework memory observations.

Real evidence retained under /tmp (each with .log and .exit):

- `qb-stage11pc3r1-persistent-initial-red`: two mutable snapshot-alias failures.
- `qb-stage11pc3r1-persistent-public-initial-red`: two repeated-snapshot failures;
  actual JAX/TF public HVP tracing made four/two snapshots.
- `qb-stage11pc3r1-persistent-public-first-fix` and
  `qb-stage11pc3r1-persistent-public-weak-identity`: public TF final-release
  remained red, despite correct values and one snapshot. These are not hidden.
- `qb-stage11pc3r1-persistent-pool-focus`: 44 passed, including allocation-before-
  copy rejection, aliases/views, partial failure/recovery, pool sharing,
  parent caps, no-refund work and concurrent admission.
- `qb-stage11pc3r1-persistent-broad-focus`: 408 passed, one absent optional test
  skipped, before the last three public lifetime/status tests were added.
- `qb-stage11pc3r1-persistent-public-final-focus`: 46 passed. Actual compiled
  low-cap failures return status 3 plus NaN without second-derivative execution;
  valid same-kernel retries have correct changed-input HVPs, shared owners and
  no repeated pool copies. A TF ConcreteFunction remains usable after its
  polymorphic function dies; final owner deletion releases the pool. Concurrent
  native HVP requests charge 128 resident bytes for one physical 64-byte root.

TensorFlow uses public callback/graph/gradient registration APIs. The status
rejection rule contains no per-request output tensors or kernel; callback
registry invocation holds a weak reference and a weak graph-identity table
retains its payload. This is verified for the stated explicit status-query
graphs, not all ordinary TF gradients or complete graph-wide budgets.

### Clean Frozen-Tree Evidence

Tested tree: `10d077e8490050c26a1eaaefddfacad70a977abc`.
Production subtree: `402fe1df4def2406fac1449198d35611dc450bbf`.
Export: `/tmp/qb-stage11pc3r1-persistent-validate.TusCsH/source`.
The separate index contains 42 explicitly owned paths plus committed HEAD;
the real index was not staged. User Studio/Router dirt is absent from the
export. After all gates, production/tests/examples in both the export and
working source compare equal to the tested tree. Subsequent edits are reports
only. Older results below still apply only to their earlier exact trees.

All prefixes below have independent `.log` and `.exit` receipts in `/tmp`.

| Gate | Actual result | Prefix |
| --- | --- | --- |
| SDK-free full | 1816 passed, 385 optional skips; 226.93s; exit 0 | `qb-stage11pc3r1-persistent-clean-sdkfree` |
| Main installed full, matrix core | 2424 passed, 5 skipped, 3 existing public oracle xfails; 315.44s; exit 0 | `qb-stage11pc3r1-persistent-clean-matrix` |
| Main installed full, matrix dev | Same counts; 314.75s; exit 0 | same matrix log |
| True full coverage | Same counts; 867.01s; 25410/28237 statements = 89.98831320607714%; same 68 exclusions | same matrix log; `qb-stage11pc3r1-persistent-full-coverage.json` |
| Complete local matrix | All 28 section headings reached; actual shell exit 0 | same matrix log/exit |
| Alternate installed full | 2422 passed, 5 skipped, 5 existing public oracle xfails; 314.43s; exit 0 | `qb-stage11pc3r1-persistent-clean-alternate` |
| Independent JAX 0.12, derivative/interfaces | 254 passed, 140 missing-framework skips; 15.72s; exit 0 | `qb-stage11pc3r1-persistent-clean-jax012` |
| Independent TF, derivative/interfaces | 273 passed, 126 missing-framework skips; 17.82s; exit 0 | `qb-stage11pc3r1-persistent-clean-tf` |
| Interfaces plus retained-graph/ordinary budget focus | 207 passed, 1 missing-installation-contract skip; 23.91s; exit 0 | `qb-stage11pc3r1-persistent-clean-interfaces-retained-graph` |
| Compileall | exit 0 | `qb-stage11pc3r1-persistent-clean-compile` |
| Legal | 4 passed; exit 0 | `qb-stage11pc3r1-persistent-clean-legal` |
| Privacy/security | 32 passed; exit 0 | `qb-stage11pc3r1-persistent-clean-privacy` |

Coverage increased from the prior 89.86520579542997% baseline with no new
exclusions. It is line coverage, not a percentage of implemented SDK functions.
Matrix Finance, Optimization, ML, Dynamics, Metal, Experiments and Addons
installed-only subsets were explicitly not executed because dependencies were
absent. Passing offline compatibility tests, Runtime discovery or Quafu/QOS
adapters is not real hardware/service evidence or production/full parity.
No hardware, cloud account or credential was used.

Five runtime version/import-origin receipts use
`qb-stage11pc3r1-persistent-clean-versions-{main,alternate,sdkfree,jax012,tf}`.
All import QuantumBridge from the export. Main: NumPy 2.4.6, Qiskit 2.4.1,
Aer 0.17.2, PennyLane 0.44.1, JAX 0.7.1, TF 2.21.0, Torch 2.12.0,
Autograd 1.8.0. Alternate: Qiskit 2.6.0, PennyLane 0.42.3, JAX 0.6.2,
Autograd 1.9.1. These mixed environments intentionally include reported
user/system-site imports; they are not called SDK-free. The SDK-free and
independent framework environments use NumPy 2.5.4 and have no quantum SDKs;
the former also has none of the four frameworks. JAX gates enable x64.

Pip receipts use `qb-stage11pc3r1-persistent-clean-pip-<environment>`.
SDK-free/JAX/TF isolated checks exit 0. Main/alternate both exit 1 with the
same pre-existing conflicts: pyquafu 0.4.5 requires NumPy <2 but has 2.4.6,
and WeasyPrint 68.1 requires tinycss2 >=1.5 but has 1.4.0. No package or
environment changes were made to conceal those failures.

`git diff --check` passed. The owned-path artifact check finds no environment,
wheel, egg/dist-info, bytecode or vendored-package paths. A filename-only
common credential/private-key pattern scan finds no matches (rg exit 1 is its
documented no-match result); this limited check is not universal secret
detection. No source/test ports or token content are added.

### Review And Next Priority

The complete authorized ChatGPT follow-up, including the 466-item prompt,
was read through the normal UI. It keeps R1/C3 PARTIAL and prioritizes these
gates, then ordinary TF eager/compiled/nested/persistent GradientTape ownership,
followed by noncontiguous flatten/indexing and MPS workspace. Public status-query
lifetime evidence must not be generalized to ordinary gradient graph lifetime.
Foreign closures, custom container/reduction protocols and slotted foreign
configuration are explicit further audit boundaries, not zero-byte storage.

Full final R1 acceptance, all ordinary graph lifetimes, universal scratch/MPS/
foreign configuration ownership and the full independent Qiskit/PennyLane goal
remain incomplete. No R1 commit, remote push or exact-SHA remote CI is claimed.

## Earlier Slice History

The sections below preserve earlier observations and then-open requirements.
Their pending/implemented statements apply to those earlier snapshots, not to
the latest frozen-tree evidence at the top of this report.

Date: 2026-10-21. Baseline: `71f211dc2c106fdb675603d112c80dc2c334423e`.
Status: IN_PROGRESS / PARTIAL, uncommitted development. This is not completed
C3-R1, completed C3 or full independent Qiskit/PennyLane parity.

## Scope Implemented

Existing native quantum plans and differentiation algorithms are unchanged in
purpose. This slice corrects allocation ordering and lifetime ownership around
them; it is not a second GradientEngine or an upstream quantum SDK fallback.

- Mapped first/second source matrices, packed directions, native recorder maps
  and points reserve shape/dtype-derived bytes before allocating. Second-map
  contractions use explicit bounded row/column workspace, not an einsum
  optimizer's unproved intermediate-memory assumption.
- First-order native seed identity storage reserves once before allocation;
  its row views share that lease rather than pretending to be fresh copies.
- Ordinary Torch/Autograd fixed snapshots, unpack copies, dtype conversions,
  selected Jacobians/source maps and VJP/HVP outputs acquire native storage
  leases. Views share a root lifetime, real copies reserve separately.
- Existing conservative Device result leases can remain attached to native
  result roots until the last root/view dies. Explicitly owned source maps are
  not charged again in those result leases. Torch copies boundary outputs into
  framework storage; framework tensors/graphs are not included in native bytes.
- Generic Torch classes and Autograd primitive rules register once, with
  invocation ownership held by the actual graph rather than a registration
  closure. Weak-reference tests verify real release, including failed second
  backward, retained graphs and repeated pullbacks.
- MPS initial bond estimation no longer calls a property that copies tensors.

## Observed Tests

Initial red and subsequent focused gate receipts are in the
[allocation audit](stage11p_c3_r1_allocation_audit.md). Every named prefix has
both a complete `.log` and independent `.exit` under `/tmp`.

Before the last small estimator/guard changes, the interface/Device focus
passed 373 tests with one conditional missing-installation contract skip.
The later allocation/lifetime focus passed 67 tests. Three initial graph
failures and two corrected genuine initial allocation failures were actually
observed before their corresponding production fixes.

Intermediate clean-tree results are recorded below. Final R1 full gates must
be repeated after the remaining ownership changes; an intermediate green
snapshot is not accepted complete R1.
The prior C3 full coverage of 89.86520579542997% with 68 exclusions is a
baseline, not a new R1 measurement.

## Intermediate Clean-Tree Receipts

Tested Git tree: `71f72ce03998d0baa356a1cd9b07f6fdfa33669c`.
Production subtree: `f981be3333cf8762c890b892d1408093bb1eba05`.
Export: `/tmp/qb-stage11pc3r1-validate.fcy3Pg`.
All 16 owned Python source/test files subsequently match that tree by Git blob
hash. Report updates after the run only add evidence; there is no new commit.
The export was produced from HEAD plus the 22 explicitly owned R1 paths using
a separate temporary Git index. The user's real index and unrelated files were
not staged or exported as new work.

Each prefix below has a full `.log` and independent `.exit` in `/tmp`.

| Gate | Actual result | Prefix |
| --- | --- | --- |
| Main full suite | 2389 passed, 5 skipped, 3 existing public xfailed, 296.06 s, exit 0 | `qb-stage11pc3r1-clean-main` |
| SDK-free full suite | 1789 passed, 377 absent-dependency/conditional skips, 227.61 s, exit 0 | `qb-stage11pc3r1-clean-sdkfree` |
| Alternate, all derivative/interface tests | 374 passed, 1 conditional skip, 2 existing public xfailed, 38.07 s, exit 0; not alternate full | `qb-stage11pc3r1-clean-alternate-focus` |
| Independent JAX 0.12, all derivative/interface tests | 223 passed, 136 absent-framework/conditional skips, x64 enabled, 18.28 s, exit 0 | `qb-stage11pc3r1-clean-jax012` |
| Independent TensorFlow, same directories | 242 passed, 122 absent-framework/conditional skips, 15.74 s, exit 0 | `qb-stage11pc3r1-clean-tf` |
| Compileall | exit 0 | `qb-stage11pc3r1-clean-compile` |
| Legal | 4 passed, exit 0 | `qb-stage11pc3r1-clean-legal` |
| Explicit no-cloud/no-token file focus | 17 passed, exit 0 | `qb-stage11pc3r1-clean-privacy` |

Version and import-origin receipts are `qb-stage11pc3r1-versions-<environment>`.
All use Python 3.12.6 and import the exported source, not an editable copy of the
dirty working tree. Main: NumPy 2.4.6, Qiskit 2.4.1/Aer 0.17.2, PennyLane
0.44.1, JAX 0.7.1, Torch 2.12.0, Autograd 1.8.0, TensorFlow 2.21.0.
Alternate: Qiskit 2.6.0, PennyLane 0.42.3, JAX 0.6.2, Autograd 1.9.1;
other versions match main. SDK-free has NumPy 2.5.4 with neither quantum SDK
nor the four optional differentiation frameworks. Independent JAX/TF also use
NumPy 2.5.4; JAX is 0.12.0 and TensorFlow is 2.21.0 respectively.

Alternate full suite, new true full coverage and the complete 28-section matrix
have not been run on this R1 snapshot. They remain mandatory final gates after
the outstanding runtime work. Earlier C3 counts are not substituted for them.

## Authorized Review Follow-Up

The intermediate results and open gaps were actually sent to the existing
authorized ChatGPT conversation. Its complete reply, including the internally
scrolling code-block tail, was read. It keeps R1/C3 PARTIAL and prioritizes:

1. Persistent source/kernel/selection-map storage identity and shared owners;
   prove a real copy is denied before allocation, while dropping one plan
   cannot release a peer plan's still-live storage.
2. Public Device-to-Result ownership, not only the private ordinary-framework
   result transfer implemented here. Deleting device/plan must not release
   arrays or user-held views still reachable from a returned Result.
3. Actual initial red contracts for noncontiguous flatten and advanced-index
   copies; then nested outputs, QWC covariance/metadata and validation scratch.
4. MPS original tensors, QR/SVD, two-site/SWAP contractions, trajectories and
   snapshots, distinguishing controlled owned arrays from external workspace.
5. Freeze all remaining code, then rerun every full/independent/matrix/coverage
   gate before scoped local commit or final R1 acceptance.

The pseudocode in that review is a contract illustration, not evidence that
new suggested API names already exist. At that intermediate snapshot the public
Device protocol still treated returned payload as caller-owned after callback
return. The follow-up slice below changes that behavior; the earlier snapshot
is not evidence for the subsequent fix.

## Follow-Up: Public Result And Active-Scope Copies

The shared executor now always transfers its pre-acquired conservative result
buffer lease to returned native array roots. The private ordinary-framework-only
switch is removed. Public Jacobian/JVP/VJP/Hessian/HVP results and nested views
remain valid/charged after deleting device and source; retaining a result can
correctly prevent a second request from fitting the same parent budget. Work
does not decrease when the last result/view finally dies.

Actual initial public-result negatives: seven failed in
`/tmp/qb-stage11pc3r1-result-initial-red.log/.exit` before the public fix;
then seven passed. Earlier tests requiring zero in every success-return snapshot
were corrected to check live storage and actual release through the same
captured ledger. Numerical/H2/100-wire/QWC/shots assertions remain in place.
The derivative directory then passed 196 tests before the subsequent copy work.

`Tape.copy` and host-device copies now share a native ndarray copy memo under
an active ResourceScope. Known array copies acquire storage leases before the
copy; repeated references to one source object get one destination. Distinct
ndarray view objects receive distinct destination copies, matching deepcopy's
actual behavior rather than deduplicating merely by input addresses. Graph
scalars already preserved by Tape's existing memo remain preserved. Array
subclass copy behavior is kept; extra custom workspace is explicitly unknown.

Three real source/device-copy initial failures were recorded in
`qb-stage11pc3r1-configuration-initial-red`. Another real failure showed a status
Result retaining a partially copied configuration through its exception frames
(`qb-stage11pc3r1-failed-result-initial-red-corrected`). A preceding draft had
misplaced unrelated recovery lines; those were restored before the corrected
pre-fix run. Returned status errors now detach traceback/cause/context chains;
the raising/debugging API retains ordinary tracebacks. The failure Result stays
alive during a GC-based release test. Unreachable cyclic garbage can stay
charged until actually collected; no global forced collection or fictitious
early zero is introduced. Receipts remain historical snapshots.

These fixes do not finish persistent source ownership: kernel construction
outside an active ResourceScope still uses the existing unmanaged copy path.
Foreign object/custom copy internals, all metadata scratch, MPS internals and
ordinary JAX/TF whole-graph budgeting remain open. The new broader regression
passed 867 tests, one conditional skip, exit 0, in 271.54 s
(`qb-stage11pc3r1-copy-regression`), before a final observation fix. That fix
was driven by three actual red cases where the retained raw Jacobian/second
arrays exceeded the old observed public-payload bytes. Observation now counts
the same deduplicated ndarray roots as retention. Its final result/copy/failure
focus passed 35 tests (`qb-stage11pc3r1-result-copy-final-focus`, exit 0).
Earlier clean-tree full results above do not validate this new runtime snapshot.
No new commit/push or final R1 acceptance is claimed.

### Follow-Up Frozen Snapshot

This second intermediate slice is tested separately from the earlier one:
Git tree `c57a5e098f620876149705a91294ffc74db870ca`, production subtree
`86f2614883d87e906ba53acb3029fa10c69a7ce1`, exported at
`/tmp/qb-stage11pc3r1-result-validate.YbUo2S` from 32 explicitly owned paths.
Main full: **2403 passed, 5 skipped, 3 existing public xfailed**, 308.29 s,
exit 0 (`/tmp/qb-stage11pc3r1-result-clean-main.log/.exit`). Fresh additional
receipts on the same snapshot are below. No source/test changes are inferred
validated from a previous snapshot. All 26 owned Python files were subsequently
compared by Git blob hash and match this frozen tree; only reports gained
post-run evidence. The real working index remains untouched.

| Gate | Actual result | Prefix under `/tmp/` |
| --- | --- | --- |
| SDK-free full | 1803 passed, 377 absent-dependency/conditional skips, 227.30 s, exit 0 | `qb-stage11pc3r1-result-clean-sdkfree` |
| Independent JAX 0.12, derivative/interfaces | 237 passed, 136 absent-framework/conditional skips, x64 enabled, 18.69 s, exit 0 | `qb-stage11pc3r1-result-clean-jax012` |
| Independent TF, derivative/interfaces | 256 passed, 122 absent-framework/conditional skips, 16.47 s, exit 0 | `qb-stage11pc3r1-result-clean-tf` |
| Alternate derivative/interfaces only | 388 passed, 1 conditional skip, 2 existing public xfailed, 38.56 s, exit 0 | `qb-stage11pc3r1-result-clean-alternate-focus` |
| Compileall | exit 0 | `qb-stage11pc3r1-result-clean-compile` |
| Legal | 4 passed, exit 0 | `qb-stage11pc3r1-result-clean-legal` |
| No-cloud/no-token file focus | 17 passed, exit 0 | `qb-stage11pc3r1-result-clean-privacy` |

Each prefix has a complete log and independent exit receipt. Versions and
exported import origins are `qb-stage11pc3r1-result-versions-<environment>`;
versions match the environment table above. Isolated pip checks
(`qb-stage11pc3r1-result-pip-<environment>`) pass in SDK-free/independent JAX/TF,
but main/alternate still exit 1 for their pre-existing pyquafu 0.4.5 NumPy<2
constraint against 2.4.6 and WeasyPrint 68.1 tinycss2>=1.5 requirement against
1.4.0. No dependency environment was modified to hide these conflicts.
Alternate full, new true full coverage and full 28-section matrix remain
pending final runtime completion, not replaced by these focuses or older gates.

### Persistent Kernel Follow-Up Contract

The next authorized ChatGPT reply was completely read, including all ten tasks
in its 370-item scrolling code block. It recommends a separate immutable
persistent storage owner/pool and per-callback resident admission leases:

- Kernel construction can occur outside request ResourceScope without quantum
  Device work. Its actual copied roots require a separate persistent allocation
  policy; failing to implement that policy must remain explicitly incomplete.
- Request limits apply at actual callbacks, not during JAX/TF tracing. Charge
  resident roots once per request before Device execution, release admission
  leases on all exits, but do not free the persistent physical storage.
- Report persistent-owned bytes, request resident charges and newly allocated
  bytes separately. Two requests charging one kernel do not allocate two kernels
  or establish a process RSS bound. No global implicit tracing ResourceScope.
- Use actual JAX JIT/TF graph red-green tests for trace success, runtime status 3
  without Device work, valid retry with correct derivatives, no stale input or
  repeated deep copy. Current limits are static: use distinct static compiled
  configurations rather than inventing a mutable runtime-limits API.
- Verify two compiled callable owners, dropping one owner/kernel variable,
  surviving views, eventual final release, no double release and no reliance
  on prompt GC as a correctness mechanism. Test nested/shared-parent/concurrent
  requests; explicitly reject unsupported concurrency rather than hide it.
- Preserve the existing Result/graph/shift-free second-adjoint/64-shared/HVP/
  QWC/partial-shot/100-wire/H2 regressions, audit Circuit copies and scratch,
  then freeze and rerun all final full/matrix/coverage/pip/legal gates.

At that earlier snapshot this was an agreed next contract, not an implemented
or verified persistent pool. The latest slice above adds the scoped pool.
The full independent Qiskit/PennyLane goal and C3-R1 remain incomplete.

## Memory Contract And Remaining Work

Counts refer to owned native numerical storage, not process RSS. Conservative
result/workspace reservations may exceed actual live buffer bytes, but they
are not observed BLAS/LAPACK/framework allocator peaks. Receipts are snapshots:
a callback-end snapshot may correctly show retained graph or result storage.
Actual release tests inspect the same live ledger after real references die.
Consumed derivative work and completed physical shots remain cumulative.

Remaining R1/C3 gaps include generalized foreign kernel/source/device storage,
universal validation/metadata/flatten scratch accounting, a complete MPS
allocation-by-allocation proof, unobservable allocator/failed-sampler work,
and ordinary JAX/TF graph-wide resource ownership. Those ordinary unified
graph options remain explicitly unsupported; supported per-query status APIs
do not imply a cross-callback/JIT account. No fabricated callback counts or
global mutable compiled ledger is added.

HVP still uses existing directional maps, not a hidden full quantum Hessian.
The 100-wire MPS example does not establish arbitrary entanglement efficiency;
fixed-geometry H2 ansatz differentiation is not differentiable SCF/geometry.
The much larger Qiskit/PennyLane API/ecosystem gaps remain those in the
[core ledger](../compat/core_parity_ledger.md); this slice does not close them.

## Repository And Remote

Only owned runtime/tests/documentation belong to this work. Existing unrelated
Studio/Router edits are preserved and excluded from validation exports. No
vendor/package/environment tree, credential, cloud/hardware call, tag or release
is added. No R1 commit is justified before its scoped acceptance gates.

Remote remains unpushed/unverified. The previous ordinary push was refused
because the existing OAuth authorization lacks workflow scope. No retry,
credential/auth/TLS change, workflow removal or bypass is attempted. A fresh
owner-authorized normal fetch, fast-forward ancestry check and ordinary push
are required before any remote success/CI claim.
