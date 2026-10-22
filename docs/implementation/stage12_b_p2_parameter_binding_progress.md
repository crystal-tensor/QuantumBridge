# Stage 12-B P2 Native Parameter And Composite Binding

Date: 2026-10-22 (Asia/Shanghai). Starting HEAD
4df5bf338427f8f3052669d603dab689fed68520; previous native bridge code
2ec69c4b1eb0059b26633569442456986e440e1e. Full independent Qiskit/PennyLane
functional replacement remains ACTIVE / INCOMPLETE, C3 PARTIAL. This document
records a bounded native slice with completed final local acceptance, not whole-SDK parity. No cloud,
hardware, credentials, Studio/Capture, source vendor, push, tag or release.

## Actual Gaps And Reused Math

| Candidate | Evidence before this slice | Action |
| --- | --- | --- |
| Scalar Parameter identity | INCORRECT: same-name instances collapsed | Fresh UUID identity; copies preserve equality; reject conflicting names atomically |
| Actual ParameterVectorElement | MISSING; vector elements were scalar names and sorted lexically | Native subtype, parent/index, stable resize UUIDs, true natural element ordering |
| Circuit.assign_parameters partial/default strict semantics | INCORRECT: strict meant all parameters must bind | Strict rejects unknown keys; symbolic partial assignment allowed; legacy bind_parameters retains full-numeric guard |
| Composite formal params and complete parameter_map | INCORRECT/MISSING: empty formal tuple and no actual remapping | Existing Circuit binding maps gate expressions and phase before creating Instruction |
| Parameterized IR/QPY identity | INCORRECT/MISSING: identity/type loss, opaque provenance, unsupported QPY vector symbols | Extend existing AST/identity records and published QPY v13 vector records; no new IR |
| Existing arithmetic expression evaluation | EXISTING_CORRECT for the ten sampled algebras | Keep implementation; independent dense/tensor math regression |
| Existing compose/inverse/integer power | EXISTING_CORRECT for the six sampled static scenarios | Keep implementation; no new structural engine |
| Existing nonlinear QNode derivative execution | EXISTING_CORRECT in sampled first/second derivative chains | Reuse parameter-shift/adjoint and C2A HVP, no new autodiff framework |
| Managed Instruction.copy and new IR vector containers | Incorrect admission/lifetime/limit propagation | Existing strict native configuration copy; validate before vector factory; aggregate and nested caller limits |

The native class remains Circuit. There is no new QuantumCircuit facade,
universal Gate class, second Parameter system, simulator or QNode engine.
Instruction public APIs are not guessed: public Instruction has no
assign_parameters/bind_parameters/power methods in either sampled version.
Native Instruction.power is a pre-existing extension, not public ABI parity.

## Native API And Semantics

- Parameter(name, uuid=None): fresh scalar identities, normalized string UUIDs;
  same name/UUID compares equal, different scalar names do not; scalar and
  vector-element types remain distinct. UUID return type is not public UUID ABI.
- ParameterVector(name, length=0), resize(length), actual
  ParameterVectorElement(vector, index, uuid=None): preserve prefix identities
  and deterministic restored tails; standalone bracketed scalar names still
  sort lexically. Vector objects are not collapsed by their display name.
- Circuit.assign_parameters(parameters, inplace=False, strict=True): accepts
  existing scalar/string mappings, actual vector-key mappings and positional
  values, including simultaneous symbolic substitution. Validation precedes
  mutation; managed foreign mapping/array protocols are rejected.
- Native inplace still returns self, unlike public None; disclosed Partial
  return ABI. Circuit.bind_parameters(strict=True) is the existing numeric
  execution guard and never invents default values for remaining symbols.
- Circuit.to_instruction(name=None, label=None, *, parameter_map=None): supports
  a complete parameter map, including public-shaped positional mapping while
  preserving the native positional-name extension. Gate and global-phase
  expressions retain their actual shared identities.
- Instruction.copy(name=None): uses the existing strict native configuration
  copier in an active ResourceScope; shared native references use one memo,
  buffers reserve before copying and escaped views retain the actual lease.
  Unmanaged legacy copying and other existing structural allocators are not a
  global process-memory bound.

New IR vector containers obey caller max_parameter_nodes before resize,
including total distinct roots, provenance and nested control bodies. Invalid
identity UUID/name records reject before a positive vector allocation. Existing
name-only legacy IR receives deterministic legacy scalar identities because
the original UUID cannot be recovered. Explicit UUID loss policy in QASM remains
reject/sidecar; fresh automatic identities do not make all text exports fail.
Loop-local parameter UUIDs remain lexical locals after IR roundtrip.
Vector-element loop locals also retain their subtype and bounded vector record,
not just a scalar name/UUID that would fail to match the typed body identity.

