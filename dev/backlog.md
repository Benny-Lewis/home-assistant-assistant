# Backlog

Transcript-derived issues and improvement areas from user session analysis (2026-03-07 to 2026-03-15).
Each entry traces back to one or more session transcripts and is self-contained for future sessions.

## Transcript Legend

| ID | File | Date | Description |
|----|------|------|-------------|
| T1 | `2026-03-08-174642-implement-the-following-plan.txt` | 2026-03-08 | Notification polish: deep links, message cleanup, cooldown delays |
| T2 | `2026-03-08-104445-command-messagehome-assistant-assistantha-analy.txt` | 2026-03-08 | ha-analyze → shade timing → Z-Wave lock troubleshooting → lock automations |
| T3 | `2026-03-07-180934-command-messagehome-assistant-assistantha-analy.txt` | 2026-03-07 | ha-analyze → shade timing → Z-Wave lock troubleshooting (earlier attempt) |
| T4 | `2026-03-07-170833-command-messagehome-assistant-assistantha-onboa.txt` | 2026-03-07 | ha-apply-naming execution (9-phase Z-Wave entity rename plan) |
| T5 | `2026-03-07-133844-command-messagehome-assistant-assistantha-onboa.txt` | 2026-03-07 | ha-naming audit and plan generation (naming spec review, area cleanup) |
| T6 | `2026-03-12-163104-this-session-is-being-continued-from-a-previous-co.txt` | 2026-03-12 | ha-lovelace dashboard prototyping: HACS card install, storage-dashboard mutation, multi-card showcase |
| T7 | `2026-03-13-181110-home-assistant-assistantha-naming.txt` | 2026-03-13 | ha-naming re-audit, blocked-item resolution, ha-apply-naming execution, deploy, dashboard fallout and recovery |
| T8 | `2026-03-15-084839-this-session-is-being-continued-from-a-previous-co.txt` | 2026-03-15 | Camera dashboard finalization, stale memory context drift |
| T9 | `2026-03-15-092628-add-the-ikea-temp-humidity-in-the-office-to-my-d.txt` | 2026-03-15 | Add IKEA sensor to dashboards, wrong skill auto-selection, Git Pull trigger failures |
| T10 | `2026-03-15-124402-implement-the-following-plan.txt` | 2026-03-15 | White noise automation with placeholder entity IDs, premature config generation before prerequisites |
| T11 | `2026-03-15-144436-implement-the-following-plan.txt` | 2026-03-15 | Alexa Media Player auth failure → HA Cloud pivot, Aqara ZHA pairing, Git Pull sync bypass via REST API |

> **Severity key:**
> - **S2 (Bug)** — Incorrect behavior that produces wrong output, silent failures, or errors
> - **S3 (UX Friction)** — Correct behavior but painful user experience
> - **S4 (Missing Feature)** — Capability gap that users hit and had to work around
> - **S5 (Polish)** — Minor annoyance, cosmetic, or documentation gap

## Completed

| ID | Severity | Fixed In | Summary |
|----|----------|----------|---------|
| BL-001 | S2 | 1.3.x | Stop hook no longer references `python3`; session-check.sh detects correct Python and writes breadcrumb |
| BL-002 | S2 | 1.3.2 | `hass-cli raw ws` blocked at hook level in env-guard.sh; residual skill references are informational only |
| BL-006 | S3 | 1.3.3 | Automation entity ID derivation from `alias` documented in ha-automations and ha-resolver |
| BL-014 | S2 | 1.3.3 | Mid-sequence condition placement documented in ha-automations with examples and common-mistake entry |
| BL-019 | S2 | 1.4.0 | Storage-mode save contract with read-after-write verification via lovelace-dashboard.py |
| BL-020 | S3 | 1.4.0 | Sections view safe-edit playbook with grid sizing tables in SKILL.md |
| BL-021 | S3 | 1.4.0 | Entity preflight validation before dashboard saves via find-entities subcommand |
| BL-022 | S4 | 1.4.0 | Custom card research workflow with stable fallback order in SKILL.md |
| BL-029 | S3 | 1.5.0 | Editing conventions added as Safety Invariant #7 (minimal edits only) |
| BL-030 | S3 | 1.5.0 | Post-edit verification added as Safety Invariant #8 (deploy/reload + entity check) |
| BL-003 | S3 | 1.5.0 | History API URL encoding gotcha added to diagnostic-api.md |
| BL-007 | S3 | 1.5.0 | Entity existence validation added to ha-automations step 1 |
| BL-013 | S3 | 1.5.0 | Z-Wave re-inclusion side-effects warning added to ha-troubleshooting |
| BL-017 | S5 | 1.5.0 | common-patterns.md updated to 2024+ YAML syntax |
| BL-018 | S5 | 1.5.0 | Fixed `--no-headers` with `service list` in ha-resolver |

## PR Groupings

Work is grouped into PRs by theme. Sequence reflects recommended order, not strict dependency.

### PR 1: Lovelace & Dashboard (BL-019, BL-020, BL-021, BL-022)

| ID | Severity | Summary |
|----|----------|---------|
| BL-019 | S2 | Storage-mode dashboard save contract (success/failure detection) |
| BL-020 | S3 | Sections view safe-edit playbook (incremental mutations, grid sizing) |
| BL-021 | S3 | Dashboard entity preflight validation before save |
| BL-022 | S4 | Custom-card research workflow after HACS install |

### PR 2: Naming Planning Quality (BL-011, BL-012, BL-027)

| ID | Severity | Summary |
|----|----------|---------|
| BL-011 | S3 | Surface BLOCKED entries during plan review, not mid-execution |
| BL-012 | S3 | Spec coherence check — flag plan vs convention contradictions |
| BL-027 | S2 | Stale area trust — don't auto-plan renames when evidence conflicts |

### PR 3: Naming Execution Reliability (BL-008, BL-009, BL-010, BL-024, BL-025, BL-026)

| ID | Severity | Summary |
|----|----------|---------|
| BL-008 | S2 | Canonical stale entity removal helper (no more 6-attempt discovery) |
| BL-009 | S2 | Friendly-name update via registry override clear, not silent no-op |
| BL-010 | S3 | Dry-run detects already-renamed targets, adjusts counts |
| BL-024 | S2 | Backup strategy doesn't commit `.claude` artifacts or pollute deploy |
| BL-025 | S2 | Target-collision preflight before any rename starts |
| BL-026 | S2 | Verification distinguishes parse failure from missing entity |

### PR 4: Naming UX (BL-023, BL-015, BL-016)

| ID | Severity | Summary |
|----|----------|---------|
| BL-023 | S3 | `/ha-apply-naming` invocation path — no `disable-model-invocation` error |
| BL-015 | S4 | Area registry create/delete/rename helper |
| BL-016 | S3 | Progress messaging for long-running agents |

### PR 5: Deploy & Sync (BL-004, BL-005, BL-028)

| ID | Severity | Summary |
|----|----------|---------|
| BL-028 | S3 | Webhook-based auto-pull on push (root-cause fix for deploy timing) |
| BL-004 | S3 | Git Pull add-on trigger + sync verification helper (fallback for non-webhook setups) |
| BL-005 | S3 | Post-deploy verification distinguishes pre-sync from post-sync state |

### PR 6: Docs & Knowledge Gaps (BL-003, BL-007, BL-013, BL-017, BL-018)

| ID | Severity | Summary |
|----|----------|---------|
| BL-003 | S3 | History API via hass-cli URL encoding workaround |
| BL-007 | S3 | Entity existence validation before automation conditions/triggers |
| BL-013 | S3 | Z-Wave re-inclusion side-effects warning (lock codes, device settings) |
| BL-017 | S5 | Update common-patterns.md to 2024+ YAML syntax |
| BL-018 | S5 | Fix `--no-headers` with `service list` in ha-resolver |

### PR 7: Dashboard Reference Repair & Skill Routing (BL-031, BL-033)

| ID | Severity | Summary |
|----|----------|---------|
| BL-031 | S4 | Storage dashboard entity reference scanner + repair helper after renames |
| BL-033 | S3 | Auto-select ha-lovelace skill for dashboard requests |

### PR 8: Analysis & Troubleshooting UX (BL-032, BL-034, BL-035)

