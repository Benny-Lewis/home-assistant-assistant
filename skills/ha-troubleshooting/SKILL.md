---
name: ha-troubleshooting
description: Use when user asks "why didn't X work", "not working", "debug", "check logs", mentions something "stopped working", needs to diagnose Home Assistant issues, or has device/integration problems like "unavailable", "unresponsive", device connection issues, Z-Wave/Zigbee/WiFi troubleshooting.
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash(hass-cli:*,python*,py:*)
---

# Home Assistant Troubleshooting

> **This skill is READ-ONLY.** It diagnoses issues but does not fix them.
> To apply fixes, use the appropriate generator skill (ha-automations, ha-scripts, ha-scenes)
> with proper safety guards. See the ha-resolver skill for entity verification.

> **Do NOT install packages** (`pip install`, `npm install`, etc.) without asking the user first.
> Modifying the user's environment is a side effect (Safety Invariant #5).

## Overview

Debug automations, devices, integrations, and diagnose why things didn't work. Core principle: gather data first, then analyze—never guess without evidence.

## When to Use

**Symptoms:**
- User asks "why didn't my automation trigger?"
- Something "stopped working" or "isn't working"
- User wants to "debug", "check logs", "troubleshoot"
- Automation triggered but action didn't happen
- User says "it used to work"
- Device is "unavailable", "unresponsive", or shows "unknown" state
- Integration or protocol issues (Z-Wave, Zigbee, WiFi, Matter)
- User asks for help with a specific device that isn't behaving correctly

**When NOT to use:**
- Creating new automations → use `ha-automations`
- Creating new scripts → use `ha-scripts`
- Creating new scenes → use `ha-scenes`
- Setting up a brand new device → use `ha-devices`

## Quick Reference

| Command | Purpose |
|---------|---------|
| `hass-cli state get automation.name` | Check if automation enabled |
| `MSYS_NO_PATHCONV=1 hass-cli raw get /api/error_log` | Get error logs (may 404) |
| `$PY "$PLUGIN_ROOT/helpers/trace-fetch.py" list automation.<name>` | List automation traces (see helper setup below) |
| `MSYS_NO_PATHCONV=1 hass-cli raw get "/api/history/period?filter_entity_id=X"` | Entity history |
| `MSYS_NO_PATHCONV=1 hass-cli raw get "/api/logbook?entity=X"` | Logbook events (causation chain) |

**Error log fallback:** If `/api/error_log` returns 404, try these alternatives in order:
1. `MSYS_NO_PATHCONV=1 hass-cli raw get /api/error/all` — alternative endpoint
2. Check for `home-assistant.log` in the config directory (if accessible)
3. Guide user to Settings > System > Logs in the HA web UI
4. Note in evidence table: "Error logs: unavailable via API — checked manually via UI"

## Process

1. **Identify issue** — What automation/entity/feature isn't working?
2. **Resolve entities** — Use Resolver module to verify entity_ids exist
   - Check if entities mentioned in error actually exist
   - Look for typos, renamed entities, missing integrations
3. **Gather data** — Attempt ALL five checks before moving to analysis

   > **Tip:** For complex multi-automation debugging, delegate to the ha-log-analyzer or config-debugger agent. Inline handling is fine for straightforward cases. Either way, the evidence table in step 5 is required.

   - **3a. Automation state**
     ```bash
     hass-cli state get automation.<name>
     ```
     Look for `state: on` (enabled) or `state: off` (disabled).

   - **3b. Automation traces**
     ```bash
     PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt 2>/dev/null || echo '.')"
     PY="$(cat .claude/ha-python.txt 2>/dev/null || command -v python3 || command -v python || command -v py)"
     $PY "$PLUGIN_ROOT/helpers/trace-fetch.py" list automation.<name>
     ```
     Shows trigger, conditions, actions, and variables for recent runs.
     Use `get automation.<name> <run_id>` for full trace detail.
     Note: `/api/trace` REST endpoint returns 404; `hass-cli raw ws` is broken on HA 2026.2+.

   - **3c. Error logs**
     ```bash
     MSYS_NO_PATHCONV=1 hass-cli raw get /api/error_log
     ```
     If 404, follow the fallback chain in Quick Reference above.

   - **3d. Entity history**
     ```bash
     MSYS_NO_PATHCONV=1 hass-cli raw get "/api/history/period?filter_entity_id=<entity_id>"
     ```
     Check whether the trigger entity reached the expected state.

   - **3e. Logbook events**
     ```bash
     MSYS_NO_PATHCONV=1 hass-cli raw get "/api/logbook?entity=<entity_id>"
     ```
     Shows automation triggers, state changes, and causation chains (what caused what).

   **Rule:** Do NOT skip to analysis without attempting all five checks. If a check fails or returns empty, record it in the evidence table as `✗ Failed` with the reason.

4. **Analyze** — Compare expected vs actual behavior
5. **Report with evidence** — Present findings using this ran-vs-skipped table:

   | Check | Status | Result | Evidence |
   |-------|--------|--------|----------|
   | Automation state | ✓ Ran | on/off | `state: on` from hass-cli |
   | Automation traces | ✓ Ran | triggered/not found | Trace showed condition X failed |
   | Error logs | ✗ Failed | 404 | API returned 404, checked UI instead |
   | Entity history | ✓ Ran | state reached | History shows change at HH:MM |
   | Logbook events | ✓ Ran | causation found | Logbook shows automation triggered by X |

   **Status values:** `✓ Ran` — check completed, `⊘ Skipped (reason)` — not applicable, `✗ Failed` — check errored (404, timeout, etc.)

   Every check from step 3 MUST appear in the table. Never silently omit a check.

