# Stage 11K Native QNode Autodiff And Differentiable Execution

Date: 2026-10-19

## Baseline And Audit

Starting main/origin/main: 8e47c9bae19b29cb5a478b0437d20ac2f72e4cc1.
Baseline Actions 39248641174 passed 22 jobs. This is baseline evidence only,
not the new commit's CI. Stage 11H/I/J history and user Studio/Router files
are preserved. No hardware, credential, tag, release or vendor operation occurs.

The audit found native QNode forward execution and Tape measurements already
worked, but QNode had no differentiation protocol, nested-return protocol or
framework backward rule. Torch/JAX helpers converted arrays only. The generic
parameter_shift helper assumed a unit-frequency scalar input: applying it to
RY(theta), RY(theta) at theta=.4 returned zero instead of -1.4347121818.
The implementation below retains the existing QNode/Tape/device architecture,
adds gate-occurrence recording and upgrades that public helper for QNode input.
The generic callable helper remains explicitly limited to known unit-frequency
functions, with its non-default shift coefficient corrected.

## Native APIs

NativeQNode is an alias of the enhanced QNode, not a parallel execution stack.
The existing fn(tape, ...), num_qubits, device, shots and seed interface remains.
New optional settings: interface, diff_method, gradient_kwargs and max_diff=1.

| API | Executable behavior |
| --- | --- |
| QNode(...) / NativeQNode(...) | Native forward evaluation, positional/keyword inputs, nested measurement tuples/lists/dicts |
| gradient / compute_jacobian / jacobian | Real first derivatives, scalar or array inputs, shared angles and classical chain rule |
| compute_vjp / compute_jvp | Explicit output cotangent/input tangent validation and native Jacobian products |
| execute_and_compute_derivatives / vjp / jvp | Values and matching derivatives/products from one constructed execution plan |
| argnums / argnames | Selected trainable positional/keyword inputs; other inputs remain fixed |
| diff_method | parameter-shift, finite-diff, adjoint, best; simulator backprop explicitly unsupported |
| ShotSpec / ShotVector | None, integer, ordered partitions and (shots,copies), seeded independent execution |
| Tape rotation methods | RX/RY/RZ/Phase, CRX/CRY/CRZ/CP, RXX/RYY/RZZ and expanded Rot record separate gate occurrences |
| last_metadata | Actual derivative method, shifted evaluation count, chain-rule/input mapping, shot partitions and MPS resource evidence |

Native classical preprocessing uses an independent first-order dual trace for
arithmetic, powers, sin/cos/tan/exp/log/sqrt and smooth absolute value. Torch
and Autograd instead preserve their own classical graphs up to each recorded
gate angle. Their quantum primitives call the same native Jacobian/VJP engine.
No upstream quantum SDK computes native values or native gradients.

Jacobian output follows the measurement return tree with input shape appended
to each numeric leaf. Multiple selected arguments return a tuple of such trees.
Probabilities retain the existing q0-first label dictionary with zero entries
made explicit. VJP cotangents must match the exact output tree; JVP tangents
must match the selected argument shapes. Complex derivative outputs are rejected,
not silently cast to real. Native numpy evaluation and framework dtype behavior
are independently tested; Torch supports CPU real floating tensors only.

## Algorithms And Capabilities

Parameter-shift changes each recorded gate occurrence independently, executes
the shifted native circuit, then applies the input-angle Jacobian. Controlled
rotations use their two nonzero frequencies rather than an invalid two-point
unit-frequency assumption. Variance gradients differentiate both first and
second moments. Finite difference is a separately named gate-angle reference.

Adjoint executes the native forward vector once, propagates inverse states and
observable cotangents backwards, and accumulates 2 Re<lambda|dU|psi>. It does
not call parameter-shift, finite difference, or a PennyLane gradient. Pauli and
Hamiltonian application avoids constructing global dense observables; small
explicit Hermitian matrices are supported. Probability cotangents are streamed
one at a time, not stored as an output-by-state dense array.

