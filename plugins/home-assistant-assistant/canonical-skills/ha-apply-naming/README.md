---
name: ha-apply-naming
description: Execute a naming plan to rename entities and update all references
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# Apply Naming Plan

> **Safety Invariant #5:** Never deploy unless explicitly requested.
> **Safety Invariant #3:** Use AST editing, not brittle string replacement.
>
> Default mode is DRY-RUN. Use `--execute` to apply changes.

Execute the naming plan created by `/ha-naming` (plan workflow) to rename entities, devices, and update all references.

## Dry-Run Default

**By default, this skill shows what WOULD change without modifying anything.**

To actually apply changes, user must explicitly add `--execute`:
```
/ha-apply-naming --execute
```

Without `--execute`, show preview:
```
## Dry Run Preview

The following changes would be made:

| Entity | Current | New |
|--------|---------|-----|
| light.light_1 | light.light_1 | light.living_room_ceiling |
| light.light_2 | light.light_2 | light.living_room_lamp |

Files that would be updated:
- automations.yaml (3 references)
- scenes.yaml (2 references)

Run with `--execute` to apply these changes.
```

**After showing the dry-run preview, use AskUserQuestion:**
- Question: "Dry-run complete. What would you like to do?"
- Option 1: "Execute all phases" → proceed with `--execute` behavior
- Option 2: "Execute Phase N only" → proceed with `--phase N --execute`
- Option 3: "Done for now" → stop, user can return later

## Prerequisites

- **Naming plan** — search in order:
  1. `.claude/naming-plan.yaml` (canonical)
  2. Glob for `**/naming-plan*` or `**/rename-plan*`
  3. `.claude/ha.conventions.json` (conventions only, no rename mappings)
- If nothing found: "No naming plan found. Run `/ha-naming` first."
- hass-cli configured for entity renames
- Git configured for config file updates

## Workflow Index

Full execution procedure lives in per-skill references:

- `references/execution.md` — Safety Features (backup, AST editing, phased execution), the 8-phase Execution Process (Preparation → Stale Entity Removal), Post-Plan Scope Gate, Progress Reporting format, and the final Output / "What Ran vs Skipped" template
- `references/recovery.md` — Rollback Capability and Error Handling procedures for failed phases
