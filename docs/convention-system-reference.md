---
title: "Convention System Quick Reference"
date: 2026-01-25
type: reference-card
related:
  - docs/prevention-strategies.md
  - docs/context-injection-guide.md
---

# Convention System Quick Reference

## Core Concepts

### What is a Convention?
A user-specific pattern or preference that should be respected consistently throughout generated output.

**Examples:**
- Naming pattern: `<area>_<trigger>_<action>` vs `<area>-<trigger>-<action>`
- Implementation choice: Use timer helpers vs inline delays
- Feature preference: Use feature X vs feature Y
- Entity naming: Capitalization, separators, order

### Why Conventions Matter
Without conventions, plugins generate output that:
- Doesn't match existing patterns
- Requires manual correction (wastes tokens and time)
- Breaks HA automations if patterns are critical
- Makes users lose trust in the plugin

### The Convention Lifecycle
```
User has config → Analyze patterns → Detect conventions →
Store in settings → Inject into skills → Validate output → Done
```

---

## Implementation Checklist

### Quick Start (30 minutes)
- [ ] Create `.claude/plugin-name.md` schema with `conventions:` section
- [ ] Add shell expansion to skill: `!`cat .claude/plugin-name.md`
- [ ] Add Step 0: Load conventions, fail-fast if missing
- [ ] Document what conventions are required

### Full Implementation (2-4 hours)
- [ ] Create convention discovery agent
- [ ] Create setup-conventions skill
- [ ] Implement pattern analysis logic
- [ ] Add validation checklist
- [ ] Write test cases
- [ ] Document configuration options

---

## Essential Code Patterns

### Pattern 1: Shell Expansion for Loading Conventions

```markdown
## Your Configuration

!`cat .claude/your-plugin.md 2>/dev/null | head -100 || echo "No config found"`

## Step 0: Verify Conventions Loaded

[Check if conventions section appeared above]
```

**Why:** Content is rendered into markdown before Claude execution, guaranteeing availability.

### Pattern 2: Fail-Fast on Missing Context

```markdown
[CRITICAL] Is there a conventions: section above?
- YES → Use those conventions for all generation
- NO → STOP and ask user to run /setup-conventions first
- ERROR → Show parsing error and ask to fix
```

**Why:** Prevents silent generation of wrong output.

### Pattern 3: Store Rules + Examples

```yaml
conventions:
  # Rules (generalizable)
  naming_rules:
    separator: "_"
    case: "snake_case"
    area_position: "prefix"

  # Derived pattern (from rules above)
  pattern: "<area>_<trigger>_<action>"

  # Examples (concrete reference)
  examples:
    - id: "kitchen_motion_light_on"
```

**Why:** Rules generalize to new cases; examples provide validation reference.

### Pattern 4: Validate Output Before Showing

```markdown
## Validation Checklist

- [ ] Generated ID matches pattern?
- [ ] Feature preferences respected?
- [ ] YAML syntax valid?
- [ ] All required fields present?

If any fail → Regenerate with fixes → Re-validate
```

**Why:** Catches violations before user sees output.

### Pattern 5: Confidence-Based Output Modification

```markdown
{% if confidence == "high" %}
  These conventions are accurate and reliable.
{% elsif confidence == "medium" %}
  ⚠️ These conventions have medium confidence. Please review.
{% else %}
  ⚠️ Low confidence conventions. Please review carefully.
{% endif %}
```

**Why:** Communicates reliability clearly to user.

---

## Common Convention Types

### Naming Conventions

| Type | Examples | Storage | Auto-detect |
|------|----------|---------|------------|
| Entity ID pattern | `<area>_<type>` | Pattern + rules | Yes |
| Separator | `_` vs `-` | Single character | Yes |
| Case | snake_case vs kebab-case | Enum | Yes |
| Area position | prefix vs suffix | Enum | Yes |
| Prefix/suffix | `if_`, `has_` | List of prefixes | Yes |

**Storage format:**
```yaml
naming_rules:
  entity_id_pattern: "<area>_<trigger>_[if_<condition>]_<action>"
  separator: "_"
  case: "snake_case"
  area_position: "prefix"
  condition_prefix: "if_"
