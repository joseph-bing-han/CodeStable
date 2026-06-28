---
doc_type: task-list
task: task-archive-stale-active-rewrite
goal: Prevent cs-task archive from reporting success when the active source path is rewritten after mv
status: archived
workflow: issue
owner_skill: cs-task
created: 2026-06-30
updated: 2026-06-30
archived: 2026-06-30
related_docs:
  - .codestable/issues/2026-06-30-task-archive-stale-active-rewrite/task-archive-stale-active-rewrite-report.md
  - .codestable/issues/2026-06-30-task-archive-stale-active-rewrite/task-archive-stale-active-rewrite-fix-note.md
  - .codestable/issues/2026-06-30-task-archive-stale-active-rewrite/task-archive-stale-active-rewrite-code-review.md
  - cs-task/SKILL.md
  - cs-task/reference.md
  - tests/test_workflow_contracts.py
---

# Prevent cs-task archive from reporting success when the active source path is rewritten after mv

## 1. 任务目标

修复 `cs-task archive` 在执行 `mv` 后仍可能因旧 active 路径被重新写回而误报成功的问题，确保最终回复前必须以当前文件系统事实确认 active 源路径不存在。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 记录 mv 后 active 路径被旧内容重新写回的现象
- [x] 收紧 cs-task archive 后续写入与最终验证协议
- [x] 更新 reference 与 workflow contract 测试
- [x] 同步已安装 skill 副本
- [x] 运行验证
- [x] 执行 CodeStable code review gate

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| report | `.codestable/issues/2026-06-30-task-archive-stale-active-rewrite/task-archive-stale-active-rewrite-report.md` | 记录 mv 后 active 源路径被重新写回的归档验证缺陷 |
| fix-note | `.codestable/issues/2026-06-30-task-archive-stale-active-rewrite/task-archive-stale-active-rewrite-fix-note.md` | 修复记录与验证计划 |
| review | `.codestable/issues/2026-06-30-task-archive-stale-active-rewrite/task-archive-stale-active-rewrite-code-review.md` | Code review gate 通过证据 |
| skill | `cs-task/SKILL.md` | 归档动作新增 active 源路径失效、禁止旧 buffer 写回与最终文件系统验证 |
| reference | `cs-task/reference.md` | 同步归档参考协议 |
| test | `tests/test_workflow_contracts.py` | 增加归档二阶验证契约断言 |

## 5. 执行步骤

### 1. 记录问题报告

- 状态：done
- 来源：issue
- 完成信号：issue report 已落盘并确认本次走快速修复。

### 2. 修复 archive 后续写入协议

- 状态：done
- 来源：issue
- 完成信号：`cs-task/SKILL.md` 与 `cs-task/reference.md` 明确 mv 后禁止再写 active 源路径，最终回复前必须重新读取当前文件系统事实。

### 3. 增加契约测试并同步安装副本

- 状态：done
- 来源：issue
- 完成信号：测试断言覆盖 stale active rewrite / final verification / shell test 不足，且 installed skill 同步。

### 4. 运行验证

- 状态：done
- 来源：workflow
- 完成信号：`uvx pytest -q` 通过，且 source / installed skill 关键 archive 规则一致。

### 5. 执行 CodeStable code review gate

- 状态：done
- 来源：workflow
- 完成信号：code review gate passed 并落盘 review 证据。

## 6. 中断恢复提示

任务已归档；历史记录位于 `.codestable/tasks/archived/2026-06-30-task-archive-stale-active-rewrite.md`。

## 7. 完成与归档记录

2026-06-30：修复、测试与 code review gate 均已完成；已通过 `mv` 将 active 原文件移动到 `.codestable/tasks/archived/2026-06-30-task-archive-stale-active-rewrite.md`，并只在 archived 目标文件上更新归档状态。最终验证要求 active 源路径不存在。
