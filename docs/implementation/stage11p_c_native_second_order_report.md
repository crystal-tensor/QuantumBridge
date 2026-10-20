# Stage 11P-C Bounded Native Second Derivatives

Date: 2026-10-20. Starting local main: `612c25a17299e6e518998f065a2b31415e2ee274`.
Full independent Qiskit/PennyLane functional replacement remains ACTIVE /
INCOMPLETE. This checkpoint does not redefine the goal as a subset or adapter.

## Implemented Scope

Native `max_diff=2` adds `compute_hessian`, `compute_hvp` and their
execute-and-compute counterparts. First-order default behavior remains guarded.
Gate recipes cover RX/RY/RZ/phase, CRX/CRY/CRZ, CP and RXX/RYY/RZZ. Controlled
rotations retain both frequencies .5/1; second rules convolve signed exact
shift rules, including diagonal and mixed pairs, not finite differences.

Second classical traces retain nonlinear/shared input-map curvature. Native
HVP traces store gradient-direction derivatives and accumulate each quantum
mixed contribution directly, without an input-sized identity/full Hessian.
Native output/argument blocks preserve output trees and selected input shapes.

Existing transformed child execution and reverse processors are reused.
SecondDual payloads trace only numerical means/classical slots, not resource
metadata. Child curvature, processing curvature, coefficient and cross-child
product terms all contribute. Analytic variance includes the second moment,
mean Hessian and gradient outer product. No original-QNode bypass is used.

Torch custom backward/double backward, Autograd primitive VJP, JAX custom JVP
and TF nested custom gradients now use genuine native second derivatives.
Outer classical losses and preprocessing remain in the framework graph.
The second boundary rejects third differentiation, rather than silently
returning zeros. Framework paths currently use packed Hessians; they do not
claim streamed framework HVP, GPU simulation, XLA lowering or simulator backprop.

## Work And Boundaries

Finite-shot support requires explicit seeds, positive integer shots and verified
linear quantum-output processing. None/uniform/weighted fixed-coefficient QWC
vectors have independent group/partition/shift streams and exact physical-work
receipts. Finite variance, unverified nonlinear sampled processing, local fixed
measurement seeds and coefficient-dependent weighted integer allocation reject.
No stochastic pathwise or strict estimator-accuracy guarantee is made.

HigherOrderLimits preflights input/output/Hessian elements, shift pairs, total
tapes/shots, derivative buffers and graph/processing nodes. Pair construction
stops at the shift budget before materializing a quadratic recipe list.
Shift/tape counts denote plan evaluations/partitions, not a claim that a
multi-measurement plan invokes the simulator only once. Device measurement
telemetry and physical shots are accounted separately.
Derivative-buffer limits are distinct from each device's state-memory budget;
neither is a universal resident-memory or arbitrary Python callback sandbox.
Explicit second adjoint/finite-difference requests, general record-conditioned
second derivatives, reused parameterized loops and postselection are not added.

## Initial Failures And Repairs

- Four actual initial red contracts: native RY Hessian, real TF nested tapes,
  Torch double backward and nonlinear/coefficient QWC TF second derivative.
  Receipt: `/tmp/qb-stage11pc-initial-red.log`, exit 1, 8.36 seconds.
- The first integrated TF H2 attempt correctly rejected 15,990 planned shifts:
  fixed numerical phases had been packed as independent framework variables.
  Numeric constants are now frozen separately; only real framework scalars
  enter differentiable packed inputs. Budgets were not relaxed.
- Public transformed live-coefficient PennyLane Hessians can return unresolved
  ArrayBox objects. The native result is independently checked analytically
  before classifying this as an upstream unsupported numerical oracle, not a
  positive match or a native failure hidden by an expected failure.
- Two further actual red tests exposed missing static second-callback shape
  preflight in JAX/TF. Declared Hessian sizes are now checked before callback
  creation, so a budget failure cannot itself allocate an oversized NaN tensor.
- The first clean matrix stopped at one obsolete max_diff=2 rejection assertion
  (2,125 passes, five skips, three expected upstream failures). It now validates
  the correct first gradient at max_diff=2 and retains explicit max_diff=3
  rejection. This failed receipt is not counted as a successful matrix.

## Integrated Evidence

The 100-wire GHZ/RY/QWC MPS test forbids native vector/density expansion,
checks Hessian/HVP against cos/sin derivatives and checks every actual second
execution's bond/storage/truncation telemetry. This is low-entanglement evidence,
not an arbitrary-circuit efficiency claim.

H2 uses one native Gaussian/RHF/Jordan-Wigner build at 1.4 bohr. Ansatz
Hessian/HVP are compared with both native unsplit execution and an independently
specified two-determinant matrix formula. Actual regularized/clipped Newton
updates reduce energy. Nested TF second derivatives reuse the fixed Hamiltonian.
These are not molecular-geometry Hessians or differentiable Hartree-Fock.

The SDK-free example returns value 0.646615706406933, Hessian
`[[-0.6723327735811431, -1.060970578417505], [-1.060970578417505, -2.586462825627732]]`,
and streamed HVP `[0.04935806409279426, 0.35155061632131757]`, four real second
shift evaluations, zero physical shots.

