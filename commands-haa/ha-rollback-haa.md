---
name: ha-rollback
description: Roll back Home Assistant configuration to a previous state
---

# Rollback Home Assistant Changes

Revert to a previous configuration state.

## Flow

1. **Check for uncommitted changes**
   ```bash
   git status
   ```

   If changes exist, ask:
   a) Discard uncommitted changes and roll back
   b) Commit current changes first
   c) Cancel

2. **Show recent commits**
   ```bash
   git log --oneline -10
   ```

   Display formatted list with:
   - Relative time (2 hours ago, yesterday)
   - Commit message
   - Files changed

3. **User selects**
   a) Undo just the last change
   b) Roll back to specific commit (enter number)
   c) Show more history
   d) Cancel

4. **Show what will be reverted**
   ```bash
   git diff HEAD~<n>..HEAD
   ```

5. **Confirm**
   a) Confirm rollback
   b) Show full diff
   c) Cancel

6. **Execute rollback**
   ```bash
   git revert --no-commit HEAD~<n>..HEAD
   git commit -m "Rollback: <description>"
   git push
   ```

7. **Reload Home Assistant**
   ```bash
   hass-cli service call automation.reload
   hass-cli service call script.reload
   hass-cli service call scene.reload
   ```

8. **Confirm**
   "Rollback complete. Configuration reverted to [state]."

   "Note: Rolled-back changes are still in git history.
   To restore them later, ask: 'Restore the [name] I rolled back'"
