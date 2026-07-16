---
doc_type: issue-review
issue: 2026-07-01-code-review-bootstrap-shortcut
status: blocked
reviewed: 2026-07-01
round: 1
---

# code-review-bootstrap-shortcut 代码审查报告

## 1. Scope And Inputs

- Report: `.codestable/issues/2026-07-01-code-review-bootstrap-shortcut/code-review-bootstrap-shortcut-report.md`
- Analysis: `.codestable/issues/2026-07-01-code-review-bootstrap-shortcut/code-review-bootstrap-shortcut-analysis.md`
- Fix note: `.codestable/issues/2026-07-01-code-review-bootstrap-shortcut/code-review-bootstrap-shortcut-fix-note.md`
- Implementation evidence: `cs-code-review/SKILL.md`、`cs-code-review/scripts/configure-review-subagent.py`、`cs-code-review/references/subagent-config.md`、`tests/test_configure_review_subagent.py`、`tests/test_workflow_contracts.py`、当前 git diff、workflow contract 测试输出、reviewer bootstrap 输出
- Diff basis: `git status --short` 显示本轮 CodeStable skill、测试和 issue 产物修改；`git diff --cached` 为空
- Baseline dirty files: 当前仓库已有同一 reviewer 配置主线相关修改；本报告只审 `code-review-bootstrap-shortcut` issue 范围内的新增 bootstrap 短路修复

### Independent Review

- Status: blocked
- Detection: codestable-managed-subagent
- Agent IDE: cursor
- Managed agent: `.cursor/agents/cs-code-reviewer.md`
- Configured reviewer: `.codestable/config/code-review-subagent.yaml` model={configured} thinking_budget={configured}
- Actual reviewer: model={not-invoked} thinking_budget={not-invoked} model_apply_status={applied-to-managed-file} thinking_budget_apply_status={unsupported-by-host-frontmatter}
- Provider / agent: none
- Raw output: `configure-review-subagent.py` returned `status=configured`, `agent_name=cs-code-reviewer`, `managed_agent_path=.cursor/agents/cs-code-reviewer.md`; managed file read confirmed marker/name/model and self-bootstrap guard. No actual `cs-code-reviewer` review response is available because current tool layer does not expose a project custom subagent invocation API.
- Merge policy: pending/blocked 时不得定稿为 passed
- Gate effect: blocks final verdict until completed or owner explicitly approves local-only fallback

## 2. Diff Summary

- 新增：当前 issue 的 report / analysis / fix-note / code-review 产物和 active task。
- 修改：`cs-code-review/SKILL.md` 增加不可跳过 `Reviewer bootstrap` 启动阶段；`configure-review-subagent.py` 生成的 managed reviewer 加入 self-bootstrap guard；`subagent-config.md` 和测试增加对应约束。
- 验证：workflow contract 和 reviewer 配置目标测试通过；已执行 reviewer bootstrap 配置脚本并读取 managed agent 文件确认 self-bootstrap guard。
- 风险热点：workflow gate 顺序、旧 review 报告短路、custom subagent invocation 证据。

## 3. Findings

### blocking

- [ ] CR-001 `custom-subagent-invocation` 当前 runtime 未暴露按项目 custom subagent 名称调用 `cs-code-reviewer` 的入口
  - Evidence: reviewer bootstrap 已真实执行并生成 `.cursor/agents/cs-code-reviewer.md`；文件内容包含 `name: cs-code-reviewer`、`model: "gpt-5.5"`、`CodeStable managed` marker 和 self-bootstrap guard。但当前可用 Subagent 工具只暴露内置类型，不能指定项目 custom agent `cs-code-reviewer` 执行审查。
  - Impact: 本次修复已消除“旧 blocked 报告短路 reviewer bootstrap”以及“managed reviewer 自身缺少自修复指令”的流程 bug，但仍缺少独立 reviewer 的审查回执；不能把本地 review 或内置 general-purpose subagent 伪装成 configured reviewer。
  - Expected fix scope: 等 Cursor runtime 暴露项目 custom subagent 调用入口后显式调用 `cs-code-reviewer`；或由 owner 明确接受 local-only / current-conversation fallback 后重跑 gate。

### important

- none

### nit

- none

### suggestion

- 后续可把 reviewer bootstrap 的执行结果写成更固定的 review evidence 字段，方便下游区分 `configured`、`invoked`、`returned` 三个状态。

### learning

- 旧 review 报告只能作为历史输入；任何涉及当前文件存在性、managed agent 状态、actual reviewer 的字段都必须重新验证。

### praise

- 本次修复把“不能用旧 blocked verdict 短路当轮 bootstrap”的要求提升到启动检查顶部，并用 contract test 锁住关键语义，直接覆盖了本次复现路径。

## 4. Test And QA Focus

- 已执行：workflow contract 测试通过。
- 已执行：`configure-review-subagent.py` 返回 `status=configured`，`agent_ide=cursor`，`agent_name=cs-code-reviewer`，`model_apply_status=applied`。
- 已执行：读取 `.cursor/agents/cs-code-reviewer.md`，确认 managed marker、name、model 和 self-bootstrap guard。
- QA 必须重点复核：下一次 `/cs-code-review` 不应直接复述旧 blocked 报告，而应先运行 reviewer bootstrap。
- QA 必须重点复核：直接启动 `/cs-code-reviewer` 时，如果 `.cursor/agents/cs-code-reviewer.md` 缺失，reviewer 指令必须先运行配置脚本生成 / 修复自身文件，而不是直接汇报 invocation blocked。

## 5. Residual Risk

- 当前修复解决的是 workflow bootstrap 短路；项目 custom subagent 的真实调用仍受 runtime 能力限制。
- `.cursor/` 被 `.gitignore` 忽略，因此旧报告里的 managed agent 生成状态不能跨会话视为事实，必须每轮重新验证。

## 6. Verdict

- Status: blocked
- Next: 等 runtime 支持显式调用项目 custom subagent `cs-code-reviewer` 后重跑本审查；不得用 Explore / general-purpose / built-in subagent 替代
