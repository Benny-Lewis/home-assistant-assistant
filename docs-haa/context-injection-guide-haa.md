---
title: "Context Injection Guide: How to Build Convention-Aware Plugins"
date: 2026-01-25
type: implementation-guide
related:
  - docs/prevention-strategies.md
  - docs/plans/2026-01-25-feat-convention-discovery-system-plan.md
---

# Context Injection Guide: How to Build Convention-Aware Plugins

This guide provides step-by-step instructions for applying the prevention strategies to build robust, context-aware Claude Code plugins.

## Quick Start: The 5-Minute Overview

**Problem:** Your plugin generates output that ignores user-specific conventions → user has to fix it

**Solution:** Load user conventions at skill startup, not at runtime

**Implementation:**
1. Create a discovery skill/agent (reads user config files)
2. Store discovered conventions in `.claude/plugin-name.md`
3. Use shell expansion (`!` syntax) to inject conventions into skills
4. Add validation that checks output against conventions

**Time to implement:** 2-4 hours for a typical plugin

---

## Step-by-Step Implementation

### Phase 1: Understand Your Context Dependencies

**Goal:** Map out exactly what context your plugin needs to know

**Instructions:**

1. **List all user-specific choices your plugin makes:**
   ```
   Examples:
   - Naming patterns (IDs, aliases, etc.)
   - File locations or formats
   - Behavior preferences (use feature X vs Y)
   - Entity naming conventions
   - Entity type mappings
   - API endpoints or authentication
   - Output format preferences
   ```

2. **For each dependency, determine:**
   - **Can it vary per-user?** (Yes → needs storage in settings)
   - **Can it be auto-detected?** (Yes → create analyzer)
   - **What's the impact if wrong?** (Critical → fail-fast, Low → warn)
   - **Is there a sensible default?** (Yes → always have fallback)

3. **Create a context dependency inventory:**

   ```markdown
   ## Context Dependencies for [Your Plugin]

   ### Dependency 1: Naming Pattern for [Entity Type]
   - **Impact:** Critical (output completely wrong if violated)
   - **Auto-detectable:** Yes (analyze existing entity IDs)
   - **Storage:** `.claude/your-plugin.md` in `conventions:` section
   - **Failure mode:** Fail-fast, ask user to run /setup-conventions
   - **Default:** HA community standard: `<area>_<type>_<name>`

   ### Dependency 2: Preferred Feature Implementation
   - **Impact:** High (might not work with user's HA config)
   - **Auto-detectable:** Partial (check if feature is installed)
   - **Storage:** User settings
   - **Failure mode:** Warn, offer alternative approach
   - **Default:** Most widely compatible option
   ```

4. **Identify the critical path:**
   - Which dependencies MUST be right for output to be useful?
   - Which can degrade gracefully if wrong?
   - Create a failure hierarchy

**Acceptance:** You have a document listing all dependencies with their properties.

---

### Phase 2: Design the Convention Storage Schema

**Goal:** Define how conventions will be stored in the settings file

**Instructions:**

1. **Create YAML schema for your conventions:**

   ```yaml
   ---
   # Plugin settings (existing fields)
   [your existing settings...]

   # NEW: Convention settings (discovered by /setup-conventions)
   conventions:
     # Rules (generalized, not overfitted to specific examples)
     naming_rules:
       entity_id_pattern: "<area>_<trigger>_[if_<condition>]_<action>"
       entity_id_separator: "_"
       entity_id_case: "snake_case"
       area_position: "prefix"

     # Behavior preferences
     use_feature_x: true          # Boolean choice
     threshold_seconds: 30        # Numeric choice
     default_mode: "single"       # Enumerated choice

     # Detection metadata (set by discovery process)
     detected_from_existing: false
     last_detected: null
     confidence: null             # high, medium, low, none

     # Examples (concrete reference data)
     examples:
       - id: "kitchen_motion_light_on"
         type: "automation"
       - id: "backyard_door_open_if_dark_alert"
         type: "automation"
   ---
   ```

2. **Key design principles:**
   - **Rules before patterns:** Store `separator: "_"` + `case: "snake_case"` instead of pattern string
   - **Metadata for reliability:** Track confidence, when it was detected, source
   - **Examples for validation:** Concrete reference data to validate new output against
   - **All optional:** Sensible defaults for every field

