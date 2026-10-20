# Stage 11P-C2A Native Second-Order Adjoint

Date: 2026-10-20. Starting local main:
`eafc143afaa8dd8cc6be2076bff8ecd5b33e28a8`.
Full independent Qiskit/PennyLane functional replacement remains ACTIVE /
INCOMPLETE. This is one implemented core algorithm, not a reduced final goal.
The complete ChatGPT reply, read through Chrome during validation, requests C3
unified derivative execution/resource/status next and reserves D for Capture.
This independently started adjoint addition is therefore C2A, not completed D.

## Native Algorithm

Explicit `adjoint` now computes analytic Hessians or direction-only HVPs for
noiseless unitary native StatevectorDevice plans. `best` retains its prior
second-order parameter-shift selection. The derivative plan invokes the actual
native device for its authoritative primal and checks its tangent sweep's
primal against that result. It does not call shift recipes, finite differences
or a quantum SDK. Existing native gate matrices, local application, observable
actions, children and numerical processors remain the engine.

For gate U and source direction-induced angle tangent eta, the forward state
tangent obeys `dpsi_next = U dpsi + eta U' psi`. The existing reverse gradient
`g_i = 2 Re <lambda | U'_i | psi_before>` is differentiated independently:
the reverse state and its tangent are restored with U-adjoint, and the gradient
tangent retains lambda-tangent, state-tangent and `eta U''` terms. Supported
constant-generator gates use `U'' = U' U-adjoint U'`, including controlled
generators with a zero block. This keeps both controlled-rotation frequencies.
Quantum gradients and directional curvature contract immediately with the
source classical Jacobian and second map; no gate-pair Hessian is constructed.

Expectation, ordered marginal probability and variance outputs are supported.
Variance uses `(O^2 - 2 mean O) psi` and its tangent, including mean-tangent
corrections. Nonlinear/shared input maps, stationary maps, Hamiltonian coefficient
slots and cross-child processor terms retain the existing genuine second chain
rule. Four classical framework second graphs reach this same engine. Third
quantum derivatives remain explicitly rejected by the existing boundary.

One forward tangent sweep per direction and one reverse curvature sweep per
output/direction keep a constant number of working state vectors, not a retained
state trajectory.
Full Hessians repeat source directions within the existing output budget;
HVPs retain one column. First Jacobians/classical maps may still be dense.
Work receipts distinguish native base evaluation, directional/reverse sweeps,
logical tape evaluations and zero shifted/physical-shot counts. Logical tape
counts are not a claim that each multi-measurement plan calls the simulator once.

## Limits And Scope

Preflight checks analytic Statevector capability, actual gate generators,
finite unitaries/Hermitian observables, ordered wires, derivative order and
output/Hessian sizes before quantum simulation. A conservative bound includes
working state vectors, local/dense matrices and derivative arrays against both
HigherOrderLimits and device memory. `max_adjoint_operations` bounds planned
dense-element work; it is not a measured CPU-operation or wall-clock guarantee.
Child batches and JAX transposed output rows check cumulative work before any
child/row executes. No unsupported path silently substitutes parameter shifts.

Owned source graph arrays, arbitrary user converter internals, framework/runtime
allocations and global process memory are not sandboxed. Other derivative
methods retain their separate budgets. This does not add mixed/MPS/noisy,
sampled, general measurement-record/loop/postselection second adjoints, all
missing generators, simulator backpropagation, GPU/TPU or complete device/plugin
protocols. Coherently deferred supported unitary children remain a distinct path.
Unused terminal measurement metadata keeps the existing analytic expectation
contract; a test initially confused it with an actual mid-circuit record and
was corrected to exercise a real mid-circuit read plus subsequent gate. A
separate positive test preserves valid terminal behavior instead of restricting
production just to make a negative assertion pass.

## Evidence

Initial three red contracts: 3 failed in 0.19 seconds, exit 1, before runtime
changes. New tests independently check RX/RY/RZ/phase, CP, controlled RX/RY/RZ,
RXX/RYY/RZZ; complex Hermitian observables and a constant global phase; mixed
partials, probabilities, variance and stationary nonlinear maps. Native shift
results are a separate cross-check, not the adjoint implementation.

A 64-occurrence shared RY input evaluates HVP
`-.4 * 64^2 * cos(64 * .003)` with shift budget one. The test forbids all shift
recipes and records exactly two actual statevector calls: the base measurement
and authoritative adjoint primal. Its internal tangent/reverse applications are
reported separately. Full native H2 Hessian/HVP/Newton tests run both methods.
The all-four-framework H2 CLI uses one Gaussian/RHF/JW build at 1.4 bohr,
forbids another chemistry build during differentiation, and matches the
independent two-determinant matrix formula. E is -1.0279252771620968 and HVP
is approximately 0.2799425351344631, within the unchanged existing tolerance.
These are fixed-Hamiltonian ansatz derivatives, not geometry Hessians or DiffHF.

