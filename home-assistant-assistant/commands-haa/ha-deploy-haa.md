---
name: ha-deploy
description: Deploy Home Assistant configuration changes with validation
---

# Deploy Home Assistant Changes

Deploy changes to automations, scripts, and scenes with validation.

## Pre-Deploy Validation

Always validate before deploying. Delegate to ha-config-validator agent.

If validation fails, show errors and offer:
a) Fix automatically (if typo/suggestion available)
b) Go back to editing
c) Abort deploy

## Default Flow (auto_deploy: false)

1. **Show diff**
   ```bash
   git diff --staged
   git diff
   ```

   Display changes in formatted box.

2. **Ask for confirmation**
   Options:
   a) Deploy now
   b) Edit commit message
   c) Go back to editing
   d) Keep working - deploy later
   e) Discard changes

3. **Commit**
   ```bash
   git add <changed_files>
   git commit -m "<message>"
   ```

4. **Push (if remote configured)**
   ```bash
   git push
   ```

   If push fails, ask user:
   a) Continue anyway (reload HA with local changes)
   b) Abort
   c) Retry

5. **Reload Home Assistant**
   ```bash
   hass-cli service call automation.reload
   hass-cli service call script.reload
   hass-cli service call scene.reload
   ```

6. **Verify**
   Check automation/script/scene appears in HA:
   ```bash
   hass-cli state get automation.<name>
   ```

7. **Confirm success**
   "Deployed successfully. [name] is now active."

## Auto-Deploy Flow (auto_deploy: true)

Skip steps 1-2, go directly to commit/push/reload.
Still run validation.

## Configuration

Read settings from `.claude/home-assistant-assistant.md`:
- auto_deploy: boolean
- auto_commit: boolean
- auto_push: boolean
- auto_reload: boolean
- commit_prefix: string
