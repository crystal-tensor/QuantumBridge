# Stage 12-A P0.3 Native Mixed-Radix Operator Composition

Date: 2026-10-21. Status: bounded native function slices validated by fresh
frozen-runtime FULL/framework/coverage/matrix gates; scoped checkpoint pending.
Baseline HEAD: 9e3224b, documentation over P0.2-A code 12098c9. No P0.3 commit or
push yet. Full independent Qiskit/PennyLane replacement stays ACTIVE / INCOMPLETE;
complete Operator/state classes, public compatibility and C3 remain PARTIAL.

## Actual Native Functions

- Existing Operator.compose(other,qargs,front) now executes square and typed
  rectangular mixed-radix mapped products, including noncontiguous/reversed
  targets, different input/output host partitions and unequal total sizes.
- Native existing default is A @ B; front=True is B @ A. Dot and @ keep native
  multiplication order. Default mapped products contract the host input side;
  front=True contracts the output side. Each chosen subsystem is replaced by
  the actual new input/output dimension without sorting targets.
- Strict matching partitions on the contracted side remain required, not just
  equal total sizes. Local subsystem-count changes stay Unsupported. Full typed
  rectangular products already worked in P0.2-A and are retained as regressions,
  not presented as newly implemented functions.
- Full raw rectangular products and reflected @ now infer the uncontracted
  side when the inferred contracted partition matches the host. Raw square
  products retain their native legacy partition inference; local raw rectangles
  require typed Operator metadata. No silent repartition makes an invalid
  typed contraction legal.
- The existing shared mixed-radix index/stride helper performs row/column
  contraction. The final dense Operator matrix is mathematically required and
  allocated; no separate full-system embedded/Kronecker operator is built.
  One reusable row/column scratch accompanies the final output. Right action
  uses B, not its conjugate; density evolution remains the separate A rho A-dagger.
- Known final output, row/column scratch, required input conversions and full
  matmul packing are admitted before the first factory/core work. Existing
  ownership retains real roots/views. This is bounded known-array accounting,
  not Python/BLAS/framework hidden workspace or process RSS measurement.

No upstream execution engine, new simulator or facade is used. Native q0-first,
dict probabilities, DensityMatrix shape-tuple dim and existing full-map state
partition semantics are retained. No general mapped channels, circuit lowering,
qudit synthesis, templates, RNG, state arithmetic/purity, Capture or Studio work
is included. Full public power/fractional-power contracts are not implemented.

## Public Contracts And Finite Difference Investigation

Only installed Qiskit 2.4.1/2.6 public APIs/signatures were inspected; no upstream
implementation or test source was read/ported. Probes have complete /tmp logs and
independent exits: qb-stage12a-p03-public-{qiskit241,qiskit260} and corrected-width
qb-stage12a-p03-public-v2-{qiskit241,qiskit260}; all exit 0. V2 has 66 structured
records per version, excluding its version header, including signatures,
successful calls AND exceptions. Parsed records agree across the two versions;
this is not 66 passing native tests or an exhaustive API survey.

- Public default compose is B @ A; public front=True, dot and @ are A @ B.
  Native default compose is intentionally the opposite. Differential tests use
  the explicit complementary front value and convert ordered dimensions/targets.
- Both versions support typed full and local rectangular composition with the
  verified ordered partitions. Equal total size alone is insufficient for full
  partition matching. Initial raw-rectangle probes on contracted dims (3,2)
  correctly fail because a raw matrix infers (6,), not that partition.
- Initial malformed-target probes conflated target width and value errors. V2
  uses matching local widths: public duplicate/negative/bool targets can be
  accepted; out-of-range gives IndexError and floats TypeError. Native distinct,
  nonnegative, in-range, integral/no-bool validation stays explicit. Native empty
  qargs is a valid scalar action; these public empty-qargs probes reject it.
- Public power has float/branch_cut_rotation/assume_unitary parameters and the
  sampled fractional call succeeds. Native integer power is an existing bounded
  subset, not full power parity or a new P0.3 implementation.

