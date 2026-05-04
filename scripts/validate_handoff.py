#!/usr/bin/env python3
"""Validate generated HANDOFF.md artifacts.

Usage:
  python3 scripts/validate_handoff.py HANDOFF.md [more/HANDOFF.md ...]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


MARKER_ENUMS = {
    "HANDOFF_SCHEMA_VERSION": {"1"},
    "HANDOFF_MODE": {"compact", "expanded", "prompt-only"},
    "DETAIL_ARTIFACTS_READY": {"yes", "no", "not-needed"},
    "NEW_SESSION_PROMPT_READY": {"yes", "no"},
    "DISK_STATE_RECORDED": {"yes", "no"},
    "VALIDATION_RECORDED": {"yes", "no"},
    "SECRET_REDACTION_CHECKED": {"yes", "no"},
    "SAFE_FOR_NEW_SESSION": {"yes", "no"},
}
REQUIRED_FIELDS = [
    "HANDOFF_READY",
    "HANDOFF_SCHEMA_VERSION",
    "HANDOFF_MODE",
    "DETAIL_ARTIFACTS_READY",
    "NEW_SESSION_PROMPT_READY",
    "DISK_STATE_RECORDED",
    "VALIDATION_RECORDED",
    "SECRET_REDACTION_CHECKED",
    "SAFE_FOR_NEW_SESSION",
    "BLOCKERS",
]
SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9_-]{20,}",
    r"ghp_[A-Za-z0-9_]{20,}",
    r"AKIA[0-9A-Z]{16}",
    r"-----BEGIN .*PRIVATE KEY",
    r"(?i)(api[_-]?key|token|password|secret)\s*=\s*['\"][^'\"]+['\"]",
]


def extract_marker_values(path: Path, text: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    pattern = re.compile(
        r"```text\n(HANDOFF_AUTOMATION_V1\n.*?END_HANDOFF_AUTOMATION_V1)\n```",
        re.DOTALL,
    )
    blocks = pattern.findall(text)
    if len(blocks) != 1:
        return {}, [f"{path}: expected exactly one HANDOFF_AUTOMATION_V1 block, found {len(blocks)}"]

    values: dict[str, str] = {}
    lines = blocks[0].splitlines()
    actual_keys = [line.split(":", 1)[0] if ":" in line else line for line in lines[1:-1]]
    if actual_keys != REQUIRED_FIELDS:
        errors.append(f"{path}: marker fields must appear exactly once in schema order")
    seen: set[str] = set()
    for line in lines[1:-1]:
        if ":" not in line:
            errors.append(f"{path}: invalid marker line {line!r}")
            continue
        key, value = line.split(":", 1)
        if key in seen:
            errors.append(f"{path}: duplicate marker {key}")
        if key not in REQUIRED_FIELDS:
            errors.append(f"{path}: unknown marker {key}")
        seen.add(key)
        values[key] = value.strip()
    return values, errors


def validate_handoff(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    values, marker_errors = extract_marker_values(path, text)
    errors.extend(marker_errors)
    if not values:
        return errors

    for field in REQUIRED_FIELDS:
        if field not in values:
            errors.append(f"{path}: missing marker {field}")
    for field, allowed in MARKER_ENUMS.items():
        value = values.get(field)
        if value is not None and value not in allowed:
            errors.append(f"{path}: marker {field} has invalid value {value!r}")

    if values.get("SAFE_FOR_NEW_SESSION") == "yes":
        for field in ["DISK_STATE_RECORDED", "VALIDATION_RECORDED", "SECRET_REDACTION_CHECKED"]:
            if values.get(field) != "yes":
                errors.append(f"{path}: SAFE_FOR_NEW_SESSION=yes requires {field}=yes")
        if values.get("BLOCKERS") != "none":
            errors.append(f"{path}: SAFE_FOR_NEW_SESSION=yes requires BLOCKERS=none")
    if values.get("SECRET_REDACTION_CHECKED") == "yes" and "Secret redaction check:" not in text:
        errors.append(f"{path}: SECRET_REDACTION_CHECKED=yes requires a Secret redaction check entry")

    mode = values.get("HANDOFF_MODE")
    details = values.get("DETAIL_ARTIFACTS_READY")
    if mode == "expanded":
        if details != "yes":
            errors.append(f"{path}: expanded mode requires DETAIL_ARTIFACTS_READY=yes")
        for rel in sorted(set(re.findall(r"`(details/[^`]+\.md)`", text))):
            if not (path.parent / rel).exists():
                errors.append(f"{path}: referenced detail artifact is missing: {rel}")
    elif mode in {"compact", "prompt-only"} and details != "not-needed":
        errors.append(f"{path}: {mode} mode requires DETAIL_ARTIFACTS_READY=not-needed")

    for field in ["- Goal:", "- Current state:", "- Next action:", "- Blocker:"]:
        if text.count(field) != 1:
            errors.append(f"{path}: expected exactly one TL;DR field {field}")
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, text):
            errors.append(f"{path}: possible unredacted secret matching {pattern}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoffs", nargs="+", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    for path in args.handoffs:
        if not path.exists():
            errors.append(f"{path}: file does not exist")
            continue
        errors.extend(validate_handoff(path))

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    for path in args.handoffs:
        print(f"ok: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
