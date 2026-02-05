# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin for Home Assistant. It allows users to manage Home Assistant configurations through natural language—creating automations, scripts, scenes, and dashboards by describing what they want instead of manually editing YAML.

**Type**: Claude Code plugin (markdown-based, no build system or compiled code)

## Repository Structure

```
home-assistant-assistant/      # The plugin (load with --plugin-dir)
merge-plan/                    # Merge documentation and progress tracking
references/                    # Shared reference documentation
modules/                       # Shared procedures (resolver, editor, validator)
```

**Status:** The 61-item merge plan is complete. The `home-assistant-assistant/` folder contains the consolidated, safety-hardened implementation.

## Safety Invariants

All generated YAML and commands enforce these invariants:

1. **No unsupported attributes** - Always check `supported_features`/`supported_color_modes` before suggesting device attributes
2. **No semantic substitution** - Never replace "after no motion" (inactivity) with raw timers
3. **AST editing only** - No brittle string replacement; use Edit tool with precise old/new strings
4. **No secrets printed** - Never echo tokens; show "TOKEN is set ✓" not the value
5. **Never auto-deploy** - All side-effectful commands require explicit user request
6. **Evidence tables** - All validation outputs show "what ran vs skipped"

## Plugin Architecture

The plugin follows Claude Code's plugin structure:

```
home-assistant-assistant/
  .claude-plugin/
    plugin.json               # Plugin manifest - metadata, component discovery
  skills/
    */SKILL*.md               # Domain knowledge (automations, scripts, scenes, config, etc.)
  agents/
    *.md                      # Subagents with specialized prompts (entity-resolver,
                              # config-validator, log-analyzer, naming-analyzer)
  commands/
    *.md                      # Slash commands (legacy - should migrate to skills)
  hooks/
    hooks.json                # Event-driven automation (YAML validation on file edits)
  templates/
    *.md                      # Reference templates for generated configs
```

**Key architectural note**: Per Anthropic documentation, `commands/` is legacy. Skills with `user-invocable: true` frontmatter are the unified mechanism. The merged plugin should migrate all commands to skills.

## Testing

No automated tests exist. Manual testing approach:

```bash
# Load plugin for testing
claude --plugin-dir "C:\Users\blewis\dev\home-assistant-assistant\home-assistant-assistant"
```

See `home-assistant-assistant/TEST_PLAN.md` for the manual test plan covering:
- Plugin loading verification
- Command testing procedures
- Skill trigger testing
- Agent testing scenarios
- Hook testing

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

## Key Commands (Current)

| Command | Description |
|---------|-------------|
| `/ha-connect` or `/ha:onboard` | First-time setup wizard |
| `/ha:generate <type>` | Generate YAML (automation, scene, script, dashboard) |
| `/ha:validate` | Check configuration for errors |
| `/ha-deploy` or `/ha:deploy` | Push changes to Home Assistant via git |
| `/ha-rollback` | Revert to previous configuration |
| `/ha:audit-naming` | Analyze naming consistency |
| `/ha:new-device` | Guided workflow for new devices |

## Key Files

**Merge documentation:**
- `merge-plan/PROGRESS.md` - 61-item checklist (all complete)
- `merge-plan/ha_plugins_merge_fix_plan-v4.md` - Detailed merge strategy
- `merge-plan/analysis-report.md` - Compliance review against Anthropic docs

**Core modules:**
- `modules/resolver.md` - Entity resolution and capability snapshots
- `modules/editor.md` - YAML AST editing procedures
- `modules/validator.md` - Evidence-based validation
- `modules/intent-classifier.md` - Inactivity vs delay classification

**Testing:**
- `home-assistant-assistant/TEST_PLAN.md` - Manual test plan with safety invariant tests

**References:**
- `references/yaml-syntax.md` - HA 2024+ YAML schema (triggers/conditions/actions)
- `references/log-patterns.md` - Common error patterns and fixes

## Development Notes

- Settings stored in `.claude/settings.local.json` (gitignored)
- Conventions stored in `.claude/ha.conventions.json` (user's naming patterns)
- Hooks trigger on Edit/Write operations targeting `.yaml` files to remind users about deployment
- The plugin uses hass-cli for HA API operations and git for configuration deployment
- All commands with side effects have `disable-model-invocation: true` in frontmatter
