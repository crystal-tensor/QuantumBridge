# Stage 12-A P0.1 Native Mixed-Radix Progress

Historical P0.1 checkpoint report. Later native local-operator development is
recorded in [the P0.2-A report](stage12_a_p02_mapped_operator_progress.md);
Unsupported statements here refer to the P0.1 code, not the later candidate.

Date: 2026-10-21. Status: bounded P0.1 native function slices accepted after
fresh same-runtime gates; complete state classes/public compatibility remain
PARTIAL. Full independent native Qiskit/PennyLane replacement remains
ACTIVE / INCOMPLETE; C3 stays PARTIAL.
Baseline HEAD d22e88f89f95ae3a251de5fc9e18c7dde4170c43 contains documentation
over the accepted bounded R2 runtime b1d345b. R2 green receipts do not validate
the new P0 source. The final gates below precede the scoped local checkpoint;
no push or new-SHA remote CI is claimed.

## Actual Implementation

The existing Statevector/DensityMatrix classes and numeric arrays are reused.
The shared state_dimensions helper validates positive integral dimensions,
their exact product, qubit identity, native subsystem positions and q0-first
mixed-radix basis digits. It is not a second simulator or an SDK facade.

- Explicit (2,4), (3,2), (2,3,2), single-qudit and trivial (1,) metadata remain
  distinct. A power-of-two total alone does not imply all subsystems are qubits.
- from_int generates the actual full basis vector/density, including dimension
  6, using existing pre-admitted array helpers. Integer 4 still infers (2,2);
  integer 6 infers (6,). Explicit native empty dims retain the existing zero-
  qubit semantics, separately from observed public from_int empty-tuple errors.
- Constructors gain keyword-only dims without repurposing legacy Statevector's
  positional normalize flag. Existing raw constructors without dims still
  enforce the old binary-size requirement; explicit dims are required for
  nonbinary raw arrays. DensityMatrix.dim remains its native shape tuple.
- Copies, state/density conversion, tensor/expand, conjugate/transpose/adjoint,
  reversal and same-size full numeric operator evolution preserve real ordered
  dimensions and complex data. Full-system matrices execute native NumPy
  products through the existing ownership helpers, not upstream SDK execution.
  Density adjoint retains a typed object; the existing Statevector adjoint
  returns a numeric row array, not a dimension-bearing typed state.
- Marginal probabilities, categorical samples, measurement collapse and reset
  use actual mixed-radix digits, not binary masks. Native dict/list containers,
  q0-first order and existing explicit per-call seed behavior remain. Large
  native digit labels use a separator when needed to avoid ambiguity.
- Density partial trace generalizes its existing reshape/trace calculation to
  actual dimensions. Known reduction outputs are pre-admitted, retained by
  real roots/views, and use NumPy trace's out buffer. Native keep-style behavior
  preserves the original subsystem order, even if keep is supplied reversed.
- Composed from_int -> tensor -> density -> partial_trace -> probabilities
  runs natively for (2,4) and (3,2), with independent numerical reductions.

No object RNG, new arithmetic/purity API, general channel/observable engine,
Capture, Studio, cloud, token/auth/TLS, tag/release or vendoring work is added.
New numeric buffers use existing ledger ownership; Python labels/containers,
scalar loops and hidden numerical workspace are not measured process RSS.

## Explicit Remaining Boundaries

Mapped mixed-radix operator qargs, qubit circuits on a nonbinary partition,
operator-object conversion, and general channel evolution remain unsupported
in this batch. The direct Channel.evolve entry also rejects a mixed-radix
DensityMatrix before it can silently reconstruct an inferred-qubit result.
Legacy binary-only concurrence/negativity/Schmidt/mutual-information entry
points reject new nonbinary native objects rather than reinterpret a single
four-level subsystem as two qubits. These are bounded guards, NOT completed
mixed-radix channel or analysis implementations. Raw numeric legacy callers
keep their existing binary interpretation.

