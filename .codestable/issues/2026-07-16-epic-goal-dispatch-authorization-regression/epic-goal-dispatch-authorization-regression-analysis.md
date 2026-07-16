---
doc_type: issue-analysis
issue: 2026-07-16-epic-goal-dispatch-authorization-regression
status: confirmed
root_cause_type: logic
related: [epic-goal-dispatch-authorization-regression-report.md]
tags: [cs-epic, goal, authorization, state-machine]
---

# Epic Goal 派发授权交互回归根因分析

## 1. 问题定位

| 关键位置 | 说明 |
|---|---|
| `plugins/codestable/skills/cs-epic/SKILL.md:142` | `restoreEpicStage` 把缺少 acceptance 与 commit 授权建模成两个串行 `HumanCheckpoint`。 |
| `plugins/codestable/skills/cs-epic/references/goal/protocol.md:42` | GoalPackage 协议同样先后返回两种 checkpoint，只有都通过才选择 driver。 |
| `plugins/codestable/skills/cs-onboard/tools/codestable-workflow-next.py:1357` | runtime 先返回 `authorize-epic-goal-acceptance`，下一轮再返回 `authorize-epic-goal-commits`。 |
| `plugins/codestable/skills/cs-epic/references/goal/support/goal-command-template.md:6` | `/goal` 模板只在两项授权完成后才交付或派发，用户无法直接确认实际执行指令。 |

## 2. 失败路径还原

**正常路径**：全部 design 统一确认 → 生成 goal package 和完整 `/goal` 指令 → 展示执行范围 →
用户确认一次 → 原子记录 acceptance 与 scoped-commit 两份机器授权证据 → 立即派发 Goal driver。

**失败路径**：全部 design 统一确认 → 生成 goal package → acceptance 缺失分支返回第一个
`HumanCheckpoint` → 用户批准后 runtime 恢复 → commit 缺失分支返回第二个 `HumanCheckpoint` →
第二次批准后才生成或派发 `/goal`。

**分叉点**：`plugins/codestable/skills/cs-epic/SKILL.md:142` - 状态机把两个需要独立核验的
机器证据错误映射成两个必须串行交互的 owner 决策。

## 3. 根因

**根因类型**：逻辑错误。

**根因描述**：`1.0.4` 为避免 Goal driver 隐式完成 acceptance 或未经授权自动 commit，正确增加了
两份独立 `ApprovalRef`；但实现进一步要求两次独立输入和两次 checkpoint。机器证据需要分别命名、
分别复核，并不意味着用户必须分两轮批准。一次明确展示完整 `/goal` 与副作用范围的确认，可以原子
产生两份证据，同时保留 acceptance ref 不可替代 commit ref 的安全约束。

**是否有多个根因**：有。主因是 checkpoint 建模过细；次因是 goal package 模板、runtime 路由、
测试共同固化了串行交互，使问题稳定复现。当前工作区还在修正 `ready-to-dispatch + pending` 的状态
矛盾，但单独修正该矛盾不能消除两次确认。

## 4. 影响面

- **影响范围**：所有首次生成且两项授权尚未批准的 Epic goal；单 feature Goal 只有 acceptance，暂不受影响。
- **潜在受害模块**：`cs-epic` 主状态机、GoalPackage 协议、workflow-next runtime、goal command 模板、共享 goal 约定和相关测试。
- **数据完整性风险**：不会损坏业务代码，但可能留下 `ready-to-dispatch` 与 pending authorization 并存的矛盾状态。
- **严重程度复核**：维持 P1；核心长程执行被稳定阻断，但可通过两次人工批准绕过。

## 5. 修复方案

### 方案 A：一次 checkpoint，原子写入两份独立授权证据

- **做什么**：新增统一的 `ConfirmGoalExecutionAuthorization` 和对应 authorize/reject input；package
  首次写入时两项仍为 pending。checkpoint 展示完整 `/goal`、acceptance 与 scoped-commit 范围；一次
  批准原子把 `goal-acceptance`、`goal-commits` 两项都写为 approved，然后立即派发。
- **优点**：恢复期望交互；保留现有 runtime/gate 对两份 ref 的机械核验；迁移与风险最小。
- **缺点 / 风险**：需要同步修改 skill、protocol、runtime 文案和测试；必须保证原子更新，不能只批准一项。
- **影响面**：Epic goal package 与派发路径；不改变 push、publish、deploy 等外部副作用门。

### 方案 B：用单一 `goal-execution` ApprovalRef 替换两份证据

- **做什么**：删掉 acceptance/commit 两个字段和命名 decision，只保留一个 umbrella authorization。
- **优点**：状态模型最简单，交互与数据都只有一个概念。
- **缺点 / 风险**：acceptance 与 Git commit 无法在运行时独立撤销或复核；需要迁移所有既有 goal-state、
  consistency gate 和 feature loop，兼容性与安全回归风险较大。
- **影响面**：所有 Epic goal artifacts、runtime gates、审计协议与历史状态恢复。

### 方案 C：先授权 acceptance 开始实现，首次 commit 前再询问

- **做什么**：第一次确认后派发 driver，保留 commit pending；feature accepted 后再 handoff 请求 commit。
- **优点**：实现可以更早开始，提交仍保持独立决策。
- **缺点 / 风险**：长程 goal 会在第一个 feature 边界再次中断，仍不满足一次确认后连续执行的目标。
- **影响面**：driver feature loop 和 handoff 恢复路径。

### 推荐方案

**推荐方案 A**。它把用户交互恢复为一次确认，同时继续用两份不同的 `ApprovalRef` 约束 acceptance
和 scoped commit；安全边界没有被删除，只是不再错误地表现为两个串行对话门。
