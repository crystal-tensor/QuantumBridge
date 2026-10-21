# Stage 12-A P0.6 Existing Subsystem Gap Audit

Date: 2026-10-22 (Asia/Shanghai). Baseline HEAD:
ac34b6d79fc00291f72ea132248c822895057a74. Previous goal turn made progress:
actual native state arithmetic was committed and full frozen gates terminated.
This audit follows P0.6 Task 1 and the Task 8 stop condition; it does not invent
a new permutation API or repeat an already implemented feature as new work.
The full independent Qiskit/PennyLane replacement objective remains ACTIVE /
INCOMPLETE, C3 PARTIAL, and no Studio or cloud/hardware work is included.

## Existing Function Evidence

The existing `Statevector.reverse_qargs` / `DensityMatrix.reverse_qargs` already
perform a real mixed-radix index permutation, reverse dimension metadata and
invert correctly. They are not simple flat array reversals. Existing native
`partial_trace(keep)` methods retain selected subsystems in original subsystem
order, independent of the order of the keep list; this established convention
is asserted by the P0.1 tests and is not changed to manufacture a failure.
The module function performs actual row/column-axis contraction, not block
selection. Existing mapped evolution/expectation compose with both operations.

Temporary independently authored audit:
`/tmp/qb-stage12a-p06-existing-subsystems.py`. Each command has a complete
`/tmp/PREFIX.log` and independent `.exit`:

| Prefix | Actual terminal result |
| --- | --- |
| qb-stage12a-p06-main-existing | exit 1: audit author did not catch an exception from a sampled public all-traced Statevector call; not a native mathematical red |
| qb-stage12a-p06-main-existing-corrected | exit 0; 432 native operation groups; installed Qiskit 2.4.1 |
| qb-stage12a-p06-alternate-existing | exit 0; 432 native operation groups; installed Qiskit 2.6.0 |
| qb-stage12a-p06-sdkfree-existing | exit 0; 432 native operation groups; no Qiskit/PennyLane or AD frameworks installed |

Each native group checks complete complex arrays and dimensions, not only trace
or probabilities. These are scripted assertion groups, NOT new pytest passing
test counts. Six geometries: (2,3,2), (3,2,4), (2,3,4), (3,2), (2,4), (1,).
Both state classes, managed/unmanaged and strided/contiguous storage are covered.
All subsets, including reversed keep lists, trace-all and keep-all, are checked.
Oracle A explicitly enumerates row/column mixed-radix indices and contracted
digits; Oracle B independently reshapes, contracts tensor axes and reshapes the
result. Neither calls production helpers. Density fixtures are complex mixed
states with nonzero coherences, not just diagonal classical distributions.

Actual chain A: (3,2,4) vector -> reverse to (4,2,3) -> local nonunitary
Operator.evolve on subsystem 2 -> local expectation. The complete evolved vector
agrees with an independent whole-system matrix; expectation is
1.0571918367346937 + 0j. Chain B: the original vector -> density -> nontrivial
partial trace retaining subsystems (2,0) in established original order -> (3,4)
reduced density -> purity 0.9915715118700543 + 3.839978632706798e-18j. The complete
complex reduced matrix agrees with both independent contraction oracles.

## Public Contracts And Limits

Both installed Qiskit versions have public reverse_qargs() on both classes and
module-level quantum_info.partial_trace(state,qargs), where qargs are discarded
subsystems, unlike the native method's retained set. Native high-radix q0 and
public low-radix q0 are explicitly translated by reversed metadata/positions.
Neither sampled public class has permute(), permute_qargs(), reshape() or a
partial_trace() method. No nonexistent public method is implemented here.

Both versions produce the same audit exception/difference pattern: 20 sampled
public all-traced Statevector calls raise ValueError, while native trace-all has
the independently checked scalar-register density result. Another 28 public
return/metadata differences are 20 all-traced DensityMatrix scalar returns and
8 one-dimensional-subsystem empty-keep metadata cases. Numerical values in the
28 successful differing-contract cases agree; return type/dimensions do not.
Repeated storage/scope variants are counted separately, not 48 unique semantic
defects. These are observed compatibility boundaries, NOT upstream defect or
implementation-internals claims. P0.2/P0.3 differential artifacts stay unchanged.

## Decision And Actual Next Gap

NO_NEW_FUNCTIONAL_GAP_IN_SURVEYED_EXISTING_OPERATIONS. No production/test/example
code is changed for reverse/reduction. This does not claim every subsystem API
or complete public compatibility. Task 8 stops this audit without a false
feature commit or duplicate new full-gate run. Runtime equality to P0.5 code
87076d532084f993842859318802ef8155455776 exits 0. Its existing FULL evidence is
still for that identical runtime; no fresh P0.6 FULL/matrix result is claimed.

A separate real public core function is missing:
`DensityMatrix.partial_transpose(qargs)`. Qiskit 2.4.1 and 2.6.0 expose and execute
it; QuantumBridge does not. This swaps selected row/column subsystem indices,
not a subsystem permutation on both axes and not a partial trace. Actual
two-qudit calls on a normalized entangled (native 3,2) state return unchanged
dimension metadata, trace approximately one and eigenvalues (-0.5,0,0,0.5,0.5,0.5).
Negative partial-transpose eigenvalues must NOT be projected to PSD.
It is the proposed next native function, not implemented or accepted by this
audit and not mislabeled as a fabricated general permutation API.

No credential/auth/TLS change, package installation, upstream source/test port,
vendoring, push, tag/release, history rewrite, user Router/Studio edit or real
service execution is performed. The seven unexecuted ecosystem subsets, known
pip conflicts and separate dirty Router legal failure remain unresolved.
