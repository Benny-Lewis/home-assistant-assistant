#!/usr/bin/env bash
# PreToolUse guard for Bash commands.
# - Blocks env dumps that would expose HASS_TOKEN (Safety Invariant #4)
# - Blocks hass-cli raw ws which is broken on HA 2026.2+
# Exit 0 = allow, Exit 2 = block (stderr shown to model).

INPUT="$(cat)"
CMD="$(echo "$INPUT" | sed -n 's/.*"command" *: *"\(.*\)".*/\1/p' | head -1)"

# Patterns that dump env vars (would expose HASS_TOKEN)
if echo "$CMD" | grep -qE '(^|\|[[:space:]]*)(\benv\b|\bprintenv\b|\bset\b|\bexport -p\b)([[:space:]]|$|\|)'; then
  echo "BLOCKED: This command would dump environment variables, risking HASS_TOKEN exposure (Safety Invariant #4). Use the safe pattern instead: printf '%s' \"\$HASS_TOKEN\" | wc -c" >&2
  exit 2
fi

# hass-cli raw ws is broken on HA 2026.2+ (returns "Unknown command" for all message types)
if echo "$CMD" | grep -qE 'hass-cli[[:space:]]+raw[[:space:]]+ws'; then
  echo "BLOCKED: hass-cli raw ws is broken on HA 2026.2+ — returns 'Unknown command' for all message types. Use hass-cli -o json built-in commands (entity list, area list, device list) or Python websocket helpers instead." >&2
  exit 2
fi

exit 0
