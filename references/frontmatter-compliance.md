# Frontmatter Compliance Audit

Audit date: 2026-02-05

## Skills Audit

### Compliant (lowercase-hyphenated names)
| File | name |
|------|------|
| ha-toolkit/skills-ha-toolkit/ha-automations-ha-toolkit/SKILL-ha-toolkit.md | `ha-automations` |
| ha-toolkit/skills-ha-toolkit/ha-scenes-ha-toolkit/SKILL-ha-toolkit.md | `ha-scenes` |
| ha-toolkit/skills-ha-toolkit/ha-scripts-ha-toolkit/SKILL-ha-toolkit.md | `ha-scripts` |
| ha-toolkit/skills-ha-toolkit/ha-troubleshooting-ha-toolkit/SKILL-ha-toolkit.md | `ha-troubleshooting` |
| home-assistant-assistant/skills-haa/ha-automations-haa/SKILL-haa.md | `ha-automations` |
| home-assistant-assistant/skills-haa/ha-conventions-haa/SKILL-haconventions-haa.md | `ha-conventions` |
| home-assistant-assistant/skills-haa/ha-scenes-haa/SKILL-haa.md | `ha-scenes` |
| home-assistant-assistant/skills-haa/ha-scripts-haa/SKILL-haa.md | `ha-scripts` |
| home-assistant-assistant/skills-haa/ha-troubleshooting-haa/SKILL-haa.md | `ha-troubleshooting` |

### Fixed (previously non-compliant)
| File | Old name | New name |
|------|----------|----------|
| ha-toolkit/skills-ha-toolkit/ha-automation-ha-toolkit/SKILL-ha-toolkit.md | `Home Assistant Automation` | `ha-automation` |
| ha-toolkit/skills-ha-toolkit/ha-config-ha-toolkit/SKILL-haconfig-ha-toolkit.md | `Home Assistant Configuration` | `ha-config` |
| ha-toolkit/skills-ha-toolkit/ha-devices-ha-toolkit/SKILL-devices-ha-toolkit.md | `Home Assistant Devices and Integrations` | `ha-devices` |
| ha-toolkit/skills-ha-toolkit/ha-jinja-ha-toolkit/SKILLjijna-ha-toolkit.md | `Home Assistant Jinja Templating` | `ha-jinja` |
| ha-toolkit/skills-ha-toolkit/ha-lovelace-ha-toolkit/SKILLlovelace-ha-toolkit.md | `Home Assistant Lovelace Dashboards` | `ha-lovelace` |
| ha-toolkit/skills-ha-toolkit/ha-naming-ha-toolkit/SKILLnaming-ha-toolkit.md | `Home Assistant Naming Conventions` | `ha-naming` |

## Commands Audit

### Already Compliant (had name field)
| File | name |
|------|------|
| ha-toolkit/commands-ha-toolkit/ha-connect-ha-toolkit.md | `ha-connect` |
| ha-toolkit/commands-ha-toolkit/ha-deploy-ha-toolkit.md | `ha-deploy` |
| ha-toolkit/commands-ha-toolkit/ha-rollback-ha-toolkit.md | `ha-rollback` |
| home-assistant-assistant/commands-haa/ha-connect-haa.md | `ha-connect` |
| home-assistant-assistant/commands-haa/ha-deploy-haa.md | `ha-deploy` |
| home-assistant-assistant/commands-haa/ha-rollback-haa.md | `ha-rollback` |

### Fixed (added missing name field)
| File | Added name |
|------|------------|
| ha-toolkit/commands-ha-toolkit/analyze-ha-toolkit.md | `ha:analyze` |
| ha-toolkit/commands-ha-toolkit/apply-naming-ha-toolkit.md | `ha:apply-naming` |
| ha-toolkit/commands-ha-toolkit/audit-naming-ha-toolkit.md | `ha:audit-naming` |
| ha-toolkit/commands-ha-toolkit/deploy-ha-toolkit.md | `ha:deploy` |
| ha-toolkit/commands-ha-toolkit/generate-ha-toolkit.md | `ha:generate` |
| ha-toolkit/commands-ha-toolkit/new-device-ha-toolkit.md | `ha:new-device` |
| ha-toolkit/commands-ha-toolkit/onboard-ha-toolkit.md | `ha:onboard` |
| ha-toolkit/commands-ha-toolkit/plan-naming-ha-toolkit.md | `ha:plan-naming` |
| ha-toolkit/commands-ha-toolkit/setup-ha-toolkit.md | `ha:setup` |
| ha-toolkit/commands-ha-toolkit/validate-ha-toolkit.md | `ha:validate` |

## Agents Audit

### All Compliant (no changes needed)
| File | name |
|------|------|
| ha-toolkit/agents-ha-toolkit/config-debugger-ha-toolkit.md | `config-debugger` |
| ha-toolkit/agents-ha-toolkit/device-advisor-ha-toolkit.md | `device-advisor` |
| ha-toolkit/agents-ha-toolkit/ha-config-validator-ha-toolkit.md | `ha-config-validator` |
| ha-toolkit/agents-ha-toolkit/ha-entity-resolver-ha-toolkit.md | `ha-entity-resolver` |
| ha-toolkit/agents-ha-toolkit/ha-log-analyzer-ha-toolkit.md | `ha-log-analyzer` |
| ha-toolkit/agents-ha-toolkit/naming-analyzer-ha-toolkit.md | `naming-analyzer` |
| home-assistant-assistant/agents-haa/ha-config-validator-haa.md | `ha-config-validator` |
| home-assistant-assistant/agents-haa/ha-convention-analyzer-haa.md | `ha-convention-analyzer` |
| home-assistant-assistant/agents-haa/ha-entity-resolver-haa.md | `ha-entity-resolver` |
| home-assistant-assistant/agents-haa/ha-log-analyzer-haa.md | `ha-log-analyzer` |

---

## Rules Applied

1. **name**: Must be lowercase-hyphenated (e.g., `ha-automations`)
2. **description**: Human-readable, can include trigger keywords
3. **version**: Optional but recommended
4. **allowed-tools**: Restrict to minimum needed (read-only skills shouldn't write)
5. **disable-model-invocation**: Use for dangerous operations (deployment, apply)
