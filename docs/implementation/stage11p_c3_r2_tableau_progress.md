# C3-R2 Tableau And Dense Allowance Progress

Date: 2026-10-21. Status: bounded R2 test gates completed; C3 remains PARTIAL.
Committed baseline remains 89bd0f161dea5b653d2b61137265de4bb6ca4ce6.
Full independent Qiskit/PennyLane functional replacement is ACTIVE/INCOMPLETE.
P0/P1 changes and user Studio/Router files are preserved. No new simulator,
tableau hierarchy, quantum SDK execution engine or source/test port was added.

## Actual Native Changes

- Clifford bool storage, phase-column construction, identity, copy/deepcopy,
  dtype exports and generator conversions now use prior array admission.
  Borrowed tableau views retain existing roots; real copies have separate
  leases, including copies outside a scope with an actual source account.
- Symplectic validation reuses one owned bool vector instead of constructing
  unowned dense symplectic forms/products. GF(2) basis/solve/nullspace use owned
  matrices and direct row swaps/XOR destinations, not advanced-index copies.
- Existing compose/front/qargs, adjoint, conjugation, generator updates and
  synthesis operate on the tableau. The inverse is Clifford.adjoint, not an
  invented inverse method. Adjoint fills J M-transpose J directly and preserves
  signed Pauli phases; synthesis and equality avoid full temporary comparison
  matrices. Public Pauli x/z exports and managed symplectic conversion are
  admitted; boolean qubit indices/widths reject as invalid.
- The existing small-gate cache now stores bounded immutable Python action
  tuples rather than ndarray storage. Matrix recognition/conjugation uses the
  existing native Pauli/matrix primitives with admitted numerical workspace.
  No per-row code/image ndarray or integer casting buffers are created during
  gate application. The existing cache size limit of 128 is unchanged.
- Stabilizer generator completion, expectation, measurement, reset, probability
  arrays and categorical label outputs preserve the same mathematical rules.
  Known Unicode ndarray outputs receive separate real storage leases. Completed
  sampled trajectories remain spent even if later label formatting fails.
- Dense Clifford matrix expansion admits the complete destination before
  synthesis. The existing StabilizerState.to_statevector 100-qubit preflight
  was already correct and is retained as a regression, not a fabricated red.
- One additional concrete audit defect was fixed in the existing
  StatevectorDevice.density_matrix method: scoped pure and dynamic-ensemble
  outputs reuse the P0 DensityMatrix implementation and an admitted accumulator.
  Returned arrays and escaped views now own the actual matrix storage. The
  original coarse device guard and unmanaged numerical behavior remain.

Unmanaged matrix array protocols remain available; managed foreign factories
reject before dispatch. Pauli's unmanaged NumPy conversion behavior is retained.
Python labels, scalar/iterator/RNG internals, immutable cache objects and hidden
NumPy/BLAS/LAPACK workspace remain unavailable, not measured RSS. Native numeric
root accounting is not a universal custom-object/allocator contract.

## Red/Fix Chronology

Complete logs and independent exits are under each /tmp prefix below.

