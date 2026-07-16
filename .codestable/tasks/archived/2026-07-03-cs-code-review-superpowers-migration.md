---
doc_type: task-list
task: cs-code-review-superpowers-migration
goal: Migrate cs-code-review to the SuperPowers-style reviewer subagent flow and sync the installed skill copy
status: archived
workflow: feature
owner_skill: cs-code-review
created: 2026-07-03
updated: 2026-07-03
archived: 2026-07-03
related_docs:
  - cs-code-review/SKILL.md
  - cs-code-review/references/report-template.md
  - cs-code-review/references/code-reviewer-prompt.md
  - cs-issue/SKILL.md
  - cs-issue-fix/SKILL.md
  - cs-refactor/SKILL.md
  - cs-refactor-ff/SKILL.md
  - cs-feat/SKILL.md
  - cs-feat-design/SKILL.md
  - cs-feat-impl/SKILL.md
  - cs-feat-accept/SKILL.md
  - cs-feat-ff/SKILL.md
  - cs/SKILL.md
  - cs-onboard/SKILL.md
  - cs-onboard/reference/shared-conventions.md
  - cs-onboard/reference/workflow-conventions.md
  - cs-onboard/reference/system-overview.md
  - .codestable/features/2026-07-03-cs-code-review-superpowers-migration/cs-code-review-superpowers-migration-review.md
---

# Migrate cs-code-review to the SuperPowers-style reviewer subagent flow and sync the installed skill copy

## 1. 任务目标

将 `cs-code-review` 从旧的 Paseo / detect-review-agent / managed reviewer 链路迁移为 SuperPowers `requesting-code-review` 风格的 reviewer subagent 模式，并保持当前项目源文件与 `~/.agents/skills/cs` 安装副本一致。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 定位当前 CodeStable 项目内 `cs-code-review` 与相关技能源文件
- [x] 把 SuperPowers-style code review 迁移应用到当前项目源文件
- [x] 从当前项目源文件同步到 `~/.agents/skills/cs`
- [x] 拆分 shared-conventions，确保单个 Markdown 不超过 300 行
- [x] 对本次 skill 迁移执行 `cs-code-review` gate

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| skill | `cs-code-review/SKILL.md` | `cs-code-review` 主技能说明，已迁移为 reviewer subagent 模式 |
| template | `cs-code-review/references/report-template.md` | CodeStable review 报告模板 |
| prompt | `cs-code-review/references/code-reviewer-prompt.md` | reviewer subagent prompt 模板 |
| related-skill | `cs-issue/SKILL.md` | issue 流程里的 review 文件名与 gate 表述同步 |
| related-skill | `cs-issue-fix/SKILL.md` | issue fix 收尾与 review gate 表述同步 |
| related-skill | `cs-refactor/SKILL.md` | refactor review 文件名与 gate 表述同步 |
| related-skill | `cs-refactor-ff/SKILL.md` | refactor fastforward review gate 表述同步 |
| related-skill | `cs-feat/SKILL.md` | feature 流程代码审查阶段表述同步 |
| related-skill | `cs-feat-design/SKILL.md` | shared-conventions 拆分后 roadmap / compound 检索引用同步到 workflow-conventions |
| related-skill | `cs-feat-impl/SKILL.md` | shared-conventions 拆分后反射检查引用同步到 workflow-conventions |
| related-skill | `cs-feat-accept/SKILL.md` | shared-conventions 拆分后 roadmap / 收尾提交引用同步到 workflow-conventions |
| related-skill | `cs-feat-ff/SKILL.md` | feature fastforward review 文件名与 gate 表述同步 |
| related-skill | `cs/SKILL.md` | 根入口 route level 表述同步 |
| onboard-skill | `cs-onboard/SKILL.md` | 标准骨架 reference 列表补入 workflow-conventions |
| shared-reference | `cs-onboard/reference/shared-conventions.md` | onboarding 目录结构、共享元数据与 checklist 生命周期口径 |
| shared-reference | `cs-onboard/reference/workflow-conventions.md` | 从 shared-conventions 拆出的 workflow 运行规则、scoped commit 与反射检查口径 |
| shared-reference | `cs-onboard/reference/system-overview.md` | 进一步参考拆分 shared / workflow 两类共享口径 |
| review | `.codestable/features/2026-07-03-cs-code-review-superpowers-migration/cs-code-review-superpowers-migration-review.md` | 本轮 code review gate，status passed |

## 5. 执行步骤

### 1. 定位源文件与安装副本

- 状态：done
- 来源：manual
- 完成信号：已确认当前项目源文件在 `/Users/joseph/code/CodeStable`，安装副本在 `~/.agents/skills/cs`。

### 2. 迁移 `cs-code-review` 源文件

- 状态：done
- 来源：manual
- 完成信号：当前项目 `cs-code-review` 已替换为 reviewer subagent 模式，旧检测脚本与旧 agent 配置已移除。

### 3. 同步相关技能表述

- 状态：done
- 来源：manual
- 完成信号：当前项目相关 `cs-*` 技能已同步 `{slug}-review.md`、`blocking / important` 与 reviewer subagent / self fallback 表述。

### 4. 同步安装副本

- 状态：done
- 来源：manual
- 完成信号：`~/.agents/skills/cs` 已同步当前项目的 `cs-code-review` 与相关技能表述。

### 5. 拆分共享口径文档

- 状态：done
- 来源：code-review-important-finding
- 完成信号：`cs-onboard/reference/shared-conventions.md` 已拆出 `cs-onboard/reference/workflow-conventions.md`；source 与 installed copy 的旧章节引用已同步改向，两个单文件均低于 300 行。

### 6. 执行代码审查 gate

- 状态：done
- 来源：workflow-spine
- 完成信号：本次 skill 迁移的 `{slug}-review.md` 已落盘，review `status: passed`，reviewer 为 `subagent`。

## 6. 中断恢复提示

任务已归档。若后续要继续清理其他技能里的 Paseo / local reviewer 链路，另起独立任务。

## 7. 完成与归档记录

- 完成日期：2026-07-03
- 归档日期：2026-07-03
- review evidence：`.codestable/features/2026-07-03-cs-code-review-superpowers-migration/cs-code-review-superpowers-migration-review.md`
- 结论：`cs-code-review` 已迁移为 reviewer subagent + self fallback 模式，source 与 installed copy 已同步，本轮 review gate passed。
