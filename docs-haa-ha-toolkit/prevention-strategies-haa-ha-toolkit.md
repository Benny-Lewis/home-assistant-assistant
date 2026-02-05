---
title: "Prevention Strategies: Context Injection and Convention Discovery"
date: 2026-01-25
type: guidelines
related:
  - docs/plans/2026-01-25-feat-convention-discovery-system-plan.md
  - agents/ha-convention-analyzer.md
  - skills/ha-conventions/SKILL.md
---

# Prevention Strategies: Context Injection and Convention Discovery

## Problem Summary

Claude Code plugin skills were generating output (YAML automations, naming patterns, etc.) without knowing user preferences, conventions, or project-specific context. This led to:

- **Incorrect naming patterns** - IDs didn't follow user's established conventions
- **Wrong implementation choices** - Used inline delays instead of user's timer helper pattern
- **Wasted tokens and time** - Skills re-discovered or asked about context that should have been pre-loaded
- **Poor user experience** - Requiring 2+ manual corrections before acceptable output

**Root cause:** Skills had no way to access user context at initialization time.

## Solution Implemented

A **convention discovery and context injection system** that:

1. **Discovers** user conventions from existing config (automated)
2. **Stores** conventions as structured rules + examples (durable)
3. **Injects** conventions at skill load time via shell expansion (atomic)
4. **Validates** generated output against conventions (fail-fast)

---

## Prevention Strategies for Other Plugins

### Strategy 1: Identify Context Dependencies Early

**When designing a plugin, ask:**

| Question | Why It Matters | Example |
|----------|---|---------|
| What user conventions/preferences does this plugin need to know? | Prevents context gap discovery later | Naming patterns, file locations, API versions |
| Can those conventions vary per-user or per-project? | Determines storage scope | Home Assistant: naming varies by household |
| What happens if the plugin generates output without knowing conventions? | Reveals risk level | Completely wrong IDs, wasted tokens |
| Can conventions be auto-discovered? | Enables automation | Yes: analyze existing config files |

**Action:** Create a "context dependency inventory" as part of plugin design:

```markdown
## Context Dependencies for [Plugin Name]

### Required Context
- [ ] User preference A
  - Discovery method: [auto-detect from config / ask user / default]
  - Storage: [plugin settings / per-project config / environment]
  - Failure mode: [strict / fallback with warning / skip feature]

### Optional Context
- [ ] Enhancement A
  - Similar breakdown as above

### Risk Assessment
- Without this context, plugin quality: [critical / high / medium / low]
- User frustration level: [high / medium / low]
```

---

### Strategy 2: Implement Context Injection at Load Time

**DO:**
- Use shell expansion (`!` syntax in markdown) to inject context at skill load time
- This renders content BEFORE Claude sees it, guaranteeing context is present
- Inject context as markdown content (not hidden comments)
- Include fallback defaults for unconfigured users

**DON'T:**
- Rely on runtime file reads within skill execution
- Hide context in YAML frontmatter comments
- Assume context will be "remembered" across multiple skill invocations
- Ask for context during generation if it should have been pre-loaded

**Implementation pattern:**

```markdown
---
name: your-skill
description: Skill that uses context
allowed-tools: Read, Write, Bash
---

## Your Project's Configuration

!`cat .claude/your-plugin.md 2>/dev/null | head -50 || echo "## Default Configuration (no custom config found)"`

## Skill Process

Start with verification step that checks if context loaded properly.
```

**Why this works:**
- Shell expansion runs BEFORE Claude's execution environment
- Content is rendered into the markdown that Claude reads
- Context is visible and debuggable
- Fallback is automatic and clear

---

### Strategy 3: Fail-Fast on Low Confidence Context

**When auto-discovered context has low confidence, don't pretend certainty.**

**Patterns to implement:**

#### Confidence Levels

```yaml
confidence: high   # ≥80% of samples match AND ≥5 samples
confidence: medium # 50-79% match OR ≥80% but <5 samples
confidence: low    # <50% match OR <3 samples
confidence: none   # No discernible pattern
```

#### Fail-Fast Behavior

