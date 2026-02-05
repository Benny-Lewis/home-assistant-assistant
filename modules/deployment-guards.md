# Deployment Guards Module

Rules and patterns for protecting users from unintended side effects.

> **Safety Invariant #5:** Never deploy unless explicitly requested.
> See `references/safety-invariants.md` for full details.

## Purpose

Side-effectful operations (write, commit, push, reload) can:
- Break working configurations
- Interrupt running automations
- Push untested changes to production
- Lose work if done prematurely

This module defines the guardrails all commands must implement.

## Side-Effect Classification

### Safe Operations (No Guard Required)

| Operation | Why Safe |
|-----------|----------|
| Read file | No state change |
| List entities | Read-only API |
| Search codebase | No modification |
| Generate YAML (preview) | Output only |
| Validate syntax | Analysis only |

### Guarded Operations (Confirmation Required)

| Operation | Risk Level | Required Guard |
|-----------|------------|----------------|
| Write file | Medium | Show diff, confirm |
| Git add | Low | Part of commit flow |
| Git commit | Medium | Show changes, confirm |
| Git push | High | Explicit confirmation |
| HA reload | High | Explicit confirmation |
| Entity rename | High | Dry-run default |
| Config apply | High | Preview + confirm |

## Implementation Patterns

### 1. Frontmatter Guards

Side-effectful commands must include:

```yaml
---
name: ha-deploy
description: Deploy configuration changes
disable-model-invocation: true  # Prevents auto-triggering
allowed-tools: Read, Bash, AskUserQuestion  # Minimal permissions
---
```

**`disable-model-invocation: true`** means:
- Command cannot be triggered by Claude interpreting user intent
- User must explicitly type `/ha-deploy`
- Prevents "I'll just deploy that for you" behavior

### 2. Dry-Run Default

Commands that modify state should default to preview mode:

```markdown
## Default Behavior

Show what WOULD happen without making changes:

1. Read current state
2. Compute proposed changes
3. Display diff/preview
4. Ask: "Apply these changes? [y/N]"

Default answer is NO - user must explicitly confirm.
```

### 3. Explicit Confirmation Flow

```markdown
## Proposed Changes

| File | Action | Summary |
|------|--------|---------|
| automations.yaml | Update | Modified kitchen_motion |
| scripts.yaml | Add | New script morning_routine |

## Commands That Will Run

1. `git add automations.yaml scripts.yaml`
2. `git commit -m "Update kitchen automation, add morning routine"`
3. `git push origin main`
4. `hass-cli service call homeassistant.reload_all`

**This will push to production and reload Home Assistant.**

Proceed? (yes/no): _
```

### 4. Staged Confirmation

For high-risk operations, confirm each stage:

```markdown
## Stage 1: Local Changes
- Write automations.yaml ✓
- Write scripts.yaml ✓

Commit these changes? (yes/no): _

## Stage 2: Push to Remote
Changes committed locally.

Push to origin/main? (yes/no): _

## Stage 3: Reload Home Assistant
Changes pushed.

Reload Home Assistant now? (yes/no): _
```

## Command-Specific Guards

### /ha-deploy

```yaml
disable-model-invocation: true
```

Flow:
1. Show `git diff` of pending changes
2. Confirm commit message
3. Confirm push to remote
4. Confirm HA reload (separate step)

### /ha:apply-naming

```yaml
disable-model-invocation: true
```

Flow:
1. Default to `--dry-run`
2. Show all proposed renames
3. Allow phase-by-phase application
4. Each phase requires confirmation

### /ha-rollback

```yaml
disable-model-invocation: true
```

Flow:
1. Show what will be reverted
2. Confirm rollback commit
3. Confirm push
4. Confirm reload

## Anti-Patterns

### Never Do This

```markdown
# BAD - Auto-deploys without asking
After generating the automation, I'll deploy it for you.
*deploys*
Done! Your automation is now live.

# BAD - Assumes consent
Since you asked for an automation, I'll write it to automations.yaml
and push it to your Home Assistant.

# BAD - Buries confirmation
I've made the changes. The automation is ready.
[tiny text: changes were pushed to production]
```

### Always Do This

```markdown
# GOOD - Explicit choice
I've generated the automation YAML. Here's a preview:

[yaml preview]

What would you like to do?
1. Save to automations.yaml (local only)
2. Save and deploy to Home Assistant
3. Copy to clipboard
4. Make changes first

# GOOD - Clear about consequences
This will:
- Commit changes to git
- Push to origin/main
- Trigger Home Assistant to reload

Your currently running automations will briefly restart.

Proceed? (yes/no):
```

## Integration Points

- **/ha-deploy**: Primary deployment command
- **/ha:apply-naming**: Bulk rename operations
- **/ha-rollback**: Revert operations
- **ha-automations skill**: Generate only, route write to commands
- **ha-scenes skill**: Generate only, route write to commands
