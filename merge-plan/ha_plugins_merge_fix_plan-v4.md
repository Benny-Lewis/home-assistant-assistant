# HA Plugins Merge & Fix Plan (Living Implementation Notes)

This document is the **actionable** follow-on to the transcript scorecard.
It records:
- concrete fixes mapped to observed failures,
- where those fixes live in each plugin’s file tree,
- the merge architecture (modules + contracts),
- a regression test plan derived from the transcripts.

> The companion doc **“Claude Code Plugin Comparison”** remains the formal evaluation + scoring artifact.

---

## Current status
- ✅ Transcript-backed comparison completed.

### Ingested: home-assistant-assistant (plugin 2)
- ✅ `.claude-plugin/marketplace.json`
- ✅ `plugin-haa.json` (manifest)
- ✅ `hooks/hooks.json`
- ✅ Commands: `commands/ha-connect.md`, `commands/ha-deploy.md`, `commands/ha-rollback.md`
- ✅ Agents: `agents/ha-config-validator.md`, `agents/ha-convention-analyzer.md`, `agents/ha-entity-resolver.md`, `agents/ha-log-analyzer.md`
- ✅ Skills:
  - `skills/ha-automations/SKILL.md` + `references/common-patterns.md` + `references/yaml-syntax.md`
  - `skills/ha-conventions/SKILL.md`
  - `skills/ha-scenes/SKILL.md` + `references/yaml-syntax.md` (uploaded as `yaml-syntax-sceenes.md`)
  - `skills/ha-scripts/SKILL.md` + `references/yaml-syntax.md` (uploaded as `yaml-scripts-syntax.md`)
  - `skills/ha-troubleshooting/SKILL.md` + `references/log-patterns.md`

### Ingested: ha-toolkit (plugin 1)
- ✅ `plugin-ha-toolkit.json` (manifest)
- ✅ `hooks/hooks.json` (uploaded as `hooks.json`)
- ✅ Commands: `commands/generate.md`, `commands/setup.md`, `commands/onboard.md`, `commands/new-device.md`, `commands/plan-naming.md`, `commands/apply-naming.md`, `commands/validate.md`, `commands/deploy.md`, `commands/analyze.md`, `commands/audit-naming.md`
- ✅ Agents: `agents/device-advisor.md`, `agents/naming-analyzer.md`, `agents/config-debugger.md`
- ✅ Skills: `skills/ha-automation/SKILL.md`, `skills/ha-config/SKILL.md`, `skills/ha-devices/SKILL.md`, `skills/ha-jinja/SKILL.md`, `skills/ha-lovelace/SKILL.md`
- ✅ Skills: `skills/ha-naming/SKILL.md` (uploaded as `SKILLnaming.md`)

### 0.2 Plugin manifest diff notes
**ha-toolkit (`plugin-ha-toolkit.json`)**
- Declares `commands`, `agents`, `skills`, and `hooks` paths.
- `homepage` currently points to the `home-assistant-assistant` repo (likely a copy/paste bug).

**home-assistant-assistant (`plugin-haa.json`)**
- Minimal manifest (name/version/description/author/homepage/keywords).
- Recommendation: add explicit `commands/agents/skills/hooks` fields for consistency with ha-toolkit, unless you intentionally want Claude Code to rely on defaults.


### Settings and templates (out of scope for merge)
Per your note: **we will not include or ship any project-local settings/templates** that were only used during plugin development sessions (e.g., `.claude/settings.local.json`, template md files). The merged plugin will treat *settings as user project state* and only document a recommended schema/creation flow.

### Rough ingestion progress
- **Core plugin surfaces ingestion: 100%** (40/40 by our current definition).
- Remaining intake is now *optional* (templates/planning/docs/settings glue).

### Pending / housekeeping
- ✅ Plugin manifests disambiguated and diffed:
  - `plugin-ha-toolkit.json`
  - `plugin-haa.json`
- ⚠️ Manifest issues to fix during merge:
  - `ha-toolkit` manifest `homepage` points at the **home-assistant-assistant** repo (likely wrong).
  - `home-assistant-assistant` manifest omits `commands/agents/skills/hooks` pointers (OK if optional, but reduces clarity/portability).
---

## 0) North-star invariants (acceptance criteria)
The merged solution must enforce:
1) **No unsupported attributes** written without explicit override.
2) **No semantic substitutions** unless equivalence conditions are satisfied.
3) **No brittle string insertions** for YAML changes (AST editing only).
4) **No secret material printed** (no token prefixes).
5) **Never deploy** unless explicitly requested.
6) **Validation is evidence-based** (don’t say “passed” unless it actually ran and passed).

### 0.1 Commands vs Skills (Claude Code) — how we’ll use both
Your screenshots capture the *direction of travel*: commands and skills feel increasingly “the same thing” from a user mental model.
But the official docs still draw a useful distinction we can exploit:

- **Slash commands** are *user-invoked entrypoints* (file-based prompts with frontmatter). They can also be invoked by the model via the `SlashCommand` tool unless you disable that.
  - Use `allowed-tools` to scope blast radius.
  - Use `disable-model-invocation: true` for any side-effectful command (also removes its metadata from context).
  - `/permissions` can deny `SlashCommand` entirely.
- **Skills** are *model-invoked capabilities* (procedures + knowledge) designed for **progressive disclosure** and reuse.

**How this impacts the merge:**

**A. Keep “entrypoints” thin**
- Keep a small set of memorable slash commands (`/ha-connect`, `/ha-generate`, `/ha-validate`, `/ha-deploy`) that *route* to the right skill and gather missing context.
- Avoid duplicating business logic in both locations.

**B. Put the real logic in skills (Skill-first architecture)**
- Treat each domain capability (automations, scenes, scripts, troubleshooting, naming, device capability checks) as a skill with a clear contract.
- Put deep examples/pattern libraries in `references/` and load on-demand.

**C. Side effects are always user-gated**
- Anything that can change state (deploy/reload/create helpers/apply patches) must be:
  - `disable-model-invocation: true` if kept as a slash command
  - or a skill that explicitly requires user confirmation before writing/deploying

**D. Token + context hygiene**
- Don’t flood context with giant command descriptions; keep descriptions short.
- Don’t preload huge pattern libraries—use progressive disclosure.

---

## 1) home-assistant-assistant — fixes (mapped to observed failures)

### 1.1 Semantic substitution bug: timer pattern used for inactivity semantics
**Observed:** In `simple-automation`, a timer-based pattern was emitted for “turn off 3 minutes after motion stops,” which is not equivalent unless motion-off gating/cancel logic exists.

**Where likely to fix:**
- `skills/ha-automations/skill.md`
- `skills/ha-automations/references/common-patterns.md`
- any templates under `templates/` if they exist for automations

**Fix design:**
- Add an **intent classifier**:
  - *Inactivity / delay-after-off* → use `wait_for_trigger` on `to: off` with `for:` OR trigger `to: off` with `for:`.
  - *Pure delay* → timer helper allowed.
- Timer helper allowed for inactivity only if:
  - timer starts when motion goes `off`,
  - timer cancels/resets if motion goes `on`,
  - off action re-checks motion is still `off` at expiry.

