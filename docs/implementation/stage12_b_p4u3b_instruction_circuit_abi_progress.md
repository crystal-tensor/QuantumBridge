# Stage 12-B P4-U3B Native Instruction And Circuit Contracts

Status: SUPPORTED CHECKPOINT VALIDATED / NOT COMPLETE U3, P4 OR FULL SDK PARITY.
Start local HEAD:ae70e19757b5ed6d4c2417477860a7b235b77d01; previous runtime
a23c40e9030eb685c2f41fd5b4d1021db1ca9343. GLOBAL baseline
30944/33929=91.20221639305609%, exclusions68. Full independent Qiskit/PennyLane
functional replacement remains ACTIVE / INCOMPLETE, not production parity.
The actually received, corrected U3B task is preserved in
stage12_b_p4u3b_instruction_circuit_abi_execution_prompt.md.

## Real Implementation

- Public fifth positional Instruction label and num_clbits now work. Native
  definition/metadata remain explicit keywords; num_bits is a keyword alias
  with duplicate-width conflicts rejected rather than guessed. Nonnegative
  integer Instruction widths can be staged; Gate keeps its positive-width
  execution invariant. ParameterList, binding plans and owned copy paths remain.
- Instruction inverse returns Gate for supported unitary definitions, actual
  AnnotatedOperation when deferred, and typed CircuitError for unsupported
  ordinary inverse. Constructor/copy/binding of deferred objects is separate
  from unitary resolution/execution. An opaque or nonunitary annotation is not
  silently treated as a Gate. The old native inverse-name extension is now an
  explicit name= keyword; one legacy test is migrated without changing math.
- repeat creates real owned Instruction invocation objects, not flattened
  fragments or count-only wrappers. The existing Circuit/lowering/device/AD
  engine executes them; no second engine is introduced. Aggregate definition,
  cycle, parameter namespace and work checks run before repeat snapshots.
  Both unitary and classical/nonunitary definitions retain their semantics.
- Circuit compose/assign_parameters mutate and return None for inplace=True;
  non-inplace returns an independent Circuit. compose's public positional
  front/inplace order is aligned and failed mutation stays atomic. Native
  internal users call mutation then use the owner; a Pauli inplace return is
  a different protocol and is not rewritten as a Circuit call.
- Circuit inverse appends _dg on every inverse, preserves full complex phase
  and supports deferred Gate inverse objects. Circuit repeat uses its own
  observed index/count/name rules, not Instruction's positive-integral rule.
- Native IR has explicit Instruction records, including binding lineage,
  labels, quantum/classical widths and definitions. Existing legacy annotation
  records are accepted; identity is not fabricated from an operation name.
- Actual QPY v13 custom Instruction records now retain owned invocation
  identity and labels, including opaque records with no definition. Actual
  public bilateral tests verify the wire records, not just two matching native
  codecs. Shared numeric limits still span nested records/circuits. OpenQASM
  explicitly rejects unresolved Instruction references even when metadata loss
  is allowed; core executable semantics are not disposable metadata.
- Existing lowering expands Instruction references and newly exposed control
  bodies through the existing execution path. Statevector shot dispatch and
  the probability sampler lower before choosing dynamic/measurement behavior.
  Real mapped measurement/reset/legacy and structured control execute on four
  native devices. MPS100-wire and Torch/Autograd/JAX/TF derivatives are tested.

## Actual Evidence So Far

Independent prefixes are /tmp/qb-stage12b-p4u3b-* with .log/.exit receipts.

- initial-red:10failed/2passed/exit1 on unchanged runtime. Correct classification
  is7 Instruction plus3 Circuit cases, not ten different missing functions.
  first-native:12passed/exit0 after real production changes.
- Four public-only probes per actual version rerun44 Instruction,43 boundary,
  seven separate Circuit-repeat and33 extra constructor/naming/error records.
  These are observations, not completed-function counts. Public Instruction
  control/power remain ABSENT and are native extensions, not missing APIs.