Public compatibility is still partial. Native q0-first, probability dictionaries
and density shape-tuple dim are deliberately not relabeled as public Qiskit
semantics. Optional differentials explicitly reverse dimension/qarg conventions
and compare numerical probabilities/reductions. A public compatibility facade
is not implemented or counted as native mathematics. The versioned 158-case
public audit remains reference evidence, not 158 native test passes.

## Actual Red And Recovery Receipts

Every prefix is under /tmp with full log and independent exit.

| Prefix | Actual result |
| --- | --- |
| qb-stage12a-p01-construction-red | 43 failed / 13 passed, 0.25s, exit 1 on unchanged native construction |
| qb-stage12a-p01-construction-green | 160 passed including prior state-resource and legacy invalid-size cases, 0.37s, exit 0 |
| qb-stage12a-p01-propagation-red | 56 failed / 59 passed, 0.62s, exit 1 after construction support but before propagation fixes |
| qb-stage12a-p01-propagation-first-recovery | 362 passed, 2.36s, exit 0 |
| qb-stage12a-p01-propagation-final-focus | 443 passed, 3.78s, exit 0 after added resource/public-oracle cases |
| qb-stage12a-p01-binary-analysis-red | 8 failed / 137 deselected, 0.16s, exit 1; actual silent binary reinterpretation or wrong error path |
| qb-stage12a-p01-expanded-native-regression | 1529 passed / 1 conditional skip / 2 existing warnings, 113.07s, exit 0; derivative/interfaces/device/Aer/quantum-info before final direct-channel guard |
| qb-stage12a-p01-direct-channel-red | 2 failed / 145 deselected, 0.13s, exit 1; direct native channel entry lost mixed-radix partition metadata |
| qb-stage12a-p01-before-freeze-focus | 693 passed / 2 existing warnings, 9.61s, exit 0; state/Clifford/Result/Aer/Device after the bounded channel guard |

The new file currently has 147 parametrized cases. It checks actual complex
data before dimensions, independently indexed reductions/reset, normalization,
trace/PSD, original caller data, real root/view lifetime, pre-factory quota
denial and explicit native/public bit-order mapping. Existing binary tests and
tolerances were not rewritten to manufacture failures or make fixes pass.

## Bounded Function Evidence Inventory

Following the completed frozen-tree gates below, the first six measured native
function slices are Verified Native within the stated contracts/fixtures.
Guard-only behavior is verified refusal, NOT implemented channel/analysis
mathematics. This is not an entire class/API parity claim.

| Native call slice | Numerical and contract evidence | Remaining boundary |
| --- | --- | --- |
| Statevector/DensityMatrix.from_int and explicit numeric dims | Real basis indices and complex data, exact product/order, (2,4)/(3,2)/(2,3,2)/(6,)/(1,)/empty native cases, independent values, pre-factory rejection and owned-root lifetime | Raw no-dims nonbinary constructors remain rejected; public empty from_int exceptions differ |
| copy/tensor/expand/conjugate/transpose/adjoint/reverse | Independent complex arrays/permutations and dimensions, typed conversion, actual ownership helpers; optional public calls only where the public method exists | Statevector adjoint is the existing numeric row, not a typed state; absent public methods are NATIVE_MATH_ONLY |
| Same-size full-system numeric evolve | Independent complex phase operators in authored tests and a full complex Fourier matrix in both public black-box comparisons | Mixed mapped qargs, qubit circuits on nonbinary partitions and operator-object conversion remain Unsupported |
| probabilities/sample/measure/reset | Actual high-radix digits and selected order, independent marginal/collapse/reset mathematics, normalized categorical draws, complex phase, genuinely mixed density reset and deterministic public basis samples | Native dict/list containers and per-call seeds are retained; no object RNG or universal stochastic-stream parity |
| Native keep-style partial_trace | Independent row/column contraction, complex reduced matrices, trace/PSD/dims/order, known NumPy out buffers and final-view lifetime; public trace-out conversion is explicit | Public keep/discard and wire conventions differ; four observed public num_qubits differences per version remain Partial |
| from_int -> tensor -> density -> partial_trace -> probabilities | Actual SDK-free composed calls for (2,4)/(3,2), independent reduced matrices, normalized probabilities and actual ordered dimensions | Local numerical proof, not a cloud/hardware or full ecosystem workflow |
| Existing analysis/direct-channel entries on mixed typed objects | Genuine pre-fix silent reinterpretation/metadata loss and explicit Unsupported after the guard | Correct refusal only; general mixed-radix analysis/channel mathematics NOT implemented |

