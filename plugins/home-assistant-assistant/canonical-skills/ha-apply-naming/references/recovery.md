# ha-apply-naming — Recovery

Rollback and error-handling procedures for `/ha-apply-naming` execution failures.

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