| Prefix | Actual result |
| --- | --- |
| qb-stage11pc3r2-tableau-initial-red | 31 failed / 6 passed; initial fixture subsequently corrected |
| qb-stage11pc3r2-tableau-corrected-red | 31 failed / 6 passed on unchanged runtime after correcting qargs oracle mapping and factory-spy entry; true budget/ownership/invalid-bool/early-expansion gaps |
| qb-stage11pc3r2-tableau-first-fix | 60 passed with existing Clifford/Stabilizer mathematics |
| qb-stage11pc3r2-tableau-expanded | invocation error: nonexistent tests/simulator directory; exit 4, no tests ran |
| qb-stage11pc3r2-tableau-expanded-recovery | 680 passed / 1 existing Aer warning, 19.73s, exit 0 |
| qb-stage11pc3r2-dense-return-initial-red | 4 failed; dynamic fixture initially used only terminal measurement, not a genuine mid-circuit measurement |
| qb-stage11pc3r2-dense-return-corrected-red | 4 genuine failures / 54 deselected, 0.08s; corrected mid-circuit fixture on an independent export with pre-fix Device source and current other sources |
| qb-stage11pc3r2-tableau-dense-recovery | 1 failed / 745 passed; terminal-measurement fixture mismatch, not changed physical semantics |
| qb-stage11pc3r2-tableau-final-focus | 2 failed / 753 passed; same fixture and a real managed native Pauli conversion whitelist gap |
| qb-stage11pc3r2-tableau-final-recovery | 755 passed / 2 existing warnings, 21.02s after corrected fixture and explicit native Pauli conversion |
| qb-stage11pc3r2-tableau-final-api | 148 passed, 2.69s including preserved unmanaged array-protocol behavior |
| qb-stage11pc3r2-tableau-empty-complex-red | 8 failed / 2 passed / 59 deselected; actual managed empty complex dtype regression, including ndarray subclasses |
| qb-stage11pc3r2-tableau-empty-complex-recovery | invocation error: nonexistent tests/quantum_info directory; exit 4, no tests ran |
| qb-stage11pc3r2-tableau-empty-complex-final-focus | 393 passed, 4.94s, exit 0 after dtype-based correction |

A separate hypothesis that nonpositive Clifford.power was a missing public API
was rejected by direct Qiskit 2.4.1 black-box calls: 0/-1/-2/-7 all raise
QiskitError. The speculative four failing tests were removed before production
changes; they are NOT product red/fix evidence. The existing positive-only
power contract and its negative tests remain unchanged. The oracle output is
qb-stage11pc3r2-power-contract-oracle.log/.exit, exit 0.

No physical tolerance or memory cap was relaxed and no coverage exclusion was
added. Native signed-Pauli conjugation is checked against complete complex
matrices, not only final probabilities. Existing numerical compose/adjoint
behavior was preserved, not falsely claimed as a discovered numerical defect.

## Mathematical And Lifetime Evidence

The new Tableau test file has 69 cases. It includes 1-5 qubit complete complex
composition/front-order, adjoint, Pauli +/-/i phases, synthesis, qargs embedding,
GF(2) solve/nullspace, redundant/underconstrained signed generators, symplectic
pairing, invalid inputs and zero-qubit boundaries. Four public Qiskit label,
compose, adjoint and signed-Pauli cases are optional black-box oracles only.

The 100-qubit test forbids Clifford.to_matrix, Operator.from_circuit and
Statevector.from_circuit, then actually prepares GHZ, computes both inverse
compositions, evaluates an X-string, measures and samples selected qubits.
Actual returned storage is four 40200-byte tableau roots plus 24 sample-label
bytes, 160824 bytes total, retained through user objects/views. Dense expansion
tests reject before the matrix/synthesis factory. This is native CPU tableau
execution, not a real 100-qubit cloud/hardware claim.

Failure cases include first and later quota denial, source-account copying,
last-view release, invalid symplectic construction, confirmed-shot preservation
after formatting failure and valid-overbudget-valid recovery on the same ledger.
Actual Result/Aer Clifford snapshots serialize generator labels, not a newly
invented native Result.tableau field; existing serialized schemas are preserved.

## Old Dense Allowance Audit

Receipt qb-stage11pc3r2-dense-allowance-audit records a one-qubit native QNode
value 0.9553364891256059. Its legacy workspace is 512 bytes, its actual owned
initial array is 32 bytes, and live storage at that point is 576 bytes including
other real request storage. The initial array belongs to the active ledger.
There is overlap, but the eight-state aggregate does not identify individually
replaceable roles well enough to justify subtracting an arbitrary component.

