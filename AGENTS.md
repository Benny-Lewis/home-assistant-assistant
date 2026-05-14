# AGENTS.md

Shared guidance for Claude Code and Codex when working in this repository.

## Project Overview

This is a Claude Code and Codex plugin for Home Assistant. It allows users to manage Home Assistant configurations through natural language: creating automations, scripts, scenes, and dashboards by describing what they want instead of manually editing YAML.

Type: Claude Code and Codex plugin (markdown-based, no build system or compiled code)

## Safety Invariants

All generated YAML and commands enforce eight safety invariants (canonical wording in `references/safety-invariants.md`):

1. No unsupported attributes - Always check `supported_features`/`supported_color_modes` before suggesting device attributes
2. No semantic substitution - Never replace "after no motion" (inactivity) with raw timers
3. AST editing only - No brittle string replacement; use Edit tool with precise old/new strings
4. No secrets printed - Never echo tokens; show "TOKEN is set" not the value
5. Never deploy unless explicitly requested - All side-effectful skills require explicit user request and confirmation
6. Evidence tables - All validation outputs show "what ran vs skipped"
7. Minimal edits only - Make only the specific changes requested; do not reorganize adjacent content
8. Verify after config edits - Offer deploy/reload after YAML changes; validate entity IDs exist before use

## Plugin Architecture

The plugin has two agent-facing surfaces that share one canonical workflow source:

- Claude Code reads `.claude-plugin/`, `skills/`, `agents/`, and `hooks/`.
- Codex reads `.codex-plugin/`, `codex-skills/`, `codex/`, and `.agents/plugins/marketplace.json`.
- Canonical Home Assistant behavior stays in `skills/` and `references/`; Codex wrappers adapt invocation/tool semantics without forking domain logic.

```text
.claude-plugin/
  plugin.json               # Plugin manifest - metadata, component discovery
.codex-plugin/
  plugin.json               # Codex plugin manifest - points at codex-skills and codex hooks
.agents/plugins/
  marketplace.json          # Codex marketplace source for this single-plugin repo
skills/
  ha-automations/           # Automation creation + domain knowledge (user-invocable)
  ha-scripts/               # Script creation + domain knowledge (user-invocable)
  ha-scenes/                # Scene creation + domain knowledge (user-invocable)
  ha-config/                # Config organization knowledge (user-invocable)
  ha-jinja/                 # Jinja templating knowledge (user-invocable)
  ha-lovelace/              # Dashboard design knowledge (user-invocable)
  ha-naming/                # Naming conventions + audit + plan (user-invocable)
  ha-apply-naming/          # Naming execution (user-invocable, NO model invocation)
  ha-devices/               # Device knowledge + new device workflow (user-invocable)
  ha-troubleshooting/       # Debugging knowledge (user-invocable)
  ha-onboard/               # Setup wizard + connection + settings (user-invocable)
  ha-deploy/                # Deploy + rollback (user-invocable, in-skill confirmation gates)
  ha-validate/              # Validation workflow + procedures (user-invocable, agent-preloadable)
  ha-analyze/               # Setup analysis + recommendations (user-invocable)
  ha-resolver/              # Entity resolution (NOT user-invocable, agent-preloaded)
codex-skills/
  ha-*/                     # Codex-compatible wrapper skills with Codex-valid frontmatter
codex/
  hooks.json                # Codex hook mapping
  session_check.py          # Codex SessionStart check (no Bash dependency)
  env_guard.py              # Codex PreToolUse guard, including PowerShell env dumps
  references/skill-adapter.md
agents/
  *.md                      # 6 subagents: config-debugger, ha-config-validator,
                            # device-advisor, naming-analyzer, ha-entity-resolver,
                            # ha-log-analyzer
helpers/
  area-search.py            # Area-based entity search (registry cross-referencing)
  entity-registry.py        # Entity registry operations
  ha-overview.py            # HA setup overview generation
  trace-fetch.py            # Automation trace fetching
  lovelace-dashboard.py     # Lovelace dashboard fetch/save/verify/find-entities
hooks/
  hooks.json                # Event-driven hooks (SessionStart, PreToolUse, PostToolUse)
  session-check.sh          # Claude async env check (HASS_TOKEN, HASS_SERVER, python detection)
  env-guard.sh              # PreToolUse guard for Bash commands
  docs-check.sh             # Documentation validation
  docs-check.py             # Documentation validation helper
references/
  safety-invariants.md      # Core safety rules referenced by all skills
  settings-schema.md        # Settings file schema
  hass-cli.md               # hass-cli usage reference
  ha-web-ui.md              # HA web UI reference
  dashboard-api.md          # WebSocket API contract for storage dashboards
templates/
  templates.md              # Reference templates for generated configs
```

