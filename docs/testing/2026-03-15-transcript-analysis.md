# Transcript Analysis: Plugin Performance Review (March 2026)

**Date:** 2026-03-15
**Analyst:** Claude (Opus 4.6)
**Scope:** 11 Claude Code session transcripts from `~/dev/ha` (March 7–15, 2026)
**Previous round:** `2026-02-18-manual-test-analysis.md` (single troubleshooting transcript)

This round covers onboarding, analysis, naming/renaming, dashboards, automations, and device integration workflows. Findings are cross-referenced against `~/dev/ha-mcp` (ha-mcp MCP server, v6.6.1, 95+ tools) for capabilities that could be ported or adapted.

---

## Transcripts Analyzed

| # | Date | File | Size | Primary Workflow |
|---|------|------|------|-----------------|
| 1 | Mar 7 | `2026-03-07-133844-*ha-onboa*.txt` | 67KB | `/ha-naming` audit (672 entities, 14 areas) |
| 2 | Mar 7 | `2026-03-07-170833-*ha-onboa*.txt` | 58KB | `/ha-apply-naming` execution (112 renames, 9 phases) |
| 3 | Mar 7 | `2026-03-07-180934-*ha-analy*.txt` | 71KB | `/ha-analyze` + shade timing + Z-Wave lock troubleshooting |
| 4 | Mar 8 | `2026-03-08-104445-*ha-analy*.txt` | 108KB | Z-Wave lock re-inclusion + lock automations |
| 5 | Mar 8 | `2026-03-08-174642-implement*.txt` | 46KB | Notification polish (deep links, cooldown) |
| 6 | Mar 12 | `2026-03-12-163104-this-session*.txt` | 31KB | Dashboard card exploration (mini-graph, mushroom) |
| 7 | Mar 13 | `2026-03-13-181110-*ha-naming*.txt` | 135KB | Large naming execution (203 renames) + dashboard fixes + camera |
| 8 | Mar 15 | `2026-03-15-084839-this-session*.txt` | 10KB | Camera dashboard finalization |
| 9 | Mar 15 | `2026-03-15-092628-add-the-ikea*.txt` | 9KB | Add IKEA sensor to dashboards |
| 10 | Mar 15 | `2026-03-15-124402-implement*.txt` | 141KB | White noise automation (placeholder config) |
| 11 | Mar 15 | `2026-03-15-144436-implement*.txt` | 155KB | Alexa + Aqara button integration |

**Total transcript volume:** ~870KB across 11 sessions

---

## Findings

### F1. ha-apply-naming Blocked by `disable-model-invocation` Flag

**Severity:** CRITICAL | **Transcripts:** #7 | **Time wasted:** ~45 min

User called `/ha-apply-naming`. The Skill tool rejected it: *"Error: Skill home-assistant-assistant:ha-apply-naming cannot be used with Skill tool due to disable-model-invocation."* Claude then manually reimplemented the entire execution workflow using bash + Python + hass-cli — rebuilding what the skill already does.

The flag was designed to prevent the model from inventing rename operations on its own, but it also blocks legitimate user-initiated execution. The user even noted: *"you should be able to call the ha-apply-naming yourself even though I can't"* (line 379).

**Options to consider:**
- Remove the flag and rely on the skill's own safety gates (dry-run default, confirmation prompts)
- Create a wrapper execution path that bypasses the flag for user-initiated invocations
- The current design makes the skill effectively unusable

**ha-mcp note:** ha-mcp's `ha_rename_entity` handles renames directly via WebSocket `config/entity_registry/update` — no intermediate skill layer. Could be ported as a lightweight Python helper that sidesteps this issue entirely.

---

### F2. Storage Dashboard Entity References Require Manual Browser Editing

**Severity:** CRITICAL | **Transcripts:** #6, #7, #9 | **Time wasted:** ~60 min across sessions

