---
name: ha:onboard
description: First-time setup wizard for Home Assistant toolkit
allowed-tools: Read, Bash, AskUserQuestion, Glob, Grep
---

# Home Assistant Toolkit Onboarding

> **Connection setup uses `/ha-connect` shared procedure.**
> Secret handling and cross-platform guidance are centralized there.

Guide the user through setting up their environment to use the HA Toolkit plugin.

## Wizard Overview

| Step | Description | Shared Procedure |
|------|-------------|------------------|
| 1 | Environment detection | This command |
| 2 | hass-cli installation | This command |
| 3 | HA connection setup | → `/ha-connect` |
| 4 | Git repository setup | This command |
| 5 | HA-side Git Pull config | This command |
| 6 | Verification tests | This command |

## Step 1: Environment Detection

Detect the user's environment:

```bash
# Check OS
uname -s 2>/dev/null || echo "Windows"

# Check git
git --version 2>/dev/null || echo "NOT_INSTALLED"

# Check hass-cli
hass-cli --version 2>/dev/null || echo "NOT_INSTALLED"

# Check Python
python3 --version 2>/dev/null || python --version 2>/dev/null || echo "NOT_INSTALLED"
```

Present findings and ask if they want to proceed or skip to specific steps.

## Step 2: hass-cli Installation

If hass-cli is not installed:

**macOS:**
```bash
brew install homeassistant-cli
```

**Linux/Windows (via pip):**
```bash
pip install homeassistant-cli
```

Verify: `hass-cli --version`

## Step 3: HA Connection Setup

**Delegate to `/ha-connect`.**

Do NOT duplicate token handling here. Say:
"Now let's connect to your Home Assistant instance."

Then invoke the `/ha-connect` shared procedure which handles:
- Token creation guidance
- Cross-platform env var setup (Bash, PowerShell, CMD)
- Secret safety (presence check only, never print value)
- Connection verification

After `/ha-connect` completes, continue to Step 4.

## Step 4: Git Repository Setup

Ask the user about their git setup:

**Option A: Existing HA Config Repo**
- Ask for the repository URL
- Clone if not already local
- Verify has configuration.yaml

**Option B: New Repository Needed**
- Guide them to create repo (GitHub, GitLab)
- Initialize and push current config

**Option C: Skip Git**
- Document that deploy/version control won't work
- Continue with limited functionality

For SSH repos, verify key setup:
```bash
ssh -T git@github.com 2>&1 | head -1
```

## Step 5: HA-Side Git Pull Setup

Guide the user to configure Home Assistant to pull from git.

**For HAOS/Supervised (Git Pull Add-on):**
1. Settings → Add-ons → Add-on Store
2. Search "Git pull" → Install
3. Configure:
   ```yaml
   git_branch: main
   git_command: pull
   repository: git@github.com:username/ha-config.git
   auto_restart: true
   ```

**For non-HAOS:** Provide cron job alternative.

Ask user to confirm HA-side setup is complete.

## Step 6: Verification Tests

| Test | Command | Expected |
|------|---------|----------|
| Git connectivity | `git fetch origin` | No errors |
| hass-cli | `hass-cli state list --limit 1` | Returns entity |
| Config path | Check for configuration.yaml | File exists |

Present results:
```
## Onboarding Results

| Component | Status |
|-----------|--------|
| Git | ✅ Connected to github.com/user/ha-config |
| hass-cli | ✅ Connected to homeassistant.local |
| Entities | ✅ 147 entities accessible |
| Config path | ✅ Valid |

🎉 Setup complete! Quick start:
- `/ha:generate automation "description"` - Generate automations
- `/ha:validate` - Validate your config
- `/ha-deploy` - Deploy changes to HA
```

## Skip Behavior

At any step, user can say "skip":
- Accept and move to next step
- Note in final summary
- Some features may not work

## Settings Storage

Save configuration to `.claude/settings.local.json`:
```json
{
  "ha": {
    "config_path": "/path/to/ha-config",
    "git_remote": "git@github.com:user/repo.git",
    "setup_complete": true,
    "setup_date": "2026-02-05"
  }
}
```

Note: Connection settings (HASS_TOKEN, HASS_SERVER) are stored as
environment variables, NOT in the settings file. See `/ha-connect`.

## Post-Onboarding

"Setup complete! Available commands:
- `/ha:generate` - Generate automations, scripts, scenes
- `/ha:validate` - Check configuration for errors
- `/ha-deploy` - Deploy changes to Home Assistant
- `/ha:setup` - Update individual settings
- `/ha-connect` - Reconfigure HA connection"
