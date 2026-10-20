# Stage 11O-B6 Native Coherent Deferred Measurements

Date: 2026-10-20. Starting branch: `main`; local starting HEAD:
`bd88f88550b1eb6ab79c5fe3d8a1364f49cf2570`.
The full Qiskit/PennyLane functional replacement objective remains ACTIVE /
INCOMPLETE. This is a native supported-subset checkpoint, not full SDK parity.

## Red Test And Physical Contract

The first persisted test failed with AttributeError because the native
`defer_measurements` API did not exist. Its circuit is H0, measure0 -> m, H0,
if m then X1. Native dynamic branch execution gives four logical probabilities
of .25. Deleting the measurement and using the changed q0 as a control gives
the incorrect probability 1 for 00. The implemented coherent circuit is
H0, CX(0,a), H0, CX(a,1), with one fresh initialized record wire.

The original nonselective mixed density is compared with the expanded pure
state's reduced density, not directly with the larger pure state. The first
test proves both probabilities and reduced density. Additional tests retain
record-conditioned distributions after the original measured wire changes.

## Actual Native Implementation

The registered transform emits one real child Tape, with no mid-measurement
or classical-feedback instruction in the supported unitary result. Existing
NativeTransform/TransformProgram, child ExecutionPlan, parameter AST recorder,
compiler and quantum derivative engines are reused. It does not delegate
the child back to the original dynamic circuit or use an SDK executor.

Each measurement owns an independent, trailing, zero-initialized ancilla.
Receipt fields retain source bit/measurement ID/wire, assigned ancilla,
actual condition dependencies/output spans, logical output map, real width,
operation expansion and configured limits. Repeated live records cannot alias.
Nonzero user initialization or a configured noisy feedback device rejects.
Device capacity and execution limits include the actual expanded circuit.

Supported Boolean predicates are evaluated as bounded disjoint control
assignments using the existing native classical evaluator. Unitary conditional
rotations and nested controls preserve angle expressions. Multi-controls use
commuting Z-projector/parity rotations, not a full-register matrix. For example,
the all-one control projector is the product of (I-Z)/2 factors. Expanding that
product gives bounded native parity RZ gates, with phase terms retained.
Small opaque unitaries have a separate local matrix-width guard before control
matrix allocation. Thirty-three gate cases compare complete complex coherent
states against direct controlled matrices, without phase alignment.

Branch global phase is coherently controlled, including native symbolic phase.
Raw numeric parameter binding, callable/QNode dispatch, repeated fresh calls,
multi-Tape composition, native compile/routing and QWC composition execute.
Invalid original logical wires cannot become accidentally valid ancilla reads.
Reapplying deferral does not lose the original record-resource receipt.

## Records, Sampling And Derivatives

Native Tape `probs`, `sample`, `counts` support `records=`. Ordered record bits
precede explicitly requested quantum wires; records without wires request only
records. On the original circuit, the existing DynamicExecutionEngine supplies
actual classical branches/trajectories. After defer, requests become actual
terminal ancilla reads. Joint sampling retains record/quantum correlations;
it is not reconstructed from independently sampled marginal distributions.

The first derivative proof RY(theta)0, m=measure0, if m X1, expval(Z1) gives
cos(theta), -sin(theta). Actual deferred child shift and available native
adjoint agree with the native dynamic derivative and analytic reference.
Tests include Torch backward/gradcheck/autograd.grad, Autograd, shared/nonlinear
inputs, kwargs, coefficients, nested outputs, vector cotangents, records and
multi-Tape/QWC composition. This uses B5 bounded Jacobian products, not a new
matrix-free reverse-mode implementation or hidden finite-difference fallback.

QWC groups really share sample buffers. Tests check IDs, covariance, independent
shift/partition streams, all allocation policies and physical work: two groups
at 301 parent shots use 2408 derivative shots without total allocation, or 1204
with uniform/weighted allocation. The [100,(200,2)] single-group derivative
uses 2000 shots. Finite gradients are stochastic estimates; energy SE is not
a gradient-error bound. Existing finite-variance and higher-order guards remain.

## Non-Dense MPS And Chemistry

The required 100-logical-wire GHZ circuit measures q0, applies H0, uses the old
record to control X99, then applies native AngleEmbedding RY(theta)99. Deferral
actually produces 101 wires. Dense statevector, full density and MPS expansion
APIs are patched to fail. At theta .3, native MPS gives energy
.9553364891256055 and gradient -.2955202066613396, matching cos/-sin.
Actual peak bond is 2, tensor storage 12800 bytes, discarded weight/truncations
0, shifts 2, transforms 3, physical shots 0. Limits are max_bond_dim 4,
max_memory_mb 2, cutoff 0 and capacity 101. Storage is not peak SVD workspace;
this is not arbitrary-entanglement efficiency or a hardware execution claim.

