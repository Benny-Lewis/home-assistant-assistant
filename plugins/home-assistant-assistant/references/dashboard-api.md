# Storage Dashboard WebSocket API Contract

Reference for storage-mode Lovelace dashboard operations via the Home Assistant WebSocket API.

> This is a pure reference document. For operational workflows, see `skills/ha-lovelace/SKILL.md`.

## WebSocket Commands

| Command | Purpose | Success Response | Failure Response |
|---------|---------|-----------------|-----------------|
| `lovelace/config` | Fetch dashboard config | `{success: true, result: {views: [...]}}` | `{success: false, error: {code, message}}` |
| `lovelace/config/save` | Save dashboard config | `{success: true, result: null}` | `{success: false, error: {code, message}}` |
| `lovelace/dashboards/list` | List all storage dashboards | `{success: true, result: [...]}` | -- |

## Key Fields

- **`url_path`**: Identifies the target dashboard. Omit or use `"lovelace"` for the default dashboard.
- **`force: true`**: On fetch commands, bypasses HA's config cache to get current state. Always use this after saves.

## Critical: Save Response Contract

A successful `lovelace/config/save` returns:

```json
{"id": 1, "type": "result", "success": true, "result": null}
```

**`result: null` is correct** — it is NOT an error. This is the expected success response.

A failed save returns:

```json
{"id": 1, "type": "result", "success": false, "error": {"code": 3, "message": "..."}}
```

The `error` object contains:
- `code` (integer): Error code (e.g., 3 for invalid config)
- `message` (string): Human-readable error description

## Dashboard Identity

- **`url_path`**: URL-facing identifier used in dashboard URLs (e.g., `/lovelace/my-dashboard`)
- **`dashboard_id`**: Internal identifier returned on dashboard creation
- New dashboard `url_path` values must be valid slugs: lowercase, alphanumeric, hyphens, and underscores. Convention: use hyphens for readability (e.g., `my-dashboard`).
- `"lovelace"` and `"default"` both target the built-in default dashboard.

## Fetch Example

```json
{"id": 1, "type": "lovelace/config", "url_path": "my-dashboard", "force": true}
```

Response:
```json
{
  "id": 1,
  "type": "result",
  "success": true,
  "result": {
    "views": [
      {
        "title": "Overview",
        "path": "home",
        "type": "sections",
        "sections": [...]
      }
    ]
  }
}
```

## Save Example

```json
{"id": 2, "type": "lovelace/config/save", "url_path": "my-dashboard", "config": {"views": [...]}}
```

Response (success):
```json
{"id": 2, "type": "result", "success": true, "result": null}
```

## Helper

The plugin provides `helpers/lovelace-dashboard.py` for programmatic dashboard operations with built-in save verification. See the helper's docstring for usage.
