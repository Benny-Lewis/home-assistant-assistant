# ha-mcp Architecture Snapshot

Captured: 2026-02-21  
Analyst: Codex  
External repo path: `C:\Users\Ben\dev\ha-mcp`  
Origin: `https://github.com/homeassistant-ai/ha-mcp.git`  
Commit: `3dc098812a4dc7044c8883f57a9c2048297d3ee8`

## Scope

This snapshot captures architecture-relevant signals for possible Skills + MCP composition in the Home Assistant Assistant plugin review. It is not a full code audit.

## Key Architecture Signals

1. Skills and MCP are explicitly positioned as complementary:
- `README.md:146`
- `README.md:148`

2. Server design is lazy-initialized and modular:
- Core server class with lazy client/tool creation: `src/ha_mcp/server.py:42`
- FastMCP server construction: `src/ha_mcp/server.py:75`
- Registry + enhanced tool registration: `src/ha_mcp/server.py:121`, `src/ha_mcp/server.py:124`

3. Tool loading is auto-discovered and filterable:
- Filter env var: `src/ha_mcp/config.py:71`
- Registry discovery/filtering: `src/ha_mcp/tools/registry.py:4`, `src/ha_mcp/tools/registry.py:101`
- Module preset mechanism: `src/ha_mcp/tools/registry.py:35`

4. Tool semantics are annotated with MCP hints:
- Widespread `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` usage across tool modules.
- Annotation policy tests: `tests/src/unit/test_tool_annotations.py:81`

5. Tool surface governance exists (size constraint):
- Runtime/decorated tool count guard + consolidation pressure: `tests/src/unit/test_tool_annotations.py:126`

6. OAuth + transport strategy supports broad client compatibility:
- OAuth proxy for per-request credentials: `src/ha_mcp/__main__.py:19`
- OAuth mode entrypoint and base URL requirement: `src/ha_mcp/__main__.py:665`, `src/ha_mcp/__main__.py:673`
- OAuth metadata compatibility extensions (Claude.ai/ChatGPT): `src/ha_mcp/auth/provider.py:199`, `src/ha_mcp/auth/provider.py:258`

7. Operational telemetry and async status tracking are built in:
- Usage logger ring buffer + async persistence: `src/ha_mcp/utils/usage_logger.py:18`, `src/ha_mcp/utils/usage_logger.py:174`
- Device operation lifecycle manager: `src/ha_mcp/utils/operation_manager.py:65`

8. Test footprint includes architecture-quality checks:
- E2E harness documented: `tests/README.md:26`
- Protocol-level tool error signaling tests: `tests/src/unit/test_tool_error_signaling.py:1`
- Performance baseline tests: `tests/src/e2e/performance/test_performance_baselines.py:1`

## Candidate Reuse Areas (For Later Review Phase)

Potential high-value candidates to evaluate for selective adoption or interop:

1. Discovery + state tools:
- `tools_search.py`, `tools_entities.py`

2. Safe mutating flows with verification hints:
- `tools_service.py`, `tools_config_automations.py`, `tools_config_helpers.py`, `tools_config_scripts.py`

3. Dashboard/config orchestration:
- `tools_config_dashboards.py`, `tools_resources.py`

4. Registry/refactor primitives:
- `tools_registry.py`, `tools_areas.py`, `tools_labels.py`, `tools_groups.py`, `tools_zones.py`

5. Operability foundations:
- `errors.py`, `utils/usage_logger.py`, `utils/operation_manager.py`

## Integration Implication (Provisional)

Current evidence favors a hybrid model: keep Skills for decision quality and design intent, and use MCP for deterministic execution and system interaction breadth. The repository itself states this complement directly (`README.md:146`, `README.md:148`).