```markdown
## Step 0: Load and Verify Conventions

!`cat .claude/plugin-config.md 2>/dev/null | grep -A 5 "conventions:" || echo "NO CONVENTIONS CONFIGURED"`

[CRITICAL] Check output above:
- If "NO CONVENTIONS CONFIGURED" appears:
  → STOP here and ask user: "I don't know your conventions yet.
    Please run /setup-conventions first, or tell me to use defaults."
  → Do NOT generate output that might be wrong

- If confidence is `low` or `none`:
  → Add this banner to your output: "⚠️ Low confidence in detected patterns.
    Please review naming carefully."
  → Offer to re-run detection with user guidance
```

**Benefits:**
- Prevents incorrect output from being presented as authoritative
- Clearly communicates uncertainty to user
- Prompts explicit correction rather than silent failure
- Enables iterative refinement of detected patterns

---

### Strategy 4: Store Context as Rules + Examples, Not Pattern Strings

**DO:**
```yaml
conventions:
  separator: "_"              # Rule 1: What separator to use
  case: "snake_case"          # Rule 2: What case convention
  area_position: "prefix"     # Rule 3: Where area appears

  # Derived patterns from rules
  automation_id_pattern: "<area>_<trigger>_[if_<condition>]_<action>"

  # Concrete examples for validation
  examples:
    - id: "kitchen_motion_light_on"
      alias: "Kitchen: Motion → Light On"
```

**DON'T:**
```yaml
conventions:
  pattern: "<area>_<trigger>_<action>"  # Too brittle, overfits to data
```

**Why this matters:**

| Approach | Strength | Weakness |
|----------|----------|----------|
| Rules + Examples | Generalizes to new cases, resilient to edge cases | Requires more upfront analysis |
| Pattern strings only | Simple to store | Overfits to specific samples, breaks on variations |

**Example: Why rules win**

User has automations: `kitchen_motion_on`, `backyard_motion_on` (6 total)
Rules say: `<area>_<trigger>_<action>`

New automation: `basement_motion_light_on` (3 words, adds detail)
- **Rules approach:** Accepts it - matches the rules (area_trigger_action) ✓
- **Pattern string:** Might reject it if pattern was fitted to specific examples ✗

---

### Strategy 5: Design Convention Discovery as a User-Initiated Action

**Pattern to follow:**

1. **Separate skill/command for discovery** - Don't auto-run
   ```yaml
   disable-model-invocation: true  # Prevent Claude from randomly running this
   ```

2. **Low-permission discovery tool** - Read-only access
   ```yaml
   allowed-tools: Read, Grep, Glob  # No Bash, no destructive operations
   ```

3. **Explicit confirmation before saving** - Show diff if updating
   ```markdown
   ## Current Conventions
   [Show what's currently saved]

   ## Detected Changes
   [Show what analysis found]

   ## Your Choice
   - [Accept detected] [Keep existing] [Customize]
   ```

4. **Fork context for analysis** - Isolated execution
   ```yaml
   context: fork  # Don't pollute main conversation with config data
   ```

**Benefits:**
- Users don't accidentally trigger detection
- Prevents permission creep
- Analysis doesn't clutter conversation history
- Explicit control over when conventions change

---

### Strategy 6: Create Testable Convention Validation

**Validation checklist for any generated output:**

```markdown
## Validation Checklist

[ ] Naming Compliance
   - Generated ID matches user's pattern
   - Generated alias matches user's pattern
   - If enforce_conventions: true, reject non-compliant output

[ ] Context Usage Compliance
   - If timer helpers preferred, check long delays use timers
   - If strict mode enabled, enforce all conventions
   - Report any deviations before showing to user

[ ] Syntax Validation
   - Modern YAML syntax (triggers: not trigger:)
   - All entity IDs exist (or marked as [TBD: entity_name])
   - No deprecated Home Assistant syntax

[ ] If Any Check Fails
   - Identify the specific failure
   - Fix the output
   - Run validation again
   - Only proceed when all pass
```

**Red flags to catch in testing:**

- Generated output contradicts stored conventions
- Conventions showed as "high confidence" but output didn't match
- User had to correct the same type of error 2+ times
- Same issue appeared in multiple generated automations

---

### Strategy 7: Red Flags - Watch for These Patterns

#### In Plugin Design

| Red Flag | What It Means | Fix |
|----------|---------------|-----|
| "We'll just ask the user each time" | No context persistence | Implement discovery + storage |
| "Conventions don't matter for this plugin" | Misunderstanding user needs | Audit actual usage, ask users |
| "We can detect this at runtime" | Late binding of critical context | Move to load-time injection |
| "Skills will remember what I said" | Ignoring session-to-session context | Store in durable settings file |

