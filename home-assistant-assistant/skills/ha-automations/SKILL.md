---
name: ha-automations
description: Use when user mentions Home Assistant automations, describes "when X happens do Y" patterns, asks about triggers/conditions/actions, or wants to automate smart home devices.
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash(hass-cli:*)
---

# Home Assistant Automations

> **Safety Invariants:** #1 (capability check), #2 (no timer substitution), #5 (no implicit deploy)
> See `references/safety-invariants.md` and `references/intent-classifier.md`

## Overview

Create Home Assistant automations from natural language descriptions. Core principle: resolve entities first, classify intent, validate before writing.

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

1. **Resolve entities** via ha-entity-resolver agent (Invariant #1)
2. **Classify intent** - Is this inactivity detection or pure delay? (Invariant #2)
   - "After no motion for X" → Inactivity → Use `for:` in trigger, NOT timers
   - "Wait X then do Y" → Pure delay → `delay:` or timer acceptable
   - See `references/intent-classifier.md` for classification rules
3. **Get capability snapshot** for devices being controlled
4. **Check conflicts** for existing automations on same entities
5. **Generate YAML** using `references/yaml-syntax.md` and `references/common-patterns.md`
6. **Preview** with inline comments explaining choices
7. **Save and offer deployment** (Invariant #5 - never auto-deploy):
   - Save to automations.yaml
   - Ask: "Saved. Ready to deploy to Home Assistant?"
   - If yes → invoke /ha:deploy (which has its own confirmation)
   - If no → "OK, you can deploy later with /ha:deploy"
   - **Never suggest manual file transfer (scp, rsync, manual copy). Always use /ha:deploy.**

## Inactivity vs Delay (Critical)

**This is the #1 source of broken automations.** See `references/intent-classifier.md`.

| User Says | Intent | Correct Pattern |
|-----------|--------|-----------------|
| "Turn off after 5 min of no motion" | Inactivity | `to: "off"` with `for: "00:05:00"` |
| "Wait 5 minutes then turn off" | Delay | `delay:` in actions |
| "5 min after motion stops" | Inactivity | `to: "off"` with `for:` |

**NEVER use timers for inactivity** unless you also add cancel-on-motion logic.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Guessing entity IDs | Always resolve via ha-entity-resolver |
| Timer for inactivity | Use `for:` in trigger instead |
| Missing conditions | Add time/state guards to prevent unwanted triggers |
| Invalid services | Verify service exists before using |
| Auto-deploying | Ask user first, never assume |

## References

- `references/yaml-syntax.md` - Full syntax documentation
- `references/common-patterns.md` - Copy-paste templates
