---
doc_type: task-list
task: entry-subskills-full-workflow-spine
goal: 修复 CodeStable 子入口不能承接完整工作流闭环的问题
status: archived
workflow: issue
owner_skill: cs-code-review
created: 2026-06-21
updated: 2026-06-21
archived: 2026-06-21
related_docs:
  - .codestable/issues/2026-06-21-entry-subskills-full-workflow-spine/entry-subskills-full-workflow-spine-report.md
  - .codestable/issues/2026-06-21-entry-subskills-full-workflow-spine/entry-subskills-full-workflow-spine-analysis.md
  - .codestable/issues/2026-06-21-entry-subskills-full-workflow-spine/entry-subskills-full-workflow-spine-fix-note.md
  - .codestable/issues/2026-06-21-entry-subskills-full-workflow-spine/entry-subskills-full-workflow-spine-code-review.md
---

# 修复 CodeStable 子入口不能承接完整工作流闭环的问题

## 1. 任务目标

修复 direct entry 进入 `cs-issue`、`cs-brainstorm` 等子入口时无法稳定承接完整闭环的问题，让入口级技能和根入口在流程收口上保持一致。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 建立 issue 记录并锁定缺陷范围
- [x] 完成根因分析并确定修复策略
- [x] 修改共享协议与相关入口技能文档
- [x] 完成自检、fix-note、code review 与归档收口

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| issue-report | `.codestable/issues/2026-06-21-entry-subskills-full-workflow-spine/entry-subskills-full-workflow-spine-report.md` | 记录现象、预期与影响 |
| issue-analysis | `.codestable/issues/2026-06-21-entry-subskills-full-workflow-spine/entry-subskills-full-workflow-spine-analysis.md` | 记录根因、影响面与推荐修法 |
| issue-fix | `.codestable/issues/2026-06-21-entry-subskills-full-workflow-spine/entry-subskills-full-workflow-spine-fix-note.md` | 记录统一协议修复、改动文件与验证结果 |
| code-review | `.codestable/issues/2026-06-21-entry-subskills-full-workflow-spine/entry-subskills-full-workflow-spine-code-review.md` | 最终质量门禁，确认修复无阻塞项 |
| runtime-ref | `.codestable/reference/shared-conventions.md` | 当前项目运行时共享约定副本 |
| runtime-ref | `.codestable/reference/system-overview.md` | 当前项目运行时总览副本 |
| source-skill | `cs/SKILL.md` | 根入口补齐“不是唯一完整入口”口径 |
| source-skill | `cs-feat/SKILL.md` | feature 入口补齐完整入口语义 |
| source-skill | `cs-issue/SKILL.md` | issue 入口补齐完整入口语义 |
| source-skill | `cs-brainstorm/SKILL.md` | brainstorm 入口补齐下游主线延续语义 |
| source-skill | `cs-refactor/SKILL.md` | refactor 入口补齐完整入口语义 |
| source-skill | `cs-roadmap/SKILL.md` | roadmap 入口补齐 minimal-loop 延续语义 |
| source-skill | `cs-audit/SKILL.md` | audit 入口补齐 finding 继续推进语义 |
| source-template | `cs-onboard/reference/shared-conventions.md` | 模板共享约定补齐完整入口守卫 |
| source-template | `cs-onboard/reference/system-overview.md` | 模板总览新增入口等价原则 |
| source-readme | `README.md` | 中文总览同步 direct-entry 语义 |
| source-readme | `README.en.md` | 英文总览同步 direct-entry 语义 |

## 5. 执行步骤

### 1. 建立 issue 记录并锁定缺陷范围

- 状态：done
- 来源：user
- 完成信号：issue 目录、report 与任务边界都已明确

### 2. 完成根因分析并确定修复策略

- 状态：done
- 来源：issue
- 完成信号：analysis 写明根因、影响面与推荐修法

### 3. 修改共享协议与相关入口技能文档

- 状态：done
- 来源：analysis
- 完成信号：共享约定、系统总览和目标入口技能口径已同步

### 4. 完成自检、fix-note、code review 与归档收口

- 状态：done
- 来源：issue
- 完成信号：fix-note、code-review 落盘且任务已归档

## 6. 中断恢复提示

如需回顾本次闭环，直接读取 archived 任务与 issue 目录下的 report / analysis / fix-note / code-review。

## 7. 完成与归档记录

2026-06-21：issue report、analysis、fix-note、code-review 已全部落盘；当前项目源码与运行时副本都已修复，外部 `/Users/joseph/.agents/skills/cs` 目录未保留改动，待用户后续自行 `git pull` 同步；任务已归档到 `.codestable/tasks/archived/2026-06-21-entry-subskills-full-workflow-spine.md`，active 目录无同名残留。
