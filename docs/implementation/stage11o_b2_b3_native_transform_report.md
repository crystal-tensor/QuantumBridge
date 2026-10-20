# Stage 11O-B2/B3 QNode And Basic Native Transforms

Date: 2026-10-20. Starting local commit:
`7e00be78452cc15ba41bea74d6397113739be380`.

The full Qiskit/PennyLane replacement objective remains active and incomplete.
This checkpoint delivers actual QNode dispatch and the supported basic native
transform contracts, not whole Stage 11O-B or complete public SDK parity.
No Studio/Router development, token/cloud/hardware access, vendoring, release,
tag or history rewriting. Prior 11M/11N/11O-C/11O-A/11O-B1 commits are preserved.

## Fresh Native QNode Dispatch

`merge_rotations(node)`, other registered native transforms,
`node.with_transform(program)` and `program.execute_qnode(node, *args, **kwargs)`
reuse the existing QNode. A native callable is supported with explicit
`qnode_options={"num_qubits": ..., ...}`; implicit SDK-style global queuing is
not claimed. Tape dispatch returns `(Tapes, processing_fn)`. Structural
transforms accept unmeasured Tapes without adding fake terminal measurements;
raw numerical execution still requires terminal measurements or an explicit
output tree.

Each QNode call constructs a fresh source Tape using current positional and
keyword arguments. The existing AngleRecorder and compiled-parameter
reconstruction preserve symbolic/shared/nonlinear input expressions. Native
child ExecutionPlans and reverse result processing are shared with the B1 raw
executor, not replaced by a second quantum interpreter. The batch plan keeps
child parameter slices, source recorder, postprocessor dependencies and
parent-to-child spans for the later native VJP integration.

The first red test failed with missing `execute_qnode`; it now proves two
actual calls at theta .2 and .7 produce respectively `0.7777349304367746` and
`-0.1533922732199`, matching `0.7*cos(3*theta)+0.2` and each original QNode.
CountingDevice records six independently executed child circuits with gate
angles .6/.6/.6 and 2.1/2.1/2.1 and disjoint evaluation IDs. The original node
is not mutated. Further tests vary batch width between calls, keep an old
prepared plan usable, and verify nested/keyword/shot/seed behavior.

Transform copies own their structures and do not keep the source builder's
mutable recorder as an emitter. A callback appending a constant rotation
must not append a new angle into the original recorder. Live scalar graph
references and native parameter ASTs themselves are retained, not detached.

## Real Basic Transforms

| Transform | Actual supported computation | Explicit boundary |
| --- | --- | --- |
| merge_rotations | Existing same-axis native algebra within safe segments, repeated chains, preserved expressions | Runtime/control/metadata boundaries; not the entire public commuting optimizer |
| cancel_inverses | Stack-based adjacent fixed dagger/self-inverse and proved native symbolic opposite rotations | Never crosses measurement/reset/barrier/Store/conditions/control/unknown metadata; does not guess framework expression equality |
| decompose | Registered native Circuit/Instruction/Template definitions, native algebraic compound/controlled gates, wire/parameter/global-phase reconstruction | Fresh custom names, native sorted formal parameter order, unitary bit-free custom definitions; unsupported definitions reject |
| compile | Existing 11L target/layout/routing/basis/optimization/scheduling pipeline; actual compiled Tape execution | Equal width, identity initial layout and restored final layout required for unchanged measurements; unproved remapping/ancilla growth rejects |
| split_to_single_terms | One Tape with unique native Pauli measurements, identity offsets, retained zero terms, duplicate coefficients, nested and shot partition reconstruction | Not QWC/joint sampling or total-shot allocation; static finite real coefficients; non-expval sums reject |

Custom definitions with opaque matrix metadata require a bounded complete
complex matrix equality proof, including phase, not probability equivalence.
The proof also checks unitarity with `rtol=0, atol=1e-12`; a new counterexample
at a 1e-7 amplitude error exposed the general Operator helper's looser default
relative tolerance, which is not used for this proof.
Self/mutual recursion, incorrect dimensions/parameter counts, dynamic custom
definitions and unknown side effects reject. Native standard-gate semantics
cannot be overridden with a contradictory custom definition.

Decomposition has output/work/depth budgets checked during expansion, before
oversized results reach the executor. The existing compiler now shares these
budgets across lexical control bodies; they do not reset for each body.
The native compiler's configured node budget is passed to its decomposition
passes. Transform-level resource limits remain in force independently.

The internal `split_hamiltonian` retains its separate B1 per-term-Tapes
behavior. Public-contract `split_to_single_terms` is a distinct real algorithm:
it does not merely rename that prototype. Constant identity-only input returns
one child with no measurements, as in the pinned public APIs. Its plan can
evaluate without a Device measurement; metadata is not a claim of physical
random draws or a fabricated simulator call.

## Mathematical And Public Evidence

