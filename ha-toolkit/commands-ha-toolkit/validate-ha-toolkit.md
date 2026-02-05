---
name: ha:validate
description: Validate Home Assistant configuration for errors
allowed-tools: Read, Bash, Glob, Grep, AskUserQuestion
argument-hint: [file-or-directory]
---

# Validate Home Assistant Configuration

Check Home Assistant configuration files for errors and issues.

## Validation Methods

### Method 1: Local YAML Validation

Check YAML syntax and structure locally:

1. Find all YAML files in config directory
2. Parse each file for YAML syntax errors
3. Check for common HA-specific issues:
   - Invalid entity_id format
   - Missing required keys
   - Deprecated configuration
   - Duplicate keys

### Method 2: HA Config Check (if hass-cli available)

Use Home Assistant's built-in validation:
```bash
hass-cli service call homeassistant.check_config
```

This validates against the actual HA installation.

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

### YAML Syntax
- Valid YAML structure
- Proper indentation (2 spaces)
- Correct quoting of strings
- Valid boolean values (true/false, not True/False)

### Home Assistant Specific
- Entity ID format: `domain.entity_name` (lowercase, underscores)
- Service format: `domain.service_name`
- Required keys present (alias for automations, etc.)
- Valid domains (light, switch, sensor, etc.)
- Template syntax (Jinja2 validation)

### Security Checks
- No hardcoded passwords/tokens
- secrets.yaml references used appropriately
- No sensitive data in tracked files

### Best Practice Checks
- Automations have descriptions
- Entity IDs follow naming convention
- No duplicate entity IDs
- Deprecated options flagged

## Output Format

```
Configuration Validation Report
═══════════════════════════════

✅ configuration.yaml - Valid
✅ automations.yaml - Valid (12 automations)
⚠️  packages/climate.yaml - 1 warning
   Line 23: Deprecated 'platform: template' - use 'template:' instead
❌ packages/lights.yaml - 1 error
   Line 45: Invalid entity_id 'light.Living Room' (spaces not allowed)

Summary:
────────
Files checked: 8
Errors: 1
Warnings: 1
Passed: 6

To fix errors, review the files above or run:
  /ha:generate to recreate configurations
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

Ask user before making any changes.

## Integration with Deploy

After validation passes, suggest:
```
Configuration is valid! Run /ha:deploy to push changes to Home Assistant.
```
