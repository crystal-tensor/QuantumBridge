# Stage 5.8 Post-release Verification v0.1

Status: Post-release verification complete  
Date: 2026-06-04  

QuantumBridge v0.1.0-p1-rc1 remains a P1 release candidate. This verification
does not start P2 implementation and does not add SDK functionality.

## 1. Release URL

- Release URL: `https://github.com/crystal-tensor/QuantumBridge/releases/tag/v0.1.0-p1-rc1`
- GitHub web page status: release page is reachable and renders the P1 RC1
  release notes.
- Verification note: unauthenticated GitHub REST API requests were rate-limited
  during this check, so release metadata was verified through the GitHub web
  release page plus Git tag state.

## 2. Tag

- Tag: `v0.1.0-p1-rc1`
- Remote tag status: present on `origin`
- Tag object: `77249853a215f2535f0dc46ed8e263100b4734a5`
- Tag type: annotated tag

## 3. Tag Commit

- Tag commit: `bbd4bbca5c5a04ad009504874b14c8e9387b52c0`
- Short SHA: `bbd4bbc`
- Commit message: `docs: prepare remote CI verification for P1 RC`

## 4. Release Type

- Release type: pre-release
- Production/latest release: no production release is approved by this check
- Release notes warning: states that this is not production ready

## 5. Release Notes Consistency

Release notes file:

- `docs/release_notes/v0.1.0-p1-rc1.md`

The GitHub release page renders the same P1 RC title and release-candidate
positioning from the repository release-notes file:

- `QuantumBridge v0.1.0-p1-rc1`
- P1 release candidate, not production release
- optional Qiskit adapter status
- optional PennyLane adapter status
- matrix status
- coverage summary
- known limitations
- legal / attribution notice
- next P2 roadmap section

## 6. CI Result

P1 RC CI source:

- GitHub Actions run id: `26938623406`
- Run URL: `https://github.com/crystal-tensor/QuantumBridge/actions/runs/26938623406`

Matrix result:

| Matrix profile | Result |
| --- | --- |
| `core-only` | success |
| `qiskit-extra` | success |
| `pennylane-extra` | success |
| `dev` | success |

## 7. Current Main Status

- `origin/main` before this Stage 5.8 verification document:
  `c44b960391ba94536e7cf5f227c2a731db01a7cb`
- Main delta after `v0.1.0-p1-rc1`: release notes and release freeze
  documentation only
- README claim check: README explicitly says QuantumBridge does not claim full
  feature parity or full replacement coverage
- P2 implementation check: no P2 SDK code was added to `main`
- Stage 5.8 document status: this document is a post-release verification
  record added after the P1 RC freeze.

## 8. Current `p2/planning` Status

- `origin/p2/planning`: `72d47666594b970c5f10e14e6b1c43d1a7afc213`
- Branch content relative to `origin/main`: `docs/roadmap/p2_start_plan_v0.1.md`
- P2 planning branch status: present
- P2 implementation status: not started

## 9. P2 Planning Review Permission

P2 planning review may begin. The planning review should focus on issue scope,
owners, risk ranking, and review gates.

## 10. P2 Implementation Permission

P2 implementation should not begin yet. Implementation requires explicit
approval after P2 planning review and must happen on P2 branches without
mutating the P1 RC tag.

## 11. Conclusion

Post-release verification confirms that the P1 RC tag exists, the pre-release
page exists, the documented P1 RC CI matrix passed, README does not claim full
feature parity, `main` has not entered P2 code development, and the
`p2/planning` branch exists for planning-only work.
