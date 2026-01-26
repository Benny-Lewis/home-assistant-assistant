---
name: ha-conventions
description: >
  Detect and configure naming conventions for your Home Assistant setup.
  Use when setting up the plugin for the first time or when your naming
  patterns change. Analyzes existing automations to learn your patterns.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob
---

# Home Assistant Convention Discovery

Detect naming patterns from your existing Home Assistant configuration and save them for consistent automation generation.

## When to Use

- First time setting up the Home Assistant plugin
- After creating many automations manually and wanting to codify patterns
- When you want to change your naming conventions
- To review what conventions are currently configured

## Process

### 1. Check Existing Conventions

First, check if conventions are already configured:

```bash
cat .claude/home-assistant-assistant.md 2>/dev/null | grep -A 30 "conventions:"
```

**If conventions exist**, ask the user:
> "You already have conventions configured. Would you like to:
> 1. View current conventions
> 2. Re-detect from your current config (will show diff before saving)
> 3. Cancel"

### 2. Locate HA Config

Check for the HA config path in settings. If not set, ask:
> "Where is your Home Assistant config directory?
> - Local path (e.g., `/home/homeassistant/.homeassistant/`)
> - SSH remote (e.g., `root@homeassistant.local:/config/`)"

Save the path to settings for future use.

### 3. Run Detection

Launch the `ha-convention-analyzer` agent to analyze:
- `automations.yaml` - ID and alias patterns
- `timer.yaml` - timer naming patterns (if exists)
- Inline delay vs timer helper usage

The analyzer runs in a forked context to avoid polluting the main conversation with raw config data.

### 4. Present Findings

Show the user what was detected:

```
## Detected Conventions

### Automation IDs
Pattern: <area>_<trigger>_<action>
Examples: kitchen_motion_light_on, backyard_door_open_alert
Confidence: high (12/15 match)

### Automation Aliases
Pattern: "<Area>: <Trigger> → <Action>"
Examples: "Kitchen: Motion → Light On"
Confidence: high (14/15 match)

### Timer Usage
Preference: Timer helpers for delays > 30s
Evidence: 4 automations use timer.start, 2 use inline delay
Confidence: medium

### No Pattern Detected
- Automation modes (mixed single/restart/queued usage)
```

### 5. Handle No Pattern Case

If no consistent pattern is detected (or no automations exist):

> "No consistent naming pattern detected in your config. Would you like to adopt Home Assistant community conventions?
>
> **Recommended defaults:**
> - ID: `<area>_<trigger>_[if_<condition>]_<action>`
> - Alias: `"<Area>: <Trigger> → <Action>"`
> - Timer naming: `<area>_<purpose>`
> - Use timer helpers for delays > 30 seconds
>
> [Accept defaults] [Customize] [Skip for now]"

### 6. User Confirmation

For each detected convention, ask user to confirm:

> "I detected this pattern for automation IDs: `<area>_<trigger>_<action>`
>
> Is this correct? [Yes] [Modify] [Use default instead]"

Allow the user to:
- Accept as detected
- Modify the pattern
- Use the HA community default instead
- Skip this field (will use default)

### 7. Save Conventions

Write the confirmed conventions to `.claude/home-assistant-assistant.md`:

```yaml
conventions:
  separator: "_"
  case: "snake_case"
  area_position: "prefix"
  condition_prefix: "if_"
  automation_id_pattern: "<area>_<trigger>_[if_<condition>]_<action>"
  automation_alias_pattern: "<Area>: <Trigger> [If <Condition>] → <Action>"
  timer_naming: "<area>_<purpose>"
  use_timer_helpers: true
  timer_threshold_seconds: 30
  default_automation_mode: "single"
  enforce_conventions: false
  detected_from_existing: true
  last_detected: "2026-01-25"
  confidence: "high"
  examples:
    - id: "kitchen_motion_light_on"
      alias: "Kitchen: Motion → Light On"
    - id: "backyard_door_open_if_dark_floodlight_on"
      alias: "Backyard: Door Open If Dark → Floodlight On"
```

### 8. Confirmation

After saving, confirm:

> "✅ Conventions saved! Your automations will now follow these patterns:
> - IDs: `kitchen_motion_light_on`
> - Aliases: `"Kitchen: Motion → Light On"`
> - Timer helpers for delays > 30 seconds
>
> Run `/ha-conventions` again anytime to update."

## Re-Detection Flow

When re-detecting with existing conventions:

1. Run detection as normal
2. Compare new findings to existing conventions
3. Show a diff:
   ```
   Convention changes detected:

   automation_id_pattern:
   - OLD: <area>_<action>
   + NEW: <area>_<trigger>_<action>

   Keep existing or update to new?
   ```
4. Require explicit confirmation before overwriting

## Settings File Format

Conventions are stored in `.claude/home-assistant-assistant.md` in the YAML frontmatter section. If the file doesn't exist, create it from the template.

## Error Handling

| Error | Response |
|-------|----------|
| Config path not set | Prompt user to provide path |
| Cannot access config files | Offer manual convention entry or use defaults |
| No automations.yaml | Offer defaults, explain this is normal for new installs |
| YAML parse error | Report error location, offer to skip that file |

## Output

After successful configuration:
- Conventions saved to settings file
- Summary of what was configured
- Instructions for how conventions will be used
