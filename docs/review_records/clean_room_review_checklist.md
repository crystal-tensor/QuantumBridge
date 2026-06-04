# Clean-room Review Checklist

Review ID: REVIEW-TBD  
Date: TBD  
Reviewer: TBD  
Contribution: TBD  

## Source and Text Review

- [ ] Contributor attestation is present.
- [ ] Changed files include required clean-room headers where applicable.
- [ ] No prohibited source code appears in the contribution.
- [ ] No third-party tests, fixtures, comments, or error messages were copied.
- [ ] Documentation prose is independently written.
- [ ] Examples are newly authored for QuantumBridge.

## Architecture and API Review

- [ ] Public names use generic domain terminology or have written justification.
- [ ] Module layout follows QuantumBridge design records.
- [ ] Error classes and messages are QuantumBridge-authored.
- [ ] No third-party internal architecture is mirrored.

## Behavior and Test Review

- [ ] Tests trace to math, public standards, user scenarios, or QuantumBridge specs.
- [ ] Tests do not assert copied third-party error strings.
- [ ] Numerical tolerances are explained where needed.
- [ ] Edge cases are covered for the changed behavior.

## License and Release Review

- [ ] New dependencies are listed.
- [ ] Dependency licenses are acceptable or flagged.
- [ ] Trademark-sensitive text is factual and limited.
- [ ] Patent-sensitive features are flagged for legal review when needed.

## Decision

Decision: Pending  
Required follow-up: TBD
