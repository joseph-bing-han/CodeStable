---
doc_type: task-list
task: mandatory-task-spine-hardening
goal: 为本次 CodeStable 强制 Task 主线改造补建任务并完成闭环收口
status: archived
workflow: task
owner_skill: cs-task
created: 2026-06-19
updated: 2026-06-19
archived: 2026-06-19
related_docs:
  - README.md
  - cs/SKILL.md
  - cs-brainstorm/SKILL.md
  - cs-task/SKILL.md
  - cs-task/reference.md
  - cs-onboard/reference/shared-conventions.md
  - cs-onboard/reference/system-overview.md
---

# 为本次 CodeStable 强制 Task 主线改造补建任务并完成闭环收口

## 1. 任务目标

为本次 CodeStable 强制 Task 主线改造补建正式 Task List，把已完成修改、后续一致性复核与最终归档纳入统一账本。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 补建本次修改的 Task List 并登记核心文档
- [x] 复核受影响技能与总览文档的 Task 主线表述是否一致
- [x] 完成最终 code review / 验收收口并归档任务

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| overview | `README.md` | 体系总览中补齐 tasks 实体与 `cs-task` 入口 |
| entry-skill | `cs/SKILL.md` | 根入口改为由下游在首次落盘前自动 create / recovery |
| brainstorm-entry | `cs-brainstorm/SKILL.md` | brainstorm 落盘分支不再保留“是否接入 Task”的旧分支语义 |
| task-skill | `cs-task/SKILL.md` | 明确 Task 是强制主线，`completed` 后必须立即 archive |
| task-protocol | `cs-task/reference.md` | 补齐 Task List schema、状态机与归档闭环规则 |
| shared-convention | `cs-onboard/reference/shared-conventions.md` | 共享约定中统一强制 Task 主线与收口顺序 |
| system-overview | `cs-onboard/reference/system-overview.md` | 系统总览中补齐 `cs-task` 路由与强制 Task 主线 |

## 5. 执行步骤

### 1. 盘点本次改造范围

- 状态：done
- 来源：用户要求所有会落盘 workflow 强制接入 Task 主线
- 完成信号：已识别根入口、共享约定、Task 协议与关键总览文档的改造范围

### 2. 补建 Task List 并登记核心索引

- 状态：done
- 来源：用户指出“本次修改，缺失 task”
- 完成信号：`.codestable/tasks/active/mandatory-task-spine-hardening.md` 已创建且包含核心文档索引

### 3. 复核受影响技能与协议口径一致性

- 状态：done
- 来源：本次 Task 主线改造的最终自检要求
- 完成信号：关键入口、共享协议、总览文档与终点技能不再残留“跳过 Tasks”“策略要求进入 Tasks”“是否进入 Tasks”等旧表述

### 4. 完成最终收口并归档

- 状态：done
- 来源：CodeStable Task 闭环要求
- 完成信号：完成一致性复扫并形成归档记录，任务已移动到 `archived/` 且 active 无同名残留

## 6. 中断恢复提示

本任务已归档；若后续继续强化 Task 主线，请基于新的改造目标创建新 Task List。

## 7. 完成与归档记录

2026-06-19：已为本轮 CodeStable Task 主线改造补建正式任务账本；完成对根入口、brainstorm 入口、Task 协议与共享约定的二次复核，并通过关键词复扫确认旧表述已清零。任务已归档到 `.codestable/tasks/archived/2026-06-19-mandatory-task-spine-hardening.md`。