## Validation

Runtime/test snapshot: `76c5f867f39b23bf3eb640e46c8dd35b78a4a74e`.
Production subtree: `40cf4dc536253e8c98a2e2ae55e78043211fb1a0`.
No dirty user Studio/Router content is included. These are new Stage 11P-C
receipts; earlier Stage 11P-B gates are not used to validate changed source.

| Gate | Actual result |
| --- | --- |
| Matrix first full pytest | 2,128 passed, 5 skipped, 3 xfailed, 57 warnings; 220.94 s |
| Matrix second full pytest | 2,128 passed, 5 skipped, 3 xfailed, 57 warnings; 218.25 s |
| SDK-free full pytest | 1,620 passed, 312 dependency skips, 5 warnings; 167.92 s; exit 0 |
| Alternate interfaces/derivatives/transforms/second-order/public subset | 284 passed, 1 skipped, 2 public xfails; 50.47 s; exit 0 |
| Independent JAX 0.12.0 regressions/second order | 52 passed, 6 absent-other-framework skips; 5.31 s; exit 0 |
| Final native/second-framework/public focus | 65 passed, 2 public xfails; 7.10 s; exit 0 |
| Legal/migration subset | 5 passed; 0.11 s; exit 0 |
| compileall / git diff --check | Both exit 0 |
| Complete local matrix | All 28 sections finished; exit 0 |
| Embedded true full coverage run | 2,128 passed, 5 skipped, 3 xfailed, 57 warnings; 615.06 s; exit 0 |

Statement coverage is 23,534 / 26,286 = 89.53054858099368%, with 2,752
missing statements and the same 68 excluded lines as the prior checkpoint.
No coverage exclusions are added. HigherOrderLimits is 28/28, second-order
quantum execution is 205/223, second classical tracing is 104/111 covered
statements. Coverage is not API or full functional parity evidence.

Logs and independent exit files are `/tmp/qb-stage11pc-matrix.*`,
`/tmp/qb-stage11pc-sdkfree.*`, `/tmp/qb-stage11pc-alternate.*` and
`/tmp/qb-stage11pc-latest-jax.*`. The failed first matrix and first alternate
oracle attempt are preserved separately as `*-initial.log` / `*-initial.exit`.

An oracle-only patch after the matrix freeze catches the actual public 0.42.3
NotImplementedType failure; it does not change native source or hide native
failures. Its clean targeted snapshot is
`cb512cc9152f36e9a993ad026f171b5449a33c99`. The matrix and that snapshot have
identical production Python source. Final public tests are rerun in both
installed versions. Each version has six actual numerical matches (all four
backprop cases plus two direct shift cases), and two transformed public shift
limitations. Version 0.44.1 returns unresolved ArrayBox objects; 0.42.3 raises
NotImplementedType. These two cases are not positive parity evidence. The
third full-suite xfail is the previously documented public JAX shift/VMAP path.

All environments use Python 3.12.6. Main overlay: NumPy 2.4.6, Qiskit 2.4.1,
PennyLane 0.44.1, JAX 0.7.1, Torch 2.12.0, Autograd 1.8.0, TF 2.21.0,
PyArrow 23.0.1. Alternate overlay: Qiskit 2.6.0, PennyLane 0.42.3, JAX 0.6.2,
Autograd 1.9.1; same NumPy/Torch/TF/PyArrow. Independent JAX is 0.12.0 with
NumPy 2.5.4 and no quantum SDK/TF/Torch/Autograd. SDK-free NumPy 2.5.4 has
none of the quantum SDKs or four optional autodiff frameworks.

The main overlay's fresh pip check exits 1 for pre-existing WeasyPrint/tinycss2
and pyquafu/NumPy conflicts. It is not called dependency-clean or a real Quafu
validation. No installed/global environment was modified in this checkpoint.

## Remaining Acceptance Work

This is a working bounded second-order checkpoint, not complete Stage 11P/full
gradient parity. Further work includes additional gate generators and complete
device protocols, second adjoint, streamed framework HVP, combined whole-device
and derivative memory accounting, broader stochastic second-order/error-status
contracts, general record/loop/postselection derivatives, and third/higher
orders. The integrated H2 second proof currently covers native and TF paths;
the other three frameworks have real analytic/product-rule Hessian evidence,
not an assertion that every chemistry/framework combination is validated.
Full Qiskit/PennyLane core and ecosystem replacement and real authorized cloud
backend evidence remain separate, unfinished requirements. Studio stays last.

## Source And Publication

Zero upstream implementation/test ports and no vendoring. Optional frameworks
provide classical differentiation; no SDK quantum engine supplies native values
or derivatives. No cloud/hardware/token, Studio/Router, tag/release, credential,
authentication/TLS or package/environment-tree changes are included.
The user's unrelated dirty Studio/Router files are preserved and excluded from
clean scoped validation and any checkpoint commit. No remote push or exact-SHA
CI success is claimed without restored authorization and a fresh FF check.

ChatGPT collaboration was authorized, but its complete prior prompt remained an
unresolved content reference after a plain-text follow-up. Partial streamed
text was not treated as a complete new specification. This checkpoint follows
the explicit broad user goal and independently observed source gaps.
