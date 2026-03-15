#!/usr/bin/env python3
"""Repository documentation consistency checks.

Checks:
1) Internal markdown links resolve (including same-file and cross-file anchors).
2) Required docs files exist.
3) Safety invariant count references are consistent.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".git", "docs", "node_modules"}

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

REQUIRED_FILES = [
    Path("README.md"),
    Path("CLAUDE.md"),
    Path("COMPONENTS.md"),
    Path("references/safety-invariants.md"),
    Path("references/settings-schema.md"),
    Path("references/hass-cli.md"),
    Path("templates/templates.md"),
]

COUNT_FILES = [
    Path("README.md"),
    Path("CLAUDE.md"),
    Path("COMPONENTS.md"),
    Path("references/safety-invariants.md"),
]


def slugify_heading(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[`*_~]", "", text)
    text = re.sub(r"[^a-z0-9\-\s]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def markdown_files() -> Iterable[Path]:
    for path in ROOT.rglob("*.md"):
        rel_parts = set(path.relative_to(ROOT).parts)
        if rel_parts & EXCLUDE_DIRS:
            continue
        yield path


def collect_headings(path: Path) -> set[str]:
    anchors: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m = HEADING_RE.match(line)
        if m:
            anchors.add(slugify_heading(m.group(2)))
    return anchors


def validate_markdown_links(errors: list[str]) -> None:
    heading_cache: dict[Path, set[str]] = {}
    for md in markdown_files():
        text = md.read_text(encoding="utf-8")
        for idx, line in enumerate(text.splitlines(), start=1):
            for match in MARKDOWN_LINK_RE.finditer(line):
                raw_target = match.group(1)
                if raw_target.startswith(("http://", "https://", "mailto:")):
                    continue

                target = raw_target.split("?")[0]
                path_part, _, anchor = target.partition("#")

                if path_part == "":
                    target_file = md
                elif path_part.startswith("/"):
                    target_file = ROOT / path_part.lstrip("/")
                else:
                    target_file = (md.parent / path_part).resolve()

                if not target_file.exists():
                    rel_target = target_file.relative_to(ROOT) if target_file.is_relative_to(ROOT) else target_file
                    errors.append(
                        f"{md.relative_to(ROOT)}:{idx} broken link target '{raw_target}' (missing file: {rel_target})"
                    )
                    continue

                if anchor:
                    if target_file not in heading_cache:
                        heading_cache[target_file] = collect_headings(target_file)
                    if slugify_heading(anchor) not in heading_cache[target_file]:
                        errors.append(
                            f"{md.relative_to(ROOT)}:{idx} broken anchor in '{raw_target}' (anchor '{anchor}' not found)"
                        )


def validate_required_files(errors: list[str]) -> None:
    for req in REQUIRED_FILES:
        if not (ROOT / req).exists():
            errors.append(f"missing required file: {req}")

    skill_dirs = sorted((ROOT / "skills").glob("*"))
    if not skill_dirs:
        errors.append("no skill directories found under skills/")
    for skill_dir in skill_dirs:
        if skill_dir.is_dir() and not (skill_dir / "SKILL.md").exists():
            errors.append(f"missing required skill spec: {skill_dir.relative_to(ROOT) / 'SKILL.md'}")

    agent_files = sorted((ROOT / "agents").glob("*.md"))
    if not agent_files:
        errors.append("no agent docs found under agents/*.md")


def validate_invariant_count_consistency(errors: list[str]) -> None:
    canonical_path = ROOT / "references/safety-invariants.md"
    canonical = canonical_path.read_text(encoding="utf-8")

    # Derive the invariant count from the canonical source-of-truth document,
    # rather than hard-coding a stale value.
    expected_count = len(re.findall(r"^###\s+\d+\.\s", canonical, flags=re.MULTILINE))
    if expected_count == 0:
        errors.append("references/safety-invariants.md has no numbered invariant sections")
        return

    words = {
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five",
        6: "six",
        7: "seven",
        8: "eight",
        9: "nine",
        10: "ten",
    }
    count_word = words.get(expected_count)

    for rel_path in COUNT_FILES:
        content = (ROOT / rel_path).read_text(encoding="utf-8").lower()

        if rel_path == Path("references/safety-invariants.md"):
            if count_word and f"the {count_word} invariants" not in content:
                errors.append(f"{rel_path} should define 'The {count_word.title()} Invariants'")
            continue

        if count_word:
            has_count_phrase = (
                f"{count_word} safety invariants" in content
                or f"{expected_count} safety invariants" in content
                or f"{count_word} invariants" in content
                or f"{expected_count} invariants" in content
            )
            if not has_count_phrase:
                errors.append(f"{rel_path} should mention '{count_word} (safety) invariants' or '{expected_count} (safety) invariants'")

    # Defensive cross-check: ensure headings are sequentially numbered from 1..N.
    expected_sequence = [f"{i}." for i in range(1, expected_count + 1)]
    actual_sequence = re.findall(r"^###\s+(\d+\.)\s", canonical, flags=re.MULTILINE)
    if actual_sequence != expected_sequence:
        errors.append(
            "references/safety-invariants.md has non-sequential numbered invariant headings "
            f"(expected {expected_sequence}, found {actual_sequence})"
        )


def main() -> int:
    errors: list[str] = []
    validate_markdown_links(errors)
    validate_required_files(errors)
    validate_invariant_count_consistency(errors)

    if errors:
        print("docs-check: FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    print("docs-check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
