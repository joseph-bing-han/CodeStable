---
doc_type: task-list
task: mandatory-task-review-spine-regression
goal: 修复完整入口流程仍可能缺失 cs-task 与 cs-code-review 的 workflow spine 回归
status: archived
workflow: issue
owner_skill: cs-task
created: 2026-06-29
updated: 2026-06-29
archived: 2026-06-29
related_docs:
  - .codestable/issues/2026-06-29-mandatory-task-review-spine-regression/mandatory-task-review-spine-regression-report.md
  - .codestable/issues/2026-06-29-mandatory-task-review-spine-regression/mandatory-task-review-spine-regression-analysis.md
  - .codestable/issues/2026-06-29-mandatory-task-review-spine-regression/mandatory-task-review-spine-regression-fix-note.md
  - .codestable/issues/2026-06-29-mandatory-task-review-spine-regression/mandatory-task-review-spine-regression-review.md
---

# 修复完整入口流程缺失 Task 与 Code Review 主线回归

## 1. 任务目标

根据 Cursor 对话记录修复 CodeStable workflow spine，确保任何入口的完整流程不会缺失 `cs-task`、`cs-code-review` 和最终归档。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 读取对话记录并落 issue report
- [x] 分析 Task / Review 缺失根因
- [x] 补强共享协议与关键技能
- [x] 验证并同步安装目录
- [x] 写 fix-note / review 并归档 Task

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| report | `.codestable/issues/2026-06-29-mandatory-task-review-spine-regression/mandatory-task-review-spine-regression-report.md` | 问题报告 |
| analysis | `.codestable/issues/2026-06-29-mandatory-task-review-spine-regression/mandatory-task-review-spine-regression-analysis.md` | 根因分析 |
| fix-note | `.codestable/issues/2026-06-29-mandatory-task-review-spine-regression/mandatory-task-review-spine-regression-fix-note.md` | 修复记录 |
| code-review | `.codestable/issues/2026-06-29-mandatory-task-review-spine-regression/mandatory-task-review-spine-regression-review.md` | 审查报告 |

## 5. 执行步骤

### 1. 记录复发问题

- 状态：done
- 来源：用户提供 Cursor 对话记录
- 完成信号：issue report 已落盘

### 2. 分析根因

- 状态：done
- 来源：issue 标准路径
- 完成信号：analysis 已落盘并明确修复方案

### 3. 修改 workflow spine 协议

- 状态：done
- 来源：analysis 推荐方案
- 完成信号：共享协议与关键技能明确 Task / Review / Archive 不可跳过

### 4. 验证与同步

- 状态：done
- 来源：issue-fix 退出要求
- 完成信号：测试通过，安装目录同步

### 5. 归档

- 状态：done
- 来源：cs-task 闭环要求
- 完成信号：Task 移动到 archived 且 active 无同名残留

## 6. 中断恢复提示

本任务已完成，归档后无需恢复。

## 7. 完成与归档记录

2026-06-29 已完成修复、review、安装目录同步，并归档到 `.codestable/tasks/archived/2026-06-29-mandatory-task-review-spine-regression.md`。active 目录无同名残留。
