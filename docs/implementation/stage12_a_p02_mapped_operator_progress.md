# Stage 12-A P0.2-A Native Mapped Numeric Operator

Date: 2026-10-21. Status: bounded native function slices validated by fresh
frozen-runtime FULL/framework/coverage/matrix gates; scoped checkpoint pending.
Baseline HEAD: 2bd746c, documentation over P0.1 runtime 89f4dc9. Full independent
Qiskit/PennyLane functional replacement remains ACTIVE / INCOMPLETE, C3 PARTIAL.
P0.1 receipts do not validate this new source. No P0.2 commit or push yet.

## Native Functions Implemented

- Operator now accepts positive nonbinary/rectangular numeric buffers, infers
  binary dimensions or a single qudit per side, and accepts actual positional
  or keyword input_dims/output_dims. Products must match matrix columns/rows;
  dim is (input size, output size). num_qubits is defined only for identical
  all-binary input/output partitions. No arbitrary shape is relabeled as qubits.
- Existing Operator copy/conjugate/transpose/adjoint/tensor/expand/reverse/
  reshape/arithmetic preserve ordered input/output partitions and actual
  complex data. Transpose/adjoint swap sides; rectangular reverse uses separate
  row/column permutations. Native existing compose multiplication order remains
  unchanged. Complete Operator public/algebra parity is NOT claimed.
- Existing Statevector.evolve and DensityMatrix.evolve execute local numeric
  square maps on mixed dimensions, including noncontiguous and reversed qargs.
  Native q0 is the high radix, selected order is not sorted, and unselected
  positions retain their own basis indices. Nonunitary results are not normalized.
- DensityMatrix local rectangular maps update each selected output subsystem
  and execute A rho A-dagger. Both state types support full-system typed
  rectangular maps, including input dimension 4 -> output dimension 6, and
  output subsystem-count changes in a full-system map. Explicit (4,) remains
  one qudit, distinct from inferred (2,2), even though both have total size 4.
- The existing utils.math apply_unitary/apply_density_operator entry points gain
  one shared actual mixed-radix index/stride branch. Original default binary
  Device kernels are unchanged. No upstream quantum engine or second simulator
  is introduced. No full-system embedded/Kronecker operator is built locally.
- State output is one Dout complex vector. Density uses a Dout*Din intermediate,
  Dout^2 output and max(Din,Dout) reusable row/column scratch. Known groups and
  required operator conversion/copy are checked before the first factory/core
  action; existing ArrayOwnership retains actual result/view storage. Scalar
  Python/index and hidden ufunc iterator workspace are not measured process RSS.

Native probability dictionaries, q0-first ordering, DensityMatrix shape-tuple
dim and valid binary calls are retained. Raw same-size full-system maps preserve
the native state partition; a same-input/output typed full square map retains
that legacy partition too. This is not a drop-in public namespace/facade.

## Explicit Unsupported And Partial Boundaries

- Local Statevector rectangular maps remain Unsupported within the sampled
  Qiskit 2.4.1/2.6 public failure boundary; this is NOT mathematical impossibility
  or a permanent prohibition on a future native extension.
- Local insertion/removal of subsystem positions is Unsupported. Full-system
  typed output-count changes are supported separately.
- General mapped Kraus/Choi/SuperOp channels, mixed-radix circuits/instructions,
  qudit synthesis, general observables, object RNG, state arithmetic/purity,
  Capture/Studio and whole-SDK facade work are not implemented here.
- Mixed-radix Operator-on-Operator mapped compose and qudit/rectangular
  to_instruction remain Unsupported. The new typed operator is rejected by
  unextended channel constructors rather than silently losing its partition.
  This guard is not a general channel implementation.
- Complete Statevector/DensityMatrix/Operator classes and public compatibility
  remain Partial. No hardware/cloud/push/new-SHA CI, release/tag/vendor or
  credential/auth/TLS work is part of this batch.

## Actual Public Experiments

Only installed public APIs were called; no upstream source/tests were read,
copied or ported. Initial public probes per version have 222 case records. The
refined probes have 240 case records plus two operator metadata records; both
process exits are 0 and parsed case/operator JSON diff is 0. These are recorded
API outcomes INCLUDING exceptions, NOT 240 passing native tests. Prefixes:
qb-stage12a-p02-public-{qiskit241,qiskit260} and
qb-stage12a-p02-public-refined-{qiskit241,qiskit260}, full logs/exits under /tmp.

Verified boundaries:

- Operator itself has NO evolve method in either version. Actual entries are
  Statevector/DensityMatrix.evolve(Operator,...); no speculative method was added.
