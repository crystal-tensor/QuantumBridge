| ID | Title | Type | Priority | Area | Description | Acceptance Criteria |
|---|---|---|---|---|---|---|
| P2-001 | Define QASM grammar subset | Design | High | QASM parser | Write the owned grammar scope for the supported OpenQASM subset. | Grammar doc lists supported and rejected statements with examples. |
| P2-002 | Implement grammar parser spike | Engineering | High | QASM parser | Prototype a parser without copying third-party grammar code. | Spike parses P1-supported examples and rejects unsupported statements. |
| P2-003 | Add QASM diagnostic tests | Test | High | QASM parser | Add tests for malformed input and unsupported syntax. | Tests assert QuantumBridge-owned diagnostic behavior. |
| P2-004 | Decide Aer adapter dependency policy | Review | High | Aer adapter | Confirm whether Aer is optional, extra-only, and CI-safe. | Decision doc accepted by maintainers and legal reviewer. |
| P2-005 | Design minimal Aer adapter | Design | High | Aer adapter | Define supported delegation paths and result conversion. | Design has clear non-goals and no parity claims. |
| P2-006 | Add Aer installed-environment test plan | Test | Medium | Aer adapter | Plan tests that run only when Aer is installed. | Test plan distinguishes unavailable dependency from failure. |
| P2-007 | Expand PennyLane operation coverage list | Design | Medium | PennyLane coverage | Select the next safe operation subset. | Backlog lists operations, observables, and unsupported cases. |
| P2-008 | Add PennyLane template bridge plan | Design | Medium | PennyLane coverage | Define minimal template compatibility boundaries. | Plan names supported templates without claiming plugin parity. |
| P2-009 | Add compiler routing design | Design | High | Compiler | Specify routing behavior for coupling constraints. | Design includes examples, invariants, and rejected cases. |
| P2-010 | Add compiler layout design | Design | Medium | Compiler | Specify initial layout selection behavior. | Design documents deterministic behavior and metadata. |
| P2-011 | Add decomposition pass plan | Design | Medium | Compiler | Define native-gate decomposition boundary. | Plan identifies supported decompositions and equivalence tests. |
| P2-012 | Add depth reduction pass plan | Design | Medium | Compiler | Define safe local depth reduction rules. | Plan includes circuit equivalence acceptance checks. |
| P2-013 | Add two-qubit optimization pass plan | Design | Medium | Compiler | Plan safe reductions for adjacent two-qubit operations. | Plan lists exact rewrite rules and no-op cases. |
| P2-014 | Design noisy sampler execution | Design | High | Noise | Move from metadata-only noise toward real noisy sampling. | Design defines channels, ordering, seeds, and statistical tolerances. |
| P2-015 | Add noise channel behavior tests | Test | High | Noise | Test bit-flip, phase-flip, depolarizing, and readout behavior. | Tests use owned mathematical expectations and seeded runs. |
| P2-016 | Define result JSON schema | Design | High | Result schema | Create versioned result serialization schema. | Schema covers counts, probabilities, statevector, expectation, and metadata. |
| P2-017 | Add serialization compatibility tests | Test | Medium | Serialization | Add round-trip and metadata preservation tests. | Tests pass for current schema and documented legacy examples. |
| P2-018 | Replace visualization placeholders | Engineering | Low | Visualization | Complete text drawer and decide matplotlib drawer minimum. | Placeholder modules either implemented or explicitly retained with docs. |
| P2-019 | Add remote CI evidence record | CI | High | CI | Capture actual GitHub Actions matrix run URL and result. | Review doc includes successful workflow URL and commit SHA. |
| P2-020 | Add coverage gate policy | CI | Medium | Coverage | Decide whether P2 requires a coverage threshold. | Policy sets threshold or explicitly defers it. |
| P2-021 | Add source distribution check | Packaging | Medium | Packaging | Validate sdist and wheel contents before release. | Build artifacts include license/docs and exclude caches. |
| P2-022 | Complete legal review | Review | High | Legal review | Review Apache, notices, optional adapters, and attribution. | Signed review status is recorded. |
| P2-023 | Complete trademark review | Review | High | Trademark review | Review all public references to Qiskit, PennyLane, IBM, and Xanadu. | No endorsement or full-parity language remains. |
| P2-024 | Align docs for P2 entry | Docs | Medium | Docs | Update roadmap/review docs after P1 RC approval. | Docs state P2 scope and retain experimental caveats. |
| P2-025 | Add examples policy | Docs | Medium | Examples | Define examples that avoid implying full upstream compatibility. | Example list is approved and tied to supported behavior. |
| P2-026 | Add benchmark plan | Design | Low | Benchmarks | Plan small benchmarks for native simulator and adapters. | Plan defines metrics without production performance claims. |
| P2-027 | Prepare internal demo | Task | Low | Internal demo | Prepare a small P1 demo for reviewers. | Demo runs locally and states unsupported features. |
| P2-028 | Define API stability levels | Design | High | API stability | Mark stable, experimental, and placeholder APIs. | API stability table is published in docs. |
| P2-029 | Define versioning policy | Design | High | Versioning | Decide pre-release and compatibility version rules. | Versioning doc maps package versions to RC tags. |
| P2-030 | Define release process | Process | High | Release process | Document tag, CI, review, and publication steps. | Release checklist requires remote CI and human approval. |
