# Changelog

## 1.5.0

### Changed

- **Progressive-disclosure refactor** — four large SKILL.md files split into per-skill `references/*.md` so the SKILL.md becomes a tight triggering surface (frontmatter, safety banner, decision rules, workflow index) while procedural detail moves to references:
  - `ha-apply-naming` SKILL.md: 395 → 66 lines — Safety Features, 8-phase Execution Process, Post-Plan Scope Gate, Progress Reporting, and Output template moved to `references/execution.md`; Rollback and Error Handling moved to `references/recovery.md`
  - `ha-naming` SKILL.md: 517 → 84 lines — Anti-Patterns and Migration Strategy moved to `references/anti-patterns.md`; the full Audit Workflow moved to `references/audit-workflow.md`; the full Plan Workflow moved to `references/plan-workflow.md`
  - `ha-onboard` SKILL.md: 517 → 73 lines — Steps 1-8 plus Skip Behavior moved to `references/setup-steps.md`; Settings Storage schema, Reconfigure Individual Settings, and Post-Onboarding moved to `references/post-setup.md`
  - `ha-devices` SKILL.md: 587 → 71 lines — Common Integration Types moved to `references/integrations.md`; Device Categories moved to `references/device-categories.md`; Adding Devices, Entity Management, Area Organization, Device Groups, Troubleshooting, and the New Device Setup Workflow moved to `references/workflow.md`
- **ha-deploy description rewritten** — frontmatter description now front-loads explicit trigger phrases ("deploy", "push changes", "send to HA", "sync to Home Assistant", "rollback", "revert") so the skill triggers reliably on the language users actually use
- **CLAUDE.md** — added a short progressive-disclosure note listing the 10 skills that use the `references/` pattern and pointing at the Workflow Index as the navigation hook

### Fixed

- **Broken per-skill reference paths** — qualified four `references/...` mentions in ha-onboard, ha-troubleshooting, ha-lovelace, and ha-jinja as plugin-root references (they point at the repo-root `references/` directory, not a skill-local one)
- **Deprecated `version:` frontmatter** — removed the stale `version:` field from ha-config, ha-jinja, and ha-lovelace SKILL.md files
- **Missing safety-invariant banners** — added canonical banners citing the relevant invariants from `references/safety-invariants.md` to ha-jinja (#4, #8), ha-config (#4, #7, #8), and ha-analyze (#5, #6)

### Added

- **`.claude/settings.json`** — project-scoped allowlist for read-only hass-cli subcommands (`raw get`, `state list/get`, `-o json entity/area/device/state list`, `--version`) and the project eval harness invocation; narrow per-subcommand patterns only, no broad `Bash(hass-cli:*)` wildcard
- **Gitignore** — `skills/*-workspace/` added so skill-creator's throwaway eval workspaces (e.g. `ha-deploy-workspace/`) stay out of the tracked tree

## 1.4.0

### Added

- **`lovelace-dashboard.py` helper** — WebSocket helper for storage-mode dashboard operations with three subcommands: `fetch` (get dashboard config), `save-and-verify` (save with read-after-write verification), and `find-entities` (recursive entity ID extraction for preflight validation)
- **Storage Dashboard Save Contract** (BL-019) — mandatory fetch/modify/save-and-verify workflow in ha-lovelace SKILL.md with deterministic exit codes; documents that `result: null` is success, not an error
- **Sections View Mutation Rules** (BL-020) — one-section-at-a-time edit playbook with `max_columns` tuning table and `grid_options.rows` sizing table
- **Entity Preflight Validation** (BL-021) — workflow requiring all entity IDs to resolve against live HA before dashboard saves, with ha-resolver cross-reference for near-miss correction
- **Custom Card Research Workflow** (BL-022) — stable documentation lookup order: plugin reference → HACS installed resources → GitHub API → web search
- **`references/dashboard-api.md`** — WebSocket API contract reference for storage-mode dashboards
- **`skills/ha-lovelace/references/dashboard-guide.md`** — card types, layout options, grid sizing, HACS cards, and complete dashboard examples (adapted from ha-mcp)
- **Regression guards** — 9 new eval cases (REG-014 through REG-022) covering all new content

### Changed

- **ha-lovelace SKILL.md restructured** — card reference content moved to `references/dashboard-guide.md`; four new workflow sections added; `allowed-tools` expanded to include `Bash(hass-cli:*,python*,py:*)`; version bumped to 0.2.0

## 1.3.3

### Documentation

- **Automation entity ID derivation** (BL-006) — documented that HA derives entity IDs from the `alias` field (not the `id` field) in ha-automations, yaml-syntax reference, and ha-resolver, with derivation rules, examples, and correct/incorrect lookup commands
- **Mid-sequence condition gates** (BL-014) — documented that conditions placed within action sequences gate only subsequent actions (earlier actions still run), with YAML examples in ha-automations and yaml-syntax reference
- **Regression guards** — added REG-012 (alias derivation) and REG-013 (mid-sequence conditions) eval cases
- **Backlog entries** — added BL-017 (`common-patterns.md` deprecated syntax) and BL-018 (`--no-headers` with `service list`)

## 1.3.2

### Fixed

- **Block `hass-cli raw ws` at the hook level** — PreToolUse guard now blocks `hass-cli raw ws` commands (broken on HA 2026.2+) before they execute, preventing wasted tool calls and retry cascades. The block message directs to `hass-cli -o json` built-in commands and Python websocket helpers.
- **Eval coverage** — added CAP-009 regression guard verifying the `hass-cli raw ws` block remains in env-guard.sh

## 1.3.1

### Fixed

- **Self-hosted marketplace source resolution** - switched the single-plugin marketplace entry to `source: "./"` so Claude installs the plugin from the marketplace checkout instead of recursively repackaging the marketplace repo into the plugin cache on local-scope installs and updates

## 1.3.0

### Added

- **`ha-overview.py` helper** - `/ha-analyze` now has a stdlib-only overview helper that returns exact JSON metrics plus source availability for live HA and local config data

### Fixed

- **`ha-analyze` evidence contract** - analysis guidance now requires exact counts, an evidence table, explicit inference labeling, and single-skill follow-up routing instead of inline mutation
- **Trace timestamp rendering** - `trace-fetch.py` now keeps timezone offsets in rendered timestamps so analysis and troubleshooting flows do not silently present UTC as local time
- **Regression coverage for analysis reliability** - evals now guard against approximate metrics, missing evidence tables, direct mutation from analysis, unstable overview output, and timezone loss

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