#### In Implementation

| Red Flag | What It Means | Fix |
|----------|---------------|-----|
| File reads inside skill action | Context not injected at load time | Use shell expansion (`!` syntax) |
| Regex pattern strings only | Brittleness and overfitting | Add rule-based validation |
| "enforce: false" as default | No way to catch user errors | Make enforcement optional but visible |
| No validation section in skill | Silent failures | Add explicit checklist with fail-fast |
| Low-confidence patterns treated as certain | Misleading users | Add uncertainty banners |
| Skills ask "What's your convention?" multiple times | Discovery not happening | Run discovery once, store, inject |

#### In Testing

| Red Flag | What It Means | Fix |
|----------|---------------|-----|
| "Mostly works, user fixes the rest" | Design issue, not testing issue | Go back to strategy 1 |
| Manual corrections needed each session | Context not persisting | Implement persistence layer |
| Token waste on discovering context | Load-time injection not implemented | Use shell expansion |
| Same error type appears 2+ times | Validation not strict enough | Enhance validation checklist |

---

## Design Patterns to Follow

### Pattern 1: Shell Expansion for Context Injection

**When:** You have user-specific configuration that should always be available

**How:**
```markdown
---
name: skill-that-needs-context
allowed-tools: Read, Grep, Glob
---

## User's Configuration

!`cat .claude/settings.md 2>/dev/null | grep -A 20 "config:" || echo "Default configuration"`

## Skill Process

[Step 1: Verify config loaded above, fail-fast if missing]
[Rest of skill process uses config from above]
```

**Why it works:**
- Runs during markdown preprocessing, before Claude execution
- Content is rendered and visible (not hidden)
- Automatic fallback to defaults
- Cannot be accidentally skipped

### Pattern 2: Confidence-Based Behavior Adjustment

**When:** Context is auto-discovered and might be incomplete

**How:**
```markdown
## Detected Conventions

Confidence: {{ confidence }}

{% if confidence == "high" %}
  These patterns are reliable. Using them strictly.
{% elsif confidence == "medium" %}
  These patterns show 50-79% consistency. Will use but note uncertainty.
{% elsif confidence == "low" %}
  ⚠️ Low confidence. Recommend running /reconfigure.
{% endif %}
```

**Why it works:**
- Communicates uncertainty explicitly
- Triggers appropriate user action based on confidence
- Prevents over-confident wrong output

### Pattern 3: Read-Only Discovery Agent

**When:** You need to analyze user files without modifying them

**How:**
```yaml
---
name: analyzer-agent
description: Analyze existing config to extract patterns
allowed-tools: Read, Grep, Glob    # No Bash, no Write
model: sonnet
context: fork                       # Isolated execution
---
```

**Why it works:**
- Prevents accidental modifications
- Keeps conversation clean (fork context)
- Analysis is predictable and auditable
- Easy to re-run for updated detection

### Pattern 4: Explicit User Confirmation Before Persistence

**When:** Automatically detected context will be saved permanently

**How:**
```markdown
## Detected Convention

Pattern: {{ detected_pattern }}
Examples: {{ examples }}
Confidence: {{ confidence }}

Current saved convention:
{{ current_convention }}

## Your choice:
- [✓] Accept detected pattern
- [→] Keep current pattern
- [!] Customize manually
- [?] Need help deciding
```

**Why it works:**
- Users understand what's being saved
- Prevents silent overwrites of working conventions
- Builds trust in the system
- Creates opportunities for education/refinement

---

## Testing Approaches

### Test Case 1: Fresh Install (No Conventions)

**Setup:** New user, no existing configuration

**Test steps:**
1. Plugin loads without conventions configured
2. Skill gracefully falls back to defaults
3. Output mentions uncertainty: "Using default conventions; run /setup to detect yours"
4. User can still create valid output with defaults

**Pass criteria:**
- No errors from missing conventions
- Clear guidance on how to set up
- Generated output is reasonable (even if not optimized)

### Test Case 2: High-Confidence Detection

**Setup:** User has 15+ automations following consistent pattern

**Test steps:**
1. Run convention discovery
2. Analyze output for confidence level (should be "high")
3. Generate new automation using discovered patterns
4. Verify output matches detected patterns exactly
5. Re-run discovery - should find same patterns

**Pass criteria:**
- Confidence shows as "high"
- Generated output perfectly matches patterns
- No manual corrections needed
- Token cost is minimal (conventions pre-loaded)

