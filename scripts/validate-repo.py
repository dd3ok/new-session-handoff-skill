#!/usr/bin/env python3
"""Validate the handoff skill repository contract."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "new-session-handoff"
EXPECTED_MARKER_LINES = [
    "HANDOFF_AUTOMATION_V1",
    "HANDOFF_READY: <absolute path or not-written>",
    "HANDOFF_SCHEMA_VERSION: 1",
    "HANDOFF_MODE: compact|expanded|prompt-only",
    "DETAIL_ARTIFACTS_READY: yes|no|not-needed",
    "NEW_SESSION_PROMPT_READY: yes|no",
    "DISK_STATE_RECORDED: yes|no",
    "VALIDATION_RECORDED: yes|no",
    "SECRET_REDACTION_CHECKED: yes|no",
    "SAFE_FOR_NEW_SESSION: yes|no",
    "BLOCKERS: none|<short reason>",
    "END_HANDOFF_AUTOMATION_V1",
]
HANDOFF_FILES = [
    SKILL_DIR / "references" / "handoff-template.md",
    ROOT / "examples" / "HANDOFF.filled.example.md",
    ROOT / "examples" / "compact-bugfix" / "HANDOFF.md",
    ROOT / "examples" / "expanded-architecture" / "HANDOFF.md",
    ROOT / "examples" / "unsafe-handoff" / "HANDOFF.md",
]
DETAIL_TEMPLATES = [
    "detail-architecture-template.md",
    "detail-changed-files-template.md",
    "detail-validation-template.md",
    "detail-open-questions-template.md",
    "detail-pitfalls-template.md",
]
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
TRUST_ORDER_LINES = [
    "1. Current explicit user instruction in this session.",
    "2. Current working tree and Git state.",
    "3. Repository instruction files such as AGENTS.md, CLAUDE.md, GEMINI.md, PLAN.md.",
    "4. HANDOFF.md.",
    "5. Focused detail artifacts referenced by HANDOFF.md.",
    "6. Prior chat history only if explicitly provided by the user.",
]


class Validator:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def fail(self, message: str) -> None:
        self.errors.append(message)

    def require_exists(self, path: Path) -> None:
        if not path.exists():
            self.fail(f"missing required path: {path.relative_to(ROOT)}")

    def read(self, path: Path) -> str:
        self.require_exists(path)
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def validate_frontmatter(self) -> None:
        path = SKILL_DIR / "SKILL.md"
        text = self.read(path)
        lines = text.splitlines()
        if len(lines) < 4 or lines[0] != "---":
            self.fail("SKILL.md must start with YAML frontmatter delimiter")
            return
        try:
            end = lines[1:].index("---") + 1
        except ValueError:
            self.fail("SKILL.md frontmatter closing delimiter is missing")
            return

        frontmatter = lines[1:end]
        data: dict[str, str] = {}
        for line in frontmatter:
            if ":" not in line:
                self.fail(f"invalid frontmatter line: {line}")
                continue
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')

        name = data.get("name", "")
        description = data.get("description", "")
        if set(data) != {"name", "description"}:
            self.fail("SKILL.md frontmatter must contain only name and description")
        if name != SKILL_DIR.name:
            self.fail(f"frontmatter name must match skill directory: {name!r}")
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?", name):
            self.fail(f"frontmatter name has invalid format: {name!r}")
        if not description:
            self.fail("frontmatter description is required")
        if len(description) > 1024:
            self.fail("frontmatter description exceeds 1024 characters")
        lower_description = description.lower()
        if "explicit" not in lower_description:
            self.fail("frontmatter description must limit use to explicit user requests")
        if "/new" not in lower_description or "pty" not in lower_description:
            self.fail("frontmatter description must state the session-control boundary")
        body = "\n".join(lines[end + 1 :])
        if not body.strip().startswith("# New Session Handoff"):
            self.fail("SKILL.md body should start with '# New Session Handoff'")

    def validate_references(self) -> None:
        skill_text = self.read(SKILL_DIR / "SKILL.md")
        for ref in sorted(set(re.findall(r"`(references/[^`]+)`", skill_text))):
            self.require_exists(SKILL_DIR / ref)
        for name in DETAIL_TEMPLATES:
            self.require_exists(SKILL_DIR / "references" / name)
        self.require_exists(SKILL_DIR / "schemas" / "handoff-automation-v1.schema.json")
        openai_yaml = self.read(SKILL_DIR / "agents" / "openai.yaml")
        if "allow_implicit_invocation" in openai_yaml:
            self.fail("agents/openai.yaml must not use unvalidated allow_implicit_invocation policy")
        if "NEW_SESSION_PROMPT.txt" not in skill_text:
            self.fail("SKILL.md must name NEW_SESSION_PROMPT.txt as the canonical prompt file")

    def extract_marker_block(self, text: str, path: Path) -> list[str] | None:
        pattern = re.compile(
            r"```text\n(HANDOFF_AUTOMATION_V1\n.*?END_HANDOFF_AUTOMATION_V1)\n```",
            re.DOTALL,
        )
        blocks = pattern.findall(text)
        if len(blocks) != 1:
            self.fail(
                f"{path.relative_to(ROOT)} must contain exactly one automation marker block, found {len(blocks)}"
            )
            return None
        return blocks[0].splitlines()

    def validate_marker_blocks(self) -> None:
        for path in HANDOFF_FILES:
            text = self.read(path)
            block = self.extract_marker_block(text, path)
            if block is None:
                continue
            actual_names = [line.split(":", 1)[0] for line in block]
            expected_names = [line.split(":", 1)[0] for line in EXPECTED_MARKER_LINES]
            if actual_names != expected_names:
                self.fail(f"{path.relative_to(ROOT)} marker block does not match expected field order")
            self.validate_marker_values(path, block)

        for path in [
            SKILL_DIR / "SKILL.md",
            SKILL_DIR / "references" / "marker-semantics.md",
            SKILL_DIR / "references" / "quality-checklist.md",
            ROOT / "README.md",
        ]:
            text = self.read(path)
            for marker in [line.split(":", 1)[0] for line in EXPECTED_MARKER_LINES[1:-1]]:
                if marker not in text:
                    self.fail(f"{path.relative_to(ROOT)} missing marker name {marker}")

    def validate_marker_values(self, path: Path, block: list[str]) -> None:
        values: dict[str, str] = {}
        for line in block:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            values[key] = value.strip()
        if any("<" in value or "|" in value for value in values.values()):
            if "references/handoff-template.md" not in path.as_posix():
                self.fail(f"{path.relative_to(ROOT)} marker block contains placeholder values")
            return
        for key, allowed in MARKER_ENUMS.items():
            value = values.get(key, "")
            if value not in allowed:
                self.fail(f"{path.relative_to(ROOT)} marker {key} has invalid value {value!r}")
        if values.get("SAFE_FOR_NEW_SESSION") == "yes":
            for key in ["DISK_STATE_RECORDED", "VALIDATION_RECORDED", "SECRET_REDACTION_CHECKED"]:
                if values.get(key) != "yes":
                    self.fail(f"{path.relative_to(ROOT)} SAFE_FOR_NEW_SESSION=yes requires {key}=yes")
            if values.get("BLOCKERS") != "none":
                self.fail(f"{path.relative_to(ROOT)} SAFE_FOR_NEW_SESSION=yes requires BLOCKERS=none")
            mode = values.get("HANDOFF_MODE")
            detail_state = values.get("DETAIL_ARTIFACTS_READY")
            if mode == "expanded" and detail_state != "yes":
                self.fail(f"{path.relative_to(ROOT)} expanded handoff requires DETAIL_ARTIFACTS_READY=yes")
            if mode in {"compact", "prompt-only"} and detail_state != "not-needed":
                self.fail(f"{path.relative_to(ROOT)} {mode} handoff requires DETAIL_ARTIFACTS_READY=not-needed")

    def validate_handoff_sections(self) -> None:
        required_sections = [
            "## TL;DR / Operational Summary",
            "## Recovery Contract",
            "## Session Target",
            "## Repo Snapshot",
            "## Required Reading",
            "## Change Manifest",
            "## Validation Manifest",
            "## Remaining Work",
            "## Fresh Session Prompt",
            "## Automation Markers",
        ]
        tldr_fields = ["- Goal:", "- Current state:", "- Next action:", "- Blocker:"]
        for path in HANDOFF_FILES:
            text = self.read(path)
            for section in required_sections:
                if section not in text:
                    self.fail(f"{path.relative_to(ROOT)} missing section {section}")
            for field in tldr_fields:
                if text.count(field) != 1:
                    self.fail(f"{path.relative_to(ROOT)} must contain exactly one TL;DR field {field}")
            if "Expected drift from captured state:" not in text:
                self.fail(f"{path.relative_to(ROOT)} missing expected drift field")
            if (
                "If disk state differs" not in text
                and "If the handoff conflicts" not in text
                and "Trust order: disk/current working tree" not in text
                and "Current working tree and Git state" not in text
            ):
                self.fail(f"{path.relative_to(ROOT)} must state disk-conflict handling")
            if "SECRET_REDACTION_CHECKED: yes" in text and "Secret redaction check:" not in text:
                self.fail(f"{path.relative_to(ROOT)} records secret check yes without a check method")
        template = self.read(SKILL_DIR / "references" / "handoff-template.md")
        for line in TRUST_ORDER_LINES:
            if line not in template:
                self.fail(f"handoff-template.md missing trust order line: {line}")

    def validate_expanded_artifacts(self) -> None:
        handoff = ROOT / "examples" / "expanded-architecture" / "HANDOFF.md"
        text = self.read(handoff)
        for rel in sorted(set(re.findall(r"`(details/[^`]+\.md)`", text))):
            self.require_exists(handoff.parent / rel)

    def validate_secret_hygiene(self) -> None:
        secret_patterns = [
            r"sk-[A-Za-z0-9_-]{20,}",
            r"ghp_[A-Za-z0-9_]{20,}",
            r"(?i)(api[_-]?key|token|password|secret)\s*=\s*['\"][^'\"]+['\"]",
        ]
        checked_roots = [
            ROOT / "README.md",
            ROOT / "SECURITY.md",
            ROOT / "examples",
            SKILL_DIR,
        ]
        for base in checked_roots:
            paths = [base] if base.is_file() else sorted(base.rglob("*"))
            for path in paths:
                if not path.is_file() or path.suffix not in {".md", ".txt", ".yaml"}:
                    continue
                text = path.read_text(encoding="utf-8")
                for pattern in secret_patterns:
                    if re.search(pattern, text):
                        self.fail(f"possible secret in {path.relative_to(ROOT)}")

    def run(self, checks: set[str]) -> int:
        all_checks = {
            "frontmatter": self.validate_frontmatter,
            "references": self.validate_references,
            "markers": self.validate_marker_blocks,
            "examples": self.validate_handoff_sections,
            "expanded": self.validate_expanded_artifacts,
            "secrets": self.validate_secret_hygiene,
        }
        selected = all_checks if "all" in checks else {k: v for k, v in all_checks.items() if k in checks}
        unknown = checks - set(all_checks) - {"all"}
        for check in sorted(unknown):
            self.fail(f"unknown check: {check}")
        for check, fn in selected.items():
            before = len(self.errors)
            fn()
            if len(self.errors) == before:
                print(f"ok: {check}")
        if self.errors:
            for error in self.errors:
                print(f"error: {error}", file=sys.stderr)
            return 1
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="append",
        default=[],
        help="Check to run: frontmatter, references, markers, examples, expanded, secrets, all",
    )
    args = parser.parse_args()
    checks = set(args.check or ["all"])
    return Validator().run(checks)


if __name__ == "__main__":
    raise SystemExit(main())
