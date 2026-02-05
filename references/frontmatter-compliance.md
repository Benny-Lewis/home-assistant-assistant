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

## Rules Applied

1. **name**: Must be lowercase-hyphenated (e.g., `ha-automations`)
2. **description**: Human-readable, can include trigger keywords
3. **version**: Optional but recommended
4. **allowed-tools**: Restrict to minimum needed (read-only skills shouldn't write)
5. **disable-model-invocation**: Use for dangerous operations (deployment, apply)