Native tests compare complete matrices, control/wire order, global phase,
dynamic execution, ordered measurement positions and reconstructed values.
The Stage 11O-C geometry-generated H2 Hamiltonian is constructed once, then
used with real native excitation/template and transform/compile workflows.
At excitation angles .1/.3, the SDK-free example gives energies
`-1.094678786310578` / `-1.0279252771621032`; errors against unsplit native
execution are `6.66e-15` / `7.33e-15`. These are not ground-state or transformed
gradient claims; no fixed Hamiltonian lookup or per-angle SCF recomputation.

Sixteen independently authored public black-box tests cover measurement
splitting/deduplication/constant/zero/variance/shots, repeated QNode calls,
inverse cancellation, matrix decomposition/compile/merge/custom global phase
and generated-H2 integration. Upstream implementation/test files were not
opened/copied or imported as private helpers; production never calls the SDK.

The pinned public SDK drops generated GlobalPhase operations when excluded
from its requested target basis, and RY does not expand into an arbitrary
RX/RZ basis there. Public matrix oracles therefore explicitly include RY and
GlobalPhase, and independently prove their own input/output complex matrix
equality before comparison with native output. No phase alignment, probability
substitution or loosened matrix tolerance is used to conceal discrepancies.
The native implementation also passes independent RX/RZ/CX-only matrix tests.

## Verification

Final production code is verified from the clean tracked-tree snapshot
`/tmp/qb-stage11ob23-final-THOdsv`, excluding unrelated user Studio/Router
changes. This batch adds 41 independently authored native test functions
(94 cases) and 16 public differential functions. The measured focused run
including the existing 66 B1 cases is 176 passed.

| Gate | Measured result |
| --- | --- |
| Full main, Python 3.12.6, Qiskit 2.4.1 / Aer 0.17.2 / PennyLane 0.44.1 / Torch 2.12.0 / Autograd 1.8.0 / PySCF 2.13.1 | 1687 passed, 4 skipped |
| Full SDK-free, without Qiskit/PennyLane/Torch/Autograd/PySCF | 1387 passed, 129 skipped |
| Full alternate, Qiskit 2.6.0 / Aer 0.17.2 / PennyLane 0.42.3 / Autograd 1.9.1, no Torch/PySCF | 1643 passed, 48 skipped |
| Package line coverage | 21415 / 24082 statements, 88.92533842704094%; 68 unchanged excluded lines |
| New dispatcher / gate transform coverage | 100% / 97.79411764705883% |
| Shared batch program / measurement transforms | 97.82608695652173% / 97.2027972027972% |
| Native cancellation/merge / shared compiler decomposition | 97.40259740259741% / 94.78260869565217% |
| Full local matrix, including embedded coverage | Exit 0; embedded full coverage run also reports 1687 passed / 4 skipped |
| compileall, quantumbridge/examples/scripts | Exit 0 |
| Focused legal/ledger/no-vendor/no-token | 8 passed |
| Three new examples in SDK-free environment | Exit 0, with numerical assertions and real evaluation IDs |
| Isolated environment pip checks | Both clean |

Coverage increased from B1's 88.75190001688904%, without new exclusions or
weakened numerical tolerances. Full suites retain 11H-11O-A simulator,
dynamic/control, serialization, compiler, ordinary gradient/framework,
template and molecular chemistry regressions. Public differential cases
passed on both pinned PennyLane versions within their full suites.

An additional direct runtime probe routed a three-wire nonlocal CNOT with
`restore_layout=False`: the actual nonidentity final layout raised
`UnsupportedFeature` rather than silently measuring the wrong physical wires.
The persistent tests also cover nonidentity initial maps and ancilla growth.

Pre-existing global dependency conflicts remain unchanged: WeasyPrint 68.1
needs tinycss2 >=1.5 (installed 1.4), and pyquafu 0.4.5 needs NumPy <2
(installed 2.4.6). No environment or package was changed. Optional unavailable
dependencies are explicit skips, not evidence of full ecosystem coverage.
Logs: `/tmp/qb-stage11ob23-main.log`, `/tmp/qb-stage11ob23-sdkfree.log`,
`/tmp/qb-stage11ob23-alternate.log`, `/tmp/qb-stage11ob23-matrix.log` and
coverage JSON `/tmp/qb-stage11ob23-full-coverage.json`.

## Remaining Work

Transformed native Jacobian/VJP and framework backward integration remain
unimplemented: batch plans explicitly reject derivative calls and live
framework/Dual bindings before conversion. Ordinary untransformed QNode
gradient evidence is not reused as proof. JAX/TensorFlow remain unsupported;
module-prefix guards are not end-to-end framework verification.

Still required: true QWC joint sampling and shot allocation (B4), native
postprocessing/quantum VJP with Torch/Autograd and 100-qubit MPS/template plus
transform derivatives (B5), a proved deferred-measurement subset and full
integration (B6). Also open are the full public transform/pipeline/operation
catalogue, general layouts/ancillas/observables, trainable Hamiltonian
coefficients, capture/broadcasting and complete interface/device parity.

The user-authorized direct-main policy is retained, but existing workflow
OAuth/network publication limits are not bypassed or repeatedly retried.
Remote tracking is stale; no push or exact-new-SHA Actions success is claimed.
