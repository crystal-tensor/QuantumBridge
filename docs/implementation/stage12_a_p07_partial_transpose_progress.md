# Stage 12-A P0.7 Native DensityMatrix Partial Transpose

Date: 2026-10-22 (Asia/Shanghai). Status: actual native method implemented;
bounded slice validated by terminal fresh frozen FULL/framework/matrix gates.
Baseline HEAD ac34b6d79fc00291f72ea132248c822895057a74, main branch. No push or
new-SHA remote CI is claimed. Full independent Qiskit/PennyLane functional
replacement remains ACTIVE / INCOMPLETE; complete state classes/public parity
and C3 remain PARTIAL. Studio stays last and no real cloud/hardware is executed.

## Actual Function

`DensityMatrix.partial_transpose(qargs)` is now a real method on the existing
native class. For every selected subsystem it exchanges the row and column
mixed-radix digits. It does not conjugate, normalize, project PSD or build a
full-system superoperator. The result retains the actual ordered dimension
partition and uses independent complex128 storage. Native q0 remains the
highest radix; DensityMatrix.dim remains the existing shape tuple. No invented
Statevector partial-transpose, general permutation, channel, negativity or
second simulation API is introduced. Correct reverse/partial_trace are unchanged.

Actual entry: `rho.partial_transpose([0, 2])` for a density with dims (2,3,2).
Targets are native subsystem positions, not flat matrix row numbers.

The only production path changed is information/density_matrix.py. It reuses
the existing state-data validation, known conversion/output admission, native
basis digits/index functions and retained ndarray ownership. The mathematical
index permutation is independently authored; no upstream implementation or
test source is read, copied or used as the production engine. NumPy and the
existing native state classes perform all production computation.

## P0.6 Evidence-First Audit

The [preceding audit](stage12_a_p06_subsystem_gap_audit.md) finds no new native
mathematical gap in the existing reverse/reduction functions as surveyed, with
432 assertion groups in main, alternate and SDK-free runtimes. They are not
new pytest cases or complete public API proof. A first audit harness failed to
catch a sampled public all-traced Statevector exception; that harness was
corrected without touching production mathematics. Public trace-all/one-level
return and metadata differences stay explicit. P0.6 does not fabricate a
feature commit or rewrite correctly implemented functions.

