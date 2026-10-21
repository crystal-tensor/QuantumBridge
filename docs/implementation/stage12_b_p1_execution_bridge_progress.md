# Stage 12-B P1 Native Circuit And Instruction Execution Bridge

Date: 2026-10-22 (Asia/Shanghai). Baseline main HEAD
e6eac726fbd5446d3ba8b4c5fe1c2f4fb7897613. Full independent Qiskit/PennyLane core
functional replacement remains ACTIVE / INCOMPLETE; C3 remains PARTIAL.
This is a bounded actual execution slice, not production or whole-SDK parity.
No push, remote CI, real hardware, credential, vendor, tag/release or history
rewrite. Protected user Router/Studio dirt is not part of this slice.

## Scope And Classification

The native class is Circuit, not a newly introduced QuantumCircuit facade;
Instruction exists, but a universal Gate class is not added. The existing IR
represents binary wires, not arbitrary qudits. A length-eight state partitioned
as (2,4) must not be silently interpreted as three qubits.

| Surveyed path | Before this slice | Action |
| --- | --- | --- |
| Static Circuit -> Operator.from_circuit | EXISTING_CORRECT for sampled standard/rotation/custom/composite/phase/order paths | Reuse matrix columns and gate kernels, no new engine |
| Static Circuit -> Statevector/DensityMatrix.from_circuit | EXISTING_CORRECT in sampled full-complex comparisons | Reuse existing devices |
| Constructor Operator/Statevector/DensityMatrix(Circuit or Instruction) | MISSING_FUNCTION | Native typed dispatch, no upstream computation |
| Statevector/DensityMatrix.from_instruction | MISSING_FUNCTION | Native Instruction normalization then existing device |
| Statevector/DensityMatrix.evolve(Instruction) | MISSING_FUNCTION | Existing native circuit paths and strict binary guard |
| Typed mixed-radix state.to_operator | INCORRECT_GUARD | Actual projector/density numeric conversion with retained partition |
| Operator.from_circuit with terminal measurement | INCORRECT_GUARD | Reject instead of silently dropping measurement |
| Raw numeric Instruction normalization copy | Incorrect resource admission | Existing controlled configuration copy, no unadmitted deepcopy |
| Qudit Circuit/Instruction, general mapped channels | IR_UNSUPPORTED / outside scope | Guards retained, no new IR |
| Complete public layout/Gate/dynamic Statevector/error ABI | UNVERIFIED / Partial | No full parity claim |

## Public Contract Evidence

Only installed Qiskit 2.4.1 and 2.6.0 public constructors, methods and
inspect.signature calls are surveyed. No upstream implementation or test source
is read, ported or used as the production engine. Probe
/tmp/qb-stage12b-public.py, raw prefixes /tmp/qb-stage12b-public241 and
/tmp/qb-stage12b-public260, complete logs and independent exits 0. Literal
contract records and canonical hashes are in
[the generated artifact](../compat/stage12_b_p1_public_execution_contracts.json).
Each version records 49 outcomes after its version header. Canonical hashes are
61ab52785f800b7720f87c3c312793a4ca405e1b9b6b392900fd20c54b60a075 (2.4.1) and
cb0bba8cb28d6d0ebde55837ae3533d3e6b197f7b40c3a72b76ae9df0fe11d8f (2.6.0).
The raw records differ in Instruction signature annotations and three unbound
parameter error messages (including generated UUIDs). Sampled numeric results
agree, not every signature/error byte or all API inputs.

Public Statevector.from_instruction and DensityMatrix.from_instruction are real
APIs, as are Circuit/Instruction constructors and evolve inputs. Public
Statevector.from_circuit exists; public DensityMatrix.from_circuit is absent in
the sampled versions (native convenience method retained). Public qudit numeric
states/operators do not establish qudit QuantumCircuit support. Native q0-high
versus public q0-low mappings are explicit in every optional comparison,
including reversed local unitary targets and mapped instruction positions.

Native terminal-measurement Statevector construction retains its premeasurement
pure-state convention; density construction uses existing actual measurement/
reset/feedback machinery. This is not matching every public dynamic or stochastic
Statevector contract. Dynamic circuits cannot become unitary Operators. Existing
strict physical initial-density validation remains; no general nonphysical
Circuit density execution is claimed. No exact layout/exception/aliasing ABI or
all Gate subclasses is claimed. P0.2/P0.3 differential artifacts stay unchanged.

