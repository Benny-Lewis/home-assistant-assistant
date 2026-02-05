---
name: ha-connect
description: Set up connection to Home Assistant instance
---

# Home Assistant Connection Setup

Guide the user through connecting to their Home Assistant instance.

## Prerequisites Check

First, check if hass-cli is installed:
```bash
hass-cli --version
```

If not installed, guide user:
"hass-cli is required but not installed.

Install it with:
  pip install homeassistant-cli

Then run /ha-connect again."

## Check Existing Configuration

Check if HA_TOKEN is already set:
```bash
echo $HA_TOKEN | head -c 10
```

If set, ask: "Found existing HA_TOKEN. Do you want to reconfigure?"

## Setup Flow

1. Welcome message:
   "Let's connect to your Home Assistant! This is a one-time setup.

   I'll need two things:
   - An access token (like a password for the API)
   - Your Home Assistant's URL"

2. Guide user to get token:
   "Open your Home Assistant web interface and go to:
   Profile (bottom left) > Long-Lived Access Tokens > Create Token

   Give it a name like 'Claude Code' and click Create.

   Important: Copy the token now - HA only shows it once!

   Paste your token here:"

3. After user pastes token, detect shell and add to config:
   - Check $SHELL for zsh or bash
   - Add to appropriate config file (~/.zshrc or ~/.bashrc):
     ```bash
     export HA_TOKEN="<token>"
     export HASS_TOKEN="$HA_TOKEN"
     ```
   - Source the file

4. Ask for URL:
   "Now I need your Home Assistant URL. This is usually something like:
   - http://homeassistant.local:8123 (default)
   - http://192.168.1.100:8123 (IP address)

   What's your Home Assistant URL?"

5. Add URL to shell config:
   ```bash
   export HA_URL="<url>"
   export HASS_SERVER="$HA_URL"
   ```

6. Validate connection:
   ```bash
   hass-cli state list | head -5
   ```

7. If successful, show summary:
   "Setup complete!

   Your Home Assistant at <url>:
   - [count] entities
   - [count] automations
   - [count] scripts
   - [count] scenes

   You can now ask me to create automations, troubleshoot issues,
   or manage your Home Assistant config."

8. If connection fails, show troubleshooting:
   "Couldn't connect. Common issues:
   - Is Home Assistant running?
   - Are you on the same network?
   - Is the URL correct?

   Want to try a different URL?"
