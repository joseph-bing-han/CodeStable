#!/usr/bin/env python3
"""Report CodeStable lifecycle state without mutating the repository."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from codestable_common import (
    Finding,
    bucket_paths,
    current_branch,
    default_branch,
    git_status,
    is_implementation_path,
    iter_units,
    missing_review_findings,
    scan_backlog,
)
from codestable_runtime import runtime_health


def diagnose(root: Path) -> dict[str, object]:
    root = root.resolve()
    changed = git_status(root)
    changed_paths = [item.path for item in changed]
    implementation_changes = [path for path in changed_paths if is_implementation_path(path)]
    units = iter_units(root)
    review_findings = missing_review_findings(root, units)
    backlog = scan_backlog(root)
    runtime = runtime_health(root, source_skill_dir=Path(__file__).resolve().parents[1])
    branch = current_branch(root)
    default = default_branch(root)

    findings: list[Finding] = []
    if not runtime["ok"]:
        if runtime["status"] in {"not-onboarded", "onboard-incomplete"}:
            message = "CodeStable onboarding is incomplete; run `cs-onboard`."
        elif runtime["status"] == "unsafe-runtime-root":
            message = "CodeStable runtime root is a symlink; replace it with a real repository directory before sync."
        else:
            message = "CodeStable runtime assets are incomplete or stale; run runtime sync."
        findings.append(
            Finding(
                severity="P1",
                message=message,
                path=", ".join([*runtime["missing"], *runtime.get("drifted_paths", [])]),
            )
        )
    findings.extend(review_findings)
    if backlog:
        findings.append(
            Finding(
                severity="P2",
                message="CodeStable backlog contains human-review or follow-up items.",
            )
        )

    if any(finding.severity == "P1" for finding in findings):
        status = "blocked"
        next_action = "Resolve P1 findings before reporting the task complete."
    elif implementation_changes:
        status = "implementation-active"
        next_action = "Complete the implementation batch, then run the CodeStable review gate."
    elif changed_paths:
        buckets = set(bucket_paths(changed_paths))
        status = "planning-safe" if buckets <= {"codestable", "docs"} else "dirty"
        next_action = "Review dirty buckets and keep the active Task synchronized."
    elif backlog:
        status = "attention-needed"
        next_action = "Resolve or explicitly defer the backlog items."
    else:
        status = "idle"
        next_action = "No CodeStable lifecycle action is required."

    return {
        "ok": status != "blocked",
        "status": status,
        "next_action": next_action,
        "checkout": {
            "root": root.as_posix(),
            "current_branch": branch,
            "default_branch": default,
            "is_default_branch": branch == default if branch and default else None,
        },
        "changed_files": changed_paths,
        "dirty_buckets": bucket_paths(changed_paths),
        "implementation_changes": implementation_changes,
        "active_units": [unit.as_posix() for unit in units],
        "backlog": [asdict(item) for item in backlog],
        "findings": [asdict(finding) for finding in findings],
        "tooling": {"runtime": runtime},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_pos", nargs="?", default=None, help="Repository root (positional; same as --root)")
    parser.add_argument("--root", default=".", help="Repository root to inspect")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    arguments = parser.parse_args()

    root = arguments.root_pos or arguments.root
    report = diagnose(Path(root))
    if arguments.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"CodeStable doctor: {report['status']}")
        print(f"Next action: {report['next_action']}")
        for finding in report["findings"]:
            path = f" ({finding['path']})" if finding.get("path") else ""
            print(f"- {finding['severity']}: {finding['message']}{path}")
        runtime = report["tooling"]["runtime"]
        runtime_hint = f" - {runtime['hint']}" if runtime.get("hint") else ""
        print(f"Runtime assets: {runtime['status']}{runtime_hint}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
