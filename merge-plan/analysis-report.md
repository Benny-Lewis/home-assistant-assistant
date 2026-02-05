# Plugin Comparison Report: Documentation Compliance Review

This document analyzes every section of `ha_plugins_merge_fix_plan-v4.md` against official Anthropic Claude Code documentation (fetched 2026-02-05) and provides specific recommendations for what to change before using it to build the final plugin.

## Executive Summary

- **Total sections analyzed:** 48
- **Correct:** 12
- **Partially Correct:** 32
- **Incorrect:** 2
- **Missing Context:** 2
- **Critical issues found:** 5

### Top 5 Findings

1. **Sections 0.1 and 3.0 are built on a distinction Anthropic has eliminated.** The official docs state: *"Custom slash commands have been merged into skills."* The `commands/` directory is labeled *"legacy"* in the plugins reference. The entire "slash commands route; skills implement" architecture must be rewritten.

2. **`allowed-tools` semantics are consistently misunderstood across ~15 sections.** The report treats it as "restrict to only these tools." The actual meaning: *"these tools can be used WITHOUT asking permission."* Tools NOT listed are still available — Claude just asks first. This is not a hard block.

3. **Agent-specific frontmatter fields are never leveraged.** The report never mentions `memory` (persistent cross-session learning), `skills` (preloading skill content into agents), or `permissionMode` — all documented agent capabilities that would strengthen the merged plugin.

4. **`argument-hint` frontmatter field is never mentioned.** Multiple skills accept arguments but none specify this field, which provides autocomplete hints in the `/` menu.

5. **Hook configurations lack required specifics.** The report describes hooks by behavior but never specifies hook handler `type` (command/prompt/agent), case-sensitive event names, or `${CLAUDE_PLUGIN_ROOT}` path requirements.

---

## How to Read This Document

**Classifications:**
- **Correct** — Aligns with official docs. No change needed.
- **Partially Correct** — Right direction, details need adjustment.
- **Incorrect** — Contradicts official docs. Must be rewritten.
- **Missing Context** — Valid but incomplete.

