---
name: ha-lovelace
description: This skill should be used when the user asks about "dashboard", "lovelace", "card", "view", "theme", "UI", mentions dashboard design, card configuration, dashboard layout, or needs help with Home Assistant Lovelace dashboard creation and customization.
user-invocable: true
version: 0.2.0
allowed-tools: Read, Grep, Glob, Bash(hass-cli:*,python*,py:*,gh:*)
---

# Home Assistant Lovelace Dashboards

> **Safety Invariants:** #5 (no implicit deploy), #7 (minimal edits), #8 (post-edit verify)
> See `references/safety-invariants.md`

This skill provides workflow procedures for creating and managing Lovelace dashboards.

For card types, layout options, and examples, read `references/dashboard-guide.md`.

## Important: Templating in Lovelace

**Most Lovelace cards do NOT support Jinja2 templating.**

If you type `{{ states('sensor.x') }}` in an Entities card, Button card, or most other cards,
it will display as literal text — NOT the sensor value.

**Exception: Markdown Card** — renders templates server-side.

For dynamic values in other cards:
1. **Template entities** — create a template sensor/binary_sensor, display that entity
2. **Custom cards** — install cards like `button-card` that implement their own templating

See `ha-jinja` skill for templating reference.

## Dashboard Modes

### YAML Mode
File-managed dashboards deployed via git. Edit `ui-lovelace.yaml` (or per-dashboard YAML files) and deploy with `/ha-deploy`.

```yaml
# configuration.yaml
lovelace:
  mode: yaml
  resources:
    - url: /local/card.js
      type: module
```

### Storage Mode
UI-managed dashboards mutated via the WebSocket API. Use `helpers/lovelace-dashboard.py` for programmatic operations. See `references/dashboard-api.md` for the API contract.

## Dashboard Organization

Organize dashboards by room, function, or user — see `references/dashboard-guide.md` for examples of each pattern.

**General principles:**
- Group related entities in the same section
- Use consistent icon families (mdi:)
- Design for smallest screen first (mobile-first)
- Prefer more views over cluttered views
- Use conditional cards to hide irrelevant information

---

## Entity Preflight Validation

> Addresses BL-021: Dashboard entity preflight validation.

**Before any dashboard save that adds or changes entity references, validate every entity ID.**

### Workflow

1. **Extract entity IDs** from the proposed dashboard config. During in-progress editing, scan the JSON directly. For auditing existing dashboards:
   ```bash
   PY="$(cat .claude/ha-python.txt 2>/dev/null || command -v python3 || command -v python || command -v py)"
   PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt)"
   "$PY" "$PLUGIN_ROOT/helpers/lovelace-dashboard.py" find-entities <url_path>
   ```

2. **Validate each entity** against live state:
   ```bash
   hass-cli state get <entity_id>
   ```
   If "not found", resolve using `ha-resolver` patterns (area search, name search, capability snapshot).

3. **Suggest corrections** for near-misses. Common pattern: abbreviated entity name vs full device-qualified name (e.g., `sensor.fan_vent_temperature` → `sensor.upstairs_hallway_whole_house_fan_temperature`).

4. **Do NOT save until all entities resolve.** A single wrong entity renders the card as "Entity not found" in the UI.

---

## Storage Dashboard Save Contract

> Addresses BL-019: Storage-mode dashboard save contract with success/failure detection.

**Every storage-mode dashboard mutation MUST follow this workflow.**

### Mandatory Save Workflow

1. **Fetch current config:**
   ```bash
   PY="$(cat .claude/ha-python.txt 2>/dev/null || command -v python3 || command -v python || command -v py)"
   PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt)"
   "$PY" "$PLUGIN_ROOT/helpers/lovelace-dashboard.py" fetch <url_path> > current.json
   ```

2. **Modify the JSON** — edit `current.json` with the desired changes.

3. **Save and verify:**
   ```bash
   "$PY" "$PLUGIN_ROOT/helpers/lovelace-dashboard.py" save-and-verify <url_path> current.json
   ```

4. **Check exit code:**
   - Exit 0 = save confirmed (view count and paths verified)
   - Exit non-zero = **save failed or verification failed — do NOT claim success**

5. **Visual verification:** Ask the user to open the dashboard URL in their browser and confirm it renders correctly.

### Common Mistake

A successful save returns `result: null`. This is correct — **null is not an error**. A failure returns `success: false` with an `error` object. See `references/dashboard-api.md` for full response format.

---

## Sections View Mutation Rules

> Addresses BL-020: Sections view safe-edit playbook.

### One Section at a Time

**Never replace the entire `sections` array in a single save.** Instead:

1. Fetch current config
2. Modify ONE section (add, edit, or remove)
3. Save and verify
4. Confirm the view renders correctly
5. Proceed to the next section

Bulk section replacement risks validation conflicts and blank views.

### `max_columns` Tuning

| Content type | Recommended `max_columns` |
|---|---|
| Tile cards (compact) | 4 |
| Custom cards with legends | 3 |
| Dense multi-entity cards | 2-3 |

Overly wide layouts cause cards to render too narrow, especially custom cards with legends or multiple entities.

### `grid_options.rows` Sizing

| Card content | Recommended `rows` |
|---|---|
| Single entity, no extras | 1 (default) |
| Entity with legend or name | 2 |
| Multi-entity with legend + extrema | 3 |
| Graph card with 3+ entities | 3-4 |

If legends overlap or cards look cramped, increase `rows`.

### Blank View Recovery

If a structural edit produces a blank view:
1. The sections array is likely malformed
2. Re-fetch the current config from HA (it may have reverted)
3. Compare against the last known-good state
4. Fix the structure and re-save

### Visual Verification

After EVERY structural mutation, ask the user to verify the view renders before making the next change. Do not batch structural changes.

---

## Custom Card Research Workflow

> Addresses BL-022: Stable workflow for researching custom card capabilities.

### Documentation Lookup Order

When the user asks about custom card options or capabilities, follow this stable fallback order:

1. **Plugin reference first:** Check `references/dashboard-guide.md` popular cards section for common cards (Mushroom, mini-graph-card, button-card, card-mod, apexcharts-card, layout-card).

2. **HACS / installed resources:** Check what's installed:
   ```bash
   hass-cli raw get /api/lovelace/resources
   ```

3. **GitHub API:** Fetch the card's README directly:
   ```bash
   gh api repos/<owner>/<repo>/readme --jq .content | base64 -d
   ```
   Examples:
   - `gh api repos/kalkih/mini-graph-card/readme --jq .content | base64 -d`
   - `gh api repos/piitaya/lovelace-mushroom/readme --jq .content | base64 -d`

4. **Web search (last resort):** Only if the above fail or return rate-limited responses.

### Post-Install Availability

After installing a custom card via HACS, the HA frontend must reload before the new card type is recognized:
1. Hard-refresh the browser (Ctrl+Shift+R / Cmd+Shift+R)
2. If that doesn't work, restart Home Assistant

Do NOT attempt to use a newly installed card type in a dashboard save until the user confirms the frontend has reloaded.

### Common Mistake

Each custom card has its own configuration schema. Do NOT guess option names based on other cards or built-in cards. Always check the card's README for supported options.
