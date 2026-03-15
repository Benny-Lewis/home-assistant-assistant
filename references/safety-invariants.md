# Safety Invariants

These are the **north-star rules** that every skill, command, and agent in this plugin must follow. Violations break user trust and cause real-world failures.
This file is the canonical source of truth for invariant count and wording.

## The Eight Invariants

### 1. No Unsupported Attributes

**Rule:** Never emit YAML attributes without first verifying the device supports them.

**Why:** Writing `color_temp: 300` for a bulb that only supports brightness causes HA errors or silent failures.

**Enforcement:**
```markdown
Before emitting any YAML that sets device attributes:
1. Call Resolver module to get capability snapshot
2. Check supported_features / supported_color_modes / hvac_modes
3. Only emit attributes that appear in the snapshot
4. If user requests unsupported attribute, warn and ask for override
```

**Example - Light Scene:**
```yaml
# BAD - assumes color temperature support
- light.bedroom_lamp:
    brightness: 200
    color_temp: 350  # Device may not support this!

# GOOD - checked capabilities first
# Resolver showed: supported_color_modes: [brightness]
- light.bedroom_lamp:
    brightness: 200
    # color_temp omitted - not supported
```

### 2. No Semantic Substitutions

**Rule:** Never replace user intent with a "equivalent" pattern unless equivalence is proven.

**Why:** "Turn off lights after 5 minutes of no motion" (inactivity) is NOT the same as "wait 5 minutes then turn off" (pure delay). Timer substitution breaks the semantic.

**The Inactivity vs Delay Classifier:**

| User Intent | Pattern | Timer Allowed? |
|-------------|---------|----------------|
| "After no motion for 5 min" | Inactivity | Only with cancel-on-motion logic |
| "Wait 5 minutes then..." | Pure delay | Yes |
| "5 min after motion stops" | Inactivity | Only with cancel-on-motion logic |
| "Delay for 5 minutes" | Pure delay | Yes |

**Correct Inactivity Pattern:**
```yaml
# Use trigger with for: (preferred)
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "off"
    for: "00:05:00"
actions:
  - action: light.turn_off
    target:
      entity_id: light.room
```

**Incorrect Substitution:**
```yaml
# BAD - timer doesn't cancel if motion resumes!
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "off"
actions:
  - action: timer.start
    target:
      entity_id: timer.room_delay
    data:
      duration: "00:05:00"
```

### 3. No Brittle String Edits

**Rule:** Never modify YAML using simple string replacement. Use AST editing or unique anchors.

**Why:** `old_string: "alias: Kitchen"` might match multiple places or fail if formatting varies.

**Enforcement:**
```markdown
When modifying existing YAML:
1. Always Read the file first
2. Find content by ID field (unique identifier)
3. Include 3+ lines of context for uniqueness
4. Use Editor module procedures
5. Validate YAML syntax after edit
```

**See:** `skills/ha-naming/references/editor.md` for safe editing procedures.

### 4. No Secrets Printed

**Rule:** Never echo, print, or log tokens, API keys, or secret prefixes.

**Why:** Secrets in logs/transcripts can be leaked, indexed, or accidentally committed.

**Enforcement:**
```markdown
When handling credentials:
- Report only: "configured" / "not set" / "present (length: N)"
- Never: echo $HASS_TOKEN, print(token), show first/last characters
- Settings files: store env var NAME, not the value
- Error messages: "token invalid" not "token xyz123... invalid"
```

**Example:**
```bash
# BAD - leaks the token value
echo "Token: $HASS_TOKEN"
echo "Token prefix: ${HASS_TOKEN:0:10}..."
echo "Token set: ${HASS_TOKEN:+yes}${HASS_TOKEN:-no}"  # :-no expands to value when set!

# BAD - dumps all env vars including HASS_TOKEN
env | grep -i hass
printenv | grep TOKEN
set | grep HASS
export -p | grep HASS

# GOOD - reports presence without revealing value
TLEN=$(printf '%s' "$HASS_TOKEN" | wc -c); echo "TOKEN_LEN=$TLEN"
```

> **Hook enforcement:** The `env-guard.sh` PreToolUse hook blocks `env`, `printenv`, `set`,
> and `export -p` commands automatically. If you need to check env var presence, use the
> safe `wc -c` pattern above.

### 5. Never Deploy Unless Explicitly Requested

**Rule:** No side-effectful action (commit, push, reload, write) without explicit user confirmation.

**Why:** Unexpected deployments can break working systems, interrupt users, or push untested changes.

**Enforcement:**
```markdown
Side-effectful commands must:
1. Set `disable-model-invocation: true` in frontmatter
2. Default to dry-run / preview mode
3. Show exactly what will happen before acting
4. Require explicit "yes, deploy now" confirmation
5. Offer "save for later" as the default path
```