15 skills total: 14 user-invocable + 1 infrastructure (`ha-resolver`). `ha-validate` is both user-invocable and agent-preloadable.

Progressive disclosure: skills with long procedural content keep `SKILL.md` as a tight triggering surface (frontmatter, safety banner, decision rules, workflow index) and move step-by-step detail into per-skill `references/*.md`. Skills currently using this pattern: `ha-apply-naming`, `ha-automations`, `ha-devices`, `ha-lovelace`, `ha-naming`, `ha-onboard`, `ha-resolver`, `ha-scenes`, `ha-scripts`, `ha-troubleshooting`. When exploring a skill, read its `SKILL.md` first, then follow the Workflow Index to the specific reference file needed.

## Marketplace Packaging Note

For this repo's self-hosted single-plugin marketplace, keep `.claude-plugin/marketplace.json` pointing the plugin entry at `source: "./"`.

Do not point that marketplace entry back to this same repository via a remote git/GitHub URL. In Claude Code's local-scope install/update path, that can cause the marketplace repo to be recursively repackaged into the plugin cache and break updates on Windows.

For Codex, keep `.agents/plugins/marketplace.json` pointing the plugin entry at local `path: "./"`, because this repository is itself the plugin root.

## Testing

Deterministic eval harness checks safety contracts and regression guards with no Home Assistant connection needed:

```powershell
# Run all suites (3 passes each)
powershell -ExecutionPolicy Bypass -File dev/testing/scripts/eval-harness.ps1 -Suite all -Passes 3

# Run a single suite
powershell -ExecutionPolicy Bypass -File dev/testing/scripts/eval-harness.ps1 -Suite capability
powershell -ExecutionPolicy Bypass -File dev/testing/scripts/eval-harness.ps1 -Suite regression
```

Suites:

- `capability` - safety contracts: `disable-model-invocation` flags, deploy validation gates, push target resolution, tool allowlists, breadcrumb gitignore, invariant count
- `regression` - guards against past bugs: broken skill references, deploy wording drift, settings schema keys, helper function correctness (trace URLs, area matching, overview JSON, timestamps)

Cases are JSON files in `dev/testing/evals/{capability,regression}/`. Each case declares file-content or command-output checks. The harness runs multi-pass and reports single-run pass rate and pass@k.

Manual testing approach, still required for live Home Assistant workflows:

```bash
# Load plugin for testing (from repo root)
claude --plugin-dir .
```

Codex wrapper skill specs should validate with Codex's skill validator when available. The wrapper files intentionally avoid Claude-only frontmatter keys such as `user-invocable` and `disable-model-invocation`.

## Prerequisites for Plugin Users

Local machine:

- Claude Code or Codex with plugin support
- Git, for version control of Home Assistant configs
- hass-cli: `pip install homeassistant-cli`

Home Assistant:

- Git Pull add-on, which syncs configs from git repository
- Long-Lived Access Token for hass-cli authentication

Environment variables:

```bash
export HASS_SERVER="http://homeassistant.local:8123"
export HASS_TOKEN="your-long-lived-access-token"
```

Optional Codex/HA MCP integrations may use `HOMEASSISTANT_URL` and `HOMEASSISTANT_TOKEN`, but the shared skills still expect `HASS_SERVER` and `HASS_TOKEN` for `hass-cli` workflows.

Do not silently add or launch `ha-mcp` with a real long-lived Home Assistant token. Codex MCP stdio setup stores `HOMEASSISTANT_TOKEN` in the local Codex config when using `codex mcp add --env`; get explicit user approval for that storage. Safe smoke tests can use dummy credentials to verify `uvx ha-mcp@latest` starts.

