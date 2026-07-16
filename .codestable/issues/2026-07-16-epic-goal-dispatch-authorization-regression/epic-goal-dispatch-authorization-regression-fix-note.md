---
doc_type: issue-fix
issue: 2026-07-16-epic-goal-dispatch-authorization-regression
status: confirmed
path: standard
fix_date: 2026-07-16
related: [epic-goal-dispatch-authorization-regression-analysis.md]
tags: [cs-epic, goal, authorization, regression]
---

# Epic Goal 派发授权交互回归修复记录

## 1. 根因摘要

`cs-epic` 把两份需要独立机械核验的 authorization evidence 映射成两个串行用户 checkpoint。
证据分离被错误扩大为交互分离，导致用户无法确认一条完整 `/goal` 后立即开始实现。

## 2. 实际采用方案

- 保留 `approval-report.md#goal-acceptance` 与 `approval-report.md#goal-commits` 两份独立 ref，但只展示一个 `ConfirmGoalExecutionAuthorization`。
- 首次 package 写 `awaiting-authorization`、两项 pending decision 与 pending `approval_groups.goal-execution`。
- owner 一次批准后，先 atomic replace canonical approval report，写入非空 confirmation ID、approved group 与两项 approved decision，形成 durable commit point；再幂等同步 goal-state projection。
- durable group 已批准但 projection 半更新时返回 `repair-epic-goal-execution-authorization`，不再次询问；修复后立即 dispatch。
- canonical rejection 仍 handoff；空 ID、group missing/pending/invalid 只进入同一个 execution user gate。
- 仅没有新 marker 的 1.0.4 旧 artifact 可走严格 legacy compatibility。

## 3. 改动范围

- `cs-epic/SKILL.md`、goal protocol 与 command template：统一 typed checkpoint，并建模 group ready/repair/rejection/legacy 状态。
- `codestable_gate_common.py`：共享 canonical approval path 与 named approval group 校验，阻止 unit 外 symlink。
- `codestable-workflow-next.py`：统一 user gate、durable repair、严格 legacy 与拒绝优先级。
- `codestable-goal-consistency-gate.py`：最终审计核验 group ID、两份 named ref 与 state projection。
- approval/shared conventions 的 source 与 runtime copy：记录原子 approval group 和 scoped commit 边界。
- workflow、consistency、skill contract tests：覆盖 pending、半更新、错 ID、stale rejected projection、空 ID、state-first、legacy、外部 symlink、repair 后 dispatch。
- 本 issue 的 report、analysis、approval、fix 与 review artifacts。

## 4. 验证结果

- pending 两项只返回 `authorize-epic-goal-execution`，同时展示两份 ref。
- approved durable group + pending/半更新/错 ID/stale rejected projection：只返回 repair，不返回 user gate。
- 空 confirmation ID：返回统一 user gate，不进入 repair loop。
- repaired projection：直接返回 `dispatch_goal`。
- external `approval-report.md` symlink：workflow user gate、final gate failed，均不进入 repair。
- final official suite：`608 passed, 1 skipped`。
- package checker、runtime sync check、`git diff --check`：全部通过。
- 独立 `codex/gpt-5.6-sol` review 最终 `passed`，`VerifiedNoWrite: true`。

## 5. 遗留事项

- 尚未执行真实宿主从一次 owner answer 到 atomic replace、projection repair、driver dispatch 的端到端 smoke；repo 内各阶段行为已分别覆盖。
- 通用 validator 对 CodeStable 既有扩展 frontmatter 的兼容问题不在本 issue 范围；本轮使用仓库 package checker。
- 工作区仍有本 issue 之外的并行改动；提交只纳入明确 scoped paths。
