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
