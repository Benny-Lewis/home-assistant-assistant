# Convention Discovery System Plan: Comparison to Claude Code Best Practices

## Executive Summary

Your plan is **well-aligned** with Claude Code's extensibility patterns and demonstrates sophisticated understanding of the architecture. There are a few areas where tighter alignment with official patterns could improve reliability and maintainability.

---

## Component-by-Component Analysis

### 1. `/ha-conventions` Command ✅ Strong Alignment

**Your approach:**
```yaml
---
name: ha-conventions
description: Detect and configure naming conventions for your Home Assistant setup
---
```

**Best practices alignment:**
- ✅ User-initiated (slash command) — correct pattern for one-time setup tasks
- ✅ Interactive confirmation flow before saving
- ✅ Offers sensible defaults when no patterns detected
- ✅ Stores configuration in a persistent location (`.claude/home-assistant-assistant.md`)

**Minor improvements:**
- Consider using gerund form: `detecting-conventions` or `convention-detection` per naming conventions
- Description should include *when* to use it: "Detect and configure naming conventions for your Home Assistant setup. **Use when setting up the plugin for the first time or when your naming patterns change.**"

---

### 2. `ha-convention-analyzer` Subagent ✅ Excellent Pattern

**Your approach:**
```yaml
---
name: ha-convention-analyzer
description: Analyzes existing Home Assistant configuration to detect naming patterns
tools: Bash, Read, Grep
model: sonnet
context: fork
---
```

**Best practices alignment:**
- ✅ `context: fork` — isolates exploration from main conversation (critical for large config analysis)
- ✅ Read-only tools (`Bash, Read, Grep`) — appropriate constraint for analysis-only task
- ✅ Model selection (`sonnet`) — cost-efficient for pattern detection vs Opus
- ✅ Returns structured output back to command

**This is exactly the recommended pattern** from Anthropic's docs: "Subagents maintain separate context from the main agent, preventing information overload and keeping interactions focused. This isolation ensures that specialized tasks don't pollute the main conversation context with irrelevant details."

**One consideration:** "Subagents cannot spawn other subagents" — your plan correctly keeps this single-level.

---

### 3. Skills Integration — Step 0 Pattern ⚠️ Needs Refinement

**Your approach:**
```markdown
## Process

0. **Load conventions**
   - Read `.claude/home-assistant-assistant.md`
   - Extract the `conventions:` section
   - If no conventions configured:
     - Inform user: "No naming conventions configured."
     - Suggest: "Run `/ha-conventions` to detect..."
```

**Issue:** Skills are *model-invoked*, not *user-invoked*. A skill that starts by reading a config file adds latency to every invocation.

**Best practice:** "Skills are reusable, filesystem-based resources that provide Claude with domain-specific expertise... Skills load on-demand and eliminate the need to repeatedly provide the same guidance across multiple conversations."

**Recommended refinement:**

Instead of having the skill dynamically read conventions at runtime, inject the conventions into the skill's context window via **dynamic frontmatter** or **shell expansion**:

```yaml
---
name: ha-automations
description: Create Home Assistant automations following your naming conventions
---

## Your Conventions

!`cat .claude/home-assistant-assistant.md | grep -A 20 "conventions:"`

## Instructions
...
```

The `!` syntax runs the command at skill load time, not execution time. Per the docs: "This is preprocessing, not something Claude executes. Claude only sees the final result."

---

### 4. Settings Storage Schema ✅ Good, Consider Alternatives

**Your approach:** YAML frontmatter in `.claude/home-assistant-assistant.md`

```yaml
---
conventions:
  automation_id_pattern: "<area>_<trigger>_[if_<condition>]_<action>"
  use_timer_helpers: true
  timer_threshold_seconds: 30
---
```

**Best practices:**
- ✅ Human-readable YAML format
- ✅ Location in `.claude/` directory is correct
- ✅ Sensible defaults documented

**Alternative consideration:** Claude Code's official pattern for plugin settings uses the `templates/` directory with YAML frontmatter, which you're already following. However, for *runtime configuration* that changes frequently, some teams use a separate `settings.json` file that's easier to parse programmatically.

---

### 5. Progressive Disclosure Pattern ✅ Properly Applied

**Your approach:** SKILL.md references external files:
- `references/common-patterns.md`
- Timer pattern documentation
- Naming requirements section

**This aligns perfectly with the progressive disclosure principle:** "The context window is a public good... Not every token in your Skill has an immediate cost. At startup, only the metadata (name and description) from all Skills is pre-loaded. Claude reads SKILL.md only when the Skill becomes relevant, and reads additional files only as needed."

