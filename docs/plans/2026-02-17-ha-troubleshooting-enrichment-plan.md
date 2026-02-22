# ha-troubleshooting Enrichment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enrich ha-troubleshooting with History, Logbook, and Trace diagnostic procedures so Claude can query what actually happened instead of just giving advice.

**Architecture:** New `references/diagnostic-api.md` documents History and Logbook REST API procedures. New `helpers/trace-fetch.py` uses Python `websockets` library to bypass broken `hass-cli raw ws` for trace access. SKILL.md gets minimal additions (logbook step, fixed trace command, reference link). Existing broken trace commands in SKILL.md, log-patterns.md, and ha-log-analyzer.md are fixed.

**Tech Stack:** hass-cli (REST API), Python websockets library (WebSocket API for traces), markdown

**Verified endpoints (2026-02-17):**
- History: `hass-cli raw get "/api/history/period?filter_entity_id=X"` — works
- Logbook: `hass-cli raw get "/api/logbook?entity=X"` — works
- Trace REST: `hass-cli raw get /api/trace/automation.X` — **404, does not exist**
- Trace WebSocket via hass-cli: `hass-cli raw ws '{"type":"trace/list",...}'` — **broken (Unknown command)**
- Python websockets: installed (v16.0), can connect directly to HA WebSocket API

---

### Task 1: Create trace-fetch.py helper

**Files:**
- Create: `helpers/trace-fetch.py`

**Reference:** ha-mcp's `tools_traces.py` and `websocket_client.py` (at `C:/Users/Ben/dev/ha-mcp/src/ha_mcp/`) for the WebSocket protocol and trace data structure. Adapt, don't copy — our helper is a standalone CLI script, not an MCP tool.

**Step 1: Write the helper script**

