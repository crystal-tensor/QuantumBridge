# Stage 11L Native Transpiler Report

Status: native implementation and clean local validation passed; publication is
verified separately against the resulting commit SHA.
Date: 2026-10-19. Base `d0cca5b`; full replacement objective remains incomplete.

## Implemented

- Native DAG input/output/operation nodes, quantum/classical/variable resource
  dependencies, deterministic topological order, mutation and validation.
  Structured control boundaries are conservative synchronization fences.
  Loops expose structural, not fictitious runtime, depth. Consecutive block
  replacement is supported; noncontiguous contraction explicitly rejects.
- PassManager analysis immutability, PropertySet version/invalidation,
  prerequisites/preservation, callbacks, seed, trace, bounded repetition and
  named StagedPassManager. Existing Circuit-based pass contract is retained;
  this is not the complete upstream DAG-pass/plugin API.
- Directed CouplingMap shortest paths; Target per-instruction qargs, duration
  in seconds, error, measurement/reset/conditional/channel availability,
  alignment/granularity and feedback metadata. Missing timing data rejects.
- Validated logical/physical Layout, inverse, user/trivial/topology-degree
  initial choice and target-width ancillas. Routing reports the permutation
  relative to physical input separately from initial logical layout.
- Algebraic exact-phase translation of the tested H/X/Y/Z/S/T/SX/rotations,
  phase/U-family, CX/CZ/SWAP, controlled rotations/phase and Pauli interactions
  into rx/ry/rz/cx or rz/sx/x/cx. Unsupported routes reject without fitting.
- Real shortest-path SWAP routing, directed CX reversal, operand/measurement
  mapping and optional restoration. Default restoration occurs per interaction
  for correctness, not optimality. Forward, restoration and nested swap costs
  are separate; `inserted_swaps` retains the forward-only legacy metric.
- Existing inverse cancellation, zero/identity removal and rotation merging
  now preserve symbolic expressions. Optimization never crosses measurement,
  reset, barrier, conditional or structured lexical boundaries.
- if/for/while/switch/store/break/continue bodies recursively compile and
  reconcile layout at joins. No runtime branch is evaluated by the compiler.
- Static ASAP/ALAP scheduling with actual durations, alignment, readout/feedback
  dependencies, parallel disjoint wires, makespan, limits and optional delays.
  Full structured dynamic scheduling explicitly rejects; no hardware timing
  assertion is made. Synthetic target durations in tests are not calibrations.
- QNode.compile retains native first-order classical graphs when decomposition
  splits parameters or optimization merges them, including Torch/Autograd.
  Nonidentity/unrestored layouts and expanded-width measurement mappings reject.
- Compiled 100-qubit GHZ-chain MPS execution is tested with dense APIs disabled;
  this does not imply efficient arbitrary entanglement or optimal routing.
- Offline DeviceSpec and static backend configuration compile to native Target.
  No token reading, cloud access, hardware submission or new dependency.

## Validation

Final clean tracked-tree snapshot: `/tmp/qb-stage11l-final.D0KGog`. This excludes
unrelated user Studio/Router changes and untracked files, without reverting or
staging them. Code was unchanged between these final runs.

| Gate | Final result |
| --- | --- |
| SDK-free full pytest | 899 passed, 116 skipped |
| Installed full pytest + explicit coverage | 1090 passed, 4 skipped |
| Installed SDK/framework versions | Qiskit 2.4.1, Aer 0.17.2, PennyLane 0.44.1, Torch 2.12.0, Autograd 1.8.0 |
| Alternate full pytest | 1054 passed, 40 skipped |
| Alternate SDK/framework versions | Qiskit 2.6.0, Aer 0.17.2, PennyLane 0.42.3, Autograd 1.9.1; Torch absent |
| Native compiler scenario functions/instances | 41 / 125 |
| New public operator differential scenarios | 12 passed in both SDK environments |
| Structured compile/execute scenarios | 10 passed, including loop/store/break/continue |
| Focused compiler/public/framework tests | 155 passed |
| Existing compiler/density/stabilizer regressions | 183 passed |
| Overall line coverage | 87.5253%; baseline 87.0240%; no exclusions added |
| DAG / routing / scheduling / PassManager coverage | 99.54% / 97.30% / 96.59% / 100% |
| Target / basis translation / compiled parameter graph coverage | 97.17% / 92.39% / 100% |
| Complete local matrix | exit 0 |
| compileall / staged whitespace check | exit 0 |
| Legal and no-token/no-vendor subset | 6 passed; full suites also passed |
| Three SDK-free examples | exit 0 via python -m examples.native_transpile_* |

The four installed skips are the existing pyquafu/NumPy incompatibility, two
absent dynamics checks and one absent optimization check. Missing optional
framework/SDK tests in other environments are skips, not claimed execution.
The matrix's existing coverage detector reports unavailable; the explicit
pytest-cov run above is the coverage evidence. An initial example invocation
resolved an older editable install; module invocation from the clean snapshot
then verified the actual staged code. Initial full-run regressions were fixed
before all final clean reruns, not waived or excluded.

The old dynamic-transpilation rejection assertions were replaced by actual
before/after runtime state checks because that capability is now implemented.
Existing unsupported QASM conditional-export assertions remain. Abstract
simulation targets preserve channel support; explicit physical Targets must
opt in to channels. The old dynamic_execution_order report field is preserved.
Pass elapsed times are exposed through manager.metrics/callbacks, not stored
in deterministic compiled circuit metadata.

## Remaining Limits

Full transpiler parity remains PARTIAL: arbitrary unitary/gate synthesis,
commutation optimization, optimal routing/layout search, custom flow-controller
plugins, dynamic timing, calibrations and full upstream Target/DAG protocols
are not complete. Legacy flat conditionals requiring phase-changing translation
must be expressed as structured if bodies, otherwise explicitly rejected.
Compiler limits bound graph size, pass iterations, swaps, structural depth,
control nesting and static makespan. Dense state/operator tests stay small.

Complete Qiskit/PennyLane parity still requires serialization, additional Aer
contracts, templates/qchem/ecosystem functions, JAX/TF/capture/higher-order
autodiff, and separately authorized real Quafu validation. Studio stays last.

## Publication

Stage 11K `d0cca5b` is local and unpublished at the starting checkpoint. Previous
remote `8e47c9b`/CI 39248641174 is not evidence for this batch. Only normal
fast-forward publication is permitted; no force/rebase/reset/tag/release.
Before commit, git fetch succeeded and origin/main remained `8e47c9b`; the
left/right comparison was 0/1, preserving unpublished Stage 11K. Commit/push
and exact-new-SHA Actions results are recorded in the execution handoff after
this source report is committed; they are not inferred from local tests.

## References

- [Public transpiler model](https://quantum.cloud.ibm.com/docs/en/api/qiskit/transpiler)
- [Public DAG API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/dagcircuit)
- [Public Target API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.transpiler.Target)

Public mathematical/API behavior only. No third-party implementation, test,
package, environment, credential, tutorial prose or branding copied.
