# Connection Check Module

Shared procedure for verifying Home Assistant connectivity. Used by /ha-connect, /ha:setup, /ha:onboard, and any command that needs HA access.

> **Safety Invariant #4:** No secret material printed (no token prefixes).
> See `references/safety-invariants.md` for full details.

## Purpose

Provide a single, reusable connection verification that:
- Never prints tokens or secrets
- Works cross-platform (bash, PowerShell, Git Bash)
- Reports exactly what ran and what was verified
- Gracefully handles missing tools

## Prerequisites Check

### 1. Environment Variables

Check for standard HA environment variables:

```bash
# Primary (preferred)
echo "HASS_SERVER: ${HASS_SERVER:+configured}"
echo "HASS_TOKEN: ${HASS_TOKEN:+configured}"

# Alternatives (legacy support)
echo "HA_SERVER: ${HA_SERVER:+configured}"
echo "HA_TOKEN: ${HA_TOKEN:+configured}"
```

**Security rule:** Never echo the actual token value. Only report "configured" or "not set".

### 2. hass-cli Availability

```bash
# Check if hass-cli is installed
command -v hass-cli > /dev/null && echo "hass-cli: installed" || echo "hass-cli: not found"

# Check version
hass-cli --version 2>/dev/null || echo "version: unknown"
```

### 3. Git Availability (for deploy workflow)

```bash
command -v git > /dev/null && echo "git: installed" || echo "git: not found"
```

## Connection Test Procedure

### Step 1: Verify hass-cli Can Reach HA

Run a minimal, read-only command:

```bash
# Simple connectivity test - get HA info
hass-cli info 2>&1
```

If this fails, common causes:
- Wrong URL in HASS_SERVER
- Invalid or expired token
- Network/firewall issues
- HA not running

### Step 2: Verify Entity Access

```bash
# List a few entities to confirm API access
hass-cli state list 2>&1 | head -5
```

**Note:** Avoid `--limit` flag as it's not universally supported. Use `| head` instead.

### Step 3: Count Available Entities (Optional)

```bash
# Get entity count for user context
hass-cli state list 2>&1 | wc -l
```

## Cross-Platform Commands

### Bash / Zsh / Git Bash (Unix-like)

```bash
export HASS_SERVER="http://homeassistant.local:8123"
export HASS_TOKEN="your-token-here"
```

### PowerShell

```powershell
$env:HASS_SERVER = "http://homeassistant.local:8123"
$env:HASS_TOKEN = "your-token-here"
```

### Windows CMD

```cmd
set HASS_SERVER=http://homeassistant.local:8123
set HASS_TOKEN=your-token-here
```

## Settings File Integration

If using `.claude/settings.local.json`:

```bash
# Read settings
if [ -f ".claude/settings.local.json" ]; then
    HA_URL=$(python3 -c "import json; print(json.load(open('.claude/settings.local.json')).get('ha_url', ''))")
    TOKEN_ENV=$(python3 -c "import json; print(json.load(open('.claude/settings.local.json')).get('ha_token_env', 'HASS_TOKEN'))")
fi
```

## Output Contract

Connection check must always produce:

```markdown
## Connection Status

### Environment

| Variable | Status |
|----------|--------|
| HASS_SERVER | ✓ Configured |
| HASS_TOKEN | ✓ Configured |

### Tools

| Tool | Status | Version |
|------|--------|---------|
| hass-cli | ✓ Installed | 0.9.6 |
| git | ✓ Installed | 2.43.0 |

### Connectivity Test

| Test | Status | Details |
|------|--------|---------|
| HA Reachable | ✓ Passed | homeassistant.local:8123 |
| API Access | ✓ Passed | 142 entities available |
| Config Path | ⊘ Not configured | Optional for validation |

### Result

**Connected** - Ready to use HA Toolkit

### What Ran

1. ✓ Checked HASS_SERVER environment variable
2. ✓ Checked HASS_TOKEN environment variable
3. ✓ Ran `hass-cli info`
4. ✓ Ran `hass-cli state list | head -5`
```

## Error Handling

### Token Not Configured

```markdown
## Connection Failed

**Issue:** HASS_TOKEN not set

**Fix:** Create a Long-Lived Access Token in Home Assistant:
1. Go to your HA profile (click your name in sidebar)
2. Scroll to "Long-Lived Access Tokens"
3. Click "Create Token"
4. Set the environment variable:

**Bash/Zsh:**
```bash
export HASS_TOKEN="your-token-here"
```

**PowerShell:**
```powershell
$env:HASS_TOKEN = "your-token-here"
```
```

### Connection Refused

```markdown
## Connection Failed

**Issue:** Cannot reach Home Assistant at ${HASS_SERVER}

**Possible causes:**
- Home Assistant is not running
- Wrong URL (check http vs https, port number)
- Firewall blocking connection
- VPN required but not connected

**Debug:**
```bash
curl -s ${HASS_SERVER}/api/ -H "Authorization: Bearer ${HASS_TOKEN}"
```
```

## Integration Points

- **/ha-connect**: Primary connection setup command
- **/ha:setup**: Reconfigure existing connection
- **/ha:onboard**: Full onboarding wizard
- **/ha-deploy**: Pre-deploy connectivity check
- **/ha-validate**: Pre-validation connectivity check
