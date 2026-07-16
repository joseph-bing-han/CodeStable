---
doc_type: issue-review
issue: 2026-06-30-task-archive-move-original
status: passed
reviewer: subagent
reviewed: 2026-06-30
round: 1
---

# task-archive-move-original 代码审查报告

## 1. Scope And Inputs

- Report / analysis / fix-note: 本次为缺失 Task 的 backfill 场景，问题与修复依据来自当前对话、Task spine 和 git diff。
- Task: `.codestable/tasks/active/task-archive-move-original.md`
- Implementation evidence: `cs-task/SKILL.md`、`cs-task/reference.md`、`tests/test_workflow_contracts.py`
- Diff basis: `git status --short` 显示 3 个 tracked 修改；`git diff` 覆盖本次协议与测试改动。
- Validation: `uvx pytest -q` 通过 21 tests。
- Baseline dirty files: 无可见 tracked 范围外修改。

### Independent Review

- Status: completed
- Detection: paseo-subagent recommended but no callable Paseo CLI in current runtime; used Cursor subagent review.
- Cursor config: `.codestable/config/code-review-subagent.yaml` model=gpt-5.5 thinking_budget=xhigh
- Provider / agent: Cursor subagent
- Raw output: 当前对话 subagent 返回 verdict `passed`，无 blocking / important findings。
- Merge policy: 已核验 subagent finding 与本地 diff；nit / suggestion 不阻塞通过。
- Gate effect: reviewer is `subagent`; review evidence gate can treat this as passed.

## 2. Diff Summary

- 新增：`.codestable/tasks/active/task-archive-move-original.md`、本 review 报告
- 修改：`cs-task/SKILL.md`、`cs-task/reference.md`、`tests/test_workflow_contracts.py`
- 删除：无 tracked 删除
- 未跟踪 / staged：`.codestable/` 可能被 ignore，Task 与 review 作为 CodeStable 运行产物存在。
- 风险热点：workflow 协议行为、Task 归档闭环、agent 执行一致性。

## 3. Findings

### blocking

none

### important

none

### nit

- [ ] REV-001 `tests/test_workflow_contracts.py` 测试函数名仍偏向 ignore-filtered scan，但新增断言已经覆盖 archive move contract。
  - Evidence: 同一测试函数新增了 `mv`、禁止复制式归档、active 同名源硬退出条件的断言。
  - Impact: 不影响正确性；未来测试失败时定位语义略宽。

### suggestion

- [ ] REV-002 `cs-task/reference.md` 可后续补充更完整的反漂移断言。
  - Evidence: 当前测试已断言 reference 包含“先移动 active 原文件”和 `mv` 示例；对“禁止复制式归档”和“硬退出条件”的 reference 断言相对少于 SKILL.md。
  - Impact: 不阻塞本次修复；属于后续增强。

### learning

- Task 归档协议必须把“移动源文件”和“active 源消失”作为同一个原子闭环来描述，否则 agent 容易退化成复制式归档。

### praise

- 本次修改同时更新了 skill、reference 和 workflow contract test，降低了同类协议回归风险。

## 4. Test And QA Focus

- QA 必须重点复核：在 `.codestable/` 被 `.gitignore` 忽略时，completed task 归档必须先 `mv` active 原文件到 archived 目标路径。
- 建议新增或加强的测试：未来如引入可执行 task archive runtime，应补充 sandbox integration test 覆盖目标已存在、残留清理、删除失败、archived 状态不一致。
- 不能靠 review 完全确认的点：当前 CodeStable 归档主要由 skill 协议驱动；真实行为仍依赖后续 agent 严格执行协议。

## 5. Residual Risk

- 本次修复是文档协议与契约测试收紧，不是独立归档器实现。后续如果新增可执行归档工具，应把本协议落实为代码级原子 move 操作。

## 6. Verdict

- Status: passed
- Next: 更新 Task 为 completed，并同轮执行 `cs-task archive`，用 `mv` 移动 active 原文件到 archived 后只编辑 archived 目标。
