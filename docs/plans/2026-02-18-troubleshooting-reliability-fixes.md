# Troubleshooting Reliability Fixes — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix the 5 failure modes discovered in the v1.2.0 ha-troubleshooting manual test — eliminate the 23 minutes of wasted time on helper discovery, failed API calls, and retry loops.

**Architecture:** Add `history` and `logbook` REST API commands to `trace-fetch.py` (using stdlib `urllib.request`, bypassing hass-cli for query-param endpoints). Update all skill/agent markdown files to use a resilient helper discovery pattern with fast fallback. Add fail-fast env check and anti-agent-spawning guidance to the troubleshooting skill.

**Tech Stack:** Python 3 (stdlib only — `urllib.request`, `json`, `asyncio`, `websockets`), Markdown skill files

**Analysis doc:** `docs/testing/2026-02-18-manual-test-analysis.md`

---

## Task 1: Add `history` and `logbook` commands to trace-fetch.py

**Why:** `hass-cli raw get` with query parameters fails under MINGW due to URL mangling. trace-fetch.py already handles HASS_SERVER/HASS_TOKEN and works reliably. History and Logbook are REST APIs (not WebSocket), so we use `urllib.request` from stdlib.

**Files:**
- Modify: `helpers/trace-fetch.py`

**Step 1: Add the `history` command function**

Add after the `cmd_get` function (after line 225). Uses `urllib.request` to call `/api/history/period` directly:

```python
def cmd_history(entity_id: str, hours: int = 24) -> None:
    """Fetch state history for an entity via REST API."""
    hass_server = os.environ.get("HASS_SERVER", "").rstrip("/")
    token = os.environ.get("HASS_TOKEN", "")

    if not hass_server or not token:
        print("Error: HASS_SERVER and HASS_TOKEN environment variables must be set.")
        print("Run /ha-onboard to configure.")
        sys.exit(1)

    from datetime import datetime, timedelta, timezone
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError

    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)
    start_iso = start.strftime("%Y-%m-%dT%H:%M:%S") + "+00:00"

    url = (
        f"{hass_server}/api/history/period/{start_iso}"
        f"?filter_entity_id={entity_id}&minimal_response&no_attributes"
    )

    req = Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })

    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except HTTPError as e:
        print(f"Error: HTTP {e.code} from {hass_server}")
        if e.code == 401:
            print("Authentication failed — check HASS_TOKEN.")
        sys.exit(1)
    except URLError as e:
        print(f"Error: Could not connect to {hass_server}: {e.reason}")
        sys.exit(1)

    if not data or not data[0]:
        print(f"No history found for {entity_id} in the last {hours}h.")
        return

    states = data[0]
    print(f"History for {entity_id} (last {hours}h, {len(states)} entries):\n")
    print(f"{'timestamp':<25}  {'state':<15}")
    print("-" * 42)
    for s in states:
        ts = s.get("last_changed", "?")
        if "T" in str(ts) and ("+" in str(ts) or str(ts).endswith("Z")):
            ts = str(ts).split("+")[0].replace("T", " ")[:19]
        state = s.get("state", "?")
        print(f"{ts:<25}  {state:<15}")
```

**Step 2: Add the `logbook` command function**

Add after the `cmd_history` function:

```python
def cmd_logbook(entity_id: str, hours: int = 24) -> None:
    """Fetch logbook entries for an entity via REST API."""
    hass_server = os.environ.get("HASS_SERVER", "").rstrip("/")
    token = os.environ.get("HASS_TOKEN", "")

    if not hass_server or not token:
        print("Error: HASS_SERVER and HASS_TOKEN environment variables must be set.")
        print("Run /ha-onboard to configure.")
        sys.exit(1)

    from datetime import datetime, timedelta, timezone
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError

    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)
    start_iso = start.strftime("%Y-%m-%dT%H:%M:%S") + "+00:00"
    end_iso = end.strftime("%Y-%m-%dT%H:%M:%S") + "+00:00"

    url = (
        f"{hass_server}/api/logbook/{start_iso}"
        f"?entity={entity_id}&end_time={end_iso}"
    )

    req = Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })

    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except HTTPError as e:
        print(f"Error: HTTP {e.code} from {hass_server}")
        if e.code == 401:
            print("Authentication failed — check HASS_TOKEN.")
        sys.exit(1)
    except URLError as e:
        print(f"Error: Could not connect to {hass_server}: {e.reason}")
        sys.exit(1)

    if not data:
        print(f"No logbook entries for {entity_id} in the last {hours}h.")
        return

    print(f"Logbook for {entity_id} (last {hours}h, {len(data)} entries):\n")
    print(f"{'timestamp':<25}  {'entity':<40}  {'message'}")
    print("-" * 90)
    for entry in data:
        ts = entry.get("when", "?")
        if "T" in str(ts) and ("+" in str(ts) or str(ts).endswith("Z")):
            ts = str(ts).split("+")[0].replace("T", " ")[:19]
        name = entry.get("name", "?")
        message = entry.get("message", "")
        context = entry.get("context_message", "")
        line = f"{ts:<25}  {name:<40}  {message}"
        if context:
            line += f"  ({context})"
        print(line)
```

**Step 3: Wire up the new commands in `main()`**

Modify the `main()` function to add `history` and `logbook` subcommands. Replace the existing `main()` (lines 228-256):

```python
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        if len(sys.argv) < 3:
            print("Error: list requires an entity_id.")
            print("Usage: trace-fetch.py list <entity_id>")
            sys.exit(1)
        asyncio.run(cmd_list(sys.argv[2]))

    elif command == "get":
        if len(sys.argv) < 4:
            print("Error: get requires entity_id and run_id.")
            print("Usage: trace-fetch.py get <entity_id> <run_id>")
            sys.exit(1)
        asyncio.run(cmd_get(sys.argv[2], sys.argv[3]))

    elif command == "history":
        if len(sys.argv) < 3:
            print("Error: history requires an entity_id.")
            print("Usage: trace-fetch.py history <entity_id> [--hours N]")
            sys.exit(1)
        hours = 24
        if "--hours" in sys.argv:
            idx = sys.argv.index("--hours")
            if idx + 1 < len(sys.argv):
                hours = int(sys.argv[idx + 1])
        cmd_history(sys.argv[2], hours)

    elif command == "logbook":
        if len(sys.argv) < 3:
            print("Error: logbook requires an entity_id.")
            print("Usage: trace-fetch.py logbook <entity_id> [--hours N]")
            sys.exit(1)
        hours = 24
        if "--hours" in sys.argv:
            idx = sys.argv.index("--hours")
            if idx + 1 < len(sys.argv):
                hours = int(sys.argv[idx + 1])
        cmd_logbook(sys.argv[2], hours)

    else:
        print(f'Unknown command: "{command}"')
        print("Commands: list, get, history, logbook")
        sys.exit(1)
```

**Step 4: Update the module docstring**

Replace the docstring (lines 2-18) to document all four commands:

```python
"""Fetch automation traces, entity history, and logbook entries from Home Assistant.

Uses Python websockets for trace commands (WebSocket API) and urllib for
history/logbook commands (REST API). Bypasses hass-cli to avoid MINGW
path mangling issues with query-parameter URLs.

Requires: HASS_SERVER and HASS_TOKEN environment variables.
Requires: websockets library (installed with hass-cli's Python) for trace commands.

Usage:
    python trace-fetch.py list <entity_id>
    python trace-fetch.py get <entity_id> <run_id>
    python trace-fetch.py history <entity_id> [--hours N]
    python trace-fetch.py logbook <entity_id> [--hours N]

Examples:
    python trace-fetch.py list automation.motion_light
    python trace-fetch.py get automation.motion_light abc123-run-id
    python trace-fetch.py history binary_sensor.kitchen_motion --hours 12
    python trace-fetch.py logbook light.kitchen --hours 6
"""
```

**Step 5: Verify manually**

```bash
cd ~/dev/ha
py "C:/Users/Ben/dev/home-assistant-assistant/helpers/trace-fetch.py" history binary_sensor.downstairs_bathroom_motion --hours 4
py "C:/Users/Ben/dev/home-assistant-assistant/helpers/trace-fetch.py" logbook binary_sensor.downstairs_bathroom_motion --hours 4
py "C:/Users/Ben/dev/home-assistant-assistant/helpers/trace-fetch.py"  # Should show updated usage
```

