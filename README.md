# home-assistant-assistant

A Claude Code plugin that lets you setup and manage your Home Assistant through natural language. Describe what you want — "turn off the kitchen lights after 5 minutes of no motion" — and the plugin resolves entity names against your real HA instance, checks device capabilities, generates YAML, validates everything, and deploys to your Home Assistant via git after your confirmation.

## Quick Start

Install thke plugin. In Claude Code: 
```
/plugin marketplace add Benny-Lewis/home-assistant-assistant
/plugin install home-assistant-assistant@home-assistant-assistant
```

Launch the onboarding wizard:
```
/ha-onboard
```

The onboarding wizard walks you through hass-cli installation, token setup, git configuration, and HA connection — one step at a time. It will save progress if you need to stop halfway.

## How It Works

You run Claude Code from a directory containing a clone of your Home Assistant configuration. When you make a request, such as a new automation, scene, or script, the plugin resolves your natural language to actual entity IDs by querying your HA instance through `hass-cli`. It pulls a capability snapshot for every device it touches and refuses to emit attributes a device doesn't support. If you say "warm white" for a brightness-only bulb, it stops and asks what you'd like to do instead. When your config is ready, it validates across progressive tiers (YAML syntax, HA schema, entity existence, service verification) and deploys via git commit, push, and HA reload — with explicit confirmation at every step. The entire workflow, from "make the porch lights come on at sunset" to a deployed, running automation, happens in a single conversation.

## Examples

### Build an automation from a sentence
```
> When no motion is detected in the hallway for 10 minutes, turn off the lights and set the thermostat to 67 degrees
```

The plugin classifies this as an inactivity pattern (not a delay — the distinction matters), finds actual entity names `binary_sensor.hallway_motion` and `light.hallway` on your HA machine using hass-cli, verifies the thermostat supports `set_temperature`, and generates YAML like this:

```yaml
- alias: "Hallway lights off on no motion"
  id: hallway_lights_off_no_motion
  trigger:
    - trigger: state
      entity_id: binary_sensor.hallway_motion
      to: "off"
      for: "00:10:00"
  action:
    - action: light.turn_off
      target:
        entity_id: light.hallway
    - action: climate.set_temperature
      target:
        entity_id: climate.hallway_thermostat
      data:
        temperature: 67
```

The `for: "00:10:00"` on the trigger is the key detail. If motion resumes before 10 minutes, the trigger resets automatically — no extra cancel logic needed. Claude then asks for your review before commiting the update to git and deploying it to your Home Assistant.

---

### Audit and fix entity naming:
```
> "Audit my entity names"
```

Claude runs `/ha-naming`, which scans every entity, automation, script, and scene. It detects your dominant naming pattern and flags inconsistencies — mixed casing, missing area prefixes, `sensor_1` sitting next to `living_room_temperature`. It writes a rename plan to `.claude/naming-plan.yaml` with dependency analysis: which automations, scripts, scenes, and dashboards reference each entity that would be renamed.

It asks you to review the plan, remove any renames you don't want, and then runs `/ha-apply-naming`. It executes the plan with a dry-run preview first, updating every reference across your configuration files. The two-step design means you always see exactly what will change before it changes.

---

### Debug a broken automation:
```
> Why didn't my kitchen motion light trigger last night?
```
The troubleshooting skill checks automation state, pulls traces, queries error logs, and examines entity history. It builds an evidence table — a row-by-row accounting of what was checked, what passed, what failed, and what was skipped. If the root cause is a misconfigured trigger, a renamed entity, or a state that never fires, it shows you the evidence and offers a fix with deployment.

---

### Design a dashboard
```
> Create a climate dashboard with temperature and humidity for each room
```

Resolves your climate sensors against the live instance, checks which attributes each one actually exposes (not every sensor reports humidity), and generates Lovelace card YAML that matches your real hardware. No placeholder entity IDs, no attributes your devices don't support.

## Skills

| Skill | What it does |
|-------|-------------|
| `/ha-onboard` | First-time setup wizard with resume detection |
| `/ha-automations` | Create automations with intent classification and entity resolution |
| `/ha-scripts` | Create reusable action sequences with mode selection |
| `/ha-scenes` | Create device presets with capability verification |
| `/ha-validate` | Progressive validation: YAML syntax, schema, entity existence, services |
| `/ha-deploy` | Git-based deploy and rollback with confirmation gates |
| `/ha-naming` | Audit naming patterns, generate rename plans |
| `/ha-apply-naming` | Execute rename plans with dry-run default and phased rollout |
| `/ha-analyze` | Analyze your setup for automation opportunities and config health |
| `/ha-troubleshooting` | Debug automations with evidence-backed diagnostics |
| `/ha-devices` | New device setup: naming, automations, dashboard integration |
| `/ha-config` | Configuration structure and organization guidance |
| `/ha-lovelace` | Dashboard design: cards, views, layouts, themes |
| `/ha-jinja` | Jinja2 templating reference and patterns |


## Agents

Six specialized subagents handle work that benefits from deep, focused analysis:

- **config-debugger** — Traces automation logic step by step, cross-references entity states, produces diagnostic evidence tables
- **ha-config-validator** — Progressive validation in tiers: YAML syntax, then schema, then live HA config check
- **ha-entity-resolver** — Resolves natural-language descriptions ("the kitchen motion sensor") to real entity IDs with full capability snapshots
- **ha-log-analyzer** — Gathers logs, automation traces, and entity history via the HA API
- **device-advisor** — New device setup: naming, capability discovery, automation suggestions, dashboard placement
- **naming-analyzer** — Quantified naming audit with output scaling based on entity count

Agents are spawned by skills when needed. They run in isolated context, do their analysis, and return results. You don't invoke them directly.

## Hooks

- **Session Start** — verifies your environment and routes to the right skill.
- **Post-edit** — ensures Claude follows the correct sequence per the skill, and asks you to review any edits before deploying.

## Design

Every component in this plugin enforces five safety invariants. No YAML is emitted with unsupported device attributes. Inactivity patterns are never silently replaced with timers. Config edits use context-aware anchors, not brittle string replacement. Tokens are never printed. Nothing deploys without explicit confirmation.

Validation outputs include evidence tables — not just "passed" or "failed," but what checks actually ran, what was skipped, and why. When the plugin can't fully validate (no HA connection, hass-cli unavailable), it says so. False confidence is worse than no confidence.

The plugin treats your HA instance as the source of truth. Entity IDs are resolved, not guessed. Device capabilities are queried, not assumed. If something doesn't exist or isn't supported, the plugin stops and tells you — it doesn't invent a workaround.

The entire plugin is 42 markdown files and one 91-line JavaScript hook. Every skill is a spec file — YAML frontmatter declaring tools and permissions, markdown body defining the complete behavior — that Claude Code reads and executes. See [Component Reference](COMPONENTS.md) for the full inventory.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- [hass-cli](https://github.com/home-assistant-ecosystem/home-assistant-cli) (installed during onboarding)
- Git repository for your HA config (setup during onboarding)
- Home Assistant with a long-lived access token (token setup during onboarding)

## License

[MPL-2.0](LICENSE)