One real H2 geometry at 1.4 bohr builds Gaussian integrals/RHF/fermionic/JW
Hamiltonian once. The original B5 standard excitation energy/gradient remain
-1.0279252771620968 / .40622294673301496 at theta .3. Adding a measured/reused
wire and conditional AngleEmbedding gives energy -.7958578898722166 and
native gradient .181811259942503; both match actual original dynamic execution.
Two native optimization steps reach theta .23157294720151306 and energy
-.80691353798818. Integrals/SCF are not rebuilt per child or shift. This feedback
ansatz need not conserve electron number and is not claimed to find a ground
state. General molecules, basis sets and differentiable HF remain incomplete.

## Boundaries And Public Evidence

Explicitly unsupported: reset; postselection including impossible/zero cases;
noisy/readout-dependent feedback; arbitrary nonunitary/Kraus instructions;
conditional measurements; runtime loops; classical Store/arithmetic and
measurement-dependent gate angles; snapshots; undefined full state output;
unmapped dense observables; unsafe memories/aliases; unproved parameterized
opaque gates; and exceeded width/expansion/output/shot/device budgets.
These remain in the full-parity ledger rather than being declared complete.

Eight independently authored public API scenarios execute PennyLane 0.44.1
and 0.42.3. They cover reused wires, density, zero/else controls, Boolean
records, original record distributions, nonlinear gradients, shared
coefficient/gate product rules and statistical finite shots. No implementation
or test code is ported. Public calls are test oracles only.
The published [dynamic-circuit documentation](https://docs.pennylane.ai/en/stable/introduction/dynamic_quantum_circuits.html)
describes coherent deferral and its extra-wire cost. Native defaults preserve
logical wire selection and use an explicit record keyword; this is not a claim
of complete public signatures, reset/postselection or capture compatibility.

## Verification Receipts

| Gate | Receipt |
| --- | --- |
| First persisted test | Failed old missing API; now passes probabilities, reduced density and actual child structure |
| New native module | 53 independent test functions / 94 cases passed, including final malformed-control resource-map guard |
| New public scenarios | 8 passed in each installed PennyLane version |
| Shared native circuit/interface/gradient/QML/compiler/transform regression | 399 passed / 1 warning |
| SDK-free examples | Five actual executions passed with numeric assertions |
| Main full | 1914 passed / 4 skipped / 51 warnings, 61.11s |
| SDK-free full | 1567 passed / 147 skipped / 5 warnings, 50.57s |
| Alternate full | 1858 passed / 60 skipped / 8 warnings, 55.51s |
| Explicit full-package coverage | 1914 passed / 4 skipped / 51 warnings, 157.25s; 22458 / 25144 statements = 89.31753102131721%; 68 unchanged excluded lines |
| Complete matrix with actual embedded coverage | All 28 sections reached the final OpenFermion gate (1 passed); two plain full runs each 1914 passed / 4 skipped / 51 warnings (57.83s / 57.64s); actual embedded coverage 1914 passed / 4 skipped / 51 warnings in 155.59s, 25144 statements / 2686 missing |
| Compileall / attribution/privacy / pip checks | Compileall exit 0; clean snapshot attribution/no-vendor/no-cloud/no-token checks 9 passed; both isolated pip checks clean |

Full gates use a clean tracked/index snapshot, excluding unrelated user
Studio/Router work. The known dirty-workspace Router attribution issue is
separate and must not be hidden by adding or changing that user file.

The tested snapshot is `/tmp/qb-stage11ob6-check-LK39wE`. Python is 3.12.6 in
all three environments. Main uses NumPy 2.4.6, Qiskit 2.4.1/Aer 0.17.2,
PennyLane 0.44.1, Torch 2.12.0, Autograd 1.8.0 and PySCF 2.13.1. Alternate
uses NumPy 2.5.4, Qiskit 2.6.0/Aer 0.17.2, PennyLane 0.42.3 and Autograd
1.9.1, without Torch/PySCF. SDK-free uses NumPy 2.5.4 and has no Qiskit,
PennyLane, Torch, Autograd or PySCF. Missing frameworks are explicit skips,
not native or framework evidence. Main retains only the known pyquafu 0.4.5 /
NumPy 2.x and WeasyPrint 68.1 / tinycss2 1.4 pip conflicts. No environment or
dependency changes were made. Main full skips are the pyquafu conflict,
unavailable Dynamics (two tests) and unavailable Optimization (one test).

Coverage increased from 89.13324708926261%, without configuration or exclusion
changes. The new coherent-deferral module covers 313 / 318 statements (98.43%);
the record-measurement module covers 64 / 66 (96.97%). These are package/code
coverage metrics, not percentages of SDK functional parity. The final focused
A/B/C/system command passed 1159 tests with 6 warnings in 49.15s, including
native chemistry, public chemistry/template oracles, compiler, serialization,
devices, interfaces and B1-B6 transforms.

The direct dirty-workspace attribution probe again returned 5 passed / 1 failed
because the pre-existing untracked `quantumbridge/router/core.py` is absent
from the migration ledger. It is outside this batch and the clean snapshot.
No user Router file was modified, staged or deleted to hide that result.

The matrix log is `/tmp/qb-stage11ob6-matrix.log`. Its original terminal handle
was no longer available on resumption, so a separate shell exit-code receipt
could not be recovered. Completion evidence is the full log through the final
command, with no failed test section, and no remaining matrix/coverage process;
the existing script uses `set -euo pipefail`. Finance, Optimization, ML,
Dynamics, Metal, Experiments and Addons installed-dependency lanes were
explicitly unavailable, not executed and not counted as installed coverage.
The matrix ran existing Studio backend regression tests, not Studio development.

All 14 staged Python source/test/example files matched the tested snapshot by
SHA256. Final receipt edits are documentation-only; the final index snapshot
is checked separately for attribution/privacy and whitespace before commit.

## Git And Completion Questions

Only scoped B6 implementation/tests/examples/docs are included. Existing
11M/11N/11O-C/11O-A/B1-B5 history is retained. No reset/rebase/amend/force,
tag/release, vendoring, token/cloud/hardware work or Studio work is performed.
No push/new-SHA Actions proof is claimed; stale origin/main is not live proof.
Publication needs owner-restored authorization, a fresh successful fetch and
verified fast-forward relation before ordinary push, followed by exact-SHA CI.

| Final question | Answer and evidence |
| --- | --- |
| 1. Actual coherent conversion? | Yes within the supported subset: actual enlarged unitary child with no MCM/classical feedback, not dynamic delegation |
| 2. Correct measured-wire reuse? | Yes: the persisted H/measure/H/conditional-X counterexample matches four .25 probabilities and logical reduced density |
| 3. Real managed ancillas? | Yes: one fresh initialized trailing record wire per MCM, explicit mappings, capacity/alias/expansion guards |
| 4. Terminal probability equivalence? | Yes for tested supported analytic and record/quantum joint cases; finite shots use statistical comparisons |
| 5. Reduced density equivalence? | Yes after tracing record ancillas; not a comparison of unequal-width pure/mixed states |
| 6. Unsupported semantics reject? | Yes; explicit boundaries and negative/resource tests above, no silent semantic substitution |
| 7. TransformProgram composition? | Yes: real children, reverse reconstruction, QWC and native compile/routing tests |
| 8. Native transformed gradients? | Yes: analytic/dynamic/shift/available adjoint comparisons, shared/nonlinear inputs and coefficient product rules |
| 9. Actual Torch/Autograd? | Yes where installed: backward, gradcheck, autograd.grad and Autograd grad; absent frameworks are skipped, not claimed |
| 10. QWC/allocation? | Yes for supported observables/policies: shared samples, covariance, IDs, independent streams, shot vectors and real shot totals |
| 11. 100-qubit non-dense MPS? | Yes: 100 logical / 101 actual wires, peak bond 2, 12800 tensor bytes, dense APIs forbidden; bounded example only |
| 12. Native H2 preserved? | Yes: real fixed-geometry integrals/RHF/JW reused, B5 standard energy/gradient retained and B6 feedback energy/gradient checked |
| 13. A templates regression? | Yes for the eight supported families; full template catalog/contracts remain partial |
| 14. B1-B5 regression? | Yes: actual batching/dispatch/basic transforms/QWC/gradients included in focused and full suites |
| 15. C chemistry regression? | Yes: native chemistry plus installed public PySCF/PennyLane oracles; not full chemistry parity |
| 16. Three environments/coverage/matrix? | Passed full suites as listed; 89.31753102131721% coverage, unchanged exclusions; all matrix sections finished per log, shell handle caveat above |
| 17. Git local only? | Yes: scoped ordinary local main commit; no push, rewrite, tag, release or unrelated user files |
| 18. New-SHA remote CI? | No: owner-restored authorization/fresh fetch/fast-forward publication and exact-SHA CI remain outstanding |
| 19. Which 11O parts are PARTIAL? | Full template/operation catalog, public transform dispatcher/defer/reset/postselection, higher-order/matrix-free/JAX/TF/capture and general/differentiable qchem remain open |
| 20. Next full-core gaps? | Complete transform/measurement contracts and differentiable interfaces/device protocols, then the ranked remaining Qiskit/PennyLane core and ecosystem gaps |

See the joint report for all A/B/C modules and the gap report for remaining
full API contracts. Stage 11O genuinely expands independently executable
native PennyLane functionality. Complete PennyLane functional parity: NO.
Complete Qiskit functional parity: NO. The full goal remains active.
