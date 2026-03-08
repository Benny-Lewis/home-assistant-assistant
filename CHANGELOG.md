# Changelog

## 1.2.1

### Added

- **Token leak guard** — PreToolUse hook (`env-guard.sh`) blocks `env`, `printenv`, `set`, and `export -p` commands that would expose HASS_TOKEN (Safety Invariant #4)
- **Device & integration troubleshooting** — ha-troubleshooting skill now covers unavailable/unresponsive devices with Z-Wave, Zigbee, and WiFi protocol-specific diagnostics
- **HA Web UI reference** (`references/ha-web-ui.md`) — documents Shadow DOM limitations and preferred alternatives for browser automation
- Package installation added to side-effect classification table (Safety Invariant #5)

### Fixed

- **ha-analyze follow-up routing** — after analysis, the model now routes to the appropriate skill instead of editing config files directly
- **ha-deploy Git Pull timing** — no longer enters futile sleep/retry loops after push; documents Git Pull add-on polling delay and allows "Pending" verification status
- **PostToolUse hook errors** — added error suppression to prevent noisy hook failure messages
- **Parallel data collection** — ha-analyze now collects data in independent batches so one failed source doesn't cancel others

### Documentation

- ha-devices cross-references ha-troubleshooting for existing device issues
- `python3: command not found` on Windows documented in CLAUDE.md Known Environment Issues
- Safety Invariant #4 expanded with explicit bad examples for env-dumping commands

## 1.2.0

### Added

- **Diagnostic API reference** (`references/diagnostic-api.md`) — History, Logbook, and Trace API procedures for ha-troubleshooting, with command syntax, response shapes, interpretation guides, and gotchas
- **trace-fetch.py helper** — WebSocket-based trace access bypassing broken `hass-cli raw ws` (HA 2026.2+) and missing `/api/trace` REST endpoint
- **Logbook diagnostic step** — step 3e in troubleshooting process with `hass-cli raw get /api/logbook?entity=X` for causation chain analysis
- Logbook row added to all evidence table templates (SKILL.md, log-patterns.md, ha-log-analyzer.md)

### Fixed

- **Broken trace command** — `/api/trace/automation.<name>` REST endpoint returns 404 (never existed). Replaced with `trace-fetch.py` helper across SKILL.md, log-patterns.md, and ha-log-analyzer.md

## 1.1.0

### New

- **Area search helper** (`helpers/area-search.py`) — Cross-references HA entity, device, and area registries to find all entities in a room/area with a single command. Supports domain filtering and multi-area matching.
- **Template evaluation via CLI** — ha-jinja skill now includes `hass-cli raw post /api/template` patterns for testing Jinja templates against the live HA instance.

### Improved

- **Entity resolver agent** — Area-based queries (e.g., "kitchen lights") now resolve in 1 tool use instead of 15, using the new area-search helper.
- **Session hook migrated to bash** — Removes Node.js as a runtime dependency. Hook now writes breadcrumb files for reliable agent discovery across all platforms.
- **Registry commands updated** — All `hass-cli raw ws` commands replaced with built-in `-o json` commands (`area list`, `entity list`, `device list`), which are more reliable on current HA versions.
- **Domain count command fixed** — awk filter now correctly skips header rows from `state list` output.

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
5. Never deploy unless explicitly requested (explicit confirmation at every side-effectful step)
6. Evidence tables (what ran vs. skipped in all validation output)
