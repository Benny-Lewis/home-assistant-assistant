# Diagnostic API Procedures

Runbook for querying History, Logbook, and Traces from Home Assistant to gather evidence during troubleshooting.

## Contents

- [History API](#history-api) — raw state change timeline
- [Logbook API](#logbook-api) — human-readable event causation chain
- [Trace API](#trace-api-via-trace-fetchpy) — automation/script execution steps
- [When to Use Which](#when-to-use-which)

---

## History API

### Command Syntax

```bash
# Basic (last 24h)
MSYS_NO_PATHCONV=1 hass-cli raw get "/api/history/period?filter_entity_id=<entity_id>"

# With end time (URL-encoded ISO timestamp)
MSYS_NO_PATHCONV=1 hass-cli raw get "/api/history/period?filter_entity_id=<entity_id>&end_time=2026-02-17T23%3A00%3A00"

# Faster response (strips intermediate attributes)
MSYS_NO_PATHCONV=1 hass-cli raw get "/api/history/period?filter_entity_id=<entity_id>&minimal_response"

# Multiple entities
MSYS_NO_PATHCONV=1 hass-cli raw get "/api/history/period?filter_entity_id=light.kitchen,binary_sensor.motion"
```

### Key Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `filter_entity_id` | (none) | Comma-separated entity IDs — ALWAYS specify this |
| `end_time` | now | End of window (ISO 8601, URL-encoded) |
| `minimal_response` | false | Strips attributes from intermediate states |
| `no_attributes` | false | Strips all attributes |

### Response Shape

Array of arrays — outer per entity, inner per state change:

```json
[
  [
    {
      "entity_id": "light.kitchen",
      "state": "on",
      "attributes": {"brightness": 128},
      "last_changed": "2026-02-17T10:30:00+00:00",
      "last_updated": "2026-02-17T10:30:00+00:00"
    },
    ...
  ]
]
```

With `minimal_response`: intermediate states only have `state` + `last_changed`.

### Interpretation

- Empty inner array → entity exists but no state changes in period
- Empty outer array → entity not found or outside retention window (~10 day default)
- Build timeline by scanning `last_changed` timestamps in order
- Check whether trigger entity actually reached the expected state at the expected time

### Gotchas

- `MSYS_NO_PATHCONV=1` required on Windows/MINGW64 (prevents Git Bash mangling the URL)
- Default window is 1 day before request time — extend with `end_time` if debugging older events
- Always use `filter_entity_id` — unfiltered returns ALL entities (huge, slow)
- `end_time` uses `&` not `?` — common mistake: `...period?end_time=...` (wrong) vs `...period?filter_entity_id=X&end_time=...` (correct)

---

## Logbook API

### Command Syntax

```bash
# Last 24h, all entities (broad — add entity filter)
MSYS_NO_PATHCONV=1 hass-cli raw get /api/logbook

# Filter to one entity
MSYS_NO_PATHCONV=1 hass-cli raw get "/api/logbook?entity=<entity_id>"

# With time range
MSYS_NO_PATHCONV=1 hass-cli raw get "/api/logbook/<start_ISO>?end_time=<end_ISO>"
# Example: /api/logbook/2026-02-17T22:00:00?end_time=2026-02-17T23:00:00
```

### Key Parameters

| Parameter | Notes |
|-----------|-------|
| `entity` | Single entity_id — NOT comma-separated (only one per request) |
| `<start_ISO>` | Path segment, URL-encoded ISO timestamp for window start |
| `end_time` | Query parameter, end of window |

### Logbook vs History

| | Logbook | History |
|--|---------|---------|
| Format | Human-readable events ("turned on by automation") | Raw state values (on/off/123.4) |
| Use for | Causation: what triggered what | Timeline: did state X happen at time Y? |
| Entity filter | One entity only | Multiple comma-separated |

### Response Shape

Flat array of event objects:

```json
[
  {
    "when": "2026-02-17T22:31:00.123456+00:00",
    "name": "Kitchen Light",
    "message": "turned on",
    "entity_id": "light.kitchen",
    "domain": "light",
    "context_entity_id": "automation.motion_light",
    "context_entity_id_name": "Motion Light",
    "context_message": "triggered by state of binary_sensor.kitchen_motion"
  }
]
```

### Interpretation

- `"triggered by state of X"` → automation fired because entity X changed
- `context_entity_id` shows WHICH automation/script caused a change
- Use logbook to trace causation chains: "light turned on → which automation did it? → what triggered that?"
- Absence of an expected event = entity was never in that state during the window

### Gotchas

- `entity` parameter is SINGULAR — no comma-separated lists (unlike history's `filter_entity_id`)
- Make one request per entity if you need multiple
- Results may include service calls and other HA events alongside state changes

---

## Trace API (via trace-fetch.py helper)

### Why a Helper

- `/api/trace` REST endpoint does not exist (returns 404)
- `hass-cli raw ws` is broken on HA 2026.2+ (returns "Unknown command")
- The `trace-fetch.py` helper uses Python `websockets` library to connect directly to the HA WebSocket API

### Command Syntax

```bash
# Discover Python and plugin root from breadcrumb files
PY="$(cat .claude/ha-python.txt 2>/dev/null || command -v python3 || command -v python || command -v py)"
PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt 2>/dev/null || echo '.')"

# List recent traces (shows run_id, timestamp, state, trigger)
$PY "$PLUGIN_ROOT/helpers/trace-fetch.py" list automation.<name>
$PY "$PLUGIN_ROOT/helpers/trace-fetch.py" list script.<name>

# Get full trace for a specific run
$PY "$PLUGIN_ROOT/helpers/trace-fetch.py" get automation.<name> <run_id>
```

### Response: List Mode

```
run_id                                    timestamp             state       trigger
---...---
920aa6b0f792d39f5ab2d2ca5cf1a8bb          2026-02-18 05:29:23   stopped     state of binary_sensor.downstairs_bathroom_motion
```

Fields:
- `run_id` — identifier for use with `get` command
- `timestamp` — UTC start time of the run (local display)
- `state` — `stopped` (completed), `running`, or error state
- `trigger` — human-readable description of what triggered the run

### Response: Get Mode

Full JSON trace (pipe to a file or `| python -m json.tool` for readability). Key top-level fields:

| Field | Description |
|-------|-------------|
| `trigger` | What triggered the automation (human-readable) |
| `state` | Final state: `stopped`, `running`, `error` |
| `script_execution` | `finished`, `aborted`, `error` |
| `trace` | Dict of path → step data (see below) |
| `config` | The automation YAML config at time of run |

### Trace Path Navigation

The `trace` dict uses dotted paths as keys:

| Path | Meaning |
|------|---------|
| `trigger/0` | Trigger that fired; `changed_variables.trigger` has platform, entity, from/to state |
| `condition/0`, `condition/1` | Each condition; `result.result` is `true` (passed) or `false` (failed) |
| `action/0`, `action/1` | Each action; `result.params` shows what was called; `error` key if it failed |

### Common Patterns

| Symptom | What to look for in trace |
|---------|--------------------------|
| Automation never triggered | No entries in `list` output |
| Triggered but action didn't run | `condition/N` has `result.result: false` |
| Action ran but nothing happened | `action/N.result.params` — check service/target |
| Action errored | `action/N.error` key present |
| Wrong trigger | `trigger/0.changed_variables.trigger.entity_id` — is it the right entity? |

### Gotchas

- Automations need an `id:` field in YAML for traces to be stored (UI-created automations have this automatically)
- Only the last 5 traces are kept by default (configurable via `stored_traces:` in the automation)
- Traces are in-memory — lost on HA restart
- Traces are keyed by `unique_id` internally (the helper handles resolution automatically)
- Scripts also support traces: use `script.<name>` with the same commands

---

## When to Use Which

| Question | Use |
|----------|-----|
| Did entity X reach state Y? | History API |
| When did entity X change? | History API |
| What automation turned on light Y? | Logbook API (filter by light Y, check `context_entity_id`) |
| What triggered automation X? | Trace API (`list` then `get`) |
| Which condition failed? | Trace API (`get`, inspect `condition/N.result.result`) |
| What actions ran? | Trace API (`get`, inspect `action/N.result`) |
| Did the automation even run? | Trace API (`list`) + History API (trigger entity) |
| Is there an error in execution? | Trace API (`get`, look for `error` keys) + Error logs |
