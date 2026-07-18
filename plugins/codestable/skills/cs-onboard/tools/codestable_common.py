#!/usr/bin/env python3
"""Shared helpers for CodeStable repository state tools."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from codestable_gate_common import load_yaml_text


IMPLEMENTATION_PREFIXES = (
    "app/",
    "backend/",
    "client/",
    "frontend/",
    "lib/",
    "packages/",
    "scripts/",
    "server/",
    "src/",
    "supabase/migrations/",
    "test/",
    "tests/",
)

IMPLEMENTATION_SUFFIXES = (
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".svelte",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
)

UNIT_ROOTS = ("features", "issues", "refactors")
CANONICAL_REVIEWERS = frozenset({"subagent"})
LEGACY_READABLE_REVIEWERS = frozenset({"subagent+ocr"})
SUBAGENT_REVIEWERS = CANONICAL_REVIEWERS | LEGACY_READABLE_REVIEWERS
REVIEW_SCHEMA_BY_UNIT_ROOT = {
    "features": ("feature-review", "feature"),
    "issues": ("issue-review", "issue"),
    "refactors": ("refactor-review", "refactor"),
}
LEGACY_REVIEW_CUTOFF_DATE = date(2026, 7, 17)
# reviewer gate 不再硬编码固定 provider/model：reviewer 使用当前模型的最高思考等级即可，
# 只对已知需要显式档位的模型强制约束（gpt-5.6-sol 的最高档在宿主里叫 xhigh）。
REVIEWER_REASONING_OVERRIDES = {
    "gpt-5.6-sol": "xhigh",
}
# Fast / Explore 轻量预设或已知降级异构模型不得充当 reviewer。这类预设（例如
# Explore 会用的 gpt-5.6-tera-*）正是 review 被静默降级到低思考档的根因；模型名
# 按分隔符切成的 token 中若有整段等于任一标记即 fail-closed，防止契约声明的
# “禁止 Fast/Explore”只停留在散文层。
#
# 必须按 token 段精确匹配、不能用裸子串：像 "gemini-2.5-pro" 这样的合法顶配模型名
# 含子串 "mini"（ge+mini），"elite" 含 "lite"，裸子串会把它们误判成降级模型。
# 按 "-._/ " 切段后 "gemini"/"2.5"/"pro" 均不等于任何标记，因此 Gemini Pro 可通过；
# 而 "gpt-5.6-tera-high" 切出的 "tera" 段整段命中标记，仍被拒。
FORBIDDEN_REVIEWER_MODEL_MARKERS = frozenset(
    {
        "tera",
        "fast",
        "explore",
        "explorer",
        "flash",
        "haiku",
        "mini",
        "nano",
        "lite",
        "small",
    }
)
REVIEWER_MODEL_TOKEN_RE = re.compile(r"[a-z0-9]+")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
AGENT_REF_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
KNOWN_SKILL_DIRS = {
    "codestable-maintainer",
    "cs",
    "cs-audit",
    "cs-brainstorm",
    "cs-code-review",
    "cs-doc-api",
    "cs-doc-tutorial",
    "cs-docs",
    "cs-docs-neat",
    "cs-domain",
    "cs-epic",
    "cs-feedback",
    "cs-feat",
    "cs-feat-accept",
    "cs-feat-design",
    "cs-feat-design-review",
    "cs-feat-ff",
    "cs-feat-impl",
    "cs-feat-qa",
    "cs-goal",
    "cs-issue",
    "cs-issue-analyze",
    "cs-issue-fix",
    "cs-issue-report",
    "cs-keep",
    "cs-note",
    "cs-onboard",
    "cs-refactor",
    "cs-refactor-ff",
    "cs-req",
    "cs-roadmap",
    "cs-roadmap-impl-goal",
    "cs-roadmap-review",
    "cs-task",
}


@dataclass(frozen=True)
class ChangedFile:
    status: str
    path: str


@dataclass(frozen=True)
class Finding:
    severity: str
    message: str
    path: str | None = None


@dataclass(frozen=True)
class BacklogItem:
    kind: str
    path: str
    line: int
    text: str


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_output(root: Path, *args: str) -> str:
    result = run_git(root, *args)
    if result.returncode != 0:
        return result.stderr.strip()
    return result.stdout.strip()


def git_status(root: Path, *extra_args: str) -> list[ChangedFile]:
    result = run_git(root, "status", "--porcelain", "-uall", *extra_args)
    if result.returncode != 0:
        return []

    changed: list[ChangedFile] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        raw_path = line[3:]
        if " -> " in raw_path:
            raw_path = raw_path.split(" -> ", 1)[1]
        changed.append(ChangedFile(status=status, path=raw_path.strip('"')))
    return changed


def staged_files(root: Path) -> list[ChangedFile]:
    result = run_git(root, "diff", "--cached", "--name-status")
    if result.returncode != 0:
        return []
    changed: list[ChangedFile] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        status, _, path = line.partition("\t")
        if "\t" in path:
            path = path.rsplit("\t", 1)[-1]
        changed.append(ChangedFile(status=status, path=path))
    return changed


def current_branch(root: Path) -> str | None:
    result = run_git(root, "branch", "--show-current")
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def ref_exists(root: Path, ref: str) -> bool:
    return run_git(root, "rev-parse", "--verify", "--quiet", ref).returncode == 0


def default_branch(root: Path) -> str | None:
    origin_head = run_git(root, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if origin_head.returncode == 0:
        value = origin_head.stdout.strip()
        if value.startswith("origin/"):
            return value.split("/", 1)[1]
    for candidate in ("main", "master"):
        if ref_exists(root, candidate) or ref_exists(root, f"refs/heads/{candidate}"):
            return candidate
    return current_branch(root)


def is_implementation_path(path: str) -> bool:
    if path.startswith(".codestable/"):
        return False
    return path.startswith(IMPLEMENTATION_PREFIXES) or path.endswith(IMPLEMENTATION_SUFFIXES)


def path_bucket(path: str) -> str:
    if path.startswith(".codestable/"):
        return "codestable"
    first = Path(path).parts[0] if Path(path).parts else ""
    if first in KNOWN_SKILL_DIRS:
        return "installed_skill"
    if path.startswith("supabase/migrations/"):
        return "migrations"
    if path.startswith("docs/database/"):
        return "database_docs"
    if path.startswith(("data/input/", "data/output/")):
        return "data"
    if path.endswith((".log", ".jsonl")) or "/logs/" in path or path.startswith("logs/"):
        return "logs"
    if path.startswith(("docs/", "doc/")) or path.endswith(".md"):
        return "docs"
    if path.startswith("tests/") or path.startswith("test/"):
        return "tests"
    if is_implementation_path(path):
        return "code"
    return "unknown"


def is_secret_like_path(path: str) -> bool:
    lower = path.lower()
    name = Path(lower).name
    return name.startswith(".env") or "secret" in lower or "token" in lower or "credential" in lower


SECRET_QUOTED_VALUE_RE = re.compile(
    r"(?i)(token|api[_-]?key|secret|password|credential)(\s*[:=]\s*)(['\"])([^'\"\n]+)(['\"])"
)
SECRET_VALUE_RE = re.compile(
    r"(?i)(token|api[_-]?key|secret|password|credential)(\s*[:=]\s*)([^\s'\"`]+)"
)


def redact_text(text: str) -> str:
    text = SECRET_QUOTED_VALUE_RE.sub(r"\1\2\3[REDACTED]\5", text)
    text = SECRET_VALUE_RE.sub(r"\1\2[REDACTED]", text)
    text = re.sub(r"(?i)(bearer\s+)[a-z0-9._~+/=-]{12,}", r"\1[REDACTED]", text)
    text = re.sub(r"eyJ[a-zA-Z0-9_-]{12,}\.[a-zA-Z0-9_-]{12,}\.[a-zA-Z0-9_-]{12,}", "[REDACTED_JWT]", text)
    return text


def bucket_paths(paths: list[str]) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {}
    for path in paths:
        buckets.setdefault(path_bucket(path), []).append(path)
    return {bucket: sorted(values) for bucket, values in sorted(buckets.items())}


def unit_dir_for(path: str) -> Path | None:
    parts = Path(path).parts
    if len(parts) < 3 or parts[0] != ".codestable" or parts[1] not in UNIT_ROOTS:
        return None
    return Path(*parts[:3])


def unit_slug(unit_dir: Path) -> str:
    return unit_dir.name.split("-", 3)[-1]


def review_file_for(unit_dir: Path) -> Path:
    return unit_dir / f"{unit_slug(unit_dir)}-review.md"


def legacy_issue_review_file_for(unit_dir: Path) -> Path | None:
    """Return the pre-canonical Issue review filename, when applicable."""
    if unit_dir.parts[1] != "issues":
        return None
    return unit_dir / f"{unit_slug(unit_dir)}-code-review.md"


def all_checklist_steps_done(path: Path) -> bool:
    if not path.exists():
        return False

    in_steps = False
    saw_step = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped == "steps:":
            in_steps = True
            continue
        if in_steps and stripped and not raw_line.startswith((" ", "-")):
            break
        if not in_steps:
            continue
        if stripped.startswith("- "):
            saw_step = True
        if stripped.startswith("status:"):
            _, _, value = stripped.partition(":")
            if value.strip() != "done":
                return False
    return saw_step


def unit_needs_review(root: Path, unit_dir: Path) -> bool:
    unit_root = root / unit_dir
    if not unit_root.exists():
        return False
    unit_type = unit_dir.parts[1]

    if unit_type == "features":
        return any(unit_root.glob("*-ff-note.md")) or any(
            all_checklist_steps_done(path) for path in unit_root.glob("*-checklist.yaml")
        )

    if unit_type == "issues":
        return any(unit_root.glob("*-fix-note.md"))

    if unit_type == "refactors":
        return any(unit_root.glob("*-apply-notes.md")) or any(
            all_checklist_steps_done(path) for path in unit_root.glob("*-checklist.yaml")
        )

    return False


def find_touched_units(changed: list[ChangedFile]) -> set[Path]:
    units: set[Path] = set()
    for item in changed:
        unit_dir = unit_dir_for(item.path)
        if unit_dir is not None:
            units.add(unit_dir)
    return units


def iter_units(root: Path) -> list[Path]:
    units: list[Path] = []
    codestable = root / ".codestable"
    for unit_root in UNIT_ROOTS:
        parent = codestable / unit_root
        if not parent.exists():
            continue
        units.extend(path.relative_to(root) for path in parent.iterdir() if path.is_dir())
    return sorted(units, key=lambda path: path.as_posix())


def review_unit_schema(path: Path) -> tuple[str, str, str, str] | None:
    unit_dir = path.parent
    unit_root = unit_dir.parent.name
    schema = REVIEW_SCHEMA_BY_UNIT_ROOT.get(unit_root)
    if schema is None or unit_dir.parent.parent.name != ".codestable":
        return None
    expected_doc_type, identity_field = schema
    slug = unit_slug(Path(".codestable") / unit_root / unit_dir.name)
    expected_filename = f"{slug}-review.md"
    return expected_doc_type, identity_field, unit_dir.name.lower(), expected_filename


def reviewer_reasoning_is_valid(model: object, reasoning: object) -> bool:
    """校验 reviewer 模型与思考等级。

    契约是 reviewer 使用**当前对话主模型的可用最高思考等级**。gate 无法枚举每个
    模型的档位名，也不能假设某个通用档位名（如 low/medium）一定不是最高档——某些
    模型只有单一档位，那个唯一档就是它的最高档，不应因此判失败。因此：

    - 对任意模型只要求 model/reasoning 均为非空字符串；具体是否为“最高档”由派发
      纪律与 REVIEWER_REASONING_OVERRIDES 保证，不用通用档位名黑名单机械否决。
    - 模型名按分隔符切成的 token 段中若有整段等于 FORBIDDEN_REVIEWER_MODEL_MARKERS
      （Fast/Explore/tera 等降级异构预设）时拒绝——这类预设是“换了个更弱的模型”，与
      档位高低无关，是 review 被静默降级的根因，契约声明的“禁止 Fast/Explore”必须由
      gate 强制。按 token 段精确匹配而非裸子串，避免误伤合法模型名（如 "gemini-2.5-pro"
      含子串 "mini"、"elite" 含 "lite"）。
    - 对已知需要显式最高档名的模型（见 REVIEWER_REASONING_OVERRIDES）强制到指定值。
    """
    if type(model) is not str or not model.strip():
        return False
    if type(reasoning) is not str or not reasoning.strip():
        return False
    # 输入先归一化一次，后续匹配与查表统一复用同一个小写形式，避免 casing 不一致
    # 造成的绕过（例如 FORBIDDEN 用小写匹配、override 用原样查表时，"GPT-5.6-Sol"
    # 会跳过 gpt-5.6-sol 的 xhigh 强制）。REVIEWER_REASONING_OVERRIDES 的 key 也用小写。
    normalized_model = model.strip().lower()
    model_tokens = set(REVIEWER_MODEL_TOKEN_RE.findall(normalized_model))
    if model_tokens & FORBIDDEN_REVIEWER_MODEL_MARKERS:
        return False
    required = REVIEWER_REASONING_OVERRIDES.get(normalized_model)
    if required is not None:
        return reasoning.strip().lower() == required
    return True


def review_has_canonical_evidence(path: Path) -> bool:
    schema = review_unit_schema(path)
    if schema is None:
        return False
    expected_doc_type, identity_field, expected_identity, expected_filename = schema
    if path.name != expected_filename:
        return False
    fields = review_frontmatter_data(path)
    round_value = fields.get("round")
    reviewer_ref = fields.get("reviewer_ref")
    reviewer_provider = fields.get("reviewer_provider")
    task_generation_sha256 = fields.get("task_generation_sha256")
    review_basis_sha256 = fields.get("review_basis_sha256")
    return bool(
        fields.get("status") == "passed"
        and fields.get("reviewer") in CANONICAL_REVIEWERS
        and fields.get("doc_type") == expected_doc_type
        and fields.get(identity_field) == expected_identity
        and type(round_value) is int
        and round_value > 0
        and fields.get("reviewer_state") == "completed"
        and type(reviewer_ref) is str
        and AGENT_REF_RE.fullmatch(reviewer_ref.strip())
        and type(reviewer_provider) is str
        and reviewer_provider.strip()
        and reviewer_reasoning_is_valid(
            fields.get("reviewer_model"), fields.get("reviewer_reasoning")
        )
        and fields.get("reviewer_readonly") is True
        and type(task_generation_sha256) is str
        and SHA256_RE.fullmatch(task_generation_sha256)
        and type(review_basis_sha256) is str
        and SHA256_RE.fullmatch(review_basis_sha256)
    )


def task_generation_sha256(root: Path, task: str) -> str | None:
    task_path = root / ".codestable/tasks/active" / f"{task}.md"
    if not task_path.is_file():
        return None
    try:
        content = task_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    if not content.startswith("---\n"):
        return None
    end_index = content.find("\n---\n", 4)
    if end_index == -1:
        return None
    try:
        fields = load_yaml_text(content[4:end_index])
    except (RuntimeError, ValueError):
        return None
    if not isinstance(fields, dict):
        return None
    created = fields.get("created")
    stable_generation = {
        "doc_type": fields.get("doc_type"),
        "task": fields.get("task"),
        "goal": fields.get("goal"),
        "workflow": fields.get("workflow"),
        "created": created.isoformat() if type(created) is date else created,
    }
    if (
        stable_generation["doc_type"] != "task-list"
        or stable_generation["task"] != task
        or any(value in {None, ""} for value in stable_generation.values())
    ):
        return None
    serialized = json.dumps(
        stable_generation,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def review_basis_path_is_excluded(path: str, review_path: str) -> bool:
    path_object = Path(path)
    return bool(
        path == review_path
        or path.startswith(".codestable/tasks/")
        or path_object.name == "approval-report.md"
        or path_object.name == "goal-state.yaml"
        or path_object.name.endswith("-qa.md")
        or path_object.name.endswith("-acceptance.md")
    )


def review_basis_sha256(root: Path, review_path: Path) -> str:
    resolved_root = root.resolve()
    review_relative = review_path.resolve().relative_to(resolved_root).as_posix()
    records: list[tuple[str, str, str]] = []
    if (resolved_root / ".git").exists():
        changed_files = git_status(resolved_root)
        for changed_file in changed_files:
            path = changed_file.path
            if review_basis_path_is_excluded(path, review_relative):
                continue
            absolute_path = resolved_root / path
            digest = (
                hashlib.sha256(absolute_path.read_bytes()).hexdigest()
                if absolute_path.is_file()
                else "deleted"
            )
            records.append((path, changed_file.status, digest))
    else:
        for absolute_path in sorted(
            path
            for path in resolved_root.rglob("*")
            if path.is_file() and ".git" not in path.parts
        ):
            relative_path = absolute_path.relative_to(resolved_root).as_posix()
            if review_basis_path_is_excluded(relative_path, review_relative):
                continue
            records.append(
                (
                    relative_path,
                    "filesystem",
                    hashlib.sha256(absolute_path.read_bytes()).hexdigest(),
                )
            )
    serialized = json.dumps(
        sorted(records),
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def review_evidence_matches_repository(path: Path) -> bool:
    schema = review_unit_schema(path)
    if schema is None or not review_has_canonical_evidence(path):
        return False
    fields = review_frontmatter_data(path)
    root = path.parent.parent.parent.parent
    task = unit_slug(path.parent.relative_to(root))
    return bool(
        fields.get("task_generation_sha256") == task_generation_sha256(root, task)
        and fields.get("review_basis_sha256") == review_basis_sha256(root, path)
    )


def review_has_subagent_evidence(path: Path, *, allow_legacy_issue_filename: bool = False) -> bool:
    schema = review_unit_schema(path)
    if schema is None:
        return False
    expected_doc_type, identity_field, expected_identity, expected_filename = schema
    legacy_issue_filename = (
        f"{unit_slug(path.parent)}-code-review.md" if path.parent.parent.name == "issues" else None
    )
    acceptable_filenames = {expected_filename}
    if allow_legacy_issue_filename and legacy_issue_filename is not None:
        acceptable_filenames.add(legacy_issue_filename)
    if path.name not in acceptable_filenames:
        return False
    fields = review_frontmatter_data(path)
    return bool(
        fields.get("status") == "passed"
        and fields.get("reviewer") in SUBAGENT_REVIEWERS
        and fields.get("doc_type") == expected_doc_type
        and fields.get(identity_field) == expected_identity
    )


def review_frontmatter_data(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return {}
    if not content.startswith("---\n"):
        return {}
    end_index = content.find("\n---\n", 4)
    if end_index == -1:
        return {}

    try:
        parsed = load_yaml_text(content[4:end_index])
    except (RuntimeError, ValueError):
        return {}
    if not isinstance(parsed, dict) or any(type(key) is not str for key in parsed):
        return {}
    return parsed


def review_frontmatter_fields(path: Path) -> dict[str, str]:
    parsed = review_frontmatter_data(path)

    fields: dict[str, str] = {}
    for field_name, field_value in parsed.items():
        if type(field_value) not in {str, int, float, bool} or field_value is None:
            continue
        fields[field_name.strip().lower()] = str(field_value).strip().lower()
    return fields


def workflow_family(workflow: str) -> str:
    if workflow.startswith("issue"):
        return "issues"
    if workflow.startswith("refactor"):
        return "refactors"
    if workflow.startswith("feature"):
        return "features"
    return workflow


def unit_has_archived_task(root: Path, unit_dir: Path) -> bool:
    archived_root = root / ".codestable/tasks/archived"
    if not archived_root.exists():
        return False
    task_slug = unit_slug(unit_dir)
    if (root / ".codestable/tasks/active" / f"{task_slug}.md").exists():
        return False
    expected_unit_root = unit_dir.parts[1]
    for task_path in archived_root.glob(f"????-??-??-{task_slug}.md"):
        try:
            archived_date = date.fromisoformat(task_path.name[:10])
        except ValueError:
            continue
        if archived_date >= LEGACY_REVIEW_CUTOFF_DATE:
            continue
        fields = review_frontmatter_data(task_path)
        created_date = fields.get("created")
        updated_date = fields.get("updated")
        if (
            fields.get("doc_type") == "task-list"
            and fields.get("task") == task_slug
            and fields.get("status") == "archived"
            and fields.get("archived") == archived_date
            and type(created_date) is date
            and type(updated_date) is date
            and created_date <= archived_date
            and updated_date <= archived_date
            and workflow_family(str(fields.get("workflow") or "")) == expected_unit_root
        ):
            return True
    return False


def missing_review_findings(root: Path, units: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for unit_dir in units:
        if not unit_needs_review(root, unit_dir):
            continue
        review_path = review_file_for(unit_dir)
        full_review_path = root / review_path
        legacy_issue_review_path = legacy_issue_review_file_for(unit_dir)
        full_legacy_issue_review_path = (
            root / legacy_issue_review_path if legacy_issue_review_path is not None else None
        )
        if review_has_canonical_evidence(full_review_path):
            continue
        if unit_has_archived_task(root, unit_dir) and (
            review_has_subagent_evidence(full_review_path)
            or (
                full_legacy_issue_review_path is not None
                and review_has_subagent_evidence(
                    full_legacy_issue_review_path,
                    allow_legacy_issue_filename=True,
                )
            )
        ):
            continue
        if not full_review_path.exists():
            findings.append(
                Finding(
                    severity="P1",
                    message="Completed CodeStable implementation unit is missing code review evidence ({slug}-review.md).",
                    path=review_path.as_posix(),
                )
            )
        else:
            findings.append(
                Finding(
                    severity="P1",
                    message="CodeStable implementation review must use a canonical Task agent reviewer (reviewer: subagent).",
                    path=review_path.as_posix(),
                )
            )
    return findings


def resolve_unit(root: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate.resolve().relative_to(root.resolve())
    if (root / candidate).exists():
        return candidate
    matches = [unit for unit in iter_units(root) if value in unit.name or value == unit_slug(unit)]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ValueError(f"unit not found: {value}")
    raise ValueError(f"unit is ambiguous: {value}")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


BACKLOG_PATTERNS = (
    ("needs-human-review", re.compile(r"needs-human-review", re.IGNORECASE)),
    ("human-review", re.compile(r"human review required", re.IGNORECASE)),
    ("accepted-p2", re.compile(r"accepted.{0,40}P2|P2.{0,40}accepted", re.IGNORECASE)),
    ("deferred-p2", re.compile(r"deferred.{0,40}P2|P2.{0,40}deferred", re.IGNORECASE)),
    ("follow-up", re.compile(r"^\s*(?:[-*]\s+|\d+\.\s+)?follow[- ]ups?(?:\s*:|\b)", re.IGNORECASE)),
)
ATTENTION_CANDIDATES_HEADING_RE = re.compile(r"attention\.md.{0,40}candidates?|candidates?.{0,40}attention\.md", re.IGNORECASE)
MARKDOWN_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+)")
FOLLOW_UP_SECTION_HEADING_RE = re.compile(r"^\s*#{1,6}\s+follow[- ]ups?\s*$", re.IGNORECASE)
BACKLOG_SCAN_EXCLUDED_SUFFIXES = ("-review-packet.md",)
BACKLOG_SCAN_EXCLUDED_PREFIXES = (".codestable/reference/",)
FOLLOW_UP_BLOCKING_TEXT_MARKERS = (
    "before merge",
    "before publish",
    "before release",
    "before ship",
    "before completion",
    "blocking",
    "must",
    "required",
)
RESOLVED_FOLLOW_UP_RE = re.compile(
    r"(?:subagent review )?follow[- ]up(?:s)?(?:\s+(?:fix(?:es)?|review|evidence|implementation)|$)|"
    r"follow[- ]up(?:s)?.{0,40}(?:backlog|fixed;|passed after|was added before|has been fixed)|"
    r"passed after.{0,40}follow[- ]up|"
    r"after follow[- ]up fixes|"
    r"follow[- ]up.{0,80}(?:no (?:new )?(?:remaining )?p0|no (?:new )?(?:remaining )?p1|"
    r"no (?:new )?(?:remaining )?p2|closed|fixed|resolved|已修|无 p0|无 p1|无阻塞)",
    re.IGNORECASE,
)
CANCELED_UNIT_STATUSES = {"canceled", "cancelled", "abandoned"}
STATUS_RE = re.compile(r"^\s*status:\s*['\"]?([a-z0-9_-]+)['\"]?\s*$", re.IGNORECASE)


def should_scan_backlog_file(rel_path: str) -> bool:
    return not (
        rel_path.startswith(BACKLOG_SCAN_EXCLUDED_PREFIXES)
        or rel_path.endswith(BACKLOG_SCAN_EXCLUDED_SUFFIXES)
    )


def is_blocking_follow_up_text(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in FOLLOW_UP_BLOCKING_TEXT_MARKERS)


def is_resolved_backlog_match(kind: str, text: str) -> bool:
    if kind != "follow-up":
        return False
    if is_blocking_follow_up_text(text):
        return False
    return bool(RESOLVED_FOLLOW_UP_RE.search(text))


def unit_lifecycle_status_files(root: Path, unit_dir: Path) -> list[Path]:
    unit_root = root / unit_dir
    slug = unit_slug(unit_dir)
    names = (
        f"{slug}-acceptance.md",
        f"{slug}-ff-note.md",
        f"{slug}-fix-note.md",
        f"{slug}-apply-notes.md",
    )
    return [unit_root / name for name in names if (unit_root / name).exists()]


def file_has_canceled_status(path: Path) -> bool:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return False
    for line in lines:
        match = STATUS_RE.match(line)
        if match and match.group(1).lower() in CANCELED_UNIT_STATUSES:
            return True
    return False


def unit_has_canceled_lifecycle_status(root: Path, rel_path: str) -> bool:
    unit_dir = unit_dir_for(rel_path)
    if unit_dir is None:
        return False
    return any(file_has_canceled_status(path) for path in unit_lifecycle_status_files(root, unit_dir))


def scan_backlog(root: Path) -> list[BacklogItem]:
    codestable = root / ".codestable"
    if not codestable.exists():
        return []
    items: list[BacklogItem] = []
    for path in sorted(codestable.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml", ".txt"}:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        rel_path = path.relative_to(root).as_posix()
        if not should_scan_backlog_file(rel_path):
            continue
        if unit_has_canceled_lifecycle_status(root, rel_path):
            continue
        in_attention_candidates = False
        in_follow_up_section = False
        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()
            if ATTENTION_CANDIDATES_HEADING_RE.search(stripped):
                in_attention_candidates = True
                continue
            if FOLLOW_UP_SECTION_HEADING_RE.search(stripped):
                in_follow_up_section = True
                continue
            if in_attention_candidates:
                if stripped.startswith("#"):
                    in_attention_candidates = False
                elif not stripped:
                    continue
                else:
                    bullet = MARKDOWN_BULLET_RE.match(line)
                    if bullet:
                        items.append(
                            BacklogItem(
                                kind="attention-candidate",
                                path=rel_path,
                                line=line_no,
                                text=bullet.group(1).strip(),
                            )
                        )
                    continue
            if in_follow_up_section:
                if stripped.startswith("#"):
                    in_follow_up_section = False
                else:
                    bullet = MARKDOWN_BULLET_RE.match(line)
                    if bullet:
                        text = bullet.group(1).strip()
                        items.append(
                            BacklogItem(
                                kind="follow-up",
                                path=rel_path,
                                line=line_no,
                                text=text,
                            )
                        )
                        continue
            for kind, pattern in BACKLOG_PATTERNS:
                if pattern.search(line):
                    if is_resolved_backlog_match(kind, stripped):
                        continue
                    items.append(BacklogItem(kind=kind, path=rel_path, line=line_no, text=stripped))
                    break
    return items


def unit_for_path(path: str) -> str | None:
    unit_dir = unit_dir_for(path)
    return unit_dir.as_posix() if unit_dir is not None else None


def has_secret_like_untracked(root: Path) -> list[str]:
    secret_paths: list[str] = []
    for item in git_status(root):
        if item.status != "??":
            continue
        lower = item.path.lower()
        name = Path(lower).name
        if name.startswith(".env") or "secret" in lower or "token" in lower:
            secret_paths.append(item.path)
    return sorted(secret_paths)


def tracked_ignored_paths(root: Path) -> list[str]:
    result = run_git(root, "ls-files", "-ci", "--exclude-standard")
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
