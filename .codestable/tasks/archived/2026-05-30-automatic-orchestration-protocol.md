---
doc_type: task-list
task: automatic-orchestration-protocol
goal: Implement the CodeStable automatic orchestration protocol roadmap
status: archived
workflow: roadmap
owner_skill: cs-task
created: 2026-05-30
updated: 2026-05-30
archived: 2026-05-30
related_docs:
  - .codestable/roadmap/automatic-orchestration-protocol/automatic-orchestration-protocol-roadmap.md
  - .codestable/roadmap/automatic-orchestration-protocol/automatic-orchestration-protocol-items.yaml
  - cs-onboard/reference/shared-conventions.md
  - .codestable/reference/shared-conventions.md
  - cs/SKILL.md
  - cs-feat/SKILL.md
  - cs-issue/SKILL.md
  - cs-task/SKILL.md
  - cs-roadmap/SKILL.md
  - cs-brainstorm/SKILL.md
  - cs-feat-design/SKILL.md
  - cs-feat-impl/SKILL.md
  - cs-feat-accept/SKILL.md
  - cs-issue-report/SKILL.md
  - cs-issue-analyze/SKILL.md
  - cs-issue-fix/SKILL.md
---

# Implement the CodeStable automatic orchestration protocol roadmap

## 1. 任务目标

分步实施 CodeStable 自动编排协议 roadmap，先完成最小闭环 `orchestration-shared-protocol`，再推进入口技能、阶段技能和一致性验收。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 实施 `orchestration-shared-protocol`：在共享口径中加入自动编排协议
- [x] 实施 `orchestration-entry-skills`：改造入口型技能自动执行路由结果
- [x] 实施 `orchestration-stage-skills`：改造阶段型技能 review 后自动衔接
- [x] 实施 `orchestration-consistency-pass`：清理旧式表述并完成一致性验收

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| roadmap | `.codestable/roadmap/automatic-orchestration-protocol/automatic-orchestration-protocol-roadmap.md` | 自动编排协议规划 |
| roadmap-items | `.codestable/roadmap/automatic-orchestration-protocol/automatic-orchestration-protocol-items.yaml` | 子 feature 清单 |
| shared-conventions | `cs-onboard/reference/shared-conventions.md` | 新项目 onboard 共享口径模板 |
| shared-conventions | `.codestable/reference/shared-conventions.md` | 当前项目共享口径副本 |
| entry-skill | `cs/SKILL.md` | 总入口自动编排规则 |
| entry-skill | `cs-feat/SKILL.md` | feature 入口自动编排规则 |
| entry-skill | `cs-issue/SKILL.md` | issue 入口自动编排规则 |
| entry-skill | `cs-task/SKILL.md` | task recovery 自动进入 owner skill 规则 |
| entry-skill | `cs-roadmap/SKILL.md` | roadmap 完成后自动进入 minimal loop feature 规则 |
| stage-skill | `cs-brainstorm/SKILL.md` | brainstorm 分诊后的自动交接规则 |
| stage-skill | `cs-feat-design/SKILL.md` | design review 通过后自动进入实现 |
| stage-skill | `cs-feat-impl/SKILL.md` | implement review 通过后自动进入验收 |
| stage-skill | `cs-feat-accept/SKILL.md` | acceptance 收尾自动交接 req/note |
| stage-skill | `cs-issue-report/SKILL.md` | report 确认后自动进入 analyze/fix |
| stage-skill | `cs-issue-analyze/SKILL.md` | analysis 方案确认后自动进入 fix |
| stage-skill | `cs-issue-fix/SKILL.md` | issue fix 终局规则保留真实确认 |

## 5. 执行步骤

### 1. 实施共享自动编排协议

- 状态：done
- 来源：roadmap item `orchestration-shared-protocol`
- 完成信号：`cs-onboard/reference/shared-conventions.md` 和 `.codestable/reference/shared-conventions.md` 都包含自动编排、checkpoint、handoff、结构化提问协议，并通过行数检查。

### 2. 改造入口型技能

- 状态：done
- 来源：roadmap item `orchestration-entry-skills`
- 完成信号：`cs`、`cs-feat`、`cs-issue`、`cs-task`、`cs-roadmap` 不再要求用户复制粘贴已判定的下一步 skill。

### 3. 改造阶段型技能

- 状态：done
- 来源：roadmap item `orchestration-stage-skills`
- 完成信号：brainstorm、feature、issue 阶段技能在用户 review 通过后自动进入下一阶段，同时保留真实 checkpoint。

### 4. 一致性验收

- 状态：done
- 来源：roadmap item `orchestration-consistency-pass`
- 完成信号：相关技能旧式路由表述已清理，roadmap items 状态已同步，Markdown 文档均不超过 300 行。

## 6. 中断恢复提示

任务已完成并归档；如需继续，可启动后续 `cs-arch backfill`。

## 7. 完成与归档记录

2026-05-30：已完成共享协议、入口技能、阶段技能和一致性验收；roadmap items 状态已同步为 done。

2026-05-30：归档到 `.codestable/tasks/archived/2026-05-30-automatic-orchestration-protocol.md`，active 中同名任务已清理。
