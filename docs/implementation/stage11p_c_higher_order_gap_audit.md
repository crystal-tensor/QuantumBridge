# Stage 11P-C Higher-Order Gap Audit

Starting local main: 612c25a17299e6e518998f065a2b31415e2ee274.
Full Qiskit/PennyLane independent functional replacement remains ACTIVE /
INCOMPLETE. This is an initial source audit, not a higher-order completion claim.

## Authoritative Starting Gaps

- QNode has no compute_hessian or compute_hvp. Its native derivative entry
  explicitly rejects max_diff other than one.
- ExecutionPlan computes real shift/adjoint Jacobians only. Controlled
  rotations use the two-frequency first-order recipe; their second-order
  diagonal/mixed rules must be derived rather than assumed to be Pauli rules.
- Native classical Dual stores a float primal and first derivative vector.
  Its nonlinear operations and ParameterExpression reconstruction do not
  retain an input-map Hessian.
- TransformedExecutionPlan and processing_jacobian propagate first-order
  child/processing Jacobians only. Second order needs both child Hessians
  and the processing Hessian's cross terms, including live coefficients.
- Variance already corrects first derivatives using the mean. A second-order
  implementation also needs the mean Hessian and gradient outer product.
- Torch backward rejects graph-enabled execution. Autograd rejects boxed VJP
  inputs. JAX derivative custom-JVP and TF VJP explicitly reject higher order.
  Removing these guards without real second-order rules would fabricate zeros.
- NativeHostKernel owns safe source/configuration snapshots and real native
  quantum execution, but currently returns detached numeric Jacobians. It
  must supply verified second-order information through framework rules.
- Native MPS supports non-dense shift execution, not dense expansion or MPS
  adjoint. Reused parameterized loops, postselection and stochastic pathwise
  derivatives remain explicit unsupported contracts.

## Initial Red Contracts

Four independently authored tests are persisted before production edits:
native RY/Z Hessian, actual nested TF GradientTape, actual Torch double
backward, and transformed QWC with nonlinear sin(theta)+2*theta and a shared
gate/coefficient variable. The latter requires

E = a*sin(g), a=.9+.1*theta, g=sin(theta)+2*theta;
E'' = .2*cos(g)*g' - a*sin(g)*(g')**2 - a*cos(g)*sin(theta).

Real execution failures must be recorded, not inferred from missing APIs or
counted from skipped optional dependencies. At the initial audit/test addition,
no production code had changed. The actual persisted run was four failures,
8.36 seconds, exit 1: `/tmp/qb-stage11pc-initial-red.log` and its independent
`.exit` receipt. Subsequent implementation is described in the separate
second-order report; this section records the starting state, not current gaps.

The previous collaboration reply completed but its final body was exposed as
an unreadable content reference. A normal authorized follow-up asks for the
complete task as plain text. Until that full reply is read, no partial streamed
prompt is treated as a complete specification. The red contracts above also
follow directly from the user's full functional replacement objective.
