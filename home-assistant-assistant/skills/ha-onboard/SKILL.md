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

## Pacing

**Present one step (or substep) at a time.** After presenting a step, stop and wait for the user to confirm they've completed it before moving on. Do not show upcoming steps — the user doesn't need to see what's next until they get there.

When the wizard starts, give a brief high-level summary (2-3 sentences max) of what we'll do, then begin at the step indicated by Resume Detection. Do NOT show the full wizard overview table to the user.

## Resume Detection

Before starting the wizard, check multiple environment signals to determine where the user left off.

**Run this as a single script. Wait for the results before deciding which step to present. Do NOT run any step content until resume detection is complete.**

```bash
# Check all environment signals
[ -f "configuration.yaml" ] && echo "HAS_CONFIG" || echo "NO_CONFIG"
git remote -v 2>/dev/null | head -1 || echo "NO_GIT_REMOTE"
hass-cli --version 2>/dev/null || echo "NO_HASS_CLI"
[ -n "$HASS_TOKEN" ] && echo "HAS_TOKEN" || echo "NO_TOKEN"
[ -n "$HASS_SERVER" ] && echo "HAS_SERVER" || echo "NO_SERVER"
```

Use this decision table to skip to the right step:

| Signal | Meaning | Skip to |
|--------|---------|---------|
| No `configuration.yaml` + no hass-cli + no token | Fresh start | Step 1 |
| No `configuration.yaml` + hass-cli or token present | Wrong directory (setup already started) | Ask user for their config path, verify it contains `configuration.yaml`, then tell them to restart Claude Code from that directory (Step 4 logic) |
| `configuration.yaml` + no git remote | Config dir but no git setup | Step 2 |
| `configuration.yaml` + git remote + no hass-cli | Git done, need CLI tools | Step 5 |
| `configuration.yaml` + git remote + hass-cli + no token/server | Need connection setup | Step 6 |
| `configuration.yaml` + git remote + hass-cli + token + server | Need Git Pull or verify | Step 7 |
| All present | Run verification | Step 8 |

**Note:** The Git Pull add-on runs on the HA appliance and can't be detected from the local machine. If all other signals are present, skip to Step 7 and ask the user whether they've already configured it. If yes, proceed to Step 8.

Tell the user which step you're resuming at and why (e.g., "I see you have hass-cli installed but no connection configured — let's pick up at Step 6").

## Wizard Overview

| Step | Description |
|------|-------------|
| 1 | Environment detection |
| 2 | Git setup on Home Assistant |
| 3 | Clone config locally |
| 4 | **Restart session** (hard stop) |
| 5 | hass-cli installation |
| 6 | HA connection setup (token, URL, env vars) |
| 7 | Git Pull add-on configuration |
| 8 | Verification tests |

## Step 1: Environment Detection

Detect the user's environment:

```bash
# Check OS
uname -s 2>/dev/null || echo "Windows"

# Check git
git --version 2>/dev/null || echo "NOT_INSTALLED"

# Check Python
python3 --version 2>/dev/null || python --version 2>/dev/null || echo "NOT_INSTALLED"
```

Present findings and ask if they want to proceed.

If git is not installed, it must be installed before continuing — it's required for all remaining steps.

**→ Wait for user confirmation before proceeding to Step 2.**

## Step 2: Git Setup on Home Assistant

The user's Home Assistant already has their configuration. This step gets it into a git repo and pushed to GitHub so they can clone it locally.

Tell the user what this step will accomplish in one sentence, then start with substep 2a. **Present one substep at a time.**

### 2a: Install Terminal & SSH Add-on

Guide the user through the HA Web UI:

1. Open Home Assistant web interface
2. Go to **Settings > Add-ons > Add-on Store**
3. Search for **"Terminal & SSH"** (the official one by Home Assistant)
4. Click **Install**
5. After install, click **Start**
6. The Terminal tab will appear in the add-on page — click it to open

**→ Wait for user to confirm the add-on is installed and the terminal is open.**

