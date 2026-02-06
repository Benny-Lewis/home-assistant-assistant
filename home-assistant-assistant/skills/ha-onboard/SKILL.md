---
name: ha-onboard
description: Use when user needs to set up their Home Assistant connection, configure settings, install prerequisites, or mentions "onboard", "setup", "connect", "configure".
user-invocable: true
allowed-tools: Read, Bash, AskUserQuestion, Glob, Grep
---

# Home Assistant Onboarding & Connection Setup

> **Safety Invariant #4:** Never print or echo tokens/secrets.
> Check presence only, never display values.

Guide the user through setting up their environment to use the HA Toolkit plugin, connecting to Home Assistant, and configuring settings.

## Wizard Overview

| Step | Description |
|------|-------------|
| 1 | Environment detection |
| 2 | hass-cli installation |
| 3 | HA connection setup (token, URL, env vars) |
| 4 | Git repository setup |
| 5 | HA-side Git Pull config |
| 6 | Verification tests |

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

### Prerequisites Check

Check if hass-cli is installed:

```bash
hass-cli --version
```

If not installed, guide user to install it first (Step 2).

### Check Existing Configuration

Check if HASS_TOKEN is already set (presence only, NOT value):

**Bash/Git Bash:**
```bash
[ -n "$HASS_TOKEN" ] && echo "HASS_TOKEN is set" || echo "HASS_TOKEN is not set"
```

**PowerShell:**
```powershell
if ($env:HASS_TOKEN) { "HASS_TOKEN is set" } else { "HASS_TOKEN is not set" }
```

**CMD:**
```cmd
if defined HASS_TOKEN (echo HASS_TOKEN is set) else (echo HASS_TOKEN is not set)
```

If set, ask: "Found existing HASS_TOKEN. Do you want to reconfigure?"

### Token Creation & Environment Variable Setup

1. **Welcome message:**
   "Let's connect to your Home Assistant! This is a one-time setup.

   I'll need two things:
   - An access token (like a password for the API)
   - Your Home Assistant's URL"

2. **Guide user to get token:**
   "Open your Home Assistant web interface and go to:
   Profile (bottom left) > Long-Lived Access Tokens > Create Token

   Give it a name like 'Claude Code' and click Create.

   Important: Copy the token now - HA only shows it once!

   **Do not paste the token here.** Instead, set it as an environment variable.
   I'll show you how based on your platform."

3. **Platform-specific environment variable setup:**

   **For Bash/Zsh (macOS, Linux, Git Bash on Windows):**
   "Add these lines to your shell config (~/.bashrc, ~/.zshrc, or ~/.bash_profile):
   ```bash
   export HASS_TOKEN='your-token-here'
   export HASS_SERVER='http://homeassistant.local:8123'
   ```
   Then run: `source ~/.bashrc` (or your config file)"

   **For PowerShell (Windows):**
   "Run these commands, or add them to your PowerShell profile:
   ```powershell
   $env:HASS_TOKEN = 'your-token-here'
   $env:HASS_SERVER = 'http://homeassistant.local:8123'
   ```
   For persistence, add to `$PROFILE`:
   ```powershell
   [Environment]::SetEnvironmentVariable('HASS_TOKEN', 'your-token-here', 'User')
   [Environment]::SetEnvironmentVariable('HASS_SERVER', 'http://homeassistant.local:8123', 'User')
   ```"

   **For CMD (Windows):**
   "Set system environment variables:
   Settings > System > About > Advanced system settings > Environment Variables
   Add HASS_TOKEN and HASS_SERVER as User variables"

4. **After user confirms setup, validate connection:**
   ```bash
   hass-cli state list | head -5
   ```

5. **If successful, show summary:**
   "Connection successful!

   Your Home Assistant at <url>:
   - [count] entities found
   - [count] automations
   - [count] scripts
   - [count] scenes"

6. **If connection fails, show troubleshooting:**
   "Couldn't connect. Common issues:
   - Is Home Assistant running?
   - Are you on the same network?
   - Is HASS_SERVER set correctly?
   - Is the token valid (not expired)?

   Check token is set (but don't show it!):
   `[ -n "$HASS_TOKEN" ] && echo "Token set" || echo "Token not set"`"

### Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| HASS_TOKEN | Long-lived access token | (secret) |
| HASS_SERVER | Home Assistant URL | http://homeassistant.local:8123 |

### Security Notes

- **Never echo tokens** - check presence only
- **Never commit tokens to git** - use environment variables
- Tokens can be revoked in HA > Profile > Long-Lived Access Tokens

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
1. Settings > Add-ons > Add-on Store
2. Search "Git pull" > Install
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
| Git | Connected to github.com/user/ha-config |
| hass-cli | Connected to homeassistant.local |
| Entities | 147 entities accessible |
| Config path | Valid |

Setup complete! Quick start:
- Ask me to create automations, scripts, or scenes
- `/ha:validate` - Validate your config
- `/ha:deploy` - Deploy changes to HA
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
environment variables, NOT in the settings file.

See `references/settings-schema.md` for full schema.

## Reconfigure Individual Settings

For returning users who want to update a specific setting without re-running onboarding:

| Setting | Description | Action |
|---------|-------------|--------|
| connection | URL and token | Re-run Step 3 (connection setup) |
| config_path | Local path to HA config | Update `.claude/settings.local.json` |
| git_remote | Git remote URL | Update `.claude/settings.local.json` |
| conventions | Naming conventions | Use the `ha-naming` skill |

### Config Path Setting

1. Ask user for the new path
2. Verify path exists and contains configuration.yaml
3. Update `.claude/settings.local.json`

### Git Remote Setting

1. Ask user for the git remote URL
2. Verify access: `git ls-remote <url> 2>&1 | head -1`
3. Update `.claude/settings.local.json`

### Quick Update Mode

```
/ha:onboard config_path /home/user/ha-config
/ha:onboard git_remote git@github.com:user/repo.git
```

Update the setting and confirm.

## Post-Onboarding

"Setup complete! You can now:
- Ask me to create automations, scripts, or scenes
- `/ha:validate` - Check configuration for errors
- `/ha:deploy` - Deploy changes to Home Assistant
- `/ha:onboard` - Reconfigure individual settings"
