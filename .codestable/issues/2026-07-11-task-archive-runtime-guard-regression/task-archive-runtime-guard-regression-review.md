---
doc_type: issue-review
issue: 2026-07-11-task-archive-runtime-guard-regression
status: passed
reviewer: subagent
reviewed: 2026-07-18
round: 3
---

# Task 归档后 active 文件重现回归代码审查报告

## 1. Scope And Inputs

- Workflow source: issue
- Requirements / plan: report、analysis、fix-note 与用户确认的方案 B
- Checklist / task: `.codestable/tasks/active/task-archive-runtime-guard-regression.md`
- Implementation evidence: Task runtime、cs-task 协议、onboard 分发资产与行为测试
- Diff basis: working tree；显式读取可能未出现在 diff 中的 runtime 与测试文件
- Baseline dirty files: 插件打包检查既有失败项不属于本轮

### Subagent Review

- Status: failed
- Prompt template: `cs-code-review/code-reviewer.md`
- Runtime agent: none
- Runtime params: none
- Model handling: self_review_current_model
- Raw output: reviewer provider unavailable，未产生有效审查结果
- Merge policy: 按模型安全规则降级为当前主模型 self review
- Gate effect: self-review fallback

## 2. Diff Summary

- 新增：Task runtime、项目 runtime 入口、runtime 行为测试、Issue 产物
- 修改：cs-task skill/reference、onboard 工具参考与目录结构、插件检查和契约测试
- 删除：无
- 未跟踪 / staged：新增文件已按精确路径审查；无 staged diff
- 风险热点：并发、归档崩溃恢复、archived 正本完整性

## 3. Findings

### blocking

none。Round 1 `REV-001` 已修复：归档内容在移动前完成校验；移动后任一写入失败都会恢复归档前 active 原始字节并清除未完成 tombstone。两条故障注入测试覆盖 archived 内容写入失败与 completed tombstone 写入失败。

### important

none。Round 1 `REV-002` 已修复：cleanup 先校验 archived 正本与 `archived_sha256`，不一致时返回 `archived-target-integrity-failed` 并保留 active 快照。

### nit

none

### suggestion

- 后续可为 runtime 内部并发调用增加每 Task 文件锁；本轮 tombstone 已能拒绝后发的受控写入，外部编辑器仍由 cleanup 检测。

### learning

- tombstone 只有在失败路径可恢复时才是状态机保护；仅记录 `archiving` 而不实现回滚会把瞬时错误固化。

### praise

- 同源残留与分叉残留明确分流，避免静默删除真实分叉内容。
- legacy archived 正本也参与 active 写入拒绝，兼容已有项目。

## 4. Test And QA Focus

- QA 必须重点复核：移动后 archived 写入失败、tombstone 完成写入失败、archived 正本损坏后 cleanup；上述场景已有自动化故障注入覆盖。
- 建议新增或加强的测试：后续可增加两个独立进程同时操作同一 Task 的压力测试。
- 不能靠 review 完全确认的点：外部 IDE 在稳定窗口之后直接写回仍需后续 scan/cleanup 发现。

## 5. Residual Risk

- 操作系统层无法禁止绕过 runtime 的编辑器写入；归档最终检查与后续 recovery scan 仍不可省略。

## 6. Verdict

- Status: passed
- Reviewer: historical Round 2 self review; Round 3 独立 subagent focused review 已核验 runtime 状态机、崩溃恢复、TOCTOU 防护与行为测试，无 blocking 或 important finding。
- Next: 更新 Task 为 completed，并通过新 Task runtime 执行 `cs-task archive`。
