---
name: ha-validate
description: Validate Home Assistant configuration files for errors. Use when user says "validate", "check config", "is this correct", or before deployment.
user-invocable: true
allowed-tools: Read, Bash, Glob, Grep, AskUserQuestion
argument-hint: [file-or-directory]
---

# Validate Home Assistant Configuration

> **Evidence-First Approach:** Always show what checks ran vs. were skipped.
> Users need to know what was validated, not just what passed.
>
> **Safety Invariants:**
> - **#1:** No unsupported attributes without verification (validation catches these)
> - **#6:** All validation outputs must include "what ran vs skipped" evidence tables
>
> See `references/safety-invariants.md` for full details.

Check Home Assistant configuration files for errors and issues. This skill provides both the user-facing validation workflow and the shared validation procedures used by agents (config-debugger, ha-config-validator).

## Purpose

Validation must be **truthful**. Never claim "validation passed" without evidence. This skill provides:
- Multiple validation tiers (local -> HA-backed)
- Clear reporting of what ran vs. what was skipped
- Graceful degradation when tools are unavailable

## Scope

If $ARGUMENTS provided:
- Validate specific file or directory
- Example: `/ha:validate automations.yaml`
- Example: `/ha:validate packages/`

If no arguments:
- Validate entire configuration directory
- Start with configuration.yaml
- Follow includes to validate referenced files

## Validation Tiers

Validation runs in tiers. Higher tiers require more infrastructure but catch more issues.

### Tier 1: YAML Syntax (Always Available)

Basic YAML parsing - catches structural errors.

```bash
# Preferred: HA-backed validation includes YAML check
hass-cli raw post /api/config/core/check_config

# Fallback if HA not connected: use yq if available
yq eval '.' automations.yaml > /dev/null 2>&1 && echo "Valid" || echo "Invalid"

# Last resort: Check for obvious syntax issues via grep
# (Tabs instead of spaces, unquoted special chars)
grep -n "	" automations.yaml  # Check for tabs
```

**Note:** Do NOT use `python -c "import yaml..."` - this creates an unnecessary Python dependency.

**What it catches:**
- Indentation errors
- Missing colons
- Invalid YAML syntax
- Unquoted special characters
- Duplicate keys

**What it misses:**
- HA schema violations
- Non-existent entity references
- Invalid service calls

### Tier 2: Schema Validation (When Available)

Validates against Home Assistant's expected structure.

```bash
# Check if HA config validator is available
hass-cli config check 2>/dev/null
```

HA-specific structure checks:
- Required keys present (alias for automations, etc.)
- Entity ID format: `domain.entity_name` (lowercase, underscores)
- Service format: `domain.service_name`
- Valid domains (light, switch, sensor, etc.)
- Valid boolean values (true/false, not True/False)
- Deprecated options flagged

**What it catches:**
- Missing required fields
- Invalid field types
- Unknown configuration keys

### Tier 3: Runtime Validation (HA-Backed)

Validates against the actual Home Assistant instance. **Prefer HA-backed validation when available** - it catches issues that local checks miss.

```bash
# Verify entity exists
hass-cli state get light.kitchen_main

# Verify service exists
hass-cli service list | grep "light.turn_on"

# Full config check (requires HA access)
hass-cli raw post /api/config/core/check_config
```

**What it catches:**
- Non-existent entities
- Unavailable services
- Device capability mismatches
- Integration-specific validation
- Template rendering verification

### Security Checks (All Tiers)

- No hardcoded passwords/tokens
- secrets.yaml references used appropriately
- No sensitive data in tracked files

## Routing to HA-Backed Validation

```bash
[ -n "$HASS_TOKEN" ] && [ -n "$HASS_SERVER" ] && echo "Connected" || echo "Not connected"
```

**If connected**, prefer HA-backed validation:
```bash
hass-cli service call homeassistant.check_config
```

**If not connected**, run local validation only and note limitation:
"Note: Running local validation only. For complete validation, connect to HA with `/ha:onboard`."

## Validation Procedure

### 1. Detect Available Tools

```bash
# Check what's available
YAML_CHECK="false"
HA_CHECK="false"

yq --version 2>/dev/null && YAML_CHECK="true"
hass-cli state list > /dev/null 2>&1 && HA_CHECK="true"
```

### 2. Run Available Validations

Run all available tiers in order:

```
1. YAML Syntax -> Always run
2. Schema Check -> Run if hass-cli available
3. Entity Resolution -> Run if hass-cli available
```

### 3. Report Results with Evidence Table

## Confidence Levels

Based on what validations actually ran:

| Checks Completed | Confidence |
|------------------|------------|
| YAML only | Low - syntax OK, semantics unknown |
| YAML + Schema | Medium - structure OK, runtime unknown |
| YAML + Schema + HA | High - fully validated |