| Backend | Supported native derivatives | Explicit limits |
| --- | --- | --- |
| Statevector | Analytic adjoint, occurrence shift, finite difference, expectations/variance/probability Jacobians | Adjoint rejects shots, mid-measurement/reset/CPTP and conditional evolution |
| DensityMatrix | Fixed-noise shift/finite-diff and complete analytic feedback ensembles | No mixed-to-pure substitution; mixed adjoint unsupported |
| MPS | Tensor-native shift/finite-diff, local expectations and supported dynamic ensembles | No dense fallback or MPS adjoint; truncation can bias gradient estimates |
| Tableau | Existing forward Clifford execution retained | Continuous gradients explicitly unsupported, never Clifford-rounded |

Each MPS evaluation preserves configured cutoff/memory, peak bond and discarded
weight. Pure analytic outputs include the final bond profile; analytic mixtures
include each branch profile; trajectories retain an observed per-link maximum
profile. Gradient metadata retains the evaluated resources and approximation
warning. Discarded weight is not claimed to bound final infidelity.

Dynamic parameter-shift differentiates pre-measurement probabilities and gates
inside conditional bodies, including shared inputs. Tests compare complete
ensemble expectations, not only one sampled trajectory. Trainable classical
thresholds, nonsmooth branches, arbitrary postselection, continuous tableau
parameters and reused parameterized loop bodies are explicitly unsupported.

## Framework And Shot Evidence

Torch tests execute tensor input/output, nonlinear Torch preprocessing, scalar
loss backward, autograd.grad, gradcheck, vector cotangents, fixed features,
unused inputs, float32/float64, and real SGD updates. A two-parameter native
shift/Torch SGD example reduces loss 0.4132459974 -> -0.9951666606 in 30 steps.

Autograd tests execute real grad and jacobian through nonlinear preprocessing
and native quantum execution, including array inputs, scalar losses and an
optimization loop. These are custom primitive VJPs, not array conversion.
JAX grad/JIT/VMAP and TensorFlow GradientTape are NOT implemented or claimed.
Their constructors/forward selection fail explicitly instead of coercing a
tracer to numpy. Verification of future implementations must use optional
isolated framework environments and real backward/JIT capability tests, without
adding these packages to core dependencies. Higher-order Torch/Autograd/native
derivatives and simulator-level backprop are also explicitly unsupported.

Finite shots now execute actual sampled expval/variance/probs, not analytic
statistics carrying a shots label. Shot vector partitions/copies have separate
seeds, ordering and metadata; counts totals are tested per partition. Finite-shot
gradients are labeled estimates and tested with statistical tolerances. No
unsupported sampling uncertainty or generalization benefit is claimed.

For backward compatibility only, a legacy QNode containing a state/density
query keeps state/expval/variance/probs analytic while sample/counts use shots.
This mode emits FutureWarning and records each measurement's actual shot count
plus legacy_analytic_state_queries. Prefer shots=None and local sample/counts
shots for this mixed query. This extension is not claimed as PennyLane's full
shot/state contract.

## Independent Verification

Native tests verify analytic RX/RY/RZ, phase/controlled/multiqubit generators,
shared and nonlinear inputs, Hamiltonians, nested outputs, probabilities,
variance, VJP/JVP orientation, finite-diff convergence, keyword/array/fixed
inputs, mixed noise, dynamic branch derivatives, shot vectors and rejection
paths. The 100-qubit MPS RY+GHZ-chain local Z gradient equals -sin(theta), with
statevector and density expansion calls replaced by failures and peak bond two.

The native two-qubit adjoint training example reduces loss
1.3081243682 -> -1.9999637417 in 50 deterministic steps, retaining gradient trace
and provenance. This is an executable optimization proof, not model generalization.

Fourteen public PennyLane black-box differential scenarios cover RX, RY, RZ,
phase, shared inputs, scaling, nonlinear preprocessing, controlled rotation,
probabilities, variance, fixed noise, dynamic feedback, Hamiltonian and MPS.
Each prints expected/native/upstream values, absolute/relative differences,
tolerance, actual version and status. Both PL 0.44.1 and 0.42.3 were exercised.
Pure native tests run without Qiskit/PennyLane/framework installations.

