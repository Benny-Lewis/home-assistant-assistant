---
title: "feat: Add Convention Discovery System"
type: feat
date: 2026-01-25
brainstorm: docs/brainstorms/2026-01-25-convention-discovery-system-brainstorm.md
---

# feat: Add Convention Discovery System

## Overview

Add a convention discovery and enforcement system to the Home Assistant plugin. This ensures generated automations, scripts, and entities match each user's existing naming patterns and best practices - eliminating the need for manual corrections.

## Problem Statement

In a real test session, the plugin:
- Ignored the user's naming spec (1,800 lines) entirely
- Required 2 user corrections before producing correct output
- Wasted 41.5k tokens and 1m 10s exploring for specs that should have been pre-loaded
- Used inline `delay:` instead of the user's established timer helper pattern
- Took ~12 minutes instead of the target ~3-4 minutes

**Root cause:** Skills don't know about or load user conventions before generating YAML.

## Proposed Solution

1. **New `/ha-conventions` skill** - Detects naming patterns from existing HA config (using skills/ not commands/)
2. **New convention analyzer agent** - Extracts patterns from automations/timers in forked context
3. **Convention storage** - Saves detected patterns as rules + examples to plugin settings file
4. **Skill integration** - Skills inject conventions via shell expansion at load time
5. **Validation loop** - Post-generation validation ensures convention compliance

## Technical Approach

### Architecture

```
User runs /ha-conventions
         │
         ▼
┌─────────────────────────┐
│ ha-convention-analyzer  │ ◄── Subagent analyzes existing config
│ (context: fork)         │
└───────────┬─────────────┘
            │ Returns detected patterns
            ▼
┌─────────────────────────┐
│ /ha-conventions command │ ◄── Shows patterns, asks for confirmation
└───────────┬─────────────┘
            │ User confirms/adjusts
            ▼
┌─────────────────────────┐
│ .claude/home-assistant- │ ◄── Conventions stored in YAML frontmatter
│ assistant.md            │
└─────────────────────────┘
            │
            ▼ (Later, when user creates automation)
┌─────────────────────────┐
│ ha-automations skill    │ ◄── Step 0: Load conventions before generating
│ (Step 0: Load convs)    │
└─────────────────────────┘
```

### Implementation Phases

#### Phase 1: Convention Storage Schema

Update the settings template to include convention fields.

**File:** `templates/home-assistant-assistant.md`

**Changes:**
```yaml
---
# Existing settings...
ha_url: "http://homeassistant.local:8123"
auto_deploy: false

# NEW: Convention settings (populated by /ha-conventions)
conventions:
  # Naming rules (more robust than single pattern string)
  separator: "_"                    # "_" or "-"
  case: "snake_case"                # snake_case, kebab-case
  area_position: "prefix"           # prefix or suffix
  condition_prefix: "if_"           # How conditions are marked

  # Computed patterns (derived from rules above)
  automation_id_pattern: "<area>_<trigger>_[if_<condition>]_<action>"
  automation_alias_pattern: "<Area>: <Trigger> [If <Condition>] → <Action>"
  timer_naming: "<area>_<purpose>"

  # Behavior preferences
  use_timer_helpers: true           # Use timer helpers instead of inline delay:
  timer_threshold_seconds: 30       # Use timers for delays > this value
  default_automation_mode: "single" # single, restart, queued, parallel
  enforce_conventions: false        # Strict mode: refuse to generate non-compliant YAML

  # Detection metadata
  detected_from_existing: false     # true if auto-detected
  last_detected: null               # ISO date of last detection
  confidence: null                  # high, medium, low

  # Examples (stored for pattern matching reference)
  examples:
    - id: "backyard_door_open_if_dark_floodlight_on"
      alias: "Backyard: Door Open If Dark → Floodlight On"
    - id: "kitchen_motion_light_on"
      alias: "Kitchen: Motion → Light On"
---
```

**Why rules + examples instead of just patterns:**
- Rules (separator, case) are harder to "overfit" from messy data
- Examples provide concrete reference for pattern matching
- Easier to validate and enforce programmatically

**Acceptance criteria:**
- [ ] Template includes `conventions:` section with all fields
- [ ] Fields have sensible defaults (timer helpers on, 30s threshold)
- [ ] Comments explain each field's purpose
- [ ] Includes both rules and derived patterns
- [ ] Examples section populated during detection

