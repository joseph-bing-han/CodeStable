---
doc_type: issue-fix
issue: 2026-06-29-mandatory-task-review-spine-regression
path: standard
fix_date: 2026-06-29
related:
  - mandatory-task-review-spine-regression-analysis.md
tags: [workflow, task, code-review, handoff]
---

# 完整入口缺失 Task 与 Code Review 主线修复记录

## 1. 实际采用方案

采用分析阶段推荐的方案 B：新增共享 Workflow spine gate，并同步 issue、task、code-review 和代码型出口。

## 2. 改动文件清单

- `.codestable/reference/shared-conventions.md`
- `.codestable/reference/system-overview.md`
- `cs-onboard/reference/shared-conventions.md`
- `cs-onboard/reference/system-overview.md`
- `cs-issue-report/SKILL.md`
- `cs-issue-analyze/SKILL.md`
- `cs-issue-fix/SKILL.md`
- `cs-code-review/SKILL.md`
- `cs-task/SKILL.md`
- `cs-feat-ff/SKILL.md`
- `cs-refactor/SKILL.md`
- `cs-refactor-ff/SKILL.md`

## 3. 修复内容

1. 共享协议新增 `Workflow spine gate`：代码型 workflow 不允许缺 `Task → spec 产物 → code review → archive` 任一环。
2. issue report / analyze 阶段明确 chat-only report / analysis 不算完成，无 Task / 无 report 不允许继续。
3. issue fix 阶段明确 fix-note 后必须立即执行 `cs-code-review`，不能只提示下一步。
4. `cs-code-review` 新增 Task gate：review 前必须有 active Task，缺失先 backfill；review passed 后负责更新 Task owner/status 并触发后续 gate。
5. `cs-task` 新增 backfill 模式：用户指出缺 task 或发现产物已有但 Task 缺失时，补建后必须续跑缺失 gate，不能只补账本。
6. feature fastforward 与 refactor 出口补强为立即进入 `cs-code-review`。

## 4. 验证结果

- 对话记录已分析：`/Users/joseph/Downloads/cursor_mqtt_log_warning_analysis.md` 暴露了 report、Task、code review 三处断点。
- 口径验证：`rg` 命中 `Workflow spine`、`backfill`、`无 review 不闭环`、`chat-only report 不算完成`、`不能只告诉用户下一步` 等关键约束。
- 测试验证：`uvx pytest -q` 通过，结果为 `52 passed in 13.95s`。
- 行数验证：本次修改的 tracked Markdown 文件均不超过 300 行；未再修改既有超 300 行的 `cs-feat-impl/SKILL.md`。

## 5. 遗留事项

- 当前 `.codestable/` 产物被 `.gitignore` 忽略，仅作为本地 CodeStable 运行记录。
- 已同步 `/Users/joseph/.agents/skills/cs` 安装目录，本机后续调用会直接读到本次修复。
