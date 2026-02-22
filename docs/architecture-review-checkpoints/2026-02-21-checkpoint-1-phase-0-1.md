# Architecture Review Checkpoint 1 (Phase 0 + Phase 1)

Date: 2026-02-21
Source plan: `docs/architecture-review-workplan.md` (Section 6.2 Phase 0 and Phase 1)
Scope: Execute assumptions calibration and current-state architecture inventory without implementation changes.

## Current State Summary

- The reviewed system is a Claude Code plugin architecture, not an MCP server implementation.
- Core composition is: plugin metadata, skills, agents, hooks, helpers, and shared references.
- Deterministic Home Assistant interaction is implemented through `hass-cli` and local helper scripts.
- High-impact operations (deploy, rollback, naming execution) are human-gated with explicit confirmation and evidence-oriented reporting.

Primary evidence:
- `README.md:3`
- `CLAUDE.md:9`
- `CLAUDE.md:16`
- `CLAUDE.md:17`
- `CLAUDE.md:19`
- `skills/ha-resolver/SKILL.md:5`
- `skills/ha-deploy/SKILL.md:10`

## Phase 0 Output: Q-001..Q-023 Triage

Legend:
- `Resolved`: answer inferred from current architecture and explicit repo contracts.
- `Deferred`: missing policy decision or target-state decision not encoded in current repo.

| ID | Status | Triage Rationale | Primary CRIT Mapping | Evidence |
|---|---|---|---|---|
| Q-001 | Resolved | Non-negotiable behavior is defined by safety invariants (capability checks, no semantic substitution, safe editing, no secret output, explicit deploy confirmation, evidence tables). | CRIT-001, CRIT-002, CRIT-020, CRIT-031 | `references/safety-invariants.md:7`, `references/safety-invariants.md:124`, `references/safety-invariants.md:196` |
| Q-002 | Resolved | Primary scaling axis in current design is reliability/safety correctness, not throughput. | CRIT-003, CRIT-010, CRIT-034, CRIT-061 | `skills/ha-validate/SKILL.md:30`, `skills/ha-deploy/SKILL.md:12` |
| Q-003 | Resolved | Primary deployment surface is Claude Code plugin runtime. | CRIT-012, CRIT-021, CRIT-035 | `README.md:3`, `CLAUDE.md:9` |
| Q-004 | Deferred | No numeric trigger false-positive/false-negative threshold policy is specified. | CRIT-007, CRIT-013 | `skills/ha-automations/SKILL.md:3`, `skills/ha-naming/SKILL.md:3` |
| Q-005 | Deferred | No explicit model acceptance matrix exists; agents inherit model and no automated matrix tests exist. | CRIT-018, CRIT-062 | `agents/config-debugger.md:32`, `CLAUDE.md:74` |
| Q-006 | Resolved | Current architecture assumes Claude Code local runtime with Bash, env vars, and local tools. | CRIT-021, CRIT-035 | `skills/ha-resolver/SKILL.md:5`, `hooks/session-check.sh:19` |
| Q-007 | Resolved | High-stakes flows requiring plan/validate/execute/verify controls: deploy/rollback and naming execution. | CRIT-020, CRIT-025, CRIT-031 | `skills/ha-deploy/SKILL.md:10`, `skills/ha-apply-naming/SKILL.md:13` |
| Q-008 | Resolved | Allowed autonomy is human-gated for side effects; read-only diagnostics are autonomous within tool limits. | CRIT-031, CRIT-033 | `skills/ha-deploy/SKILL.md:13`, `references/safety-invariants.md:126` |
| Q-009 | Resolved | Minimum verification evidence requires ran-vs-skipped reporting and pre-deploy validation gate. | CRIT-011, CRIT-025 | `skills/ha-validate/SKILL.md:183`, `skills/ha-deploy/SKILL.md:39` |
| Q-010 | Deferred | Background execution constraint is explicit, but broader parallel/headless policy boundaries are not codified globally. | CRIT-033, CRIT-046 | `agents/config-debugger.md:38`, `skills/ha-devices/SKILL.md:5` |
| Q-011 | Resolved | Version pinning exists at plugin package level; broader skill/tool versioning policy remains implicit. | CRIT-036 | `.claude-plugin/plugin.json:3`, `.claude-plugin/marketplace.json:17` |
| Q-012 | Deferred | No container/session reuse contract exists for this plugin runtime architecture. | CRIT-037 | `CLAUDE.md:9`, `hooks/session-check.sh:53` |
| Q-013 | Resolved | Pattern in scope is direct skill execution with targeted subagent delegation, not orchestrator/evaluator-loop architecture. | CRIT-039, CRIT-044 | `skills/ha-devices/SKILL.md:417`, `skills/ha-troubleshooting/SKILL.md:56` |
| Q-014 | Deferred | No standardized machine-parseable contract (JSON schema/XML) is defined for major outputs. | CRIT-041 | `skills/ha-validate/SKILL.md:340` |
| Q-015 | Deferred | No hard global caps for retries/iterations and escalation are formally defined. | CRIT-042, CRIT-043 | `skills/ha-deploy/SKILL.md:333`, `skills/ha-apply-naming/SKILL.md:264` |
| Q-016 | Deferred | Reliability acceptance metric (single-run/pass@k/consistency) is not defined. | CRIT-057, CRIT-061 | `CLAUDE.md:74` |
| Q-017 | Deferred | Trial isolation requirements for an eval harness are not defined. | CRIT-058 | `CLAUDE.md:74` |
| Q-018 | Deferred | Capability vs regression suite lifecycle policy is not defined. | CRIT-056 | `CLAUDE.md:74` |
| Q-019 | Resolved | Current repo keeps deterministic HA execution in skills/agents via `hass-cli`; no MCP tool layer is implemented here. | CRIT-063 | `skills/ha-resolver/SKILL.md:5`, `skills/ha-automations/SKILL.md:5` |
| Q-020 | Deferred | No MCP tool-surface budget is applicable/defined in current repo state. | CRIT-066 | `skills/ha-resolver/SKILL.md:5` |
| Q-021 | Deferred | Transport scope (stdio/http/sse/oauth) is an MCP decision not defined in this plugin state. | CRIT-067, CRIT-068 | `skills/ha-resolver/SKILL.md:5` |
| Q-022 | Deferred | No explicit async mutation tracking/status polling contract is defined for a future MCP surface. | CRIT-070 | `helpers/trace-fetch.py:132` |
| Q-023 | Deferred | No CI quality gate for annotation-policy tests exists in current state. | CRIT-065 | `CLAUDE.md:74` |

