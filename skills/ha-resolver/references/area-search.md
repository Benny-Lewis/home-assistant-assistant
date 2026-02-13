# Area-Based Entity Search

Find all entities in a specific room or area using HA registries.

> **Why registries:** Entity-to-area assignment lives in the entity registry
> (direct `area_id`) or device registry (via `device_id`). State attributes
> are NOT authoritative for area membership.

## Step 1: List Areas

**Quick:**
```bash
hass-cli area list
```

**Full details** (includes floor_id, aliases, icons):
```bash
MSYS_NO_PATHCONV=1 hass-cli raw ws '{"type":"config/area_registry/list"}'
```

Response fields per area: `area_id`, `name`, `floor_id`, `icon`, `aliases`, `picture`.

Match the user's query to an `area_id` or `name` (case-insensitive).

## Step 2: Get Entity Registry

```bash
MSYS_NO_PATHCONV=1 hass-cli raw ws '{"type":"config/entity_registry/list"}'
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
MSYS_NO_PATHCONV=1 hass-cli raw ws '{"type":"config/device_registry/list"}'
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

When WebSocket commands fail (e.g., hass-cli version doesn't support `raw ws`):

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
# Get floors
MSYS_NO_PATHCONV=1 hass-cli raw ws '{"type":"config/floor_registry/list"}'

# Then filter areas by floor_id from area registry results
```
