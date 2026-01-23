# Home Assistant Assistant

## What This Is

A Claude Code plugin that enables Home Assistant users to manage their smart home configuration through natural language conversation. Users can create automations, scripts, scenes, dashboards, and maintain their Home Assistant setup without manual YAML editing or web UI navigation.

## Core Value

Users can create and manage Home Assistant automations through natural language conversation instead of manual web UI work.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Connect to and read Home Assistant configuration (entities, devices, existing automations)
- [ ] Understand Home Assistant setup and translate to actionable context
- [ ] Generate Home Assistant automations from natural language descriptions
- [ ] Generate scripts and scenes from natural language
- [ ] Support iterative refinement through conversation (work with user to clarify requirements)
- [ ] Validate configuration changes before deployment
- [ ] Deploy configuration changes safely to Home Assistant instance
- [ ] Create and modify Lovelace dashboards from natural language
- [ ] Configure devices and integrations
- [ ] Read and explain existing configuration
- [ ] Analyze and migrate entity IDs and friendly names to consistent naming standard
- [ ] Support common Home Assistant configuration tasks

### Out of Scope

- Home Assistant Cloud integration — Local instances only for MVP
- Legacy Home Assistant versions — Target modern/current versions only
- Real-time monitoring and alerting — Focus on configuration, not runtime monitoring
- Mobile app integration — Claude Code CLI is desktop-focused
- Automatic changes without confirmation — Always require user approval for deployment

## Context

**Target audience:** General Home Assistant community (not single-user tool)

**Current workflow pain points:**
- Users manually open Home Assistant web UI for all configuration changes
- YAML editing is error-prone and tedious
- No AI-assisted workflow exists for Home Assistant management
- Home Assistant configurations become messy over time (inconsistent naming, hard to maintain)

**Key workflow:** User describes desired automation/configuration in natural language → Claude understands context → Generates configuration → User reviews and approves → Changes deployed safely

**First-time user success:** User installs plugin, says "create an automation that turns off all lights at 10pm," Claude reads their setup and creates working automation.

**Technical environment:**
- Starting from scratch (greenfield project)
- Modern Home Assistant installations
- Local instances (not HA Cloud)
- Likely prerequisites: HA config as git repo, CLI tool or file/API access for deployment

## Constraints

- **Platform**: Local Home Assistant instances only — Defer HA Cloud to v2
- **Versions**: Modern/current Home Assistant versions — Don't worry about legacy support
- **Architecture**: Claude Code plugin (marketplace distribution) — Skills, subagents, reference docs, templates
- **Tech stack**: No constraints specified — Choose optimal technologies during implementation
- **Safety**: Validation/checks before deployment — Not critical path, figure out as we build

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Claude Code plugin (not MCP server) | User wants marketplace distribution with skills/subagents/reference docs pattern | — Pending |
| Focus v1 on automations/scripts/scenes | Most common use case, delivers core value quickly | — Pending |
| Research integration approach before planning | Need to understand HA ecosystem, config management patterns, deployment strategies | — Pending |
| Local-only for MVP | Simpler architecture, most common use case | — Pending |
| Conversational/iterative workflow | Not one-shot commands, but collaborative refinement | — Pending |

---
*Last updated: 2026-01-22 after initialization*
