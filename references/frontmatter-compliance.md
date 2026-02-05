# Frontmatter Compliance Audit

Audit date: 2026-02-05

## Skills Audit

### Compliant (lowercase-hyphenated names)
| File | name |
|------|------|
| home-assistant-assistant/skills-home-assistant-assistant/ha-automations-home-assistant-assistant/SKILL.md | `ha-automations` |
| home-assistant-assistant/skills-home-assistant-assistant/ha-scenes-home-assistant-assistant/SKILL.md | `ha-scenes` |
| home-assistant-assistant/skills-home-assistant-assistant/ha-scripts-home-assistant-assistant/SKILL.md | `ha-scripts` |
| home-assistant-assistant/skills-home-assistant-assistant/ha-troubleshooting-home-assistant-assistant/SKILL.md | `ha-troubleshooting` |
| home-assistant-assistant/skills/ha-automations/SKILL.md | `ha-automations` |
| home-assistant-assistant/skills/ha-conventions/SKILL-haconventions.md | `ha-conventions` |
| home-assistant-assistant/skills/ha-scenes/SKILL.md | `ha-scenes` |
| home-assistant-assistant/skills/ha-scripts/SKILL.md | `ha-scripts` |
| home-assistant-assistant/skills/ha-troubleshooting/SKILL.md | `ha-troubleshooting` |

### Fixed (previously non-compliant)
| File | Old name | New name |
|------|----------|----------|
| home-assistant-assistant/skills-home-assistant-assistant/ha-automation-home-assistant-assistant/SKILL.md | `Home Assistant Automation` | `ha-automation` |
| home-assistant-assistant/skills-home-assistant-assistant/ha-config-home-assistant-assistant/SKILL-haconfig.md | `Home Assistant Configuration` | `ha-config` |
| home-assistant-assistant/skills-home-assistant-assistant/ha-devices-home-assistant-assistant/SKILL-devices.md | `Home Assistant Devices and Integrations` | `ha-devices` |
| home-assistant-assistant/skills-home-assistant-assistant/ha-jinja-home-assistant-assistant/SKILLjijna.md | `Home Assistant Jinja Templating` | `ha-jinja` |
| home-assistant-assistant/skills-home-assistant-assistant/ha-lovelace-home-assistant-assistant/SKILLlovelace.md | `Home Assistant Lovelace Dashboards` | `ha-lovelace` |
| home-assistant-assistant/skills-home-assistant-assistant/ha-naming-home-assistant-assistant/SKILLnaming.md | `Home Assistant Naming Conventions` | `ha-naming` |

## Commands Audit

### Already Compliant (had name field)
| File | name |
|------|------|
| home-assistant-assistant/commands-home-assistant-assistant/ha-connect.md | `ha-connect` |
| home-assistant-assistant/commands-home-assistant-assistant/ha-deploy.md | `ha-deploy` |
| home-assistant-assistant/commands-home-assistant-assistant/ha-rollback.md | `ha-rollback` |
| home-assistant-assistant/commands/ha-connect.md | `ha-connect` |
| home-assistant-assistant/commands/ha-deploy.md | `ha-deploy` |
| home-assistant-assistant/commands/ha-rollback.md | `ha-rollback` |

### Fixed (added missing name field)
| File | Added name |
|------|------------|
| home-assistant-assistant/commands-home-assistant-assistant/analyze.md | `ha:analyze` |
| home-assistant-assistant/commands-home-assistant-assistant/apply-naming.md | `ha:apply-naming` |
| home-assistant-assistant/commands-home-assistant-assistant/audit-naming.md | `ha:audit-naming` |
| home-assistant-assistant/commands-home-assistant-assistant/deploy.md | `ha:deploy` |
| home-assistant-assistant/commands-home-assistant-assistant/generate.md | `ha:generate` |
| home-assistant-assistant/commands-home-assistant-assistant/new-device.md | `ha:new-device` |
| home-assistant-assistant/commands-home-assistant-assistant/onboard.md | `ha:onboard` |
| home-assistant-assistant/commands-home-assistant-assistant/plan-naming.md | `ha:plan-naming` |
| home-assistant-assistant/commands-home-assistant-assistant/setup.md | `ha:setup` |
| home-assistant-assistant/commands-home-assistant-assistant/validate.md | `ha:validate` |

## Agents Audit

### All Compliant (no changes needed)
| File | name |
|------|------|
| home-assistant-assistant/agents-home-assistant-assistant/config-debugger.md | `config-debugger` |
| home-assistant-assistant/agents-home-assistant-assistant/device-advisor.md | `device-advisor` |
| home-assistant-assistant/agents-home-assistant-assistant/ha-config-validator.md | `ha-config-validator` |
| home-assistant-assistant/agents-home-assistant-assistant/ha-entity-resolver.md | `ha-entity-resolver` |
| home-assistant-assistant/agents-home-assistant-assistant/ha-log-analyzer.md | `ha-log-analyzer` |
| home-assistant-assistant/agents-home-assistant-assistant/naming-analyzer.md | `naming-analyzer` |
| home-assistant-assistant/agents/ha-config-validator.md | `ha-config-validator` |
| home-assistant-assistant/agents/ha-convention-analyzer.md | `ha-convention-analyzer` |
| home-assistant-assistant/agents/ha-entity-resolver.md | `ha-entity-resolver` |
| home-assistant-assistant/agents/ha-log-analyzer.md | `ha-log-analyzer` |

---

## Rules Applied

1. **name**: Must be lowercase-hyphenated (e.g., `ha-automations`)
2. **description**: Human-readable, can include trigger keywords
3. **version**: Optional but recommended
4. **allowed-tools**: Restrict to minimum needed (read-only skills shouldn't write)
5. **disable-model-invocation**: Use for dangerous operations (deployment, apply)