3. **Document field purposes:**

   ```yaml
   naming_rules:
     entity_id_pattern: |
       Template for generating entity IDs.
       Variables: <area>, <type>, <name>, <condition>
       Example: "<area>_<type>_<name>" = "kitchen_light_main"

     detected_from_existing:
       Whether patterns were auto-discovered from existing config.
       false = manually specified or default
       true = auto-discovered, may need re-validation
   ```

**Acceptance:** You have a complete YAML schema that could be deployed now.

---

### Phase 3: Create the Discovery Analyzer

**Goal:** Build an agent that analyzes existing config to extract conventions

**Instructions:**

1. **Create analyzer agent** (`agents/your-plugin-analyzer.md`):

   ```yaml
   ---
   name: your-plugin-analyzer
   description: >
     Analyzes your existing [Config Type] to detect naming patterns
     and conventions. Returns structured analysis for confirmation.
   tools: Read, Grep, Glob
   model: sonnet
   ---

   # [Your Plugin] Convention Analyzer

   Analyze existing config files to detect user's conventions.

   ## Process

   1. **Locate config files**
      - Check for [main_file.ext]
      - Check for [optional_file.ext]
      - Report findings

   2. **Extract patterns**
      - Read all entities of interest
      - Categorize by naming pattern
      - Identify separators, case, position

   3. **Calculate confidence**
      - Count entities matching each pattern
      - If ≥80% match AND ≥5 samples → high
      - If 50-79% match OR <5 samples → medium
      - If <50% match OR <3 samples → low

   4. **Report findings**
      [Show patterns with examples and confidence]
   ```

2. **Implement pattern analysis logic:**

   ```python
   # Pseudocode for pattern analysis
   def analyze_naming(entity_ids: List[str]) -> Pattern:
       """Extract naming pattern from sample IDs."""

       # Rule 1: Detect separator
       separators = defaultdict(int)
       for eid in entity_ids:
           for char in "_-. ":
               separators[char] += eid.count(char)
       dominant_separator = max(separators)  # e.g., "_"

       # Rule 2: Detect case
       cases = defaultdict(int)
       for eid in entity_ids:
           if eid == eid.lower(): cases["snake_case"] += 1
           elif eid == eid.upper(): cases["UPPER"] += 1
           else: cases["mixed"] += 1
       dominant_case = max(cases)  # e.g., "snake_case"

       # Rule 3: Detect position of area prefix
       # (check if first segment is typically a room/location name)

       return Pattern(
           separator=dominant_separator,
           case=dominant_case,
           area_position="prefix"
       )

   def calculate_confidence(matches: int, total: int) -> str:
       """Map percentage to confidence level."""
       pct = matches / total
       if pct >= 0.80 and matches >= 5: return "high"
       if pct >= 0.50: return "medium"
       return "low"
   ```

3. **Handle edge cases:**

   ```markdown
   ## Handling Mixed/Legacy Conventions

   If you detect multiple distinct patterns:

   Pattern A: `<area>_<action>` (5 entities, older style)
   Pattern B: `<area>_<trigger>_<action>` (8 entities, newer style)

   Report both and recommend the dominant pattern:
   - Total: 13 entities analyzed
   - Pattern B is dominant (62%)
   - Pattern A may be legacy
   - Recommendation: Adopt Pattern B for new entities

   Let the user choose which to standardize on.
   ```

4. **Add fallback defaults:**

   ```markdown
   ## No Pattern Detected

   If no consistent pattern found (or no existing config):

   **Recommend Home Assistant/industry standard:**
   - ID pattern: `<area>_<type>_<name>`
   - Case: `snake_case`
   - Separator: `_`

   **User choices:**
   - [ ] Accept recommendation
   - [ ] Customize patterns
   - [ ] Use different defaults
   ```

**Acceptance:** Agent can be invoked and produces structured pattern analysis.

---

### Phase 4: Create the Discovery Skill

**Goal:** User-facing skill that orchestrates discovery and confirmation

**Instructions:**

