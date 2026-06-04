# QuantumBridge MVP Development Plan v0.1

Status: Draft  
Date: 2026-06-04  
Source basis: Stage-one functional specification and stage-two MVP design documents.  

This document is a stage-three planning artifact. It contains no SDK implementation code.

## 1. Development principles for stage three

- Implementation team may begin coding only from approved QuantumBridge design documents and allowed public mathematical references.
- No contributor may view, download, copy, or adapt Qiskit or PennyLane source code, tests, comments, examples, error messages, or documentation prose.
- Every source file must include the required clean-room header.
- Every implementation task must have a task record and clean-room source basis.
- Every test must cite a behavior-test-plan item or independent mathematical basis.
- Implementation must not add broader features opportunistically.

## 2. Recommended implementation order

1. Repository and governance setup.
2. Core errors, parameters, operations, measurements, and circuit model.
3. QuantumBridge IR conversion.
4. Gate mathematics and statevector device.
5. Result object and serialization.
6. Shot sampler.
7. Observables and Hamiltonian expectation.
8. Parameter-shift gradient.
9. Optimizer, VQE, and QAOA.
10. OpenQASM export.
11. Full behavior test pass and clean-room audit.

## 3. Task breakdown

### T3-01: Repository setup

Input documents:

- `functional_spec_v0.1.md`
- `mvp_scope_v0.1.md`
- `clean_room_audit_report_v0.1.md`
- `contributor_clean_room_attestation.md`

Deliverables:

- Package metadata design.
- Test tooling decision.
- License selection or license placeholder pending owner decision.
- Source tree skeleton only when coding phase is approved.

Acceptance criteria:

- No implementation behavior is added before task approval.
- Clean-room headers are defined.
- Contributor attestation process is ready.

Clean-room risks:

- Pulling dependency examples or generated project templates that include source patterns.

Coding allowed in stage three:

- Yes, after project owner approves stage-three start.

### T3-02: Core model

Input documents:

- `api_contract_v0.1.md`
- `mvp_architecture_v0.1.md`
- `mvp_scope_v0.1.md`

Deliverables:

- Circuit, Parameter, Operation, Measurement, and QuantumBridge-authored error model.
- Validation for wire bounds, arity, parameter binding, and measurement mapping.

Acceptance criteria:

- Construction behavior matches API contract.
- No simulator math is required in this task.
- Unit tests cover independent construction scenarios.

Clean-room risks:

- Accidentally copying third-party class names beyond generic terms.
- Accidentally copying error message wording.

Coding allowed in stage three:

- Yes.

### T3-03: QuantumBridge IR

Input documents:

- `ir_design_v0.1.md`
- `api_contract_v0.1.md`

Deliverables:

- Circuit-to-IR conversion for MVP fields.
- Serialization-ready IR representation.
- Validation of supported IR records.

Acceptance criteria:

- IR can represent gates, parameters, measurements, observables, shots, and metadata defined in MVP.
- IR serialization follows the design draft or documented refinement.
- Unsupported records fail clearly.

Clean-room risks:

- Mirroring an existing SDK IR or graph model.
- Copying external serialization examples.

Coding allowed in stage three:

- Yes.

### T3-04: Gate mathematics and statevector simulator

Input documents:

- `simulator_design_v0.1.md`
- `behavior_test_plan_v0.1.md`

Deliverables:

- Standard gate matrix behavior for MVP gates.
- Statevector evolution for supported one- and two-qubit gates.
- Custom unitary validation.

Acceptance criteria:

- T01, T02, T03 exact probability portion, and related gate tests pass.
- Numeric tolerances are documented.

Clean-room risks:

- Copying matrix tables, comments, or implementation snippets from external SDKs.
- Using external SDKs as test oracles.

Coding allowed in stage three:

- Yes, using public textbook mathematics and design notes.

### T3-05: Result object and serialization

Input documents:

- `api_contract_v0.1.md`
- `simulator_design_v0.1.md`
- `behavior_test_plan_v0.1.md`

Deliverables:

- Result container for statevector, probabilities, counts, expectations, metadata, and trace.
- Dictionary and JSON-compatible serialization contract.

Acceptance criteria:

- T14 passes.
- Serialization of complex amplitudes is deterministic and documented.

Clean-room risks:

- Copying serialization layouts from another project.

Coding allowed in stage three:

- Yes.

### T3-06: Shot sampler

Input documents:

- `simulator_design_v0.1.md`
- `behavior_test_plan_v0.1.md`

Deliverables:

- Seeded finite-shot sampler.
- Counts and empirical probabilities.

Acceptance criteria:

- T03 sampling portion, T06, and T07 pass.
- Counts sum exactly to shots.

Clean-room risks:

- Brittle tests based on another project's random output.

Coding allowed in stage three:

- Yes.

### T3-07: Observables and Hamiltonian expectation

Input documents:

- `simulator_design_v0.1.md`
- `algorithm_design_v0.1.md`
- `behavior_test_plan_v0.1.md`

Deliverables:

- Identity, PauliX, PauliY, PauliZ, Pauli-word, and Hamiltonian contracts.
- Exact expectation evaluation on statevectors.

Acceptance criteria:

- T04 and T08 pass.
- Hamiltonian expectation is linear in term weights.

Clean-room risks:

- Copying observable composition API from an existing SDK.

Coding allowed in stage three:

- Yes.

### T3-08: Parameter-shift gradient

Input documents:

- `gradient_design_v0.1.md`
- `behavior_test_plan_v0.1.md`

Deliverables:

- Parameter-shift gradient for RX, RY, and RZ expectation objectives.
- Unsupported-gradient diagnostics.

Acceptance criteria:

- T05 and T16 pass.
- Gradient metadata records method and evaluated parameters.

Clean-room risks:

- Copying gradient tape or transform architecture from another project.
- Copying error wording.

Coding allowed in stage three:

- Yes.

### T3-09: Optimizer and VQE

Input documents:

- `algorithm_design_v0.1.md`
- `gradient_design_v0.1.md`
- `behavior_test_plan_v0.1.md`

Deliverables:

- Simple gradient descent optimizer.
- VQE orchestration contract.
- Trace and callback support.

Acceptance criteria:

- T09 passes.
- Result contains final energy, final parameters, trace, and stop reason.

Clean-room risks:

- Copying tutorial VQE examples.
- Making convergence tests too dependent on hidden implementation details.

Coding allowed in stage three:

- Yes.

### T3-10: QAOA

Input documents:

- `algorithm_design_v0.1.md`
- `gradient_design_v0.1.md`
- `behavior_test_plan_v0.1.md`

Deliverables:

- Small unweighted MaxCut cost construction.
- QAOA objective and result contract.
- Trace and callback support.

Acceptance criteria:

- T10 and T11 pass.
- Result metadata states objective sign convention.

Clean-room risks:

- Copying QAOA tutorial circuits or parameter examples.
- Ambiguous bit-order convention.

Coding allowed in stage three:

- Yes.

### T3-11: OpenQASM export

Input documents:

- `ir_design_v0.1.md`
- `api_contract_v0.1.md`
- `behavior_test_plan_v0.1.md`

Deliverables:

- Export supported MVP subset.
- Reject unsupported operations safely.

Acceptance criteria:

- T12 and T13 pass.
- Export never silently drops unsupported instructions.

Clean-room risks:

- Copying exporter implementation or exact diagnostics from another SDK.
- Overclaiming OpenQASM support.

Coding allowed in stage three:

- Yes, using public OpenQASM specification concepts only.

### T3-12: Clean-room audit and release candidate

Input documents:

- `clean_room_stage2_review.md`
- `clean_room_audit_report_v0.1.md`
- `clean_room_review_checklist.md`

Deliverables:

- Completed stage-three audit.
- Dependency license inventory.
- Source and documentation review.
- Release recommendation.

Acceptance criteria:

- No unresolved high-severity clean-room findings.
- Human review completed.
- Public release is blocked until legal review if required by project owner.

Clean-room risks:

- Missing contributor attestations.
- Undocumented dependency license obligations.

Coding allowed in stage three:

- No new feature coding; review and remediation only.

## 4. Task start gates

Before coding begins:

- Stage-two documents must be accepted by project owner.
- Contributors must complete clean-room attestation.
- Implementation team must confirm they will not use prohibited sources.
- Test team must commit to behavior-test provenance rules.

Before merge or release candidate:

- Tests must map to behavior test plan IDs.
- Source headers must be present.
- Audit checklist must be completed.

## 5. Stage-three recommendation

This plan recommends entering stage-three implementation only after:

- `clean_room_stage2_review.md` is accepted.
- A project license decision is made or a release-blocking license placeholder is recorded.
- Human clean-room lead approves the design documents.

