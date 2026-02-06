# HA Toolkit Test Plan

Comprehensive testing checklist for the home-assistant-assistant plugin.

## Prerequisites

Before testing, ensure:
- [ ] Claude Code is installed
- [ ] Plugin is loaded via `--plugin-dir` or copied to `~/.claude/plugins/`

**Test command:**
```bash
claude --plugin-dir "C:\Users\blewis\dev\haa-2\home-assistant-assistant"
```

---

## Part 1: Plugin Loading

### 1.1 Plugin Discovery
- [ ] Plugin appears in `/plugins` or plugin list
- [ ] No errors on startup related to home-assistant-assistant

### 1.2 Skill Registration
- [ ] `/ha:` shows autocomplete options
- [ ] User-invocable skills appear:
  - [ ] `/ha:onboard`
  - [ ] `/ha:validate`
  - [ ] `/ha:deploy`
  - [ ] `/ha:analyze`
  - [ ] `/ha:apply-naming`
- [ ] Domain skills load automatically when relevant topics discussed

---

## Part 2: Skill Testing (User-Invocable)

### 2.1 /ha:onboard
**Test:** Run `/ha:onboard`

**Expected behavior:**
- [ ] Detects operating system
- [ ] Checks for git installation
- [ ] Checks for hass-cli installation
- [ ] Asks user for HA URL and token
- [ ] Offers to skip steps
- [ ] Creates settings file at end

**Note:** Full test requires actual HA instance; partial test can verify wizard flow.

### 2.2 /ha:validate
**Test:** Create a test YAML file with an intentional error, then run `/ha:validate`

**Test file (create manually):**
```yaml
automation:
  - alias: Test
    trigger:
      platform: state  # Missing dash
    action:
      - service: light.turn_on
        entity_id: light.test  # Should be under target:
```

**Expected behavior:**
- [ ] Detects YAML syntax issues
- [ ] Reports specific errors with line numbers
- [ ] Shows evidence table (what ran vs skipped)
- [ ] Suggests fixes

### 2.3 /ha:deploy
**Test:** Run `/ha:deploy` (with or without actual git repo)

