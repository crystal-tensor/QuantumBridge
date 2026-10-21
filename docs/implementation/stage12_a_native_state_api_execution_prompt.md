# Stage 12-A P0 Execution Contract

Date: 2026-10-21. Native code baseline:
`b1d345b3731276f5f2721cb42c2397d98981ac5c`.
C3 remains PARTIAL. Full independent Qiskit/PennyLane replacement remains
ACTIVE / INCOMPLETE. The designated ChatGPT conversation's completed reply
accepted the report-based finite C3 review, not an independent source audit.
Review/status documents created after b1d345b are not part of that checkpoint.

## Scope And Compatibility Decision

P0 implements actual Statevector/DensityMatrix mixed-radix subsystem dimensions,
their numerical propagation and necessary public compatibility contracts. Do not
develop the later RNG/arithmetic/purity batches early. No Capture or Studio.

Preserve existing native q0-first ordering, dictionary probabilities and
DensityMatrix.dim shape tuples. Public compatibility entry points explicitly
translate verified wire/qargs conventions, containers, dimensions and errors.
Prefer existing compatibility entry points and mode mechanisms. If insufficient,
propose and exercise a minimal boundary, not a second state simulator or an
upstream-only facade. Shared native state/density mathematics does the work.
Do not label unchanged native contracts as full Qiskit compatibility.

Explicit dimensions such as (2,4) must remain distinguishable from (2,2,2).
A (3,2) state is not three qubits. Total Hilbert dimension equals the product
of subsystem dimensions; ordering and qubit/qudit identity remain traceable.
Preserve existing legal zero-qubit behavior; distinguish public from_int empty-
dimension quirks from other constructors instead of guessing a universal rule.

## Required Sequence

1. Inspect current native signatures and use installed public Qiskit 2.4.1 and
   2.6 APIs as black-box references only. No upstream implementation/test source
   reads, copies or ports. Build a versioned contract matrix for from_int,
   dims/dim/num_qubits, tensor/expand/evolve, probability qargs, measurement,
   actual public partial_trace entry points and legal/illegal/empty dimensions.
   Include (2,4), (3,2), (2,3,2), one qudit and zero-subsystem boundaries.
2. Record genuine pre-fix native failures: explicit dimensions flattened or
   lost, nonbinary dimensions rejected, and actual invalid-input contract gaps.
   Preserve logs, independent exits, exact call entry and public reference.
3. Reuse existing numeric arrays, Statevector/DensityMatrix objects, ResourceScope
   and ownership helpers. Fix the actual subsystem representation/invariant, not
   only external metadata or a fabricated qubit interpretation.
4. Add genuine propagation failures across state/density conversion, copy,
   tensor/expand/evolve, measure/reset/probabilities/sample, subsystem mapping
   and partial_trace. Include a case with correct amplitudes but incorrect dims.
   Verify both numerical data and dimensions after correction.
5. Keep explicit restrictions for operations not yet extended beyond qubits;
   never silently apply binary logic or call Unsupported a completed feature.
   Do not duplicate already-correct tensor/expand/evolve implementations.
6. Maintain separate native-contract and compatibility-contract tests. A public
   container/wire/error conversion cannot replace genuine native mathematics.
7. Verify mixed-radix basis indexing/order, Bell/qudit products, density trace/
   Hermiticity/PSD, tensor order, reduced density, normalization and collapse,
   using independent mathematics and optional public differentials. Execute
   from_int -> tensor -> DensityMatrix -> partial_trace -> probabilities.
8. Admit directly introduced ndarray buffers before allocation and preserve real
   result/view lifetimes. Fix actual resource errors within this batch, not an
   unbounded whole-allocator audit. Retain state/Tableau/100-qubit MPS/HVP/
   four-framework/QASM/QPY/Aer noise-save-set/H2/Result regressions.
9. After focused SDK-free/main/alternate and public differential gates, freeze
   P0 source and run fresh three-environment FULL, independent JAX/TF,
   Torch/Autograd, explicit full coverage, actual 28-section matrix, compile/
   legal/privacy/no-token/no-vendor. R2 passes cannot accept new P0 source.
   Current exact coverage baseline is 90.35145452152166%, exclusions 68.
10. Stage only P0-owned paths and commit normally after required gates; preserve
    user Studio/Router dirt. No push without restored workflow authorization and
    fresh fast-forward proof; no credentials/OAuth/TLS changes, token reads,
    cloud/hardware, tags/releases, vendor or history rewriting.

