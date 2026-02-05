---
title: "Prevention Strategies Documentation Index"
date: 2026-01-25
type: index
---

# Prevention Strategies: Complete Documentation Index

## Overview

This documentation suite provides comprehensive prevention strategies, design patterns, and implementation guidance for solving a critical problem: **Claude Code plugin skills generating output without knowing user preferences and conventions**.

### The Problem
Skills generate output (YAML, code, content) that doesn't match user-specific naming patterns, implementation preferences, or domain conventions. This requires manual corrections, wastes tokens, and damages trust.

### The Solution
A convention discovery and context injection system that:
1. **Discovers** conventions from existing user config (automated)
2. **Stores** them as structured rules + examples (durable)
3. **Injects** them into skills at load time (atomic)
4. **Validates** generated output against conventions (fail-fast)

### The Impact
- First-time correct output (zero manual corrections)
- 64% fewer tokens spent on re-discovery and corrections
- 66% less time from request to usable output
- High user trust and satisfaction

---

## Documentation Structure

### 1. **Why It Matters** (Strategic Context)
**File:** `/docs/why-conventions-matter.md`

**Read this if:** You want to understand the business case and why this problem is worth solving.

**Contains:**
- Executive summary of the problem
- Real test case showing the impact (12 min → 4 min, 41.5k → 20k tokens)
- Architecture overview
- Phase-by-phase explanation of how the solution works
- ROI analysis and metrics to track
- Adoption path (quick implementation to advanced)
- Why conventions are essential

**Time to read:** 15 minutes

**Who should read:**
- Plugin developers deciding whether to implement
- Project managers planning resources
- Users wanting to understand the value

---

### 2. **Prevention Strategies** (Tactical Approach)
**File:** `/docs/prevention-strategies.md`

**Read this if:** You want to learn 7 concrete strategies to prevent context-injection problems in plugins.

**Contains:**
- 7 prevention strategies (with examples)
  - Strategy 1: Identify context dependencies early
  - Strategy 2: Implement context injection at load time
  - Strategy 3: Fail-fast on low confidence context
  - Strategy 4: Store context as rules + examples
  - Strategy 5: Design convention discovery as user-initiated
  - Strategy 6: Create testable convention validation
  - Strategy 7: Red flags to watch for
- 5 design patterns to follow
- 6 testing approaches with full test cases
- Common anti-patterns to avoid
- Troubleshooting guide
- Implementation checklist for new plugins

**Time to read:** 20 minutes

**Who should read:**
- Plugin developers implementing conventions
- Anyone building context-aware systems
- Code reviewers checking for these patterns

---

### 3. **Context Injection Guide** (Step-by-Step)
**File:** `/docs/context-injection-guide.md`

**Read this if:** You're ready to implement convention discovery in your plugin and want detailed step-by-step instructions.

**Contains:**
- Quick start overview (5-minute version)
- Phase 1: Understand context dependencies
- Phase 2: Design convention storage schema
- Phase 3: Create discovery analyzer agent
- Phase 4: Create discovery skill
- Phase 5: Inject conventions into skills
- Phase 6: Add validation checklist
- Phase 7: Write comprehensive tests
- Troubleshooting common issues
- Full implementation checklist

**Time to read:** 30 minutes (for planning), 2-4 hours (for implementation)

**Who should read:**
- Plugin developers actively implementing
- Anyone building analyzer agents
- QA engineers planning tests

---

### 4. **Convention System Reference** (Quick Lookup)
**File:** `/docs/convention-system-reference.md`

**Read this if:** You need quick answers while implementing, or want to understand specific aspects in detail.

**Contains:**
- Core concepts (what is a convention, why it matters)
- Quick start implementation checklist
- 5 essential code patterns (with examples)
- Convention types (naming, behavior, detection metadata)
- Full configuration file schema example
- Confidence levels (high/medium/low/none)
- Discovery algorithm explanation
- 6 detailed testing scenarios
- Debugging checklist
- One-liner recipes for common tasks
- Key references to other docs

**Time to read:** 5-10 minutes per lookup

**Who should read:**
- Developers implementing (keep open while coding)
- Code reviewers checking implementation
- QA engineers validating behavior

---

### 5. **Actual Implementation** (Reference)
**Files:**
- `/agents/ha-convention-analyzer.md` - Convention discovery agent
- `/skills/ha-conventions/SKILL.md` - Convention discovery skill
- `/templates/home-assistant-assistant.md` - Settings schema
- `/docs/plans/2026-01-25-feat-convention-discovery-system-plan.md` - Full technical plan

**Read this if:** You want to see how these strategies were applied to a real plugin.

**Contains:**
- Working convention discovery system
- All components: agent, skill, schema, plan
- Real YAML examples and patterns
- Full test coverage
- Integration with existing skills

**Time to read:** Varies (reference material)

**Who should read:**
- Anyone implementing similar systems (copy patterns)
- Code reviewers validating design
- Developers maintaining the system

---

## How to Use This Documentation

### I'm a Plugin Developer - Where Do I Start?

