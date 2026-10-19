# Stage 11O Native PennyLane Gap Audit

Date: 2026-10-20. Starting local main:
`0d00362191efb85d2d7b1d14b15d5234156a74fb`.
This is the required pre-implementation audit, not a completion report.
The complete Stage 11O instruction was received from the owner-authorized
ChatGPT collaboration conversation and read before starting this audit.
Full Qiskit/PennyLane functional replacement remains ACTIVE / INCOMPLETE.

## Baseline And Ownership

Stage 11M `76ea077` and Stage 11N `0d00362` are preserved. Last fetched
origin/main is `45fe338fc0f02de9c19e0af89723755952e5fc98`; its current remote
state is stale/unverified after the latest normal fetch timed out. Local
tracking comparison is behind zero/ahead two, not a fresh remote receipt.
The existing workflow-scope authorization issue is unresolved. No new M/N/O
exact-SHA Actions result exists. Do not rewrite history, delete workflow,
change TLS/credentials, force push or request tokens in chat to bypass this.
Owner handles normal authorization/network restoration independently.

Native local baseline: SDK-free 1120 passed/118 optional skips; installed
1366/4; alternate 1330/40; coverage 88.18100757913508% (19779/22430, existing
68 excluded lines unchanged), full local matrix exit 0. See the Stage 11N
report for exact environments and limits. Green subset tests are not evidence
that untested templates or molecular electronic structure are complete.

Unrelated user Studio/Router changes and untracked files must remain untouched.
No Studio, cloud/hardware, token, vendor, environment, tag or release work is
part of this batch. Only explicitly owned Stage 11O paths may be staged later.

## Templates

| Existing API/path | Actual status | Missing or risky behavior |
| --- | --- | --- |
| qml.angle_embedding | NATIVE_PARTIAL | Emits rotations but float coercion prevents trainable trace preservation; zip can truncate width mismatch; wire/default conventions require public tests |
| qml.amplitude_embedding | METADATA_ONLY | Records input metadata without a preparation operation |
| circuit_library.amplitude_encoding | NATIVE_PARTIAL | Actually creates a preparation unitary; dense completion needs construction budgets and correct integration with Tape/QNode |
| circuit_library.basis_state | NATIVE_EXECUTABLE subset | Native X preparation; requested arbitrary-wire BasisEmbedding and full input validation absent |
| qml.basic_entangler_layers | NATIVE_PARTIAL | Actual RY/open-chain gates, not complete public rotation/ring/shape/trace contract |
| qml.strongly_entangling_layers | NATIVE_PARTIAL | Actual Euler gates but unconditional cyclic entangler, float coercion, no configurable ranges/imprimitive or complete shape checks |
| qml.hardware_efficient_ansatz | NATIVE_PARTIAL | Executable small ansatz, not a full template family or UCCSD |
| IQPEmbedding | NOT_STARTED | No native public template implementation found |
| circuit_library.qft | NATIVE_PARTIAL | Executable circuit builder; complete ordered-wire/phase/gradient/serialization template contract requires evidence |
| TrotterProduct / ApproxTimeEvolution | NOT_STARTED | No native step/composition/error contract found |
| Native UCCSD / excitation templates | NOT_STARTED | Existing chemistry ansatz is hardware-efficient, not an excitation-based UCCSD implementation |
| compat.pennylane_full.templates_adapter | UPSTREAM_ONLY | Inventory/passthrough/result scaffold, not native template execution |

## Transforms

| Existing API/path | Actual status | Missing behavior |
| --- | --- | --- |
| transforms.identity_circuit_transform | NATIVE_EXECUTABLE identity subset | Circuit copy only, no multi-Tape/postprocessing |
| transforms.measurement_count | METADATA_ONLY helper | Counts circuit measurements, not a measurement transform |
| transforms.gradient_transforms | NATIVE_PARTIAL | Numerical callable finite difference/SPSA/metric/QNG, not a general Tape transform protocol |
| Native compiler/PassManager | NATIVE_EXECUTABLE supported subset | Reusable compiler foundation, not itself a Tape/result-postprocessing protocol |
| Transform contract / TransformProgram | NOT_STARTED | Need real ordered child Tape executions and composed result reconstruction |
| cancel_inverses / merge_rotations | NOT_STARTED as Tape transforms | Reuse safe existing compiler logic without crossing measurement/reset/control boundaries |
| decompose / compile | NOT_STARTED as Tape transforms | Preserve parameter trace, measurements, layout and global phase |
| split_to_single_terms / split_non_commuting | NOT_STARTED | Actual multi-execution, coefficient/order/tree reconstruction and shot allocation absent |
| defer_measurements | NOT_STARTED | Must preserve restricted physical/control semantics or explicitly reject, never delete measurements |
| compat.pennylane_full.transforms_adapter | UPSTREAM_ONLY | Optional public lookup/wrapping, not native transform computation |

## Quantum Chemistry

