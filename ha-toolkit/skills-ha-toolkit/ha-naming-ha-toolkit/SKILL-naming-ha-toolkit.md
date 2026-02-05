---
name: ha-naming
description: This skill should be used when the user asks about "naming", "entity_id", "rename", "naming convention", "entity naming", "device naming", "consistent names", mentions organizing entities, standardizing names, or needs help with Home Assistant naming best practices.
version: 0.1.0
allowed-tools: Read, Grep, Glob
---

# Home Assistant Naming Conventions

This skill provides guidance on consistent naming for Home Assistant entities, devices, and configurations.

**Detailed reference tables:** `references-ha-toolkit/naming-conventions.md`

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

## Anti-Patterns to Avoid

| Bad | Good | Why |
|-----|------|-----|
| `light.light_1` | `light.living_room_ceiling` | Generic names are meaningless |
| `light.lr_cl_1` | `light.living_room_ceiling_1` | Abbreviations without context |
| `light.living_room_main_ceiling_light_above_couch` | `light.living_room_ceiling_main` | Overly long |
| Mixed patterns across entities | Consistent pattern everywhere | Inconsistency creates confusion |

## Migration Strategy

When renaming existing entities:

1. **Audit current naming**: Use `/ha:audit-naming`
2. **Choose convention**: Pick pattern that fits majority
3. **Plan changes**: Document before executing
4. **Update dependencies**: Find all references in automations/scripts
5. **Execute carefully**: Use `/ha:apply-naming`
6. **Test thoroughly**: Verify automations work

## Best Practices

1. **Be consistent**: Choose a pattern and stick to it
2. **Be descriptive**: Names should explain what/where
3. **Use areas**: Prefix with location for natural grouping
4. **Avoid numbers when possible**: Use qualifiers (left, right, main)
5. **Plan for growth**: Leave room for additional devices
6. **Document conventions**: Record your naming rules

## References

- `references-ha-toolkit/naming-conventions.md` - Complete tables for areas, devices, domains
- `ha-conventions` skill - Detect naming patterns from your existing config
