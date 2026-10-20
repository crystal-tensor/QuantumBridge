# Stage 11P-B Native TensorFlow Gap Audit

Date: 2026-10-20. Starting local main:
`edf4728f9d51d8825a2f07390edbea71435fa80d`.
Full independent Qiskit/PennyLane functional replacement remains ACTIVE /
INCOMPLETE. This initial audit is not a TensorFlow completion claim.

## Starting Components

| Component | Starting status / native reuse |
| --- | --- |
| Native QNode / Tape / AngleRecorder | NATIVE_EXECUTABLE: source recording, parameter AST, owned native plans and output trees |
| Native shift/adjoint/Jacobian/VJP | NATIVE_EXECUTABLE first-order supported contracts; higher order remains unsupported |
| TransformProgram / QWC / coefficients | NATIVE_EXECUTABLE real child execution, joint groups, reverse postprocessing and coefficient product rules |
| interfaces/jax_autodiff.py | NATIVE_EXECUTABLE supported CPU JAX bridge with source/shape/native host plan machinery; not an alternative quantum engine |
| interfaces/qnode_autodiff.py | NATIVE_EXECUTABLE supported Torch/Autograd; TensorFlow dispatch explicitly UNSUPPORTED |
| diff/scalars.py | TF coefficient primal/differentiation explicitly UNSUPPORTED; no graph-retaining native TF bridge |
| TF native interface module | NOT_STARTED at this HEAD; no native TF array/gradient implementation |
| compat/pennylane_full/interface_adapter.py | PASSTHROUGH/inventory scaffold only; not native TensorFlow quantum execution |
| MPS / ShotSpec / result trees | NATIVE_EXECUTABLE bounded tensor/sampling/native gradient components to reuse |
| TF graph/XLA/distributed/export protocols | NOT_STARTED / UNSUPPORTED; not established by an eager value conversion |

There must not be a second QNode, Device or quantum gradient algorithm.
The source/host plan machinery currently inside the JAX bridge can be shared
where it genuinely removes duplication; framework graph rules remain separate.
Existing JAX/Torch/Autograd behavior must remain under regression tests.

## Environment Evidence

The actual host is macOS 27.0.1 arm64, Python 3.12.6 universal2. The main
environment has no TensorFlow. Official PyPI metadata currently supplies
TensorFlow 2.21.0, Python >=3.10, NumPy >=1.26.0, including the 223488205-byte
`tensorflow-2.21.0-cp312-cp312-macosx_12_0_arm64.whl`.
The isolated `/tmp/qb-stage11pb-tf-env` actually loaded TensorFlow 2.21.0,
NumPy 2.5.4, reported CPU:0 / eager=True, and executed a float64 Variable.
`uv pip check` completed with exit 0. Normal verified uv/PyPI downloads were
used; no base environment, authentication or TLS settings were changed.
TensorFlow remains optional, not a core dependency.

## Persisted Red Contracts

`tests/interfaces/test_native_tensorflow_grad.py` contains two independent
tests requiring actual TensorFlow. First, GradientTape of RY/Z squared loss
must return -2*cos(theta)*sin(theta). Second, the real transformed QWC result
for (.7+.1*theta)X0 + .2X0Z1 must retain both product-rule terms. Both instrument
the existing native ExecutionPlan Jacobian and prohibit finite-diff.
Before production edits both actually failed (2 failed, 1.33s, exit 1): basic
`qnode_interface` UnsupportedFeature and transformed `transform_interface`
UnsupportedFeature. Both subsequently passed with actual TF tensors, native
Jacobian spies and unchanged independent formulas. Missing-TF skips are not
red evidence and not TensorFlow functionality evidence.

## Public API Boundary

The official [custom-gradient contract](https://www.tensorflow.org/api_docs/python/tf/custom_gradient)
requires explicit derivative rules and extra handling for variables read
inside the decorated operation. The
[NumPy host-function contract](https://www.tensorflow.org/api_docs/python/tf/numpy_function)
does not provide autodiff by itself and has XLA/export/process restrictions.
These public contracts are references only; no upstream implementation or
tests are copied. Independent native derivatives must supply the VJP.

TensorFlow will own classical preprocessing and outer-loss graphs; native
plans will own quantum execution/derivatives and reverse postprocessing.
Symbolic values must not be read during tracing. Real CPU graph execution,
shape/dtype/error status, snapshots of configuration, seed semantics and
bounded callbacks need explicit tests rather than labels or tracing counts.
Variable closure support must either be proved with the correct graph/variable
contract or rejected explicitly. Higher order/GPU/TPU/XLA/distributed/portable
SavedModel remain open until independently implemented and verified.

Legacy PennyLane TF oracle availability will be checked in a compatible
isolated environment; unsupported/unavailable upstream paths cannot count as
matching evidence. Independent math/native/other-interface references remain
mandatory even when a public oracle is unavailable.

No user Studio/Router, cloud/hardware/token, history rewrite, tag/release,
workflow/authentication/TLS changes or new remote CI claim belongs to this batch.
