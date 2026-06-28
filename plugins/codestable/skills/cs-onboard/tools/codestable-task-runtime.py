#!/usr/bin/env python3
"""Execute guarded CodeStable Task lifecycle file operations.

Concurrency support boundary (see CS5-I05):
    The active-Task compare-and-swap treats the on-disk file (by pathname and
    content SHA) as the single source of truth. A writer that opened the *old*
    active file descriptor before a CAS capture and keeps writing to that
    now-unlinked inode afterwards is explicitly NOT supported: once the CAS
    moves the old entry into quarantine, subsequent writes to the stale open
    descriptor land on an inode no longer referenced by the active pathname and
    are intentionally discarded. Callers must always re-read and re-write the
    active pathname (never hold a long-lived active FD across a CAS) so that the
    expected-SHA compare-and-swap can detect and preserve concurrent updates.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import stat
import sys
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Iterator

# Reuse the single shared strict YAML loader so Task, review, and workflow
# artifacts converge on one duplicate-key-rejecting parser instead of drifting
# across separate implementations. Anchor the sibling import on this script's
# own directory so both subprocess execution and in-process test loading
# (importlib spec loading, which does not auto-extend sys.path) resolve it.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from codestable_gate_common import load_yaml_text


TASK_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ARCHIVE_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FRONTMATTER_PATTERN = re.compile(r"\A---\n(?P<frontmatter>.*?)\n---\n", re.DOTALL)
FIELD_PATTERN_TEMPLATE = r"(?m)^(?P<prefix>{field}:\s*).*$"
CURRENT_STATUS_PATTERN = re.compile(r"(?m)(^## 2\. 当前状态\s*$\n+)([^\n]+)")
TASK_SECTION_HEADINGS = (
    "## 1. 任务目标",
    "## 2. 当前状态",
    "## 3. Agent 原生 Tasks 同步区",
    "## 4. CodeStable 文档索引",
    "## 5. 执行步骤",
    "## 6. 中断恢复提示",
    "## 7. 完成与归档记录",
)
TASK_REQUIRED_FIELDS = frozenset(
    {
        "doc_type",
        "task",
        "goal",
        "status",
        "workflow",
        "owner_skill",
        "created",
        "updated",
        "archived",
        "related_docs",
    }
)
ARCHIVING_TOMBSTONE_FIELDS = frozenset(
    {
        "task",
        "state",
        "source_status",
        "source_sha256",
        "archived_path",
        "archived_date",
        "staging_path",
    }
)
ARCHIVED_TOMBSTONE_FIELDS = ARCHIVING_TOMBSTONE_FIELDS | {"archived_sha256"}
ACTIVE_STATUSES = frozenset({"active", "blocked", "completed", "cancelled"})
ARCHIVABLE_STATUSES = frozenset({"completed", "cancelled"})
BLOCKING_TOMBSTONE_STATES = frozenset({"archiving", "archived"})
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ARCHIVED_TASK_FILE_PATTERN = re.compile(
    r"^(?P<archive_date>\d{4}-\d{2}-\d{2})-(?P<task>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$"
)
TOMBSTONE_REQUIRED_FROM_DATE = date(2026, 7, 17)
ACTIVE_STATUS_TRANSITIONS: dict[str, frozenset[str]] = {
    "active": frozenset({"active", "blocked", "completed", "cancelled"}),
    "blocked": frozenset({"blocked", "active"}),
    "completed": frozenset({"completed"}),
    "cancelled": frozenset({"cancelled"}),
}


class TaskRuntimeError(RuntimeError):
    """Raised when a guarded Task operation cannot be completed safely."""


@dataclass(frozen=True)
class TaskPaths:
    root: Path
    task: str
    task_root: Path
    active_root: Path
    archived_root: Path
    tombstone_root: Path
    staging_root: Path
    conflict_root: Path
    lock_root: Path
    active_path: Path
    tombstone_path: Path
    staging_path: Path
    conflict_path: Path
    lock_path: Path


@dataclass(frozen=True)
class RuntimeFinding:
    code: str
    message: str
    path: str


@dataclass(frozen=True)
class ArchiveResult:
    task: str
    archived_path: str
    tombstone_path: str
    removed_stale_rewrites: int


@dataclass(frozen=True)
class ArchiveInspection:
    task: str
    state: str
    archived_path: str | None
    tombstone_path: str
    task_status: str | None
    workflow: str | None
    owner_skill: str | None
    related_docs: tuple[str, ...]
    task_sha256: str | None
    findings: tuple[RuntimeFinding, ...]


@dataclass(frozen=True)
class DirectoryIdentity:
    device: int
    inode: int


@dataclass(frozen=True)
class FileIdentity:
    device: int
    inode: int
    size: int


@dataclass(frozen=True)
class TaskOperationLock:
    file_descriptor: int
    lock_file_identity: FileIdentity
    directory_fd: int
    directory_identity: DirectoryIdentity
    lock_path: Path


def relative_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def validate_task_slug(task: str) -> None:
    if not TASK_SLUG_PATTERN.fullmatch(task):
        raise TaskRuntimeError(f"Invalid task slug: {task!r}")


def validate_archive_date(archive_date: str) -> None:
    if not ARCHIVE_DATE_PATTERN.fullmatch(archive_date):
        raise TaskRuntimeError(f"Invalid archive date: {archive_date!r}")
    try:
        date.fromisoformat(archive_date)
    except ValueError as error:
        raise TaskRuntimeError(f"Invalid archive date: {archive_date!r}") from error


def ensure_no_symlink_components(root: Path, path: Path, label: str) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise TaskRuntimeError(f"Task {label} path escapes the repository root: {path}") from error

    current = root
    for component in relative.parts:
        current = current / component
        if current.is_symlink():
            raise TaskRuntimeError(f"Task {label} path contains a symlink: {current}")


def ensure_canonical_path(path: Path, canonical_root: Path, label: str) -> None:
    if not path.is_absolute() or any(component in {"", ".", ".."} for component in path.parts):
        raise TaskRuntimeError(f"Task {label} path is not canonical: {path}")
    normalized_path = Path(os.path.normpath(path))
    if normalized_path != path:
        raise TaskRuntimeError(f"Task {label} path is not canonical: {path}")
    ensure_no_symlink_components(canonical_root.parent.parent.parent, canonical_root, label)
    ensure_no_symlink_components(canonical_root.parent.parent.parent, path, label)
    try:
        path.relative_to(canonical_root)
    except ValueError as error:
        raise TaskRuntimeError(
            f"Task {label} path must stay inside the canonical {label} directory: {canonical_root}"
        ) from error
    if path.exists() and path.is_symlink():
        raise TaskRuntimeError(f"Task {label} path must not be a symlink: {path}")


def ensure_safe_directory(root: Path, directory: Path, label: str) -> None:
    try:
        relative_directory = directory.relative_to(root)
    except ValueError as error:
        raise TaskRuntimeError(f"Task {label} directory escapes the repository root: {directory}") from error

    directory_fd, _ = open_verified_directory(root)
    try:
        for component in relative_directory.parts:
            try:
                os.mkdir(component, mode=0o700, dir_fd=directory_fd)
            except FileExistsError:
                pass
            child_fd = open_directory_component(directory_fd, component, directory)
            os.close(directory_fd)
            directory_fd = child_fd
    finally:
        os.close(directory_fd)


def directory_open_flags() -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def open_directory_component(parent_fd: int, component: str, directory: Path) -> int:
    try:
        child_fd = os.open(component, directory_open_flags(), dir_fd=parent_fd)
    except OSError as error:
        raise TaskRuntimeError(
            f"Directory path contains a symlink or non-directory component: {directory}"
        ) from error
    child_stat = os.fstat(child_fd)
    if not stat.S_ISDIR(child_stat.st_mode):
        os.close(child_fd)
        raise TaskRuntimeError(f"Expected a real directory, found: {directory}")
    return child_fd


def open_verified_directory(directory: Path) -> tuple[int, DirectoryIdentity]:
    absolute_directory = directory.absolute()
    directory_fd = os.open(os.path.sep, directory_open_flags())
    try:
        for component in absolute_directory.parts[1:]:
            child_fd = open_directory_component(directory_fd, component, absolute_directory)
            os.close(directory_fd)
            directory_fd = child_fd
        opened_stat = os.fstat(directory_fd)
        identity = DirectoryIdentity(opened_stat.st_dev, opened_stat.st_ino)
        return directory_fd, identity
    except BaseException:
        os.close(directory_fd)
        raise


def verify_open_directory(
    directory_fd: int,
    expected_identity: DirectoryIdentity,
    directory: Path,
) -> None:
    current_stat = os.fstat(directory_fd)
    current_identity = DirectoryIdentity(current_stat.st_dev, current_stat.st_ino)
    if current_identity != expected_identity:
        raise TaskRuntimeError(f"Directory identity changed during operation: {directory}")
    path_fd, path_identity = open_verified_directory(directory)
    os.close(path_fd)
    if path_identity != expected_identity:
        raise TaskRuntimeError(f"Directory path identity changed during operation: {directory}")


def file_identity(file_stat: os.stat_result) -> FileIdentity:
    return FileIdentity(file_stat.st_dev, file_stat.st_ino, file_stat.st_size)


def verify_task_operation_lock(operation_lock: TaskOperationLock) -> None:
    verify_open_directory(
        operation_lock.directory_fd,
        operation_lock.directory_identity,
        operation_lock.lock_path.parent,
    )
    descriptor_identity = file_identity(os.fstat(operation_lock.file_descriptor))
    try:
        pathname_stat = os.stat(
            operation_lock.lock_path.name,
            dir_fd=operation_lock.directory_fd,
            follow_symlinks=False,
        )
    except FileNotFoundError as error:
        raise TaskRuntimeError(
            f"Task lock pathname changed while held: {operation_lock.lock_path}"
        ) from error
    pathname_identity = file_identity(pathname_stat)
    if (
        descriptor_identity.device != operation_lock.lock_file_identity.device
        or descriptor_identity.inode != operation_lock.lock_file_identity.inode
        or pathname_identity.device != operation_lock.lock_file_identity.device
        or pathname_identity.inode != operation_lock.lock_file_identity.inode
        or not stat.S_ISREG(pathname_stat.st_mode)
        or pathname_stat.st_nlink != 1
    ):
        raise TaskRuntimeError(
            f"Task lock pathname changed while held: {operation_lock.lock_path}"
        )


def read_bytes_no_follow(path: Path) -> bytes:
    directory_fd, directory_identity = open_verified_directory(path.parent)
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        file_descriptor = os.open(path.name, flags, dir_fd=directory_fd)
        try:
            chunks: list[bytes] = []
            while True:
                chunk = os.read(file_descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            verify_open_directory(directory_fd, directory_identity, path.parent)
            return b"".join(chunks)
        finally:
            os.close(file_descriptor)
    finally:
        os.close(directory_fd)


def unlink_no_follow(path: Path) -> None:
    directory_fd, directory_identity = open_verified_directory(path.parent)
    try:
        verify_open_directory(directory_fd, directory_identity, path.parent)
        os.unlink(path.name, dir_fd=directory_fd)
        verify_open_directory(directory_fd, directory_identity, path.parent)
    finally:
        os.close(directory_fd)


def create_unique_directory(parent: Path, prefix: str) -> Path:
    parent_fd, parent_identity = open_verified_directory(parent)
    try:
        for _ in range(100):
            directory_name = f"{prefix}{os.urandom(12).hex()}"
            try:
                os.mkdir(directory_name, mode=0o700, dir_fd=parent_fd)
            except FileExistsError:
                continue
            verify_open_directory(parent_fd, parent_identity, parent)
            return parent / directory_name
    finally:
        os.close(parent_fd)
    raise TaskRuntimeError(f"Unable to create a unique directory inside: {parent}")


def remove_directory_no_follow(path: Path) -> None:
    parent_fd, parent_identity = open_verified_directory(path.parent)
    try:
        verify_open_directory(parent_fd, parent_identity, path.parent)
        os.rmdir(path.name, dir_fd=parent_fd)
        verify_open_directory(parent_fd, parent_identity, path.parent)
    finally:
        os.close(parent_fd)


def replace_path_atomically(source: Path, destination: Path) -> None:
    source_fd, source_identity = open_verified_directory(source.parent)
    if source.parent == destination.parent:
        destination_fd = source_fd
        destination_identity = source_identity
        close_destination_fd = False
    else:
        destination_fd, destination_identity = open_verified_directory(destination.parent)
        close_destination_fd = True
    try:
        verify_open_directory(source_fd, source_identity, source.parent)
        verify_open_directory(destination_fd, destination_identity, destination.parent)
        os.replace(
            source.name,
            destination.name,
            src_dir_fd=source_fd,
            dst_dir_fd=destination_fd,
        )
        verify_open_directory(source_fd, source_identity, source.parent)
        verify_open_directory(destination_fd, destination_identity, destination.parent)
    finally:
        if close_destination_fd:
            os.close(destination_fd)
        os.close(source_fd)


def move_path_no_replace(source: Path, destination: Path) -> None:
    source_fd, source_identity = open_verified_directory(source.parent)
    if source.parent == destination.parent:
        destination_fd = source_fd
        destination_identity = source_identity
        close_destination_fd = False
    else:
        destination_fd, destination_identity = open_verified_directory(destination.parent)
        close_destination_fd = True
    destination_created = False
    source_removed = False
    try:
        source_stat = os.stat(source.name, dir_fd=source_fd, follow_symlinks=False)
        if not stat.S_ISREG(source_stat.st_mode) or source_stat.st_nlink != 1:
            raise TaskRuntimeError(f"Source must be a single-link regular file: {source}")
        source_file_identity = file_identity(source_stat)
        verify_open_directory(source_fd, source_identity, source.parent)
        verify_open_directory(destination_fd, destination_identity, destination.parent)
        os.link(
            source.name,
            destination.name,
            src_dir_fd=source_fd,
            dst_dir_fd=destination_fd,
            follow_symlinks=False,
        )
        destination_created = True
        linked_stat = os.stat(
            destination.name,
            dir_fd=destination_fd,
            follow_symlinks=False,
        )
        linked_identity = file_identity(linked_stat)
        if (
            linked_identity.device != source_file_identity.device
            or linked_identity.inode != source_file_identity.inode
        ):
            raise TaskRuntimeError("No-replace move linked an unexpected file identity")
        os.unlink(source.name, dir_fd=source_fd)
        source_removed = True
        os.fsync(source_fd)
        if destination_fd != source_fd:
            os.fsync(destination_fd)
        verify_open_directory(source_fd, source_identity, source.parent)
        verify_open_directory(destination_fd, destination_identity, destination.parent)
    except BaseException:
        if destination_created:
            try:
                if source_removed and not directory_entry_exists(source_fd, source.name):
                    os.link(
                        destination.name,
                        source.name,
                        src_dir_fd=destination_fd,
                        dst_dir_fd=source_fd,
                        follow_symlinks=False,
                    )
                os.unlink(destination.name, dir_fd=destination_fd)
                os.fsync(destination_fd)
                if destination_fd != source_fd:
                    os.fsync(source_fd)
            except OSError:
                pass
        raise
    finally:
        if close_destination_fd:
            os.close(destination_fd)
        os.close(source_fd)


@contextmanager
def task_operation_lock(paths: TaskPaths) -> Iterator[TaskOperationLock]:
    ensure_safe_directory(paths.root, paths.lock_root, "lock")
    if paths.lock_path.exists() and paths.lock_path.is_symlink():
        raise TaskRuntimeError(f"Task lock path must not be a symlink: {paths.lock_path}")
    directory_fd, directory_identity = open_verified_directory(paths.lock_root)
    flags = os.O_CREAT | os.O_RDWR
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    file_descriptor = os.open(paths.lock_path.name, flags, 0o600, dir_fd=directory_fd)
    try:
        lock_stat = os.fstat(file_descriptor)
        if not stat.S_ISREG(lock_stat.st_mode) or lock_stat.st_nlink != 1:
            raise TaskRuntimeError(f"Task lock must be a single-link regular file: {paths.lock_path}")
        fcntl.flock(file_descriptor, fcntl.LOCK_EX)
        operation_lock = TaskOperationLock(
            file_descriptor=file_descriptor,
            lock_file_identity=file_identity(lock_stat),
            directory_fd=directory_fd,
            directory_identity=directory_identity,
            lock_path=paths.lock_path,
        )
        verify_task_operation_lock(operation_lock)
        try:
            yield operation_lock
        finally:
            verify_task_operation_lock(operation_lock)
    finally:
        fcntl.flock(file_descriptor, fcntl.LOCK_UN)
        os.close(file_descriptor)
        os.close(directory_fd)


def task_paths(root: Path, task: str) -> TaskPaths:
    validate_task_slug(task)
    resolved_root = root.resolve()
    task_root = resolved_root / ".codestable/tasks"
    active_root = task_root / "active"
    archived_root = task_root / "archived"
    tombstone_root = task_root / "tombstones"
    staging_root = task_root / "staging"
    conflict_root = task_root / "conflicts"
    lock_root = task_root / "locks"
    paths = TaskPaths(
        root=resolved_root,
        task=task,
        task_root=task_root,
        active_root=active_root,
        archived_root=archived_root,
        tombstone_root=tombstone_root,
        staging_root=staging_root,
        conflict_root=conflict_root,
        lock_root=lock_root,
        active_path=active_root / f"{task}.md",
        tombstone_path=tombstone_root / f"{task}.json",
        staging_path=staging_root / f"{task}.md",
        conflict_path=conflict_root / f"{task}.md",
        lock_path=lock_root / f"{task}.lock",
    )
    ensure_canonical_path(paths.active_path, paths.active_root, "active")
    ensure_canonical_path(paths.tombstone_path, paths.tombstone_root, "tombstone")
    ensure_canonical_path(paths.staging_path, paths.staging_root, "staging")
    ensure_canonical_path(paths.lock_path, paths.lock_root, "lock")
    ensure_no_symlink_components(paths.root, paths.archived_root, "archived")
    ensure_no_symlink_components(paths.root, paths.conflict_root, "conflict")
    return paths


def find_archived_task_paths(paths: TaskPaths) -> list[Path]:
    if not paths.archived_root.exists():
        return []
    matches: list[Path] = []
    for name in list_directory_names_no_follow(paths.archived_root):
        match = ARCHIVED_TASK_FILE_PATTERN.fullmatch(name)
        if match is None or match.group("task") != paths.task:
            continue
        validate_archive_date(match.group("archive_date"))
        if not is_regular_file_no_follow(paths.archived_root, name):
            raise TaskRuntimeError(f"Archived Task must be a regular file: {name}")
        archived_path = paths.archived_root / name
        ensure_canonical_path(archived_path, paths.archived_root, "archived")
        matches.append(archived_path)
    return matches


def find_task_conflict_paths(paths: TaskPaths) -> list[Path]:
    if not paths.conflict_root.exists():
        return []
    matches: list[Path] = []
    for name in list_directory_names_no_follow(paths.conflict_root):
        if not name.startswith(f"{paths.task}-") or not name.endswith(".md"):
            continue
        if not is_regular_file_no_follow(paths.conflict_root, name):
            raise TaskRuntimeError(f"Task conflict must be a regular file: {name}")
        matches.append(paths.conflict_root / name)
    return matches


def list_directory_names_no_follow(directory: Path) -> list[str]:
    directory_fd, directory_identity = open_verified_directory(directory)
    try:
        names = sorted(os.listdir(directory_fd))
        verify_open_directory(directory_fd, directory_identity, directory)
        return names
    finally:
        os.close(directory_fd)


def is_regular_file_no_follow(directory: Path, name: str) -> bool:
    directory_fd, directory_identity = open_verified_directory(directory)
    try:
        entry_stat = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        verify_open_directory(directory_fd, directory_identity, directory)
        return stat.S_ISREG(entry_stat.st_mode)
    finally:
        os.close(directory_fd)


def calculate_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in pairs:
        if key in payload:
            raise TaskRuntimeError(f"Task tombstone contains duplicate field: {key}")
        payload[key] = value
    return payload


def reject_nonfinite_json_constant(value: str) -> object:
    raise TaskRuntimeError(f"Task tombstone contains invalid JSON constant: {value}")


def read_tombstone(paths: TaskPaths) -> dict[str, object] | None:
    if not paths.tombstone_path.exists():
        return None
    try:
        payload = json.loads(
            read_bytes_no_follow(paths.tombstone_path).decode("utf-8"),
            object_pairs_hook=reject_duplicate_json_keys,
            parse_constant=reject_nonfinite_json_constant,
        )
    except json.JSONDecodeError as error:
        raise TaskRuntimeError(f"Invalid task tombstone JSON: {paths.tombstone_path}") from error
    if not isinstance(payload, dict):
        raise TaskRuntimeError(f"Invalid task tombstone payload: {paths.tombstone_path}")
    return payload


def write_bytes_atomically(path: Path, content: bytes) -> None:
    directory_fd, directory_identity = open_verified_directory(path.parent)
    temporary_name = f".{path.name}.{os.urandom(12).hex()}"
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    file_descriptor = os.open(temporary_name, flags, 0o600, dir_fd=directory_fd)
    try:
        with os.fdopen(file_descriptor, "wb") as temporary_file:
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        verify_open_directory(directory_fd, directory_identity, path.parent)
        os.replace(
            temporary_name,
            path.name,
            src_dir_fd=directory_fd,
            dst_dir_fd=directory_fd,
        )
        os.fsync(directory_fd)
        verify_open_directory(directory_fd, directory_identity, path.parent)
    finally:
        try:
            os.unlink(temporary_name, dir_fd=directory_fd)
        except FileNotFoundError:
            pass
        os.close(directory_fd)


def write_json_atomically(path: Path, payload: dict[str, object]) -> None:
    serialized = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    write_bytes_atomically(path, serialized)


def write_bytes_exclusive(path: Path, content: bytes, temporary_label: str = "claim") -> None:
    directory_fd, directory_identity = open_verified_directory(path.parent)
    temporary_name = f".{path.name}.{temporary_label}-{os.urandom(12).hex()}"
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    file_descriptor = os.open(temporary_name, flags, 0o600, dir_fd=directory_fd)
    committed_identity: FileIdentity | None = None
    try:
        with os.fdopen(file_descriptor, "wb") as temporary_file:
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        committed_identity = file_identity(
            os.stat(temporary_name, dir_fd=directory_fd, follow_symlinks=False)
        )
        verify_open_directory(directory_fd, directory_identity, path.parent)
        try:
            os.link(
                temporary_name,
                path.name,
                src_dir_fd=directory_fd,
                dst_dir_fd=directory_fd,
                follow_symlinks=False,
            )
        except FileExistsError:
            raise
        os.fsync(directory_fd)
        try:
            verify_open_directory(directory_fd, directory_identity, path.parent)
        except TaskRuntimeError:
            try:
                target_stat = os.stat(
                    path.name,
                    dir_fd=directory_fd,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                target_stat = None
            if target_stat is not None:
                target_identity = file_identity(target_stat)
                if (
                    committed_identity is not None
                    and target_identity.device == committed_identity.device
                    and target_identity.inode == committed_identity.inode
                ):
                    os.unlink(path.name, dir_fd=directory_fd)
                    os.fsync(directory_fd)
            raise
    finally:
        removed_temporary = False
        try:
            os.unlink(temporary_name, dir_fd=directory_fd)
            removed_temporary = True
        except FileNotFoundError:
            pass
        if removed_temporary:
            os.fsync(directory_fd)
        os.close(directory_fd)


def write_json_exclusive(path: Path, payload: dict[str, object]) -> None:
    """Create ``path`` with the given JSON payload atomically and exclusively."""
    serialized = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    write_bytes_exclusive(path, serialized, temporary_label="claim")


def read_regular_file_from_directory(
    directory_fd: int,
    filename: str,
) -> tuple[bytes, FileIdentity]:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    file_descriptor = os.open(filename, flags, dir_fd=directory_fd)
    try:
        initial_stat = os.fstat(file_descriptor)
        if not stat.S_ISREG(initial_stat.st_mode) or initial_stat.st_nlink != 1:
            raise TaskRuntimeError(f"Task file must be a single-link regular file: {filename}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(file_descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        final_stat = os.fstat(file_descriptor)
        initial_identity = file_identity(initial_stat)
        final_identity = file_identity(final_stat)
        if final_identity != initial_identity:
            raise TaskRuntimeError(f"Task file changed while being read: {filename}")
        return b"".join(chunks), final_identity
    finally:
        os.close(file_descriptor)


def write_temporary_file(
    directory_fd: int,
    filename_prefix: str,
    content: bytes,
) -> tuple[str, FileIdentity]:
    temporary_name = f".{filename_prefix}.{os.urandom(12).hex()}"
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    file_descriptor = os.open(temporary_name, flags, 0o600, dir_fd=directory_fd)
    try:
        with os.fdopen(file_descriptor, "wb") as temporary_file:
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        return temporary_name, file_identity(
            os.stat(temporary_name, dir_fd=directory_fd, follow_symlinks=False)
        )
    except BaseException:
        try:
            os.unlink(temporary_name, dir_fd=directory_fd)
        except FileNotFoundError:
            pass
        raise


def directory_entry_exists(directory_fd: int, filename: str) -> bool:
    try:
        os.stat(filename, dir_fd=directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    return True


def restore_quarantined_active(
    active_fd: int,
    quarantine_fd: int,
    active_name: str,
) -> None:
    if directory_entry_exists(active_fd, active_name):
        return
    try:
        os.link(
            active_name,
            active_name,
            src_dir_fd=quarantine_fd,
            dst_dir_fd=active_fd,
            follow_symlinks=False,
        )
    except FileExistsError:
        return
    os.unlink(active_name, dir_fd=quarantine_fd)


def preserve_quarantined_active_conflict(
    paths: TaskPaths,
    quarantine_fd: int,
) -> Path:
    ensure_safe_directory(paths.root, paths.conflict_root, "conflict")
    conflict_fd, conflict_identity = open_verified_directory(paths.conflict_root)
    conflict_name = f"{paths.task}-cas-{os.urandom(12).hex()}.md"
    try:
        os.link(
            paths.active_path.name,
            conflict_name,
            src_dir_fd=quarantine_fd,
            dst_dir_fd=conflict_fd,
            follow_symlinks=False,
        )
        os.unlink(paths.active_path.name, dir_fd=quarantine_fd)
        os.fsync(conflict_fd)
        verify_open_directory(
            conflict_fd,
            conflict_identity,
            paths.conflict_root,
        )
    finally:
        os.close(conflict_fd)
    return paths.conflict_root / conflict_name


def compare_and_swap_active_task(
    paths: TaskPaths,
    new_content: bytes,
    expected_sha256: str,
    operation_lock: TaskOperationLock,
) -> None:
    active_fd, active_identity = open_verified_directory(paths.active_root)
    quarantine_name = f".task-cas-{os.urandom(12).hex()}"
    quarantine_fd: int | None = None
    temporary_name: str | None = None
    moved_existing = False
    committed_identity: FileIdentity | None = None
    try:
        verify_task_operation_lock(operation_lock)
        current_content, _ = read_regular_file_from_directory(active_fd, paths.active_path.name)
        current_sha256 = calculate_sha256(current_content)
        if current_sha256 != expected_sha256:
            raise TaskRuntimeError(
                f"Active Task compare-and-swap conflict: expected {expected_sha256}, "
                f"found {current_sha256}"
            )

        os.mkdir(quarantine_name, mode=0o700, dir_fd=active_fd)
        quarantine_fd = open_directory_component(
            active_fd,
            quarantine_name,
            paths.active_root / quarantine_name,
        )
        verify_open_directory(active_fd, active_identity, paths.active_root)
        verify_task_operation_lock(operation_lock)
        os.replace(
            paths.active_path.name,
            paths.active_path.name,
            src_dir_fd=active_fd,
            dst_dir_fd=quarantine_fd,
        )
        moved_existing = True

        captured_content, _ = read_regular_file_from_directory(
            quarantine_fd,
            paths.active_path.name,
        )
        captured_sha256 = calculate_sha256(captured_content)
        if captured_sha256 != expected_sha256:
            raise TaskRuntimeError(
                f"Active Task compare-and-swap conflict: expected {expected_sha256}, "
                f"captured {captured_sha256}"
            )

        temporary_name, committed_identity = write_temporary_file(
            active_fd,
            paths.active_path.name,
            new_content,
        )
        verify_open_directory(active_fd, active_identity, paths.active_root)
        verify_task_operation_lock(operation_lock)
        try:
            os.link(
                temporary_name,
                paths.active_path.name,
                src_dir_fd=active_fd,
                dst_dir_fd=active_fd,
                follow_symlinks=False,
            )
        except FileExistsError as error:
            raise TaskRuntimeError(
                "Active Task compare-and-swap conflict: a concurrent writer recreated the active Task"
            ) from error
        os.unlink(temporary_name, dir_fd=active_fd)
        temporary_name = None
        os.fsync(active_fd)
        try:
            verify_open_directory(active_fd, active_identity, paths.active_root)
            verify_task_operation_lock(operation_lock)
        except TaskRuntimeError:
            target_stat = os.stat(
                paths.active_path.name,
                dir_fd=active_fd,
                follow_symlinks=False,
            )
            target_identity = file_identity(target_stat)
            if (
                committed_identity is not None
                and target_identity.device == committed_identity.device
                and target_identity.inode == committed_identity.inode
            ):
                os.unlink(paths.active_path.name, dir_fd=active_fd)
            restore_quarantined_active(
                active_fd,
                quarantine_fd,
                paths.active_path.name,
            )
            raise

        os.unlink(paths.active_path.name, dir_fd=quarantine_fd)
        moved_existing = False
        os.rmdir(quarantine_name, dir_fd=active_fd)
        os.fsync(active_fd)
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name, dir_fd=active_fd)
            except FileNotFoundError:
                pass
        if moved_existing and quarantine_fd is not None:
            if directory_entry_exists(active_fd, paths.active_path.name):
                try:
                    preserve_quarantined_active_conflict(paths, quarantine_fd)
                except (FileNotFoundError, TaskRuntimeError):
                    pass
            else:
                restore_quarantined_active(active_fd, quarantine_fd, paths.active_path.name)
        if quarantine_fd is not None:
            os.close(quarantine_fd)
        try:
            os.rmdir(quarantine_name, dir_fd=active_fd)
        except OSError:
            pass
        os.close(active_fd)


def create_active_task_exclusively(
    paths: TaskPaths,
    content: bytes,
    operation_lock: TaskOperationLock,
) -> None:
    active_fd, active_identity = open_verified_directory(paths.active_root)
    temporary_name: str | None = None
    committed_identity: FileIdentity | None = None
    try:
        temporary_name, committed_identity = write_temporary_file(
            active_fd,
            paths.active_path.name,
            content,
        )
        verify_open_directory(active_fd, active_identity, paths.active_root)
        verify_task_operation_lock(operation_lock)
        try:
            os.link(
                temporary_name,
                paths.active_path.name,
                src_dir_fd=active_fd,
                dst_dir_fd=active_fd,
                follow_symlinks=False,
            )
        except FileExistsError as error:
            raise TaskRuntimeError(
                "Active Task create conflict: a concurrent writer created the active Task"
            ) from error
        os.unlink(temporary_name, dir_fd=active_fd)
        temporary_name = None
        os.fsync(active_fd)
        try:
            verify_open_directory(active_fd, active_identity, paths.active_root)
            verify_task_operation_lock(operation_lock)
        except TaskRuntimeError:
            try:
                target_stat = os.stat(
                    paths.active_path.name,
                    dir_fd=active_fd,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                target_stat = None
            if target_stat is not None:
                target_identity = file_identity(target_stat)
                if (
                    committed_identity is not None
                    and target_identity.device == committed_identity.device
                    and target_identity.inode == committed_identity.inode
                ):
                    os.unlink(paths.active_path.name, dir_fd=active_fd)
                    os.fsync(active_fd)
            raise
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name, dir_fd=active_fd)
            except FileNotFoundError:
                pass
        os.close(active_fd)


def parse_frontmatter_fields(content: str) -> dict[str, object]:
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        raise TaskRuntimeError("Task file must start with YAML frontmatter")
    try:
        parsed = load_yaml_text(match.group("frontmatter"))
    except (ValueError, RuntimeError) as error:
        raise TaskRuntimeError(f"Task frontmatter YAML is invalid: {error}") from error
    if not isinstance(parsed, dict) or any(not isinstance(key, str) for key in parsed):
        raise TaskRuntimeError("Task frontmatter must be a mapping with string keys")
    return parsed


def validate_task_content(
    content: str,
    task: str,
    allowed_statuses: frozenset[str],
) -> dict[str, object]:
    fields = parse_frontmatter_fields(content)
    missing_fields = sorted(TASK_REQUIRED_FIELDS - fields.keys())
    if missing_fields:
        raise TaskRuntimeError(
            f"Task frontmatter is missing required fields: {', '.join(missing_fields)}"
        )
    unknown_fields = sorted(fields.keys() - TASK_REQUIRED_FIELDS)
    if unknown_fields:
        raise TaskRuntimeError(
            f"Task frontmatter contains unknown fields: {', '.join(unknown_fields)}"
        )
    if fields.get("doc_type") != "task-list":
        raise TaskRuntimeError("Task frontmatter doc_type must be task-list")
    if fields.get("task") != task:
        raise TaskRuntimeError(f"Task frontmatter task must equal {task!r}")
    status = fields.get("status", "")
    if not isinstance(status, str):
        raise TaskRuntimeError("Task frontmatter status must be a string")
    if status not in allowed_statuses:
        allowed = ", ".join(sorted(allowed_statuses))
        raise TaskRuntimeError(f"Task status must be one of: {allowed}")
    for field_name in ("doc_type", "task", "goal", "status", "workflow", "owner_skill"):
        if type(fields.get(field_name)) is not str or not fields.get(field_name):
            raise TaskRuntimeError(f"Task frontmatter {field_name} must not be empty")
    for field_name in ("created", "updated"):
        field_value = fields.get(field_name)
        if type(field_value) is not date:
            raise TaskRuntimeError(f"Task frontmatter {field_name} must be an ISO date")
    archived_value = fields["archived"]
    if status == "archived":
        if type(archived_value) is not date:
            raise TaskRuntimeError("Archived Task must record a valid archived date")
    elif archived_value is not None:
        raise TaskRuntimeError("Active Task frontmatter archived must be null")
    section_positions: list[int] = []
    for heading in TASK_SECTION_HEADINGS:
        if content.count(heading) != 1:
            raise TaskRuntimeError(f"Task body must contain exactly one section: {heading}")
        section_positions.append(content.index(heading))
    if section_positions != sorted(section_positions):
        raise TaskRuntimeError(
            "Task body required sections must appear in canonical order"
        )
    related_docs = fields.get("related_docs")
    if type(related_docs) is not list or not all(
        type(related_path) is str and related_path for related_path in related_docs
    ):
        raise TaskRuntimeError("Task frontmatter related_docs must be a list of paths")
    status_match = CURRENT_STATUS_PATTERN.search(content)
    if not status_match or status_match.group(2).strip() != status:
        raise TaskRuntimeError("Task body current status must match frontmatter status")
    return fields


def expected_tombstone_paths(paths: TaskPaths, archived_date: str) -> tuple[str, str]:
    archived_path = paths.archived_root / f"{archived_date}-{paths.task}.md"
    return relative_path(archived_path, paths.root), relative_path(paths.staging_path, paths.root)


def validate_tombstone_payload(
    paths: TaskPaths,
    payload: dict[str, object],
    expected_state: str | None = None,
) -> dict[str, object]:
    state = payload.get("state")
    if expected_state is not None and state != expected_state:
        raise TaskRuntimeError(f"Task tombstone state must be {expected_state!r}")
    if state not in BLOCKING_TOMBSTONE_STATES:
        raise TaskRuntimeError(f"Task tombstone has invalid state: {state!r}")
    expected_fields = (
        ARCHIVED_TOMBSTONE_FIELDS if state == "archived" else ARCHIVING_TOMBSTONE_FIELDS
    )
    actual_fields = frozenset(payload)
    if actual_fields != expected_fields:
        missing_fields = sorted(expected_fields - actual_fields)
        unknown_fields = sorted(actual_fields - expected_fields)
        details: list[str] = []
        if missing_fields:
            details.append(f"missing fields: {', '.join(missing_fields)}")
        if unknown_fields:
            details.append(f"unknown fields: {', '.join(unknown_fields)}")
        raise TaskRuntimeError(f"Task tombstone schema is invalid ({'; '.join(details)})")
    if payload.get("task") != paths.task:
        raise TaskRuntimeError("Task tombstone task does not match the requested Task")
    source_status = payload.get("source_status")
    if source_status not in ARCHIVABLE_STATUSES:
        raise TaskRuntimeError("Task tombstone source_status is invalid")
    source_sha256 = payload.get("source_sha256")
    if not isinstance(source_sha256, str) or not SHA256_PATTERN.fullmatch(source_sha256):
        raise TaskRuntimeError("Task tombstone source_sha256 is invalid")
    archived_date = payload.get("archived_date")
    if not isinstance(archived_date, str):
        raise TaskRuntimeError("Task tombstone archived_date is missing")
    validate_archive_date(archived_date)
    expected_archived_path, expected_staging_path = expected_tombstone_paths(paths, archived_date)
    if payload.get("archived_path") != expected_archived_path:
        raise TaskRuntimeError("Task tombstone archived_path is not canonical")
    if payload.get("staging_path") != expected_staging_path:
        raise TaskRuntimeError("Task tombstone staging_path is not canonical")
    archived_sha256 = payload.get("archived_sha256")
    if state == "archived":
        if not isinstance(archived_sha256, str) or not SHA256_PATTERN.fullmatch(archived_sha256):
            raise TaskRuntimeError("Completed tombstone archived_sha256 is invalid")
    elif archived_sha256 is not None:
        raise TaskRuntimeError("Archiving tombstone must not contain archived_sha256")
    return payload


def replace_frontmatter_field(content: str, field: str, value: str) -> str:
    pattern = re.compile(FIELD_PATTERN_TEMPLATE.format(field=re.escape(field)))
    updated_content, replacement_count = pattern.subn(rf"\g<prefix>{value}", content, count=1)
    if replacement_count != 1:
        raise TaskRuntimeError(f"Task frontmatter is missing required field: {field}")
    return updated_content


def prepare_archived_content(content: str, archive_date: str) -> str:
    updated_content = replace_frontmatter_field(content, "status", "archived")
    updated_content = replace_frontmatter_field(updated_content, "archived", archive_date)
    updated_content, replacement_count = CURRENT_STATUS_PATTERN.subn(
        rf"\g<1>archived",
        updated_content,
        count=1,
    )
    if replacement_count != 1:
        raise TaskRuntimeError("Task body is missing the current status section")
    return updated_content


def ensure_active_write_is_allowed(paths: TaskPaths) -> None:
    tombstone = read_tombstone(paths)
    if tombstone is not None:
        validate_tombstone_payload(paths, tombstone)
        raise TaskRuntimeError(
            f"Refusing active write for {paths.task!r}: archived tombstone exists at "
            f"{relative_path(paths.tombstone_path, paths.root)}"
        )
    archived_paths = find_archived_task_paths(paths)
    if archived_paths:
        archived_locations = ", ".join(relative_path(path, paths.root) for path in archived_paths)
        raise TaskRuntimeError(
            f"Refusing active write for {paths.task!r}: archived Task already exists at {archived_locations}"
        )


def write_active_task(
    root: Path,
    task: str,
    content_path: Path,
    expected_sha256: str | None = None,
) -> Path:
    paths = task_paths(root, task)
    with task_operation_lock(paths) as operation_lock:
        ensure_active_write_is_allowed(paths)
        content = content_path.read_text(encoding="utf-8")
        new_fields = validate_task_content(content, task, ACTIVE_STATUSES)
        if paths.active_path.exists():
            ensure_canonical_path(paths.active_path, paths.active_root, "active")
            if expected_sha256 is None:
                raise TaskRuntimeError(
                    "Updating an existing active Task requires --expected-sha256"
                )
            if not SHA256_PATTERN.fullmatch(expected_sha256):
                raise TaskRuntimeError("expected_sha256 must be a lowercase SHA-256 digest")
            current_content = read_bytes_no_follow(paths.active_path)
            current_sha256 = calculate_sha256(current_content)
            if current_sha256 != expected_sha256:
                raise TaskRuntimeError(
                    f"Active Task compare-and-swap conflict: expected {expected_sha256}, "
                    f"found {current_sha256}"
                )
            current_fields = validate_task_content(
                current_content.decode("utf-8"),
                task,
                ACTIVE_STATUSES,
            )
            old_status = current_fields["status"]
            new_status = new_fields["status"]
            if new_status not in ACTIVE_STATUS_TRANSITIONS[old_status]:
                raise TaskRuntimeError(
                    f"Invalid task status transition: {old_status} -> {new_status}"
                )
        elif expected_sha256 is not None:
            raise TaskRuntimeError("Cannot use --expected-sha256 when creating a new active Task")
        ensure_safe_directory(paths.root, paths.active_root, "active")
        ensure_canonical_path(paths.active_path, paths.active_root, "active")
        content_bytes = content.encode("utf-8")
        if expected_sha256 is None:
            create_active_task_exclusively(paths, content_bytes, operation_lock)
        else:
            compare_and_swap_active_task(
                paths,
                content_bytes,
                expected_sha256,
                operation_lock,
            )
    return paths.active_path


def archived_path_from_tombstone(paths: TaskPaths, tombstone: dict[str, object]) -> Path:
    validate_tombstone_payload(paths, tombstone)
    archived_date = str(tombstone["archived_date"])
    archived_path = paths.archived_root / f"{archived_date}-{paths.task}.md"
    ensure_canonical_path(archived_path, paths.archived_root, "archived")
    return archived_path


def archive_integrity_findings(
    paths: TaskPaths,
    tombstone: dict[str, object] | None,
    *,
    include_active: bool,
) -> list[RuntimeFinding]:
    findings: list[RuntimeFinding] = []
    archived_paths = find_archived_task_paths(paths)
    if tombstone is None:
        historical_archive = False
        if len(archived_paths) == 1:
            match = ARCHIVED_TASK_FILE_PATTERN.fullmatch(archived_paths[0].name)
            historical_archive = bool(
                match
                and date.fromisoformat(match.group("archive_date"))
                < TOMBSTONE_REQUIRED_FROM_DATE
            )
        if historical_archive:
            archived_path = archived_paths[0]
            archived_date = archived_path.name[:10]
            try:
                archived_fields = validate_task_content(
                    read_bytes_no_follow(archived_path).decode("utf-8"),
                    paths.task,
                    frozenset({"archived"}),
                )
            except (UnicodeError, TaskRuntimeError) as error:
                findings.append(
                    RuntimeFinding(
                        code="invalid-historical-archived-task",
                        message=str(error),
                        path=relative_path(archived_path, paths.root),
                    )
                )
            else:
                archived_frontmatter_date = archived_fields.get("archived")
                if (
                    not isinstance(archived_frontmatter_date, date)
                    or archived_frontmatter_date.isoformat() != archived_date
                ):
                    findings.append(
                        RuntimeFinding(
                            code="historical-archive-date-mismatch",
                            message="Historical archived Task date does not match its filename",
                            path=relative_path(archived_path, paths.root),
                        )
                    )
            if paths.active_path.exists():
                findings.append(
                    RuntimeFinding(
                        code="historical-active-archive-conflict",
                        message="Historical archived Task has a conflicting active Task",
                        path=relative_path(paths.active_path, paths.root),
                    )
                )
        elif archived_paths:
            findings.append(
                RuntimeFinding(
                    code="missing-archive-tombstone",
                    message="Archived Task exists without a completed tombstone",
                    path=relative_path(archived_paths[0], paths.root),
                )
            )
        if paths.staging_path.exists():
            findings.append(
                RuntimeFinding(
                    code="orphaned-archive-staging",
                    message="Staging Task exists without a recoverable archiving tombstone",
                    path=relative_path(paths.staging_path, paths.root),
                )
            )
        conflict_paths = find_task_conflict_paths(paths)
        if conflict_paths:
            findings.append(
                RuntimeFinding(
                    code="unresolved-task-conflict",
                    message="Task has unresolved preserved conflict evidence",
                    path=relative_path(conflict_paths[0], paths.root),
                )
            )
        return findings

    try:
        validate_tombstone_payload(paths, tombstone, expected_state="archived")
    except TaskRuntimeError as error:
        findings.append(
            RuntimeFinding(
                code="invalid-archive-tombstone",
                message=str(error),
                path=relative_path(paths.tombstone_path, paths.root),
            )
        )
        return findings

    archived_date = str(tombstone["archived_date"])

    if len(archived_paths) != 1:
        findings.append(
            RuntimeFinding(
                code="archive-target-count-invalid",
                message="Task must have exactly one archived canonical document",
                path=relative_path(paths.archived_root, paths.root),
            )
        )
        return findings

    archived_path = archived_paths[0]
    expected_archived_path = paths.archived_root / f"{archived_date}-{paths.task}.md"
    raw_archived_path = tombstone.get("archived_path")
    expected_relative_path = relative_path(expected_archived_path, paths.root)
    if raw_archived_path != expected_relative_path or archived_path != expected_archived_path:
        findings.append(
            RuntimeFinding(
                code="archived-target-path-mismatch",
                message="Archived tombstone path does not match the canonical archive target",
                path=relative_path(archived_path, paths.root),
            )
        )
        return findings

    try:
        archived_fields = validate_task_content(
            archived_path.read_text(encoding="utf-8"),
            paths.task,
            frozenset({"archived"}),
        )
    except (OSError, UnicodeError, TaskRuntimeError):
        findings.append(
            RuntimeFinding(
                code="invalid-archived-task-document",
                message="Archived target is not a valid archived Task document",
                path=relative_path(archived_path, paths.root),
            )
        )
        return findings
    archived_frontmatter_date = archived_fields.get("archived")
    if (
        not isinstance(archived_frontmatter_date, date)
        or archived_frontmatter_date.isoformat() != archived_date
    ):
        findings.append(
            RuntimeFinding(
                code="archived-date-mismatch",
                message="Archived Task frontmatter date does not match the tombstone",
                path=relative_path(archived_path, paths.root),
            )
        )

    expected_archived_sha256 = tombstone.get("archived_sha256")
    actual_archived_sha256 = calculate_sha256(read_bytes_no_follow(archived_path))
    if (
        not isinstance(expected_archived_sha256, str)
        or not SHA256_PATTERN.fullmatch(expected_archived_sha256)
        or actual_archived_sha256 != expected_archived_sha256
    ):
        findings.append(
            RuntimeFinding(
                code="archived-target-integrity-failed",
                message="Archived target does not match the completed tombstone snapshot",
                path=relative_path(archived_path, paths.root),
            )
        )
    if include_active and paths.active_path.exists():
        findings.append(
            RuntimeFinding(
                code="active-residue-present",
                message="Archived Task still has an active residue",
                path=relative_path(paths.active_path, paths.root),
            )
        )
    if paths.staging_path.exists():
        findings.append(
            RuntimeFinding(
                code="archive-staging-residue",
                message="Completed archive still has a staging residue",
                path=relative_path(paths.staging_path, paths.root),
            )
        )
    conflict_paths = find_task_conflict_paths(paths)
    if conflict_paths:
        findings.append(
            RuntimeFinding(
                code="unresolved-task-conflict",
                message="Task has unresolved preserved conflict evidence",
                path=relative_path(conflict_paths[0], paths.root),
            )
        )
    return findings


def inspect_archived_task(root: Path, task: str) -> ArchiveInspection:
    paths = task_paths(root, task)
    try:
        tombstone = read_tombstone(paths)
        archived_paths = find_archived_task_paths(paths)
    except TaskRuntimeError as error:
        finding = RuntimeFinding(
            code="archive-inspection-failed",
            message=str(error),
            path=relative_path(paths.task_root, paths.root),
        )
        return ArchiveInspection(
            task=task,
            state="invalid",
            archived_path=None,
            tombstone_path=relative_path(paths.tombstone_path, paths.root),
            task_status=None,
            workflow=None,
            owner_skill=None,
            related_docs=(),
            task_sha256=None,
            findings=(finding,),
        )

    findings = archive_integrity_findings(paths, tombstone, include_active=True)
    if tombstone is None and not archived_paths and not findings:
        state = "active" if paths.active_path.exists() else "missing"
        return ArchiveInspection(
            task=task,
            state=state,
            archived_path=None,
            tombstone_path=relative_path(paths.tombstone_path, paths.root),
            task_status=None,
            workflow=None,
            owner_skill=None,
            related_docs=(),
            task_sha256=None,
            findings=(),
        )

    if not findings and tombstone is None and archived_paths:
        state = "historical"
    else:
        state = "valid" if not findings else (
            "incomplete" if tombstone and tombstone.get("state") == "archiving" else "invalid"
        )
    archived_path = relative_path(archived_paths[0], paths.root) if len(archived_paths) == 1 else None
    task_status: str | None = None
    workflow: str | None = None
    owner_skill: str | None = None
    related_docs: tuple[str, ...] = ()
    task_sha256: str | None = None
    if state in {"valid", "historical"} and len(archived_paths) == 1:
        archived_content = read_bytes_no_follow(archived_paths[0])
        archived_fields = validate_task_content(
            archived_content.decode("utf-8"),
            task,
            frozenset({"archived"}),
        )
        task_status = str(archived_fields["status"])
        workflow = str(archived_fields["workflow"])
        owner_skill = str(archived_fields["owner_skill"])
        related_docs = tuple(str(path) for path in archived_fields["related_docs"])
        task_sha256 = calculate_sha256(archived_content)
    return ArchiveInspection(
        task=task,
        state=state,
        archived_path=archived_path,
        tombstone_path=relative_path(paths.tombstone_path, paths.root),
        task_status=task_status,
        workflow=workflow,
        owner_skill=owner_skill,
        related_docs=related_docs,
        task_sha256=task_sha256,
        findings=tuple(findings),
    )


def preserve_conflicting_residue(paths: TaskPaths, quarantine_path: Path) -> Path:
    ensure_safe_directory(paths.root, paths.conflict_root, "conflict")
    conflict_path = paths.conflict_root / f"{paths.task}-{os.urandom(12).hex()}.md"
    replace_path_atomically(quarantine_path, conflict_path)
    return conflict_path


def recover_finalized_archive_staging_locked(
    paths: TaskPaths,
    tombstone: dict[str, object],
) -> list[RuntimeFinding]:
    validate_tombstone_payload(paths, tombstone, expected_state="archived")
    if not paths.staging_path.exists():
        return []
    if paths.active_path.exists():
        return [
            RuntimeFinding(
                code="finalized-archive-staging-with-active",
                message="Finalized archive has both staging and active Task documents",
                path=relative_path(paths.staging_path, paths.root),
            )
        ]

    archived_path = archived_path_from_tombstone(paths, tombstone)
    if not archived_path.exists():
        return [
            RuntimeFinding(
                code="finalized-archive-staging-target-missing",
                message="Finalized archive staging cannot be verified because the archived target is missing",
                path=relative_path(paths.staging_path, paths.root),
            )
        ]
    staging_content = read_bytes_no_follow(paths.staging_path)
    if calculate_sha256(staging_content) != tombstone.get("source_sha256"):
        return [
            RuntimeFinding(
                code="finalized-archive-staging-source-mismatch",
                message="Finalized archive staging does not match the source snapshot",
                path=relative_path(paths.staging_path, paths.root),
            )
        ]
    try:
        staging_text = staging_content.decode("utf-8")
        validate_task_content(staging_text, paths.task, ARCHIVABLE_STATUSES)
        expected_archived_content = prepare_archived_content(
            staging_text,
            str(tombstone["archived_date"]),
        ).encode("utf-8")
    except (UnicodeError, TaskRuntimeError) as error:
        return [
            RuntimeFinding(
                code="finalized-archive-staging-invalid",
                message=str(error),
                path=relative_path(paths.staging_path, paths.root),
            )
        ]
    expected_archived_sha256 = str(tombstone["archived_sha256"])
    if (
        calculate_sha256(expected_archived_content) != expected_archived_sha256
        or calculate_sha256(read_bytes_no_follow(archived_path)) != expected_archived_sha256
    ):
        return [
            RuntimeFinding(
                code="finalized-archive-staging-target-mismatch",
                message="Finalized archive target does not match the verified staging transformation",
                path=relative_path(archived_path, paths.root),
            )
        ]
    unlink_no_follow(paths.staging_path)
    return []


def cleanup_archived_task_residue_locked(paths: TaskPaths) -> list[RuntimeFinding]:
    tombstone = read_tombstone(paths)
    if tombstone is None:
        return []
    validate_tombstone_payload(paths, tombstone)
    if tombstone.get("state") == "archiving":
        recovery_findings = recover_archiving_task_locked(paths, tombstone)
        if recovery_findings:
            return recovery_findings
        tombstone = read_tombstone(paths)
        if tombstone is None:
            return []
        validate_tombstone_payload(paths, tombstone, expected_state="archived")

    finalized_staging_findings = recover_finalized_archive_staging_locked(paths, tombstone)
    if finalized_staging_findings:
        return finalized_staging_findings

    integrity_findings = archive_integrity_findings(paths, tombstone, include_active=False)
    if integrity_findings:
        return integrity_findings
    if not paths.active_path.exists():
        return []

    expected_source_sha256 = tombstone.get("source_sha256")
    quarantine_directory = create_unique_directory(paths.active_root, ".task-quarantine-")
    try:
        quarantine_path = quarantine_directory / paths.active_path.name
        replace_path_atomically(paths.active_path, quarantine_path)
        active_sha256 = calculate_sha256(read_bytes_no_follow(quarantine_path))
        if isinstance(expected_source_sha256, str) and active_sha256 == expected_source_sha256:
            unlink_no_follow(quarantine_path)
            if paths.active_path.exists():
                return [
                    RuntimeFinding(
                        code="concurrent-active-residue",
                        message="A concurrent active Task rewrite appeared during stale residue cleanup",
                        path=relative_path(paths.active_path, paths.root),
                    )
                ]
            return []
        if not paths.active_path.exists():
            replace_path_atomically(quarantine_path, paths.active_path)
            return [
                RuntimeFinding(
                    code="divergent-active-residue",
                    message="Active residue differs from the archived source snapshot; manual resolution is required",
                    path=relative_path(paths.active_path, paths.root),
                )
            ]
        conflict_path = preserve_conflicting_residue(paths, quarantine_path)
        return [
            RuntimeFinding(
                code="divergent-active-conflict",
                message="Divergent residue and a concurrent active write were both preserved",
                path=relative_path(conflict_path, paths.root),
            )
        ]
    finally:
        try:
            remove_directory_no_follow(quarantine_directory)
        except OSError:
            pass


def cleanup_archived_task_residue(root: Path, task: str) -> list[RuntimeFinding]:
    paths = task_paths(root, task)
    with task_operation_lock(paths):
        return cleanup_archived_task_residue_locked(paths)


def recover_archiving_task_locked(
    paths: TaskPaths,
    tombstone: dict[str, object],
) -> list[RuntimeFinding]:
    try:
        validate_tombstone_payload(paths, tombstone, expected_state="archiving")
    except TaskRuntimeError as error:
        return [
            RuntimeFinding(
                code="incomplete-archive",
                message=str(error),
                path=relative_path(paths.tombstone_path, paths.root),
            )
        ]
    source_sha256 = str(tombstone["source_sha256"])
    archived_date = str(tombstone["archived_date"])
    try:
        archived_path = archived_path_from_tombstone(paths, tombstone)
    except TaskRuntimeError as error:
        return [
            RuntimeFinding(
                code="incomplete-archive",
                message=str(error),
                path=relative_path(paths.tombstone_path, paths.root),
            )
        ]

    active_exists = paths.active_path.exists()
    staging_exists = paths.staging_path.exists()
    archived_exists = archived_path.exists()
    if active_exists and not staging_exists and not archived_exists:
        if calculate_sha256(read_bytes_no_follow(paths.active_path)) == source_sha256:
            unlink_no_follow(paths.tombstone_path)
            return []
        return [
            RuntimeFinding(
                code="incomplete-archive",
                message="Active Task changed after the archiving tombstone was created",
                path=relative_path(paths.active_path, paths.root),
            )
        ]
    if staging_exists:
        if active_exists:
            return [
                RuntimeFinding(
                    code="incomplete-archive",
                    message="Both active and staging Task documents exist during recovery",
                    path=relative_path(paths.staging_path, paths.root),
                )
            ]
        staging_content = read_bytes_no_follow(paths.staging_path)
        if calculate_sha256(staging_content) != source_sha256:
            return [
                RuntimeFinding(
                    code="incomplete-archive",
                    message="Staging Task does not match the tombstone source snapshot",
                    path=relative_path(paths.staging_path, paths.root),
                )
            ]
        staging_text = staging_content.decode("utf-8")
        validate_task_content(staging_text, paths.task, ARCHIVABLE_STATUSES)
        archived_content = prepare_archived_content(staging_text, archived_date).encode("utf-8")
        if archived_exists and read_bytes_no_follow(archived_path) != archived_content:
            return [
                RuntimeFinding(
                    code="incomplete-archive",
                    message="Archived target conflicts with the recoverable staging snapshot",
                    path=relative_path(archived_path, paths.root),
                )
            ]
        if not archived_exists:
            ensure_safe_directory(paths.root, paths.archived_root, "archived")
            try:
                write_bytes_exclusive(
                    archived_path,
                    archived_content,
                    temporary_label="recovery",
                )
            except FileExistsError:
                if read_bytes_no_follow(archived_path) != archived_content:
                    return [
                        RuntimeFinding(
                            code="incomplete-archive",
                            message="Archived target appeared concurrently with conflicting content",
                            path=relative_path(archived_path, paths.root),
                        )
                    ]
        tombstone["state"] = "archived"
        tombstone["archived_sha256"] = calculate_sha256(archived_content)
        write_json_atomically(paths.tombstone_path, tombstone)
        unlink_no_follow(paths.staging_path)
        return []
    if archived_exists and not active_exists:
        return [
            RuntimeFinding(
                code="incomplete-archive",
                message="Archived-only recovery lacks the staging source snapshot and cannot be authenticated",
                path=relative_path(archived_path, paths.root),
            )
        ]
    return [
        RuntimeFinding(
            code="incomplete-archive",
            message="Archiving tombstone cannot be recovered from the current filesystem state",
            path=relative_path(paths.tombstone_path, paths.root),
        )
    ]


def scan_task_runtime(root: Path) -> list[RuntimeFinding]:
    resolved_root = root.resolve()
    task_root = resolved_root / ".codestable/tasks"
    findings: list[RuntimeFinding] = []
    task_slugs: set[str] = set()
    artifact_roots = {
        "active": (task_root / "active", ".md"),
        "tombstone": (task_root / "tombstones", ".json"),
        "staging": (task_root / "staging", ".md"),
    }
    for label, (artifact_root, suffix) in artifact_roots.items():
        if not artifact_root.exists():
            continue
        try:
            names = list_directory_names_no_follow(artifact_root)
        except TaskRuntimeError as error:
            findings.append(
                RuntimeFinding(
                    code="invalid-runtime-artifact-directory",
                    message=str(error),
                    path=relative_path(artifact_root, resolved_root),
                )
            )
            continue
        for name in names:
            artifact_path = artifact_root / name
            task = name[: -len(suffix)] if name.endswith(suffix) else ""
            if not task or not TASK_SLUG_PATTERN.fullmatch(task):
                findings.append(
                    RuntimeFinding(
                        code="invalid-runtime-artifact",
                        message=f"Invalid {label} Task artifact name",
                        path=relative_path(artifact_path, resolved_root),
                    )
                )
                continue
            if not is_regular_file_no_follow(artifact_root, name):
                findings.append(
                    RuntimeFinding(
                        code="invalid-runtime-artifact",
                        message=f"{label.capitalize()} Task artifact must be a regular file",
                        path=relative_path(artifact_path, resolved_root),
                    )
                )
                continue
            task_slugs.add(task)

    archived_root = task_root / "archived"
    if archived_root.exists():
        for name in list_directory_names_no_follow(archived_root):
            archived_path = archived_root / name
            match = ARCHIVED_TASK_FILE_PATTERN.fullmatch(name)
            if match is None or not is_regular_file_no_follow(archived_root, name):
                findings.append(
                    RuntimeFinding(
                        code="invalid-runtime-artifact",
                        message="Invalid archived Task artifact",
                        path=relative_path(archived_path, resolved_root),
                    )
                )
                continue
            try:
                validate_archive_date(match.group("archive_date"))
            except TaskRuntimeError as error:
                findings.append(
                    RuntimeFinding(
                        code="invalid-runtime-artifact",
                        message=str(error),
                        path=relative_path(archived_path, resolved_root),
                    )
                )
                continue
            task = match.group("task")
            task_slugs.add(task)

    conflict_root = task_root / "conflicts"
    if conflict_root.exists():
        for name in list_directory_names_no_follow(conflict_root):
            conflict_path = conflict_root / name
            matching_tasks = [
                task for task in task_slugs if name.startswith(f"{task}-") and name.endswith(".md")
            ]
            if not matching_tasks or not is_regular_file_no_follow(conflict_root, name):
                findings.append(
                    RuntimeFinding(
                        code="invalid-runtime-artifact",
                        message="Invalid or orphaned Task conflict artifact",
                        path=relative_path(conflict_path, resolved_root),
                    )
                )
                continue
            task_slugs.add(max(matching_tasks, key=len))

    for task in sorted(task_slugs):
        paths = task_paths(resolved_root, task)
        try:
            with task_operation_lock(paths):
                if paths.active_path.exists():
                    try:
                        validate_task_content(
                            read_bytes_no_follow(paths.active_path).decode("utf-8"),
                            task,
                            ACTIVE_STATUSES,
                        )
                    except (UnicodeError, TaskRuntimeError) as error:
                        findings.append(
                            RuntimeFinding(
                                code="invalid-active-task-document",
                                message=str(error),
                                path=relative_path(paths.active_path, resolved_root),
                            )
                        )
                tombstone = read_tombstone(paths)
                if tombstone is not None:
                    validate_tombstone_payload(paths, tombstone)
                if tombstone and tombstone.get("state") == "archiving":
                    recovery_findings = recover_archiving_task_locked(paths, tombstone)
                    findings.extend(recovery_findings)
                    if recovery_findings:
                        continue
                    tombstone = read_tombstone(paths)
                if tombstone and tombstone.get("state") == "archived":
                    cleanup_findings = cleanup_archived_task_residue_locked(paths)
                    findings.extend(cleanup_findings)
                    if cleanup_findings:
                        continue
                    inspection = inspect_archived_task(resolved_root, task)
                    findings.extend(inspection.findings)
                    continue
                if find_archived_task_paths(paths):
                    findings.extend(archive_integrity_findings(paths, None, include_active=True))
                if paths.staging_path.exists():
                    findings.append(
                        RuntimeFinding(
                            code="orphaned-archive-staging",
                            message="Staging Task exists without a recoverable archiving tombstone",
                            path=relative_path(paths.staging_path, resolved_root),
                        )
                    )
                conflict_paths = find_task_conflict_paths(paths)
                if conflict_paths:
                    findings.append(
                        RuntimeFinding(
                            code="unresolved-task-conflict",
                            message="Task has unresolved preserved conflict evidence",
                            path=relative_path(conflict_paths[0], resolved_root),
                        )
                    )
        except (OSError, UnicodeError, TaskRuntimeError) as error:
            findings.append(
                RuntimeFinding(
                    code="task-runtime-scan-failed",
                    message=str(error),
                    path=relative_path(paths.task_root, resolved_root),
                )
            )
    return findings


def archive_task(
    root: Path,
    task: str,
    archive_date: str,
    stability_checks: int = 3,
    stability_delay_ms: int = 100,
) -> ArchiveResult:
    validate_archive_date(archive_date)
    if stability_checks < 1:
        raise TaskRuntimeError("stability_checks must be at least 1")
    if stability_delay_ms < 0:
        raise TaskRuntimeError("stability_delay_ms cannot be negative")

    paths = task_paths(root, task)
    with task_operation_lock(paths) as operation_lock:
        existing_tombstone = read_tombstone(paths)
        if existing_tombstone is not None:
            validate_tombstone_payload(paths, existing_tombstone)
        if existing_tombstone and existing_tombstone.get("state") == "archived":
            recovery_findings = cleanup_archived_task_residue_locked(paths)
            if recovery_findings:
                finding = recovery_findings[0]
                raise TaskRuntimeError(f"{finding.code}: {finding.message} ({finding.path})")
            inspection = inspect_archived_task(paths.root, task)
            if inspection.state != "valid":
                finding = inspection.findings[0]
                raise TaskRuntimeError(f"{finding.code}: {finding.message} ({finding.path})")
            if existing_tombstone.get("archived_date") != archive_date:
                raise TaskRuntimeError("Task was already archived with a different archive date")
            return ArchiveResult(
                task=task,
                archived_path=str(inspection.archived_path),
                tombstone_path=inspection.tombstone_path,
                removed_stale_rewrites=0,
            )
        if existing_tombstone and existing_tombstone.get("state") == "archiving":
            recovery_findings = recover_archiving_task_locked(paths, existing_tombstone)
            if recovery_findings:
                finding = recovery_findings[0]
                raise TaskRuntimeError(
                    f"Task already has an active archived tombstone: {finding.message}"
                )
            existing_tombstone = read_tombstone(paths)
            if existing_tombstone and existing_tombstone.get("state") == "archived":
                if existing_tombstone.get("archived_date") != archive_date:
                    raise TaskRuntimeError("Task was already archived with a different archive date")
                inspection = inspect_archived_task(paths.root, task)
                return ArchiveResult(
                    task=task,
                    archived_path=str(inspection.archived_path),
                    tombstone_path=inspection.tombstone_path,
                    removed_stale_rewrites=0,
                )

        if not paths.active_path.is_file():
            raise TaskRuntimeError(
                f"Active task does not exist: {relative_path(paths.active_path, paths.root)}"
            )
        source_content = read_bytes_no_follow(paths.active_path)
        source_text = source_content.decode("utf-8")
        source_fields = validate_task_content(source_text, task, ARCHIVABLE_STATUSES)
        source_status = source_fields["status"]
        archive_date_value = date.fromisoformat(archive_date)
        created_date = source_fields["created"]
        updated_date = source_fields["updated"]
        if archive_date_value < max(created_date, updated_date):
            raise TaskRuntimeError(
                "Archive date cannot be earlier than the Task created or updated date"
            )
        archived_path = paths.archived_root / f"{archive_date}-{task}.md"
        ensure_canonical_path(archived_path, paths.archived_root, "archived")
        existing_archived_paths = find_archived_task_paths(paths)
        if existing_archived_paths:
            archived_locations = ", ".join(
                relative_path(existing_path, paths.root) for existing_path in existing_archived_paths
            )
            raise TaskRuntimeError(f"Archive target already exists: {archived_locations}")

        ensure_safe_directory(paths.root, paths.active_root, "active")
        ensure_safe_directory(paths.root, paths.archived_root, "archived")
        ensure_safe_directory(paths.root, paths.tombstone_root, "tombstone")
        ensure_safe_directory(paths.root, paths.staging_root, "staging")
        if paths.staging_path.exists():
            raise TaskRuntimeError(
                "Archive staging already exists without a recoverable tombstone; "
                "manual conflict resolution is required"
            )
        source_sha256 = calculate_sha256(source_content)
        tombstone_payload: dict[str, object] = {
            "task": task,
            "state": "archiving",
            "source_status": source_status,
            "source_sha256": source_sha256,
            "archived_path": relative_path(archived_path, paths.root),
            "archived_date": archive_date,
            "staging_path": relative_path(paths.staging_path, paths.root),
        }
        try:
            verify_task_operation_lock(operation_lock)
            write_json_exclusive(paths.tombstone_path, tombstone_payload)
        except FileExistsError as error:
            raise TaskRuntimeError(
                f"Concurrent archive detected for {paths.task!r}: tombstone already exists at "
                f"{relative_path(paths.tombstone_path, paths.root)}"
            ) from error

        try:
            verify_task_operation_lock(operation_lock)
            try:
                move_path_no_replace(paths.active_path, paths.staging_path)
            except FileExistsError as error:
                if paths.tombstone_path.exists():
                    unlink_no_follow(paths.tombstone_path)
                raise TaskRuntimeError(
                    "Archive staging conflict: a concurrent writer created the staging Task"
                ) from error
            captured_content = read_bytes_no_follow(paths.staging_path)
            if calculate_sha256(captured_content) != source_sha256:
                if not paths.active_path.exists():
                    replace_path_atomically(paths.staging_path, paths.active_path)
                if paths.tombstone_path.exists():
                    unlink_no_follow(paths.tombstone_path)
                raise TaskRuntimeError("Active Task changed after archive claim")
            captured_text = captured_content.decode("utf-8")
            validate_task_content(captured_text, task, ARCHIVABLE_STATUSES)
            archived_content = prepare_archived_content(captured_text, archive_date).encode("utf-8")
            verify_task_operation_lock(operation_lock)
            write_bytes_exclusive(
                archived_path,
                archived_content,
                temporary_label="archive",
            )
            tombstone_payload["state"] = "archived"
            tombstone_payload["archived_sha256"] = calculate_sha256(archived_content)
            verify_task_operation_lock(operation_lock)
            write_json_atomically(paths.tombstone_path, tombstone_payload)
            verify_task_operation_lock(operation_lock)
            unlink_no_follow(paths.staging_path)
        except Exception as archive_error:
            current_tombstone = read_tombstone(paths)
            recovery_findings = (
                recover_archiving_task_locked(paths, current_tombstone)
                if current_tombstone and current_tombstone.get("state") == "archiving"
                else []
            )
            inspection = inspect_archived_task(paths.root, task)
            if inspection.state != "valid":
                if recovery_findings:
                    finding = recovery_findings[0]
                    raise TaskRuntimeError(
                        f"Archive failed and recovery failed: {finding.message}"
                    ) from archive_error
                raise

        removed_stale_rewrites = 0
        for check_index in range(stability_checks):
            if check_index > 0 and stability_delay_ms:
                time.sleep(stability_delay_ms / 1000)
            active_existed_before_cleanup = paths.active_path.exists()
            findings = cleanup_archived_task_residue_locked(paths)
            if findings:
                finding = findings[0]
                raise TaskRuntimeError(f"{finding.code}: {finding.message} ({finding.path})")
            if active_existed_before_cleanup and not paths.active_path.exists():
                removed_stale_rewrites += 1

        inspection = inspect_archived_task(paths.root, task)
        if inspection.state != "valid":
            finding = inspection.findings[0]
            raise TaskRuntimeError(f"{finding.code}: {finding.message} ({finding.path})")
        return ArchiveResult(
            task=task,
            archived_path=str(inspection.archived_path),
            tombstone_path=inspection.tombstone_path,
            removed_stale_rewrites=removed_stale_rewrites,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execute guarded CodeStable Task lifecycle operations.")
    parser.add_argument("--root", default=".", help="Repository root containing .codestable/tasks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    write_parser = subparsers.add_parser("write-active", help="Create or replace an active Task safely.")
    write_parser.add_argument("--task", required=True)
    write_parser.add_argument("--content-file", required=True)
    write_parser.add_argument("--expected-sha256")

    archive_parser = subparsers.add_parser("archive", help="Archive a completed or cancelled Task safely.")
    archive_parser.add_argument("--task", required=True)
    archive_parser.add_argument("--date", required=True)
    archive_parser.add_argument("--stability-checks", type=int, default=3)
    archive_parser.add_argument("--stability-delay-ms", type=int, default=100)

    cleanup_parser = subparsers.add_parser("cleanup", help="Clean exact stale active rewrites.")
    cleanup_parser.add_argument("--task")

    inspect_parser = subparsers.add_parser("inspect", help="Verify canonical archived Task evidence.")
    inspect_parser.add_argument("--task", required=True)

    subparsers.add_parser("scan", help="Scan all archived tombstones and clean exact stale rewrites.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    root = Path(arguments.root)

    try:
        if arguments.command == "write-active":
            active_path = write_active_task(
                root,
                arguments.task,
                Path(arguments.content_file),
                arguments.expected_sha256,
            )
            payload: dict[str, object] = {
                "ok": True,
                "task": arguments.task,
                "active_path": relative_path(active_path, root.resolve()),
            }
        elif arguments.command == "archive":
            payload = {
                "ok": True,
                **asdict(
                    archive_task(
                        root,
                        arguments.task,
                        arguments.date,
                        arguments.stability_checks,
                        arguments.stability_delay_ms,
                    )
                ),
            }
        elif arguments.command == "inspect":
            inspection = inspect_archived_task(root, arguments.task)
            payload = {
                "ok": inspection.state in {"valid", "historical"},
                **asdict(inspection),
            }
        else:
            findings = (
                cleanup_archived_task_residue(root, arguments.task)
                if arguments.command == "cleanup" and arguments.task
                else scan_task_runtime(root)
            )
            payload = {
                "ok": not findings,
                "findings": [asdict(finding) for finding in findings],
            }
    except (OSError, UnicodeError, TaskRuntimeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, indent=2))
        return 1

    print(json.dumps(payload, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