### 2b: Initialize Git in /config

In the HA terminal (from the add-on):

```bash
cd /config
git init
git add .
git commit -m "Initial Home Assistant config"
```

If git complains about identity, have them set it first:
```bash
git config user.email "you@example.com"
git config user.name "Your Name"
```

**→ Wait for user to confirm the commit succeeded.**

### 2c: Create GitHub Repository

Guide the user:

1. Go to [github.com/new](https://github.com/new) in their browser
2. Name it something like `ha-config`
3. Set it to **Private**
4. Do NOT initialize with README, .gitignore, or license (the repo already has content)
5. Click **Create repository**
6. Copy the HTTPS URL (e.g., `https://github.com/username/ha-config.git`)

**→ Wait for user to share the repo URL before proceeding.**

### 2d: Push to GitHub

Back in the HA terminal:

```bash
cd /config
git remote add origin https://github.com/USERNAME/ha-config.git
git branch -M main
git push -u origin main
```

GitHub will prompt for authentication. Guide the user to use a **Personal Access Token** (not their password):

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. **Generate new token (classic)**
3. Give it `repo` scope
4. Copy the token
5. When git asks for password, paste the token

Confirm the push succeeded:
"Check that your code appears at `https://github.com/USERNAME/ha-config` in your browser."

**→ Wait for user to confirm the push succeeded before proceeding to Step 3.**

## Step 3: Clone Config Locally

On the user's desktop machine (where Claude Code is running):

```bash
git clone https://github.com/USERNAME/ha-config.git
```

Verify the clone has configuration.yaml:
```bash
ls ha-config/configuration.yaml
```

**→ Wait for user to confirm the clone succeeded before proceeding to Step 4.**

## Step 4: Restart Session

This is a **hard stop**. The remaining steps must run from inside the cloned config directory.

Tell the user:

"Your HA config is now cloned locally. To continue setup:

1. Exit this Claude Code session
2. `cd ha-config` (or wherever you cloned it)
3. Start Claude Code again with the plugin:
   ```
   claude --plugin-dir path/to/home-assistant-assistant
   ```
4. Run `/ha:onboard` again — I'll detect the config and pick up where we left off (Step 5)."

**Do not proceed past this point.** The remaining steps require being in the config directory.

## Step 5: hass-cli Installation

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

**→ Wait for user to confirm hass-cli is installed before proceeding to Step 6.**

## Step 6: HA Connection Setup

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
   "Let's connect to your Home Assistant!

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

**→ Wait for user to confirm connection is working before proceeding to Step 7.**

## Step 7: Git Pull Add-on Configuration

Guide the user to configure Home Assistant to auto-pull from their GitHub repo.

**For HAOS/Supervised (Git Pull Add-on):**
1. Settings > Add-ons > Add-on Store
2. Search "Git pull" > Install
3. Configure:
   ```yaml
   git_branch: main
   git_command: pull
   repository: https://github.com/username/ha-config.git
   auto_restart: true
   ```

The repository URL should use HTTPS to match the setup from Step 2.

**For non-HAOS:** Provide cron job alternative.

Ask user to confirm HA-side setup is complete.

**→ Wait for user to confirm Git Pull add-on is configured before proceeding to Step 8.**

## Step 8: Verification Tests

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

**Exception:** Git setup (Steps 2-3) cannot be skipped — git is required for the deploy workflow.

## Settings Storage

Save configuration to `.claude/settings.local.json`:
```json
{
  "ha": {
    "config_path": "/path/to/ha-config",
    "git_remote": "https://github.com/user/repo.git",
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
| connection | URL and token | Re-run Step 6 (connection setup) |
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
/ha:onboard git_remote https://github.com/user/repo.git
```

Update the setting and confirm.

## Post-Onboarding

"Setup complete! You can now:
- Ask me to create automations, scripts, or scenes
- `/ha:validate` - Check configuration for errors
- `/ha:deploy` - Deploy changes to Home Assistant
- `/ha:onboard` - Reconfigure individual settings"
