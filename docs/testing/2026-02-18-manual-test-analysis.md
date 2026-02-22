# Manual Test Analysis: ha-troubleshooting v1.2.0

**Date:** 2026-02-18
**Test:** `claude --plugin-dir C:/Users/Ben/dev/home-assistant-assistant` from `~/dev/ha`
**Prompt:** "Why does my downstairs bathroom motion light keep triggering? It ran multiple times this morning."
**Transcript:** `2026-02-18-manual-test-transcript.txt` (same directory)

## Summary

The skill loaded and ultimately produced a correct, high-quality analysis — but the path to get there was extremely inefficient. Total time: ~26 minutes, of which ~23 minutes was wasted on discovery failures and retries. The root causes are: (1) fragile helper discovery via breadcrumb files, (2) no fail-fast guidance when hass-cli is unavailable, and (3) History/Logbook API calls using hass-cli instead of the proven Python websocket pattern.

## What Worked

- **trace-fetch.py**: Once found, worked perfectly. List and get commands both returned correct data. The trace data was the backbone of the final analysis.
- **Final analysis quality**: Correctly diagnosed PIR sensor re-trigger cycles, reconstructed a full timeline from traces, and offered 3 actionable options.
- **Evidence table**: Present and correctly formatted with all 6 rows including failed checks.
- **ha-troubleshooting skill loaded**: Correctly invoked via the troubleshooting intent.
- **hass-cli state get**: Worked for individual entity state checks (lines 76-82) once the session stabilized.

## What Went Wrong

### Failure 1: Shell environment broken at session start (lines 17-39)

The first ~1 minute reveals a fundamentally broken shell environment:

```
line 17: Bash(hass-cli state list | grep -i "bathroom\|bath" | ...) → Exit code 2
line 21: Bash(hass-cli state list automation | grep -i "bath")     → Sibling tool call errored
line 24: Bash(hass-cli state list | grep -i "bath" 2>&1 | head)    → Exit code 1
line 27: Bash(hass-cli state get sensor.test 2>&1 | head -5)       → Exit code 1
line 30: Bash(hass-cli 2>&1 | head -5; echo "---"; which hass-cli) → No output
line 35: Bash(dir "C:\Users\Ben\dev\ha" 2>&1 | head -40)           → Exit code 1
line 38: Bash(pwd && ls -la 2>&1 | head -30)                       → Exit code 1
```

**Key observation:** Even `pwd && ls` failed (line 38). This isn't just a missing env var — basic shell commands were broken. The `which hass-cli` returning **no output at all** (line 30) means hass-cli wasn't in PATH.

**Root cause analysis:** The SessionStart hook is async (`"async": true`). It runs in the background, so the model can start executing before the hook completes. The hook writes breadcrumb files and reports env var status — but the model's first Bash calls may execute in a shell where PATH hasn't been fully initialized, or where `--plugin-dir` changes the shell context.

**Impact:** 5 wasted tool calls + cascaded into the Explore agent spawn.

### Failure 2: Explore agent overkill (lines 41-42) — 2 min, 41 tool uses

After hass-cli failed, the model spawned an Explore agent ("Find bathroom automation files") which took 2 minutes with 41 tool uses. This searched the local filesystem for automation YAML files.

**Why this happened:** The SKILL.md says "Gather data" but doesn't tell the model what to do when hass-cli is unavailable. Without guidance, it fell back to general-purpose exploration.

**Better approach:** The skill should explicitly say: "If hass-cli fails, check `echo $HASS_SERVER && echo $HASS_TOKEN && which hass-cli` first. If env vars are missing, tell the user to run /ha-onboard. Don't spawn search agents."

### Failure 3: 20-minute agent to find trace-fetch.py (lines 50-68)

The worst issue. The breadcrumb-based discovery failed:

```
line 50: PLUGIN_ROOT="$(cat /c/Users/Ben/dev/ha/.claude/ha-plugin-root.txt 2>/dev/null)"
         → empty string (file doesn't exist)
line 57: Task(Bash agent: "Find trace-fetch.py and plugin root")
         → 25 tool uses, 20 minutes 36 seconds
```