The same audit exposed the direct Device density defect: a returned 256-byte
matrix had no account and live bytes were zero. After the bounded fix,
qb-stage11pc3r2-dense-allowance-after-fix records owner=true, output=256 bytes
and live=256 bytes. Four new real quota/lifetime/physics cases cover the fix.

No legacy dense allowance was removed. derivative_planning.device_working_bytes
and qnode_engine workspace reservations are unchanged from HEAD (diff exit 0).
Unproven adjoint/dynamic-variance/other working-array paths and external workspace
still require protection and explicit limits. Some other known native paths
remain outside this bounded batch; they are not relabeled as unknown external
workspace. R2/C3 therefore stays PARTIAL rather than claiming universal memory
closure. This audit does not authorize infinite allocator expansion.

## Final Validation Status

Invalidated first candidate: 6cc46f8d1cb9ee3a4b537fd3458ea045413d9597, exported with an
independent Git index to /tmp/qb-stage11pc3r2-tableau-candidate.sjfhQK/source.
It no longer matches the corrected sources. Review found that empty complex
ndarrays have no scalar leaves and were incorrectly accepted as zero-qubit
boolean tableaux only in managed mode. The correction reads the explicit base
ndarray dtype without foreign array protocols; empty boolean tableaux remain
valid. User Studio/Router dirt stays excluded.

| Prefix | Candidate validation |
| --- | --- |
| qb-stage11pc3r2-tableau-sdkfree-full | 2389 passed / 420 skipped / 5 warnings, 238.04s, exit 0 |
| qb-stage11pc3r2-tableau-main-coverage-full | Invalidated candidate deliberately interrupted after confirmed input regression; exit 2; 2403 passed / 5 skipped / 3 xfailed at interruption, NOT a full pass |

Both receipts above are historical first-candidate evidence only. Partial
coverage from the interrupted run is not a final coverage result. A fresh
corrected snapshot and new receipts are required below.

Corrected frozen source tree: `85b2c716a8bb24fdf4a79de969ec5eb295ce1e09`,
export `/tmp/qb-stage11pc3r2-tableau-v2.CwI3qD/source`, built from HEAD plus
the same 23 explicit R2 paths using a separate index. Production matches the
working tree (Git diff exit 0); the real Git index remains unstaged. The new
empty-complex cases cover two empty shapes, complex64/complex128, explicit
ndarrays and ndarray subclasses, and preserve both valid empty bool shapes.
V2 final receipts are pending; no earlier snapshot is substituted for them.

| V2 receipt prefix under /tmp | Actual result |
| --- | --- |
| qb-stage11pc3r2-tableau-v2-sdkfree-full | 2399 passed / 420 skipped / 5 warnings, 252.77s, exit 0 |
| qb-stage11pc3r2-tableau-v2-main-coverage-full | 3042 passed / 5 skipped / 3 existing public-oracle xfailed / 57 warnings, 1411.86s, exit 0 |
| qb-stage11pc3r2-tableau-v2-alternate-full | 3040 passed / 5 skipped / 5 existing public-oracle xfailed / 49 warnings, 471.34s, exit 0 |
| qb-stage11pc3r2-tableau-v2-jax012 | 844 passed / 168 missing-other-framework/optional skips, 37.53s, exit 0; derivative_execution/interfaces |
| qb-stage11pc3r2-tableau-v2-tf | 866 passed / 151 missing-other-framework/optional skips, 49.93s, exit 0; derivative_execution/interfaces |
| qb-stage11pc3r2-tableau-v2-torch-autograd | 46 passed / 984 unrelated deselected, 14.92s, exit 0; same directories with explicit torch-or-autograd selection |
| qb-stage11pc3r2-tableau-v2-compile | compileall quantumbridge/tests/examples, exit 0 |
| qb-stage11pc3r2-tableau-v2-legal | 4 passed, 0.12s, exit 0 |
| qb-stage11pc3r2-tableau-v2-privacy | 49 passed / 1 existing optional-bridge warning, 1.67s, exit 0; 17 explicit offline/no-token/no-vendor/interchange-security files |

