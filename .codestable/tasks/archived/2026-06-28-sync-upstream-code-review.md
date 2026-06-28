---
doc_type: task-list
task: sync-upstream-code-review
goal: Sync upstream native cs-code-review and preserve automated review gates
status: archived
workflow: feature
owner_skill: cs-task
created: 2026-06-28
updated: 2026-06-28
archived: 2026-06-28
related_docs:
  - .codestable/features/2026-06-28-sync-upstream-code-review/sync-upstream-code-review-design.md
  - .codestable/features/2026-06-28-sync-upstream-code-review/sync-upstream-code-review-checklist.yaml
  - .codestable/features/2026-06-28-sync-upstream-code-review/sync-upstream-code-review-acceptance.md
  - .codestable/features/2026-06-28-sync-upstream-code-review/sync-upstream-code-review-review.md
---

# Sync upstream native cs-code-review and preserve automated review gates

## 1. 任务目标

把本地 fork 安全同步到 upstream 最新版，采用 upstream 原生 `cs-code-review`，并保留各流程完成后自动进入 code review 的门禁闭环。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 起草并确认 feature design
- [x] 执行 upstream rebase / 语义合并
- [x] 校准各流程自动 review 入口
- [x] 验收同步结果并进入 code review

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| design | `.codestable/features/2026-06-28-sync-upstream-code-review/sync-upstream-code-review-design.md` | 同步方案 |
| checklist | `.codestable/features/2026-06-28-sync-upstream-code-review/sync-upstream-code-review-checklist.yaml` | 执行与验收清单 |
| acceptance | `.codestable/features/2026-06-28-sync-upstream-code-review/sync-upstream-code-review-acceptance.md` | 验收报告 |
| review | `.codestable/features/2026-06-28-sync-upstream-code-review/sync-upstream-code-review-review.md` | 最终 code review 报告 |

## 5. 执行步骤

### 1. 起草并确认 design

- 状态：done
- 来源：cs-feat-design
- 完成信号：design 通过整体 review，并生成 checklist

### 2. 执行 upstream 同步

- 状态：done
- 来源：design
- 完成信号：迁移分支完成 rebase 或等价语义合并，冲突已解决

### 3. 校准自动 review gates

- 状态：done
- 来源：design
- 完成信号：feature / issue / refactor / fastforward 流程均指向 upstream 原生 `cs-code-review`

### 4. 验收与最终 review

- 状态：done
- 来源：feature workflow
- 完成信号：acceptance 与 `cs-code-review` 均完成，Task 可归档

### 5. 最终 code review

- 状态：done
- 来源：cs-code-review
- 完成信号：code review 报告落盘，Critical / Important 清零

### 6. 修复 code review blocking / important

- 状态：done
- 来源：cs-code-review
- 完成信号：REV-001 / REV-002 / REV-003 已修复并重跑 code review

## 6. 中断恢复提示

本任务已归档；无需恢复。

## 7. 完成与归档记录

2026-06-28：upstream-first rebase / overlay 收敛 / 验收 / code review 均已完成。

2026-06-28：已归档到 `.codestable/tasks/archived/2026-06-28-sync-upstream-code-review.md`，active 中不应保留同名任务。