- Local rectangular DensityMatrix calls work and update dimensions. Every
  sampled local rectangular Statevector call fails with ValueError/reshape.
  Both state types accept full-system typed rectangular maps; sampled raw
  rectangular evolve calls fail output-dimension validation.
- Initial invalid-qargs probes used a scalar operator and therefore conflated
  width and target errors. Refined matching-matrix probes show public bool
  targets accepted, public DensityMatrix duplicate targets sometimes accepted,
  and other malformed targets raising different exception classes. Native
  validation deliberately stays distinct/nonnegative/in-range/integral/no-bool.
  This is Partial Public Compatibility, not exact exception or acceptance parity.
- Five raw constructor shapes and inferred typed full rectangular maps were
  also compared in both versions. Native/public input/output dimensions, dim,
  data and relevant num_qubits agree for these samples.

Extra propagation probes qb-stage12a-p02-extra-v3-public-{qiskit241,qiskit260}
assert native correctness against independent basis enumeration and a separate
tensor-contraction calculation. One observed public numerical difference per
version remains for Statevector on native dims (2,3,2), selected (2,1), output
local dims (3,2), after explicit native/public order conversion. Native matches
both independent oracles and the public DensityMatrix result. The public
Statevector max amplitude difference is 0.11547005383792554; its outer product
differs from public DensityMatrix evolution by 0.02863564212655281, so this is
not merely global phase. The observed difference is retained as Partial Public
Compatibility without asserting its internal upstream cause or changing native
mathematics to imitate it. Process exit 0 here does NOT mean public equality in
that recorded case. Earlier extra/v2 receipts are preserved as probe history;
v3 ensures an independent-oracle assertion cannot be caught as a public error.

Complete literal inputs, matrix elements, phase-bearing amplitudes, explicit
native/public target/dimension conversion, independent outputs and actual
native/public state/density outputs for BOTH versions are preserved in
[the generated reproduction data](../compat/stage12_a_p02_public_differential_case.json).
Its status is PUBLIC_DIFFERENTIAL_MISMATCH. Two distinct native index algorithms
and density agreement support the stated native contract; they do not establish
an upstream defect or eliminate a possible unresolved public-semantics issue.
The artifact was generated from frozen 2973040c and contains no source port.

## Native Red And Recovery Evidence

Every prefix below is under /tmp with a complete log and independent .exit.

| Prefix | Actual result and meaning |
| --- | --- |
| qb-stage12a-p02-initial-native-red | 68 failed / 18 passed, 0.51s, exit 1; native mapped support and constructor/dims gaps |
| qb-stage12a-p02-after-construction-native-red | 63 failed / 23 passed, 0.50s, exit 1; constructor now works, real numeric-correct/dims-flattened copies exposed |
| qb-stage12a-p02-operator-dims-focus | 12 passed / 150 deselected, exit 0; selector did NOT run all named regression files |
| qb-stage12a-p02-operator-existing-regression | 81 passed, 0.25s, exit 0, real unfiltered Operator/copy/channel regression |
| qb-stage12a-p02-native-first-recovery | 162 passed, 0.36s, exit 0 |
| qb-stage12a-p02-information-regression-first | exit 4, nonexistent test filename, no tests run; command error, NOT product red |
| qb-stage12a-p02-information-regression-corrected | 2 failed / 480 passed, 1.93s, exit 1; obsolete P0.1 numeric-evolve Unsupported assertions |
| qb-stage12a-p02-channel-boundary-red | 24 failed / 86 deselected, 0.27s, exit 1; typed operator accepted with lost dimensions or wrong error |
| qb-stage12a-p02-channel-and-information-recovery | 575 passed, 2.76s, exit 0 |
| qb-stage12a-p02-foreign-boundary-red | 8 failed / 110 deselected, 0.23s, exit 1; new subclass metadata dispatch boundary |
| qb-stage12a-p02-foreign-boundary-green | 8 selected cases passed, exit 0 |
| qb-stage12a-p02-expanded-mapping-focus | 180 passed, 0.36s, exit 0 |
| qb-stage12a-p02-complete-mapping-focus | 207 passed, 0.36s, exit 0 |
| qb-stage12a-p02-expanded-native-regression | 1738 passed / 1 conditional skip / 2 warnings, 116.70s, exit 0; before final constructor default extension |
| qb-stage12a-p02-constructor-public-default-red | 9 failed / 2 passed / 215 deselected, 0.28s, exit 1; raw nonbinary/rectangular inference and positional dimensions |
| qb-stage12a-p02-pre-freeze-main-focus | 990 passed / 2 existing warnings, 11.35s, exit 0; final runtime, before last six added tests |
| qb-stage12a-p02-pre-freeze-alternate-focus | 990 passed / 2 existing warnings, 12.73s, exit 0; same qualification |
| qb-stage12a-p02-pre-freeze-sdkfree-focus | 500 passed / 46 optional-reference skips, 0.71s, exit 0 |
| qb-stage12a-p02-final232-main-focus | 232 passed, 0.49s, exit 0 |
| qb-stage12a-p02-final232-sdkfree-focus | 203 passed / 29 missing-Qiskit reference skips, 0.33s, exit 0 |
| qb-stage12a-p02-final232-alternate-focus | 232 passed, exit 0 |

