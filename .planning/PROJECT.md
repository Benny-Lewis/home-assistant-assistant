# Home Assistant Assistant

## What This Is

A Claude Code plugin that enables natural language management of Home Assistant. Users can create automations, scripts, and scenes by describing what they want in plain language, instead of manually editing YAML or clicking through the web UI. Designed for the broader Home Assistant community.

## Core Value

Users can manage their Home Assistant through natural language conversation instead of manual YAML editing and web UI clicking.

## Requirements

### Validated

(None yet — ship to validate)

### Active

**Foundation (must solve first):**
- [ ] Connect to and read Home Assistant configuration
- [ ] Understand existing entities, automations, and devices
- [ ] Safe deployment mechanism with validation before applying changes
- [ ] Git-based configuration management
- [ ] Rollback capability if changes break things

**Core Automation Features:**
- [ ] Create automations from natural language descriptions
- [ ] Modify existing automations conversationally
- [ ] Create scripts from natural language
- [ ] Create scenes from natural language
- [ ] Test and validate changes before deployment

**User Experience:**
- [ ] Iterative conversation to refine automations before creation
- [ ] Show what changes will be made before applying them
- [ ] Preview generated configuration
- [ ] Explain existing automations in plain language

### Out of Scope

- Dashboards/Lovelace UI — defer to v2 (more complex interaction model)
- Device/integration configuration — defer to v2 (riskier, could break integrations)
- Naming cleanup/migration — defer to v2 (valuable but one-time operation)
- Home Assistant Cloud support — v1 targets local instances only
- Legacy Home Assistant versions — target modern/current versions only

## Context

**Target Users:** General Home Assistant community, not just advanced users.

**Common Pain Points:**
- Manual YAML editing is error-prone and tedious
- Web UI automation builder is limited for complex scenarios
- No good AI-assisted workflow exists today
- HA configs become messy over time with inconsistent naming (entity IDs, friendly names, automation names)
- Hard to find and maintain automations in large configs

**Current Workflow Being Replaced:**
Users today manually open the HA web UI and configure automations themselves. They want to describe what they want in natural language and have Claude handle the implementation details.

**Automation Complexity Range:**
Users build everything from simple triggers ("when motion detected, turn on light") to complex multi-step sequences with conditions ("if temp > X AND time is Y AND person home, then do A, B, C").

## Constraints

- **Home Assistant Version**: Modern/current versions only, don't support legacy
- **Deployment Target**: Local Home Assistant instances (v1 scope)
- **Architecture**: Claude Code plugin with skills, subagents, reference docs (NOT an MCP server)
- **Prerequisites**: Likely requires HA config as git repo, possibly CLI tool or API access (needs research)
- **Tech Stack**: No constraints, to be determined during planning

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| — | — | — |

---
*Last updated: 2026-01-23 after initialization*
