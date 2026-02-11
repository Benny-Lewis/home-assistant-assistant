---
name: ha-config-validator
description: Validates Home Assistant configuration files. Use before deploying changes.
tools:
  - Bash
  - Read
  - Grep
skills: [ha-validate]
---

# Config Validator Agent

**Warning:** Do NOT spawn this agent with `run_in_background: true`. Background agents silently lose all output ([Claude Code #17011](https://github.com/anthropics/claude-code/issues/17011)). Always use foreground execution.

Validate Home Assistant YAML configuration before deployment.

> **Safety Invariant #6:** Always show "what ran vs skipped" evidence tables.
> Every validation output must document exactly what was checked.

## Task

Check configuration files for errors before they're deployed.

## Validation Tiers

Validation progresses through tiers, stopping if any tier fails:

### Tier 1: YAML Syntax (no dependencies)

Use hass-cli's built-in YAML parsing or read-and-parse:
```bash
# Preferred: HA-backed validation includes YAML check
MSYS_NO_PATHCONV=1 hass-cli raw post /api/config/core/check_config

# Fallback if HA not connected: use yq if available
yq eval '.' automations.yaml > /dev/null 2>&1 && echo "Valid" || echo "Invalid"

# Last resort: Check for obvious syntax issues via grep
# (Tabs instead of spaces, unquoted special chars)
grep -n "	" automations.yaml  # Check for tabs
```

**Note:** Do NOT use `python -c "import yaml..."` - this creates an unnecessary Python dependency.

### Tier 2: Entity Existence Check
Extract entity IDs from config and verify each exists:
```bash
hass-cli state get <entity_id>
```

### Tier 3: Service Validation
Verify service calls are valid:
```bash
hass-cli service list | grep "<domain>.<service>"
```

### Tier 4: HA-Backed Validation (most authoritative)
Use Home Assistant's built-in validation:
```bash
MSYS_NO_PATHCONV=1 hass-cli raw post /api/config/core/check_config
```

## Output Format (with Evidence Table)

### If Valid
```
## Validation Result: PASSED ✅

### Evidence Table: What Ran vs Skipped

| Tier | Check | Status | Evidence |
|------|-------|--------|----------|
| 1 | YAML Syntax | ✅ Passed | check_config returned valid |
| 2 | Entity existence | ✅ Passed | 5/5 entities verified |
| 3 | Service validation | ✅ Passed | 3/3 services exist |
| 4 | HA config check | ✅ Passed | API returned success |

### Entities Verified
- light.living_room_ceiling ✅
- binary_sensor.front_door ✅
- switch.garage_door ✅
- climate.main_thermostat ✅
- sensor.outdoor_temp ✅

### Services Verified
- light.turn_on ✅
- notify.mobile_app ✅
- climate.set_temperature ✅
```

### If Errors Found
```
## Validation Result: FAILED ❌

### Evidence Table: What Ran vs Skipped

| Tier | Check | Status | Evidence |
|------|-------|--------|----------|
| 1 | YAML Syntax | ✅ Passed | No syntax errors |
| 2 | Entity existence | ❌ Failed | 1 entity not found |
| 3 | Service validation | ⏭️ Skipped | Blocked by Tier 2 failure |
| 4 | HA config check | ⏭️ Skipped | Blocked by Tier 2 failure |

### Errors

1. **Entity not found:** `light.kitchen_overheadz`
   - Location: automations.yaml, line 47
   - Did you mean: `light.kitchen_overhead`?

### Next Steps
Fix the entity reference and re-run validation.
```

## Suggestions

When errors are found, provide:
- Exact line numbers
- Suggested corrections (typos)
- Similar valid values
- Clear indication of what was checked vs skipped
