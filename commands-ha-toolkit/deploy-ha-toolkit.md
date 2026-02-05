---
description: Push configuration changes to Home Assistant via git
allowed-tools: Read, Write, Bash, AskUserQuestion, Glob
---

# Deploy Configuration to Home Assistant

Push local configuration changes to the git repository, triggering Home Assistant to pull and reload.

## Prerequisites

- Git repository configured (via /ha:onboard)
- Changes to commit
- Git Pull add-on running on Home Assistant

## Process

### Step 1: Check for Changes

Check git status to see what's changed:
```bash
git status --short
```

If no changes:
- Inform user there's nothing to deploy
- Ask if they want to pull latest from remote instead

### Step 2: Validate Configuration

Before deploying, validate the configuration:
- Run local YAML validation
- If hass-cli available, run HA config check
- Stop if validation fails (unless user overrides)

### Step 3: Review Changes

Show the user what will be deployed:
```bash
git diff --stat
```

For each changed file, show a brief summary of what changed.

Ask user to confirm they want to deploy these changes.

### Step 4: Commit Changes

Create a commit with a descriptive message:

Ask user for commit message or generate one based on changes:
- "Update automation: motion lights"
- "Add new scene: movie night"
- "Fix template sensor: average temperature"

```bash
git add -A
git commit -m "commit message"
```

### Step 5: Push to Remote

Push changes to the remote repository:
```bash
git push origin main
```

Handle push failures:
- Fetch and merge if behind remote
- Resolve conflicts if necessary
- Retry push

### Step 6: Trigger HA Reload (Optional)

If hass-cli is configured, offer to trigger a reload:
```bash
hass-cli service call homeassistant.reload_core_config
```

Or for specific domains:
```bash
hass-cli service call automation.reload
hass-cli service call script.reload
hass-cli service call scene.reload
```

### Step 7: Verify Deployment

After push:
1. Wait a moment for HA to pull (based on Git Pull interval)
2. Check if changes are reflected (if possible)
3. Report success

## Output

```
Deployment Summary
══════════════════

Changes deployed:
  📝 automations.yaml (+15, -3)
  📝 packages/climate.yaml (+8, -0)

Commit: abc1234 "Add motion-triggered lighting automation"
Pushed to: origin/main

Home Assistant will pull changes within 5 minutes.
To force immediate reload, the Git Pull add-on can be restarted.

✅ Deployment complete!
```

## Rollback Information

After successful deploy, inform user:
```
To rollback this deployment:
  git revert abc1234
  git push origin main
Or run: /ha:deploy --rollback
```

## Flags

- `--force` - Skip validation and deploy anyway
- `--dry-run` - Show what would be deployed without committing
- `--rollback` - Revert the last deployment