The P0.2 literal reproduction is unchanged. A finite investigation reduces its
observed public Statevector difference to two subsystems and identity data:
public little-radix dims (2,3), state 1j at flat index 1, local Operator identity
as input (3,2) -> output (2,3), qargs (1,0). Independent basis enumeration and
public DensityMatrix plus public Operator.compose followed by full evolution
give flat index 4; direct public Statevector.evolve retains flat index 1.
Both versions show this exact difference, not floating error, nonunitarity,
global phase or a necessary third subsystem. Sorting qargs AND reversing local
dims reproduces the direct state result, but changes the formal arguments; it
does not establish an equivalent correction for all three public APIs.
This remains PUBLIC_DIFFERENTIAL_MISMATCH / Partial Public Compatibility, not
an assertion about upstream implementation defects. Native math is not changed
to reproduce it. The small hand-calculated native state/density/composition test
separately checks the correct ordered map.

V3 repeats the public probes and adds asserted native hand-calculated output,
actual public density, the native composition matrix and measured public
composition/state outcomes. Both v3 processes
exit 0; this asserts native math, NOT direct public Statevector equality.
The complete small literal two-version data is retained in
[the minimal reproduction artifact](../compat/stage12_a_p03_minimal_public_differential_case.json),
separately from the unchanged P0.2 original. V3 prefixes are
qb-stage12a-p03-public-v3-{qiskit241,qiskit260}.

## Actual Native Red And Recovery

All prefixes below are under /tmp, with complete .log and independent .exit.

| Prefix | Actual result and meaning |
| --- | --- |
| qb-stage12a-p03-initial-native-red | 106 failed / 15 passed, 1.09s, exit 1; mapped/reflected-rectangle gaps are genuine; two new resource tests also used the wrong Limits keyword, so not all failures are independent math evidence |
| qb-stage12a-p03-first-native-recovery | 118 passed / 3 failed, 0.33s, exit 1; remaining failures are new test-author errors: two Limits keywords and nonexistent DensityMatrix(Statevector) conversion |
| qb-stage12a-p03-corrected-native-focus | 121 passed, 0.32s, exit 0; uses actual max_total_memory_bytes and from_statevector entry points, no tolerance weakened |
| qb-stage12a-p03-information-regression | 1004 passed / 1 existing Aer warning, 7.59s, exit 0; before the last 19 tests |
| qb-stage12a-p03-expanded-native-focus | 138 passed, 0.38s, exit 0 |
| qb-stage12a-p03-final140-main-focus | 140 passed, 0.34s, exit 0 |
| qb-stage12a-p03-final140-alternate-focus | 140 passed, 0.39s, exit 0 |
| qb-stage12a-p03-final140-sdkfree-focus | 114 passed / 26 absent-Qiskit reference skips, 0.24s, exit 0 |
| qb-stage12a-p03-expanded-native-regression | 1903 passed / 1 conditional skip / 2 existing warnings, 116.48s, exit 0; before final invalid-dimension factory assertion |

The new file covers 12 distinct mapped geometries, both multiplication sides,
actual complex/nonunitary and rectangular maps, two independent basis/tensor
oracles, six state-action geometries, full typed regression/raw extensions,
adjoint side/order reversal, strided arrays with embedding/reshape disabled,
whole-group denial and real view/root release/recovery, safe explicit ndarray
buffers/foreign rejection, scalar empty targets and a real end-to-end composition
-> state evolve -> density -> partial_trace -> native probabilities workflow.
No old correct assertion or numerical tolerance was edited to fabricate a red.

The completed designated-conversation clarification permits freezing these
specific slices, not final acceptance or an unpublished-source audit. Its three
checks map to existing tests: both multiplication sides and explicit public
front conversion; six state/composition geometries including total-size changes;
and validation before allocation. Only the existing invalid-dimension test gains
a final forbidden-factory assertion before freezing; no numerical tolerance,
production feature or unrelated test is changed for that clarification.

Fresh whole-workspace legal prefix qb-stage12a-p03-workspace-legal has 1 failed /
3 passed in 0.15s, exit 1, solely the existing untracked Router source-ledger gap.
This is not hidden by the upcoming controlled-export legal result.

## Frozen Runtime Acceptance

Frozen tree: 7a9ebe78e38273636bdb6694c1dc2ef6910b36d4, from a separate index
at /tmp/qb-stage12a-p03-candidate.KEk1qC/index. Controlled export:
/tmp/qb-stage12a-p03-candidate.KEk1qC/source. Production subtree:
004ad870b19ccac9b8452b0a69e6a2c7f75317c4; tests subtree:
c87b21526e1dc987895ccea694b703ac542bad07; examples subtree:
bc98969f13dab27017074f4e40efdfc98d623c62. Both controlled working source and
export production/tests/examples equality exit 0; the normal index is empty.
Only report/ledger receipt text may change during gates, not runtime/tests/examples.

