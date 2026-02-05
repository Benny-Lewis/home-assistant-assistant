# Editor Module

Shared procedures for safe YAML editing that preserves formatting and avoids brittle string replacements.

## Purpose

Home Assistant YAML files often have:
- Comments that should be preserved
- Specific indentation styles
- Anchor/alias references
- Multi-document files

Brittle string-based edits fail when:
- Anchor text isn't unique
- Indentation varies
- Comments interfere with matching

## Recommended Approach: AST Editing

### Using ruamel.yaml (Python)

If Python and ruamel.yaml are available:

```python
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True

# Load with comments preserved
with open('automations.yaml') as f:
    data = yaml.load(f)

# Find and update by ID
for automation in data:
    if automation.get('id') == 'target_automation_id':
        automation['alias'] = 'New Alias'
        break

# Write back with formatting preserved
with open('automations.yaml', 'w') as f:
    yaml.dump(data, f)
```

### Check for ruamel.yaml

```bash
python3 -c "from ruamel.yaml import YAML; print('available')" 2>/dev/null || echo "not available"
```

## Fallback: Structured Edit with Read Tool

When AST editing isn't available, use Claude Code's Edit tool with these safeguards:

### 1. Always Read First

```
Read the target file completely before editing.
```

### 2. Use Unique Anchors

Find content by unique identifiers:
- `id:` field for automations/scripts/scenes
- `alias:` as secondary anchor
- Surrounding context (3+ lines) for uniqueness

### 3. Include Full Block Context

Bad (brittle):
```yaml
old_string: "alias: Old Name"
new_string: "alias: New Name"
```

Good (unique context):
```yaml
old_string: |
  - id: kitchen_motion_light
    alias: Old Name
    trigger:
new_string: |
  - id: kitchen_motion_light
    alias: New Name
    trigger:
```

### 4. Preserve Indentation Exactly

Match the exact indentation of the target file:
- Home Assistant typically uses 2-space indentation
- Copy indentation from the Read output

## Edit Operations

### Add New Automation

1. Read `automations.yaml`
2. Find the end of the file or a logical insertion point
3. Append with proper formatting:

```yaml
- id: new_automation_id
  alias: New Automation
  description: ""
  triggers:
    - trigger: state
      entity_id: sensor.example
  conditions: []
  actions:
    - action: light.turn_on
      target:
        entity_id: light.example
```

### Update Existing Automation

1. Read file and locate by `id:`
2. Replace the entire automation block
3. Preserve any comments above the block

### Delete Automation

1. Read file and locate by `id:`
2. Remove the entire block including the leading `-`
3. Watch for orphaned comments

## Multi-Document Files

Some HA configs use `---` separators. Handle with care:

```yaml
# Document 1
automation: !include automations.yaml
---
# Document 2
script: !include scripts.yaml
```

When editing, preserve document structure.

## Validation After Edit

After any edit operation:

1. **Syntax check**:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('automations.yaml'))"
   ```

2. **HA config check** (if available):
   ```bash
   hass-cli config check
   ```

## Output Contract

After editing, report:

```markdown
## Edit Summary

| File | Operation | Target | Status |
|------|-----------|--------|--------|
| automations.yaml | Update | kitchen_motion_light | ✓ Success |

### Changes Made
- Updated alias from "Old Name" to "New Name"
- Updated trigger entity from sensor.old to sensor.new

### Validation
- YAML syntax: ✓ Valid
- HA config check: ✓ Passed (or "skipped - hass-cli unavailable")
```

## Integration Points

- **ha-automations skill**: Uses Editor for automation CRUD
- **ha-scenes skill**: Uses Editor for scene updates
- **ha-scripts skill**: Uses Editor for script modifications
- **ha:apply-naming command**: Uses Editor for bulk renames
