# Stage 12-A P0.5 Native State Arithmetic And Purity

Date: 2026-10-22 (Asia/Shanghai). Status: bounded native functions implemented;
fresh final frozen FULL/framework/coverage/matrix processes terminated.
Baseline HEAD: b3111bea1e6795763220221abe46ad3ee4ca8e76, documentation over actual
P0.4 code 84623f0. Full independent Qiskit/PennyLane functional replacement stays
ACTIVE / INCOMPLETE; complete classes/public compatibility and C3 remain PARTIAL.
No push, new-SHA remote CI or real cloud/hardware execution is claimed.

## Actual Functions

| Function | Actual delta |
| --- | --- |
| Statevector add/sub/neg | New native complex linear algebra, including flat equal-size/different-partition inputs and numeric column vectors; result keeps left dimensions and independent storage |
| Statevector mul/rmul/div | Existing finite arithmetic retained; introduced output/conversion admission and actual owner/root lifetimes; scalar reciprocal precision and Python zero-division behavior corrected |
| Statevector trace/purity | New squared norm / fourth-power norm, including unnormalized, zero and nonfinite inputs; no fictitious norm() method |
| Statevector inner | Existing inner product retains conjugate convention; now exact ordered dimension matching and managed numeric-buffer sanitation/conversion admission, without hidden strided flatten copies |
| DensityMatrix arithmetic | New add/sub/neg/mul/rmul/div, actual complex matrix math, no automatic normalization; vector inputs are explicitly converted mathematically through their outer product without a separate full temporary outer matrix |
| DensityMatrix trace/purity | Existing trace gains controlled numeric reads; purity fixes forced-real failure/loss and computes complex Tr(rho squared), not a Frobenius norm for arbitrary non-Hermitian input |
| Statevector to_dict | Existing export corrected to retain tiny nonzero values and drop zeros after rounding, with actual ordered labels and wide-qudit separators |
| DensityMatrix to_dict | New numeric export, ordered column|row labels and rounding/nonzero behavior |
| Both is_valid | Existing validity gains public-observed atol/rtol/None calling defaults, finite checks, stable vector norm and numeric protocol guards; density checks trace, Hermiticity and PSD with known input packing/eigenvalue admission |
| Physical density admission callers | Minimal necessary regression fix: initial-state and Set Density callers explicitly keep their original atol=1e-10 / rtol=0, not the generic query's looser defaults |

Implementation uses the existing state classes, dimensions, ownership and
ResourceScope machinery. No second simulator, facade, upstream quantum engine,
source/test port, RNG/capture/channel implementation or Studio work is included.
Known output arrays and required numeric conversions are admitted before the
first factory. Persistent outputs follow active request ownership, otherwise
the actual left source storage account. Escaped views retain their real roots.
Read-only trace/purity/inner/dictionary paths borrow strided complex numeric
buffers without full matrix products/flatten copies. Known strided density
validity packing and eigenvalue output are admitted together; unexposed NumPy/
LAPACK, scalar/iterator and Python dictionary storage are NOT measured RSS.

## Public Contracts

Only installed Qiskit 2.4.1/2.6.0 public constructors/calls and signatures were
used. No upstream implementation/tests were read or ported. Script:
/tmp/qb-stage12a-p05-public-contracts.py. Current complete v4 raw prefixes are
qb-stage12a-p05-public-v4-qiskit241 and qb-stage12a-p05-public-v4-qiskit260,
each with full .log and independent process .exit 0.

Each version has 443 records excluding the version header: 417 calls and 24
method signatures plus 2 tolerance-default records; 51 calls record exceptions.
The complete canonical record SHA256 is identical in both sampled versions:
9bca2e43f977adc99a847ea04199287758da8eee68dd8123c311f1d2ac4dae65.
Canonicalization parses the JSONL records after the version header and uses
Python json.dumps(records, sort_keys=True, ensure_ascii=True,
separators=(',', ':')), UTF-8, without a trailing newline. The earlier recorded
004cc770... digest did not retain reproducible serializer settings; this
post-commit documentation correction replaces that ambiguous receipt only.
The raw v4/final-v2 logs and all selected literal outcomes are unchanged.
That is sampled version agreement, NOT 443 passing native tests, an exhaustive
API inventory or proof of equality for all versions/inputs. Selected literal
results are in the [public contract artifact](../compat/stage12_a_p05_public_state_arithmetic_contracts.json).

