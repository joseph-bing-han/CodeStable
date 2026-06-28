---
doc_type: task-list
task: codestable-legacy-structure-cleanup
goal: Remove confirmed legacy .codestable directories and migrate remaining legacy architecture content into the current CodeStable structure
status: archived
workflow: onboarding
owner_skill: cs-onboard
created: 2026-07-05
updated: 2026-07-05
archived: 2026-07-05
related_docs:
  - .codestable/audits/2026-07-05-codestable-local-adaptation/codestable-local-adaptation-audit.md
---

# Remove confirmed legacy .codestable directories and migrate remaining legacy architecture content into the current CodeStable structure

## 1. 任务目标

基于用户已确认的清理授权，删除空的 `.codestable/config/`，并把 `.codestable/architecture/ARCHITECTURE.md` 迁移到当前 CodeStable 主线可接受的位置，然后清理旧遗留目录结构。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 复核遗留目录现状与待迁移文档内容
- [x] 迁移 `architecture/ARCHITECTURE.md` 到当前主线目录
- [x] 删除已确认可清理的遗留目录
- [x] 更新审计记录并归档 Task

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| audit | `.codestable/audits/2026-07-05-codestable-local-adaptation/codestable-local-adaptation-audit.md` | 本次本地适配与后续遗留清理记录 |

## 5. 执行步骤

### 1. 复核遗留目录现状与待迁移文档内容

- 状态：done
- 来源：user request
- 完成信号：已确认 `.codestable/config/` 为空目录，`.codestable/architecture/ARCHITECTURE.md` 为早期骨架文档。

### 2. 迁移 `architecture/ARCHITECTURE.md` 到当前主线目录

- 状态：done
- 来源：user request
- 完成信号：旧架构骨架内容已迁移到当前主线目录中的新文档，且旧 `ARCHITECTURE.md` 已移除。

### 3. 删除已确认可清理的遗留目录

- 状态：done
- 来源：user request
- 完成信号：`.codestable/config/` 与空的 `.codestable/architecture/` 目录已删除。

### 4. 更新审计记录并归档 Task

- 状态：done
- 来源：workflow gate
- 完成信号：审计记录已更新，Task 已归档且 active 无同名残留。

## 6. 中断恢复提示

如果任务中断，先读取本 Task 与 `.codestable/audits/2026-07-05-codestable-local-adaptation/codestable-local-adaptation-audit.md`，然后检查 `.codestable/compound/` 下是否已生成新的架构迁移文档。

## 7. 完成与归档记录

- 2026-07-05：Task 创建，准备执行遗留目录清理与架构骨架迁移。
- 2026-07-05：已完成架构骨架迁移、遗留目录删除与审计更新，准备执行归档。
- 2026-07-05：Task 已归档到 `.codestable/tasks/archived/2026-07-05-codestable-legacy-structure-cleanup.md`。
