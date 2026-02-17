#!/usr/bin/env python3
"""Area-based entity search for Home Assistant.

Uses hass-cli built-in commands with -o json to cross-reference entity, device,
and area registries. No external dependencies beyond stdlib.

Usage:
    python area-search.py list-areas
    python area-search.py search <area_name>
    python area-search.py search <area_name> --domain light
"""

import json
import os
import subprocess
import sys


def hass_cli_json(*args):
    """Call hass-cli with -o json and return parsed JSON list."""
    try:
        result = subprocess.run(
            ["hass-cli", "-o", "json", *args],
            capture_output=True, text=True, timeout=60,
        )
    except FileNotFoundError:
        print("Error: hass-cli not found. Install: pip install homeassistant-cli")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"Error: Timed out. Server: {os.environ.get('HASS_SERVER', '(not set)')}")
        sys.exit(1)

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "HASS_SERVER" in stderr or "HASS_TOKEN" in stderr:
            print("Error: HASS_SERVER or HASS_TOKEN not set. Run /ha-onboard to configure.")
        else:
            print(f"Error: hass-cli failed: {stderr or 'unknown error'}")
        sys.exit(1)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Error: Could not parse hass-cli output as JSON.")
        sys.exit(1)


def area_matches(area_id, area_name, query):
    """Case-insensitive substring match in both directions."""
    q = query.lower()
    aid = (area_id or "").lower()
    aname = (area_name or "").lower()
    return q in aid or q in aname or aid in q or aname in q


def cmd_list_areas():
    """List all areas."""
    areas = hass_cli_json("area", "list")
    if not areas:
        print("No areas found.")
        return
    print(f"Areas ({len(areas)}):")
    for a in sorted(areas, key=lambda x: x.get("name", "")):
        aid = a.get("area_id", "?")
        name = a.get("name", "?")
        print(f"  {aid} — {name}")


def cmd_search(query, domain_filter=None):
    """Search for entities in an area, optionally filtered by domain."""
    # Fetch all three registries via hass-cli built-in commands
    areas = hass_cli_json("area", "list")
    entities = hass_cli_json("entity", "list")
    devices = hass_cli_json("device", "list")

    # Build area lookup: {area_id: area_name}
    area_names = {}
    for a in areas:
        area_names[a.get("area_id", "")] = a.get("name", "")

    # Find matching area(s)
    matched_areas = {}
    for aid, aname in area_names.items():
        if area_matches(aid, aname, query):
            matched_areas[aid] = aname

    if not matched_areas:
        print(f'No area matching "{query}" found.\n')
        print("Available areas:")
        for aid in sorted(area_names):
            print(f"  {aid} — {area_names[aid]}")
        return

    # Build device-to-area map: {device_id: area_id}
    device_area_map = {}
    for d in devices:
        did = d.get("id", "")
        darea = d.get("area_id")
        if did and darea:
            device_area_map[did] = darea

    # Resolve entities to areas and collect matches
    for target_aid, target_name in sorted(matched_areas.items()):
        results = {}  # {domain: [(entity_id, name, source)]}

        for ent in entities:
            # Skip disabled entities
            if ent.get("disabled_by"):
                continue

            eid = ent.get("entity_id", "")
            ent_area = ent.get("area_id")
            dev_id = ent.get("device_id")

            # Resolve area: entity direct > device fallback
            if ent_area:
                resolved_area = ent_area
                source = "direct"
            elif dev_id and dev_id in device_area_map:
                resolved_area = device_area_map[dev_id]
                source = "via device"
            else:
                continue

            if resolved_area != target_aid:
                continue

            # Domain filter
            domain = eid.split(".")[0] if "." in eid else ""
            if domain_filter and domain != domain_filter:
                continue

            name = ent.get("name") or ent.get("original_name") or eid
            results.setdefault(domain, []).append((eid, name, source))

        # Output
        print(f"## Entities in {target_name} (area_id: {target_aid})\n")

        if not results:
            filter_note = f' (domain: {domain_filter})' if domain_filter else ""
            print(f'No entities found in "{target_name}"{filter_note}.')
            continue

        total = 0
        for domain in sorted(results):
            items = sorted(results[domain])
            total += len(items)
            print(f"{domain} ({len(items)}):")
            for eid, name, source in items:
                print(f"  {eid} — {name} [{source}]")
            print()

        print(f"Total: {total} entities in {len(results)} domains")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  area-search.py list-areas")
        print("  area-search.py search <area_name>")
        print("  area-search.py search <area_name> --domain <domain>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list-areas":
        cmd_list_areas()
    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: search requires an area name.")
            print("Usage: area-search.py search <area_name> [--domain <domain>]")
            sys.exit(1)
        query = sys.argv[2]
        domain_filter = None
        if "--domain" in sys.argv:
            idx = sys.argv.index("--domain")
            if idx + 1 < len(sys.argv):
                domain_filter = sys.argv[idx + 1]
        cmd_search(query, domain_filter)
    else:
        print(f'Unknown command: "{command}"')
        print("Commands: list-areas, search")
        sys.exit(1)


if __name__ == "__main__":
    main()