True full JSON `/tmp/qb-stage11pc3r2-tableau-v2-full-coverage.json` records
27456/30388 statements = **90.35145452152166%**, missing 2932, excluded 68.
This exceeds 90.17352569642976% without added exclusions or relaxed tolerances.
It is the corrected v2 FULL run, not interrupted v1 data or a development union;
line coverage still does not measure complete SDK functional parity.

Fresh `qb-stage11pc3r2-tableau-v2-versions-{main,alternate,sdkfree,jax012,tf}`
receipts all exit 0 and import QuantumBridge from the v2 export. Python is
3.12.6 throughout. Main NumPy/Qiskit/Aer/PennyLane/JAX/TF/Torch/Autograd are
2.4.6/2.4.1/0.17.2/0.44.1/0.7.1/2.21.0/2.12.0/1.8.0. Alternate Qiskit,
PennyLane, JAX and Autograd are 2.6.0/0.42.3/0.6.2/1.9.1. Main and alternate
include disclosed user/system-package origins and are not fully isolated.
SDK-free and independent JAX 0.12.0/TF 2.21.0 use NumPy 2.5.4 without quantum
SDKs; SDK-free has none of the four AD frameworks. BLAS/OMP threads are one;
JAX x64 is enabled.

Matching `v2-pip-*` receipts exit 0 for SDK-free/JAX/TF. Main/alternate exit 1
for the unchanged pyquafu 0.4.5 requirement NumPy<2 against NumPy 2.4.6, and
WeasyPrint 68.1 requiring tinycss2>=1.5.0 against 1.4.0. These are unresolved
pre-existing environment conflicts, not reported as green or corrected by this
runtime patch. No installation, credential or environment adjustment occurred.

A filename-only scan of the 23 owned files for explicit private-key headers
and common GitHub/OpenAI credential formats found no matches (rg exit 1 means
no matches, not an execution failure here). No owned vendor/site-packages/venv/
wheel/dist-info/egg-info paths were found. This limited scan does not certify
all possible secret formats or the user's unrelated files. Privacy gates do
not claim real hardware authentication or cloud execution.

The four new test files separately compare equal to the export (cmp exit 0
each); production/tests/examples match when checked with the independent
candidate index (Git diff exit 0). A check against the ordinary unstaged index
misreported the four untracked test files as deletions; this was an index
selection mistake, not source deletion. The real index remains unchanged.

The actual complete 28-section matrix terminated with shell exit 0:
`qb-stage11pc3r2-tableau-v2-full-matrix.log/.exit`. All 28 headers and the final
OpenFermion section are present. Each section uses the main environment; its
core-only label does not imply SDK isolation. The actual SDK-free FULL is
separate above. Seven optional installed-dependency subsets were NOT_EXECUTED,
not passed. Existing Studio baseline tests ran without Studio development.

