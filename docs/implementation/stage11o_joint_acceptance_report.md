# Stage 11O Joint Acceptance

Date: 2026-10-20; B6 starting HEAD `bd88f88`, branch main. This report concerns
integration of implemented Stage 11O-A/B/C native capabilities, not the whole
Qiskit/PennyLane replacement objective. Three-environment full regression and
explicit coverage passed; the complete local matrix log reaches its final gate.

## Templates

| Native template | Actual supported execution | Evidence and remaining contract |
| --- | --- | --- |
| AngleEmbedding | X/Y/Z gate emission, ordered/partial wires, real angle graphs | Native/public state/gradient tests; B6 101-wire feedback gradient; broadcast/capture/full device API partial |
| BasisEmbedding | Integer/string/vector computational occupation | Native/public wire-order/state tests; general state-preparation API partial |
| AmplitudeEmbedding | Bounded complex state, padding/normalization/zero-input guards | Native/public state tests; input differentiation and portable general synthesis incomplete |
| BasicEntanglerLayers | RX/ring and supported rotation semantics, no duplicate two-wire edge | Native/public operation/unitary/gradient tests; arbitrary operation types/broadcast incomplete |
| StronglyEntanglingLayers | Euler layers, ranges, CX/CZ, shared parameters | Native/public unitary/framework tests; general imprimitives/capture incomplete |
| IQPEmbedding | Features, pair products, repetitions | Native/public state/gradient tests; complete operation/broadcast contracts incomplete |
| QFT | Real gates, ordered wires, inverse/swaps, complete bounded complex phase | Native/public full-unitary tests; full operation/resource API incomplete |
| TrotterProduct | Bounded Pauli product formulas order 1/2 and time derivatives | Native/public approximation/phase/gradient tests; higher/general formulas/trainable coefficients incomplete |

Sources: `quantumbridge/templates.py`, `quantumbridge/qml/template_core.py`.
Behavioral gates: `tests/templates`, `tests/compat/test_native_template_differential.py`,
`tests/transforms/test_native_transformed_autodiff.py` and B6 integration tests.
Native emission and execution do not imply the complete public template catalog.

## Transforms

| Checkpoint | Actual integrated capability | Persistent boundary |
| --- | --- | --- |
| B1 | Owned Tape copies, actual child batches, reverse result reconstruction and independent execution receipts | Complete dispatcher/operation protocols incomplete |
| B2 | Fresh QNode and explicitly configured callable dispatch, parameter reconstruction | Full public signatures/capture not established |
| B3 | merge/cancel/decompose/compile/single-term splitting, exact phase and restored layout | Complete commute/decomposition/observable/layout catalogs incomplete |
| B4 | Real QWC joint samples, covariance, deterministic uniform/weighted allocation and shot vectors | General observables/allocators/public defaults differ |
| B5 | Native child shift/adjoint plus postprocessing/source chain, coefficients, Torch/Autograd and sampled gradients | Explicit bounded Jacobian products; not matrix-free, higher-order, JAX/TF or full derivative-device API |
| B6 | Fresh coherent records, real enlarged unitary child, logical reduced/record outputs, native gradient, QWC and native compiler routing | Reset/postselection/noise/conditional MCM/loops/Store/snapshots/full-state and complete public API remain open |

Mathematical evidence includes the measured-wire-reuse counterexample,
untraced complex controlled matrices without phase alignment, original dynamic
versus logical reduced density, stochastic joint records and real shifted work.
Finite-shot RNG paths need statistical agreement, not per-shot identity.
Original mixed states are not compared directly to expanded coherent pure
states. Passive metadata/covariance/error estimates are not derivative leaves.

## Native Chemistry

The source implementations in `quantumbridge/chemistry` and `quantumbridge/qchem.py`
provide real normalized H STO-3G s-shell integrals, closed-shell RHF iterations,
AO-to-MO tensors, fermionic CAR, Jordan-Wigner, bounded exact diagonalization,
occupation/excitation helpers and native excitation/VQE workflows. They are not
the older fixed educational H2/LiH Hamiltonian examples or installed-package
passthrough adapters. Geometry and units affect the computed integrals.

