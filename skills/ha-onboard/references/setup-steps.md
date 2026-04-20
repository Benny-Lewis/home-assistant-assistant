# ha-onboard — Wizard Steps

The full 8-step onboarding wizard. SKILL.md holds the pacing rules, resume detection, and wizard overview; this file holds the step-by-step procedure.

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
4. Run `/ha-onboard` again — I'll detect the config and pick up where we left off (Step 5)."

**Do not proceed past this point.** The remaining steps require being in the config directory.

## Step 5: hass-cli Installation

If hass-cli is not installed, offer to install it:

"You'll need hass-cli to communicate with Home Assistant. I can install it for you now — okay to proceed?"

If user agrees, install based on platform:

**macOS (if Homebrew available):**
```bash
brew install homeassistant-cli
```

**All platforms (pip fallback):**
```bash
pip install homeassistant-cli
```

Verify after install:
```bash
hass-cli --version
```

If the install fails, show the error and suggest the user troubleshoot their Python/pip setup.

**→ Proceed to Step 6 after successful install.**

## Step 6: HA Connection Setup

### Check Existing Configuration

Check if HASS_TOKEN is already set (presence only, NOT value):

**Bash/Git Bash:**
```bash
TLEN=$(printf '%s' "$HASS_TOKEN" | wc -c); echo "TOKEN_LEN=$TLEN"
```
If `TOKEN_LEN>0`, the token is set.

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
   `TLEN=$(printf '%s' "$HASS_TOKEN" | wc -c); echo "TOKEN_LEN=$TLEN"`
   (TOKEN_LEN>0 means it's set)"

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

First, check if the Git Pull add-on is already installed:
```bash
MSYS_NO_PATHCONV=1 hass-cli raw get /api/hassio/addons 2>/dev/null | grep -qi "git"
```

**If add-on detected:** "Git Pull add-on is already installed. Is it configured to pull from your repo?" If yes → skip to Step 8. If no → show configuration instructions below.

**If add-on NOT detected or API unavailable:** Ask the user how they want HA to receive config updates, using AskUserQuestion:
1. **Git Pull add-on** (Recommended) — guide installation below
2. **SSH access** — user will manually pull or use `ssh <host> 'cd /config && git pull'`
3. **Manual** — user pulls on the HA side themselves

Cache the answer in `.claude/settings.local.json` under `deploy.pull_method`.

**Git Pull add-on installation (if needed):**

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

**→ Wait for user to confirm before proceeding to Step 8.**

## Step 8: Verification Tests

### CLAUDE.md Conflict Check

Before running verification tests, check for a `CLAUDE.md` in the HA config root:

```bash
[ -f "CLAUDE.md" ] && echo "HAS_CLAUDE_MD" || echo "NO_CLAUDE_MD"
```

If `HAS_CLAUDE_MD`: warn the user and present options via AskUserQuestion:

"Found a `CLAUDE.md` file in your HA config directory. This file provides project-level instructions to Claude Code. If it contains workflow guidance (like deploy commands or rename procedures), it may take priority over this plugin's skills."

Options:
1. **Keep it** — your CLAUDE.md instructions will take priority; use `/ha-naming`, `/ha-deploy` etc. explicitly when you want plugin workflows
2. **Remove or rename it** — plugin skills will auto-activate based on your questions
3. **Review it now** — I can show you what's in it

If `NO_CLAUDE_MD`: skip this check silently.

### Core Verification Tests

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
- `/ha-validate` - Validate your config
- `/ha-deploy` - Deploy changes to HA
```

## Skip Behavior

At any step, user can say "skip":
- Accept and move to next step
- Note in final summary
- Some features may not work

**Exception:** Git setup (Steps 2-3) cannot be skipped — git is required for the deploy workflow.
