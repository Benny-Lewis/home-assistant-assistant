---
name: ha-connect
description: Set up connection to Home Assistant instance
---

# Home Assistant Connection Setup

> **Safety Invariant #4:** Never print or echo tokens/secrets.
> Check presence only, never display values.

Guide the user through connecting to their Home Assistant instance.

## Prerequisites Check

First, check if hass-cli is installed:

**Bash/Git Bash:**
```bash
hass-cli --version
```

**PowerShell:**
```powershell
hass-cli --version
```

If not installed, guide user:
"hass-cli is required but not installed.

Install it with:
  pip install homeassistant-cli

Then run /ha-connect again."

## Check Existing Configuration

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

## Setup Flow

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

   ⚠️ **Do not paste the token here.** Instead, set it as an environment variable.
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
   Settings → System → About → Advanced system settings → Environment Variables
   Add HASS_TOKEN and HASS_SERVER as User variables"

4. **After user confirms setup, validate connection:**
   ```bash
   hass-cli state list | head -5
   ```

5. **If successful, show summary:**
   "✅ Connection successful!

   Your Home Assistant at <url>:
   - [count] entities found
   - [count] automations
   - [count] scripts
   - [count] scenes

   You can now ask me to create automations, troubleshoot issues,
   or manage your Home Assistant config."

6. **If connection fails, show troubleshooting:**
   "❌ Couldn't connect. Common issues:
   - Is Home Assistant running?
   - Are you on the same network?
   - Is HASS_SERVER set correctly?
   - Is the token valid (not expired)?

   Check token is set (but don't show it!):
   `[ -n "$HASS_TOKEN" ] && echo "Token set" || echo "Token not set"`

   Want to try a different URL?"

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| HASS_TOKEN | Long-lived access token | (secret) |
| HASS_SERVER | Home Assistant URL | http://homeassistant.local:8123 |

## Security Notes

- **Never echo tokens** - check presence only
- **Never commit tokens to git** - use environment variables
- Tokens can be revoked in HA → Profile → Long-Lived Access Tokens