The v2 coercion probe accidentally reused a vector variable, mislabeling a raw
array as Statevector. V3 fixes the harness; v4 adds the vector-norm versus
norm-square tolerance counterexample. The earlier logs remain, but only v4 is
the current complete survey. This is a probe-author error, not native product
math evidence. No old correct test or tolerance was changed to manufacture red.

- Both classes support the sampled arithmetic magic methods. Statevector trace
  and purity exist, but norm() does not. DensityMatrix.inner() does not exist.
  No guessed method is introduced.
- Public add/sub use equal total size and keep the left dims; inner requires
  matching ordered partitions. Raw-column and density/vector conversion cases
  are separately recorded rather than equating subsystem structures.
- Statevector trace/purity return float64; DensityMatrix returns complex128,
  including a non-Hermitian case with purity approximately 0.63 - 0.1j. Native
  functions preserve these numerical types and complex components.
- Public validity defaults are atol=1e-8 and rtol=1e-5; vector validity compares
  norm to one, while density compares trace and physical conditions. The public
  sample norm=1+9e-6 is valid as a vector but its outer density fails trace-one.
- Native invalid negative/nonfinite tolerances are explicitly rejected rather
  than copying the public sample's permissive/warning behavior. Complete mutable
  upstream tolerance-mixin configuration remains UNVERIFIED / not implemented.
- Observed public DensityMatrix minus a vector equals addition of its outer
  product; native subtraction subtracts the converted matrix. Negation before
  conversion is a mathematically consistent interpretation of those black-box
  outcomes, NOT a verified claim about upstream implementation internals.
  This is an explicit Partial Public Compatibility boundary, not an assertion
  of an upstream defect or a hidden relabeling as exact parity.
- Native builtin numeric list subtraction is supported; sampled public list
  subtraction raises TypeError. Native error classes and strict managed foreign
  protocol rules are not a complete external-object/public exception ABI.
- Public tiny values survive unrounded export, zeros vanish after rounding,
  wide mixed labels use commas and density keys are column|row. Optional native
  comparisons explicitly reverse public dimension metadata, not native wires.
- Native empty-register dictionary labels 0 and 0|0 remain a deliberate native
  extension; sampled public to_dict raises ValueError. Native dict probabilities
  and DensityMatrix shape-tuple dim conventions are unchanged.

P0.2/P0.3 PUBLIC_DIFFERENTIAL_MISMATCH artifacts and their correct evolution
math remain unchanged; no new arithmetic path erases that compatibility gap.

## Mathematics And Composition

Oracle A uses explicit independent NumPy vector/matrix algebra, inner product
and trace-square. Oracle B uses known normalized diagonal spectra and unitary
conjugation, including coherent complex Hermitian matrices; purity equals the
sum of squared spectral weights. Neither reuses production helpers.
Dimensions cover qubit/qutrit/qudit, (2,4), (3,2), (2,3,2), distinct same-product
partitions, large digit labels, scalar registers, strided arrays, unnormalized
and nonfinite data. Hermitian/PSD tests do not silently project invalid inputs.

Three actual native chains pass:

1. Basis -> scalar -> addition -> inner -> expectation: coherent qutrit
   (|0> + i|1>)/sqrt(2), norm squared 1, diagonal expectation 0.
2. Statevectors -> densities -> weighted mixture -> purity -> partial_trace ->
   expectation: weights 0.3/0.7, purity 0.58, diagonal expectation -0.4. This is
   not coherent amplitude addition, whose pure outer product has purity 1.
   This particular fixture is one qutrit: keep=(0,) retains the whole register,
   not a new nontrivial dimensional-reduction proof. Existing mixed-radix
   partial-trace tests cover actual subsystem removal separately.
3. from_int -> tensor -> arithmetic -> density -> mapped nonunitary evolve ->
   local expectation, checked against an independent whole-system matrix
   contraction without renormalization.

## Genuine Red And Recovery

All prefixes are under /tmp, each with full .log and independent .exit.

