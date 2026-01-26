---
name: ha-automations
description: Create Home Assistant automations following your naming conventions. Use when user mentions automations, describes "when X happens do Y" patterns, asks about triggers/conditions/actions, or wants to automate smart home devices.
allowed-tools: Read, Bash(hass-cli:*), Edit, Write
---

# Home Assistant Automations

## Your Project's Conventions

!`cat .claude/home-assistant-assistant.md 2>/dev/null | head -60 || echo "No conventions configured - using defaults"`

## Default Conventions (if none above)

- ID: `<area>_<trigger>_[if_<condition>]_<action>`
- Alias: `"<Area>: <Trigger> [If <Condition>] → <Action>"`
- Timer naming: `<area>_<purpose>`
- Use timer helpers for delays > 30 seconds

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

0. **Verify conventions loaded** (CRITICAL - be atomic)
   - Check if conventions section appears in "Your Project's Conventions" above
   - [CRITICAL] If "No conventions configured" shown, STOP and ask:
     "I don't know your naming conventions yet. Please run `/ha-conventions` first,
     or tell me to use default HA community standards."
   - If confidence is `low` or `none`, add uncertainty banner to output

1. **Resolve entities** via ha-entity-resolver agent
2. **Check conflicts** for existing automations on same entities
3. **Generate YAML** using `references/yaml-syntax.md` and `references/common-patterns.md`
4. **Validate** against naming conventions and timer preferences (see Validation Checklist)
5. **Preview** with inline comments
6. **Write** to automations.yaml (and timer.yaml if needed)
7. **Deploy** via /ha-deploy

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Guessing entity IDs | Always resolve via ha-entity-resolver |
| Missing conditions | Add time/state guards to prevent unwanted triggers |
| Invalid services | Verify service exists before using |
| YAML syntax errors | Validate with hass-cli before writing |
| Using inline delay for long waits | Use timer helpers for delays > 30 seconds |
| Ignoring naming conventions | Always follow patterns from conventions |

## Naming Requirements

Generated automations MUST follow user's conventions from `.claude/home-assistant-assistant.md`.

**If conventions configured:**
- Use the exact patterns from `conventions.automation_id_pattern` and `conventions.automation_alias_pattern`
- Follow the separator, case, and area_position rules

**If no conventions (fallback defaults):**
- ID: `<area>_<trigger>_[if_<condition>]_<action>`
- Alias: `"<Area>: <Trigger> [If <Condition>] → <Action>"`

**Examples matching common patterns:**

| Area | Trigger | Condition | Action | ID | Alias |
|------|---------|-----------|--------|----|----|
| backyard | door_open | dark | floodlight_on | `backyard_door_open_if_dark_floodlight_on` | `"Backyard: Door Open If Dark → Floodlight On"` |
| kitchen | motion | - | light_on | `kitchen_motion_light_on` | `"Kitchen: Motion → Light On"` |
| garage | sunset | - | lock | `garage_sunset_lock` | `"Garage: Sunset → Lock"` |

## Timer vs Delay Decision

**Check user conventions first:** If `conventions.use_timer_helpers` is set, follow it.

**Default behavior (or if not set):**
- Duration > `conventions.timer_threshold_seconds` (default 30s) → Use timer helper
- Duration ≤ threshold → Inline `delay:` is acceptable

**Timer helper pattern:**
1. Create timer in `timer.yaml` with `restore: true`
2. Create automation to start timer (with `mode: restart` for retriggering)
3. Create automation triggered by `timer.finished` event

**Always explain the choice to user** when proposing an automation with delays.

**Why timer helpers?**
- `restore: true` survives HA restarts
- Visible countdown on dashboard
- Can be canceled/extended programmatically
- More robust than inline `delay:` which is lost on restart

## Validation Checklist

After generating automation YAML, validate before presenting to user:

1. **Naming compliance**
   - Does ID match `automation_id_pattern`?
   - Does alias match `automation_alias_pattern`?
   - If `enforce_conventions: true` and non-compliant, regenerate

2. **Timer/delay compliance**
   - If delay > threshold, is timer helper used?
   - If timer used, is `restore: true` set?

3. **Syntax validation**
   - Use modern `triggers:` syntax (not `trigger:`)
   - Use modern `actions:` syntax (not `action:`)
   - Verify all entity IDs exist (via ha-entity-resolver)

4. **If validation fails:**
   - Review error messages
   - Fix the YAML
   - Run validation again
   - Only proceed when all checks pass

## Automation Creation Progress

Copy this checklist and track progress:

```
- [ ] Step 0: Load and verify conventions from settings
- [ ] Step 1: Resolve entity IDs via ha-entity-resolver
- [ ] Step 2: Determine timer vs delay based on duration
- [ ] Step 3: Generate automation YAML following conventions
- [ ] Step 4: Validate against naming patterns
- [ ] Step 5: If timer needed, generate timer.yaml entry
- [ ] Step 6: Present to user for review
- [ ] Step 7: Write to automations.yaml
- [ ] Step 8: Deploy via /ha-deploy
```

## References

- `references/yaml-syntax.md` - Full syntax documentation
- `references/common-patterns.md` - Copy-paste templates
