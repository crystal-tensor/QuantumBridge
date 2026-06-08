# Stage 6.4 P2 Review Gate v0.1

## 1. PR URL

https://github.com/crystal-tensor/QuantumBridge/pull/1

## 2. PR Head Commit

Review input head commit:

```text
0bba0cc1395866c57bf29b65215abce556b7dc46
```

Stage 6.4 adds this review document plus attribution clarifications. The merge
readiness conclusion applies to the P2 branch after those review-only updates.

## 3. PR Base

```text
main
```

## 4. Changed Files / Additions / Deletions

At Stage 6.4 review input head:

```text
163 files changed, 5973 insertions(+), 217 deletions(-)
```

The changed files are implementation, tests, examples, documentation,
requirements constraints, and CI configuration. No vendored third-party package
trees, wheels, source distributions, or `site-packages` directories were found
in the PR diff.

## 5. GitHub Actions Run

GitHub Actions run:

```text
26952159703
```

User-provided status:

```text
success
```

## 6. GitHub Actions Matrix Results

Expanded matrix passed:

- `core-only`
- `qiskit-extra`
- `pennylane-extra`
- `dev`
- `chemistry-core`
- `chemistry-extra`
- `chemistry-compatible`
- `qiskit-nature-extra`
- `algorithms-extra`
- `openfermion-extra`
- `quafu-compatible`

## 7. Track A Review

Track A covers QuantumBridge native SDK expansion:

- QASM grammar parser/exporter subset.
- Result schema v0.2 and JSON serialization.
- Compiler pass expansion and compiler reports.
- Basic noise execution path.
- PennyLane adapter and template coverage expansion.

Review conclusion:

- Scope is P2-level and does not enter P3.
- No evidence of Qiskit or PennyLane source copy was found in the PR diff.
- P1 baseline behavior remains covered by the matrix and local tests.

## 8. Track B Review

Track B covers optional upstream integration:

- Qiskit Nature API inventory and optional adapter path.
- Qiskit Algorithms API inventory and optional adapter path.
- PySCF and OpenFermion adapter smoke workflows.
- Native minimal H2 chemistry subset and installed H2 verification.
- LiH and H2O smoke workflows only.

Review conclusion:

- Qiskit Nature, Qiskit Algorithms, PySCF, and OpenFermion are optional
  dependencies.
- They are represented as adapter, passthrough, or inventory workflows.
- The PR does not claim full upstream parity or native replacement.

## 9. Dependency Compatibility Review

Stage 6.3 established:

- `qiskit-nature==0.8.0` requires NumPy 2.
- `pyquafu==0.4.5` requires `numpy<2.0.0`.
- These constraints cannot be satisfied in one verified environment.

Resolution:

- `chemistry` / `chemistry-compatible`: NumPy 2.x stack.
- `quafu` / `quafu-compatible`: NumPy `<2` stack.
- `all-optional` no longer forces the conflicting stacks into one environment.

## 10. Quafu / Chemistry Environment Split

The split is explicit in:

- `pyproject.toml`
- `requirements/constraints-chemistry.txt`
- `requirements/constraints-quafu.txt`
- `.github/workflows/test-matrix.yml`
- `scripts/run_local_matrix.sh`
- `README.md`

Review conclusion:

- The conflict is handled by environment isolation rather than dependency
  masking.
- This is merge-ready from a dependency strategy perspective.

## 11. Legal / Attribution Review

Reviewed records:

- `THIRD_PARTY_NOTICES.md`
- `docs/legal/qiskit_nature_algorithms_attribution_v0.1.md`
- `docs/legal/third_party_source_policy.md`
- `docs/migration/source_migration_ledger.md`

Stage 6.4 clarification:

- pyquafu / Quafu attribution and compatibility status are explicitly recorded.
- Qiskit Nature, Qiskit Algorithms, PySCF, and OpenFermion remain optional
  upstream dependencies.
- No source-port mode was introduced.

## 12. Unsupported Claims Review

README and review docs were checked for unsupported claims.

No unsupported positive claim was found for:

- full Qiskit replacement.
- full PennyLane replacement.
- full Qiskit Nature parity.
- full Qiskit Algorithms parity.
- official upstream endorsement.
- production-grade chemistry.
- implemented materials band-gap workflow.

README correctly states:

- H2 installed workflow is verified.
- LiH / H2O are smoke workflows.
- materials band-gap prediction is not implemented.

## 13. Remaining Risks

- PR description still contains the old dependency known-issue wording on the
  GitHub page. Automation attempted to update it but GitHub returned `403`.
- Remote Actions status was provided as successful by the user; this local
  environment cannot verify Actions through `gh` because `gh` is not logged in.
- Optional chemistry workflows remain smoke/adapter-level, not production
  chemistry.
- Qiskit Nature / Algorithms inventories are runtime inventories, not full
  parity promises.

## 14. Merge Blockers

No code or dependency blocker was found.

Administrative blocker:

- Update the PR description manually to replace the old `Known Issue` text with
  the Stage 6.3 environment-split conclusion.

Recommended replacement text:

```text
Dependency compatibility was reviewed in Stage 6.3. pyquafu and chemistry stacks require incompatible NumPy ranges, so QuantumBridge now treats them as separate optional environments:
- chemistry / chemistry-compatible: NumPy 2.x stack for Qiskit Nature, Qiskit Algorithms, PySCF, and OpenFermion
- quafu / quafu-compatible: NumPy <2 stack for pyquafu

The project does not require all optional dependencies to coexist in one environment.
```

## 15. Release Blockers

Do not publish `v0.2.0-alpha1` yet.

Release blockers:

- Merge PR #1 only after the PR description is updated.
- Confirm post-merge `main` CI remains green.
- Prepare alpha release notes that preserve optional dependency, smoke workflow,
  and non-production boundaries.
- Repeat legal / attribution review for public release wording.

## 16. Merge Recommendation

Recommendation:

```text
Merge-ready after manual PR description update.
```

No automatic merge should be performed in Stage 6.4.

## 17. v0.2.0-alpha1 Recommendation

Recommendation:

```text
Do not publish v0.2.0-alpha1 yet.
```

Alpha can be reconsidered after merge, post-merge CI, release notes, and
release review.

## 18. Conclusion

PR #1 is technically ready for P2 merge. The dependency conflict was handled by
explicit chemistry/quafu environment isolation and expanded CI. Legal and
attribution records now cover the optional upstream dependencies, including
pyquafu. The only remaining pre-merge action is a manual PR description update
because automated PR metadata update is blocked by GitHub permissions.