- integration:2failed/1535passed/3xfailed. Both were old contracts that needed
  explicit migration: positional inverse name and eager nonunitary annotation
  construction rejection. Execution rejection remains tested, not removed.
- repeat-objects-red:5failed/exit1 proved flattened-object/IR/QPY gaps.
  reference-recovery:17passed/exit0 after actual typed invocation/codec work.
- reference-integration:1failed/1541passed/3xfailed exposed a real binding-plan
  restoration regression: validating a formal template against already bound
  owner values. The resource walker now honors the explicitly supplied formal
  namespace. lineage-recovery:197passed/2xfailed/exit0.
- public-differential241/public-differential260:95passed/exit0 each, including
  actual construction/errors, return types, repeat definitions, Circuit names,
  distinct repeat policies and actual bilateral custom Instruction QPY.
- resource-execution-red:2failed/16passed/exit1 exposed statevector shot
  dispatch before reference expansion. resource-execution-final-candidate:
  23passed/exit0 after the real sampler fix and four-framework checks.
- One new test initially mistook legacy if_else metadata for ControlBlock;
  another mistook formal owner params for evaluated gate angles. Both tests
  were corrected to exercise the actual typed-control path and inspect both
  formal values and executable angle. complete-focus initially1675passed with
  that one test error; focused-cov1676passed/3xfailed/exit0 after correction.
  This is FOCUS coverage only, never whole-package coverage.
- new-boundaries-red:4failed/7passed/exit1. Unsupported QASM references surfaced
  as downstream basis-translation FormatValidationError, not the intended
  early UnsupportedFeature. Explicit preflight now classifies that unsupported
  path before translation. No silent successful QASM output was observed.
- pre-freeze-focus:1687passed/3xfailed/5warnings/15.19s/exit0, including the
  repaired early QASM category and malformed Instruction/binding resource tests.
  The SDK-free example exits0 with real repeated objects, mapped counts0100
  and analytic Hessian8.209167119094106. It captures the derivative before an
  intentional inplace binding makes that Circuit constant.
- callsite-audit exits0: ten owned production Instruction construction calls
  use at most five positional args; Gate's explicit base initializer is also
  migrated. Eight Circuit inplace calls consume no return (expression statements);
  two return-consuming compose sites are Pauli/PauliList protocols and are not
  changed. No extracted compose/assign_parameters method attributes are found.
  This is an untyped inventory plus manual receiver review, not a proof about
  external aliases/plugins. Actual compiler/transform/device paths remain gated.
- Independent frozen R1 repeat-control probes exposed a real missing integration:
  gate control passed, but Instruction.control and Circuit.control failed on
  preserved references (probe2:2failed/1passed/exit1). R1 is invalid as final
  acceptance. Its live driver/main child were deliberately terminated for this
  confirmed new failure, not slowness or silence; no R1 FULL is reused. Circuit
  control now routes reference definitions through the existing structural Gate
  engine, preserving controlled global phase/open controls and avoiding dense
  fallback. Six controlled cases and a101-wire MPS guard are migrated into the
  controlled suite. Fresh R2 must run all29 checkpoint child gates.
- Control after actual QPY import now rebuilds width-dependent register metadata
  and avoids duplicating coherently encoded global phase. Existing structural
  RY lowering requires controlled SX and its inverse in this path. QPY writes
  the real CSXGate field and an exact three-CSX custom Gate definition for its
  inverse; no nonexistent inverse class is invented. Two actual public QPY
  read/matrix regressions cover those records. The new collection branch first
  exposed five Measurement.name errors; an explicit Measurement type guard
  repairs that regression without changing the measurement representation.
- r2-measurement-recovery:620passed/3xfailed/4warnings/3.51s/exit0.
  r2-pre-freeze-focus:1784passed/3xfailed/5warnings/30.55s/exit0, covering core,
  circuit, serialization, compiler, actual public ABI and allocation/ownership.
  These recovery runs are not substituted for the fresh frozen R2 FULL gates.