| Existing API/path | Actual status | Missing or incorrect behavior |
| --- | --- | --- |
| chemistry.Molecule | NATIVE_PARTIAL | Geometry/XYZ container; atomic numbers/electron count, finite geometry, units, spin/charge/basis validation need strengthening |
| chemistry.ElectronicIntegrals | METADATA_ONLY container | Stores one/two-body objects; computes no integral |
| primitive/contracted Gaussian basis/integrals | NOT_STARTED | Normalization, Boys, overlap/kinetic/attraction/ERI and nuclear geometry calculation absent |
| Restricted Hartree-Fock / SCF | NOT_STARTED | No native overlap orthogonalization/Fock/density/eigenproblem/convergence iteration |
| chemistry.MinimalH2Driver | METADATA_ONLY reference | Fixed reference energy/nuclear value, not geometry-dependent electronic structure |
| Stage 9D H2/LiH workflows | NATIVE_PARTIAL fixed-model solver | Actual diagonalization of preset coefficients; no geometry-derived integrals/SCF |
| chemistry.FermionicOp | NATIVE_PARTIAL, needs repair | Container exists; normal_ordered only reorders tokens, missing CAR signs/contractions |
| chemistry.JordanWignerMapper | NATIVE_PARTIAL, needs repair | Number-operator subset exists; general products unsupported and zero creation coefficient can map to nonzero Y |
| ParityMapper / BravyiKitaevMapper | UNSUPPORTED | Explicit planned errors, not native mapping implementations |
| chemistry.ExactDiagonalizationSolver | NATIVE_EXECUTABLE matrix subset | Real eigensolve; must act on newly generated Hamiltonian and track particle sector/nuclear constant correctly |
| chemistry.VQEChemistrySolver | NATIVE_PARTIAL | Real ansatz optimizer on provided Hamiltonian; not differentiable molecular integrals or SCF |
| hf_state / excitations / excitations_to_wires | NOT_STARTED | Occupations, spin-orbital ordering and excitation/parity contracts absent |
| active space / properties / geometry derivatives / differentiable HF | NOT_STARTED | Do not infer from fixed Hamiltonian or VQE angle derivatives |
| compat.pennylane_full.qchem_adapter and external chemistry drivers | UPSTREAM_ONLY | Installed SDK computation is not native electronic structure |

## Executed Baseline Probes

These read-only probes ran before changing implementation. They expose existing
untested limitations, not regressions introduced by Stage 11N.

1. SDK-free `qml.amplitude_embedding(Circuit(1), [0, 1])` adds zero operations;
   actual state remains `[1, 0]`, with `mode=metadata-only`. It does not prepare
   the requested excited state.
2. `FermionicOp({'-_0 +_0': 1}).normal_ordered()` returns only `+_0 -_0` with
   coefficient +1. The canonical anticommutator requires identity minus number;
   token sorting is not correct normal ordering.
3. Mapping `FermionicOp({'+_0': 0})` produces matrix norm
   `0.7071067811865476`, rather than zero. General molecular mapping must not
   build on this uncorrected coefficient/sign logic.
4. Legacy MinimalH2Driver at H-H distances 0.5 and 1.5 returns the same nuclear
   value `0.7151043390810812`. Stage 9D H2 coefficient matrices at those distinct
   geometries are exactly equal. These are fixed reference workflows, not the
   requested geometry-to-electronic-structure computation.
5. Native StronglyEntanglingLayers with one wire and weights `[[[.1,.2,.3]]]`
   raises distinct-wires ValueError. Public PennyLane 0.44.1 executes the same
   one-wire template and returns probabilities approximately
   `[0.9900332889206209, 0.009966711079379187]`. Full two-version tests remain due.

## Integration And Next Implementation Gates

Reuse native Tape/Circuit and Stage 11K AngleRecorder/ExecutionPlan, preserving
Dual/shared/nonlinear parameter traces, nested measurement trees and actual
Torch/Autograd quantum derivatives. Do not cast trainable data to float. Add
the real transform protocol around that shared execution foundation, with
ordered child results and explicit postprocessing; renaming PassManager is
not sufficient. Preserve Stage 11L physical layout/phase/boundaries, Stage 11M
lossless subset/rejection policies and Stage 11N noise/snapshot limits.

For chemistry first correct/test CAR and general Jordan-Wigner algebra, then
add bounded normalized s-Gaussian integrals and actual closed-shell H2 STO-3G
RHF. State units, contraction data provenance, chemist/physicist tensor indices,
spin orbitals and nuclear-energy convention. Compare at least two geometries
to independent mathematical tests and optional public PennyLane/PySCF calls.
Public basis data needs a source/license record before inclusion. No source
implementation copying, runtime basis downloads or SDK-native substitution.

Required new native scenario minima: templates 35, transforms 30, chemistry 35;
public comparisons 12/12/10, respectively. Require >=6 real templates, >=3
differentiable templates, >=5 real transforms and true geometry/integral/RHF/
fermionic/JW/4-qubit/exact/VQE closure before claiming this batch's minimum is
met. Full library parity remains incomplete even then. Require 100-wire local
MPS/template gradients with dense expansion forbidden and all three clean full
environments, coverage baseline/no exclusions, matrix, legal and examples.

## Public Contract References

- [Molecular Hamiltonian public API](https://docs.pennylane.ai/en/stable/code/api/pennylane.qchem.molecular_hamiltonian.html)
- [StronglyEntanglingLayers public API](https://docs.pennylane.ai/en/stable/code/api/pennylane.StronglyEntanglingLayers.html)

Current stable pages identify version 0.45.1; implementation oracles remain
pinned to installed 0.44.1 and alternate 0.42.3. Documentation is a public
contract reference, not copied implementation or proof of native completion.

## Subsequent Chemistry Checkpoint

The tables/probes above describe the starting `0d00362` baseline, not the
post-implementation state. Stage 11O-C now repairs the demonstrated CAR and
Jordan-Wigner defects and adds real geometry-derived hydrogen s-Gaussian
integrals, RHF, spin Hamiltonians, number-sector energies and native excitation
VQE/gradients. See `stage11o_native_qchem_report.md` for actual evidence and
limitations. Template and multi-Tape transform findings remain open; this
checkpoint does not complete Stage 11O or the full parity goal.