Existing `tests/qchem` and `tests/compat/test_native_qchem_differential.py`
cover independent physical/matrix identities and installed public PySCF/
PennyLane comparisons. B5 and B6 reuse one geometry-derived Hamiltonian through
QWC/native derivatives/optimizer; no per-child or per-shift SCF reconstruction.
The standard theta .3 H2 energy is -1.0279252771620968 with derivative
.40622294673301496. B6 feedback energy/derivative are -.7958578898722166 /
.181811259942503 and agree with original native dynamic execution. The latter
ansatz is not assumed to conserve particle number or yield a ground state.

Other elements/angular shells/bases, robust open-shell/general SCF, fully
differentiable HF, general molecular properties, active spaces/tapering and
complete UCCSD/qchem interfaces remain incomplete. Geometry finite-difference
consistency is not analytic integral/SCF differentiation.

## Non-Dense And Compiler Evidence

B5 retains the 100-wire GHZ/template/QWC gradient. B6 adds a real measured/
reused-wire experiment with 100 logical and 101 actual MPS wires, one record,
peak bond 2, 12800 tensor bytes, zero observed truncation/discarded weight,
2 shifted evaluations, 3 transforms and zero physical shots. Full dense APIs
are forbidden during the proof. Neither tensor bytes nor discarded weight is
a general gradient error bound or a peak transient-workspace measurement.

A separate small native compiler test includes record ancilla in the 3-wire
Target, routes the coherent circuit on directed coupling and restores logical
terminal outputs. Insufficient Target/device width rejects; no physical
hardware deployment is inferred from simulator expansion.

## Final Gates And Scope

| Gate | Final receipt |
| --- | --- |
| Native/public B6 focused | 94 native cases; 8 public cases in each SDK version |
| Shared preflight | 399 passed / 1 warning |
| SDK-free / main / alternate full | 1567 passed / 147 skipped; 1914 passed / 4 skipped; 1858 passed / 60 skipped |
| Explicit package coverage | 22458 / 25144 = 89.31753102131721%, 68 unchanged excluded lines; 1914 passed / 4 skipped |
| Complete matrix / actual embedded coverage | All 28 sections completed through final OpenFermion 1 passed; two plain fulls 1914 passed / 4 skipped each; embedded coverage 1914 passed / 4 skipped, 25144 statements / 2686 missing, 155.59s; original shell handle unavailable on resumption |
| Focused A/B/C/system suites | 1159 passed / 6 warnings, including native/public chemistry and templates, interfaces, devices, compiler, serialization and transforms |
| Compileall / legal/privacy / isolated pip checks | Exit 0; 9 passed in clean snapshot; both isolated environments clean |
| Five new SDK-free examples | All five numeric assertion executions passed again on the final runtime snapshot |

Line coverage and pytest totals describe executed code/tests, not the fraction
of the entire SDK function library implemented. Module-specific artifacts and
remaining behavior in the tables above are the functional evidence.
Unavailable installed-dependency matrix lanes are explicit non-execution,
not positive installed coverage. The matrix completion receipt is its complete
log through the final command under the existing `set -euo pipefail` script;
the original terminal handle no longer exists to recover a separate exit code.
All 14 staged Python files matched the tested snapshot by SHA256; final
receipt-only documentation edits receive separate index-snapshot checks.
The current authoritative gap ranking is
`docs/implementation/stage11o_remaining_functional_parity_gaps.md`.
No tag/release/history rewrite or user Studio/Router change is included.
The existing untracked Router attribution issue is reported separately from
clean tracked/index snapshot tests. Local commits are not published/new-SHA
remote CI evidence. Full functional parity remains ACTIVE / INCOMPLETE.
