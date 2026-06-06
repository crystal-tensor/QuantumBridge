# Stage 7.4 PR Order and Merge Readiness Report

Status: review complete, no merge performed
Date: 2026-06-06

## 1. PR #1 Status

PR #1 is open and GitHub reports it as mergeable. Its head is
`4dd8c3b2002431620b83876a8221e347ac1bb6ae`; CI run `26989790630` passed all
11 jobs. Stage 6.3 resolved the pyquafu/chemistry NumPy incompatibility by
separating optional environments.

## 2. PR #1 Merge Recommendation

Conditionally yes. Prefer squash merge after its metadata and Markdown
formatting are corrected, the branch is updated against `main`, and final CI
is green. No automatic merge was performed.

## 3. PR #1 Manual Actions

1. Authenticate GitHub and replace the obsolete known-issue paragraph with the
   reviewed environment-split wording in
   `docs/review/stage7_4_pr1_merge_readiness_v0.1.md`.
2. Clean trailing whitespace in the seven files reported by
   `git diff --check origin/main...origin/p2/dual-track-expansion`.
3. Update the branch against the latest `main`.
4. Confirm PR and post-merge `main` CI are green.

## 4. PR #2 Status

PR #2 is open and mergeable at reviewed head
`5f4510075439940dd27e4b7ae14e5a2b83d6d0de`. Latest reviewed CI run
`27054066563` passed the 17-job matrix. Local verification reproduced
150 passed, 3 skipped, and 91% coverage.

## 5. PR #2 Merge Recommendation

No, not now. PR #1 must merge first.

## 6. PR #2 Rebase Requirement

Yes. PR #2 overlaps PR #1 in ten workflow, dependency, attribution, schema,
inventory, and local-matrix files. Rebase after PR #1 and resolve those files
under review before rerunning the complete matrix.

## 7. PR #2 Metadata

The remote title/body still describe an older Stage 7.0 state. The GitHub
connector returned HTTP 403 and `gh auth status` reports no authenticated host,
so the metadata could not be changed automatically. The exact replacement
title/body is recorded in
`docs/review/stage7_4_pr2_merge_readiness_v0.1.md`.

## 8. Metal Status

Metal remains advisory and unsupported for executable integration. Local
Python 3.12 installation failed. CI package installation succeeded under
Python 3.11, but the real upstream import failed on the legacy GUI/NumPy ABI
stack. The green advisory job validates failure reporting, not Metal execution,
EM simulation, or fabrication.

## 9. UI and OpenClaw Draft Status

No untracked UI/OpenClaw drafts were found. The following 11 documents are
already tracked in PR #2 but are outside the ecosystem merge scope:

- `2026-06-06_quantumbridge_stage7_review.md`
- `docs/compat/matrix/openclaw_ecosystem_coverage_master_matrix.md`
- `docs/review/2026-06-06_stage7_2_review_preparation.md`
- `docs/review/codex_next_prompt_2026-06-06.md`
- `docs/review/openclaw_review_stage7_2_final_2026-06-06.md`
- `docs/review/stage7_2_review_preparation_v0.1.md`
- `docs/roadmap/openclaw_issue_backlog.md`
- `docs/ui/quantumbridge_studio_api_contract_v0.1.md`
- `docs/ui/quantumbridge_studio_product_spec_v0.1.md`
- `docs/ui/quantumbridge_studio_roadmap_v0.1.md`
- `docs/ui/quantumbridge_studio_wireframe_plan_v0.1.md`

Do not delete them. Move them to a dedicated `p3/ui-product-planning` branch
before PR #2 is merged, or obtain explicit scope approval.

## 10. Diff-check Result

Initial `git diff --check origin/main...HEAD` reported trailing whitespace in
27 Markdown files. The whitespace was removed mechanically without semantic
changes. The worktree comparison against `origin/main` now passes. After the
cleanup is committed, rerun the exact `origin/main...HEAD` form.

PR #1 independently still fails diff-check in seven Markdown files and needs a
small cleanup commit on its own branch.

## 11. Test Results

- `python3 -m pytest -q -rs`: 150 passed, 3 skipped in 3.42 seconds.
- `python3 -m pytest --cov=quantumbridge`: 150 passed, 3 skipped; 91% coverage.
- `bash scripts/run_local_matrix.sh`: completed successfully in an isolated
  temporary worktree.
- Local matrix default lane: 138 passed, 15 optional-dependency skips.
- Qiskit, PennyLane, Aer, PennyLane-full, ecosystem-inventory, and dev lanes
  passed. Extras absent from the default environment were reported as not
  executed; their installed-environment evidence remains the Stage 7.2
  isolated verification and remote matrix.

## 12. Release Recommendation

Do not publish `v0.3.0` or an ecosystem alpha release. No tag or release was
created, and the P1 RC tag was not modified.

## 13. Next Owner Actions

1. Clean and update PR #1, then squash merge it.
2. Wait for green `main` CI.
3. Move the 11 UI/OpenClaw documents to `p3/ui-product-planning`.
4. Rebase PR #2 and review its ten overlapping files.
5. Apply the prepared PR #2 title/body through an authenticated GitHub session.
6. Push the final PR #2 head and require all non-advisory matrix jobs to pass.
7. Conduct final Stage 7 scope/legal review before considering merge.
