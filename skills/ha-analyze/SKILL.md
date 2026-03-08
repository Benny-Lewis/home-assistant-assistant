---
name: ha-analyze
description: Analyze Home Assistant setup and provide improvement suggestions. Use when user asks for "analysis", "suggestions", "improvements", "optimization", or "review my setup".
user-invocable: true
allowed-tools: Read, Bash, Glob, Grep, AskUserQuestion
---

# Analyze Home Assistant Setup

> **Data-Derived Analysis:** All metrics and suggestions must be backed by evidence.
> Do NOT invent statistics. Only report what was actually measured.
> Never use approximate counts. If you cannot measure a value exactly, write `not available`.

Perform comprehensive analysis of the Home Assistant configuration and provide actionable suggestions for improvements, new automations, and optimizations.

## Evidence Requirements

Every metric reported must include:
1. How it was measured (command or file read)
2. Actual count/value (not estimated)
3. Source (hass-cli output, file path, or "not available")
4. Availability status (`Ran`, `Unavailable`, or `Skipped`)

Example:
```text
Entities: 147 (status: Ran, source: hass-cli -o json raw get /api/states)
Automations: 23 (status: Ran, source: grep -c "^- id:" automations.yaml)
Notify services: not available (status: Unavailable, source: hass-cli -o json raw get /api/services)
```

Do NOT report metrics you cannot verify.

## Operating Rules

- Do NOT edit config files directly or deploy from `/ha-analyze`.
- Do NOT mix live hass-cli calls with file reads in the same parallel batch.
- Do NOT use browser automation for HA analysis.
- Every recommendation must include `Observed:`, `Inference:`, and `Next skill:`.
- If a source fails, continue with remaining sources and record the failure in the evidence table.

## Analysis Areas

If `$ARGUMENTS` are provided, focus on the requested area:
- `automations` - automation efficiency and opportunities
- `energy` - energy management and monitoring
- `security` - security-related suggestions
- `presence` - presence detection improvements
- `performance` - configuration optimization

If no arguments are provided, analyze all areas.

## Data Collection

### Step 0: Orientation Snapshot

Prefer the overview helper first. It returns exact JSON metrics plus source availability.

```bash
PY="$(cat .claude/ha-python.txt 2>/dev/null)"
if [ -z "$PY" ]; then
  for candidate in python3 python py; do
    if command -v "$candidate" >/dev/null 2>&1; then
      PY="$candidate"
      break
    fi
  done
fi

PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt 2>/dev/null)"
if [ -n "$PY" ] && [ -n "$PLUGIN_ROOT" ] && [ -f "$PLUGIN_ROOT/helpers/ha-overview.py" ]; then
  "$PY" "$PLUGIN_ROOT/helpers/ha-overview.py" snapshot
fi
```

If the helper is unavailable, continue with the direct commands below and record the helper as `Unavailable`. Do NOT spawn an agent just to locate the helper.

### Step 1: Live Overview Commands

Run these in order. Keep them in a live-data batch separate from file reads.

```bash
hass-cli -o json area list
hass-cli -o json device list
hass-cli -o json entity list
hass-cli -o json raw get /api/states
hass-cli -o json raw get /api/services
```

### Step 2: Local Config Commands

Run these in a separate batch from live data:

```bash
grep -c "^- id:" automations.yaml
grep -c "^  description: ''$" automations.yaml
grep -R "notify\\.|person\\.|doorbell|humidity|lock\\." dashboards templates configuration.yaml automations.yaml
```

### Step 3: Targeted Follow-ups

Only run follow-ups after the overview is complete. Examples:

```bash
hass-cli state get person.<name>
hass-cli state get binary_sensor.indoor_humidity_alert
hass-cli state get lock.<name>
hass-cli state list | grep "^automation\\."
```

When naming a specific entity, automation, or dashboard in a recommendation, cite the command or file read that supports it.

## Analysis Categories

### 1. Automation Opportunities

Identify measured gaps such as:
- motion/occupancy sensors that are not referenced by matching room automations
- people/device trackers that exist without home/away automation references
- alerts/sensors that exist without a notification path

### 2. Energy Analysis

Look for:
- energy or humidity sensors with no action path
- always-on or unavailable devices that should be investigated or cleaned up
- climate-related entities with monitoring but no automation references

### 3. Security Analysis

Look for:
- locks, door sensors, cameras, or doorbell entities with no notification or away-mode references
- unavailable security devices that create blind spots
- actual notify service availability before claiming notification gaps

### 4. Presence Detection

Look for:
- `person.*` entities and device tracker counts
- excessive unavailable device trackers that indicate tracker clutter
- missing home/away automation references

### 5. Configuration Health

Look for:
- blank descriptions
- unused or stale recovery files
- unavailable entities that still influence dashboards or automations

## Smart Suggestion Rules

- Label raw facts as `Observed:`.
- Label conclusions as `Inference:`.
- If a conclusion is only likely, say so explicitly.
- Point to one downstream skill with `Next skill:`.
- Do not recommend cleanup/removal for a specific entity unless you have exact evidence for it.

## Output Format

```text
Home Assistant Analysis Report

Evidence Table
| Source | Command/File | Status | Exact Value |
|--------|--------------|--------|-------------|
| Overview helper | helpers/ha-overview.py snapshot | Ran | entities=625 |
| Areas | hass-cli -o json area list | Ran | 19 |
| Devices | hass-cli -o json device list | Ran | 125 |
| Live states | hass-cli -o json raw get /api/states | Ran | 625 |
| Services | hass-cli -o json raw get /api/services | Ran | notify=3 |
| automations.yaml | grep -c "^- id:" automations.yaml | Ran | 25 |

Overview
- Entities: 625
- Automations: 25
- Areas: 19
- Devices: 125
- Unavailable entities: 195
- Device trackers: 49
- Unavailable device trackers: 45

Top Recommendations

1. HIGH IMPACT: Clean up stale presence trackers
   Observed: 49 device_tracker entities exist and 45 are currently unavailable.
   Inference: This likely indicates tracker clutter rather than active presence coverage.
   Next skill: ha-troubleshooting

2. HIGH IMPACT: Add presence-based actions only if usage is verified
   Observed: person.ben exists and no home/away automation references were found.
   Inference: Presence-based automations are likely missing.
   Next skill: ha-automations

3. QUICK WIN: Fill in blank automation descriptions
   Observed: 8 automations still use description: ''.
   Inference: This is a maintainability gap, not a runtime bug.
   Next skill: ha-automations

Detailed Analysis

Automations:
  Cite exact counts and exact references only.

Energy:
  Separate measured facts from suggestions.

Security:
  Do not claim missing alerts unless you checked notify services and automation references.

Performance:
  Do not call the config "efficient" without measured support.

Next Steps:
  Ask one routing question only:
  "Which should I do next: build an automation, investigate a device issue, review naming/config hygiene, or stop here?"
```

## Interactive Mode

After presenting analysis:
1. Ask one routing question.
2. Route to exactly one appropriate skill:
   - automation changes -> `ha-automations`
   - script changes -> `ha-scripts`
   - scene changes -> `ha-scenes`
   - naming/organization -> `ha-naming`
   - device issues -> `ha-troubleshooting`
   - new devices -> `ha-devices`
3. If no next action is chosen, stop after the analysis summary.

## Scheduling

Suggest running analysis periodically:

```text
Tip: Run /ha-analyze monthly to discover new optimization opportunities as your setup evolves.
```
