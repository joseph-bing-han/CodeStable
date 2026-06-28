---
doc_type: issue-fix
issue: 2026-06-30-task-archive-ignored-active-scan
status: fixed
severity: high
created: 2026-06-30
updated: 2026-06-30
---

# task-archive-ignored-active-scan fix note

## 1. 问题

执行 `/cs-task 归档` 时，实际存在 `.codestable/tasks/active/remove-worktree-flow.md`，但归档盘点阶段报告 active task 为 0，导致遗漏未归档 Task。

## 2. 根因

`.codestable/` 被 `.gitignore` 忽略，而 `cs-task` 原协议只写“扫描 / 读取 `.codestable/tasks/active/*.md`”，没有强制使用不受 ignore 过滤的目录枚举方式。Cursor 的 Glob / 文件搜索会受 ignore 规则影响，返回 0 后被误当作 active 目录为空。

## 3. 修复

- 在 `cs-task/SKILL.md` 增加 Task 目录扫描硬约束。
- 明确 recovery / archive / history / cleanup 不能只用受 ignore 过滤的 Glob、rg 或文件搜索结果判断 active / archived 是否为空。
- 要求每次盘点 Task 目录时，必须使用不受 ignore 过滤的目录枚举读取 `.codestable/tasks/active` 和 `.codestable/tasks/archived` 下的 `*.md` 文件名，再逐个读取 frontmatter。
- 同步更新 `cs-task/reference.md` 的目录结构规则和归档残留清理协议。
- 增加合同测试 `test_task_archive_scan_must_not_trust_ignore_filtered_search_only`，防止协议回退。

## 4. 验证

- `tests/test_workflow_contracts.py` 已新增合同测试，覆盖 ignore 过滤风险和目录枚举要求。
- 预期命令：`uvx --with pytest pytest tests/test_workflow_contracts.py`。

## 5. 风险

- 本次修复的是 `cs-task` 的 skill 协议和合同测试；实际执行时仍要求 agent 遵守协议，使用未过滤目录枚举交叉确认，而不是只看 Glob / rg 返回值。