| Matrix section | Actual result |
| --- | --- |
| core-only | FULL 3042 passed / 5 skipped / 3 existing public xfailed / 57 warnings; 472.86s |
| qiskit-extra | 5 passed |
| pennylane-extra | 9 passed |
| qiskit-aer-extra | 146 passed |
| qiskit-finance-extra | dependency unavailable; NOT_EXECUTED |
| qiskit-optimization-extra | dependency unavailable; NOT_EXECUTED |
| qiskit-machine-learning-extra | dependency unavailable; NOT_EXECUTED |
| qiskit-nature-extra | 21 passed |
| qiskit-algorithms-extra | 26 passed |
| qiskit-dynamics-extra | dependency unavailable; advisory subset NOT_EXECUTED |
| qiskit-metal-extra | dependency unavailable; advisory subset NOT_EXECUTED |
| qiskit-runtime-extra | 5 passed; offline, no hardware claim |
| qiskit-experiments-extra | dependency unavailable; NOT_EXECUTED |
| qiskit-addons-extra | dependencies unavailable; NOT_EXECUTED |
| pennylane-full-extra | 44 passed; not whole-SDK parity |
| mqt-compat | 15 passed |
| torchquantum-compat | 17 passed |
| qos-uqci-compat | 11 passed; no real hardware proof |
| quafu-compat | 15 passed; offline, not real cloud or a conflict-free pyquafu environment |
| benchpress-compat | 19 passed |
| studio-backend-api | 33 existing baseline tests passed; no Studio changes |
| ecosystem-inventory | 27 passed; inventories do not prove function implementation |
| dev | FULL 3042 passed / 5 skipped / 3 xfailed / 57 warnings, 470.03s; FULL coverage same counts, 1402.31s |
| chemistry-core | 5 passed |
| chemistry-extra | 30 passed |
| qiskit-nature-p2-extra | 5 passed |
| algorithms-extra | 10 passed |
| openfermion-extra | 1 passed |

After actual script termination, `qb-stage11pc3r2-tableau-v2-matrix-coverage-export`
exited 0. JSON `/tmp/qb-stage11pc3r2-tableau-v2-matrix-coverage.json` independently
records the same 27456/30388 = 90.35145452152166%, missing 2932, excluded 68.
This is the script's actual full-coverage database, not a focused replacement.
Both the working and exported production/tests/examples still match v2 tree
85b2c716a8bb24fdf4a79de969ec5eb295ce1e09 using its independent index (each Git
diff exit 0). Inventory scripts regenerated private-export documentation only;
those generated inventory docs were not copied into the owner's workspace.
All needed test/matrix/coverage-export processes are terminal. Existing pip
conflicts remain disclosed rather than reported as clean environment checks.
Earlier P0/P1 receipts are not substituted for these fresh v2 results.

The completed test gates permit a scoped ordinary R2 local checkpoint; its
actual SHA must be recorded by Git and the execution result, not invented here.
No push or new-SHA remote CI is verified. No auth/TLS/token reads, real cloud/hardware, subagents, tag/release,
vendor or history rewrite. The highest objective remains all actual native
Qiskit/PennyLane core APIs, not line coverage or array accounting alone. After
the bounded R2 gates, request joint review and prioritize Stage 12 real missing
function behavior. Studio stays last.

The P2 scope/results and first candidate FULL result were sent to the owner's
designated ChatGPT conversation. Its completed reply confirmed: finish all
same-tree gates, scoped ordinary local checkpoint, then truthful joint C3
review (Verified native / Partial native / Unsupported / Unverified), and
Stage 12 actual missing API behavior. That reply is report-based, not a source
audit or final acceptance, and is recorded in the R2 execution spec.

## Read-Only Next API Survey

While the main coverage run proceeds, receipt
`qb-stage11pc3r2-tableau-v2-next-api-survey` (exit 0) records actual native and
installed Qiskit 2.4.1 public signatures and small from_int calls, without
reading upstream implementation/test source. This is gap identification, not
new Stage 12 implementation or a numerical parity pass.

Both native state classes lack object seed and add/subtract; DensityMatrix
also lacks scalar multiplication/division, and Statevector lacks its public
purity method. Explicit dims=(2,4) is flattened to native (2,2,2), while public
Qiskit preserves (2,4); dims=(3,2) rejects natively but succeeds publicly.
Probability and sample return containers and DensityMatrix.dim also differ;
compatibility work must preserve existing native callers rather than blindly
change their established API. Tensor/expand/evolve already exist and need
behavioral boundary tests, not speculative duplicate implementations. Neither
public state class exposes a variance method: absence of that name alone is
not a genuine Qiskit API gap. Actual observable variance must be scoped to the
appropriate supported interface. These bounded candidates remain deferred
until final R2 gates and the finite joint review.
