---
title: "Convention Discovery System for Claude Code Plugins"
category: "architecture-issues"
tags:
  - naming-conventions
  - pattern-detection
  - shell-expansion
  - fail-fast
  - plugin-architecture
  - context-injection
module: "home-assistant-assistant"
symptoms:
  - "Plugin ignored user naming conventions when generating output"
  - "Generated automations used inline delays instead of timer helpers"
  - "Skills had no mechanism to detect patterns from existing configuration"
  - "Wasted tokens exploring for specs that should have been pre-loaded"
date_documented: "2026-01-25"
---

# Convention Discovery System for Claude Code Plugins

## Problem

A Claude Code plugin for Home Assistant automation was generating output that ignored the user's established naming patterns and preferences.

**Observed symptoms:**
- Plugin ignored a 1,800-line naming spec entirely
- Required 2 user corrections before producing correct output
- Wasted 41.5k tokens and ~12 minutes exploring for specs
- Used inline `delay:` instead of established timer helper patterns
- Generated IDs and aliases that didn't match existing conventions

**Root cause:** Skills didn't know about or load user conventions before generating YAML. There was no mechanism to detect, store, or inject user preferences into the generation workflow.

## Solution

Implemented a **Convention Discovery System** with four components:

### 1. Convention Analyzer Agent

A read-only subagent that analyzes existing configuration files to detect patterns.

**File:** `agents/ha-convention-analyzer.md`

```yaml
---
name: ha-convention-analyzer
tools:
  - Read
  - Grep
  - Glob
model: sonnet
---
```

**Responsibilities:**
- Read `automations.yaml` and `timer.yaml`
- Extract all `id:` and `alias:` values
- Detect patterns (separators, area prefixes, trigger/action suffixes)
- Calculate confidence levels (high ≥80% AND ≥5 samples)
- Handle mixed/legacy conventions gracefully

### 2. Convention Discovery Skill

User-facing skill for running detection and confirming patterns.

**File:** `skills/ha-conventions/SKILL.md`

```yaml
---
name: ha-conventions
disable-model-invocation: true
allowed-tools: Read, Grep, Glob
---
```

**Key design decisions:**
- `disable-model-invocation: true` prevents Claude from randomly triggering detection
- Read-only tools prevent accidental modifications during analysis
- User confirmation required before saving conventions

### 3. Convention Storage Schema

Stores detected patterns as **rules + examples** (not just pattern strings).

**File:** `.claude/home-assistant-assistant.md`

```yaml
conventions:
  # Rules (more robust than pattern strings)
  separator: "_"
  case: "snake_case"
  area_position: "prefix"
  condition_prefix: "if_"

  # Derived patterns
  automation_id_pattern: "<area>_<trigger>_[if_<condition>]_<action>"
  automation_alias_pattern: "<Area>: <Trigger> [If <Condition>] → <Action>"

  # Behavior preferences
  use_timer_helpers: true
  timer_threshold_seconds: 30

  # Detection metadata
  confidence: "high"
  detected_from_existing: true
```

**Why rules + examples?** Rules like `separator: "_"` are harder to overfit from messy data than trying to extract a complete pattern string.

### 4. Shell Expansion Context Injection

Skills inject conventions at **load time** using shell expansion.

**File:** `skills/ha-automations/SKILL.md`

```markdown
## Your Project's Conventions

!`awk '/^---$/{if(++n==2)exit}1' .claude/home-assistant-assistant.md 2>/dev/null || echo "No conventions configured - using defaults"`
```

**Why shell expansion?**
- The `!`command`` syntax runs at skill load time (preprocessing)
- Claude receives already-rendered content with actual conventions
- No runtime file reads needed - data is pre-loaded
- Graceful fallback if file doesn't exist

### 5. Fail-Fast Step 0

Skills verify conventions are loaded before generating output.

```markdown
0. **Verify conventions loaded** (CRITICAL - be atomic)
   - Check if conventions section appears above
   - [CRITICAL] If "No conventions configured" shown, STOP and ask:
     "Please run `/ha-conventions` first, or tell me to use defaults."
   - If confidence is `low`, add uncertainty banner to output
```

## Why This Works

1. **Load-time injection** - Conventions are pre-loaded via shell expansion, not read at runtime
2. **Fail-fast verification** - Skills won't proceed without knowing conventions
3. **Rules over patterns** - Storing rules (separator, case) is more robust than pattern strings
4. **Read-only detection** - Analyzer uses only Read/Grep/Glob, can't cause side effects
5. **User confirmation** - Discovery requires explicit user approval before saving
6. **Graceful degradation** - Works with defaults if conventions aren't configured

## Results

| Metric | Before | After |
|--------|--------|-------|
| User corrections needed | 2+ | 0 |
| Token usage | ~41.5k | ~20k |
| Time to completion | ~12 min | ~4 min |
| Naming accuracy | Low | High |

## Prevention Strategies

### For Other Plugin Developers

1. **Identify context dependencies early** - What user preferences affect your output?
2. **Implement context injection at load time** - Use `!` shell expansion, not runtime reads
3. **Fail-fast on missing context** - Don't generate with wrong assumptions
4. **Store rules, not just patterns** - Rules are more robust than derived strings
5. **Make discovery user-initiated** - Use `disable-model-invocation: true`
6. **Use read-only tools for analysis** - Analyzer agents shouldn't have write access

### Red Flags

- Skill generates output without checking user preferences
- Hardcoded patterns instead of configurable conventions
- Runtime file reads instead of load-time injection
- No fallback when preferences aren't configured
- Analysis agents with write permissions

## Related Documentation

- **Brainstorm:** `docs/brainstorms/2026-01-25-convention-discovery-system-brainstorm.md`
- **Plan:** `docs/plans/2026-01-25-feat-convention-discovery-system-plan.md`
- **Plan Reviews:** `docs/plans/reviews/` (Claude, ChatGPT, Gemini feedback)

## Files Changed

| File | Action | Purpose |
|------|--------|---------|
| `templates/home-assistant-assistant.md` | Modified | Added conventions schema |
| `agents/ha-convention-analyzer.md` | Created | Pattern detection agent |
| `skills/ha-conventions/SKILL.md` | Created | Discovery workflow skill |
| `skills/ha-automations/SKILL.md` | Modified | Shell expansion + validation |
| `skills/ha-automations/references/common-patterns.md` | Modified | Timer helper patterns |