## Red And Local Recovery Receipts

Each /tmp prefix below has a full .log and independent .exit; observations are
not silently overwritten. These are development receipts, not frozen FULL gates.

- Initial native red: /tmp/qb-stage12b-p2-initial-native-red, 9 failed/1 passed.
- Identity/IR red: /tmp/qb-stage12b-p2-identity-io-red, 3 failed.
- Public QPY vector red-v2: /tmp/qb-stage12b-p2-qpy-vector-native-red-v2,
  3 genuine failures after fixing the separate missing-public-import fixture.
- Initial broader integration: /tmp/qb-stage12b-p2-broad-integration,
  10 failed/1573 passed/2 skipped/3 existing xfailed. Fresh automatic UUIDs
  initially triggered the old explicit-identity QASM loss guard; this is fixed
  without weakening the guard for explicit identities. A writer collision test
  now checks both earlier builder rejection and still-invalid raw writer input.
- IO recovery: /tmp/qb-stage12b-p2-io-recovery, 210 passed.
- QPY main-v2/alternate: /tmp/qb-stage12b-p2-qpy-vector-main-v2 and
  /tmp/qb-stage12b-p2-qpy-vector-alternate, 179 passed each.
- Native nonlinear derivatives: /tmp/qb-stage12b-p2-nonlinear-derivatives,
  6 passed/75 deselected; parameter-shift and adjoint at three input points.
- Resource red: /tmp/qb-stage12b-p2-resource-red, 8 failed/2 passed. Real
  production failures include prevalidation allocation, missing nested limits,
  unaccounted copies, view lease loss and foreign copy execution.
- First resource recovery: /tmp/qb-stage12b-p2-resource-recovery,
  1 failed/9 passed; remaining failure was a test spy counting recovery fixture
  construction across independent parse budgets, not a production budget leak.
- Resource recovery-v2: /tmp/qb-stage12b-p2-resource-recovery-v2,
  117 passed, exit 0, including identity, full complex math, QPY and Instruction.
- Larger integration r2: /tmp/qb-stage12b-p2-integration-r2, 1855 passed,
  2 warnings in 274.09s, exit 0. This subset did not include all transform tests.
- First frozen full tree 2e373101036d666069541511b2d8fc445c2266f0,
  /tmp/qb-stage12b-p2-final.TORIYv/source: compile/legal/privacy/public/example
  gates passed; SDK-free FULL then failed with 2 failed/3621 passed/561 skipped
  in 212.13s, actual exit 1. Both failures are existing H2 transformed-QNode
  workflows with transient internal __qb_angle_0 identity collisions.
- Minimal compiled-phase red: /tmp/qb-stage12b-p2-compiled-phase-red,
  3 actual failures. record_compiled_parameters generated a fresh phase
  parameter while its copied gate list still had old same-name identities.
  It now computes the phase first (keeping recorder order), replaces gate
  identities, then installs/validates phase. The new identity guard is retained;
  no derivative engine, math tolerance or test expectation is weakened.
- Later loop-element red: /tmp/qb-stage12b-p2-vector-loop-red, 1 failed/14
  deselected. IR preserved UUID but demoted a vector loop local to scalar, so it
  leaked into free parameters. The existing control-node parameter record now
  includes its native vector identity and reuses the bounded decoder. The
  recovery checks actual two-iteration noncommuting RX/RY density execution at
  three parameter points; a separate limit test covers the loop header itself.

## Independent Math And Actual Chains

tests/core/test_native_parameter_composition_math.py contains ten genuinely
distinct arithmetic/binding algebras, eight composite scenarios and six static
structural scenarios, each at (.2,-.3), (-.7,.5), (.8,1.1). Counts are 30+24+18
numeric cases, not 72 distinct functions. Three two-chain tests and six actual
derivative tests make 81 initial cases in that file, plus three compiled-phase
replacement regressions added after the SDK-free FULL failure. Dense basis embedding/product and
per-gate tensor contraction are independent of native operator/device helpers.
Comparisons use complete complex matrices/vectors and mixed density matrices,
noncommuting rotations, shared nonlinear parameters, phase and reversed wires.

Nonlinear derivative circuit: RX(p*q+p*p,0), RY(2*p+q,0), CX(0,1), RZ(p*q,1),
phase p*p/3. Z0 expectation is cos(p*q+p*p)*cos(2*p+q). Its analytic gradient,
analytic Hessian times (.4,-.2), native Jacobian/HVP and central finite
differences (step 1e-6) agree. Partial p assignment also feeds an actual
one-parameter QNode. Existing methods are reused, not reimplemented.