Expected: history shows timestamped state changes, logbook shows event entries with context. Usage text lists all 4 commands.

**Step 6: Commit**

```bash
git add helpers/trace-fetch.py
git commit -m "feat: add history and logbook REST commands to trace-fetch.py

Bypasses hass-cli for /api/history and /api/logbook endpoints which fail
under MINGW due to query-parameter URL mangling. Uses stdlib urllib.request."
```

---

## Task 2: Add fail-fast environment check to SKILL.md

**Why:** The model retried failed hass-cli commands 5+ times without diagnosing the root cause. A single env check would have caught the issue instantly.

**Files:**
- Modify: `skills/ha-troubleshooting/SKILL.md:48-56` (Process section, before step 1)

**Step 1: Add Step 0 to the Process section**

Insert before `1. **Identify issue**` (line 50). Add this block:

```markdown
**Step 0: Verify environment** — run BEFORE any data gathering:
```bash
echo "HASS_SERVER=$HASS_SERVER"; echo "HASS_TOKEN is $([ -n "$HASS_TOKEN" ] && echo 'set' || echo 'NOT SET')"; which hass-cli 2>&1 || echo "hass-cli NOT IN PATH"
```

If HASS_SERVER or HASS_TOKEN is missing → tell user to run `/ha-onboard`. Stop.
If hass-cli is not in PATH → tell user to install: `pip install homeassistant-cli`. Stop.

> **Do NOT** retry hass-cli commands if this check fails. Do NOT spawn Explore or Bash agents to search for alternatives. Diagnose first, then act.
```

**Step 2: Verify the edit reads correctly**

Read `skills/ha-troubleshooting/SKILL.md` and confirm Step 0 appears before step 1 with correct formatting.

**Step 3: Commit**

```bash
git add skills/ha-troubleshooting/SKILL.md
git commit -m "fix: add fail-fast env check to ha-troubleshooting skill

Prevents the model from retrying failed hass-cli commands or spawning
expensive agents when env vars are simply missing."
```

---

## Task 3: Update helper discovery pattern — troubleshooting skill + references

**Why:** The breadcrumb pattern (`cat .claude/ha-plugin-root.txt`) failed because the async hook hadn't written the file yet. Need a resilient fallback that's fast and doesn't spawn agents.

**The new discovery pattern** (used everywhere helpers are referenced):

```bash
PY="$(cat .claude/ha-python.txt 2>/dev/null || command -v python3 || command -v python || command -v py)"
PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt 2>/dev/null)"
# Fallback if breadcrumb missing (async hook may not have run yet)
if [ ! -f "$PLUGIN_ROOT/helpers/trace-fetch.py" ]; then
  PLUGIN_ROOT="$(dirname "$(dirname "$(find "$HOME" -maxdepth 5 -path '*/home-assistant-assistant/helpers/trace-fetch.py' -type f 2>/dev/null | head -1)")" 2>/dev/null)"
fi
```

For area-search references, replace `trace-fetch.py` with `area-search.py` in the find.

**Files:**
- Modify: `skills/ha-troubleshooting/SKILL.md:64-70`
- Modify: `skills/ha-troubleshooting/references/diagnostic-api.md:154-165`
- Modify: `skills/ha-troubleshooting/references/log-patterns.md:89-99, 133-139`

**Step 1: Update SKILL.md helper block (lines 64-70)**

Replace the existing 3b trace command block with:

```markdown
   - **3b. Automation traces**
     ```bash
     PY="$(cat .claude/ha-python.txt 2>/dev/null || command -v python3 || command -v python || command -v py)"
     PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt 2>/dev/null)"
     if [ ! -f "$PLUGIN_ROOT/helpers/trace-fetch.py" ]; then
       PLUGIN_ROOT="$(dirname "$(dirname "$(find "$HOME" -maxdepth 5 -path '*/home-assistant-assistant/helpers/trace-fetch.py' -type f 2>/dev/null | head -1)")" 2>/dev/null)"
     fi
     $PY "$PLUGIN_ROOT/helpers/trace-fetch.py" list automation.<name>
     ```
     Shows trigger, conditions, actions, and variables for recent runs.
     Use `get automation.<name> <run_id>` for full trace detail.
     Note: `/api/trace` REST endpoint returns 404; `hass-cli raw ws` is broken on HA 2026.2+.
```

