# Stage 11O-A/B Native Template And Transform Audit

Date: 2026-10-20. Starting local HEAD:
`df9bd22240ea13b38d5c78be926ea073aa05edfb`.

This is a pre-implementation audit, not a completion report. The original
Stage 11O audit and the completed, bounded Stage 11O-C chemistry checkpoint
remain separately inspectable. Full Qiskit/PennyLane replacement is incomplete.

## Verified Baseline

Clean tracked-tree tests for the chemistry checkpoint: SDK-free 1174 passed /
121 skipped, installed 1437 / 4, alternate 1397 / 44. Package-wide line coverage
is 20289 / 22946 statements, 88.42063976292164%, with 68 unchanged exclusions.
Full local matrix, compileall, focused legal checks and the three new SDK-free
chemistry examples pass. These receipts do not validate unimplemented templates
or a multi-Tape transform protocol.

Stage 11M `76ea077`, Stage 11N `0d00362` and Stage 11O-C `df9bd22` are preserved
local commits. Last successful remote tracking value `45fe338` is stale.
Tracking ahead 3 / behind 0 is not proof of current remote state. No new remote
publication or exact-SHA Actions success is claimed. Do not poll/bypass the
existing workflow authorization problem or rewrite history to publish.

## Current Implementation And Gaps

| Existing component | Actual behavior | Missing contract / safe reuse |
| --- | --- | --- |
| `qml/embeddings.py::angle_embedding` | Emits rotations into Circuit or Tape | `float(value)` breaks the first-order input trace; zip silently truncates excess features; validate shape, wires, axes and preserve parameters |
| `qml/embeddings.py::amplitude_embedding` | Stores feature metadata only | No prepared quantum state; must replace with actual bounded real/complex preparation, padding/norm checks and explicit differentiation capability |
| `qml/templates.py::basic_entangler` and layers | RY rotations and open-chain CNOT on Circuit | Not the public BasicEntanglerLayers default RX/closed ring contract; missing wire/shape/rotation controls and Tape-safe parameter handling |
| `qml/templates.py::strongly_entangling_layers` | RZ/RY/RZ and fixed range-one cyclic CNOT | Casts parameters to float, lacks ranges/imprimitive/shape validation, tries illegal self-CNOT on one wire |
| `circuit_library/data_preparation.py` | Real native basis and full-vector unitary state preparation | Reuse state-preparation mathematics, add explicit preallocation dimension budgets and wire mapping; do not imply amplitude input gradients |
| `circuit_library/templates.py::qft` | Actual H/controlled-phase/swaps, optional inverse | Can reuse native decomposition; add selected wire mapping, complete complex-unitary tests, resource limits and explicit template API |
| IQP / Trotter template families | No concrete native family API found | Implement public supported gate semantics independently, not a generic upstream wrapper |
| Native `core/Operation`, `Circuit`, `qml/Tape` | Existing gate/control/parameter/measurement objects execute | Reuse them; do not add a second incompatible Tape or Operation engine |
| `qml/QNode`, `diff/qnode_engine.py` | Actual forward, shared/nonlinear trace, first-order quantum derivatives and shot partitions | Add transform dispatch that uses the same program for forward and backward, preserving current API behavior |
| `diff/compiled_parameters.py` | Re-records split/merged compiled parameter expressions | Reuse parameter-AST reconstruction after single-Tape gate transformations; do not float-convert expressions |
| `interfaces/qnode_autodiff.py` | Actual native-Jacobian Torch VJP and Autograd primitive | New transformed execution plans must retain this same framework bridge and higher-order rejection |
| `transforms/circuit_transforms.py` | Identity Circuit copy only | No Tape batch or executable postprocessor |
| `transforms/gradient_transforms.py` | Existing numerical callable gradient / metric / QNG helpers | Not a Tape dispatcher or TransformProgram; keep distinct, working APIs |
| Compiler PassManager / decomposition / cancellation | Real bounded compilation and dynamic-aware segmentation | Reuse lower-level algebra/target rules, but build real Tape batching, QNode dispatch and reverse postprocessing separately |
| `qml/MeasurementRequest` and measurement tree helpers | Native measurement requests and nested output representation | Reuse for linear-term splitting; retain coefficient order, identity terms, result tree and shot semantics |
| `devices` / simulator / dynamic engine | Existing native vector, density, MPS, tableau and noise paths | Preserve method capabilities and limits; do not obtain large MPS outputs through dense expansion |
| `serialization` | Actual QASM2/3 and QPY v13 supported subsets | Serialize concrete expanded native gates where lossless; unsupported objects/metadata must reject rather than disappear |
| Stage 11O-C chemistry | Actual geometry, Gaussian integrals, RHF, fermionic/JW Hamiltonian and VQE | Reuse the generated molecule/Hamiltonian for template/transform energy tests, not fixed Stage 9D coefficients |

