---
description: Reconfigure HA Toolkit settings (URL, token, paths)
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion
argument-hint: [setting-name]
---

# Reconfigure HA Toolkit Settings

Allow the user to update specific settings without running full onboarding.

## Available Settings

If no argument provided, ask the user which setting they want to update:

1. **ha_url** - Home Assistant URL
2. **ha_token** - Long-Lived Access Token
3. **config_path** - Local path to HA config repository
4. **repo_remote** - Git remote URL

If argument provided ($ARGUMENTS), update that specific setting.

## Process

1. Read current settings from `.claude/ha-toolkit.local.md` if it exists
2. Ask user for the new value for the requested setting
3. Update the settings file
4. Test the new configuration:
   - For ha_url/ha_token: Test with `hass-cli state list --limit 1`
   - For config_path: Verify configuration.yaml exists
   - For repo_remote: Test with `git ls-remote`
5. Report success or failure

## Settings File Location

Settings are stored in `.claude/ha-toolkit.local.md` in the current project directory.

If no settings file exists, create one with the updated value and suggest running `/ha:onboard` for complete setup.

## Quick Update Mode

For simple updates without full validation:
```
/ha:setup ha_url http://192.168.1.100:8123
/ha:setup config_path /home/user/ha-config
```

Update the setting and confirm the change.
