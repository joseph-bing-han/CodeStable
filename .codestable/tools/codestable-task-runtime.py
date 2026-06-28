#!/usr/bin/env python3
"""Run the repository's canonical CodeStable Task runtime."""

from __future__ import annotations

import runpy
from pathlib import Path


repository_root = Path(__file__).resolve().parents[2]
runtime_path = (
    repository_root
    / "plugins/codestable/skills/cs-onboard/tools/codestable-task-runtime.py"
)
runpy.run_path(str(runtime_path), run_name="__main__")