| ID | Severity | Summary |
|----|----------|---------|
| BL-032 | S3 | Timezone conversion for displayed timestamps |
| BL-034 | S3 | API-first guidance for HA UI operations; document browser automation limitations |
| BL-035 | S3 | Proactive solution offering after analysis; close-the-loop convention |

### PR 9: Config Generation Safety (BL-036, BL-037)

| ID | Severity | Summary |
|----|----------|---------|
| BL-036 | S3 | Don't generate YAML with placeholder entity IDs; wait for prerequisites |
| BL-037 | S5 | Portable Jinja strftime format codes |

---

## 1. Hook System

### BL-001: Stop hook fails with `python3: command not found` on Windows

- **Severity:** S2
- **Transcripts:**
  - T2:310-312 — `Stop hook error: Failed with non-blocking status code: /usr/bin/bash: line 1: python3: command not found`
  - T2:481-483 — same error after deploy
  - T3:310-312, 481-483 — same error in a different session
  - Appears 8+ times across T2 and T3 (after nearly every assistant response)
- **Affected components:** Hook system (stop hook), `hooks/session-check.sh`
- **Description:** On Windows (MINGW64), the stop hook attempts to run `python3` which doesn't exist — Windows provides `python` or `py`. The SessionStart hook correctly detects the right Python command and writes it to `.claude/ha-python.txt`, but the stop hook doesn't read that breadcrumb file. The error is non-blocking (execution continues) but appears after every response, creating noise and confusion about whether something actually failed.
- **Rationale:** The two-tier discovery pattern (breadcrumb → `command -v` fallback) documented in the plugin's conventions works correctly for helpers but isn't applied to the stop hook. This affects all Windows users.
- **Suggested approach:**
  1. Identify which hook is the "stop hook" — it may be a user-level hook in `.claude/hooks.json` or another plugin, not this plugin's hooks. If it's in this plugin's `hooks/hooks.json`, update it to read `.claude/ha-python.txt` before falling back to `python3`.
  2. If the stop hook is external to this plugin, document the issue in CLAUDE.md Known Environment Issues with a fix users can apply.
  3. Add a regression eval case checking that no hook references hardcoded `python3`.

---

## 2. API & CLI Reliability

### BL-002: Model still attempts `hass-cli raw ws` despite it being broken

- **Severity:** S2
- **Transcripts:**
  - T1:389-401 — Model tries `hass-cli raw ws '{"type": "trace/list", "domain": "automation"}'` → `success: false, error: {code: unknown_command}`. Then tries again without domain filter → same error. Both fail.
  - T2:1089-1092 — `hass-cli raw ws '{"type": "zwave_js/node_status", ...}'` → `Error: Exit code 2`
  - T4:781-788 — `hass-cli raw ws '{"type": "config/entity_registry/remove", ...}'` → `success: false`
  - T4:790-794 — `hass-cli raw ws '{"type":"config/entity_registry/list"}'` → no output
- **Affected components:** `references/hass-cli.md`, `hooks/env-guard.sh`, all skills that reference hass-cli
- **Description:** `hass-cli raw ws` is broken on HA 2026.2+ (returns "Unknown command" for all message types). This is documented in CLAUDE.md as a known gotcha and was addressed in v1.1.0 by replacing ws commands in skill docs with built-in `-o json` commands. However, the model's general HA knowledge still leads it to attempt ws commands when skill docs don't cover a specific use case (traces, entity registry removal, Z-Wave node operations). Each attempt wastes a tool call and often triggers a cascade of retries.
- **Rationale:** This appeared in 4 of 5 transcripts, making it the most widespread issue. Documentation alone is insufficient — the model's training data includes ws patterns that override skill guidance.
- **Suggested approach:**
  1. Add a `hass-cli raw ws` block to `hooks/env-guard.sh` (exit code 2 with a message like "BLOCKED: `hass-cli raw ws` is broken on HA 2026.2+. Use `hass-cli -o json` built-in commands or Python websocket helpers instead.")
  2. Add an eval case to the capability suite verifying that the hook blocks ws commands.

### BL-003: History API knowledge gap causes 400 errors during troubleshooting

- **Severity:** S3
- **Transcripts:**
  - T1:473-496 — Model tries `/api/history/period/2026-03-08T23:10:00+00:00?filter_entity_id=binary_sensor.entryway_doorbell_person&end_time=2026-03-08T23:13:00+00:00&minimal_response` → `400 Bad Request`. Tries again without `&minimal_response` → still 400. Finally succeeds with `/api/history/period?filter_entity_id=...` (no time window params) on line 498.
- **Affected components:** `references/diagnostic-api.md`, `skills/ha-troubleshooting/SKILL.md`
- **Description:** When investigating duplicate notifications, the model needed to query entity state history for a specific time window. The History API's time-window parameters (`/period/{timestamp}?end_time=...`) returned 400 errors via hass-cli, likely due to URL encoding issues with the `+00:00` timezone offset in the path segment. The model had to fall back to querying the entire history and filtering with grep, which is inefficient and returns excessive data.
- **Rationale:** The `references/diagnostic-api.md` (added in v1.2.0) documents History API procedures but may not cover the hass-cli URL encoding quirk. Any user debugging automation timing will hit this pattern.
- **Suggested approach:**
  1. Add a "History API via hass-cli" section to `references/diagnostic-api.md` documenting that time-window parameters in the URL path don't work reliably through hass-cli due to URL encoding. Recommend the parameterless form with grep filtering, or a Python helper.
  2. Consider adding a `helpers/entity-history.py` helper that wraps the History API with proper URL encoding and time filtering.

---

## 3. Deploy & Sync Workflow

### BL-004: No mechanism to force or verify Git Pull add-on sync after deploy

- **Severity:** S3
- **Transcripts:**
  - T2:435-479 — After pushing shade timing changes, model tries to trigger Git Pull: `hass-cli raw post /api/hassio/addons/core_git_pull/start` (line 438) → no visible effect. Tries `sleep 5` + reload → old aliases still shown (line 443-447). Tries `sleep 5` + reload again → still stale (line 451-457). Gives up and reports "Pending" status.
  - T2:1624-1702 — After pushing lock automations, model tries 8+ different API endpoints to trigger/check Git Pull: `curl` to `/api/hassio/addons/core_git_pull/logs` → no output (line 1641-1644); `curl` to `.../info` → JSON parse error (line 1651-1669); `hass-cli raw get` → `InvalidURL` due to MINGW path conversion (line 1671-1674); another attempt → `401 Unauthorized` (line 1697-1702). Finally uses Python websocket to trigger Git Pull successfully (line 1707-1713).
  - T3:435-479 — Identical pattern: push, try to trigger Git Pull, fail, report Pending.
- **Affected components:** `skills/ha-deploy/SKILL.md`
- **Description:** The ha-deploy skill pushes to git and calls `automation.reload`, but HA's on-disk config hasn't been updated yet because the Git Pull add-on operates on its own schedule. The model then enters a pattern of: try Supervisor API → fail (different auth) → sleep + retry → still stale → give up. v1.2.1 improved this by documenting the "Pending" status and eliminating futile retry loops, but users still have no programmatic way to force a sync or verify it completed.
- **Rationale:** Every deploy session in the transcripts hit this issue. The Supervisor API requires a different auth mechanism (Supervisor token, not long-lived access token), which the model doesn't have access to via hass-cli. The Python websocket approach found in T2:1707 works but isn't documented anywhere.
- **Suggested approach:**
  1. Add a `helpers/git-pull-trigger.py` helper that uses the HA websocket API to start the Git Pull add-on and wait for completion. The websocket approach bypasses Supervisor auth requirements.
  2. Update `skills/ha-deploy/SKILL.md` to call this helper after push, replacing the current "Pending" status with actual sync verification.
  3. Document in `references/hass-cli.md` that Supervisor add-on APIs require different auth than hass-cli provides.

### BL-005: Post-deploy verification shows stale HA state without actionable next step

- **Severity:** S3
- **Transcripts:**
  - T2:429-461 — After deploying shade changes, the model verifies by querying `hass-cli state list | grep "automation.*shade"` and sees old aliases. Reports them as evidence of success ("Pending") but the user has no way to confirm the changes actually took effect until the next Git Pull cycle.
  - T2:1624-1631 — After deploying lock automations, same pattern: `hass-cli state list | grep "automation.*lock"` shows old state.
