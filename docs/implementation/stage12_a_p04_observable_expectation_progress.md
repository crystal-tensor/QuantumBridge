# Stage 12-A P0.4 Native Mixed-Radix Observable Expectation

Date: 2026-10-22 (Asia/Shanghai). Status: bounded native function slice validated
by fresh frozen-runtime FULL/framework/coverage/matrix gates. Baseline HEAD: d2d1d37, documentation
over P0.3 code be9d5e3. Full independent Qiskit/PennyLane replacement remains
ACTIVE / INCOMPLETE. Complete state/Operator/public parity and C3 remain PARTIAL.
No push, new-SHA remote CI or cloud/hardware execution is claimed.

## Actual Native Functions

- Statevector.expectation_value computes <psi|O|psi> using the existing ordered
  mixed-radix local action. DensityMatrix.expectation_value directly computes
  Tr(rho O) with the same local index/stride generator. No full-system embedded
  operator, separate simulator or SDK execution engine is used.
- Noncontiguous and reversed targets preserve supplied order. Qutrit/qudit and
  mixed registers use real subsystem dimensions, not binary reinterpretation.
  Typed local observables require matching input/output partitions and square
  matrices. A non-Hermitian observable returns a genuine complex value; neither
  the input state nor the intermediate action is renormalized.
- Native Operator data is borrowed, not copied through to_matrix. Existing
  strided state/observable arrays require neither flatten nor hidden matmul
  packing. Pure states allocate one D-element complex action buffer; density
  with borrowed complex buffers uses direct scalar indices and no new ndarray.
- Known native Pauli/Sparse exports, required dtype/container conversions and
  pure-state work are admitted as a group before the first matrix factory.
  Managed foreign matrix protocols and object arrays are rejected; explicit
  numeric ndarray subclasses are sanitized to base views without dispatching
  their array/ufunc/index protocols. Python/scalar iterator storage is not RSS.
- The existing full-system Statevector sparse-Pauli path remains matrix-free
  and preserves real-coefficient behavior. Complex coefficients, including a
  5e-13 imaginary coefficient, are not lost through the old real Hamiltonian
  conversion. Its managed numeric input is sanitized before the legacy vdot
  path. This is not a universal audit/closure of its older resource internals.
- Native q0-high, dict probabilities, DensityMatrix shape-tuple dim and full
  no-qargs flat numeric partition semantics are preserved. An explicit local
  numeric Operator can act on binary targets of a mixed register, but Pauli and
  SparsePauli objects remain binary-only. Managed foreign protocols are not a
  complete foreign observable ABI; unmanaged legacy protocols remain bounded
  existing behavior, not a claim of full public compatibility.

No variance method, new VQE/AD/QNode system, mapped channel engine, state RNG,
purity/arithmetic, Capture, Studio or cloud integration is introduced.

## Independent Mathematics And Real Red/Recovery

The new 183-case file tests 12 geometries on both state classes, managed and
unmanaged Hermitian/non-Hermitian values, reversed/noncontiguous targets,
nonuniform qutrit weights, six pure/density-outer geometries, unnormalized
states, actual strided buffers, zero-register/scalar and trivial subsystems,
typed invalid partitions, malformed targets, whole-budget denial, real escaped
root/view release and recovery, foreign protocols and tiny complex coefficients.

Oracle A explicitly enumerates small whole-system basis matrices independently
of production maps. Oracle B uses tensor transpose/partial trace and a separate
local trace contraction. Neither reuses the production indexing helper. A native
evolve -> density -> partial_trace -> local expectation scenario and a qutrit
finite-difference objective with analytic derivative -sin(2 theta)+2 cos(2 theta)
also pass. No correct old test, tolerance or coverage exclusion was weakened.

Each prefix below is under /tmp with a complete .log and independent .exit.

