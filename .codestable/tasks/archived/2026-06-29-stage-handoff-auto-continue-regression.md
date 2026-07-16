---
doc_type: task-list
task: stage-handoff-auto-continue-regression
goal: 修复新版 CodeStable 阶段 handoff 退化为推荐用户手动运行下一 skill 的回归
status: archived
workflow: issue
owner_skill: cs-task
created: 2026-06-29
updated: 2026-06-29
archived: 2026-06-29
related_docs:
  - .codestable/issues/2026-06-29-stage-handoff-auto-continue-regression/stage-handoff-auto-continue-regression-report.md
  - .codestable/issues/2026-06-29-stage-handoff-auto-continue-regression/stage-handoff-auto-continue-regression-analysis.md
  - .codestable/issues/2026-06-29-stage-handoff-auto-continue-regression/stage-handoff-auto-continue-regression-fix-note.md
  - .codestable/issues/2026-06-29-stage-handoff-auto-continue-regression/stage-handoff-auto-continue-regression-review.md
---

# 修复新版 CodeStable 阶段 handoff 自动续跑回归

## 1. 任务目标

修复新版 CodeStable 中 direct entry 和阶段 handoff 可能退化成“建议用户手动运行下一 skill”的问题，恢复入口到归档的完整主线。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 记录 issue report 与根因分析
- [x] 补强共享协议与系统总览
- [x] 同步关键入口和阶段出口 skill 文案
- [x] 验证行数、grep 和测试结果
- [x] 写 fix-note / code-review
- [x] 同步运行目录并归档本 Task

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| report | `.codestable/issues/2026-06-29-stage-handoff-auto-continue-regression/stage-handoff-auto-continue-regression-report.md` | 问题报告 |
| analysis | `.codestable/issues/2026-06-29-stage-handoff-auto-continue-regression/stage-handoff-auto-continue-regression-analysis.md` | 根因分析 |
| fix-note | `.codestable/issues/2026-06-29-stage-handoff-auto-continue-regression/stage-handoff-auto-continue-regression-fix-note.md` | 修复记录 |
| code-review | `.codestable/issues/2026-06-29-stage-handoff-auto-continue-regression/stage-handoff-auto-continue-regression-review.md` | 本地审查报告 |

## 5. 执行步骤

### 1. 记录复发问题

- 状态：done
- 来源：用户反馈新版 CS direct entry 无法自动推进
- 完成信号：report 和 analysis 已落盘

### 2. 加固共享协议

- 状态：done
- 来源：推荐方案 B
- 完成信号：shared conventions / system overview 明确禁止推荐出口并要求当前 agent 执行目标 skill

### 3. 同步关键技能出口

- 状态：done
- 来源：推荐方案 B
- 完成信号：`cs`、`cs-issue`、`cs-issue-report`、`cs-issue-analyze`、`cs-brainstorm`、`cs-feat`、`cs-refactor`、`cs-roadmap`、`cs-audit` 已补强

### 4. 验证与收口

- 状态：done
- 来源：CodeStable issue-fix 退出要求
- 完成信号：行数、grep、测试通过，fix-note / code-review 已落盘

### 5. 同步运行目录与归档

- 状态：done
- 来源：当前安装目录 `/Users/joseph/.agents/skills/cs` 与项目源码分离
- 完成信号：运行目录已同步，Task 已归档到 `.codestable/tasks/archived/2026-06-29-stage-handoff-auto-continue-regression.md`

## 6. 中断恢复提示

本任务已归档，无需恢复。

## 7. 完成与归档记录

2026-06-29 已完成修复、review、运行目录同步，并归档到 `.codestable/tasks/archived/2026-06-29-stage-handoff-auto-continue-regression.md`。active 目录无同名残留。
