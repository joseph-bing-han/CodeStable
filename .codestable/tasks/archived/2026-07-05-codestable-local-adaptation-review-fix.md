---
doc_type: task-list
task: codestable-local-adaptation-review-fix
goal: Fix the remaining CodeStable local adaptation review findings and restore review consistency
status: archived
workflow: onboarding
owner_skill: cs-onboard
created: 2026-07-05
updated: 2026-07-05
archived: 2026-07-05
related_docs:
  - .codestable/audits/2026-07-05-codestable-local-adaptation/codestable-local-adaptation-review.md
  - .codestable/audits/2026-07-05-codestable-local-adaptation/codestable-local-adaptation-audit.md
---

# Fix the remaining CodeStable local adaptation review findings and restore review consistency

## 1. 任务目标

基于 `codestable-local-adaptation-review.md` 的 review 结论，修复仍然成立的问题，并把相关审计文档回写到与当前共享约定一致的状态。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 复核 review finding 与当前仓库事实
- [x] 修复仍然成立的 review finding
- [x] 验证修复结果并归档 Task

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| review | `.codestable/audits/2026-07-05-codestable-local-adaptation/codestable-local-adaptation-review.md` | 本轮 code review 报告 |
| audit | `.codestable/audits/2026-07-05-codestable-local-adaptation/codestable-local-adaptation-audit.md` | 本轮适配审计记录 |

## 5. 执行步骤

### 1. 复核 review finding 与当前仓库事实

- 状态：done
- 来源：review-fix
- 完成信号：已确认 `REV-001` 对应的 active 残留当前已不存在；`REV-002` 关于标准目录口径不一致仍然成立。

### 2. 修复仍然成立的 review finding

- 状态：done
- 来源：review-fix
- 完成信号：审计文档不再把 `.codestable/brainstorms/` 表述为当前标准目录，并明确该目录与共享约定的关系。

### 3. 验证修复结果并归档 Task

- 状态：done
- 来源：workflow gate
- 完成信号：相关文档已更新，active 无残留，Task 已归档。

## 6. 中断恢复提示

如果任务中断，先读取本 Task、review 报告与本地适配审计文档，再确认 `brainstorms/` 是否仍被写入“当前标准目录”列表。

## 7. 完成与归档记录

- 2026-07-05：Task 创建，准备修复本地适配 review 的剩余问题。
- 2026-07-05：已修复 `REV-002`，并确认 `REV-001` 对应的 active 残留当前已不存在，准备执行归档。
- 2026-07-05：Task 已归档到 `.codestable/tasks/archived/2026-07-05-codestable-local-adaptation-review-fix.md`。