After entity renames, storage-mode dashboard cards showed "Entity not found." Claude had to fix them via:
1. 50+ individual Chrome browser clicks (slow, error-prone)
2. JavaScript WebSocket calls (faster, but caused side effects — wrong entities replaced)
3. In transcript #6, dashboard saves repeatedly failed with cryptic "error: 3" before discovering incremental saves were needed

The plugin has no tool for scanning or updating entity references in storage dashboards. Storage dashboards live in HA's `.storage/lovelace*` files (not in git), so the existing YAML-editing workflow doesn't apply.

**What would help:** A helper that fetches storage dashboard config via WebSocket, scans all cards for entity references, reports broken ones, applies find-and-replace for renamed entities (with dry-run preview), and saves back.

**ha-mcp note:** `tools_config_dashboards.py` (2100+ lines) has full dashboard CRUD via WebSocket, including card-level operations and entity reference scanning. The `ha_dashboard_find_card` tool searches for entity references within dashboards. Key patterns:
- Multi-pass entity resolution (scan cards → validate entities → collect missing)
- Safe regex-based entity ID replacement in card configs
- Incremental save pattern (clear sections → add one-by-one) to avoid "error: 3"
- `dashboard_guide.md` and `card_types.json` as reference data

---

### F3. Git Pull Sync Delays and Failures

**Severity:** MAJOR | **Transcripts:** #3, #4, #9, #11 | **Time wasted:** ~40 min across sessions