## Phase 1 Output: Architecture Boundary Map

| Boundary | Current-State Contract | Evidence |
|---|---|---|
| Package boundary | Plugin metadata and distribution descriptors define the installable unit. | `.claude-plugin/plugin.json:2`, `.claude-plugin/marketplace.json:2` |
| Skill boundary | Skill frontmatter defines invocation and tool permissions (`user-invocable`, `allowed-tools`). | `skills/ha-automations/SKILL.md:4`, `skills/ha-automations/SKILL.md:5` |
| Infrastructure skill boundary | `ha-resolver` is non-user-invocable and acts as shared deterministic resolution module. | `skills/ha-resolver/SKILL.md:4`, `skills/ha-resolver/SKILL.md:8` |
| Agent boundary | Agents are separate prompts with optional preloaded skills and explicit foreground-only constraint. | `agents/config-debugger.md:35`, `agents/config-debugger.md:38` |
| Hook boundary | Session and post-tool hooks enforce deterministic startup checks and workflow reminders. | `hooks/hooks.json:3`, `hooks/hooks.json:15` |
| Runtime boundary | Tooling stack is Bash + `hass-cli` + local Python helpers; no MCP server runtime in this repo. | `skills/ha-resolver/SKILL.md:5`, `helpers/area-search.py:23`, `helpers/trace-fetch.py:45` |
| Local state boundary | Runtime breadcrumbs and settings are written under `.claude/` for session continuity. | `hooks/session-check.sh:53`, `hooks/session-check.sh:54`, `skills/ha-onboard/SKILL.md:427` |
| Verification boundary | Validation and troubleshooting mandate evidence tables describing what ran vs skipped. | `skills/ha-validate/SKILL.md:183`, `skills/ha-troubleshooting/SKILL.md:95` |

## Phase 1 Output: Control-Flow Map

1. Session intake:
   - Session start hook runs env checks and emits routing guidance.
   - Evidence: `hooks/hooks.json:3`, `hooks/session-check.sh:67`, `hooks/session-check.sh:69`.