| Prefix qb-stage12a-p05- | Actual evidence |
| --- | --- |
| initial-native-red | 202 failed / 34 passed / 1 divide warning, 1.04s, exit 1; missing arithmetic/trace/purity/export and actual partition/admission gaps; existing correct slices were regressions, not called new implementations |
| first-native-recovery | 8 failed / 228 passed, 0.71s, exit 1; introduced 1x1 density matrix misclassified as a column vector, creating a second outer product |
| corrected236-native-focus | 236 passed, exit 0; fixed the genuine operand-kind ambiguity, not a tolerance/test change |
| information-regression | 1391 passed / 1 existing Aer warning, 8.83s, exit 0; before later added protocol/physical-admission assertions |
| foreign-inspection-red | 2 failed / 236 deselected, 0.17s, exit 1; managed isinstance consulted an opaque __class__ property |
| expanded-native-focus | 272 passed, 0.73s, exit 0 after exact managed-type discrimination |
| final272-alternate-focus | 272 passed, 0.72s, exit 0 |
| final272-sdkfree-focus | 264 native passed / 8 absent-Qiskit reference skips, 0.49s, exit 0 |
| expanded-native-regression | 1 failed / 2357 passed / 1 skip / 2 existing warnings, 126.29s, exit 1; the unchanged device assertion caught relaxed physical-state admission after query tolerance defaults changed |
| physical-admission-red | 4 failed / 278 deselected, 0.17s, exit 1; narrowed both initial/replacement density routes, managed/unmanaged |
| final282-main-focus | 282 passed, 0.81s, exit 0 after explicit strict tolerance at the two callers |
| final282-alternate-focus | 282 passed, 0.89s, exit 0 |
| final282-sdkfree-focus | 268 native passed / 14 absent-Qiskit reference skips, 0.55s, exit 0 |
| corrected-expanded-native-regression | 2368 passed / 1 conditional skip / 2 existing warnings, 127.01s, exit 0; strict physical admission restored with existing assertions untouched |
| fraction-regression-red | 6 failed / 282 deselected, 0.26s, exit 1; scalar Number inputs became NumPy object-dtype ufunc errors, including a verified preexisting Statevector Fraction input |
| final288-main-focus | 288 passed, 1.13s, exit 0 after unmanaged non-native Number conversion |
| final288-alternate-focus | 288 passed, 1.03s, exit 0 |
| final288-sdkfree-focus | 274 native passed / 14 absent-Qiskit reference skips, 0.65s, exit 0 |
| refreeze-expanded-native-regression | 2374 passed / 1 conditional skip / 2 existing warnings, 139.46s, exit 0 after the Number fix |

### Superseded First Freeze

The first freeze cc3c2f7b0fcc4ae238aa575d539486cb07021a54 and v1 driver started
before a supplemental preexisting Number-input check. P0.4's controlled export
executes Statevector times Fraction(1,2), as does installed public Qiskit; P0.5
instead raised a NumPy object-output casting error. Six narrowed cases expose
the three existing vector operations and analogous new density operations.
Unmanaged non-native Number values now convert to a numeric complex scalar
after reciprocal evaluation, preserving NumPy scalar reciprocal precision.
Managed foreign-protocol rejection is unchanged. This is a real compatibility
regression fix, not a new feature or a reason to weaken assertions.

The owned v1 SDK-free pytest PID/parent were verified before deliberate SIGTERM
for this confirmed defect. That gate records exit -15; driver session 37853
terminated exit 241. Its earlier compile/legal/privacy/public receipts and
interrupted FULL are superseded, NOT final acceptance of corrected code. This
was not an observation timeout or a restart on a stale lock. The archived first
tree remains. A new final tree and v2 gate prefixes must rerun every required
gate after the Number fix; no old-tree green result is reused.

The existing device test and physical tolerance were retained. No correct old
assertion, numerical tolerance or coverage exclusion was weakened. The corrected
expanded regression terminated with exit 0; frozen final gates remain separate.

## Final Frozen Gates

The completed designated-conversation review on 2026-10-22 permits freezing the
reported boundaries, not final acceptance or an independent source audit. Its
last checks map to existing tests: complex/unnormalized algebra and purity; the
unchanged strict physical-admission assertion plus four narrowed red cases;
and explicit Public Partial/Unverified coercion/export/tolerance/foreign ABI.
No duplicate test or extra functionality is added for the reminder. It requests
the already saved P0.5 Tasks 10-12 unchanged, with all processes terminal before
scoped local commit and no cloud/credentials/Studio/Router/push/vendor/history work.

### Received Freeze Reminder

确认：Stage 12-A P0.5 已具备进入最终冻结门禁的条件。建议保留现有 native 数学语义和
明确的公开兼容差异，不再扩展本批功能。本判断仅依据你的执行报告，不代表独立源码审计，
也不是 P0.5 最终验收。

