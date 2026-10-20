# Stage 11P-C2 Streamed Framework Hessian-Vector Products

Date: 2026-10-20. Starting local main:
`8961779f3408bb3961f75751d973b7b88580e831`.
Full independent Qiskit/PennyLane functional replacement remains ACTIVE /
INCOMPLETE. This checkpoint does not replace that goal with an adapter or subset.

## Implemented Scope

True CPU Torch, Autograd, JAX and TensorFlow second rules now request a native
directional derivative, not an output-by-parameter-by-parameter Hessian followed
by contraction. The existing convolved exact shift engine, native plans,
devices, transform children and processors perform the quantum calculation.
There is no quantum SDK call, finite-difference substitution or detached
constant-gradient stand-in. Nonlinear source maps, live Hamiltonian coefficients,
outer classical losses and cotangent derivatives retain their real chain rules.

Torch double backward returns both the contracted native HVP and Jacobian times
direction. Autograd uses its public fused primitive VJP registration so both
input branches share one real directional call. TF nested custom gradients
pass the actual incoming direction to CPU callbacks and bound directional error
buffers before allocation. Third quantum derivatives still explicitly reject.

JAX has one optional module-global linear primitive, explicit JVP/transpose,
sequential mapped rules and CPU host lowering. `jax.extend.core.Primitive` and
the documented interpreter extension namespaces are used, not `jax._src` or a
private SDK derivative helper. Differentiating only the linear direction at a
fixed primal is supported; differentiating that primal again rejects third
quantum derivatives. Numerical transposition streams one direction per active
output row. Two planning passes check aggregate shifts/tapes/shots before any
row executes, without retaining all row plans or materializing a full Hessian.

Finite-shot HVP recipes and seeded streams are direction independent. This
defines an actually linear sampled operator for transposition, including zero
directions and stationary nonlinear source maps. Structural input dependency
survives numerically zero first/second directional values; fixed numerical gate
angles do not acquire irrelevant derivative recipes. None/uniform/weighted
fixed-coefficient QWC shot vectors preserve real partition/group/shift receipts.
The existing rejection of sampled variance, nonlinear stochastic processors,
local fixed measurement seeds and trainable weighted integer allocation remains.

## Independent Evidence

Four genuine framework contracts initially failed in 3.65 seconds, exit 1,
before production edits. Each sets `max_hessian_elements=1`, exercises a shared
nonlinear gate/coefficient QWC loss and spies on the actual native second plan:
the direction must be supplied and the second tensor's last dimension is one.
The old first/second-order tests remain, including explicit third-order guards.
The callback preflight test now rejects a tiny actual memory budget rather
than requiring an unused dense Hessian allocation.

Additional tests cover nested vector losses and cotangent product terms, real
JAX forward/reverse/JIT/VMAP/direction differentiation, aggregate transpose row
budgets, invalid inputs, eager exceptions and compiled NaN failure propagation.
Finite-shot RY examples use 80,000 actual native second-order shots for 10,000
shots per evaluation. The TF eager forward, first and second callbacks together
observe 130,000 physical shots; those are not inferred trace-time counts.

Actual four-framework 100-wire GHZ/RY/QWC MPS HVPs forbid dense vector, density
and reduced-density conversion. Every real second evaluation checks bond two,
bounded tensor storage, zero discarded/truncated weight and zero physical shots.
This is low-entanglement evidence, not arbitrary-circuit MPS efficiency.

`python -m examples.native_framework_hvp --interface all --chemistry` builds one
native Gaussian/RHF/Jordan-Wigner H2 Hamiltonian at 1.4 bohr and then forbids
another chemistry build while all four frameworks execute. An independent
two-determinant matrix formula checks each value and HVP. The actual initial
example run found a 4.171e-9 precision mismatch from constructing the Torch
direction as float32; the fix uses the input dtype in each framework, without
relaxing the acceptance tolerance. Initial failure receipts are retained.

Observed all-four H2 values: -1.0279252771620968; directional curvature is
0.2799425351344644 (TF last digit 3), with full-Hessian budget one and exactly
one geometry build. Toy shared-input values are 0.3054913975185895; HVP is
[-0.21737561189204485, 0.34934884273009875]. These are fixed-Hamiltonian ansatz
derivatives, not geometry Hessians or differentiable Hartree-Fock.

## Validation

Runtime/test snapshot: `a1aeee28168b876a984e4f491606d0cba4cce6ea`.
Production subtree: `4bffe74ef667765097e7e9b345d563db852566ce`.
Only 19 explicit checkpoint-owned paths enter this clean Git-tree snapshot;
unrelated dirty user Studio/Router content is preserved and excluded. The
snapshot is `/tmp/qb-stage11pc2-final.UQ0Qbq`. Final report-only additions do not
change the frozen runtime or tests. Earlier C/C2 preliminary gates are not
substituted for this source's actual validation.

