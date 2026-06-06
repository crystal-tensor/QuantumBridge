# Stage 7.4 PR #1 Merge Readiness v0.1

Status: conditionally merge-ready
Date: 2026-06-06

## 1. PR URL

https://github.com/crystal-tensor/QuantumBridge/pull/1

## 2. Head Commit

`4dd8c3b2002431620b83876a8221e347ac1bb6ae`

The branch is `p2/dual-track-expansion`, targeting `main`. GitHub reports the
PR as open and mergeable. The branch is seven commits ahead of and one commit
behind the current remote `main`.

## 3. CI Status

GitHub Actions run `26989790630` completed successfully. All 11 jobs passed:

- core-only
- qiskit-extra
- pennylane-extra
- dev
- chemistry-core
- chemistry-extra
- chemistry-compatible
- qiskit-nature-extra
- algorithms-extra
- openfermion-extra
- quafu-compatible

Because the branch is now one commit behind `main`, the final merge candidate
should be updated and the resulting PR/main CI should be green.

## 4. Dependency Conflict Result

Stage 6.3 established that the chemistry and pyquafu stacks require
incompatible NumPy ranges. QuantumBridge resolves this through isolated
optional environments:

- `chemistry` / `chemistry-compatible`: NumPy 2.x with Qiskit Nature, Qiskit
  Algorithms, PySCF, and OpenFermion.
- `quafu` / `quafu-compatible`: NumPy below 2 with pyquafu.

The project does not require all optional dependencies to coexist in one
environment. This is a reviewed compatibility boundary, not an unresolved
single-environment installation promise.

## 5. Legal and Attribution

The PR updates third-party notices, the migration ledger, and attribution
documents for the optional upstream packages. Those packages are described as
optional dependencies, adapters, or passthrough integrations. No capability is
represented as QuantumBridge-original when it comes from an upstream package.

## 6. Third-party Source Vendoring

No tracked Qiskit, Qiskit Nature, Qiskit Algorithms, PySCF, OpenFermion, or
pyquafu source tree, wheel, site-packages directory, virtual environment, or
installed-package metadata was found.

## 7. Unsupported Claim Review

No affirmative full-replacement, full-parity, official-endorsement,
production-chemistry, or materials-band-gap claim was found. H2 is described
as an installed workflow; LiH and H2O remain smoke workflows.

## 8. Merge Blockers

The implementation has no identified functional blocker. The following
delivery actions remain:

1. Replace the obsolete pyquafu/NumPy known-issue wording in the PR body with
   the reviewed environment-split conclusion.
2. Remove trailing whitespace from seven Markdown files on the PR branch so
   `git diff --check main...HEAD` passes.
3. Update the branch against the latest `main` and confirm the final CI result.

The GitHub connector returned HTTP 403 for metadata updates and `gh` is not
logged in, so item 1 requires an authenticated maintainer action.

Required replacement text:

```markdown
Dependency compatibility was reviewed in Stage 6.3. pyquafu and chemistry stacks require incompatible NumPy ranges, so QuantumBridge treats them as separate optional environments:
- chemistry / chemistry-compatible: NumPy 2.x stack for Qiskit Nature, Qiskit Algorithms, PySCF, and OpenFermion
- quafu / quafu-compatible: NumPy <2 stack for pyquafu

The project does not require all optional dependencies to coexist in one environment.
```

## 9. Merge Recommendation

Recommend merge after the three delivery actions above. Use **squash merge**:
the seven Stage 6 commits form one coherent P2 delivery unit and a squash keeps
the protected baseline history easier to audit.

Do not merge automatically from this review. After merge, wait for `main` CI
to become fully green before changing PR #2.

## 10. Post-merge Actions

1. Confirm the squash commit and all `main` matrix jobs are green.
2. Rebase PR #2 onto the updated `main`.
3. Review the ten files modified by both PRs, especially workflow, dependency,
   legal, schema-export, inventory, and local-matrix files.
4. Rerun the complete Stage 7 remote matrix.
5. Keep the P1 RC tag unchanged.