2. Skill routing:
   - User request triggers skill based on frontmatter trigger descriptions.
   - Evidence: `skills/ha-automations/SKILL.md:3`, `skills/ha-troubleshooting/SKILL.md:3`.
3. Policy/reasoning layer:
   - Skills apply domain policy (resolve entities first, capability checks, stop on mismatch).
   - Evidence: `skills/ha-automations/SKILL.md:40`, `skills/ha-scenes/SKILL.md:46`.
4. Deterministic execution layer:
   - `hass-cli` and helper scripts perform data retrieval/actions.
   - Evidence: `skills/ha-resolver/SKILL.md:66`, `helpers/trace-fetch.py:97`.
5. Delegation layer (conditional):
   - Complex cases can delegate to agents via Task workflow.
   - Evidence: `skills/ha-devices/SKILL.md:417`, `skills/ha-troubleshooting/SKILL.md:56`.
6. Verification layer:
   - Validation runs tiered checks and emits evidence-first output contract.
   - Evidence: `skills/ha-validate/SKILL.md:47`, `skills/ha-validate/SKILL.md:332`.
7. Side-effect guardrail layer:
   - Deploy/rollback and write-heavy actions require explicit confirmation.
   - Evidence: `skills/ha-deploy/SKILL.md:13`, `skills/ha-automations/SKILL.md:53`.
8. Reporting and continuation:
   - Post-edit hook reinforces next-step flow (`/ha-deploy` availability and AskUserQuestion pathing).
   - Evidence: `hooks/hooks.json:21`.

## Criteria Applicability Setup (Initial)

| Criteria Range | Initial Applicability | Rationale | Seed Evidence |
|---|---|---|---|
| CRIT-001..CRIT-005 | Applicable | Core architecture strategy/modularity/scalability criteria directly apply. | `README.md:22`, `references/safety-invariants.md:3` |
| CRIT-006..CRIT-034 | Applicable | Skill contract, activation, safety, reliability, and runtime constraints are central to implementation. | `skills/ha-automations/SKILL.md:2`, `skills/ha-deploy/SKILL.md:10`, `hooks/hooks.json:3` |
| CRIT-035..CRIT-038 | Partially Applicable | Runtime API lifecycle criteria are relevant conceptually, but architecture is Claude Code plugin-first. | `README.md:3`, `CLAUDE.md:9` |
| CRIT-039..CRIT-048 | Applicable | Agent pattern selection and delegation discipline are present in current workflows. | `skills/ha-devices/SKILL.md:5`, `agents/config-debugger.md:38` |
| CRIT-049..CRIT-062 | Applicable (gap-driving) | Evaluation criteria are in-scope, but automated eval infrastructure is not implemented yet. | `docs/architecture-review-workplan.md:401`, `CLAUDE.md:74` |
| CRIT-063 | Applicable | Current architecture already separates guidance/policy and deterministic system execution. | `skills/ha-resolver/SKILL.md:2`, `skills/ha-resolver/SKILL.md:5` |
| CRIT-064, CRIT-066, CRIT-071 | Partially Applicable | Tool surface and telemetry concerns exist but are not governed by MCP-native mechanisms yet. | `skills/ha-deploy/SKILL.md:5`, `.claude/settings.local.json:3` |
| CRIT-065, CRIT-067..CRIT-070 | Not Applicable (current-state) | MCP protocol annotation/transport/async criteria require an MCP server surface not present in repo. | `skills/ha-resolver/SKILL.md:5`, `skills/ha-automations/SKILL.md:5` |

## Decisions Needed (to resolve deferred questions)

1. Trigger false-positive/false-negative thresholds (`Q-004`).
2. Target model matrix and required versions (`Q-005`).
3. Parallel/headless policy boundaries (`Q-010`).
4. Structured output standard (JSON schema, XML, or mixed) (`Q-014`).
5. Retry and iteration caps plus escalation rules (`Q-015`).
6. Reliability acceptance metric (single-run, pass@k, consistency, or hybrid) (`Q-016`).
7. Eval harness isolation and capability/regression split policy (`Q-017`, `Q-018`).
8. MCP scope decisions if adoption is planned (`Q-020` to `Q-023`).

## Notes

- This checkpoint persists the Phase 0 and Phase 1 execution output from chat.
- `docs/architecture-review-workplan.md` Section 5 remains unchanged at this stage; statuses there are still `Open` until explicitly synchronized.
