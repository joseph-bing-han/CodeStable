---
doc_type: task-list
task: refresh-codestable-onboard
goal: Refresh the project's .codestable structure and shared assets to the current cs-onboard standard
status: archived
workflow: onboarding
owner_skill: cs-onboard
created: 2026-06-30
updated: 2026-06-30
archived: 2026-06-30
related_docs:
  - .codestable/audits/2026-06-30-codestable-version-refresh/codestable-version-refresh-audit.md
---

# Refresh the project's .codestable structure and shared assets to the current cs-onboard standard

## 1. 任务目标

把当前仓库的 `.codestable/` 结构、共享 `tools/` 与 `reference/` 资源刷新到最新 `cs-onboard` 标准，同时保留未确认迁移的旧内容原位不动。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 扫描当前 `.codestable/` 现状与技能包版本差异
- [x] 刷新共享 `tools/` 与 `reference/` 目录
- [x] 补齐缺失骨架目录
- [x] 落盘迁移审计记录
- [x] 验证结果并完成归档

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| audit | `.codestable/audits/2026-06-30-codestable-version-refresh/codestable-version-refresh-audit.md` | 本次版本刷新与迁移审计记录 |

## 5. 执行步骤

### 1. 扫描当前 `.codestable/` 现状与技能包版本差异

- 状态：done
- 来源：cs-onboard migration
- 完成信号：已确认当前仓库属于迁移路径，且识别出缺失骨架与需刷新共享目录

### 2. 刷新共享 `tools/` 与 `reference/` 目录

- 状态：done
- 来源：cs-onboard migration
- 完成信号：项目内共享目录已由技能包当前版本覆盖刷新

### 3. 补齐缺失骨架目录

- 状态：done
- 来源：cs-onboard migration
- 完成信号：标准骨架中的缺失聚合根已补齐

### 4. 落盘迁移审计记录

- 状态：done
- 来源：cs-onboard migration
- 完成信号：审计报告已记录刷新动作、保留原位项与适配结论

### 5. 验证结果并完成归档

- 状态：done
- 来源：workflow gate
- 完成信号：目录刷新结果已验证，Task 已归档且 active 原件已清理

## 6. 中断恢复提示

已归档，无需续跑。

## 7. 完成与归档记录

- 2026-06-30：已完成 `.codestable/` 版本刷新、骨架补齐与迁移审计落盘，Task 归档到 `.codestable/tasks/archived/2026-06-30-refresh-codestable-onboard.md`。