```

### Behavior Conventions

| Type | Examples | Storage | Auto-detect |
|------|----------|---------|------------|
| Feature choice | Use X vs Y | Boolean or enum | Partial |
| Threshold values | Timer > 30s | Integer | No |
| Default values | Mode = "single" | String | No |
| Enforcement level | Strict vs permissive | Boolean | No |

**Storage format:**
```yaml
behavior:
  use_timer_helpers: true
  timer_threshold_seconds: 30
  default_automation_mode: "single"
  enforce_conventions: false
```

### Detection Metadata

| Field | Purpose | Example |
|-------|---------|---------|
| `detected_from_existing` | Was this auto-detected? | `true` or `false` |
| `last_detected` | When was it detected? | `2026-01-25` |
| `confidence` | How confident? | `high`, `medium`, `low`, `none` |
| `examples` | Reference data | List of real examples |

**Storage format:**
```yaml
metadata:
  detected_from_existing: true
  last_detected: "2026-01-25"
  confidence: "high"
  examples:
    - id: "kitchen_motion_light_on"
      alias: "Kitchen: Motion → Light On"
```

---

## Configuration File Format

### Full Schema Example

```yaml
---
# Regular plugin settings
plugin_url: "..."
api_key: "..."

# Convention settings (populated by setup-conventions skill)
conventions:
  # Naming rules
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
  default_automation_mode: "single"
  enforce_conventions: false

  # Detection metadata
  detected_from_existing: true
  last_detected: "2026-01-25"
  confidence: "high"

  # Examples for validation
  examples:
    - id: "kitchen_motion_light_on"
      alias: "Kitchen: Motion → Light On"
    - id: "backyard_door_open_if_dark_floodlight_on"
      alias: "Backyard: Door Open If Dark → Floodlight On"
---
```

### Partial/Default State

If conventions not configured, skill should work with defaults:

```yaml
conventions: {}  # Empty, will use built-in defaults

# OR in Step 0, detect empty and explain:
# "No conventions configured. Using Home Assistant defaults.
#  Run /setup-conventions to auto-detect your patterns."
```

---

## Confidence Levels

### High Confidence (≥80% match AND ≥5 samples)
```yaml
Confidence: high (12/15 entities match pattern)
```
- Meaning: Pattern is reliable
- Action: Use pattern with confidence, no warnings needed
- Example: 12 automations use `<area>_<trigger>_<action>`, 3 outliers

### Medium Confidence (50-79% match OR ≥80% but <5 samples)
```yaml
Confidence: medium (7/10 entities match pattern)
OR
Confidence: medium (4/4 entities match, but only 4 samples)
```
- Meaning: Pattern exists but not dominant
- Action: Use pattern but add ⚠️ uncertainty banner
- Example: 7 automations use new pattern, 3 use old pattern

### Low Confidence (<50% match OR <3 samples)
```yaml
Confidence: low (2/10 entities match, too few samples)
```
- Meaning: No clear pattern, or not enough data
- Action: Ask user to confirm or provide pattern manually
- Example: Each automation has unique naming style

### None (All unique, no pattern)
```yaml
Confidence: none (each entity has unique pattern)
```
- Meaning: Cannot detect pattern from existing config
- Action: Offer defaults and let user customize
- Example: No existing automations, fresh config

---

## Discovery Algorithm

### Basic Pattern Detection

```
For each entity or config section:
  Extract relevant fields (id, alias, etc.)

For each field:
  Count separator characters:
    "_" appears 12 times
    "-" appears 0 times
    " " appears 2 times
  → Dominant separator: "_"

  Check case patterns:
    snake_case appears 12 times
    UPPER appears 0 times
  → Dominant case: "snake_case"

  Check area position:
    [area]_<rest> pattern: 12 matches
    <rest>_[area] pattern: 0 matches
  → Area position: "prefix"

Calculate confidence:
  matched = 12 (entity count matching primary pattern)
  total = 15 (total entities analyzed)
  pct = matched / total = 80%

  if pct >= 80% and matched >= 5:
    confidence = "high"
  elif pct >= 50%:
    confidence = "medium"
  else:
    confidence = "low"
```

### Handling Mixed Patterns

```
Pattern A: <name>_<type> (5 entities, 33%)
Pattern B: <area>_<type>_<name> (10 entities, 67%)

