# Stage 11O-B5 Native Transformed Autodiff

Date: 2026-10-20. Starting local HEAD:
`8031a8afefb6fe7b582be8ac1a3f3923ef43b5ca`.
Full Qiskit/PennyLane functional replacement remains ACTIVE / INCOMPLETE.
This is a supported first-order transformed differentiation checkpoint, not
B6, complete Stage 11O integration, or complete SDK/derivative-device parity.
No Studio/Router work, cloud/token/hardware access, vendoring, tags/releases
or history rewriting is part of this batch.

## First Red Test

The first persisted Torch test uses RY(theta) on q0, q1 in zero and
H = .7 X0 + .2 X0 Z1, followed by the actual QWC transform. At theta .37,
energy is .9 sin(theta), and loss = energy**2 must backpropagate
2 * energy * .9 cos(theta). Before implementation it failed at the old live
input UnsupportedFeature guard. It now returns a Torch tensor with a real
gradient rule and passes the exact analytic squared-loss derivative check.
The recorded algorithm is native parameter-shift with two shifted evaluations,
one real child Tape and a proved postprocessing chain rule, not a hardcoded
function, SDK gradient or finite-difference implementation.

## Native Computation Path

The existing TransformedExecutionPlan retains original_recorder, child_plans,
parameter_slices, processing_levels and parent-child spans. Native child
ExecutionPlans now expose numeric Pauli-group means to the existing quantum
shift/adjoint algorithms. Group metadata, bitstrings, covariance, SE and UUIDs
remain passive; flattening all dataclass numbers as derivatives is not used.

`diff/processing.py` computes a bounded first-order postprocessing Jacobian
with the existing native Dual algebra, tracing only numeric result leaves and
declared classical scalar slots. Tangent seeds are chunked rather than forming
an input-sized identity matrix. The processors execute in their actual reverse
transform reconstruction order. Child quantum Jacobians are contracted with
this processing Jacobian, followed by the source classical chain rule.
VJP/JVP/execute-derivative APIs use these actual matrices. This is an explicit,
bounded Jacobian-product implementation, not a matrix-free reverse-mode VJP or
the complete public derivative-device protocol.

Torch/Autograd supply only the classical scalar graph, optimizer and interface
bridge. All quantum derivatives come from native child shift/adjoint code.
An explicitly requested finite-diff method is not relabelled as adjoint; no
unsupported rule silently falls back to finite differences. Torch gradcheck
uses finite differences as a test oracle while the implementation under test
uses native adjoint.

## Coefficients And Graph Ownership

Hamiltonian construction, scalar multiplication and Tape copying retain
supported scalar graphs, including non-leaf Torch tensors and Autograd/Dual
values. `diff/scalars.py` inspects numeric primals for native planning while
registering original graph objects as separate processing parameters. This
primal unboxing is not loss of the retained derivative graph.

The actual result includes both terms:
sum(c * dmean) + sum(dc * mean). Tests cover coefficient-only inputs, one theta
in gates and coefficients, shared/nonlinear parameters, identity offsets,
zero-valued trainable coefficients and Hamiltonian scaling. Ordinary live
coefficient QNodes reuse native single-term preprocessing and the same engine.
Gate and coefficient slots are distinguished in metadata.

Prepared coefficient-bearing plans are tied to their planning primals because
grouping/allocation/provenance may depend on them. Changed coefficient primals
explicitly require a fresh QNode plan; ordinary QNode calls already construct
fresh plans. Raw Tape live gates/bindings/coefficients remain unsupported;
use a recorded QNode for native or framework input derivatives. The internal
term-Tapes splitting prototype remains static-coefficient-only.

Weighted allocation rejects zero-weight trainable groups: their means may
still be required for dc*mean. None/uniform preserve these means. Shot
allocation is held fixed during quantum shifts; it is a resource policy, not
a differentiable path through integer rounding or sampled bitstrings.

## Sampling And Statistical Boundaries