## Required Delivery

Report the two-version public behavior matrix, actual native gaps, dimension
invariants, public/native compatibility boundary, real red/fix/math/differential
evidence, composed workflow, fresh test tree/full gates/coverage/matrix exit,
actual local SHA and truthful remote status. Then return to the designated
conversation and ask for the next bounded function batch. Later RNG/arithmetic/
purity gaps remain open. A facade, metadata-only patch or green test count is
not the highest full replacement objective.

The first read-only contract survey is recorded in
[the P0 contract matrix](../compat/stage12_a_state_api_contract_matrix.md).
P0 native implementation is not claimed by that survey.

## Completed Follow-Up: P0.1 Construction And Core Propagation

After the corrected two-version survey and documentation checkpoint d22e88f
were reported, the designated conversation's completed reply was fully read.
It requires direct native implementation next, not repeated public surveys.
The separately failed dirty-workspace Router legal check must remain disclosed;
do not remove or modify the user's Router to manufacture a green result.

- Establish actual dimensions invariants in existing state/density objects and
  ResourceScope: product equals array dimension, ordered subsystems retained,
  mixed radix is not inferred to be qubits merely from power-of-two total size.
  Handle (1,), a single qudit and empty cases per verified entry-point contract.
- Save genuine native construction reds for Statevector.from_int(5,(2,4)),
  from_int(4,(3,2)), from_int(7,(2,3,2)), state-to-density conversion, (6,),
  (1,), invalid dimensions and out-of-range indices. Do not rewrite correct old
  tests merely to obtain failures. Record mathematical/public expectations.
- Implement basis amplitudes/density and dimension-preserving copies/conversion
  using existing native numeric arrays and admitted allocations. No upstream
  quantum engine, source/test port, second state simulator or metadata-only fix.
- Then save and fix propagation reds in existing copy/tensor/expand, full-system
  operators that preserve subsystem structure, state-to-density, probabilities,
  measure/reset and supported partial_trace entry points. Replace binary index
  assumptions with true mixed-radix mathematics, or explicitly reject a still
  unsupported subpath rather than return silently misinterpreted results.
- Preserve native q0-first, dict probabilities, density shape-tuple dim and old
  valid binary callers. Maintain separate native/public contract tests; reuse
  existing compatibility entry points where sufficient. Do not add a large
  facade or count boundary conversion as the native mathematical implementation.
- Execute from_int -> tensor -> DensityMatrix -> partial_trace -> probabilities
  for both (2,4) and (3,2), checking amplitudes, trace, dimensions, reduced
  density, normalized probabilities and qargs ordering against independent
  mathematics and optional public oracles. Include correct numbers/wrong dims
  as a real pre-fix failure.
- Run construction/propagation focuses and state/density/Clifford/Result/MPS/
  Device regressions, then freeze source and report actual native APIs,
  unsupported mixed-radix paths, compatibility differences, math/differentials,
  source equality and remaining gates. Before a code commit, run the previously
  agreed fresh FULL/framework/coverage/28-section/compliance gates on P0 source;
  do not reuse R2 receipts. Only stage P0-owned files, no push or history rewrite.
- P0.1 must deliver actual construction and core dimension propagation. Defer
  RNG/arithmetic/purity/full observables/general-channel expansion, Router,
  global allocator audits, Capture and Studio. Decide P0.2 from actual remaining
  failures. Full functional replacement remains ACTIVE / INCOMPLETE.

## Completed Follow-Up: P0.1 Frozen-Tree Gates And Bounded Acceptance

The completed reply in the designated conversation was fully read after the
native implementation and SDK-free FULL result were reported. The feedback is
based on this execution report, not an independent external source audit.
Its execution requirements are preserved here in English:

1. Keep production/tests/examples frozen at tree
   7aeb821e37b374ce0c3676d6d49236828155dccc (HEAD d22e88f). Wait for the
   already-running main FULL coverage process to terminate naturally; record
   its real exit, complete counts and coverage JSON. Then run alternate FULL,
   independent JAX/TF, Torch/Autograd focus, actual 28-section matrix, compile,
   legal/privacy/security/no-token/no-vendor, five environment versions and
   import origins, and pip check. Preserve full logs and independent exits.
   Missing matrix dependencies are NOT_EXECUTED. Recheck source equality.
   Baseline coverage is 90.35145452152166%, with 68 exclusions; it is not a
   functional-completion metric. Preserve genuine failures, minimally fix real
   regressions, refreeze and rerun affected/necessary FULL gates. Never borrow
   old-tree passes.
