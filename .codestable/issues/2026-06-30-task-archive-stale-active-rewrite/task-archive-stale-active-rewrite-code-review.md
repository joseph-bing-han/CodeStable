---
doc_type: issue-review
issue: 2026-06-30-task-archive-stale-active-rewrite
status: passed
reviewer: subagent
reviewed: 2026-06-30
round: 1
---

# task-archive-stale-active-rewrite 代码审查报告

## 1. Scope And Inputs

- Report: `.codestable/issues/2026-06-30-task-archive-stale-active-rewrite/task-archive-stale-active-rewrite-report.md`
- Fix note: `.codestable/issues/2026-06-30-task-archive-stale-active-rewrite/task-archive-stale-active-rewrite-fix-note.md`
- Task: `.codestable/tasks/active/task-archive-stale-active-rewrite.md`
- Implementation evidence: `cs-task/SKILL.md`、`cs-task/reference.md`、`tests/test_workflow_contracts.py`
- Diff basis: `git status --short` 与 `git diff`，tracked 改动集中在三份源文件。
- Validation: `uvx pytest -q` 通过 21 tests。
- Baseline dirty files: 无可见 tracked 范围外修改。

### Independent Review

- Status: completed
- Detection: Cursor subagent review
- Cursor config: `.codestable/config/code-review-subagent.yaml` model=gpt-5.5 thinking_budget=xhigh
- Provider / agent: Cursor subagent
- Raw output: subagent verdict `passed`，无 blocking / important findings。
- Merge policy: 已核验 subagent finding 与本地 diff；nit / suggestion 不阻塞通过。
- Gate effect: reviewer is `subagent`; review evidence gate can treat this as passed.

## 2. Diff Summary

- 新增：本 issue 的 report、fix-note、review、active Task 运行产物。
- 修改：`cs-task/SKILL.md`、`cs-task/reference.md`、`tests/test_workflow_contracts.py`
- 删除：无 tracked 删除。
- 未跟踪 / staged：`.codestable/` 可能被 ignore，issue / task 作为 CodeStable 运行产物存在。
- 风险热点：workflow 归档收尾、ignored 目录最终验证、旧 active path 写回。

## 3. Findings

### blocking

none

### important

none

### nit

- [ ] REV-001 `tests/test_workflow_contracts.py` 当前测试函数名承载语义较多。
  - Evidence: 同一测试同时断言 ignore-filtered search、`mv` 非复制归档、stale active rewrite 防护、最终回复前验证、不能依赖历史 shell test exit code。
  - Impact: 不影响本次正确性；后续若继续扩展可拆成更小测试。

### suggestion

- [ ] REV-002 可后续增加 installed skill 副本同步校验。
  - Evidence: 当前 contract test 只读取仓库内 `cs-task/SKILL.md` 与 `cs-task/reference.md`；本次 installed copy 通过人工读取确认一致。
  - Impact: 不阻塞本次修复；属于后续自动化增强。

### learning

- 对 ignored workflow 目录做归档时，`mv` 后的源路径必须视为失效路径；最终回复前必须重新读取当前文件系统事实，而不是复用历史 shell exit code。

### praise

- 本次修复同时覆盖 source skill、reference、installed copy 与 contract test，能降低同类流程回归风险。

## 4. Test And QA Focus

- QA 必须重点复核：`cs-task archive` 在 `mv` 后只能编辑 archived 目标，不能再写 active 源路径。
- 建议新增或加强的测试：未来若实现可执行归档工具，应新增行为测试模拟 `mv -> archived 更新 -> active 源路径被重新写回 -> final verification 必须失败或清理后再验证`。
- 不能靠 review 完全确认的点：当前修复为协议与文本契约级别，不是可执行归档器实现。

## 5. Residual Risk

- 当前没有 runtime archiver，因此真实归档行为仍依赖 agent 严格执行协议。若后续新增工具，应把本协议落实成代码级原子 move 和 final filesystem verification。

## 6. Verdict

- Status: passed
- Next: 更新 Task 为 completed，并同轮执行 `cs-task archive`：先移动 active 原文件到 archived，再只编辑 archived 目标，并在最终回复前重新验证 active 源路径不存在。