**Root cause:** The SessionStart hook writes `.claude/ha-plugin-root.txt` into the **current working directory's** `.claude/` folder. Two things can go wrong:
1. The async hook hasn't finished writing by the time the model needs it
2. Under `--plugin-dir`, the hook fires from the plugin directory context, but the working directory is `~/dev/ha` — the breadcrumb may end up in the wrong location

After the agent finally found the path by brute-force searching, the model hardcoded it:
```
line 68: py "/c/Users/Ben/dev/home-assistant-assistant/helpers/trace-fetch.py" list ...
```
This worked immediately.

**Why the breadcrumb pattern is fundamentally fragile:**
- It depends on: (a) async hook completing before first use, (b) hook running in the right directory, (c) `.claude/` being writable, (d) the file not being cleaned up
- It's a multi-step chain where any link breaking causes a 20-minute recovery
- The `CLAUDE_PLUGIN_ROOT` variable is available in hooks but NOT in the model's Bash calls

**Better approach:** Use `$CLAUDE_PLUGIN_ROOT` — but this is only available in hooks, not in Bash tool calls. The real fix is to have the skill reference helpers using a **built-in variable or a deterministic path** rather than breadcrumb files.

### Failure 4: History API failures (lines 95-124) — 6 retries, all failed

After trace-fetch.py succeeded, the model attempted History API calls via hass-cli:

```
line 95:  hass-cli raw get "/api/history/period?filter_entity_id=..."  → Exit code 1
line 100: hass-cli raw get "/api/history/period?filter_entity_id=..."  → Exit code 127
line 106: hass-cli raw get "/api/logbook?entity=..." | python -c ...   → Sibling tool call errored
line 111: hass-cli raw get "/api/history/period?filter_entity_id=..."  → JSON parse error (char 3)
line 116: hass-cli raw get "/api/history/period?filter_entity_id=..."  → Exit code 1
line 121: hass-cli raw get "/api/history/..." > /tmp/motion_hist...     → Exit code 1
```

**Critical detail:** `hass-cli state get` WORKED on line 76, but `hass-cli raw get` FAILED on lines 95+. And exit code 127 (line 100) means the binary literally wasn't found — intermittent PATH loss.

The JSON parse error ("Expecting value: line 1 column 4 char 3") on line 111 suggests hass-cli returned a non-JSON error response (likely YAML-formatted error text or an HTML 404 page), and the piped python parser choked on it.

**But then line 127 worked:**
```
line 127: hass-cli raw get /api/states/binary_sensor.downstairs_bathroom_motion → Success (YAML output)
```

So `hass-cli raw get` for `/api/states/` works, but `/api/history/period` and `/api/logbook` don't. This points to a specific issue with those two endpoints — possibly URL quoting/encoding in MINGW, or the endpoints requiring different auth handling.

**Most likely cause:** MINGW path conversion. Despite `MSYS_NO_PATHCONV=1`, the `?` and `&` in query parameters may still be mangled. The `/api/states/` endpoint has no query params (just a path), which is why it succeeds.

### Failure 5: Logbook API 404 (line 141-143)

```
line 141: hass-cli raw get "/api/logbook?entity=binary_sensor.downstairs_bathroom_motion"
          → Exit code 1
```

Same root cause as History failures. The Logbook API endpoint also uses query parameters that likely get mangled by MINGW/hass-cli interaction.

## Failure Pattern Summary

| # | Failure | Root Cause | Time Wasted | Fix Category |
|---|---------|-----------|-------------|--------------|
| 1 | Shell broken at start | Async hook + PATH not ready | ~1m | Skill guidance |
| 2 | Explore agent for files | No fail-fast guidance in SKILL.md | ~2m | Skill guidance |
| 3 | 20min finding trace-fetch.py | Breadcrumb files missing/wrong dir | ~20m | Helper discovery |
| 4 | History API (6 retries) | MINGW query param mangling | ~2m | Move to Python helper |
| 5 | Logbook API 404 | Same as #4 | ~0.5m | Move to Python helper |

**Total waste: ~25.5 minutes out of ~26 minutes.**

## Additional Patterns Identified

### Pattern A: Retry without diagnosis

