from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def test_issue_direct_entries_cannot_degrade_to_chat_only_handoff() -> None:
    for rel_path in (
        "cs-issue/SKILL.md",
        "cs-issue-report/SKILL.md",
        "cs-issue-analyze/SKILL.md",
        "cs-issue-fix/SKILL.md",
    ):
        text = read(rel_path)
        assert "当前 agent" in text
        assert ("不能只" in text or "不能回复“建议使用" in text)


def test_issue_spine_requires_task_review_and_archive() -> None:
    shared = read("cs-onboard/reference/shared-conventions.md")
    assert "Task → spec 产物 → code review → archive" in shared
    assert "续跑缺失 review / QA / acceptance 证据" in shared

    issue = read("cs-issue/SKILL.md")
    assert "cs-code-review" in issue
    assert "cs-task archive" in issue

    fix = read("cs-issue-fix/SKILL.md")
    assert "无 Task 不修复" in fix
    assert "无 review 不闭环" in fix
    assert "必须同时检查 `.codestable/tasks/active/*.md` 与 `.codestable/tasks/archived/YYYY-MM-DD-*.md`" in fix
    assert "禁止补建新的 active Task" in fix


def test_removed_legacy_checkout_gate_contracts_do_not_remain() -> None:
    legacy_tool = "codestable-" + "work" + "tree" + "-gate.py"
    legacy_phrase = "work" + "tree gate"

    task = read("cs-task/SKILL.md")
    assert "review / QA / acceptance 证据" in task

    fix = read("cs-issue-fix/SKILL.md")
    assert "修复门禁（Task + review evidence）" in fix
    assert legacy_tool not in fix

    shared = read("cs-onboard/reference/shared-conventions.md")
    assert legacy_phrase not in shared


def test_task_backfill_is_discoverable_from_frontmatter() -> None:
    task = read("cs-task/SKILL.md")
    assert "缺少 task" in task.split("---", 2)[1]
    assert "backfill task" in task.split("---", 2)[1]


def test_task_archive_scan_must_not_trust_ignore_filtered_search_only() -> None:
    task = read("cs-task/SKILL.md")
    reference = read("cs-task/reference.md")

    assert "`.codestable/` 可能被 `.gitignore` 忽略" in task
    assert "不能只用会受 ignore 过滤的 Glob、rg" in task
    assert "不得只凭 Glob / rg 的 0 结果判断无任务" in task
    assert "归档对象盘点同样必须遵守" in task
    assert "active 中没有同名残留" in task
    assert "mv \".codestable/tasks/active/{task}.md\"" in task
    assert "禁止用“读取 active 内容 → 写入 archived 新文件 → 稍后再删 active”的复制式归档" in task
    assert "active 源路径视为失效路径" in task
    assert "禁止再对 `.codestable/tasks/active/{task}.md` 使用 ApplyPatch / Edit / Write / 保存旧 buffer" in task
    assert "最终回复用户前" in task
    assert "不能只依赖一次 shell `test ! -e active && test -e archived` 的历史 exit code" in task
    assert "归档后的 active 同名源不存在是硬退出条件" in task
    assert "最终回复前的当前文件系统验证通过才允许报告成功" in task
    assert "active 与 archived 都没有对应 Task spine" in task
    assert "仅 `.codestable/tasks/active/{slug}.md` 缺失不等于缺少 task" in task
    assert "禁止创建新的 active Task" in task
    assert "不受 ignore 过滤的目录枚举" in reference
    assert "判断 active / archived 是否为空前" in reference
    assert "判断 Task 是否缺失时必须同时检查 active 与 archived" in reference
    assert "不得重新创建 `.codestable/tasks/active/{task}.md`" in reference
    assert "必须先把 active 原文件移动 / 重命名到 archived 目标路径" in reference
    assert "mv \".codestable/tasks/active/{task}.md\"" in reference
    assert "active 源路径视为失效路径" in reference
    assert "最终回复用户前" in reference
    assert "不能只依赖一次 shell `test ! -e active && test -e archived` 的历史 exit code" in reference


def test_code_review_subagent_does_not_use_managed_project_config() -> None:
    review = read("cs-code-review/SKILL.md")
    template = read("cs-code-review/references/report-template.md")

    assert ".codestable/config/code-review-subagent.yaml" not in review
    assert "首次运行 `cs-code-review`" not in review
    assert "review_subagent:" not in review
    assert "thinking_budget" not in review
    assert "fallback_policy" not in review
    assert "后续运行直接读取该配置" not in review
    assert "Cursor subagent" in review
    assert "runtime" in review
    assert "local-only" in review
    assert "不得使用 Explore subagent" in review

    assert "Cursor config" not in template
    assert ".codestable/config/code-review-subagent.yaml" not in template
    assert "model={configured/current-conversation-fallback}" not in template
    assert "thinking_budget={configured/current-conversation-fallback}" not in template
    assert "Runtime params" in template


def test_code_review_backfill_must_respect_archived_task_spine() -> None:
    review = read("cs-code-review/SKILL.md")

    assert "必须复用来源 workflow 的 Task spine" in review
    assert "查找时必须同时检查 active 与 archived" in review
    assert "active 找不到但 archived 中已有同 slug 且 `status: archived`" in review
    assert "禁止 backfill 新 active Task" in review
    assert "active 与 archived 都缺失时才 backfill" in review
    assert "不得为了 review / 总结 / 收尾再创建新的 active Task" in review
