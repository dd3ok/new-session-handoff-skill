#!/usr/bin/env python3
"""Compatibility wrapper for the portable handoff validator."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = ROOT / "skills" / "new-session-handoff" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))

from validate_handoff import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
