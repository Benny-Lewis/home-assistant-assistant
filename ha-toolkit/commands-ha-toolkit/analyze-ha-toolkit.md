---
name: ha:analyze
description: Analyze Home Assistant setup and provide suggestions for improvements
allowed-tools: Read, Bash, Glob, Grep, AskUserQuestion
argument-hint: [focus-area]
---

# Analyze Home Assistant Setup

Perform comprehensive analysis of the Home Assistant configuration and provide actionable suggestions for improvements, new automations, and optimizations.

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
hass-cli entity list --output json

# State history (for pattern detection)
hass-cli state history --entity light.* --since "7 days ago"

# Device list
hass-cli device list --output json

# Area list
hass-cli area list --output json
```

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
══════════════════════════════

Overview:
  Entities: 147
  Automations: 23
  Areas: 8
  Devices: 45

🎯 Top Recommendations

1. HIGH IMPACT: Add motion-triggered lights
   Devices: living_room_light, kitchen_light
   Motion sensors available: living_room_motion, kitchen_motion
   Potential: Reduce manual switching, energy savings
   [Generate with: /ha:generate automation motion lights]

2. MEDIUM IMPACT: Create light groups
   5 ungrouped lights in living room
   Benefit: Easier control, scene creation
   [Generate with: /ha:generate helper light group]

3. QUICK WIN: Add away mode
   Presence detection available but unused
   Suggestion: Turn off lights/adjust HVAC when away
   [Generate with: /ha:generate automation away mode]

📊 Detailed Analysis

Automations:
  ✓ Good coverage: Lighting (80%)
  ⚠ Gap: Climate control (20%)
  ✗ Missing: Security notifications

Energy:
  Monitored devices: 12/45
  Suggestion: Add monitoring to high-power devices

Security:
  Sensors: 8 doors/windows
  Gap: No notification automations

Performance:
  ✓ Config is efficient
  Note: 3 template sensors could be simplified

Next Steps:
  1. Run /ha:generate for suggested automations
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
