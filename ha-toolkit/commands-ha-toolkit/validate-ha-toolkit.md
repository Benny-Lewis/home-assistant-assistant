---
name: ha:validate
description: Validate Home Assistant configuration for errors
allowed-tools: Read, Bash, Glob, Grep, AskUserQuestion
argument-hint: [file-or-directory]
---

# Validate Home Assistant Configuration

> **Evidence-First Approach:** Always show what checks ran vs. were skipped.
> Users need to know what was validated, not just what passed.

Check Home Assistant configuration files for errors and issues.

## Validation Tiers

Validation runs in tiers. Higher tiers require more infrastructure but catch more issues.

### Tier 1: YAML Syntax (always runs)
- Valid YAML structure
- Proper indentation
- No duplicate keys

### Tier 2: Schema Validation (always runs)
- HA-specific structure checks
- Required keys present
- Valid entity_id format
- Valid service format

### Tier 3: HA-Backed Validation (when connected)
- Full config check via HA API
- Integration-specific validation
- Template rendering verification

**Prefer HA-backed validation when available** - it catches issues that local checks miss.

## Routing to HA-Backed Validation

Check if hass-cli is configured:
```bash
[ -n "$HASS_TOKEN" ] && [ -n "$HASS_SERVER" ] && echo "Connected" || echo "Not connected"
```

**If connected**, prefer HA-backed validation:
```bash
hass-cli service call homeassistant.check_config
```

**If not connected**, run local validation only and note limitation:
"Note: Running local validation only. For complete validation, connect to HA with `/ha-connect`."

## Scope

If $ARGUMENTS provided:
- Validate specific file or directory
- Example: `/ha:validate automations.yaml`
- Example: `/ha:validate packages/`

If no arguments:
- Validate entire configuration directory
- Start with configuration.yaml
- Follow includes to validate referenced files

## Checks Performed

### YAML Syntax (Tier 1)
- Valid YAML structure
- Proper indentation (2 spaces)
- Correct quoting of strings
- Valid boolean values (true/false, not True/False)
- No duplicate keys

### Home Assistant Schema (Tier 2)
- Entity ID format: `domain.entity_name` (lowercase, underscores)
- Service format: `domain.service_name`
- Required keys present (alias for automations, etc.)
- Valid domains (light, switch, sensor, etc.)
- Deprecated options flagged

### HA-Backed (Tier 3)
- Full config check against running HA
- Integration availability
- Template rendering
- Entity existence verification

### Security Checks (all tiers)
- No hardcoded passwords/tokens
- secrets.yaml references used appropriately
- No sensitive data in tracked files

## Output Format (Evidence Table)

**Always include the "What Ran vs Skipped" table:**

```
## Configuration Validation Report

### Evidence Table: What Ran vs Skipped

| Check | Status | Notes |
|-------|--------|-------|
| YAML Syntax | ✅ Ran | 8 files parsed |
| Schema Validation | ✅ Ran | HA 2024+ schema |
| HA Config Check | ⏭️ Skipped | Not connected to HA |
| Entity Existence | ⏭️ Skipped | Requires HA connection |
| Template Rendering | ⏭️ Skipped | Requires HA connection |
| Security Scan | ✅ Ran | No secrets exposed |

### Results

✅ configuration.yaml - Valid
✅ automations.yaml - Valid (12 automations)
⚠️  packages/climate.yaml - 1 warning
   Line 23: Deprecated 'platform: template' - use 'template:' instead
❌ packages/lights.yaml - 1 error
   Line 45: Invalid entity_id 'light.Living Room' (spaces not allowed)

### Summary

| Metric | Count |
|--------|-------|
| Files checked | 8 |
| Errors | 1 |
| Warnings | 1 |
| Passed | 6 |

### Limitations

The following checks were skipped because HA is not connected:
- Entity existence verification
- Template rendering validation
- Integration-specific checks

Run `/ha-connect` to enable full validation.
```

## Error Explanations

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

## Integration with Deploy

After validation passes:
```
Configuration is valid! Run /ha-deploy to push changes to Home Assistant.
```

If HA-backed validation was skipped:
```
Local validation passed, but full validation requires HA connection.
You can deploy with /ha-deploy, but some issues may only appear after reload.
```
