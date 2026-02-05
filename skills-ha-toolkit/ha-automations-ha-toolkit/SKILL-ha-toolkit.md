---
name: ha-automations
description: Use when user mentions Home Assistant automations, describes "when X happens do Y" patterns, asks about triggers/conditions/actions, or wants to automate smart home devices.
---

# Home Assistant Automations

## Overview

Create Home Assistant automations from natural language descriptions. Core principle: resolve entities first, validate before writing.

## When to Use

**Symptoms:**
- User says "automate", "when X do Y", "trigger", "if X then Y"
- Mentions schedules, motion, presence, or device state changes
- Wants devices to respond to events automatically

**When NOT to use:**
- One-time sequences → use `ha-scripts`
- Setting device states directly → use `ha-scenes`
- Debugging existing automations → use `ha-troubleshooting`

## Quick Reference

| Component | Purpose |
|-----------|---------|
| alias | Human-readable name |
| trigger | What starts it (state, time, event) |
| condition | Additional requirements (optional) |
| action | What happens when triggered |

## Process

1. **Resolve entities** via ha-entity-resolver agent
2. **Check conflicts** for existing automations on same entities
3. **Generate YAML** using `references/yaml-syntax.md` and `references/common-patterns.md`
4. **Preview** with inline comments
5. **Write** to automations.yaml
6. **Deploy** via /ha-deploy

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Guessing entity IDs | Always resolve via ha-entity-resolver |
| Missing conditions | Add time/state guards to prevent unwanted triggers |
| Invalid services | Verify service exists before using |
| YAML syntax errors | Validate with hass-cli before writing |

## References

- `references/yaml-syntax.md` - Full syntax documentation
- `references/common-patterns.md` - Copy-paste templates
