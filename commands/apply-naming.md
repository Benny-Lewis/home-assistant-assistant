---
description: Execute the naming plan to rename entities and update references
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
argument-hint: [--dry-run | --phase N]
---

# Apply Naming Plan

Execute the naming plan created by `/ha:plan-naming` to rename entities, devices, and update all references.

## Prerequisites

- Naming plan exists at `.claude/naming-plan.yaml`
- hass-cli configured for entity renames
- Git configured for config file updates

## Safety Features

### Automatic Backup
Before any changes, create a backup:
- Git commit current state with message "Pre-rename backup"
- Record entity states via hass-cli

### Dry Run Mode
If `--dry-run` in arguments:
- Show all changes that would be made
- Don't execute any renames
- Validate the plan can be executed

### Phased Execution
If `--phase N` in arguments:
- Execute only the specified phase
- Allow manual verification between phases

## Execution Process

### Phase 1: Preparation

1. Read the naming plan from `.claude/naming-plan.yaml`
2. Verify plan status is not "completed"
3. Create pre-rename backup
4. Validate all source entities exist

### Phase 2: Entity ID Renames (via hass-cli)

For each entity rename in the plan:

```bash
# Rename entity via HA API
hass-cli entity rename old_entity_id new_entity_id
```

**Note:** This changes the entity registry in Home Assistant. The actual device is not affected, only how HA identifies it.

Track progress:
```yaml
renames_completed:
  - light.light_1 → light.living_room_ceiling ✓
  - light.light_2 → light.living_room_lamp ✓
```

### Phase 3: Friendly Name Updates

Update friendly names via hass-cli:
```bash
hass-cli entity update entity_id --name "New Friendly Name"
```

### Phase 4: Configuration File Updates

For each config file that references renamed entities:

1. Read the file
2. Replace old entity IDs with new ones
3. Update automation names if planned
4. Write the updated file

Use Edit tool for precise replacements:
- `old_string: light.light_1`
- `new_string: light.living_room_ceiling`

### Phase 5: Dashboard Updates

Update Lovelace dashboards:
- Find entity references in dashboard YAML
- Replace with new entity IDs
- Preserve dashboard structure

### Phase 6: Validation

After all renames complete:

1. Validate all config files
2. Check entity accessibility:
   ```bash
   hass-cli state get light.living_room_ceiling
   ```
3. Test key automations (manually trigger)
4. Verify dashboards render correctly

### Phase 7: Cleanup

1. Update plan status to "completed"
2. Create post-rename git commit
3. Generate summary report

## Rollback Capability

If any phase fails:
1. Stop execution
2. Report what was completed
3. Offer rollback options:
   - Revert git changes
   - Re-rename entities back (if possible)
   - Manual rollback instructions

Store rollback information:
```yaml
rollback:
  git_commit_before: abc1234
  entity_renames:
    - new: light.living_room_ceiling
      old: light.light_1
```

## Progress Reporting

Show progress during execution:

```
Applying Naming Plan
════════════════════

Phase 1: Preparation
  ✓ Backup created (commit: def5678)
  ✓ Plan validated

Phase 2: Entity Renames (8 of 23)
  ✓ light.light_1 → light.living_room_ceiling
  ✓ light.light_2 → light.living_room_lamp
  ⏳ switch.switch_1 → switch.living_room_fan
  ...

Phase 3: Friendly Names
  [pending]

Phase 4: Config Updates
  [pending]

Current: Renaming entities...
```

## Output

```
Naming Plan Applied
═══════════════════

Summary:
  Entities renamed: 23/23
  Friendly names updated: 23/23
  Config files updated: 8
  Dashboard files updated: 3

Git Commits:
  Pre-rename backup: abc1234
  Post-rename changes: def5678

Validation:
  ✓ All configs valid
  ✓ All entities accessible
  ⚠ 2 automations need manual testing

Recommended Next Steps:
  1. Test critical automations manually
  2. Check dashboards in HA UI
  3. Run /ha:deploy to sync with HA
  4. Monitor logs for entity errors

Rollback available:
  git revert def5678 abc1234
  Or contact support with plan ID: naming-2024-01-15
```

## Error Handling

If an error occurs:
- Stop at current step
- Report error details
- Save partial progress
- Provide recovery options:
  1. Retry failed operation
  2. Skip and continue
  3. Rollback completed changes
  4. Exit and investigate manually
