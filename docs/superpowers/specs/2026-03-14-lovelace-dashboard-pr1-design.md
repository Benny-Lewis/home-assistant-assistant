# Lovelace & Dashboard PR 1 — Design Spec

**Date:** 2026-03-14
**Backlog items:** BL-019, BL-020, BL-021, BL-022
**Approach:** B — SKILL.md workflow + references/ + helper

## Problem Summary

The ha-lovelace skill covers basic card syntax and YAML-mode dashboards but has no operational support for storage-mode dashboard mutation. Four gaps identified from transcript analysis:

1. **BL-019 (S2):** No documented success/failure contract for storage-mode saves. The assistant misread `error: 3` responses as success, reporting dashboard edits as complete while HA served stale config.
2. **BL-020 (S3):** No safe-edit playbook for sections views. Bulk section replacement produced blank pages; `max_columns` and `grid_options.rows` sizing required trial-and-error.
3. **BL-021 (S3):** No entity preflight validation before dashboard saves. Guessed entity IDs rendered as "not found" cards immediately on save.
4. **BL-022 (S4):** No stable workflow for researching custom card options after HACS install. The assistant fell back to ad hoc web searches and hit rate limits.

## File Structure

### New files

```
skills/ha-lovelace/
  references/
    dashboard-guide.md          # Card/layout reference (~350-400 lines)
references/
  dashboard-api.md              # WebSocket API contract (~80 lines)
helpers/
  lovelace-dashboard.py         # fetch / save-and-verify / find-entities (~200 lines)
```

### Modified files

```
skills/ha-lovelace/SKILL.md     # Restructured: workflow procedures (~250 lines)
```

## Component 1: `helpers/lovelace-dashboard.py`

### Pattern

Follows `entity-registry.py` — WebSocket via `websockets` library, `HASS_SERVER`/`HASS_TOKEN` env vars. Copy-pastes the same `build_ws_url`/`ws_connect_and_auth` boilerplate (each helper is self-contained; no shared module — matching the existing pattern of the 4 other helpers).

### Subcommands

#### `fetch <url_path>`

- Sends `{"type": "lovelace/config", "url_path": "<url_path>", "force": true}`
- Outputs JSON config to stdout
- `url_path` defaults to `"lovelace"` (default dashboard) if omitted
- Exit 0 on success, exit 1 on error

#### `save-and-verify <url_path> <config_file>`

- Reads new config from `<config_file>` (JSON file path, or `-` for stdin). The config file must contain the full dashboard config object (e.g., `{"views": [...]}`) — the helper wraps it as `{"config": <file_contents>}` in the WebSocket message.
- Sends `{"type": "lovelace/config/save", "config": ..., "url_path": ...}`
- Checks response: `success: true` → proceed to verify; `success: false` → exit 1 with error message
- **Read-after-write verification:** re-fetches config via `lovelace/config` with `force: true`, then compares:
  - View count: `len(saved_views) == len(fetched_views)`
  - View paths: each view's `path` field (if present in the saved config) matches. Views without explicit `path` fields are skipped (HA auto-generates paths from titles, which is acceptable).
- Exit 0 + prints verification summary on match
- Exit 1 + prints diff summary on mismatch

#### `find-entities <url_path>`

- Fetches config, walks all cards recursively, extracts every `entity` and `entities[]` value
- **Traversal keys:** `cards` (stacks, grids), `card` (conditional), `elements` (picture-elements), `sections[].cards[]` (sections views), and `badges` (view-level entity references) — all traversed recursively
- Outputs deduplicated entity ID list to stdout (one per line)
- Exit 0 always (informational output)
- Used by BL-021 preflight: pipe to `hass-cli state get` to validate each exists
- Also useful for auditing existing dashboards for stale entity references

### Intentional scope limits