examples/native_parameterized_execution.py prints three complete numeric
records for chain A (partial bind -> Operator -> complex Statevector ->
expectation) and chain B (subcircuit -> Instruction reused on (2,0) and (0,1)
-> parent binding -> mixed DensityMatrix -> keep wires [2,0] -> purity and
expectation). Native keep semantics retain original order (0,2), not request
order. Records include full arrays, phases, actual wire maps and oracle errors.
Development main and SDK-free runs both exit 0:
/tmp/qb-stage12b-p2-example-main and /tmp/qb-stage12b-p2-example-sdkfree.

Final R3 example receipts repeat both calls at all three points, including full
arrays; the table shows selected actual outputs (no probability-only oracle).

| p, q | Chain A complex expectation | Chain B reduced purity (real part) | Chain B expectation (real part) |
| --- | --- | --- | --- |
| .2, -.3 | .6807681142109357 - .3027050057117917i | .408933684395557 | .15388395284886092 |
| -.7, .5 | .6396221325349747 - .1535585301619700i | .43075328553159054 | .21651829077111984 |
| .8, 1.1 | .9318329061675701 - .26181212965459105i | .43241756306733337 | .03196712658874662 |

Maximum SDK-free example operator error is 1.1102230246251565e-16; density
error is 8.441528768080323e-17. B's imaginary trace residuals remain in the
raw receipt (at most 5.106922375383448e-17), not silently projected to real.

## Public Black-Box Evidence And Remaining Differences

scripts/probe_parameterized_public_contracts.py inspects only public signatures
and calls in installed Qiskit 2.4.1 and 2.6.0. Each v3 log contains its version
header and 75 outcome records, not 75 native tests. Complete literal records,
two QPY protocol probes per version and the SDK-free native numeric example
are saved in docs/compat/stage12_b_p2_parameter_contracts.json. No upstream
implementation/test source is read or ported. Raw prefixes:
/tmp/qb-stage12b-p2-public-v3-241 and /tmp/qb-stage12b-p2-public-v3-260.

Final R3 repeats are retained as literal JSON lines in the same artifact.
Qiskit 2.4.1's mixed scalar/vector-root-name tie has initial order
[theta,theta[0],theta0,theta[99]] but final order
[theta[0],theta,theta0,theta[99]]. Native uses the former stable policy; this
ambiguous root-name boundary is Partial Public Compatibility, not an assertion
that every parameter order matches every public process. The sampled 2.6.0
repeat keeps the initial order. All other repeated records match their own
version after generated UUID/address normalization. Pure vector natural-index
order and standalone bracketed-name lexical order are separately verified.

The first final audit (/tmp/qb-stage12b-p2-r3-final-audit, exit 1) incorrectly
expected only UUID/address text differences. It also compared raw Python JSON
numbers against a JavaScript-formatted artifact: 0.0 becomes 0 in that
formatter, not evidence of public return-type variation. The v2 audit compares
the preserved initial raw JSON records against final raw records, allows only
the explicitly recorded mixed-name tie, and passes with exit 0. No runtime,
math tolerance, coverage target, xfail or old public mismatch is altered.

Minimal phase difference: RX(p+r,0), RY(r*r,1), phase p/3, then
to_instruction(parameter_map={p:2*target,r:target}). 2.4.1 maps the gates but
retains p/3 and parameters [p,target]; binding only target in an appended parent
still cannot produce an Operator. 2.6.0 maps phase to 2*target/3 and has only
target. Native maps both gates and phase and passes independent full-complex
math; it does not emulate 2.4.1's leftover symbol. This is an explicit public
version difference, not claimed identical compatibility or a hidden xfail.

QPY vector element data follows the published !HQ16sQ header plus UTF-8 vector
name, with actual vector type, index and UUID; expression symbol key v is not
treated as scalar p. Native/public binary roundtrips and actual bound matrices
run in both reference environments. Public UUID.int-index observation yields
one root in both versions. A shrunken vector retaining removed elements fails
in 2.4.1 with IndexError and in 2.6.0 with QpyError; native rejects early with
serialization UnsupportedFeature. Error ABI remains Partial. Public QPY docs:
https://qiskit.qotlabs.org/docs/api/qiskit/qpy.

