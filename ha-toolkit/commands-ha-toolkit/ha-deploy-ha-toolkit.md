---
name: ha-deploy
description: Deploy Home Assistant configuration changes with validation
disable-model-invocation: true
---

# Deploy Home Assistant Changes

> **Safety Invariant #5:** Never deploy unless explicitly requested.
> This command has side effects (git push, service calls).
> Only invoke when user explicitly requests deployment.

Deploy changes to automations, scripts, and scenes with validation.

## Pre-Deploy Validation

**Always validate before deploying.** Delegate to ha-config-validator agent.

If validation fails, show errors and offer:
a) Fix issues (describe what to change)
b) Go back to editing
c) Abort deploy

## Deploy Flow

**Every deployment requires explicit user confirmation.**

### 1. Show diff
```bash
git diff --staged
git diff
```
Display changes in formatted box.

### 2. Confirm intent
"Ready to deploy these changes to Home Assistant.

**What will happen:**
1. Commit changes to git
2. Push to remote (if configured)
3. Reload automations/scripts/scenes in HA
4. Verify entities exist

**Proceed with deployment?** [Yes / Edit commit message / Go back / Abort]"

### 3. Commit
```bash
git add <changed_files>
git commit -m "<message>"
```

### 4. Push (if remote configured)
```bash
git push
```

If push fails:
"Push failed. Options:
a) Continue anyway (reload HA with local changes only)
b) Retry push
c) Abort deployment"

### 5. Reload Home Assistant
```bash
hass-cli service call automation.reload
hass-cli service call script.reload
hass-cli service call scene.reload
```

### 6. Verify deployment (resolver-driven)

**Do NOT assume entity ID format.** Verify entity actually exists:

```bash
# Find the automation by alias/ID pattern
hass-cli state list | grep -i "automation.*<name_pattern>"
```

If found:
```bash
hass-cli state get automation.<actual_id>
```

Report verification result with evidence:
```
| Check | Result | Evidence |
|-------|--------|----------|
| Git commit | ✅ | commit abc123 |
| Git push | ✅ | origin/main updated |
| Automation reload | ✅ | Service call succeeded |
| Entity exists | ✅ | Found: automation.kitchen_motion_light |
| Entity enabled | ✅ | state: on |
```

### 7. Confirm success
"✅ Deployed successfully.

**Created:** automation.kitchen_motion_light
**Status:** Enabled
**Commit:** abc123

Test it by triggering the automation, or run `/ha-validate` to verify."

## Auto-Deploy Mode

⚠️ **Auto-deploy is deprecated.** Per Safety Invariant #5, all deployments
require explicit confirmation. The `auto_deploy` setting is ignored.

If user has `auto_deploy: true` in settings, warn:
"Note: auto_deploy is deprecated for safety reasons. All deployments now
require explicit confirmation. Would you like me to remove this setting?"

## Error Recovery

**If deployment fails:**

1. Check HA logs:
   ```bash
   hass-cli raw get /api/error_log | tail -20
   ```

2. Offer rollback option:
   "Deployment failed. Would you like to:
   a) View error details
   b) Rollback to previous commit
   c) Try to fix and redeploy"

## Configuration

Read settings from `.claude/settings.local.json`:
- commit_prefix: string (e.g., "ha: ")
- git_remote: string (e.g., "origin")
- git_branch: string (e.g., "main")
