# Stage 11O-B1 Native Transform Execution

Date: 2026-10-20. Starting local HEAD:
`a161c2894d592beaaa9937344fe3857f48743943`.

This is the B1 foundation checkpoint, not completion of Stage 11O-B, full
Templates/Transforms parity or Qiskit/PennyLane replacement. The active
full-replacement goal remains incomplete. No Studio/Router development,
cloud/hardware execution, credential access, vendoring or history rewrite.

## Native Contract And Execution

- `TransformProgram` composes native `Tape -> (Tapes, processing_fn)` functions.
  It copies owned circuit/measurement structures while retaining immutable
  symbolic expressions and live scalar graph references. Custom callbacks
  receive an owned Tape, not the original input structure.
- Each child executes using the existing `ExecutionPlan`, `QNode` measurement
  logic and native Device. There is no second quantum interpreter, SDK
  passthrough or substitution of a precomputed Hamiltonian result.
- Processors receive one independently evaluated result per child, including
  that child's shot partitions. Stages reconstruct results in reverse order
  using batch slices. Nested dict/list/tuple outputs retain their structure.
- `execute_transform(..., return_metadata=True)` returns value and metadata:
  actual child plan evaluation IDs, operation counts, partition shots/seeds,
  stage widths and reverse reconstruction order. An ID denotes a real child
  plan evaluation, not a promise that a multi-measurement Device runs its
  simulator only once. Existing Device Results and measurement paths remain
  unchanged; raw values follow the existing QNode output convention.
- Native parameter bindings are supported. Source seeds deterministically
  derive child seeds separately unless a transform supplies an explicit child
  seed; request-local seeds remain explicit overrides.

## Actual Transform Subsets

`split_hamiltonian` is an internal expval-to-term-Tapes prototype, not the
complete public PennyLane `split_to_single_terms` contract. Static finite real
Hamiltonians and native Pauli observables are supported. Identity and duplicate
nonzero terms really execute; zero terms are validated before omission. A
constant-zero Hamiltonian correctly reconstructs zero without fake execution.
Variance and unsupported observables explicitly reject. Geometry-generated
Stage 11O-C H2 Hamiltonians are reused without recomputing integrals per term.

`merge_rotations` reuses the existing compiler's same-axis rotation algebra.
Repeated adjacent RX/RY/RZ/phase chains merge without coercing symbolic/live
angles to float. Mid-circuit measurement, reset, Store, directives, condition,
control blocks, simulator instructions and unknown operation metadata remain
boundaries. B1 leaves entire control bodies unchanged. Measurement positions
and circuit global phase are preserved. Unknown metadata is not discarded.

The old functional `basic_entangler_layers` now emits a migration FutureWarning
for its RX/ring behavior. The modern `templates.BasicEntanglerLayers` object
does not warn, while `hardware_efficient_ansatz` retains explicit RY/open-chain
behavior. A regression checks distinct old/new gate sequences and equality of
the explicit modern object with the functional modern behavior.

## Independent Evidence

The SDK-free example actually executes three weighted Pauli child Tapes,
prints their IDs and reconstructs `0.800396076954677`, equal to the unsplit
native expectation (absolute error zero in the recorded run). The counting
Device test independently verifies three distinct circuit/observable calls;
metadata alone is not the proof. Synthetic child values also independently
verify coefficient reconstruction, and an explicit three-stage callback test
verifies reverse, not forward, postprocessing.

New tests cover one-to-one/one-to-three/zero execution, arbitrary nested
measurement structures, identity/duplicate/zero terms, ordered wires,
invalid observables, dynamic execution, complete complex unitaries, shot
partitions/local overrides, deterministic distinct child seeds, structural
immutability, graph retention, malformed contracts and resource limits.
Native ParameterExpression reconstruction retains the derivative of
`sin(x) + 2*x`; a Torch nonleaf preprocessing expression retains its actual
classical backward graph. Neither is claimed as transformed quantum VJP.

The H2 integration actually executes 15 term Tapes and reconstructs
`-1.0616035008129299` at the tested excitation angle, equal to the unsplit
geometry-derived Hamiltonian expectation. This is not a ground-state claim
or a transformed gradient test.

## Verification

The final code was verified in a clean tracked-tree snapshot at
`/tmp/qb-stage11ob1-verified-zDXx7P`, excluding unrelated user Studio/Router
files. The new suite has 43 independently authored test functions, expanded
to 66 cases; 64 run without optional frameworks and two require Torch.