| Prefix qb-stage12a-p04- | Actual result |
| --- | --- |
| initial-native-red | 147 failed / 23 passed, 1.61s, exit 1; genuine mapped-expectation, validation and admission gaps |
| first-native-recovery | 170 passed, 0.35s, exit 0 |
| information-regression | 1193 passed / 1 existing warning, 7.75s, exit 0; before final added tests |
| expanded-native-focus | 1 failed / 180 passed, 0.40s, exit 1; new test-author fixture error: an outer product had a real input trace imaginary residual ~1e-17, incorrectly assumed exactly zero when testing 5e-13 coefficients to 5e-26 |
| final181-main-focus | 181 passed, 0.36s, exit 0; fixture changed to an exact computational basis, NOT a relaxed tolerance or numerical imaginary truncation |
| sparse-protocol-red | 2 failed / 181 deselected, 0.18s, exit 1; genuine legacy full sparse expectation dispatched a foreign ndarray vdot protocol |
| final183-main-focus | 183 passed, 0.35s, exit 0 after numeric shape/view sanitation |
| final183-alternate-focus | 183 passed, 0.38s, exit 0 |
| final183-sdkfree-focus | 171 passed / 12 absent-Qiskit reference skips, 0.23s, exit 0 |
| expanded-native-regression | 2086 passed / 1 conditional skip / 2 existing warnings, 117.35s, exit 0 |

## Installed Public Contract Evidence

Only installed Qiskit 2.4.1/2.6.0 public constructors/calls/signatures were
inspected. No upstream source/tests were read, copied or ported. Script:
/tmp/qb-stage12a-p04-public-contracts.py. V2 raw prefixes:
qb-stage12a-p04-public-v2-qiskit241 and qb-stage12a-p04-public-v2-qiskit260,
both process exit 0. Each records 182 outcomes excluding the version header,
including 84 numerical oracles with maximum error 4.440892098500626e-16 and
68 exceptions. The 12 observed version differences are mixed-Pauli TypeError
message wording only; numerical outcomes/signatures in this sample agree.
This is NOT 182 passing native tests or proof of exhaustive API equality.

The [generated public contract artifact](../compat/stage12_a_p04_public_expectation_contracts.json)
retains selected literal results and complete-probe statistics.

- Both public classes expose expectation_value but not variance(). No speculative
  variance method is introduced. Public numeric values include complex128;
  Pauli paths may return Python float. Native numeric values are complex128,
  with the existing full real sparse fast path still real, not full return ABI.
- Ordered typed input partitions matter, not just their product. Public
  Statevector sometimes accepts typed output repartitioning; DensityMatrix
  differs by target/path. Native expectation requires a dimension-preserving
  typed endomorphism, rather than copying that inconsistent acceptance.
- Public Statevector accepts a raw full 6x6 matrix on dimensions (3,2), whereas
  DensityMatrix infers (6,) and rejects the sampled call. Native legacy full
  no-qargs numeric behavior remains permitted on both, not exact public parity.
- A nonempty public register rejects sampled empty-qargs scalar actions. Native
  empty targets deliberately allow scalar action. Public true zero-register
  typed operators and explicit trivial (1,) partitions do work with matching
  targets; raw 1x1 inference to () must not be confused with a (1,) partition.
- Public duplicate/bool/negative targets have varying acceptance/exceptions;
  native targets remain distinct nonnegative integral/in-range and no-bool.
- Pauli/Sparse objects on true mixed public states fail TypeError in both
  versions, even on a binary subset. Numeric typed Operator counterparts work.
  Native Pauli objects remain binary-only; mixed numeric local action works.
- Unnormalized states/densities and tiny nonzero imaginary coefficients retain
  their mathematical scale/complex value. No normalization is inferred.

The P0.2 and P0.3 PUBLIC_DIFFERENTIAL_MISMATCH artifacts remain byte-for-byte
unchanged. New expectation does not alter correct mapped evolution to imitate
unexplained public Statevector behavior. Unsupported/UNVERIFIED subsets remain
explicit, not Supported based only on name inventories or green tests.

## Final Gate Receipts

