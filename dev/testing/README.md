# Eval Harness Bootstrap

This directory contains the initial AR-F003 deterministic eval harness.

## Goals

- Enforce high-risk safety and contract invariants as executable checks.
- Separate `capability` and `regression` suites.
- Track both:
  - single-run pass rate (primary)
  - pass@3 (secondary)

## Layout

- `dev/testing/scripts/eval-harness.ps1`
  - Runner for all eval suites.
- `dev/testing/evals/capability/*.json`
  - Capability checks for active core flows.
- `dev/testing/evals/regression/*.json`
  - Regression checks seeded from reviewed incident findings.

## Check Types

- `path` checks assert file contents contain or omit specific strings.
- `command` checks run a shell command from the repository root and assert against stdout using the same `contains` / `not_contains` fields.

## Run Locally

```powershell
powershell -ExecutionPolicy Bypass -File dev/testing/scripts/eval-harness.ps1 -Suite all -Passes 3
```

Run one suite:

```powershell
powershell -ExecutionPolicy Bypass -File dev/testing/scripts/eval-harness.ps1 -Suite capability -Passes 3
```

Write a JSON report:

```powershell
powershell -ExecutionPolicy Bypass -File dev/testing/scripts/eval-harness.ps1 -Suite all -Passes 3 -ReportPath C:\Temp\ha-eval-report.json
```

## Current Scope

Bootstrap checks cover:

- side-effect contract enforcement (`ha-apply-naming`)
- deploy validation gate and no bypass flag
- deploy remote/branch settings contract
- breadcrumb artifact ignore hygiene
- canonical safety invariant wording/count consistency
- broken `ha-conventions` reference regression checks

This is an intentionally minimal baseline for AR-F003. It is designed to expand with structured behavioral evals next.