**SKILL.md patch needed:**
- Replace the rule “>30s → timer helper” with the classifier + equivalence guard.
- Update tool allowlist in front matter if the skill relies on agents/tasks.

### 1.2 Toolchain assumptions (python/node) and AskUserQuestion schema errors
**Observed:** onboarding + some automation flows attempted `python3` and had AskUserQuestion options schema bug.

**Where likely to fix:**
- `agents/ha-entity-resolver.md` (prompt/tooling suggestions)
- `commands/ha-connect.md` (onboarding workflow)
- `templates/` (if prompt scaffolding emits malformed AskUserQuestion)

**Fix design:**
- Remove python/node dependencies for file operations; rely on built-in Claude Code tools (`Read/Edit/Write/Grep/Glob`) and `hass-cli`.
- Add a guard in any “ask user to choose” step: always provide ≥2 options.

### 1.3 Secret leakage risk (token prefixes)
**Observed:** onboarding printed `TOKEN_PREFIX: ...` in transcript.

**Where likely to fix:**
- `commands/ha-connect.md` or onboarding agent instructions

**Fix design:**
- Explicit directive: never echo tokens or prefixes; only log “configured / present / length”.

### 1.4 Brittle edits (“string not found” insertions)
**Observed:** occasional failures inserting YAML based on anchor strings.

**Where likely to fix:**
- skills that modify YAML (`skills/ha-automations`, `skills/ha-scenes`, `skills/ha-scripts`)

**Fix design:**
- Introduce an AST editor module/agent: parse YAML with `ruamel.yaml`, update by `id`, preserve formatting.
- Expose as a reusable internal tool/agent or shared template.

### 1.5 Deploy reminder hook is too unconditional
**Observed:** `hooks/hooks.json` injects reminders on Edit/Write for automations/scripts/scenes.

**File:** `hooks/hooks.json`

**Fix design:**
- Make deploy suggestion conditional on validation being available/passed, or switch to a post-edit summary hook.
- Expand file matching to additional HA config targets (packages/helpers).
- De-duplicate reminders within a session.

### 1.6 Validation + deploy pipeline truthiness and portability
**Observed:** The transcripts show frequent “validation passed” UX; this must be **evidence-based** and resilient to missing local toolchains.

**Files:**
- `agents/ha-config-validator.md`
- `commands/ha-deploy.md`

**Fix design:**
- **Eliminate hard python dependency** in validation (python/python3 may not exist). Prefer HA’s own config validation endpoint and treat YAML syntax as implied by HA validation. If a YAML parser is used, it must be optional with a clear fallback.
- Validation output must include **what actually ran** (which checks executed vs skipped) and must never print “Validation passed” unless all required checks ran and passed.
- Deploy flow must never reload or claim success until validation returns success.
- Verification step should not assume `automation.<name>` entity_id exists; instead verify by listing automations or searching by `id`/alias.
- Align settings source of truth: consolidate config into a single predictable file (avoid referencing non-existent `.claude/home-assistant-assistant.md` if you don’t ship it).

### 1.7 Onboarding hardening for `/ha-connect` (secrets + portability)
**Observed in `commands/ha-connect.md`:**
- Prints the token prefix (`echo $HA_TOKEN | head -c 10`) → **secret leakage**.
- Encourages persisting tokens in shell rc files (`~/.zshrc`, `~/.bashrc`) → high-risk, and brittle on Windows.
- Uses non-standard env names (`HA_TOKEN`, `HA_URL`) while `hass-cli` commonly expects `HASS_TOKEN` / `HASS_SERVER` (and/or a CLI config file).

**Fix design (minimal, high impact):**
1) Never print tokens/prefixes. Only report “present/not present”.
2) Prefer standard env var names (`HASS_TOKEN`, `HASS_SERVER`). Support `HA_*` as aliases for backwards compatibility.
3) Do not auto-edit shell rc by default. Offer three explicit storage options:
   - (Recommended) `hass-cli` config file (if available)
   - (Safe, project-scoped) `.claude/settings.local.json`
   - (Ephemeral) export in the current shell session only
4) Cross-platform guidance: include PowerShell/Git Bash equivalents; avoid assuming zsh/bash.
5) Evidence-based verification: run a single read-only call (e.g., list a few states) and report exactly what ran.

**Where to implement:**
- Patch `commands/ha-connect.md` frontmatter:
  - add tight `allowed-tools`
  - set `disable-model-invocation: true`
- Add a reusable “connection check” procedure/skill used by deploy/validate/generate.

---

### 1.8 Convention inference is strong; wire it into generation and keep it cheap
**New evidence:** `agents/ha-convention-analyzer.md` provides an explicit, conservative process to infer naming conventions (IDs + aliases) and timer preferences with confidence levels.

**Why this matters:**
- This is the cleanest way to make generated output match *the user’s repo* instead of hardcoding “our” conventions.

**Fix / integration plan:**
- Add a `ha-conventions` skill (or keep `/ha-conventions` as thin command) that:
  1) runs the convention analyzer agent,
  2) stores its results in a small project-local artifact (e.g., `.claude/ha.conventions.json`),
  3) makes generators read those conventions when rendering IDs/aliases and deciding inline delay vs helpers.
- Add an output scaling rule: if conventions report is long, summarize + optionally write full report.

**Guardrails:**
- Convention inference should never override semantics (timer “preference” cannot justify timer substitution for inactivity).

---

### 1.9 `ha-scenes` skill needs capability checks and “no implicit deploy”
**New evidence:** `skills/ha-scenes/skill.md` is clean and short, but it currently:
- implies “Write to scenes.yaml” then “Deploy via /ha-deploy” as part of the default process.

**Fix design:**
- Add a mandatory “capability snapshot” step before choosing scene attributes (brightness-only vs color_temp, etc.).
- Change step 7 to: “Offer optional deploy/reload *only if user explicitly requests*.”
- Add explicit tool scoping (read-only by default). If it writes scenes.yaml, require a task/confirmation step.

---

### 1.10 `ha-scripts` skill is structurally solid but needs the same safety contracts (capability checks + no implicit deploy)
**New evidence:** `skills/ha-scripts/skill.md` correctly frames scripts as reusable sequences (not event-driven) and provides a sensible flow: intent → resolve entities → generate YAML → preview → write → deploy.

**Issues / merge impact:**
1) **Implicit deploy:** step 6 says “Deploy via /ha-deploy.” This violates invariant #5 (never deploy unless explicitly requested).
2) **No capability gate:** scripts often touch `climate`, `media_player`, `cover`, etc., where valid service data depends on supported modes/features. The skill doesn’t require capability snapshots prior to emitting service calls.
3) **Write defaults:** the process assumes writing to `scripts.yaml`. In the merged architecture we want “generate” and “apply” split, with write gated.

**Fix design:**
- Add capability snapshot requirement (same contract as scenes).
- Make deploy optional: offer only if user explicitly asks.
- Add mode guidance as a contract: if delays/waits or concurrency possible, require explicit `mode` selection.
- Split generate vs apply: generator outputs YAML + assumptions; apply skill edits via AST editor and then validates.

---