## Key Skills

| Skill | Slash Command | Description |
|-------|---------------|-------------|
| ha-onboard | `/ha-onboard` | First-time setup wizard, connection, settings |
| ha-validate | `/ha-validate` | Check configuration for errors with evidence tables |
| ha-deploy | `/ha-deploy` | Deploy changes or rollback via git |
| ha-analyze | `/ha-analyze` | Analyze setup and suggest improvements |
| ha-naming | `/ha-naming` | Naming conventions, audit, rename planning |
| ha-apply-naming | `/ha-apply-naming` | Execute a naming plan (dry-run default) |
| ha-automations | (auto) | Create automations from descriptions |
| ha-scripts | (auto) | Create scripts from descriptions |
| ha-scenes | (auto) | Create scenes from descriptions |
| ha-devices | (auto) | Device knowledge + new device workflow |
| ha-config | (auto) | Configuration organization guidance |
| ha-lovelace | (auto) | Dashboard design + storage-mode operations |
| ha-jinja | (auto) | Jinja templating guidance |
| ha-troubleshooting | (auto) | Debugging and log analysis |
| ha-resolver | (agent) | Entity resolution, preloaded by agents |

## Key Files

Core wiring:

- `hooks/hooks.json` - Hook event-command mapping (SessionStart, PreToolUse, PostToolUse)
- `references/safety-invariants.md` - Canonical safety rules, referenced by all skills
- `skills/ha-resolver/SKILL.md` - Entity resolution, preloaded by agents and not user-invocable

Domain-specific references:

- `skills/ha-automations/references/intent-classifier.md` - Inactivity vs delay classification
- `skills/ha-naming/references/editor.md` - YAML AST editing procedures

Eval cases:

- `dev/testing/evals/capability/core-safety-contracts.json` - Safety contract checks
- `dev/testing/evals/regression/phase3-findings-regression.json` - Regression guards

## Development Notes

- Settings stored in `.claude/settings.local.json` (gitignored)
- Conventions stored in `.claude/ha.conventions.json` (user naming patterns)
- SessionStart async hook runs env check via bash (`HASS_TOKEN`, `HASS_SERVER`, `configuration.yaml`, settings) and writes breadcrumb files for agent discovery
- Codex SessionStart writes the same gitignored `.claude/ha-python.txt` and `.claude/ha-plugin-root.txt` breadcrumbs for compatibility with shared helper references
- PreToolUse Bash hook runs `env-guard.sh` for command safety checks
- PostToolUse Edit|Write hook reminds about `/ha-deploy` after config changes
- The plugin uses hass-cli for HA API operations, local Python helpers for registry/trace workflows, and git for configuration deployment
- `ha-apply-naming` uses `disable-model-invocation: true`; `ha-deploy` uses in-skill confirmation gates instead
- Codex wrappers must preserve `ha-apply-naming` as a manual-execution contract even though Codex does not consume `disable-model-invocation`

## hass-cli Gotchas

- `hass-cli raw ws` is broken on HA 2026.2+; use built-in `-o json` commands (`area list`, `entity list`, `device list`)
- `--no-headers` only works with `entity list`; not `state list`, `device list`, or `service list`
- State list domain count: `hass-cli state list | awk '$1 ~ /\./ {split($1, a, "."); print a[1]}' | sort | uniq -c | sort -rn`

## Known Environment Issues

### `python3: command not found` on Windows

Windows typically provides `python` or `py`, not `python3`. The Claude hook detects this automatically via `session-check.sh`; Codex hooks run through `codex/session_check.py` to avoid requiring Git Bash on Windows. If you see `python3` errors from hooks, check user-level hooks (`.claude/hooks.json`) or other plugins for hardcoded `python3` references.

## Releasing Updates

- Bump `version` in both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`; keep them in sync
- Update `CHANGELOG.md` with a summary of changes
- If renaming slash commands or changing install steps, add a Breaking Changes section to the changelog
- Merge to main; marketplace source URL points to the repo, auto-update pulls latest
