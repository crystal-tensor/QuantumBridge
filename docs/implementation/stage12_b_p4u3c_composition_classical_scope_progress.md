# Stage 12-B P4-U3C Native Composition And Classical Scope

Status: SUPPORTED CHECKPOINT VERIFIED / PARTIAL; NOT COMPLETE U3C, U3, P4 OR FULL SDK PARITY.
Start local HEAD:44760ed86722f17b8877b03f95ce575f1714bdfc, documentation-only
follow-up of accepted runtime af66875b13593706282dac1ace0481911a2bbb27.
GLOBAL baseline31253/34235=91.28961589017088%, exclusions68.
Full independent native Qiskit/PennyLane functional parity/full replacement
stays ACTIVE / INCOMPLETE. The complete actually received U3C task is saved in
`stage12_b_p4u3c_composition_classical_scope_execution_prompt.md`.

## Real Native Changes

- Circuit.compose supports wrap, copy, var_remap and inline_captures with
  transactional mutation/None returns. Existing wire/measurement/block maps
  are reused. Quantum and classical integer, negative-index and slice forms
  match independently observed public behavior; nested/nonintegral/duplicate/
  wrong-length maps have observed CircuitError categories.
- wrap retains a real Gate or nonunitary Instruction with an executable
  definition, not a flattened surrogate. Quantum/classical mapping, exact
  complex phase, decompose levels and parameter lineage are tested.
- Circuit source copy=True isolates its operation snapshots. copy=False reuses
  an owned native operation; checked live owner views keep actual parameters,
  Circuit indexing, binding, execution and serialization synchronized. Storage
  remains alive after source deletion. Existing owned-array budgets still
  protect copies and validation workspace; borrowed existing storage is not
  claimed to be new allocated storage or a process-RSS bound.
- A distinct public contract was actually observed in both versions: direct
  Gate/Instruction composition reuses that given operation even with copy=True,
  and wrap does not add a synthetic definition. Native direct composition now
  follows it, including actual opaque Gate staging and deferred annotation.
- Immutable Var/Stretch identities, inputs/locals/captures, lookup/iterators,
  add_uninitialized_var, public initialized add_var, add_input/add_capture and
  add_stretch are native. Existing add_var(name,dtype,initial) remains an
  explicit native extension with its legacy expression syntax.
- Remapping rewrites real declarations, stores and all nested expression
  references, including nested local identifiers and captured variables.
  Inlining occurs after remapping and requires the target storage identity.
  Parameter and classical namespaces are separate. Types, names, scopes and
  missing/colliding captures are checked before committing a target.
- Scope-only circuits enter the existing dynamic executor. Four native devices
  execute capture stores, measurement-derived conditions and loop updates with
  real classical snapshots. Stretch is a duration identifier only; this does
  not add a duration/timing executor.
- Native IR preserves typed identifier records and actual execution. QPY/QASM
  cannot yet transport these scopes and explicitly reject them, even when
  metadata loss is allowed. Actual public QPY metadata cannot smuggle fake
  native variables past a zero-variable wire header.
- Existing compiler segments drop temporary inherited declarations; semantic
  outputs/layout/transforms preserve the actual scope. One shared native
  decoded-parameter interning helper restores operation/vector identities in
  QPY and IR without weakening ordinary external defensive-copy isolation.
- Managed source admission rejects foreign graph/copy/remap callbacks before
  copying. Definition/work, variable/remap counts, copy storage and measurement
  positions are admitted first. Remapping a ControlBlock avoids copying its
  whole subtree before remapping it again. Failure leaves inplace targets intact.

## Actual Development Evidence

Prefixes are `/tmp/qb-stage12b-p4u3c-*`, with distinct .log/.exit receipts.
These are development candidates, not final frozen FULL acceptance.

- initial-baseline:254passed/exit0. initial-reds:12failed/1passed/exit1 on the
  unchanged runtime; first-native:13passed/exit0 after actual implementation.
- Public-only probes independently record actual Qiskit2.4.1/2.6.0 signatures,
  wrappers, copy lifetimes, typed scope/remaps, captures, wire forms and error
  categories. No implementation source inspection or source-port counts.
