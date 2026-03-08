#!/usr/bin/env bash
# PreToolUse guard: blocks Bash commands that would dump environment variables
# (prevents HASS_TOKEN leaks — Safety Invariant #4).
# Exit 0 = allow, Exit 2 = block (stderr shown to model).

INPUT="$(cat)"
CMD="$(echo "$INPUT" | sed -n 's/.*"command" *: *"\(.*\)".*/\1/p' | head -1)"

# Patterns that dump env vars (would expose HASS_TOKEN)
if echo "$CMD" | grep -qE '(^|\|[[:space:]]*)(\benv\b|\bprintenv\b|\bset\b|\bexport -p\b)([[:space:]]|$|\|)'; then
  echo "BLOCKED: This command would dump environment variables, risking HASS_TOKEN exposure (Safety Invariant #4). Use the safe pattern instead: printf '%s' \"\$HASS_TOKEN\" | wc -c" >&2
  exit 2
fi

exit 0
