---
doc_type: issue-analysis
issue: 2026-06-29-stage-handoff-auto-continue-regression
status: confirmed
root_cause_type: missing-guard
related:
  - stage-handoff-auto-continue-regression-report.md
tags: [workflow, handoff, checkpoint, direct-entry]
---

# 阶段 Handoff 自动续跑回归根因分析

## 1. 问题定位

| 关键位置 | 说明 |
|---|---|
| `cs-onboard/reference/shared-conventions.md:184` | 新版共享协议只写“完整入口”和“自动编排”，但没有显式禁止“推荐使用某 skill / 请运行某 skill”的出口。 |
| `cs-onboard/reference/shared-conventions.md:188` | handoff 只说 `open_questions` 为空必须继续，没有把“当前 agent 必须读取并执行目标 SKILL.md”写成动作级约束。 |
| `cs-issue-report/SKILL.md:150` | report 退出后只说“下一步阶段 2 根因分析”，缺少结构化 L2 checkpoint 的固定选项与禁止推荐出口。 |
| `cs-issue-analyze/SKILL.md:168` | analyze 退出后只说“自动进入 cs-issue-fix”，缺少用户确认后的动作级续跑约束。 |
| `cs-brainstorm/SKILL.md:18` | 已说明 brainstorm 是完整入口，但 case 出口没有统一禁止把目标 skill 名称交还给用户。 |

## 2. 失败路径还原

**正常路径**：入口 skill 判定阶段 → 如果无开放问题，当前 agent 读取目标 `SKILL.md` 并继续执行 → 如果是 L2 review，结构化选项让用户选“通过继续” → 用户确认后自动进入下游 → Task、文档、review、归档持续推进。

**失败路径**：入口或阶段 skill 产出“下一步是 X / 建议使用 X” → 当前回合结束 → 用户必须重新触发 skill → 下游无法稳定复用当前 handoff、Task 和阶段上下文 → 完整主线断裂。

**分叉点**：共享协议和具体出口都缺少“禁止 chat-only 推荐”和“当前 agent 必须执行目标 skill”的动作级硬约束。

## 3. 根因

**根因类型**：missing-guard

**根因描述**：旧修复主要强调 direct entry 也是完整入口，但新版技能仍存在弱出口表述。Markdown 技能被 runtime 读取时，如果只写“下一步某 skill”而没有动作级约束，模型容易把它解释成对用户的建议，而不是本轮必须继续执行的 handoff。

**是否有多个根因**：有。主根因是共享协议缺少动作级禁止语；次根因是 issue / brainstorm / roadmap 等具体 skill 的阶段出口没有统一写成结构化 checkpoint 与自动续跑。

## 4. 影响面

- **影响范围**：所有 direct-entry 与阶段 handoff，重点是 `cs`、`cs-issue`、`cs-brainstorm`、`cs-feat`、`cs-refactor`、`cs-roadmap`、`cs-audit`。
- **潜在受害模块**：Task List 创建 / 更新、issue analysis、feature design、roadmap 到 feature 的交接、audit finding 到 issue/refactor 的交接。
- **数据完整性风险**：无业务数据风险；有流程数据风险，可能造成文档或 Task 缺失。
- **严重程度复核**：维持 P1，因为它影响 CodeStable 主承诺，而非单个文案瑕疵。

## 5. 修复方案

### 方案 A：只改 `cs-issue-report` 出口

- **做什么**：把 report 退出文案改成结构化 checkpoint。
- **优点**：改动最少。
- **缺点 / 风险**：只能修复本次例子，其它入口继续漂移。
- **影响面**：低，但覆盖不足。

### 方案 B：共享协议动作级加固，并同步关键入口与阶段出口

- **做什么**：在 shared conventions / system overview 加入“禁止推荐出口”和“当前 agent 必须执行目标 skill”；同步 `cs`、`cs-issue`、`cs-issue-report`、`cs-issue-analyze`、`cs-brainstorm`、`cs-feat`、`cs-refactor`、`cs-roadmap`、`cs-audit`。
- **优点**：覆盖入口等价、阶段 checkpoint 和跨 lane handoff。
- **缺点 / 风险**：涉及多个 Markdown 文件，需要控制单文件 300 行限制。
- **影响面**：中等，符合问题范围。

### 方案 C：让所有入口都强制回到 `cs`

- **做什么**：子入口只做提示，让用户统一从 `cs` 开始。
- **优点**：实现简单。
- **缺点 / 风险**：违背 direct-entry 完整入口目标，也不符合用户要求。
- **影响面**：高且方向错误。

### 推荐方案

**推荐方案 B**，理由：本次是共享流程契约和多个出口共同导致的回归，必须从协议层和关键 skill 同时加固。