**Your SKILL.md structure:**
- ✅ Core instructions in main file
- ✅ Pattern library in `references/`
- ✅ Domain-specific guidance (timer vs delay decision tree)

**Keep it under 500 lines:** "Keep SKILL.md body under 500 lines for optimal performance. If your content exceeds this, split it into separate files."

---

### 6. Validation/Feedback Loop Pattern ⚠️ Missing from Plan

**Gap identified:** Your plan doesn't include a validation step after generating YAML.

**Best practice:** "Implement feedback loops... Common pattern: Run validator → fix errors → repeat. This pattern greatly improves output quality."

**Recommended addition:**

```markdown
## Validation Process

After generating automation YAML:
1. Run: `python scripts/validate_automation.py output.yaml`
2. If validation fails:
   - Review error messages
   - Fix the YAML
   - Run validation again
3. Only proceed to /ha-deploy when validation passes
```

You could create a `validate_automation.py` that checks:
- YAML syntax validity
- Naming convention compliance
- Required fields present
- Entity IDs match expected patterns

---

### 7. Confidence Levels ✅ Smart Design

**Your approach:**
| Confidence | Criteria |
|------------|----------|
| High | ≥80% match AND ≥5 samples |
| Medium | 50-79% match OR ≥80% but <5 samples |
| Low | <50% match OR <3 samples |

**This is well-considered.** Having explicit thresholds prevents the analyzer from over-confidently suggesting patterns from minimal data.

---

## Architecture Comparison Table

| Component | Your Plan | Claude Code Pattern | Alignment |
|-----------|-----------|---------------------|-----------|
| Convention setup | `/ha-conventions` command | User-invoked slash command | ✅ Correct |
| Pattern detection | `ha-convention-analyzer` subagent | `context: fork` subagent | ✅ Correct |
| Convention storage | YAML frontmatter in settings file | Markdown with YAML frontmatter | ✅ Correct |
| Skill loading | Step 0: Read conventions | Shell expansion (`!`) at load time | ⚠️ Refine |
| Progressive disclosure | References in `references/` | Separate files loaded on-demand | ✅ Correct |
| Validation loop | Not specified | Validator → fix → repeat | ⚠️ Add |
| Tool restrictions | Read-only for analyzer | `allowed-tools` in frontmatter | ✅ Implicit |

---

## Recommended Enhancements

### 1. Add Shell Expansion for Convention Loading

```yaml
---
name: ha-automations
description: Create Home Assistant automations with proper naming and timer patterns
---

## Your Project's Conventions

!`cat .claude/home-assistant-assistant.md 2>/dev/null | head -50 || echo "No conventions configured - using defaults"`

## Default Conventions (if none configured)
...
```

### 2. Add Validation Scripts

Create `scripts/validate_automation.py`:
```python
#!/usr/bin/env python3
"""Validate generated automation YAML against conventions."""

import sys
import yaml
import re

def validate(filepath, conventions_path):
    # Load conventions
    # Validate naming patterns
    # Check for timer helper usage where required
    # Return specific error messages
    pass
```

### 3. Enhance Subagent Description

```yaml
---
name: ha-convention-analyzer
description: >
  Analyzes existing Home Assistant configuration to detect naming patterns 
  and conventions. Use when running /ha-conventions command. Returns 
  structured patterns for automation IDs, aliases, and timer usage with 
  confidence levels.
tools: Bash, Read, Grep
model: sonnet
---
```

### 4. Add Workflow Checklist Pattern

Per best practices: "For particularly complex workflows, provide a checklist that Claude can copy into its response and check off as it progresses."

```markdown
## Automation Creation Workflow

Copy this checklist and track progress:

```
Automation Progress:
- [ ] Step 1: Load conventions from settings
- [ ] Step 2: Resolve entity IDs via ha-entity-resolver
- [ ] Step 3: Determine timer vs delay based on duration
- [ ] Step 4: Generate automation YAML
- [ ] Step 5: Validate against conventions
- [ ] Step 6: If timer needed, generate timer.yaml entry
- [ ] Step 7: Present to user for review
```
```

---

## Summary

**Strengths of your plan:**
- Sophisticated use of `context: fork` for convention analysis
- Proper separation of concerns (command → subagent → skill)
- Clear confidence level criteria
- Good progressive disclosure structure
- Timer vs delay decision logic is well-specified

**Areas to refine:**
1. Use shell expansion (`!`) instead of runtime reads for convention loading
2. Add validation feedback loop with scripts
3. Include workflow checklists for complex operations
4. Enhance descriptions with "when to use" clauses

Your plan demonstrates strong understanding of Claude Code's architecture. The main refinements are about optimizing token efficiency and adding verification steps.
