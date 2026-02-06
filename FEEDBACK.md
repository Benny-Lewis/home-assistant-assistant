# Plugin Testing Feedback

Collected during manual testing sessions. Each item should be actionable for implementation.

---

## Issues

### 1. No working directory / git repo detection
- **Severity**: major
- **Context**: Opened Claude in `~/dev` (a general folder, not an HA config git repo) with the plugin loaded
- **Observed**: Plugin responded normally, never flagged that the working directory isn't an HA config repo. Even spawned the entity-resolver agent and generated YAML with no mention of where it would be saved.
- **Expected**: On first interaction (or at least before any file operations), the plugin should check whether the current directory looks like an HA config repo (e.g. contains `configuration.yaml`, `.git`, etc.). If not, it should warn the user and suggest either navigating to one or setting one up.
- **Notes**: This could lead to configs being written to random locations. The plugin has a deploy flow that assumes a git repo — if there's no repo, that whole chain breaks silently.

### 2. No first-run detection / onboarding gate
- **Severity**: major
- **Context**: User said "hello can you help me with my home assistant" then "create an automation" — first-ever interaction with the plugin, nothing configured.
- **Observed**: Plugin jumped straight into automation creation. It loaded the `ha-automations` skill, resolved entities via `hass-cli` (which happened to work because env vars were set from prior manual testing), and generated YAML — all without checking whether this was a first-time user.
- **Expected**: The plugin should detect first-run state (e.g. no `.claude/ha.conventions.json`, no prior onboarding marker) and intercept before doing real work. It should guide the user through `/ha-connect` or `/ha:onboard` first: verify `hass-cli` is installed, confirm `HASS_SERVER`/`HASS_TOKEN` are set, confirm working directory is correct, explain the workflow. Only after setup is confirmed should it proceed with tasks like automation creation.
- **Notes**: In this test, `hass-cli` happened to work because env vars were already set. In a true first-run scenario it would have failed with confusing errors. The onboarding check should be a gate that all skills/commands respect, not something the user has to remember to run.

## Ideas / Future Work

<!-- Longer-term ideas that come up during testing -->