Only the obsolete numeric-evolve rejection was removed from the two parametrized
P0.1 guard cases because that operation is now implemented and tested here.
Circuit/to_operator refusal, independent numerical tolerances and other valid
old binary assertions were retained. This was not rewritten to fabricate reds.

## Focused Mathematical And Ownership Coverage

The new file has 232 parametrized cases. Independent complex enumeration tests
include genuine mixed densities, non-Hermitian/nonunitary matrices, different
target dimensions, noncontiguous/reversed targets, state/density consistency,
strided caller data, no hidden reshape/full embedded matrix, and actual composed
from_int -> tensor -> mapped evolve -> density -> partial_trace -> probabilities.
For non-trace-preserving maps, unselected reduced density is compared with the
correct weighted contraction, NOT incorrectly required to remain unchanged.
An isometric rectangular map separately checks the trace-preserving invariant.

Budget tests patch actual factories/core operations, deny just below the entire
known group, run at the admitted known peak, retain escaped views, fail again
while a view holds its real root, release and successfully rerun. Rectangular
strided density examples include Dout != Din and the actual operator copy.
These are finite known-ndarray contracts, not whole-Python/BLAS/framework RSS.

## Frozen Runtime Acceptance

Frozen candidate: 2973040caa14122063d708d9df3a7c9adcada707, exported to
/tmp/qb-stage12a-p02-candidate.Aks4iC/source from a separate index containing
exactly 14 owned paths. Working runtime/tests/examples match it (Git diff exit
0), excluding the separately protected user files. The normal index is empty.
No runtime/test/example edits occur during these final gates. Later report-only
updates do not change the runtime tested by these receipts.
The later reproduction JSON is an additional documentation-only owned artifact;
it is not a runtime/test change or an excuse to reinterpret the mismatch as pass.

| Fresh final candidate gate | Actual state |
| --- | --- |
| qb-stage12a-p02-v1-compile | compileall quantumbridge/tests/examples, exit 0 |
| qb-stage12a-p02-v1-legal | Controlled export: 4 passed, 0.11s, exit 0 |
| qb-stage12a-p02-v1-privacy | 17 explicit files: 49 passed / 1 existing warning, 1.73s, exit 0 |
| qb-stage12a-p02-v1-public-extra-{qiskit241,qiskit260} | Both exit 0 with native independent math asserted; observed public numerical difference retained, not counted as equality |
| qb-stage12a-p02-v1-sdkfree-full | 2743 passed / 455 optional-dependency skips / 5 warnings, 250.84s, exit 0 |
| qb-stage12a-p02-v1-main-coverage-full | 3421 passed / 5 skipped / 3 existing xfailed / 57 warnings, 1415.44s, exit 0 |
| qb-stage12a-p02-v1-main-coverage-json | Exit 0; 27687 / 30607 lines = 90.45969876172117%, missing 2920, excluded 68 |
| qb-stage12a-p02-v1-alternate-full | 3419 passed / 5 skipped / 5 existing xfailed / 49 warnings, 473.72s, exit 0 |
| qb-stage12a-p02-v1-jax012 | 844 passed / 168 absent-framework skips, 37.42s, exit 0 |
| qb-stage12a-p02-v1-tf | 866 passed / 151 absent-framework skips, 50.63s, exit 0 |
| qb-stage12a-p02-v1-torch-autograd | 46 passed / 984 deselected, 14.91s, exit 0; explicitly selected Torch/Autograd cases only |
| qb-stage12a-p02-v1-full-matrix | Original 28-section script terminated with shell exit 0; 7 absent-dependency subsets NOT_EXECUTED |
| qb-stage12a-p02-v1-matrix-coverage-json | Exit 0; independently reproduces 27687 / 30607 = 90.45969876172117%, missing 2920, excluded 68 |
| qb-stage12a-p02-v1-versions-{main,alternate,sdkfree,jax012,tf} | All five exit 0; actual QuantumBridge import origins are the frozen export |
| qb-stage12a-p02-v1-pip-{main,alternate} | Both exit 1; only existing WeasyPrint/tinycss2 and pyquafu/NumPy conflicts, NOT clean dependency checks |
| qb-stage12a-p02-v1-pip-{sdkfree,jax012,tf} | All three exit 0, no broken requirements reported |
| qb-stage12a-p02-workspace-legal | Dirty workspace: 1 failed / 3 passed, 0.15s, exit 1; existing untracked Router source-ledger gap |
| qb-stage12a-p02-v1-scoped-secret-patterns | git grep exit 1 and empty output: no hits for scanned private-key/common GitHub/OpenAI patterns, not a universal secret audit |

