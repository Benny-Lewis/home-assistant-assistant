---
name: ha-scripts
description: Use when user wants reusable action sequences, mentions "script", "sequence of actions", or needs to chain multiple commands that can be triggered manually or from automations.
allowed-tools: Read, Grep, Glob, Bash(hass-cli:*)
---

# Home Assistant Scripts

> **Safety Invariants:** #1 (capability check), #5 (no implicit deploy)
> See `references/safety-invariants.md`

## Overview

Create reusable action sequences that can be triggered manually or from automations. Core principle: scripts are for repeatable sequences, not event-driven behavior.

## When to Use

**Symptoms:**
- User says "create a script", "sequence of actions", "chain commands"
- Wants something they can trigger manually (button, voice, dashboard)
- Needs to reuse the same action sequence in multiple automations
- Describes a multi-step process without a trigger event

**When NOT to use:**
- Event-driven behavior ("when X happens") → use `ha-automations`
- Setting multiple devices to specific states → use `ha-scenes`
- Debugging existing scripts → use `ha-troubleshooting`

## Quick Reference

| Component | Purpose |
|-----------|---------|
| alias | Human-readable name |
| sequence | List of actions to perform |
| mode | single, restart, queued, parallel |
| fields | Input parameters for the script |

## Process

1. **Understand intent** - What sequence of actions?
2. **Resolve entities** via ha-entity-resolver agent (Invariant #1)
3. **Get capability snapshot** - For each device, verify supported services/attributes
4. **Generate YAML** using `references/yaml-syntax.md`
5. **Preview** with inline comments explaining choices
6. **Offer options** (Invariant #5 - never auto-deploy):
   - Save to scripts.yaml (local only)
   - Save and deploy via /ha-deploy
   - Copy to clipboard for manual paste

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using script when automation needed | If there's a trigger event, use automation instead |
| Unsupported service attributes | Get capability snapshot first (Invariant #1) |
| Forgetting mode for long sequences | Add `mode: restart` or `queued` for interruptible scripts |
| Hardcoding values | Use `fields` for reusable parameters |
| Missing delays between actions | Add `delay` between sequential device commands |
| Auto-deploying without asking | Offer options, let user choose (Invariant #5) |

## References

- `references/yaml-syntax.md` - Full syntax documentation