**Official sources used:**
- [Plugins guide](https://code.claude.com/docs/en/plugins)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference)
- [Skills guide](https://code.claude.com/docs/en/skills)
- [Subagents guide](https://code.claude.com/docs/en/sub-agents)
- [Hooks reference](https://code.claude.com/docs/en/hooks)
- [MCP guide](https://code.claude.com/docs/en/mcp)

---

## Section-by-Section Analysis

---

### Current Status (lines 14–62)

**Classification: Partially Correct**

**Analysis:**
- References `.claude-plugin/marketplace.json` for plugin 2 — there is no official `marketplace.json` inside `.claude-plugin/`. Only `plugin.json` belongs there. Marketplace files live at the marketplace level, not inside individual plugins.
- Lists files in `commands/` without flagging that `commands/` is labeled **"legacy"** in the plugins reference: *"Skill Markdown files (legacy; use skills/ for new skills)"*.
- The manifest diff notes correctly identify that `home-assistant-assistant` omits `commands/agents/skills/hooks` pointers. Per the plugins reference, these are optional — Claude Code auto-discovers directories at the plugin root.

**Recommendations:**
1. Remove or correct the `.claude-plugin/marketplace.json` reference.
2. Add a note that `commands/` is legacy; the merged plugin should place all logic in `skills/`.
3. The recommendation to "add explicit commands/agents/skills/hooks fields for consistency" is fine but should note these fields are optional — Claude Code discovers default directories automatically.

---

### 0) North-star invariants (lines 63–71)

**Classification: Correct**

No conflicts with official documentation. These are project-level acceptance criteria (no unsupported attributes, no semantic substitutions, no brittle edits, no secret leakage, never deploy without request, evidence-based validation). All sound.

---

### 0.1 Commands vs Skills (lines 72–101)

**Classification: Incorrect**

**Analysis:**
This section builds the entire merge architecture on a distinction between "slash commands" and "skills" that **Anthropic has officially eliminated**:

> *"Custom slash commands have been merged into skills. A file at `.claude/commands/review.md` and a skill at `.claude/skills/review/SKILL.md` both create `/review` and work the same way."* — Skills docs

The document states: *"the official docs still draw a useful distinction we can exploit."* This is wrong. The docs explicitly say they are the same thing. The `commands/` directory is labeled **"legacy"** in the plugins reference.

Furthermore, the section conflates two different frontmatter fields:
- `disable-model-invocation: true` — Prevents Claude from loading the skill AND removes its description from context. Only user can invoke.
- `user-invocable: false` — Hides from `/` menu but Claude CAN still invoke it.

The document uses `disable-model-invocation: true` correctly for side-effectful entrypoints but frames it as a "slash command" property rather than a skill frontmatter property.

**Recommendations:**
1. **Rewrite this section entirely.** Replace the commands-vs-skills distinction with a single unified skill model:
   - All capabilities are skills in `skills/<name>/SKILL.md`.
   - Use `disable-model-invocation: true` for user-initiated entrypoints (deploy, rollback, connect).
   - Use `user-invocable: false` for background knowledge skills Claude should auto-invoke.
   - Use `argument-hint` for autocomplete hints on user-invoked skills.
2. The "Keep entrypoints thin" advice (Section A) is still valid — just frame it as "thin skills that delegate to other skills" rather than "commands that route to skills."
3. The "Side effects are always user-gated" advice (Section C) is correct — just use `disable-model-invocation: true` instead of framing it as a "slash command" property.

---

### 1.1 Semantic substitution bug (lines 106–126)

**Classification: Partially Correct**

**Analysis:**
The domain fix (intent classifier for inactivity vs. pure delay) is sound.

Line 125: *"Update tool allowlist in front matter if the skill relies on agents/tasks."* — The term "tool allowlist" is misleading. The correct field is `allowed-tools`, and its semantics are: **tools Claude can use WITHOUT asking permission** when the skill is active. It does NOT restrict which tools are available. Tools not listed are still usable — Claude just asks first.

**Recommendations:**
1. Replace "tool allowlist" with `allowed-tools` and clarify its actual semantics: auto-permitted tools, not a hard restriction.
2. If the skill needs to delegate to agents/tasks, add `Task` to `allowed-tools` so Claude can spawn subagents without asking.

---

### 1.2 Toolchain assumptions + AskUserQuestion schema (lines 127–138)

**Classification: Partially Correct**

**Analysis:**
- "Remove python/node dependencies" is sound and consistent with plugin portability.
- "Always provide ≥2 options" for AskUserQuestion — this is a reasonable convention but not verified as a hard platform requirement.
- References `commands/ha-connect.md` — this is in the legacy `commands/` directory.

**Recommendations:**
1. Note that `commands/` is legacy; migrate to `skills/`.
2. Frame the "≥2 options" rule as a project convention, not a platform requirement, unless verified.

---

### 1.3 Secret leakage risk (lines 139–147)

**Classification: Correct**

The "never echo tokens or prefixes" directive is sound. References `commands/ha-connect.md` which is legacy but the fix itself is correct.

**Recommendations:**
1. Minor: note `commands/` migration needed.

---

### 1.4 Brittle edits — AST editor (lines 148–157)

**Classification: Incorrect**

**Analysis:**
Line 155: *"Introduce an AST editor module/agent: parse YAML with `ruamel.yaml`, update by `id`, preserve formatting."*

This contradicts Section 1.2 which says "Remove python/node dependencies." `ruamel.yaml` is a Python library. More fundamentally, Claude Code's tool model works through `Read`, `Edit`, `Write`, `Bash`, etc. — there is no built-in YAML AST manipulation. Executing Python scripts requires `Bash`, which is functional but introduces a Python runtime dependency.

**Recommendations:**
1. Resolve the Python dependency contradiction. Two options:
   - **Accept Python as an optional dependency**: Bundle a small Python script in the plugin's `scripts/` directory, reference via `${CLAUDE_PLUGIN_ROOT}/scripts/yaml-editor.py`, and degrade gracefully if Python is missing.
   - **Use Claude's native capabilities**: Rely on Claude reading the full YAML, understanding the structure, and using `Edit` to make precise changes. This is less reliable but has zero dependencies.
2. If using scripts, ensure they live inside the plugin root (required for plugin caching) and are referenced with `${CLAUDE_PLUGIN_ROOT}`.

---

### 1.5 Deploy reminder hook (lines 158–167)

**Classification: Partially Correct**

**Analysis:**
The hook behavior recommendations are sound (conditional, deduplicated, expanded file matching). However, the section omits critical hook configuration details:
- No hook handler `type` specified. Must be one of: `command`, `prompt`, or `agent`.
- No event name casing noted. Hook events are **case-sensitive**: `PostToolUse`, not `postToolUse`.
- No `${CLAUDE_PLUGIN_ROOT}` path reference for any scripts.
- A `prompt`-type hook would be ideal here: it evaluates whether to show the reminder without needing a script file.

**Recommendations:**
1. Specify the hook handler type. A `prompt`-type `PostToolUse` hook with matcher `Edit|Write` would be ideal for intelligent, conditional reminders.
2. Note case-sensitive event names.
3. If using `command` type, reference scripts via `${CLAUDE_PLUGIN_ROOT}`.

---

### 1.6 Validation + deploy pipeline (lines 168–181)

**Classification: Partially Correct**

**Analysis:**
Domain recommendations are solid (eliminate Python dependency, evidence-based validation output, resolver-driven verification). Two structural issues:
- References `commands/ha-deploy.md` — legacy directory.
- Line 180: *"Align settings source of truth: consolidate config into a single predictable file (avoid referencing non-existent `.claude/home-assistant-assistant.md`)"* — correct flag, but the recommended replacement (`.claude/settings.local.json`) is not an officially documented pattern for plugin-created artifacts. It's a valid convention choice but should be labeled as such.

**Recommendations:**
1. Note `commands/` migration needed.
2. Label `.claude/settings.local.json` as a project convention, not an official plugin pattern.

---

### 1.7 Onboarding hardening /ha-connect (lines 182–203)

**Classification: Partially Correct**

**Analysis:**
The security recommendations are excellent (never print tokens, prefer standard env vars, cross-platform guidance, evidence-based verification). Structural issues:
- Line 199: *"Patch `commands/ha-connect.md` frontmatter: add tight `allowed-tools`, set `disable-model-invocation: true`"* — correct usage of both fields, but should migrate from `commands/` to `skills/`.
- Line 200: *"Add a reusable 'connection check' procedure/skill"* — good. This is a natural candidate for `user-invocable: false` (Claude uses it internally, users don't invoke it directly).

**Recommendations:**
1. Migrate from `commands/ha-connect.md` to `skills/ha-connect/SKILL.md`.
2. The "connection check" procedure should be a skill with `user-invocable: false`.
3. Add `argument-hint` to the connect skill if it accepts arguments.

---

### 1.8 Convention inference (lines 205–222)

**Classification: Correct**

Sound recommendations to integrate convention analysis into generation. Minor terminology issue: line 213 says *"Add a `ha-conventions` skill (or keep `/ha-conventions` as thin command)"* — since commands and skills are the same, the "(or keep as thin command)" phrasing is redundant.

**Recommendations:**
1. Remove "(or keep as thin command)" — it's always a skill.

---

### 1.9 ha-scenes skill (lines 224–233)

**Classification: Partially Correct**

**Analysis:**
Line 232: *"Add explicit tool scoping (read-only by default). If it writes scenes.yaml, require a task/confirmation step."*

Omitting `Write`/`Edit` from `allowed-tools` does NOT make the skill read-only. It means Claude must **ask permission** before writing. This is "write-gated" not "read-only." The distinction matters for user expectations.

**Recommendations:**
1. Reframe "read-only by default" as "write-gated by default (Claude asks permission before writing)."
2. Specify the concrete `allowed-tools` list: `Read, Grep, Glob` for read-only; add `Write, Edit` only if auto-writes are desired.

---

### 1.10 ha-scripts skill (lines 235–249)

**Classification: Partially Correct**

Same tool scoping issue as 1.9. Additionally, line 247 mentions the AST editor, which has the same Python dependency contradiction as Section 1.4.

**Recommendations:**
1. Same `allowed-tools` clarification as 1.9.
2. Resolve AST editor approach per 1.4 recommendations.

---

### 1.11 ha-troubleshooting skill (lines 251–265)

**Classification: Partially Correct**

**Analysis:**
Line 260: *"Tool scoping: make this a read-only skill (no Write/Edit). Allow `Bash` only for `hass-cli`."*

There is **no mechanism in `allowed-tools` to conditionally allow Bash "only for hass-cli commands."** If `Bash` is in `allowed-tools`, Claude can run any Bash command without asking. To restrict Bash to hass-cli, you need either:
- A `PreToolUse` hook on `Bash` that validates the command string, OR
- Strong prompt instructions in the SKILL.md body.

**Recommendations:**
1. Replace "Allow `Bash` only for `hass-cli`" with: "Include `Bash` in `allowed-tools` with explicit SKILL.md instructions restricting Bash to `hass-cli` commands. For stronger enforcement, add a `PreToolUse` hook on `Bash` that validates the command."
2. Clarify that omitting `Write`/`Edit` causes permission prompts, not hard blocks.

---

### 1.12 ha-log-analyzer agent (lines 267–277)

**Classification: Partially Correct / Missing Context**

**Analysis:**
The domain recommendations are sound. However, the section never addresses the agent's frontmatter configuration. Agent frontmatter uses **different fields** than skill frontmatter:
- Agents use `tools` (allowlist) and `disallowedTools` (denylist), NOT `allowed-tools`.
- Agents have `permissionMode` (default/acceptEdits/dontAsk/bypassPermissions/plan).
- Agents have `skills` to preload skill content.
- Agents have `memory` for persistent cross-session learning.

**Recommendations:**
1. Add a structural check: verify the agent uses `tools`/`disallowedTools` (not `allowed-tools`).
2. Specify `permissionMode` (likely `dontAsk` or `default` for a read-only diagnostic agent).
3. Consider `skills: [ha-troubleshooting]` to preload troubleshooting knowledge.
4. Consider `memory: project` for accumulating diagnostic patterns across sessions.

---

### 1.13 YAML syntax references (lines 279–303)

**Classification: Correct**

Sound HA domain recommendations (plural keys, modern syntax, capability-driven attributes). The progressive disclosure structure (references in `references/`) aligns with official best practices (SKILL.md under 500 lines).

---

### 1.14 log-patterns reference (lines 304–320)

**Classification: Correct**

The progressive disclosure restructuring correctly applies the official pattern. Moving procedural content to the skill/agent while keeping the file as a pattern library is best practice.

---

### 1.15 /ha-rollback (lines 322–339)

**Classification: Partially Correct**

**Analysis:**
Line 331: `disable-model-invocation: true` — correct for a side-effectful command.

Line 338: *"Tool scoping: `Read`, `Bash`, `AskUserQuestion` only."* — Including `Bash` in `allowed-tools` means Claude can run ANY Bash command without asking, including `git push`. This contradicts line 336: *"No network writes unless the user explicitly opts in."*

**Recommendations:**
1. Remove `Bash` from `allowed-tools`. Without it, Claude asks permission for every Bash command, giving the user a gate on `git push` and HA reload.
2. Migrate from `commands/` to `skills/`.
3. Add `argument-hint` if the skill accepts arguments (e.g., commit hash).

---

### 1.16 ha-conventions skill (lines 340–356)

**Classification: Partially Correct**

**Analysis:**
- Line 344: `.claude/home-assistant-assistant.md` correctly flagged as non-existent. The fix to use `.claude/ha.conventions.json` is sound.
- Line 345: Bash tool mismatch correctly identified. If the skill's workflow requires Bash, add it to `allowed-tools`.
- Line 346: Timer heuristic fix is sound and consistent with Section 1.1.

**Recommendations:**
1. Clarify whether `.claude/home-assistant-assistant.md` is "wrong pattern" or "missing file." If machine-readable, use JSON. If human-readable, `.md` is fine but must be created during onboarding.
2. Ensure `ha-conventions` name complies (it does: lowercase, hyphens, under 64 chars).
3. Verify SKILL.md is under 500 lines; move lengthy convention documentation to `references/`.

---

### 2.1 Capability blind spot (lines 359–375)

**Classification: Correct**

Sound domain fix (capability-checked generation contract). References `commands/generate.md` which is legacy but the fix itself is correct.

**Recommendations:**
1. Minor: note `commands/` migration needed.

---

### 2.2 Output truncation (lines 377–383)

**Classification: Correct**

The output scaling rule (summary + chunking/report for large lists) is a reasonable convention with no platform conflicts.

---

### 2.3 Missing semantic safety defaults (lines 385–400)

**Classification: Partially Correct**

The default gating table is sound (presence triggers with `from:` gating). Minor gap: the implementation targets include skills that may be long — should note progressive disclosure (keep contract in SKILL.md, move the gating table to `references/`).

**Recommendations:**
1. If the gating table is large, put it in `references/default-gating.md` and reference from SKILL.md.

---

### 2.4 Edit fragility (lines 401–408)

**Classification: Correct**

Aligns with Section 1.4 (adopt AST editing, adopt HAA's validation contract). Same Python dependency question applies.

---

### 2.5 /ha:generate entrypoint (lines 410–424)

**Classification: Partially Correct**

**Analysis:**
Line 422: *"Make `/ha:generate` a thin router; move logic into domain skills; split generate vs apply; keep write permissions off by default."*

This is sound architecture but:
- The `/ha:generate` naming uses the plugin namespace format (`/plugin-name:skill-name`), which is correct.
- "Keep write permissions off by default" — should be expressed as concrete `allowed-tools` without `Write`/`Edit`.
- Missing `argument-hint` for what the generate command accepts.

**Recommendations:**
1. Specify `allowed-tools: Read, Grep, Glob, AskUserQuestion` (no Write/Edit).
2. Add `argument-hint: [type] [description]` to indicate expected input.
3. Note this should be a skill in `skills/`, not `commands/`.

---

### 2.6 /ha:setup settings management (lines 426–446)

**Classification: Partially Correct**

**Analysis:**
The unified settings recommendation is sound. However:
- `.claude/ha-toolkit.local.md` is not an officially documented pattern. Neither is `.claude/settings.local.json` for plugin-created artifacts. Both are project conventions.
- Line 443: *"Constrain `Bash` usage to `hass-cli` and `git` checks"* — as noted in 1.11, `allowed-tools` cannot restrict Bash to specific commands. Needs hooks or prompt instructions.
- Line 441: *"disable-model-invocation: true since it touches credentials"* — correct usage.

**Recommendations:**
1. Label all `.claude/` settings patterns as project conventions, not official plugin patterns.
2. Replace "constrain Bash to hass-cli" with a hook-based or prompt-based enforcement approach.
3. Specify concrete `allowed-tools` list.

---

### 2.7 Naming contract (lines 448–468)

**Classification: Correct**

Well-aligned with official docs. The progressive disclosure recommendation (SKILL.md contract + `references/` for tables) directly follows the 500-line guideline.

---

### 2.8 Naming analyzer agent (lines 470–495)

**Classification: Partially Correct**

**Analysis:**
The agent recommendations are sound but miss several agent-specific capabilities:
- **`memory` field**: A naming analyzer would benefit greatly from `memory: project` to accumulate naming patterns across sessions.
- **`skills` field**: Should preload `ha-naming-conventions` skill for domain knowledge.
- **`permissionMode`**: A read-only audit agent should use `dontAsk` or keep `default`.
- Line 479: *"Tighten: keep Bash read-only and restrict to `hass-cli`"* — agents use `tools` (allowlist) and `disallowedTools` (denylist), not `allowed-tools`. And Bash cannot be restricted to specific commands via these fields.

**Recommendations:**
1. Add `memory: project` to accumulate naming patterns.
2. Add `skills: [ha-naming-conventions]` to preload naming rules.
3. Use `tools` and `disallowedTools` (agent fields), not `allowed-tools` (skill field).
4. For Bash restriction, add a `PreToolUse` hook in the agent's frontmatter or use strong prompt instructions.

---

### 2.9 /ha:apply-naming (lines 497–513)

**Classification: Partially Correct**

Line 504: `disable-model-invocation: true` — correct for side-effectful rename operations.

**Recommendations:**
1. Migrate from `commands/` to `skills/`.
2. Specify `allowed-tools` explicitly.
3. Add `argument-hint` for expected input format.

---

### 2.10 config-debugger agent (lines 514–525)

**Classification: Partially Correct**

**Analysis:**
Sound recommendations for read-only diagnostic routing. Missing agent-specific capabilities:
- Should use `disallowedTools: [Write, Edit]` instead of manually listing allowed tools.
- Missing `memory: project` for accumulating debug patterns.
- Missing `permissionMode` specification.

**Recommendations:**
1. Use `disallowedTools: [Write, Edit, NotebookEdit]` to block writes while allowing everything else.
2. Add `memory: project` for cross-session learning.
3. Specify `permissionMode: default`.

---

### 2.11 ha-toolkit hooks.json (lines 526–551)

**Classification: Partially Correct**

**Analysis:**
The hook design recommendations are sound (post-edit lint, pre-edit reminder, dedupe, extend file matchers). Missing specifics:
- No hook handler `type` specified. The post-edit lint is a natural fit for `prompt` type (LLM evaluates the edit).
- No `${CLAUDE_PLUGIN_ROOT}` mentioned for any script paths.
- Event names should be explicitly noted as case-sensitive.

**Recommendations:**
1. Specify hook types: `prompt` for intelligent lint, `command` for deterministic validation scripts.
2. Reference all script paths via `${CLAUDE_PLUGIN_ROOT}`.
3. Note case-sensitive event names: `PreToolUse`, `PostToolUse`.

---

### 2.12 /ha:validate (lines 552–579)

**Classification: Partially Correct**

**Analysis:**
The two-tier validation approach (HA-backed first, best-effort local second) is sound.

- Line 561: Tool mismatch (advertises auto-fix but can't write) — correctly identified.
- The recommendation for a "thin router into a shared Validator skill" is good architecture.
- Missing: `argument-hint` for the file/directory argument.
- Missing: `allowed-tools` specification.
- Consider `context: fork` for heavy validation runs to isolate from main context.

**Recommendations:**
1. Add `argument-hint: [file-or-directory]`.
2. Specify `allowed-tools` (Read, Grep, Glob, Bash for hass-cli).
3. Consider `context: fork` for isolation during heavy validation.

---

### 2.13 /ha:deploy (lines 580–613)

**Classification: Partially Correct**

**Analysis:**
The deploy pipeline recommendations are sound (validation-first, explicit opt-in for each phase, resolver-driven verification). Issues:
- Line 588: References `.claude/home-assistant-assistant.md` — not an official pattern, correctly flagged.
- `disable-model-invocation: true` — correct for deploy.
- The "auto_deploy mode" criticism is sound (violates north-star invariant #5).
- Missing `allowed-tools` specification. Deploy needs `Bash` for git/hass-cli, but as noted, this auto-permits ALL Bash commands.

**Recommendations:**
1. Specify `allowed-tools` carefully. Consider omitting `Bash` and letting Claude ask permission for each command (safer for deploy).
2. Add `argument-hint` if the skill accepts arguments.
3. Unify settings in a clearly-labeled project convention file.

---

### 2.14 /ha:analyze (lines 614–639)

**Classification: Partially Correct**

**Analysis:**
Sound recommendations (data-derived metrics, evidence for claims, capability-aware suggestions). The "focus-area" argument pattern is good.

**Recommendations:**
1. Add `argument-hint: [focus-area]` to indicate expected arguments.
2. Specify `allowed-tools: Read, Grep, Glob, Bash` (read-only + hass-cli).
3. Migrate from `commands/` to `skills/`.
4. Consider `context: fork` for heavy analysis runs.

---

### 2.15 /ha:audit-naming (lines 640–654)

**Classification: Correct**

Sound recommendations (analyzer-only, no edits, no deploy, evidence-backed counts).

**Recommendations:**
1. Minor: note `commands/` migration.
2. Consider using the `agent` frontmatter field to delegate to `naming-analyzer`.

---

### 2.16 /ha:onboard (lines 655–671)

**Classification: Partially Correct**

**Analysis:**
Line 666: *"Make onboarding a manual-only entrypoint (`disable-model-invocation: true`) and restrict Write/Edit to only the settings artifact."*

`allowed-tools` cannot restrict Write/Edit to specific file paths. It operates at the tool name level only. Path-level restrictions must be enforced in the skill body instructions or via hooks.

**Recommendations:**
1. Replace "restrict Write/Edit to only the settings artifact" with: "Include Write/Edit in `allowed-tools` and add explicit SKILL.md instructions limiting writes to the settings file. For stronger enforcement, use a `PreToolUse` hook."
2. Specify concrete `allowed-tools` list.

---

### 2.17 /ha:new-device (lines 672–695)

**Classification: Partially Correct**

**Analysis:**
Sound architecture (plan + generate snippets, capability-checked, naming-aware). Missing:
- `argument-hint: [device-description]` for the freeform input.
- The agent delegation should use the `agent` frontmatter field formally.

**Recommendations:**
1. Add `argument-hint: [device-description]`.
2. Specify `allowed-tools`.
3. Migrate from `commands/` to `skills/`.

---

### 2.18 ha-config skill (lines 696–715)

**Classification: Partially Correct**

Line 704: *"Skill frontmatter `name` is non-compliant (contains spaces/caps). Rename to something like `ha-configuration`."* — Correct per official docs: *"Lowercase letters, numbers, and hyphens only (max 64 characters)."*

**Recommendations:**
1. Name fix is correct. Keep recommendation.
2. Add `allowed-tools` specification (likely read-only: Read, Grep, Glob).
3. Verify SKILL.md is under 500 lines with progressive disclosure.

---

### 2.19 ha-devices skill (lines 716–739)

**Classification: Partially Correct**

Line 725: *"Skill frontmatter `name` is non-compliant. Rename to something like `managing-ha-devices`."* — Name must be lowercase/hyphens only, which `managing-ha-devices` satisfies, but consider a shorter name like `ha-devices` (the directory name already works).

**Recommendations:**
1. Use `ha-devices` as the name (matches directory, compliant, concise).
2. Add `allowed-tools: Read, Grep, Glob` (read-only reference skill).
3. Apply progressive disclosure: contract in SKILL.md, primers in `references/`.

---

### 2.20 ha-jinja skill (lines 740–756)

**Classification: Partially Correct**

Line 748: Name compliance fix — correct. `ha-jinja-templating` or simply `ha-jinja` works.

**Recommendations:**
1. Use `ha-jinja` (concise, compliant).
2. Add `allowed-tools: Read, Grep, Glob` (reference skill).
3. Apply progressive disclosure.

---

### 2.21 ha-lovelace skill (lines 757–773)

**Classification: Partially Correct**

Line 765: Name compliance fix — correct. `ha-lovelace-dashboards` or `ha-lovelace` works.

**Recommendations:**
1. Use `ha-lovelace` (concise, compliant).
2. Add `allowed-tools: Read, Grep, Glob` (reference skill).
3. Apply progressive disclosure.
4. Consider leaving `disable-model-invocation` as false so Claude can consult this when generating dashboard YAML.

---

### 2.22 ha-naming skill (lines 774–806)

**Classification: Partially Correct**

Line 783–784: Name fix to `ha-naming-conventions` — correct and compliant.

Line 791–795: "Enforcement hooks: wire naming rules into generators" — sound but should specify which hook type and event. A `prompt`-type `PostToolUse` hook on Write/Edit targeting YAML files could inject naming compliance reminders.

**Recommendations:**
1. Name fix is correct. Keep.
2. Specify hook types for enforcement (e.g., `prompt`-type `PostToolUse`).
3. Add `allowed-tools: Read, Grep, Glob` (reference/contract skill).
4. Clarify role: pure reference (no `agent` field) vs. active analysis (delegate via `agent` field).

---

### 3.0 Component choice (lines 808–823)

**Classification: Incorrect**

**Analysis:**
Line 811: *"We can still use a clean separation: Entry points (slash commands) ... Skills (core logic)"*

This directly contradicts official docs. Skills ARE the slash commands. The `commands/` directory is legacy. The "slash commands route; skills implement" architecture builds on a distinction that no longer exists.

The correct architecture is:
- All capabilities live in `skills/<name>/SKILL.md`.
- `disable-model-invocation: true` + `argument-hint` = user-invoked entrypoint.
- Default (no flags) = model-invoked capability.
- `user-invocable: false` = background knowledge.

**Recommendations:**
1. **Rewrite this section.** Replace the two-category model with a single-category model (all skills) differentiated by frontmatter flags.
2. The operational rule "Do not duplicate logic in both places" remains valid — just frame it as "thin skills delegate to comprehensive skills."

---

### 3.1 Skill authoring constraints (lines 824–831)

**Classification: Partially Correct**

**Analysis:**
Line 826: *"Keep each SKILL.md body <500 lines"* — correct per official docs.
Line 827: *"Avoid nested references"* — correct.
Line 828: *"Make description do real work"* — correct.
Line 829: *"Use allowed-tools to minimize blast radius"* — the intent is right but "minimize blast radius" mischaracterizes the field. `allowed-tools` controls auto-permission, not availability.
Line 830: *"Prefer utility scripts for deterministic operations"* — correct.

**Missing:**
- Skill name constraint: lowercase letters, numbers, hyphens only, max 64 characters.
- `argument-hint` field for user-invoked skills.
- `context: fork` for heavy isolated tasks.
- The distinction between `disable-model-invocation: true` (removes from context) and `user-invocable: false` (keeps in context).

**Recommendations:**
1. Add skill name constraints (max 64 chars, lowercase/hyphens only).
2. Add `argument-hint` as a recommended field for user-invoked skills.
3. Add `context: fork` guidance for heavy tasks.
4. Clarify that `allowed-tools` means "auto-permitted without asking," not "only these tools available."
5. Document the `disable-model-invocation` vs `user-invocable` distinction.

---

### 3.2 Verification-first contract (lines 832–836)

**Classification: Correct**

Sound engineering practice with no platform conflicts.

---

### 3.2.1 Packaging + caching constraints (lines 837–852)

**Classification: Partially Correct**

**Analysis:**
Line 841: *"Converge on a single installable root layout"* — the listed structure (`.claude-plugin/plugin.json`, `commands/`, `skills/`, `agents/`, `hooks/`) is correct except `commands/` is legacy.

Line 843: *"Decide whether to migrate most slash entrypoints into `skills/`"* — this should not be a decision. The official docs are clear: `commands/` is legacy, skills are the current standard. Migrate.

Line 849: *"Any references must use `${CLAUDE_PLUGIN_ROOT}` for portability"* — correct.

**Missing:**
- `.mcp.json` at plugin root for MCP server configuration.
- `.lsp.json` at plugin root for LSP servers.
- Plugin manifest field validation against the full supported set (including `outputStyles`, `lspServers`).

**Recommendations:**
1. Remove `commands/` from the target layout. Use `skills/` exclusively.
2. Add `.mcp.json` and `.lsp.json` to the layout if applicable.
3. Add a manifest validation step checking against all supported fields.

---

### 3.2.2 Repo-wide compliance sweeps (lines 853–907)

**Classification: Partially Correct**

**Analysis by item:**

**Items 1-7:** Sound recommendations (frontmatter audit, reference hygiene, content normalization, dependency checks, secrets hardening, choice overload guard, checklists).

Item 1 should add: skill name max 64 characters, and audit against the complete valid frontmatter field lists for both skills AND agents (they're different).

**Item 8 (eval-driven development):** Sound but outside plugin architecture scope.

**Item 9 (templates):** Sound.

**Item 10 (`context: fork`):** Line 903: *"Consider `context: fork` for deep troubleshooting / large scans to keep main context clean."* — Imprecise. `context: fork` creates a **fresh subagent WITHOUT conversation history**, not merely "keeps context clean." It has no awareness of prior conversation.

**Item 11 (`argument-hint`):** Correctly identifies the field. Should note it applies to skills (which ARE slash commands).

**Missing from the sweep:**
- **Hook compliance audit**: case-sensitive event names, valid hook types, `${CLAUDE_PLUGIN_ROOT}` in paths.
- **Agent frontmatter audit**: `tools`/`disallowedTools` semantics, `permissionMode`, `memory`, `skills`.
- **`user-invocable` / `disable-model-invocation` semantic audit** per each skill.
- **Plugin manifest field validation** against supported set (including `outputStyles`, `lspServers`).

**Recommendations:**
1. Item 1: Add max 64 char constraint and separate audits for skill vs agent frontmatter.
2. Item 10: Clarify `context: fork` creates a subagent without conversation history.
3. Item 11: Note `argument-hint` applies to skills (the unified mechanism).
4. **Add Item 12:** Hook compliance — case-sensitive events, valid types, `${CLAUDE_PLUGIN_ROOT}` paths.
5. **Add Item 13:** Agent frontmatter audit — `tools`/`disallowedTools`, `permissionMode`, `memory`, `skills`.
6. **Add Item 14:** `user-invocable` / `disable-model-invocation` semantic review per skill.
7. **Add Item 15:** Plugin manifest field validation.

---

### 3.3 Modules and contracts (lines 909–931)

**Classification: Correct (minor gap)**

The module decomposition (Resolver, Planner, Renderer, Editor, Validator+Reporter) is sound architecture. Minor gap: does not map modules to their corresponding skills/agents or specify which frontmatter fields apply to each.

**Recommendations:**
1. Add a mapping from each module to its skill(s) and/or agent(s), with relevant frontmatter configuration.
2. For the Editor module, note whether it should be `user-invocable: false` (model-only) or `disable-model-invocation: true` (user-only for safety).

---

### 4) Regression test plan (lines 933–943)

**Classification: Correct**

All scenarios align with north-star invariants. No platform conflicts.

**Recommendations:**
1. Consider adding a test scenario for plugin installation and skill discoverability: verify skills appear under `/plugin-name:skill-name` namespace, `user-invocable: false` skills are hidden, `disable-model-invocation: true` skills are excluded from context.

---

## Cross-Cutting Findings

### 1. Terminology: Eliminate the Commands vs Skills Distinction

**Affected sections:** 0.1, 1.2, 1.3, 1.6, 1.7, 1.15, 2.5, 2.9, 2.12, 2.13, 2.14, 2.15, 2.16, 2.17, 3.0, 3.2.1

**Official position:** *"Custom slash commands have been merged into skills."* The `commands/` directory is *"legacy."*

**Action:** Add a global note at the top of the document: "All capabilities in the merged plugin will use `skills/<name>/SKILL.md`. The `commands/` directory is legacy and will not be used." Then remove all references to a commands-vs-skills distinction.

### 2. `allowed-tools` Semantics Must Be Corrected

**Affected sections:** 1.1, 1.7, 1.9, 1.10, 1.11, 1.15, 2.5, 2.6, 2.11, 2.12, 2.13, 2.16, 2.17

**Official definition:** `allowed-tools` = *"Tools Claude can use without asking permission when this skill is active."*

**What it does NOT do:** It does not restrict which tools are available. Tools not listed are still usable — Claude just asks the user first.

**What it cannot do:** It cannot restrict a tool to specific arguments (e.g., "Bash only for hass-cli"). For that, use `PreToolUse` hooks or prompt instructions.

**Action:** Add a global clarification near the top of the document. Then review every section that mentions tool scoping.

### 3. Agent Frontmatter Fields Must Be Distinguished from Skill Fields

**Affected sections:** 1.12, 2.8, 2.10

| Feature | Skill Field | Agent Field |
|---------|------------|-------------|
| Tool control | `allowed-tools` (auto-permit list) | `tools` (allowlist) / `disallowedTools` (denylist) |
| Model invocation | `disable-model-invocation` | N/A (agents are always model-invoked) |
| User visibility | `user-invocable` | N/A (agents appear in `/agents`) |
| Execution context | `context: fork` | Always runs in own context |
| Persistent memory | N/A | `memory: user\|project\|local` |
| Preloaded skills | N/A | `skills: [skill-name, ...]` |
| Permission mode | N/A | `permissionMode` |

**Action:** Every section that discusses an agent must use agent-specific fields.

### 4. Missing Frontmatter Fields Across All Skills

**Fields that should be specified for every skill:**

| Field | When to use |
|-------|------------|
| `allowed-tools` | Always — defines auto-permitted tools |
| `argument-hint` | Any skill that accepts arguments |
| `disable-model-invocation` | Side-effectful skills (deploy, rollback, apply, connect) |
| `user-invocable` | Background knowledge skills (set to `false`) |

**Action:** Add a frontmatter specification to every skill section in the document.

### 5. Hook Configuration Requires Specifics

**Affected sections:** 1.5, 2.11, 2.22

Every hook recommendation must specify:
1. **Event name** (case-sensitive): `PreToolUse`, `PostToolUse`, etc.
2. **Matcher pattern**: Tool name regex (e.g., `Edit|Write`)
3. **Handler type**: `command`, `prompt`, or `agent`
4. **Script paths**: Must use `${CLAUDE_PLUGIN_ROOT}`

**Action:** Review all hook sections and add these specifics.

### 6. Settings Patterns Are Conventions, Not Official

**Affected sections:** 2.6, 2.13, 2.16

`.claude/settings.local.json`, `.claude/ha-toolkit.local.md`, `.claude/home-assistant-assistant.md` — none are officially documented patterns for plugin-created artifacts. The document should label its recommended settings format as a project convention choice.

**Action:** Add a note: "The settings file format is a project convention. The merged plugin will document its recommended schema but not ship the file."

### 7. `context: fork` Is Underutilized

**Affected sections:** 2.12, 2.13, 2.14, 3.2.2

Several skills described as "thin routers" to shared sub-skills would benefit from `context: fork` for isolating heavy work (validation, analysis, troubleshooting) from the main conversation context. The report mentions it only once (3.2.2 item 10) and imprecisely.

**Action:** Identify which skills should use `context: fork` and add it to their frontmatter specifications.

---

## Quick Reference: Key Official Facts

| # | Fact | Source |
|---|------|--------|
| 1 | `commands/` is legacy; use `skills/` | [Plugins reference](https://code.claude.com/docs/en/plugins-reference) |
| 2 | Skills and slash commands are merged | [Skills guide](https://code.claude.com/docs/en/skills) |
| 3 | `.claude-plugin/` contains ONLY `plugin.json` | [Plugins guide](https://code.claude.com/docs/en/plugins) |
| 4 | Plugin skills namespaced `/plugin-name:skill-name` | [Plugins guide](https://code.claude.com/docs/en/plugins) |
| 5 | Hook events are case-sensitive | [Hooks reference](https://code.claude.com/docs/en/hooks) |
| 6 | Three hook handler types: command, prompt, agent | [Hooks reference](https://code.claude.com/docs/en/hooks) |
| 7 | `allowed-tools` = auto-permitted, not a hard restriction | [Skills guide](https://code.claude.com/docs/en/skills) |
| 8 | `${CLAUDE_PLUGIN_ROOT}` required for all paths | [Plugins reference](https://code.claude.com/docs/en/plugins-reference) |
| 9 | Skill name: lowercase, numbers, hyphens, max 64 chars | [Skills guide](https://code.claude.com/docs/en/skills) |
| 10 | SKILL.md under 500 lines; use `references/` | [Skills guide](https://code.claude.com/docs/en/skills) |
| 11 | `disable-model-invocation: true` removes from context entirely | [Skills guide](https://code.claude.com/docs/en/skills) |
| 12 | `user-invocable: false` hides from menu but model CAN invoke | [Skills guide](https://code.claude.com/docs/en/skills) |
| 13 | Agent fields: tools, disallowedTools, permissionMode, skills, memory | [Subagents guide](https://code.claude.com/docs/en/sub-agents) |
| 14 | `context: fork` = subagent WITHOUT conversation history | [Skills guide](https://code.claude.com/docs/en/skills) |
| 15 | `argument-hint` provides autocomplete hints | [Skills guide](https://code.claude.com/docs/en/skills) |
| 16 | Plugin manifest only requires `name` | [Plugins reference](https://code.claude.com/docs/en/plugins-reference) |
| 17 | `outputStyles` and `lspServers` are supported manifest fields | [Plugins reference](https://code.claude.com/docs/en/plugins-reference) |
