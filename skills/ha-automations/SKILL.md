---
name: ha-automations
description: Use when user mentions Home Assistant automations, describes "when X happens do Y" patterns, asks about triggers/conditions/actions, or wants to automate smart home devices.
user-invocable: true
allowed-tools: Read, Grep, Glob, Edit, Bash(hass-cli:*), AskUserQuestion
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
| alias | Human-readable name **and entity ID source** |
| trigger | What starts it (state, time, event) |
| condition | Additional requirements (optional) |
| action | What happens when triggered |

## Automation Entity IDs

The YAML `id` field is for internal tracking only — it is **not** the entity ID. HA derives entity IDs from the `alias` field.

| Field | Purpose | Example |
|-------|---------|---------|
| `id` | Internal tracking (traces, UI) | `1234567890` |
| `alias` | Display name **→ entity ID source** | `"Morning Lights"` → `automation.morning_lights` |

**Derivation rule:** lowercase, spaces → underscores, special characters removed.

| Alias | Derived Entity ID |
|-------|-------------------|
| `"Turn On Kitchen Lights"` | `automation.turn_on_kitchen_lights` |
| `"Motion — Hallway (Night)"` | `automation.motion_hallway_night` |

**Correct lookup:**
```bash
hass-cli state get automation.turn_on_kitchen_lights  # derived from alias
```

**Incorrect lookup:**
```bash
hass-cli state get automation.1234567890  # WRONG — id ≠ entity ID
```

## Process

1. **Resolve entities** via ha-entity-resolver agent (Invariant #1)
2. **Classify intent** - Is this inactivity detection or pure delay? (Invariant #2)
   - "After no motion for X" → Inactivity → Use `for:` in trigger, NOT timers
   - "Wait X then do Y" → Pure delay → `delay:` or timer acceptable
   - See `references/intent-classifier.md` for classification rules
3. **Get capability snapshot** for devices being controlled
   - If user's request requires unsupported attributes, **STOP and use AskUserQuestion** to explain the mismatch and offer alternatives before proceeding.
4. **Check conflicts** for existing automations on same entities
5. **Generate YAML** using `references/yaml-syntax.md` and `references/common-patterns.md`
6. **Preview** with inline comments explaining choices
7. **Save and offer deployment** (Invariant #5 - never auto-deploy):
   - Save to automations.yaml
   - When editing existing files, include enough surrounding context in `old_string` to be unique (e.g., include the scene name or automation alias above the edit point). If appending, use the last few lines of the file as the anchor.
   - **MANDATORY: Call the AskUserQuestion tool** (do NOT just print text) with:
     - Question: "Saved to automations.yaml. What would you like to do next?"
     - Option 1: "Deploy now" → invoke ha-deploy skill
     - Option 2: "Keep editing" → ready for more changes
   - **Never suggest manual file transfer (scp, rsync, manual copy). Always use ha-deploy.**

## Inactivity vs Delay (Critical)

**This is the #1 source of broken automations.** See `references/intent-classifier.md`.

| User Says | Intent | Correct Pattern |
|-----------|--------|-----------------|
| "Turn off after 5 min of no motion" | Inactivity | `to: "off"` with `for: "00:05:00"` |
| "Wait 5 minutes then turn off" | Delay | `delay:` in actions |
| "5 min after motion stops" | Inactivity | `to: "off"` with `for:` |

**NEVER use timers for inactivity** unless you also add cancel-on-motion logic.

## Conditions in Action Sequences

HA supports placing `condition:` blocks mid-action-sequence as **gates**. Earlier actions still run; only subsequent actions are skipped if the condition fails.

```yaml
actions:
  - action: lock.lock                  # Always runs
    target:
      entity_id: lock.front_door
  - condition: state                   # Gate — checks before continuing
    entity_id: person.ben
    state: "not_home"
  - action: notify.mobile_app          # Only runs if person is away
    data:
      message: "Door locked — you're away"
```

**Key rules:**
- Actions **before** the condition always execute
- Actions **after** the condition only execute if it passes
- This is NOT the same as top-level `conditions:` (which gate the entire automation)

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Guessing entity IDs | Always resolve via ha-entity-resolver |
| Timer for inactivity | Use `for:` in trigger instead |
| Missing conditions | Add time/state guards to prevent unwanted triggers |
| Invalid services | Verify service exists before using |
| Auto-deploying | Ask user first, never assume |
| Looking up by `id` field | Entity ID derives from `alias`, not `id` |
| Condition gates entire sequence | Top-level `conditions:` gates all; mid-sequence gates only subsequent actions |

## References

- `references/yaml-syntax.md` - Full syntax documentation
- `references/common-patterns.md` - Copy-paste templates
