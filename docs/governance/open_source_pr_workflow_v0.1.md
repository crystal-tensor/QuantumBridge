# QuantumBridge Contribution Workflow v0.1

**Version**: v0.1  
**Date**: 2026-06-09  
**Status**: Owner-directed mainline workflow with future PR option  

## 1. Current Workflow

The current owner instruction is to use direct push to `main` for active
development tasks. Direct push does not remove engineering gates. Every mainline
change must remain scoped, tested, documented, and reversible by normal git
history.

## 2. Direct-Push Gate

Before pushing `main`:

1. Sync with `git pull --ff-only origin main`.
2. Check `git status`.
3. Do not include unrelated drafts or generated dependency artifacts.
4. Keep the commit scope clear.
5. Run required local tests.
6. Commit with a descriptive message.
7. Push `main`.
8. Confirm the latest GitHub Actions `main` run is green.

## 3. Required Commit Information

Handoff reports should include:

- changed files;
- test results;
- coverage when run;
- risk notes;
- non-goals;
- whether any untracked files were intentionally left out.

## 4. Forbidden Content

Do not commit:

- tokens or credentials;
- `site-packages`;
- `wheel` artifacts;
- `dist-info`;
- `egg-info`;
- virtual environments;
- vendored third-party source code;
- release archives unless a release gate explicitly allows them.

## 5. Public Claim Policy

Do not claim:

- official endorsement by upstream projects;
- full replacement of Qiskit, PennyLane, Quafu, or QOS-UQCI;
- production parity;
- production-grade chemistry, finance, ML, optimization, experiments,
  dynamics, chip design, cloud runtime, or hardware support unless a later
  reviewed stage proves and scopes that claim.

## 6. Future PR Mode

If the owner later re-enables PR-based external collaboration, PRs should
include summary, tests, risks, non-goals, advisory/offline labels, and CI-green
status before merge. This future mode is not active under the current owner
instruction.