That audit identifies this real missing public method instead. The designated
conversation's complete P0.7 Tasks 0-13 and closing instructions are saved in
[the execution prompt](stage12_a_native_state_api_execution_prompt.md#stage-12-a-p07-received-execution-prompt).
An initial completed-marked UI view omitted the last tasks; the requested
supplement and later-visible original tail were both read. This was UI/retrieval
handling, not a product mathematical red or an independent external audit.

## Public Contracts

Only installed Qiskit 2.4.1/2.6.0 public constructors, methods and signatures
are inspected. The complete v2 probe is
/tmp/qb-stage12a-partial-transpose-public.py; raw per-version prefixes are
/tmp/qb-stage12a-pt-public-v2-241 and /tmp/qb-stage12a-pt-public-v2-260, each
with complete .log and independent .exit 0. The older 130-record survey lacks
later metadata/geometry coverage and is not the current complete survey.

Each complete version has 196 records excluding its version header: 2 method
signatures, 183 regular calls and 11 edge calls. There are 35 exception outcomes
(including 30 None-target cases); 153 normal numerical calls match the explicit
independent tensor definition. These are reference observations, NOT native
passing-test counts. The sampled complete records are identical in both
versions, not proof of equality for every input/version. Canonical full-record
SHA256: 4207d5d5e3316bd221a5a0da19d1559f55380ecc4e8d1c34dbfffe392c660062.
Canonicalization: parsed JSONL after header, Python json.dumps with sort_keys=True,
ensure_ascii=True, separators=(',', ':'), UTF-8, no trailing newline. Selected
literal results are in the [public artifact](../compat/stage12_a_p07_public_partial_transpose_contracts.json).

- DensityMatrix.partial_transpose is a real public class method; Statevector
  does not expose it in these versions. No guessed method is added.
- Valid target order has the same mathematical result, with metadata translated
  explicitly between native high-radix q0 and public low-radix q0.
- Empty targets perform identity; all targets perform ordinary transpose, NOT
  adjoint. Complex non-Hermitian/unnormalized matrices are not silently repaired.
- Public empty/all cases may share input storage. Native always returns its own
  retained output. That deliberate copy/ownership distinction is Partial Public
  Compatibility, not universal public aliasing parity.
- Public samples accept duplicate, bool and certain out-of-range targets, while
  native rejects these under its established strict target validation. Negative,
  float, string, scalar, generator and None exception/return contracts are also
  recorded; exact arbitrary-object/error ABI is not completed.
- Managed targets require explicit builtin tuple/list numeric sequences, rejecting
  opaque iteration before callbacks. Unmanaged iterable extension and optional
  public ndarray targets are not a promise of matching every foreign protocol.
- DensityMatrix partition/num_qubits observations in the 48 optional comparisons
  match after explicit wire conversion; native shape-tuple dim differs from the
  public scalar dim. Historical other-state metadata and P0.2/P0.3 differential
  artifacts remain untouched, not relabeled by this function's passing tests.

## Independent Mathematics And Actual Calls

Oracle A explicitly enumerates full row/column basis digits with independently
used NumPy indexing and exchanges only selected digits. Oracle B independently
reshapes a 2n-axis tensor, transposes selected row/column axes and restores the
matrix. Neither uses production dimensions/stride helpers. Complete complex
matrices are compared exactly; trace/purity/spectra are additional checks, not
substitutes for the complete comparison.

Sixteen geometry/target configurations cover single qubit, qutrit, qudit,
(2,2), (3,2), (2,4), (2,3,2), (3,2,4), one-level and zero-register states;
empty/full, middle, noncontiguous and reversed target selections. Four distinct
matrix kinds are pure outer products, complex coherent mixtures, arbitrary
non-Hermitian matrices and unnormalized pure matrices, with contiguous and
strided inputs. Involution, trace/trace-square invariance, ordinary full
transpose, Hermiticity where applicable and disjoint target composition are
checked. Input buffers stay unchanged and outputs do not alias them.

Chain A actually executes Statevector -> DensityMatrix -> partial_transpose ->
NumPy eigenvalue verification for three distinct Schmidt-weight/phase/scale
fixtures. Spectra are derived from those input coefficients, independently
recomputed from the reference full matrix, and include genuine negative values.
No negativity function is introduced or hidden PSD correction allowed.
Chain B executes mapped nonunitary Operator.evolve -> DensityMatrix ->
nontrivial partial_trace -> partial_transpose -> local complex expectation,
preserving dims (3,4) and comparing the complete reduced/transposed matrix
with an independent full-system numeric contraction. Numeric receipts follow
the actual composition command, not a claimed hardware/algorithm benchmark.

The frozen-export composition-main and composition-sdkfree commands each
terminate exit 0 and return the same four receipts. For Schmidt probability
0.5 / scale 1, the negative eigenvalue is -0.5000000000000001; for probability
0.7 / phase i / scale 1 it is -0.45825756949558405; probability 0.2 / phase -i /
scale 2 gives -1.5999999999999999 and trace 3.9999999999999996. Chain B retains
dims (3,4), trace 0.9356617412048445 + 1.7580269153782645e-18j and actual complex
expectation 0.2642173896102946 + 0.9055559385959111j, not an automatically
normalized or forced-real output. The test independently verifies these
complete matrices and derived values, not just the printed scalar receipts.

## Red And Recovery

Each prefix below is under /tmp with full .log and independent .exit.

| Prefix qb-stage12a-p07- | Actual terminal result |
| --- | --- |
| native-red | 197 failed, 1.11s, exit 1; all lack the actual partial_transpose entry, AttributeError, before production edit |
| first-recovery | 197 passed, 0.49s, exit 0 after the 24-line native method and reuse imports |
| focused-main | 197 passed, 0.46s, exit 0; explicit Hermiticity assertion also retained |
| focused-alternate | 197 passed, 0.49s, exit 0 |
| focused-sdkfree | 149 passed / 48 absent-Qiskit reference skips, 0.32s, exit 0 |
| native-regression | information/devices/operators/Aer: 1501 passed / 2 warnings, 10.98s, exit 0 |
| workspace-legal | 1 failed / 3 passed, 0.15s, exit 1, solely the existing unrelated user Router source-ledger gap |

The 197 focused tests comprise 149 dependency-free cases and 48 optional public
comparisons. No old correct assertion, tolerance or coverage exclusion was
weakened. No P0.7 production or test-author recovery defect was observed in this
focused pass; it is not an assertion that all future FULL gates already pass.

## Resources And Boundaries

Known input conversion and output complex storage are pre-admitted as one group,
before either factory. Strided complex buffers are read through basic numeric
indices without a full packing or superoperator temporary. Persistent output
storage follows the active ResourceScope or, on the tested native complex
source-buffer path outside a scope, its actual storage owner. This is not a
completed arbitrary caller-replaced-buffer/external-protocol accounting ABI.
Escaped views retain the original output root until the last view dies.
Tests verify exact conversion/output peaks, factory-before-admission denial,
valid -> overbudget -> valid recovery, source/active-owner separation and input
preservation. Numeric ndarray subclasses are viewed as explicit base numeric
storage; opaque target iteration, foreign receivers and object dtype reject
before callbacks. Python digit/index containers and scalar/NumPy interpreter
workspaces are not a measured RSS bound, as the existing ledger receipt states.

## Final Frozen Gates

Frozen tree: 03424712bedfb9268f1f93e0150b01afeda43fbf. Separate index:
/tmp/qb-stage12a-p07-candidate.RoknbA/index; source export:
/tmp/qb-stage12a-p07-candidate.RoknbA/source. Production subtree:
7d9830110ddd99aaee3b9061175e8dc47e34c402; tests subtree:
6c51188347f421a8c54d2f1abbe8202156741b31; unchanged examples subtree:
bc98969f13dab27017074f4e40efdfc98d623c62. Controlled workspace/export runtime
equality checks exit 0. These checks cover the frozen Git paths, not a claim
that the dirty workspace has no additional user files. Exactly ten owned paths
are in the separate candidate index; the normal index stays empty during gates.
No production/test/example bytes change after freezing; later receipt text is
documentation only, not falsely described as the same full documentation tree.

Driver /tmp/qb-stage12a-p07-final-gates.py, session 78096, terminates exit 0 and
prints ALL_GATES_TERMINATED_REVIEW_RECEIPTS. Every command has its own complete
/tmp/qb-stage12a-p07-final-NAME.log and independent .exit. Main/alternate pip
failures are explicitly accepted only for the exact two known conflicts below,
not classified as clean environments. No necessary gate process remains live.

| Final gate suffix | Actual terminal receipt |
| --- | --- |
| compile | compileall quantumbridge/tests/examples, exit 0 |
| legal | Controlled export 4 passed, 0.12s, exit 0 |
| privacy | 17 privacy/security files, 49 passed / 1 existing warning, 3.13s, exit 0 |
| public-v2-qiskit241 / public-v2-qiskit260 | Both exits 0, complete raw logs byte-identical to the recorded v2 probes per version; 196 records each, not native pass counts |
| composition-main / composition-sdkfree | Both exits 0, same four actual native numerical receipts listed above |
| sdkfree-full | 3451 passed / 555 absent-optional skips / 5 warnings, 255.25s, exit 0 |
| main-coverage-full | 4229 passed / 5 skipped / 3 existing xfailed / 57 warnings, 1439.29s, exit 0 |
| alternate-full | 4227 passed / 5 skipped / 5 existing xfailed / 49 warnings, 495.71s, exit 0 |
| jax012 | Independent JAX 0.12, 844 passed / 168 skipped, 37.96s, exit 0 |
| tf | Independent TensorFlow, 866 passed / 151 skipped, 50.21s, exit 0 |
| torch-autograd | 46 passed / 984 deselected, 15.10s, exit 0 |
| full-matrix | Original unmodified 28 sections, actual shell exit 0; seven missing-dependency subsets NOT_EXECUTED |
| main-coverage-json / matrix-coverage-json | Both exits 0; per-file and total results identical: 28014/30911 = 90.6279318042121%, missing 2897 / excluded 68 |
| versions-main / alternate / sdkfree / jax012 / tf | All five exit 0; QuantumBridge imports from the frozen export in every environment |
| pip-main / pip-alternate | Both exit 1, exactly the two known conflicts below |
| pip-sdkfree / pip-jax012 / pip-tf | All three exit 0, no broken requirements found |
| scoped-secret-patterns | git grep exit 1, zero-byte log, no matches in the selected patterns/owned paths; not a universal credential audit |

No old P0.5 green result substitutes for P0.7. Coverage rises from
27992/30889 = 90.62125675806922% to 28014/30911 = 90.6279318042121%, exclusions
68 unchanged. Exercised source lines are not API/function completion.

### Complete Original Matrix

| Section | Actual outcome |
| --- | --- |
| core-only | 4229 passed / 5 skipped / 3 xfailed / 57 warnings, 493.78s; installed main environment, not the separate actual SDK-free gate |
| qiskit-extra / pennylane-extra / qiskit-aer-extra | 5 / 9 / 146 passed; Aer 1 warning |
| qiskit-finance-extra / qiskit-optimization-extra / qiskit-machine-learning-extra | NOT_EXECUTED: dependencies absent |
| qiskit-nature-extra / qiskit-algorithms-extra | 21 / 26 passed; Algorithms 11 warnings |
| qiskit-dynamics-extra / qiskit-metal-extra | NOT_EXECUTED: absent advisory dependencies |
| qiskit-runtime-extra | 5 passed, offline contracts only |
| qiskit-experiments-extra / qiskit-addons-extra | NOT_EXECUTED: dependencies absent |
| pennylane-full-extra / mqt-compat / torchquantum-compat | 44 / 15 / 17 passed |
| qos-uqci-compat / quafu-compat | 11 / 15 passed, offline only, not service/hardware execution |
| benchpress-compat / studio-backend-api / ecosystem-inventory | 19 / 33 / 27 passed, 3 / 1 / 1 warnings; existing Studio regression only, no Studio edits; inventory is not implementation coverage |
| dev | FULL 4229 passed / 5 skipped / 3 xfailed / 57 warnings, 493.21s; separate FULL coverage with same counts, 1447.52s |
| chemistry-core / chemistry-extra / qiskit-nature-p2-extra | 5 / 30 / 5 passed; chemistry-extra 5 warnings |
| algorithms-extra / openfermion-extra | 10 / 1 passed; algorithms-extra 5 warnings |

### Environment And Whole-Workspace Limits

All five runtimes are Python 3.12.6. Main: NumPy 2.4.6, Qiskit 2.4.1, Aer 0.17.2,
PennyLane 0.44.1, JAX 0.7.1, TF 2.21.0, Torch 2.12.0, Autograd 1.8.0. Alternate:
Qiskit 2.6.0, PennyLane 0.42.3, JAX 0.6.2, Autograd 1.9.1, other listed versions
unchanged. Both have mixed venv/user/system import origins and are NOT hermetic.
SDK-free: NumPy 2.5.4, no quantum SDKs or four AD frameworks. Independent JAX/TF
use NumPy 2.5.4 and only their respective JAX 0.12.0 / TF 2.21.0 framework.

Fresh main and alternate pip checks each fail on exactly: WeasyPrint 68.1
requires tinycss2>=1.5.0 but 1.4.0 is installed; pyquafu 0.4.5 requires NumPy<2
but 2.4.6 is installed. No package/credential/auth/TLS repair is performed.
Whole dirty-workspace legal separately records 1 failed / 3 passed / 0.15s /
exit 1, solely the existing untracked user Router source-ledger gap. Controlled
legal passes are narrower and do not resolve or supersede that failure. User
Studio/Router edits and untracked files are left untouched.

## Scoped Commit Boundary

All required processes terminated before normal staging. The finalized candidate
differs from the tested full tree only in final receipt documentation;
production/tests/examples stay identical. Normal local code commit:
cd0370b9f48112337d54b025483f938573bc8e3e, `feat: add native mixed-radix partial
transpose`, exactly ten owned files, 2057 insertions / 4 deletions.

Normal staged full tree and committed full tree both equal finalized candidate
df9720cd0d425dadf9a4638e41d77294449e742d. Final candidate export:
/tmp/qb-stage12a-p07-final-code.vbDSyb/source. Full candidate/export equality
exits 0; frozen/candidate/committed production, tests and examples subtrees are
identical, checked with actual exit 0 after commit. The final documentation
export also passes fresh legal 4 tests / 0.23s and privacy/security 49 tests /
1 existing warning / 1.76s, both exits 0, with independent
/tmp/qb-stage12a-p07-final-doc-{legal,privacy}.log/.exit receipts.

The actual code SHA receipt and any next-task transcript are documentation-only
follow-ups, not a second runtime change or evidence that post-test report text
existed in the original FULL export. No push or new-SHA remote CI is claimed.

## Designated Conversation Follow-Up

The actual code SHA, complete terminal receipts and all compatibility/environment
limits were sent to the authorized conversation. Its completed reply accepts
the reported bounded function slice, explicitly not an independent source/log
audit or full class/SDK parity. The complete next Stage 12-B P1 Tasks 0-13 and
closing execution decision are saved in the
[execution prompt](stage12_a_native_state_api_execution_prompt.md#stage-12-b-p1-received-execution-prompt).
The next scope first distinguishes existing-correct static qubit execution,
incorrect conversion guards and actual IR_UNSUPPORTED nonbinary circuits.
No new circuit IR or blind guard removal is authorized by that recommendation.
No Stage 12-B implementation/acceptance is claimed by this P0.7 receipt.

Complete State/Density/Operator/general-channel/Circuit/QNode and whole ecosystem
functionality remains incomplete or unverified. This bounded mathematical
function slice has Verified Native evidence; complete public/class parity does not.
Full Qiskit/PennyLane replacement stays ACTIVE / INCOMPLETE; C3 PARTIAL; remote
new-SHA CI NOT_VERIFIED; no credentials/real service/vendor/tag/release/history
rewrite or Studio/Router work is performed.