### Test Case 3: Mixed/Legacy Conventions

**Setup:** User has some old automations + new ones with different patterns

**Test steps:**
1. Run convention discovery
2. Verify output shows BOTH patterns with counts
3. Verify confidence shows as "medium"
4. Verify output includes uncertainty banner
5. User chooses which pattern to standardize on
6. Verify choice is saved and respected in future generation

**Pass criteria:**
- Both patterns clearly reported
- Confidence is medium (not falsely high)
- User can choose which to standardize on
- Future generation respects choice

### Test Case 4: Validation Catches Errors

**Setup:** Skills generate output that doesn't match conventions

**Test steps:**
1. Manually edit a skill to ignore conventions (for testing)
2. Generate output that violates conventions
3. Validation checklist should catch the error
4. Error is clearly reported before showing to user
5. If enforce_conventions: true, generation is rejected

**Pass criteria:**
- Violations are caught every time
- Error message is clear
- User can choose to fix or override (with warning)
- No invalid output is presented as correct

### Test Case 5: Context Persistence Across Sessions

**Setup:** User configures conventions in session 1

**Test steps:**
1. Configure conventions via /setup-conventions
2. Generate automation (uses conventions)
3. Close Claude Code, start new session
4. Generate another automation
5. Verify new automation uses SAME conventions from session 1

**Pass criteria:**
- Conventions are loaded from settings file (not re-asked)
- Token cost is O(conventions_size), not O(detection_analysis)
- Same patterns consistently applied
- User doesn't have to re-configure

### Test Case 6: Updating Conventions

**Setup:** User had conventions, config has changed significantly

**Test steps:**
1. User runs /setup-conventions again
2. Detect new patterns from updated config
3. Show diff: old vs new conventions
4. Ask for explicit confirmation to update
5. If user confirms, save new conventions
6. Verify next generation uses new patterns

**Pass criteria:**
- Diff clearly shows changes
- Requires explicit confirmation (not auto-save)
- New patterns are actually used
- Old conventions are completely replaced (no merge confusion)

---

## Implementation Checklist for New Plugins

Use this checklist when preventing context-injection issues in other plugins:

### Discovery Phase
- [ ] Identify all user context dependencies (Strategy 1)
- [ ] Decide if each dependency should be auto-discovered or user-provided
- [ ] Create analyzer agent/skill for auto-discovery (read-only tools)
- [ ] Design confidence calculation (Strategy 3)
- [ ] Create settings schema for storing context (Strategy 4)

### Injection Phase
- [ ] Implement shell expansion in skills (Strategy 2)
- [ ] Add Step 0 verification (fail-fast on missing context)
- [ ] Add uncertainty banner for low-confidence context
- [ ] Create fallback defaults for unconfigured users

### Validation Phase
- [ ] Create validation checklist for generated output
- [ ] Map output back to conventions (did generation respect them?)
- [ ] Implement enforcement modes (strict vs permissive)
- [ ] Add clear error messages for validation failures

### Storage Phase
- [ ] Define settings file schema (rules + examples, not patterns only)
- [ ] Implement save/update logic with user confirmation
- [ ] Add ability to view current conventions
- [ ] Implement re-detection with diff display

### Testing Phase
- [ ] Test fresh install (Strategy 7, red flags)
- [ ] Test high-confidence detection (Test Case 2)
- [ ] Test mixed conventions (Test Case 3)
- [ ] Test validation catches errors (Test Case 4)
- [ ] Test persistence across sessions (Test Case 5)
- [ ] Test update workflow (Test Case 6)

---

## Common Anti-Patterns to Avoid

### Anti-Pattern 1: Runtime Context Discovery

```markdown
## ❌ DON'T DO THIS

## Skill Process

1. Ask user: "What's your naming pattern?"
2. User responds in chat
3. Generate output using response
4. Next session, ask again (context lost)
```

**Problem:** Context doesn't persist, requires re-entry

**Solution:** Store context in settings file, inject at load time

### Anti-Pattern 2: Hidden/Commented Configuration

```markdown
## ❌ DON'T DO THIS

<!-- User config: kitchen_motion_light_on -->
<!-- Confidence: high -->

[Skill process that somehow uses these commented values]
```

**Problem:** Context is not actually visible to Claude, only to markdown parser

**Solution:** Use shell expansion to inject context into visible markdown