Overall Statevector/DensityMatrix classes and public compatibility remain
PARTIAL. SDK function families outside these slices are not accepted by this
inventory. Complete native Qiskit/PennyLane replacement remains incomplete.

## Frozen Candidate And Validation

Candidate tree: 7aeb821e37b374ce0c3676d6d49236828155dccc, exported to
/tmp/qb-stage12a-p01-candidate.F04OYk/source using a separate Git index. The
actual working index remains empty; user Studio/Router changes are excluded.
Runtime/tests/examples match the candidate (separate-index Git diff exit 0).
Later report-only edits do not change the runtime accepted by these receipts.

| Fresh frozen-tree gate | Actual result |
| --- | --- |
| qb-stage12a-p01-v1-sdkfree-full | 2540 passed / 426 optional-dependency skipped / 5 warnings, 240.57s, exit 0 |
| qb-stage12a-p01-v1-main-coverage-full | 3189 passed / 5 skipped / 3 existing public-oracle xfailed / 57 warnings, 1411.55s, exit 0 |
| qb-stage12a-p01-v1-main-coverage-json | Export exit 0: 27570/30483 = 90.44385395138274%, missing 2913, excluded 68 |
| qb-stage12a-p01-v1-alternate-full | 3187 passed / 5 skipped / 5 existing public-oracle xfailed / 49 warnings, 470.74s, exit 0 |
| qb-stage12a-p01-v1-jax012 | Independent JAX 0.12: 844 passed / 168 absent-other-framework skips, 37.57s, exit 0 |
| qb-stage12a-p01-v1-tf | Independent TF 2.21: 866 passed / 151 absent-other-framework skips, 50.43s, exit 0 |
| qb-stage12a-p01-v1-torch-autograd | 46 passed / 984 unrelated deselected, 15.07s, exit 0 |
| qb-stage12a-p01-v1-full-matrix | Actual unchanged shell script reached all 28 sections; final exit 0, seven unavailable-dependency subsets NOT_EXECUTED |
| qb-stage12a-p01-v1-matrix-coverage-json | Independent export exit 0; exact same 27570/30483 = 90.44385395138274%, missing 2913, excluded 68 |
| qb-stage12a-p01-v1-compile | compileall quantumbridge/tests/examples, exit 0 |
| qb-stage12a-p01-v1-legal | Controlled export: 4 passed, exit 0 |
| qb-stage12a-p01-v1-workspace-legal | Dirty workspace: 1 failed / 3 passed, 0.14s, exit 1; existing untracked Router source-ledger gap, not included in this candidate |
| qb-stage12a-p01-v1-privacy | 17 explicit offline/no-token/no-vendor/interchange-security files: 49 passed / 1 existing bridge warning, 1.66s, exit 0 |
| qb-stage12a-p01-v1-versions-{main,alternate,sdkfree,jax012,tf} | All exit 0; each imports quantumbridge from the frozen private export |
| qb-stage12a-p01-v1-pip-{sdkfree,jax012,tf} | Each exit 0 |
| qb-stage12a-p01-v1-pip-{main,alternate} | Each exit 1; existing WeasyPrint 68.1/tinycss2 1.4 and pyquafu 0.4.5/NumPy 2.4.6 conflicts |
| qb-stage12a-p01-v1-source-equality-{working,export} | Both exit 0 after the actual matrix; production/tests/examples match the tested candidate within the controlled scope |
| qb-stage12a-p01-v1-scoped-secret-patterns | git grep exit 1 with empty output: no hits for the explicitly scanned private-key/common GitHub/OpenAI formats, not a universal secret audit |