## Actual Implementation And Mathematics

Operator constructors and native Instruction execution normalize through existing
Circuit.from_instruction and use existing gate_matrix/apply_unitary/device paths.
State-to-Operator now retains ordered input/output dimensions. The pure state
conversion is the actual outer product, not a column map, normalization or a PSD
repair. It writes a retained complex128 projector without an unadmitted conjugate
matrix. Density conversion borrows its numeric buffer and keeps its existing
storage owner. Explicit new projector and density-construction outputs are
preflighted. Raw instruction metadata uses controlled native configuration copy;
the existing composite-definition copy already uses that mechanism.

Oracle A independently enumerates basis bits, embeds each gate, then multiplies
dense matrices in temporal order. Oracle B independently contracts each local
gate tensor into the state and restores the original axis order; no native
index/kernel helpers or prebuilt embedded operators are used. Both compare full
complex results, not just probabilities or equivalence up to phase. Standard
H/CX/RX/RY/RZ, custom complex numeric unitary, composite definitions, parameter
binding, noncommuting order and global phase are covered. Full/mapped/reversed/
noncontiguous targets and mixed-radix numeric projector partitions are checked.

Chain A: parameterized Circuit -> binding -> Operator -> complex initial
Statevector.evolve -> complex observable expectation. Chain B: Circuit ->
composite Instruction -> actual density execution -> nontrivial partial_trace ->
purity/expectation. The existing native partial_trace keep convention preserves
original subsystem order; a first new oracle mistakenly used keep-list order and
was corrected without changing production reduction behavior or tolerance.
The example runs real native calls independently of optional SDK imports.

## Red And Focused Recovery

Each prefix below is /tmp/qb-stage12b-, with full .log and independent .exit.

| Prefix | Actual result |
| --- | --- |
| native-red | 47 failed / 2 passed, 0.73s, exit 1 before production edits; missing constructors/Instruction execution/from_instruction and stale numeric guards |
| normalizer-red | 1 failed, exit 1; old numeric metadata deepcopy fails to raise at insufficient budget |
| terminal-measurement-red | 1 failed, exit 1; old from_circuit silently discards terminal measurement |
| first-recovery | 197 passed / 1 new oracle failure, exit 1; keep-list-order reference corrected to old native convention |
| second-recovery | 198 passed, 0.47s, exit 0 |
| expanded-focus | 63 passed / 2 failures, exit 1; added density-result preflight and corrected recovery fixture to fit real gate workspace rather than nominal output size |
| focused-main | 65 passed, 0.40s, exit 0 |
| focused-alternate | 65 passed, exit 0 |
| focused-sdkfree | 61 passed / 4 absent-Qiskit optional skips, 0.26s, exit 0 |
| native-regression | information/devices/operators/core/Aer/serialization/compiler/operator-copy resources: 1937 passed / 2 existing warnings, 12.40s, exit 0 |

The first standalone baseline/example harness launches lacked an explicit import
root and saw an unrelated installed checkout, so those receipts fail and are not
product regressions. The baseline retry also needed /tmp versus /private/tmp
realpath normalization in its origin assertion. Final gates pin PYTHONPATH=.
and record actual versions/origins; failed harness receipts are not discarded.
The corrected existing-baseline-v3 receipt is exit 0, six full-complex comparisons
on the previous P0.7 controlled production export with its actual origin asserted.
It establishes that sampled static math was already correct before this slice,
not that all Circuit APIs are complete. Example-main-v2 and example-sdkfree exit
0 with norm 0.9999999999999996, reduced purity 0.9131093670410124 and preserved
typed projector dims (2,4), trace 408 (deliberately unnormalized input).

The old mixed-radix circuit prohibition test still verifies UnsupportedFeature
before binary kernels. Its numeric to_operator prohibition alone is obsolete
after a real typed conversion exists, and is replaced by full complex/partition
checks above. No existing numerical tolerance, xfail or coverage exclusion is
weakened. Storage tests verify admission before factories, failed-ledger reuse,
root/view lifetime, strided inputs, complex64/real conversion, outside-scope known
source-owner projector and opaque managed protocol rejection. Python/NumPy
iterator/LAPACK hidden workspace is not RSS accounting or a universal foreign ABI.

## Final Gates

