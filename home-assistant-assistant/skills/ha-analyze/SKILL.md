---
name: ha-analyze
description: Analyze Home Assistant setup and provide improvement suggestions. Use when user asks for "analysis", "suggestions", "improvements", "optimization", or "review my setup".
user-invocable: true
allowed-tools: Read, Bash, Glob, Grep, AskUserQuestion
---

# Analyze Home Assistant Setup

> **Data-Derived Analysis:** All metrics and suggestions must be backed by evidence.
> Do NOT invent statistics. Only report what was actually measured.

Perform comprehensive analysis of the Home Assistant configuration and provide actionable suggestions for improvements, new automations, and optimizations.

## Evidence Requirements

**Every metric reported must include:**
1. How it was measured (command or file read)
2. Actual count/value (not estimated)
3. Source (hass-cli output, file path, or "not available")

**Example:**
```
Entities: 147 (from: hass-cli entity list | wc -l)
Automations: 23 (from: grep -c "^- id:" automations.yaml)
```

**Do NOT report metrics you cannot verify.**

## Analysis Areas

If $ARGUMENTS provided, focus on specific area:
- `automations` - Automation efficiency and opportunities
- `energy` - Energy management and monitoring
- `security` - Security-related suggestions
- `presence` - Presence detection improvements
- `performance` - Configuration optimization

If no arguments, analyze all areas.

## Data Collection

### From hass-cli (if available):
```bash
# Entity inventory
hass-cli entity list

# State history (for pattern detection)
hass-cli state history --entity light.* --since "7 days ago"

# Device list
hass-cli device list

# Area list
hass-cli area list
```

> Output is tabular text, not JSON. See `references/hass-cli.md` for parsing patterns.

### From local config:
- Read automations.yaml for existing automations
- Read packages/ for organized configs
- Analyze dashboard configurations
- Check integration configurations

## Analysis Categories

### 1. Automation Opportunities

Identify devices that could benefit from automation:

**Lights without motion automation:**
- "Living room light has no motion sensor automation"
- Suggest: Connect to motion sensor if available

**Repeated patterns:**
- "You turn on kitchen lights every day at 7am"
- Suggest: Create time-based automation

**Related devices not linked:**
- "Motion sensor and light in same room not connected"
- Suggest: Create motion-triggered automation

### 2. Energy Analysis

**High-usage devices:**
- Identify devices with energy monitoring
- Flag always-on devices that could be scheduled

**Missing monitoring:**
- "These high-power devices lack energy monitoring"
- Suggest: Add smart plugs with metering

**Optimization opportunities:**
- "HVAC runs continuously, consider schedule"
- "Lights left on in unoccupied rooms"

### 3. Security Analysis

**Coverage gaps:**
- "Front door has sensor, back door does not"
- "No motion sensor in garage"

**Missing alerts:**
- "Door sensors not triggering notifications"
- Suggest: Add alert automations

**Away mode:**
- "No presence-based security mode"
- Suggest: Create away/home mode automations

### 4. Presence Detection

**Device tracker analysis:**
- What presence detection methods in use
- Accuracy assessment
- Redundancy suggestions

**Home/Away automations:**
- What happens when everyone leaves
- What happens on arrival
- Suggestions for improvements

### 5. Configuration Health

**Unused entities:**
- Entities not used in any automation/dashboard
- Suggest: Clean up or utilize

**Deprecated configurations:**
- Old-style configs that should be updated
- Suggest: Migration path

**Performance issues:**
- Complex templates that could be simplified
- Frequent polling that could be event-based

## Smart Suggestions Engine

Based on analysis, generate suggestions:

### Pattern-Based
```yaml
observation: "You have 5 lights in the living room"
suggestion: "Create a light group for easier control"
automation_template: |
  light:
    - platform: group
      name: Living Room Lights
      entities:
        - light.living_room_ceiling
        - light.living_room_lamp
        # ...
```

### Device Capability-Based
```yaml
observation: "Your thermostat supports scheduling"
current: "No schedule automations found"
suggestion: "Create temperature schedule"
benefit: "Save energy, improve comfort"
```

### Best Practice-Based
```yaml
observation: "Automations lack descriptions"
suggestion: "Add descriptions for documentation"
benefit: "Easier troubleshooting and maintenance"
```

## Output Format

```
Home Assistant Analysis Report

Overview:
  Entities: 147
  Automations: 23
  Areas: 8
  Devices: 45

Top Recommendations

1. HIGH IMPACT: Add motion-triggered lights
   Devices: living_room_light, kitchen_light
   Motion sensors available: living_room_motion, kitchen_motion
   Potential: Reduce manual switching, energy savings

2. MEDIUM IMPACT: Create light groups
   5 ungrouped lights in living room
   Benefit: Easier control, scene creation

3. QUICK WIN: Add away mode
   Presence detection available but unused
   Suggestion: Turn off lights/adjust HVAC when away

Detailed Analysis

Automations:
  Good coverage: Lighting (80%)
  Gap: Climate control (20%)
  Missing: Security notifications

Energy:
  Monitored devices: 12/45
  Suggestion: Add monitoring to high-power devices

Security:
  Sensors: 8 doors/windows
  Gap: No notification automations

Performance:
  Config is efficient
  Note: 3 template sensors could be simplified

Next Steps:
  1. Ask me to create any suggested automation
  2. Review and customize generated configs
  3. Run /ha:deploy to apply changes
```

## Interactive Mode

After presenting analysis:
1. Ask if user wants to implement any suggestion
2. Offer to generate the automation/config
3. Guide through testing
4. Iterate on improvements

## Scheduling

Suggest running analysis periodically:
```
Tip: Run /ha:analyze monthly to discover new optimization opportunities
as your setup evolves.
```
