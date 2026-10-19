# Stage 11M Serialization Gap Audit

Starting HEAD: `45fe338fc0f02de9c19e0af89723755952e5fc98`, 2026-10-19.
The preceding goal turn made verified progress: native compiler commit published,
exact-SHA Actions 39259350086 succeeded with 22/22 jobs. That is not Stage 11M CI.

## Existing Evidence

1. `quantumbridge/qasm/` contains a genuine native lexer, recursive parser,
   small AST, visitor, importer and exporter, not an upstream passthrough.
2. The supported source language is a narrow OpenQASM 2.0 subset: qelib1,
   multiple registers, bound basic gates/rotations, indexed and whole-register
   measurements, pi arithmetic and barriers. Exporter and parser gate sets
   differ, so not every exported instruction currently roundtrips.
3. Public entry points operate on strings only. File/stream APIs are absent.
4. Existing importer discards Barrier AST nodes. Exporter writes delay as a
   comment and omits Circuit.global_phase, creating silent-loss risks.
5. Parameters must be bound to reals for export. Source expressions become
   numeric values; free typed native parameter AST preservation is absent.
6. Custom gate/opaque declarations and conventional register conditions are
   not parsed. Export of conditions rejects; no complete QASM3 language exists.
7. Register names/maps are local parser data, not retained as a circuit
   interchange contract. Classical runtime variables and control blocks exist
   natively (Stage 11J), but their source-language import/export does not.
8. Circuit/IRProgram/ControlBlock JSON stores executable native arithmetic and
   typed classical ASTs. This is QuantumBridge IR JSON, not QPY or OpenQASM.
9. No QPY module or binary protocol implementation exists at this baseline.
10. QOS-UQCI's compatibility artifact embeds the same limited QASM2 string and
    labels itself offline. Its validation checks the format/header, not full
    parsing or execution, and is not interoperability proof.
11. The core parity ledger repeats obsolete pre-11K/11L descriptions below
    current evidence tables. Reconciliation must preserve historical reports
    while providing a single current status view.

## Protocol Choice And Acceptance

Public constants in Qiskit 2.4.1 report QPY_VERSION=17 and minimum export=13;
Qiskit 2.6.0 reports 18 and minimum=13. Version 13 is therefore the initial
common, explicitly versioned target, using native operation-replay symbolic
encoding, not unsafe serialized symbolic Python text. Public specification and
public dump/load oracle bytes are the evidence, never installed implementation
or tests. Some live documentation program discriminator wording differs from
actual public version-13 files; both real SDK readers/writers must be tested.

Native QPY must contain actual versioned registers/instructions/parameter data,
not JSON after a magic header. Unsupported objects/versions reject explicitly.
QASM2 cannot encode every native phase/control object; default export must be
lossless or reject. QASM3 needs real typed source execution and lexical scope.
Format limits and include allowlists apply even with strict=False. No parsing
may execute code or read arbitrary includes. Hardware/token access is excluded.

## Sources

- [QPY public format](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qpy)
- [OpenQASM specification](https://openqasm.com/)
- [Public QASM2 API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qasm2)
- [Public QASM3 API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qasm3)

Full Qiskit/PennyLane replacement remains incomplete. Stage 11M evidence must
be recorded independently for each format, version and supported object type.
