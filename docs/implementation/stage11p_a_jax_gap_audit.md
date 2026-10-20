# Stage 11P-A Native JAX Gap Audit

Date: 2026-10-20. Starting local main HEAD:
`bc17863eef852419b52263112724a6659e67a8f8`.
Full independent Qiskit/PennyLane functional parity remains ACTIVE / INCOMPLETE.
This audit starts a new implementation batch; it is not a completion report.

## Existing Components

| Component | Starting status and native reuse |
| --- | --- |
| interfaces/jax_interface.py | INTERFACE_STUB for autodiff: to_jax only converts an array; it is not a quantum derivative bridge |
| interfaces/qnode_autodiff.py | NATIVE_EXECUTABLE supported CPU Torch/Autograd bridges; JAX dispatch explicitly UNSUPPORTED |
| qml/qnode.py and Tape | NATIVE_EXECUTABLE owned source recording, measurement trees, native ExecutionPlan and transform entry points |
| diff/qnode_engine.py | NATIVE_EXECUTABLE angle-occurrence shift/adjoint, real native device execution, Jacobian/JVP/VJP products and sampled work receipts |
| diff/trace.py | NATIVE_EXECUTABLE first-order Dual preprocessing and result tree reconstruction; not a replacement for JAX preprocessing |
| diff/scalars.py | NATIVE_EXECUTABLE live Torch/Autograd coefficients; JAX coefficient primals explicitly UNSUPPORTED |
| diff/compiled_parameters.py | NATIVE_EXECUTABLE parameter AST replay across native compilation/transform reconstruction |
| transforms/program.py | NATIVE_EXECUTABLE child plans/reverse postprocessing/native coefficient product rule; JAX/TF input rejected at source |
| B4 QWC / PauliGroupResult | NATIVE_EXECUTABLE real shared samples, group means/covariance, bounded shot allocation and output metadata |
| B5 transformed autodiff | NATIVE_EXECUTABLE bounded explicit child/postprocessing Jacobian products, not matrix-free VJP |
| B6 coherent defer | NATIVE_EXECUTABLE supported record-ancilla subset; reset/postselection/noisy/general dynamic semantics remain unsupported |
| Native MPS / ShotSpec / result trees | NATIVE_EXECUTABLE native tensors, bounded sampling/partitions and real/typed nested outputs; no JAX integration yet |
| JAX eager/grad/JVP/jacrev/jacfwd/JIT/VMAP | NOT_STARTED at the starting SHA beyond the array conversion stub |
| TensorFlow / higher-order / capture | UNSUPPORTED or NOT_STARTED as documented; outside this first-order JAX batch |

There is no existing JAX SDK passthrough used as a quantum engine. Quantum
execution and derivatives must continue to use these native components.

## First Persisted Tests

`tests/interfaces/test_native_jax_grad.py` adds two independent mathematical
contracts: actual jax.value_and_grad of RY/Z gives cos(theta)/-sin(theta),
and a transformed QWC Hamiltonian gives .9 sin(theta)/.9 cos(theta). Both
instrument the existing native child Jacobian and prohibit finite-diff.
Both tests actually failed (exit 1) before runtime edits in isolated CPU
JAX/jaxlib 0.12.0 / NumPy 2.5.4 with x64 enabled and no Qiskit/PennyLane.
The failures were native qnode_interface and transform_interface
UnsupportedFeature respectively. Missing-JAX skips are not red evidence.

The main environment currently has no JAX/jaxlib. A new isolated environment
is outside the repository. Its first bundled-pip download failed verified TLS
certificate validation; a normal system-pip attempt failed with a TLS EOF.
Neither certificate checks nor global TLS/authentication settings were changed.
The existing uv installer succeeded with its normal defaults; no certificate
override or verification bypass was used. The main environment is unchanged.

## Planned Integration Boundary

Reuse the existing QNode source recorder, native child plans and B5 bounded
Jacobians. JAX owns differentiable preprocessing and outer loss chain rules;
the native engine owns quantum values/derivatives and reverse postprocessing.
Trace-time shape planning must never convert a JAX tracer to float/NumPy or
run a quantum simulator. Runtime host callbacks, if used, must be explicit,
pure, CPU-only and use declared shape/dtype and sequential VMAP semantics.
No callback side effect may be reported as a guaranteed JIT execution count.

The public [callback contract](https://docs.jax.dev/en/latest/_autosummary/jax.pure_callback.html)
and [custom derivative contract](https://docs.jax.dev/en/latest/notebooks/Custom_derivative_rules_for_Python_code.html)
are architecture references only; no upstream implementation/test source is
ported. A custom JVP must be linear in tangents and separately verified in
forward and reverse mode. Numerical callback failures need an explicit tested
status/validation protocol, not reliance on exceptions inside pure_callback.

Static shape/Jacobian/parameter/shot/transform/batch limits must reject before
large allocation. Float32/x64 behavior, coefficients, nested trees, finite-shot
seeds, analytic JIT/VMAP, native MPS and geometry-derived H2 are independent
acceptance gates. None is claimed implemented by this initial audit.

No Studio/Router, cloud/hardware/token, workflow/authentication changes,
history rewrite, tag/release, vendoring or remote CI claim belongs to this batch.
