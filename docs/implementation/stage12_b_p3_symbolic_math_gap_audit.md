# Stage 12-B P3 Symbolic Mathematics Gap Audit

Starting HEAD: 0ef945242b0950b30e4fdf5e4e32f028e2033f75, local main.
Cached origin/main: 45fe338fc0f02de9c19e0af89723755952e5fc98;
cached comparison 0 behind / 35 ahead is not live remote evidence. No push.
Pre-existing Studio/Router changes are protected and outside this work.

## Observed Starting Implementation

- `core/parameters.py` executes real arithmetic `+ - * / **` and unary negation.
  No symbolic elementary functions, symbolic gradient, assign, subs, numeric,
  is_real, is_symbol or optional sympify entry points exist.
- Binding recurses over arithmetic AST, preserves native UUID and vector
  identities, and already performs simultaneous numeric/symbolic substitution
  through Circuit. Do not manufacture a failure in that correct path.
- Parameters are real-only at coercion/binding; complex arithmetic is not a
  supported scalar expression contract at this starting snapshot.
- ParameterExpression has no resource preflight. Existing serialization bounds
  provide per-format node/depth constraints, not construction/calculus bounds.
- The classical Dual/SecondDual graph already implements sin/cos/tan/exp/log,
  power, sqrt and piecewise abs, but is not a symbolic AST differentiation engine.
- `diff/compiled_parameters.py` reconstructs arithmetic only. New symbolic
  nodes must dispatch through the existing trace/interface numeric operations.
- IR accepts only arithmetic nodes. QPY v13 replay implements arithmetic only.
  Text exporter rejects function nodes; text lowering has numeric math calls.
  These must be changed or explicitly rejected, never silently serialized away.
- P2 identity, vector, phase, binding, resource and numerical regression tests
  must continue to run. The full core goal remains ACTIVE / INCOMPLETE.

## Starting Evidence Collection

The first two persisted red families exercise missing sin/exp calculus and
the missing public simultaneous `subs` entry. Public calls and signatures are
recorded separately against installed Qiskit 2.4.1 and 2.6.0 without inspecting
upstream source/tests. Primary public references are the IBM
[ParameterExpression API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.ParameterExpression)
and [QPY protocol](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qpy).

No claim of P3 acceptance, complete ParameterExpression parity, remote CI,
real hardware execution, or complete SDK replacement is made by this audit.

## Implemented After The Persisted Reds

The initial native run has six genuine failures (three sin/exp, three subs),
exit 1 at `/tmp/qb-stage12b-p3-red-initial-v2`. Initial gate-launch attempts
passed an extra directory argument to the old runner and did not run tests;
they are not counted as functional reds. The corrected public probes each
finished exit 0, with raw literal results retained in the contracts artifact.

Eleven elementary families now have native AST execution, complex principal
scalar arithmetic where explicitly supported, real nonsmooth domain guards,
native symbolic gradient and repeated/mixed gradient. Simultaneous replacement
uses original references only. Zero multiplication/cancellation retain tracked
membership; numeric(strict=False) can prove the supported mathematical zeros.
Construction, numeric powers, substitution, differentiation, nested work
scopes and serialization use bounds, not a claim of Python allocator/RSS limits.

The compiled parameter evaluator now dispatches function nodes into existing
native Dual/SecondDual and optional framework operations. IR and QPY preserve
native identities. The QPY v13 published unary opcode subset is implemented
independently and tested bilaterally, without upstream source lookup or ports.
QASM3 supports the representable elementary subset through its actual parser.
Sign/conjugate and guarded derivative source export remain explicitly rejected.

Public differences: full bind's scalar return, constant gradient's native
expression return, string key/native allow_partial extensions, error classes,
and sign differentiation. Both public versions lack a sqrt method. Their abs
zero derivative errors; neither sign gradient executes. Native never calls
these engines for its core arithmetic/calculus. Optional sympify is outward
only and is not identity-preserving or a production differentiation backend.

Focused numerical proof now includes complete complex matrices, partial and
formal mapped Instruction binding, inverse/power, coherently controlled bound
phase, density/state evolution, native compiled circuits, exact analytic
Jacobian/Hessian/HVP and actual four-framework first/second graphs. This is
not complete Circuit/Gate/ParameterExpression/SDK parity. Final immutable-tree
FULL/matrix acceptance is tracked separately and not inferred from focuses.
That final acceptance now passes on runtime tree d2204131: SDK-free/main/
alternate FULL 3875/4752/4750 passed, original 28-section matrix exit 0,
90.7832% global line coverage with unchanged exclusions, and actual public
probes retaining 110 outcomes per version. Details and remaining limits are
in the accompanying native symbolic mathematics report.

Later adversarial execution found real issues missed by the first scalar and
smooth-only focuses: Torch abs/sign zero derivatives silently returned zero,
TF graph gradient-override guards did not survive nested tapes, and NumPy
integer bindings could wrap 64-bit powers. Persisted negative tests retain
these failures. Dedicated native/interface fixes and positive/domain graph
recoveries precede a new immutable final tree; earlier FULL results are not
reused as acceptance for the repaired source.
