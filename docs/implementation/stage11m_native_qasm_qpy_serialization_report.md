# Stage 11M Native Serialization Report

Date: 2026-10-19. Starting HEAD: `45fe338fc0f02de9c19e0af89723755952e5fc98`.
Branch: `main`; ordinary direct push authorized by the owner. Full functional
Qiskit/PennyLane replacement remains **incomplete**. This checkpoint implements
and tests executable format subsets, not complete language or SDK object parity.

## Implementation And Public API

`quantumbridge.serialization` provides `qasm2_loads/load/dumps/dump`,
`qasm3_loads/load/dumps/dump`, `qpy_loads/load/dumps/dump/get_version`,
`serialize_circuit`, `deserialize_circuit`, `convert_circuit_format`,
`validate_serialization_roundtrip`, `SerializedCircuit` and `SerializationLimits`.
File APIs accept paths and correctly typed streams. Unknown formats, versions,
instructions and unrepresentable semantics reject; they never become an empty
circuit, identity instruction, comment or fake successful result.

The source implementation has a bounded lexer, recursive grammar, typed AST,
semantic lowering and source exporter. It reuses native Circuit, Parameter AST,
ClassicalExpression, ControlBlock, IR, devices and differentiation, not SDK
execution or a second circuit model. Existing QASM entry points delegate to the
new codec; legacy import explicitly retains its permissive gate-name dialect.
Barriers and delays are actual instructions. Old tests were upgraded where
previously unsupported U3/barrier/condition behavior now actually works.

### OpenQASM 2

Supported subset: version 2.0, builtin qelib1 include, multiple named registers,
U/CX and supported standard gates, arithmetic/pi, indexed/broadcast operands,
custom gate definitions with bounded expansion, measurement/reset/barrier,
comments, full-register equality conditions and files/strings. Export emits
explicit algebraic SWAP/CSWAP definitions instead of assuming nonstandard qelib1
names exist. Unknown/opaque executable calls and recursive definitions reject,
including unused cycles and undefined gate calls.

Free parameters, nonrepresentable global phase, delay and non-downgradable
dynamic blocks reject. Custom definitions preserve executable semantics, not
the original definition-object identity or source formatting. Whole-block
snapshot semantics cannot be rewritten into repeated conditions if the body
writes the tested classical state.

### OpenQASM 3

Supported declared subsets: 3.0 and 3.1; switch requires 3.1. Typed bool, bit,
bounded uint/int, explicit float[64] input/const, assignments/casts/arithmetic,
gate parameters, gphase, delay units, lexical scopes, if/else, for, while,
switch/cases, break/continue and measurement feedback lower to actual native
runtime operations. Signed int uses width-checked two's-complement execution.
Legacy flattened branch metadata is reconstructed into structured blocks while
preserving entry snapshots, nesting and repeated block entry.

Reserved names, duplicate declarations, undefined variables, const writes,
shadowed loop-angle bindings and numeric/resource limits are checked. Runtime
gate angles outside supported bound loop parameters, runtime float arithmetic,
float[32]/fixed angle types, general arrays/functions, modifiers, defcal,
OpenPulse, extern, stretch/box and full timing algebra are unsupported.

