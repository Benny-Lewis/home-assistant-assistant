Here’s how your **Convention Discovery System plan** stacks up against Claude Code **plugin / skill / subagent / command** best practices — and what I’d tweak.

---

## ✅ What you’re doing that matches best practices

### 1) You’re shrinking “huge specs” into a compact, reusable contract (big win)

Your root cause is “the naming spec is 1,800 lines and didn’t get loaded” .

Claude’s official Skill guidance is basically: **keep skills concise, because once they load they compete with your conversation and everything else** ([Claude][1]).
Your approach (detect → store summary patterns → reuse forever) is *exactly* how you avoid that failure mode.

### 2) Correct separation of concerns: **command/entrypoint → analyzer → stored settings → generation**

Your architecture is clean and “Claude-native”: one user-facing trigger (`/ha-conventions`), one narrow analyzer, saved settings, then Skills consume it .

This maps well to how Claude Code expects tooling to be * = user interaction + workflow

* **subagent** = isolated analysis work
* **settings file** = persistent state

### 3) Using a forked context subagent for analysis is the right move

Claude Code explicitly supports `context: fork` for running a skill in isolation so it doesn’t pollute the main conversation ([Claude Code][2]).

Your analyzer agent is basically that idea, expressed as a reusable subagent .

### 4) Plugin layout aligns with the official plugin structure expectations

The Claude Code plugin`.claude-plugin/plugin.json` is *only* the manifest; `commands/`, `agents/`, `skills/`, etc. must be at the plugin root ([Claude Code][3]).
Your proposed file locations are consistent with that .

---

## ⚠️ The biggest mismatch: you’re implementing `/ha-conventions` as a **command**, but Claude is moving toward **skills as the universal abstractay:

> custom slash commands have been merged into skills
> `commands/review.md` and `skills/review/SKILL.md` both create `/review`
> ([Claude Code][2])

And the plugin reference even calls `commands/` “legacy” and recommends `skills/` for new work ([Claude Code][3]).

### What I’d change

Instead of:

* `commands/ha-conventions.md`

Prefer:

* `skills/ha-conventions/SKILL.md`

Because Skills give you extra control knobs you’ll want:

* `allowed-tools` to avoid permission prompts ([Claude Code][2])
* `disable-model-invocation: true` so Claude doesn’t randomly trigger it ([Claude Code][2])
* optional `context: fork` patterns if you ever embed detection directly ([Claude Code][2])

So `/ha-conventions` should be a *manual skill* (invoked by user), not a legacy command.

---

## ⚠️ One subtle risk: pattern detection can “overfit” and become brittle

Right now you’re storing patterns like:

* `<area>_<trigger>_[if_<condition>]_<action>` 

That’s good as a **template**, but the analyzer needs to be careful not to hallucinate structure from messy human naming.

### Practical fix: store conventions as *rules + examples*, not just a single pattern string

Example schema upgrade (mentally):

* `separator: "_" | "-"`
* `case: snake_case | kebab-case`
* `must_start_with_area: true/false`
* `condition_prefix: "if3 only)
* `anti_examples: [...]` (optional)

This makes enforcement easier *and* reduces “false confidence” when a user’s naming is inconsistent.

Your confidence rubric is solid already  — I’d keep that.

---

## ⚠️ Tooling best-practice tweak: tighten permissions for analyzer and generation

Your analyzer agent uses `Bash, Read, Grep` .

That’s reasonable, but best practice is:

* **Analyzer**: usually read-only (`Read, Grep, Glob`) unless Bash is truly needed
* **Generator skill**: should explicitly set `allowed-tools` so Claun constantly ([Claude Code][2])

This matters because tool sprawl is how “simple tasks become 12 minutes and 40k tokens.”

---

## 👍 The “Step 0: Load corect — with one improvement

Your plan adds Step 0 to the automations skill: read `.claude/home-assistant-assistant.md`, load `conventions:`, fallback defaults, suggest running `/ha-conventions` .

That is exactly the right enforcement point.

### One improvement: make Step 0 *fail-fast* when confidence is low

If confidence is `low/none`, don’t pretend the pattern is authoritative:

* generate using HA defaults
* add a **“convention uncertainty” banner**
* push the user toward `/ha-conventions` refinement

This prevents “I followed your conventions” when it was actually guessed.

---

## What I would ship version”

**1) `skills/ha-conventions/SKILL.md`**

* `disable-model-invocation: true`
* `allowed-tools: Read, Grep, Glob` (and Bash only if needed)

**2) Keep `agents/ha-convention-analyzer.md`** exactly like you planned

* narrow role, structured output 

**3) Keep `.claude/home-assistant-assistant.md`** as the settings store

* but expand schema slightly to be rule-based (not just one string pattern)

**4) Enforce conventions only inside the generation skill** (Step 0)

* never “globally” preload giant specs
* this aligns with Claude’s “only load what’s needed” skill model ([Claude][1])

---

If you want, I can rewrite your plan into an updated version entions command` with a **manual skill**

* adds recommended frontmatter + tool restrictions
* tweaks the convention schema so it’s harder to overfit and easier to enforce

[1]: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices "Skill authoring best practices - Claude API Docs"
[2]: https://code.claude.com/docs/en/skills "Extend Claude with skills - Claude Code Docs"
[3]: https://code.claude.com/docs/en/plugins-reference "Plugins reference - Claude Code Docs"
