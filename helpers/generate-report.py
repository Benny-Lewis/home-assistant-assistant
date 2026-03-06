#!/usr/bin/env python3
"""Generate a markdown project report from repository sources."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_first_paragraph(readme_text: str) -> str:
    lines = readme_text.splitlines()
    in_intro = False
    intro_lines: list[str] = []

    for line in lines:
        if line.startswith("# "):
            in_intro = True
            continue

        if in_intro:
            if line.startswith("## "):
                break
            if line.strip() == "":
                if intro_lines:
                    break
                continue
            intro_lines.append(line.strip())

    return " ".join(intro_lines).strip()


def extract_skills_count(readme_text: str) -> int:
    skills_section = re.search(r"## Skills\n(.*?)(?:\n## |\Z)", readme_text, re.S)
    if not skills_section:
        return 0

    rows = [
        line
        for line in skills_section.group(1).splitlines()
        if line.strip().startswith("|") and "---" not in line
    ]

    # subtract header row
    return max(0, len(rows) - 1)


def extract_latest_release(changelog_text: str) -> tuple[str, list[str]]:
    version_match = re.search(r"^##\s+([^\n]+)", changelog_text, re.M)
    if not version_match:
        return "Unknown", []

    version = version_match.group(1).strip()
    section_match = re.search(rf"^##\s+{re.escape(version)}\n(.*?)(?:\n##\s+|\Z)", changelog_text, re.S | re.M)
    if not section_match:
        return version, []

    bullets = re.findall(r"^\s*-\s+(.*)$", section_match.group(1), re.M)
    return version, bullets[:5]


def get_recent_commits(limit: int = 5) -> list[str]:
    cmd = ["git", "log", f"-{limit}", "--date=short", "--pretty=format:%h | %ad | %s"]
    try:
        out = subprocess.check_output(cmd, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    if not out:
        return []
    return out.splitlines()


def build_report(repo_root: Path) -> str:
    readme_text = read_file(repo_root / "README.md")
    changelog_text = read_file(repo_root / "CHANGELOG.md")

    summary = extract_first_paragraph(readme_text)
    skill_count = extract_skills_count(readme_text)
    latest_version, latest_notes = extract_latest_release(changelog_text)
    commits = get_recent_commits(5)

    lines: list[str] = []
    lines.append("# Project Report")
    lines.append("")
    lines.append("## Summary")
    lines.append(summary or "Summary unavailable.")
    lines.append("")
    lines.append("## Status")
    lines.append(f"- Latest release in `CHANGELOG.md`: **{latest_version}**")
    lines.append(f"- Documented skills in `README.md`: **{skill_count}**")
    lines.append("")
    lines.append("## Usage")
    lines.append("- Install in Claude Code via `/plugin install home-assistant-assistant@plugins`.")
    lines.append("- Start onboarding with `/ha-onboard`.")
    lines.append("- Use skill commands such as `/ha-automations`, `/ha-validate`, and `/ha-deploy`.")
    lines.append("")
    lines.append("## Latest Work")

    if latest_notes:
        lines.append("### Changelog Highlights")
        for note in latest_notes:
            lines.append(f"- {note}")
        lines.append("")

    if commits:
        lines.append("### Recent Commits")
        for commit in commits:
            lines.append(f"- {commit}")
    else:
        lines.append("- No git history available.")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate project REPORT markdown")
    parser.add_argument("-o", "--output", type=Path, help="Write report to file instead of stdout")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    report = build_report(repo_root)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
