---
# Home Assistant connection
ha_url: "http://homeassistant.local:8123"

# Deploy behavior
auto_deploy: false
auto_commit: true
auto_push: true
auto_reload: true
commit_prefix: ""

# Validation
validate_on_edit: true
validate_on_deploy: true

# Creation workflow
skip_entity_confirmation: false
check_conflicts: true

# Troubleshooting
log_history_hours: 24

# Rollback
history_count: 5

# File locations
automations_file: "automations.yaml"
scripts_file: "scripts.yaml"
scenes_file: "scenes.yaml"

# Safety
create_backup: false

# Convention settings (populated by /ha-conventions)
# Run /ha-conventions to auto-detect from your existing config
conventions:
  # Naming rules (more robust than single pattern string)
  separator: "_"                    # "_" or "-"
  case: "snake_case"                # snake_case, kebab-case
  area_position: "prefix"           # prefix or suffix
  condition_prefix: "if_"           # How conditions are marked in IDs

  # Computed patterns (derived from rules above)
  automation_id_pattern: "<area>_<trigger>_[if_<condition>]_<action>"
  automation_alias_pattern: "<Area>: <Trigger> [If <Condition>] → <Action>"
  timer_naming: "<area>_<purpose>"

  # Behavior preferences
  use_timer_helpers: true           # Use timer helpers instead of inline delay:
  timer_threshold_seconds: 30       # Use timers for delays > this value
  default_automation_mode: "single" # single, restart, queued, parallel
  enforce_conventions: false        # Strict mode: refuse to generate non-compliant YAML

  # Detection metadata (set by /ha-conventions)
  detected_from_existing: false     # true if auto-detected from your config
  last_detected: null               # ISO date of last detection
  confidence: null                  # high, medium, low, or null

  # Examples (stored for pattern matching reference)
  examples: []
---
