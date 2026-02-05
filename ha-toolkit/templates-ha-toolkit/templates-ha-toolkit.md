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
---