### 1.11 `ha-troubleshooting` skill is the right “evidence-first” spine; tighten it into the merged validation contract
**New evidence:** `skills/ha-troubleshooting/skill.md` has the correct posture: gather evidence first, then analyze; it explicitly recommends automation state checks, error logs, traces, and entity history.

**Strengths to keep:**
- Explicit “never guess without evidence” principle.
- Simple 5-step flow (identify → gather → analyze → report → offer fixes).
- Uses trace/history/logs as first-class data sources.

**Merge fixes:**
1) **Tool scoping:** make this a read-only skill (no Write/Edit). Allow `Bash` only for `hass-cli` and optionally Read/Grep for local YAML.
2) **Trace portability:** don’t hardcode brittle endpoints. Prefer UI traces; CLI/API only if known-good.
3) **Unify with validator/reporting:** troubleshooting outputs should share the same “what ran vs skipped” evidence table as `ha-config-validator`.
4) **Resolver integration:** always resolve canonical entity IDs first via `ha-entity-resolver` (avoid guessing `automation.name`).
5) **Output scaling:** if history/log output is large, summarize + offer chunking or write a report file.

---

### 1.12 `ha-log-analyzer` agent is a good skeleton; make it resolver-driven and portable
**What it’s for:** a repeatable sequence to explain “why didn’t it trigger?” using automation state, traces, history, and the error log.

**Merge fixes:**
- **Resolver-first:** never assume `automation.<name>`; always resolve a canonical entity id.
- **Trace as best-effort:** prefer UI traces; only use CLI/API traces if confirmed working; never claim “trace checked” unless it was.
- **History window is explicit:** always state the time range searched (e.g., last 24h) and allow override.
- **Evidence table required:** include “what ran vs skipped” in every run.

---

### 1.13 YAML syntax references are outdated; consolidate + modernize
**Problem:** we currently have *multiple* YAML “syntax reference” docs across the plugins, and they don’t agree. Several still teach legacy keys like `trigger:`/`condition:`/`action:` with `platform:`/`service:`.

**Files implicated (current uploads):**
- `skills/ha-automations/references/yaml-syntax.md` (uploaded as `yaml-syntax.md`)
- `skills/ha-scenes/references/yaml-syntax.md` (uploaded as `yaml-syntax-sceenes.md`)
- `skills/ha-scripts/references/yaml-syntax.md` (uploaded as `yaml-scripts-syntax.md`)

**Merge fixes (single source of truth):**
1) **Automations:** update to current Home Assistant YAML docs (plural top-level keys):
   - `triggers` / `conditions` / `actions`
   - list items use `- trigger:` / `- condition:` / `- action:`
   - standardize on `target:` + `data:` for service/action calls
2) **Scripts:** update to current script docs (sequence actions):
   - keep the current `sequence:` structure, but prefer the modern action form rather than teaching only `service:`
   - keep `choose`, `delay`, `wait` patterns, but ensure examples match HA’s current YAML vocabulary
3) **Scenes:** the basic `entities:` mapping is directionally correct, but tighten guidance:
   - **color temperature units:** do not claim “Kelvin or mired” interchangeably; treat as *capability-driven* (`color_temp_kelvin` vs `color_temp`) and generate whichever the entity actually exposes.
   - avoid promising cross-domain state changes that may not be reliably scene-applied (locks/climate/media) unless capability + behavior is verified.
   - include `id:` in the example format for editor compatibility.

**Generator rule:** never output a mixed schema. If the user repo uses an older format, we either:
- detect and match it, or
- offer a one-time migration and keep outputs consistent thereafter.

### 1.14 `log-patterns` reference is useful, but needs portability + best-effort trace guidance
**New evidence:** `skills/ha-troubleshooting/references/log-patterns.md` is a solid starter pattern library (entity not found, service typos, template errors, connectivity, unavailable entities).

**Issues / merge fixes:**
1) **Brittle trace endpoint guidance:** it recommends `hass-cli raw get /api/trace/automation.name`.
   - Fix: treat traces as best-effort; prefer UI traces; only run CLI/API traces if confirmed working.
2) **History queries missing a window:** it shows `/api/history/period?filter_entity_id=...` without an explicit start.
   - Fix: always specify “last N hours” (explicit window) and report it.
3) **Entity id placeholders:** uses `automation.name` / `automation_name` patterns.
   - Fix: resolver-first; show placeholders as `{automation_entity_id}` and always resolve it.
4) **Cross-platform shell assumptions:** examples use `grep`.
   - Fix: keep `grep` as an optional convenience, but provide a PowerShell alternative or a pure-Claude workflow (“search within fetched logs”).

**Restructure (progressive disclosure):**
- Keep this file as the *pattern library only* (errors → likely cause → fix).
- Move “how to fetch traces/logs/history” into the troubleshooting skill/agent, where we can enforce evidence tables + tool scoping.

---

### 1.15 `/ha-rollback` is useful, but must be safer-by-default
**New evidence:** `commands/ha-rollback.md` (uploaded as `ha-rollback.md`).

**Issues:**
- It does a `git push` by default (high-risk, and violates “never do side effects unless asked”).
- It performs HA reload without an explicit user request.

**Fix design:**
- Add `disable-model-invocation: true`.
- Change defaults to:
  1) show `git status` + current `HEAD` + recent commits,
  2) checkout a rollback commit **locally** (or create a `rollback/<timestamp>` branch),
  3) stop and ask if you want to (a) validate locally, (b) reload HA, and/or (c) push.
- No network writes unless the user explicitly opts in.

**Tool scoping (recommended):** `Read`, `Bash`, `AskUserQuestion` only.

### 1.16 `ha-conventions` skill is high leverage but currently inconsistent
**New evidence:** `skills/ha-conventions/SKILL.md` (uploaded as `SKILL-haconventions.md`).

**Issues:**
1) It references `.claude/home-assistant-assistant.md`, but your repo tree doesn’t show that file (and relying on it breaks portability).
2) The SKILL uses Bash commands in examples, but its frontmatter tools do **not** include `Bash` (tooling mismatch).
3) It recommends “timer helpers for delays > 30 seconds,” which caused a transcript failure when “inactivity” semantics were substituted with a timer pattern.

**Fix design:**
- Make conventions output a small, explicit artifact:
  - write to `.claude/ha.conventions.json` (or store inside `.claude/settings.local.json`) and treat it as the single source of truth.
- Fix tool mismatch:
  - either remove Bash snippets and use Claude-native `Read/Grep/Glob`, or add `Bash` explicitly.
- Replace the “>30s ⇒ timer helper” heuristic with a semantics-first classifier:
  - distinguish **pure delay** vs **delay-after-state-change (inactivity)**.
  - allow timers only when equivalence constraints are met (cancel/reset on re-activation).

## 2) ha-toolkit — fixes (mapped to observed failures)

### 2.1 Capability blind spot (unsupported attributes)
**Observed:** scene included `color_temp` on a brightness-only lamp.

**Current file evidence:** `home-assistant-assistant/agents/device-advisor.md` has a solid “device onboarding” flow, but it never requires *capability discovery* before suggesting automations/scenes/cards; it jumps straight from identification → naming → suggestions.

**Where likely to fix:**
- `agents/device-advisor.md` (make capability checks mandatory before emitting YAML)
- downstream generators (e.g., `commands/generate.md`, scene/automation skills)