The main FULL warning summary contains existing scaffold/partial-support notices,
upstream deprecations, sparse-solver and optimizer/OpenMP warnings, and existing
native QNode/template migration warnings. The five skips are the incompatible
pyquafu/NumPy environment, two unavailable Dynamics cases, one unavailable
Optimization case and the missing-JAX-installation contract (JAX is installed).
They do not validate the missing dependency paths or imply new P0.2 API parity.

The sequential suite reached ALL_GATES_TERMINATED_REVIEW_RECEIPTS and its outer
process exited 0. Every constituent gate has its own complete log and .exit;
the two known pip failures were explicitly allowed by the orchestration, not
recast as successful checks. Main and matrix coverage independently agree and
exclusions remain 68 versus the preceding 90.44385395138274% baseline. This is
line coverage, not a fraction of requested APIs completed.

### Actual Matrix Outcomes

The core-only label runs the installed main environment; the separate SDK-free
FULL above is the proof without either quantum SDK or any of the four AD SDKs.
Matrix core FULL and dev FULL each finish with 3421 passed / 5 skipped / 3 xfailed
/ 57 warnings (472.67s and 472.72s). The additional dev coverage invocation has
the same counts and takes 1408.23s. Its .coverage data is the independent matrix
JSON above. Inventory scripts generated data only in the private export.

| Matrix section | Actual outcome |
| --- | --- |
| qiskit-extra / pennylane-extra / qiskit-aer-extra | 5 / 9 / 146 passed |
| qiskit-nature-extra / qiskit-algorithms-extra | 21 / 26 passed |
| qiskit-runtime-extra | 5 passed, bounded offline/import/result paths; no cloud evidence |
| pennylane-full-extra | 44 passed; section name does not mean full-library parity |
| mqt-compat / torchquantum-compat | 15 / 17 passed |
| qos-uqci-compat / quafu-compat | 11 / 15 passed, offline paths only |
| benchpress-compat / studio-backend-api | 19 / 33 passed; unchanged existing Studio tests, no Studio development |
| ecosystem-inventory | 27 passed after the existing inventory generators |
| chemistry-core / chemistry-extra | 5 / 30 passed |
| qiskit-nature-p2-extra / algorithms-extra / openfermion-extra | 5 / 10 / 1 passed |
| Finance / Optimization / Machine Learning / Dynamics / Metal / Experiments / Addons | All seven NOT_EXECUTED because their optional dependency is absent |

### Environments And Origins

All five interpreters report Python 3.12.6 and import QuantumBridge from the
frozen export. Main has NumPy 2.4.6, Qiskit 2.4.1, Aer 0.17.2, PennyLane 0.44.1,
JAX 0.7.1, TensorFlow 2.21.0, Torch 2.12.0 and Autograd 1.8.0. Alternate has
NumPy 2.4.6, Qiskit 2.6.0, Aer 0.17.2, PennyLane 0.42.3, JAX 0.6.2,
TensorFlow 2.21.0, Torch 2.12.0 and Autograd 1.9.1. Both use mixed venv/user/
system package origins; they are NOT hermetic environments. SDK-free has NumPy
2.5.4 and none of those quantum/AD SDKs. Independent JAX has NumPy 2.5.4/JAX
0.12.0 only; independent TF has NumPy 2.5.4/TF 2.21.0 only.

Actual main/alternate pip check failures are WeasyPrint 68.1 requiring tinycss2
>=1.5.0 with 1.4.0 installed, and pyquafu 0.4.5 requiring NumPy <2 with 2.4.6
installed. No environment was altered to suppress them. The full requested
replacement and C3 remain incomplete; this bounded validation does not close
all public state/Operator APIs, dependency combinations or real hardware work.

The user's Studio/Router tracked and untracked changes remain outside the batch.
Whole-workspace legal has the separately known untracked Router ledger gap;
controlled-export legal must not be represented as certifying those files.
No deletion or fabricated attribution is used to hide that failure. The normal
Git index remains empty until scoped checkpoint staging after required gates.