---

#### Phase 2: Convention Analyzer Agent

Create a subagent that analyzes existing HA config files in an isolated context.

**File:** `agents/ha-convention-analyzer.md`

```yaml
---
name: ha-convention-analyzer
description: >
  Analyzes existing Home Assistant configuration to detect naming patterns
  and conventions. Use when running /ha-conventions skill. Returns
  structured patterns for automation IDs, aliases, and timer usage with
  confidence levels. Handles mixed/legacy naming gracefully.
tools: Read, Grep, Glob
model: sonnet
---
```

**Note:** Read-only tools only (`Read, Grep, Glob`). No `Bash` unless truly needed - prevents tool sprawl and permission prompts.

**Agent responsibilities:**
1. Read `automations.yaml` from HA config (prefer Python YAML parsing if available)
2. Extract all `id:` and `alias:` values
3. Identify patterns (area prefixes, trigger/action suffixes, separators)
4. **Detect multiple conflicting patterns** - If "old style" vs "new style" found, report both with counts
5. Check `timer.yaml` for timer naming patterns
6. Detect if user uses timer helpers vs inline delays
7. Report patterns with confidence levels and sample sizes

**Handling mixed/legacy conventions:**
```markdown
If you detect distinct groups of naming styles (e.g., automations from 2023
use "old_format" while 2025 automations use "new_format"), report:
- The most recent/dominant pattern as primary
- Note the conflict and counts for each style
- Let the user choose which to standardize on
```

**Output format:**
```markdown
## Detected Conventions

### Automation IDs
- **Pattern:** `<area>_<trigger>_<action>`
- **Examples found:**
  - `backyard_door_open_floodlight_on`
  - `kitchen_motion_light_on`
- **Confidence:** high (8/10 automations follow pattern)

### Automation Aliases
- **Pattern:** `"<Area>: <Trigger> → <Action>"`
- **Examples found:**
  - `"Backyard: Door Open → Floodlight On"`
  - `"Kitchen: Motion → Light On"`
- **Confidence:** high

### Timer Usage
- **Pattern:** Timer helpers for delays > 30s
- **Examples found:**
  - `timer.backyard_floodlight_auto_off` (5 min)
  - `timer.kitchen_light_auto_off` (3 min)
- **Confidence:** medium (3/5 long delays use timers)

### No Pattern Detected
- Automation modes (mixed usage)
```

**Acceptance criteria:**
- [ ] Agent reads automations.yaml via SSH or local path
- [ ] Extracts and categorizes naming patterns
- [ ] Reports confidence levels (high/medium/low)
- [ ] Handles "no pattern found" gracefully
- [ ] Returns structured output for command parsing

---

#### Phase 3: `/ha-conventions` Skill

Create the user-facing skill for convention detection and confirmation.

**File:** `skills/ha-conventions/SKILL.md` (NOT commands/ - skills provide more control)

```yaml
---
name: ha-conventions
description: >
  Detect and configure naming conventions for your Home Assistant setup.
  Use when setting up the plugin for the first time or when your naming
  patterns change.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob
---
```

**Why skills/ instead of commands/:**
- `disable-model-invocation: true` prevents Claude from randomly triggering detection
- `allowed-tools` restricts permissions to read-only operations
- Skills support `context: fork` for isolated analysis
- Skills are the recommended approach for new Claude Code plugins

**Command flow:**

1. **Check existing conventions**
   - Read `.claude/home-assistant-assistant.md`
   - If conventions exist, ask: "Conventions already configured. Re-detect or view current?"

2. **Run detection** (if needed)
   - Launch `ha-convention-analyzer` agent with `context: fork`
   - Analyze automations.yaml, timer.yaml, scripts.yaml

3. **Present findings**
   - Show detected patterns with examples
   - Show confidence levels
   - Highlight any inconsistencies

4. **Handle no-pattern case**
   - If no consistent pattern found, offer defaults:
     ```
     No consistent naming pattern detected. Would you like to adopt
     Home Assistant community conventions?

     Recommended:
     - ID: <area>_<trigger>_[if_<condition>]_<action>
     - Alias: "<Area>: <Trigger> → <Action>"
     - Timer naming: <area>_<purpose>
     ```