## Output Format (Evidence Table)

**Always include the "What Ran vs Skipped" table:**

### If Valid

```
## Validation Result: PASSED

### Evidence Table: What Ran vs Skipped

| Tier | Check | Status | Evidence |
|------|-------|--------|----------|
| 1 | YAML Syntax | Passed | check_config returned valid |
| 2 | Entity existence | Passed | 5/5 entities verified |
| 3 | Service validation | Passed | 3/3 services exist |
| 4 | HA config check | Passed | API returned success |

### Entities Verified
- light.living_room_ceiling
- binary_sensor.front_door
- switch.garage_door
- climate.main_thermostat
- sensor.outdoor_temp

### Services Verified
- light.turn_on
- notify.mobile_app
- climate.set_temperature

**Confidence:** High
```

### If Errors Found

```
## Validation Result: FAILED

### Evidence Table: What Ran vs Skipped

| Tier | Check | Status | Evidence |
|------|-------|--------|----------|
| 1 | YAML Syntax | Passed | No syntax errors |
| 2 | Entity existence | Failed | 1 entity not found |
| 3 | Service validation | Skipped | Blocked by Tier 2 failure |
| 4 | HA config check | Skipped | Blocked by Tier 2 failure |

### Errors

1. **Entity not found:** `light.kitchen_overheadz`
   - Location: automations.yaml, line 47
   - Did you mean: `light.kitchen_overhead`?

### Next Steps
Fix the entity reference and re-run validation.
```

### Full Report Format

```
## Configuration Validation Report

### Evidence Table: What Ran vs Skipped

| Check | Status | Notes |
|-------|--------|-------|
| YAML Syntax | Ran | 8 files parsed |
| Schema Validation | Ran | HA 2024+ schema |
| HA Config Check | Skipped | Not connected to HA |
| Entity Existence | Skipped | Requires HA connection |
| Template Rendering | Skipped | Requires HA connection |
| Security Scan | Ran | No secrets exposed |

### Results

configuration.yaml - Valid
automations.yaml - Valid (12 automations)
packages/climate.yaml - 1 warning
   Line 23: Deprecated 'platform: template' - use 'template:' instead
packages/lights.yaml - 1 error
   Line 45: Invalid entity_id 'light.Living Room' (spaces not allowed)

### Summary

| Metric | Count |
|--------|-------|
| Files checked | 8 |
| Errors | 1 |
| Warnings | 1 |
| Passed | 6 |

**Confidence:** Medium (HA-backed validation unavailable)

### Limitations

The following checks were skipped because HA is not connected:
- Entity existence verification
- Template rendering validation
- Integration-specific checks

Run `/ha:onboard` to enable full validation.
```

## Error Reporting

When validation fails, provide actionable information:

```markdown
## Validation Failed

**File:** automations.yaml
**Line:** 42
**Error:** Unknown entity `light.kicthen_main`

### Suggested Fix
Did you mean `light.kitchen_main`? (Typo detected)

### Similar Entities
- light.kitchen_main
- light.kitchen_counter
- light.kitchen_island
```

For each error found, provide:
1. File and line number
2. What's wrong
3. How to fix it
4. Example of correct syntax

## Auto-Fix Suggestions

For common issues, offer to fix automatically:
- Indentation problems
- Quote issues
- Boolean formatting
- Entity ID casing

**Always ask user before making any changes.**

## Pre-Deploy Validation Checklist

Before any deploy operation, run:

1. **Syntax** - Is YAML valid?
2. **Schema** - Does structure match HA expectations?
3. **Entities** - Do all referenced entities exist?
4. **Services** - Are all called services available?
5. **Capabilities** - Do devices support the requested attributes?

## Output Contract

Validation output must always include:

```markdown
## Validation Summary

**Status:** PASSED | FAILED | INCOMPLETE
**Confidence:** High | Medium | Low

### Evidence Table

| Check | Ran | Result | Details |
|-------|-----|--------|---------|
| ... | ... | ... | ... |

### Issues (if any)

1. [Issue description with fix suggestion]

### Next Steps

- [If passed] Ready for deployment via `/ha:deploy`
- [If failed] Fix issues above, then re-validate
- [If incomplete] Consider connecting to HA for full validation
```

## Integration with Deploy

After validation passes:
```
Configuration is valid! Run /ha:deploy to push changes to Home Assistant.
```

If HA-backed validation was skipped:
```
Local validation passed, but full validation requires HA connection.
You can deploy with /ha:deploy, but some issues may only appear after reload.
```

## Integration Points

- **/ha:deploy skill**: Pre-deploy validation gate
- **ha-automations skill**: Post-generation validation
- **ha-config-validator agent**: Deep validation analysis (preloads this skill)
- **config-debugger agent**: Debugging validation (preloads this skill)
