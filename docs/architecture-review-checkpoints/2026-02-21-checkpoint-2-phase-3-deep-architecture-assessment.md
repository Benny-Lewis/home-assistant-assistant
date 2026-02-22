# Architecture Review Checkpoint 2 (Phase 3 Deep Assessment)

Date: 2026-02-21  
Source plan: `docs/architecture-review-workplan.md` (Section 6.2, Phase 3)  
Scope: Deep architecture assessment across boundaries, contracts, state flow, safety, reliability, observability, performance, and maintainability.

## Findings (Ordered by Severity)

### AR-F001 - Side-Effect Guardrail Drift (High)

- Domain: Contracts, Safety, Deterministic Guardrails
- Criteria: `CRIT-020`, `CRIT-030`, `CRIT-031`
- Compliance: `Non-Compliant`
- Confidence: `High`
- Risk statement: Side-effectful naming execution is documented as deterministic/no-model, but the enforcement mechanism is missing in the actual skill contract. This creates a gap where behavior can diverge from the intended mechanical execution model.
- Evidence:
  - `references/safety-invariants.md:133`
  - `CLAUDE.md:133`
  - `COMPONENTS.md:40`
  - `skills/ha-apply-naming/SKILL.md:1`
  - `skills/ha-apply-naming/SKILL.md:5`
- Recommended remediation: Add explicit `disable-model-invocation: true` to `skills/ha-apply-naming/SKILL.md` frontmatter and verify docs/contracts stay in sync.
- Estimated implementation complexity: `Low`

### AR-F002 - Deploy Validation Bypass Path (High)

- Domain: Safety, Reliability
- Criteria: `CRIT-025`, `CRIT-031`, `CRIT-034`
- Compliance: `Partially Compliant`
- Confidence: `High`
- Risk statement: Deploy flow says validation is mandatory but also exposes `--force` to skip validation, creating an unsafe bypass for high-impact operations.
- Evidence:
  - `skills/ha-deploy/SKILL.md:39`
  - `skills/ha-deploy/SKILL.md:177`
  - `references/safety-invariants.md:126`
  - `references/safety-invariants.md:196`
- Recommended remediation: Remove `--force` for normal operation, or restrict it behind an explicit advanced policy gate with stronger warnings and post-action verification requirements.
- Estimated implementation complexity: `Low`

### AR-F003 - No Automated Test/Eval Enforcement for Core Invariants (High)

- Domain: Reliability, Verification Architecture, Eval Readiness
- Criteria: `CRIT-011`, `CRIT-017`, `CRIT-054`, `CRIT-062`
- Compliance: `Non-Compliant`
- Confidence: `High`
- Risk statement: The architecture enforces many safety and quality rules in prompt text, but lacks automated tests/eval harnesses to catch regressions at scale.
- Evidence:
  - `CLAUDE.md:74`
  - `docs/architecture-review-workplan.md:364`
  - `docs/architecture-review-workplan.md:366`
- Recommended remediation: Add minimum automated coverage now (trigger tests, deploy-gate tests, invariant checks) and then extend to capability/regression suites aligned with Section 5a policy.
- Estimated implementation complexity: `Medium`

### AR-F004 - Deploy Configuration Contract Mismatch (Medium)

- Domain: Contracts, Reliability, Operability
- Criteria: `CRIT-010`, `CRIT-027`
- Compliance: `Partially Compliant`
- Confidence: `High`
- Risk statement: Deploy skill documents configurable remote/branch but executes a hardcoded push target (`origin main`), increasing failure risk for non-default repos.
- Evidence:
  - `skills/ha-deploy/SKILL.md:98`
  - `skills/ha-deploy/SKILL.md:194`
  - `skills/ha-deploy/SKILL.md:195`
- Recommended remediation: Resolve remote/branch from settings with sane defaults and surface chosen values before push.
- Estimated implementation complexity: `Low`

### AR-F005 - Runtime Breadcrumb Files Are Not Ignored (Medium)

