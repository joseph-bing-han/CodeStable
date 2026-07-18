---
doc_type: issue-review
issue: 2026-07-17-historical-review-evidence-remediation
status: passed
reviewer: subagent
reviewed: 2026-07-18
round: 1
review_basis: independent-readonly-then-closure
---

# historical-review-evidence-remediation 独立审查报告

## Verdict

**passed**

首轮 focused review 曾将 `codestable-code-reviewer` 的 `model: gpt-5.6-sol` 标为 blocking。owner 明确：该字段为 Cursor 宿主协议兜底，应忽略，不作为缺陷。已恢复并写清「优先当前主模型最高档；`model:` 仅作宿主兜底」。其余 important 项（self 与 live complete gate 分层、protocol 单一路径）已在协议层收敛。

## Findings

### blocking

无。

### important

无未决项。

- **self vs live complete**：协议已写明 `reviewer: self` 合法，但 `workflow-next` complete 仍要求 full canonical `reviewer: subagent` 生命周期证据；禁止 self 伪写 subagent。
- **派发路径**：custom agent → model-safe bridge → 当前主模型最高档 self；禁止 Explore/Fast/unknown-model。
- **Cursor host model 兜底**：`plugins/codestable/agents/code-reviewer.md` 保留 `model: gpt-5.6-sol` 作为宿主兜底，不改变「当前主模型最高思考档」派发意图。

### nit

- 历史单元 remediation review 多为 thin `subagent` + pre-cutoff archived Task（无 full lifecycle hash/ref）；对 historical doctor 目标正确，不作为 live gate 证据。

## Strengths

- legacy Issue `*-code-review.md` 兼容仍校验 schema/identity/status/reviewer。
- 严格 SemVer + 最近 invalid VERSION fail-closed。
- root `cs-*` tools-only 与 package checker 负向测试。
- Cursor Feature review/QA/acceptance 与 requirement delta 机械回写闭环。
- 源码 doctor review findings 清零（`status: implementation-active`，findings count 0）。

## Verification Evidence

| 项 | 结果 |
|---|---|
| doctor review findings | 0 |
| package checker | ok |
| runtime sync check | ok |
| full pytest（先前批次） | 720 passed, 1 skipped |
| review 相关契约测试 | 60 passed（本轮 targeted） |
| `git diff --check` | exit 0 |

## Residual Risk

- 历史 `reviewer: subagent` 无 agent_ref 时依赖声明 + archive 锚点，不可重放独立 agent 会话。
- live complete 仍不接受 self 过 canonical gate；需独立 subagent 生命周期字段。
- Cursor Team Marketplace 真实导入体验未在本仓证明。

## Recommendation

允许写本 issue review 为 **passed**，并 `cs-task complete` + archive。