**Fix design (capability-checked generation contract):**
- Add a required step **between Device Identification and Naming**:
  1) Resolve the canonical entity id(s)
  2) Pull a capability snapshot via `hass-cli state get <entity_id>`
  3) Extract and store “allowed knobs” per domain
  4) Enforce: **only emit YAML fields/services that are supported**, unless user explicitly overrides.

---

### 2.2 Output truncation on inventories
**Observed:** unconfigured-detection list truncated.

**Fix design:**
- Add an “Output scaling rule”:
  - If list > ~25 items, output a **summary** + ask whether to (a) continue in chunks, or (b) write a report file.

---

### 2.3 Missing semantic safety defaults
**Observed:** arrival trigger lacked `from: not_home` gating.

**New evidence:** `home-assistant-assistant/skills/ha-automation/skill.md` is currently a *general tutorial* skill and it does not enforce state-transition gating rules as defaults (e.g., "to home" triggers should usually specify a `from` to avoid re-fires / startup edge cases).

**Fix design:**
- Add a **default gating table** to the skill (and the generator contract):
  - Presence: `to: home` ⇒ default `from: not_home` (unless user explicitly wants "any transition to home")
  - Presence: `to: not_home` ⇒ default `from: home`
  - Motion inactivity: prefer `to: off` with `for:` rather than timer substitution.

**Where to implement:**
- `home-assistant-assistant/skills/ha-automation/skill.md` (policy + templates)
- the merged generator skill (`skills/ha-automations/`) to guarantee the rule is applied even if a user never reads the tutorial.

### 2.4 Edit fragility and weaker traceability
**Observed:** occasional edit failures; fewer “validation passed” tables/diffs.

**Fix design:**
- Adopt home-assistant-assistant’s validation + reporting contract.
- Replace brittle edits with AST editing.

---

### 2.5 `/ha:generate` entrypoint is schema-inconsistent + too write-happy
**Observed:** `home-assistant-assistant/commands/generate.md` is the main generator entrypoint, but its embedded YAML patterns still use legacy keys like `trigger:`/`action:`/`condition:` with `platform:`/`service:`.

**New evidence:** `home-assistant-assistant/skills/ha-automation/skill.md` is also written in this older syntax (and even includes a top-level `automation:` block), which conflicts with Home Assistant’s current *plural* YAML schema (`triggers`/`conditions`/`actions`) and the “automations.yaml must be a list” rule.

**Why this matters:**
- Mixed schemas cause subtle validation failures and makes AST editing harder.
- Top-level `automation:` is wrong for `automations.yaml` and encourages brittle insertion edits.

**Fix design (high leverage, low risk):**
1) Standardize on the current HA YAML schema.
2) Ban `automation:` root in generator outputs unless the target is explicitly `configuration.yaml` labeled blocks.
3) Make `/ha:generate` a thin router; move logic into domain skills; split generate vs apply; keep write permissions off by default.

---