Frozen tree: 6b5b392729bddba40c458106bc5c465139298b67. Separate index:
/tmp/qb-stage12a-p04-candidate.lZI50z/index; controlled source export:
/tmp/qb-stage12a-p04-candidate.lZI50z/source. Production subtree:
33bcbb0233c7dd73074c61dab958a916f4d1dca4; tests subtree:
2095b8d21259903c29902dded2927a7c2bf3aaaa; examples subtree:
bc98969f13dab27017074f4e40efdfc98d623c62. Source/export runtime equality exits 0.
Ten owned paths were frozen; the normal index stayed empty during gates.
Runtime/tests/examples did not change. Only report/ledger receipt text changes
after freezing, not the tested runtime. Final staging/commit proof follows below.

Fresh whole-workspace legal qb-stage12a-p04-workspace-legal: 1 failed / 3 passed,
0.13s, exit 1, on the existing untracked user quantumbridge/router/core.py source
ledger gap. No provenance is invented or user source removed to make it pass.
The separate controlled-export legal result does not hide this workspace gap.

Sequential driver: /tmp/qb-stage12a-p04-gates.py; process session 20407 terminated
with exit 0 and ALL_GATES_TERMINATED_REVIEW_RECEIPTS. No needed process is live.
Final prefixes are /tmp/qb-stage12a-p04-v1- with .log and independent .exit.
The driver explicitly allows only the two predeclared existing pip failures;
they remain failures, not reclassified passes. These are fresh P0.4 results.

| Gate suffix | Actual terminal receipt |
| --- | --- |
| compile | compileall quantumbridge/tests/examples, exit 0 |
| legal | Controlled export: 4 passed, 0.10s, exit 0 |
| privacy | 17 explicit files, 49 passed / 1 existing warning, 1.43s, exit 0 |
| public-v2-{qiskit241,qiskit260} | Both exit 0; each 182 outcomes / 84 numerical oracles / 68 exceptions, max error 4.440892098500626e-16; only 12 message differences, NOT native passing-test counts |
| sdkfree-full | 3028 passed / 493 missing-optional skips / 5 warnings, 247.42s, exit 0 |
| main-coverage-full | 3744 passed / 5 skipped / 3 existing xfailed / 57 warnings, 1428.19s, exit 0 |
| main-coverage-json | Exit 0: 27794/30713 = 90.49588122293491%, missing 2919, excluded 68 |
| alternate-full | 3742 passed / 5 skipped / 5 existing xfailed / 49 warnings, 480.99s, exit 0 |
| jax012 | 844 passed / 168 absent-other-framework skips, 38.02s, exit 0 |
| tf | 866 passed / 151 absent-other-framework skips, 50.62s, exit 0 |
| torch-autograd | 46 passed / 984 deselected, 15.12s, exit 0; selected cases only |
| full-matrix | Original 28-section script, shell exit 0; seven absent-dependency subsets NOT_EXECUTED |
| matrix-coverage-json | Exit 0, independent same 27794/30713 = 90.49588122293491%, missing 2919, excluded 68 |
| versions-{main,alternate,sdkfree,jax012,tf} | All five exit 0; QuantumBridge imported from the frozen export |
| pip-{main,alternate} | Both exit 1, only the existing WeasyPrint/tinycss2 and pyquafu/NumPy conflicts |
| pip-{sdkfree,jax012,tf} | All three exit 0, no broken requirements reported |
| scoped-secret-patterns | git grep exit 1, 0-byte log: no private-key/common GitHub/OpenAI pattern hits, not universal credential audit |

Both coverage totals exceed the previous 90.47525850539844% baseline with 68
exclusions unchanged. Line coverage is not function/API completion.

### Actual 28-Section Matrix

