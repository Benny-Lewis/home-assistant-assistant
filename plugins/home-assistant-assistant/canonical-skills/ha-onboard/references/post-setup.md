# ha-onboard — Settings Storage, Reconfiguration, and Post-Onboarding

Reference for how onboarding persists its state, how to update individual settings later, and what to say after the wizard completes.

## Settings Storage

Save configuration to `.claude/settings.local.json`:
```json
{
  "permissions": {
    "allow": [
      "Skill(ha-onboard)",
      "Skill(ha-validate)",
      "Skill(ha-deploy)",
      "Skill(ha-analyze)",
      "Skill(ha-naming)",
      "Skill(ha-apply-naming)",
      "Skill(ha-automations)",
      "Skill(ha-scripts)",
      "Skill(ha-scenes)",
      "Skill(ha-devices)",
      "Skill(ha-config)",
      "Skill(ha-lovelace)",
      "Skill(ha-jinja)",
      "Skill(ha-troubleshooting)",
      "Bash(hass-cli *)"
    ]
  },
  "ha": {
    "config_path": "/path/to/ha-config",
    "git_remote": "https://github.com/user/repo.git",
    "git_branch": "main",
    "setup_complete": true,
    "setup_date": "2026-02-05"
  },
  "deploy": {
    "pull_method": "git_pull_addon",
    "git_remote": "origin",
    "git_branch": "main"
  }
}
```

The `permissions.allow` array auto-approves all plugin skills and hass-cli commands, removing per-use permission prompts. Uses short skill names (e.g., `Skill(ha-naming)`) — this is the canonical format Claude Code expects for permission matching.

Note: Connection settings (HASS_TOKEN, HASS_SERVER) are stored as
environment variables, NOT in the settings file.

See `references/settings-schema.md` (plugin root) for full schema.

## Reconfigure Individual Settings

For returning users who want to update a specific setting without re-running onboarding:

| Setting | Description | Action |
|---------|-------------|--------|
| connection | URL and token | Re-run Step 6 (connection setup) |
| config_path | Local path to HA config | Update `.claude/settings.local.json` |
| git_remote | Git remote URL | Update `.claude/settings.local.json` |
| git_branch | Git branch for deploy pushes | Update `.claude/settings.local.json` |
| conventions | Naming conventions | Use the `ha-naming` skill |

### Config Path Setting

1. Ask user for the new path
2. Verify path exists and contains configuration.yaml
3. Update `.claude/settings.local.json`

### Git Remote Setting

1. Ask user for the git remote URL
2. Verify access: `git ls-remote <url> 2>&1 | head -1`
3. Update `.claude/settings.local.json`

### Git Branch Setting

1. Ask user for the git branch name
2. Verify it exists (or can be created): `git show-ref --verify --quiet refs/heads/<branch> || git ls-remote --heads origin <branch>`
3. Update `.claude/settings.local.json`

### Quick Update Mode

```
/ha-onboard config_path /home/user/ha-config
/ha-onboard git_remote https://github.com/user/repo.git
/ha-onboard git_branch main
```

Update the setting and confirm.

## Post-Onboarding

"Setup complete! You can now:
- Ask me to create automations, scripts, or scenes
- `/ha-validate` - Check configuration for errors
- `/ha-deploy` - Deploy changes to Home Assistant
- `/ha-onboard` - Reconfigure individual settings"