## Frozen-Tree Validation

The tested Git tree is `7092a5eb39da241140ab82a3bb07dec6e0042572`, with
production subtree `736ceb10986a75e283f35eb75d83e8f50f4b3fe1`, exported to
`/tmp/qb-stage11pd-final.qPcnpc` without unrelated Router/Studio work. The
checkpoint was renamed from D to C2A after this freeze, with documentation-only
changes. Final staging verifies unchanged production, test and example trees.
The `stage11pd` temporary log names identify the original run, not Capture work.

All environments use Python 3.12.6. No environment was modified for this run.

| Gate | Actual result | Independent log/exit prefix in `/tmp/` |
| --- | --- | --- |
| Complete 28-section local matrix, main installed environment | exit 0; full pytest twice: 2200 passed, 5 skipped, 3 public xfailed; true coverage run: same counts | `qb-stage11pd-final-matrix` |
| True full coverage | 23846 / 26617 statements = 89.58936018334147%; 68 exclusions unchanged | `qb-stage11pd-final-coverage.json` plus matrix log |
| SDK-free full pytest | 1657 passed, 347 missing-dependency skipped; exit 0 | `qb-stage11pd-final-sdkfree` |
| Alternate installed second-order regression | 665 passed, 1 skipped, 2 public xfailed; exit 0; not a full alternate suite | `qb-stage11pd-final-alternate` |
| Independent JAX 0.12 CPU regression | 100 passed, 21 absent-framework skipped; exit 0 | `qb-stage11pd-final-jax012` |
| Independent JAX float32 | 2 passed, 3 deselected; exit 0 | `qb-stage11pd-final-jax-float32` |
| Four-framework native H2 adjoint CLI | all four match the independent formula; one geometry build; exit 0 | `qb-stage11pd-final-h2` |
| Three independent random native mathematical probes | Hessian, symmetry and HVP differences at most 4.44e-16; exit 0; probes are not pytest/coverage cases | `qb-stage11pd-final-random-crosscheck` |
| Compileall; frozen legal/migration subset | exit 0; legal/migration 6 passed | frozen-tree validation receipts |

Main installed versions: NumPy 2.4.6, Qiskit 2.4.1, Aer 0.17.2,
PennyLane 0.44.1, JAX/jaxlib 0.7.1, Torch 2.12.0, Autograd 1.8.0,
TensorFlow 2.21.0. Alternate versions include Qiskit 2.6.0,
PennyLane 0.42.3, JAX 0.6.2 and Autograd 1.9.1. SDK-free NumPy is 2.5.4.
The new second-adjoint module covers 157 / 174 statements (90.229885%).
The matrix reports unavailable Finance, Optimization, Machine Learning,
Dynamics, Metal, Experiments and Addons lanes explicitly, not as executed
compatibility passes. Its existing Studio backend regression runs do not
implement or modify Studio.

A fresh main-environment `pip check` returns exit 1 for two pre-existing
conflicts: WeasyPrint 68.1 requires tinycss2 >= 1.5.0 (installed 1.4.0), and
pyquafu 0.4.5 requires NumPy < 2 (installed 2.4.6). These are not resolved by
changing or combining the deliberately separate optional environments.

Local validation does not establish remote publication. The bounded ordinary
fetch failed with a network low-speed timeout (exit 128;
`/tmp/qb-stage11pd-fetch.log` and `.exit`). Remote main is stale/unverified;
no push is attempted without a successful fresh fetch and verified
fast-forward relationship. Old remote CI is not evidence for this source.
Full native Device derivative requests, shared runtime resource ownership and
derivative-specific graph status remain C3 work, not capabilities delivered here.

## References And Publication

[Jones and Gacon](https://arxiv.org/abs/2009.02823) supplies a public mathematical
reference for the first-order reversible adjoint gradient. The tangent-over-
reverse extension above is independently differentiated and implemented here;
the paper is not claimed to validate these new second-order contracts. No
upstream implementation/test source was opened/copied or used as the native
engine. Optional frameworks provide classical graphs only. Source ports: zero.
No Studio/Router, cloud/hardware/token, tag/release, environment/package-tree,
credential or authentication/TLS changes belong to this checkpoint. Remote
publication/exact-SHA CI require separate actual receipts.
