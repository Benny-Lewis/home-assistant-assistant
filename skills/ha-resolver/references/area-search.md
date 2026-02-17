# Area-Based Entity Search

Find all entities in a specific room or area using HA registries.

> **Why registries:** Entity-to-area assignment lives in the entity registry
> (direct `area_id`) or device registry (via `device_id`). State attributes
> are NOT authoritative for area membership.

## Step 0: Quick Method (Helper Script)

If the area-search helper is available, use it instead of the manual steps below.
It performs Steps 1–3 automatically (fetches all registries, cross-references
entity and device area assignments, groups by domain):

```bash
PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt 2>/dev/null)"
PY="$(cat .claude/ha-python.txt 2>/dev/null || command -v python3 || command -v python || command -v py)"
$PY "$PLUGIN_ROOT/helpers/area-search.py" search "<area_name>"
$PY "$PLUGIN_ROOT/helpers/area-search.py" search "<area_name>" --domain light
$PY "$PLUGIN_ROOT/helpers/area-search.py" list-areas
```

Breadcrumb files are written by the session startup hook. Python auto-detection
is the fallback if the breadcrumb is missing. If `$PLUGIN_ROOT` is empty,
proceed with the manual steps below.

## Step 1: List Areas

```bash
hass-cli -o json area list
```

Response fields per area: `area_id`, `name`, `floor_id`, `icon`, `aliases`, `picture`.

Match the user's query to an `area_id` or `name` (case-insensitive).

## Step 2: Get Entity Registry

```bash
hass-cli -o json entity list
```

Filter results where `area_id` matches the target area. Each entry includes:
- `entity_id` — the entity identifier
- `area_id` — direct area assignment (may be null)
- `device_id` — link to device registry (for fallback)
- `original_name` — name from the integration
- `disabled_by` — skip if not null (entity disabled)
- `hidden_by` — note if hidden

## Step 3: Device Registry Fallback

Entities without a direct `area_id` may inherit area from their device.

```bash
hass-cli -o json device list
```

For each entity with `area_id: null` but a non-null `device_id`:
1. Find the device in the device registry by `id`
2. Check if the device has an `area_id`
3. If yes, the entity belongs to that area (via device)

## Resolution Priority

| Priority | Source | Meaning |
|----------|--------|---------|
| 1 | Entity registry `area_id` | Directly assigned to area |
| 2 | Device registry `area_id` | Inherited from parent device |
| 3 | None | No area assigned |

## Step 4: Format Results

Group entities by domain for readability:

```markdown
## Entities in Kitchen (area_id: kitchen)

**Lights (3):**
- light.kitchen_ceiling — Kitchen Ceiling Light
- light.kitchen_counter — Kitchen Counter Lights
- light.kitchen_pendant — Kitchen Pendant

**Sensors (2):**
- sensor.kitchen_temperature — Kitchen Temperature
- binary_sensor.kitchen_motion — Kitchen Motion

**Switches (1):**
- switch.kitchen_coffee_maker — Coffee Maker
```

Include area source in evidence tables when relevant:

| Entity | Area Source | Notes |
|--------|-----------|-------|
| light.kitchen_ceiling | direct | Entity registry area_id |
| sensor.kitchen_temperature | device | Via device abc123 |
| switch.kitchen_outlet | none | No area assigned |

## Grep Fallback

When JSON commands are too slow or unavailable:

```bash
hass-cli state list | grep -i "kitchen"
```

This is less accurate — it matches entity_ids and descriptions containing the area name but misses entities with non-descriptive IDs (e.g., `sensor.lumi_abc123` assigned to kitchen via registry).

**Note degradation in evidence table:** "Area search: grep fallback (registry unavailable)"

## Multi-Area Search

To find entities across multiple areas (e.g., "all downstairs rooms"):

1. Get floor registry to find floor_id for "downstairs"
2. Get area registry, filter areas by `floor_id`
3. Run entity registry search for each matching area
4. Combine results

```bash
# Get areas with floor_id
hass-cli -o json area list

# Filter areas by floor_id, then search entities for each matching area
```
