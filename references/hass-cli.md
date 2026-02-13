# hass-cli Reference

> Verified against hass-cli 0.9.6

## Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `hass-cli entity list` | List all entities | `hass-cli entity list` |
| `hass-cli state get <entity>` | Get state of one entity | `hass-cli state get light.living_room` |
| `hass-cli state list` | List all entity states | `hass-cli state list` |
| `hass-cli service list` | List available services | `hass-cli service list` |
| `hass-cli service call <service>` | Call a service | `hass-cli service call light.turn_on --arguments entity_id=light.living_room` |
| `hass-cli area list` | List all areas | `hass-cli area list` |
| `hass-cli device list` | List all devices | `hass-cli device list` |
| `hass-cli raw get <path>` | Raw API GET | `hass-cli raw get /api/states` |
| `hass-cli raw post <path>` | Raw API POST | `hass-cli raw post /api/services/light/turn_on` |
| `hass-cli raw ws '<json>'` | WebSocket message | `hass-cli raw ws '{"type":"config/area_registry/list"}'` |
| `hass-cli config check` | Validate HA config | `hass-cli config check` |
| `hass-cli entity rename <old> <new>` | Rename an entity | `hass-cli entity rename light.old light.new` |

## Supported Flags

| Flag | Description |
|------|-------------|
| `-o json` / `-o yaml` / `-o table` | Output format (short flag only: `-o json`, not `--output json`) |
| `--no-headers` | Suppress column headers in tabular output |
| `--columns <cols>` | Select specific columns (comma-separated) |

### JSON Output for Full Attributes

Default tabular output only shows entity, description, state, and changed columns. Use `-o json` to get full attributes including `supported_features`, `supported_color_modes`, etc.:

```bash
hass-cli -o json state get light.living_room
```

> **Note:** Use the short flag `-o json`, not `--output json` (long form may not work in all versions).

## MINGW / Git Bash Note

On Windows with MINGW64 (Git Bash), paths starting with `/` get mangled by MSYS path conversion. For `hass-cli raw` commands, prefix with:

```bash
MSYS_NO_PATHCONV=1 hass-cli raw get /api/states
```

This is **not** needed for non-path commands like `entity list`, `state get`, etc.

## WebSocket Commands

`hass-cli raw ws` sends a WebSocket message and returns the response as JSON.

```bash
# Area registry
MSYS_NO_PATHCONV=1 hass-cli raw ws '{"type":"config/area_registry/list"}'

# Entity registry (includes area_id, device_id, disabled_by per entity)
MSYS_NO_PATHCONV=1 hass-cli raw ws '{"type":"config/entity_registry/list"}'

# Device registry (includes area_id, manufacturer, model per device)
MSYS_NO_PATHCONV=1 hass-cli raw ws '{"type":"config/device_registry/list"}'

# Floor registry
MSYS_NO_PATHCONV=1 hass-cli raw ws '{"type":"config/floor_registry/list"}'
```

**Response format:** JSON with `success: true/false` and `result: [...]` array.

**MINGW note:** Always use `MSYS_NO_PATHCONV=1` prefix for `raw ws` commands on Windows — the JSON payload may be misinterpreted.

### Common Registry Message Types

| Type | Returns |
|------|---------|
| `config/area_registry/list` | Areas with `area_id`, `name`, `floor_id`, `icon`, `aliases` |
| `config/entity_registry/list` | Entities with `entity_id`, `area_id`, `device_id`, `disabled_by`, `hidden_by` |
| `config/device_registry/list` | Devices with `id`, `area_id`, `name`, `manufacturer`, `model` |
| `config/floor_registry/list` | Floors with `floor_id`, `name`, `level`, `aliases` |

## Parsing Tabular Output

hass-cli outputs plain text tables. Use standard CLI tools to extract data:

```bash
# Count entities
hass-cli entity list | wc -l

# Filter by domain
hass-cli entity list | grep "^light\."

# Get specific columns
hass-cli entity list --no-headers --columns entity_id,state

# Find entities in a specific state
hass-cli state list | grep "unavailable"

# Count entities by domain
hass-cli entity list --no-headers | awk -F'.' '{print $1}' | sort | uniq -c | sort -rn
```

## Common Pitfalls

1. **JSON output** — Use `-o json` (short flag) for full attributes. The long flag `--output json` may not work.
2. **MINGW path mangling** — Use `MSYS_NO_PATHCONV=1` for `raw get/post` commands.
3. **Service call arguments** — Use `--arguments` flag with key=value pairs.
4. **Entity rename** — Only changes the registry ID, not the device itself.
5. **Rate limiting** — Avoid rapid-fire calls in loops; batch where possible.

## Performance Notes

`entity list` can be slow on large setups (>500 entities). For bulk entity inventory:
- Use `state list` + grep for faster results (state list streams output, entity list buffers)
- Use Bash tool's `timeout` parameter (e.g., 60000ms) for entity list on large setups
- For domain-specific queries, always pipe through grep: `hass-cli state list | grep "^light\."`
