#!/usr/bin/env python3
"""Collect exact Home Assistant overview metrics for /ha-analyze.

This helper is intentionally stdlib-only and degrades gracefully. It returns
JSON even when one or more live data sources are unavailable so the caller can
report "what ran vs skipped" without inventing counts.

Usage:
    python ha-overview.py snapshot
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def command_to_text(command: list[str]) -> str:
    return " ".join(command)


def unavailable_source(command: list[str], error: str) -> dict[str, Any]:
    return {
        "status": "unavailable",
        "command": command_to_text(command),
        "error": error,
    }


def run_json_command(command: list[str]) -> tuple[Any | None, dict[str, Any]]:
    env = os.environ.copy()
    env.setdefault("MSYS_NO_PATHCONV", "1")

    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
    except FileNotFoundError as exc:
        return None, unavailable_source(command, str(exc))

    source = {
        "status": "ok" if proc.returncode == 0 else "unavailable",
        "command": command_to_text(command),
        "returncode": proc.returncode,
    }

    if proc.stderr.strip():
        source["stderr"] = proc.stderr.strip()

    if proc.returncode != 0:
        if proc.stdout.strip():
            source["stdout"] = proc.stdout.strip()
        return None, source

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        source["status"] = "unavailable"
        source["error"] = f"invalid JSON: {exc}"
        return None, source

    if isinstance(data, list):
        source["item_count"] = len(data)
    return data, source


def read_automations_yaml(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    source = {
        "status": "ok",
        "file": str(path),
    }

    if not path.exists():
        source["status"] = "unavailable"
        source["error"] = "file not found"
        return {
            "automations": None,
            "automations_blank_description": None,
        }, source

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        source["status"] = "unavailable"
        source["error"] = str(exc)
        return {
            "automations": None,
            "automations_blank_description": None,
        }, source

    automation_count = len(re.findall(r"(?m)^- id:", text))
    blank_descriptions = len(re.findall(r"(?m)^\s+description:\s*''\s*$", text))
    source["item_count"] = automation_count

    return {
        "automations": automation_count,
        "automations_blank_description": blank_descriptions,
    }, source


def service_ids(services: list[dict[str, Any]], domain_name: str) -> list[str]:
    ids: list[str] = []
    for domain in services:
        if domain.get("domain") != domain_name:
            continue
        service_map = domain.get("services", {})
        for service_name in sorted(service_map):
            ids.append(f"{domain_name}.{service_name}")
    return ids


def count_domains(states: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter()
    for state in states:
        entity_id = state.get("entity_id", "")
        if "." not in entity_id:
            continue
        counts[entity_id.split(".", 1)[0]] += 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def snapshot() -> dict[str, Any]:
    hass_cli = shutil.which("hass-cli")
    areas_data: list[dict[str, Any]] | None = None
    devices_data: list[dict[str, Any]] | None = None
    entity_registry_data: list[dict[str, Any]] | None = None
    states_data: list[dict[str, Any]] | None = None
    services_data: list[dict[str, Any]] | None = None

    if hass_cli:
        areas_data, areas_source = run_json_command([hass_cli, "-o", "json", "area", "list"])
        devices_data, devices_source = run_json_command(
            [hass_cli, "-o", "json", "device", "list"]
        )
        entity_registry_data, entity_registry_source = run_json_command(
            [hass_cli, "-o", "json", "entity", "list"]
        )
        states_data, states_source = run_json_command(
            [hass_cli, "-o", "json", "raw", "get", "/api/states"]
        )
        services_data, services_source = run_json_command(
            [hass_cli, "-o", "json", "raw", "get", "/api/services"]
        )
    else:
        missing = "hass-cli not found in PATH"
        areas_source = unavailable_source(["hass-cli", "-o", "json", "area", "list"], missing)
        devices_source = unavailable_source(["hass-cli", "-o", "json", "device", "list"], missing)
        entity_registry_source = unavailable_source(
            ["hass-cli", "-o", "json", "entity", "list"], missing
        )
        states_source = unavailable_source(
            ["hass-cli", "-o", "json", "raw", "get", "/api/states"], missing
        )
        services_source = unavailable_source(
            ["hass-cli", "-o", "json", "raw", "get", "/api/services"], missing
        )

    automation_metrics, automations_source = read_automations_yaml(Path.cwd() / "automations.yaml")

    person_entities: list[str] = []
    notify_service_ids: list[str] = []
    unavailable_entities: list[str] = []
    unavailable_device_trackers: list[str] = []
    domain_counts: dict[str, int] | None = None

    if isinstance(states_data, list):
        person_entities = sorted(
            state["entity_id"]
            for state in states_data
            if isinstance(state, dict) and str(state.get("entity_id", "")).startswith("person.")
        )
        unavailable_entities = sorted(
            state["entity_id"]
            for state in states_data
            if isinstance(state, dict) and state.get("state") == "unavailable"
        )
        unavailable_device_trackers = sorted(
            entity_id for entity_id in unavailable_entities if entity_id.startswith("device_tracker.")
        )
        domain_counts = count_domains(states_data)

    if isinstance(services_data, list):
        notify_service_ids = service_ids(services_data, "notify")

    metrics = {
        "areas": len(areas_data) if isinstance(areas_data, list) else None,
        "devices": len(devices_data) if isinstance(devices_data, list) else None,
        "entity_registry_entries": (
            len(entity_registry_data) if isinstance(entity_registry_data, list) else None
        ),
        "entities": len(states_data) if isinstance(states_data, list) else None,
        "unavailable_entities": len(unavailable_entities) if isinstance(states_data, list) else None,
        "device_trackers": (
            domain_counts.get("device_tracker", 0) if isinstance(domain_counts, dict) else None
        ),
        "unavailable_device_trackers": (
            len(unavailable_device_trackers) if isinstance(states_data, list) else None
        ),
        "person_entities": len(person_entities) if isinstance(states_data, list) else None,
        "notify_services": len(notify_service_ids) if isinstance(services_data, list) else None,
        "automations": automation_metrics["automations"],
        "automations_blank_description": automation_metrics["automations_blank_description"],
        "domains": domain_counts,
    }

    return {
        "generated_at": utc_now_iso(),
        "cwd": str(Path.cwd()),
        "metrics": metrics,
        "details": {
            "person_entity_ids": person_entities,
            "notify_service_ids": notify_service_ids,
            "unavailable_entity_ids_sample": unavailable_entities[:25],
            "unavailable_device_tracker_ids_sample": unavailable_device_trackers[:25],
        },
        "sources": {
            "areas": areas_source,
            "devices": devices_source,
            "entity_registry": entity_registry_source,
            "states": states_source,
            "services": services_source,
            "automations_yaml": automations_source,
        },
    }


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] != "snapshot":
        print(__doc__)
        sys.exit(1)

    print(json.dumps(snapshot(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