The first frozen candidate 9d781623a95887114904986999ec377346cb7c66 completed
SDK-free FULL (3512 passed / 559 skipped / 5 warnings, 242.21s, exit 0), compile,
controlled legal, 17-file privacy, public probes and native examples. Its main
FULL coverage then correctly terminated exit 1: 4291 passed / 3 failed / 5 skipped /
3 existing xfailed / 57 warnings, 1387.80s. All three failures are the measured
QASM2/QASM3/QPY cases in the old bilateral helper: it explicitly removed public
terminal measurements but relied on native Operator silently removing them.
The helper now asserts exact original measurement wire/bit order and native
Operator rejection, then explicitly removes terminal measurements on BOTH sides
for the unchanged full matrix comparison/tolerance. No measurement serialization
check is dropped, no xfail/skip or production rejection guard is relaxed. Production
code does not change after this finding. The failed frozen tree/receipts remain
preserved; acceptance will use a fresh unique tree with the corrected test helper.

Final candidate: /tmp/qb-stage12b-p1-final.meq38g/source, frozen full tree
58a823d8c3ecea58f88aa49e88827fccc5dc6ef4. Production subtree
e8220fbf133714336a049fe9b991014429e4e0c7 is unchanged from the failed first
candidate; final tests fd159923c7ae78a2dde74036dd391c7b9b0fcc22 and examples
897454bfa679dd00e53a742a94f7e5146b422590 include the corrected helper. Only
Git-controlled production/tests/examples are the runtime identity boundary,
not user untracked Router/example/test files or generated inventory documents.
There are 1067 controlled runtime files; frozen export and current workspace
byte comparisons finish exit 0. Matrix scripts generate inventory documents in
the disposable export; those outputs are not claimed as implemented APIs or
copied back into this commit.

Sequential driver /tmp/qb-stage12b-final-gates.py uses the final export and
prefix /tmp/qb-stage12b-r2-final-. All 26 child invocations have full .log and
independent .exit receipts. Exec session 94497 genuinely terminates exit 0 with
ALL_GATES_TERMINATED_REVIEW_RECEIPTS. This aggregate does NOT relabel the two
explicit known pip failures below as clean. No needed process remains live.

| Final receipt suffix | Actual terminal result |
| --- | --- |
| compile | compileall quantumbridge/tests/examples, exit 0 |
| legal | controlled export 4 passed, 0.11s, exit 0 |
| privacy | all 17 existing security/no-cloud/no-token files, 49 passed / 1 existing warning, 1.46s, exit 0 |
| public-qiskit241 / public-qiskit260 | 49 public observations each, exits 0; only three generated unbound-Parameter UUID messages differ from their initial per-version literal artifact |
| example-main / example-sdkfree | actual native example, identical numeric receipts, exits 0 |
| sdkfree-full | 3512 passed / 559 skipped / 5 warnings, 242.75s, exit 0 |
| main-coverage-full | 4294 passed / 5 skipped / 3 existing xfailed / 57 warnings, 1396.61s, exit 0 |
| alternate-full | 4292 passed / 5 skipped / 5 existing xfailed / 49 warnings, 484.43s, exit 0 |
| jax012 | 844 passed / 168 absent-framework skips, 35.13s, exit 0 |
| tf | 866 passed / 151 absent-framework skips, 47.53s, exit 0 |
| torch-autograd | 46 passed / 984 deselected, 14.59s, exit 0 |
| full-matrix | original complete 28-section shell, actual exit 0 |
| main-coverage-json / matrix-coverage-json | exits 0, per-file and totals equality verified |
| versions-main/alternate/sdkfree/jax012/tf | all five complete version/origin logs, exits 0; QuantumBridge resolves to this final frozen export in every one |
| pip-main / pip-alternate | exit 1 each, exact two pre-existing conflicts listed below, not clean environments |
| pip-sdkfree / pip-jax012 / pip-tf | exits 0 |

The original matrix's core FULL records 4294 passed / 5 skipped / 3 existing
xfailed / 57 warnings, 483.33s. Dev FULL records the same counts, 483.62s;
dev FULL coverage records the same counts, 1412.13s. These are repeated test
invocations, not three times as many unique native functions. Both coverage JSONs
agree per file and in totals: 28079/30976 = 90.64759814049587%, missing 2897,
excluded 68 unchanged, above the 90.6279318042121% prior baseline. Line coverage
is not an SDK/API parity percentage.

