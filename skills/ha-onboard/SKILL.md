---
name: ha-onboard
description: Use when user needs to set up their Home Assistant connection, configure settings, install prerequisites, or mentions "onboard", "setup", "connect", "configure".
user-invocable: true
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion, Glob, Grep
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

**Run this script exactly as written (multi-line, not reformatted). Wait for the results before deciding which step to present. Do NOT run any step content until resume detection is complete.**

```bash
# Check all environment signals
[ -f "configuration.yaml" ] && echo "HAS_CONFIG" || echo "NO_CONFIG"
REMOTE=$(git remote -v 2>/dev/null | head -1)
echo "${REMOTE:-NO_GIT_REMOTE}"
hass-cli --version 2>/dev/null || echo "NO_HASS_CLI"
TLEN=$(printf '%s' "$HASS_TOKEN" | wc -c); echo "TOKEN_LEN=$TLEN"
echo "SERVER=${HASS_SERVER:-UNSET}"
```

Use this decision table to skip to the right step:

| Signal | Meaning | Skip to |
|--------|---------|---------|
| `NO_CONFIG` + `NO_HASS_CLI` + `TOKEN_LEN=0` | Fresh start | Step 1 |
| `NO_CONFIG` + hass-cli or `TOKEN_LEN>0` | Wrong directory | Ask user for config path (see below) |
| `HAS_CONFIG` + no git remote | Config dir, no git | Step 2 |
| `HAS_CONFIG` + git remote + `NO_HASS_CLI` | Git done, need CLI | Step 5 |
| `HAS_CONFIG` + git remote + hass-cli + `TOKEN_LEN=0` or `SERVER=UNSET` | Need connection | Step 6 |
| `HAS_CONFIG` + git remote + hass-cli + `TOKEN_LEN>0` + server set | All local setup done | Step 7 |

**Wrong-directory handling:** Do NOT run Step 1 checks (OS, git, Python detection) — the user's tools are already installed. Ask: "I see you have [hass-cli / a token / both] set up, but there's no `configuration.yaml` here. Do you have your HA config cloned somewhere else?" If YES → ask for the path, verify it contains `configuration.yaml`, then tell them to restart Claude Code from that directory (Step 4 logic). If NO → start at Step 2 (Git Setup on Home Assistant) since they need to clone their config first.

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

## Workflow Index

Full procedural content lives in per-skill references:

- `references/setup-steps.md` — the 8-step wizard procedure (environment detection, git setup on HA, local clone, restart gate, hass-cli install, connection setup with platform-specific env var guidance, Git Pull add-on, verification tests) plus Skip Behavior
- `references/post-setup.md` — Settings Storage schema for `.claude/settings.local.json`, the Reconfigure Individual Settings flow (connection / config_path / git_remote / git_branch / conventions) with Quick Update Mode, and the post-onboarding message
- `references/settings-schema.md` (plugin root, not skill-local) — full settings schema reference
