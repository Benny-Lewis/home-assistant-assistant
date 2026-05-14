---
name: ha-deploy
description: Use when the user says "deploy", "push changes", "send to HA", "sync to Home Assistant", "rollback", "revert", or otherwise asks to apply or undo local YAML edits on the live HA instance. Commits to git, pushes, and reloads HA; requires explicit confirmation at each side-effectful step.
---

# ha-deploy

Codex compatibility wrapper.

First read `../../codex/references/skill-adapter.md`, then read and follow `../../canonical-skills/ha-deploy/README.md` as the source of truth for this workflow.

Preserve every deployment confirmation gate from the canonical skill. Do not push, reload, restart, or roll back without explicit user confirmation for the concrete action.
