---
name: ha:onboard
description: First-time setup wizard for Home Assistant toolkit
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion, Glob, Grep
---

# Home Assistant Toolkit Onboarding

Guide the user through setting up their environment to use the HA Toolkit plugin. This is an interactive, multi-step wizard with skippable sections.

## Step 1: Environment Detection

Detect the user's environment:

- Operating System: Check platform (Windows, macOS, Linux)
- Git: Check if git is installed (!`git --version 2>/dev/null || echo "NOT_INSTALLED"`)
- hass-cli: Check if installed (!`hass-cli --version 2>/dev/null || echo "NOT_INSTALLED"`)
- Python/pip: Check availability (!`python3 --version 2>/dev/null || python --version 2>/dev/null || echo "NOT_INSTALLED"`)

Present findings to user and ask if they want to proceed with setup or skip (they already have everything configured).

## Step 2: hass-cli Installation

If hass-cli is not installed, guide the user through installation based on their OS:

**macOS:**
```bash
brew install homeassistant-cli
```

**Linux/Windows (via pip):**
```bash
pip install homeassistant-cli
```

After installation, verify with `hass-cli --version`.

## Step 3: hass-cli Configuration

Configure hass-cli to connect to the user's Home Assistant instance.

Ask the user for:
1. Home Assistant URL (e.g., `http://homeassistant.local:8123` or `https://ha.example.com`)
2. Long-Lived Access Token (guide them to create one: Profile → Security → Long-Lived Access Tokens → Create Token)

Help them set environment variables. Create or update shell profile:

**For bash/zsh (~/.bashrc or ~/.zshrc):**
```bash
export HASS_SERVER="http://homeassistant.local:8123"
export HASS_TOKEN="your-long-lived-access-token"
```

**For Windows (PowerShell profile or environment variables):**
```powershell
$env:HASS_SERVER = "http://homeassistant.local:8123"
$env:HASS_TOKEN = "your-token"
```

Test the connection:
```bash
hass-cli state list --limit 1
```

If successful, proceed. If failed, troubleshoot:
- Check URL is accessible
- Verify token is valid
- Check for network/firewall issues

## Step 4: Git Repository Setup

Ask the user about their current git setup:

**Option A: Existing HA Config Repo**
- Ask for the repository URL
- Clone it locally if not already cloned
- Verify structure looks like HA config (has configuration.yaml)

**Option B: New Repository Needed**
- Guide them to create a new repo (GitHub, GitLab, etc.)
- Help export current HA config
- Initialize git repo and push

**Option C: Skip Git Setup**
- User doesn't want git-based config management
- Document that some features (deploy, version control) won't work

For SSH-based repos, verify SSH key setup:
```bash
ssh -T git@github.com 2>&1 | head -1
```

## Step 5: Home Assistant Side Setup

Guide the user to configure their Home Assistant to pull from git:

1. **Install Git Pull Add-on** (for HAOS/Supervised):
   - Navigate to Settings → Add-ons → Add-on Store
   - Search for "Git pull"
   - Install and configure

2. **Configure Git Pull Add-on:**
   ```yaml
   git_branch: main
   git_command: pull
   git_remote: origin
   repository: git@github.com:username/ha-config.git
   auto_restart: true
   repeat:
     active: true
     interval: 300
   ```

3. **For non-HAOS installations:**
   - Provide alternative: cron job with git pull
   - Or manual pull workflow

Ask user to confirm they've completed HA-side setup.

## Step 6: Plugin Configuration

Create the plugin settings file to store user's configuration:

Write to `.claude/ha-toolkit.local.md`:
```yaml
---
ha_url: "user-provided-url"
config_repo_path: "/path/to/local/ha-config"
config_repo_remote: "git@github.com:user/repo.git"
setup_complete: true
setup_date: "YYYY-MM-DD"
---

# HA Toolkit Settings

This file stores your Home Assistant toolkit configuration.
```

Add `.claude/ha-toolkit.local.md` to `.gitignore` if not already present.

## Step 7: Verification Tests

Run verification tests to ensure everything works:

### Test 1: Git Connectivity
```bash
cd /path/to/ha-config && git fetch origin
```
Expected: No errors

### Test 2: hass-cli Connection
```bash
hass-cli state list --limit 1
```
Expected: Returns at least one entity

### Test 3: Entity Access
```bash
hass-cli entity list | head -5
```
Expected: Lists entities

### Test 4: Config Path Valid
Check that the HA config path contains configuration.yaml

### Test 5: Git Sync Round-Trip (Optional)
- Create a test file
- Commit and push
- Wait for HA to pull (or trigger manually)
- Verify file appears on HA
- Delete test file and clean up

Present results summary:
```
Onboarding Results:
───────────────────
✅ Git: Connected to github.com/user/ha-config
✅ hass-cli: Connected to homeassistant.local:8123
✅ Entities: 147 entities accessible
✅ Config Path: Valid (/path/to/ha-config)
⚠️  Git Sync: Skipped (optional)

🎉 Setup complete! You're ready to use the HA Toolkit.

Quick start commands:
  /ha:generate automation "description"  - Generate automations
  /ha:audit-naming                        - Check naming consistency
  /ha:validate                            - Validate your config
  /ha:analyze                             - Get suggestions
```

## Skip Behavior

At any step, if the user says "skip" or indicates they already have something configured:
- Accept their answer and move to the next step
- Don't block on missing components
- Note what was skipped in the final summary
- Some features may not work without all components

## Error Handling

If any step fails:
- Explain what went wrong clearly
- Offer troubleshooting suggestions
- Allow user to retry or skip
- Document partial setup state

## Post-Onboarding

After onboarding completes (or is skipped), inform the user:
- What commands are available (`/ha:` prefix)
- How to reconfigure settings (`/ha:setup`)
- Where to get help
- Suggest trying `/ha:analyze` to get started