关键数学与兼容边界：Statevector/DensityMatrix 加减、标量运算有原生数学与专项测试证据；
Statevector trace=norm^2、purity=norm^4 与未归一化态代数定义一致；DensityMatrix
purity=Tr(rho^2) 保留非 Hermitian 输入的复数结果，合理；is_valid() 公开默认容差已隔离
旧 Device 严格物理校验，处理合理；mixed-radix 左操作数维度保留，flat 同大小运算与
partition 等价明确区分；DensityMatrix - Statevector 的 native 数学有定义，Public
Compatibility 仍 Partial；外部协议、可变 tolerance mixin 继续 Partial/Unverified。

特别确认 DensityMatrix - Statevector：建议保留当前 native 行为，不为复制尚未厘清的
公开 coercion 过程而改写核心减法。当右操作数为 |psi> 时，原生语义为 rho-|psi><psi|。
如果公开行为表现为先取负振幅再构造外积，则因 (-|psi>)(-<psi|)=|psi><psi|，它可能
产生与上述减法不同的结果。分别记录 NATIVE_MATH_VERIFIED（明确数学定义、独立 oracle）
与 PARTIAL_PUBLIC_COMPATIBILITY（公开行为不同，尚未完整复现）。不推断 Qiskit 内部源码
实现，也不将差异称为上游错误。一般 DensityMatrix 减法是线性代数运算，结果不一定是
合法物理密度矩阵；不应自动投影 PSD 或归一化。

冻结前最后三项确认，无需新功能，只核对现有测试：

1. 复数代数：负号、复数标量、非 Hermitian purity、未归一化 Statevector trace/purity
   缩放，不无依据截断虚部。
2. 旧 Device 校验隔离：公开风格 is_valid 默认容差不能放松初始化和 SetDensity 严格检查，
   四条已报告红灯及原有断言保留。
3. 兼容差异完整保留：Density-State、list subtraction、zero-register to_dict、tolerance/
   foreign ABI 等不因专项通过而标为完整公开对等。

如果现有 282 条专项与 2368 条广域已覆盖这些要求，直接冻结，不新增重复测试。按已保存
P0.5 Task 10-12 执行：冻结唯一 production/tests/examples 树；SDK-free FULL、main FULL
+ explicit coverage、alternate FULL；独立 JAX/TF、Torch/Autograd；原完整 28 段 matrix
取得 shell exit；compileall、controlled legal、privacy/security、no-token/no-vendor、
五环境 version/origin/pipcheck；核对 frozen/export/workspace/staged/committed；全部必要
门禁结束后仅 stage P0.5 的 11 个归属文件，正常本地 commit 并报告 SHA。

Coverage 基线 90.49588122293491%，excluded 68 不增加。真实回归要留日志、最小修复、
重新冻结，不沿用旧树结果。保留用户 Studio/Router，分开报告 whole-workspace/controlled
legal。不 push/auth/TLS/token/云硬件/vendor/tag/release/history rewrite。立即冻结 P0.5
并开始同树完整门禁；本批尚未通过最终验收，完整 native full functional replacement
仍 ACTIVE / INCOMPLETE，C3 PARTIAL，Studio 最后。

### Actual Final Freeze And Terminal Gates

Final v2 runtime tree: e6f261f588ea5ef3086dd48ced00549774a0d4e6. Separate index:
/tmp/qb-stage12a-p05-v2-candidate.2sjeWl/index; immutable source export:
/tmp/qb-stage12a-p05-v2-candidate.2sjeWl/source. Production subtree:
c69bbb070e7430d27f6af47975b3ad3c38612d7e; tests subtree:
ad320442a59a4c44aa7155ffbb03a548a9792f5b; examples subtree:
bc98969f13dab27017074f4e40efdfc98d623c62. Both source/export runtime equality
checks exit 0. Eleven owned files are in the private index; the normal index
stays empty during gates. Runtime/tests/examples will not change during this
final pass; only report/ledger receipt text may be updated.

Driver /tmp/qb-stage12a-p05-v2-gates.py, session 62593, terminates exit 0 with
ALL_GATES_TERMINATED_REVIEW_RECEIPTS. Each gate has its own complete
/tmp/qb-stage12a-p05-v2-NAME.log and independent .exit. No v1 or P0.4 result is
reused as final acceptance. Main/alternate pip checks are explicit allowed
failures in this driver, not silently clean environments.

