---
doc_type: task-list
task: refresh-codestable-onboard
goal: Refresh the project's .codestable structure and shared assets to the current cs-onboard standard
status: archived
workflow: onboarding
owner_skill: cs-onboard
created: 2026-07-03
updated: 2026-07-03
archived: 2026-07-03
related_docs:
  - .codestable/audits/2026-07-03-codestable-version-refresh/codestable-version-refresh-audit.md
---

# Refresh the project's .codestable structure and shared assets to the current cs-onboard standard

## 1. 任务目标

把当前仓库的 `.codestable/` 结构、共享 `tools/`、`reference/` 与新版 gate 配置刷新到当前 `cs-onboard` 标准，同时保留未确认迁移的既有项目内容原位不动。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 扫描当前 `.codestable/` 现状与新版技能包资源
- [x] 刷新共享 `tools/`、`reference/` 与 `gates/` 目录
- [x] 补齐缺失骨架目录
- [x] 落盘迁移审计记录
- [x] 验证刷新结果并归档 Task

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| audit | `.codestable/audits/2026-07-03-codestable-version-refresh/codestable-version-refresh-audit.md` | 本次版本刷新与迁移审计记录 |

## 5. 执行步骤

### 1. 扫描当前 `.codestable/` 现状与新版技能包资源

- 状态：done
- 来源：cs-onboard migration
- 完成信号：已确认当前仓库存在 `.codestable/`，属于迁移刷新路径；未发现 `.ccodestable/` 目录。

### 2. 刷新共享 `tools/`、`reference/` 与 `gates/` 目录

- 状态：done
- 来源：cs-onboard migration
- 完成信号：项目内共享资产已由 `plugins/codestable/skills/cs-onboard/` 当前版本覆盖刷新。

### 3. 补齐缺失骨架目录

- 状态：done
- 来源：cs-onboard migration
- 完成信号：标准骨架中的缺失聚合根已补齐。

### 4. 落盘迁移审计记录

- 状态：done
- 来源：cs-onboard migration
- 完成信号：审计报告已记录刷新动作、保留原位项与适配结论。

### 5. 验证刷新结果并归档 Task

- 状态：done
- 来源：workflow gate
- 完成信号：目录刷新结果已验证，Task 已归档且 active 原件已清理。

## 6. 中断恢复提示

已归档，无需续跑。

## 7. 完成与归档记录

- 2026-07-03：已完成 `.codestable/` 版本刷新，覆盖同步 `tools/` 与 `reference/`，新增同步 `gates/roadmap-goal-gates.yaml`，并落盘审计报告。