6. **Suggest fixes** — Describe what to change, but do NOT auto-apply
   - Route to appropriate skill (ha-automations, ha-scripts, ha-scenes)
   - User must explicitly request changes

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Guessing without checking logs | Always check automation state and traces first |
| Assuming automation is enabled | Verify with `hass-cli state get` |
| Not checking entity history | Trigger entity may never have reached trigger state |
| Ignoring time/sun conditions | Check if conditions were met at the time |

## Common Issues

| Symptom | Likely Cause |
|---------|--------------|
| Automation never triggers | Wrong entity ID, automation disabled, trigger state never reached |
| Triggers but no action | Condition not met, service call error |
| Works sometimes | Time/sun condition, entity unavailable intermittently |
| Used to work | Recent config change, entity renamed, integration issue |

## Device & Integration Troubleshooting

When a device is unavailable, unresponsive, or behaving incorrectly, follow this process.

### Step 1: Check Device State

```bash
# Find all entities for the device
hass-cli state list | grep -i "<device_name>"

# Get detailed state for each entity
hass-cli state get <entity_id>
```

Look for: `state: unavailable`, `state: unknown`, or unexpected attribute values.

### Step 2: Check Integration Health

```bash
# Look up the device in the registry
hass-cli -o json device list | grep -A 5 -i "<device_name>"
```

Check: Is the device still registered? What integration owns it? Are other devices on the same integration working?

### Step 3: Protocol-Specific Checks

#### Z-Wave

- **Check node status** via the Z-Wave JS UI add-on dashboard (Settings → Add-ons → Z-Wave JS UI → Open Web UI)
- **Compare to working devices** — if other Z-Wave devices work, the issue is device-specific (range, interview, security)
- **Common causes:**
  - Device out of range (mesh too weak)
  - Failed S2 security interview — device needs exclusion and re-inclusion
  - Security class mismatch — device paired with wrong security level
  - Dead node — device lost power or hardware failure
  - Firmware issue — check for updates in Z-Wave JS UI
- **Do NOT** attempt Z-Wave websocket API operations directly — use the Z-Wave JS UI add-on dashboard for node management (interview, heal, exclude/include)
- **Re-inclusion side effects** — Excluding and re-including a Z-Wave device can cause:
  - **User codes cleared** (locks) — all programmed codes may be wiped. Back up codes via the manufacturer's app BEFORE re-inclusion
  - **Device settings reset** — parameters, associations, and configuration values may revert to factory defaults
  - **Entity IDs changed** — if HA assigns a new node ID, entity IDs may change, breaking automations that reference them
  - **Device parameters need reconfiguration** — wake-up intervals, reporting thresholds, etc.
  - Always warn the user about these risks before proceeding with Z-Wave exclusion/re-inclusion

#### Zigbee

- **Check coordinator** — is the Zigbee coordinator (ZHA/Zigbee2MQTT) running?
- **Check mesh** — devices far from coordinator with no repeaters may drop off
- **Common causes:**
  - WiFi interference (Zigbee and WiFi share 2.4GHz)
  - Battery exhaustion (sleepy end devices)
  - Channel conflict — try changing Zigbee channel
  - Device fell off mesh — re-pair the device

#### WiFi

- **Check device connectivity** — is the device on the network?
- **Common causes:**
  - IP address changed (device needs static IP or DHCP reservation)
  - WiFi signal weak (check RSSI if available)
  - Cloud service outage (for cloud-dependent integrations)
  - Firmware update changed behavior

### Step 4: Evidence Table

Present findings using this ran-vs-skipped table:

| Check | Status | Result | Evidence |
|-------|--------|--------|----------|
| Entity state | ✓ Ran | unavailable/ok | `state: unavailable` from hass-cli |
| Device registry | ✓ Ran | registered/missing | Device found in registry |
| Other devices on integration | ✓ Ran | working/also failing | Checked 3 other Z-Wave devices |
| Protocol-specific | ✓ Ran / ⊘ Skipped | details | Z-Wave JS UI checked / not applicable |
| Error logs | ✓ Ran / ✗ Failed | details | Relevant errors found / 404 |

**Status values:** `✓ Ran` — check completed, `⊘ Skipped (reason)` — not applicable, `✗ Failed` — check errored

### Common Device Issues

| Symptom | Likely Cause | First Step |
|---------|--------------|------------|
| `unavailable` state | Device offline, integration down, or communication failure | Check physical power + integration status |
| `unknown` state | Integration connected but device not reporting | Check device firmware, re-interview |
| Intermittent availability | Weak signal, interference, or flaky hardware | Check mesh/signal strength, move device closer |
| Works in UI but not automation | Entity ID mismatch, automation disabled, or condition not met | Use automation troubleshooting (above) |
| All devices on integration down | Integration or coordinator failure | Restart integration, check coordinator hardware |

## References

- `references/log-patterns.md` - Common error patterns and fixes
- `references/diagnostic-api.md` - History, Logbook, and Trace API procedures
- `references/ha-web-ui.md` - Browser automation limitations with HA's Shadow DOM