Exactly ten owned paths differ from baseline in the separate index:

- quantumbridge/information/operator.py
- quantumbridge/utils/math.py
- tests/information/test_mixed_radix_operator_composition.py
- docs/implementation/stage12_a_p03_operator_composition_progress.md
- docs/compat/stage12_a_p03_minimal_public_differential_case.json
- docs/migration/source_migration_ledger.md
- docs/compat/core_parity_ledger.md
- docs/compat/stage12_a_state_api_contract_matrix.md
- README.md
- docs/implementation/stage12_a_native_state_api_execution_prompt.md

The final minimal invalid-dimension factory assertion preserves 140 passes in
qb-stage12a-p03-prefreeze-main-focus, 0.43s, exit 0. Final sequential gate driver:
/tmp/qb-stage12a-p03-gates.py; each gate prefix is qb-stage12a-p03-v1- with full
.log and an independent .exit written only on termination. No final FULL result
is claimed before its actual terminal receipt.

| Fresh frozen-candidate gate | Actual state |
| --- | --- |
| qb-stage12a-p03-v1-compile | compileall quantumbridge/tests/examples, exit 0 |
| qb-stage12a-p03-v1-legal | Controlled export: 4 passed, 0.12s, exit 0 |
| qb-stage12a-p03-v1-privacy | 17 explicit files: 49 passed / 1 existing warning, 1.61s, exit 0 |
| qb-stage12a-p03-v1-public-v3-{qiskit241,qiskit260} | Both exit 0; native minimal math asserted, direct public Statevector mismatch retained, not equality |
| qb-stage12a-p03-v1-sdkfree-full | 2857 passed / 481 absent-dependency skips / 5 warnings, 251.15s, exit 0 |
| qb-stage12a-p03-v1-main-coverage-full | 3561 passed / 5 skipped / 3 existing xfailed / 57 warnings, 1415.97s, exit 0 |
| qb-stage12a-p03-v1-main-coverage-json | Exit 0; 27737 / 30657 lines = 90.47525850539844%, missing 2920, excluded 68 |
| qb-stage12a-p03-v1-alternate-full | 3559 passed / 5 skipped / 5 existing xfailed / 49 warnings, 475.57s, exit 0 |
| qb-stage12a-p03-v1-jax012 | 844 passed / 168 absent-framework skips, 37.62s, exit 0 |
| qb-stage12a-p03-v1-tf | 866 passed / 151 absent-framework skips, 50.15s, exit 0 |
| qb-stage12a-p03-v1-torch-autograd | 46 passed / 984 deselected, 15.00s, exit 0; the selected framework cases only |
| qb-stage12a-p03-v1-full-matrix | Original full 28-section script terminated with shell exit 0; 7 missing-dependency subsets NOT_EXECUTED |
| qb-stage12a-p03-v1-matrix-coverage-json | Exit 0; independently reproduces 27737 / 30657 = 90.47525850539844%, missing 2920, excluded 68 |
| qb-stage12a-p03-v1-versions-{main,alternate,sdkfree,jax012,tf} | All five exit 0, QuantumBridge imports from the frozen export |
| qb-stage12a-p03-v1-pip-{main,alternate} | Both exit 1, only existing WeasyPrint/tinycss2 and pyquafu/NumPy conflicts; NOT clean checks |
| qb-stage12a-p03-v1-pip-{sdkfree,jax012,tf} | All three exit 0, no broken requirements reported |
| qb-stage12a-p03-v1-scoped-secret-patterns | git grep exit 1 with an empty 0-byte log: no private-key/common GitHub/OpenAI pattern hits, not a universal credential audit |
| qb-stage12a-p03-workspace-legal | Whole dirty workspace: 1 failed / 3 passed, existing user Router ledger gap, exit 1 |

The sequential driver reached ALL_GATES_TERMINATED_REVIEW_RECEIPTS and exited 0;
all needed processes are terminal. Two known pip failures were explicitly allowed
by the driver, not rewritten as passes. Main and independent matrix coverage
agree; exclusions remain 68 versus the preceding 90.45969876172117% baseline.
Neither line coverage nor test counts establish complete API coverage.

### Actual Full Matrix