Every supported finite-shot shift executes real child/group measurements,
using fresh independent shift/partition seed streams. Baseline and linear
moment evaluations are real calls too, not fabricated reuse. Repeating an
explicit seed replays a baseline experiment, with fresh actual execution IDs.
Receipts identify baseline/linear/shift work, angle index/sign/shift, seeds,
partitions, actual bitstrings and physical shots. Forward work is separated
from derivative work and totalled; tests match these totals to a Device spy.

None/uniform/weighted policies and [100,(200,2)] partition/copy ordering are
tested through derivatives. Total sampled work and retained joint sample data
are preflight bounded for the complete derivative calculation, including
preceding forward shots where present. Fixed local measurement seeds reject
instead of defeating independent shifted streams.

Finite-shot derivatives are stochastic estimates. Energy covariance/SE and
MPS truncation metadata are not gradient error bounds. No universal unbiased
nonlinear stochastic-estimator guarantee is claimed. Analytic var(P) uses
1-mean(P)**2 and -2*mean*dmean. Finite-shot transformed variance derivatives
are explicitly unsupported across grouping, single-term and identity-like
transforms until their estimator contract is proved.

Higher order, simulator backprop, capture/JAX/TF/GPU, general postselection,
reused parameterized loop derivatives, arbitrary user postprocessor operations
and complete public transform/operation contracts remain unsupported or partial.
Unsupported user float casts during derivative tracing raise instead of
returning a false zero. Existing supported ordinary gradient regressions are
retained; old B1/B2/B4 unsupported assertions are upgraded to real positive
native gradient checks, not deleted.

## Non-Dense MPS And Chemistry

The 100-wire proof prepares native MPS GHZ, applies AngleEmbedding RY(theta)
on q99, then real merge/QWC transforms and native parameter-shift. For
H = Z0 Z99 + .2 Z0, measured energy at .3 is .955336489125606 and gradient
-.2955202066613397, matching cos(.3)/-sin(.3). Dense statevector/full-density
APIs are replaced with functions that fail. Actual transform count is 2,
shifted evaluation count 2, shots 0, peak bond 2, tensor storage 12672 bytes,
discarded weight 0 and truncations 0, within max_bond_dim 4 / max_memory_mb 2.

MPS telemetry is captured from actual expectation/sample/state calls. No extra
resource-only circuit or trajectory job is run. Tensor-byte telemetry describes
observed final tensor storage, not peak SVD workspace. This low-entanglement,
zero-truncation example does not prove arbitrary 100-qubit efficiency or a
general error bound for gradients through truncated MPS simulations.

The chemistry test builds the real geometry-derived H2 Gaussian/RHF/JW
Hamiltonian once. Native excitation/template, decompose/QWC energy, transformed
shift/adjoint gradients and optimizer steps are compared with actual unsplit
native energy/gradient. Molecular Hamiltonian reconstruction is forbidden
inside the tested optimizer loop. The SDK-free example starts at theta .3,
energy -1.0279252771620968 and gradient .40622294673301496; three native steps
reach theta .008959535246871334 and energy -1.1150587068712685. This is not a
ground-state convergence, general-molecule or fully differentiable SCF claim.

## Public Evidence And Verification

Eight independently authored public differential scenarios cover QWC quantum
shift, merged nonlinear shared angles, trainable coefficients, output VJP
order, analytic variance, identity/duplicate/offset derivatives, finite-shot
statistical gradients and actual geometry-derived H2 excitation gradients.
They execute public PennyLane APIs, not private SDK gradient helpers or SDK
implementation/test source. Both PL 0.44.1 and 0.42.3 are test targets.
The H2 excitation sign convention retains the existing complete-unitary proof
against public DoubleExcitation(-theta); no phase alignment is substituted.

