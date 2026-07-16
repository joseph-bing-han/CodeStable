---
doc_type: issue-review
issue: 2026-07-16-epic-goal-dispatch-authorization-regression
status: passed
reviewed: 2026-07-16
round: 4
lane_a_state: completed
lane_a_ref: "10f5ba8d-f177-4187-a43b-f325cc1b5acc"
lane_a_reason: "owner-authorized codex/gpt-5.6-sol fallback passed after full re-review and focused closures; VerifiedNoWrite"
lane_b_state: skipped
lane_b_ref: ""
lane_b_reason: "skipped-scope-ambiguous: workspace contains unrelated dirty and untracked paths"
---

# Epic Goal 派发授权交互回归代码审查报告

## 1. Scope And Inputs

- Design: `epic-goal-dispatch-authorization-regression-analysis.md`
- Implementation evidence: `epic-goal-dispatch-authorization-regression-fix-note.md`
- Diff basis: 当前 scoped unstaged diff；工作区其他 code-review、docs、issue/refactor 改动不纳入 verdict
- Review mode: initial independent review + full re-review + focused closure

## 2. Independent Review

- `claude/claude-fable-5` reviewer `a2322ff9-23c2-41f1-a469-06cd9cf7a8b7` 与 retry `ea90075b-2a25-48d8-b660-ca98f13e99b9` 均在推理前返回 provider 503。
- owner 明确授权 fallback 到 Paseo `codex/gpt-5.6-sol`。
- reviewer `1e9da17e-fe69-40b3-a31d-f7abfcd3dbbe` 首轮要求补 durable commit point、崩溃恢复与真实状态组合测试。
- reviewer `1689af66-5618-493a-9049-fca34c203bde` 复审发现正式 Spec 未建模 canonical group，以及外部 symlink 可形成永久 repair。
- reviewer `10f5ba8d-f177-4187-a43b-f325cc1b5acc` 完整复审与两次 focused closure，最终 `passed`；各轮起止 status/diff/file SHA 一致，`VerifiedNoWrite: true`。

## 3. Closed Findings

### blocking

- closed：canonical `approval_groups.goal-execution` 是唯一 durable commit point；落盘后 projection 任意半更新只自动 repair，不再次 user gate。
- closed：Skill 与 goal protocol 只允许非空 `GroupApproved` + matching projection，或严格 `StrictLegacy104` 构造 ready；state-first 不得 dispatch。
- closed：canonical approval path 必须留在 workflow unit；外部 symlink 在 workflow/final gate 均 fail-closed，不再 repair loop。
- closed：canonical rejection 优先 handoff；有效 approved group 的 stale rejected projection 优先 repair；空 confirmation ID 进入 user gate，不得永久 repair。

### important

- none

### nit

- none

## 4. Verification

- focused runtime/contract/scenario closure：`302 passed`
- final official suite：`608 passed, 1 skipped`
- `python3 tools/check-plugin-package.py`：passed
- `codestable-runtime-sync.py --root . --check --json`：`ok`，`drifted_paths: []`
- `git diff --check`：passed
- independent final closure：`212 passed`，两份 300 行 skill/protocol 文档满足行数约束

## 5. Residual Risk

- repo 内测试分别覆盖 owner confirmation 后的 repair decision 与已修复 projection 的 dispatch；尚未在真实宿主中执行从一次 owner answer、atomic replace、state repair 到 driver dispatch 的完整交互 smoke。
- 该宿主集成风险不构成当前 repo 修复 blocker；runtime、Spec 与测试已一致。

## 6. Verdict

- Status: passed
- Findings: blocking none, important none, nit none
- Reviewer: Paseo `codex/gpt-5.6-sol`
- VerifiedNoWrite: true

## 7. Focused Closure

- approved group + stale rejected projection：repair，closed
- approved group + empty confirmation ID：single user gate，closed
- ready approved group：dispatch，closed
- canonical group/named rejection：handoff，closed