| Section | Actual result |
| --- | --- |
| core-only | 3744 passed / 5 skipped / 3 xfailed / 57 warnings, 478.37s |
| qiskit-extra | 5 passed |
| pennylane-extra | 9 passed |
| qiskit-aer-extra | 146 passed / 1 warning |
| qiskit-finance-extra | NOT_EXECUTED: dependency absent |
| qiskit-optimization-extra | NOT_EXECUTED: dependency absent |
| qiskit-machine-learning-extra | NOT_EXECUTED: dependency absent |
| qiskit-nature-extra | 21 passed |
| qiskit-algorithms-extra | 26 passed / 11 warnings |
| qiskit-dynamics-extra | NOT_EXECUTED: advisory dependency absent |
| qiskit-metal-extra | NOT_EXECUTED: advisory dependency absent |
| qiskit-runtime-extra | 5 passed, offline compatibility only |
| qiskit-experiments-extra | NOT_EXECUTED: dependency absent |
| qiskit-addons-extra | NOT_EXECUTED: dependency absent |
| pennylane-full-extra | 44 passed |
| mqt-compat | 15 passed |
| torchquantum-compat | 17 passed |
| qos-uqci-compat | 11 passed, offline only |
| quafu-compat | 15 passed, offline only |
| benchpress-compat | 19 passed / 3 warnings |
| studio-backend-api | 33 existing regression tests passed / 1 warning; no Studio development |
| ecosystem-inventory | 27 passed / 1 warning; inventory is not complete implementation |
| dev | FULL: 3744 passed / 5 skipped / 3 xfailed / 57 warnings, 479.77s; separate FULL coverage: same counts, 1425.35s |
| chemistry-core | 5 passed |
| chemistry-extra | 30 passed / 5 warnings |
| qiskit-nature-p2-extra | Inventory generator plus 5 passed |
| algorithms-extra | Inventory generator plus 10 passed / 5 warnings |
| openfermion-extra | 1 passed |

The core-only label uses the installed main environment, not an SDK-free venv.
The separate SDK-free FULL above is actual no-SDK proof. Matrix-generated
inventories do not establish functional/native parity or real hardware use.

### Runtime Versions And Origins

Every gate uses Python 3.12.6. Main: NumPy 2.4.6, Qiskit 2.4.1, Aer 0.17.2,
PennyLane 0.44.1, JAX 0.7.1, TensorFlow 2.21.0, Torch 2.12.0, Autograd 1.8.0.
Alternate: NumPy 2.4.6, Qiskit 2.6.0, Aer 0.17.2, PennyLane 0.42.3, JAX 0.6.2,
TensorFlow 2.21.0, Torch 2.12.0, Autograd 1.9.1. Main/alternate import from mixed
venv/user/system paths as recorded in full logs; they are NOT hermetic.
SDK-free: NumPy 2.5.4, no Qiskit/Aer/PennyLane or four AD frameworks. Independent
JAX: NumPy 2.5.4/JAX 0.12.0 only. Independent TF: NumPy 2.5.4/TF 2.21.0 only.
All five QuantumBridge origins resolve to the actual frozen source export.

Both nonclean pip checks report WeasyPrint 68.1 requiring tinycss2 >=1.5.0 while
1.4.0 is installed, and pyquafu 0.4.5 requiring NumPy <2 while 2.4.6 is installed.
No new dependency conflict, dependency change, environment cleanup or credential
operation is part of P0.4. Real Quafu execution is NOT_VERIFIED by this batch.

## Scoped Ownership And Checkpoint

Only these ten paths belong to the implementation checkpoint:

- quantumbridge/information/statevector.py
- quantumbridge/information/density_matrix.py
- quantumbridge/utils/math.py
- tests/information/test_mixed_radix_observable_expectation.py
- docs/compat/stage12_a_p04_public_expectation_contracts.json
- docs/implementation/stage12_a_p04_observable_expectation_progress.md
- docs/compat/core_parity_ledger.md
- docs/compat/stage12_a_state_api_contract_matrix.md
- docs/migration/source_migration_ledger.md
- README.md

User Studio/Router and other unrelated dirty/untracked paths are excluded.
Report/ledger receipts are documentation-only deltas over the tested freeze;
production/tests/examples equality is checked separately, not falsely claimed
as a byte-identical full tree after updating receipts. The exact scoped staged
tree is compared to its final index/export and then to the actual commit.
Final documentation legal/privacy checks are separate cheap gates, not rerun
FULL or a substitute for the actual frozen FULL/framework/matrix receipts.
No push, auth/TLS workaround, token access, cloud/hardware call, vendor, tag,
release, user-source cleanup or history rewrite is part of this checkpoint.

## Designated Conversation Clarification

