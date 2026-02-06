# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin for Home Assistant. It allows users to manage Home Assistant configurations through natural language—creating automations, scripts, scenes, and dashboards by describing what they want instead of manually editing YAML.

**Type**: Claude Code plugin (markdown-based, no build system or compiled code)

## Repository Structure

```
home-assistant-assistant/      # The plugin (load with --plugin-dir)
merge-plan/                    # Merge documentation and progress tracking
references/                    # Development references (yaml-syntax, frontmatter-compliance)
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
home-assistant-assistant/
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
    ha-deploy/                # Deploy + rollback (user-invocable, NO model invocation)
    ha-validate/              # Validation workflow + procedures (user-invocable, agent-preloadable)
    ha-analyze/               # Setup analysis + recommendations (user-invocable)
    ha-resolver/              # Entity resolution (NOT user-invocable, agent-preloaded)
  agents/
    *.md                      # Subagents with specialized prompts (config-debugger,
                              # ha-config-validator, device-advisor, naming-analyzer)
  hooks/
    hooks.json                # Event-driven hooks (SessionStart, PreToolUse, PostToolUse)
  references/
    safety-invariants.md      # Core safety rules referenced by all skills
    settings-schema.md        # Settings file schema
  templates/
    *.md                      # Reference templates for generated configs
```

**15 skills total:** 13 user-invocable + 1 infrastructure (ha-resolver) + 1 user-invocable-and-agent-preloaded (ha-validate)

## Testing

No automated tests exist. Manual testing approach:

```bash
# Load plugin for testing
claude --plugin-dir "C:\Users\blewis\dev\home-assistant-assistant\home-assistant-assistant"
```

See `home-assistant-assistant/TEST_PLAN.md` for the manual test plan covering:
- Plugin loading verification
- Skill testing (user-invocable and domain)
- Agent testing scenarios
- Hook testing
- Safety invariant regression tests

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
| ha-onboard | `/ha:onboard` | First-time setup wizard, connection, settings |
| ha-validate | `/ha:validate` | Check configuration for errors with evidence tables |
| ha-deploy | `/ha:deploy` | Deploy changes or rollback via git |
| ha-analyze | `/ha:analyze` | Analyze setup and suggest improvements |
| ha-naming | `/ha:naming` | Naming conventions, audit, rename planning |
| ha-apply-naming | `/ha:apply-naming` | Execute a naming plan (dry-run default) |
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

**Merge documentation:**
- `merge-plan/PROGRESS.md` - 61-item checklist (all complete)
- `merge-plan/ha_plugins_merge_fix_plan-v4.md` - Detailed merge strategy
- `merge-plan/analysis-report.md` - Compliance review against Anthropic docs

**Infrastructure skill (preloaded by agents):**
- `skills/ha-resolver/SKILL.md` - Entity resolution and capability snapshots

**Skill references (domain-specific):**
- `skills/ha-automations/references/intent-classifier.md` - Inactivity vs delay classification
- `skills/ha-naming/references/editor.md` - YAML AST editing procedures

**Testing:**
- `home-assistant-assistant/TEST_PLAN.md` - Manual test plan with safety invariant tests

**Development references (repo root):**
- `references/yaml-syntax.md` - HA 2024+ YAML schema (triggers/conditions/actions)
- `references/frontmatter-compliance.md` - Anthropic plugin spec compliance

## Development Notes

- Settings stored in `.claude/settings.local.json` (gitignored)
- Conventions stored in `.claude/ha.conventions.json` (user's naming patterns)
- SessionStart async hook runs env check via node (HASS_TOKEN, HASS_SERVER, configuration.yaml, settings)
- PreToolUse Edit|Write prompt hook reminds about /ha:deploy after config changes
- PostToolUse hooks validate YAML structure after file edits
- The plugin uses hass-cli for HA API operations and git for configuration deployment
- Skills with side effects have `disable-model-invocation: true` in frontmatter