### Anti-Pattern 3: Pattern-Only Storage

```yaml
## ❌ DON'T DO THIS

conventions:
  id_pattern: "<area>_<trigger>_<action>"
  # Pattern is overfitted to specific examples
```

**Problem:** Brittle, breaks on edge cases, doesn't generalize

**Solution:** Store rules + examples that support pattern validation

### Anti-Pattern 4: Silent Failure on Missing Context

```markdown
## ❌ DON'T DO THIS

[Load conventions]
[If not found, just use hardcoded defaults]
[Generate output without mentioning uncertainty]
```

**Problem:** User thinks output is convention-respecting when it might not be

**Solution:** Fail fast with clear message, ask user to configure or confirm defaults

### Anti-Pattern 5: Validation Without Enforcement

```markdown
## ❌ DON'T DO THIS

[Generate output that violates conventions]
[Note in hidden comment: "This doesn't match conventions"]
[Show user the output anyway]
```

**Problem:** Violations go unnoticed, user has to manually correct

**Solution:** Fail fast, report violations clearly, optionally refuse to show non-compliant output

---

## Troubleshooting Guide

### Issue: Generated output ignores user conventions

**Diagnostic questions:**
1. Is context being injected at skill load time? (Check shell expansion)
2. Is context being validated in Step 0? (Check fail-fast logic)
3. Is confidence level appropriate? (Check detection)
4. Are conventions actually being stored? (Check settings file)

**Solution path:**
1. Verify shell expansion renders correctly: look at skill in Claude interface
2. Add explicit logging: "Loaded conventions: [show what was loaded]"
3. Check if conventions file exists and has correct format
4. Re-run discovery if confidence is low

### Issue: Users have to re-enter conventions each session

**Diagnostic questions:**
1. Are conventions being persisted to a file? (Check storage)
2. Is the settings file in the right location? (Check settings schema)
3. Is the file being read at skill load time? (Check injection)

**Solution path:**
1. Verify settings file path is correct and consistent
2. Add debug output: "Loading from [path]: [success/fail]"
3. Check file permissions (should be readable by Claude Code)
4. Test persistence across multiple CLI sessions

### Issue: Confidence level is always "medium" or "low"

**Diagnostic questions:**
1. Is sample size too small? (Check detection agent)
2. Are patterns actually consistent? (Manual review)
3. Is confidence calculation formula wrong? (Check Strategy 3)
4. Is mixing/legacy detection triggering false negatives?

**Solution path:**
1. Show user the actual breakdown: "8/12 match pattern A, 4/12 match pattern B"
2. Let user choose which pattern to standardize on
3. Re-run detection after user makes changes (should increase confidence)
4. If truly mixed, offer to migrate old automations

### Issue: Validation catches errors too late (after showing user)

**Diagnostic questions:**
1. Is validation running before output generation? (Check step order)
2. Are validation checks comprehensive? (Check validation checklist)
3. Is validation result being shown to user? (Check output formatting)

**Solution path:**
1. Move validation to earlier in skill process
2. Add comprehensive checklist before user-facing output
3. Show validation results clearly: pass/fail for each check
4. Refuse to show non-compliant output if enforce_conventions: true

---

## Success Metrics

### For Convention System Implementation

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Manual corrections needed | 0 per session | Log corrections in test sessions |
| Token cost per generation | -50% vs without conventions | Compare before/after token counts |
| Time to first valid output | <3 minutes | Measure from skill invocation to deployment |
| User confidence in output | High | Survey or observation |
| Discovery confidence | ≥80% for established users | Check detected confidence levels |

### For Preventing Similar Issues

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Context identified early | 100% of plugins | Checklist in design phase |
| Context persistence | Works across sessions | Test Case 5 |
| Validation effectiveness | Catches 95%+ of violations | Test Case 4 |
| User clarity on conventions | High (easy to understand) | Show conventions output to users |
| Re-detection accuracy | Same patterns detected each time | Test Case 2, re-run detection |

---

## References

- **Implementation:** `/skills/ha-conventions/SKILL.md` - Full skill implementation
- **Agent:** `/agents/ha-convention-analyzer.md` - Pattern detection agent
- **Plan:** `/docs/plans/2026-01-25-feat-convention-discovery-system-plan.md` - Full technical plan
- **Settings schema:** `/templates/home-assistant-assistant.md` - Convention storage format
- **Test results:** TBD - Add test session logs here after implementation