The model retried failed commands 5-6 times with small variations (adding `2>&1`, changing `head` limits, redirecting to files) without ever diagnosing *why* they failed. The SKILL.md should include a "if this fails, check these things" diagnostic step.

### Pattern B: Agent spawning as panic response

When direct commands failed, the model immediately spawned heavyweight agents (Explore: 41 tool uses, Bash: 25 tool uses) instead of trying lightweight diagnostics. A single `echo $HASS_SERVER && which hass-cli` would have diagnosed the env issue in seconds.

### Pattern C: `hass-cli raw get` is unreliable for endpoints with query params

The single-entity `/api/states/<entity>` endpoint (no query params) worked fine. The History and Logbook endpoints (with `?` and `&` query params) consistently failed. `MSYS_NO_PATHCONV=1` is necessary but may not be sufficient for all MINGW path mangling cases.

### Pattern D: The working commands all bypass hass-cli for complex operations

trace-fetch.py (Python websockets) worked perfectly. `hass-cli state get` (simple path, no query params) worked. Every failure involved `hass-cli raw get` with query strings. The pattern is clear: use Python helpers for anything requiring URL parameters.

## Concrete Fixes

### Fix 1: Replace breadcrumb discovery with `$CLAUDE_PLUGIN_ROOT` injection (HIGH)

**Problem:** Breadcrumb files (`.claude/ha-plugin-root.txt`) are fragile — depend on async hook timing and correct working directory.

**Solution:** The SessionStart hook already has access to `$CLAUDE_PLUGIN_ROOT`. Instead of writing a breadcrumb file and having the SKILL.md read it, inject the plugin root path directly into the skill instructions using the hook's `additionalContext` output.

**But wait** — SessionStart hooks output plain text (not `additionalContext` JSON). And the async hook's output arrives "next turn", not immediately. So the model still needs a fallback.

**Actual fix — two-tier approach:**
1. **Primary:** In SKILL.md and reference docs, replace the breadcrumb pattern with: `PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt 2>/dev/null || find /c/Users -maxdepth 6 -path '*/home-assistant-assistant/helpers/trace-fetch.py' -printf '%h/..\n' 2>/dev/null | head -1 || echo '.')"` — but this `find` is slow and platform-specific.
2. **Better primary:** Have the session hook write the breadcrumb SYNCHRONOUSLY before the model starts. But we can't — async is required on Windows to avoid freezing.
3. **Best approach:** Use the `$CLAUDE_PLUGIN_ROOT` env var that Claude Code sets for plugin hooks. The session hook already uses it (`bash "$CLAUDE_PLUGIN_ROOT/hooks/session-check.sh"`). If we can get this into the model's context... We can include it in the hook's text output, and the SKILL.md can say "look for 'Plugin root: <path>' in the session diagnostics output."

**Recommended fix:** Make the SKILL.md helper commands use an inline discovery chain that's fast and deterministic:
```bash
PY="$(cat .claude/ha-python.txt 2>/dev/null || command -v python3 || command -v python || command -v py)"
PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt 2>/dev/null)"
if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/helpers/trace-fetch.py" ]; then
  # Breadcrumb missing — use glob to find it (fast, <1s)
  PLUGIN_ROOT="$(dirname "$(ls -1d /c/Users/*/dev/home-assistant-assistant/helpers/trace-fetch.py 2>/dev/null | head -1)" 2>/dev/null)"
  PLUGIN_ROOT="${PLUGIN_ROOT%/helpers}"
fi
```

This is fast (<1 second), works without breadcrumbs, and doesn't require spawning an agent. But it's fragile to non-standard install locations. A more portable approach: search from the known plugin directory pattern.

