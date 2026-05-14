---
name: ha-naming
description: Use when user asks about "naming", "entity_id", "rename", "naming convention", "audit naming", "plan naming", mentions organizing entities, standardizing names, or needs help with Home Assistant naming best practices, audits, or rename planning.
user-invocable: true
allowed-tools: Read, Write, Bash, Glob, Grep, AskUserQuestion
---

# Home Assistant Naming Conventions

This skill provides guidance on consistent naming for Home Assistant entities, devices, and configurations.

## Why Naming Matters

Good naming enables:
- **Findability**: Quickly locate entities
- **Automation**: Easier to reference in automations
- **Grouping**: Natural grouping by area/function
- **Maintenance**: Understand purpose at a glance
- **Voice Control**: Natural spoken commands

## Entity ID Structure

Entity IDs follow the pattern: `domain.identifier`

```
light.living_room_ceiling
sensor.kitchen_temperature
binary_sensor.front_door_contact
```

### Entity ID Rules
- Lowercase only
- Underscores for spaces (no hyphens, spaces)
- No special characters
- Maximum 255 characters
- Must be unique within domain

## Recommended Pattern: Area First

`{domain}.{area}_{device_type}_{qualifier}`

```
light.living_room_ceiling_main
sensor.kitchen_temperature
switch.garage_outlet_1
```

**Benefits:**
- Entities group by area in lists
- Easy to find all devices in a room
- Natural for voice commands: "Turn on living room lights"

## Friendly Names

Friendly names (displayed in UI) can include:
- Proper capitalization
- Spaces
- Special characters

**Example:** `friendly_name: "Living Room Ceiling Light"`

## Best Practices

1. **Be consistent**: Choose a pattern and stick to it
2. **Be descriptive**: Names should explain what/where
3. **Use areas**: Prefix with location for natural grouping
4. **Avoid numbers when possible**: Use qualifiers (left, right, main)
5. **Plan for growth**: Leave room for additional devices
6. **Document conventions**: Record your naming rules

## Workflow Index

Deeper material lives in per-skill references:

- `references/naming-conventions.md` — complete tables for areas, devices, and domains
- `references/anti-patterns.md` — common mistakes and the migration strategy for fixing them
- `references/audit-workflow.md` — the read-only audit procedure: data prefetch, pattern detection, area coverage, report format, and CLI options (`--json`, `--brief`, `--domain`)
- `references/plan-workflow.md` — the planning procedure: convention selection, rename-mapping generation, dependency analysis, and the `.claude/naming-plan.yaml` schema
- `references/editor.md` — AST editing patterns used by `/ha-apply-naming`

User-facing workflows reached through this skill:
- **Audit:** scan config for naming inconsistencies (see `audit-workflow.md`)
- **Plan:** generate `.claude/naming-plan.yaml` based on audit + chosen convention (see `plan-workflow.md`)
- **Apply:** execute the plan via `/ha-apply-naming` (separate skill)