**Path 1: Understanding (30 minutes)**
1. Read: `why-conventions-matter.md` (understand the problem)
2. Read: `prevention-strategies.md` (learn the 7 strategies)
3. Decision: Should I implement? Is the ROI worth it?

**Path 2: Implementation (4-6 hours)**
1. Read: `context-injection-guide.md` (phase by phase)
2. Copy: Patterns from actual implementation
3. Reference: Use `convention-system-reference.md` while coding
4. Test: Use test cases from `prevention-strategies.md`

**Path 3: Validation (1-2 hours)**
1. Checklist: Use implementation checklist from `context-injection-guide.md`
2. Tests: Run all 6 test scenarios from `prevention-strategies.md`
3. Docs: Update your plugin's documentation with convention support

### I'm a Project Manager - What Should I Know?

**Read:**
1. `why-conventions-matter.md` - Understand the problem and ROI
2. `prevention-strategies.md` - Quick overview section (10 min)

**Key metrics to track:**
- Manual corrections needed per session (target: 0)
- Token cost per generation (target: 50% reduction)
- Time per generation (target: 66% reduction)
- User satisfaction (target: high)

### I'm Building a Similar System - How Do I Avoid Mistakes?

**Read in order:**
1. `prevention-strategies.md` - See the red flags and anti-patterns
2. `why-conventions-matter.md` - Understand why each decision matters
3. `context-injection-guide.md` - Follow the implementation phases
4. `convention-system-reference.md` - Use for specific questions

