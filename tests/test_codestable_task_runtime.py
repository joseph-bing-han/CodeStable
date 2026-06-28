from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest


TOOLS_DIRECTORY = Path(__file__).resolve().parents[1] / "plugins/codestable/skills/cs-onboard/tools"


def load_task_runtime():
    module_path = TOOLS_DIRECTORY / "codestable-task-runtime.py"
    specification = importlib.util.spec_from_file_location("codestable_task_runtime", module_path)
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


task_runtime = load_task_runtime()


def task_content(task: str, status: str = "active") -> str:
    return (
        "---\n"
        "doc_type: task-list\n"
        f"task: {task}\n"
        f"goal: Complete {task}\n"
        f"status: {status}\n"
        "workflow: feature\n"
        "owner_skill: cs-feat\n"
        "created: 2026-07-17\n"
        "updated: 2026-07-17\n"
        "archived: null\n"
        "related_docs: []\n"
        "---\n\n"
        f"# Complete {task}\n\n"
        "## 1. 任务目标\n\nComplete the task.\n\n"
        f"## 2. 当前状态\n\n{status}\n\n"
        "## 3. Agent 原生 Tasks 同步区\n\n- [x] Complete implementation\n\n"
        "## 4. CodeStable 文档索引\n\n无。\n\n"
        "## 5. 执行步骤\n\n无。\n\n"
        "## 6. 中断恢复提示\n\n无。\n\n"
        "## 7. 完成与归档记录\n\nReady.\n"
    )


def write_content_file(root: Path, content: str) -> Path:
    content_path = root / "task-content.md"
    content_path.write_text(content, encoding="utf-8")
    return content_path


def test_write_active_task_uses_guarded_path(tmp_path: Path) -> None:
    task = "guarded-write"
    content_path = write_content_file(tmp_path, task_content(task))

    active_path = task_runtime.write_active_task(tmp_path, task, content_path)

    assert active_path == tmp_path / ".codestable/tasks/active/guarded-write.md"
    assert active_path.read_text(encoding="utf-8") == task_content(task)


def test_archive_moves_task_and_writes_completed_tombstone(tmp_path: Path) -> None:
    task = "archive-task"
    source_content = task_content(task, status="completed")
    content_path = write_content_file(tmp_path, source_content)
    active_path = task_runtime.write_active_task(tmp_path, task, content_path)

    result = task_runtime.archive_task(
        tmp_path,
        task,
        "2026-07-17",
        stability_checks=1,
        stability_delay_ms=0,
    )

    archived_path = tmp_path / result.archived_path
    tombstone_path = tmp_path / result.tombstone_path
    tombstone = json.loads(tombstone_path.read_text(encoding="utf-8"))
    assert not active_path.exists()
    assert archived_path.is_file()
    assert "status: archived" in archived_path.read_text(encoding="utf-8")
    assert tombstone["state"] == "archived"
    assert tombstone["archived_path"] == result.archived_path


def test_cleanup_removes_exact_stale_rewrite(tmp_path: Path) -> None:
    task = "stale-rewrite"
    source_content = task_content(task, status="completed")
    content_path = write_content_file(tmp_path, source_content)
    task_runtime.write_active_task(tmp_path, task, content_path)
    task_runtime.archive_task(
        tmp_path,
        task,
        "2026-07-17",
        stability_checks=1,
        stability_delay_ms=0,
    )
    stale_active_path = tmp_path / ".codestable/tasks/active/stale-rewrite.md"
    stale_active_path.parent.mkdir(parents=True, exist_ok=True)
    stale_active_path.write_text(source_content, encoding="utf-8")

    findings = task_runtime.cleanup_archived_task_residue(tmp_path, task)

    assert findings == []
    assert not stale_active_path.exists()


def test_cleanup_blocks_divergent_active_residue(tmp_path: Path) -> None:
    task = "divergent-rewrite"
    content_path = write_content_file(tmp_path, task_content(task, status="completed"))
    task_runtime.write_active_task(tmp_path, task, content_path)
    task_runtime.archive_task(
        tmp_path,
        task,
        "2026-07-17",
        stability_checks=1,
        stability_delay_ms=0,
    )
    divergent_active_path = tmp_path / ".codestable/tasks/active/divergent-rewrite.md"
    divergent_active_path.parent.mkdir(parents=True, exist_ok=True)
    divergent_active_path.write_text(task_content(task, status="active"), encoding="utf-8")

    findings = task_runtime.cleanup_archived_task_residue(tmp_path, task)

    assert [finding.code for finding in findings] == ["divergent-active-residue"]
    assert divergent_active_path.exists()