**Final recommendation:** Use `$CLAUDE_PLUGIN_ROOT` in the hook to write the breadcrumb, but add a fast fallback **in the skill instructions** that doesn't spawn agents. The skill should say: "If PLUGIN_ROOT is empty after the breadcrumb read, run `find ~ -maxdepth 5 -name trace-fetch.py -path '*/home-assistant-assistant/*' 2>/dev/null | head -1` and extract the root from that."

### Fix 2: Add History + Logbook commands to trace-fetch.py (HIGH)

**Problem:** `hass-cli raw get` with query parameters fails under MINGW due to path/URL mangling. History and Logbook APIs need query params.

**Solution:** Add `history` and `logbook` subcommands to trace-fetch.py. It already has a working WebSocket connection pattern, but History and Logbook are REST APIs, not WebSocket. However, trace-fetch.py already imports `urllib.parse` and has HASS_SERVER/HASS_TOKEN available — it can make direct HTTP requests using `urllib.request` (stdlib, no extra deps).

**New commands:**
```bash
$PY "$PLUGIN_ROOT/helpers/trace-fetch.py" history <entity_id> [--hours 24]
$PY "$PLUGIN_ROOT/helpers/trace-fetch.py" logbook <entity_id> [--hours 24]
```

This bypasses hass-cli entirely for these problematic endpoints.

### Fix 3: Add fail-fast env check guidance to SKILL.md (HIGH)

**Problem:** When hass-cli fails, the model retries 5+ times and spawns agents instead of diagnosing the root cause.

**Solution:** Add an explicit "Environment Check" step at the top of the Process section:

```markdown
**Step 0: Verify environment** (do this FIRST, before any data gathering)
```bash
echo "HASS_SERVER=$HASS_SERVER"; echo "HASS_TOKEN is $([ -n "$HASS_TOKEN" ] && echo 'set' || echo 'NOT SET')"; which hass-cli
```
If HASS_SERVER or HASS_TOKEN is missing, tell the user to run /ha-onboard. Do NOT retry hass-cli commands or spawn agents.
```

### Fix 4: Add anti-agent-spawning guidance to SKILL.md (MEDIUM)

**Problem:** Model spawns expensive agents (41 + 25 tool uses) for discovery tasks that should take one command.

**Solution:** Add explicit guidance:
```markdown
> **Do NOT spawn Explore or Bash agents** for helper discovery or hass-cli debugging.
> If a command fails, run the diagnostic check above. If env vars are set and hass-cli
> is in PATH, the issue is likely MINGW path mangling — use the Python helper instead.
```

### Fix 5: Update all breadcrumb references across skills and agents (MEDIUM)

**Problem:** 6 files reference the breadcrumb pattern. If we improve discovery in one place, the others still have the fragile pattern.

**Affected files:**
- `skills/ha-troubleshooting/SKILL.md` (lines 66-68)
- `skills/ha-troubleshooting/references/diagnostic-api.md` (lines 155-157)
- `skills/ha-troubleshooting/references/log-patterns.md` (lines 91-92, 135-137)
- `agents/ha-log-analyzer.md` (lines 43-45)
- `agents/ha-entity-resolver.md` (lines 45-46)
- `skills/ha-resolver/SKILL.md` (need to check)

**Solution:** Update all to use the same resilient discovery pattern with fast fallback.

### Fix 6: Update SKILL.md to use Python helper for History/Logbook (LOW)

**Problem:** The Quick Reference and diagnostic steps still direct to `hass-cli raw get` for History and Logbook.

**Solution:** Once Fix 2 adds these commands to trace-fetch.py, update all references to use the Python helper as primary and hass-cli as fallback.

## Priority Order

1. **Fix 2** — Add history/logbook to trace-fetch.py (eliminates the most common failure mode)
2. **Fix 3** — Fail-fast env check in SKILL.md (prevents 5+ retry waste)
3. **Fix 1** — Resilient helper discovery (prevents 20-minute agent spawns)
4. **Fix 4** — Anti-agent-spawning guidance (defense in depth)
5. **Fix 5** — Update all breadcrumb references (consistency)
6. **Fix 6** — Update SKILL.md to prefer Python helper (completes the fix)

## Reproduction Steps

```bash
cd ~/dev/ha
claude --plugin-dir C:/Users/Ben/dev/home-assistant-assistant
# Then ask: "Why does my downstairs bathroom motion light keep triggering?"
```

Verify after fixes:
- [ ] trace-fetch.py `history` and `logbook` commands work
- [ ] Helper found on first try without breadcrumb files
- [ ] If hass-cli fails, model checks env vars immediately (no retries, no agents)
- [ ] History/Logbook evidence table rows show ✓ Ran
- [ ] Total troubleshooting time < 3 minutes
