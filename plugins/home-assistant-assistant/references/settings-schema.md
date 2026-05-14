# Settings Schema Reference

This document defines the unified settings format for the HA Toolkit plugin.

## Settings File Location

Settings are stored in `.claude/settings.local.json` in the user's Home Assistant config repository.

**Important:**
- This file is user-managed, not shipped with the plugin
- Must be gitignored (add `.claude/` to `.gitignore`)
- Created on first run of `/ha-onboard`

## Schema

```json
{
  "permissions": {
    "allow": ["string[] - tool permission rules auto-approved for this project"]
  },
  "ha": {
    "config_path": "string (optional) - path to HA config directory",
    "git_remote": "string (optional, legacy fallback) - git remote or URL for push",
    "git_branch": "string (optional, legacy fallback) - git branch for push",
    "setup_complete": "boolean - whether onboarding finished",
    "setup_date": "string - ISO date of last onboarding"
  },
  "deploy": {
    "pull_method": "string (optional) - how HA gets config updates: 'git_pull_addon' | 'ssh' | 'manual'",
    "git_remote": "string (optional, preferred) - git remote or URL for deploy push",
    "git_branch": "string (optional, preferred) - git branch for deploy push"
  }
}
```

Deploy push target resolution:
1. `deploy.git_remote` / `deploy.git_branch`
2. `ha.git_remote` / `ha.git_branch` (legacy fallback)
3. `origin` / `main`

### Permissions

The `permissions.allow` array auto-approves plugin tools so the model can invoke them without per-use confirmation prompts. Onboarding writes the complete list:

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
  }
}
```

- Format: `Skill(skill-name)` for skills, `Bash(pattern)` for shell commands
- `Bash(hass-cli *)` covers all hass-cli commands with a single wildcard rule
- ha-resolver is excluded (agent-only, invoked via Task tool not Skill tool)
- Without these entries, each skill invocation prompts for user approval, creating friction that makes the model prefer answering from context instead of invoking skills

## Example

```json
{
  "permissions": {
    "allow": ["Skill(ha-onboard)", "Skill(ha-deploy)", "Bash(hass-cli *)"]
  },
  "ha": {
    "config_path": "/config",
    "git_remote": "origin",
    "git_branch": "main",
    "setup_complete": true,
    "setup_date": "2026-02-22"
  },
  "deploy": {
    "pull_method": "git_pull_addon",
    "git_remote": "origin",
    "git_branch": "main"
  }
}
```

## Migration from Legacy Formats

### From `.claude/ha-toolkit.local.md`

The old markdown format used `ha_url` and `ha_token` keys directly. Migrate by:
1. Reading values from the `.md` file
2. Creating `.claude/settings.local.json` with the schema above
3. Setting `ha_token_env` to `HASS_TOKEN` (prefer env vars over stored tokens)
4. Removing the old `.md` file

### From `.claude/home-assistant-assistant.md`

Same migration process. The old format also supported `auto_deploy` and `auto_commit`.

## Security Notes

- **Never store tokens directly** - use `ha_token_env` to reference an environment variable
- **Never print tokens** - even when echoing settings back to the user
- The `.claude/` directory must be gitignored to prevent accidental token exposure
