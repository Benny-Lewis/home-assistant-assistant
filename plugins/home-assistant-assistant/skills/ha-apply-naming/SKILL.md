---
name: ha-apply-naming
description: Execute a naming plan to rename entities and update all references.
---

# ha-apply-naming

Codex compatibility wrapper.

First read `../../codex/references/skill-adapter.md`, then read and follow `../../canonical-skills/ha-apply-naming/README.md` as the source of truth for this workflow.

The canonical Claude skill uses `disable-model-invocation: true`. Codex does not use that frontmatter key, so preserve it as a hard manual-execution contract: dry-run first, require explicit user approval, and execute the reviewed plan mechanically.
