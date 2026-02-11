# Component Reference

Full reference for all plugin components. For a quick overview, see [README.md](README.md).

## Components

| Component | Count |
|-----------|-------|
| Skills | 15 |
| Agents | 6 |
| Hooks | 2 |

## Skills

Skills are the core of the plugin. 14 are user-invocable (you can ask for them directly), 1 is infrastructure (preloaded by agents).

### Setup & Deployment (3)

| Skill | Description | Tools |
|-------|-------------|-------|
| `ha-onboard` | First-time setup wizard — walks through hass-cli install, token creation, environment variables, HA connection, and git-based deployment config | Read, Bash, AskUserQuestion, Glob, Grep |
| `ha-deploy` | Deploy config changes to HA via git commit + push + reload, or rollback to a previous commit. Confirmation gate before every side-effectful step | Read, Write, Bash, AskUserQuestion, Glob |
| `ha-validate` | Validate configuration files with progressive tiers — YAML syntax, HA schema, entity existence, service validation. Outputs evidence tables showing what ran vs. skipped | Read, Bash, Glob, Grep, AskUserQuestion |

`ha-validate` is also agent-preloadable — agents like `ha-config-validator` load it automatically.

### Config Generation (3)

| Skill | Description | Tools |
|-------|-------------|-------|
| `ha-automations` | Create automations from natural language descriptions. Classifies intent (inactivity vs. delay), resolves entities, checks capabilities, generates HA 2024+ trigger/condition/action YAML | Read, Grep, Glob, Edit, Bash(hass-cli), AskUserQuestion |
| `ha-scripts` | Create scripts with sequences, modes (single/restart/queued/parallel), fields, and proper action syntax | Read, Grep, Glob, Edit, Bash(hass-cli), AskUserQuestion |
| `ha-scenes` | Create scenes with device capability verification — checks `supported_features` and `supported_color_modes` before emitting any device attributes | Read, Grep, Glob, Edit, Bash(hass-cli), AskUserQuestion |

### Naming & Organization (2)

| Skill | Description | Tools |
|-------|-------------|-------|
| `ha-naming` | Audit naming patterns across entities, suggest conventions, and generate rename plans. Plans are saved to `.claude/naming-plan.yaml` | Read, Write, Bash, Glob, Grep, AskUserQuestion |
| `ha-apply-naming` | Execute a naming plan — rename entities via hass-cli and update all YAML references. Dry-run by default. **No model invocation** (`disable-model-invocation: true`) — executes the plan mechanically | Read, Bash, Glob, Grep, AskUserQuestion |

### Analysis & Troubleshooting (2)

| Skill | Description | Tools |
|-------|-------------|-------|
| `ha-analyze` | Analyze your HA setup and provide improvement suggestions — unused entities, missing automations, config organization, security | Read, Bash, Glob, Grep, AskUserQuestion |
| `ha-troubleshooting` | Debug HA issues — log analysis, automation trace inspection, entity state checking, common error patterns | Read, Grep, Glob, Bash(hass-cli) |

### Domain Knowledge (4)

These skills provide reference knowledge and activate automatically when you ask about their domain:

| Skill | Description | Tools |
|-------|-------------|-------|
| `ha-config` | Configuration file structure — `configuration.yaml`, packages, includes, `secrets.yaml`, splitting and organizing config files | Read, Grep, Glob |
| `ha-lovelace` | Dashboard design — card types, views, layouts, themes, conditional cards, custom components | Read, Grep, Glob |
| `ha-jinja` | Jinja2 templating — template sensors, `value_template`, `state_attr()`, `states()`, filters, and debugging | Read, Grep, Glob |
| `ha-devices` | Device and integration knowledge — device types, setup workflows, Zigbee/Z-Wave/WiFi, entity relationships | Read, Grep, Glob, Bash, AskUserQuestion, Task |

### Infrastructure (1)

| Skill | Description | Tools |
|-------|-------------|-------|
| `ha-resolver` | Entity resolution and capability snapshots. Resolves natural names ("kitchen lights") to entity IDs, captures `supported_features`/`supported_color_modes`. **Not user-invocable** — preloaded by agents | Bash(hass-cli) |

