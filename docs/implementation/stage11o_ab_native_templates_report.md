# Stage 11O-A Native Template Checkpoint

Date: 2026-10-20. Starting local HEAD: `df9bd22240ea13b38d5c78be926ea073aa05edfb`.
This report covers native templates, not completion of Stage 11O-A/B. The
multi-Tape TransformProgram, measurement splitting/grouping and transformed
native VJP remain required unfinished Stage 11O-B work. Full core parity is
ACTIVE / INCOMPLETE. Stage 11O-C remains a separately audited partial chemistry
implementation; no new elements, basis libraries or SCF features were added.

## Executable API

`from quantumbridge import templates` exposes concrete native objects:
AngleEmbedding, BasisEmbedding, AmplitudeEmbedding, BasicEntanglerLayers,
StronglyEntanglingLayers, IQPEmbedding, QFT and TrotterProduct. Each has a real
`decomposition()` of existing native Operation objects, `to_circuit()` and
`apply(Circuit_or_Tape, wire_map=None)`. NativeTemplate is a shared emission
interface, not an SDK passthrough or a second quantum execution engine.

The actual implementations enhance `qml/embeddings.py`, `qml/templates.py`
and the new `qml/subroutines.py`. Named template wires can be explicitly mapped
to native integer wires; decomposition/to_circuit uses the ordered compact
local register. Applying it preserves the caller's selected wire order and
the existing Tape parameter recorder, including live framework expressions.
Objects do not capture a stale QNode result: construct/apply them inside the
existing native QNode callable for each input.

| Template | Actual implementation and current boundary |
| --- | --- |
| AngleEmbedding | RX/RY/RZ, partial feature vectors, strict shape/wires and preserved scalar/vector input graph |
| BasisEmbedding | Actual X gates for integer, bitstring or zero/one vector; static inputs only, prepares a basis state from zero input |
| AmplitudeEmbedding | Actual bounded normalized real/complex unitary state preparation; padding precedes normalization; input gradients unsupported |
| BasicEntanglerLayers | Shape (layers,wires), one-parameter RX/RY/RZ/phase, no one-wire entangler, one two-wire CNOT, larger closed ring |
| StronglyEntanglingLayers | Shape (layers,wires,3), RZ(phi), RY(theta), RZ(omega), per-layer ranges and CX/CZ; no one-wire self-gate |
| IQPEmbedding | H/RZ per feature and CX/RZ/CX feature-product interactions, repeated and custom pair patterns |
| QFT | Reused native H/controlled-phase/swaps circuit, selected wires, inverse, no-swap option, bounded wire count |
| TrotterProduct | Native Pauli-string basis changes/parity ladders/rotations, positive-time exp(+i t H), first/second-order formulas, bounded steps |

## Compatibility Changes

The existing functional `qml.angle_embedding` retains its default Y rotation;
the new `templates.AngleEmbedding` defaults to X like the public target API.
The legacy `basic_entangler` RY/open-chain helper remains distinct and retains
its meaning. `basic_entangler_layers` now has the explicit public RX/ring
behavior: its former RY/open-chain implementation was not equivalent. Callers
wanting the old RY/open-chain layers can use `hardware_efficient_ansatz`.
StronglyEntanglingLayers now cycles its default range rather than incorrectly
using range one in every layer. These changes are intentional and tested.

The old amplitude test asserted only a planned-state-preparation marker. It
now tests the actual complex state before applying later gates. Metadata says
native-executed only because a real native unitary is present and executed.

## Mathematical Semantics

Rot's sequential decomposition produces the matrix
`RZ(omega) @ RY(theta) @ RZ(phi)`, not the opposite Euler order. IQP uses
`RZZ(features[a]*features[b])` and repeats the full H/encoding/interaction layer.
Complete QFT matrices are compared against the independent positive-sign DFT
definition, not just probabilities. The no-swap version has explicit reversed
output-bit ordering, and the inverse is checked as the complex adjoint.

Trotter follows the public positive-sign `exp(+i t H)` convention. First-order
circuits emit the listed Hamiltonian operands in reverse execution order;
second order emits the forward half-step then reversed half-step. A valid but
different second-order ordering found during development was corrected to the
public contract, not accommodated by a looser tolerance. Identity terms are
represented by cancelling RZ/phase rotations that retain the exact global
phase without detaching a trainable time parameter. For noncommuting terms,
finite-step errors are real approximation errors. First-order time negation
is not generally the adjoint without reversing its operand order; the symmetric
second-order formula does satisfy the tested time-sign/adjoint relation.

Amplitude preparation reuses native unitary completion of a normalized vector.
Normalization is scale-stable for tiny/huge finite real input. Static feature
and dimension checks happen before synthesis. It requires an untouched zero
target subsystem, not a reset/overwrite of an arbitrary entangled input.
The requirement is retained on the native operation and checked at runtime by
the vector, density, MPS and shared dynamic execution paths. Custom nonzero
density/MPS inputs reject; zero inputs and unaffected spectator states work.
This is not a complete general StatePrep implementation or differentiable
amplitude synthesis. Unsupported simulator representations reject explicitly.

## Gradients And Scientific Integration

Angle, Basic and StronglyEntangling templates retain shared/nonlinear input
expressions and tensor shapes through the existing first-order native
parameter-shift/adjoint engines. Tests include independent analytic chain
rules, keywords/nontrainable inputs, nested multi-output Jacobian, VJP/JVP,
Torch backward/SGD and Autograd tensor gradients. IQP feature-product and
Trotter-time gradients also have real native tests. No simulator backprop or
higher-order derivative support is inferred from these framework VJPs.

