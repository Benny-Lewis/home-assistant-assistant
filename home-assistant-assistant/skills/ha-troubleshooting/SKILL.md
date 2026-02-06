---
name: ha-troubleshooting
description: Use when user asks "why didn't X work", "not working", "debug", "check logs", mentions something "stopped working", or needs to diagnose Home Assistant issues.
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
| `hass-cli raw get /api/error_log` | Get error logs |
| `hass-cli raw get /api/trace/automation.name` | Get automation trace |
| `hass-cli raw get "/api/history/period?filter_entity_id=X"` | Entity history |

## Process

1. **Identify issue** - What automation/entity/feature isn't working?
2. **Resolve entities** - Use Resolver module to verify entity_ids exist
   - Check if entities mentioned in error actually exist
   - Look for typos, renamed entities, missing integrations
3. **Gather data** via ha-log-analyzer agent
   - Automation state (enabled/disabled)
   - Recent traces and error logs
   - Entity history around incident time
4. **Analyze** - Compare expected vs actual behavior
5. **Report with evidence** - Present findings with "what was checked" table
6. **Suggest fixes** - Describe what to change, but do NOT auto-apply
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