| Gate | Actual result |
| --- | --- |
| Matrix first full pytest | 2,162 passed, 5 skipped, 3 xfailed, 57 warnings; 243.05 s |
| Matrix second full pytest | 2,162 passed, 5 skipped, 3 xfailed, 57 warnings; 238.97 s |
| SDK-free full pytest | 1,628 passed, 338 dependency skips, 5 warnings; 181.38 s; exit 0 |
| Main broad interface/gradient/transform/second focus | 621 passed, 1 skipped; 210.73 s; exit 0 |
| Alternate broad focus plus public second-order tests | 627 passed, 1 skipped, 2 public xfails; 226.21 s; exit 0 |
| Independent JAX 0.12.0 regressions and new HVP tests | 70 passed, 18 absent-other-framework skips; 13.94 s; exit 0 |
| Independent JAX 0.12.0 float32 new-HVP tests | 10 passed, 16 deselected; 2.15 s; exit 0 |
| Final all-four toy and one-build H2 examples | Both exit 0, numerical results above |
| Frozen legal/migration subset | 6 passed; 0.11 s; exit 0 |
| compileall / git diff --check | Both exit 0 |
| Complete local matrix | All 28 sections finished; exit 0 |
| Embedded true full coverage run | 2,162 passed, 5 skipped, 3 xfailed, 57 warnings; 657.16 s; exit 0 |

True statement coverage is 23,676 / 26,430 = 89.5800227014756%, with 2,754
missing statements and the same 68 excluded lines as the preceding checkpoint.
No exclusions were added. Native second execution covers 213/230 statements,
second classical tracing 111/116, JAX linear primitive 70/74, shared host 255/265,
Torch/Autograd bridge 142/146 and TF bridge 193/201. This is code-path evidence,
not an API/full functional parity percentage.

All environments use Python 3.12.6. Main overlay: NumPy 2.4.6, Qiskit 2.4.1,
Aer 0.17.2, PennyLane 0.44.1, JAX/jaxlib 0.7.1, Torch 2.12.0, Autograd 1.8.0,
TF 2.21.0 and PyArrow 23.0.1. Alternate overlay uses Qiskit 2.6.0, PennyLane
0.42.3, JAX 0.6.2 and Autograd 1.9.1, with the same NumPy/Torch/TF. Independent
JAX 0.12.0 / NumPy 2.5.4 has no quantum SDK or other three frameworks. SDK-free
NumPy 2.5.4 has neither quantum SDK nor any of the four optional frameworks.
No global/installed environment was changed during this checkpoint.

The fresh main-overlay `pip check` exits 1 for existing WeasyPrint 68.1 /
tinycss2 1.4.0 and pyquafu 0.4.5 / NumPy >=2 conflicts. It is not a clean
dependency environment or real Quafu execution proof. Matrix sections for
missing optional packages explicitly report unavailable; completing the matrix
does not imply those upstream packages were installed or every adapter ran.
The three full-suite xfails are already documented public shift/VMAP and
transformed Hessian limitations, not native failures counted as passes.

Logs and independent exits use `/tmp/qb-stage11pc2-final-{matrix,sdkfree,alternate,
jax012,jax-float32,h2,toy,pipcheck}.{log,exit}`. The main broad focus uses
`/tmp/qb-stage11pc2-main-final-focus.*`. Original red and initial H2 precision
failure logs remain separate and are not counted as passing evidence.

## Remaining Boundaries

First Jacobians and classical maps can still be dense. Directional second
storage avoids the full native output Hessian, not all quadratic memory.
Derivative/trace limits and each native device's state-memory limits remain
separate; no universal combined process-memory or user-code sandbox is claimed.
This does not add all gate generators, second adjoint, general record/loop or
postselection second derivatives, third/higher quantum orders, simulator
backpropagation, GPU/TPU/XLA execution or complete framework/device protocols.

JAX compiled HVP host failures yield NaNs, while eager failures raise. The
existing `jax_with_status` result is a forward status, not a complete new
derivative-error status protocol. JIT metadata remains static configuration;
pure callbacks may be eliminated/repeated/reordered, so trace-time callback
counts are not observed physical execution receipts. Mapped limits bound logical
per-axis expansion, not all possible scheduling or nested outer transformations.
No strict sampled estimator accuracy or stochastic pathwise derivative claim
is made. Complete core/ecosystem replacement and authorized real Quafu/backend
evidence remain separate unfinished requirements. Studio stays last.

## Sources And Publication

Zero upstream implementation/test source ports and no vendoring. Public JAX
[custom derivative](https://docs.jax.dev/en/latest/301/custom-jvp-vjp.html),
[callback](https://docs.jax.dev/en/latest/201/callbacks.html) and
[primitive](https://docs.jax.dev/en/latest/601/jax-primitives.html) contracts are
behavioral references; independently authored scalar/polynomial probes and real
native tests verify the bridge. Optional frameworks own classical graphs only.
No cloud/hardware/token, Studio/Router, tags/releases, credential, authentication,
TLS or package/environment-tree changes belong to this checkpoint.
Ordinary noninteractive fetch succeeded. Fetched remote main is
`45fe338fc0f02de9c19e0af89723755952e5fc98`, an ancestor of the local baseline
(12 committed local checkpoints ahead before this batch). GitHub connector
confirmed [run 103](https://github.com/crystal-tensor/QuantumBridge/actions/runs/39259350086)
succeeded for that old remote SHA; this is not CI evidence for the new source.
GitHub CLI is not authenticated. Ordinary noninteractive `git push --dry-run`
failed with a receive timeout; no credential/TLS workaround was attempted.
Remote publication and exact-new-SHA CI still require separate observed receipts.