**Side-effect classification:**
| Action | Side-effectful? | Requires confirmation? |
|--------|-----------------|------------------------|
| Read file | No | No |
| List entities | No | No |
| Generate YAML (preview) | No | No |
| Write to file | Yes | Yes |
| Git commit | Yes | Yes |
| Git push | Yes | Yes |
| HA reload | Yes | Yes |
| Entity rename | Yes | Yes |
| Install package (pip/npm/etc.) | Yes | Yes |

**Package Installation:** Installing packages on the user's machine (`pip install`, `npm install`, etc.)
modifies their environment. Always ask before installing. Exception: `/ha-onboard` Step 5
(hass-cli installation) already has an explicit confirmation gate.

### 6. Evidence Tables Required

**Rule:** Validation, deployment, and diagnostic outputs must include a "what ran vs skipped" table.

**Why:** Summary-only status can hide skipped checks and create false confidence.

See "Invariant 6 Details" below for the required table format.

### 7. Minimal Edits Only

**Rule:** Make only the specific changes requested. Do not reorganize, merge, or restructure adjacent content unless explicitly asked.

**Why:** Unrequested restructuring can break working configurations and create unexpected side effects. Users expect precise, surgical edits.

**Enforcement:**
```markdown
When editing YAML or dashboard configs:
1. Change only the targeted lines
2. Preserve surrounding structure, ordering, and formatting
3. If adjacent content has issues, note them separately — do not fix them as part of the current edit
```

### 8. Verify After Config Edits

**Rule:** After editing YAML config files, offer to deploy and verify changes are live. Validate entity IDs exist before use.

**Why:** YAML config changes are not live until deployed and reloaded. Entity references that don't exist cause silent runtime failures (conditions evaluate to false, triggers never fire).

**Enforcement:**
```markdown
After saving config edits:
1. Offer `/ha-deploy` to deploy and reload
2. Before writing entity references in automations/scripts/scenes, verify each entity exists via `hass-cli state get <entity_id>`
3. Note: `hass-cli config check` validates YAML syntax only — it does NOT check entity existence
```

## Applying Invariants

### For Skills

Add to skill frontmatter or body:
```markdown
## Safety Checklist

Before generating output:
- [ ] Capability snapshot obtained (Invariant 1)
- [ ] Intent classified (inactivity vs delay) (Invariant 2)
- [ ] No hardcoded device attributes without verification

Before writing:
- [ ] User explicitly requested write/deploy (Invariant 5)
- [ ] Using Editor module for YAML changes (Invariant 3)
- [ ] Only targeted lines changed, no adjacent restructuring (Invariant 7)

After writing:
- [ ] Offered `/ha-deploy` to deploy and reload (Invariant 8)
- [ ] Verified entity IDs exist via `hass-cli state get` (Invariant 8)

Before reporting validation/diagnostics:
- [ ] Include an evidence table with checks run vs skipped (Invariant 6)
```

### For Commands

Add to command frontmatter:
```yaml
---
name: ha-dangerous-command
disable-model-invocation: true  # Invariant 5
allowed-tools: Read, Grep, Glob  # Minimize blast radius
---
```

### For Agents

Include in agent system prompt:
```markdown
## Safety Rules

You must follow these invariants:
1. Always get capability snapshots before suggesting device attributes
2. Never substitute timers for inactivity patterns without explicit logic
3. Never print tokens or secret values
4. Never initiate deployment without explicit user request/confirmation
5. Report checks run/skipped using an evidence table (Invariant 6)
6. Make only the specific changes requested — no adjacent restructuring (Invariant 7)
7. After config edits, offer deploy/reload and verify entity IDs exist (Invariant 8)
```

### Invariant 6 Details

All validation, deployment, and diagnostic outputs must include a "what ran vs skipped" table:

```markdown
## What Ran vs Skipped

| Check | Status | Result | Details |
|-------|--------|--------|---------|
| YAML Syntax | Ran | Passed | Valid YAML structure |
| HA Schema | Ran | Passed | All fields recognized |
| Entity Resolution | Ran | 3/3 found | All entities exist |
| Service Validation | Skipped | - | hass-cli unavailable |
| HA Config Check | Skipped | - | No HA connection |
```

**Why this matters:**
- Prevents false confidence ("validation passed" when only syntax was checked)
- Users can see exactly what protection they have
- Makes gaps in validation visible and actionable

**Required for:**
- `/ha-validate` output
- Pre-deploy validation in `/ha-deploy`
- Post-generation validation in skills
- Troubleshooting diagnostics

---

## Violation Reporting

If you detect an invariant violation in existing code, document it:

```markdown
## Invariant Violation Found

**File:** skills/ha-scenes/SKILL.md
**Invariant:** #5 (Never deploy unless requested)
**Issue:** Step 7 says "Deploy via /ha-deploy" as default action
**Fix:** Change to "Optionally deploy if user explicitly requests"
```
