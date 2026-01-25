---
name: ha-troubleshooting
description: Use when user asks "why didn't X work", "not working", "debug", "check logs", mentions something "stopped working", or needs to diagnose Home Assistant issues.
---

# Home Assistant Troubleshooting

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
2. **Gather data** via ha-log-analyzer agent
3. **Analyze** - Compare expected vs actual behavior
4. **Report** - Present timeline and findings
5. **Offer fixes** - If issue identified, offer to fix it

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
