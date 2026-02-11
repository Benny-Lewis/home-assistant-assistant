# Changelog

## 1.0.0

Initial public release.

### Skills (15 total)

**User-invocable slash commands (6):**
- `/ha-onboard` — First-time setup wizard, connection verification, settings configuration
- `/ha-validate` — Configuration validation with evidence tables
- `/ha-deploy` — Git-based deploy and rollback with confirmation gates
- `/ha-analyze` — Setup analysis and improvement recommendations
- `/ha-naming` — Naming convention audit and rename planning
- `/ha-apply-naming` — Naming plan execution (dry-run by default, no model invocation)

**Domain knowledge skills (8):**
- ha-automations — Automation creation with trigger/condition/action patterns
- ha-scripts — Script sequences, modes, and fields
- ha-scenes — Scene creation with device capability verification
- ha-config — Configuration structure, packages, secrets management
- ha-lovelace — Dashboard design, card types, layouts
- ha-jinja — Jinja template syntax and patterns
- ha-devices — Device types, integrations, new device workflows
- ha-troubleshooting — Log analysis, debugging, common error patterns

**Infrastructure (1):**
- ha-resolver — Entity resolution preloaded by agents

### Agents (6)

- config-debugger — Analyzes and fixes configuration errors
- ha-config-validator — Deep configuration validation
- ha-entity-resolver — Entity resolution for other agents
- ha-log-analyzer — Home Assistant log analysis
- device-advisor — Device setup recommendations
- naming-analyzer — Naming pattern analysis

### Hooks

- SessionStart — async environment check (HASS_TOKEN, HASS_SERVER, configuration.yaml, settings)
- PostToolUse (Edit|Write) — reminds about `/ha-deploy` after config file changes

### Safety Invariants

Six enforced invariants across all skills, agents, and hooks:
1. No unsupported attributes (capability-checked YAML generation)
2. No semantic substitution (inactivity vs. delay classification)
3. AST editing only (no brittle string replacement)
4. No secrets printed (token presence only, never values)
5. Never auto-deploy (explicit confirmation at every side-effectful step)
6. Evidence tables (what ran vs. skipped in all validation output)