Primary public references:
[PennyLane grad](https://docs.pennylane.ai/en/stable/code/api/pennylane.grad.html)
and [parameter shift](https://docs.pennylane.ai/en/stable/code/api/pennylane.gradients.param_shift.html).
Implementation and tests are independently authored; source port count is zero.

The clean tracked/index snapshot is `/tmp/qb-stage11ob5-check-xoRhWf`;
unrelated user working files are not part of this verification tree. The new
native module contains 47 independent test functions / 50 cases, alongside
eight new public differential scenarios. The native-focused regression is
299 passed. Earlier alternate new-scenario preflight was 47 passed / 9 skipped
before the final two extra native safety tests; the final full results below
include those extra cases.

| Gate | Final receipt |
| --- | --- |
| Main full | 1812 passed / 4 skipped / 50 warnings, 54.14s |
| SDK-free full | 1476 passed / 143 skipped / 5 warnings, 44.29s |
| Alternate full | 1758 passed / 58 skipped / 8 warnings, 49.30s |
| Explicit package coverage | 1812 passed / 4 skipped, 146.04s; 22048 / 24736 statements = 89.13324708926261%; 68 unchanged excluded lines |
| Complete local matrix with actual embedded coverage | Exit 0, all 28 sections reached; two plain full runs each 1812 passed / 4 skipped; actual embedded coverage run 1812 passed / 4 skipped in 148.92s with the same 22048 / 24736 covered statements |
| SDK-free examples / compileall / legal and privacy checks | All three examples exit 0; compileall exit 0; focused attribution/no-vendor/no-cloud/no-token checks 9 passed |

Coverage increased from 89.04424125630408%; no coverage configuration or
exclusions changed. Changed-module coverage includes PauliGroupResult 100%,
QWC 98.03%, quantum derivative engine 98.08%, TransformProgram 96.62%,
coefficient scalar handling 93.75%, postprocessing derivatives 89.74% and
MPS device 98.55%. This package coverage is not a percentage of SDK parity.

All three interpreters are Python 3.12.6. Main uses NumPy 2.4.6, Qiskit 2.4.1,
Aer 0.17.2, PennyLane 0.44.1, Torch 2.12.0, Autograd 1.8.0 and PySCF 2.13.1.
Alternate uses NumPy 2.5.4, Qiskit 2.6.0, Aer 0.17.2, PennyLane 0.42.3 and
Autograd 1.9.1; Torch/PySCF are absent. The SDK-free environment has no
Qiskit, PennyLane, Torch, Autograd or PySCF. Dependency-dependent skips are
reported rather than counted as native/framework evidence. Main skips are
the known pyquafu NumPy conflict, unavailable Qiskit Dynamics (two tests) and
unavailable Qiskit Optimization (one test). Synthetic JAX/TF prefix guards
are not real installed-framework end-to-end differentiation evidence.

Both isolated environments pass pip check. Main retains its pre-existing
pyquafu 0.4.5 / NumPy 2.x and WeasyPrint 68.1 / tinycss2 1.4 conflicts; no
dependency/environment change was made or hidden by this batch.

The matrix explicitly reports unavailable Finance, Optimization, ML, Dynamics,
Metal, Experiments and Addons installed-dependency lanes as not executed;
passing native/offline checks does not establish those absent dependencies'
runtime compatibility. Existing Studio backend tests are regression checks,
not new Studio development. Before commit, all 20 staged Python source,
test and example files have identical SHA-256 content to the tested snapshot.
The final report-only receipt update does not change their runtime contents.
Explicit coverage, the matrix and all example/check processes have finished.

An additional direct dirty-workspace attribution probe returned 5 passed /
1 failed: the pre-existing untracked `quantumbridge/router/core.py` mentions
upstream names but is not registered in the migration ledger. That user file
is outside this batch and the verified tracked/index snapshot; it is not
modified, staged, deleted or silently added to this commit. The clean-snapshot
results above must not be read as a claim that the user's entire dirty
workspace is green.

## Publication And Remaining Scope

Only this batch's files are staged/committed; unrelated user Studio/Router
changes remain untouched. No push or exact-new-SHA remote CI is claimed.
Existing publication OAuth/network limits are not bypassed, repeatedly retried
or treated as permission to rewrite history. Stale origin/main tracking is not
current remote proof. The local 11M/11N/11O-C/11O-A/B1-B4 chain is preserved.

B6 deferred measurements and whole Stage 11O-A/B/C integration remain open.
All documented unsupported/partial contracts above and the complete Qiskit /
PennyLane full functional replacement goal remain unfinished. Passing a bounded
local checkpoint or green matrix does not establish complete functional parity.