The designated response completed on 2026-10-21 after the actual development
results and frozen tree were reported. It confirms no reported logic issue
requiring a stop, but explicitly is not an independent source audit or final
acceptance. Keep the frozen code and finish existing gates, not a new feature.
Its suggested scale invariant is already explicitly tested in
test_expectation_is_linear_in_non_normalized_state_weights: pure input x2 gives
expectation x4; density input x3 gives expectation x3. No repeat test or runtime
change is needed. Complete boundary/acceptance reminder is recorded below.

> 确认：根据你提供的执行报告，Stage 12-A P0.4 的实现边界总体合理，目前没有发现必须
> 停止全量门禁的逻辑问题。本次仅依据你的报告判断，不代表独立源码审计。冻结树
> 6b5b392729bddba40c458106bc5c465139298b67 仍处于验证阶段，不能提前认定 P0.4 验收完成。
>
> 需要特别保持的四个数学与兼容边界：
> 1. 非 Hermitian Observable 的复数期望。Statevector 应计算 <psi|O|psi>，
> DensityMatrix 应计算 Tr(rho O)。保留复数结果是正确的。若使用未归一化状态，
> 不应偷偷除以范数或迹。
> 2. 局部期望与 qargs 顺序。反序、非连续 qargs 必须依照实际 mixed-radix 子系统
> 顺序执行，不能在内部排序。两个独立 oracle 与两版公开数值最大差异约 4.44e-16，
> 是有力的已测数值证据，但不代表所有输入组合已覆盖。
> 3. Observable 的适用范围。局部 observable 必须是所选子系统上的维度保持型算符。
> Typed local endomorphism、empty scalar、full flat numeric 的原生行为与公开契约
> 差异应继续明确列为 Partial Public Compatibility。Pauli/Sparse 的 binary-only
> 限制也应保留，不能凭本次通用 numeric Operator 成功而宣布它们支持 mixed-radix。
> 4. 红灯与测试修正。将含约 1e-17 浮点虚部的 fixture 替换为精确基态，而没有放宽
> 容差，是合理的测试修正。应保留最初失败和修正原因，不将 fixture 错误计为生产数学缺陷。
>
> 一个建议保留的验收断言：对于非归一化状态或非幺正 evolve 产生的状态，建议确认现有
> 测试已经直接验证 <O>_(c psi) = |c|^2 <O>_psi，以及 Tr((c rho)O) = c Tr(rho O)。
> 第二式适用于相应线性扩展的数值对象；如果当前 DensityMatrix 公共构造器不接受某些
> 非物理输入，不必为此扩大 API，只需在现有支持的数值路径验证不发生隐藏归一化。
> 若已有等价断言，不要增加重复工作。
>
> 当前执行决定：保持 P0.4 代码冻结，继续正在依次执行的全部门禁，不启动新功能。
> SDK-free/main/alternate FULL、四框架专项、完整 coverage 和原 28 段 matrix 必须
> 获得最终退出码。Coverage exclusions 保持 68，不借用 P0.3 结果。五环境 import
> origins、pipcheck 以及受测树一致性继续独立记录。Whole-workspace Router legal
> 失败与 controlled-export legal 通过分别披露，不修改用户文件。只有全部必要门禁
> 达到既定条件后，才限定 stage、正常本地提交并报告真实 SHA；新 SHA 远端 CI 仍为未验证。
> 结论：P0.4 目前不需要调整核心算法方向，也不需要扩展到新功能。等待完整门禁终态后
> 再进行有界验收。完整 Qiskit/PennyLane 原生 full functional parity/full replacement
> 继续保持 ACTIVE / INCOMPLETE，C3 保持 PARTIAL，Studio 最后。

## Remaining Objective

Still incomplete: all remaining State/Operator/channel/random/synthesis public
contracts; complete QuantumCircuit/library/transpilation and Primitives V2;
Providers/jobs, QASM/QPY and full Aer; complete algorithm/industry libraries;
full PennyLane operations, QNode/devices/measurements/transforms/templates/qchem,
all differentiation/interface/plugin/resource/kernel/qnn/qcut/shadow contracts.
This batch is a useful independent native numeric building block, not full
Qiskit/PennyLane replacement, production equivalence or real Quafu execution.
