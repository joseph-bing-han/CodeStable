---
doc_type: task-list
task: task-archive-runtime-guard-regression
goal: Fix Task archive stale active rewrites with executable runtime guards
status: archived
workflow: issue
owner_skill: cs-task
created: 2026-07-11
updated: 2026-07-11
archived: 2026-07-11
related_docs:
  - .codestable/issues/2026-07-11-task-archive-runtime-guard-regression/task-archive-runtime-guard-regression-report.md
  - .codestable/issues/2026-07-11-task-archive-runtime-guard-regression/task-archive-runtime-guard-regression-analysis.md
  - .codestable/issues/2026-07-11-task-archive-runtime-guard-regression/task-archive-runtime-guard-regression-fix-note.md
  - .codestable/issues/2026-07-11-task-archive-runtime-guard-regression/task-archive-runtime-guard-regression-review.md
---

# 修复 Task 归档后 active 文件重现回归

## 1. 任务目标

把 Task 归档一致性从文字协议提升为可执行运行时保护，防止或可靠处理归档后的旧 active 路径写回。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 记录本次真实使用回归及历史修复边界
- [x] 分析失败路径、根因、影响面和修复方案
- [x] 按确认方案实现归档运行时保护
- [x] 增加行为测试并完成验证
- [x] 执行 CodeStable code review gate
- [x] 完成并归档 Task

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| issue-report | `.codestable/issues/2026-07-11-task-archive-runtime-guard-regression/task-archive-runtime-guard-regression-report.md` | 记录归档后 active 文件重新出现的真实回归 |
| issue-analysis | `.codestable/issues/2026-07-11-task-archive-runtime-guard-regression/task-archive-runtime-guard-regression-analysis.md` | 定位文字协议与真实运行时之间的防护缺口 |
| issue-fix | `.codestable/issues/2026-07-11-task-archive-runtime-guard-regression/task-archive-runtime-guard-regression-fix-note.md` | 记录完整 Task runtime、review-fix 与验证证据 |
| issue-review | `.codestable/issues/2026-07-11-task-archive-runtime-guard-regression/task-archive-runtime-guard-regression-review.md` | Round 2 self review passed |
| historical-issue | `.codestable/issues/2026-06-30-task-archive-stale-active-rewrite/task-archive-stale-active-rewrite-fix-note.md` | 记录上一轮仅文本契约修复的范围 |

## 5. 执行步骤

### 1. 记录回归

- 状态：done
- 来源：用户现场报告
- 完成信号：报告包含现象、复现路径、期望、环境和 P1 严重程度。

### 2. 根因分析与方案确认

- 状态：done
- 来源：issue
- 完成信号：定位到具体文件与失败路径，形成至少两种修复方案并由用户确认。

### 3. 定点修复与行为测试

- 状态：done
- 来源：issue analysis
- 完成信号：完整 Task runtime、archived tombstone、回滚和 stale rewrite 行为测试通过；全量测试 71 passed。

### 4. 代码审查与归档

- 状态：done
- 来源：workflow
- 完成信号：Round 2 code review passed，准备通过新 runtime 归档。

## 6. 中断恢复提示

实现、验证和 review 已完成；仅需通过 Task runtime 执行归档。

## 7. 完成与归档记录

2026-07-11：完整 Task runtime、行为测试和 Round 2 review 已完成；进入 runtime archive。
