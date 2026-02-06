#!/usr/bin/env bash
# Session start environment check for the home-assistant-assistant plugin.
# Always exits 0 — outputs plain-text diagnostics as session context.

warnings=()

# 1. Git repo check
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  warnings+=("WARNING: Current directory is not a git repository. The deploy workflow requires git. Consider navigating to your HA config repo or running 'git init'.")
fi

# 2. configuration.yaml check
if [ ! -f "configuration.yaml" ]; then
  warnings+=("WARNING: No configuration.yaml found in the current directory. This doesn't look like a Home Assistant config repo. Commands like /ha:deploy and /ha:validate expect to run from the root of your HA config directory.")
fi

# 3. HASS_TOKEN check (presence only — never print the value)
if [ -z "$HASS_TOKEN" ]; then
  warnings+=("WARNING: HASS_TOKEN is not set. hass-cli commands will fail. Run /ha:onboard to configure.")
else
  echo "HASS_TOKEN: set (${#HASS_TOKEN} chars)"
fi

# 4. HASS_SERVER check
if [ -z "$HASS_SERVER" ]; then
  warnings+=("WARNING: HASS_SERVER is not set. hass-cli commands will fail. Run /ha:onboard to configure.")
else
  echo "HASS_SERVER: $HASS_SERVER"
fi

# 5. Onboarding check
settings_file=".claude/settings.local.json"
if [ -f "$settings_file" ]; then
  echo "Settings file: found"
else
  warnings+=("NOTE: No settings file found ($settings_file). If this is your first time, run /ha:onboard to get started.")
fi

# Print warnings
if [ ${#warnings[@]} -gt 0 ]; then
  echo ""
  echo "=== Home Assistant Assistant: Session Diagnostics ==="
  for w in "${warnings[@]}"; do
    echo "  $w"
  done
  echo "====================================================="
fi

exit 0