Matrix subset receipts: Qiskit 5, PennyLane 9, Aer 146 (1 warning), Nature 21,
Algorithms 26 (11 warnings), Runtime 5 offline, PennyLane-full 44, MQT 15,
TorchQuantum 17, QOS-UQCI 11 offline, Quafu 15 offline, Benchpress 19 (3 warnings),
legacy Studio backend 33 (1 warning, no UI implementation), ecosystem inventory
27 (1 warning, not implemented APIs), chemistry-core 5, chemistry-extra 30
(5 warnings), Nature-P2 5, algorithms-extra 10 (5 warnings), OpenFermion 1.
Seven absent-upstream compatibility subsets remain NOT_EXECUTED: Finance,
Optimization, Machine Learning, Dynamics, Metal, Experiments and Addons.
No missing subset is counted as passed; offline Runtime/QOS/Quafu are not real
cloud or hardware execution. Legacy Studio tests are preserved regression only.

Additional frozen composition-main/sdkfree receipts under /tmp/qb-stage12b-r2-
both exit 0 and are fully identical, including complete complex operator, initial
and evolved state, full density and reduced density arrays. Chain A dims (2,2,2),
angle .43, phase .5133333333333333, complex expectation
3.566415398158454 - .07286255615149341j; maximum dense and tensor reference errors
1.3877787807814457e-17 and 1.1188630228279524e-16. Chain B retains actual order
(0,2) for requested keep [2,0], dims (2,2), purity
.5917174240127703 - 4.920127980470387e-18j, expectation
-.03971096803364596 - 1.599198204416119e-17j; full/reduced density reference errors
8.777083671441753e-17 and 1.0103182026100664e-16. These are pure complex initial
density fixtures, not certification of all mixed/dynamic state APIs.

## Environments And Remaining Boundaries

All five use Python 3.12.6. Main uses NumPy 2.4.6, Qiskit 2.4.1, Aer .17.2,
PennyLane .44.1, JAX .7.1, TensorFlow 2.21.0, Torch 2.12.0, Autograd 1.8.0.
Alternate uses NumPy 2.4.6, Qiskit 2.6.0, Aer .17.2, PennyLane .42.3, JAX .6.2,
TensorFlow 2.21.0, Torch 2.12.0, Autograd 1.9.1. SDK-free has NumPy 2.5.4 and
none of those optional quantum/AD SDKs. Independent JAX uses NumPy 2.5.4/JAX
.12.0 only; independent TF uses NumPy 2.5.4/TF 2.21.0 only. Actual raw origins
are recorded, not inferred from executable names: main/alternate mix venv,
user-site and system packages and are NOT hermetic. Torch is system-site in
both, main Qiskit/PennyLane/Aer/Autograd are user-site. All QuantumBridge origins
are /private/tmp/qb-stage12b-p1-final.meq38g/source/quantumbridge/__init__.py.

Known main/alternate pip conflicts, exact and unchanged:

- weasyprint 68.1 requires tinycss2 >=1.5.0, installed 1.4.0.
- pyquafu .4.5 requires NumPy >=1.20.3,<2, installed 2.4.6.

Fresh whole dirty-workspace legal is separately 1 failed / 3 passed, 0.12s,
exit 1: original user untracked quantumbridge/router/core.py lacks its source
ledger entry. It is not altered, falsely attributed or deleted to green the
test. Final controlled legal is the passing distinct export result above.
Scoped private-key/AWS/save-token patterns on this batch's explicit controlled
paths return git-grep exit 1 with empty log (no hits), not a universal credential
audit. The 17-file privacy suite and source attribution remain bounded evidence.

Complete Circuit/Instruction/Gate/layout signatures, arbitrary public subclasses,
dynamic Statevector error/stochastic behavior, nonbinary circuit IR, general mapped
channels and the remaining whole Qiskit/PennyLane core families are unfinished.
Correct existing static circuit and typed numeric Operator math is reused, not
relabeled as newly written or full parity. P0.2/P0.3 mismatch artifacts are
unchanged. Studio is last. No real cloud/hardware or new-SHA remote CI is verified.

## Local Commit

The bounded slice meets the above local acceptance conditions. The following
scoped normal commit records only its explicit owned files after staged/export/
workspace runtime equality and whitespace checks; actual commit SHA and final
post-commit equality are appended in the receipt update, not guessed in advance.