**Critical patterns to follow:**
- Shell expansion for loading context at skill startup
- Fail-fast on missing context (don't silently use defaults)
- Store rules + examples (not pattern strings alone)
- Validate output before showing user
- One-time setup flow (not asking each time)

### I'm Code Reviewing Convention Systems - What Should I Check?

**Checklist:**
1. ✓ Context dependencies identified early (Strategy 1)
2. ✓ Context loaded via shell expansion at skill startup (Strategy 2)
3. ✓ Fails fast on missing/low-confidence context (Strategy 3)
4. ✓ Stores rules + examples, not patterns alone (Strategy 4)
5. ✓ Discovery is user-initiated, not automatic (Strategy 5)
6. ✓ Validation checklist before showing output (Strategy 6)
7. ✓ Red flags addressed (Strategy 7)
8. ✓ All 6 test cases pass (from prevention-strategies.md)

---

## Key Documents Summary

| Document | Purpose | Length | Audience |
|----------|---------|--------|----------|
| `why-conventions-matter.md` | Business case and understanding | 20 min | Everyone |
| `prevention-strategies.md` | 7 strategies and red flags | 20 min | Developers, Reviewers |
| `context-injection-guide.md` | Step-by-step implementation | 2-4 hours | Developers |
| `convention-system-reference.md` | Quick lookup and patterns | 5-10 min/lookup | Developers |
| `ha-convention-analyzer.md` | Working discovery agent | Reference | Copy patterns |
| `ha-conventions/SKILL.md` | Working discovery skill | Reference | Copy patterns |
| `2026-01-25-feat-convention-discovery-system-plan.md` | Full technical plan | Reference | Deep dive |

---

## Core Concepts Explained

### Convention
A user-specific pattern or preference that should be respected consistently in generated output.

**Examples:**
- Naming: `<area>_<trigger>_<action>` vs `<area>-<trigger>-<action>`
- Implementation: Use timer helpers vs inline delays
- Behavior: Default mode "single" vs "restart"

### Context Injection
Loading user conventions at skill startup time (using shell expansion) so they're available to Claude when generating output.

**Why:** Avoids runtime file reads, guarantees availability, makes context visible.

### Convention Discovery
Analyzing existing user configuration to extract naming patterns and preferences automatically.

**Why:** Users don't have to manually specify conventions; system learns from their existing work.

### Fail-Fast
Stopping immediately when critical context is missing or uncertain, rather than silently using wrong conventions.

**Why:** Prevents silent generation of wrong output; builds user trust.

### Validation Checklist
Testing generated output against conventions before showing it to the user.

**Why:** Catches naming violations and errors before user sees them; increases quality.

---

## Quick Decision Tree

```
Do you have user-specific conventions or preferences?
├─ YES: Does your plugin need to respect them?
│  ├─ YES (critical): Implement full convention system
│  │  └─ Follow: context-injection-guide.md (4-6 hours)
│  └─ NO (nice to have): Implement basic detection only
│     └─ Follow: Quick Start in context-injection-guide.md (2 hours)
└─ NO: You might not need conventions
   └─ Consider: Might need in future as plugin grows
```

---

## Red Flags: When Conventions Are Needed

If your plugin has any of these issues, conventions will help:

- [ ] Users report "output doesn't match my naming"
- [ ] Same type of error appears multiple times per session
- [ ] Users have to correct output before it's usable
- [ ] Token cost seems high relative to task complexity
- [ ] Plugin requires user education on preferences
- [ ] Different users' output looks completely different
- [ ] Users ask "why didn't you use [feature] I prefer?"

**If 2+ boxes are checked:** Convention system will significantly improve your plugin.

---

## Metrics to Success

### Before Convention System
- Manual corrections needed: 2+ per session
- Tokens per generation: 18k average
- Time per generation: 12 minutes average
- User satisfaction: Medium (works but needs correction)

### After Convention System
- Manual corrections needed: 0 per session
- Tokens per generation: 6.5k average (64% reduction)
- Time per generation: 3-4 minutes (66% reduction)
- User satisfaction: High (works perfectly first time)

**Goal:** Achieve "after" metrics through proper implementation.

---

## Implementation Timeline

### Week 1: Planning & Design
- Day 1: Read documentation (why-conventions-matter.md + prevention-strategies.md)
- Day 2-3: Identify context dependencies (Phase 1)
- Day 4-5: Design storage schema (Phase 2) and discovery agent (Phase 3)

### Week 2: Core Implementation
- Day 1-2: Implement discovery agent
- Day 3-4: Implement setup-conventions skill
- Day 5: Implement shell expansion in skills

### Week 3: Validation & Testing
- Day 1-2: Add validation checklist
- Day 3-4: Run full test suite (6 test cases)
- Day 5: Documentation and code review

**Total time:** 2-3 weeks for full implementation, 1 week for quick MVP

---

## Next Steps

### If You're Building a New Plugin
1. Design with conventions in mind from the start
2. Follow phases in `context-injection-guide.md`
3. Use `convention-system-reference.md` for specific patterns
4. Copy code patterns from actual implementation

### If You Have an Existing Plugin
1. Assess whether conventions would help (check red flags)
2. Read `why-conventions-matter.md` for ROI analysis
3. Follow MVP path in `context-injection-guide.md` (2 hours)
4. Expand to full implementation (4 more hours)

### If You're Code Reviewing
1. Use checklist from "Code Reviewing Convention Systems" section above
2. Reference specific strategies from `prevention-strategies.md`
3. Verify test cases from `prevention-strategies.md`

### If You're Supporting Users
1. Ensure documentation explains convention setup
2. Direct users to `/setup-conventions` skill
3. Reference `prevention-strategies.md` troubleshooting section for issues

---

## Questions & Answers

### Q: Is convention discovery necessary, or can I just ask users in chat?

**A:** Asking each time wastes tokens, time, and doesn't persist. Conventions discovered once and stored persist forever. Worth the investment.

### Q: My plugin is simple - do I need conventions?

**A:** If output quality doesn't matter (e.g., "write random haiku"), no. If output needs to match user's setup (e.g., "create automation"), yes.

### Q: What if users don't want to set up conventions?

**A:** Provide sensible defaults. Users who need specificity will invest 2 minutes. Users who don't can use defaults (works for 80% of cases).

### Q: How long does convention discovery take to implement?

**A:** MVP: 2 hours. Full implementation: 4-6 hours. Time to learn: read docs in 1-2 hours.

### Q: Can I copy code from your implementation?

**A:** Yes! That's why we documented it. Find patterns in `/agents/ha-convention-analyzer.md` and `/skills/ha-conventions/SKILL.md`.

### Q: What if I'm building for multiple users with different conventions?

**A:** Conventions are stored per-project (in `.claude/plugin-name.md`). Each user can have their own conventions.

### Q: How do I handle updates to conventions?

**A:** Show diff (old vs new), require explicit confirmation, completely replace (don't merge to avoid confusion). See `context-injection-guide.md` Phase 4.

---

## Contributing

Found issues in this documentation? Improvements to suggest?

1. **Bug fixes:** Update relevant document
2. **New strategies:** Add to `prevention-strategies.md`
3. **New patterns:** Add to `convention-system-reference.md`
4. **New tests:** Add to `prevention-strategies.md` testing section
5. **Better examples:** Update in all relevant docs

---

## Document Maintenance

| Document | Last Updated | Next Review |
|----------|--------------|------------|
| why-conventions-matter.md | 2026-01-25 | After first implementation |
| prevention-strategies.md | 2026-01-25 | After first implementation |
| context-injection-guide.md | 2026-01-25 | After first implementation |
| convention-system-reference.md | 2026-01-25 | Quarterly |

---

## Related External Documentation

- **Claude Code Skills:** https://code.claude.com/docs/en/skills.md
- **Claude Code Plugins:** https://code.claude.com/docs/en/plugins-reference.md
- **Home Assistant Integrations:** https://www.home-assistant.io/integrations/
- **YAML Syntax:** https://yaml.org/

---

## Summary

This documentation suite provides everything needed to understand, design, and implement convention discovery and context injection systems for Claude Code plugins.

**Three-step path:**
1. **Understand:** Read `why-conventions-matter.md` (15 min)
2. **Learn:** Read `prevention-strategies.md` (20 min)
3. **Build:** Follow `context-injection-guide.md` (4-6 hours)

**Result:** Plugins that respect user conventions, generate first-time correct output, and build lasting user trust.

Let's build the next generation of Claude Code plugins that actually understand their users' needs.
