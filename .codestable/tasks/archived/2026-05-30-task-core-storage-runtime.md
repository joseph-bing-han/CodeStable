---
doc_type: task-list
task: task-core-storage-runtime
goal: Implement the core CodeStable task storage and recovery runtime
status: archived
workflow: feature
owner_skill: cs-feat-impl
created: 2026-05-30
updated: 2026-05-30
archived: 2026-05-30
related_docs:
  - .codestable/roadmap/codestable-task-system/codestable-task-system-roadmap.md
  - .codestable/roadmap/codestable-task-system/codestable-task-system-items.yaml
  - .codestable/features/2026-05-30-task-core-storage-runtime/task-core-storage-runtime-design.md
  - .codestable/features/2026-05-30-task-core-storage-runtime/task-core-storage-runtime-checklist.yaml
  - .codestable/features/2026-05-30-task-core-storage-runtime/task-core-storage-runtime-acceptance.md
---

# Implement the core CodeStable task storage and recovery runtime

## 1. 任务目标

实现 roadmap 第一条 `task-core-storage-runtime`：新增 `cs-task` 技能和参考协议，并让根入口与共享约定识别 `.codestable/tasks/`。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 创建 feature design、checklist 和 active task
- [x] 新增 cs-task/SKILL.md 和 cs-task/reference.md
- [x] 更新 cs/SKILL.md 和 shared conventions
- [x] 校验 YAML、行数和 lints
- [x] 回写 roadmap item 和汇报

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| roadmap | `.codestable/roadmap/codestable-task-system/codestable-task-system-roadmap.md` | Task System 总规划 |
| roadmap-items | `.codestable/roadmap/codestable-task-system/codestable-task-system-items.yaml` | 子 feature 清单 |
| design | `.codestable/features/2026-05-30-task-core-storage-runtime/task-core-storage-runtime-design.md` | 本 feature 设计 |
| checklist | `.codestable/features/2026-05-30-task-core-storage-runtime/task-core-storage-runtime-checklist.yaml` | 本 feature 推进清单 |
| acceptance | `.codestable/features/2026-05-30-task-core-storage-runtime/task-core-storage-runtime-acceptance.md` | 本 feature 验收报告 |

## 5. 执行步骤

### 1. 创建 feature 文档骨架

- 状态：done
- 来源：roadmap item `task-core-storage-runtime`
- 完成信号：feature design、checklist 和 active task 已创建

### 2. 新增 cs-task 核心技能

- 状态：done
- 来源：design 第 2.1 节
- 完成信号：`cs-task/SKILL.md` 和 `cs-task/reference.md` 存在并定义恢复、完成和归档协议

### 3. 更新入口和共享约定

- 状态：done
- 来源：design 第 2.3 节
- 完成信号：`cs/SKILL.md` 能路由到 `cs-task`，shared conventions 包含 tasks 目录

### 4. 校验并回写

- 状态：done
- 来源：cs-feat-impl 收尾
- 完成信号：YAML 校验通过，roadmap item 标记 done，行数检查通过

## 6. 中断恢复提示

下次运行 `cs task` 时，本任务应出现在历史任务中；下一步可继续 roadmap 的 `task-integration-policy`。

## 7. 完成与归档记录

2026-05-30：实现和验收均已完成，roadmap item 已回写为 done，任务已归档到 `.codestable/tasks/archived/2026-05-30-task-core-storage-runtime.md`。
