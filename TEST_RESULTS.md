# Onboard Resume Detection — Test Results

**Date:** 2025-02-05
**Changes under test:** `home-assistant-assistant/skills/ha-onboard/SKILL.md` — token/server length-based detection, wrong-directory handling
**Commit before changes:** `24a49e5`

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

## UX Feedback

| # | Feedback | Status | Source |
|---|----------|--------|--------|
| 1 | Step 5 should auto-install hass-cli | Fixed (ask permission, then install) | Test 3 Run 1 |

---

## Summary of bugs

| # | Bug | Severity | Seen in | Status |
|---|-----|----------|---------|--------|
| 1 | `${#HASS_TOKEN}` fails when script is semicolon-joined (MINGW `#` parsing) | High | Test 1 Branch 1, Test 3 Run 1 | **Fixed** — replaced with `printf '%s' \| wc -c` |
| 2 | `NO_GIT_REMOTE` never prints (`head -1` returns 0 on empty input) | Medium | Test 1 All runs | **Fixed** — variable capture + `${REMOTE:-NO_GIT_REMOTE}` |
| 3 | `unset` in terminal doesn't affect Claude Code bash (profile re-sources) | Test setup issue (not a code bug) | Test 1 Branch 1 | N/A |