The [standard U convention](https://openqasm.com/language/standard_library.html)
has a phase differing from U3. Default parsing preserves that exact phase.
Public Qiskit 2.4.1/2.6.0 source import/export uses the U3 convention for builtin
U; importing that dialect requires explicit `dialect="qiskit"`. Native export
uses u3 plus explicit gphase, avoiding the ambiguity. Standard-subset output is
also loaded by both public SDKs in the tests.

### Real QPY Version 13

This is actual public binary QPY, **not JSON with a QPY header**, pickle, an SDK
passthrough, a private envelope or a renamed native IR format. Native code
encodes/decodes the QISKIT header, format version, circuit count, symbolic
encoding, program payload, circuit header, registers, metadata, instruction
records/arguments/labels, numeric values, UUID parameters and arithmetic replay.

The [public protocol documentation](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qpy)
and public dump/load bytes were references. No upstream implementation or tests
were copied or vendored. Qiskit 2.4.1 reports QPY_VERSION 17, 2.6.0 reports 18;
both publicly export version 13. Format version is distinct from SDK version.

Protocol observations verified with both SDKs: circuit program tag is `q`
(some documentation still says `c`); global-phase scalars are network order,
instruction numeric payloads are little endian in v13; arithmetic replay uses
35-byte records. Reversed arithmetic opcodes are supported, along with ordinary
addition/subtraction/multiplication/division/power. Symbolic Python text is not
evaluated. UUID/name conflicts reject rather than corrupt the symbol map.

Named and multiple circuits, exact register maps, supported basic gates,
measure/reset/barrier, dt delay, numeric/symbolic global phase, shared and
nonlinear arithmetic parameters, labels and finite JSON metadata roundtrip.
Absent native names use an empty binary name; empty explicit native names
reject. Missing native UUIDs receive deterministic wire-format identities;
explicit UUIDs survive IR and binary roundtrips. Core Parameter equality remains
name-based, so full upstream identity semantics are not claimed.

QPY remains **PARTIAL**: only format version 13 is supported. Custom instruction
definitions, dynamic/standalone-classical payloads, nonempty TranspileLayout,
calibrations, parameter vectors, general symbolic functions and other versions
explicitly reject. The public v13 Delay payload drops non-dt units on reload in
the tested SDKs; native export rejects such input instead of silently turning
ns into dt. QASM3 preserves those units. Unknown instruction metadata,
non-string JSON keys/tuples, noncomputational measurements and malformed gate
signatures also reject rather than silently change meaning.

## Interchange And Preservation

Default export is lossless for the declared supported semantic subset or
rejects. Deliberate `allow_metadata_loss=True` source export emits warnings.
`metadata_policy="external"` keeps root native name/provenance/layout/schedule
and parameter UUID metadata in a separately identified sidecar, never falsely
inside a standard QPY/source field. Nested opaque metadata remains unsupported,
not silently stripped. Native IR JSON is explicitly named `ir-json`, not QPY.

Six independent parameterized Circuit -> restored native QNode comparisons
(RX/RY/RZ/shared/nonlinear/entangled Hamiltonian) verify values and both native
adjoint and parameter-shift gradients for QPY and QASM3. Python callables are not
serialized; `QNode.from_circuit` reconstructs the native parameter chain rule.
Compiler tests retain exact phase, parameter binding, directed routing,
measurement order and external layout/schedule metadata. Both formats execute
100-qubit GHZ chains using MPS with dense APIs forbidden and peak bond two;
this is not an arbitrary-entanglement efficiency claim.

Existing QOS-UQCI compatibility artifacts now retain explicit external metadata
and parse their actual source during validation. Existing Quafu source-only
transport integration explicitly opts into external metadata, while job names
remain separate transport fields. These tests use mocks/offline paths only;
they are not real cloud/hardware evidence. No Studio or Router files are changed.

## Safety And Test Evidence

Limits cover input bytes/tokens/AST/expression depth, includes, gate expansion,
circuits/instructions/registers/qubits/clbits, metadata, custom definitions,
parameter nodes and nesting. Only builtin standard includes are permitted;
no arbitrary file/network include, eval, exec, pickle or unknown-gate fallback.
Malformed binary lengths, types, flags, magic, layouts, UUID references,
padding, replay stacks, versions, truncation and trailing bytes reject.
Exponent/shift and numeric power budgets prevent hostile integer allocation.
Errors expose format/version, source line/column or byte offset, reason and
recovery information.

New tests: 27 QASM2 scenarios, 33 QASM3 scenarios including 14 independent
dynamic source programs, 18 QPY binary scenarios, security/interchange and
semantic counterexamples. Three additional legacy snapshot scenarios execute
after source roundtrip. Six gradient scenarios run in both formats. Optional
public tests provide ten bilateral QASM2, ten bilateral QASM3, ten bilateral
real-QPY scenarios plus public multicircuit/metadata/dt interoperability.

Final clean tracked-tree validation (no Studio/Router working-tree overlay):

| Environment/check | Result |
| --- | --- |
| SDK/framework-free temporary environment | 1030 passed, 117 optional skips |
| Qiskit 2.4.1 / Aer 0.17.2 / PennyLane 0.44.1 / Torch 2.12.0 / Autograd 1.8.0 | 1252 passed, 4 optional skips |
| Qiskit 2.6.0 / Aer 0.17.2 / PennyLane 0.42.3 / Autograd 1.9.1, no Torch | 1216 passed, 40 optional skips |
| New native + public serialization tests in both SDK environments | 162 passed each: 131 native and 31 public cases |
| Explicit full `--cov=quantumbridge` | 19041/21667 statements, 87.8801865%, baseline 87.5253299% |
| New lexer/parser/lowering/exporter | 100% / 97.50% / 96.70% / 97.58% |
| QPY binary / arithmetic replay / branch normalization | 95.71% / 94.57% / 93.88% |
| compileall | Exit 0 |
| Full `bash scripts/run_local_matrix.sh` | Exit 0; optional missing packages reported by the existing matrix |
| Legal + explicit offline/privacy tests | 7 passed |
| Exact new qiskit-extra command | 36 passed locally |
| Five examples in SDK-free environment | All exit 0 |

No coverage exclusion or configuration was added; 68 existing excluded lines
remain unchanged. Public QASM3 importer 0.6.0 is present in both SDK environments.
An initial pip TLS certificate failure in the alternate environment was recovered
without disabling TLS: verified PyPI wheel downloads were SHA256-checked, then
normally installed only into that temporary environment. No packages/artifacts
were added to the repository.

`pip check` passes in both temporary environments. The existing user/global
environment reports two unrelated installed-package conflicts: pyquafu 0.4.5
requires NumPy<2 whereas that environment has NumPy 2.4.6, and WeasyPrint 68.1
requires tinycss2>=1.5 whereas 1.4 is installed. Those global packages were not
modified. The pyquafu execution test explicitly skips the incompatible lane;
this checkpoint is not a pyquafu/live-hardware verification claim.

The initial regression exposed 15 legacy metadata-policy integration failures;
these were fixed at their callers, not waived by loosening lossless defaults.
Unrelated untracked/user Studio/Router content is excluded from the snapshot.

## Examples

All five run with no installed Qiskit/PennyLane/frameworks:

- `python -m examples.native_qasm2_roundtrip`
- `python -m examples.native_qasm3_dynamic_roundtrip`
- `python -m examples.native_qpy_binary_roundtrip`
- `python -m examples.native_format_interchange`
- `python -m examples.native_serialization_compiled_circuit`

The QPY example optionally also calls public SDK load/dump when available.
The CI qiskit-extra lane now installs the optional QASM3 importer and runs the
new public bilateral tests. No runtime dependency was added to pyproject.toml.

## Publication And Remaining Work

The report is authored before its containing commit; resolve its exact SHA
with `git log -1 --format=%H -- docs/implementation/stage11m_native_qasm_qpy_serialization_report.md`.
The publication receipt records that SHA, ordinary push and exact-SHA Actions
separately. Baseline Actions 39259350086 (22/22 success) belongs to Stage 11L,
not to this new work. Do not treat baseline CI as Stage 11M validation.

No force push, history rewrite, tag/release, upstream source/test vendoring,
token reading or hardware submission. Full library/SDK parity remains active:
remaining format/object branches, Aer save/set/noise, full templates/qchem/
transforms, JAX/TF/capture/higher-order autodiff and many industry functions
still require implementation and independent tests. Studio stays last.
