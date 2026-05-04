#!/usr/bin/env python3
"""Validate skill frontmatter."""

from pathlib import Path
import runpy
import sys

sys.argv = [sys.argv[0], "--check", "frontmatter"]
runpy.run_path(str(Path(__file__).with_name("validate-repo.py")), run_name="__main__")
