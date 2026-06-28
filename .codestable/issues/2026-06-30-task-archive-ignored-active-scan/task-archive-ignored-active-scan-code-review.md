---
doc_type: issue-review
issue: 2026-06-30-task-archive-ignored-active-scan
status: passed
reviewer: subagent
reviewed: 2026-06-30
round: 1
---

# task-archive-ignored-active-scan 代码审查报告

## 1. Scope And Inputs

- Fix note: `.codestable/issues/2026-06-30-task-archive-ignored-active-scan/task-archive-ignored-active-scan-fix-note.md`
- Task: `.codestable/tasks/active/task-archive-ignored-active-scan.md`
- Implementation evidence: 用户截图、归档漏扫复盘、当前 diff、合同测试结果
- Diff basis: `cs-task/SKILL.md`、`cs-task/reference.md`、`tests/test_workflow_contracts.py`
- Baseline dirty files: 已存在的 `cs-code-review/*` 与 code review subagent 合同测试改动属于前一个 issue，上下文相关但不是本 issue 的核心风险点

### Independent Review

- Status: completed
- Detection: cursor-subagent
- Cursor config: `.codestable/config/code-review-subagent.yaml` model=configured thinking_budget=configured
- Provider / agent: generic code review subagent with current-conversation fallback
- Raw output: independent reviewer reported no blocking or important findings; nit about archive section and exit condition wording was fixed
- Merge policy: 已逐条核验并合并有效建议
- Gate effect: passed

## 2. Diff Summary

- 新增：issue fix-note、issue code-review、active/archived Task 产物
- 修改：`cs-task/SKILL.md`、`cs-task/reference.md`、`tests/test_workflow_contracts.py`
- 删除：active Task 将在归档时移除
- 未跟踪 / staged：未单独 stage
- 风险热点：`.codestable/` 被 `.gitignore` 忽略时，受 ignore 影响的搜索工具可能返回 0

## 3. Findings

### blocking

none

### important

none

### nit

- [x] REV-001 `cs-task/SKILL.md` archive/history 小节可局部重复 Task 目录扫描硬约束，降低执行 agent 跳读遗漏概率。
  - Evidence: independent reviewer 建议在归档对象盘点处重复强调。
  - Resolution: 已补充“归档对象盘点同样必须遵守 Task 目录扫描硬约束”。
- [x] REV-002 `cs-task/SKILL.md` 退出条件可重复要求 active 中无同名残留。
  - Evidence: independent reviewer 指出原退出条件只写移动到 archived 和 frontmatter 一致。
  - Resolution: 已将 archive 退出条件改为“已移动到 archived、frontmatter 状态一致，且 active 中没有同名残留”。

### suggestion

none

### learning

- `.codestable/` 被 `.gitignore` 忽略时，CodeStable 自身运行态文件不能用受 ignore 影响的 Glob / rg 作为唯一事实来源；目录枚举和显式文件读取才是 Task spine 的 source of truth。

### praise

- 修复同时更新了 skill 协议、reference 协议和合同测试，避免只靠口头约定防漏扫。

## 4. Test And QA Focus

- QA 必须重点复核：`/cs-task 归档` 盘点 active/archived 时先用不受 ignore 过滤的目录枚举；Glob / rg 返回 0 时不能直接报告无任务。
- 建议新增或加强的测试：若未来有可执行 task runtime，可增加带 `.gitignore` 的端到端归档测试。
- 不能靠 review 完全确认的点：实际 agent 运行时是否严格遵守 skill 协议仍依赖执行者，但合同测试已锁住文本协议。

## 5. Residual Risk

- 本次修复的是 CodeStable skill/reference 协议和合同测试，不是独立可执行归档程序；未来 agent 仍必须按协议使用未过滤目录枚举进行交叉确认。

## 6. Verdict

- Status: passed
- Next: issue flow completed; archive Task.
