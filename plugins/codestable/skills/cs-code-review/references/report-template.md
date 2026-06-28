# cs-code-review 报告模板

报告落在来源 workflow 的 spec 目录，文件名 `{slug}-review.md`。

新报告的 reviewer gate 锚点固定为 `subagent`。历史 `subagent+ocr` 只作旧报告读取兼容，新流程不得生成。

`status: passed` 的 canonical 证据必须同时写全 reviewer 身份与实现绑定字段，缺任一项 gate 不放行：
- `reviewer_provider`、`reviewer_model`、`reviewer_reasoning`、`reviewer_readonly: true`：如实记录本轮独立 reviewer 的 provider / 模型 / 只读态，`reviewer_reasoning` 填当前模型的最高思考等级；`gpt-5.6-sol` 例外，固定填 `xhigh`。reviewer 不可用时不得伪填。
- `reviewer_ref` 为宿主返回的真实 UUID AgentRef。
- `task_generation_sha256` 绑定当前 active Task 的稳定身份（doc_type/task/goal/workflow/created）。
- `review_basis_sha256` 绑定本轮独立 reviewer 实际审查的实现改动内容摘要；review 后实现再变必须重新 review。
- `task_generation_sha256` / `review_basis_sha256` 由 `codestable-review-basis.py` 计算，不得手填。

```markdown
---
doc_type: feature-review|issue-review|refactor-review
feature|issue|refactor: YYYY-MM-DD-slug
status: passed|changes-requested|blocked
reviewer: subagent # reviewer 未完成时省略
reviewed: YYYY-MM-DD
round: 1
reviewer_state: ready-to-launch|pending|completed|failed|unavailable
reviewer_ref: "" # pending 时必须填写宿主返回的真实 AgentRef
reviewer_provider: openai # status: passed 必填，如实填本轮 reviewer provider
reviewer_model: gpt-5.6-sol # status: passed 必填，如实填本轮 reviewer 模型
reviewer_reasoning: xhigh # status: passed 必填，填当前模型最高思考等级；gpt-5.6-sol 固定 xhigh
reviewer_readonly: true # status: passed 必填
task_generation_sha256: "" # status: passed 必填，由工具计算
review_basis_sha256: "" # status: passed 必填，由工具计算
reviewer_reason: ""
---

# {slug} 代码审查报告

## 1. Scope And Inputs

- Task: {active task path}
- Design / Analysis: {path}
- Checklist / Fix note / Apply notes: {path}
- Evidence pack: {path / none}
- Gate results: {path / none}
- DoD results: {path / none}
- Diff basis: {git status / diff / range 摘要}
- Review mode: initial | full-rereview | focused-closure
- Batch completeness: {为什么当前完整实现批次已全部完成}
- Baseline dirty files: {none / 范围外文件}

### Independent Review

- Backend/config: {按 agent-conventions 与 attention 选择的 reviewer}
- State: ready-to-launch|pending|completed|failed|unavailable
- AgentRef: {id / none}
- Merge policy: {逐条本地事实核验、去重与严重度归一}
- Gate effect: {passed / changes-requested / blocked}

## 2. Diff Summary

- 新增：{文件列表}
- 修改：{文件列表}
- 删除：{文件列表}
- 未跟踪 / staged：{文件列表}
- 风险热点：{跨模块 / 权限 / 数据 / 并发 / UI / API / none}

## 3. Adversarial Pass

- 假设的生产 bug：{最可能失败方向}
- 主动攻击的反例：{3-5 条}
- 结果：{升级为 findings / residual-risk / none}

## 4. Findings

### blocking

- [ ] REV-001 `{file:line}` {问题}
  - Evidence: {仓库事实}
  - Impact: {影响}
  - Expected fix scope: {修复边界}

### important

- [ ] REV-00N `{file:line}` {问题}
  - Evidence: {仓库事实}
  - Impact: {影响}

### nit

- [ ] REV-00N `{file:line}` {建议}

### suggestion

- [ ] REV-00N {建议}

### learning

- {经验 / none}

### praise

- {值得保留的做法 / none}

## 5. Test And QA Focus

- QA 重点：{场景}
- 建议测试：{unit / integration / e2e / none}
- Review 无法确认：{列表 / none}

## 6. Residual Risk

- {风险 + 后续处理 / none}

## 7. Verdict

- Status: passed|changes-requested|blocked
- Next: {来源 workflow review-fix / QA / acceptance / cs-task complete}

## 8. Focused Closure

- Closed findings: {REV ids / none}
- Attributed delta: {files / hunks / none}
- Targeted verification: {commands / none}
- Classification: {为什么没有行为、契约、安全、数据、并发或架构变化 / none}
```

`status: passed` 时必须同时满足：对应 unit identity 字段与目录一致、`round` 为正整数、`reviewer_state: completed`、`reviewer_ref` 非空。缺任一项都不是 canonical 独立 review evidence。

完整复审增加 `round` 并重置 reviewer state。focused closure 保留首次 `reviewer: subagent` 锚点，不伪造新 reviewer。没有某类 finding 时写 `none`，不删除章节。
