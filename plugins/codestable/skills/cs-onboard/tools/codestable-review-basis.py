#!/usr/bin/env python3
"""Compute canonical CodeStable review provenance digests.

`cs-code-review` uses this helper to fill a passing review report's
``task_generation_sha256`` and ``review_basis_sha256`` frontmatter fields.
Both digests are machine-derived so the review gate can detect a review that
was written against a different Task generation or a stale implementation
worktree. The digests must never be hand-authored.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1":
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.execvpe(sys.executable, [sys.executable, *sys.argv], os.environ)
sys.dont_write_bytecode = True

from codestable_common import (
    review_basis_sha256,
    task_generation_sha256,
    unit_slug,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compute review provenance digests")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument(
        "--unit",
        required=True,
        help="Unit directory relative to the repository root, e.g. .codestable/features/2026-07-17-slug",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    root = Path(arguments.root).resolve()
    unit_dir = Path(arguments.unit)
    if unit_dir.is_absolute():
        unit_dir = unit_dir.resolve()
    else:
        unit_dir = (root / unit_dir).resolve()

    try:
        unit_dir.relative_to(root)
    except ValueError:
        print(json.dumps({"ok": False, "error": "unit directory escapes the repository root"}, indent=2))
        return 1

    slug = unit_slug(unit_dir)
    review_path = unit_dir / f"{slug}-review.md"
    generation_digest = task_generation_sha256(root, slug)
    if generation_digest is None:
        print(
            json.dumps(
                {"ok": False, "error": f"no valid active Task generation for {slug}"},
                indent=2,
            )
        )
        return 1

    payload = {
        "ok": True,
        "unit": unit_dir.relative_to(root).as_posix(),
        "task": slug,
        "task_generation_sha256": generation_digest,
        "review_basis_sha256": review_basis_sha256(root, review_path),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