One public-oracle difference is retained rather than hidden: at theta=.47,
PL 0.42.3's automatically deferred shared-parameter conditional gradient was
-0.0245536202, but its forward central difference and its public explicit
defer_measurements transform gave -0.0491072352. Native and mathematical values
agree with the latter. PL 0.44.1 automatic gradient differs only by ~2.7e-9.
The differential test records both automatic and explicit results and uses the
explicit public transform plus independent central difference as the oracle.
An initial Hamiltonian test-oracle setup also queued an unused Pauli operator;
the reference was corrected to construct only the measured observable.

Final verification uses a clean tracked archive plus the exact staged patch;
unrelated user files are neither included nor reverted. All gates below exited
zero on the final implementation:

| Gate | Final result |
| --- | --- |
| SDK-free full pytest -q -rs | 774 passed, 113 skipped |
| Installed full pytest with explicit coverage | 951 passed, 4 skipped |
| Installed versions | Qiskit 2.4.1, Aer 0.17.2, PennyLane 0.44.1; Torch and Autograd available |
| Alternate full pytest -q -rs | 916 passed, 39 skipped |
| Alternate versions | Qiskit 2.6.0, Aer 0.17.2, PennyLane 0.42.3; Torch absent |
| Gradients/QML/interfaces/devices/primitives/circuit paths | 230 passed |
| New native derivative test instances / framework cases | 26 / 7 |
| Public gradient differential scenarios | 14 passed on each SDK version |
| Explicit overall line coverage | 87.0240%, baseline 86.6755%; no exclusions added |
| Native adjoint / gradient engine | 92.96% / 97.70% |
| Classical derivative trace / framework bridge / ShotSpec | 96.30% / 97.18% / 100% |
| Final complete local matrix | exit 0 |
| compileall / staged whitespace check | exit 0 |
| Native training/adjoint/shot examples in SDK-free environment | exit 0 each |
| Torch training example | exit 0 |
| Privacy/dependency/vendor scan and full legal tests | passed; no project dependency or package payload added |

The installed four skips remain the pyquafu/NumPy conflict, two absent dynamics
checks and an absent optimization check. SDK-free/alternate skips are optional
SDKs/frameworks absent in those environments; they are not marked as executed
backward tests. The matrix's existing optional coverage detector reported
unavailable; explicit pytest-cov above supplies the measured coverage. An initial
multi-source --cov invocation encountered NumPy's duplicate-import error; the
standard --cov=quantumbridge invocation and all final clean runs passed.

An additional native test disables the shift/finite-difference occurrence path
and proves adjoint still returns the analytic derivative with zero shifted
evaluations. No historical regression test was weakened or removed. New-commit
publication/CI is verified using its exact SHA after commit; baseline CI is not
reused as new-commit evidence.

## Resources And Remaining Work

Current explicit budgets: 1024 real input coordinates for dual tracing, 4096
recorded gate angles, 2 million output-by-angle Jacobian entries, probability
outputs at most 16 wires, generic dense sampled observables at most 10 wires,
generic dense adjoint observables at most 12 wires and 100 million estimated
probability-adjoint contraction elements. Native device memory/branch/execution
limits and total shot-vector max_shots apply. These are rejection limits, not
silent approximations. Adjoint probability cotangents are streamed.

Stage 11K delivers a verified first-order native differentiation and two-framework
closed loop. Full QNode/autodiff parity remains PARTIAL: general broadcasting,
all gradient recipes/operators, arbitrary parameterized loops/postselection,
MPS/mixed adjoint, simulator backprop, JAX/TF, higher-order derivatives, capture
and complete transform/device/executor contracts remain open. Complete Qiskit
transpilation/serialization, all simulators/algorithms/ecosystems and authorized
real hardware verification also remain in the full objective. Studio stays last.

## Public References

- [PennyLane QNode API](https://docs.pennylane.ai/en/stable/code/api/pennylane.QNode.html)
- [PennyLane parameter-shift API](https://docs.pennylane.ai/en/stable/code/api/pennylane.gradients.param_shift.html)
- [PennyLane interface semantics](https://docs.pennylane.ai/en/stable/introduction/interfaces.html)
- [Public deferred measurement transform](https://docs.pennylane.ai/en/stable/code/api/pennylane.defer_measurements.html)

Public behavior/mathematics only; no third-party implementation/test code copied.