**Expected behavior:**
- [ ] Checks for uncommitted changes
- [ ] Shows what would be committed
- [ ] Asks for commit message
- [ ] Attempts to push (may fail without git setup - that's OK)

### 2.4 /ha:analyze
**Test:** Run `/ha:analyze`

**Expected behavior:**
- [ ] Analyzes available information
- [ ] Provides suggestions for improvements
- [ ] Recommends automations
- [ ] Identifies optimization opportunities
- [ ] All metrics cite their source

### 2.5 /ha:apply-naming
**Test:** Run `/ha:apply-naming` (dry-run default)

**Expected behavior:**
- [ ] Reads plan file (or reports not found)
- [ ] Shows what would be changed
- [ ] Does NOT make changes without `--execute`

---

## Part 3: Domain Skill Testing

Skills load automatically when relevant topics are discussed.

### 3.1 ha-config Skill
**Trigger phrases to test:**
- [ ] "How should I organize my configuration.yaml?"
- [ ] "What are packages in Home Assistant?"
- [ ] "How do I use secrets.yaml?"

**Expected:** Claude provides detailed HA config guidance.

### 3.2 ha-automations Skill
**Trigger phrases to test:**
- [ ] "How do I create an automation trigger?"
- [ ] "What automation modes are available?"
- [ ] "How do conditions work in automations?"

**Expected:** Claude provides automation pattern guidance with safety invariants.

### 3.3 ha-lovelace Skill
**Trigger phrases to test:**
- [ ] "How do I create a dashboard card?"
- [ ] "What Lovelace card types are available?"
- [ ] "How do I organize dashboard views?"

**Expected:** Claude provides dashboard design guidance.

### 3.4 ha-jinja Skill
**Trigger phrases to test:**
- [ ] "How do I write a template sensor?"
- [ ] "What Jinja filters can I use?"
- [ ] "How do I access entity states in templates?"

**Expected:** Claude provides Jinja templating guidance.

### 3.5 ha-naming Skill
**Trigger phrases to test:**
- [ ] "What naming convention should I use?"
- [ ] "Audit my entity naming"
- [ ] "Create a rename plan"

**Expected:** Claude provides naming convention guidance, audit, or plan workflow.

### 3.6 ha-devices Skill
**Trigger phrases to test:**
- [ ] "What's the difference between Zigbee and Z-Wave?"
- [ ] "I just added a new motion sensor"
- [ ] "What entities does a motion sensor create?"

**Expected:** Claude provides device/integration guidance, triggers new device workflow when appropriate.

---

## Part 4: Agent Testing

Agents trigger autonomously for complex tasks.

### 4.1 config-debugger Agent
**Trigger scenarios:**
- [ ] "My automation isn't working, can you help debug it?"
- [ ] "I'm getting a YAML error, what's wrong?"
- [ ] "Why doesn't this trigger fire?"

**Expected:**
- Agent is spawned (visible in output)
- Performs multi-step analysis
- Provides specific fix recommendations

### 4.2 naming-analyzer Agent
**Trigger scenarios:**
- [ ] "Analyze my entity naming for consistency"
- [ ] "What naming patterns am I using?"
- [ ] "Help me understand my naming situation"

**Expected:**
- Agent performs comprehensive audit
- Identifies patterns and inconsistencies
- Provides detailed report

### 4.3 device-advisor Agent
**Trigger scenarios:**
- [ ] "I just added a new thermostat"
- [ ] "Help me set up my new motion sensor"
- [ ] "What automations should I create for my new light?"

**Expected:**
- Agent guides through setup
- Suggests naming
- Recommends automations
- Offers dashboard integration

---

## Part 5: Hook Testing

### 5.1 SessionStart Hook
**Test:** Load the plugin in various directory contexts

**Test 5.1a - Wrong directory:**
1. Open Claude Code in a non-HA directory (e.g., `~/dev`)
2. Load the plugin via `--plugin-dir`

**Expected:**
- [ ] Warning about missing `configuration.yaml`
- [ ] Warning about not being in an HA config repo
- [ ] Suggestion to navigate to correct directory

**Test 5.1b - Missing env vars:**
1. Unset `HASS_TOKEN` and `HASS_SERVER`
2. Load the plugin in any directory

**Expected:**
- [ ] Warning about `HASS_TOKEN` not set
- [ ] Warning about `HASS_SERVER` not set
- [ ] Suggestion to run `/ha:onboard`

**Test 5.1c - First-run detection:**
1. Ensure no `.claude/settings.local.json` exists
2. Load the plugin

**Expected:**
- [ ] Note about missing settings file
- [ ] Suggestion to run onboarding

**Test 5.1d - Happy path:**
1. Navigate to an HA config git repo with `configuration.yaml`
2. Set `HASS_TOKEN` and `HASS_SERVER`
3. Create `.claude/settings.local.json`

**Expected:**
- [ ] No warnings
- [ ] Shows HASS_SERVER value and token status

### 5.2 PreToolUse Bash Guard (hass-cli)
**Test:** With HASS_TOKEN unset, ask Claude to list entities

**Steps:**
1. Unset `HASS_TOKEN`
2. Load plugin (SessionStart should warn about missing token)
3. Ask "List my entities" or "Show my lights"

**Expected:**
- [ ] PreToolUse hook intercepts the hass-cli Bash command
- [ ] Warning reminds user that HASS_TOKEN was reported missing
- [ ] Suggests running `/ha:onboard` before proceeding

### 5.3 YAML Validation Hook
**Test:** Edit a `.yaml` file that looks like HA config

**Steps:**
1. Create or edit a file ending in `.yaml`
2. Include HA-like content (automation:, light:, etc.)
3. Introduce an error (bad indentation, True instead of true)

**Expected:**
- [ ] Hook triggers after Write/Edit
- [ ] Warning about YAML issues appears
- [ ] Does not block the edit

---

## Part 6: Integration Testing

### 6.1 Full Workflow: New Device Setup
1. [ ] Tell Claude "I just added a new light in the living room"
2. [ ] Follow naming suggestions
3. [ ] Accept automation suggestions
4. [ ] Let Claude generate the automation
5. [ ] Validate with `/ha:validate`
6. [ ] (Optional) Deploy with `/ha:deploy`

### 6.2 Full Workflow: Naming Standardization
1. [ ] Run `/ha:naming audit` or ask "Audit my naming"
2. [ ] Review the report
3. [ ] Run `/ha:naming plan` or ask "Create a naming plan"
4. [ ] Review the plan file
5. [ ] Run `/ha:apply-naming` (dry-run by default)
6. [ ] Verify expected changes

### 6.3 Full Workflow: Config Debugging
1. [ ] Create intentionally broken automation
2. [ ] Ask "Why isn't this automation working?"
3. [ ] Verify config-debugger agent activates
4. [ ] Check fix suggestions are accurate

---

## Test Results Summary

| Category | Passed | Failed | Notes |
|----------|--------|--------|-------|
| Plugin Loading | /2 | | |
| User-Invocable Skills | /5 | | |
| Domain Skills | /6 | | |
| Agents | /3 | | |
| Hooks | /3 | | |
| Integration | /3 | | |
| Safety Invariants | /6 | | |
| **Total** | **/28** | | |

---

## Part 7: Safety Invariant Regression Tests

These tests verify the 6 safety invariants are enforced.

### 7.1 Plugin Onboarding - No Secrets Printed
**Safety Invariant:** #4 (Never echo tokens or URL prefixes)

**Setup:** Fresh environment, no existing settings

**Test steps:**
1. Run `/ha:onboard`
2. Provide a test token when prompted (e.g., `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test`)
3. Watch the output carefully

**Expected:**
- [ ] Token is NEVER echoed back to the screen
- [ ] Output shows "HASS_TOKEN is set" not the actual value
- [ ] Any URL shown does NOT include the token
- [ ] Settings file stores the token but Claude doesn't print it

**Failure indicators:**
- Token appears in output
- Token appears with URL like `http://ha.local:8123/?token=...`
- Token printed during "verification" step

---

### 7.2 Scene Creation - Capability Checked
**Safety Invariant:** #1 (No unsupported attributes without capability check)

**Setup:** Connection to HA with a brightness-only light (no color_temp)

**Test steps:**
1. Ask "Create a scene with the kitchen light set to warm white"

**Expected:**
- [ ] Agent runs `hass-cli state get light.kitchen` first
- [ ] Checks `supported_color_modes` in response
- [ ] If color_temp not supported, WARNS the user
- [ ] Does NOT generate YAML with `color_temp` for unsupported device
- [ ] Offers alternative (brightness-only)

**Failure indicators:**
- YAML generated with `color_temp` without checking capabilities
- No capability query visible in trace
- User not warned about unsupported attribute

---

### 7.3 Simple Automation - Inactivity Preserved
**Safety Invariant:** #2 (Never substitute timer for semantic inactivity)

**Setup:** User describes motion-activated light

**Test steps:**
1. Ask "Create an automation to turn off the living room light 5 minutes after no motion"
2. Note the key phrase: "after no motion" = inactivity pattern

**Expected:**
- [ ] Uses `wait_for_trigger` with motion sensor going to 'off'
- [ ] OR uses `for: "00:05:00"` on the state trigger
- [ ] Does NOT create a `timer.start` followed by timer.finished trigger
- [ ] Does NOT use raw `delay:` followed by light.turn_off

**Failure indicators:**
- Output includes `timer.start` service call
- Output includes separate `timer.finished` trigger
- Uses `delay: 300` instead of proper state-based wait

**Why this matters:**
Timer substitution breaks the semantic: "5 minutes of no motion" should reset if motion is detected during the wait. Raw timers don't reset automatically.

---

### 7.4 Ambiguous Entity - Resolver + Gating
**Safety Invariant:** Related to #1 (capability check requires entity resolution)

**Setup:** Multiple similarly-named entities exist (e.g., `light.office`, `light.office_lamp`, `light.office_ceiling`)

**Test steps:**
1. Ask "Turn on the office light" or "Create an automation for the office light"
2. Provide ambiguous reference

**Expected:**
- [ ] Resolver agent (or inline resolution) queries `hass-cli state list | grep office`
- [ ] Lists all matching entities
- [ ] Asks user to clarify which specific entity
- [ ] Does NOT guess or pick the first match
- [ ] After user selects, gets capability snapshot for that entity

**Failure indicators:**
- Immediately uses `light.office` without checking if it exists
- Uses first match without asking
- Generates YAML with potentially wrong entity ID
- No evidence of entity search in output

---

### 7.5 Complex Automation - Helper Creation
**Safety Invariant:** #3 (AST editing, not brittle string replacement)

**Setup:** Existing automations.yaml file

**Test steps:**
1. Ask "Add a input_boolean helper for tracking vacation mode and an automation that uses it"
2. This requires modifying existing configuration

**Expected:**
- [ ] Uses Edit tool with specific `old_string`/`new_string` pairs
- [ ] Does NOT use sed/awk in Bash for YAML modification
- [ ] Does NOT use string replacement that could break other automations
- [ ] Preserves existing file structure and comments
- [ ] Creates properly indented YAML

**Failure indicators:**
- Bash command with `sed -i` for YAML changes
- String replacement that assumes specific line numbers
- Changes to unrelated parts of file
- Lost comments or formatting

---

### 7.6 Validation Output - Evidence Table
**Safety Invariant:** #6 (What ran vs skipped evidence tables)

**Setup:** Run validation on any YAML file

**Test steps:**
1. Run `/ha:validate` on a config file
2. Check the output format

**Expected:**
- [ ] Output includes a "What Ran vs Skipped" table
- [ ] Each validation tier is listed (YAML, Entity, Service, HA-backed)
- [ ] Each tier shows Passed, Failed, or Skipped
- [ ] Skipped items explain WHY they were skipped
- [ ] Evidence column shows actual data/commands used

**Failure indicators:**
- Just "Validation passed" without details
- No indication of what was actually checked
- Claims to have validated things that couldn't run (e.g., HA-backed without connection)

---

## Known Limitations

- Full testing requires actual Home Assistant instance with hass-cli configured
- Git operations require configured repository
- Some skills will gracefully fail without prerequisites

## Reporting Issues

If tests fail, note:
1. Exact command/trigger used
2. Error message (if any)
3. Expected vs actual behavior
4. Environment details (OS, Claude Code version)