- native-integration:1700passed/3xfailed/exit0.
- scope-execution-red initially9failed/28passed. Two test mistakes were then
  corrected: a missing zero-probability output was not a semantic difference,
  and Operator lives in quantumbridge.information rather than the root module.
  The earlier collection-only run also used a nonexistent generic qasm_dumps;
  actual versioned qasm2/qasm3 APIs replaced it before evaluating behaviors.
  Corrected red:10failed/27passed/exit1, including actual scope loss after JSON
  normalization, not incidental tuple-metadata rejection. Real fixes recover
  all50 initial composition/scope/format cases.
- copy-lifetime-red:3failed/7passed. Two were real stale owner index/QPY record
  defects. The matrix-storage test also initially forgot the existing66-byte
  unitary-validation workspace; its corrected budget accounts for that work
  without weakening storage admission. copy-lifetime-recovery had one unrelated
  JAX float32 tolerance failure because that command omitted JAX_ENABLE_X64;
  all subsequent framework gates explicitly enable x64, with unchanged tolerances.
- live-owner-integration:2failed/1745passed/3xfailed exposed actual QPY vector
  container and compiler segment scope regressions. vector-compiler-recovery:
  259passed/exit0 after actual runtime fixes.
- resource-red:4failed/11passed, one being a test's nonexistent root CircuitError
  import. Correcting it and repairing actual graph/invocation/measurement
  admission yields62 resource/lifetime/scope/format cases passed.
- resource-compiler-integration:1failed/2116passed/3xfailed, solely cycle-error
  precedence. The cycle guard was moved before invocation comparison, retaining
  the original regression and its diagnostic contract.
- dynamic-phase-red:4failed/20passed. Actual layout scope conflict and IR vector
  identity were repaired. Tests corrected compute_gradient/to_statevector names
  to the real compute_jacobian/MatrixProductState.statevector APIs. Recovery:
  70passed/exit0, including actual four-framework derivatives and no-dense MPS.
- Corrected public wire differential red:11failed/30passed. This follows fixing
  public fixture chaining: public measure returns InstructionSet, not Circuit;
  native Measurement has no name field. Actual production wire handling then
  recovers41passed independently in both installed versions.
- development-cov:2182passed/3xfailed/5warnings/221.21s/exit0. This is FOCUS
  coverage, not GLOBAL; its dirty-worktree denominator includes unowned Router.
  New scope/composition modules have130/139 and92/98 lines, shared parameter
  graph32/32. This does not establish whole-package coverage or parity.
- Direct-owner red:2failed/10passed; direct-annotation red:1failed/12deselected.
  Actual dual-version direct-operation observations above were migrated, not
  guessed from Circuit copy semantics. Native direct/lifetime/phase recovery:
  74passed/exit0. Empty-name actual store snapshot red was repaired too.
- pre-freeze-focus:2197passed/3xfailed/5warnings/77.43s/exit0. Current public260:
  49passed/exit0, including literal public contracts, full noncontiguous complex
  matrix and actual bilateral wrapped QPY plus external fake-sidecar rejection.
- SDK-free example exits0: Hessian8.209167119094104, mapped counts010:4,
  captured counter3 on each of4 shots, MPS100 expectation0.9210609940028851.
  No upstream SDK, AD framework, cloud or hardware is needed for that example.

## Actual Final R1 Verification

All31 sequential children and the driver terminated with exit0. The separate
final receipt/origin/coverage/matrix audit also exits0. The prefix is
`/tmp/qb-stage12b-p4u3c-r1-`; each child has a real .log and .exit receipt.
These runs use one frozen candidate, not combined old/new implementation runs.

| Gate | Actual terminal result |
| --- | --- |
| compile / controlled legal | exit0 / 4passed, exit0 |
| Circuit / serialization | 223passed / 521passed,3xfailed |
| Compiler / QML / devices | 141 / 122 / 94passed |
| H2 / Aer / MPS focus | 207passed |
| SDK-free FULL | 4646passed,1142skipped,6warnings,289.37s |
| Qiskit2.4.1 / PennyLane0.44.1 FULL | 6055passed,5skipped,7xfailed,64warnings,1595.61s |
| Qiskit2.6.0 / PennyLane0.42.3 FULL | 6053passed,5skipped,9xfailed,52warnings,546.87s |
| Independent JAX focus | 1485passed,474skipped |
| Independent TensorFlow focus | 1487passed,472skipped |
| Torch / Autograd focus | 452passed,1skipped |
| Public2.4.1 / public2.6.0 broad focus | each2004passed,3xfailed |
| SDK-free examples | all8 exit0, including native_circuit_composition |
| Original unchanged28-section matrix | SDK-free execution, all28 ordered sections reached, exit0 |
| Actual package import origins | all5 frozen-source origins verified, exit0 |