1. **Create skill** (`skills/setup-conventions/SKILL.md`):

   ```yaml
   ---
   name: setup-conventions
   description: >
     Detect and configure naming conventions for your [System].
     Run once to auto-detect from your existing config, then
     conventions are automatically applied to generated output.
   disable-model-invocation: true
   allowed-tools: Read, Grep, Glob, Write
   context: fork
   ---

   # Configure Your Conventions

   ## Step 1: Check Existing Conventions

   Read current conventions from settings:
   !`cat .claude/your-plugin.md 2>/dev/null | grep -A 30 "conventions:" || echo "No conventions configured yet"`

   [Check output above:
   - If conventions listed → offer to re-detect or review
   - If "No conventions" → proceed to detection]

   ## Step 2: Run Detection

   [Invoke your analyzer agent]

   ## Step 3: Present Findings

   [Display detected patterns with examples and confidence]

   ## Step 4: User Confirmation

   For each detected pattern:
   ```

   Detected Pattern: `<area>_<trigger>_<action>`
   Examples: kitchen_motion_light_on, backyard_door_open_alert
   Confidence: high (12/15 entities match)

   Accept this pattern? [Yes] [Modify] [Use default instead]
   ```

   ## Step 5: Save Conventions

   Write confirmed conventions to `.claude/your-plugin.md`:
   - Update YAML frontmatter with conventions
   - Set `detected_from_existing: true`
   - Set `last_detected: [today's date]`
   - Set `confidence: [detected_level]`

   ## Step 6: Confirm

   "✅ Conventions saved! Future output will follow these patterns.
    Run this skill again anytime to re-detect."
   ```

2. **Add re-detection flow:**

   ```markdown
   ## If Conventions Already Exist

   Show current conventions, then ask:
   "Would you like to:
   1. Keep current conventions
   2. Re-detect from updated config (will show diff)
   3. View current conventions"

   If re-detecting:
   - Run detection as normal
   - Compare old vs new
   - Show diff before saving
   - Require explicit confirmation
   ```

3. **Handle error cases:**

   ```markdown
   ## Error Handling

   | Situation | Response |
   |-----------|----------|
   | Config path not found | "Where is your config? [/path/to/config]" |
   | Cannot read files | "I can't access your config. Would you like to manually enter conventions?" |
   | No existing config | "No existing entities found. Using community defaults. [show defaults]" |
   | YAML parse error | "Error parsing [file] line X: [error]. Skipping that file." |
   ```

**Acceptance:** Skill runs successfully and saves conventions to settings file.

---

### Phase 5: Inject Conventions Into Skills

**Goal:** Make conventions available to all skills automatically

**Instructions:**

1. **Update your main skill** (`skills/your-skill/SKILL.md`):

   ```yaml
   ---
   name: your-skill
   description: Your skill description
   allowed-tools: Read, Write, Bash, etc.
   ---

   ## Your Project's Conventions

   !`cat .claude/your-plugin.md 2>/dev/null | head -80 || echo "## Default Conventions (no custom config found)

   Using Home Assistant community standards:
   - ID pattern: <area>_<type>_<name>
   - Case: snake_case
   - Separator: _"`

   ## Step 0: Verify Conventions

   [CRITICAL] Check the conventions section above:
   - If "Default Conventions" appears → conventions not configured
     - STOP and ask: "I don't know your conventions yet. Please run /setup-conventions first, or let me use defaults."
     - Do NOT generate output that might not match your actual conventions
   - If "Malformed" or error appears → settings file is broken
     - Ask: "Your settings file seems corrupted. Should I recreate it?"

   If conventions show as `confidence: low` or `none`:
   - Add this banner to your output: "⚠️ Detected conventions have low confidence.
     Please review naming patterns carefully."

   ## Step 1: [Your Next Step]

   [Rest of your skill process, using conventions loaded above]
   ```

2. **Why shell expansion works:**

   ```
   Shell expansion timing:
   ┌─ User invokes skill
   │
   ├─ Claude Code preprocessor runs
   │  └─ `!cat ...` executes, renders file content into markdown
   │
   ├─ Claude Code sends skill markdown to Claude
   │  └─ Conventions section is now part of the skill text
   │
   └─ Claude executes skill
      └─ Conventions are already loaded, no runtime file access needed
   ```

3. **Implement Step 0 verification:**

   ```markdown
   ## Critical Step 0: Load Conventions

   Conventions injected above? Check:
   - [ ] If I see convention rules (separator, case, etc.) → ✓ Good
   - [ ] If I see "Default Conventions" → ⚠️ User not configured
   - [ ] If I see error or truncated output → ✗ Bad

   Action based on check:
   - ✓ Good → Continue to next step using loaded conventions
   - ⚠️ Not configured → STOP and ask:
       "I don't know your conventions yet.
        Please run `/setup-conventions` first to detect them,
        or tell me to use Home Assistant defaults."
       Do NOT generate output without this confirmation.
   - ✗ Error → Ask user to run `/setup-conventions` to fix settings.
   ```

4. **Add naming requirements section:**

   ```markdown
   ## Naming Requirements

   Generated output MUST follow these conventions:

   **Naming Pattern:** `{{ conventions.naming_rules.entity_id_pattern }}`
   - Separator: `{{ conventions.naming_rules.entity_id_separator }}`
   - Case: `{{ conventions.naming_rules.entity_id_case }}`
   - Example: `{{ conventions.examples[0].id }}`

   **Implementation choice:**
   - Use `{{ conventions.preferred_feature }}` if available
   - Fall back to default: `{{ default_implementation }}`

   [Use variables from conventions when generating output]
   ```

**Acceptance:** Skills can be invoked and conventions are visible in the skill text.

---

### Phase 6: Add Validation Checklist

**Goal:** Ensure generated output respects conventions before showing user

**Instructions:**

1. **Create validation section in skill:**

   ```markdown
   ## Validation Checklist

   After generating output, validate before presenting to user:

   **[ ] Naming Compliance**
   - Does generated ID match pattern `{{ pattern }}`?
   - Does generated alias match convention?
   - Count separators, case, position
   - If any violation → [FAIL and regenerate]

   **[ ] Feature Compliance**
   - If feature X preferred → is it used? (not feature Y)
   - If threshold set → is it respected?
   - If optional convention → is it included?

   **[ ] Syntax Validation**
   - Is YAML valid? (can parse without errors)
   - Are entity IDs resolvable? (exist in HA)
   - Are required fields present?

   **If Any Check Fails:**
   1. Identify the specific failure
   2. Fix the output
   3. Run validation again
   4. Only show to user when all checks pass
   ```

2. **Implement validation logic:**

   ```python
   # Pseudocode validation
   def validate_against_conventions(output: str, conventions: Dict) -> bool:
       """Check if output respects conventions."""

       # Extract generated ID
       generated_id = parse_id_from_output(output)

       # Check naming pattern
       if not matches_pattern(generated_id, conventions.id_pattern):
           return False, f"ID '{generated_id}' doesn't match pattern"

       # Check feature usage
       if conventions.use_feature_x and "feature_x" not in output:
           return False, "Feature X not used (required by convention)"

       # Check syntax
       if not is_valid_yaml(output):
           return False, "Invalid YAML syntax"

       return True, "All checks passed"
   ```

3. **Handle validation failures:**

   ```markdown
   ## When Validation Fails

   **Example failure:**
   - Generated ID: `light_kitchen_motion` (wrong order)
   - Expected pattern: `<area>_<trigger>_<action>`
   - Should be: `kitchen_motion_light`

   **Response:**
   1. Show clear error: "ID doesn't match your convention pattern"
   2. Show expected pattern: `<area>_<trigger>_<action>`
   3. Show example: `kitchen_motion_light_on`
   4. Regenerate with correct pattern
   5. Validate again before showing user

   **Never show user non-compliant output** (or show with clear warning if enforce_conventions: false)
   ```

4. **Add confidence-based messaging:**

   ```markdown
   ## Output Validation Report

   {% if confidence == "high" %}
     ✅ Output validated against high-confidence conventions.
        Naming patterns are accurate.
   {% elsif confidence == "medium" %}
     ⚠️ Output validated against medium-confidence conventions.
        Please review naming patterns to ensure they match your setup.
   {% elsif confidence == "low" %}
     ⚠️ Output validated against low-confidence conventions.
        STRONGLY recommend running `/setup-conventions` to improve accuracy.
        Please carefully review all naming before deploying.
   {% endif %}
   ```

**Acceptance:** Validation catches mismatches before user sees output.

---

### Phase 7: Write Comprehensive Tests

**Goal:** Verify convention system works correctly end-to-end

**Instructions:**

1. **Test Case: Fresh Install**

   ```markdown
   ## Test: Fresh Install (No Conventions)

   **Setup:**
   - No `.claude/your-plugin.md` file (or empty conventions)

   **Steps:**
   1. Run main skill
   2. Skill should show "Default Conventions"
   3. Skill should NOT fail
   4. Skill should explain: "Run /setup-conventions to auto-detect yours"
   5. Generate sample output
   6. Output should be valid (though maybe not optimized)

   **Pass if:**
   - No errors
   - Output is usable
   - User is guided to run setup
   - Fallback defaults work correctly
   ```

2. **Test Case: High Confidence Detection**

   ```markdown
   ## Test: High Confidence Detection

   **Setup:**
   - User has 10+ existing entities following consistent pattern
   - All IDs: `<area>_<type>_<name>` with `_` separator

   **Steps:**
   1. Run /setup-conventions
   2. Analyzer detects: 12/12 entities match pattern
   3. Confidence should show: "high"
   4. Pattern should be: `<area>_<type>_<name>`
   5. Example should be shown: `kitchen_light_main`
   6. User confirms and saves
   7. Run main skill and generate new output
   8. Generated output should match pattern exactly
   9. Validation should pass

   **Pass if:**
   - Confidence is "high"
   - Pattern correctly identified
   - Generated output matches perfectly
   - Zero manual corrections needed
   ```

3. **Test Case: Mixed Conventions (Legacy + New)**

   ```markdown
   ## Test: Mixed Conventions

   **Setup:**
   - 5 entities with old pattern: `<name>_<type>`
   - 10 entities with new pattern: `<area>_<type>_<name>`

   **Steps:**
   1. Run /setup-conventions
   2. Analyzer detects both patterns with counts
   3. Confidence should show: "medium"
   4. Output should show:
      - Pattern A: `<name>_<type>` (5 entities, 33%)
      - Pattern B: `<area>_<type>_<name>` (10 entities, 67%)
      - Recommendation: Use Pattern B (dominant)
   5. User can choose which pattern to adopt
   6. Chosen pattern is saved
   7. Future generation uses chosen pattern

   **Pass if:**
   - Both patterns clearly reported with counts
   - Confidence is appropriately "medium"
   - User can choose standard
   - No forced assumption
   ```

4. **Test Case: Validation Catches Errors**

   ```markdown
   ## Test: Validation Catches Violations

   **Setup:**
   - Conventions configured: `<area>_<type>_<name>` with `_` separator
   - Temporarily modify skill to ignore conventions (for testing)

   **Steps:**
   1. Generate output with ID: `light_kitchen_main` (wrong order)
   2. Expected pattern: `kitchen_light_main`
   3. Validation should catch error
   4. Error message should show:
      - What was generated: `light_kitchen_main`
      - What was expected: `<area>_<type>_<name>`
      - Example: `kitchen_light_main`
   5. Skill should NOT show this output to user
   6. Skill should regenerate with correct naming

   **Pass if:**
   - Error is caught every time
   - Error message is clear
   - Output is regenerated
   - User never sees the bad output
   ```

5. **Test Case: Persistence Across Sessions**

   ```markdown
   ## Test: Context Persists Across Sessions

   **Setup:**
   - Session 1: Configure conventions via /setup-conventions
   - Session 2: New CLI session, closed previous window

   **Steps:**
   1. Save conventions to `.claude/your-plugin.md` (Session 1)
   2. Close Claude Code entirely
   3. Start new Claude Code session
   4. Run main skill
   5. Skill should load conventions from file
   6. Skill should NOT ask to re-configure
   7. Generated output should use saved conventions
   8. Token cost should be minimal (not re-detecting)

   **Pass if:**
   - Conventions loaded from file (no re-ask)
   - Same patterns applied
   - No duplicate detection tokens spent
   ```

6. **Test Case: Update Workflow**

   ```markdown
   ## Test: Re-detect and Update Conventions

   **Setup:**
   - Existing conventions saved (old pattern)
   - Config has changed (new entities with different pattern)

   **Steps:**
   1. Run /setup-conventions
   2. Skill detects existing conventions
   3. Offers option: "Keep current or re-detect?"
   4. User chooses "re-detect"
   5. Analyzer detects new pattern
   6. Skill shows DIFF:
      - OLD: `<area>_<type>` (from previous save)
      - NEW: `<area>_<type>_<name>` (from latest analysis)
   7. User must explicitly confirm: "Update to new?"
   8. Skill saves new conventions (completely replaces old)
   9. Future generation uses NEW conventions

   **Pass if:**
   - Diff clearly shows changes
   - Requires explicit confirmation
   - Old conventions completely replaced
   - No merge confusion
   ```

**Acceptance:** All 6 test cases pass.

---

## Troubleshooting Common Issues

### Issue: "Conventions not loading"

**Symptom:** Skill shows "Default Conventions" but settings file exists

**Diagnosis:**
```bash
# Check if file exists and is readable
cat .claude/your-plugin.md | head -20

# Check file has conventions section
grep -A 5 "conventions:" .claude/your-plugin.md
```

**Solutions:**
1. Verify file path is correct in shell expansion: `!`cat .claude/your-plugin.md`
2. Check YAML syntax in settings file (may be malformed)
3. Run `/setup-conventions` to recreate settings file
4. Check file permissions (should be readable)

---

### Issue: "Generated output doesn't match conventions"

**Symptom:** Output ignores rules, uses wrong naming

**Diagnosis:**
1. Check if Step 0 is actually failing (should STOP on missing conventions)
2. Check if conventions actually loaded (look at skill markdown text)
3. Check if validation is running (should catch violations)

**Solutions:**
1. Add explicit logging to Step 0: "Conventions loaded: [show what loaded]"
2. Run `/setup-conventions` to verify conventions are saved
3. Check if validation section is actually being executed
4. If confidence is low, might be expected (add uncertainty banner)

---

### Issue: "Confidence level always wrong"

**Symptom:** High confidence when should be medium, or vice versa

**Diagnosis:**
1. Check confidence calculation in analyzer
2. Check sample sizes in detection output
3. Manually count matches vs total

**Solutions:**
1. Verify formula: `confidence: high` if `match% >= 80% AND samples >= 5`
2. For small samples, medium confidence is correct
3. Show user the actual breakdown: "8/10 match, so confidence is high"
4. Let user override if they disagree

---

### Issue: "Re-detection loses important details"

**Symptom:** User ran setup once, ran it again, old settings got replaced

**Diagnosis:**
1. Check if confirmation was shown before save
2. Check if diff was displayed
3. Check if explicit confirmation was required

**Solutions:**
1. Always show diff: old vs new conventions
2. Require explicit confirmation before saving
3. Consider merge strategy instead of complete replacement
4. Add warning: "This will overwrite your current conventions"

---

## Checklist for Your Plugin

Use this as you implement:

### Discovery Phase
- [ ] Identified all context dependencies
- [ ] Created context dependency inventory
- [ ] Decided auto-detect vs manual for each
- [ ] Designed YAML schema for storage
- [ ] Created analyzer agent

### Skill Phase
- [ ] Created `/setup-conventions` skill
- [ ] Skill can detect patterns from config
- [ ] Skill shows confidence levels
- [ ] Skill handles no-pattern case (defaults)
- [ ] Skill gets user confirmation
- [ ] Skill saves to `.claude/plugin-name.md`

### Integration Phase
- [ ] Added shell expansion to main skill (`!` syntax)
- [ ] Step 0 loads conventions
- [ ] Step 0 fails fast on missing
- [ ] Added uncertainty banners for low confidence
- [ ] Implemented validation checklist
- [ ] Validation runs before output to user

### Testing Phase
- [ ] Fresh install test passes
- [ ] High confidence test passes
- [ ] Mixed conventions test passes
- [ ] Validation catches errors
- [ ] Persistence across sessions works
- [ ] Update workflow works

### Documentation Phase
- [ ] Documented context dependencies
- [ ] Documented configuration schema
- [ ] Documented how to run setup skill
- [ ] Documented how conventions are applied
- [ ] Documented troubleshooting steps

---

## Key Takeaways

1. **Identify context early** - Don't discover you need conventions mid-implementation
2. **Store rules not patterns** - `separator: "_"` is more robust than pattern string
3. **Inject at load time** - Shell expansion (`!` syntax) makes it reliable
4. **Fail fast on uncertainty** - Don't silently use wrong conventions
5. **Validate before showing** - Catch naming violations before user sees output
6. **Make setup simple** - One skill to run, automatic detection, clear confirmation
7. **Persist across sessions** - Store in settings file, load at startup
8. **Handle updates gracefully** - Show diff, require confirmation, don't merge

Follow these principles and your plugin will respect user conventions automatically, require zero manual corrections, and build user trust.
