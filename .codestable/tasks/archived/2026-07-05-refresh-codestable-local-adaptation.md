---
doc_type: task-list
task: refresh-codestable-local-adaptation
goal: Update the local .codestable workspace to the current CodeStable standard and audit remaining compatibility gaps
status: archived
workflow: onboarding
owner_skill: cs-onboard
created: 2026-07-05
updated: 2026-07-05
archived: 2026-07-05
related_docs:
  - .codestable/audits/2026-07-05-codestable-local-adaptation/codestable-local-adaptation-audit.md
---

# Update the local .codestable workspace to the current CodeStable standard and audit remaining compatibility gaps

## 1. 任务目标

在已完成共享资产刷新的基础上，继续升级 `.codestable/attention.md` 到新版骨架，并补做一次兼容性扫描，明确哪些目录属于当前标准、哪些是历史遗留且暂时保留原位。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 复核当前 `.codestable/` 与既有刷新记录
- [x] 升级 `attention.md` 到新版骨架并保留现有内容
- [x] 输出本次兼容性扫描审计记录
- [x] 验证结果并归档 Task

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| audit | `.codestable/audits/2026-07-05-codestable-local-adaptation/codestable-local-adaptation-audit.md` | 本次本地适配与兼容性扫描记录 |

## 5. 执行步骤

### 1. 复核当前 `.codestable/` 与既有刷新记录

- 状态：done
- 来源：cs-onboard migration
- 完成信号：已确认 2026-07-03 刷新记录存在，且本地 `.codestable/` 已同步新版共享 `tools/`、`reference/` 与 `gates` 资产。

### 2. 升级 `attention.md` 到新版骨架并保留现有内容

- 状态：done
- 来源：user request
- 完成信号：`attention.md` 含新版“报告语言”段落，且既有项目碎片知识分节仍保留。

### 3. 输出本次兼容性扫描审计记录

- 状态：done
- 来源：user request
- 完成信号：已明确记录当前标准目录、历史遗留目录与处理建议。

### 4. 验证结果并归档 Task

- 状态：done
- 来源：workflow gate
- 完成信号：相关文档已落盘，Task 已完成并归档且 active 无残留。

## 6. 中断恢复提示

如果任务中断，先读取本 Task 与 `.codestable/audits/2026-07-05-codestable-local-adaptation/codestable-local-adaptation-audit.md`，然后检查 `attention.md` 是否已经补入新版“报告语言”段落。

## 7. 完成与归档记录

- 2026-07-05：Task 创建，准备继续完成 `attention.md` 升级与兼容性扫描。
- 2026-07-05：已完成 `attention.md` 骨架升级与兼容性扫描审计，准备执行归档。
- 2026-07-05：Task 已归档到 `.codestable/tasks/archived/2026-07-05-refresh-codestable-local-adaptation.md`。
