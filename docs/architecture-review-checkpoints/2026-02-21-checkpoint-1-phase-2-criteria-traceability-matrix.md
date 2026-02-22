# Architecture Review Checkpoint 1 - Phase 2 Criteria Traceability Matrix

Date: 2026-02-21  
Source plan: `docs/architecture-review-workplan.md` (Section 6.2, Phase 2)  
Scope: Map `CRIT-001..CRIT-071` to current repository artifacts, set applicability, and capture rationale for later compliance scoring in Phase 3.

## Applicability Summary

- `Applicable`: 55
- `Partially Applicable`: 9
- `Not Applicable`: 7

## Matrix

| CRIT | Applicability | Current-State Rationale | Evidence |
|---|---|---|---|
| CRIT-001 | Applicable | Core behavior is a reusable resolve -> validate -> deploy mechanism, not one-off hardcoded outputs. | `README.md:22`; `skills/ha-resolver/SKILL.md:17`; `skills/ha-validate/SKILL.md:49` |
| CRIT-002 | Applicable | Responsibilities are split across plugin manifest, skills, agents, hooks, and helpers. | `CLAUDE.md:14`; `CLAUDE.md:19`; `COMPONENTS.md:7` |
| CRIT-003 | Applicable | Scale paths exist via agent delegation, helper scripts, and timeout guidance. | `skills/ha-devices/SKILL.md:5`; `skills/ha-devices/SKILL.md:417`; `skills/ha-analyze/SKILL.md:58` |
| CRIT-004 | Applicable | Outputs are evidence-backed and require measured values instead of intuition-only responses. | `skills/ha-analyze/SKILL.md:10`; `skills/ha-analyze/SKILL.md:17`; `skills/ha-validate/SKILL.md:30` |
| CRIT-005 | Applicable | Versioned plugin packaging plus explicit release steps support evolution with controlled updates. | `.claude-plugin/plugin.json:3`; `.claude-plugin/marketplace.json:17`; `CLAUDE.md:143` |
| CRIT-006 | Applicable | Skill packaging follows `SKILL.md` + frontmatter contract across all skill directories. | `skills/ha-automations/SKILL.md:1`; `skills/ha-automations/SKILL.md:2`; `skills/ha-automations/SKILL.md:5` |
| CRIT-007 | Applicable | Skill descriptions include trigger cues ("what + when") for routing behavior. | `skills/ha-automations/SKILL.md:3`; `skills/ha-troubleshooting/SKILL.md:3`; `skills/ha-onboard/SKILL.md:3` |
| CRIT-008 | Applicable | Skills use progressive disclosure by linking references for detail-heavy procedures. | `skills/ha-automations/SKILL.md:11`; `skills/ha-automations/SKILL.md:48`; `skills/ha-naming/SKILL.md:12` |
| CRIT-009 | Applicable | Security controls are codified through no-secret-output rules and safety invariants. | `references/safety-invariants.md:98`; `references/safety-invariants.md:107`; `skills/ha-validate/SKILL.md:10` |
| CRIT-010 | Applicable | Workflows define fallback paths, stop conditions, and recovery options for command/API failure. | `skills/ha-troubleshooting/SKILL.md:42`; `skills/ha-deploy/SKILL.md:330`; `helpers/trace-fetch.py:102` |
| CRIT-011 | Applicable | Validation checks are explicit, but automated trigger/functional baseline tests are still missing. | `skills/ha-validate/SKILL.md:320`; `skills/ha-validate/SKILL.md:332`; `CLAUDE.md:74` |
| CRIT-012 | Partially Applicable | Current target is Claude Code only; cross-surface portability is not yet implemented. | `README.md:3`; `CLAUDE.md:9`; `docs/architecture-review-workplan.md:359` |
| CRIT-013 | Applicable | Operability loops exist through periodic analysis and naming audits for refinement. | `skills/ha-analyze/SKILL.md:224`; `skills/ha-analyze/SKILL.md:234`; `skills/ha-naming/SKILL.md:100` |
| CRIT-014 | Applicable | Most skills are concise, but two exceed the 500-line context target. | `skills/ha-config/SKILL.md:432`; `skills/ha-onboard/SKILL.md:503`; `skills/ha-devices/SKILL.md:583` |
| CRIT-015 | Applicable | Primary reference links are local and shallow (same skill directory `references/` pattern). | `skills/ha-automations/SKILL.md:48`; `skills/ha-resolver/SKILL.md:26`; `skills/ha-troubleshooting/SKILL.md:133` |
| CRIT-016 | Applicable | Complex operations are documented as sequential stages with explicit checkpoints. | `skills/ha-automations/SKILL.md:38`; `skills/ha-deploy/SKILL.md:25`; `skills/ha-naming/SKILL.md:331` |
| CRIT-017 | Applicable | Verification-first discipline is present, but no automated eval harness is yet defined. | `skills/ha-validate/SKILL.md:30`; `skills/ha-validate/SKILL.md:320`; `CLAUDE.md:74` |
| CRIT-018 | Partially Applicable | Cross-model validation is intentionally narrowed to Sonnet 4.6, reducing breadth by policy. | `docs/architecture-review-workplan.md:359`; `CLAUDE.md:74` |
| CRIT-019 | Applicable | Deterministic helper scripts are used for complex ops with explicit error handling and exits. | `helpers/area-search.py:19`; `helpers/area-search.py:33`; `helpers/trace-fetch.py:70` |
| CRIT-020 | Applicable | High-impact flows enforce validate/confirm/report gates before side effects. | `skills/ha-deploy/SKILL.md:37`; `skills/ha-deploy/SKILL.md:65`; `references/safety-invariants.md:196` |
| CRIT-021 | Partially Applicable | Runtime assumptions are explicit for local Claude Code; API/runtime variants are deferred. | `CLAUDE.md:9`; `skills/ha-onboard/SKILL.md:269`; `docs/architecture-review-workplan.md:361` |
| CRIT-022 | Not Applicable | Current architecture uses `hass-cli` commands, not MCP tool addressing. | `skills/ha-resolver/SKILL.md:5`; `docs/architecture-review-workplan.md:361` |
| CRIT-023 | Partially Applicable | Cross-platform guidance exists, but bash-centric hook/runtime assumptions remain. | `skills/ha-onboard/SKILL.md:269`; `skills/ha-onboard/SKILL.md:277`; `hooks/session-check.sh:1` |
| CRIT-024 | Applicable | UX defaults favor constrained stepwise flow (one step at a time, dry-run defaults). | `skills/ha-onboard/SKILL.md:17`; `skills/ha-apply-naming/SKILL.md:17`; `skills/ha-deploy/SKILL.md:201` |
| CRIT-025 | Applicable | Major workflows include built-in verification contracts and evidence tables. | `skills/ha-validate/SKILL.md:332`; `skills/ha-troubleshooting/SKILL.md:95`; `references/safety-invariants.md:196` |
| CRIT-026 | Applicable | Non-trivial operations are staged (check, validate, confirm, execute, recover). | `skills/ha-deploy/SKILL.md:27`; `skills/ha-deploy/SKILL.md:37`; `skills/ha-deploy/SKILL.md:328` |
| CRIT-027 | Applicable | Inputs are structured through scenario cues, environment checks, and explicit scope questions. | `skills/ha-automations/SKILL.md:19`; `skills/ha-onboard/SKILL.md:23`; `skills/ha-troubleshooting/SKILL.md:20` |
| CRIT-028 | Applicable | Context hygiene is managed via step gating and isolated agent contexts. | `skills/ha-onboard/SKILL.md:17`; `README.md:113`; `COMPONENTS.md:83` |
| CRIT-029 | Applicable | Persistent instructions are split across specialized skills/references instead of one monolith. | `CLAUDE.md:16`; `CLAUDE.md:20`; `README.md:133` |
| CRIT-030 | Applicable | Deterministic guardrails are enforced by hooks and safety-policy contracts. | `hooks/hooks.json:3`; `hooks/hooks.json:15`; `references/safety-invariants.md:130` |
| CRIT-031 | Applicable | Permission surface is constrained by per-skill allowed tools and onboarding allowlists. | `skills/ha-deploy/SKILL.md:5`; `references/settings-schema.md:35`; `references/settings-schema.md:61` |
| CRIT-032 | Applicable | Research/debug tasks are isolatable through dedicated subagents with scoped prompts. | `README.md:104`; `README.md:113`; `agents/config-debugger.md:42` |
| CRIT-033 | Applicable | Parallel/headless policy is explicitly constrained to read-only diagnostics. | `docs/architecture-review-workplan.md:360`; `agents/config-debugger.md:38`; `agents/ha-log-analyzer.md:12` |
| CRIT-034 | Applicable | Known failure modes are mitigated via fallback chains and explicit recovery paths. | `skills/ha-troubleshooting/SKILL.md:42`; `skills/ha-validate/SKILL.md:33`; `skills/ha-deploy/SKILL.md:336` |
| CRIT-035 | Partially Applicable | Plugin runtime contract is explicit, but API-surface correctness criteria are not fully in scope yet. | `README.md:3`; `CLAUDE.md:9`; `CLAUDE.md:37` |
| CRIT-036 | Partially Applicable | Release versioning exists, but no explicit managed-latest vs pinned policy by environment. | `.claude-plugin/plugin.json:3`; `.claude-plugin/marketplace.json:17`; `CHANGELOG.md:3` |
| CRIT-037 | Not Applicable | Session/container reuse policy is explicitly out of scope for the current runtime surface. | `docs/architecture-review-workplan.md:361`; `CLAUDE.md:9` |
| CRIT-038 | Applicable | Long-running operations include timeout and retry/recovery guidance. | `skills/ha-analyze/SKILL.md:58`; `references/hass-cli.md:102`; `skills/ha-deploy/SKILL.md:333` |
| CRIT-039 | Applicable | Task-shape routing exists via specialized skills and explicit "when to use / not use" sections. | `skills/ha-automations/SKILL.md:17`; `skills/ha-scenes/SKILL.md:17`; `skills/ha-troubleshooting/SKILL.md:27` |
| CRIT-040 | Applicable | Production hardening signals are strong (safety invariants, confirmation gates, validation-before-deploy). | `README.md:122`; `skills/ha-deploy/SKILL.md:11`; `skills/ha-deploy/SKILL.md:39` |
| CRIT-041 | Applicable | Structured-output policy is now set (JSON for machine artifacts, Markdown for human-facing output). | `docs/architecture-review-workplan.md:362`; `skills/ha-validate/SKILL.md:334`; `skills/ha-resolver/SKILL.md:250` |
| CRIT-042 | Applicable | Failures trigger explicit fallback or escalation paths rather than silent continuation. | `agents/ha-config-validator.md:26`; `skills/ha-apply-naming/SKILL.md:257`; `skills/ha-deploy/SKILL.md:346` |
| CRIT-043 | Applicable | Iteration and retry bounds are now explicitly defined in policy. | `docs/architecture-review-workplan.md:363`; `skills/ha-deploy/SKILL.md:333` |
| CRIT-044 | Applicable | Delegation is bounded to named agents with explicit task context and foreground execution. | `skills/ha-devices/SKILL.md:417`; `agents/device-advisor.md:38`; `agents/config-debugger.md:38` |
| CRIT-045 | Applicable | Budget controls now include retry/iteration caps and future tool-count cap policy. | `docs/architecture-review-workplan.md:363`; `docs/architecture-review-workplan.md:367` |
| CRIT-046 | Applicable | Parallelism is allowed only in safe contexts; side-effectful work remains sequential. | `docs/architecture-review-workplan.md:360`; `skills/ha-scripts/SKILL.md:36` |
| CRIT-047 | Applicable | Cost/latency concerns are recognized via timeout guidance and bounded command/turn/token policy. | `skills/ha-analyze/SKILL.md:58`; `references/hass-cli.md:100`; `docs/architecture-review-workplan.md:365` |
| CRIT-048 | Partially Applicable | Outputs preserve primary analysis evidence, but there is no dedicated citation post-processing layer. | `README.md:113`; `skills/ha-troubleshooting/SKILL.md:95` |
| CRIT-049 | Applicable | Quality model is criteria-first through explicit safety invariants and validation contracts. | `references/safety-invariants.md:3`; `skills/ha-validate/SKILL.md:320`; `docs/architecture-review-workplan.md:281` |
| CRIT-050 | Applicable | Quality checks span multiple dimensions (syntax, schema, entities, services, capability, security). | `skills/ha-validate/SKILL.md:324`; `skills/ha-validate/SKILL.md:328`; `skills/ha-validate/SKILL.md:125` |
| CRIT-051 | Applicable | Evaluation scenarios are grounded in real user task categories across generation and debugging flows. | `skills/ha-automations/SKILL.md:19`; `skills/ha-troubleshooting/SKILL.md:20`; `skills/ha-analyze/SKILL.md:32` |
| CRIT-052 | Applicable | Grading is currently manual/evidence-table based; scalable automated grading is a known gap. | `skills/ha-validate/SKILL.md:181`; `skills/ha-troubleshooting/SKILL.md:97`; `CLAUDE.md:74` |
| CRIT-053 | Applicable | Structured evaluator outputs are now policy-backed, but no dedicated LLM grader implementation yet. | `docs/architecture-review-workplan.md:362`; `CLAUDE.md:74` |
| CRIT-054 | Applicable | Throughput-oriented automated eval loops are not yet implemented, but this criterion is in-scope as a gap. | `CLAUDE.md:74`; `docs/architecture-review-workplan.md:425` |
| CRIT-055 | Applicable | Partial eval decomposition exists (checks/evidence/outcomes), but no formal harness objects yet. | `skills/ha-troubleshooting/SKILL.md:95`; `skills/ha-validate/SKILL.md:332`; `CLAUDE.md:74` |
| CRIT-056 | Applicable | Capability/regression split policy is explicitly decided and traceable. | `docs/architecture-review-workplan.md:366` |
| CRIT-057 | Applicable | Non-determinism metric policy now includes primary single-run and secondary pass@3. | `docs/architecture-review-workplan.md:364` |
| CRIT-058 | Applicable | Eval isolation baseline is explicitly defined (clean snapshot + reset state + bounded budgets). | `docs/architecture-review-workplan.md:365` |
| CRIT-059 | Applicable | Troubleshooting/validation focus on observed outcomes and evidence, not rigid procedural mimicry. | `skills/ha-troubleshooting/SKILL.md:94`; `skills/ha-troubleshooting/SKILL.md:103` |
| CRIT-060 | Applicable | Real-incident-driven suite growth is explicitly encoded in promotion policy. | `skills/ha-troubleshooting/SKILL.md:16`; `docs/architecture-review-workplan.md:366` |
| CRIT-061 | Applicable | Ops baselining is partially specified via command/turn/token budget requirements and measured reporting. | `docs/architecture-review-workplan.md:365`; `skills/ha-analyze/SKILL.md:17` |
| CRIT-062 | Applicable | Model-upgrade readiness is currently constrained by Sonnet-only scope and missing automated matrix tests. | `docs/architecture-review-workplan.md:359`; `CLAUDE.md:74` |
| CRIT-063 | Applicable | Current design already separates policy/guidance (skills/agents) from deterministic execution (`hass-cli` + helpers). | `README.md:22`; `skills/ha-resolver/SKILL.md:8`; `helpers/area-search.py:23` |
| CRIT-064 | Partially Applicable | Surface governance exists at skill/tool permissions; MCP module-filter governance is deferred. | `skills/ha-automations/SKILL.md:5`; `references/settings-schema.md:35`; `docs/architecture-review-workplan.md:367` |
| CRIT-065 | Not Applicable | MCP annotation discipline (`readOnlyHint`/`destructiveHint`) is deferred until MCP adoption. | `docs/architecture-review-workplan.md:370`; `skills/ha-resolver/SKILL.md:5` |
| CRIT-066 | Applicable | Explicit MCP tool-count budget is now defined for future adoption phases. | `docs/architecture-review-workplan.md:367` |
| CRIT-067 | Not Applicable | Multi-transport operation is intentionally out of initial scope (stdio-only if MCP is adopted). | `docs/architecture-review-workplan.md:368` |
| CRIT-068 | Not Applicable | OAuth interoperability is deferred with HTTP/SSE/OAuth transport deferral. | `docs/architecture-review-workplan.md:368` |
| CRIT-069 | Not Applicable | Protocol-native MCP error signaling is not applicable until an MCP server layer exists. | `skills/ha-resolver/SKILL.md:5`; `docs/architecture-review-workplan.md:361` |
| CRIT-070 | Not Applicable | Async operation ID/status protocol is deferred until MCP mutation tooling exists. | `docs/architecture-review-workplan.md:369` |
| CRIT-071 | Partially Applicable | Some measured operational reporting exists, but no low-overhead telemetry subsystem is implemented. | `skills/ha-analyze/SKILL.md:17`; `skills/ha-analyze/SKILL.md:58`; `CLAUDE.md:74` |

## Immediate Implications For Phase 3

1. Highest-value deep-assessment gaps are `CRIT-011`, `CRIT-017`, `CRIT-052..CRIT-055`, and `CRIT-061..CRIT-062` (evaluation and reliability infrastructure).
2. MCP-specific criteria (`CRIT-065`, `CRIT-067..CRIT-070`) are deferred by explicit policy and should be evaluated only in the Skills+MCP composition phase.
3. Context-structure debt exists for oversized skills (`CRIT-014`) and should be assessed for split/refactor impact during remediation planning.
