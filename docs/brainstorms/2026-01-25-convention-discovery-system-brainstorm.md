---
topic: Convention Discovery System for HA Plugin
date: 2026-01-25
status: complete
chosen_approach: Convention Discovery System (Approach 1)
---

# Convention Discovery System for Home Assistant Plugin

## What We're Building

A convention discovery and enforcement system that ensures the HA plugin generates automations, scripts, and other entities that match each user's existing naming patterns and best practices.

### The Problem

In a test session creating a backyard floodlight automation:
- Agent ignored the user's 1,800-line naming spec
- Proposed wrong naming format (had to be corrected twice)
- Used inline `delay:` instead of timer helpers (user's established pattern)
- Wasted 41.5k tokens and 1m 10s finding the naming spec after user prompted
- Total session: ~12 minutes, ~80k tokens (should have been ~3-4 min, ~20k tokens)

### The Solution

1. **Convention detection** - Analyze user's existing HA config to extract naming patterns
2. **User confirmation** - Present detected patterns for user approval/adjustment
3. **Persistent storage** - Save conventions to plugin settings file
4. **Skill integration** - Skills read conventions before generating YAML

## Why This Approach

### Chosen: Convention Discovery System

**Over "Embedded Defaults":**
- This is a multi-user plugin - each user has different conventions
- Can't assume one naming pattern fits all
- Users shouldn't have to manually configure preferences

**Over "Just-in-Time Learning":**
- One-time detection is better than repeated analysis every request
- Persistent conventions document serves as foundation for future migration feature
- More predictable behavior (same conventions applied consistently)

### Design Decisions from Research

| Decision | Rationale |
|----------|-----------|
| Store in `.claude/home-assistant-assistant.md` | Per Claude Code best practices, plugin settings go in YAML frontmatter of this file |
| Use `context: fork` + Explore agent for detection | Best practice for codebase analysis tasks |
| Default to timer helpers for >30s durations | HA community uses both patterns, but timers are restart-safe |
| Detect + confirm flow | Auto-detection reduces manual work; confirmation gives user control |

## Key Decisions

### 1. Convention Storage Location

**Decision:** Store in existing `.claude/home-assistant-assistant.md` settings file

```yaml
---
# Existing settings
ha_url: http://homeassistant.local:8123
auto_deploy: false

# New convention settings
conventions:
  automation_id_pattern: "<area>_<trigger>_[if_<condition>]_<action>"
  automation_alias_pattern: "<Area>: <Trigger> [If <Condition>] -> <Action>"
  timer_naming: "<area>_<purpose>_timer"
  use_timer_helpers: true
  timer_threshold_seconds: 30
  detected_from_existing: true
  last_detected: 2026-01-25
---
```

### 2. Fallback for No Existing Pattern

**Decision:** If no consistent pattern detected (or new install), offer HA community conventions as default:

- ID: `<area>_<trigger>_[if_<condition>]_<action>`
- Alias: `"<Area>: <Trigger> -> <Action>"`
- Timer naming: `<area>_<purpose>_timer`

User can accept defaults or define their own.

### 3. Timer vs Delay Default

**Decision:** Default to timer helpers when duration > 30 seconds

Research shows both patterns are valid in HA community. Timer helpers provide:
- Restart safety (`restore: true`)
- Dashboard visibility
- External control (cancel/pause)

Inline `delay:` is fine for short durations or non-critical actions.

### 4. Skill Integration

**Decision:** Add convention loading as Step 0 in `ha-automations/SKILL.md`

```markdown
## Process

0. **Load conventions** from `.claude/home-assistant-assistant.md`
   - Read the `conventions:` section from settings
   - If no conventions exist, prompt user to run `/ha-conventions` first

1. Resolve entities via ha-entity-resolver
...
```

## Open Questions

1. **Migration feature scope** - How should the future `/ha-migrate` command work?
   - Full rename of all entities?
   - Selective migration?
   - Dry-run mode?

2. **Convention versioning** - What happens when user's preferences change?
   - Re-run detection?
   - Manual edit of settings file?

3. **Conflict handling** - What if detected pattern conflicts with HA best practices?
   - Warn user?
   - Offer alternatives?

## Files to Create/Modify

### New Files
- `commands/ha-conventions.md` - Detection + confirmation command
- `agents/ha-convention-analyzer.md` - Pattern extraction agent

### Modified Files
- `skills/ha-automations/SKILL.md` - Add convention loading step
- `skills/ha-automations/references/common-patterns.md` - Replace delay with timer pattern
- `templates/home-assistant-assistant.md` - Add conventions schema

## Research Sources

### Home Assistant
- No official naming standard, but `<area>_<function>` is most common
- Timer helpers recommended for restart-safety
- `mode: restart` common for motion lights with delays

### Claude Code Plugins
- Convention storage in `.claude/plugin-name.md` with YAML frontmatter
- Use `context: fork` + Explore agent for codebase analysis
- Progressive disclosure: SKILL.md references supporting files