**Step 2: Update SKILL.md history/logbook steps (3d, 3e)**

Replace the existing `hass-cli raw get` commands for history (3d) and logbook (3e) with the new trace-fetch.py commands:

```markdown
   - **3d. Entity history**
     ```bash
     $PY "$PLUGIN_ROOT/helpers/trace-fetch.py" history <entity_id>
     ```
     Check whether the trigger entity reached the expected state.
     Use `--hours N` to widen the window (default: 24h).

   - **3e. Logbook events**
     ```bash
     $PY "$PLUGIN_ROOT/helpers/trace-fetch.py" logbook <entity_id>
     ```
     Shows automation triggers, state changes, and causation chains (what caused what).
     Use `--hours N` to widen the window (default: 24h).
```

**Step 3: Update Quick Reference table**

Replace the history and logbook rows in the Quick Reference table (lines 39-40) with:

```markdown
| `$PY "$PLUGIN_ROOT/helpers/trace-fetch.py" history <entity_id>` | Entity state history |
| `$PY "$PLUGIN_ROOT/helpers/trace-fetch.py" logbook <entity_id>` | Logbook events (causation chain) |
```

**Step 4: Update diagnostic-api.md**

In `skills/ha-troubleshooting/references/diagnostic-api.md`:

- Update the trace command syntax block (lines 154-165) to use the new discovery pattern with fallback
- Update the History API section (lines 18-30) to show `trace-fetch.py history` as primary, with hass-cli as fallback
- Update the Logbook API section (lines 82-92) to show `trace-fetch.py logbook` as primary, with hass-cli as fallback
- Add notes about MINGW query param issues in the Gotchas sections

**Step 5: Update log-patterns.md**

In `skills/ha-troubleshooting/references/log-patterns.md`:

- Update both trace command blocks (lines 89-99 and 133-139) to use the new discovery pattern with fallback
- Update the History API reference in the debugging checklist (line 124) to use `trace-fetch.py history`
- Update the Logbook API reference (line 129) to use `trace-fetch.py logbook`

**Step 6: Verify edits**

Read all three files and confirm:
- Discovery pattern has fallback `find` in all code blocks
- History/Logbook now point to trace-fetch.py
- No orphaned `hass-cli raw get` references for history/logbook (keep them only in diagnostic-api.md as documented fallback)

**Step 7: Commit**

```bash
git add skills/ha-troubleshooting/SKILL.md skills/ha-troubleshooting/references/diagnostic-api.md skills/ha-troubleshooting/references/log-patterns.md
git commit -m "fix: resilient helper discovery + Python helper for history/logbook

Replace fragile breadcrumb-only discovery with find fallback.
Switch history/logbook from hass-cli raw get (MINGW-broken) to trace-fetch.py."
```

---

## Task 4: Update helper discovery pattern — resolver skill + agents

**Why:** Same breadcrumb fragility affects ha-resolver and agent files for area-search.py.

**Files:**
- Modify: `skills/ha-resolver/SKILL.md:62-71, 108-115`
- Modify: `skills/ha-resolver/references/area-search.md:14-25`
- Modify: `agents/ha-entity-resolver.md:43-59`
- Modify: `agents/ha-log-analyzer.md:41-48`

**The area-search discovery pattern:**

```bash
PY="$(cat .claude/ha-python.txt 2>/dev/null || command -v python3 || command -v python || command -v py)"
PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt 2>/dev/null)"
if [ ! -f "$PLUGIN_ROOT/helpers/area-search.py" ]; then
  PLUGIN_ROOT="$(dirname "$(dirname "$(find "$HOME" -maxdepth 5 -path '*/home-assistant-assistant/helpers/area-search.py' -type f 2>/dev/null | head -1)")" 2>/dev/null)"
fi
$PY "$PLUGIN_ROOT/helpers/area-search.py" search "<area_name>"
```

**Step 1: Update ha-resolver SKILL.md — first block (lines 62-71)**

