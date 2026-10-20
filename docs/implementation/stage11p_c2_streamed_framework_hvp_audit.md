# Stage 11P-C2 Streamed Framework HVP Audit

Starting local main: 8961779f3408bb3961f75751d973b7b88580e831.
The preceding turn made concrete progress: committed native exact second-order
rules and genuine four-framework second derivatives, with clean matrix and
coverage evidence. Complete Qiskit/PennyLane independent functional parity
remains ACTIVE / INCOMPLETE.

## Observed Starting Gaps

Native direction-only second execution already streams Hessian-vector products.
Framework bridges instead request a full native Hessian and then contract it:
Torch NativeSecondVJP uses an output-by-parameter-by-parameter tensor; Autograd
native_hessian returns that tensor; TF second_order_vjp and JAX second JVP use
the same packed Hessian path through NativeHostKernel.run_second.

This blocks actual framework HVPs under a small full-Hessian budget and creates
unnecessary second-order storage. Source classical maps, coefficient slots,
actual child processors and external framework losses must all keep their real
chain rules. Merely deleting a storage check, returning a detached constant,
using finite differences or disguising full-Hessian materialization is invalid.

Four independent initial contracts exercise real Torch, Autograd, JAX and TF
HVPs for a shared nonlinear gate/coefficient QWC loss, with a native plan spy
requiring directional execution and max_hessian_elements=1. Their initial
execution receipt before runtime changes: four failed in 3.65 seconds, exit 1,
`/tmp/qb-stage11pc2-initial-red.log` and its independent `.exit` file.

JAX also requires a genuinely linear tangent rule and valid transpose for
reverse-over-reverse differentiation; a pure callback of a tangent alone does
not supply such a rule. Public JAX derivative/callback documentation is a
behavioral reference, not copied implementation/test source. No quantum SDK,
hardware, token, Studio, third-party source or remote publication work belongs
to this batch.
