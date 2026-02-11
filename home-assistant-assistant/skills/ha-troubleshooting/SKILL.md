---
name: ha-troubleshooting
description: Use when user asks "why didn't X work", "not working", "debug", "check logs", mentions something "stopped working", or needs to diagnose Home Assistant issues.
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash(hass-cli:*)
---

# Home Assistant Troubleshooting

> **This skill is READ-ONLY.** It diagnoses issues but does not fix them.
> To apply fixes, use the appropriate generator skill (ha-automations, ha-scripts, ha-scenes)
> with proper safety guards. See the ha-resolver skill for entity verification.

## Overview

Debug automations, analyze logs, and diagnose why things didn't work. Core principle: gather data first, then analyze—never guess without evidence.

## When to Use

**Symptoms:**
- User asks "why didn't my automation trigger?"
- Something "stopped working" or "isn't working"
- User wants to "debug", "check logs", "troubleshoot"
- Automation triggered but action didn't happen
- User says "it used to work"

**When NOT to use:**
- Creating new automations → use `ha-automations`
- Creating new scripts → use `ha-scripts`
- Creating new scenes → use `ha-scenes`

## Quick Reference

| Command | Purpose |
|---------|---------|
| `hass-cli state get automation.name` | Check if automation enabled |
| `MSYS_NO_PATHCONV=1 hass-cli raw get /api/error_log` | Get error logs (may 404) |
| `MSYS_NO_PATHCONV=1 hass-cli raw get /api/trace/automation.name` | Get automation trace |
| `MSYS_NO_PATHCONV=1 hass-cli raw get "/api/history/period?filter_entity_id=X"` | Entity history |

**Error log fallback:** If `/api/error_log` returns 404, try these alternatives in order:
1. `MSYS_NO_PATHCONV=1 hass-cli raw get /api/error/all` — alternative endpoint
2. Check for `home-assistant.log` in the config directory (if accessible)
3. Guide user to Settings > System > Logs in the HA web UI
4. Note in evidence table: "Error logs: unavailable via API — checked manually via UI"

## Process

1. **Identify issue** — What automation/entity/feature isn't working?
2. **Resolve entities** — Use Resolver module to verify entity_ids exist
   - Check if entities mentioned in error actually exist
   - Look for typos, renamed entities, missing integrations
3. **Gather data** — Attempt ALL four checks before moving to analysis

   > **Tip:** For complex multi-automation debugging, delegate to the ha-log-analyzer or config-debugger agent. Inline handling is fine for straightforward cases. Either way, the evidence table in step 5 is required.

   - **3a. Automation state**
     ```bash
     hass-cli state get automation.<name>
     ```
     Look for `state: on` (enabled) or `state: off` (disabled).

   - **3b. Automation traces**
     ```bash
     MSYS_NO_PATHCONV=1 hass-cli raw get /api/trace/automation.<name>
     ```
     Shows trigger, conditions, actions, and variables for recent runs.

   - **3c. Error logs**
     ```bash
     MSYS_NO_PATHCONV=1 hass-cli raw get /api/error_log
     ```
     If 404, follow the fallback chain in Quick Reference above.

   - **3d. Entity history**
     ```bash
     MSYS_NO_PATHCONV=1 hass-cli raw get "/api/history/period?filter_entity_id=<entity_id>"
     ```
     Check whether the trigger entity reached the expected state.

   **Rule:** Do NOT skip to analysis without attempting all four checks. If a check fails or returns empty, record it in the evidence table as `✗ Failed` with the reason.

4. **Analyze** — Compare expected vs actual behavior
5. **Report with evidence** — Present findings using this ran-vs-skipped table:

   | Check | Status | Result | Evidence |
   |-------|--------|--------|----------|
   | Automation state | ✓ Ran | on/off | `state: on` from hass-cli |
   | Automation traces | ✓ Ran | triggered/not found | Trace showed condition X failed |
   | Error logs | ✗ Failed | 404 | API returned 404, checked UI instead |
   | Entity history | ✓ Ran | state reached | History shows change at HH:MM |

   **Status values:** `✓ Ran` — check completed, `⊘ Skipped (reason)` — not applicable, `✗ Failed` — check errored (404, timeout, etc.)

   Every check from step 3 MUST appear in the table. Never silently omit a check.

6. **Suggest fixes** — Describe what to change, but do NOT auto-apply
   - Route to appropriate skill (ha-automations, ha-scripts, ha-scenes)
   - User must explicitly request changes

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Guessing without checking logs | Always check automation state and traces first |
| Assuming automation is enabled | Verify with `hass-cli state get` |
| Not checking entity history | Trigger entity may never have reached trigger state |
| Ignoring time/sun conditions | Check if conditions were met at the time |

## Common Issues

| Symptom | Likely Cause |
|---------|--------------|
| Automation never triggers | Wrong entity ID, automation disabled, trigger state never reached |
| Triggers but no action | Condition not met, service call error |
| Works sometimes | Time/sun condition, entity unavailable intermittently |
| Used to work | Recent config change, entity renamed, integration issue |

## References

- `references/log-patterns.md` - Common error patterns and fixes
