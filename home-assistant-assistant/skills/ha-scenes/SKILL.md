---
name: ha-scenes
description: Use when user wants device presets, mentions "scene", "mood", "setting", or describes setting multiple devices to specific states like "movie mode" or "goodnight".
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash(hass-cli:*)
---

# Home Assistant Scenes

> **Safety Invariants:** #1 (capability check), #5 (no implicit deploy)
> See `references/safety-invariants.md`

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
3. **Get capability snapshot** for each device (Invariant #1):
   - Lights: check `supported_color_modes` (brightness, color_temp, rgb_color)
   - Covers: check supported positions/tilt
   - Media players: check supported features
   - **Only include attributes the device actually supports!**
4. **Determine states** - Only use supported attributes from snapshot
5. **Generate YAML** using `references/yaml-syntax.md`
6. **Preview** with inline comments explaining capability checks
7. **Save and offer deployment** (Invariant #5 - never auto-deploy):
   - Save to scenes.yaml
   - Ask: "Saved. Ready to deploy to Home Assistant?"
   - If yes → invoke /ha:deploy (which has its own confirmation)
   - If no → "OK, you can deploy later with /ha:deploy"
   - **Never suggest manual file transfer (scp, rsync, manual copy). Always use /ha:deploy.**

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using scene for sequences | Scenes set states instantly; use scripts for timed sequences |
| Unsupported attributes | Get capability snapshot first - only use supported modes |
| Including non-stateful entities | Only include entities that have controllable states |
| Forgetting all relevant devices | Ask user to confirm all devices they want included |
| Wrong state values | Check entity for valid state options (brightness 0-255, etc.) |
| Auto-deploying without asking | Offer options, let user choose (Invariant #5) |

## References

- `references/yaml-syntax.md` - Full syntax documentation
