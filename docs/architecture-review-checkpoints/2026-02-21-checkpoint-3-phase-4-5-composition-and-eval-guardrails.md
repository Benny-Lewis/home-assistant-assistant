# Architecture Review Checkpoint 3 (Phase 4 + Phase 5)

Date: 2026-02-21  
Source plan: `docs/architecture-review-workplan.md` (Section 6.2, Phase 4 and Phase 5)  
Scope: Skills+MCP composition option analysis plus target evaluation/guardrail architecture.

## Findings-First Option Assessment

| Option | Quality | Safety | Latency/Cost | Maintenance Burden | Failure Modes | Verdict |
|---|---|---|---|---|---|---|
| Skills-heavy, minimal MCP | High for current workflows (strong domain prompting) | Strong current confirmation/evidence posture | Moderate to high token/tool overhead as scope grows | High instruction maintenance as capability surface expands | Prompt drift, oversized skill context, inconsistent deterministic behavior | Viable short-term, weak long-term scaling |
| MCP-heavy, thin skills | High deterministic breadth once mature | Strong if annotation + test discipline are enforced | Better long-run tool execution efficiency, higher near-term integration cost | High migration cost now (new runtime layer + contracts) | Tool-surface explosion, transport/auth complexity, mutation safety regressions | Not recommended as initial move |
| Hybrid selective (recommended) | Best balance: skills for intent/policy, MCP for deterministic execution hotspots | Preserves existing confirmation model while adding typed execution | Controlled improvements where MCP reduces repetitive CLI/orchestration overhead | Moderate and phased; manageable within tool-count budget | Bounded by staged adoption gates and explicit deferments | Recommended target direction |

Primary evidence:
- `README.md:22`
- `README.md:113`
- `docs/architecture-review-sources/reference-implementations/ha-mcp-architecture-snapshot.md:15`
- `docs/architecture-review-sources/reference-implementations/ha-mcp-architecture-snapshot.md:24`
- `docs/architecture-review-sources/reference-implementations/ha-mcp-architecture-snapshot.md:71`

Policy constraints applied:
- `docs/architecture-review-workplan.md:359`
- `docs/architecture-review-workplan.md:360`
- `docs/architecture-review-workplan.md:367`
- `docs/architecture-review-workplan.md:368`
- `docs/architecture-review-workplan.md:370`

## Recommended Composition Strategy (Hybrid Selective)

Recommendation:
1. Keep skills as the policy and interaction layer (intent classification, safety dialogs, user confirmation, narrative explanations).
2. Introduce MCP only for deterministic, high-reuse execution paths where shell orchestration is repetitive or brittle.
3. Enforce strict initial MCP scope limits: stdio-only, tool cap of 12, annotation-policy tests as hard gate.

Rationale:
- Matches current plugin shape and user-approved constraints while reducing long-term brittleness in execution-heavy paths.
- Avoids immediate migration to multi-transport/auth complexity.
- Preserves current safety contract (`explicit confirmation`, `evidence tables`) while making deterministic execution more inspectable.

## MCP Capability Adoption Triage

| Capability Area | Disposition | Why | Required Gates |
|---|---|---|---|
| Entity/area/device discovery tools | Adopt now | High-frequency, read-only, deterministic, low-risk | `readOnly` annotations + CI checks |
| Service/entity validation lookup tools | Adopt now | Strengthens pre-deploy checks and resolver reliability | Schema-validated JSON outputs |
| Trace/logbook/history fetchers | Adopt now | Replaces brittle command choreography in troubleshooting | Timeout + parse/error contract tests |
| Config mutation tools (automations/scripts/helpers) | Adopt later | High-value but side-effectful; requires mature mutation safety model | Confirmation gates + async operation IDs + rollback contracts |
| Dashboard/config orchestration mutators | Adopt later | Useful, but broad blast radius and high variance | Phase-gated rollout with regression suite |
| OAuth/HTTP/SSE transports | Do not adopt (initial phase) | Explicitly deferred by policy; unnecessary for current Claude Code scope | Revisit after stdio baseline stability |
| Broad module import without filtering | Do not adopt (initial phase) | Violates tool-count budget and raises cognitive/safety load | Must remain under 12-tool cap |

Primary evidence:
- `docs/architecture-review-sources/reference-implementations/ha-mcp-architecture-snapshot.md:33`
- `docs/architecture-review-sources/reference-implementations/ha-mcp-architecture-snapshot.md:37`
- `docs/architecture-review-sources/reference-implementations/ha-mcp-architecture-snapshot.md:54`
- `docs/architecture-review-workplan.md:367`
- `docs/architecture-review-workplan.md:368`
- `docs/architecture-review-workplan.md:369`
- `docs/architecture-review-workplan.md:370`

## Phase 5: Target Eval And Guardrail Architecture

### Eval Stack Design

| Layer | Design |
|---|---|
| Capability suite | New/expanded workflows and complex scenarios (multi-entity automations, troubleshooting chains, naming plan generation). |
| Regression suite | Stable, incident-backed tests promoted from capability suite after repeated stable passes. |
| Graders | Code-first deterministic graders for structure/contracts; targeted human review for ambiguous UX outputs; optional constrained LLM grader for narrative quality only. |
| Reliability metrics | Primary `single-run pass rate`; secondary `pass@3` for stochastic flows. |
| Isolation model | Clean workspace snapshot, reset `.claude` state, deterministic fixtures, bounded command/turn/token budgets. |

Primary evidence:
- `docs/architecture-review-workplan.md:364`
- `docs/architecture-review-workplan.md:365`
- `docs/architecture-review-workplan.md:366`
- `docs/architecture-review-workplan.md:425`
- `CLAUDE.md:74`

### Guardrail Gates (High-Impact Flows)

| Gate | Applies To | Enforcement |
|---|---|---|
| G1: Precondition gate | Deploy, rollback, naming execute | Required validation + explicit user confirmation before side effects |
| G2: Safety-contract gate | All mutation paths | Invariant checks (no secret output, capability verification, no silent semantic substitution) |
| G3: Output-contract gate | Validation/troubleshooting/reporting | Evidence table + machine-readable structured artifact where consumed programmatically |
| G4: Retry/loop bound gate | External command + refinement loops | Max 2 external retries; max 3 refinement iterations; escalate afterward |
| G5: Annotation-policy gate (if MCP adopted) | MCP tool catalog | Hard CI checks for read-only vs destructive classification |

Primary evidence:
- `skills/ha-deploy/SKILL.md:39`
- `skills/ha-deploy/SKILL.md:81`
- `references/safety-invariants.md:196`
- `docs/architecture-review-workplan.md:363`
- `docs/architecture-review-workplan.md:370`

## Checkpoint 3 Outcome

1. Option analysis complete across required dimensions (quality, safety, latency/cost, maintenance, failure modes).
2. Candidate MCP adoption triage completed (`Adopt now`, `Adopt later`, `Do not adopt`).
3. Eval and guardrail target architecture completed and aligned to Section 5a policies.
4. Ready to proceed to Phase 6 target-state architecture and roadmap.