- **Affected components:** `skills/ha-deploy/SKILL.md`
- **Description:** After git push + `automation.reload`, the ha-deploy skill checks HA state to verify the changes. But since HA hasn't pulled the new config yet, the verification always shows stale data. The skill currently reports "Pending — Git Pull add-on will sync on its next cycle" which is accurate but leaves the user without confirmation that their changes worked. This is the user-facing symptom of BL-004.
- **Rationale:** Verification is a core part of the deploy workflow (Safety Invariant #6 requires evidence tables). Showing stale data as "verification" undermines confidence in the deploy process.
- **Suggested approach:**
  1. If BL-004's helper is implemented, use it to wait for sync and then re-verify.
  2. If not, update the deploy verification to clearly distinguish "pre-sync check (may show stale data)" from "post-sync verification (confirms changes are live)". Offer the user a command to run later: "Run `hass-cli state list | grep [pattern]` after the next Git Pull cycle to confirm."

---

## 4. Entity Resolution & Validation

### BL-006: Automation entity IDs generated from `alias` field not documented in skill knowledge

- **Severity:** S3
- **Transcripts:**
  - T1:284-291 — After deploying 5 notification automations, the model looked up automations by their YAML `id` field values (e.g., `notify_doorbell_ring`). The lookup missed them because HA generates entity IDs from the `alias` field, not `id`. The model discovered this: "HA generates automation entity IDs from the alias field, not the YAML id field. So alias: 'Notify: Backyard Door Opened While Away' becomes automation.notify_backyard_door_opened_while_away."
- **Affected components:** `skills/ha-automations/SKILL.md`, `skills/ha-resolver/SKILL.md`
- **Description:** When creating or verifying automations, the model assumed the YAML `id` field determines the entity ID. In reality, HA derives the entity ID from the `alias` field (lowercased, spaces→underscores). The `id` field is for internal config tracking only. This caused a failed lookup that wasted tool calls before the model figured out the mapping. Any user creating automations and then trying to verify or reference them will hit this.
- **Rationale:** This is core HA domain knowledge that belongs in the automation creation skill. Without it, the model will continue to make incorrect assumptions about entity IDs after creation.
- **Suggested approach:**
  1. Add a "Entity ID Resolution" section to `skills/ha-automations/SKILL.md` documenting that HA generates automation entity IDs from the `alias` field, not the `id` field.
  2. Add the same note to `skills/ha-resolver/SKILL.md` so the entity resolver agent knows the mapping.

### BL-007: No entity existence validation before use in automation conditions

- **Severity:** S3
- **Transcripts:**
  - T2:1932-1943 — When adding a `condition: state` for `person.ben` to the lock automation, the model inserted the condition without first verifying that `person.ben` exists in the HA instance. The config validation passed, but this was coincidental — if the entity didn't exist, the automation would silently fail at runtime (conditions referencing missing entities evaluate to false).
- **Affected components:** `skills/ha-automations/SKILL.md`, `skills/ha-resolver/SKILL.md`
- **Description:** The ha-automations skill creates automations that reference entities (triggers, conditions, actions) without first resolving them against the live HA instance. The ha-resolver skill exists for this purpose but isn't invoked during automation creation. HA's config check (`/api/config/core/check_config`) validates YAML syntax but doesn't check entity existence.
- **Rationale:** Any user asking the plugin to create automations with conditions or triggers referencing entities could end up with automations that silently fail because the entity doesn't exist or has a different ID than expected.
- **Suggested approach:**
  1. Add guidance to `skills/ha-automations/SKILL.md` requiring entity resolution (via ha-resolver or `hass-cli state get`) for all entity references before writing the automation YAML.
  2. Consider adding a pre-flight check step to the automation creation workflow that verifies all referenced entities exist.

---

## 5. Naming Workflow Reliability

### BL-008: Stale entity removal requires 6 API approaches before finding one that works

- **Severity:** S2
- **Transcripts:**
  - T4:727-812 — During post-rename cleanup, the skill needed to remove 20 stale (orphaned) entities. It tried 6 different approaches in sequence:
    1. `hass-cli entity delete` (line 727-732) → command exists but silently doesn't work
    2. `hass-cli state get` verification showed entities still present (line 744-751)
    3. `hass-cli raw ws '{"type": "config/entity_registry/remove"}'` (line 781-788) → `success: false`
    4. `hass-cli raw ws '{"type":"config/entity_registry/list"}'` (line 790-794) → no output
    5. Python with `websocket` module (line 799) → `ModuleNotFoundError: No module named 'websocket'`
    6. Python async with `aiohttp` approach (line 806-812) → finally worked: "Removed 20 stale entities"
- **Affected components:** `skills/ha-apply-naming/SKILL.md`
- **Description:** The ha-apply-naming skill has no documented reliable method for removing stale entities from the HA registry. The model had to discover through trial-and-error that only the Python websocket async approach works. This wasted ~15 tool calls and significant time. The working approach (Python async connecting directly to HA websocket API) is not documented anywhere in the plugin.
- **Rationale:** Entity cleanup is a standard part of the naming workflow — any user running ha-apply-naming will need to remove stale entities after renames. The working approach needs to be the first (and ideally only) approach tried.
- **Suggested approach:**
  1. Add a `helpers/entity-cleanup.py` helper that removes entities from the HA registry via websocket API. It should accept a list of entity IDs and return success/failure for each.
  2. Update `skills/ha-apply-naming/SKILL.md` to reference this helper as the canonical stale entity removal method.
  3. Document that `hass-cli entity delete` and `hass-cli raw ws config/entity_registry/remove` do NOT work reliably.

### BL-009: `hass-cli entity update --name` silently reports success without updating friendly names

- **Severity:** S2
- **Transcripts:**
  - T4:902-907 — The skill ran `hass-cli entity update sensor.front_yard_sconces_node_status --name "Front Yard Sconces Node Status"` and similar commands. Output showed `=== Done ===` with no errors.
  - T4:948-954 — Subsequent verification showed names unchanged: `sensor.front_yard_sconces_node_status` still displayed "Frontyard Sconce Lights Node" instead of "Front Yard Sconces Node Status".
  - T4:960-966 — Python async script was needed to clear custom name overrides by setting `name: null` in the entity registry, allowing the entity to inherit the updated device name.
- **Affected components:** `skills/ha-apply-naming/SKILL.md`
- **Description:** When entities have custom name overrides in the HA entity registry (set during a previous rename), `hass-cli entity update --name` appears to succeed but doesn't actually change the displayed friendly name. The custom override takes precedence over the device name. The fix requires clearing the name override to `null` via the entity registry API, which forces the entity to inherit from the device name.
- **Rationale:** This affects any user doing multi-pass entity renames. The first rename sets a custom override; subsequent device-name-based renames fail silently because the override persists. The workaround (Python websocket to clear overrides) needs to be documented.
- **Suggested approach:**
  1. Document in `skills/ha-apply-naming/SKILL.md` that friendly name updates for previously-renamed entities require clearing the name override (setting `name: null` in entity registry) rather than setting a new name.
  2. Add this to the `helpers/entity-cleanup.py` helper (BL-008) or create a separate `helpers/entity-rename.py` helper.

### BL-010: Dry-run entity count doesn't match execution count

- **Severity:** S3
- **Transcripts:**
  - T4:78-80 — Dry-run preview: "Phase 2: Rec Room Dimmer — 48 entity renames"
  - T4:231 — Execution result: "Phase 2 complete (47/47 renames)"
  - T4:277-292 — Phase 7 entity rename failed: `light.entryway_chandelier already exists — likely renamed previously`
- **Affected components:** `skills/ha-apply-naming/SKILL.md`
- **Description:** The dry-run phase of ha-apply-naming reported 48 entity renames for Phase 2, but execution completed 47. The plan showed 113 total renames but execution completed 112 with 1 skipped. The discrepancy is caused by entities that were already renamed in a previous run. The dry-run doesn't check whether target entity IDs already exist, so it overcounts.
- **Rationale:** Count discrepancies erode user confidence in the naming workflow. If the dry-run says 48 and execution says 47, users wonder what went wrong. The fix is to make the dry-run detect already-renamed entities.
- **Suggested approach:**
  1. Add a pre-flight check to ha-apply-naming's dry-run that queries the entity registry for target entity IDs and marks already-existing ones as "skip (already renamed)".
  2. Report the adjusted count: "Phase 2: Rec Room Dimmer — 47 entity renames (1 already renamed, will skip)"

### BL-011: Naming plan includes BLOCKED entries that aren't surfaced until mid-execution

- **Severity:** S3
- **Transcripts:**
  - T5:587-598 — The generated naming plan included Phase 9 with 4 blocked entries like: `new_id: null, reason: "BLOCKED: need to identify which area this device is in"`. These were only discovered during execution when the user was already mid-way through a multi-phase rename.
  - T5:1032-1050 — User had to answer "what is wave 1 mini?" to unblock Phase 9 entries.
- **Affected components:** `skills/ha-naming/SKILL.md`, `agents/naming-analyzer.md`
- **Description:** The naming-analyzer agent generates a naming plan that may include BLOCKED entries — entities it couldn't map to an area or device. These blocks are embedded in the plan YAML but aren't prominently surfaced to the user during plan review. They only become apparent during execution (ha-apply-naming), forcing the user to stop, clarify, and restart.
- **Rationale:** Naming plans can include hundreds of renames across 9+ phases. Discovering blocks mid-execution breaks the user's flow. All ambiguities should be resolved during the planning phase.
- **Suggested approach:**
  1. Update `skills/ha-naming/SKILL.md` to require that the plan review step prominently lists all BLOCKED entries and asks the user to resolve them before marking the plan as ready.
  2. Have the naming-analyzer agent attempt to resolve blocks using `hass-cli -o json device list` and `hass-cli -o json area list` to correlate orphaned entities with device/area data before giving up.

### BL-012: No automatic spec coherence check — plan can contradict naming conventions

- **Severity:** S3
- **Transcripts:**
  - T5:225-247 — The naming spec (naming.md) said Tier 3 diagnostic entities should NOT be renamed: "Tier 3: Never Rename (Diagnostic Entities) — Keep original names - helps with troubleshooting". But the generated plan renamed ~30 diagnostic entities (node_8_rssi → rec_room_dimmer_rssi, etc.). The model discovered the contradiction only because the user asked "is the plan still a good plan to follow that agrees with the naming spec?" The model then recommended updating the spec to match actual practice.
- **Affected components:** `skills/ha-naming/SKILL.md`, `agents/naming-analyzer.md`
- **Description:** The naming-analyzer agent generates plans based on analysis of the current entity registry, but doesn't cross-check the plan against the user's naming spec document. This can produce plans that violate the user's own documented conventions. In this case, the violation was actually an improvement (area-prefixed diagnostics are better than node-number diagnostics), but the contradiction should be flagged proactively.
- **Rationale:** Users invest time writing naming conventions. If the plan generation ignores them, the conventions become stale and the user loses trust in the planning process.
- **Suggested approach:**
  1. Add a "Spec Coherence Check" step to `skills/ha-naming/SKILL.md` that runs after plan generation. It should compare the plan against the naming spec and flag any contradictions (e.g., "Plan renames 30 Tier 3 diagnostic entities, but spec says Tier 3 should not be renamed").
  2. When contradictions are found, present the user with options: "Update the spec to match the plan" or "Modify the plan to match the spec".

---

## 6. Domain Knowledge Gaps

### BL-013: ha-troubleshooting missing Z-Wave re-inclusion side effects (lock codes, device settings)

- **Severity:** S3
- **Transcripts:**
  - T2:1770-1846 — After Z-Wave lock re-inclusion, user reports: "hmm is the lock reset or something? my old codes dont work anymore." The model correctly diagnosed that the U-tec app's re-inclusion process may have cleared lock codes (line 1836-1838: "The app may have done a deeper reset of the Z-Wave radio that also cleared the code slots"). The user had to re-add codes through the U-tec app. No warning was given before or during the re-inclusion process.
- **Affected components:** `skills/ha-troubleshooting/SKILL.md`, `skills/ha-troubleshooting/references/`
- **Description:** The ha-troubleshooting skill's Z-Wave diagnostics guide users through exclusion/re-inclusion without warning about potential side effects: loss of user codes, device settings resets, changed entity IDs, and the need to re-configure device parameters. For Z-Wave locks specifically, code loss means the user gets locked out of their own house.
- **Rationale:** Z-Wave re-inclusion is a common troubleshooting step. Any user with a Z-Wave lock (or other device that stores user-configured data) should be warned about data loss before proceeding.
- **Suggested approach:**
  1. Add a "Side Effects Warning" section to the Z-Wave re-inclusion procedure in `skills/ha-troubleshooting/SKILL.md` listing potential consequences: user codes cleared, device settings reset, entity IDs changed (requiring automation updates), device parameters need reconfiguration.
  2. For locks specifically, recommend backing up codes via the manufacturer's app before proceeding.

### BL-014: ha-automations missing guidance on condition placement within action sequences

- **Severity:** S2
- **Transcripts:**
  - T2:1932-1943 — Model added a `condition: state` block between two action blocks in the lock automation:
    ```yaml
    actions:
      - action: lock.lock
        target:
          entity_id: lock.entryway
      - condition: state          # condition mid-sequence
        entity_id: person.ben
        state: "not_home"
      - action: notify.mobile_app_iphone
    ```
  - T2:1950-1956 — Model explained: "HA evaluates action sequences in order and stops if a condition fails mid-sequence — so the lock action runs first unconditionally, then the condition gates the notification." This explanation is **correct** — HA does support conditions mid-action-sequence as gates. But the skill doesn't document this pattern, leading to inconsistent usage.
- **Affected components:** `skills/ha-automations/SKILL.md`
- **Description:** HA supports conditions placed within action sequences (not just at the top level). A mid-sequence condition acts as a gate: if it fails, the remaining actions are skipped but earlier actions that already executed are not rolled back. This is a useful pattern (e.g., always lock the door but only notify if away) but isn't documented in the ha-automations skill, so the model may use it inconsistently or explain it incorrectly.
- **Rationale:** This is a power-user HA pattern that the skill should document to ensure consistent, correct usage across all automation creation requests.
- **Suggested approach:**
  1. Add a "Conditions in Action Sequences" section to `skills/ha-automations/SKILL.md` documenting the mid-sequence condition pattern with examples and explaining that conditions gate subsequent actions only (earlier actions still run).

### BL-015: Area creation/deletion not automated in ha-apply-naming workflow

- **Severity:** S4
- **Transcripts:**
  - T5:587-610 — The naming plan includes Phase 6 with area creation/deletion steps (create main_bedroom, downstairs_bathroom, etc.; delete front_foyer, hallway). These are listed in the plan YAML but have to be executed through API calls during ha-apply-naming execution.
  - T4:277-284 — During execution, area deletions were attempted via `hass-cli area delete front_foyer` — the command exists but success/failure was unclear (output truncated by rate limit, line 280-283 shows `success: false`).
- **Affected components:** `skills/ha-apply-naming/SKILL.md`, `helpers/`
- **Description:** The naming plan's Phase 6 (area registry cleanup) includes creating and deleting HA areas. Currently the model attempts this via `hass-cli area delete` and `hass-cli raw ws config/area_registry/create`, but these commands are unreliable. Area operations should use the same Python websocket approach that works for entity operations.
- **Rationale:** Area creation/deletion is a prerequisite for entity renames in later phases (entities need to be assigned to the correct area). An unreliable area step can block the entire naming workflow.
- **Suggested approach:**
 1. Add area create/delete/rename functions to an existing helper (e.g., `helpers/entity-registry.py`) or create a `helpers/area-registry.py` helper that uses the HA websocket API.
 2. Update `skills/ha-apply-naming/SKILL.md` to reference this helper for Phase 6 operations.

---

## 7. Naming Execution & Plan Reliability

### BL-023: `/ha-apply-naming` appears user-invocable but direct invocation fails

- **Severity:** S3
- **Transcripts:**
  - T7:347-352 - The user asked to run `/ha-apply-naming`; Claude attempted `Skill(home-assistant-assistant:ha-apply-naming)` and received `cannot be used with Skill tool due to disable-model-invocation`
  - T7:379 - The user had to explicitly tell Claude that it should still be able to follow the skill internally even though the direct slash invocation failed
- **Affected components:** `skills/ha-apply-naming/SKILL.md`, `README.md`, `CLAUDE.md`
- **Description:** `ha-apply-naming` is documented and presented as a slash-command workflow, but the skill metadata also sets `disable-model-invocation: true`. In practice this leaks into the user experience as a confusing tool error the first time the user tries to run the command directly. The workflow is still possible if Claude manually reads the skill and follows it, but the user should never have to understand or explain that distinction.
- **Rationale:** This is not just cosmetic. It interrupts the task at the exact moment the user is trying to move from planning to execution, and it makes the plugin look internally inconsistent: the docs say "run `/ha-apply-naming`" while the runtime says the skill cannot be used.
- **Suggested approach:**
  1. Make the invocation path consistent: either remove `user-invocable: true` for `ha-apply-naming`, or add a router/wrapper flow so `/ha-apply-naming` cleanly enters the skill protocol without throwing a disable-model-invocation error.
  2. Update `README.md` and `CLAUDE.md` to explain the intended execution path if the skill must remain non-directly invocable.
  3. Add a capability eval that asserts the user never sees the raw `disable-model-invocation` error for a documented slash command.

### BL-024: ha-apply-naming backup strategy can commit and deploy ephemeral `.claude` artifacts

- **Severity:** S2
- **Transcripts:**
  - T7:416-428 - The execution started with `git add -A && git stash --include-untracked`, then immediately `git stash pop`
  - T7:434-439 - The pre-rename backup commit `c999b4b` included temporary artifacts such as `create mode 100644 .claude/ha-prefetch-areas.json`
  - T7:957-979 - During deploy, `git diff --stat origin/main..HEAD` showed the `.claude/ha-prefetch-*` files and Claude pushed two commits, including the backup commit, to `origin/main`
  - T7:1688 - The later review explicitly listed `c999b4b` as the pre-rename backup commit now present in branch history
- **Affected components:** `skills/ha-apply-naming/SKILL.md`, `.gitignore`, deploy workflow interaction with `skills/ha-deploy/SKILL.md`
- **Description:** The current backup procedure is unsafe for a repository-backed Home Assistant workflow. Instead of creating an isolated local checkpoint, it stages everything, stashes untracked files, restores them, and then commits a "pre-rename backup" that can include large temporary `.claude` prefetch artifacts. Because deploy later pushes all branch commits, that backup commit and its temp files are promoted to `origin/main`. This pollutes git history, increases review noise, and risks leaking scratch artifacts into the canonical config repository.
- **Rationale:** This transcript shows the failure mode end-to-end, not just in theory: temporary prefetch files were committed, the branch now had two commits instead of one meaningful change, and both were pushed during normal deploy. That is a workflow bug with real repository consequences.
- **Suggested approach:**
  1. Change the backup strategy from "commit current state on the working branch" to a local-only mechanism: lightweight tag, detached backup branch, or stash reference that is never eligible for deploy.
  2. Ensure `.claude/ha-prefetch-*` and similar scratch files are ignored or explicitly excluded from rename/deploy commits.
  3. Update `ha-apply-naming` so any backup commit, if still used, is clearly marked local-only and never included in the later push set by default.

### BL-025: ha-apply-naming lacks target-collision preflight and canonical collision handling

- **Severity:** S2
- **Transcripts:**
  - T7:455 - Preflight only verified that `203/203 entities exist in registry`; it did not verify that the target IDs were free
  - T7:790 - Bulk execution hit `18 failed renames`, all due to `"already registered"` collisions
  - T7:905 - Final execution summary reported `203/203 succeeded (18 needed collision fixes)` only after ad hoc manual repair
  - T7:929-932 - Collision repair required semantic reinterpretation: `light.front_foyer_chandelier` had to become `light.top_of_stairs_chandelier`, and `wave_1_mini_*` had to be corrected from planned `front_yard_relay_*` names to `entryway_exterior_*`
- **Affected components:** `skills/ha-apply-naming/SKILL.md`, `skills/ha-naming/SKILL.md`
- **Description:** The execution workflow validates source existence but not target availability. That means the first real collision check happens in the middle of the bulk rename, after partial progress has already been made. In this transcript, 18 renames failed because the target IDs were already taken by existing entities or by earlier renames in the same batch. Recovering required manual reasoning about physical device identity and alternate names, not just retrying the same operation.
- **Rationale:** This is more severe than the existing dry-run count discrepancy issue. The workflow did not merely miscount; it entered a partially-applied state and required custom repair logic mid-run. That raises both reliability and rollback risk.
- **Suggested approach:**
  1. Add a mandatory target-collision preflight in dry-run and execute modes: check whether every `to_id` already exists in the registry before any rename starts.
  2. Surface collisions as an explicit review section before execution, with categories like "already renamed", "conflicts with active entity", and "ambiguous duplicate device".
  3. Teach `ha-naming` to emit alternate candidate IDs or "needs clarification" when the proposed target is likely to collide with an existing semantically valid name.

### BL-026: Post-rename verification can falsely conclude HA restart is required

- **Severity:** S2
- **Transcripts:**
  - T7:1039-1053 - Initial verification reported the renamed entities as `MISSING`
  - T7:1057-1071 - Claude concluded the registry update required a full HA restart for the state machine to pick up the new IDs
  - T7:1091-1125 - Follow-up checks reported `UNAVAILABLE`, then `HA NOT RESPONDING`, reinforcing the restart narrative
  - T7:1138-1144 - A plain `hass-cli state get sun.sun` worked immediately; the actual problem was that the JSON parsing path was failing, not that HA was still restarting
  - T7:1148-1156 - Re-running verification with the plain tabular command showed the renamed entities were already live
- **Affected components:** `skills/ha-apply-naming/SKILL.md`, any shared verification guidance that uses `hass-cli -o json state get`
- **Description:** The verification workflow is brittle when `hass-cli -o json state get` returns non-JSON or unexpected output. In this transcript that parsing failure cascaded into an incorrect diagnosis: Claude concluded that HA needed a restart to realize the renamed entity IDs, then interpreted follow-up parse failures as evidence that HA was still rebooting. The user had to push back before Claude discovered that plain `hass-cli state get` was working and the renamed entities were already available.
- **Rationale:** This is operationally risky. The bad diagnosis led directly to an unnecessary restart in the middle of a rename/deploy flow, which likely contributed to subsequent device reconnect noise and wasted several minutes of debugging.
- **Suggested approach:**
  1. Replace the current JSON-only verification recipe with a more defensive helper or parser that can distinguish transport failure, non-JSON CLI output, and genuine missing entities.
  2. Add an explicit health-check gate before recommending restart: confirm with a known-good entity using the same command path and confirm HA web/API availability separately.
  3. Document that registry presence plus successful plain `hass-cli state get` is sufficient evidence of rename success; restart should be a last resort, not the default explanation.

### BL-027: Naming audit can over-trust stale HA area assignments and generate wrong renames

- **Severity:** S2
- **Transcripts:**
  - T7:143 - The plan grouped `attic_* -> garage_*` under wrong-area-prefix fixes
  - T7:647-686 and T7:753-779 - Execution propagated that assumption into entity IDs and dashboard labels, renaming `sensor.attic_*` to `sensor.garage_*` and "Attic" labels to "Garage"
  - T7:1934 - The user identified that the device had physically moved and the HA device area assignment was stale
  - T7:1981-1983 - Claude explicitly concluded: `our rename to sensor.garage_temperature was incorrect` because the audit trusted the current device area over the existing semantic entity name/history
  - T7:2187-2195 - The session then had to revert the three attic entities and repair dashboard references
- **Affected components:** `skills/ha-naming/SKILL.md`, `agents/naming-analyzer.md`
- **Description:** The naming audit currently treats HA's present device-area assignment as authoritative even when other evidence suggests the assignment is stale. In this session the entities had long-established `attic_*` names and historical context consistent with "attic", but the device registry still pointed to `garage`. The audit used that stale area assignment to generate a wrong rename plan, and the execution workflow faithfully applied it, causing entity renames, dashboard edits, and follow-on confusion that all had to be reverted.
- **Rationale:** This is a high-severity planning error because it converts stale metadata into broad, automated churn. Once the bad plan exists, the execution skill amplifies the mistake across entity IDs, templates, YAML dashboards, and storage dashboards.
- **Suggested approach:**
  1. Add a confidence model to `ha-naming`: when device area, existing semantic entity IDs, git history, and dashboard labels disagree, do not auto-plan the rename; mark it for confirmation instead.
  2. Teach the naming-analyzer to treat long-lived, already-semantic entity IDs as stronger evidence than a single stale area assignment unless the user explicitly requests area-based normalization.
  3. Surface "area assignment appears stale" as its own audit category so the user can fix the metadata first, then regenerate the naming plan.

---

## 8. Lovelace & Dashboard Workflow

### BL-019: Storage-mode Lovelace saves have no documented success/failure contract

- **Severity:** S2
- **Transcripts:**
  - T6:498-507 â€” three attempts to update the experimental dashboard returned `Error: JavaScript execution error: 3`
  - T6:530-542 â€” the model observed that the view was still on the old layout even though saves appeared to return
  - T6:549-551 â€” a minimal title change proved the contract: `null = success`; the earlier `error: 3` saves had actually failed
- **Affected components:** `skills/ha-lovelace/SKILL.md`, `references/ha-web-ui.md`
- **Description:** The plugin has no canonical operational contract for mutating storage-mode dashboards. In the transcript, the model edited the live Lovelace config through browser JavaScript/WebSocket calls, received opaque `error: 3` responses, briefly hypothesized that the writes may have succeeded anyway, and only later discovered that a successful save returns `null` while the larger writes had failed. That gap matters because it allows a dangerous failure mode: the assistant can report that a dashboard edit is done while HA is still serving the old config or a broken partial config.
- **Rationale:** This is a correctness issue, not just friction. Dashboard work is user-visible immediately, and false success claims erode trust faster than most other plugin errors because the UI either stays stale or renders blank.
- **Suggested approach:**
  1. Add a dedicated `references/dashboard-api.md` with the storage-dashboard read/save contract, including expected response shapes, failure handling, and mandatory read-after-write verification.
  2. Add a helper such as `helpers/lovelace-dashboard.py` that performs fetch/save/verify operations with explicit exit codes instead of relying on opaque browser-tool return values.
  3. Update `skills/ha-lovelace/SKILL.md` to require post-save verification after every structural change: re-fetch config, verify the changed view data, then visually verify render.

### BL-020: `ha-lovelace` lacks a safe-edit playbook for sections views and dense custom-card layouts

- **Severity:** S3
- **Transcripts:**
  - T6:230 â€” replacing the demo view with a nested grid-in-sections structure produced a blank page
  - T6:551-557 â€” replacing the entire `sections` array at once caused a validation conflict, and the model had to switch to incremental section writes
  - T6:579-599 â€” the model then had to trial-and-error `max_columns`, eventually finding a working layout only after changing the structure again
  - T6:699-731 â€” once each card held three sensors, legends overlapped until the model manually increased `grid_options.rows`
- **Affected components:** `skills/ha-lovelace/SKILL.md`
- **Description:** The current Lovelace skill covers basic card syntax and YAML mode, but it does not provide an operational playbook for storage-mode sections views. The transcript shows the model learning by failure that some section structures render blank, that bulk section replacement is riskier than incremental mutation, that `max_columns` interacts with renderability, and that dense multi-entity cards need larger row allocations to avoid overlap. Without this knowledge encoded, future dashboard sessions will repeat the same sequence of blank views, structural retries, and spacing fixes.
- **Rationale:** Lovelace prototyping is iterative by nature, so a missing structure-edit playbook compounds quickly. Every additional custom card or extra legend line increases the chance of layout regressions unless the skill has concrete guardrails.
- **Suggested approach:**
  1. Extend `skills/ha-lovelace/SKILL.md` with a "Sections View Mutation Rules" section covering one-section-at-a-time edits, bulk-replacement risks, `max_columns` tuning, and `grid_options.rows` sizing for cards with legends, extrema, and multiple entities.
  2. Add known-good templates for common dense layouts: single-entity mini-graph, three-entity mini-graph, mushroom comparison grid, and bar-card comparison grid.
  3. Add a required visual verification checklist after each structural edit before making the next mutation.

### BL-021: Dashboard editing has no preflight entity validation, so broken cards ship first and get debugged later

- **Severity:** S3
- **Transcripts:**
  - T6:246-275 â€” the first dashboard render showed two "not found" cards because the model guessed `sensor.fan_vent_temperature` and `sensor.rec_room_temperature`; it had to grep live state and replace them with `sensor.upstairs_hallway_whole_house_fan_temperature` and `sensor.rec_room_ecobee_temperature`
- **Affected components:** `skills/ha-lovelace/SKILL.md`, `skills/ha-resolver/SKILL.md`
- **Description:** Unlike automation-writing flows, the dashboard workflow has no explicit step that resolves and validates every entity before a card is written. In the transcript, the dashboard rendered broken cards immediately because the model used plausible-but-wrong entity IDs. The recovery path was manual: search live state, infer the right entities, patch the dashboard, and re-render. That is avoidable. Dashboard configs should be linted against live entities before save whenever the edit is generated by the assistant.
- **Rationale:** A single wrong entity makes the UI look broken to the user even when most of the work is correct. Because dashboard work is highly visual, these failures are especially obvious and costly to user confidence.
- **Suggested approach:**
  1. Add a preflight validation step to `skills/ha-lovelace/SKILL.md`: every referenced entity must be verified via `hass-cli state get` or an explicit resolver lookup before save.
  2. Reuse `ha-resolver` patterns to offer nearest-match suggestions when a guessed entity ID does not exist.
  3. Add a small dashboard lint helper that scans a proposed view/card payload for missing entities before any save call is attempted.

### BL-022: No stable workflow exists for researching HACS custom-card capabilities after install

- **Severity:** S4
- **Transcripts:**
  - T6:40-75 â€” the model had to web-search for compact temperature-card options because the skill provided no local guidance on relevant HACS cards
  - T6:383-386 â€” when the user asked for detailed `mini-graph-card` options, fetching the GitHub README hit `429`
  - T6:386-388 â€” the model recovered by falling back to `gh api repos/kalkih/mini-graph-card/readme`
- **Affected components:** `skills/ha-lovelace/SKILL.md`
- **Description:** Once the user moved beyond native cards, the assistant had no stable in-repo workflow for answering detailed questions about installed custom cards. It had to discover candidate cards by web search, install them through HACS, then query GitHub live to explain supported options. That worked only after an additional fallback when GitHub fetch returned `429`. The capability gap is not the install itself; it is the absence of a deterministic reference path after install, so the assistant cannot reliably answer configuration questions without live web lookups.
- **Rationale:** Custom cards are central to advanced Lovelace work. If the assistant cannot reliably answer option-level questions without ad hoc browsing, every dashboard design session becomes slower and more fragile.
- **Suggested approach:**
  1. Add a Lovelace custom-card workflow section documenting preferred fallback order: local installed resources or repo metadata first, GitHub API second, generic web search last.
  2. Add concise reference notes for the most common cards this plugin is likely to recommend (`mini-graph-card`, Mushroom, Bar Card), or generate/cache local summaries after installation.
  3. Document the post-install step needed to make newly installed frontend cards available before dashboard mutation begins.

---

## 9. Documentation & UX

### BL-017: `common-patterns.md` uses deprecated 2023 YAML syntax throughout

- **Severity:** S5
- **Transcripts:** None (discovered during code review of BL-006/BL-014 changes)
- **Affected components:** `skills/ha-automations/references/common-patterns.md`
- **Description:** The common-patterns reference file still uses pre-2024 syntax: `platform:` instead of `trigger:`, `service:` instead of `action:`, and singular `trigger:`/`action:` as list keys instead of `triggers:`/`actions:`. This contradicts the "Home Assistant 2024+ (current)" schema version declared at the top of `yaml-syntax.md`. The model may copy deprecated patterns from this file into generated automations.
- **Rationale:** `yaml-syntax.md` and `common-patterns.md` are both referenced from `ha-automations/SKILL.md` step 5. Having one file on 2024+ syntax and the other on 2023 syntax sends conflicting signals.
- **Suggested approach:**
  1. Update all examples in `common-patterns.md` to 2024+ syntax (`triggers:`, `trigger:`, `actions:`, `action:`).
  2. Add a regression eval case verifying `common-patterns.md` does not contain `platform:` or `service:` (the deprecated keys).

### BL-018: `ha-resolver/SKILL.md` uses `--no-headers` with `service list`

- **Severity:** S5
- **Transcripts:** None (discovered during code review of BL-006/BL-014 changes)
- **Affected components:** `skills/ha-resolver/SKILL.md` (line ~197)
- **Description:** The Service Discovery section includes `hass-cli service list --no-headers | wc -l` for counting services. Per known gotchas (documented in CLAUDE.md and MEMORY.md), `--no-headers` only works with `entity list` — not `state list`, `device list`, or `service list`. The command will silently ignore the flag, producing an off-by-one count.
- **Rationale:** Minor (service count is informational only), but contradicts the plugin's own documented gotchas.
- **Suggested approach:**
  1. Replace `hass-cli service list --no-headers | wc -l` with `hass-cli service list | tail -n +2 | wc -l` (skip header line with awk/tail).

---

## 10. Agent UX

### BL-028: HA should auto-pull on git push instead of polling on a timer

- **Severity:** S3
- **Transcripts:**
  - T2:435-479, T2:1624-1702 — After pushing config changes, the model had no way to trigger or verify Git Pull sync; HA only picks up changes on the next polling cycle
- **Affected components:** `skills/ha-deploy/SKILL.md`, `skills/ha-onboard/SKILL.md`, HA-side configuration
- **Description:** The current deploy workflow pushes to the git remote and then waits for HA's Git Pull add-on to poll for changes on its configured interval. This creates BL-004 (no sync trigger) and BL-005 (stale verification). A better architecture would have HA listen for push events (e.g., via a GitHub/Gitea webhook calling an HA automation or the Git Pull add-on's webhook endpoint) so that config is pulled immediately after the plugin pushes. This eliminates the polling delay entirely and makes post-deploy verification reliable.
- **Rationale:** This is a root-cause fix for the deploy timing issues (BL-004, BL-005). If HA pulls immediately on push, there's no need for a trigger helper or pre/post-sync verification distinction. The Git Pull add-on already supports webhook triggers — the gap is that ha-onboard doesn't set this up and ha-deploy doesn't document or rely on it.
- **Suggested approach:**
  1. Research whether the Git Pull add-on supports a webhook trigger endpoint (it likely does via `/api/webhook/<id>`).
  2. Update `skills/ha-onboard/SKILL.md` to include webhook setup as part of initial configuration: create a webhook-triggered automation that calls the Git Pull add-on, configure the git hosting provider (GitHub, Gitea, etc.) to POST to that webhook on push.
  3. Update `skills/ha-deploy/SKILL.md` to expect near-instant sync when webhook is configured, with polling fallback documented for setups without it.
  4. If BL-004's helper is still needed (for non-webhook setups), keep it as the fallback path.

