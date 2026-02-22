# Architecture Review Checkpoint 4 (Phase 6 Target Architecture + Roadmap)

Date: 2026-02-21  
Source plan: `docs/architecture-review-workplan.md` (Section 6.2, Phase 6)  
Scope: Recommended target architecture, migration phases, risks, dependencies, and rollback strategy.

## Recommended Target Architecture

### Solution Statement

Adopt a **hybrid selective architecture**:
1. Keep Skills/Agents as the policy and UX layer.
2. Keep current `hass-cli` execution path as baseline while introducing MCP incrementally for deterministic, high-reuse tool paths.
3. Make evaluation and guardrails first-class runtime controls, not prompt-only guidance.

Primary evidence:
- `README.md:22`
- `README.md:113`
- `docs/architecture-review-checkpoints/2026-02-21-checkpoint-2-phase-3-deep-architecture-assessment.md:9`
- `docs/architecture-review-checkpoints/2026-02-21-checkpoint-3-phase-4-5-composition-and-eval-guardrails.md:8`
- `docs/architecture-review-sources/reference-implementations/ha-mcp-architecture-snapshot.md:71`

### Target Layering

| Layer | Responsibility | Current Base | Target Adjustment |
|---|---|---|---|
| L1: Policy/UX | Intent classification, user dialog, confirmation, narrative output | Skills + Agents in markdown | Keep as primary; split oversized skills and normalize contracts |
| L2: Deterministic Execution | Entity/service discovery, validation probes, diagnostics, mutations | `hass-cli` + helpers | Introduce MCP selectively (stdio-only, tool cap <= 12) where deterministic wins are clear |
| L3: Safety/Verification | Invariants, preconditions, evidence output, retry/loop bounds | Safety docs + skill instructions | Convert to enforceable gates and automated checks |
| L4: Eval/Quality Ops | Capability/regression suites, metrics, promotion lifecycle | Manual-only testing | Add harness with single-run + pass@3 metrics and isolation baseline |
| L5: State/Config | Local settings, runtime breadcrumbs, generated plans, git workflows | `.claude/*`, git repo, hooks | Harden artifact hygiene and configuration contract consistency |

Primary evidence:
- `hooks/hooks.json:3`
- `hooks/session-check.sh:53`
- `skills/ha-validate/SKILL.md:320`
- `docs/architecture-review-workplan.md:364`
- `docs/architecture-review-workplan.md:367`
- `docs/architecture-review-workplan.md:368`

## Interface Contract Targets

### Contract C1 - Skill Mutation Contract

- Required fields: `operation`, `target_files`, `dry_run_preview`, `user_confirmation`, `execution_result`, `verification_result`.
- Hard requirements:
  - Dry-run default for side-effectful paths.
  - Explicit confirmation before mutation/deploy.
  - Evidence table after execution.

Drivers:
- `skills/ha-apply-naming/SKILL.md:17`
- `skills/ha-deploy/SKILL.md:65`
- `references/safety-invariants.md:196`

### Contract C2 - Validation Contract

- Output standard:
  - Machine-consumed: JSON schema artifact.
  - Human-consumed: Markdown summary with evidence table.
- Confidence and tier transparency mandatory.

Drivers:
- `docs/architecture-review-workplan.md:362`
- `skills/ha-validate/SKILL.md:181`
- `skills/ha-validate/SKILL.md:332`

### Contract C3 - MCP Adoption Contract (When Enabled)

- Scope:
  - stdio-only initially.
  - max 12 tools initially.
  - annotation-policy tests as hard CI gate.
  - async operation IDs required for long-running or multi-entity mutations.

Drivers:
- `docs/architecture-review-workplan.md:367`
- `docs/architecture-review-workplan.md:368`
- `docs/architecture-review-workplan.md:369`
- `docs/architecture-review-workplan.md:370`

### Contract C4 - Eval Harness Contract

- Suite split: capability vs regression.
- Metrics: single-run pass rate primary, pass@3 secondary.
- Isolation: clean workspace snapshot + reset `.claude` state + bounded command/turn/token budgets.
- Retry/loop bounds: 2 external retries, 3 refinement iterations max.

Drivers:
- `docs/architecture-review-workplan.md:363`
- `docs/architecture-review-workplan.md:364`
- `docs/architecture-review-workplan.md:365`
- `docs/architecture-review-workplan.md:366`

## Implementation Roadmap

### Near-Term (0-2 Weeks): Safety And Contract Stabilization

1. Enforce `disable-model-invocation` for `ha-apply-naming` contract path.
2. Remove/restrict deploy validation bypass (`--force`).
3. Resolve deploy push contract mismatch (use configured remote/branch).
4. Ignore runtime breadcrumb artifacts in `.gitignore`.
5. Remove broken `ha-conventions` references or implement equivalent module.
6. Normalize safety invariant wording/count across canonical docs.

Success criteria:
- All high-severity Phase 3 findings closed (`AR-F001`..`AR-F003` started/owned).
- No contract mismatches between docs and executable skill frontmatter.

### Mid-Term (2-6 Weeks): Eval Foundation + Selective MCP Pilot

1. Implement minimal deterministic eval harness:
   - capability suite (core generation/validation/troubleshooting flows),
   - regression suite seeded from incidents.
2. Add structured JSON artifacts for validation/resolution/troubleshooting outputs.
3. Pilot read-only MCP tools only (discovery + diagnostics), stdio transport only.
4. Add annotation-policy tests and schema checks to CI path for any MCP-enabled tools.

Success criteria:
- Baseline metrics tracked: single-run pass rate + pass@3.
- Tool surface remains <= 12.
- No safety regression versus pre-pilot behavior.

### Long-Term (6-12 Weeks): Controlled Mutation Expansion + Ops Hardening

1. Expand MCP to selected mutation paths only after read-only pilot stability.
2. Introduce operation ID/status contracts for async or multi-entity mutation flows.
3. Add low-overhead operational telemetry for reliability/perf regression detection.
4. Establish model-upgrade readiness path using harness evidence.

Success criteria:
- Mutation reliability remains at or above baseline.
- Rollback playbooks validated under failure simulation.
- New model adoption decisions supported by harness data, not manual-only checks.

## Risks, Dependencies, Rollback

### Key Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Tool-surface growth beyond usability/safety budget | Increased operator and model error rate | Enforce 12-tool cap and explicit expansion review |
| Safety regression during deterministic integration | Incorrect or unsafe side effects | Keep confirmation gates and evidence contracts unchanged during migration |
| Eval harness under-specification | False confidence, slow regression detection | Implement isolation + suite split + metric policy before broad rollout |
| Contract drift between docs and skills | Execution ambiguity and trust loss | Add contract lint checks in CI for frontmatter + required fields |

### Dependencies

1. CI pipeline support for contract and annotation checks.
2. Stable deterministic fixtures for eval trials.
3. Ownership assignment for safety-contract and test-harness maintenance.

### Rollback Strategy

1. Phase-gated feature flags for MCP-enabled paths.
2. Preserve existing `hass-cli` workflow as fallback until each MCP slice is proven stable.
3. Immediate rollback trigger if safety-gate, validation-gate, or reliability metrics regress below agreed thresholds.

## Final Status

Phase 6 completed.  
Target architecture and implementation roadmap are ready for execution planning.
