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
