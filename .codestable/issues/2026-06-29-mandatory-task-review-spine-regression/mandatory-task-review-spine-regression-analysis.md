---
doc_type: issue-analysis
issue: 2026-06-29-mandatory-task-review-spine-regression
status: confirmed
root_cause_type: missing-guard
related:
  - mandatory-task-review-spine-regression-report.md
tags: [workflow, task, code-review, handoff]
---

# 完整入口缺失 Task 与 Code Review 主线根因分析

## 1. 问题定位

| 关键位置 | 说明 |
|---|---|
| `/Users/joseph/Downloads/cursor_mqtt_log_warning_analysis.md` | 对话显示 `/cs-issue` 只在 chat 中整理 report，后续由用户手动触发 analyze / fix / task。 |
| `cs-issue-report/SKILL.md` | 虽然写了要创建 Task，但退出条件没有把 active Task、`owner_skill` 和 `related_docs` 作为硬门禁。 |
| `cs-issue-analyze/SKILL.md` | 允许用户直接 analyze 的语义过强，缺少“无 report / 无 Task 不分析”的动作级守卫。 |
| `cs-issue-fix/SKILL.md` | 仍存在“下一步进入 code-review”的提示式出口，未明确 fix 后必须立刻执行 `cs-code-review`。 |
| `cs-code-review/SKILL.md` | 作为横切 gate，没有强制复用 / backfill Task，也没有规定 passed 后如何 complete / archive。 |
| `cs-task/SKILL.md` | 缺少“已有产物但 Task 缺失”的 backfill 恢复模式，导致用户指出缺 Task 后只补账本、不续跑 review gate。 |
| `.codestable/reference/shared-conventions.md` | 自动编排协议强调 handoff，但没有把 `Task → spec → code review → archive` 写成不可缺失的 workflow spine。 |

## 2. 失败路径还原

**正常路径**：`/cs-issue` → 自动进入 report → 首次落盘前创建 Task → report 落盘并登记 Task → 用户 L2 通过后自动 analyze → analysis 登记 Task → 用户确认方案后自动 fix → fix-note 登记 Task → 立即执行 `cs-code-review` → review passed → Task completed → `cs-task archive`。

**失败路径**：`/cs-issue` → chat 中整理 report / 初步根因 → 用户手动 `/cs-issue-analyze` → chat 中产出 analysis → 用户手动 `/cs-issue-fix` → 修代码和 fix-note → 只提示“下一步应进入 `cs-code-review`” → 用户发现 Task 缺失后手动 `/cs-task` 补建 → 仍未自动续跑 review。

**分叉点**：协议和技能都缺少全局 spine gate；单个阶段可以“看起来完成”，但没有被 Task、落盘产物、review gate 和 archive 共同约束。

## 3. 根因

**根因类型**：missing-guard

**根因描述**：已有文案把 Task 和 code review 描述成“应该做的步骤”，但没有把它们作为阶段退出前置条件。Agent 因此能用 chat-only 输出替代正式 report / analysis，能在修复完成后停在“下一步建议”，也能在发现 Task 缺失时只 backfill Task 而不继续 review gate。

**是否有多个根因**：有。主根因是共享协议缺少 workflow spine gate；次根因是 issue 阶段、code-review 横切 gate、cs-task 恢复模式各自缺少动作级硬门禁。

## 4. 影响面

- **影响范围**：所有会落盘或改代码的完整入口，尤其是 issue、feature fastforward、refactor 和后续 code review 收口。
- **潜在受害模块**：Task 恢复、CodeStable 产物索引、code review gate、archive 历史记录。
- **数据完整性风险**：无业务数据风险；有流程数据风险，后续 agent 无法恢复任务上下文或确认是否 review 通过。
- **严重程度复核**：维持 P1，因为这直接破坏完整入口的工程闭环。

## 5. 修复方案

### 方案 A：只补 issue 三个阶段

- **做什么**：强化 `cs-issue-report` / `cs-issue-analyze` / `cs-issue-fix`。
- **优点**：能修复本次 MQTT 对话暴露的直接问题。
- **缺点 / 风险**：feature / refactor / fastforward 仍可能缺 Task 或 review。
- **影响面**：覆盖不足。

### 方案 B：新增共享 Workflow spine gate，并同步 issue、task、code-review 和代码型出口

- **做什么**：在 shared conventions 与 system overview 中规定 `Task → spec → code review → archive` 不可缺；同步 issue 阶段、`cs-task` backfill、`cs-code-review` Task gate，以及 feature/refactor 的 review 出口。
- **优点**：同时覆盖入口、阶段、恢复和最终 gate。
- **缺点 / 风险**：修改文件较多，需要控制 Markdown 行数。
- **影响面**：符合问题范围。

### 方案 C：只要求用户每次手动 `/cs-task` 和 `/cs-code-review`

- **做什么**：把自动流程改成用户手动分段触发。
- **优点**：实现最少。
- **缺点 / 风险**：违背 CodeStable 完整入口目标，也违背用户本次要求。
- **影响面**：方向错误。

### 推荐方案

**推荐方案 B**，理由：这不是单个 `cs-issue` 文案问题，而是完整 workflow spine 缺少不可绕过的门禁。必须从共享协议、Task 恢复、code review gate 和关键阶段出口一起修。