Still MISSING/Partial: complete ParameterExpression sin/cos/exp/gradient/subs
surface, Circuit.to_gate/decompose/repeat and universal Gate semantics,
inplace return ABI, UUID object return ABI, complete classical/control/layout
and error/metadata contracts. Existing arithmetic correctness is not complete
ParameterExpression equivalence. General qudit Circuit IR, Primitives V2,
full QNode/device/plugin/template/algorithm/ecosystem parity remain incomplete.

## Final Frozen Runtime And Gates

Unique final R3 frozen tree: 742c5102b1cf4ffb5a6f74def7398dd362cde010.
Controlled export: /tmp/qb-stage12b-p2-r3-final.bjcM7M/source (macOS physical
origin /private/tmp/qb-stage12b-p2-r3-final.bjcM7M/source).

- Production subtree: 29f8809fb2c673afd64eca310bf0e6260fb35aa9.
- Tests subtree: 4a528297dcecc9736d325a3925aa384c38a49445.
- Examples subtree: cecb03972ee5d8e99c3ea8e193f108ece9bcaccd.
- 1072 Git-controlled runtime paths match frozen/export/workspace; staging and
  commit proofs are recorded below after the normal scoped commit.

All final functional gates run on that runtime, with fresh independent .exit
and complete .log receipts under /tmp/qb-stage12b-p2-r3-final-. They terminate;
the outer driver exits 0 after recognizing, not hiding, two known pip failures.

| Gate | Actual result | Seconds / exit |
| --- | --- | --- |
| SDK-free FULL | 3628 passed, 561 skipped, 5 warnings | 243.05 / 0 |
| Main FULL + explicit coverage | 4412 passed, 5 skipped, 3 existing xfailed, 57 warnings | 1386.66 / 0 |
| Alternate FULL | 4410 passed, 5 skipped, 5 existing xfailed, 49 warnings | 470.38 / 0 |
| Independent JAX 0.12 | 844 passed, 168 skipped | 32.35 / 0 |
| Independent TensorFlow | 866 passed, 151 skipped | 43.27 / 0 |
| Torch/Autograd focused | 46 passed, 984 deselected | 13.90 / 0 |
| Original complete local matrix | 28 section headers; actual final shell exit | 0 |
| Matrix core / dev / coverage FULL | 4412 passed each; skips/xfails/warnings as main | 470.23 / 471.10 / 1378.75; all 0 |
| Compileall / controlled legal / privacy | compile 0; 4 passed; 49 passed, 1 warning | all 0 |
| Five version/origin probes | all import this exact frozen native package | all 0 |
| pipcheck SDK-free / independent JAX / independent TF | no broken requirements | all 0 |
| pipcheck main / alternate | two exact pre-existing conflicts each | each 1, not PASS |

Main and independent matrix coverage agree per file and in total:
28268 / 31180 = 90.66067992302759%, missing 2912, excluded 68. Prior baseline
90.64759814049587% is not lowered; no exclusion or xfail is added and math
tolerances are not relaxed. This is line coverage, NOT percentage of Qiskit or
PennyLane functionality completed. Final focused tests have 122 passed in each
reference environment; the four new files contain 118 added collected cases,
including two optional public interoperability cases, not 118 new functions.

The final audit-v2 exit is 0: exactly 26 terminal child receipts, coverage
equality, 28 matrix headers, exact seven absent subsets, exact known pip
conflicts, five origins, two actual chains and preserved public differentials.
Privacy uses the original 17 named files. A separate scoped credential-pattern
scan and no-package-artifact path scan are recorded at commit time.

R2 frozen tree 5b759b039de4bb7c30359d518209170ed4d12e53 has earlier passing
SDK-free/main/alternate/framework receipts. After the genuine vector-loop
regression changed runtime, its unfinished old matrix was intentionally stopped
(actual exit 2), not accepted as green. This was not a quiet-log or observation
timeout restart. R3 starts all gates afresh and completes the original matrix;
R2/P1 receipts do not substitute for final acceptance. The first true failed
freeze and all red/recovery logs remain preserved.

## Environments And Remaining Limits

All five interpreters are Python 3.12.6. Actual versions/origins are retained
in final versions-*.log, not inferred from environment names.

| Runtime | NumPy | Optional SDK / framework versions actually loaded |
| --- | --- | --- |
| Main | 2.4.6 | Qiskit 2.4.1, Aer .17.2, PennyLane .44.1, JAX .7.1, TF 2.21.0, Torch 2.12.0, Autograd 1.8.0 |
| Alternate | 2.4.6 | Qiskit 2.6.0, Aer .17.2, PennyLane .42.3, JAX .6.2, TF 2.21.0, Torch 2.12.0, Autograd 1.9.1 |
| SDK-free | 2.5.4 | no Qiskit/Aer/PennyLane or the four AD frameworks |
| Independent JAX | 2.5.4 | JAX .12.0; no other listed optional SDK/framework |
| Independent TF | 2.5.4 | TF 2.21.0; no other listed optional SDK/framework |

