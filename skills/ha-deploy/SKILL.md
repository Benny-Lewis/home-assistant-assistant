---
name: ha-deploy
description: Deploy or roll back Home Assistant configuration changes via git
user-invocable: true
allowed-tools: Read, Write, Bash, AskUserQuestion, Glob
---

# Deploy & Rollback Home Assistant Configuration

> **CRITICAL:** This skill has side effects (git commit, git push, HA service calls).
> - NEVER invoke this skill unless the user explicitly asks to deploy, push, or rollback
> - ALWAYS show a summary of changes and get explicit user confirmation before each destructive step
> - Use AskUserQuestion to get confirmation at commit, push, and reload steps

> **Safety Invariant #5:** Never deploy unless explicitly requested.

Push local configuration changes to the git repository, triggering Home Assistant to pull and reload. Also handles rollback to previous states.

## Prerequisites

- Git repository configured (via `/ha-onboard`)
- Changes to commit (for deploy)
- Git Pull add-on running on Home Assistant

## Deploy Workflow

### Step 1: Check for Changes

```bash
git status --short
```

If no changes:
- Inform user there's nothing to deploy
- Ask if they want to pull latest from remote instead

### Step 2: Pre-Deploy Validation

**Always validate before deploying.** Delegate to ha-validate skill or ha-config-validator agent.

If validation fails, show errors and offer:
a) Fix issues (describe what to change)
b) Go back to editing
c) Abort deploy

### Step 2.5: Verify HA Can Pull

Check if `deploy.pull_method` is cached in `.claude/settings.local.json`. If cached, use that method and skip this step.

If not cached, check if Git Pull add-on is available:
```bash
MSYS_NO_PATHCONV=1 hass-cli raw get /api/hassio/addons 2>/dev/null | grep -i "git"
```

- **If found** → proceed with auto-pull workflow, cache `"deploy": { "pull_method": "git_pull_addon" }` in settings.
- **If not found or API unavailable** → ask user:

  "How does your HA instance get config updates?"
  1. **Git Pull add-on** — offer to help set it up
  2. **SSH access** — use `ssh <host> 'cd /config && git pull'`
  3. **Manual** — provide instructions to pull on HA side

  Cache the answer in `.claude/settings.local.json` under `deploy.pull_method` so we don't ask every time.

### Step 3: Review Changes — MANDATORY CONFIRMATION

Show the user what will be deployed:
```bash
git diff --staged
git diff
git diff --stat
```

For each changed file, show a brief summary of what changed.

Then use AskUserQuestion with options:
- "Deploy" — proceed with commit + push + reload
- "Edit commit message" — let user customize the message
- "Abort" — cancel deployment

**Do NOT proceed without explicit user selection.**

### Step 4: Commit Changes

Ask user for commit message or generate one based on changes:
- "Update automation: motion lights"
- "Add new scene: movie night"
- "Fix template sensor: average temperature"

```bash
git add <changed_files>
git commit -m "<message>"
```

### Step 5: Push to Remote

```bash
git push origin main
```

Handle push failures:
- Fetch and merge if behind remote
- "Push failed. Options:
  a) Continue anyway (reload HA with local changes only)
  b) Retry push
  c) Abort deployment"

### Step 6: Reload Home Assistant

If hass-cli is configured, offer to trigger a reload:
```bash
hass-cli service call automation.reload
hass-cli service call script.reload
hass-cli service call scene.reload
```

Or for full config reload:
```bash
hass-cli service call homeassistant.reload_core_config
```

### Step 7: Verify Deployment (Resolver-Driven)

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
| Git commit | commit abc123 |
| Git push | origin/main updated |
| Automation reload | Service call succeeded |
| Entity exists | Found: automation.kitchen_motion_light |
| Entity enabled | state: on |
```

### Step 8: Confirm Success

"Deployed successfully.

**Created:** automation.kitchen_motion_light
**Status:** Enabled
**Commit:** abc123

Test it by triggering the automation, or run `/ha-validate` to verify."

## Deploy Output Format

```
Deployment Summary

Changes deployed:
  automations.yaml (+15, -3)
  packages/climate.yaml (+8, -0)

Commit: abc1234 "Add motion-triggered lighting automation"
Pushed to: origin/main

Home Assistant will pull changes within 5 minutes.
To force immediate reload, the Git Pull add-on can be restarted.

Deployment complete!
```

## Flags

- `--force` - Skip validation and deploy anyway
- `--dry-run` - Show what would be deployed without committing
- `--rollback` - Enter rollback mode (see below)

## Auto-Deploy Mode (Deprecated)

Per Safety Invariant #5, all deployments require explicit confirmation.
The `auto_deploy` setting is ignored.

If user has `auto_deploy: true` in settings, warn:
"Note: auto_deploy is deprecated for safety reasons. All deployments now
require explicit confirmation. Would you like me to remove this setting?"

## Configuration

Read settings from `.claude/settings.local.json`:
- commit_prefix: string (e.g., "ha: ")
- git_remote: string (e.g., "origin")
- git_branch: string (e.g., "main")

---

## Rollback Workflow

> **Default mode is dry-run (preview only).**
> User must explicitly confirm to execute the actual rollback.

Revert to a previous configuration state.

### Step 1: Check for Uncommitted Changes

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

### Step 2: Show Recent Commits

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

### Step 3: Preview (Dry-Run)

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

### Step 4: Confirm Execution

"Ready to execute rollback.

**What will happen:**
1. Revert changes from commits abc123, def456
2. Create new commit documenting the rollback
3. Push to remote (if configured)
4. Reload automations/scripts/scenes in HA

This action modifies git history and HA configuration.

**Execute rollback?** [Yes / Show full diff / Cancel]"

### Step 5: Execute Rollback (Only After Explicit Confirmation)

```bash
git revert --no-commit HEAD~<n>..HEAD
git commit -m "Rollback: Revert abc123..def456 (user-requested)"
git push
```

### Step 6: Reload Home Assistant

```bash
hass-cli service call automation.reload
hass-cli service call script.reload
hass-cli service call scene.reload
```

### Step 7: Confirm with Evidence

```
## Rollback Complete

| Step | Result |
|------|--------|
| Git revert | Commits abc123..def456 reverted |
| Git commit | Created xyz789 |
| Git push | origin/main updated |
| HA reload | Automations/scripts/scenes reloaded |

**Configuration reverted to state from ghi789 (2 days ago).**

Note: Rolled-back changes are preserved in git history.
To restore them later: "Restore the kitchen motion lights I rolled back"
```

### Rollback Recovery

If user changes their mind:
```bash
# Find the rollback commit
git log --oneline -5

# Revert the rollback (restores original changes)
git revert <rollback-commit-hash>
```

### Rollback Error Handling

| Error | Response |
|-------|----------|
| Merge conflict during revert | Show conflict, offer manual resolution or abort |
| Push rejected | Offer: retry, force push (with warning), or local-only |
| HA reload failed | Check error logs, offer to retry or investigate |

## Deploy Error Recovery

**If deployment fails:**

1. Check HA logs:
   ```bash
   MSYS_NO_PATHCONV=1 hass-cli raw get /api/error_log | tail -20
   ```

2. Offer rollback option:
   "Deployment failed. Would you like to:
   a) View error details
   b) Rollback to previous commit
   c) Try to fix and redeploy"