## Observed Public And Native Probes

Only installed public APIs were called. No upstream implementation or test
source was read or copied. These exploratory probes are not yet the new
automated Template/Transform differential suite.

- Native QFT complete complex-matrix maximum residual against public PennyLane
  for 1/2/3/4 wires: 0, 1.15e-16, 1.24e-16, 1.69e-16. The alternate 0.42.3
  four-wire result also differs by 1.69e-16. This validates the existing small
  QFT decomposition, not arbitrary template or serialization behavior.
- Public BasicEntanglerLayers emits no CNOT for one wire, one CNOT for two,
  and a closing ring for three/four. Nontrivial wire order follows the supplied
  list. Its default rotations are RX, unlike the legacy RY/open-chain helper.
- Public StronglyEntanglingLayers on one wire emits only Rot. Default ranges
  on three wires change from one to two between the first and second layer.
- IQP public decomposition emits H/RZ for each feature and pairwise MultiRZ
  interactions with the feature product, honoring supplied wire order.
- Public TrotterProduct is the positive-sign `exp(+i t H)` approximation,
  with ordered operands affecting first-order multiplication. The pinned
  versions expose `Evolution` (0.44.1) versus `Exp` (0.42.3) children; compare
  physical matrices instead of requiring equal internal type names.
- An actual native legacy AngleEmbedding input-gradient probe raises
  UnsupportedFeature because `float` destroys its Dual trace.
- An actual legacy one-wire StronglyEntangling probe raises the distinct-wire
  validation error. Do not weaken core wire validation to accommodate it.

## Implementation Boundaries

1. Enhance existing QML template paths and expose concrete reusable template
   decomposition/application APIs. Document differences from legacy helpers;
   avoid silently equating old behavior with PennyLane semantics.
2. Validate template shape/wires/resources before expansion. Preserve real
   trainable expressions during gate emission, including shared/nonlinear
   inputs. Amplitude preparation must explicitly reject unsupported feature
   differentiation and unreasonable dense dimensions.
3. Implement Tape-to-Tapes plus a real result postprocessor, with bounded
   composition and reverse-order reconstruction. A compiler pass list alone
   cannot satisfy this contract.
4. Execute each child Tape independently. First implement safe inverse/rotation
   optimization, bounded decomposition, compilation and linear-term splitting.
   Extend to actual QWC grouping and precisely documented shot allocation.
   General commuting groups are not necessarily jointly measurable by local
   basis rotations. Deferred measurements must reject unproved dynamic cases.
5. Preserve measurement/reset/Store/barrier/conditional boundaries. Transform
   parameters before constructing a native derivative plan, never run a
   different or stale program for a framework backward pass.
6. Bound depth, tapes, per-Tape/cumulative operations, decomposition work,
   postprocessing structure and total sampled shots before executing a batch.
7. Reuse Stage 11O-C molecular Hamiltonians for real split/unsplit energy,
   gradient and optimizer comparisons without expanding the chemistry scope.

## Required Verification Before Claiming This Batch

The received Stage 11O-A/B task requires at least six concrete template types
(prefer all eight listed), three genuinely differentiable template families,
five actual transforms, independent child execution, reverse postprocessing,
native multi-Tape gradients, QWC/shot tests and generated-H2 integration.
It also requires 35 independent native template scenarios, 30 transform
scenarios, 12 + 12 public comparisons on both pinned PennyLane versions, eight
gradient/training scenarios, eight dynamic/resource/unsupported counterexamples
and seven runnable SDK-free examples.

Protect the existing first-order Torch/Autograd, compiler/global-phase, dynamic
execution, QPY v13 bilateral, simulator/noise and native chemistry regressions.
Add a 100-wire MPS template-plus-transform local measurement/shift test with
dense expansion disabled. Re-run all three clean environments, full matrix,
coverage without exclusions, examples, legal/privacy and dependency checks.

Do not move to Stage 11P before reviewing Stage 11O-A/B/C jointly. Complete
template/transform/qchem parity is still incomplete. Studio/Router, tokens,
cloud/hardware, vendoring and history rewriting are outside this batch.

## Public Contract References

- https://docs.pennylane.ai/en/stable/code/api/pennylane.AngleEmbedding.html
- https://docs.pennylane.ai/en/stable/code/api/pennylane.BasicEntanglerLayers.html
- https://docs.pennylane.ai/en/stable/code/api/pennylane.StronglyEntanglingLayers.html
- https://docs.pennylane.ai/en/stable/code/api/pennylane.AmplitudeEmbedding.html
- https://docs.pennylane.ai/en/stable/code/api/pennylane.IQPEmbedding.html
- https://docs.pennylane.ai/en/stable/code/api/pennylane.TrotterProduct.html

Documentation supplies behavioral/mathematical contracts only. Current stable
docs may name a newer SDK; executable oracles are pinned to 0.44.1 and 0.42.3.
