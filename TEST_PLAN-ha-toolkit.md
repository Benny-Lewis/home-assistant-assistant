# HA Toolkit Test Plan

Comprehensive testing checklist for the ha-toolkit plugin.

## Prerequisites

Before testing, ensure:
- [ ] Claude Code is installed
- [ ] Plugin is loaded via `--plugin-dir` or copied to `~/.claude/plugins/`

**Test command:**
```bash
claude --plugin-dir "C:\Users\blewis\dev\haa-2\ha-toolkit"
```

---

## Part 1: Plugin Loading

### 1.1 Plugin Discovery
- [ ] Plugin appears in `/plugins` or plugin list
- [ ] No errors on startup related to ha-toolkit

### 1.2 Command Registration
- [ ] `/ha:` shows autocomplete options
- [ ] All 10 commands appear in `/help`:
  - [ ] `/ha:onboard`
  - [ ] `/ha:setup`
  - [ ] `/ha:new-device`
  - [ ] `/ha:generate`
  - [ ] `/ha:validate`
  - [ ] `/ha:deploy`
  - [ ] `/ha:audit-naming`
  - [ ] `/ha:plan-naming`
  - [ ] `/ha:apply-naming`
  - [ ] `/ha:analyze`

---

## Part 2: Command Testing

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

### 2.2 /ha:setup
**Test:** Run `/ha:setup`

**Expected behavior:**
- [ ] Lists available settings to update
- [ ] Allows updating specific setting
- [ ] Validates new values

### 2.3 /ha:generate
**Test cases:**

| Test | Command | Expected |
|------|---------|----------|
| Automation | `/ha:generate automation turn on lights when motion detected` | Valid automation YAML |
| Scene | `/ha:generate scene movie night with dim lights` | Valid scene YAML |
| Script | `/ha:generate script goodnight routine` | Valid script YAML |
| Dashboard | `/ha:generate dashboard climate control card` | Valid Lovelace card YAML |
| Template | `/ha:generate template average temperature sensor` | Valid template sensor YAML |

**Verification for each:**
- [ ] Generated YAML is syntactically correct
- [ ] Follows HA best practices
- [ ] Includes comments/explanations
- [ ] Offers to write to file

### 2.4 /ha:validate
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
- [ ] Suggests fixes

### 2.5 /ha:deploy
**Test:** Run `/ha:deploy` (with or without actual git repo)

**Expected behavior:**
- [ ] Checks for uncommitted changes
- [ ] Shows what would be committed
- [ ] Asks for commit message
- [ ] Attempts to push (may fail without git setup - that's OK)

### 2.6 /ha:audit-naming
**Test:** Run `/ha:audit-naming`

**Expected behavior:**
- [ ] Attempts to gather entity information
- [ ] Analyzes naming patterns
- [ ] Reports inconsistencies
- [ ] Suggests improvements

**Note:** Full test requires hass-cli connection; partial test verifies logic.

### 2.7 /ha:plan-naming
**Test:** Run `/ha:plan-naming` (after audit)

**Expected behavior:**
- [ ] Creates detailed rename plan
- [ ] Shows dependencies
- [ ] Saves plan to `.claude/naming-plan.yaml`

### 2.8 /ha:apply-naming
**Test:** Run `/ha:apply-naming --dry-run`

**Expected behavior:**
- [ ] Reads plan file
- [ ] Shows what would be changed
- [ ] Does NOT make changes in dry-run mode

### 2.9 /ha:new-device
**Test:** Run `/ha:new-device motion sensor kitchen`

**Expected behavior:**
- [ ] Asks about device details
- [ ] Suggests naming based on conventions
- [ ] Recommends automations for device type
- [ ] Offers dashboard integration

### 2.10 /ha:analyze
**Test:** Run `/ha:analyze`

**Expected behavior:**
- [ ] Analyzes available information
- [ ] Provides suggestions for improvements
- [ ] Recommends automations
- [ ] Identifies optimization opportunities

---

## Part 3: Skill Testing

Skills load automatically when relevant topics are discussed.

### 3.1 ha-config Skill
**Trigger phrases to test:**
- [ ] "How should I organize my configuration.yaml?"
- [ ] "What are packages in Home Assistant?"
- [ ] "How do I use secrets.yaml?"

**Expected:** Claude provides detailed HA config guidance.

### 3.2 ha-automation Skill
**Trigger phrases to test:**
- [ ] "How do I create an automation trigger?"
- [ ] "What automation modes are available?"
- [ ] "How do conditions work in automations?"

**Expected:** Claude provides automation pattern guidance.

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
- [ ] "How should I name my entities?"
- [ ] "What's a good pattern for entity IDs?"

**Expected:** Claude provides naming convention guidance.

### 3.6 ha-devices Skill
**Trigger phrases to test:**
- [ ] "What's the difference between Zigbee and Z-Wave?"
- [ ] "How do I add a new device?"
- [ ] "What entities does a motion sensor create?"

**Expected:** Claude provides device/integration guidance.

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

### 5.1 YAML Validation Hook
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
1. [ ] Run `/ha:new-device light living room ceiling`
2. [ ] Follow naming suggestions
3. [ ] Accept automation suggestions
4. [ ] Generate the automation with `/ha:generate`
5. [ ] Validate with `/ha:validate`
6. [ ] (Optional) Deploy with `/ha:deploy`

### 6.2 Full Workflow: Naming Standardization
1. [ ] Run `/ha:audit-naming`
2. [ ] Review the report
3. [ ] Run `/ha:plan-naming`
4. [ ] Review the plan file
5. [ ] Run `/ha:apply-naming --dry-run`
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
| Commands | /10 | | |
| Skills | /6 | | |
| Agents | /3 | | |
| Hooks | /1 | | |
| Integration | /3 | | |
| **Total** | **/25** | | |

---

## Known Limitations

- Full testing requires actual Home Assistant instance with hass-cli configured
- Git operations require configured repository
- Some commands will gracefully fail without prerequisites

## Reporting Issues

If tests fail, note:
1. Exact command/trigger used
2. Error message (if any)
3. Expected vs actual behavior
4. Environment details (OS, Claude Code version)