- No optimistic locking / config hashing (Claude is sole editor in this plugin's context)
- No jq/Python transforms (Claude edits the JSON directly)
- No card-type filtering (simple entity extraction is sufficient for preflight)

### Size estimate

~180-200 lines, including ~40 lines of WebSocket boilerplate shared with entity-registry.py.

## Component 2: `references/dashboard-api.md`

Canonical WebSocket API contract for storage-mode dashboards. Pure reference — no procedures, no helper usage.

### Content

**WebSocket commands:**

| Command | Purpose | Success response | Failure response |
|---------|---------|-----------------|-----------------|
| `lovelace/config` | Fetch dashboard config | `{success: true, result: {views: [...]}}` | `{success: false, error: {code, message}}` |
| `lovelace/config/save` | Save dashboard config | `{success: true, result: null}` | `{success: false, error: {code, message}}` |
| `lovelace/dashboards/list` | List all storage dashboards | `{success: true, result: [...]}` | — |

**Key fields:**
- `url_path`: identifies the dashboard. Omit or use `"lovelace"` for the default dashboard.
- `force: true`: on fetches, bypasses HA's config cache to get current state.

**Critical contract:** `result: null` on save success is correct — it is not an error. A failure returns `success: false` with an `error` object containing `code` (integer) and `message` (string).

**Validation rules:**
- New dashboard `url_path` must be a valid slug (lowercase, alphanumeric, hyphens, underscores). Convention: use hyphens for readability (e.g., `my-dashboard`).
- `"lovelace"` and `"default"` target the built-in default dashboard

## Component 3: `skills/ha-lovelace/references/dashboard-guide.md`

Adapted from ha-mcp's `resources/dashboard_guide.md` (575 lines). Replaces the current card examples in SKILL.md with modernized content.

### Sections included

| ha-mcp section | Adaptation |
|---|---|
| Part 1: Dashboard Structure | Include — sections views, view types, `max_columns`, `grid_options` |
| Part 2: Built-in Cards | Include — tile, grid, features, actions, visibility (replaces current 12 card examples) |
| Part 3: Custom Cards | Abbreviated — keep usage pattern, drop Cloudflare Worker hosting specifics |
| Part 4: CSS Styling | Abbreviated — variables, card-mod basics |
| Part 5: HACS Integration | Include — when to use, popular cards list |
| Part 6: Complete Examples | Include — multi-view dashboard, custom card workflow |
| Part 7: Visual Iteration | Drop — ha-mcp-specific browser tooling |

### Key adaptations from MCP context to plugin context

- JSON examples converted to YAML for readability. Note: storage-mode dashboards use JSON internally (via WebSocket API), while YAML-mode dashboards use YAML config files. Examples use YAML for consistency with the rest of the plugin, with a note that storage-mode users work with JSON.
- ha-mcp tool references (`ha_config_set_dashboard`, `ha_hacs_search`) removed — replaced with hass-cli/helper equivalents where applicable
- Added `grid_options.rows` sizing table from BL-020 transcript evidence
- Added `max_columns` guidance: start 3-4, reduce for dense custom cards
- Kept popular HACS cards list (mushroom, mini-graph-card, button-card, card-mod, apexcharts-card, layout-card)

### Estimated size

~350-400 lines.

## Component 4: `skills/ha-lovelace/SKILL.md` Restructure

### Frontmatter changes

- Update `allowed-tools` from `Read, Grep, Glob` to `Read, Grep, Glob, Bash(hass-cli:*,python*,py:*)`

### Content that stays (updated)

- Jinja templating warning (unchanged)
- Dashboard organization guidance (brief — by room/function/user)
- YAML vs storage mode (expanded with storage-mode workflow)
- Best practices (expanded)

### Content that moves to `references/dashboard-guide.md`

- Dashboard Structure (views/cards basics)
- View Configuration
- Common Card Types (all 12)
- Tap Actions
- Responsive Design / Themes

### New section: Entity Preflight Validation (BL-021)

**Placement:** Before save contract (preflight happens before save).

**Workflow:**
1. Before any dashboard save that adds or changes entity references, extract all entity IDs from the proposed config. During in-progress editing, Claude extracts entities directly from the JSON being constructed. For auditing existing dashboards, use `python lovelace-dashboard.py find-entities <url_path>`.
2. For each entity: `hass-cli state get <entity_id>` — if "not found", resolve using ha-resolver patterns
3. For near-misses, suggest corrections to the user (e.g., `sensor.fan_vent_temperature` → `sensor.upstairs_hallway_whole_house_fan_temperature`)
4. Do NOT save until all entities resolve

Cross-references `skills/ha-resolver/SKILL.md` for entity resolution procedures.

### New section: Storage Dashboard Save Contract (BL-019)

**Placement:** After entity preflight.

**Mandatory workflow for any storage dashboard mutation:**
1. Fetch current config: `python lovelace-dashboard.py fetch <url_path>`
2. Modify the JSON
3. Save and verify: `python lovelace-dashboard.py save-and-verify <url_path> <config_file>`
4. If exit code non-zero → report failure, do NOT claim success
5. Visual verification: instruct the user to open the dashboard URL in their browser and confirm it renders correctly (the plugin is CLI-based and cannot programmatically verify visual rendering)

Cross-references `references/dashboard-api.md` for response format details.

Common mistake callout: `result: null` is success, not an error.

### New section: Sections View Mutation Rules (BL-020)

**Placement:** After save contract.

**Rules:**
- **One section at a time:** Never replace the entire `sections` array. Fetch → modify one section → save → verify → proceed to next.
- **`max_columns` tuning:** Start at 4 for tile cards, reduce to 3 for custom cards with legends (mini-graph-card, apexcharts-card).
- **`grid_options.rows` sizing table:**

| Card content | Recommended rows |
|---|---|
| Single entity, no extras | 1 (default) |
| Entity with legend or name | 2 |
| Multi-entity with legend + extrema | 3 |
| Graph card with 3+ entities | 3-4 |

- **Blank view recovery:** If a structural edit produces a blank view, the sections array is likely malformed. Re-fetch, compare against last known-good, fix structure.
- **Visual verification after each mutation** — don't batch structural changes.

### New section: Custom Card Research Workflow (BL-022)

**Placement:** After mutation rules.

**Stable fallback order for card documentation:**
1. Check `references/dashboard-guide.md` popular cards section first
2. HACS: check installed resources via hass-cli
3. GitHub API: `gh api repos/<owner>/<repo>/readme --jq .content | base64 -d`
4. Web search (last resort)

**Post-install availability:** After HACS install, HA frontend must reload. Guide user to refresh browser or restart HA if new card type isn't recognized.

**Common mistake callout:** Don't guess card option names from other cards. Each custom card has its own schema — always check the card's README.

### Estimated size

~250 lines (down from 389, with reference material moved out and workflow sections added).

## Traceability

| Backlog item | Primary deliverable | Supporting deliverables |
|---|---|---|
| BL-019 (S2) | SKILL.md "Storage Dashboard Save Contract" section | `lovelace-dashboard.py save-and-verify`, `dashboard-api.md` |
| BL-020 (S3) | SKILL.md "Sections View Mutation Rules" section | `dashboard-guide.md` sections/grid content |
| BL-021 (S3) | SKILL.md "Entity Preflight Validation" section | `lovelace-dashboard.py find-entities`, ha-resolver cross-ref |
| BL-022 (S4) | SKILL.md "Custom Card Research Workflow" section | `dashboard-guide.md` HACS/popular cards content |