The script emitted all 28 section headers. Its core-only label uses the main
installed environment; the separate SDK-free FULL above proves actual execution
without either quantum SDK or the four AD SDKs. Matrix core FULL and dev FULL
each have 3561 passed / 5 skipped / 3 xfailed / 57 warnings in 476.46s and 476.94s.
The independent dev FULL coverage run has the same counts in 1412.63s. Existing
inventory generators ran only in the private export, not the user's workspace.

| Matrix sections | Actual outcomes |
| --- | --- |
| qiskit-extra / pennylane-extra / qiskit-aer-extra | 5 / 9 / 146 passed |
| qiskit-nature-extra / qiskit-algorithms-extra | 21 / 26 passed |
| qiskit-runtime-extra | 5 passed, bounded offline paths only |
| pennylane-full-extra | 44 passed; this section name does not imply complete library parity |
| mqt-compat / torchquantum-compat | 15 / 17 passed |
| qos-uqci-compat / quafu-compat | 11 / 15 passed, offline paths only |
| benchpress-compat / studio-backend-api | 19 / 33 passed; unchanged existing Studio tests, no Studio development |
| ecosystem-inventory | 27 passed |
| chemistry-core / chemistry-extra | 5 / 30 passed |
| qiskit-nature-p2-extra / algorithms-extra / openfermion-extra | 5 / 10 / 1 passed |
| Finance / Optimization / Machine Learning / Dynamics / Metal / Experiments / Addons | Seven NOT_EXECUTED subsets, corresponding dependencies absent |

### Environments And Warnings

All five interpreters report Python 3.12.6 and actual QuantumBridge imports from
the frozen export. Main has NumPy 2.4.6, Qiskit 2.4.1, Aer 0.17.2, PennyLane
0.44.1, JAX 0.7.1, TensorFlow 2.21.0, Torch 2.12.0 and Autograd 1.8.0. Alternate
has NumPy 2.4.6, Qiskit 2.6.0, Aer 0.17.2, PennyLane 0.42.3, JAX 0.6.2,
TensorFlow 2.21.0, Torch 2.12.0 and Autograd 1.9.1. These use mixed venv/user/
system origins and are NOT hermetic. SDK-free has NumPy 2.5.4 and no quantum/AD
SDK; independent JAX has NumPy 2.5.4/JAX 0.12.0 only, and independent TF has
NumPy 2.5.4/TF 2.21.0 only.

Both actual main/alternate pip checks report WeasyPrint 68.1 requiring tinycss2
>=1.5.0 with 1.4.0 installed, and pyquafu 0.4.5 requiring NumPy <2 with 2.4.6
installed. No environment was altered to hide these conflicts. Existing test
warnings concern scaffold/partial-support notices, upstream deprecations,
solver/OpenMP and native QNode/template migration notices. The five main/alternate
skips remain the incompatible pyquafu environment, two absent Dynamics tests,
one absent Optimization test and the absent-JAX-installation contract (JAX is
actually installed). Three main and five alternate xfails are existing, not new
P0.3 expected failures.

## Bounded Function Classification

| Actual function slice | Bounded classification | Limit |
| --- | --- | --- |
| Full typed rectangular compose | Verified Native regression from P0.2-A | Matching contracted ordered partition is required; not newly implemented here |
| Mapped square/typed rectangular compose, both sides | Verified Native, independent complex mathematics and sampled public differential | Local subsystem-count changes Unsupported; no claim of arbitrary channels/circuits |
| Noncontiguous/reversed targets and ordered output dimensions | Verified Native | Native strict targets and q0-first contract are not identical to public acceptance |
| Full raw rectangles and reflected @ | Verified Native, sampled public differential | Inferred contracted partition must match; raw squares retain native legacy inference |
| Operator/state/density composition consistency | Verified Native for six geometries and the end-to-end workflow | Direct public mapped Statevector minimal difference remains unresolved |
| Known-buffer admission and root/view lifetime | Verified Native for introduced output/scratch/conversion/packing | Not universal Python/framework/BLAS/RSS accounting; C3 Partial |
| Complete Operator/State/public SDK functionality | Partial / Incomplete | Power extensions, state analysis/arithmetic/RNG and general mapped channels remain open |

Only owned paths may enter a normal local checkpoint after gates. User Studio/
Router dirt stays untouched. Whole-workspace legal's existing untracked Router
ledger gap is separate from controlled-export legal. Known main/alternate pip
conflicts and optional NOT_EXECUTED subsets must not be recast as successes.
No push or remote CI claim, cloud/hardware/token/auth/TLS, vendor, tag/release or
history rewrite is part of this batch.
