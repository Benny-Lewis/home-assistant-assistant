---
name: ha:setup
description: Reconfigure HA Toolkit settings (URL, token, paths)
allowed-tools: Read, Bash, AskUserQuestion
argument-hint: [setting-name]
---

# Reconfigure HA Toolkit Settings

> **For connection settings (URL, token)**, use `/ha-connect` which has
> cross-platform guidance and proper secret handling.

Allow the user to update specific settings without running full onboarding.

## Available Settings

If no argument provided, ask the user which setting they want to update:

| Setting | Description | Updates Via |
|---------|-------------|-------------|
| connection | URL and token | `/ha-connect` (shared procedure) |
| config_path | Local path to HA config | This command |
| git_remote | Git remote URL | This command |
| conventions | Naming conventions | `/ha-conventions` skill |

## Process

### Connection Settings

**Delegate to `/ha-connect`.**

Do NOT duplicate token handling here. The `/ha-connect` command has:
- Cross-platform env var setup (Bash, PowerShell, CMD)
- Secret safety (never prints tokens)
- Connection verification

"To update your Home Assistant connection, run `/ha-connect`."

### Config Path Setting

1. Ask user for the new path
2. Verify path exists and contains configuration.yaml
3. Update `.claude/settings.local.json`:
   ```json
   {
     "ha": {
       "config_path": "/path/to/ha-config"
     }
   }
   ```

### Git Remote Setting

1. Ask user for the git remote URL
2. Verify access: `git ls-remote <url> 2>&1 | head -1`
3. Update `.claude/settings.local.json`

## Settings File Location

Settings stored in `.claude/settings.local.json` (gitignored).

See `references/settings-schema.md` for full schema.

## Quick Update Mode

```
/ha:setup config_path /home/user/ha-config
/ha:setup git_remote git@github.com:user/repo.git
```

Update the setting and confirm.

## First-Time Setup

If no settings exist, suggest:
"No settings found. For full setup, run `/ha:onboard`.
For just connection setup, run `/ha-connect`."