Replace the discovery + command block with the resilient pattern above. Keep the fallback note about manual hass-cli commands if `$PLUGIN_ROOT` is still empty.

**Step 2: Update ha-resolver SKILL.md — second block (lines 108-115)**

Same replacement — use the resilient discovery pattern.

**Step 3: Update area-search.md reference (lines 14-25)**

Replace the command block with the resilient pattern. Keep the fallback note.

**Step 4: Update ha-entity-resolver.md agent (lines 43-59)**

Replace the discovery + command block. Keep the existing fallback note about manual hass-cli commands.

**Step 5: Update ha-log-analyzer.md agent (lines 41-48)**

Replace with the trace-fetch.py discovery pattern (this agent uses trace-fetch, not area-search).

**Step 6: Verify edits**

Read all 4 files and confirm the discovery pattern is consistent.

**Step 7: Commit**

```bash
git add skills/ha-resolver/SKILL.md skills/ha-resolver/references/area-search.md agents/ha-entity-resolver.md agents/ha-log-analyzer.md
git commit -m "fix: resilient helper discovery for resolver skill and agents

Same fallback pattern as troubleshooting skill — breadcrumb primary,
find fallback for when async hook hasn't written yet."
```

---

## Task 5: Add anti-agent-spawning guidance to SKILL.md

**Why:** The model spawned an Explore agent (41 tool uses, 2 min) and a Bash agent (25 tool uses, 20 min) when simple diagnostics would have sufficed.

**Files:**
- Modify: `skills/ha-troubleshooting/SKILL.md` (in the Process section, after the new Step 0)

**Step 1: Add guidance callout**

Insert this after the Step 0 environment check block:

```markdown
> **Recovery rules — read BEFORE spawning any agents:**
> - If hass-cli fails → run the Step 0 env check above. Do NOT retry with variations.
> - If trace-fetch.py can't be found → run the discovery block in step 3b. The `find` fallback takes <5 seconds. Do NOT spawn Bash or Explore agents.
> - If History/Logbook API fails → use `trace-fetch.py history` / `logbook` instead. These bypass hass-cli entirely.
> - Never spawn agents for discovery or connectivity debugging.
```

**Step 2: Verify the edit**

Read the file and confirm the callout appears between Step 0 and step 1.

**Step 3: Commit**

```bash
git add skills/ha-troubleshooting/SKILL.md
git commit -m "fix: add anti-agent-spawning guidance to troubleshooting skill

Explicit rules to prevent expensive agent spawns for simple discovery
and connectivity issues."
```

---

## Task 6: Version bump and changelog

**Why:** Users won't get updates without a version bump. Both `plugin.json` and `marketplace.json` must match.

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `CHANGELOG.md`

**Step 1: Read current versions**

```bash
grep '"version"' .claude-plugin/plugin.json .claude-plugin/marketplace.json
```

**Step 2: Bump to 1.2.1**

Update both files from current version to `1.2.1`.

**Step 3: Update CHANGELOG.md**

Add a `## 1.2.1` section with:
- `fix: add history and logbook commands to trace-fetch.py (bypasses MINGW-broken hass-cli raw get)`
- `fix: resilient helper discovery with find fallback (prevents 20-min agent spawns)`
- `fix: fail-fast env check in ha-troubleshooting (prevents retry loops)`
- `fix: anti-agent-spawning guidance in troubleshooting skill`

**Step 4: Commit**

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json CHANGELOG.md
git commit -m "chore: bump version to 1.2.1 with troubleshooting reliability fixes"
```

---

## Verification Checklist (post-implementation)

After all tasks complete, run the manual test from the analysis doc:

```bash
cd ~/dev/ha
claude --plugin-dir C:/Users/Ben/dev/home-assistant-assistant
# Ask: "Why does my downstairs bathroom motion light keep triggering?"
```

Verify:
- [ ] trace-fetch.py found on first try (no agent spawns)
- [ ] `trace-fetch.py history` returns data (no hass-cli raw get)
- [ ] `trace-fetch.py logbook` returns data (no hass-cli raw get)
- [ ] Evidence table has ✓ Ran for History and Logbook rows
- [ ] If hass-cli missing from PATH, model diagnoses immediately (no retries)
- [ ] Total time < 3 minutes
