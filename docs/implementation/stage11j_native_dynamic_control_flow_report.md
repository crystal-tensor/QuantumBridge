# Stage 11J Native Classical Expressions And Dynamic Control Flow

Date: 2026-10-19

## Baseline And Scope

Base main/origin/main: e0e187c92604801d4717a139ff15a158eae926f3. Stage 11H
0780285 and Stage 11I e0e187c are preserved, published ancestors. Baseline
Actions run 39244255421 passed 22 jobs; this is NOT new-commit CI evidence.
Unrelated user Studio/Router work is not modified, staged or reverted.

This implements real native classical execution/control flow, not an AST-only
adapter. All quantum state updates use QuantumBridge vector, density, MPS or
tableau representations. No upstream SDK participates in native execution.
Full Qiskit/PennyLane replacement remains incomplete and active.

## Public APIs And Semantics

| Surface | Callable native API |
| --- | --- |
| Types/expressions | core.classical.Bool, Bit, UInt, literal, variable, bit, register, cast, logical_not/and/or, binary, ClassicalExpression |
| Expression operations | Runtime ==/!=/ordering, bitwise operations/inversion, UInt add/sub/mul/shifts; symbolic Python truth raises instead of silently becoming constant |
| Storage | ClassicalStore, classical_eval, classical_assign, declared/uninitialized variable checks, snapshot to_dict/from_dict |
| Expression serialization | serialize_classical_expr / deserialize_classical_expr; executable typed trees, no eval/exec |
| Circuit control | add_var, store, if_test/if_else, for_loop, while_loop, switch, break_loop, continue_loop |
| IR | ControlBlock to_dict/from_dict/to_json/from_json/validate; IRProgram JSON/validation with executable parameter ASTs |
| Budgets | ExecutionLimits(max_loop_iterations, max_instruction_executions, max_control_depth, max_branches, max_shots) |
| QML | Tape.measure(reset=...), Tape.cond(runtime_expr, true_callback, false_callback), Tape.reset |

UInt arithmetic wraps modulo 2**width; raw out-of-range assignment is rejected
unless explicitly cast. Bool and integers are not implicitly conflated. The
first bit listed in a register is its least-significant bit; output memory is
c0-first and native quantum outputs remain q0-first. UInt width is bounded to
4096 bits to limit classical integer resources. Expressions are immutable and
all variable reads require declared, initialized storage.

Structured branches evaluate their condition at entry. While reevaluates after
each iteration. Switch has no fallthrough. For values bind a loop Parameter
and/or UInt variable; outer loop-variable state is restored afterwards. Nested
body declarations are local and recreated on each entry. Captured assignments
persist. Each shot starts with independent classical storage and a fresh state.
break exits only the innermost loop; continue skips its remaining body.

The old flattened if/else execution remains intact for existing circuits.
Structured circuits use the shared runtime interpreter with actual branching;
they are not statically expanded into an assumed equivalent unitary.

## Backend Support

| Backend | Analytic dynamic behavior | Finite shots | Explicit limits/differences |
| --- | --- | --- | --- |
| Statevector | Weighted native pure branches; expectations/probabilities and nonselective density output | Native collapse/reset/CPTP/feedback/loops, independent records | statevector() still rejects ambiguous nonunitary circuits; dense output is memory-guarded |
| DensityMatrix | Mixed initial states, selective branch feedback, CPTP maps, final and reduced density | Same runtime semantics with stochastic measurement/readout | Dense storage and branch budgets remain exponential |
| MPS | Weighted pure MPS ensembles with Pauli expectations and existing reductions | Native tensor trajectories, reset/readout/feedback/loops | No dense fallback; bond/cutoff/Schmidt statistics retained, branches capped |
| Tableau | Supported Clifford gates, measurements/reset and Clifford-mixture channels | Native tableau trajectories | Non-Clifford gates/arbitrary selective Kraus are UnsupportedFeature, not substituted |
| QNode | Native measure/cond/reset followed by expectation/probability/density/sampling | Existing sampled measurement interface uses native trajectories | Native Tape API, not complete PennyLane capture/Catalyst/autodiff/shot-vector parity |

Backend/Job/V2 sampling retains bitstrings, records, seeds and execution metadata.
Estimator uses analytic branch expectations where implemented, including noisy
X/Y without noiseless substitution. MPS systematic truncation statistics remain
separate from zero analytic sampling standard deviation. Result JSON preserves
classical ensemble or requested shot-memory snapshots. No pure MPS is falsely
used to represent a mixed ensemble.

## Verification And Evidence

tests/circuit/test_classical_expressions_native.py contains eight independent
classical semantics scenarios. tests/circuit/test_control_flow_native.py
contains 44 distinct dynamic scenarios (not parameter-grid duplicates), with
cross-backend checks where supported. They cover true/false/nested branches,
bit/register conditions, overwrites, empty/odd/even/nested for loops, parameter
binding, loop-variable restoration, runtime while termination, break/continue,
switch/default/no fallthrough, lexical state, uninitialized reads, Bell
feedforward, mixed conditional channels, JSON/mapping/instructions, Job/PUB,
QNode, budgets, readout, MPS, resource errors and explicit rejection paths.

