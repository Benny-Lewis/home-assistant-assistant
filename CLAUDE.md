# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin for Home Assistant. It allows users to manage Home Assistant configurations through natural language—creating automations, scripts, scenes, and dashboards by describing what they want instead of manually editing YAML.

**Type**: Claude Code plugin (markdown-based, no build system or compiled code)

## Repository Structure

```
.claude-plugin/
  plugin.json                   # Plugin manifest
skills/                         # 15 skill directories (14 user-invocable + 1 infrastructure)
agents/                         # 6 subagent markdown files
helpers/                        # Python helper scripts for complex operations
hooks/                          # hooks.json + session-check.sh (bash)
references/                     # safety-invariants.md, settings-schema.md, hass-cli.md
templates/                      # templates.md
```

## Safety Invariants

All generated YAML and commands enforce these invariants:

1. **No unsupported attributes** - Always check `supported_features`/`supported_color_modes` before suggesting device attributes
2. **No semantic substitution** - Never replace "after no motion" (inactivity) with raw timers
3. **AST editing only** - No brittle string replacement; use Edit tool with precise old/new strings
4. **No secrets printed** - Never echo tokens; show "TOKEN is set" not the value
5. **Never auto-deploy** - All side-effectful skills require explicit user request
6. **Evidence tables** - All validation outputs show "what ran vs skipped"

## Plugin Architecture

The plugin follows Claude Code's plugin structure:

```
.claude-plugin/
  plugin.json               # Plugin manifest - metadata, component discovery
skills/
  ha-automations/           # Automation creation + domain knowledge (user-invocable)
  ha-scripts/               # Script creation + domain knowledge (user-invocable)
  ha-scenes/                # Scene creation + domain knowledge (user-invocable)
  ha-config/                # Config organization knowledge (user-invocable)
  ha-jinja/                 # Jinja templating knowledge (user-invocable)
  ha-lovelace/              # Dashboard design knowledge (user-invocable)
  ha-naming/                # Naming conventions + audit + plan (user-invocable)
  ha-apply-naming/          # Naming execution (user-invocable, NO model invocation)
  ha-devices/               # Device knowledge + new device workflow (user-invocable)
  ha-troubleshooting/       # Debugging knowledge (user-invocable)
  ha-onboard/               # Setup wizard + connection + settings (user-invocable)
  ha-deploy/                # Deploy + rollback (user-invocable, in-skill confirmation gates)
  ha-validate/              # Validation workflow + procedures (user-invocable, agent-preloadable)
  ha-analyze/               # Setup analysis + recommendations (user-invocable)
  ha-resolver/              # Entity resolution (NOT user-invocable, agent-preloaded)
agents/
  *.md                      # Subagents with specialized prompts (config-debugger,
                            # ha-config-validator, device-advisor, naming-analyzer)
hooks/
  hooks.json                # Event-driven hooks (SessionStart, PostToolUse)
references/
  safety-invariants.md      # Core safety rules referenced by all skills
  settings-schema.md        # Settings file schema
templates/
  *.md                      # Reference templates for generated configs
```

**15 skills total:** 14 user-invocable + 1 infrastructure (ha-resolver). ha-validate is both user-invocable and agent-preloadable.

## Testing

No automated tests exist. Manual testing approach:

```bash
# Load plugin for testing (from repo root)
claude --plugin-dir .
```

## Prerequisites for Plugin Users

**Local machine**:
- Git (for version control of HA configs)
- hass-cli: `pip install homeassistant-cli`

**Home Assistant**:
- Git Pull add-on (syncs configs from git repository)
- Long-Lived Access Token (for hass-cli authentication)

**Environment variables**:
```bash
export HASS_SERVER="http://homeassistant.local:8123"
export HASS_TOKEN="your-long-lived-access-token"
```

## Key Skills

| Skill | Slash Command | Description |
|-------|---------------|-------------|
| ha-onboard | `/ha-onboard` | First-time setup wizard, connection, settings |
| ha-validate | `/ha-validate` | Check configuration for errors with evidence tables |
| ha-deploy | `/ha-deploy` | Deploy changes or rollback via git |
| ha-analyze | `/ha-analyze` | Analyze setup and suggest improvements |
| ha-naming | `/ha-naming` | Naming conventions, audit, rename planning |
| ha-apply-naming | `/ha-apply-naming` | Execute a naming plan (dry-run default) |
| ha-automations | (auto) | Create automations from descriptions |
| ha-scripts | (auto) | Create scripts from descriptions |
| ha-scenes | (auto) | Create scenes from descriptions |
| ha-devices | (auto) | Device knowledge + new device workflow |
| ha-config | (auto) | Configuration organization guidance |
| ha-lovelace | (auto) | Dashboard design guidance |
| ha-jinja | (auto) | Jinja templating guidance |
| ha-troubleshooting | (auto) | Debugging and log analysis |
| ha-resolver | (agent) | Entity resolution (preloaded by agents) |

## Key Files

**Infrastructure skill (preloaded by agents):**
- `skills/ha-resolver/SKILL.md` - Entity resolution and capability snapshots

**Skill references (domain-specific):**
- `skills/ha-automations/references/intent-classifier.md` - Inactivity vs delay classification
- `skills/ha-naming/references/editor.md` - YAML AST editing procedures

## Development Notes

- Settings stored in `.claude/settings.local.json` (gitignored)
- Conventions stored in `.claude/ha.conventions.json` (user's naming patterns)
- SessionStart async hook runs env check via bash (HASS_TOKEN, HASS_SERVER, configuration.yaml, settings) and writes breadcrumb files for agent discovery
- PostToolUse Edit|Write hook reminds about /ha-deploy after config changes
- The plugin uses hass-cli for HA API operations and git for configuration deployment
- ha-apply-naming uses `disable-model-invocation: true`; ha-deploy uses in-skill confirmation gates instead
