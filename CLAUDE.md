# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin for Home Assistant. It allows users to manage Home Assistant configurations through natural language—creating automations, scripts, scenes, and dashboards by describing what they want instead of manually editing YAML.

**Type**: Claude Code plugin (markdown-based, no build system or compiled code)

## Repository Structure

The repo contains two previously separate plugin implementations being consolidated:

```
ha-toolkit/                    # First implementation (files suffixed -ha-toolkit)
home-assistant-assistant/      # Second implementation (files suffixed -haa)
merge-plan/                    # Merge documentation and analysis
```

Both follow the same plugin architecture but have different feature sets. The merge plan documents the consolidation strategy.

## Plugin Architecture

Each plugin implementation follows Claude Code's plugin structure:

```
.claude-plugin-*/
  plugin*.json              # Plugin manifest - metadata, component discovery
skills-*/
  */SKILL*.md               # Domain knowledge (automations, scripts, scenes, config, etc.)
agents-*/
  *.md                      # Subagents with specialized prompts (entity-resolver,
                            # config-validator, log-analyzer, naming-analyzer)
commands-*/
  *.md                      # Slash commands (legacy - should migrate to skills)
hooks-*/
  hooks*.json               # Event-driven automation (YAML validation on file edits)
templates-*/
  *.md                      # Reference templates for generated configs
```

**Key architectural note**: Per Anthropic documentation, `commands/` is legacy. Skills with `user-invocable: true` frontmatter are the unified mechanism. The merged plugin should migrate all commands to skills.

## Testing

No automated tests exist. Manual testing approach:

```bash
# Load plugin for testing
claude --plugin-dir "C:\Users\blewis\dev\home-assistant-assistant\ha-toolkit"
```

See `ha-toolkit/TEST_PLAN-ha-toolkit.md` for the manual test plan covering:
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

- `merge-plan/analysis-report.md` - Compliance review against Anthropic docs (48 sections analyzed)
- `merge-plan/ha_plugins_merge_fix_plan-v4.md` - Detailed merge strategy
- `ha-toolkit/.planning-ha-toolkit/PROJECT-ha-toolkit.md` - Original project requirements
- `home-assistant-assistant/docs-haa/external-haa/` - Reference documentation for Claude Code APIs

## Development Notes

- Settings stored in `.claude/ha-toolkit.local.md` or `.claude/home-assistant-assistant.md` (gitignored)
- Hooks trigger on Edit/Write operations targeting `.yaml` files to remind users about deployment
- The plugin uses hass-cli for HA API operations and git for configuration deployment