5. **User confirmation**
   - Ask user to confirm, modify, or reject each convention
   - Allow custom pattern entry

6. **Save conventions**
   - Write to `.claude/home-assistant-assistant.md` YAML frontmatter
   - Set `detected_from_existing: true` and `last_detected: <today>`

**Acceptance criteria:**
- [ ] Command detects patterns from existing config
- [ ] Shows findings with confidence levels
- [ ] Offers sensible defaults when no pattern found
- [ ] Allows user to confirm, modify, or define custom patterns
- [ ] Saves to settings file with metadata
- [ ] Handles re-detection (update existing conventions)

---

#### Phase 4: Skill Integration

Update skills to load and apply conventions using shell expansion.

**File:** `skills/ha-automations/SKILL.md`

**Changes:**

Use shell expansion (`!` syntax) to inject conventions at skill load time - not runtime file reads:

```yaml
---
name: ha-automations
description: Create Home Assistant automations following your naming conventions
allowed-tools: Read, Bash(hass-cli:*), Edit, Write
---

## Your Project's Conventions

!`cat .claude/home-assistant-assistant.md 2>/dev/null | head -60 || echo "No conventions configured - using defaults"`

## Default Conventions (if none above)

- ID: `<area>_<trigger>_[if_<condition>]_<action>`
- Alias: `"<Area>: <Trigger> → <Action>"`
- Timer naming: `<area>_<purpose>`
- Use timer helpers for delays > 30 seconds

## Process

0. **Verify conventions loaded** (CRITICAL - be atomic)
   - Check if conventions section appears above
   - [CRITICAL] If "No conventions configured" shown, STOP and ask:
     "I don't know your naming conventions yet. Please run `/ha-conventions` first,
     or tell me to use default HA community standards."
   - If confidence is `low` or `none`, add uncertainty banner to output

1. **Resolve entities** via ha-entity-resolver agent
   ...
```

**Why shell expansion instead of runtime reads:**
- The `!`command`` syntax runs at skill load time (preprocessing)
- Claude receives the already-rendered content with actual conventions
- No need to "pretend" to read a file - data is already there
- More efficient and reliable than dynamic file reads

Add new section after Process:

```markdown
## Naming Requirements

Generated automations MUST follow user's conventions from `.claude/home-assistant-assistant.md`.

**If conventions configured:**
- Use the exact patterns from `conventions.automation_id_pattern` and `conventions.automation_alias_pattern`

**If no conventions (fallback defaults):**
- ID: `<area>_<trigger>_[if_<condition>]_<action>`
- Alias: `"<Area>: <Trigger> [If <Condition>] → <Action>"`

**Examples matching common patterns:**
| Area | Trigger | Condition | Action | ID | Alias |
|------|---------|-----------|--------|----|----|
| backyard | door_open | dark | floodlight_on | `backyard_door_open_if_dark_floodlight_on` | `"Backyard: Door Open If Dark → Floodlight On"` |
| kitchen | motion | - | light_on | `kitchen_motion_light_on` | `"Kitchen: Motion → Light On"` |
```

Add timer decision section:

```markdown
## Timer vs Delay Decision

**Check user conventions first:** If `conventions.use_timer_helpers` is set, follow it.

**Default behavior (or if not set):**
- Duration > `conventions.timer_threshold_seconds` (default 30s) → Use timer helper
- Duration ≤ threshold → Inline `delay:` is acceptable

**Timer helper pattern:**
1. Create timer in `timer.yaml` with `restore: true`
2. Create automation to start timer
3. Create automation triggered by `timer.finished` event

**Always explain the choice to user** when proposing an automation with delays.
```

**Acceptance criteria:**
- [x] Step 0 added to load conventions
- [x] Naming Requirements section documents patterns
- [x] Timer vs Delay decision tree included
- [x] Fallback defaults specified for unconfigured users
- [x] Examples show how patterns apply

---

#### Phase 5: Fix Common Patterns Reference

Update the reference file to show correct timer pattern.

**File:** `skills/ha-automations/references/common-patterns.md`

**Changes:**

Replace the Motion-Activated Light pattern (which uses inline delay) with timer helper version:

```yaml
## Motion-Activated Light (Timer Pattern - Recommended)

Use timer helpers for delays > 30 seconds. Survives HA restarts.

### timer.yaml
```yaml
[room]_light_auto_off:
  name: "[Room] Light Auto-Off Timer"
  duration: "00:05:00"
  restore: true
```

### automations.yaml - Turn on and start timer
```yaml
- id: [room]_motion_light_on
  alias: "[Room]: Motion → Light On"
  mode: restart
  triggers:
    - trigger: state
      entity_id: binary_sensor.[room]_motion
      to: "on"
  conditions:
    - condition: state
      entity_id: sun.sun
      state: "below_horizon"
  actions:
    - action: light.turn_on
      target:
        entity_id: light.[room]
    - action: timer.start
      target:
        entity_id: timer.[room]_light_auto_off
```

### automations.yaml - Turn off when timer finishes
```yaml
- id: [room]_light_timer_expired_off
  alias: "[Room]: Light Timer Expired → Off"
  triggers:
    - trigger: event
      event_type: timer.finished
      event_data:
        entity_id: timer.[room]_light_auto_off
  conditions:
    - condition: state
      entity_id: light.[room]
      state: "on"
  actions:
    - action: light.turn_off
      target:
        entity_id: light.[room]
```

**Why timer helpers?**
- `restore: true` survives HA restarts
- Visible countdown on dashboard
- Can be canceled/extended programmatically
- More robust than inline `delay:` which is lost on restart
```

Add note about when inline delay is acceptable:

```markdown
## Short Delays (< 30 seconds)

For brief delays where restart-safety isn't critical, inline delay is fine:

```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.hallway
  - delay:
      seconds: 5
  - action: light.turn_off
    target:
      entity_id: light.hallway
```

Use this pattern for:
- Brief visual feedback (flash lights)
- Sequential device commands
- Non-critical timing
```

**Acceptance criteria:**
- [x] Motion light pattern updated to timer helper version
- [x] Pattern shows timer.yaml + 2 automations (on + off)
- [x] Explanation of why timers are preferred
- [x] Short delay pattern preserved for appropriate use cases
- [x] All patterns use `triggers:` (modern syntax) not `trigger:` (deprecated)

---

#### Phase 6: Validation Feedback Loop

Add post-generation validation to ensure convention compliance.

**Pattern:** Generate → Validate → Fix → Repeat

**Add to `skills/ha-automations/SKILL.md` process:**

```markdown
## Validation Checklist

After generating automation YAML, validate before presenting to user:

1. **Naming compliance**
   - Does ID match `automation_id_pattern`?
   - Does alias match `automation_alias_pattern`?
   - If `enforce_conventions: true` and non-compliant, regenerate

2. **Timer/delay compliance**
   - If delay > threshold, is timer helper used?
   - If timer used, is `restore: true` set?

3. **Syntax validation**
   - Use modern `triggers:` syntax (not `trigger:`)
   - Use modern `actions:` syntax (not `action:`)
   - Verify all entity IDs exist (via ha-entity-resolver)

4. **If validation fails:**
   - Review error messages
   - Fix the YAML
   - Run validation again
   - Only proceed when all checks pass
```

**Acceptance criteria:**
- [x] Validation checklist added to skill
- [x] Naming compliance checked before output
- [x] Timer pattern compliance verified
- [x] Syntax validated against HA requirements

---

#### Workflow Checklist Pattern

For complex automation creation, provide a trackable checklist:

```markdown
## Automation Creation Progress

Copy this checklist and track progress:

```
Automation Progress:
- [ ] Step 0: Load and verify conventions from settings
- [ ] Step 1: Resolve entity IDs via ha-entity-resolver
- [ ] Step 2: Determine timer vs delay based on duration
- [ ] Step 3: Generate automation YAML following conventions
- [ ] Step 4: Validate against naming patterns
- [ ] Step 5: If timer needed, generate timer.yaml entry
- [ ] Step 6: Present to user for review
- [ ] Step 7: Write to automations.yaml
- [ ] Step 8: Deploy via /ha-deploy
```
```