All required frozen-runtime test processes terminated before checkpoint work.
Main true FULL coverage and independent matrix coverage above are complete;
the rounded terminal display of 90% is not substituted for the actual JSON.
The original 68 exclusions did not increase; prior true full baseline was
90.35145452152166%. Neither figure is an API-completion percentage.
Main/alternate retain mixed user/system package origins and their known pip
conflicts; they are not hermetic clean environments. SDK-free/JAX/TF have no
upstream quantum SDK installed. Framework-specific skips remain skips.

## Actual Matrix Sections

The script used the real main Python and pytest wrapper, not a reduced test
replacement. The section name core-only is not an SDK-free environment claim;
the separate SDK-free FULL above provides that evidence. All statuses below
come from the completed full-matrix log, not merely from section headers.

| Section | Actual result |
| --- | --- |
| core-only | 3189 passed / 5 skipped / 3 existing xfailed / 57 warnings, 472.84s |
| qiskit-extra | 5 passed |
| pennylane-extra | 9 passed |
| qiskit-aer-extra | 146 passed / 1 warning |
| qiskit-finance-extra | NOT_EXECUTED, dependency unavailable |
| qiskit-optimization-extra | NOT_EXECUTED, dependency unavailable |
| qiskit-machine-learning-extra | NOT_EXECUTED, dependency unavailable |
| qiskit-nature-extra | 21 passed |
| qiskit-algorithms-extra | 26 passed / 11 warnings |
| qiskit-dynamics-extra | NOT_EXECUTED, advisory dependency unavailable |
| qiskit-metal-extra | NOT_EXECUTED, advisory dependency unavailable |
| qiskit-runtime-extra | 5 passed, offline only |
| qiskit-experiments-extra | NOT_EXECUTED, dependency unavailable |
| qiskit-addons-extra | NOT_EXECUTED, dependency unavailable |
| pennylane-full-extra | 44 passed |
| mqt-compat | 15 passed |
| torchquantum-compat | 17 passed |
| qos-uqci-compat | 11 passed, offline only |
| quafu-compat | 15 passed, offline only |
| benchpress-compat | 19 passed / 3 warnings |
| studio-backend-api | 33 existing regression tests passed / 1 warning; no Studio development |
| ecosystem-inventory | Actual inventory scripts and 27 tests passed / 1 warning; inventories are not native implementations |
| dev | FULL 3189 passed / 5 skipped / 3 existing xfailed / 57 warnings, 472.30s; independent FULL coverage same counts, 1404.78s |
| chemistry-core | 5 passed |
| chemistry-extra | 30 passed / 5 warnings |
| qiskit-nature-p2-extra | Actual inventory and 5 tests passed |
| algorithms-extra | Actual inventory and 10 tests passed / 5 warnings |
| openfermion-extra | 1 passed |

Final matrix shell exit is 0. Optional absent subsets are not accepted as tested
or functionally complete. Offline provider paths do not establish cloud access.

The actual native composed demo in the SDK-free environment also exits 0:
from_int(4,(3,2)) -> tensor(from_label('+')) -> to_density_matrix() ->
partial_trace([0,2]) yields dims (3,2), trace 1.0000000000000002 and probabilities
20=21=0.5000000000000001, others zero. This is local numerical execution, not
cloud/hardware or complete public-API parity. Its receipt prefix is
qb-stage12a-p01-native-sdkfree-demo.

The designated ChatGPT conversation received the genuine implementation/red-
green/SDK-free results. Its completed feedback requires finishing these gates
before P0.1 acceptance/checkpoint, then bounded mapped-operator work. The reply
is saved in the execution prompt; it is report-based feedback, not an external
source audit. No additional functionality was started during the frozen gates.

## Local Checkpoint Receipt

Normal local code commit: 89f4dc95bd38076c869c13e9176423698d6efb53 on main,
message: feat: support native mixed-radix state construction and propagation.
Exactly 13 P0.1-owned paths were staged, 1060 insertions / 141 deletions; user
Studio/Router tracked and untracked changes remain outside the commit. Existing
binary tests were not edited. The index was empty before scoped staging and
again after the commit. No amend or identity configuration was performed; Git
used its existing automatically configured identity and emitted its warning.