Main/alternate mix venv, user-site and system-site packages; they are NOT
hermetic. Both pipchecks retain WeasyPrint 68.1 requiring tinycss2>=1.5.0 with
1.4.0 installed, and pyquafu .4.5 requiring NumPy<2 with 2.4.6 installed. These
are not silently fixed by reinstalling or weakening constraints in this slice.
Seven matrix subsets remain NOT_EXECUTED: Finance, Optimization, Machine
Learning, Dynamics, Metal, Experiments, Addons. Runtime/QOS/Quafu passing offline
tests are NOT cloud/hardware proof. The original matrix's existing Studio
offline regression runs; there is no new Studio/UI development.

Whole dirty-workspace legal separately has 1 failed/3 passed: the user-owned
untracked quantumbridge/router/core.py is absent from the source ledger.
The controlled export legal passes 4/4. That unrelated path is neither changed,
staged nor inserted into the source ledger merely to suppress the failure.
Protected Studio/Router dirt remains intact.

Still incomplete beyond the specific parameter/public-ABI gaps above: complete
Circuit/Gate/classical-control surface and calibration/scheduling contracts;
complete circuit library, state/operator/channel/analysis and transpiler
families; full Primitives V2 and Backend/Job protocols; complete Aer methods;
Algorithms/Nature/Finance/Optimization/ML/Experiments/Dynamics native parity;
full PennyLane QNode/devices/plugins/operations/measurements/transforms/templates/
qchem/interfaces/resources. No new framework, general qudit Circuit IR, cloud
execution or Capture/Studio work is smuggled into this batch. Highest full-core
functional replacement stays ACTIVE / INCOMPLETE, C3 PARTIAL.

## Local Commit And Publication

Current branch main. Normal scoped code commit:
a565aa738e85a5cb1eb00b2475cd988897429daf, full code tree
ef4c67cc36f788457a43017a7af25fb54d9c5d22. Exactly 23 owned files,
5998 insertions/77 deletions; 4380 added JSON lines are literal observations,
not upstream implementation or thousands of new functions. Explicit index
path-set verification excludes all protected Studio/Router paths. Native,
tests and examples subtrees in the real staged tree and actual commit equal
the three frozen hashes above. The controlled-runtime equality helper checks
all 1072 paths across frozen, export, staged export and workspace with no
mismatch; committed-export proof is additionally retained.

The two new-file EOF blanks caught by staged diff --check are removed before
the commit. Public probe AST is identical to the frozen probe; its sole
post-freeze source-format difference is that trailing blank line. Production,
tests and examples have no post-freeze changes. Final raw public observations
and acceptance metadata are documentation additions after the runtime freeze.
Staged controlled legal has 4 passed; scoped secret-pattern rg has no matches
(actual exit 1, empty log), not a hidden scan error. No package/environment
artifacts are in the staged paths. Whole-workspace Router legal remains the
separate known failure. Normal metadata receipts may follow this code commit
without changing its tested runtime. No push, PR, tag, release, source vendor,
history rewrite or change to credentials/TLS. New-SHA remote CI NOT_VERIFIED.

## Coordination Receipt And Next Work

The final P2 report was sent once through the authorized native conversation
tool to "Claude 代码泄漏与应对", conversation
6a20d458-a76c-83ea-9b49-f8f0caedb3cf. Actual user turn
98830664-00b2-4298-90c4-7bcba8ed627a contains this code SHA; assistant
4f0c3615-6e5a-4323-8af3-d6fe03aba199 qualifies acceptance as report-based,
not independent code review or remote CI. The native read is a content
reference; Chrome confirms actual delivery and the complete answer.

The reply initially showed a connection-interrupted partial at Section 5.
After completion, overlapping AX ranges 0-100, 57-157, 138-238, 191-291 expose
all Sections 0-24 and the final execution decision. No duplicate report, tail
request or regeneration was sent. The full function/gate-preserving normalized
P3 prompt is appended to stage12_a_native_state_api_execution_prompt.md.
It selects Native ParameterExpression Symbolic Mathematics, Differentiation
and Substitution: actual elementary functions, native symbolic derivatives,
simultaneous replacement and real Circuit/phase/gradient/serialization calls.
That next plan is received, not implemented. The highest goal stays active;
this bounded P2 acceptance is not all-core completion. A documentation-only
receipt commit may change HEAD without altering tested runtime.
