---
name: ha-scenes
description: Use when user wants device presets, mentions "scene", "mood", "setting", or describes setting multiple devices to specific states like "movie mode" or "goodnight".
---

# Home Assistant Scenes

## Overview

Create presets that set multiple entities to specific states simultaneously. Core principle: scenes capture a snapshot of desired device states, not sequences or logic.

## When to Use

**Symptoms:**
- User says "create a scene", "preset", "mood", "setting"
- Describes multiple devices in specific states ("lights dim, TV on, blinds closed")
- Mentions named states like "movie night", "goodnight", "morning", "away"
- Wants to capture current device states as a preset

**When NOT to use:**
- Needs triggers or conditions → use `ha-automations`
- Needs sequential actions with delays → use `ha-scripts`
- Debugging existing scenes → use `ha-troubleshooting`

## Quick Reference

| Component | Purpose |
|-----------|---------|
| name | Scene identifier |
| entities | Map of entity_id to desired state |

## Process

1. **Understand intent** - What state should each device be in?
2. **Resolve entities** via ha-entity-resolver agent
3. **Determine states** - brightness, color, position, etc.
4. **Generate YAML** using `references/yaml-syntax.md`
5. **Preview** with inline comments
6. **Write** to scenes.yaml
7. **Deploy** via /ha-deploy

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using scene for sequences | Scenes set states instantly; use scripts for timed sequences |
| Including non-stateful entities | Only include entities that have controllable states |
| Forgetting all relevant devices | Ask user to confirm all devices they want included |
| Wrong state values | Check entity for valid state options (brightness 0-255, etc.) |

## References

- `references/yaml-syntax.md` - Full syntax documentation
