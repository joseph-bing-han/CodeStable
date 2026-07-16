---
doc_type: task-list
task: issue-code-review-filename-gate-compat
goal: 修复 issue code review 文件名导致 CodeStable gate 误判缺失 review 的问题
status: archived
workflow: issue
owner_skill: cs-task
created: 2026-06-29
updated: 2026-06-29
archived: 2026-06-29
related_docs:
  - .codestable/issues/2026-06-29-issue-code-review-filename-gate-compat/issue-code-review-filename-gate-compat-report.md
  - .codestable/issues/2026-06-29-issue-code-review-filename-gate-compat/issue-code-review-filename-gate-compat-analysis.md
  - .codestable/issues/2026-06-29-issue-code-review-filename-gate-compat/issue-code-review-filename-gate-compat-fix-note.md
  - .codestable/issues/2026-06-29-issue-code-review-filename-gate-compat/issue-code-review-filename-gate-compat-code-review.md
---

# 修复 issue code review 文件名导致 CodeStable gate 误判缺失 review 的问题

## 1. 任务目标

修复 CodeStable gate 工具对 issue review 文件名的识别逻辑，确保 `{slug}-code-review.md` 不再被误判为缺失 review，并同步 XebnIoT 的 `.codestable` 运行时副本。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 记录 issue report / analysis 与任务边界
- [x] 修复 gate review 文件候选逻辑
- [x] 补充并运行回归测试
- [x] 同步 XebnIoT `.codestable` 运行时副本
- [x] 写 fix-note / review 并归档 Task

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| report | `.codestable/issues/2026-06-29-issue-code-review-filename-gate-compat/issue-code-review-filename-gate-compat-report.md` | 问题报告 |
| analysis | `.codestable/issues/2026-06-29-issue-code-review-filename-gate-compat/issue-code-review-filename-gate-compat-analysis.md` | 根因分析与方案 |
| fix-note | `.codestable/issues/2026-06-29-issue-code-review-filename-gate-compat/issue-code-review-filename-gate-compat-fix-note.md` | 修复记录 |
| code-review | `.codestable/issues/2026-06-29-issue-code-review-filename-gate-compat/issue-code-review-filename-gate-compat-code-review.md` | 审查报告 |

## 5. 执行步骤

### 1. 记录问题与方案

- 状态：done
- 来源：用户要求修复项目中的 bug
- 完成信号：report / analysis / Task 已落盘

### 2. 修复 gate 逻辑

- 状态：done
- 来源：analysis
- 完成信号：issue `{slug}-code-review.md` 被 gate 识别为 review 证据

### 3. 验证与同步运行时副本

- 状态：done
- 来源：用户要求同步 XebnIoT `.codestable`
- 完成信号：`uvx pytest -q` 通过，XebnIoT runtime tools/reference/hooks 已更新，XebnIoT commit gate 在 self fallback 显式开启时通过

### 4. 收口归档

- 状态：done
- 来源：cs-task 闭环要求
- 完成信号：fix-note / review 落盘，Task 归档

## 6. 中断恢复提示

本任务已归档；如需追溯，请查看本文件和关联 issue 文档。

## 7. 完成与归档记录

2026-06-29：issue code-review 文件名兼容与 self review fallback 修复已完成；测试通过；XebnIoT `.codestable` 运行时副本已同步；Task 已归档。
