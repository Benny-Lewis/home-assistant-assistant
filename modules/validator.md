# Validator Module

Shared procedures for evidence-based validation of Home Assistant configurations.

## Purpose

Validation must be **truthful**. Never claim "validation passed" without evidence. This module provides:
- Multiple validation tiers (local → HA-backed)
- Clear reporting of what ran vs. what was skipped
- Graceful degradation when tools are unavailable

## Validation Tiers

### Tier 1: YAML Syntax (Always Available)

Basic YAML parsing - catches structural errors.

```bash
# Python check
python3 -c "import yaml; yaml.safe_load(open('automations.yaml'))" && echo "✓ Valid YAML" || echo "✗ Invalid YAML"

# Alternative: yq
yq eval '.' automations.yaml > /dev/null && echo "✓ Valid YAML"
```

**What it catches:**
- Indentation errors
- Missing colons
- Invalid YAML syntax
- Unquoted special characters

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

**What it catches:**
- Missing required fields
- Invalid field types
- Unknown configuration keys

### Tier 3: Runtime Validation (HA-Backed)

Validates against the actual Home Assistant instance.

```bash
# Verify entity exists
hass-cli state get light.kitchen_main

# Verify service exists
hass-cli service list | grep "light.turn_on"

# Full config check (requires HA access)
hass-cli config check
```

**What it catches:**
- Non-existent entities
- Unavailable services
- Device capability mismatches

## Validation Procedure

### 1. Detect Available Tools

```bash
# Check what's available
YAML_CHECK="false"
HA_CHECK="false"

python3 -c "import yaml" 2>/dev/null && YAML_CHECK="true"
hass-cli state list > /dev/null 2>&1 && HA_CHECK="true"
```

### 2. Run Available Validations

Run all available tiers in order:

```
1. YAML Syntax → Always run
2. Schema Check → Run if hass-cli available
3. Entity Resolution → Run if hass-cli available
```

### 3. Report Results

Always produce an evidence table showing what ran:

```markdown
## Validation Results

### What Ran vs. Skipped

| Check | Status | Result |
|-------|--------|--------|
| YAML Syntax | ✓ Ran | Passed |
| HA Schema | ✓ Ran | Passed |
| Entity Resolution | ✓ Ran | 3/3 entities found |
| Service Validation | ⊘ Skipped | hass-cli unavailable |

### Issues Found

None

### Confidence Level

**High** - All available checks passed
```

## Confidence Levels

Based on what validations actually ran:

| Checks Completed | Confidence |
|------------------|------------|
| YAML only | Low - syntax OK, semantics unknown |
| YAML + Schema | Medium - structure OK, runtime unknown |
| YAML + Schema + HA | High - fully validated |

## Error Reporting

When validation fails, provide actionable information:

```markdown
## Validation Failed

### Error Details

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

- [If passed] Ready for deployment
- [If failed] Fix issues above, then re-validate
- [If incomplete] Consider installing hass-cli for full validation
```

## Integration Points

- **/ha-validate command**: Primary user-facing validation
- **/ha-deploy command**: Pre-deploy validation gate
- **ha-automations skill**: Post-generation validation
- **ha-config-validator agent**: Deep validation analysis