---

### BL-016: Long-running agents provide no progress indication

- **Severity:** S3
- **Transcripts:**
  - T5:57-59 — The naming-analyzer agent took 8 minutes 16 seconds with 34 tool uses and 84.1k tokens: `home-assistant-assistant:naming-analyzer(Audit HA entity naming) ⎿ Done (34 tool uses · 84.1k tokens · 8m 16s)`. During this time, the user saw nothing — no intermediate output, no progress updates, no indication of what phase the agent was in.
- **Affected components:** `agents/naming-analyzer.md`, all long-running agents
- **Description:** Subagents (launched via the Agent/Task tool) run as black boxes — the user sees "Running..." and then the final result. For agents that take 5+ minutes (naming-analyzer, ha-log-analyzer), this creates anxiety about whether the agent is stuck, making progress, or has errored silently. Claude Code's Task tool doesn't support streaming, so agents can't provide real-time updates.
- **Rationale:** This is a platform limitation (Claude Code Task tool doesn't stream agent output), but the skill can mitigate it by setting expectations upfront.
- **Suggested approach:**
  1. Update `skills/ha-naming/SKILL.md` to include an estimated duration message before launching the naming-analyzer: "Running naming audit — this typically takes 5-10 minutes for setups with 500+ entities."
  2. Consider breaking the naming-analyzer into phases (convention detection → violation scan → plan generation) with intermediate results shown to the user between phases, rather than running as a single monolithic agent call.

---

## 11. Editing Conventions

### BL-029: No editing conventions section to prevent unwanted restructuring

- **Severity:** S3
- **Transcripts:** User feedback (2026-03-15)
- **Affected components:** Multiple skills (ha-lovelace, ha-config, ha-automations, ha-naming)
- **Description:** When making dashboard or document edits, the model sometimes reorganizes, merges, or restructures adjacent content beyond what was explicitly requested. There is no documented convention constraining edits to only the specific changes asked for.
- **Rationale:** Users expect precise, minimal edits. Unrequested restructuring can break working configurations and create unexpected side effects.
- **Suggested approach:**
  1. Add an "Editing Conventions" section to relevant skills (or to `references/safety-invariants.md` as a cross-cutting rule) stating: "When making dashboard or document edits, make only the specific changes requested. Do not reorganize, merge, or restructure adjacent content unless explicitly asked."

### BL-030: No post-edit verification convention for YAML config changes

- **Severity:** S3
- **Transcripts:** User feedback (2026-03-15)
- **Affected components:** `skills/ha-automations/SKILL.md`, `skills/ha-scripts/SKILL.md`, `skills/ha-scenes/SKILL.md`, `skills/ha-config/SKILL.md`
- **Description:** After editing YAML config files, the model does not consistently trigger deployment/reload to verify changes appear on the dashboard. Entity IDs are not always verified against the actual HA instance before use. The ha-lovelace skill now has entity preflight (BL-021) and save contract (BL-019), but similar discipline is missing from YAML-mode config editing workflows.
- **Rationale:** Changes to YAML config files are not live until deployed and reloaded. Without a verification step, users may believe changes are active when they are not.
- **Suggested approach:**
  1. Add post-edit verification guidance to YAML-editing skills: after editing config files, prompt the user to deploy via `/ha-deploy` and verify the changes are live.
  2. Add entity preflight validation to automation/script/scene creation workflows (cross-reference ha-resolver for entity resolution before writing YAML).

---

## 12. Storage Dashboard Reference Repair

### BL-031: No tool to scan and fix broken entity references in storage dashboards after renames

- **Severity:** S4
- **Transcripts:**
  - T7:1388-2385 — After 203 entity renames, storage-mode dashboard cards showed "Entity not found." Claude spent ~45 minutes fixing references: first via 50+ individual Chrome browser clicks (slow, error-prone), then via JavaScript WebSocket calls (faster but caused side effects — wrong entities replaced, e.g., `sensor.attic_temperature` → `sensor.garage_temperature` which then had to be reverted).
  - T9:14-89 — Adding new sensor entities to dashboards, Claude used direct Edit tool on YAML files without loading ha-lovelace skill; user had to correct the approach.
- **Affected components:** `skills/ha-lovelace/SKILL.md`, `skills/ha-apply-naming/SKILL.md`, `helpers/`
- **Description:** BL-019/020/021 addressed dashboard save contracts, safe editing, and entity preflight validation for *new* dashboard edits. But there is no tool for the *post-rename repair* workflow: scanning existing storage dashboards for broken entity references, showing which references are broken, and applying a rename map (old_id → new_id) across all cards/views. This is distinct from BL-021 (which validates before saves) — this is about repairing existing dashboards after bulk entity renames. Storage dashboards live in HA's `.storage/lovelace*` files (not in git), so YAML editing doesn't apply.
- **Rationale:** Any user running ha-apply-naming with storage-mode dashboards will hit this. The transcript showed ~45 minutes of manual repair work that could be automated with a helper that fetches config via WebSocket, applies a rename map, and saves back with dry-run preview.
- **Suggested approach:**
  1. Create a `helpers/dashboard-refs.py` helper that: fetches storage dashboard config via WebSocket (`lovelace/config`), scans all cards for entity references, reports broken ones, applies find-and-replace for renamed entities (with dry-run preview), and saves back via WebSocket (`lovelace/config/save`).
  2. Integrate into ha-apply-naming post-execution: after renames complete, scan storage dashboards and offer to fix broken references.
  3. Reference ha-mcp's `tools_config_dashboards.py` for patterns: `ha_dashboard_find_card` searches for entity refs within dashboards; multi-pass entity resolution collects missing entities; incremental save avoids "error: 3".

---

## 13. Timestamp & Timezone Handling

### BL-032: Displayed timestamps show raw UTC without timezone conversion or labeling

- **Severity:** S3
- **Transcripts:**
  - T2:963-965 — Claude reported automation fire times as "5:36 PM" and "5:41 PM" when timestamps were UTC. User corrected: Pacific time with DST (UTC-7), actual times were 10:36 AM / 10:41 AM.
- **Affected components:** `skills/ha-troubleshooting/SKILL.md`, `skills/ha-automations/SKILL.md`, any skill displaying timestamps
- **Description:** hass-cli and the HA REST API return timestamps in UTC. The model displays them as-is without converting to the user's local timezone or labeling them as UTC. This creates confusion when users interpret timestamps as local time. The user's timezone is available from HA config (`zone.home` attributes include timezone).
- **Rationale:** Any troubleshooting or trace analysis session involves reading timestamps. Misinterpreted timestamps lead to wrong conclusions about when events occurred.
- **Suggested approach:**
  1. Detect user timezone from HA config during session: `hass-cli -o json state get zone.home` includes timezone attribute.
  2. Add guidance to skills that display timestamps: always convert UTC → local and label with timezone (e.g., "10:36 AM PDT").
  3. Consider a small utility function in an existing helper that handles the conversion.
  4. Note: ha-mcp's `tools_history.py` includes relative time *input* parsing (24h, 7d → timedelta → ISO) but also lacks *output* timezone conversion — this is a gap in both projects.

---

## 14. Skill Routing & Auto-Selection

### BL-033: Dashboard requests don't auto-select ha-lovelace skill

- **Severity:** S3
- **Transcripts:**
  - T9:14-52 — User said "add the IKEA sensor to my dashboards." Claude used direct Edit tool on YAML dashboard files without loading ha-lovelace skill. User had to correct: "use the right skill for dashboards."
  - T8:89-105 — Claude took 4 unnecessary browser actions before reading the YAML file to verify dashboard state; should have read config first.
- **Affected components:** `skills/ha-lovelace/SKILL.md`, plugin-level skill routing
- **Description:** When the user requests dashboard modifications, the model sometimes bypasses the ha-lovelace skill and uses generic Edit tool on YAML files directly. The ha-lovelace skill has entity preflight validation, save contracts, and sections-view guidance that the direct Edit path lacks. The skill should be automatically selected for any request involving dashboards, Lovelace, cards, or views.
- **Rationale:** Every dashboard edit made without the skill bypasses the safety and quality gates added in BL-019/020/021.
- **Suggested approach:**
  1. Add skill-routing guidance to `skills/ha-lovelace/SKILL.md` trigger section or to a plugin-level routing note: "For any request involving dashboards, Lovelace, cards, or views → load ha-lovelace skill before using Edit tool on dashboard YAML."
  2. Consider adding dashboard file paths to the ha-lovelace skill's trigger patterns so it activates automatically.

---

## 15. Browser Automation Reliability

### BL-034: Browser automation against HA web UI is fragile and wastes time before falling back to API

- **Severity:** S3
- **Transcripts:**
  - T2:338-385 — Chrome extension disconnected mid-Z-Wave UI navigation
  - T7:2937-2960 — Form field focus unreliable during Reolink camera setup; IP entered into password field 3 times before user took over
  - T11:1080-1172 — Accessibility tree issues during Expose Entities flow; eventually used JavaScript API instead
  - T11:505-650 — 25 minutes trying to automate Alexa sign-in via browser before pivoting to manual approach
- **Affected components:** `skills/ha-devices/SKILL.md`, `skills/ha-troubleshooting/SKILL.md`
- **Description:** HA's web UI uses Shadow DOM and web components that are inherently hostile to browser automation. Across 4 transcripts, browser automation failed for Z-Wave node management, integration config flows, entity exposure settings, and form-filling. In every case, Claude eventually fell back to API calls or manual step-by-step instructions — but only after spending 10–25 minutes on failed browser attempts.
- **Rationale:** The pattern is consistent: browser automation attempts fail, time is wasted, then the API or manual approach works. Skills should guide toward API-first, browser-last.
- **Suggested approach:**
  1. Add guidance to ha-devices and ha-troubleshooting: "HA's web UI uses Shadow DOM. Browser automation is unreliable for: Z-Wave node management, integration config flows, entity exposure settings, third-party auth flows. Use REST/WebSocket APIs as primary path; provide numbered manual steps when no API exists."
  2. When browser automation fails on the first attempt, immediately switch to API or manual instructions instead of retrying.

---

## 16. Analysis & Troubleshooting UX

### BL-035: Analysis that discovers problems doesn't proactively offer fix options

- **Severity:** S3
- **Transcripts:**
  - T1:467-593 — Analysis found duplicate notification bug (camera person-detection flicker causing 2 notifications in 11 seconds). Claude explained the root cause but didn't offer fix options until the user asked "can you explain mode: single?" Only then did Claude suggest a 60-second cooldown delay.
  - T2:770-847 — User reported "my old codes don't work" after Z-Wave re-inclusion. Claude investigated but session ended without confirming the codes were restored or providing a recovery path.
- **Affected components:** `skills/ha-troubleshooting/SKILL.md`, `skills/ha-analyze/SKILL.md`
- **Description:** When ha-troubleshooting or ha-analyze discovers an issue, the model sometimes stops at diagnosis without offering actionable remediation options. The user has to ask follow-up questions to get solutions. Additionally, sessions can end with unresolved issues and no explicit confirmation that the problem was fixed.
- **Rationale:** Users call troubleshooting skills because they want problems fixed, not just diagnosed. The gap between "here's what's wrong" and "here are 3 ways to fix it" should be closed automatically.
- **Suggested approach:**
  1. Update ha-troubleshooting and ha-analyze to require: when a problem is identified, immediately present 2–3 solution options with tradeoffs (e.g., "Option A: 60s cooldown [simple, may miss real events]. Option B: debounce helper [configurable, more complex]").
  2. Add a "close the loop" convention: before ending a session with an unresolved issue, explicitly ask "Can you confirm X is working now?"

---

## 17. Config Generation Prerequisites

### BL-036: Automations generated with placeholder entity IDs before prerequisites are confirmed

- **Severity:** S3
- **Transcripts:**
  - T10:269-272 — Generated 3 automations with hardcoded placeholders like `media_player.rec_room_echo` and `event.top_of_stairs_button` before the user had paired the Aqara button or installed Alexa Media Player. When prerequisites changed, all three automations had to be rewritten.
  - T11:1544-1550 — Assumed Aqara button would create an `event.*` entity (it didn't) and command name was `remote_button_short_press` (actual: `single`). Required 20+ minutes of debugging to discover the real trigger.
- **Affected components:** `skills/ha-automations/SKILL.md`, `skills/ha-devices/SKILL.md`
- **Description:** The model generates complete YAML automations referencing entities that don't yet exist, assuming the user will complete prerequisites later. When the real entities turn out to have different IDs or different capabilities than assumed, the automations must be rewritten. This extends BL-007 (entity existence validation) to cover the case where entities don't exist *yet* — the model should wait for them rather than guessing.
- **Rationale:** Generating config with placeholder IDs creates rework. For new device integrations, the actual entity IDs, event types, and command names are only known after the device is paired and interviewed.
- **Suggested approach:**
  1. Add to ha-automations: "When automations reference devices not yet integrated, do not write final YAML. Instead, document the planned automation structure and list prerequisites. Only generate YAML after all referenced entities are confirmed to exist."
  2. Add to ha-devices: "After device pairing, verify actual entity IDs and event types via `hass-cli -o json entity list` before proceeding to automation creation."

---

## 18. Jinja Template Portability

### BL-037: Generated Jinja templates use platform-specific strftime format codes

- **Severity:** S5
- **Transcripts:**
  - T2:561 — Automation includes `{{ now().strftime('%-I:%M %p') }}`. The `%-I` format (no-pad hour) is a GNU libc extension and is not portable to Windows or some musl-based systems.
- **Affected components:** `skills/ha-automations/SKILL.md`, `skills/ha-jinja/SKILL.md`, `templates/templates.md`
- **Description:** The `%-I` strftime format code removes leading zeros from the hour but is Linux-specific. On Windows HA instances (rare but possible) or in certain Python builds, this raises a `ValueError`. The portable alternative is `%I` (zero-padded) with `.lstrip('0')` or using `{{ now().hour % 12 or 12 }}` directly.
- **Rationale:** Most HA instances run on Linux where this works fine. Low severity, but worth noting for template reference material.
- **Suggested approach:**
  1. Note in ha-jinja or templates.md that `%-` format codes are not portable; recommend `%I` with `.lstrip('0')` for no-pad formatting.