## Final Frozen R2 Verification

All29 sequential checkpoint child gates and driver terminated with exit0.
The independent final-audit receipt also exits0. These are actual R2 results,
not R1 reuse or the original28-section P4 matrix. Receipt prefix:
`/tmp/qb-stage12b-p4u3b-r2-`. The exact scoped input tree is
`483b712b7e7ecc52cbf46b473da4e136aff71738`; frozen source:
`/var/folders/c1/gs7_18954qx7td5_t_lnmf4c0000gn/T/qb-stage12b-p4t-foundation-neb3tqj9/source`.

| Child gate | Actual R2 terminal result |
| --- | --- |
| compile | exit0 |
| legal, controlled source only | 4passed, exit0 |
| focus-circuit | 127passed, exit0 |
| focus-serialization | 511passed/3xfailed/4warnings, exit0 |
| focus-compiler | 141passed, exit0 |
| focus-qml | 122passed/1warning/272.85s, exit0 |
| focus-devices | 94passed/1warning, exit0 |
| h2-aer-mps-focus | 192passed/33.07s, exit0 |
| sdkfree-full | 4544passed/1137skipped/6warnings/271.76s, exit0 |
| main-full, Qiskit2.4.1/PennyLane0.44.1 | 5900passed/5skipped/7xfailed/64warnings/1485.17s, exit0 |
| coverage-json | exit0, whole-package coverage below |
| alternate-full, Qiskit2.6.0/PennyLane0.42.3 | 5898passed/5skipped/9xfailed/52warnings/523.99s, exit0 |
| independent jax-focus | 1382passed/470skipped/1warning, exit0 |
| independent tf-focus | 1384passed/468skipped/1warning, exit0 |
| torch-autograd-focus | 437passed/1skipped/75.48s, exit0 |
| public241, broad focus including97 new ABI cases | 1849passed/3xfailed/6warnings, exit0 |
| public260, same broad focus | 1849passed/3xfailed/2warnings, exit0 |
| Seven SDK-free examples | seven independent exit0 receipts |
| Five actual import-origin probes | five independent exit0 receipts, all import frozen source |

The seven examples are native_custom_gate_interchange, native_annotated_gate,
native_gate_modifier_gradient, native_standard_gate_decomposition,
native_mutable_gate_parameters, native_standard_gate_contracts and
native_instruction_circuit_contracts. JAX0.12.0 and TF2.21.0 independent
environments have no Qiskit/PennyLane; main actually imports JAX0.7.1,
TF2.21.0, Torch2.12.0 and Autograd1.8.0. SDK-free actual import probes confirm
neither upstream SDK nor any of the four AD frameworks is installed there.
Skips and expected failures are not passes or implemented-function counts.
The public broad-focus xfails record observed public QASM custom-standard-name
definition loss; they are not claimed as successful interoperability.

GLOBAL line coverage is31253/34235=91.28961589017088%, above the actual previous
baseline30944/33929=91.20221639305609%. Missing lines2982, excluded lines68
unchanged. Coverage is not a functional-parity percentage. Selected modules:
Instruction229/255, Circuit872/933, Gate435/458, Annotation199/202,
IR455/477, QPY675/717, text exporter292/301, Statevector138/141,
sampler50/51. No Router code is in this frozen GLOBAL denominator.