The generated Stage 11O-C four-qubit H2 Hamiltonian is reused with a native
BasisEmbedding HF reference, a trainable Strong template rotation and the
existing fermionic double-excitation circuit. Energy gradients and an actual
optimization step are checked. General Basic/Strong layers are not asserted
to preserve electron number or guarantee molecular ground-state convergence.

A 100-wire GHZ MPS plus a local trainable AngleEmbedding has the analytic
two-site correlation cos(theta) and shift gradient -sin(theta), with maximum
bond two and dense expansion APIs disabled. Measured tensor storage is 12672
bytes, discarded weight zero, 101 operations and two shifted evaluations.
Transform count is zero at this checkpoint. This proves the stated low-bond
template path, not the still-unimplemented transform composition or arbitrary
large QFT/amplitude efficiency.

## Numerical And Test Evidence

Targeted main environment: 59 native scenarios plus 15 public differential
scenarios, 74 passed. The 59 include optional Torch/Autograd tests. Public tests
call only public APIs on the pinned SDKs, not implementation/test source.
Independent mathematics covers full complex rotations/QFT/IQP/Trotter,
occupation/state preparation, analytic derivatives and explicit boundaries.

Three SDK-free examples perform actual calculations:

- `native_angle_embedding_qnode`: expectation 0.6907092328529886, shared/nonlinear
  input gradient -1.5049381923831973, native shift and adjoint agree.
- `native_entangling_templates_training`: actual two-wire Strong template,
  80 adjoint SGD steps, loss 2.6379673349167883 -> 0.0005720295635672106.
- `native_qft_and_trotter`: three-wire QFT complex residual 1.42e-15; second-order
  Trotter errors for 1/2/4/8 steps are 0.0473166, 0.0115928, 0.00288338,
  0.000719919. These demonstrate convergence, not exact finite-step evolution.

An exploratory Torch training target encountered a local optimum in this
nonlinear one-wire model; the training exercise uses a reachable local target.
The analytic derivative tolerance was not weakened to pass optimization.

Final clean tracked-tree snapshot: `/tmp/qb-stage11oa-final-jZJL0j`, built from
the starting commit and this checkpoint's staged files. User Studio/Router
changes and unrelated untracked files were excluded and remain untouched.

| Gate | Verified result |
| --- | --- |
| SDK-free full pytest | 1231 passed, 124 skipped |
| Main Qiskit 2.4.1 / PennyLane 0.44.1 full pytest | 1511 passed, 4 skipped |
| Alternate Qiskit 2.6.0 / PennyLane 0.42.3 full pytest | 1470 passed, 45 skipped |
| Public template differential, main | 15 passed |
| Public template differential, alternate | 15 passed |
| SDK-free focused native templates | 57 passed, 2 optional framework skips |
| Package-wide line coverage | 20671 / 23332, 88.59506257500429% |
| Existing excluded lines | 68, unchanged |
| Full local matrix | Exit 0; generated inventories stayed in the snapshot |
| compileall | Exit 0 for quantumbridge, examples and scripts |
| Focused legal, ledger, no-vendor/no-token checks | 8 passed |
| Three new examples in SDK-free environment | All exit 0 |
| Both isolated pip checks | No broken requirements |
| Global pip check | Existing pyquafu/NumPy and WeasyPrint/tinycss2 conflicts remain |

Core module coverage: embeddings 97.22%, subroutines 98.84%, template core
99.31%, existing QML layers 98.28%, concrete template exports 100%. Coverage
exceeds the 88.42063976292164% chemistry baseline without new exclusions.
All full runs include the Stage 11H--11O-C device, noise, compiler, serialization,
framework and chemistry regressions. The SDK-free environment has no Qiskit,
PennyLane, PySCF, Torch or Autograd installed; optional tests genuinely skip.
The alternate lacks Torch/PySCF and reports those skips rather than claiming
their execution. No global dependency conflict was hidden or repaired here.

Git publication is separate: no fresh remote HEAD or new-SHA CI is verified,
and no push is claimed. The existing authorization/remote-state issue is not
bypassed. Prior 11M/11N/11O-C local commits remain preserved.

## Limits And Serialization

TemplateLimits bounds selected wires (128), layers (256), operations (100000),
input parameter elements (4096), amplitude dimension (64), QFT wires (12) and
Trotter steps (1024). Iterator wire/pair/range inputs are consumed with finite
limits, not converted from an unbounded stream. The existing Device/MPS and
QNode derivative budgets remain independently enforced.

Expanded supported standard-gate circuits round-trip through native QASM2,
QASM3 and QPY v13, including complex-unitary equivalence. Native IR also
round-trips the bounded amplitude matrix and its zero-input requirement.
The current QPY v13 and standard QASM codecs do not encode this opaque matrix
preparation: export rejects rather than silently replacing it or dropping
its contract. Template Python objects themselves are not serialized as an
SDK object. General state-preparation decomposition into a portable hardware
gate set remains future parity work.

## Remaining Scope

Still missing: full template catalogue, complete operation/capture/broadcast
contracts, arbitrary imprimitive operations, higher Suzuki orders, trainable
Hamiltonian coefficients, differentiable amplitude features and universal
hardware decomposition of preparation matrices. Stage 11O-B's real multi-Tape
protocol/program, grouping, shot allocation, postprocessing and transformed
VJP have NOT been implemented by this checkpoint. They remain the next
required work, not optional follow-ups. No Studio/Router, token, cloud/hardware,
vendor source, tag/release or history rewrite occurs in this batch.

The independent implementation uses public mathematical/API contracts listed
in the Stage 11O-A/B gap audit. Both public SDK versions must be tested and
reported separately. An older remote CI run cannot validate unpublished code.
