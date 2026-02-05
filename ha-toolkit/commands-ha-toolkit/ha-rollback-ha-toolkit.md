---
name: ha-rollback
description: Roll back Home Assistant configuration to a previous state
disable-model-invocation: true
---

# Rollback Home Assistant Changes

> **Safety Invariant #5:** Never deploy unless explicitly requested.
> This command performs destructive git operations.
> Default mode is dry-run (preview only).

Revert to a previous configuration state.

## Dry-Run Mode (Default)

By default, rollback shows what WOULD happen without making changes.

User must explicitly confirm to execute the actual rollback.

## Flow

### 1. Check for uncommitted changes
```bash
git status
```

If changes exist, ask:
"You have uncommitted changes:
- modified: automations.yaml
- modified: scripts.yaml

Options:
a) Stash changes and continue (can restore later)
b) Commit current changes first
c) Cancel rollback"

### 2. Show recent commits
```bash
git log --oneline -10 --format="%h %ar - %s"
```

Display formatted list:
```
Recent changes:
1. abc123 (2 hours ago) - Add motion lights for kitchen
2. def456 (yesterday) - Update bedroom scene
3. ghi789 (2 days ago) - Add garage door automation
...

Which commit do you want to roll back to?
(Or type 'more' to see older history)
```

### 3. Preview (dry-run)

**ALWAYS preview before executing.**

```bash
# Show what files would change
git diff HEAD~<n>..HEAD --stat

# Show detailed changes
git diff HEAD~<n>..HEAD
```

Display preview:
```
## Rollback Preview (DRY RUN)

**Target:** Roll back to commit ghi789 (2 days ago)

**Changes that would be reverted:**
- automations.yaml: Remove 2 automations added in abc123, def456
- scripts.yaml: Restore previous version

**Commits to revert:**
- abc123: Add motion lights for kitchen
- def456: Update bedroom scene

**This is a preview. No changes have been made yet.**
```

### 4. Confirm execution

"Ready to execute rollback.

**What will happen:**
1. Revert changes from commits abc123, def456
2. Create new commit documenting the rollback
3. Push to remote (if configured)
4. Reload automations/scripts/scenes in HA

⚠️ This action modifies git history and HA configuration.

**Execute rollback?** [Yes / Show full diff / Cancel]"

### 5. Execute rollback (only after explicit confirmation)
```bash
git revert --no-commit HEAD~<n>..HEAD
git commit -m "Rollback: Revert abc123..def456 (user-requested)"
git push
```

### 6. Reload Home Assistant
```bash
hass-cli service call automation.reload
hass-cli service call script.reload
hass-cli service call scene.reload
```

### 7. Confirm with evidence
```
## Rollback Complete

| Step | Result |
|------|--------|
| Git revert | ✅ Commits abc123..def456 reverted |
| Git commit | ✅ Created xyz789 |
| Git push | ✅ origin/main updated |
| HA reload | ✅ Automations/scripts/scenes reloaded |

**Configuration reverted to state from ghi789 (2 days ago).**

Note: Rolled-back changes are preserved in git history.
To restore them later: "Restore the kitchen motion lights I rolled back"
```

## Recovery

If user changes their mind:
```bash
# Find the rollback commit
git log --oneline -5

# Revert the rollback (restores original changes)
git revert <rollback-commit-hash>
```

## Error Handling

| Error | Response |
|-------|----------|
| Merge conflict during revert | Show conflict, offer manual resolution or abort |
| Push rejected | Offer: retry, force push (with warning), or local-only |
| HA reload failed | Check error logs, offer to retry or investigate |
