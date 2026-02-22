# ha-troubleshooting Enrichment Design

**Date:** 2026-02-17
**Phase:** 1 #3 (from MCP-TO-SKILLS-ANALYSIS.md)
**Scope:** History + Logbook + Trace API procedures
**Status:** Approved (updated after API verification)

## Goal

Enrich ha-troubleshooting from "here's advice" to "let me look at what actually happened" by adding diagnostic procedures for querying entity history, logbook events, and automation traces.

## Scope

**In scope:**
- History API (`/api/history/period`) — REST, verified working
- Logbook API (`/api/logbook`) — REST, verified working
- Trace API (`trace/list`, `trace/get`) — WebSocket only, requires Python helper

**Out of scope:**
- Statistics/long-term trends (deferred to ha-analyze enrichment)
- Deep search / entity reference search (covered by native Grep)
- Device control or service calls

## API Verification Results (2026-02-17)

| API | REST endpoint | WebSocket | hass-cli raw ws | Status |
|-----|---------------|-----------|-----------------|--------|
| History | `/api/history/period` works | N/A | N/A | REST ready |
| Logbook | `/api/logbook` works | Broken (raw ws) | Broken | REST ready |
| Trace | **404 — does not exist** | `trace/list`, `trace/get` | Broken | **Needs Python helper** |

**Key finding:** The existing SKILL.md's `hass-cli raw get /api/trace/automation.<name>` command returns 404 — it has never worked. Traces are WebSocket-only. Since `hass-cli raw ws` is broken on HA 2026.2+, we need a Python helper using the `websockets` library (already installed alongside hass-cli).

**ha-mcp reference:** ha-mcp uses Python's `websockets` library to call `trace/list` and `trace/get` directly. Key detail: traces are keyed by `unique_id` (not entity_id), so the helper must resolve via `config/entity_registry/get` first.

## Design Decisions

1. **New reference file** (`references/diagnostic-api.md`) — follows ha-resolver pattern
2. **New Python helper** (`helpers/trace-fetch.py`) — follows area-search.py pattern, uses `websockets` lib directly to bypass broken hass-cli raw ws
3. **Procedure-first organization** — organized by API endpoint
4. **Concise per Anthropic guidelines** — only document HA-specific details
5. **Fix existing broken command** — replace 404 trace REST command with helper invocation

## Files to Create/Change

### New: `helpers/trace-fetch.py` (~120-150 lines)
- WebSocket client using `websockets` library
- Commands: `list <automation_entity_id>`, `get <automation_entity_id> [run_id]`
- Resolves entity_id → unique_id via entity registry
- Uses HASS_SERVER and HASS_TOKEN env vars (same as hass-cli)
- Error handling: connection, auth, not found, no traces

### New: `skills/ha-troubleshooting/references/diagnostic-api.md` (~140-160 lines)
- TOC, History API, Logbook API, Trace API (via helper), When to Use Which

### Modified: `skills/ha-troubleshooting/SKILL.md` (~15-20 lines changed)
- Fix broken trace command → use trace-fetch.py helper
- Add logbook command to Quick Reference table
- Add step 3e (Logbook) to Process section
- Add logbook row to evidence table template
- Add reference link

### Modified: `skills/ha-troubleshooting/references/log-patterns.md` (~5-10 lines)
- Fix broken trace command → use helper
- Cross-reference diagnostic-api.md
- Add logbook row to evidence table

### Modified: `agents/ha-log-analyzer.md` (~5-10 lines)
- Fix broken trace command → use helper
- Add logbook command
- Reference diagnostic-api.md

## Design Principles

- **Low freedom** for command syntax (exact commands — they're fragile)
- **Medium freedom** for response interpretation (heuristics, Claude adapts)
- **Progressive disclosure** — SKILL.md is process overview, reference loads on demand
- **Consistent with siblings** — follows area-search.py and system-overview.md patterns