### 2.6 `/ha:setup` settings management is inconsistent with `/ha-connect` and is not safe-by-default
**File evidence:** `home-assistant-assistant/commands/setup.md` uses a project-local markdown settings file `.claude/ha-toolkit.local.md` and stores **ha_url**/**ha_token** there.  It also enables `Write`/`Edit`/`Bash` by default.

**Issues:**
1) **Settings format divergence**: ha-toolkit uses `.claude/ha-toolkit.local.md`  while home-assistant-assistant is moving toward `.claude/settings.local.json` (and/or standard `hass-cli` config). Divergence makes the merged plugin brittle.
2) **Secret handling risk**: writing tokens into a plaintext markdown file is easy, but it’s not a great default. (At minimum, ensure `.claude/` is in `.gitignore` and avoid printing anything.)
3) **CLI assumption risk**: the “test” step uses `hass-cli state list --limit 1`.  Flags like `--limit` have already been a recurring failure mode; the merged approach should avoid non-portable flags or feature-detect them.
4) **Too write-happy**: this is a reconfigure command; it should be able to run read-only checks without enabling broad write access by default.

**Fix design (merge-ready):**
- **Unify settings storage** under one mechanism:
  1) Prefer standard env vars (`HASS_SERVER`, `HASS_TOKEN`) for ephemeral sessions.
  2) Prefer a single project-local config file (`.claude/settings.local.json`) for durable per-project config.
  3) Optionally support `hass-cli`’s own config file if you want CLI-native persistence.
- **Make `/ha:setup` a thin wrapper** that calls the same shared “connection check” procedure/skill as `/ha-connect`.
- **Disable model invocation** (`disable-model-invocation: true`) since it touches credentials.
- **Constrain tools**:
  - Keep `Write/Edit` only for the settings file path(s).
  - Constrain `Bash` usage to `hass-cli` and `git` checks.
- **Feature-detect CLI flags** (or avoid them): if you must limit output, do it with piping (`| head -n 1`) rather than assuming `--limit` exists.

---

### 2.7 Naming contract exists but needs to become enforceable and merge-safe
**File evidence:** `home-assistant-assistant/skills/ha-naming/skill.md` is a strong baseline naming guide (entity_id rules, recommended patterns, domain-specific examples, anti-patterns, migration steps).

**Issues (merge impact):**
1) **Skill metadata hygiene:** frontmatter `name:` should be lowercase hyphenated for reliable selection (no spaces / caps).
2) **Too much “general advice” inside the skill body:** the skill is long and table-heavy; this increases context cost when invoked. It should use progressive disclosure: keep the contract + decision rules in SKILL.md, move large tables/examples into `references/`.
3) **Not wired into generators/editors:** today it’s a guide, not a rule-set. The merged system needs a *contract* that generators must follow (and a linter/analyzer to enforce).

**Fix design (turn guide into contract):**
- Refactor into:
  - `skills/ha-naming/SKILL.md` (short):
    - One chosen default convention (Area-first) + allowed abbreviations policy
    - Canonical entity_id template per domain
    - Alias naming template for automations/scenes/scripts
    - Prohibited patterns list (numbers-first, inconsistent abbreviations, mixed ordering)
    - Output contract: when generating, always produce (a) entity_id suggestion, (b) friendly_name suggestion, (c) rationale.
  - `skills/ha-naming/references/abbreviations.md` (tables)
  - `skills/ha-naming/references/domain-examples.md` (long examples)

---

### 2.8 Naming analyzer agent is strong but needs tighter guarantees and better integration
**File evidence:** `home-assistant-assistant/agents/naming-analyzer.md` defines a structured audit process (data collection → pattern detection → inconsistency identification → dependency mapping) and a report format that quantifies issues and shows exact locations.

**Strengths to keep:**
- Clear responsibilities and report schema.
- Dependency mapping is explicitly called out (this is essential for safe rename plans).
- Uses file-native tooling (Read/Glob/Grep) plus optional `hass-cli` (“if available”).

**Issues / merge fixes:**
1) **Tool blast radius:** agent currently allows `Bash` always.
   - Tighten: keep Bash read-only and restrict to `hass-cli` + shell introspection.
   - Explicitly prohibit writing, deploying, or renaming; this agent should only *plan*.
2) **CLI portability:** the agent says “query all entities via hass-cli” but doesn’t define a stable, cross-platform query (and we’ve already seen brittle flags elsewhere).
   - Add a canonical query sequence (state list → filter → state get) aligned with `ha-entity-resolver`.
3) **Output scaling:** report format can get huge; add a rule: if >N findings, produce summary + write a report file or chunk results.
4) **Integration points:** the report references `/ha:plan-naming` and `/ha:apply-naming`.
   - In the merged plugin, standardize these as skills (or keep as thin commands) with `disable-model-invocation: true` for apply.
   - Ensure generators call naming-analyzer when introducing new entities/helpers.

**Concrete patch:**
- Keep `naming-analyzer` as a read-only audit agent.
- Implement two downstream skills:
  - `ha-plan-naming` → writes a rename plan + dependency map.
  - `ha-apply-naming` → applies plan via AST editor, then validates.

---

### 2.9 `/ha:apply-naming` is the right direction; enforce dry-run + dependency safety
**New evidence:** `commands/apply-naming.md` (uploaded as `apply-naming.md`).

**What’s good:**
- It already frames rename as a **multi-phase** operation: parse mapping → backup → apply renames → update references → validate.

**Fixes to make it merge-safe:**
1) Add `disable-model-invocation: true` (renames are side-effectful).
2) Default to **dry-run**:
   - print a plan: entities to rename, files to edit, expected diffs.
   - require confirmation before any `hass-cli` rename or file edit.
3) Replace “string replace” edits with an AST-aware updater for YAML where possible (automations/scenes/scripts).
4) Add explicit dependency coverage:
   - Lovelace YAML, templates, blueprints references, groups/areas, scripts/automations, helpers.
   - Report “searched + updated” vs “searched + not found.”
5) Validation must be evidence-based (never claim success without showing what ran).

### 2.10 `config-debugger` agent should be wired into the evidence-first troubleshooting spine
**New evidence:** `agents/config-debugger.md` (uploaded as `config-debugger.md`).

**Merge recommendation:**
- Keep it as a **read-only diagnostic subagent** and route to it from `ha-troubleshooting` when failures look like YAML/schema/structure problems.
- Align it with the validator/reporting contract:
  - always specify what checks ran vs skipped,
  - always cite the exact file(s) examined,
  - never propose “fixes” that assume a schema you haven’t verified in-repo.

**Tool scoping:** `Read`, `Grep`, `Glob`, optional `Bash` for `hass-cli` only.

### 2.11 ha-toolkit `hooks.json` is directionally better than HAA’s, but needs merge-hardening
**New evidence:** `hooks/hooks.json` (uploaded as `hooks.json`).

**What it does today**
- **PreToolUse (Edit/Write):** if editing `automations.yaml`, `scripts.yaml`, or `scenes.yaml`, it reminds the user to run `/ha-deploy` afterward.
- **PostToolUse (Write/Edit):** if a `.yaml` file looks like HA config (contains `automation:`, `script:`, `scene:`, `light:`, `sensor:`, etc.), it does a quick heuristic lint: indentation, boolean casing, entity_id format.

**What’s good (keep)**
- The **post-edit lint** concept is valuable: it catches common foot-guns immediately.
- It scopes the pre-edit reminder to high-signal HA files, which reduces noise.

**Problems (fix in merge)**
1) **Schema detection is legacy-biased** (`automation:` / `script:` / `scene:`) and can miss modern list-based schema (or falsely trigger on unrelated YAML).
2) The lint rule “2 spaces” is a **style preference**, not a hard validator; treat as advisory.
3) Entity_id validation needs a correct shape: `domain.object_id` where `object_id` allows `[a-z0-9_]+`.
4) It nudges users toward **deploy** (side effect). We want a neutral posture: validate first, deploy only when explicitly requested.

**Merged hook design (recommended)**
- Keep a **single shared hooks.json** with two prompts:
  - **Post-edit (always safe):** lightweight lint + “what changed” summary. Never claims validation success.
  - **Pre-edit (high-signal files only):** reminder phrased as:
    - “When you’re done editing, run `/ha-validate` (safe). If you want to apply changes, run `/ha-deploy`.”
- Add **dedupe** (don’t repeat the same reminder every edit).
- Extend file matchers beyond just the three YAMLs (packages, helpers, `configuration.yaml`, `packages/*.yaml`, etc.) while staying conservative.
- If `hass-cli` is available, optionally offer a *single* explicit “run real validation now?” step—never auto-run.

### 2.12 `/ha:validate` is a good skeleton but currently over-promises; make it evidence-first and HA-backed
**New evidence:** `commands/validate.md` (uploaded as `validate.md`).

**What it gets right (keep)**
- Separates **local lint** vs **HA-backed** validation.
- Supports validating a specific file/dir via `$ARGUMENTS`.
- Has a clear report format concept (file-by-file + summary).

**Concrete issues to fix**
1) **It advertises auto-fix but the command can’t write** (no `Write`/`Edit` in allowed-tools). Either:
   - add `Write/Edit` and gate all changes behind explicit confirmation, or
   - remove auto-fix claims and route fixes to a separate `/ha:apply` command.
2) **Local YAML parsing is not actually specified**, and naïve YAML parsers will choke on HA tags (`!include`, `!secret`). So local mode should be clearly labeled “best-effort lint,” not “validation.”
3) “2 spaces” + “true/false” are **style rules**, not validity rules. Treat as warnings unless HA validation confirms a failure.
4) “Valid domains (light, switch, sensor, etc.)” is brittle and incomplete. Prefer:
   - HA-backed checks (best), or
   - only validate `domain.object_id` shape syntactically.
5) “Jinja2 validation” is not reliable locally (HA templates use HA-specific globals). Only do basic structure checks unless HA can render/validate.
6) It suggests `/ha:deploy` after success; rephrase as:
   - “If you want to apply changes, run `/ha:deploy`.” (No implied side effect.)

**Merged implementation (recommended)**
- Make `/ha:validate` a thin router into a shared **Validator skill** with this precedence order:
  1) **HA-backed**: `hass-cli service call homeassistant.check_config` (or equivalent) and report the raw result.
  2) **Best-effort local lint**: only if required tools exist; never claim “valid,” only “no obvious lint errors.”
- Always output a “what ran vs skipped” table.
- Never print secrets; when flagging “possible secret,” show file + line number + key name only.

### 2.13 `/ha:deploy` has the right UX shape, but violates safety invariants unless re-scoped
**New evidence:** `commands/deploy.md` (uploaded as `ha-deploy.md`).

**What it does today**
- Forces a **pre-deploy validation** step (delegated to a config validator agent).
- Shows `git diff` + asks for confirmation (in the “auto_deploy: false” flow).
- Commits, pushes, reloads automations/scripts/scenes, then “verifies” by checking `automation.<name>`.
- Offers an **auto_deploy** mode that skips diff + confirmation.
- Reads settings from `.claude/home-assistant-assistant.md` (auto_deploy/commit/push/reload + commit_prefix).

**What’s good (keep)**
- Validation-first posture (good default ordering).
- “Show diff → confirm → commit → push → reload → verify” is the right conceptual pipeline.
- The UX includes a “deploy later” path and a discard path.

**Concrete issues to fix**
1) **Side effects not properly gated:** commit/push/reload are all side-effectful. This command must be `disable-model-invocation: true` and require explicit opt-in for each side-effect phase.
2) **Auto-deploy mode is unsafe:** skipping diff + confirmation violates our invariant (“never deploy unless explicitly requested”). If `auto_deploy` remains, it must still require an explicit “Deploy now” confirmation.
3) **Settings source is wrong/brittle:** referencing `.claude/home-assistant-assistant.md` breaks portability and conflicts with ha-toolkit’s settings approach.
4) **Verification is not resolver-driven:** `automation.<name>` is frequently wrong. Verification should:
   - resolve entity IDs (or search by automation `id` / `alias`) and show evidence.
5) **“Fix automatically” is underspecified:** it promises auto-fixes but does not define tool permissions or a safe patch workflow.
6) **Reload sequencing should be conditional:** only reload the domains actually changed (and only when requested).
7) **Push failure branch is backwards:** if push fails, it offers “continue anyway (reload HA with local changes).” That’s fine as an *option*, but it should be framed as “reload from local files only if HA reads local config,” and it must not imply success.

**Merged implementation (recommended)**
- Make `/ha:deploy` a thin, side-effectful entrypoint that routes to a shared **Deploy skill**:
  1) Run `/ha:validate` (or shared validator) and print evidence.
  2) Show diff.
  3) Ask: commit? push? reload? (each is explicit).
  4) Reload only the changed domains.
  5) Verify via resolver + evidence (list/search by id/alias).
- Unify settings in `.claude/settings.local.json` (or a small `.claude/ha.conventions.json`) and remove `.claude/home-assistant-assistant.md` references.

### 2.14 `/ha:analyze` is valuable, but must not hallucinate metrics; treat as advisory + evidence-backed
**New evidence:** `commands/analyze.md` (uploaded as `analyze.md`).

**What it gets right (keep)**
- The “focus-area” argument pattern is good (`automations`, `energy`, `security`, `presence`, `performance`).
- Strong intent: turn HA data into actionable next steps and tie suggestions back to `/ha:generate`.

**Main risk**
- The example output includes precise counts (“Entities: 147”, “Automation coverage: 80%”, etc.). Unless those were actually computed from a real inventory, this becomes **false authority**.

**Fixes for merge**
1) Make it explicit that the report is **data-derived** and include a “Data sources used” section.
2) Require evidence for each numeric claim:
   - if `hass-cli entity list --output json` ran, cite the count; if it didn’t, don’t print counts.
3) Add output scaling rules:
   - if the suggestion list is long, show top 5–10 + offer to write a report file.
4) Tighten tool behavior:
   - never write files or deploy from `/ha:analyze`.
   - it can *offer* to generate configs, but only via explicit user action.
5) Capability-aware suggestions:
   - don’t suggest a motion automation unless a motion sensor and target light are confirmed present and compatible.

**Merge placement**
- Keep `/ha:analyze` as a thin, read-only command that routes to a shared “Analyzer” skill.
- The Analyzer skill should reuse the Resolver + Convention artifact so its suggestions speak the repo’s language.

### 2.15 `/ha:audit-naming` should be an analyzer-only entrypoint (no edits)
**New evidence:** `commands/audit-naming.md` (uploaded as `audit-naming.md`).

**What it should do (merged)**
- Route to the `naming-analyzer` agent.
- Report findings + risks + a suggested rename plan.
- Offer a next step:
  - `/ha:plan-naming` (generates a plan file)
  - `/ha:apply-naming` (side-effectful; requires explicit confirmation and stays `disable-model-invocation: true`)

**Hard rules**
- No file writes.
- No deploy/reload.
- Any “counts” or “coverage” claims must cite the exact command/data source used.

### 2.16 `/ha:onboard` overlaps with `/ha:setup` + `/ha-connect`; merge into one secret-safe, portable connection wizard
**New evidence:** `commands/onboard.md` (uploaded as `onboard.md`).

**What it gets right (keep)**
- Wizard-shaped flow: environment check → HA connection → repo setup → verify.

**Issues to fix (merge)**
1) **Secret handling:** don’t default to storing tokens in shell rc files; prefer project-local settings and never echo token/prefix.
2) **Portability:** avoid brittle CLI flags like `--limit`; use safe, cross-platform smoke tests.
3) **Truthiness:** don’t print entity counts or “all good” summaries unless they were actually computed from real commands.
4) **Settings convergence:** stop writing `.claude/ha-toolkit.local.md` and converge on `.claude/settings.local.json` (plus an optional conventions artifact).
5) **Command hardening:** make onboarding a manual-only entrypoint (`disable-model-invocation: true`) and restrict Write/Edit to only the settings artifact.

**Merged behavior (recommended)**
- `/ha:onboard` becomes a thin wrapper that calls the same shared “connection check” procedure used by `/ha:setup` and `/ha-connect`.
- It writes/updates the single settings artifact, runs one read-only connectivity check, then prints a “what ran vs skipped” table.

### 2.17 `/ha:new-device` should become a capability-checked, naming-aware planner (not an auto-writer)
**New evidence:** `commands/new-device.md` (uploaded as `new-device.md`).

**What it gets right (keep)**
- Good mental model: device identification → naming → automations → dashboard → relationships → testing.
- Correctly routes complex reasoning to the `device-advisor` agent (keeps the command thin).

**Issues to fix (merge)**
1) **Side-effect creep:** it implies writing YAML + “run /ha:deploy” in the default completion output. In the merged plugin, `/ha:new-device` should default to *plan + generate snippets*, and only write/apply via an explicit apply/deploy step.
2) **Capability blind spot:** suggestions for dashboards/automations must be gated on capability snapshots (same contract as scenes/scripts).
3) **Discovery truthiness:** “recently added entities” can’t be reliably inferred without history; treat as best-effort and ask the user for the current entity_id(s) if not determinable.
4) **Naming contract integration:** it should always consult the conventions artifact + naming skill before proposing entity_ids, aliases, groups.
5) **Tool scope:** command frontmatter currently allows Write/Edit; tighten it:
   - default to Read/Grep/Glob/Bash (hass-cli read-only) + AskUserQuestion;
   - route writing to `/ha:apply` or `/ha:deploy` (both `disable-model-invocation: true`).

**Merged behavior (recommended)**
- `/ha:new-device <freeform>` → calls `device-advisor` which returns:
  - proposed naming (entity_id + friendly_name + area),
  - 3–5 automation ideas (capability-checked),
  - 1–2 dashboard card YAML options,
  - optional group/scene suggestions.
- Then it asks: “Do you want me to apply any of these changes?” and routes to the appropriate apply command.

### 2.18 ha-toolkit `ha-config` skill — merge notes + required fixes
**New evidence:** `skills/ha-config/SKILL.md` (uploaded as `SKILL-haconfig.md`).

**What’s good (keep)**
- Clear guidance on splitting config (`!include*` patterns), `packages/`, and where secrets belong.
- Encourages a modular structure that supports our “generate vs apply” split.

**Fixes needed before merge**
1) **Skill frontmatter `name` is non-compliant** (contains spaces/caps). Rename to something like `ha-configuration` (and keep `description` unchanged).
2) **HA YAML tags must be treated as valid**: local lint/format checks must not flag `!include`, `!include_dir_*`, `!secret` as YAML errors.
3) Add a short “file-target rules” subsection that generators must follow:
   - `configuration.yaml` can have `automation: !include …`
   - `automations.yaml` itself is a **list** of automations (no `automation:` root)
   - packages can contain domain keys as lists
4) Update this skill’s automation examples to the current HA YAML schema (`triggers`/`conditions`/`actions` lists with `- trigger:` and `- action:` entries), so it doesn’t teach generators a deprecated format.

**Integration points**
- Link to this skill from generator skills (automations/scenes/scripts) when the user asks “where should this live?”
- Use this skill’s patterns to drive the merged “Editor” module’s file targeting logic.

## 2.19 ha-toolkit `ha-devices` skill — merge notes + required fixes
**New evidence:** `skills/ha-devices/SKILL.md` (uploaded as `SKILL-devices.md`).

**What’s good (keep)**
- Strong conceptual “device vs entity vs integration” primer.
- Good coverage of common protocols (Zigbee/Z-Wave/Wi‑Fi/BLE) and where troubleshooting usually lives.
- Sensible mental model for device onboarding: discover → name → organize → automate → dashboard.

**Fixes needed before merge**
1) **Skill frontmatter `name` is non-compliant** (must be lowercase letters/numbers/hyphens). Rename to something like `managing-ha-devices` and keep the human-readable title in the H1.
2) **Progressive disclosure:** this file is a concept + FAQ compendium. Keep the *contract* in SKILL.md (what to do, in what order), and move the long primers/tables into `references/` so invoking this skill doesn’t flood context.
3) **Capability snapshot contract (missing):** any guidance that proposes scenes/scripts/automations or service calls must first pull a capability snapshot (supported features/attributes) for the entity IDs involved.
   - This should explicitly route through `ha-entity-resolver` and then `hass-cli state get <entity_id>` (or UI equivalents).
   - Enforce: only suggest supported attributes/modes unless user explicitly overrides.
4) **Entity hide/disable guidance should prefer UI + registry:** avoid teaching legacy YAML-only fields like `hidden: true` as a default. If YAML customization is needed, scope it under `homeassistant: customize:` and label it “advanced / last resort.”
5) **Tool scoping:** this skill should be *read-only* by default (Read/Grep/Glob, optional Bash for hass-cli). Any writes (customize, rename, dashboard edits) should route to apply/deploy entrypoints that are side-effect gated.

**Integration points (merge)**
- `/ha:new-device` should use this skill for vocabulary + structure, but route implementation to:
  - Resolver (entity + capability snapshot)
  - Naming contract
  - Generator (scenes/scripts/automations)
  - Apply/Deploy (explicit confirmation)

## 2.20 ha-toolkit `ha-jinja` skill — merge notes + required fixes
**New evidence:** `skills/ha-jinja/SKILL.md` (uploaded as `SKILLjijna.md`).

**What’s good (keep)**
- Practical template patterns: `states()`, `state_attr()`, `is_state()`, defaults, type conversions.
- Includes debugging posture (Developer Tools → Template) and common error classes.

**Fixes needed before merge**
1) **Skill frontmatter `name` is non-compliant** (spaces/caps). Rename to a lowercase hyphenated identifier, e.g. `ha-jinja-templating`.
2) **Clarify where Jinja actually runs:** the skill currently implies templating works in Lovelace broadly; keep it accurate by stating that core Lovelace YAML does *not* generally evaluate Jinja, and templating there requires specific cards/integrations.
3) **Portability:** avoid examples that rely on globals/objects not present in all contexts (or label them clearly). Always show safe defaults (`| float(0)`, `| default('unknown')`).
4) **Progressive disclosure:** keep the “contract + common patterns” in SKILL.md and move the long example sections into `references/` so the skill stays lightweight.

**Integration points (merge)**
- Use this as the templating reference for automations/scripts generation *only*.
- Any “template validation” in `/ha:validate` must be HA-backed or labeled best-effort.

## 2.21 ha-toolkit `ha-lovelace` skill — merge notes + required fixes
**New evidence:** `skills/ha-lovelace/SKILL.md` (uploaded as `SKILLlovelace.md`).

**What’s good (keep)**
- Good coverage of baseline card vocabulary (entities/button/grid/stacks/conditional/history-graph).
- Useful reminder of view structure (dashboards → views → cards) and layout modes.

**Fixes needed before merge**
1) **Skill frontmatter `name` is non-compliant** (spaces/caps). Rename to a lowercase hyphenated identifier, e.g. `ha-lovelace-dashboards`.
2) **Avoid teaching unsupported templating:** the markdown card example uses Jinja-like expressions; that should be labeled “requires custom card / add-on” (or replaced with non-templated examples) to avoid misleading users.
3) **UI mode vs YAML mode posture:** default to UI-first editing guidance, with YAML mode framed as “advanced / repo-managed.”
4) **Progressive disclosure:** move the full catalog of card examples into `references/` and keep a short decision guide in SKILL.md (what card to use when, and the minimal schema).
5) **Naming + capability integration:** any suggested dashboards should consume the conventions artifact and avoid assuming entity ids.

**Integration points (merge)**
- `/ha:new-device` can offer 1–2 card YAML options, but should default to “snippet only,” and route any writes to an apply step.

## 2.22 ha-toolkit `ha-naming` skill — merge notes + required fixes
**New evidence:** `skills/ha-naming/SKILL.md` (uploaded as `SKILLnaming.md`).

**What’s good (keep)**
- Clear breakdown of **entity_id vs friendly_name**, plus concrete patterns and anti-patterns.
- Migration strategy includes dependency updates and staged execution (audit → plan → apply → test).
- Domain-by-domain examples are pragmatic (lights/sensors/binary_sensors/switches/etc.).

**Fixes needed before merge**
1) **Frontmatter compliance:** `name:` currently has spaces/caps. Must be lowercase/hyphenated.
   - Recommendation: `ha-naming-conventions`.
2) **Progressive disclosure:** this SKILL file is long and table-heavy.
   - Keep SKILL.md focused on the *contract* + decision rules.
   - Move large tables (area abbreviations, device type abbreviations, domain catalogs) into `references/`.
   - Add TOCs to references that exceed ~100 lines.
3) **Abbreviation policy needs a single default:** it currently allows `living_room, lr` etc. This creates drift.
   - Merged contract should pick one: **full names by default**, allow abbreviations only behind an explicit “short IDs” toggle in conventions artifact.
4) **Enforcement hooks:** “Automate enforcement” is mentioned, but there’s no concrete mechanism.
   - In merge: wire naming rules into:
     - Generator (always proposes ids + friendly names + rationale)
     - Naming-analyzer (flags violations)
     - Apply-naming (AST-safe refactors)
5) **Terminology alignment:** standardize “entity_id” vs “friendly name” vs “alias” consistently across skills/commands.

**Merged output contract (what generators must emit)**
- `entity_id` suggestion (domain + object_id)
- `friendly_name` suggestion (UI)
- `alias` template for automations/scripts/scenes
- Rationale + any detected repo conventions used

**Integration points (merge)**
- `/ha:plan-naming` uses this contract + convention artifact.
- `/ha:new-device` should invoke naming contract before it suggests automations/dashboards.

## 3) Merge architecture (recommended)

### 3.0 Component choice: unify commands + skills, separate *entrypoints* from *logic*
Claude Code plugins can ship skills via both `commands/` (slash-entrypoints) and `skills/` (discoverable skills). In practice they’re converging on the same mental model, but we can still use a clean separation:

- **Entry points (slash commands):** short, memorable, user-invoked prompts (`/ha-connect`, `/ha-generate`, `/ha-validate`, `/ha-deploy`, `/ha-rollback`, `/ha-apply-naming`).
  - Keep them *thin*: gather missing info + route to the right skill/agent.
  - Any side-effectful entrypoint must be `disable-model-invocation: true`.

- **Skills (core logic):** reusable building blocks Claude can invoke when relevant.
  - “Knowledge/policy” skills can be `user-invocable: false` to avoid clutter.
  - Keep bodies short; move deep examples/tables into `references/` (progressive disclosure).

**Operational rule:**
- Do not duplicate logic in both places. Slash commands route; skills implement.

### 3.1 Skill authoring constraints we will enforce
Pulled directly from Anthropic’s Skill best practices and Claude Code docs:
- Keep each `SKILL.md` body **<500 lines**; push deep details into `references/` (progressive disclosure). (platform.claude.com)
- Avoid **nested references** (references should link from `SKILL.md`, not from each other). (platform.claude.com)
- Make `description` do real work: include trigger terms + “when to use” so Claude selects the right skill. (platform.claude.com)
- Use `allowed-tools` to *minimize blast radius* (read-only skills should not be able to write). (docs.claude.com)
- Prefer **utility scripts** for deterministic operations (YAML AST edits, validators) rather than rewriting code in-prompt. (platform.claude.com)

### 3.2 Verification-first contract (Claude Code best practices)
We’ll make “verify its work” the default behavior across both plugins:
- Every generator/editing skill must end with an **evidence-based validation step** (what ran, what was skipped, and why).
- If validation can’t run (missing `hass`, no access), the skill must downgrade claims to “unverified” and ask for the minimal next input.

### 3.2.1 Packaging + caching constraints (must-haves)
1) **Finalize plugin layout explicitly**
   - Converge on a single installable root layout:
     - `.claude-plugin/plugin.json`
     - `commands/` (only thin entrypoints)
     - `skills/` (core logic)
     - `agents/`
     - `hooks/`
   - Ensure skills follow **`skills/<skill-name>/SKILL.md`** and references are **one level deep**.
   - Decide whether to migrate most slash entrypoints into `skills/` (commands are trending legacy). If kept, commands remain wrappers.

2) **Plugin caching + path constraints**
   - Any scripts/hooks/editor helpers must live inside the plugin root.
   - Any references must use `${CLAUDE_PLUGIN_ROOT}` for portability.

### 3.2.2 Repo-wide compliance sweeps (add to merge PR plan)
1) **Frontmatter compliance audit (all skills + commands)**
   - Enforce: `name` is lowercase/nums/hyphens, no spaces, no reserved words.
   - Enforce: short, trigger-term-rich `description`.
   - Add a single checklist item to every PR: “frontmatter lint passes.”

2) **Reference hygiene + TOCs**
   - Add TOCs for reference files > ~100 lines.
   - Ensure references do not link to other references (only linked from SKILL.md).

3) **Content hygiene sweep**
   - Normalize terminology: “generate / apply / validate / deploy / reload.”
   - Flag time-sensitive guidance and move to “old patterns” sections.
   - Normalize all paths to forward slashes in docs/examples.

4) **Tool availability + dependency checks**
   - Never assume `hass-cli` exists.
   - Add a single “dependency check” procedure used everywhere:
     - detect `hass-cli` presence + version
     - detect HA connection
     - detect whether HA-backed validation is available
   - Skills must declare dependencies explicitly (and degrade gracefully).

5) **Secrets hardening (settings-level)**
   - Recommend a **project-local** settings artifact (e.g., `.claude/settings.local.json`) that onboarding can create/update.
   - Do **not** ship this file as part of the plugin.
   - Add deny rules for secret-y paths (`.env`, `secrets/**`, etc.) where applicable.
   - Never print token/prefix; only “present/not present”.
   - Ensure `.claude/` (or at least the local settings file) is ignored by git.

6) **Choice overload guard**
   - Default behavior: **one recommended path** + **one escape hatch**.
   - Avoid dumping 5+ options unless the user explicitly asks.

7) **Checklists + feedback loops in complex workflows**
   - Every multi-step workflow must include a checklist and a loop:
     - validate → fix → re-validate
   - No “pass” claims without evidence.

8) **Evaluation-driven development (formalize)**
   - Add explicit eval artifacts:
     - at least 3 eval suites (we already have transcript-derived scenarios)
     - run across target models
     - store pass/fail + deltas

9) **Templates/examples where structure matters**
   - Add explicit templates for:
     - generator outputs (automations/scenes/scripts)
     - validator reports
     - deploy summaries (“what ran vs skipped”)

10) **Context management for heavy tasks**
   - Consider `context: fork` for deep troubleshooting / large scans to keep main context clean.

11) **Slash command UX**
   - Add `argument-hint` to user-invoked entrypoints for better discoverability.

### 3.3 Modules and contracts
1) **Resolver** (from home-assistant-assistant)
   - Enumerate entities/services.
   - Capability allowlists.
   - Missing helper detection + safe creation plan.

2) **Planner** (from ha-toolkit)
   - Semantics-correct pattern library.
   - Equivalence rules (timers vs inactivity).

3) **Renderer** (hybrid)
   - Output matches repo conventions.
   - Domain-aware action splitting.

4) **Editor** (new)
   - YAML AST updates by `id`.
   - Stable formatting.

5) **Validator + Reporter** (from home-assistant-assistant)
   - Evidence-based validation.
   - Entity table + diff summary.
   - Deploy only on explicit request.

---

## 4) Regression test plan (derived from transcripts)
For each scenario, define a pass/fail checklist:
- plugin-onboarding: no secrets printed; produces durable config artifact; verifies hass-cli.
- scene-creation: capability-checked; style-consistent serialization.
- script-creation: explicit HVAC mode compatibility; validated output.
- simple-automation: inactivity semantics preserved; no timer substitution without gating.
- unconfigured-detection: complete inventory; no truncation; optional metadata preserved.
- ambiguous-entity: cross-domain handling + from→to gating; does not deploy unless asked.
- complex-automation: notify service verified; missing helper created safely; validated.

---

## Next files to request (optional)
1) **planning/** (either repo) — only if it materially changes behavior (not just notes)
2) **docs/** (either repo) — only if it contains hard requirements the plugin should follow

**Note:** Ignore `.claude/settings.local.json` from `home-assistant-assistant` for merge purposes if it was only created for a Claude Code session. The merged plugin should treat settings as **project-local, user-managed state** (created on demand, gitignored), not a shipped plugin artifact.

Now that all core surfaces are ingested, we can shift fully to the concrete merge PR plan (file-by-file patches + new shared modules + regression harness).