After git push, the Git Pull add-on didn't sync reliably. Observed across multiple sessions:
- Blind waiting with repeated `automation.reload` calls (5+ iterations in transcript #4)
- 401 errors when trying to trigger Git Pull via supervisor API (transcript #9)
- Complete sync failure requiring REST API bypass to create automations directly (transcript #11)
- No feedback on sync status — just checking if automations appeared

The long-lived access token lacks Supervisor API scope, so `hass-cli raw post /api/hassio/addons/core_git_pull/start` fails with 401. The plugin has no alternative mechanism to trigger or monitor sync.

**What would help:**
- Pre-flight check in ha-deploy: test supervisor API access early; if 401, skip addon trigger and tell user the expected wait time
- A polling helper that checks sync status instead of blind waiting
- Documented expected sync lag in the ha-deploy skill
- REST API fallback for immediate automation creation (as Claude did in transcript #11)

**ha-mcp note:** ha-mcp uses direct WebSocket API for automation CRUD (`ha_config_set_automation`), bypassing the git→pull→reload cycle entirely.

---

### F4. Entity ID Resolution Before Actions

**Severity:** MAJOR | **Transcripts:** #6, #9, #10, #11 | **Time wasted:** ~30 min across sessions

Repeated pattern of generating config that references entities without confirming they exist:
- **#6:** Dashboard demo had wrong entity IDs (`sensor.fan_vent_temperature` should be `sensor.upstairs_hallway_whole_house_fan_temperature`). Cards showed "not found."
- **#9:** Gauge cards added without validating entity existence first.
- **#10:** Automations generated with placeholder entity IDs (`media_player.rec_room_echo`) that didn't exist yet.
- **#11:** Assumed Aqara button creates `event.*` entity (it didn't) and command name was `remote_button_short_press` (actual: `single`).

The ha-resolver skill is agent-preloadable but not consistently invoked before config generation. Skills generate YAML referencing entities without confirming they exist.

**What would help:** A mandatory entity validation step before generating any automation/dashboard config. Skill guidance in ha-automations, ha-scripts, ha-scenes, ha-lovelace should explicitly require validating entity IDs. For new devices: flag when entity IDs are placeholders and don't write YAML until prerequisites are confirmed.

**ha-mcp note:** `smart_search.py` has `smart_entity_search(query, limit, domain_filter)` with fuzzy matching. The `FuzzyEntitySearcher` in `fuzzy_search.py` uses pure Python `difflib.SequenceMatcher` (no external deps) with multi-factor scoring — room keyword boosting, device type boosting, partial/token matching. Could be ported as a standalone helper.

---

### F5. Naming Plan Collision Detection Missing

**Severity:** MAJOR | **Transcripts:** #7 | **Time wasted:** ~15 min

Entity rename execution succeeded 185/203, but 18 failed with "already registered" errors:
- 17 were Shelly `wave_1_mini_*` entities where `_2` suffixed variants were renamed first, then non-`_2` variants collided with the same target names
- 1 was LG TV → `living_room_tv` colliding with an existing Chromecast entity

The naming plan audit checked source names but not whether target names would collide with each other or with existing entities during batch execution. The plan needed manual mid-execution correction.

**What would help:** Target collision check during the audit phase — collect ALL target names from the plan, detect duplicates, flag as "collision risk." A dry-run simulation that attempts all renames in order and reports collisions before live execution.

---

### F6. hass-cli Command Gaps and Failures

**Severity:** MAJOR | **Transcripts:** #2, #5, #7, #9 | **Time wasted:** ~25 min across sessions

Multiple hass-cli operations failed, with Claude trying 2–3 approaches each time before finding one that worked:

| Command | Issue | Transcript |
|---------|-------|-----------|
| `hass-cli entity delete` | Doesn't exist | #2 |
| `hass-cli raw ws` | Broken on HA 2026.2+ | #7 (already known) |
| Trace API endpoints | 404 — wrong URL guesses | #5 |
| Supervisor API | 401 unauthorized | #9 |
| History API | 400 bad request (malformed query) | #5 |

The fallback that worked was always Python scripts using REST API directly.

**What would help:** Expand `references/hass-cli.md` with a "known broken/missing" section listing commands that don't work alongside their Python API alternatives. Standardize the fallback pattern: when hass-cli fails, go straight to Python REST/WebSocket instead of trying more hass-cli syntaxes.

**ha-mcp note:** ha-mcp uses direct REST/WebSocket for everything, never hass-cli. Key endpoints worth documenting:
- Entity delete: WebSocket `config/entity_registry/remove`
- Traces: WebSocket `trace/list` + `trace/get` (entity_id → unique_id resolution needed)
- History: WebSocket `history/history_during_period`
- Supervisor: REST `/api/hassio/addons/{slug}/start` (requires supervisor scope)

---

### F7. Timezone Handling Errors

**Severity:** MODERATE | **Transcripts:** #4

Claude reported automation fire times as "5:36 PM" and "5:41 PM" when timestamps were actually UTC. User corrected: Pacific time with DST (UTC-7), so actual times were 10:36 AM / 10:41 AM.

No timezone conversion utility exists. hass-cli and REST API return UTC timestamps; Claude displayed them as-is without labeling.

**What would help:** Detect user timezone from HA config (`hass-cli -o json state get zone.home` includes timezone). A utility to convert UTC → local. Always label timestamps with zone.

**ha-mcp note:** `tools_history.py` includes relative time parsing (24h, 7d, 2w → timedelta → ISO) but doesn't convert output timestamps either. Gap in both projects.

---

### F8. Browser Automation Fragility

**Severity:** MODERATE | **Transcripts:** #4, #7, #11 | **Time wasted:** ~20 min across sessions

Recurring problems with Chrome browser automation against HA's web UI:
- Chrome extension disconnected mid-Z-Wave UI navigation (#4)
- Form field focus unreliable during camera setup — IP went into password field 3 times (#7)
- Accessibility tree issues during Expose Entities flow (#11)

HA's web UI uses Shadow DOM and web components that are inherently hostile to browser automation. In every case, Claude eventually fell back to API calls or manual step-by-step instructions.

**What would help:** Skill guidance that prioritizes API-first, browser-last. Document which HA operations are hostile to browser automation (Z-Wave node management, integration config flows, entity exposure settings). When browser automation fails, immediately provide numbered manual steps instead of retrying.

---

### F9. Specification Drift Between Naming Docs and Plans

**Severity:** MODERATE | **Transcripts:** #1

The naming.md spec said "Never rename diagnostic entities" (Tier 3), but the generated naming-plan.yaml renamed ALL diagnostic entities with area prefixes. The user's actual historical practice already contradicted the spec. Claude had to manually discover and reconcile this contradiction mid-session.

**What would help:** Pre-audit spec validation — check that naming.md is internally consistent before running the analyzer. Post-plan generation check — verify the plan doesn't violate spec rules; flag conflicts as "spec drift detected."

---

### F10. No Proactive Solution Offering

**Severity:** MODERATE | **Transcripts:** #4, #5

Two instances where analysis found problems but didn't offer solutions until the user asked:
- **#5:** Discovered duplicate notification bug (camera person-detection flicker causing 2 notifications in 11s), but didn't offer fix options until user asked "can you explain mode: single?"
- **#4:** User reported "my old codes don't work" after Z-Wave re-inclusion. Claude investigated but session ended without confirming resolution.

**What would help:** When analysis reveals a problem, immediately present 2–3 solution options with tradeoffs. Before ending a session with unresolved issues, explicitly ask "Can you confirm X is working now?"

---

### F11. Friendly Name Override Sync Failure

**Severity:** MODERATE | **Transcripts:** #2

After renaming device "Rat Room" → "Rec Room," friendly names didn't auto-update. Root cause: entities had custom name overrides from earlier renames. Had to clear overrides via Python API to let them inherit from the new device name.

This is a hidden gotcha — users expect device rename to cascade to entity friendly names, but custom overrides silently prevent it.

**What would help:** Pre-rename scan that detects entities with custom friendly_name overrides. Warning before proceeding: "10 entities have custom names that won't auto-update. Clear them?"

**ha-mcp note:** `ha_set_entity` supports setting `name=None` to clear custom overrides and revert to device-generated names.

---

### F12. Wrong Skill Auto-Selection for Dashboards

**Severity:** MODERATE | **Transcripts:** #9

User said "add the IKEA sensor to my dashboards." Claude used direct Edit tool on YAML files without loading ha-lovelace skill first. User had to correct: "use the right skill for dashboards."

**What would help:** Skill-routing guidance in SKILL.md files or plugin-level routing: "For any request involving dashboards, Lovelace, cards, or views → load ha-lovelace skill first."

---

### F13. Token/Usage Limit Hit Mid-Session

**Severity:** MODERATE | **Transcripts:** #2

During Phase 6 of naming execution, Claude hit the usage limit: *"You're out of extra usage · resets 4pm."* Lost context briefly; user had to say "proceed" to continue.

**What would help:** For large operations, estimate scope before execution and warn if it looks heavy. A checkpoint pattern — after every N operations, save progress to a file so work can resume if interrupted.

---

### F14. Excessive Verification Loops After Deploy

**Severity:** MINOR | **Transcripts:** #4

After deploying changes, Claude checked if automations were loaded 5 times in quick succession, finding nothing each time until sync completed minutes later. Repetitive and noisy.

**What would help:** Wait once (10s), check once. If not synced, explain expected wait time and offer to check again in 1–2 minutes. Don't loop.

---

### F15. Jinja Template Portability

**Severity:** MINOR | **Transcripts:** #4

Automation used `{{ now().strftime('%-I:%M %p') }}` — the `%-I` format (no-pad hour) is Linux-specific and may fail on Windows HA instances.

**What would help:** Use `%I` (standard, zero-padded) or `{{ now().strftime('%I:%M %p').lstrip('0') }}` for portable formatting. Note: most HA instances run on Linux, so this is low-risk but worth noting.

---

## What Worked Well

These patterns should be preserved and reinforced:

| Pattern | Transcripts | Notes |
|---------|-------------|-------|
| **Evidence tables** in validation output | #5, #7 | Clear "what ran vs skipped" format |
| **Dry-run before execution** | #2, #7 | Complete preview with risk assessment before destructive operations |
| **Graceful pivoting** when approaches fail | #4, #11 | Alexa auth → HA Cloud + Routines; hass-cli → Python API |
| **Systematic root cause analysis** | #3, #4, #5 | Z-Wave diagnostics, camera flicker forensics, mode:single deep-dive |
| **Minimal surgical edits** | #5 | Precise Edit tool usage, no adjacent restructuring (invariant #7) |
| **Educational explanations** | #4, #5, #6 | mode:single, automation entity IDs, card design tradeoffs |
| **Responsive refinement** | #4 | "don't need notifications every time" → immediate targeted fix |
| **Visual comparison** for dashboards | #6 | Side-by-side card type demos (20-card showcase) |
| **Post-deployment verification** | #4, #5 | Checked execution history, confirmed success via user |
| **Git checkpoint commits** | #2, #7 | Pre-rename backup commits for easy rollback |
| **Batch execution with spot-checks** | #2, #7 | Verify samples after each phase, not just at the end |
| **Architecture pivot under constraints** | #11 | input_boolean + Alexa Routines when direct media_player auth failed |

---

## ha-mcp Integration Opportunities

Components from `~/dev/ha-mcp` worth considering as ports or adaptations:

| ha-mcp Component | Source File | What It Does | Why It's Relevant |
|-----------------|------------|-------------|-------------------|
| **Fuzzy entity search** | `utils/fuzzy_search.py` (340 lines) | Pure Python difflib-based multi-factor entity matching with room/device boosting | Addresses F4 — replace hass-cli grep patterns for entity resolution |
| **Dashboard entity scanner** | `tools/tools_config_dashboards.py` | Find/replace entity refs in storage dashboards via WebSocket | Addresses F2 — the biggest time sink across sessions |
| **Trace fetching (WebSocket)** | `tools/tools_traces.py` | entity_id → unique_id resolution, diagnostic suggestions when empty | Addresses F6 — trace API was a repeated failure point |
| **History API (WebSocket)** | `tools/tools_history.py` | Relative time parsing, proper API response normalization (lc/lu short-form) | Addresses F6 — history API calls failed with bad queries |
| **Automation normalization** | `tools/tools_config_automations.py` | Context-aware field mapping (triggers/trigger at root only, preserve plural in choose/if blocks) | Reference material for ha-automations skill |
| **Dashboard guide** | `resources/dashboard_guide.md` | Modern dashboard patterns (sections view, tile cards, feature types) | Reference material for ha-lovelace skill |
| **Card types reference** | `resources/card_types.json` | 41 built-in card types with doc URLs | Reference data for ha-lovelace skill |
| **Entity rename (WebSocket)** | `tools/tools_entities.py` | Batch rename via `config/entity_registry/update`, clear name overrides with `name=None` | Addresses F1 (bypass skill flag) and F11 (friendly name overrides) |

---

## Summary

**By the numbers:**
- 15 findings total: 2 critical, 5 major, 6 moderate, 2 minor
- ~325 minutes of estimated wasted time across all sessions
- Top 3 time sinks: storage dashboard editing (~60 min), ha-apply-naming blocked (~45 min), Git Pull sync (~40 min)

**Recurring themes:**
1. **Missing tooling for storage dashboards** — the plugin is YAML-first but many users have storage-mode dashboards that aren't in git
2. **hass-cli limitations** — multiple commands are broken or missing; Python REST/WebSocket is the reliable fallback every time
3. **No pre-flight entity validation** — config gets written with wrong/missing entity IDs, then fails at runtime
4. **Git Pull sync is fragile** — the deploy→sync→reload cycle has no monitoring and fails silently

**Strongest patterns to keep:**
- Evidence tables, dry-run previews, git checkpoint commits
- Graceful pivoting when approaches fail
- Educational explanations that build user competence
- Systematic root cause analysis before suggesting fixes