| Final v2 gate suffix | Actual terminal result |
| --- | --- |
| compile | compileall quantumbridge/tests/examples, exit 0 |
| legal | Controlled export: 4 passed, 0.11s, exit 0 |
| privacy | 17 security/privacy files: 49 passed / 1 existing warning, 1.59s, exit 0 |
| public-v4-qiskit241 / public-v4-qiskit260 | Both reporters exit 0; each 443 records / 417 calls / 51 exception outcomes, not native pass counts |
| sdkfree-full | 3302 passed / 507 missing-optional skips / 5 warnings, 255.83s, exit 0 |
| main-coverage-full | 4032 passed / 5 skipped / 3 existing xfailed / 57 warnings, 1446.02s, exit 0 |
| alternate-full | 4030 passed / 5 skipped / 5 existing xfailed / 49 warnings, 493.02s, exit 0 |
| jax012 | Independent JAX 0.12: 844 passed / 168 skipped, 37.39s, exit 0 |
| tf | Independent TensorFlow: 866 passed / 151 skipped, 50.14s, exit 0 |
| torch-autograd | 46 passed / 984 deselected, 14.91s, exit 0 |
| full-matrix | Original unmodified 28 sections, actual shell exit 0; seven missing-dependency subsets NOT_EXECUTED |
| main-coverage-json / matrix-coverage-json | Both exits 0; per-file results and totals identical, 27992/30889 = 90.62125675806922%, missing 2897 / excluded 68 |
| versions-main / alternate / sdkfree / jax012 / tf | All five version/import-origin reporters exit 0 and import QuantumBridge from the frozen export |
| pip-main / pip-alternate | Both exit 1: exactly the two preexisting conflicts below |
| pip-sdkfree / pip-jax012 / pip-tf | All three exit 0, no broken requirements found |
| scoped-secret-patterns | git grep exits 1 with a zero-byte output log: no matches for the scoped patterns, not a universal credential audit |

Coverage increases from 27794/30713 = 90.49588122293491% at P0.4, with excluded
68 unchanged. It measures exercised lines, not API/function completion.
The original matrix's core-only label uses the installed main environment;
the separate sdkfree-full gate is the actual SDK-free FULL evidence.

### Original Matrix Receipt

| Section | Actual result |
| --- | --- |
| core-only | 4032 passed / 5 skipped / 3 xfailed / 57 warnings, 491.73s |
| qiskit-extra / pennylane-extra / qiskit-aer-extra | 5 / 9 / 146 passed; Aer has 1 existing warning |
| qiskit-finance-extra / qiskit-optimization-extra / qiskit-machine-learning-extra | NOT_EXECUTED: dependencies absent |
| qiskit-nature-extra / qiskit-algorithms-extra | 21 / 26 passed; Algorithms has 11 warnings |
| qiskit-dynamics-extra / qiskit-metal-extra | NOT_EXECUTED: dependencies absent, advisory subsets |
| qiskit-runtime-extra | 5 passed, offline contracts only |
| qiskit-experiments-extra / qiskit-addons-extra | NOT_EXECUTED: dependencies absent |
| pennylane-full-extra / mqt-compat / torchquantum-compat | 44 / 15 / 17 passed |
| qos-uqci-compat / quafu-compat | 11 / 15 passed, offline only, not real service execution |
| benchpress-compat / studio-backend-api / ecosystem-inventory | 19 / 33 / 27 passed; 3 / 1 / 1 warnings; existing Studio regression only, no Studio edits, inventory is not implementation coverage |
| dev | FULL 4032 passed / 5 skipped / 3 xfailed / 57 warnings, 492.03s; separate FULL coverage 4032 passed / 5 skipped / 3 xfailed / 57 warnings, 1441.25s |
| chemistry-core / chemistry-extra / qiskit-nature-p2-extra | 5 / 30 / 5 passed; chemistry-extra has 5 warnings |
| algorithms-extra / openfermion-extra | 10 / 1 passed; algorithms-extra has 5 warnings |

All runtimes are Python 3.12.6. Main uses NumPy 2.4.6, Qiskit 2.4.1,
PennyLane 0.44.1, Aer 0.17.2, JAX 0.7.1, TF 2.21.0, Torch 2.12.0 and Autograd
1.8.0. Alternate uses Qiskit 2.6.0, PennyLane 0.42.3, JAX 0.6.2 and Autograd
1.9.1, with the other reported versions unchanged. Both use mixed venv/user/
system import origins, NOT hermetic environments. SDK-free uses NumPy 2.5.4
without quantum SDKs or the four AD frameworks. Independent JAX/TF environments
also use NumPy 2.5.4 and only their respective JAX 0.12.0 / TF 2.21.0 framework.

