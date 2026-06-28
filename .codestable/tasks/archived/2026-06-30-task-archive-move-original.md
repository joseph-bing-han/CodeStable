---
doc_type: task-list
task: task-archive-move-original
goal: Fix cs-task archive so it moves the original active task file before editing archived metadata
status: archived
workflow: issue
owner_skill: cs-task
created: 2026-06-30
updated: 2026-06-30
archived: 2026-06-30
related_docs:
  - cs-task/SKILL.md
  - cs-task/reference.md
  - tests/test_workflow_contracts.py
  - .codestable/issues/2026-06-30-task-archive-move-original/task-archive-move-original-code-review.md
---

# Fix cs-task archive so it moves the original active task file before editing archived metadata

## 1. 任务目标

修复 `cs-task archive` 协议中的归档残留缺陷，确保归档必须先移动 active 原文件到 archived，再只更新移动后的 archived 文件，并用测试锁定该行为。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 分析 PayTaxNZ task 归档后 active 残留现象
- [x] 收紧 cs-task 归档协议为先移动原始 active 文件
- [x] 更新 cs-task reference 与 workflow contract 测试
- [x] 同步已安装 skill 副本
- [x] 清理 PayTaxNZ 已归档 task 的 active 残留
- [x] 执行 CodeStable code review gate

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| skill | `cs-task/SKILL.md` | 归档动作协议收紧为先移动 active 原文件 |
| reference | `cs-task/reference.md` | 归档参考协议同步先移动后编辑规则 |
| test | `tests/test_workflow_contracts.py` | 增加 contract 断言防止复制式归档回归 |
| review | `.codestable/issues/2026-06-30-task-archive-move-original/task-archive-move-original-code-review.md` | Code review gate 通过证据 |

## 5. 执行步骤

### 1. 定位归档残留根因

- 状态：done
- 来源：issue
- 完成信号：已确认 PayTaxNZ 同名 task 同时存在 active completed 与 archived archived 文件。

### 2. 修复 cs-task archive 协议

- 状态：done
- 来源：issue
- 完成信号：`cs-task/SKILL.md` 与 `cs-task/reference.md` 均要求先 `mv` active 原文件，再编辑 archived 目标文件。

### 3. 增加回归契约测试

- 状态：done
- 来源：issue
- 完成信号：`tests/test_workflow_contracts.py` 断言 `mv`、禁止复制式归档、active 同名源不存在硬退出条件。

### 4. 执行 CodeStable code review gate

- 状态：done
- 来源：workflow
- 完成信号：本次 diff 已通过 `cs-code-review` 并落盘 review 证据。

## 6. 中断恢复提示

任务已归档；历史记录位于 `.codestable/tasks/archived/2026-06-30-task-archive-move-original.md`。

## 7. 完成与归档记录

2026-06-30：Code review gate passed；已通过 `mv` 将 active 原文件移动到 `.codestable/tasks/archived/2026-06-30-task-archive-move-original.md`，并只在 archived 目标文件上更新归档状态。