---

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `templates/home-assistant-assistant.md` | Modify | Add `conventions:` section with rules + examples schema |
| `agents/ha-convention-analyzer.md` | Create | New agent for pattern detection (read-only tools) |
| `skills/ha-conventions/SKILL.md` | Create | New skill for convention discovery flow |
| `skills/ha-automations/SKILL.md` | Modify | Add shell expansion, validation checklist, workflow checklist |
| `skills/ha-automations/references/common-patterns.md` | Modify | Replace delay pattern with timer pattern |

## Acceptance Criteria

### Functional Requirements
- [x] `/ha-conventions` skill detects naming patterns from existing HA config
- [x] Skill offers sensible defaults when no patterns exist
- [x] Conventions stored as rules + examples (not just pattern strings)
- [x] Conventions saved to `.claude/home-assistant-assistant.md`
- [x] `ha-automations` skill injects conventions via shell expansion at load time
- [x] Generated automations follow user's naming conventions
- [x] Timer helpers used by default for delays > 30 seconds
- [x] Mixed/legacy conventions detected and reported to user
- [x] Validation loop checks naming compliance before output

### Quality Gates
- [x] All new files follow existing plugin patterns (YAML frontmatter, markdown structure)
- [x] Skill includes user confirmation before saving
- [x] Skills gracefully handle missing conventions (uses defaults with uncertainty banner)
- [x] Reference patterns updated to show timer helper approach
- [x] `disable-model-invocation: true` set on /ha-conventions to prevent accidental triggers
- [x] Read-only tools (`Read, Grep, Glob`) used for analyzer agent
- [x] Low-confidence patterns trigger fail-fast behavior with clear user guidance

## Success Metrics

After implementation, the same test case (backyard floodlight automation) should:
- Generate correct naming on first attempt (no user corrections needed)
- Use timer helper pattern without prompting
- Complete in ~3-4 minutes instead of ~12 minutes
- Use ~20k tokens instead of ~80k tokens

## Dependencies & Prerequisites

- Plugin already has working `/ha-connect`, `/ha-deploy` commands
- User has existing HA config accessible via SSH or local path
- `hass-cli` is configured and working

---

## Specifications (SpecFlow Analysis)

### HA Config File Access

**How the analyzer accesses config files:**

1. **Check settings for HA config path** - Read `ha_config_path` from `.claude/home-assistant-assistant.md`
2. **If not set, prompt user** - "Where is your Home Assistant config directory?"
   - Local path: `/home/homeassistant/.homeassistant/`
   - SSH remote: `root@homeassistant.local:/config/`
3. **If SSH, use existing connection** - Reuse SSH details from `/ha-connect` setup
4. **Fallback if inaccessible:**
   - Offer manual specification of conventions
   - Offer to use community defaults
   - Skip detection for now

**Error handling:**
| Error | Response |
|-------|----------|
| Path not configured | Prompt for path, save to settings |
| SSH auth failure | Show error, offer to reconfigure via `/ha-connect` |
| File not found | Proceed with available files, note missing sources |
| Parse error | Show line number, offer to skip that file |

### Template Variable Specification

**Valid template variables:**

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `<area>` | Physical location/room | `kitchen`, `backyard`, `living_room` |
| `<trigger>` | What initiates the automation | `motion`, `door_open`, `sunset` |
| `<condition>` | Optional qualifying condition | `dark`, `home`, `weekday` |
| `<action>` | What the automation does | `light_on`, `lock`, `notify` |
| `<purpose>` | Timer/script purpose | `auto_off`, `cooldown`, `sequence` |
| `<target>` | Target entity type | `light`, `fan`, `shade` |

**Extraction rules:**
- Extract from user's natural language description
- Normalize to snake_case for IDs
- Use Title Case for alias display names
- If ambiguous, ask user to clarify

**Pattern syntax:**
- `<variable>` = required variable
- `[section]` = optional section (include only if applicable)
- Literal text preserved as-is

### Settings File State Handling

| File State | `/ha-conventions` Behavior | Skill Behavior |
|------------|---------------------------|----------------|
| File doesn't exist | Create from template, then add conventions | Use fallback defaults, suggest `/ha-conventions` |
| File exists, no `conventions:` | Append conventions section | Use fallback defaults |
| File exists with conventions | Offer to view/re-detect | Load and apply conventions |
| Malformed YAML | Show error with line number, offer to reset section | Warn user, use fallback defaults |

