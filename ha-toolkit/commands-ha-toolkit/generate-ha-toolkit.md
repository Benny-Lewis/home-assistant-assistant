---
name: ha:generate
description: Generate Home Assistant YAML configurations from descriptions
allowed-tools: Read, Bash, AskUserQuestion, Glob, Grep
argument-hint: [type] [description]
---

# Generate Home Assistant Configuration

> **This command is a thin router.** It identifies the generation type and
> delegates to the appropriate skill. Do not duplicate YAML patterns here.

Generate YAML configuration for Home Assistant based on natural language descriptions.

## Supported Types and Routing

| Type | Routes To | Example |
|------|-----------|---------|
| automation | `ha-automations` skill | `/ha:generate automation motion lights` |
| script | `ha-scripts` skill | `/ha:generate script bedtime routine` |
| scene | `ha-scenes` skill | `/ha:generate scene movie night` |
| template | `ha-jinja` skill | `/ha:generate template average temp` |
| dashboard | `ha-lovelace` skill | `/ha:generate dashboard climate card` |
| helper | `ha-automations` skill | `/ha:generate helper motion timeout` |

## Process

### 1. Parse Request

Identify the type ($1) and description ($2 onwards or $ARGUMENTS).

If type is missing or unclear, ask:
"What would you like to generate?
- automation (when X happens, do Y)
- script (sequence of actions to run on demand)
- scene (set devices to specific states)
- template (computed sensor values)
- dashboard (UI cards and views)
- helper (input_boolean, input_number, timer)"

### 2. Route to Skill

Based on type, invoke the appropriate skill:

**automation** → Route to `ha-automations` skill
- Skill handles: entity resolution, inactivity classification, capability checks
- Uses `references/yaml-syntax.md` for current HA 2024+ schema

**script** → Route to `ha-scripts` skill
- Skill handles: sequence building, mode selection

**scene** → Route to `ha-scenes` skill
- Skill handles: capability snapshot, valid state options

**template** → Route to `ha-jinja` skill
- Skill handles: Jinja2 patterns, template sensor structure

**dashboard** → Route to `ha-lovelace` skill
- Skill handles: card types, templating limitations

### 3. Schema Enforcement

**All generated YAML must use HA 2024+ schema.**

Ban these deprecated patterns:
```yaml
# ❌ WRONG - Old schema (ban these)
automation:
  - alias: "Name"
    trigger:
      platform: state

# ✅ CORRECT - Current schema
- id: automation_id
  alias: "Name"
  triggers:
    - trigger: state
```

Key schema rules:
- File should be a list `[ - id: ... ]`, NOT have `automation:` root key
- Use `triggers:` (plural), `conditions:` (plural), `actions:` (plural)
- Use `trigger:` inside each trigger item, NOT `platform:`
- Use `action:` for service calls, NOT `service:`

See `references/yaml-syntax.md` for complete schema reference.

## No Direct YAML Generation

**This command MUST NOT contain YAML templates or examples.**

All YAML patterns live in:
- `references/yaml-syntax.md` - Consolidated syntax reference
- Individual skill files - Domain-specific patterns

If you need to update YAML patterns, update the reference file, not this command.

## After Generation

Skills handle the full workflow including:
1. Entity resolution
2. Capability verification
3. YAML generation
4. Preview with explanations
5. Offer to save (with Invariant #5 - ask before writing)