def test_write_active_rejects_archived_task(tmp_path: Path) -> None:
    task = "archived-task"
    content_path = write_content_file(tmp_path, task_content(task, status="completed"))
    task_runtime.write_active_task(tmp_path, task, content_path)
    task_runtime.archive_task(
        tmp_path,
        task,
        "2026-07-17",
        stability_checks=1,
        stability_delay_ms=0,
    )
    content_path.write_text(task_content(task, status="active"), encoding="utf-8")

    with pytest.raises(task_runtime.TaskRuntimeError, match="archived tombstone"):
        task_runtime.write_active_task(tmp_path, task, content_path)


def test_cleanup_preserves_concurrent_active_rewrite_during_delete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F-002 TOCTOU regression: cleanup deletes only the verified quarantine content.

    A concurrent writer that replaces ``active`` between the SHA check and the
    unlink must not lose its new content. Before the rename-to-quarantine fix,
    cleanup read the SHA from ``active_path`` and then unlinked ``active_path``
    directly, deleting whatever happened to be there at unlink time. With the
    quarantine flow the unlink targets the SHA-verified bytes, so the concurrent
    writer's content survives.
    """
    task = "toctou-concurrent-write"
    source_content = task_content(task, status="completed")
    content_path = write_content_file(tmp_path, source_content)
    task_runtime.write_active_task(tmp_path, task, content_path)
    task_runtime.archive_task(
        tmp_path,
        task,
        "2026-07-17",
        stability_checks=1,
        stability_delay_ms=0,
    )

    active_path = tmp_path / ".codestable/tasks/active/toctou-concurrent-write.md"
    active_path.parent.mkdir(parents=True, exist_ok=True)
    active_path.write_text(source_content, encoding="utf-8")

    concurrent_content = task_content(task, status="active")

    original_replace = task_runtime.replace_path_atomically
    quarantine_renames_seen: list[tuple[Path, Path]] = []

    def replace_with_concurrent_write(source: Path, destination: Path) -> None:
        result = original_replace(source, destination)
        if (
            source.name == "toctou-concurrent-write.md"
            and "task-quarantine" in destination.parent.name
        ):
            quarantine_renames_seen.append((source, destination))
            active_path.write_text(concurrent_content, encoding="utf-8")
        return result

    monkeypatch.setattr(task_runtime, "replace_path_atomically", replace_with_concurrent_write)

    findings = task_runtime.cleanup_archived_task_residue(tmp_path, task)

    monkeypatch.setattr(task_runtime, "replace_path_atomically", original_replace)

    assert quarantine_renames_seen, "cleanup must rename active into a quarantine directory"
    assert active_path.read_text(encoding="utf-8") == concurrent_content
    assert [finding.code for finding in findings] == ["concurrent-active-residue"]


def test_write_json_exclusive_rejects_existing_target(tmp_path: Path) -> None:
    """F-003 regression: O_EXCL ownership claim must fail when the target already exists.

    Two concurrent archives cannot both pass the read_tombstone precheck and
    then silently overwrite the same tombstone. The exclusive create turns the
    second writer into a hard failure instead of a data race.
    """
    target = tmp_path / "claimed-tombstone.json"
    target.write_text('{"state": "archiving"}', encoding="utf-8")

    with pytest.raises(FileExistsError):
        task_runtime.write_json_exclusive(target, {"state": "archived"})


def test_archive_rejects_preclaimed_archiving_tombstone(tmp_path: Path) -> None:
    """F-003 paired regression: an existing archiving tombstone blocks a second archive.

    Simulates the second concurrent archive entering after the first has
    claimed the tombstone but before it completes the active rename.
    """
    task = "concurrent-archive"
    content_path = write_content_file(tmp_path, task_content(task, status="completed"))
    task_runtime.write_active_task(tmp_path, task, content_path)

    tombstone_path = tmp_path / ".codestable/tasks/tombstones/concurrent-archive.json"
    tombstone_path.parent.mkdir(parents=True, exist_ok=True)
    tombstone_path.write_text(
        json.dumps(
            {
                "task": task,
                "state": "archiving",
                "source_status": "completed",
                "source_sha256": "0" * 64,
                "archived_path": ".codestable/tasks/archived/2026-07-17-concurrent-archive.md",
                "archived_date": "2026-07-17",
                "staging_path": ".codestable/tasks/staging/concurrent-archive.md",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    with pytest.raises(task_runtime.TaskRuntimeError, match="already has an active archived tombstone"):
        task_runtime.archive_task(
            tmp_path,
            task,
            "2026-07-17",
            stability_checks=1,
            stability_delay_ms=0,
        )


def test_task_paths_rejects_active_symlink_escape(tmp_path: Path) -> None:
    """F-004 regression: symlinked active directory must not escape the repository root.

    A malicious or accidental symlink at ``.codestable/tasks/active`` pointing
    outside the repo would otherwise redirect every active write off the repo.
    The path resolver must reject it before any write is attempted.
    """
    external_root = tmp_path / "external"
    external_root.mkdir()
    (external_root / "fake-active").mkdir()

    repo_root = tmp_path / "repo"
    tasks_root = repo_root / ".codestable/tasks"
    tasks_root.mkdir(parents=True)
    (tasks_root / "active").symlink_to(external_root / "fake-active")

    with pytest.raises(task_runtime.TaskRuntimeError, match="symlink"):
        task_runtime.task_paths(repo_root, "symlink-escape")


def test_task_paths_rejects_archived_symlink_escape(tmp_path: Path) -> None:
    """F-004 paired regression: archived directory symlinks are also rejected.

    Archive renames ``active`` into ``archived``; if ``archived`` is a symlink
    pointing outside the repo, the rename would leak the Task file off repo.
    """
    external_root = tmp_path / "external-archived"
    external_root.mkdir()
    (external_root / "fake-archived").mkdir()

    repo_root = tmp_path / "repo"
    tasks_root = repo_root / ".codestable/tasks"
    active_root = tasks_root / "active"
    active_root.mkdir(parents=True)
    (tasks_root / "archived").symlink_to(external_root / "fake-archived")

    content_path = write_content_file(tmp_path, task_content("archived-escape", status="completed"))
    with pytest.raises(task_runtime.TaskRuntimeError, match="symlink"):
        task_runtime.write_active_task(repo_root, "archived-escape", content_path)


def test_archive_rejects_semantically_invalid_date(tmp_path: Path) -> None:
    with pytest.raises(task_runtime.TaskRuntimeError, match="Invalid archive date"):
        task_runtime.validate_archive_date("2026-99-99")


@pytest.mark.parametrize(
    ("old_status", "new_status", "allowed"),
    [
        ("active", "active", True),
        ("active", "blocked", True),
        ("active", "completed", True),
        ("active", "cancelled", True),
        ("blocked", "blocked", True),
        ("blocked", "active", True),
        ("blocked", "completed", False),
        ("blocked", "cancelled", False),
        ("completed", "completed", True),
        ("completed", "active", False),
        ("cancelled", "cancelled", True),
        ("cancelled", "active", False),
    ],
)
def test_write_active_enforces_status_transition_matrix(
    tmp_path: Path,
    old_status: str,
    new_status: str,
    allowed: bool,
) -> None:
    task = f"transition-{old_status}-{new_status}"
    original_content_path = write_content_file(tmp_path, task_content(task, status=old_status))
    active_path = task_runtime.write_active_task(tmp_path, task, original_content_path)
    expected_sha256 = task_runtime.calculate_sha256(active_path.read_bytes())
    replacement_content_path = tmp_path / "replacement-content.md"
    replacement_content_path.write_text(task_content(task, status=new_status), encoding="utf-8")

    if allowed:
        task_runtime.write_active_task(
            tmp_path,
            task,
            replacement_content_path,
            expected_sha256,
        )
        assert f"status: {new_status}" in (
            tmp_path / f".codestable/tasks/active/{task}.md"
        ).read_text(encoding="utf-8")
    else:
        with pytest.raises(task_runtime.TaskRuntimeError, match="Invalid task status transition"):
            task_runtime.write_active_task(
                tmp_path,
                task,
                replacement_content_path,
                expected_sha256,
            )


def test_task_paths_rejects_active_symlink_to_repository_file(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    active_root = repo_root / ".codestable/tasks/active"
    active_root.mkdir(parents=True)
    repository_file = repo_root / "README.md"
    repository_file.write_text("repository content\n", encoding="utf-8")
    (active_root / "inside-repository.md").symlink_to(repository_file)

    with pytest.raises(task_runtime.TaskRuntimeError, match="symlink"):
        task_runtime.task_paths(repo_root, "inside-repository")

    assert repository_file.read_text(encoding="utf-8") == "repository content\n"


def test_task_paths_rejects_active_directory_symlink_inside_repository(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    alternate_root = repo_root / "alternate"
    alternate_root.mkdir(parents=True)
    tasks_root = repo_root / ".codestable/tasks"
    tasks_root.mkdir(parents=True)
    (tasks_root / "active").symlink_to(alternate_root)

    with pytest.raises(task_runtime.TaskRuntimeError, match="symlink"):
        task_runtime.task_paths(repo_root, "inside-directory")


def test_archive_fails_closed_when_active_changes_after_claim(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task = "claim-race"
    original_content = task_content(task, status="completed")
    updated_content = original_content.replace("Ready.", "Updated after claim.")
    content_path = write_content_file(tmp_path, original_content)
    task_runtime.write_active_task(tmp_path, task, content_path)
    active_path = tmp_path / ".codestable/tasks/active/claim-race.md"

    original_claim = task_runtime.write_json_exclusive

    def claim_then_replace(path: Path, payload: dict[str, object]) -> None:
        original_claim(path, payload)
        active_path.write_text(updated_content, encoding="utf-8")

    monkeypatch.setattr(task_runtime, "write_json_exclusive", claim_then_replace)

    with pytest.raises(task_runtime.TaskRuntimeError, match="changed after archive claim"):
        task_runtime.archive_task(
            tmp_path,
            task,
            "2026-07-17",
            stability_checks=1,
            stability_delay_ms=0,
        )

    assert active_path.read_text(encoding="utf-8") == updated_content


def test_cleanup_preserves_divergent_residue_and_concurrent_active(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task = "divergent-concurrent-write"
    source_content = task_content(task, status="completed")
    content_path = write_content_file(tmp_path, source_content)
    task_runtime.write_active_task(tmp_path, task, content_path)
    task_runtime.archive_task(
        tmp_path,
        task,
        "2026-07-17",
        stability_checks=1,
        stability_delay_ms=0,
    )

    active_path = tmp_path / ".codestable/tasks/active/divergent-concurrent-write.md"
    divergent_content = task_content(task, status="active")
    concurrent_content = divergent_content.replace("Ready.", "Concurrent update.")
    active_path.write_text(divergent_content, encoding="utf-8")
    original_replace = task_runtime.replace_path_atomically

    def replace_then_write(source: Path, destination: Path) -> None:
        original_replace(source, destination)
        if "task-quarantine" in str(destination):
            active_path.write_text(concurrent_content, encoding="utf-8")

    monkeypatch.setattr(task_runtime, "replace_path_atomically", replace_then_write)

    findings = task_runtime.cleanup_archived_task_residue(tmp_path, task)

    assert active_path.read_text(encoding="utf-8") == concurrent_content
    assert [finding.code for finding in findings] == ["divergent-active-conflict"]
    conflict_path = tmp_path / findings[0].path
    assert conflict_path.read_text(encoding="utf-8") == divergent_content


def test_scan_recovers_archive_after_process_exit_before_final_tombstone(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task = "crash-recovery"
    content_path = write_content_file(tmp_path, task_content(task, status="completed"))
    task_runtime.write_active_task(tmp_path, task, content_path)
    original_write_json = task_runtime.write_json_atomically

    def exit_before_final_tombstone(path: Path, payload: dict[str, object]) -> None:
        if payload.get("state") == "archived":
            raise SystemExit("simulated process exit")
        original_write_json(path, payload)

    monkeypatch.setattr(task_runtime, "write_json_atomically", exit_before_final_tombstone)
    with pytest.raises(SystemExit, match="simulated process exit"):
        task_runtime.archive_task(
            tmp_path,
            task,
            "2026-07-17",
            stability_checks=1,
            stability_delay_ms=0,
        )

    monkeypatch.setattr(task_runtime, "write_json_atomically", original_write_json)
    findings = task_runtime.scan_task_runtime(tmp_path)
    inspection = task_runtime.inspect_archived_task(tmp_path, task)

    assert findings == []
    assert inspection.state == "valid"


def test_scan_reports_unrecoverable_archiving_tombstone(tmp_path: Path) -> None:
    task = "incomplete-archive"
    paths = task_runtime.task_paths(tmp_path, task)
    paths.tombstone_path.parent.mkdir(parents=True, exist_ok=True)
    paths.tombstone_path.write_text(
        json.dumps(
            {
                "task": task,
                "state": "archiving",
                "source_status": "completed",
                "source_sha256": "0" * 64,
                "archived_path": ".codestable/tasks/archived/2026-07-17-incomplete-archive.md",
                "archived_date": "2026-07-17",
                "staging_path": ".codestable/tasks/staging/incomplete-archive.md",
            }
        ),
        encoding="utf-8",
    )

    findings = task_runtime.scan_task_runtime(tmp_path)

    assert [finding.code for finding in findings] == ["incomplete-archive"]


def test_archive_retry_with_same_date_is_idempotent(tmp_path: Path) -> None:
    task = "idempotent-archive"
    content_path = write_content_file(tmp_path, task_content(task, status="completed"))
    task_runtime.write_active_task(tmp_path, task, content_path)
    first_result = task_runtime.archive_task(
        tmp_path,
        task,
        "2026-07-17",
        stability_checks=1,
        stability_delay_ms=0,
    )

    second_result = task_runtime.archive_task(
        tmp_path,
        task,
        "2026-07-17",
        stability_checks=1,
        stability_delay_ms=0,
    )

    assert second_result == first_result


def test_archive_retry_with_different_date_fails_closed(tmp_path: Path) -> None:
    task = "conflicting-archive-date"
    content_path = write_content_file(tmp_path, task_content(task, status="completed"))
    task_runtime.write_active_task(tmp_path, task, content_path)
    task_runtime.archive_task(
        tmp_path,
        task,
        "2026-07-17",
        stability_checks=1,
        stability_delay_ms=0,
    )

    with pytest.raises(task_runtime.TaskRuntimeError, match="different archive date"):
        task_runtime.archive_task(
            tmp_path,
            task,
            "2026-07-18",
            stability_checks=1,
            stability_delay_ms=0,
        )


def test_write_active_requires_expected_sha_for_existing_task(tmp_path: Path) -> None:
    task = "cas-required"
    content_path = write_content_file(tmp_path, task_content(task))
    task_runtime.write_active_task(tmp_path, task, content_path)
    replacement_path = tmp_path / "replacement.md"
    replacement_path.write_text(
        task_content(task).replace("Ready.", "Replacement."),
        encoding="utf-8",
    )

    with pytest.raises(task_runtime.TaskRuntimeError, match="requires --expected-sha256"):
        task_runtime.write_active_task(tmp_path, task, replacement_path)


def test_write_active_rejects_second_stale_writer(tmp_path: Path) -> None:
    task = "cas-stale-writer"
    content_path = write_content_file(tmp_path, task_content(task))
    active_path = task_runtime.write_active_task(tmp_path, task, content_path)
    expected_sha256 = task_runtime.calculate_sha256(active_path.read_bytes())
    first_writer_path = tmp_path / "first-writer.md"
    second_writer_path = tmp_path / "second-writer.md"
    first_writer_content = task_content(task).replace("Ready.", "First writer.")
    second_writer_content = task_content(task).replace("Ready.", "Second writer.")
    first_writer_path.write_text(first_writer_content, encoding="utf-8")
    second_writer_path.write_text(second_writer_content, encoding="utf-8")

    task_runtime.write_active_task(tmp_path, task, first_writer_path, expected_sha256)

    with pytest.raises(task_runtime.TaskRuntimeError, match="compare-and-swap conflict"):
        task_runtime.write_active_task(tmp_path, task, second_writer_path, expected_sha256)

    assert active_path.read_text(encoding="utf-8") == first_writer_content


@pytest.mark.parametrize(
    "invalid_archived_path",
    [
        "../../../../escape.md",
        "/tmp/escape.md",
        ".codestable/tasks/archived/../escape.md",
    ],
)
def test_tombstone_rejects_noncanonical_archived_path(
    tmp_path: Path,
    invalid_archived_path: str,
) -> None:
    task = "canonical-tombstone"
    paths = task_runtime.task_paths(tmp_path, task)
    payload = {
        "task": task,
        "state": "archiving",
        "source_status": "completed",
        "source_sha256": "0" * 64,
        "archived_path": invalid_archived_path,
        "archived_date": "2026-07-17",
        "staging_path": ".codestable/tasks/staging/canonical-tombstone.md",
    }

    with pytest.raises(task_runtime.TaskRuntimeError, match="archived_path is not canonical"):
        task_runtime.validate_tombstone_payload(paths, payload)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda content: content.replace("goal: Complete strict-task\n", ""),
        lambda content: content.replace(
            "status: active\n",
            "status: active\nunexpected: value\n",
        ),
        lambda content: content.replace(
            "status: active\n",
            "status: active\nstatus: active\n",
        ),
        lambda content: content.replace("## 6. 中断恢复提示\n\n无。\n\n", ""),
    ],
)
def test_task_schema_rejects_invalid_mutations(tmp_path: Path, mutation) -> None:
    task = "strict-task"
    invalid_content = mutation(task_content(task))

    with pytest.raises(task_runtime.TaskRuntimeError):
        task_runtime.validate_task_content(
            invalid_content,
            task,
            task_runtime.ACTIVE_STATUSES,
        )


def test_tombstone_schema_rejects_unknown_and_missing_fields(tmp_path: Path) -> None:
    task = "strict-tombstone"
    paths = task_runtime.task_paths(tmp_path, task)
    payload = {
        "task": task,
        "state": "archived",
        "source_status": "completed",
        "source_sha256": "0" * 64,
        "archived_sha256": "1" * 64,
        "archived_path": ".codestable/tasks/archived/2026-07-17-strict-tombstone.md",
        "archived_date": "2026-07-17",
        "staging_path": ".codestable/tasks/staging/strict-tombstone.md",
        "unexpected": True,
    }

    with pytest.raises(task_runtime.TaskRuntimeError, match="unknown fields"):
        task_runtime.validate_tombstone_payload(paths, payload)

    payload.pop("unexpected")
    payload.pop("source_sha256")
    with pytest.raises(task_runtime.TaskRuntimeError, match="missing fields"):
        task_runtime.validate_tombstone_payload(paths, payload)


def test_archived_only_recovery_does_not_authenticate_content(tmp_path: Path) -> None:
    task = "archived-only-recovery"
    paths = task_runtime.task_paths(tmp_path, task)
    source_content = task_content(task, status="completed")
    archived_content = task_runtime.prepare_archived_content(
        source_content,
        "2026-07-17",
    ).replace("Ready.", "Untrusted archived content.")
    paths.archived_root.mkdir(parents=True, exist_ok=True)
    archived_path = paths.archived_root / f"2026-07-17-{task}.md"
    archived_path.write_text(archived_content, encoding="utf-8")
    paths.tombstone_root.mkdir(parents=True, exist_ok=True)
    tombstone = {
        "task": task,
        "state": "archiving",
        "source_status": "completed",
        "source_sha256": task_runtime.calculate_sha256(source_content.encode("utf-8")),
        "archived_path": f".codestable/tasks/archived/2026-07-17-{task}.md",
        "archived_date": "2026-07-17",
        "staging_path": f".codestable/tasks/staging/{task}.md",
    }
    paths.tombstone_path.write_text(json.dumps(tombstone), encoding="utf-8")

    findings = task_runtime.scan_task_runtime(tmp_path)

    assert [finding.code for finding in findings] == ["incomplete-archive"]
    persisted_tombstone = json.loads(paths.tombstone_path.read_text(encoding="utf-8"))
    assert persisted_tombstone["state"] == "archiving"
    assert "archived_sha256" not in persisted_tombstone


def test_scan_reports_unknown_state_lone_archived_staging_and_conflict(
    tmp_path: Path,
) -> None:
    task_root = tmp_path / ".codestable/tasks"
    tombstone_root = task_root / "tombstones"
    archived_root = task_root / "archived"
    staging_root = task_root / "staging"
    conflict_root = task_root / "conflicts"
    for directory in (tombstone_root, archived_root, staging_root, conflict_root):
        directory.mkdir(parents=True, exist_ok=True)

    (tombstone_root / "unknown-state.json").write_text(
        json.dumps({"task": "unknown-state", "state": "unknown"}),
        encoding="utf-8",
    )
    (archived_root / "2026-07-17-lone-archived.md").write_text(
        task_runtime.prepare_archived_content(
            task_content("lone-archived", status="completed"),
            "2026-07-17",
        ),
        encoding="utf-8",
    )
    (staging_root / "lone-staging.md").write_text(
        task_content("lone-staging", status="completed"),
        encoding="utf-8",
    )
    (conflict_root / "lone-staging-evidence.md").write_text(
        "conflict\n",
        encoding="utf-8",
    )

    findings = task_runtime.scan_task_runtime(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "task-runtime-scan-failed" in finding_codes
    assert "missing-archive-tombstone" in finding_codes
    assert "orphaned-archive-staging" in finding_codes
    assert "unresolved-task-conflict" in finding_codes


def test_scan_allows_historical_archived_task_without_tombstone(tmp_path: Path) -> None:
    task = "historical-archive"
    archived_root = tmp_path / ".codestable/tasks/archived"
    archived_root.mkdir(parents=True)
    archived_path = archived_root / f"2026-07-16-{task}.md"
    archived_path.write_text(
        task_runtime.prepare_archived_content(
            task_content(task, status="completed"),
            "2026-07-16",
        ),
        encoding="utf-8",
    )

    assert task_runtime.scan_task_runtime(tmp_path) == []
    assert task_runtime.inspect_archived_task(tmp_path, task).state == "historical"


def test_scan_reports_historical_active_archive_conflict(tmp_path: Path) -> None:
    task = "historical-conflict"
    archived_root = tmp_path / ".codestable/tasks/archived"
    active_root = tmp_path / ".codestable/tasks/active"
    archived_root.mkdir(parents=True)
    active_root.mkdir(parents=True)
    (archived_root / f"2026-07-16-{task}.md").write_text(
        task_runtime.prepare_archived_content(
            task_content(task, status="completed"),
            "2026-07-16",
        ),
        encoding="utf-8",
    )
    (active_root / f"{task}.md").write_text(task_content(task), encoding="utf-8")

    findings = task_runtime.scan_task_runtime(tmp_path)
    inspection = task_runtime.inspect_archived_task(tmp_path, task)

    assert [finding.code for finding in findings] == [
        "historical-active-archive-conflict"
    ]
    assert inspection.state == "invalid"
    assert [finding.code for finding in inspection.findings] == [
        "historical-active-archive-conflict"
    ]


@pytest.mark.parametrize(
    ("old_fragment", "new_fragment"),
    [
        ("goal: Complete typed-task", "goal: null"),
        ("workflow: feature", "workflow: []"),
        ("owner_skill: cs-feat", "owner_skill: true"),
        ("archived: null", 'archived: "null"'),
        ("related_docs: []", "related_docs: invalid"),
    ],
)
def test_task_schema_rejects_yaml_pseudo_types(
    old_fragment: str,
    new_fragment: str,
) -> None:
    task = "typed-task"
    invalid_content = task_content(task).replace(old_fragment, new_fragment)

    with pytest.raises(task_runtime.TaskRuntimeError):
        task_runtime.validate_task_content(
            invalid_content,
            task,
            task_runtime.ACTIVE_STATUSES,
        )


@pytest.mark.parametrize(
    "raw_json",
    [
        '{"task":"strict-json","task":"spoofed"}',
        '{"task":"strict-json","value":NaN}',
        '{"task":"strict-json","value":Infinity}',
    ],
)
def test_read_tombstone_rejects_duplicate_keys_and_nonfinite_values(
    tmp_path: Path,
    raw_json: str,
) -> None:
    paths = task_runtime.task_paths(tmp_path, "strict-json")
    paths.tombstone_root.mkdir(parents=True)
    paths.tombstone_path.write_text(raw_json, encoding="utf-8")

    with pytest.raises(task_runtime.TaskRuntimeError):
        task_runtime.read_tombstone(paths)


def test_scan_validates_active_task_document(tmp_path: Path) -> None:
    task = "invalid-active"
    active_root = tmp_path / ".codestable/tasks/active"
    active_root.mkdir(parents=True)
    (active_root / f"{task}.md").write_text(
        task_content(task).replace("workflow: feature", "workflow: []"),
        encoding="utf-8",
    )

    findings = task_runtime.scan_task_runtime(tmp_path)

    assert [finding.code for finding in findings] == [
        "invalid-active-task-document"
    ]


def test_scan_removes_verified_staging_after_final_tombstone(tmp_path: Path) -> None:
    task = "finalized-staging"
    source_content = task_content(task, status="completed")
    content_path = write_content_file(tmp_path, source_content)
    task_runtime.write_active_task(tmp_path, task, content_path)
    task_runtime.archive_task(
        tmp_path,
        task,
        "2026-07-17",
        stability_checks=1,
        stability_delay_ms=0,
    )
    staging_path = tmp_path / f".codestable/tasks/staging/{task}.md"
    staging_path.write_text(source_content, encoding="utf-8")

    findings = task_runtime.scan_task_runtime(tmp_path)

    assert findings == []
    assert not staging_path.exists()
    assert task_runtime.inspect_archived_task(tmp_path, task).state == "valid"


def test_scan_preserves_tampered_staging_after_final_tombstone(tmp_path: Path) -> None:
    task = "tampered-finalized-staging"
    source_content = task_content(task, status="completed")
    content_path = write_content_file(tmp_path, source_content)
    task_runtime.write_active_task(tmp_path, task, content_path)
    task_runtime.archive_task(
        tmp_path,
        task,
        "2026-07-17",
        stability_checks=1,
        stability_delay_ms=0,
    )
    staging_path = tmp_path / f".codestable/tasks/staging/{task}.md"
    staging_path.write_text(
        source_content.replace("Ready.", "Tampered staging."),
        encoding="utf-8",
    )

    findings = task_runtime.scan_task_runtime(tmp_path)

    assert [finding.code for finding in findings] == [
        "finalized-archive-staging-source-mismatch"
    ]
    assert staging_path.exists()


def test_write_json_exclusive_publishes_complete_claim_before_post_link_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "claims/task.json"
    target.parent.mkdir()
    payload = {"task": "atomic-claim", "state": "archiving"}
    original_link = task_runtime.os.link

    def link_then_exit(source, destination, *args, **kwargs):
        original_link(source, destination, *args, **kwargs)
        raise SystemExit("simulated exit after claim publication")

    monkeypatch.setattr(task_runtime.os, "link", link_then_exit)

    with pytest.raises(SystemExit, match="simulated exit"):
        task_runtime.write_json_exclusive(target, payload)

    assert json.loads(target.read_text(encoding="utf-8")) == payload


def test_write_json_exclusive_removes_displaced_claim_after_parent_swap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    claim_root = tmp_path / "claims"
    displaced_root = tmp_path / "claims-displaced"
    external_root = tmp_path / "external-claims"
    claim_root.mkdir()
    external_root.mkdir()
    target = claim_root / "task.json"
    original_link = task_runtime.os.link
    swapped = False

    def link_after_parent_swap(source, destination, *args, **kwargs):
        nonlocal swapped
        if destination == target.name and not swapped:
            claim_root.rename(displaced_root)
            claim_root.symlink_to(external_root)
            swapped = True
        return original_link(source, destination, *args, **kwargs)

    monkeypatch.setattr(task_runtime.os, "link", link_after_parent_swap)

    with pytest.raises(
        task_runtime.TaskRuntimeError,
        match="identity changed|symlink or non-directory component",
    ):
        task_runtime.write_json_exclusive(
            target,
            {"task": "atomic-claim", "state": "archiving"},
        )

    assert swapped
    assert not (external_root / target.name).exists()
    assert not (displaced_root / target.name).exists()


def test_write_active_preserves_direct_writer_during_cas_capture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task = "cas-direct-writer"
    initial_content = task_content(task)
    content_path = write_content_file(tmp_path, initial_content)
    active_path = task_runtime.write_active_task(tmp_path, task, content_path)
    expected_sha256 = task_runtime.calculate_sha256(active_path.read_bytes())
    replacement_path = tmp_path / "replacement.md"
    replacement_path.write_text(
        initial_content.replace("Ready.", "Guarded replacement."),
        encoding="utf-8",
    )
    concurrent_content = initial_content.replace("Ready.", "Direct writer.")
    original_replace = task_runtime.os.replace

    def replace_then_recreate_active(source, destination, *args, **kwargs):
        result = original_replace(source, destination, *args, **kwargs)
        if (
            source == f"{task}.md"
            and destination == f"{task}.md"
            and kwargs.get("src_dir_fd") != kwargs.get("dst_dir_fd")
        ):
            active_path.write_text(concurrent_content, encoding="utf-8")
        return result

    monkeypatch.setattr(task_runtime.os, "replace", replace_then_recreate_active)

    with pytest.raises(task_runtime.TaskRuntimeError, match="concurrent writer recreated"):
        task_runtime.write_active_task(
            tmp_path,
            task,
            replacement_path,
            expected_sha256,
        )

    assert active_path.read_text(encoding="utf-8") == concurrent_content
    captured_paths = list(
        (tmp_path / ".codestable/tasks/conflicts").glob(f"{task}-cas-*.md")
    )
    assert len(captured_paths) == 1
    assert captured_paths[0].read_text(encoding="utf-8") == initial_content


def test_write_active_update_fails_closed_on_parent_directory_swap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task = "update-directory-swap"
    initial_content = task_content(task)
    content_path = write_content_file(tmp_path, initial_content)
    active_path = task_runtime.write_active_task(tmp_path, task, content_path)
    expected_sha256 = task_runtime.calculate_sha256(active_path.read_bytes())
    replacement_path = tmp_path / "replacement.md"
    replacement_path.write_text(
        initial_content.replace("Ready.", "Replacement."),
        encoding="utf-8",
    )
    active_root = tmp_path / ".codestable/tasks/active"
    displaced_root = tmp_path / ".codestable/tasks/active-displaced"
    external_root = tmp_path / "external-active"
    external_root.mkdir()
    original_link = task_runtime.os.link
    swapped = False

    def link_after_parent_swap(source, destination, *args, **kwargs):
        nonlocal swapped
        if destination == f"{task}.md" and not swapped:
            active_root.rename(displaced_root)
            active_root.symlink_to(external_root)
            swapped = True
        return original_link(source, destination, *args, **kwargs)

    monkeypatch.setattr(task_runtime.os, "link", link_after_parent_swap)

    with pytest.raises(
        task_runtime.TaskRuntimeError,
        match="identity changed|symlink or non-directory component",
    ):
        task_runtime.write_active_task(
            tmp_path,
            task,
            replacement_path,
            expected_sha256,
        )

    assert swapped
    assert not (external_root / f"{task}.md").exists()
    assert (displaced_root / f"{task}.md").read_text(encoding="utf-8") == initial_content


def test_write_active_fails_closed_when_lock_pathname_is_replaced(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task = "lock-inode-swap"
    content_path = write_content_file(tmp_path, task_content(task))
    active_path = tmp_path / f".codestable/tasks/active/{task}.md"
    lock_path = tmp_path / f".codestable/tasks/locks/{task}.lock"
    original_link = task_runtime.os.link
    replaced = False

    def link_after_lock_replacement(source, destination, *args, **kwargs):
        nonlocal replaced
        if destination == f"{task}.md" and not replaced:
            lock_path.unlink()
            lock_path.write_text("replacement lock\n", encoding="utf-8")
            replaced = True
        return original_link(source, destination, *args, **kwargs)

    monkeypatch.setattr(task_runtime.os, "link", link_after_lock_replacement)

    with pytest.raises(task_runtime.TaskRuntimeError, match="lock pathname changed"):
        task_runtime.write_active_task(tmp_path, task, content_path)

    assert replaced
    assert not active_path.exists()


def test_write_active_fails_closed_on_parent_directory_swap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task = "directory-swap"
    content_path = write_content_file(tmp_path, task_content(task))
    active_root = tmp_path / ".codestable/tasks/active"
    displaced_root = tmp_path / ".codestable/tasks/active-displaced"
    external_root = tmp_path / "external-active"
    external_root.mkdir()
    original_link = task_runtime.os.link
    swapped = False

    def link_after_parent_swap(source, destination, *args, **kwargs):
        nonlocal swapped
        if destination == f"{task}.md" and not swapped:
            active_root.rename(displaced_root)
            active_root.symlink_to(external_root)
            swapped = True
        return original_link(source, destination, *args, **kwargs)

    monkeypatch.setattr(task_runtime.os, "link", link_after_parent_swap)

    with pytest.raises(
        task_runtime.TaskRuntimeError,
        match="identity changed|symlink or non-directory component",
    ):
        task_runtime.write_active_task(tmp_path, task, content_path)

    assert swapped
    assert not (external_root / f"{task}.md").exists()
    assert not (displaced_root / f"{task}.md").exists()