2. After gates, accept only the bounded P0.1 native functions: typed mixed-radix
   from_int/dimensions, state/density construction and conversion, tensor/expand/
   copy/conjugate/transpose/adjoint/reverse, full-system numeric evolve,
   probabilities/sample/measure/reset, partial trace and the composed basis ->
   tensor -> density -> partial_trace -> probabilities workflow. Per function,
   report actual native calls, pre-fix reds, independent complex mathematics,
   public Qiskit 2.4.1/2.6 differentials, dimension/qargs/error/ownership contracts
   and unsupported paths. Keep mixed mapped operators/circuits/general channels
   Unsupported until implemented; never confuse a single qudit with qubits in
   analysis. Preserve native q0-first/dict probabilities/density shape-tuple dim.
3. Only after required gates, stage explicitly owned P0.1 paths, compare staged
   runtime/tests/examples with the tested tree, commit normally and report SHA.
   No push, force/rebase/reset/amend, token/auth/TLS, cloud/hardware, tag/release
   or vendoring. Preserve user Router/Studio files. Report whole-workspace Router
   ledger failure separately from controlled-export legal success.
4. Only after P0.1 gates/checkpoint, consider P0.2: first mixed-radix mapped
   numeric operators with correct local embedding/dimension/qargs order; then a
   mathematically justified finite mixed-radix Kraus/channel subset; preserve
   binary-only analysis guards and separately define any true generalization.
   Each requires verified public behavior, native red/fix, independent oracle,
   public differential and composed calls. No RNG/arithmetic/purity, new global
   allocator audit, upstream passthrough, wrapper-as-engine or large facade.
5. Report verified native P0.1 functions separately from remaining public
   incompatibilities, P0.2 functions, actual gates/coverage/matrix, local SHA,
   remote CI and remaining full-SDK APIs. The order is current main FULL ->
   remaining gates -> bounded acceptance -> local checkpoint -> mapped numeric
   operator work. Full functional replacement remains ACTIVE / INCOMPLETE,
   C3 stays PARTIAL, Capture/Studio remain out of scope and Studio stays last.

## Completed Clarification: Public Metadata Differences

After main FULL coverage and the supplementary numerical comparisons were
reported, the designated conversation's completed clarification was fully read:

- Retain the native actual-partition num_qubits invariant. The four observed
  public partial_trace num_qubits differences per version are Partial Public
  Compatibility; correct native mathematics must not be changed merely to
  imitate an unexplained public result. Any later compatibility mapping belongs
  at its explicitly defined public boundary.
- Public DensityMatrix methods that do not exist, such as transpose in both
  installed versions, are NATIVE_MATH_ONLY when checking the existing native
  method. Do not count this as public-method parity or an upstream feature gap.
  Retain the incomplete initial comparison/harness failures.
- Keep tree 7aeb821e production/tests/examples frozen. Complete alternate FULL,
  independent JAX/TF/Torch/Autograd and the real 28-section matrix with logs and
  independent exits before acceptance, checkpoint or P0.2. Recheck workspace
  and export equality afterwards. Source changes require refreezing and actual
  affected/necessary full reruns, not reused receipts.
- Numerical checks and public contracts are separate judgments: the two sets
  of 158 numerical comparisons support only their measured mathematical slices.
  Keep the four metadata differences Partial and absent public methods outside
  public pass counts. Preserve mixed mapped operator/circuit/general channel
  Unsupported boundaries, and disclose the independent dirty-workspace Router
  legal failure without touching the user's files.
- After remaining gates, classify only sufficiently evidenced native slices as
  Verified Native, others Partial/Unsupported, then make a scoped normal local
  checkpoint and report SHA, tested tree and truthful remote CI. Main's 3189
  passed / 5 skipped / 3 xfailed and 90.44385395138274% coverage with 68 unchanged
  exclusions are quality evidence, not all-gates acceptance or an SDK parity
  percentage. Full replacement stays ACTIVE / INCOMPLETE; C3 stays PARTIAL and
  Capture/Studio remain excluded.
