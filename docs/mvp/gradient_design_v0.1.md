# QuantumBridge Gradient Design v0.1

Status: Draft  
Date: 2026-06-04  
Source basis: `functional_spec_v0.1.md`, public parameter-shift mathematics, and independently authored QuantumBridge MVP scope.  

This document is design-only and contains no SDK implementation code.

## 1. Gradient MVP goal

MVP v0.1 supports gradients of scalar expectation objectives built from circuits with supported parameterized rotation gates. The first gradient method is parameter-shift because it is mathematically simple, exact for the supported gate family under the standard generator convention, and easy to verify with independent analytic tests.

## 2. Parameter-shift mathematical definition

For supported one-parameter gates whose generator has the standard two-eigenvalue form used by Pauli rotations, an expectation objective

```text
f(theta) = <psi(theta)|O|psi(theta)>
```

has derivative:

```text
df/dtheta = 0.5 * [f(theta + pi/2) - f(theta - pi/2)]
```

for the MVP RX, RY, and RZ rotation convention.

For multiple parameters:

```text
grad_j f(theta_vector) = 0.5 * [f(theta_vector with theta_j + pi/2) - f(theta_vector with theta_j - pi/2)]
```

All other parameter values remain fixed during the shift for parameter `j`.

## 3. MVP 支持哪些门的梯度

Supported for parameter-shift:

- RX angle parameters.
- RY angle parameters.
- RZ angle parameters.

Supported objective type:

- Scalar exact expectation value from StatevectorDevice.
- Hamiltonian expectation represented as a sum of supported Pauli observables.

Supported parameter shapes:

- Single scalar.
- Ordered list or vector of scalars.
- Named mapping when the API can associate names with circuit parameters.

## 4. MVP 不支持哪些梯度

Not supported in MVP:

- Gradients of custom unitary matrices.
- Gradients of Phase gate unless a later design record explicitly adds its generator and shift rule.
- Gradients through measurement samples or finite-shot stochastic objectives as a stable API.
- Gradients of counts, bitstrings, or non-scalar result fields.
- Higher-order gradients.
- Adjoint differentiation.
- Backpropagation through array frameworks.
- Natural gradient and quantum natural gradient.
- General parameter transforms.
- Gradients through mid-circuit measurement, reset, noise, or conditionals.

Unsupported requests must fail with QuantumBridge-authored diagnostics and method metadata explaining which parameter or operation is outside MVP support.

## 5. Expectation gradient input/output contract

Input contract:

- Objective description: callable objective contract or structured QuantumBridge objective record.
- Parameters: scalar, ordered vector, or named mapping.
- Device: exact statevector device in MVP.
- Observable or Hamiltonian: supported observable model.
- Gradient options: selected parameter subset, shift value, and output metadata preference.

Output contract:

- Gradient values in a shape corresponding to input parameters.
- Optional scalar objective value at the unshifted point.
- Metadata:
  - method: parameter-shift.
  - shift: `pi/2` default for MVP-supported rotations.
  - evaluated parameters.
  - number of objective evaluations.
  - unsupported parameters, if any.
  - device mode.

## 6. VQE 如何调用 gradient engine

VQE uses the gradient engine when:

- The ansatz is parameterized by RX, RY, or RZ gates.
- The Hamiltonian is made of supported observables.
- The selected optimizer requests gradients.

Flow:

1. VQE builds the circuit for the current parameter vector through the ansatz contract.
2. VQE evaluates Hamiltonian expectation on the exact statevector device.
3. For each selected parameter, the gradient engine requests shifted objective evaluations.
4. VQE passes gradient values to the optimizer.
5. VQE records objective value, gradient metadata, and parameters in the trace.

If the gradient engine rejects a parameter, VQE may either fail fast or use a future fallback method. MVP default is fail fast.

## 7. QAOA 如何调用 gradient engine

QAOA uses the gradient engine when:

- Cost and mixer layers are built from supported parameterized rotations.
- The objective is a scalar expectation of the MaxCut cost Hamiltonian.
- The selected optimizer is gradient-based.

Flow:

1. QAOA converts graph edges into an MVP cost Hamiltonian.
2. QAOA builds a shallow parameterized circuit for current angles.
3. The objective evaluates expected cut value or energy under a documented sign convention.
4. Parameter-shift evaluates each cost and mixer parameter.
5. Optimizer updates angles and records trace metadata.

If QAOA uses operations outside supported gradient rules, it must declare gradient unsupported for that configuration.

## 8. NumPy / JAX / Torch 后续集成边界

MVP expectation:

- Numeric parameters may be ordinary Python floats or NumPy scalar/array values if implementation chooses NumPy.
- The gradient engine returns plain numeric values or arrays suitable for simple optimizers.

Deferred:

- JAX transformation compatibility.
- Torch autograd tensor integration.
- Native framework gradient tapes.
- Differentiation through simulator internals.

Boundary rule:

- MVP should not pretend to be a native autodiff backend. It exposes explicit gradient computation. Later framework bridges can wrap the same objective contract with framework-specific adapters.

## 9. Numerical validation

Behavior tests must compare parameter-shift results to independent analytic formulas, including:

- `RY(theta)` with `Z` expectation equals `cos(theta)`.
- Gradient equals `-sin(theta)`.
- At `theta = 0`, gradient is near `0`.
- At `theta = pi/2`, gradient is near `-1`.

Recommended tolerance:

- Exact-device parameter-shift gradient: absolute tolerance around `1e-7`.

## 10. Clean-room rationale

The gradient design is based on public parameter-shift mathematics for Pauli-generator rotations. It does not copy any third-party gradient engine, tape system, transform API, tests, comments, or documentation.

