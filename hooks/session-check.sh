#!/usr/bin/env bash
# Session start environment check for the home-assistant-assistant plugin.
# Writes breadcrumb files (.claude/ha-python.txt, .claude/ha-plugin-root.txt) for agent discovery.

warnings=()
status=()

# 1. Git repo check
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  warnings+=("Current directory is not a git repository. The deploy workflow requires git.")
fi

# 2. configuration.yaml check
if [ ! -f configuration.yaml ]; then
  warnings+=("No configuration.yaml found. This may not be a Home Assistant config directory. Commands like /ha-deploy and /ha-validate expect to run from the HA config root.")
fi

# 3. HASS_TOKEN check (never print the value)
if [ -z "$HASS_TOKEN" ]; then
  warnings+=("HASS_TOKEN is not set. hass-cli commands will fail.")
else
  status+=("HASS_TOKEN: set (${#HASS_TOKEN} chars)")
fi

# 4. HASS_SERVER check
if [ -z "$HASS_SERVER" ]; then
  warnings+=("HASS_SERVER is not set. hass-cli commands will fail.")
else
  status+=("HASS_SERVER: $HASS_SERVER")
fi

# 5. Settings file check
if [ -f .claude/settings.local.json ]; then
  status+=("Settings file: found")
else
  warnings+=("No settings file found. If this is your first time, run /ha-onboard to get started.")
fi

# 6. Detect Python command (required by hass-cli, used for helpers)
HA_PYTHON=""
if command -v python3 &>/dev/null; then HA_PYTHON=python3
elif command -v python &>/dev/null; then HA_PYTHON=python
elif command -v py &>/dev/null; then HA_PYTHON=py
fi

# 7. Plugin root (directory containing this script's parent)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HA_PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Write breadcrumb files so agents can discover Python + plugin root
# (CLAUDE_ENV_FILE vars don't propagate to subagents)
mkdir -p .claude 2>/dev/null
[ -n "$HA_PYTHON" ] && echo "$HA_PYTHON" > .claude/ha-python.txt 2>/dev/null
echo "$HA_PLUGIN_ROOT" > .claude/ha-plugin-root.txt 2>/dev/null

# Build output
output="=== Home Assistant Assistant: Session Diagnostics ===\n"
for s in "${status[@]}"; do output+="$s\n"; done
[ -n "$HA_PYTHON" ] && output+="Python: $HA_PYTHON\n"
output+="Plugin root: $HA_PLUGIN_ROOT\n"

if [ ${#warnings[@]} -gt 0 ]; then
  output+="\nWarnings:\n"
  for w in "${warnings[@]}"; do output+="  - $w\n"; done
  # Route to /ha-onboard if critical env vars missing
  if [[ "${warnings[*]}" == *"HASS_TOKEN"* ]] || [[ "${warnings[*]}" == *"HASS_SERVER"* ]]; then
    output+="\nACTION REQUIRED: Setup is incomplete. Before handling the user's request, you MUST invoke the /ha-onboard skill to walk them through setup. Acknowledge the user's request, explain that setup needs to be completed first, then launch /ha-onboard."
  elif [[ "${warnings[*]}" == *"configuration.yaml"* ]]; then
    output+="\nACTION REQUIRED: You are NOT in a Home Assistant config directory (no configuration.yaml found). Before handling the user's request, you MUST invoke the /ha-onboard skill. It will determine whether the user already has their config checked out locally or needs to set up git from scratch."
  else
    output+="\nNote: Some non-critical warnings above. Briefly mention them to the user, then proceed with their request normally."
  fi
else
  output+="\nAll checks passed. Environment is ready."
fi

output+="\n\nPlugin skill routing:"
output+="\n  - Entity renaming/naming conventions → /ha-naming"
output+="\n  - Execute a naming plan → /ha-apply-naming"
output+="\n  - Deploy config changes → /ha-deploy"
output+="\n  - Validate config → /ha-validate"
output+="\n  - Analyze/improve setup → /ha-analyze"
output+="\n  - New device setup → /ha-devices"
output+="\n  - Create automations/scripts/scenes → /ha-automations, /ha-scripts, /ha-scenes"
output+="\n====================================================="

printf '%b' "$output"