- Domain: State Flow, Portability Hygiene, Maintainability
- Criteria: `CRIT-023`, `CRIT-028`
- Compliance: `Partially Compliant`
- Confidence: `High`
- Risk statement: Session hook writes local runtime breadcrumbs into `.claude/`, but `.gitignore` does not exclude those files. This can produce noisy or accidental machine-specific commits.
- Evidence:
  - `hooks/session-check.sh:53`
  - `hooks/session-check.sh:54`
  - `.gitignore:2`
  - `.gitignore:6`
- Recommended remediation: Add `.claude/ha-python.txt` and `.claude/ha-plugin-root.txt` (or `.claude/*.txt`) to `.gitignore`.
- Estimated implementation complexity: `Low`

### AR-F006 - Broken Skill Reference (`ha-conventions`) (Medium)

- Domain: Interface Contracts, Instruction UX
- Criteria: `CRIT-024`, `CRIT-027`
- Compliance: `Partially Compliant`
- Confidence: `High`
- Risk statement: Multiple docs reference a non-existent `ha-conventions` skill, creating routing ambiguity and potential dead-end guidance.
- Evidence:
  - `skills/ha-naming/SKILL.md:96`
  - `skills/ha-automations/references/intent-classifier.md:204`
  - `CLAUDE.md:42`
  - `CLAUDE.md:57`
- Recommended remediation: Replace references with an existing capability (`ha-naming` or `.claude/ha.conventions.json`) or add the missing skill.
- Estimated implementation complexity: `Low`

### AR-F007 - Context Governance Debt in Oversized Skills (Medium)

- Domain: Maintainability, Context Efficiency
- Criteria: `CRIT-014`, `CRIT-008`
- Compliance: `Partially Compliant`
- Confidence: `High`
- Risk statement: Two core skills exceed the stated context-governance target, increasing drift risk and reducing instruction reliability under long sessions.
- Evidence:
  - `docs/architecture-review-workplan.md:246`
  - `skills/ha-onboard/SKILL.md:503`
  - `skills/ha-devices/SKILL.md:583`
- Recommended remediation: Split `ha-onboard` and `ha-devices` into lean primary flows plus deeper `references/` files.
- Estimated implementation complexity: `Medium`

### AR-F008 - Safety-Invariant Count Inconsistency Across Canonical Docs (Low)

- Domain: Documentation Integrity, Maintainability
- Criteria: `CRIT-024`
- Compliance: `Partially Compliant`
- Confidence: `High`
- Risk statement: Canonical docs disagree on whether the system has five or six invariants. This is low risk operationally but creates avoidable confusion and drift.
- Evidence:
  - `references/safety-invariants.md:5`
  - `README.md:122`
  - `CLAUDE.md:33`
  - `CHANGELOG.md:73`
- Recommended remediation: Normalize all docs to one canonical invariant set and wording.
- Estimated implementation complexity: `Low`

## Domain Compliance Snapshot

| Domain | Status | Notes |
|---|---|---|
| Boundaries | Compliant | Layer split (skills/agents/hooks/helpers) is clear and consistent. |
| Contracts | Partially Compliant | Several contract drifts exist (`AR-F001`, `AR-F004`, `AR-F006`). |
| State Flow | Partially Compliant | Flow is explicit, but local state artifact hygiene needs tightening (`AR-F005`). |
| Safety | Partially Compliant | Strong confirmation patterns, but bypass and enforcement drift remain (`AR-F001`, `AR-F002`). |
| Reliability | Non-Compliant | Missing automated invariant/eval enforcement (`AR-F003`). |
| Observability | Partially Compliant | Evidence tables are strong; broader automated measurement remains limited (`AR-F003`). |
| Performance | Partially Compliant | Timeout/scaling guidance exists; no systematic performance baseline in automation path. |
| Maintainability | Partially Compliant | Oversized skills and doc drift increase maintenance overhead (`AR-F007`, `AR-F008`). |

## Severity Calibration (Checkpoint 2)

- Critical: `0`
- High: `3` (`AR-F001`..`AR-F003`)
- Medium: `4` (`AR-F004`..`AR-F007`)
- Low: `1` (`AR-F008`)

Checkpoint 2 outcome: severity calibration complete; ready to proceed to Phase 4 option analysis with these risks as constraints.