### Skill Reference Files

Some skills include reference subdirectories with domain-specific knowledge:

| File | Used by | Content |
|------|---------|---------|
| `skills/ha-automations/references/intent-classifier.md` | ha-automations | Inactivity vs. delay pattern classification |
| `skills/ha-automations/references/common-patterns.md` | ha-automations | Common automation patterns (motion lights, schedules, notifications) |
| `skills/ha-automations/references/yaml-syntax.md` | ha-automations | HA 2024+ automation YAML syntax reference |
| `skills/ha-scripts/references/yaml-syntax.md` | ha-scripts | Script YAML syntax reference |
| `skills/ha-scenes/references/yaml-syntax.md` | ha-scenes | Scene YAML syntax reference |
| `skills/ha-naming/references/editor.md` | ha-naming | Safe YAML AST editing procedures |
| `skills/ha-naming/references/naming-conventions.md` | ha-naming | HA naming convention patterns |
| `skills/ha-troubleshooting/references/log-patterns.md` | ha-troubleshooting | Common HA error patterns and resolutions |

## Agents

Agents are subagents launched via the Task tool for deeper analysis. They run in their own context and return results.

### Debugging (2)

| Agent | Description | Tools | Preloaded Skills |
|-------|-------------|-------|------------------|
| `config-debugger` | Debug configuration errors — analyzes files, interprets error messages, traces automation logic, provides specific fixes | Read, Glob, Grep, Bash | ha-resolver, ha-validate |
| `ha-log-analyzer` | Analyze HA logs and automation traces — gathers logs via hass-cli, identifies errors, correlates events | Bash, Read, Grep | — |

### Validation (1)

| Agent | Description | Tools | Preloaded Skills |
|-------|-------------|-------|------------------|
| `ha-config-validator` | Deep configuration validation — runs progressive validation tiers before deployment | Bash, Read, Grep | ha-validate |

### Entity & Device (2)

| Agent | Description | Tools | Preloaded Skills |
|-------|-------------|-------|------------------|
| `ha-entity-resolver` | Find and validate entity IDs with capability snapshots — searches by name, room, or type | Bash, Read | ha-resolver |
| `device-advisor` | New device setup guidance — naming, capability discovery, automation suggestions, dashboard integration | Read, Glob, Grep, Bash, AskUserQuestion | ha-resolver |

### Naming (1)

| Agent | Description | Tools | Preloaded Skills |
|-------|-------------|-------|------------------|
| `naming-analyzer` | Deep naming pattern analysis — audits inconsistencies, recommends conventions, traces entity dependencies | Read, Glob, Grep, Bash | — |

## Hooks

Hooks fire automatically in response to plugin events.

| Event | Type | What it does |
|-------|------|-------------|
| `SessionStart` | async command | Runs `session-check.js` on every new session. Checks for `HASS_TOKEN`, `HASS_SERVER`, `configuration.yaml`, and settings file. Warns if anything is missing. Timeout: 10s |
| `PostToolUse` (Edit\|Write) | sync command | After any file edit or write, reminds about `ha-deploy` for validation and deployment. Timeout: 5s |

## Plugin References

Shared reference documents used across skills and agents:

| File | Description |
|------|-------------|
| `references/safety-invariants.md` | The 6 safety invariants enforced across all components |
| `references/settings-schema.md` | Schema for `.claude/settings.local.json` |
| `references/hass-cli.md` | hass-cli command reference |
| `templates/templates.md` | Reference templates for generated configurations |

## Safety Invariants

Every skill, agent, and hook enforces these rules (detailed in `references/safety-invariants.md`):

1. **No unsupported attributes** — checks `supported_features`/`supported_color_modes` before emitting device attributes
2. **No semantic substitution** — distinguishes "after no motion" (inactivity) from "wait 5 minutes" (delay)
3. **AST editing only** — no brittle string replacement; uses precise context-aware edits
4. **No secrets printed** — never echoes tokens or API keys
5. **Never auto-deploy** — all side-effectful actions require explicit confirmation
6. **Evidence tables** — all validation output shows what ran vs. what was skipped