Follow the `area-search.py` pattern:
- Shebang + docstring with usage
- Read `HASS_SERVER` and `HASS_TOKEN` from env vars
- CLI commands: `list <entity_id>`, `get <entity_id> <run_id>`
- WebSocket flow: connect → auth_required → send auth → auth_ok → send command → receive → disconnect
- Resolve entity_id → unique_id via `config/entity_registry/get` (traces are keyed by unique_id, with object_id fallback)
- Human-readable output (not JSON) for `list` mode (run_id, timestamp, state, trigger)
- JSON output for `get` mode (full trace data — too complex for tabular display)
- Error handling: connection refused, auth failed, entity not found, no traces stored
- Requires `websockets` library (already installed with hass-cli's Python)

Key details from ha-mcp to preserve:
- `trace/list` takes `domain` and `item_id` (the unique_id, NOT entity_id)
- `trace/get` takes `domain`, `item_id`, and `run_id`
- WebSocket URL: replace `http(s)` scheme with `ws(s)`, append `/api/websocket`
- Auth message: `{"type": "auth", "access_token": "<token>"}`
- Command message: `{"id": N, "type": "<command>", ...params}`

**Step 2: Test the helper**

Run against live HA instance:
```bash
PY="$(cat .claude/ha-python.txt 2>/dev/null || command -v python3 || command -v py)"
PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt 2>/dev/null || echo '.')"

# List traces for an automation
$PY "$PLUGIN_ROOT/helpers/trace-fetch.py" list automation.downstairs_bathroom_motion_light_on

# Get a specific trace (use run_id from list output)
$PY "$PLUGIN_ROOT/helpers/trace-fetch.py" get automation.downstairs_bathroom_motion_light_on <run_id>

# Error cases
$PY "$PLUGIN_ROOT/helpers/trace-fetch.py" list automation.nonexistent_automation
$PY "$PLUGIN_ROOT/helpers/trace-fetch.py"  # No args — should show usage
```

Expected: `list` shows recent traces with run_id, timestamp, state, trigger. `get` shows full trace JSON. Error cases show helpful messages.

**Step 3: Commit**

```bash
git add helpers/trace-fetch.py
git commit -m "feat: add trace-fetch.py helper for WebSocket-based trace access

hass-cli raw ws is broken on HA 2026.2+ and /api/trace REST endpoint
does not exist. This helper uses Python websockets library to connect
directly to HA WebSocket API for trace/list and trace/get commands."
```

---

### Task 2: Create diagnostic-api.md reference

**Files:**
- Create: `skills/ha-troubleshooting/references/diagnostic-api.md`

**Step 1: Write the reference file**

Structure (~140-160 lines):
```markdown
# Diagnostic API Procedures

[one-line purpose]

## Contents
- History API
- Logbook API
- Trace API
- When to Use Which

## History API

### Command Syntax
- Basic (last 24h): MSYS_NO_PATHCONV=1 hass-cli raw get "/api/history/period?filter_entity_id=<id>"
- With time range: add &end_time= (URL-encoded ISO timestamp)
- Faster response: add &minimal_response (strips intermediate attributes)
- Multiple entities: comma-separate in filter_entity_id

### Key Parameters
[table: parameter, default, notes]

### Response Shape
- Array of arrays: outer = per entity, inner = state change objects
- Each object: entity_id, state, attributes, last_changed, last_updated
- With minimal_response: intermediate states only have state + last_changed

### Interpretation
- Empty inner array = entity exists but no state changes in period
- Empty outer array = entity not found or outside retention window
- Check last_changed timestamps to build timeline of what happened
- ~10 day retention limit (configurable via recorder purge_keep_days)

### Gotchas
- MSYS_NO_PATHCONV=1 required on Windows/MINGW
- Default window is 1 day before request time
- Always use filter_entity_id — unfiltered returns ALL entities (huge response)
- end_time uses & not ? (common mistake: double ?)

## Logbook API

### Command Syntax
- Basic (last 24h, all entities): MSYS_NO_PATHCONV=1 hass-cli raw get /api/logbook
- Entity-filtered: MSYS_NO_PATHCONV=1 hass-cli raw get "/api/logbook?entity=<entity_id>"
- With time range: /api/logbook/<start_timestamp>?end_time=<end>

### Key Parameters
[table]

### Logbook vs History
[brief explanation: logbook = human events ("turned on", "triggered by"), history = raw state values]

### Response Shape
- Flat array of event objects
- Key fields: when, name, message, entity_id, domain
- Context fields (when caused by automation): context_entity_id, context_entity_id_name, context_message

### Interpretation
- "triggered by state of X" = automation fired because entity X changed
- context_entity_id shows WHICH automation/script caused a change
- Use for "what caused this?" questions — logbook traces causation chains

### Gotchas
- entity parameter is SINGULAR (not filter_entity_id, not comma-separated)
- Only one entity per request (unlike history)

## Trace API (via trace-fetch.py helper)

### Why a Helper
- /api/trace REST endpoint does not exist (returns 404)
- hass-cli raw ws is broken on HA 2026.2+ (returns "Unknown command")
- Helper uses Python websockets library to connect directly

### Command Syntax
[show helper invocation with breadcrumb discovery pattern]

### Response: List Mode
[show fields: run_id, timestamp, state, trigger]

### Response: Get Mode
[explain trace structure: trigger info, condition results, action trace]

### Trace Path Navigation
- trigger/0: what triggered the automation
- condition/0, condition/1: which conditions passed/failed (result: true/false)
- action/0, action/1: which actions ran, errors, timing

### Common Patterns
[table: symptom → what to look for in trace]

### Gotchas
- Automations need an `id:` field in YAML for traces to be stored
- Only last 5 traces kept by default (configurable via stored_traces)
- Traces are in-memory — lost on HA restart
- Traces keyed by unique_id internally (helper handles resolution)

## When to Use Which

[decision table: user question → API]
```

**Step 2: Verify commands work**

Run each documented command against live HA:
```bash
# History
MSYS_NO_PATHCONV=1 hass-cli raw get "/api/history/period?filter_entity_id=light.downstairs_bathroom&minimal_response" | head -20

# Logbook with entity filter
MSYS_NO_PATHCONV=1 hass-cli raw get "/api/logbook?entity=automation.downstairs_bathroom_motion_light_on" | head -20
```

Expected: Both return data matching the documented response shapes.

**Step 3: Commit**

```bash
git add skills/ha-troubleshooting/references/diagnostic-api.md
git commit -m "docs: add diagnostic API reference for troubleshooting

Covers History API (REST), Logbook API (REST), and Trace API
(via trace-fetch.py helper). Includes command syntax, response
interpretation, and gotchas."
```

---

### Task 3: Update SKILL.md

**Files:**
- Modify: `skills/ha-troubleshooting/SKILL.md`

**Step 1: Apply changes**

Four changes:

**3a. Quick Reference table** — add logbook row, fix trace row:
```
| `MSYS_NO_PATHCONV=1 hass-cli raw get "/api/logbook?entity=X"` | Get logbook events |
```
Replace the broken trace command with the helper invocation.

**3b. Process step 3** — add step 3e (Logbook) after step 3d:
```markdown
   - **3e. Logbook events**
     ```bash
     MSYS_NO_PATHCONV=1 hass-cli raw get "/api/logbook?entity=<entity_id>"
     ```
     Shows automation triggers, state changes, and causation chains.
```

**3c. Evidence table** — add Logbook row to the template table.

**3d. Fix trace command** (step 3b) — replace `hass-cli raw get /api/trace/...` with:
```bash
PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt 2>/dev/null)"
PY="$(cat .claude/ha-python.txt 2>/dev/null || command -v python3 || command -v python || command -v py)"
$PY "$PLUGIN_ROOT/helpers/trace-fetch.py" list automation.<name>
```

**3e. References section** — add link to diagnostic-api.md:
```markdown
- `references/diagnostic-api.md` - History, Logbook, and Trace API procedures
```

**Step 2: Verify line count**

SKILL.md should stay well under 500 lines after changes (~135-140 lines).

**Step 3: Commit**

```bash
git add skills/ha-troubleshooting/SKILL.md
git commit -m "feat: add logbook step and fix trace command in ha-troubleshooting

- Add logbook events as step 3e in diagnostic process
- Fix broken trace REST command (404) with trace-fetch.py helper
- Add logbook row to evidence table template
- Link to new diagnostic-api.md reference"
```

---

### Task 4: Update log-patterns.md

**Files:**
- Modify: `skills/ha-troubleshooting/references/log-patterns.md`

**Step 1: Apply changes**

Three changes:

**4a. Automation Trace Analysis section** — fix the broken `hass-cli raw get /api/trace/...` command. Replace with trace-fetch.py helper invocation. Add cross-reference to diagnostic-api.md for detailed trace interpretation.

**4b. Evidence Table Template** — add Logbook row.

**4c. Debugging Checklist section** — fix step 2's broken trace reference. Add logbook as a step.

**Step 2: Commit**

```bash
git add skills/ha-troubleshooting/references/log-patterns.md
git commit -m "fix: replace broken trace REST command in log-patterns.md

Trace REST endpoint (/api/trace) returns 404. Updated to use
trace-fetch.py helper. Added logbook to evidence table and
debugging checklist."
```

---

### Task 5: Update ha-log-analyzer.md agent

**Files:**
- Modify: `agents/ha-log-analyzer.md`

**Step 1: Apply changes**

Three changes:

**5a. Gather Data section** — fix trace command (replace REST with helper), add logbook command.

**5b.** Add reference to diagnostic-api.md for detailed procedures.

**5c.** Add logbook to evidence table in Output Format section.

**Step 2: Commit**

```bash
git add agents/ha-log-analyzer.md
git commit -m "fix: update ha-log-analyzer with logbook and fixed trace command"
```

---

### Task 6: Version bump, changelog, final commit

**Files:**
- Modify: `.claude-plugin/plugin.json` — bump version to 1.2.0
- Modify: `.claude-plugin/marketplace.json` — bump version to 1.2.0
- Modify: `CHANGELOG.md` — add 1.2.0 entry

**Step 1: Bump versions**

Both files: `"version": "1.1.0"` → `"version": "1.2.0"`

**Step 2: Update CHANGELOG.md**

Add entry:
```markdown
## 1.2.0

### Added
- **Diagnostic API reference** (`references/diagnostic-api.md`) — History, Logbook, and Trace API procedures for ha-troubleshooting
- **trace-fetch.py helper** — WebSocket-based trace access bypassing broken hass-cli raw ws
- **Logbook diagnostic step** — step 3e in troubleshooting process with logbook event querying
- Logbook row in all evidence table templates

### Fixed
- **Broken trace command** — `/api/trace/automation.<name>` REST endpoint returns 404 (never existed). Replaced with trace-fetch.py helper across SKILL.md, log-patterns.md, and ha-log-analyzer.md
```

**Step 3: Commit**

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json CHANGELOG.md
git commit -m "chore: bump version to 1.2.0 with changelog"
```

---

## Task Dependency Graph

```
Task 1 (trace-fetch.py) ─┐
                          ├─→ Task 2 (diagnostic-api.md) ─→ Task 3 (SKILL.md) ─┐
                          │                                                      ├─→ Task 6 (version bump)
                          └─→ Task 4 (log-patterns.md) ─────────────────────────┤
                               Task 5 (ha-log-analyzer.md) ────────────────────┘
```

Tasks 1 must complete first (other tasks reference the helper). Tasks 3, 4, 5 can run in parallel after Task 2. Task 6 runs last.