The 100-qubit MPS test builds GHZ, measures q0, conditionally corrects q99 and
reads it. Full statevector/density simulation and MPS expansion are replaced by
test failures. Seeded finite shots still complete with peak bond two and
classical records in {00,10}. This proves the tested non-dense path, not
efficient simulation for arbitrary entanglement or actual quantum hardware.

Six optional public-API differential tests cover Qiskit/Aer for-loop parameter
binding, runtime while feedback, switch statistics and Boolean XOR feedback,
plus PennyLane measure/cond and measurement reset. Pure density comparisons use
1e-10 where deterministic; sampled branch comparisons use explicit statistical
tolerances. PennyLane's deferred-measurement oracle uses one ancillary wire;
only the two logical wires' observables/probabilities are compared. No upstream
source or test code was read/copied.

Validation used a clean tracked archive plus the exact staged patch, excluding
unrelated untracked user files. All commands below exited zero:

| Check | Final measured result |
| --- | --- |
| SDK-free full pytest -q -rs | 747 passed, 93 skipped |
| Installed full pytest with explicit pytest-cov | 904 passed, 4 skipped |
| Installed versions | Qiskit 2.4.1, Aer 0.17.2, PennyLane 0.44.1 |
| Alternate full pytest -q -rs | 873 passed, 35 skipped |
| Alternate versions | Qiskit 2.6.0, Aer 0.17.2, PennyLane 0.42.3 |
| Alternate focused circuit/device/information/primitives/QML/noise/differential tests | 266 passed |
| Required circuit/device/primitives/QML paths | 194 passed |
| Overall explicit line coverage | 86.6755%, above baseline 86.18%; no exclusions added |
| Classical expression evaluator module | 95.45% |
| Structured control-flow module | 90.42% |
| Shared dynamic execution engine | 99.00% |
| bash scripts/run_local_matrix.sh | exit 0 |
| python3 -m compileall -q quantumbridge | exit 0 |
| Three native examples in SDK-free environment | exit 0 each |
| Staged whitespace, dependency and privacy/vendor path/content scans | passed; no new project dependency or secret/package payload |

The installed run's four skips are the incompatible pyquafu/NumPy environment,
two unavailable qiskit-dynamics checks and an unavailable qiskit-optimization
check. SDK-free and alternate skips are optional packages/interfaces absent in
those environments, not native dynamic failures. The local matrix's existing
optional coverage detector reported unavailable; the separately executed
explicit pytest-cov command above is the coverage evidence, not that detector.
All six new upstream differential cases passed in both installed SDK versions.
Existing legal and no-token/no-vendor tests passed in the clean full runs.

Full regression found and fixed a ShotSampler dispatch regression introduced
by the new vector run_shots method. Explicit Sampler noise now executes through
the native noise-capable device rather than being rejected or silently ignored.
Three additional regression tests prove quantum noise, readout noise, requested
memory and preservation of vector resource limits during noise configuration.
Analytic vector branch ensembles also enforce aggregate memory limits; the
matching finite-shot trajectory remains usable under the same budget.

Publication follows normal direct-push main authorization, without history
rewrites. New-commit Actions evidence must be checked against its exact SHA;
the baseline run above is not used as evidence for the new implementation.

## Limits And Remaining Differences

Default budgets: 1000 loop iterations per loop, 100000 executed instructions
per trajectory/analytic branch, control depth 32, 4096 analytic branches (or
the native device's configured branch budget), 1000000 shots. Explicit positive
ExecutionLimits can override these. Construction caps finite loop-value sets
at one million items, including bounded consumption of supplied iterables.
Expression depth is bounded at 64. These limits reject excess execution;
they do not silently drop iterations, branches, expressions or instructions.

This does not implement every Qiskit/PennyLane classical type or API signature:
floating/duration/stretch expressions, full builders/capture/plugin protocols,
all lvalue/index/parameter types and all resource-accounting interfaces remain
open. Structured native IR roundtrips are implemented; complete QASM2/3/QPY
and Qiskit structured import/export are not claimed. Dynamic transpilation,
routing/scheduling and a static dynamic-depth claim are explicitly rejected,
pending the dedicated compiler work, rather than miscompiling/dropping nodes.
Full core requirements remain in docs/compat/core_parity_ledger.md.

No new cloud/token/hardware task, release, tag or vendor upload is performed.
The new-commit push/CI outcome must be verified by its own SHA after testing.
Next priority is native QNode/autodiff, followed by compiler and serialization
coverage. Studio remains deferred. Stage 11J increases independent executable
semantics; it does not establish overall full functional parity.

## References

- [Public Qiskit classical API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/circuit_classical)
- [Public PennyLane conditional execution API](https://docs.pennylane.ai/en/stable/code/api/pennylane.cond.html)

References describe public behavior only; the implementation and tests are
independent QuantumBridge work.
