# ha-naming — Audit Workflow

> **This workflow is READ-ONLY.** It analyzes and reports, but does NOT modify.
> To apply changes, use `/ha-apply-naming` after reviewing the audit.

Scan all entities, devices, areas, automations, scripts, and scenes for naming inconsistencies.

**Agent usage:** If spawning the naming-analyzer agent, do NOT use `run_in_background: true` — background agents silently lose all output ([Claude Code #17011](https://github.com/anthropics/claude-code/issues/17011)). Always use foreground execution.

## Data Source Citation

**Every finding must cite its source:**

```
Issue: light.light_1 has no descriptive name
Source: hass-cli entity list | grep "light.light"
```

Do NOT report issues for entities you haven't verified exist.

## What Gets Audited

1. **Entity IDs** (`entity_id`) - Format: `domain.identifier`, lowercase, underscores only
2. **Friendly Names** (`friendly_name`) - Consistent capitalization style
3. **Device Names** - Consistent pattern across similar devices
4. **Area Names** - Consistent naming style
5. **Automation Names** (`alias`) - Descriptive, consistent pattern
6. **Script Names** - Action-oriented naming
7. **Scene Names** - Descriptive naming

## Existing Conventions Check

Before collecting entity data, scan for existing naming specs:

Glob patterns: `**/naming*`, `**/convention*`, `**/*style*guide*`
Also check: `.claude/ha.conventions.json`

If found, read them and report: "Found existing naming conventions at {path}. Incorporating into audit."

## Data Prefetch (MANDATORY before agent spawn)

**Collect ALL raw data once in the skill, write to temp files, then pass file paths to the agent.**
This eliminates duplicate hass-cli calls between the skill and the naming-analyzer agent.

Run these commands in parallel (use `timeout: 60000` for large setups):

```bash
# JSON outputs for structured analysis
hass-cli -o json entity list > .claude/ha-prefetch-entities.json
hass-cli -o json area list > .claude/ha-prefetch-areas.json
hass-cli -o json device list > .claude/ha-prefetch-devices.json

# Tabular state list for quick domain counting
hass-cli state list > .claude/ha-prefetch-states.txt
```

After prefetch, count entities from the states file to determine output scaling tier:
```bash
# Count entities (skip header line)
tail -n +2 .claude/ha-prefetch-states.txt | wc -l
```

**Do NOT run a separate background task for compliance statistics.** All analysis — including compliance rates — must be performed by the naming-analyzer agent in a single foreground pass over the prefetched data.

When spawning the naming-analyzer agent, instruct it to read from these prefetch files:
> "Analyze the prefetched data in `.claude/ha-prefetch-entities.json`, `.claude/ha-prefetch-areas.json`, `.claude/ha-prefetch-devices.json`, and `.claude/ha-prefetch-states.txt`."

**From local config files (also prefetch or let agent read directly):**
- Parse automations.yaml for automation names
- Parse scripts.yaml for script names
- Parse scenes.yaml for scene names
- Scan packages/ for all entity definitions

## Pattern Detection

Identify existing naming patterns:
- Area prefix: `living_room_light`, `bedroom_fan`
- Device type suffix: `light_ceiling`, `sensor_temperature`
- Function-based: `motion_sensor`, `door_lock`
- Mixed patterns (inconsistent)

## Area Coverage Check (MANDATORY)

The audit MUST include an "Area Coverage" section that cross-references entity prefixes with the area registry. This catches mismatches the user would otherwise have to identify manually.

**What to check:**
1. **Unmatched prefixes** — entity ID prefixes (e.g., `garage_*`) that have no corresponding area in the registry
2. **Empty areas** — areas registered in HA with zero entities assigned
3. **ID vs prefix mismatches** — area IDs that don't match the prefix convention used by their entities (e.g., area `ll_bath` but entities use `downstairs_bathroom_*`)
4. **Ambiguous areas** — area names that may need disambiguation (e.g., "hallway" when there are upstairs and downstairs hallways)

**How:** Cross-reference `.claude/ha-prefetch-areas.json` with entity ID prefixes extracted from `.claude/ha-prefetch-entities.json`.

Present findings proactively — do NOT wait for the user to ask "what areas do I have?"

## Inconsistency Types

1. **Case Inconsistencies** - `Living Room` vs `living room` vs `LIVING ROOM`
2. **Separator Inconsistencies** - `living_room` vs `living-room` vs `livingroom`
3. **Pattern Inconsistencies** - `kitchen_light` but `light_bedroom`
4. **Abbreviation Inconsistencies** - `temp` vs `temperature`
5. **Missing Context** - Generic names: `light.light`, `switch.switch_1`

## Audit Report Format

The audit report MUST include an evidence table (Safety Invariant #6) showing what data sources were checked:

```
## What Ran vs Skipped

| Check                  | Status  | Result                     |
|------------------------|---------|----------------------------|
| Entity registry scan   | Ran     | 147 entities               |
| Area registry scan     | Ran     | 12 areas                   |
| Device registry scan   | Ran     | 45 devices                 |
| State list scan        | Ran     | 147 states                 |
| Config file ref scan   | Ran     | 8 references found         |
| Area coverage check    | Ran     | 2 mismatches               |
| Existing spec check    | Ran     | Found at .claude/naming.md |
| Existing plan check    | Skipped | No plan file found         |
```

Then the analysis body:

```
Naming Audit Report

Entities Scanned: 147
Issues Found: 23

Pattern Analysis
Primary pattern detected: {area}_{device_type}
Coverage: 68% of entities follow this pattern

Issues by Category

Critical (blocking search/automation):
  - light.light_1 - No descriptive name
  - switch.switch - Duplicate generic name

Inconsistent Naming:
  - light.living_room_ceiling vs light.bedroom_light_ceiling
    Suggested: light.bedroom_ceiling (match pattern)

Missing Friendly Names:
  - binary_sensor.motion_1 - No friendly_name set

Style Suggestions:
  - Automation "turn on lights" - suggest "Motion: Living Room Lights On"

Summary
  Critical issues: 2
  Inconsistencies: 12
  Missing names: 5
  Style suggestions: 4

Next Steps:
  1. Run /ha-naming to create a rename plan
  2. Review and adjust the plan
  3. Run /ha-apply-naming to execute renames
```

## Audit Recommendations

Based on audit findings:
1. **Suggest a naming convention** based on majority pattern
2. **Prioritize fixes** by impact (critical -> style)
3. **Group related changes** (all lights, all sensors, etc.)
4. **Identify automation dependencies** that would break

## Audit Options

- `--json` - Output as JSON for programmatic use
- `--brief` - Summary only, no details
- `--domain [domain]` - Audit specific domain only (lights, switches, etc.)
