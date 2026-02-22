# Deferred Question Decision Proposal (Post-Checkpoint 1)

Date: 2026-02-21
Related checkpoint: `docs/architecture-review-checkpoints/2026-02-21-checkpoint-1-phase-0-1.md`
Purpose: Propose default decisions for all `Deferred` questions so Section 5 can be fully closed with explicit policy.
Status: Accepted as baseline with user-approved adjustments; canonical finalized values are captured in `docs/architecture-review-workplan.md` Section 5a.

## Proposed Defaults

| Q ID | Proposed Decision | CRIT Trace |
|---|---|---|
| Q-004 | Trigger-quality target: false-positive <= 8%, false-negative <= 10% (recall-leaning due to in-directory plugin usage context). | CRIT-007, CRIT-013 |
| Q-005 | Model scope: Sonnet 4.6 only. | CRIT-018, CRIT-062 |
| Q-010 | Parallel/headless allowed for read-only discovery and diagnostics only; any write/deploy/rollback/rename execution must remain sequential with explicit confirmation. | CRIT-033, CRIT-046 |
| Q-012 | No container/session reuse requirement for current Claude Code plugin runtime; revisit only if API/MCP runtime is introduced. | CRIT-037 |
| Q-014 | Structured output standard: JSON schema for machine-consumed artifacts, Markdown for human-facing reports; XML not required. | CRIT-041 |
| Q-015 | Hard caps: max 2 retries per external command, max 3 refinement iterations per workflow stage, then mandatory escalation to user. | CRIT-042, CRIT-043 |
| Q-016 | Acceptance metric set: single-run pass rate (primary) + pass@3 (secondary for stochastic tasks). | CRIT-057, CRIT-061 |
| Q-017 | Eval trial isolation baseline: clean workspace snapshot, reset `.claude` state, deterministic fixtures, bounded command/turn/token budgets. | CRIT-058 |
| Q-018 | Maintain separate capability and regression suites; promote tests from capability to regression after repeated stable passes and real-incident relevance. | CRIT-056 |
| Q-020 | MCP surface budget (if adopted): cap initial tool surface at 12 tools, require explicit justification for expansion. | CRIT-066 |
| Q-021 | MCP transport scope (if adopted): stdio-only in initial phase; HTTP/SSE/OAuth deferred to later phase after stability baseline. | CRIT-067, CRIT-068 |
| Q-022 | Async tracking requirement (if adopted): operations expected >10s or multi-entity mutations must expose operation ID + status polling contract. | CRIT-070 |
| Q-023 | Annotation-policy tests (if adopted): enforce as hard CI gate (`readOnly` vs destructive classification checks). | CRIT-065 |

## Why These Defaults

- They align with current plugin safety posture: explicit confirmation for side effects, evidence-first validation, and deterministic tool usage.
- They avoid over-scoping MCP concerns into the current non-MCP runtime while still setting clear adoption guardrails.
- They provide measurable policies that can be used in later Phase 2-5 assessment and roadmap work.

## Suggested Status Update Path

1. If accepted, flip these `Deferred` entries in Section 5 to `Resolved`.
2. Add one-line rationale per ID in a follow-on decision log artifact.
3. Use these defaults as constraints for CRIT compliance scoring in Phase 2+.
