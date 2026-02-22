# MCP-to-Skills Migration Analysis

## Executive Summary

This analysis evaluates 97 MCP tools from [ha-mcp](https://github.com/homeassistant-ai/ha-mcp) against the current 15-skill Claude Code plugin architecture. The goal: identify which MCP tool capabilities should be absorbed into skills (as domain knowledge, hass-cli procedures, or reference material) versus which represent genuinely new functionality worth adding.

**Key finding:** The plugin already covers the *creative* and *knowledge-intensive* aspects of Home Assistant (automation design, naming conventions, config organization, troubleshooting). What it lacks are the *operational* capabilities — querying live state, managing organizational entities (areas, labels, groups), accessing history/statistics, and performing CRUD on dashboards and helpers via the API rather than file editing.

**Recommendation:** Don't replicate MCP tools as skills. Instead, enrich existing skills with the operational procedures the MCP tools encode, and add 3-4 new targeted skills for capability gaps. This preserves the plugin's token-efficiency advantage while closing functional gaps.

---

## Table of Contents

1. [Architecture Comparison](#1-architecture-comparison)
2. [Token Efficiency: Why Skills Win](#2-token-efficiency-why-skills-win)
3. [Capability Gap Analysis](#3-capability-gap-analysis)
4. [Detailed Tool-by-Tool Assessment](#4-detailed-tool-by-tool-assessment)
5. [Recommended Changes](#5-recommended-changes)
6. [New Skills to Create](#6-new-skills-to-create)
7. [Existing Skills to Enrich](#7-existing-skills-to-enrich)
8. [New References to Create](#8-new-references-to-create)
9. [Implementation Priority](#9-implementation-priority)
10. [What NOT to Do](#10-what-not-to-do)

---

## 1. Architecture Comparison

### ha-mcp (MCP Server)

- **97 tools** registered in the MCP tool schema
- Each tool = function signature + JSON schema + description loaded into context
- Communicates with HA via REST API + WebSocket API (Python `aiohttp`/`httpx`)
- Tools are stateless API wrappers with fuzzy search, error handling, and parameter coercion
- No domain knowledge — explicitly defers to "Agent Skills" for best practices
- Token cost: ~50-77K tokens for full tool schema (mitigated by Tool Search in 2026)

### home-assistant-assistant (Claude Code Plugin)

- **15 skills** (14 user-invocable + 1 infrastructure)
- Each skill = SKILL.md with domain knowledge, procedures, safety invariants
- Communicates with HA via `hass-cli` (CLI wrapper around REST API)
- Skills encode *how* and *why*, not just *what* — intent classification, capability checking, naming conventions
- Token cost: ~0 tokens at rest; 500-2000 tokens when a skill loads on demand
- 6 specialized agents for complex multi-step tasks

### Fundamental Difference

The MCP server is a **tool layer** — it provides 97 verbs (search, create, update, delete) that an LLM can call. It has no opinion on *when* to use which verb or *how* to compose them correctly.

The plugin is a **knowledge layer** — it teaches Claude *when* inactivity requires a `for:` trigger vs. a `delay:` action, *why* you should check `supported_color_modes` before setting color temperature, and *how* to structure a naming audit. It provides fewer verbs but makes each one more likely to produce correct output.

**These are complementary, not competing.** The analysis below identifies where MCP tool capabilities can be absorbed as procedures within skills.

---

## 2. Token Efficiency: Why Skills Win

### The Math

| Approach | Context Cost | Per-Use Cost | Knowledge Included |
|----------|-------------|-------------|-------------------|
| 97 MCP tools (no Tool Search) | ~50-77K tokens | ~200-500 tokens/call (JSON response) | None — raw API responses |
| 97 MCP tools (with Tool Search) | ~8.7K tokens | ~200-500 tokens/call + schema load | None — raw API responses |
| 15 skills (current plugin) | ~0 tokens at rest | ~500-2000 tokens when loaded | Full domain knowledge, patterns, safety |
| Enriched skills (proposed) | ~0 tokens at rest | ~800-2500 tokens when loaded | Domain knowledge + operational procedures |

### Why Not Just Use Both?

Using the MCP server alongside the plugin is technically possible but introduces problems:

1. **Redundant entity resolution** — Both the MCP's `ha_search_entities` and the plugin's `ha-resolver` skill solve the same problem differently
2. **Conflicting approaches** — MCP tools create automations via WebSocket API (`ha_config_set_automation`); the plugin creates them via file editing. Users get confused about which path was taken.
3. **Double context cost** — Even with Tool Search, 97 tool descriptions + 15 skill descriptions consume unnecessary context
4. **Safety invariant bypass** — MCP tools don't enforce the plugin's safety invariants (capability checking, no semantic substitution). A user could accidentally call `ha_config_set_automation` directly, bypassing the intent classifier.

### The Right Approach

Absorb the *procedures* (API calls, parameter formats, error handling patterns) from MCP tools into skill references. Claude already has `hass-cli` — many MCP tool operations map directly to `hass-cli` commands or can be expressed as `hass-cli raw` API calls.

---

## 3. Capability Gap Analysis

### What the Plugin Has That the MCP Doesn't

| Capability | Plugin Skill | MCP Equivalent |
|-----------|-------------|---------------|
| Intent classification (inactivity vs delay) | ha-automations + intent-classifier.md | None |
| Capability-aware YAML generation | ha-scenes, ha-automations | None |
| Naming audit + plan + apply workflow | ha-naming + ha-apply-naming | `ha_rename_entity` (single rename only) |
| Git-based deploy with validation | ha-deploy | None |
| Safety invariants (6 rules) | All skills reference safety-invariants.md | None |
| Config organization guidance | ha-config | None |
| Jinja templating guidance | ha-jinja | None |
| Dashboard design guidance | ha-lovelace | `ha_get_dashboard_guide()` (fetches static markdown) |
| Systematic troubleshooting with evidence tables | ha-troubleshooting | `ha_get_automation_traces` (raw data only) |
| Setup wizard with prerequisites check | ha-onboard | None |

### What the MCP Has That the Plugin Doesn't

| Capability | MCP Tool(s) | Current Plugin Gap |
|-----------|------------|-------------------|
| **Fuzzy entity search** | `ha_search_entities` | ha-resolver uses `hass-cli state list \| grep` (exact match only) |
| **System overview** | `ha_get_overview` | No equivalent — plugin has no "orientation" step |
| **Deep config search** | `ha_deep_search` | Plugin searches files with Grep, not API-level config |
| **Dashboard CRUD via API** | `ha_config_get/set_dashboard`, `ha_dashboard_find_card` | ha-lovelace is guidance only, no write capability |
| **Helper CRUD via API** | `ha_config_list/set/remove_helper` | Plugin edits YAML files for helpers |
| **Area/Floor management** | `ha_config_list/set/remove_area/floor` | No equivalent |
| **Label management** | `ha_config_get/set/remove_label`, `ha_manage_entity_labels` | No equivalent |
| **Group management** | `ha_config_list/set/remove_group` | No equivalent |
| **History/Statistics** | `ha_get_history`, `ha_get_statistics` | No equivalent (ha-troubleshooting uses raw API but limited) |
| **Automation traces** | `ha_get_automation_traces` | ha-troubleshooting mentions traces but limited procedure |
| **Template evaluation** | `ha_eval_template` | No equivalent |
| **Blueprint management** | `ha_list/get/import_blueprint` | No equivalent |
| **Camera snapshots** | `ha_get_camera_image` | No equivalent |
| **Backup/Restore** | `ha_backup_create/restore` | No equivalent |
| **System health** | `ha_get_system_health` | No equivalent |
| **HACS integration** | `ha_hacs_search/download` | No equivalent |
| **Service discovery** | `ha_list_services` | No equivalent (plugin relies on Claude's training data) |
| **Entity registry management** | `ha_get/set_entity`, `ha_rename_entity` | ha-apply-naming uses `hass-cli entity rename` |
| **Bulk device control** | `ha_bulk_control` | No equivalent |
| **Todo/Calendar CRUD** | `ha_get/add/update/remove_todo_item`, calendar tools | No equivalent |
| **Zone CRUD** | `ha_get/create/update/delete_zone` | No equivalent |
| **Config entry flow** | `ha_config_entry_*` | No equivalent (integration setup via UI) |
| **Domain docs fetching** | `ha_get_domain_docs` | Skills contain domain knowledge inline |
| **Update management** | `ha_get_updates` | No equivalent |

---

## 4. Detailed Tool-by-Tool Assessment

### Category A: Already Covered by Plugin (No Action Needed)

These MCP tools map to existing skill capabilities. The plugin's approach is superior because it includes domain knowledge.

| MCP Tool | Plugin Equivalent | Notes |
|----------|------------------|-------|
| `ha_config_get_automation` | ha-automations (reads automations.yaml) | Plugin reads files directly |
| `ha_config_set_automation` | ha-automations (edits automations.yaml) | Plugin adds intent classification + safety |
| `ha_config_remove_automation` | ha-automations | Plugin approach is file-based |
| `ha_config_get_script` | ha-scripts | File-based |
| `ha_config_set_script` | ha-scripts | File-based with domain knowledge |
| `ha_config_remove_script` | ha-scripts | File-based |
| `ha_call_service` | hass-cli service call | Already available via Bash |
| `ha_get_state` | `hass-cli state get` | Already available via Bash |
| `ha_check_config` | ha-validate + ha-deploy | Plugin has richer validation |
| `ha_restart` | ha-deploy | Plugin wraps in deploy workflow |
| `ha_reload_core` | ha-deploy | Plugin handles reload after deploy |
| `ha_rename_entity` | ha-apply-naming | Plugin has full naming workflow |

### Category B: Enrich Existing Skills (Add Procedures)

These MCP tools provide capabilities that should be absorbed as *procedures* within existing skills.

| MCP Tool | Target Skill | What to Add |
|----------|-------------|------------|
| `ha_search_entities` | ha-resolver | Add fuzzy search procedure using `hass-cli` with enhanced grep patterns, or document `hass-cli raw` endpoint for search |
| `ha_get_overview` | ha-resolver / ha-analyze | Add "orientation" procedure — query system overview as first step |
| `ha_deep_search` | ha-troubleshooting | Add deep search procedure for finding entity references in configs |
| `ha_get_automation_traces` | ha-troubleshooting | Strengthen trace retrieval procedures with `hass-cli raw get /api/trace/` |
| `ha_get_history` | ha-troubleshooting | Add history querying procedures with `hass-cli raw get /api/history/period` |
| `ha_get_statistics` | ha-analyze | Add statistics procedures for long-term trend analysis |
| `ha_eval_template` | ha-jinja | Add template testing procedure via `hass-cli raw post /api/template` |
| `ha_get_logbook` | ha-troubleshooting | Add logbook querying procedure |
| `ha_list_services` | ha-resolver | Add service discovery procedure |
| `ha_get_entity_integration_source` | ha-devices | Add integration source lookup |
| `ha_get_system_health` | ha-analyze | Add system health check procedure |
| `ha_get_updates` | ha-analyze | Add update checking procedure |
| `ha_config_list_helpers` | ha-automations / ha-scripts | Add helper discovery procedure |
| `ha_list_blueprints` | ha-automations | Add blueprint discovery + usage procedure |

### Category C: New Skills Needed

These MCP tool clusters represent genuinely new capability areas not covered by any existing skill.

| MCP Tool Cluster | Proposed Skill | Rationale |
|-----------------|---------------|-----------|
| `ha_config_get/set_dashboard`, `ha_dashboard_find_card`, `ha_get_dashboard_guide`, `ha_get_card_types`, `ha_get_card_documentation` | **Upgrade ha-lovelace** from guidance-only to operational | Dashboard CRUD is a major gap; users expect to create dashboards, not just get advice |
| `ha_config_list/set/remove_area/floor`, `ha_config_get/set/remove_label`, `ha_config_list/set/remove_group` | **New: ha-organize** | Organizational entity management (areas, labels, groups, floors) is a coherent workflow |
| `ha_get_history`, `ha_get_statistics` | **New: ha-history** (or enrich ha-troubleshooting + ha-analyze) | History and statistics are used in both troubleshooting (what happened?) and analysis (trends over time) |
| `ha_backup_create`, `ha_backup_restore` | **Enrich ha-deploy** | Backup/restore fits naturally with the deploy/rollback workflow |
| `ha_config_set_helper`, `ha_config_remove_helper` | **New: ha-helpers** (or enrich ha-automations) | Helper CRUD via API is cleaner than file editing for storage-based helpers |

### Category D: Low Priority / Skip

These MCP tools provide niche capabilities that don't warrant dedicated skill support.

| MCP Tool | Reason to Skip |
|----------|---------------|
| `ha_get_camera_image` | Niche; CLI-based plugin can't display images |
| `ha_get_zha_devices` | Integration-specific; too narrow |
| `ha_get_addon` | Read-only add-on info; low value |
| `ha_hacs_search/download` | HACS management is better done through the UI |
| `ha_config_entry_*` | Integration setup is complex and UI-centric |
| `ha_get/add/update/remove_todo_item` | Todo management is peripheral to config management |
| `ha_config_get/set/remove_calendar_event` | Calendar management is peripheral |
| `ha_create_dashboard_resource` | Dashboard resource management is advanced/niche |
| `ha_get_domain_docs` | Plugin skills already embed domain knowledge |
| `ha_bug_report` | MCP-specific; not relevant to plugin |
| `ha_voice_assistant_*` | Voice assistant exposure is niche |
| `ha_get_integration` | Read-only integration info; covered by `hass-cli` |
| `ha_config_*_filesystem` | Plugin already has direct file access |

---

## 5. Recommended Changes

### Strategy: Absorb Procedures, Not Tools

For each MCP tool capability worth adding, create a **procedure** (a documented sequence of `hass-cli` commands) rather than reimplementing the tool's logic. Claude can follow procedures; it doesn't need pre-built functions.

**Example — Converting `ha_search_entities` to a procedure:**

MCP tool does: Python fuzzy search with thresholds, domain filtering, area filtering, grouped results

Skill procedure equivalent:
```markdown
## Entity Search Procedure

1. **Quick search:** `hass-cli state list | grep -i "<query>"`
2. **Domain-filtered:** `hass-cli state list | grep "^<domain>\." | grep -i "<query>"`
3. **Area-filtered:** `hass-cli raw get /api/config/area_registry/list` then cross-reference
4. **Detailed state:** `hass-cli -o json state get <entity_id>`
5. **All entities in area:** Use WebSocket via `hass-cli raw ws '{"type":"config/entity_registry/list"}'` then filter by area_id
```

This costs ~100 tokens in a reference file vs. ~500 tokens for the MCP tool schema, and Claude can adapt the procedure to the specific situation.

---

## 6. New Skills to Create

### 6.1 ha-organize (New Skill)

**Purpose:** Manage organizational entities — areas, floors, labels, groups

**Why:** The MCP has 12 tools for organizational CRUD. These are operationally simple but users regularly need them when setting up or restructuring their smart home.

**Scope:**
- Area CRUD: `hass-cli raw ws '{"type":"config/area_registry/list"}'`, create, update, delete
- Floor CRUD: Same pattern via WebSocket
- Label CRUD: Same pattern via WebSocket + entity label assignment
- Group CRUD: Same pattern via WebSocket

**Implementation:** Single skill with a reference file containing `hass-cli raw` procedures for each entity type. The skill instructions teach *when* to use areas vs labels vs groups (organizational best practices) while the reference provides the API procedures.

**Estimated size:** SKILL.md ~150 lines + references/organizational-api.md ~200 lines

### 6.2 ha-helpers (New Skill)

**Purpose:** Create and manage helper entities (input_boolean, input_number, input_select, timer, counter, schedule, etc.)

**Why:** The MCP has dedicated helper CRUD tools. The current plugin creates helpers by editing YAML files, but most modern HA users create helpers via the UI/API (storage-based). The API approach is more reliable and doesn't require file access to the HA config directory.

**Scope:**
- List helpers by type via WebSocket
- Create helpers via WebSocket (`{type}/create`)
- Update helpers via entity registry
- Delete helpers via WebSocket (`{type}/delete` with unique_id)
- Best practices: when to use which helper type, built-in helpers vs template sensors

**Implementation:** SKILL.md with helper selection guidance + references/helper-api.md with WebSocket procedures

**Estimated size:** SKILL.md ~200 lines + references/helper-api.md ~150 lines

### 6.3 ha-history (New Skill — or merge into ha-troubleshooting + ha-analyze)

**Purpose:** Query historical data and long-term statistics

**Why:** The MCP has `ha_get_history` (raw state changes, ~10 day retention) and `ha_get_statistics` (aggregated, permanent). These are critical for troubleshooting ("why was it cold last night?") and analysis ("monthly energy trend").

**Two options:**

**Option A — Dedicated skill:**
- Combines both history and statistics in one skill
- Teaches *when* to use which (raw history for debugging, statistics for trends)
- Procedures for `hass-cli raw` API calls

**Option B — Merge into existing skills (recommended):**
- Raw history procedures → ha-troubleshooting (fits "diagnose what happened")
- Statistics procedures → ha-analyze (fits "analyze trends and patterns")
- This avoids a new skill and keeps related capabilities together

**Estimated size:** ~100 lines of procedures split across two existing skills

---

## 7. Existing Skills to Enrich

### 7.1 ha-lovelace → Upgrade to Operational

**Current state:** Guidance-only skill with dashboard design best practices

**Gap:** Cannot actually create or modify dashboards. The MCP has full dashboard CRUD via WebSocket.

**Changes:**
1. Add dashboard CRUD procedures to SKILL.md or a new `references/dashboard-api.md`
2. Add card search procedure (equivalent to `ha_dashboard_find_card`)
3. Add dashboard listing/metadata management
4. Keep existing design guidance (this is the plugin's advantage over the MCP)

**Key procedures to add:**
```
- List dashboards: hass-cli raw ws '{"type":"lovelace/dashboards/list"}'
- Get dashboard config: hass-cli raw ws '{"type":"lovelace/config"}'
- Save dashboard config: hass-cli raw ws '{"type":"lovelace/config/save","config":{...}}'
- Create dashboard: hass-cli raw ws '{"type":"lovelace/dashboards/create",...}'
- Delete dashboard: hass-cli raw ws '{"type":"lovelace/dashboards/delete",...}'
```

**Note:** The MCP uses `jq_transform` and `python_transform` for surgical dashboard edits. The plugin should use the Edit tool with precise old/new strings for YAML-based dashboards, or WebSocket full-config replacement for storage-based dashboards.

### 7.2 ha-resolver → Enhanced Search

**Current state:** Uses `hass-cli state list | grep` for entity resolution

**Gap:** No fuzzy matching, no area-based filtering, no system overview

**Changes:**
1. Add "orientation" procedure — get system overview as first step in entity resolution
2. Add area-based entity lookup via WebSocket registry queries
3. Add domain-filtered entity listing
4. Add service discovery procedure (`hass-cli service list`)

### 7.3 ha-troubleshooting → Richer Diagnostics

**Current state:** Has diagnostic process but limited API procedures

**Changes:**
1. Add history querying procedure (raw state changes for debugging)
2. Strengthen automation trace procedures with specific `hass-cli raw` commands
3. Add logbook querying procedure
4. Add template evaluation procedure (test Jinja templates via API)
5. Improve evidence table with history data

### 7.4 ha-analyze → Data-Driven Insights

**Current state:** Analyzes setup and provides recommendations

**Changes:**
1. Add long-term statistics procedure for trend analysis
2. Add system health check procedure
3. Add update checking procedure
4. Add entity registry analysis (disabled entities, hidden entities, orphaned entities)

### 7.5 ha-automations → Blueprint Support

**Current state:** Creates automations from natural language

**Changes:**
1. Add blueprint discovery procedure (`hass-cli raw get /api/config/automation/blueprint`)
2. Add blueprint-based automation creation guidance
3. Add helper discovery procedure (check if needed helpers exist before creating automations)

### 7.6 ha-jinja → Template Testing

**Current state:** Jinja templating guidance only

**Changes:**
1. Add template evaluation procedure via `hass-cli raw post /api/template`
2. This lets users test templates before embedding them in automations

### 7.7 ha-deploy → Backup Integration

**Current state:** Git-based deploy and rollback

**Changes:**
1. Add pre-deploy backup procedure via `hass-cli raw ws '{"type":"backup/generate"}'`
2. Add backup listing procedure
3. Add restore procedure (with strong confirmation gates)

---

## 8. New References to Create

### 8.1 references/websocket-api.md

**Purpose:** Central reference for WebSocket API procedures used across multiple skills

**Contents:**
- How to use `hass-cli raw ws` for WebSocket commands
- Common message types (registry queries, config operations)
- Error handling patterns
- Authentication notes

### 8.2 references/rest-api-patterns.md

**Purpose:** Central reference for REST API procedures

**Contents:**
- `hass-cli raw get/post` patterns for common operations
- History API endpoint patterns
- Template evaluation endpoint
- Error response format

### 8.3 references/dashboard-api.md

**Purpose:** Dashboard CRUD procedures for ha-lovelace skill

**Contents:**
- WebSocket message formats for dashboard operations
- Card search algorithms (equivalent to `ha_dashboard_find_card`)
- Dashboard structure reference (views, sections, cards)
- Card type reference with entity mapping

### 8.4 references/organizational-api.md

**Purpose:** Area/floor/label/group CRUD procedures for ha-organize skill

**Contents:**
- WebSocket message formats for each entity type
- Entity registry update procedures (assign area, labels)
- Best practices for when to use areas vs labels vs groups

### 8.5 references/helper-api.md

**Purpose:** Helper CRUD procedures for ha-helpers skill

**Contents:**
- WebSocket message formats for each helper type
- Required vs optional parameters per helper type
- Helper type selection guide (when to use counter vs input_number, etc.)

---

## 9. Implementation Priority

### Phase 1: High Impact, Low Effort (Enrich Existing Skills)

1. **Enrich ha-resolver** with system overview + area-based search procedures
   - *Impact:* Every skill that resolves entities gets better results
   - *Effort:* ~100 lines of procedures added to existing reference

2. **Enrich ha-jinja** with template evaluation procedure
   - *Impact:* Users can test templates before deployment
   - *Effort:* ~20 lines added to existing skill

3. **Enrich ha-troubleshooting** with history + logbook + trace procedures
   - *Impact:* Dramatically improves debugging capability
   - *Effort:* ~150 lines of procedures in new reference file

### Phase 2: High Impact, Medium Effort (Upgrade Existing Skills)

4. **Upgrade ha-lovelace** from guidance to operational
   - *Impact:* Closes the biggest functional gap (dashboard management)
   - *Effort:* New reference file (~200 lines) + SKILL.md updates (~50 lines)

5. **Enrich ha-deploy** with backup/restore procedures
   - *Impact:* Safer deployment workflow
   - *Effort:* ~50 lines added to existing skill

6. **Enrich ha-analyze** with statistics + health procedures
   - *Impact:* Data-driven analysis instead of static recommendations
   - *Effort:* ~100 lines of procedures

### Phase 3: Medium Impact, Medium Effort (New Skills)

7. **Create ha-organize** skill (areas, floors, labels, groups)
   - *Impact:* New capability area; common setup task
   - *Effort:* New skill (~150 lines) + reference (~200 lines)

8. **Create ha-helpers** skill (helper entity CRUD)
   - *Impact:* Cleaner helper management than file editing
   - *Effort:* New skill (~200 lines) + reference (~150 lines)

### Phase 4: Low Impact, Low Effort (Polish)

9. **Enrich ha-automations** with blueprint support
   - *Impact:* Alternative automation creation path
   - *Effort:* ~50 lines added to existing skill

10. **Create references/websocket-api.md** and **references/rest-api-patterns.md**
    - *Impact:* Reduces duplication across skills
    - *Effort:* ~200 lines total, consolidating patterns from other references

---

## 10. What NOT to Do

### Don't Create 97 Skills to Mirror 97 Tools

Each MCP tool is a thin API wrapper. Creating a skill per tool would:
- Bloat the plugin from 15 to 100+ skills
- Overwhelm Claude's skill selection with near-identical descriptions
- Duplicate what `hass-cli` already provides natively
- Lose the plugin's key advantage: curated domain knowledge

### Don't Run the MCP Server Alongside the Plugin

This creates:
- Conflicting approaches (API vs file editing for automations)
- Redundant entity resolution
- Double context cost
- Safety invariant bypass risk

### Don't Replicate the MCP's Fuzzy Search in a Skill

The MCP's fuzzy search is 900+ lines of Python with thresholds, scoring, and fallbacks. A skill procedure using `hass-cli` with smart `grep` patterns achieves 80% of the capability at 1% of the complexity. For the remaining 20%, users can describe what they're looking for and Claude will iterate.

### Don't Add Device Control Tools

The MCP has `ha_call_service`, `ha_bulk_control`, and `control_device_smart` for real-time device control. The plugin is designed for *configuration management*, not real-time control. Adding device control would:
- Expand scope beyond the plugin's purpose
- Create safety concerns (accidental device triggers)
- Conflict with the "never auto-deploy" safety invariant

If users need device control, they should use `hass-cli` directly or the HA UI.

### Don't Add Camera/Media/Todo/Calendar Skills

These are peripheral to the core value proposition (configuration management). They serve niche use cases that are better handled by the HA UI or dedicated integrations.

---

## Appendix A: Complete MCP Tool Inventory

### Search & Discovery (4 tools)
- `ha_search_entities` — Fuzzy entity search with domain/area filtering
- `ha_get_overview` — AI-friendly system overview with categorization
- `ha_deep_search` — Search across automation/script/helper definitions
- `ha_get_state` — Detailed entity state with timezone metadata

### Service & Device Control (5 tools)
- `ha_call_service` — Universal service execution
- `ha_bulk_control` — Multi-device parallel control
- `ha_get_operation_status` — Async operation verification
- `ha_get_bulk_status` — Bulk operation status
- `ha_list_services` — Service discovery with parameters

### Automations (3 tools)
- `ha_config_get_automation` — Get automation config
- `ha_config_set_automation` — Create/update automation
- `ha_config_remove_automation` — Delete automation

### Scripts (3 tools)
- `ha_config_get_script` — Get script config
- `ha_config_set_script` — Create/update script
- `ha_config_remove_script` — Delete script

### Helpers (3 tools)
- `ha_config_list_helpers` — List helpers by type
- `ha_config_set_helper` — Create/update helper
- `ha_config_remove_helper` — Delete helper

### Dashboards (7 tools)
- `ha_config_get_dashboard` — Get/list dashboards
- `ha_config_set_dashboard` — Create/update with jq/python transforms
- `ha_config_update_dashboard_metadata` — Update title/icon/permissions
- `ha_config_delete_dashboard` — Delete dashboard
- `ha_get_dashboard_guide` — Dashboard design guide
- `ha_get_card_types` — List all 41 card types
- `ha_get_card_documentation` — Card-specific docs

### Areas & Floors (6 tools)
- `ha_config_list_areas` / `ha_config_set_area` / `ha_config_remove_area`
- `ha_config_list_floors` / `ha_config_set_floor` / `ha_config_remove_floor`

### Labels (3 tools)
- `ha_config_get_label` / `ha_config_set_label` / `ha_config_remove_label`
- `ha_manage_entity_labels` — Bulk label assignment

### Zones (4 tools)
- `ha_get_zone` / `ha_create_zone` / `ha_update_zone` / `ha_delete_zone`

### Groups (3 tools)
- `ha_config_list_groups` / `ha_config_set_group` / `ha_config_remove_group`

### Todo Lists (4 tools)
- `ha_get_todo` / `ha_add_todo_item` / `ha_update_todo_item` / `ha_remove_todo_item`

### Calendar (3 tools)
- `ha_config_get_calendar_events` / `ha_config_set_calendar_event` / `ha_config_remove_calendar_event`

### Blueprints (3 tools)
- `ha_list_blueprints` / `ha_get_blueprint` / `ha_import_blueprint`

### Device & Entity Registry (7 tools)
- `ha_get_device` / `ha_update_device` / `ha_remove_device`
- `ha_rename_entity`
- `ha_get_entity` / `ha_set_entity` (enable/disable/hide/labels/aliases)
- `ha_get_entity_integration_source`

### History & Statistics (2 tools)
- `ha_get_history` — Raw state changes (~10 day retention)
- `ha_get_statistics` — Aggregated long-term statistics

### Traces (1 tool)
- `ha_get_automation_traces` — Execution traces for debugging

### System (6 tools)
- `ha_check_config` / `ha_restart` / `ha_reload_core`
- `ha_get_system_info` / `ha_get_system_health` / `ha_get_updates`

### Backup (2 tools)
- `ha_backup_create` / `ha_backup_restore`

### Utility (4 tools)
- `ha_get_logbook` / `ha_eval_template` / `ha_get_domain_docs` / `ha_get_integration`

### Other (15+ tools)
- ZHA devices, add-ons, camera, HACS, config entry flow, voice assistant, resources, filesystem, bug report

---

## Appendix B: hass-cli Equivalents for Key MCP Operations

| MCP Tool | hass-cli Equivalent |
|----------|-------------------|
| `ha_get_state(entity_id)` | `hass-cli -o json state get <entity_id>` |
| `ha_search_entities(query)` | `hass-cli state list \| grep -i "<query>"` |
| `ha_call_service(domain, service, data)` | `hass-cli service call <domain>.<service> --arguments '<json>'` |
| `ha_check_config()` | `hass-cli raw post /api/config/core/check_config` |
| `ha_get_history(entity_id)` | `MSYS_NO_PATHCONV=1 hass-cli raw get "/api/history/period?filter_entity_id=<id>"` |
| `ha_eval_template(template)` | `hass-cli raw post /api/template --json '{"template":"<tpl>"}'` |
| `ha_get_logbook()` | `MSYS_NO_PATHCONV=1 hass-cli raw get "/api/logbook/<timestamp>"` |
| `ha_config_list_areas()` | `hass-cli area list` or WebSocket `config/area_registry/list` |
| `ha_get_automation_traces(id)` | `MSYS_NO_PATHCONV=1 hass-cli raw get "/api/trace/automation.<id>"` |
| `ha_list_services(domain)` | `hass-cli service list \| grep "<domain>"` |
| `ha_get_overview()` | `hass-cli -o json raw get /api/config` + `hass-cli state list` |
| WebSocket operations | `hass-cli raw ws '{"type":"<msg_type>",...}'` |

---

## Appendix C: Skill Design Principles (from Anthropic Docs)

1. **Keep SKILL.md under 500 lines** — Move detailed procedures to `references/`
2. **Progressive disclosure** — Reference supporting files, don't embed everything
3. **One primary task per skill** — Accept variations via arguments
4. **Clear invocation description** — Match natural user language
5. **Trust Claude's knowledge** — Don't explain things Claude already knows
6. **Skills are building blocks** — Design for composability
7. **References load on demand** — Only when Claude reads them
8. **Use `context: fork`** for isolated multi-step tasks
9. **Use `disable-model-invocation: true`** for dangerous operations
10. **Use hooks** for deterministic behavior (cheaper than prompt-based decisions)
