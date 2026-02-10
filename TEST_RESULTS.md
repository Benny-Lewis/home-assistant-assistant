# Plugin Test Results

**Date:** 2026-02-05 – ongoing
**Starting commit:** `24a49e5`
**Latest fix commits:** `d0c4268` (bug fixes), `fbc55dc` (UX improvements)
**Bugs:** 13 total — 12 fixed (11 verified, 1 unverified #10), 1 reclassified as not-a-bug (#12)
**UX items:** 6 total — 6 fixed (4 verified: #1 #3 #4 #6, 2 unverified: #2 #5)

## Remaining Test Plan

| Group | Tests | Priority | Notes |
|-------|-------|----------|-------|
| **A: Fix Verification** | A1–A4 done (**all pass**), A5 (analyze) remaining | 1 | Group A complete except A5 |
| **B: Safety Invariants** | B1–B3 (scene capabilities, ambiguous entities, secrets check) | 2 | Need specific entity setup |
| **C: Domain Skills** | C1–C5 (ha-config, ha-lovelace, ha-jinja, ha-naming, ha-devices) | 3 | Quick knowledge-delivery prompts |
| **D: Integration** | D1–D3 (config-debugger agent, naming pipeline, new device workflow) | 4 | Complex multi-step, if time allows |
| **N/A** | Test 5.3 (YAML Validation Hook) | — | PostToolUse hook removed (Bug #11 fix); validation now via `/ha-deploy` |
| **N/A** | Test 2 (fresh start, nothing installed) | — | Requires removing HASS_TOKEN from shell profile — risky in primary env |

---

## Group A: Fix Verification (sessions `dd8fa109`, `7e53ec54`, `5c5db733`)

### A1: Plugin Loading — Skill Count & Slash Commands

**Result: Pass** (with doc correction needed)

- 14 user-invocable skills registered (not 13 — ha-validate is both user-invocable and agent-preloadable)
- Slash commands use hyphens (`/ha-deploy`) not colons (`/ha:deploy`)
- Doc corrections applied: CLAUDE.md skill count and slash command format updated

### A2: PostToolUse Hook Removal + PreToolUse Command Hook

**Result: Pass** — Bug #11 confirmed fixed

- No PostToolUse error after file edits
- PreToolUse command hook with JSON `additionalContext` works correctly
- Session `dd8fa109` line 79: prompt hook returned `ok: false` with reason — this is the hook *blocking* the edit (correct behavior), not an error
- **Lesson:** Prompt hooks DO work on Windows. The "error" was the hook correctly evaluating and blocking.

### A3: Automation Generation Flow

**Result: Pass** — UX #3 + #4 confirmed fixed

- Session `7e53ec54`: generated automation, saved to file, mentioned `/ha-deploy`
- No `scp`/`rsync` suggestions
- Post-generation flow should use AskUserQuestion for clearer UX (see UX #6)

### A4: Deploy Skill Invocation

**Result (original): Fail** — Bug #13 found

- Session `5c5db733`: `Skill("ha-deploy")` returned `tool_use_error: cannot be used with Skill tool due to disable-model-invocation`
- Model then improvised deploy steps — skipping validation, pull method check, and evidence tables
- Entity resolver subagent improvised `--output json` flag (Bug #12)
- **Fix applied:** Removed `disable-model-invocation` from ha-deploy, added in-skill confirmation gates

### A4 Re-test: End-to-End Deploy Flow (post-fix)

**Result: Pass** — Bug #13 confirmed fixed

**Setup:** `~/dev/ha`, fresh session, prompt: "Create an automation to turn on the rec room light when motion is detected" → then "deploy"

**Automation generation (ha-automations):**
- [x] ha-automations skill loaded
- [x] Entity resolver found light.rec_room + binary_sensor.rec_room_motion
- [x] Correct YAML: state trigger, no timer substitution (Safety Invariant #2)
- [x] Saved to automations.yaml
- [ ] AskUserQuestion after save — **Fail**: model used plain text instead of AskUserQuestion tool (UX #6 not fixed)
- [x] No scp/rsync suggestion (UX #4 re-verified)

**Deploy (ha-deploy):**
- [x] `Skill("ha-deploy")` loaded successfully — **Bug #13 FIXED**
- [x] Step 1: `git status --short` — identified modified automations.yaml
- [x] Step 2: Pre-deploy validation via ha-config-validator — 4-tier evidence table, 31/31 entities, 10/10 services (Safety Invariant #6)
- [x] Step 3: AskUserQuestion fired with "Deploy" / "Only rec room" / "Abort" — confirmation gate working
- [ ] Step 2.5: Pull method check — **not observed** (skipped, may fire after commit)
- [x] Aborted cleanly on user request

**Entity resolver (Bug #12 — reclassified):**
- [x] Used `-o json` — **this actually works and returns full attributes**
- [x] Checked `hass-cli --help` first, discovered `-o json` is valid
- [ ] Tried `raw_api` subcommand (doesn't exist) — minor, self-corrected with fallback

**Root cause analysis (JSONL investigation):**
- **Bug #12 reclassified:** `-o json` is a valid hass-cli flag. Our prohibition was factually wrong. The agent was correct to use it — tabular `state get` output omits attributes needed for capability snapshots. Fix: removed prohibition, updated docs to recommend `-o json`.
- **UX #6 root cause:** `AskUserQuestion` was NOT in `allowed-tools` frontmatter (`Read, Grep, Glob, Bash(hass-cli:*)`). Skill sandbox blocked the tool call. Model silently fell back to text. Fix: added `AskUserQuestion` and `Edit` to `allowed-tools` in ha-automations, ha-scripts, ha-scenes.
- Step 2.5 (pull method) not triggered — may only fire at push time

### A4 Re-test #2: Root Cause Fixes Verified

**Result: Pass** — Bug #12 + UX #6 root causes confirmed fixed

**Setup:** `~/dev/ha`, fresh session, same prompt

**Entity resolver (Bug #12 — verified):**
- [x] Used `hass-cli -o json state get` directly on first attempt — no trial-and-error
- [x] No `raw_api`, no `--output json`, no `--help` discovery loop
- [x] Got full attributes (`supported_features: 32`, `supported_color_modes: ["brightness"]`) immediately
- [x] 3 tool uses, 24s (vs 9 tool uses / 54s in re-test #1)

**Post-save (UX #6 — verified):**
- [x] AskUserQuestion interactive prompt appeared with "Deploy now" / "Keep editing"
- [x] NOT plain text — selectable options rendered correctly
- [x] 6 tools allowed (was 4 before — confirms `Edit` + `AskUserQuestion` added to sandbox)

**Deploy (ha-deploy):**
- [x] ha-deploy skill loaded (Bug #13 still fixed)
- [x] `git diff` showed +13 lines in automations.yaml
- [x] Pre-deploy validation via ha-config-validator — 3 methods (API, SSH, service call) all passed
- [x] Evidence table present (Safety Invariant #6)
- [x] AskUserQuestion confirmation gate: "Deploy" / "Edit commit message" / "Abort"
- [x] Aborted cleanly

**Group A complete.** All issues resolved.

---

---

## Test 1: Wrong directory + hass-cli installed, no config

**Setup:** `C:\Users\Ben` (no `configuration.yaml`), hass-cli installed, HASS_TOKEN unset in terminal, HASS_SERVER unset in terminal

### Branch 1: User answers "no" (config not cloned)

**Resume detection output:**
```
NO_CONFIG
hass-cli, version 0.9.6
TOKEN_LEN=
SERVER=
```

**Agent behavior:**
- [x] Identified wrong-directory scenario
- [x] Did NOT run `uname -s` / Step 1 checks
- [x] Asked "Do you have your HA config cloned somewhere else?"
- [x] When user said "no" → correctly went to Step 2 (Git Setup on HA)
- [ ] `TOKEN_LEN` showed correct value in single script — **FAIL**: showed empty, not `0`
- [ ] `SERVER` showed correct value in single script — **FAIL**: showed empty, not `UNSET`
- [ ] No follow-up bash checks needed — **FAIL**: agent ran second `echo "TOKEN_LEN=${#HASS_TOKEN}"` which returned `TOKEN_LEN=183`

**Bugs found:**
1. **`${#HASS_TOKEN}` expansion fails when script is semicolon-joined.** Agent reformatted multi-line script as single-line semicolons. The `#` in `${#HASS_TOKEN}` was likely misinterpreted in MINGW. Branch 2 (multi-line) worked fine.
2. **`NO_GIT_REMOTE` never printed.** `head -1` returns exit 0 on empty input, so `|| echo "NO_GIT_REMOTE"` never fires.
3. **Token was actually set (183 chars) despite `unset` in terminal.** Claude Code's bash tool sources the shell profile, re-exporting the vars. The `unset` only affected the terminal that launched Claude Code, not child bash processes. This means testing "no token" requires removing the export from `.bashrc`/`.bash_profile` — not just unsetting in the terminal.

### Branch 2: User answers "yes" (config is cloned elsewhere)

**Resume detection output:**
```
NO_CONFIG
hass-cli, version 0.9.6
TOKEN_LEN=183
SERVER=http://homeassistant.local:8123
```

**Agent behavior:**
- [x] Identified wrong-directory scenario
- [x] Did NOT run `uname -s` / Step 1 checks
- [x] Asked "Do you have your HA config cloned somewhere else?"
- [x] When user said "yes" → asked for the path
- [x] Verified `configuration.yaml` exists at given path
- [x] Told user to restart Claude Code from that directory
- [x] `TOKEN_LEN` showed correct value (`183`) — script was multi-line this time
- [x] `SERVER` showed correct value (`http://homeassistant.local:8123`)

**Bugs found:**
- `NO_GIT_REMOTE` still not printed (same `head -1` bug as Branch 1)

### Run 3: From `~/dev`, hass-cli hidden, token+server set via profile

**Setup:** `C:\Users\Ben\dev` (no `configuration.yaml`), hass-cli not on PATH (hidden or not installed in this env), HASS_TOKEN=183 chars and HASS_SERVER set (via shell profile)

**Resume detection output:**
```
NO_CONFIG
NO_HASS_CLI
TOKEN_LEN=183
SERVER=http://homeassistant.local:8123
```

**Agent behavior:**
- [x] Identified wrong-directory scenario (NO_CONFIG + TOKEN_LEN>0)
- [x] Did NOT run `uname -s` / Step 1 checks
- [x] Asked "Do you have your HA config cloned somewhere else?"
- [x] `TOKEN_LEN` showed correct value (`183`) — script was multi-line
- [x] `SERVER` showed correct value
- [x] `NO_HASS_CLI` printed correctly

**Bugs found:**
- `NO_GIT_REMOTE` still not printed (same `head -1` bug)

**Notes:**
- Confirms multi-line script → `TOKEN_LEN` works. Bug #1 is specifically about semicolon-joining.
- `NO_HASS_CLI` printed correctly, confirming the `|| echo` pattern works when there's no pipe to `head`.
- hass-cli was not found — user may still have it renamed from Test 2 prep.

---

## Test 2: Fresh start (nothing installed)

**Setup:** Non-HA directory, hass-cli hidden, HASS_TOKEN removed from profile, HASS_SERVER removed from profile

**Resume detection output:**
```
(not yet tested)
```

**Agent behavior:**
- [ ] Started at Step 1
- [ ] Ran `uname -s`, `git --version`, `python3 --version`
- [ ] `TOKEN_LEN=0`
- [ ] `SERVER=UNSET`
- [ ] `NO_HASS_CLI` printed

**Bugs found:**
_(not yet tested)_

---

## Test 3: Config directory + token set

**Setup:** HA config directory (has `configuration.yaml`), hass-cli installed, HASS_TOKEN set (183 chars), HASS_SERVER set

### Run 1: hass-cli NOT restored (incomplete setup)

**Actual setup:** `~/dev/ha` (has `configuration.yaml`), hass-cli still hidden/missing, HASS_TOKEN and HASS_SERVER set via profile

**Resume detection output:**
```
HAS_CONFIG
origin     git@github.com:Benny-Lewis/home-assistant.git (fetch)
NO_HASS_CLI
TOKEN_LEN=
SERVER=
```

**Agent behavior:**
- [ ] Skipped to Step 7 — **N/A**: went to Step 5 (correct given NO_HASS_CLI, but token/server were also not detected)
- [ ] `TOKEN_LEN` showed >0 — **FAIL**: showed empty (bug #1, semicolon-joined again)
- [ ] `SERVER` showed value — **FAIL**: showed empty (bug #1)
- [x] Correctly identified HAS_CONFIG + git remote + NO_HASS_CLI → Step 5
- [x] Gave pip install instructions for hass-cli

**Bugs found:**
- Bug #1 again: agent semicolon-joined the script, `TOKEN_LEN=` and `SERVER=` both empty (2nd occurrence)
- Not a clean Test 3 — hass-cli needs to be restored first

**Notes:**
- Even though TOKEN_LEN/SERVER were empty, the agent happened to land on the right step (5) because hass-cli was missing — but for the wrong reason. With correct token detection it would have gone to Step 5 anyway (HAS_CONFIG + git + NO_HASS_CLI).

### Run 2: Full setup (after bug fixes — `printf|wc -c`, git remote variable capture)

**Setup:** `~/dev/ha` (has `configuration.yaml`), hass-cli restored, HASS_TOKEN set (183 chars), HASS_SERVER set

**Resume detection output:**
```
HAS_CONFIG
origin     git@github.com:Benny-Lewis/home-assistant.git (fetch)
hass-cli, version 0.9.6
TOKEN_LEN=183
SERVER=http://homeassistant.local:8123
```

**Agent behavior:**
- [x] All 5 signals detected correctly in a single script call
- [x] `TOKEN_LEN=183` — `printf|wc -c` fix works
- [x] `SERVER=http://homeassistant.local:8123` — correctly reported
- [x] Git remote URL printed (variable capture fix works)
- [x] Agent skipped straight to verifying connection (no unnecessary steps)
- [x] `hass-cli state list` succeeded — connection confirmed
- [x] Agent proceeded to save settings (`.claude/settings.local.json`)
- [x] No second follow-up bash checks needed
- [x] No Step 1 / Step 5 / Step 6 content shown — correctly identified all-setup-done

**Bugs found:**
- None. All three fixes (Bug #1: `printf|wc -c`, Bug #2: git remote variable capture, UX #1: Step 5 rewrite) validated.

**Notes:**
- Agent skipped directly to connection verification and settings creation rather than going to Step 7 (Git Pull add-on) — this is reasonable since the connection test proved everything works. The agent optimized the flow.

---

## Create Automation (Test Plan 3.2 + Safety Invariant 7.3)

**Setup:** `~/dev/ha`, fresh session. Prompt: "Create an automation to turn off the rec room light 10 minutes after no motion"

**Agent behavior:**
- [x] Loaded ha-automations skill
- [x] Resolved entities via ha-entity-resolver subagent (binary_sensor.rec_room_motion, light.rec_room)
- [x] Checked for existing automations on those entities — found unrelated guest room fan automation, correctly identified no conflict
- [x] Explicitly classified intent: "inactivity pattern → use `for:` on the trigger, not timers or delays" — **Safety Invariant #2 satisfied**
- [x] Generated YAML with `platform: state` + `to: "off"` + `for: "00:10:00"` — correct inactivity pattern
- [x] Added condition: only fire if light is actually on
- [x] Used `target: entity_id:` (modern format, not deprecated `entity_id` at action level)
- [x] Explained how `for:` auto-resets on motion — demonstrates understanding of the semantic
- [x] Did NOT use `timer.start` / `timer.finished` — **Safety Invariant #2 confirmed**
- [x] Did NOT use bare `delay:` — **Safety Invariant #2 confirmed**
- [x] Offered to append to automations.yaml OR copy — respects **Safety Invariant #5** (no auto-deploy)
- [x] Did NOT write the file without asking — **Safety Invariant #5 satisfied**

**Bugs found:** None.

**Notes:**
- Used `platform:` instead of `trigger:` in the trigger block (HA 2024+ style uses `trigger:` but `platform:` still works)
- Used `service:` instead of `action:` in the action block (HA 2024+ style uses `action:` but `service:` still works)
- These are minor style preferences, not bugs — both syntaxes are valid
- Entity resolution took 31s (5 tool uses) — acceptable
- Total time: 59s

**Write to file:**
- [x] Appended to automations.yaml (lines 712-728)
- [x] Used HA 2024+ syntax in actual write (`triggers:`, `trigger:`, `actions:`, `action:`) despite preview showing older syntax
- [x] Edit self-corrected after 13 matches on `mode: single` — found unique anchor (Safety Invariant #3 working)
- [ ] PostToolUse:Edit hook errored — **Bug #11** (YAML validation hook failure, needs investigation)
- [ ] Agent suggested `scp` for deployment instead of `/ha-deploy` — **UX Feedback #4**

---

## /ha-apply-naming (Test Plan 2.5)

**Setup:** `~/dev/ha`, fresh session, no `.claude/naming-plan.yaml` exists

**Agent behavior:**
- [x] Searched for naming plan file (`.claude/naming-plan.yaml`) — not found
- [x] Reported "No Naming Plan Found" clearly
- [x] Did NOT make any changes
- [x] Explained how to create a plan first (`/ha-naming`)
- [x] Explained dry-run vs `--execute` distinction
- [x] No false "setup incomplete" from SessionStart hook
- [x] Offered to run naming audit as next step

**Bugs found:** None.

---

## /ha-analyze (Test Plan 2.4)

**Setup:** `~/dev/ha`, fresh session, HASS_TOKEN + HASS_SERVER set

**Agent behavior:**
- [x] Collected data from hass-cli (areas, entities, devices, automations, scenes)
- [x] Read local config files (configuration.yaml, automations.yaml, scripts.yaml, scenes.yaml, helpers, templates)
- [x] Produced structured report with metrics citing their sources — **all metrics cite source**
- [x] Entity breakdown by domain (sensor: 510, number: 208, select: 154, etc.)
- [x] Automation coverage matrix by area (identified gaps: Office, Rec Room)
- [x] 8 prioritized recommendations (HIGH/MEDIUM/QUICK WIN)
- [x] Identified real issues: whole_home_power stuck at 0, 547-day recorder retention, empty descriptions, device_id references
- [x] Actionable next steps with "ask me to build" prompts

**Self-corrections:**
- `--output json` flag doesn't exist in hass-cli 0.9.6 — agent tried 3 times, then switched to plain text parsing
- Several `(timeout 15s)` on hass-cli entity list (1,246 entities is slow to list)

**Bugs/improvements found:**
- **Bug #10:** Agent tried `--output json` flag 3 times before discovering it doesn't exist. Need hass-cli reference doc.
- `hass-cli entity list` is slow with 1,246 entities — many commands timed out at 15s. Consider documenting that `hass-cli state list` may be faster for some queries.
- Took 4m 16s total — acceptable for a comprehensive analysis but could be faster with correct commands upfront.

**Quality assessment:** Excellent. The recommendations are specific, reference actual entities, and correctly identify unused infrastructure (plant watering helpers, presence zones, motion sensors without automations).

---

## UX Feedback

| # | Feedback | Status | Source |
|---|----------|--------|--------|
| 1 | Step 5 should auto-install hass-cli | Fixed (ask permission, then install) | Test 3 Run 1 |
| 2 | ha-apply-naming and ha-naming should scan for existing naming specs/conventions — not just `.claude/naming-plan.yaml`. User may have `naming.md`, `naming/reference/`, etc. anywhere in the project tree. Should glob for `**/naming*` patterns before declaring "no plan found." | **Fixed** (unverified) — added glob scan + multi-location search | /ha-apply-naming |
| 3 | After generating an automation/script/scene, don't offer "append to file" vs "copy it yourself". Just show the YAML, then ask "Ready to deploy?" — the file mechanics should be invisible to the user. | **Fixed** (verified A3) — replaced with save + "Ready to deploy?" | ha-automations |
| 4 | After writing config, agent suggested `scp` for deploy instead of `/ha-deploy`. Should always point to the git-based deploy workflow. | **Fixed** (verified A3) — added "Never suggest manual file transfer" rule | ha-automations |
| 5 | `/ha-deploy` should check whether Git Pull add-on (or equivalent auto-pull) is configured on HA before promising "HA pulls via Git Pull add-on" in the deploy steps. If not configured, offer alternatives (manual pull, scp, or guide to set it up). | **Fixed** (unverified) — added Step 2.5 with pull_method detection + caching | ha-deploy |
| 6 | Post-generation should use AskUserQuestion with selectable options instead of plain text prompts | **Fixed** — updated ha-automations, ha-scripts, ha-scenes to use AskUserQuestion | A3 (`7e53ec54`) |

---

## /ha-validate (Test Plan 2.2)

**Setup:** `~/dev/ha` (valid HA config), hass-cli working, HASS_TOKEN + HASS_SERVER set

**Agent behavior:**
- [x] Ran HA-backed config check (`hass-cli raw post /api/config/core/check_config`) — returned `result: valid`
- [x] Checked for tab characters in YAML files
- [x] Scanned for hardcoded passwords/tokens (found all use `!secret`)
- [x] Verified all 9 included YAML files exist
- [x] Caught missing `themes/` directory referenced in configuration.yaml
- [x] Produced evidence table (what ran vs skipped) — **Safety Invariant #6 satisfied**
- [x] Self-corrected Git Bash path mangling (`MSYS_NO_PATHCONV=1`)

**Safety Invariant #4 VIOLATION — Token leaked:**
Agent ran: `echo "HASS_TOKEN set: ${HASS_TOKEN:+yes}${HASS_TOKEN:-no}"`
The `${HASS_TOKEN:-no}` expansion outputs the full token value when it IS set (the `:-` default only fires when empty). Full JWT was printed in output. The validate skill itself doesn't contain this command — the agent improvised it during its tool availability check. Need to strengthen the safety reminder in ha-validate or add a hook guard.

**Git Bash path mangling:**
`hass-cli raw post /api/config/core/check_config` failed because MINGW converted `/api/...` to a Windows path. Agent self-corrected with `MSYS_NO_PATHCONV=1`. This is a recurring MINGW issue — should document `MSYS_NO_PATHCONV=1` as required prefix for hass-cli commands with API paths.

**Bugs found:**
- Token leak via improvised bash expansion (Safety Invariant #4)
- Git Bash path mangling on hass-cli API paths (MINGW environment issue)

### Re-test after fixes (commit cf0af33)

**Resume detection output:**
```
TOKEN_LEN=183
HASS_SERVER=set
```

**Agent behavior:**
- [x] Token check used `printf|wc -c` → `TOKEN_LEN=183`, no value leaked — **Bug #6 FIXED**
- [x] `MSYS_NO_PATHCONV=1 hass-cli raw post /api/config/core/check_config` succeeded first try — **Bug #7 FIXED**
- [x] Evidence table present with 4 tiers (YAML Syntax, Schema, HA Config Check, Security Scan)
- [x] Security scan found only placeholder API key in secrets.yaml — correctly identified as non-issue
- [x] 15 YAML files in scope
- [x] No token/secret values in any output

**Bugs found:** None — both fixes validated.

---

## /ha-deploy (Test Plan 2.3)

**Setup:** `~/dev/ha`, no uncommitted tracked changes, untracked temp files present, no `.claude/settings.local.json`

**Agent behavior:**
- [x] Ran `git status --short` — correctly identified no modified tracked files
- [x] Listed untracked files (tmp_*, tools/, .claude/, etc.)
- [x] Correctly said "nothing staged or modified to deploy"
- [x] Offered sensible next steps (stage files, clean up tmp files, run onboard)
- [ ] Falsely claimed "HASS_TOKEN and HASS_SERVER aren't configured" — **Bug #9**

**Bug #9: SessionStart hook false negative on token detection.**
`session-check.js` line 53: `warnings.some(w => w.includes('settings file'))` matched the "No settings file found" warning, triggering the `missingEnv` branch. Fixed in commit `3d06a00`. However, the bug persisted in first re-test because the user's terminal still had `unset HASS_TOKEN` from earlier testing — Claude Code inherits the terminal's env (no token), while the Bash tool spawns fresh bash that sources the profile (token present). **Root cause: terminal env vs bash profile mismatch, not the hook logic.** After restarting the terminal, the hook correctly reported "All checks passed."

### Re-test after terminal restart

**Agent behavior:**
- [x] No false "setup incomplete" claim
- [x] Ran `git status --short` + `git diff --stat` + `git diff --staged --stat`
- [x] Correctly identified no modified tracked files
- [x] Categorized untracked files (tmp, recovery, tools, .claude, docs)
- [x] Offered 3 sensible options: commit untracked files, pull from remote, force HA reload

**Bugs found:** None — Bug #9 fix confirmed after terminal restart.

**Notes:**
- The untracked temp files suggest the user's repo needs a `.gitignore` update
- "Nothing to deploy" path works correctly
### Run 2: With real changes (automation added to automations.yaml)

**Setup:** `~/dev/ha`, fresh session, `automations.yaml` modified (+17 lines), HASS_TOKEN + HASS_SERVER set

**Agent behavior:**
- [x] Ran `git status --short` — identified `M automations.yaml` plus untracked files
- [x] Ran `git diff --stat` and `git diff` — showed exactly what changed
- [x] Checked recent commit history (`git log --oneline -5`) for commit message style
- [x] Ran pre-deploy validation via ha-config-validator subagent
  - Tried SSH first (`ha core check`), then fell back to hass-cli API
  - Used `MSYS_NO_PATHCONV=1` on API call — Bug #7 fix working
  - Produced evidence table — **Safety Invariant #6 satisfied**
  - Correctly noted validation ran against live instance, not local changes
- [x] Showed deploy review: file, change summary, deployment steps
- [x] Listed steps: commit → push → HA pulls → reload
- [x] Only included tracked changes (untracked files excluded)
- [x] Asked for explicit confirmation with 3 options (deploy/edit message/abort) — **Safety Invariant #5 satisfied**
- [x] No false "setup incomplete" from SessionStart hook — Bug #9 fix confirmed

**Bugs found:** None.

**Actual deployment:**
- [x] `git add automations.yaml` + `git commit` — clean commit with good message
- [x] `git push origin main` — succeeded
- [x] `hass-cli service call automation.reload` — called, but no effect (HA hadn't pulled yet)
- [x] Agent detected automation wasn't live → tried `ssh root@homeassistant.local "cd /config && git pull"` — succeeded (fast-forward)
- [x] Reloaded automations again → `automation.rec_room_light_off_after_no_motion` appeared, state: on
- [x] Produced deployment evidence table (commit, push, pull, reload, entity exists)
- [x] Total deploy time: 2m 18s

**Bugs found:**
- Agent assumed Git Pull add-on would auto-pull, then had to SSH manually when it didn't — **UX Feedback #5** confirmed (should check/ask about auto-pull setup before promising it)
- First grep for the automation missed because the entity_id used `after` not just `off` — agent self-corrected with broader search

**Notes:**
- The SSH fallback worked well but users without SSH access to HA would be stuck
- Commit message followed repo style and included Co-Authored-By

---

## Plugin Loading (Test Plan 1.1-1.2)

**Skill registration:** `/ha` autocomplete showed 9 of 14 expected user-invocable skills.

**Missing skills — two root causes found:**
1. **Non-standard filenames:** ha-devices (`SKILL-devices.md`), ha-naming (`SKILL-naming.md`), ha-config (`SKILL-haconfig.md`), ha-jinja (`SKILL-jinja.md`), ha-lovelace (`SKILL-lovelace.md`) — Claude Code expects `SKILL.md`
2. **Missing `user-invocable: true`:** ha-config, ha-jinja, ha-lovelace, ha-automations, ha-scenes, ha-scripts, ha-troubleshooting had no `user-invocable` field (Claude Code defaulted to true for some, but not all)

**Fix applied:** Renamed all to `SKILL.md`, added `user-invocable: true` to all 14 skills (except ha-resolver which is `false`).

**Needs re-test:** Reload plugin and verify all 14 skills appear in `/ha` autocomplete.

---

## Summary of bugs

| # | Bug | Severity | Seen in | Status |
|---|-----|----------|---------|--------|
| 1 | `${#HASS_TOKEN}` fails when script is semicolon-joined (MINGW `#` parsing) | High | Test 1 Branch 1, Test 3 Run 1 | **Fixed** — replaced with `printf '%s' \| wc -c` |
| 2 | `NO_GIT_REMOTE` never prints (`head -1` returns 0 on empty input) | Medium | Test 1 All runs | **Fixed** — variable capture + `${REMOTE:-NO_GIT_REMOTE}` |
| 3 | `unset` in terminal doesn't affect Claude Code bash (profile re-sources) | Test setup issue (not a code bug) | Test 1 Branch 1 | N/A |
| 4 | 5 skills used non-standard filenames (`SKILL-*.md` instead of `SKILL.md`) | Medium | Plugin loading | **Fixed** — renamed all to `SKILL.md` |
| 5 | 7 skills missing `user-invocable: true` in frontmatter | Low | Plugin loading | **Fixed** — added to all 14 user-invocable skills |
| 6 | Token leaked via `${HASS_TOKEN:-no}` expansion in improvised bash | **Critical** | /ha-validate | **Fixed** — safety reminder + safe patterns |
| 7 | Git Bash path mangling on hass-cli API paths (MINGW converts `/api/...`) | Medium | /ha-validate | **Fixed** — `MSYS_NO_PATHCONV=1` on all hass-cli raw commands |
| 8 | `argument-hint` in frontmatter causes fully qualified slash command names | Low | Plugin loading | **Fixed** — removed from ha-devices, ha-naming, ha-validate |
| 9 | SessionStart hook: missing settings file triggers false "setup incomplete" | Medium | /ha-deploy | **Fixed** — removed settings file from missingEnv check + terminal restart |
| 10 | Agent tries `--output json` on hass-cli (flag doesn't exist in 0.9.6) | Low | /ha-analyze | **Fixed** (unverified) — created references/hass-cli.md, removed flag from skills, added prohibition to resolver agent |
| 11 | PostToolUse:Edit hook error after writing automation to automations.yaml | Medium | ha-automations | **Fixed** (verified A2) — removed PostToolUse hook entirely |
| 12 | Entity resolver uses `-o json` on hass-cli | ~~Low~~ Not a bug | A4 (`5c5db733`), A4 re-test | **Reclassified** — `-o json` is valid and returns full attributes. Prohibition was wrong. Docs corrected to recommend `-o json`. |
| 13 | ha-deploy `disable-model-invocation` causes model to bypass skill safety workflow | High | A4 (`5c5db733`) | **Fixed** (verified A4 re-test) — removed flag, added in-skill confirmation gates |