Result:
- Primary: Pattern B (67%, dominant)
- Secondary: Pattern A (33%, legacy)
- Confidence: medium (not unanimous)
- Recommendation: "Use Pattern B for new entities"
```

---

## Testing Scenarios

### Test 1: Fresh Install
```
No config file exists
→ Skill loads defaults
→ Output is valid but not optimized
→ User is shown "Run /setup-conventions"
```

### Test 2: High Confidence
```
15 entities, all match pattern
→ Detected with "high" confidence
→ Generated output matches perfectly
→ Zero manual corrections needed
```

### Test 3: Mixed Conventions
```
10 entities with pattern A, 5 with pattern B
→ Detected with "medium" confidence
→ User chooses which to standardize on
→ Future generation uses chosen pattern
```

### Test 4: Validation Catches Errors
```
Generated ID: "light_kitchen" (wrong order)
Expected pattern: "<area>_<trigger>_<action>"
→ Validation fails
→ Output regenerated
→ User never sees bad output
```

### Test 5: Persistence
```
Session 1: Save conventions
Session 2: Load same conventions
→ No re-ask, no re-detect
→ Same patterns applied
→ No wasted tokens
```

### Test 6: Update Workflow
```
Old conventions: <area>_<action>
New detection: <area>_<trigger>_<action>
→ Diff shown
→ User must confirm change
→ Old conventions completely replaced
```

---

## Debugging Checklist

### Conventions Not Loading
- [ ] Check file path in shell expansion
- [ ] Check file exists: `ls .claude/plugin-name.md`
- [ ] Check YAML syntax: `cat .claude/plugin-name.md`
- [ ] Check permissions: file must be readable
- [ ] Run `/setup-conventions` to recreate

### Output Ignoring Conventions
- [ ] Does Step 0 fail-fast? Should STOP if missing
- [ ] Are conventions actually loaded? Look at skill markdown
- [ ] Does validation run? Should catch violations
- [ ] Is confidence too low? Check if warning banner added

### Confidence Wrong
- [ ] Count actual matches vs total manually
- [ ] Check confidence formula is correct
- [ ] For small samples (< 5), medium is expected
- [ ] Show user the actual breakdown

### User Loses Work After Update
- [ ] Is diff shown before save? Must show old vs new
- [ ] Does confirmation require explicit yes? Cannot be silent
- [ ] Are old conventions completely replaced? Check for merge bugs
- [ ] Is backup created? Consider adding undo

---

## One-Liner Recipes

### Check Conventions in Settings File
```bash
cat .claude/your-plugin.md | grep -A 20 "conventions:"
```

### Verify Skill Has Conventions Loaded
Look at skill text in Claude Code interface. Should see:
```markdown
## Your Project's Conventions

separator: "_"
case: "snake_case"
...
```

### Test Confidence Calculation
```
Match count: 12
Total count: 15
Percentage: 12/15 = 80%
Samples >= 5? Yes
→ Confidence: high ✓
```

### Manually Count Pattern Matches
```bash
grep -o "pattern_here" file | wc -l
```

### Create Test Config with Conventions
```bash
cat > .claude/plugin-name.md << 'EOF'
---
conventions:
  separator: "_"
  case: "snake_case"
  pattern: "<area>_<trigger>_<action>"
  confidence: "high"
---
EOF
```

---

## Key References

**Prevention Strategies:** `/docs/prevention-strategies.md`
- 7 key strategies to prevent context-injection problems
- Red flags to watch for
- Design patterns to follow
- Testing approaches

**Context Injection Guide:** `/docs/context-injection-guide.md`
- Step-by-step implementation
- Code patterns and examples
- Full test cases
- Troubleshooting guide

**Convention Discovery System Plan:** `/docs/plans/2026-01-25-feat-convention-discovery-system-plan.md`
- Complete technical architecture
- Phases and acceptance criteria
- Schema definitions
- Future considerations

**Convention Discovery Skill:** `/skills/ha-conventions/SKILL.md`
- User-facing skill for discovering conventions
- Full workflow documentation
- Error handling
- Re-detection flow

**Convention Analyzer Agent:** `/agents/ha-convention-analyzer.md`
- How conventions are extracted from config
- Pattern analysis logic
- Confidence calculation
- Handling mixed conventions