| Gate | Measured result |
| --- | --- |
| Main full tests, Python 3.12.6, Qiskit 2.4.1 / Aer 0.17.2 / PennyLane 0.44.1 / Torch 2.12.0 / Autograd 1.8.0 / PySCF 2.13.1 | 1577 passed, 4 skipped |
| SDK-free full tests; Qiskit/PennyLane/PySCF/Torch/Autograd absent | 1295 passed, 126 skipped |
| Alternate full tests, Qiskit 2.6.0 / Aer 0.17.2 / PennyLane 0.42.3 / Autograd 1.9.1, no Torch/PySCF | 1534 passed, 47 skipped |
| Package coverage | 21020 / 23684 statements, 88.75190001688904%; 68 unchanged exclusions |
| New program module coverage | 218 / 222 statements, 98.1981981981982% |
| Circuit / measurement transform module coverage | 96.66666666666667% / 96.72131147540983% |
| Full local matrix on final code | Exit 0, including the restored embedded package coverage step; unavailable optional extras explicitly skipped |
| compileall, quantumbridge/examples/scripts | Exit 0 |
| Focused attribution, ledger, no-vendor/no-token checks | 8 passed |
| SDK-free new example | Exit 0; three real child evaluations, reconstruction error zero |
| Both isolated environment pip checks | No broken requirements |

Package coverage increased from the Stage 11O-A baseline
88.59506257500429%; no exclusion was added. Existing 11H-11O-C native and
optional public regressions remain in these full runs. New transform tests
are native mathematical/runtime tests, not a claim of public TransformProgram
or splitting differential parity.

The normal Circuit phase setter already rejects framework tensors. Additional
B1 guards cover custom callbacks directly writing phase metadata and live
framework parameter bindings, without weakening that setter. A narrow
submodule coverage invocation encountered the existing NumPy instrumentation
reentry error; the canonical package-wide `--cov=quantumbridge` run passed.
No environment or dependency was changed. Pre-existing global pip conflicts
remain: WeasyPrint 68.1 needs tinycss2 >=1.5 (installed 1.4); pyquafu 0.4.5
needs NumPy <2 (installed 2.4.6). These are not newly introduced regressions.

The first successful matrix run misleadingly printed `pytest-cov unavailable`
despite the separately passing coverage command. Its existing `grep -q` help
probe closed the pipe early under pipefail: the old probe returned 1 while
the full-consuming probe returned 0 against the same installed pytest.
The script now consumes all help output; the complete matrix rerun exited 0
and its embedded coverage step really executed. This does not add an
exclusion, disable a test or change optional dependencies.

Generated verification logs are `/tmp/qb-stage11ob1-main.log`,
`/tmp/qb-stage11ob1-sdkfree.log`, `/tmp/qb-stage11ob1-alternate.log`,
`/tmp/qb-stage11ob1-matrix.log`, with package coverage JSON at
`/tmp/qb-stage11ob1-full-coverage.json`.

## Limits And Explicit Gaps

Default bounds: 32 transforms, 128 child Tapes, 100000 instructions per Tape,
500000 instructions per batch, 200000 cumulative expansion instructions/Tapes,
64 structural/control nesting levels, 100000 postprocessing nodes/elements and
1000000 total sampled shots. Children, nested control bodies, cumulative work
and shot budgets are checked before the execution batch. Results and each
reconstruction level are also checked. User Python callbacks are trusted code,
not a sandbox: an arbitrary callback can allocate before returning its output.

Shot vectors are preserved per child, not interpreted as a shared total-shot
budget. B1 rejects changed shot specifications across a transform boundary.
This is not QWC grouping or shot allocation. Identity sampling may need no
physical random draws, even though its child plan genuinely evaluates.

QNode/callable transform dispatch, public splitting parity, QWC/total-shot
allocation, cancel/decompose/compile Tape transforms, transformed native
Jacobian/VJP/Torch/Autograd, defer_measurements and the complete 100-wire
template-plus-transform derivative integration remain required in B2-B6.
The B1 raw executor explicitly rejects live framework/Dual inputs and bindings
instead of silently detaching or pretending to supply transformed autodiff.

## Publication

Commits 11M, 11N, 11O-C and 11O-A are preserved. No force/reset/rebase/amend,
tag or release. This batch does not retry/bypass existing remote/workflow OAuth
authorization problems. No new push or exact-SHA Actions success is claimed;
stale `origin/main` tracking is not evidence of current remote state.
