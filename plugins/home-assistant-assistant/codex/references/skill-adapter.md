# Codex Skill Adapter

This file is the compatibility layer for running the shared Home Assistant Assistant skill specs under Codex.

## Source of Truth

The canonical Home Assistant workflows remain in `skills/<skill>/SKILL.md` and their skill-local `references/` files. Codex wrapper skills should read this adapter first, then read the matching canonical skill.

Do not fork Home Assistant domain behavior into `codex-skills/`. Keep safety rules, validation gates, and procedural details in the shared skill tree unless the behavior is truly Codex-specific.

## Tool Translation

- Claude `Read` maps to reading files with shell commands or available file tools.
- Claude `Grep` and `Glob` map to `rg`, `rg --files`, or the nearest shell equivalent.
- Claude `Edit` and `Write` map to `apply_patch` for repository edits.
- Claude `Bash` maps to Codex shell commands.
- Claude `AskUserQuestion` maps to one concise plain-text question.
- Claude `Task` or subagents map to Codex subagents only when the user explicitly asks for subagents, delegation, or parallel agent work. Otherwise, do the work locally.

## Invocation Translation

- Claude slash commands such as `/ha-validate` map to explicit Codex skill mentions such as `$ha-validate` when the user wants to invoke a skill by name.
- Domain skills can still trigger implicitly from their descriptions.
- The original `ha-resolver` skill is infrastructure. Use it only when another Home Assistant skill asks for entity resolution or capability snapshots.

## Safety Translation

Preserve the eight safety invariants from `references/safety-invariants.md`.

Preserve confirmation gates. In particular:

- Do not deploy, reload, restart, push, rename, or mutate live Home Assistant state unless the user explicitly requested that side effect and confirmed the concrete action.
- Do not print Home Assistant tokens or environment dumps.
- Do not emit YAML with unsupported device attributes.
- Do not substitute inactivity patterns with raw timers.
- Keep edits minimal and scoped to the request.

The canonical `ha-apply-naming` skill uses Claude's `disable-model-invocation: true`. Codex does not use that frontmatter key, so the wrapper must treat it as a hard manual-execution contract: dry-run first, require explicit approval, and execute the plan mechanically.

## Environment Notes

Most shared workflows use `hass-cli` and expect:

- `HASS_SERVER`
- `HASS_TOKEN`

Codex users may also configure HA MCP tools with:

- `HOMEASSISTANT_URL`
- `HOMEASSISTANT_TOKEN`

The MCP variables do not replace `hass-cli` variables for these shared skills unless the workflow explicitly says it can use MCP tools.