**Merge strategy for re-detection:** Show diff of old vs new, require explicit confirmation before overwriting.

### Confidence Level Calculation

| Confidence | Criteria |
|------------|----------|
| **High** | ≥80% of samples match pattern AND ≥5 samples |
| **Medium** | 50-79% match OR ≥80% but <5 samples |
| **Low** | <50% match OR <3 samples total |
| **None** | No discernible pattern (all unique) |

### Timer vs Delay Decision Logic

```
IF conventions.use_timer_helpers is explicitly false:
  → Use inline delay (respect user preference)
ELSE IF duration ≤ conventions.timer_threshold_seconds (default 30):
  → Use inline delay (below threshold)
ELSE:
  → Use timer helper (default behavior for long delays)
```

**Edge case:** If user sets `use_timer_helpers: false` but duration is >10 minutes, show warning but respect preference.

### Scope Clarification

**Phase 1 scope (this plan):**
- Automations only (automations.yaml analysis)
- Timer detection (timer.yaml analysis)
- Delay pattern detection (inline delay: vs timer.start in automations)

**Deferred to Phase 2:**
- Scripts (scripts.yaml) - different naming patterns
- Scenes (scenes.yaml) - activity-based naming
- Other helpers (input_boolean, input_select, etc.)

### Partial Conventions Handling

If some convention fields are set but others missing:

| Field | If Missing | Default |
|-------|-----------|---------|
| `automation_id_pattern` | Use HA community default | `<area>_<trigger>_[if_<condition>]_<action>` |
| `automation_alias_pattern` | Use HA community default | `<Area>: <Trigger> [If <Condition>] → <Action>` |
| `use_timer_helpers` | Default to true | `true` |
| `timer_threshold_seconds` | Default to 30 | `30` |
| `timer_naming` | Derive from area pattern | `<area>_<purpose>` |

---

## Future Considerations

This convention system lays groundwork for:
- **`/ha-migrate` command** - Rename existing entities to match conventions
- **Convention validation hooks** - Warn when generated YAML doesn't match patterns
- **Multi-user convention sharing** - Export/import convention profiles

## References

### Internal
- Brainstorm: `docs/brainstorms/2026-01-25-convention-discovery-system-brainstorm.md`
- Current skill: `skills/ha-automations/SKILL.md`
- Current patterns: `skills/ha-automations/references/common-patterns.md`
- Settings template: `templates/home-assistant-assistant.md`

### External
- HA Timer Integration: https://www.home-assistant.io/integrations/timer/
- HA Automation Modes: https://www.home-assistant.io/docs/automation/modes/
- Claude Code Skills: https://code.claude.com/docs/en/skills.md
- Claude Code Plugins Reference: https://code.claude.com/docs/en/plugins-reference.md

---

## Review Feedback Incorporated

This plan was reviewed by Claude, ChatGPT, and Gemini. Key improvements incorporated:

### From Claude Review
- ✅ Use shell expansion (`!` syntax) for convention loading at skill load time
- ✅ Add validation feedback loop (generate → validate → fix → repeat)
- ✅ Add workflow checklist pattern for complex operations
- ✅ Enhance descriptions with "when to use" clauses

### From ChatGPT Review
- ✅ Move from `commands/` to `skills/` (skills provide more control, not legacy)
- ✅ Store conventions as rules + examples (separator, case, area_position) to reduce overfitting
- ✅ Add `disable-model-invocation: true` to prevent random triggers
- ✅ Make Step 0 fail-fast when confidence is low (don't pretend patterns are authoritative)

### From Gemini Review
- ✅ Handle mixed/legacy conventions explicitly (detect multiple conflicting patterns)
- ✅ Add strict enforcement mode (`enforce_conventions: true`)
- ✅ Make Step 0 atomic (force explicit tool use with CRITICAL markers)
- ✅ Use read-only tools for analyzer agent (`Read, Grep, Glob` - no Bash)

### Verified Against Claude Code Docs
- ✅ Shell expansion `!` syntax confirmed as real feature ("inject dynamic context")
- ✅ `commands/` NOT legacy, but `skills/` recommended for new plugins
- ✅ All frontmatter fields (`disable-model-invocation`, `allowed-tools`, `context: fork`) confirmed

**Review files:** `docs/plans/reviews/`