Fresh main/alternate pip failures are exactly: WeasyPrint 68.1 requires
tinycss2>=1.5.0 but 1.4.0 is installed; pyquafu 0.4.5 requires NumPy<2 but
2.4.6 is installed. No environment repair, installation, credential or cloud
access is performed. These failures and the seven unexecuted subsets remain
open, not reclassified as pass or production support.

The native composition probe qb-stage12a-p05-composition-native also exits 0:
coherent trace 0.9999999999999998 / expectation 0; mixture trace 1 / purity 0.58 /
reduced expectation -0.39999999999999997; arithmetic mixed-state trace
1.3228427124746187; nonunitary evolved trace 3.7913708498984753 and local
expectation -2.7913708498984753 (all imaginary components zero in this fixture).
The independently checked nonunitary workflow is not silently renormalized.

Fresh whole-workspace legal qb-stage12a-p05-workspace-legal has 1 failed /
3 passed in 0.15s, exit 1, solely the existing user untracked Router source-ledger
gap. No user source cleanup or invented provenance resolves it. Controlled
export legal is a separate, narrower receipt, not whole-workspace acceptance.

### Commit Boundary

After all required processes terminated, source/export runtime equality again
exits 0 against the final v2 tree. Final receipt documentation is the only later
change; FULL results apply to identical production/tests/examples, not a claim
that later report text existed in the tested export.

Normal local code commit: 87076d532084f993842859318802ef8155455776,
`feat: implement native state arithmetic and purity`, exactly eleven owned
paths, 3862 insertions / 51 deletions. The normal staged full tree and committed
full tree both equal the finalized candidate tree
81f453ac88b7a9e71723edc243aa7b55ad87025b. Finalized candidate export:
/tmp/qb-stage12a-p05-final-code.atFdcc/source. Its full export equality exits 0;
frozen/candidate/committed production, tests and examples subtrees are identical.
The final documentation export also passes fresh legal 4 tests / 0.23s and
privacy/security 49 tests / 1 existing warning / 1.75s, both exits 0, with
/tmp/qb-stage12a-p05-final-doc-{legal,privacy}.log and independent .exit files.
Fresh final v2 public logs compare byte-identical to the earlier complete v4
logs in each version. No gate process needed for this slice remains live.

This post-commit SHA receipt and the next designated-conversation task are
documentation only, not another runtime change or a second FULL acceptance.
Existing user Studio/Router changes remain unstaged. No push/auth workaround,
new-SHA remote CI, tag/release, vendoring or real hardware execution is claimed.

### Designated Conversation Follow-Up

The actual commit, complete terminal receipts, real Fraction refreeze and all
known limits were sent to the authorized conversation. Its completed response
accepts the reported bounded slice only, explicitly not an independent source/
log/CI audit. The full next P0.6 Tasks 0-11, including the final report and
closing execution paragraph, are saved in the
[execution prompt](stage12_a_native_state_api_execution_prompt.md#stage-12-a-p06-received-execution-prompt).
It requires first proving an actual subsystem permutation/reduction gap;
already-correct functions must not be rewritten. If none is found, report
NO_NEW_FUNCTIONAL_GAP rather than inventing an API or a false feature commit.
No P0.6 functionality or acceptance is claimed by this P0.5 receipt.
The first completed-marked UI snapshot exposed only Tasks 0-10; a later full
snapshot revealed Task 11 and the closing paragraph. These were read and saved
without asking for a duplicate regenerated prompt. This corrects the earlier
UI-completeness report, not the product's numerical or gate evidence.

## Remaining Goal

This is not complete Statevector/DensityMatrix/Operator/general-channel or
Qiskit/PennyLane parity. General channels, RNG/analysis/synthesis, full public
configuration/coercion, circuits/library/transpilation/primitives/providers,
all algorithms/industry functions, full QNode/devices/measurements/transforms/
gradients/templates/qchem/interfaces/plugins/resources/kernels/qnn/qcut/shadows
and authorized real hardware remain incomplete or unverified. Full independent
native replacement stays ACTIVE / INCOMPLETE and C3 PARTIAL; Studio stays last.