The final documentation snapshot 34a323909c8abdd8c267716b29cb055510689d6a
preserves production/tests/examples from the FULL-tested 7aeb821e candidate
(Git diff exit 0). The normal staged tree exactly matched that final snapshot:
qb-stage12a-p01-final-staged-equality, exit 0. Its controlled export at
/tmp/qb-stage12a-p01-final.Mz0BdY/source also passes fresh compile (exit 0), legal
(4 passed, exit 0) and privacy/security (49 passed / 1 existing warning,
exit 0), prefixes qb-stage12a-p01-final-docs-{compile,legal,privacy}.
Commit runtime/tests/examples equality to the original FULL-tested candidate
is independently recorded by qb-stage12a-p01-committed-runtime-equality, exit 0.
These later documentation receipts do not change the tested runtime.

No push was attempted; the earlier workflow OAuth refusal was not retried or
bypassed, and no fresh remote fast-forward/CI proof is claimed. Ahead counts
are relative to cached origin/main only. New-SHA remote CI and actual hardware
remain NOT_VERIFIED. No tag/release, vendoring, credential/auth/TLS change,
cloud call or history rewriting occurred. The highest full-replacement goal
remains ACTIVE / INCOMPLETE. Further P0.2 work is a separate bounded batch.

The designated conversation received the actual code SHA and all final gates,
and its complete P0.2-A mapped-numeric-operator prompt was read and preserved
in the execution-prompt document. It calls for verified public contracts,
genuine reds, native local contractions (not an embedded full Kronecker matrix),
independent complex mathematics and fresh gates. Square dimension-preserving
operators come first; rectangular changes require proved target output dims.
No P0.2 implementation or test result is claimed by saving that next prompt.

## Supplemental Frozen-Tree Public Numerical Comparison

The external validation script /tmp/qb-stage12a-p01-propagation-oracle.py calls
only installed public APIs and the same frozen native source. It does not read
or copy upstream implementation/tests and does not alter the candidate. The
completed v2 receipts are
qb-stage12a-p01-v1-public-propagation-v2-{qiskit241,qiskit260}. Both exit 0 with
158 numerical/dimension checks each. This is a separate composed-operation
comparison, NOT the earlier 158-record initial public contract survey.

Fixtures include complex states, genuinely mixed densities (two distinct pure
components), (2,4)/(3,2)/(2,3,2)/(6,)/(1,)/binary partitions and a full complex
Fourier operator, not only identity or diagonal matrices. Comparisons cover
construction/basis, copy/conjugate/reverse, tensor/expand, full evolve,
state-density conversion, density reset, partial trace, deterministic basis
measurement/reset/sample. Complex stochastic collapse remains independently
verified by the authored tests; deterministic public samples do not establish
identical arbitrary RNG streams or object-seed compatibility.

Four public metadata differences remain in EACH version: reducing either state
class with source native dims (2,4) or (2,3,2) to native keep=[0] yields the same
2x2 reduced data and ordered dims (2,), but native num_qubits=1 while public
partial_trace returns num_qubits=None. The native actual-partition invariant is
retained. This is a recorded public-compatibility difference, not an all-API
parity pass or an assertion of the cause inside upstream code.

The first comparison receipts without the v2 suffix both exit 1 on the above
num_qubits difference. The intermediate corrected receipts both exit 1 because
the harness assumed public DensityMatrix.transpose exists; it does not in
either installed version. Those incomplete harnesses are preserved, not native
regression reds. The final script does not claim public transpose/adjoint method
parity when the method is absent; it checks that existing native operation
against independent matrix transpose/conjugation and labels it NATIVE_MATH_ONLY.
The completed two-version output diff contains only the version header.

User Studio/Router dirt is excluded from controlled source exports and never
modified or committed. Whole dirty-workspace legal checking still has the
separately recorded untracked Router source-ledger issue; scoped legal gates
must not be represented as certifying those unreviewed user files.
