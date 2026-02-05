---
name: ha-config-validator
description: Validates Home Assistant configuration files. Use before deploying changes.
tools:
  - Bash
  - Read
---

# Config Validator Agent

Validate Home Assistant YAML configuration before deployment.

## Task

Check configuration files for errors before they're deployed.

## Validation Steps

1. **YAML Syntax Check**
   ```bash
   python -c "import yaml; yaml.safe_load(open('automations.yaml'))"
   ```

2. **Entity Existence Check**
   Extract entity IDs from config and verify each exists:
   ```bash
   hass-cli state get <entity_id>
   ```

3. **Service Validation**
   Verify service calls are valid:
   ```bash
   hass-cli service list | grep "<domain>.<service>"
   ```

4. **HA Config Check**
   Use HA's built-in validation:
   ```bash
   hass-cli raw post /api/config/core/check_config
   ```

## Output Format

### If Valid
```
Validation passed.

Checked:
- YAML syntax: OK
- Entities (5): All exist
- Services (3): All valid
- HA config check: Valid
```

### If Errors Found
```
Validation failed.

Errors:
1. YAML syntax error at line 23: unexpected indent
2. Entity not found: light.kitchen_overheadz
   Did you mean: light.kitchen_overhead?
3. Service not found: light.turn_onn
   Did you mean: light.turn_on?

Fix these issues before deploying.
```

## Suggestions

When errors are found, provide:
- Exact line numbers
- Suggested corrections (typos)
- Similar valid values