The new modules add155 collected cases in the SDK-installed FULLs, without
deleting tests or relaxing existing tolerances. Each public broad focus
includes49 actual composition differential cases. Skips/xfails are not passes
or proof of missing-dependency functionality.

Main GLOBAL is explicitly exported by its dedicated child before the local
matrix:31678/34681=91.34108013033072%, missing3003, exclusions68 unchanged.
It exceeds the actual starting31253/34235=91.28961589017088%. New module line
coverage: composition98/103; classical_scope130/139; parameter_graph32/32.
Coverage is line coverage, not a percentage of full SDK functional parity.

The actual original matrix ran in the SDK-free environment. Qiskit,
PennyLane/Aer and Finance/Optimization/ML/Nature/Algorithms/Dynamics/Metal/
Runtime/Experiments/Addons, installed chemistry adapters and OpenFermion
subsets explicitly report unavailable/not executed. pytest-cov is also
unavailable in this environment, so the matrix does not run coverage. It does
not replace the separate actual main GLOBAL above. Compatibility/offline
tests and inventory completion do not demonstrate real cloud or hardware
execution, full ecosystem support or full P4 acceptance. Inventory writes
occur only in the private frozen source, not the working repository.

Controlled legal:4passed/exit0. The separate fresh dirty-worktree legal run
is1failed/3passed/exit1 solely because unowned quantumbridge/router/core.py
is absent from the ledger. That file was already outside this batch. Its
origin or license is not guessed; it is not staged, edited or attributed here.
The controlled result is not a claim that all unrelated workspace files pass.

## Frozen Candidate And Commit Boundary

- Frozen input tree:414f34c6e19af7270e7bdcf21d960f109466342b.
- Production subtree:8586d38844b2eac94ad3c975154286f3686ac60e.
- Tests subtree:bc256a454a9c2da517720aa69eb24a9ddcc52bcd.
- Examples subtree:02bf723bec63283ec9242404390952a6fffa60db.
- Private source:/var/folders/c1/gs7_18954qx7td5_t_lnmf4c0000gn/T/qb-stage12b-p4t-foundation-_ljcck3c/source.
- Exactly29 owned paths are intended for the normal local checkpoint commit.
  Stage/commit equality will be recorded only after actual audit and commit.

No push/live remote CI/auth/token/cloud/hardware/vendor/Studio/Router edits,
tag/release or history rewrite in this batch. Remote CI for the eventual new
SHA remains NOT_VERIFIED; this local evidence cannot turn historical PR runs
green or prove actual Quafu cloud execution.

## Report-Based Interim Review

The actual partial results were sent to the owner-authorized conversation
"Claude 代码泄漏与应对",6a20d458-a76c-83ea-9b49-f8f0caedb3cf. The complete
rendered reply was read at Chrome AX663-778 with completed-answer controls.
The reviewer saw no new confirmed blocker in the supplied report, but did not
inspect uncommitted source or remote CI. It requires live-owner/binding/
serialization lifetimes, actual classical traces, scope-only dispatch,
standard-format rejection and no foreign callbacks/partial mutation. It
requires all final frozen gates, including the original matrix, before only
a scoped supported-checkpoint commit; no U4/full-parity claim is permitted.

## Remaining Full-Parity Work

- Zero-width Circuit/Instruction execution and repeat, arbitrary Circuit/Gate
  name/error/signature policies, full public bit/register objects and builders,
  and from_instructions remain substantive U3 work, not hidden by this batch.
- Typed scope QPY wire records, classical custom Instruction invocation/base
  headers and typed QASM declarations/captures remain explicitly unsupported.
  Opaque Gate staging does not establish its executable validity or full QPY.
- Stretch duration expressions/timing execution and external runtime input
  value binding are not implemented by identifier declarations alone.
- Full InstructionSet/append and remaining Circuit public ABI require continued
  audit. Direct native extensions and safe managed execution do not prove
  inspect.signature or every unsafe public mutation is identical.
- Original28-section matrix, even if completed, is not full P4 or full SDK
  acceptance. Continue remaining U3 before U4. The ultimate independent native
  Qiskit/PennyLane full functional parity/full replacement goal stays active.