Runtime identities: production `b4d057c5c1a43b8c2832454d74c2d37a7ad6ba3f`,
tests `628571daadff19bdd99ad1f945d3835e041f8d3f`,
examples `0cad5682aab1089d7f035026da639ae6b9c3f65c`.
Only documentation was updated after the frozen run. Snapshot-audit actually
exits0: all1152 controlled frozen/worktree/staged runtime blobs are identical,
exactly22 owned paths staged, no protected paths or cloud/auth/vendor artifacts.
Runtime manifest SHA256:
`e8d0c2e8cd0faa04a632c250f3cd911c877374abbb8314c87740da151babf266`.
The normal local code commit is `af66875b13593706282dac1ace0481911a2bbb27`;
actual committed tree `9ff382f452e4d7cff14b66297640e846678fad6b` equals the
audited staged tree. Actual diff-tree verifies exactly the22 owned paths.
The five committed runtime subtrees equal the tested frozen subtrees above;
scripts `4f29fa856fa38764a4d4c275e6b11ba881089eaf` and requirements
`6986a51bd059a54890a20c7808cd644eff3eb271` are unchanged. There is no push.

The dirty worktree legal run is a separate actual failure:
`r2-dirty-legal`1failed/3passed/exit1, solely the pre-existing unowned
`quantumbridge/router/core.py` absent from the migration ledger. It is neither
staged nor given invented provenance. The controlled legal4passed/exit0 does
not assert the whole dirty workspace is clean.

The R2 interim report and actual complete rendered collaborator reply were
read in the authorized conversation, Chrome AX618-736 including completed
answer controls. The report-based review agreed R1 was invalid for the real
control failure, required all fresh29 R2 gates and runtime identity checks,
and allowed only a supported local checkpoint followed by remaining U3 work.
It did not independently inspect uncommitted source or remote CI. New-SHA
remote CI remains NOT_VERIFIED; no push or hardware/cloud acceptance occurred.
Original28-section matrix remains NOT_RUN; U3B/U3/P4/full SDK stay incomplete.

## Final Report-Based Collaborator Review

The actual commit, all terminal counts, GLOBAL, snapshot/commit identities,
dirty Router distinction and residual gaps were sent to the owner-authorized
conversation "Claude 代码泄漏与应对",6a20d458-a76c-83ea-9b49-f8f0caedb3cf.
The complete rendered reply was actually read: first Chrome AX656-1158
covered checkpoint review and U3C sections0-6; after the stream recovered,
AX1234-1759 covered the remaining section6 and sections7-16. Completed-answer
controls and AX1761 "answer completed" were visible. An intermediate
connection-interrupted partial reply was not treated as the complete task.

The review accepts af66875 only as the locally validated U3B supported subset,
identifies no new confirmed outstanding blocker from the supplied report,
and explicitly states it did not independently inspect unpushed source or
remote CI. It prioritizes actual Circuit composition, ownership and typed
classical scope over more standard gate names. The complete normalized next
task is saved in `stage12_b_p4u3c_composition_classical_scope_execution_prompt.md`.
That prompt is received work, not implemented or validated U3C functionality.
Full independent Qiskit/PennyLane parity stays ACTIVE / INCOMPLETE.

## Remaining Full-Parity Contracts

- Zero-width Instruction construction is staged, but repeat still explicitly
  rejects zero-width Circuit execution. This is not an implemented zero-width
  engine. Arbitrary non-string/empty Instruction names admitted by public
  construction remain outside the native valid-name execution contract.
- Native parameter ownership/atomicity and alias/default/metadata extensions
  do not imply byte-identical inspect.signature or unsafe public mutations.
- QPY custom Instruction classical-bit invocation/base headers remain explicit
  Unsupported; native IR/real execution retain classical mapping. OpenQASM
  reference declarations and unresolved annotations are not implemented.
- Classical annotated Circuit invocation storage remains unsupported even
  though its Instruction inverse annotation can be staged. Resolution of
  nonunitary/opaque inverses correctly rejects; successful construction is
  never claimed to establish executable validity.
- Full compose wrap/copy/capture/var_remap and other public Circuit signatures,
  all remaining U3 error/return contracts, U4/U5 and original P4 joint acceptance
  remain audit/implementation work. Do not mark U3 or full SDK complete.
- Preserve unowned Studio/Router changes. No push, authentication/TLS/token,
  cloud/hardware, vendor, tag/release or history rewriting occurs in this batch.
